#!/usr/bin/env python3
"""Convert matrix.csv -> matrix.parquet, stamped with the parameterisation.

    python3 scenarios/_matrix/to_parquet.py
    python3 scenarios/_matrix/to_parquet.py --in other.csv --out other.parquet

Why this exists: a bare CSV records what VARIED (the axis columns) but loses
what was HELD FIXED -- and "which model produced this table?" becomes
unanswerable once core/ moves on. Parquet stores arbitrary key/value metadata
in its footer, so the constants, the git SHA of core/, and the reading caveats
travel with the data.

Read it back WITHOUT loading the rows:

    import pyarrow.parquet as pq
    pq.read_schema('matrix.parquet').metadata

NOTE: a pandas read_parquet -> to_parquet round-trip DROPS these keys. Always
go through pyarrow (as below) when rewriting.
"""

import argparse
import json
import pathlib
import subprocess
import sys

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import axes as AX  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULTS = ROOT / "scenarios" / "_matrix" / "results"

COORD_COLUMNS = ["ccoal","ng","h2_start","avg_emi","ramp","scrap_rate","grid_ef_target","theta_ccs","whr_mode"]

CATEGORICAL = ["ccoal", "ng", "ramp", "whr_mode", "solve_result"]


def git_sha():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(ROOT)).decode().strip()
    except Exception:
        return "unknown"


def dirty():
    try:
        out = subprocess.check_output(
            ["git", "status", "--porcelain", "core/"], cwd=str(ROOT)).decode()
        return "yes" if out.strip() else "no"
    except Exception:
        return "unknown"


def build_metadata(df):
    solved = int((df.solve_result == "solved").sum())
    presolve_infeas = int(df.solve_result.astype(str).str.startswith("ERROR").sum())
    infeas = len(df) - solved - presolve_infeas

    axis_levels = {}
    for name, levels in AX.AXES.items():
        axis_levels[name] = [lv[0] if isinstance(lv, tuple) else lv for lv in levels]

    return {
        # --- provenance ---
        "model_commit": git_sha(),
        "core_dirty_at_write": dirty(),
        "generator": "scenarios/_matrix/run_matrix.py",
        "solver": "gurobi 13.0.2, Threads=1 (dual simplex; LP does not parallelise)",

        # --- the design ---
        "axes": json.dumps(axis_levels),
        "n_cells_expected": str(AX.size()),
        "n_rows": str(len(df)),
        "n_solved": str(solved),
        "n_infeasible_solver": str(infeas),
        "n_infeasible_presolve": str(presolve_infeas),

        # --- what was HELD FIXED (the part a CSV loses) ---
        "const_cap_add_common": (
            "set by the ramp axis: low/medium/high = 10/15/20 Mt/yr. Applied as FOUR "
            "INDEPENDENT per-route caps (v_capacity.mod:90-93) on build_bof, build_cdri, "
            "build_ngdri, build_scrap -- NOT a shared investment budget. build_h2dri has "
            "no per-year cap at all."),
        "const_h2_ref_cap": (
            "set by the ramp axis: low/medium/high = 4/6/8 Mt/yr. Scales the Gaussian "
            "electrolyser growth ceiling (v_capacity.mod:215-235). Perfectly collinear "
            "with cap_add_common in this run (ratio 2.5) -- the 'ramp' axis is therefore "
            "NOT H2-specific: it also sets conventional build rates."),
        "const_theta_tech": "0.5 fixed (core/parameters.mod) -- H2/RE cost learning, never swept",
        "const_theta_grid": "derived per cell from the grid_ef axis; also sets the electricity tariff",
        "const_emission_monotonic": "DROPPED in every cell (the model's only nonlinearity)",
        "const_demand": "exogenous: 152.2 Mt in 2025, +5%/yr, 515.4 Mt in 2050",
        "const_emissions_constraint": (
            "avg_emis_cap_total -- ONE cumulative constraint over 2025-2050, not per-year: "
            "sum(total_emissions) <= avg_emi * sum(total_steel)"),

        # --- how to read it ---
        "caveat_error_rows": (
            "solve_result starting 'ERROR: ...presolve: constraint steel_balance...' are "
            "GENUINE infeasibilities proven by AMPL presolve, concentrated in the "
            "scarce-coal/bau-gas/late-H2 corner. COUNT THEM AS INFEASIBLE. Use "
            "solved = (solve_result == 'solved'); do not filter ERROR rows out."),
        "caveat_extrapolated": (
            "extrapolated == 1 means theta_grid left its calibrated [0,1] window, so the "
            "COUPLED electricity tariff is extrapolated beyond its $0.055-0.085/kWh anchors "
            "(out to $0.025-0.110). Filter extrapolated == 0 for any cost claim; the "
            "feasibility frontier is still usable across the full band."),
        "caveat_import_bill": (
            "import_bill INVERTS: scarce regimes post LOWER bills while costing MORE per "
            "tonne, because a binding cap forbids importing. Read it with ccoal_bind_yrs / "
            "ng_bind_yrs -- a low bill with a high bind count is forced scarcity."),
        "caveat_scrap_ceiling": (
            "share_scrap saturates at util_max * life_scrap * cap_add_common / demand[2050] "
            "= 0.95*15*cap_add_common/515.4Mt (0.2765 / 0.4147 / 0.5530 for low/medium/high "
            "ramp). This is a capacity BUILD-RATE limit, not scrap availability."),
        "caveat_infeasible_numerics": (
            "infeasible rows retain whatever numerics the solver left in the variables. "
            "Every metric column is meaningless unless solve_result == 'solved'."),
        "caveat_grid_tripwire": (
            "grid_ef_2050 is read back from the SOLVED model and must track grid_ef_target "
            "row for row. If it goes constant while the target varies, the "
            "one-AMPL-instance-per-run invariant was broken and the grid axis was inert."),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="src", default=str(RESULTS / "matrix.csv"))
    p.add_argument("--out", dest="dst", default=str(RESULTS / "matrix.parquet"))
    args = p.parse_args()

    src, dst = pathlib.Path(args.src), pathlib.Path(args.dst)
    print(f"reading {src} ({src.stat().st_size/1e6:.0f} MB) ...")
    df = pd.read_csv(src, on_bad_lines="skip")

    # A --resume pass re-solves any cell whose row was lost from the write
    # buffer when a prior run was killed (SIGTERM discards it), so the CSV can
    # carry duplicate coordinates. The LP is deterministic, so duplicates agree
    # -- but they must go before any count or groupby is trusted.
    coords = [c for c in COORD_COLUMNS if c in df]
    before = len(df)
    df = df.drop_duplicates(subset=coords, keep="last").reset_index(drop=True)
    if before != len(df):
        print(f"  deduplicated on {len(coords)} coordinate columns: "
              f"{before:,} -> {len(df):,} rows ({before-len(df):,} removed)")

    expected = AX.size()
    if len(df) != expected:
        print(f"  WARNING: {len(df):,} rows != {expected:,} expected cells "
              f"({expected-len(df):+,})")
    else:
        print(f"  row count matches the design exactly: {expected:,}")

    for c in CATEGORICAL:
        if c in df:
            df[c] = df[c].astype("category")

    table = pa.Table.from_pandas(df)
    meta = {**(table.schema.metadata or {})}
    meta.update({k.encode(): v.encode() for k, v in build_metadata(df).items()})
    table = table.replace_schema_metadata(meta)

    pq.write_table(table, dst, compression="zstd")
    print(f"wrote {dst} ({dst.stat().st_size/1e6:.0f} MB, "
          f"{src.stat().st_size/dst.stat().st_size:.1f}x smaller)")

    back = pq.read_schema(dst).metadata
    print(f"metadata keys: {sum(1 for k in back if not k.startswith(b'pandas'))}")
    print(f"  model_commit = {back[b'model_commit'].decode()}")
    print(f"  rows = {back[b'n_rows'].decode()}  solved = {back[b'n_solved'].decode()}")


if __name__ == "__main__":
    sys.exit(main())
