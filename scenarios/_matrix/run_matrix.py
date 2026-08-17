#!/usr/bin/env python3
"""Unified Section A design matrix: solve every cell of the axis cross product.

Replaces the six per-study drivers with one runner over one axis registry
(axes.py). Each study becomes a SLICE of the output table rather than a
separate script.

    python3 scenarios/_matrix/run_matrix.py --smoke          # 20 cells
    python3 scenarios/_matrix/run_matrix.py --verify         # baseline cell only
    python3 scenarios/_matrix/run_matrix.py -j 6             # full matrix
    python3 scenarios/_matrix/run_matrix.py -j 6 --resume    # continue a partial run

Output: results/matrix.csv (one row per cell, solved or not).

--------------------------------------------------------------------------
INVARIANT -- ONE AMPL INSTANCE PER RUN. DO NOT "OPTIMIZE" THIS AWAY.
--------------------------------------------------------------------------
Reusing an AMPL instance across cells would save ~0.07 s/run, and it would
silently break the grid-EF axis. `n9_grid_ef_end` is declared in
core/definitions.mod:168 as `param ... default <expression involving
theta_grid>`. AMPL evaluates a `default` expression ONCE, on first read, and
freezes it. A reused instance therefore pins the grid EF at whatever the
first cell produced, while every subsequent row still records the REQUESTED
target -- a table that looks perfectly plausible and is wrong.

The grid_ef_2050 column exists to catch exactly this: it is read back from
the solved model, so it must track grid_ef_target row for row. If it ever
goes constant while grid_ef_target varies, this invariant has been violated.

Threads=1 is deliberate too: measured, Gurobi gets ~9% from a 10x thread
budget on this LP (it solves by dual simplex, which does not parallelize).
Parallelism belongs across cells, not inside them.
"""

import argparse
import csv
import itertools
import multiprocessing as mp
import os
import pathlib
import sys
import tempfile
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import axes as AX  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULTS = ROOT / "scenarios" / "_matrix" / "results"
CCOAL_NG_AXES = ROOT / "scenarios" / "import-dependence" / "axes"

# Coordinates written by Python; metrics read back from the solved model.
COORD_COLUMNS = [
    "ccoal", "ng", "h2_start", "scrap_rate", "grid_ef_target",
    "ramp", "build_cap", "legacy", "avg_emi",
]
STATUS_COLUMNS = ["solve_result", "objective", "theta_grid", "extrapolated"]

# (csv column, AMPL expression). Read back after solve.
METRIC_COLUMNS = [
    ("grid_ef_2050",      "n9_grid_ef[2050]"),
    ("tariff_2050",       "ng_cost_power[2050]"),
    ("lcop",              "m_lcop"),
    ("cum_co2",           "m_cum_co2"),
    ("avg_emis",          "m_avg_emis"),
    ("ccoal_bill",        "m_cum_ccoal_bill"),
    ("ng_bill",           "m_cum_ng_bill"),
    ("import_bill",       "m_cum_ccoal_bill + m_cum_ng_bill"),
    ("ng_import_qty",     "m_cum_ng_import"),
    ("ccoal_import_qty",  "m_cum_ccoal_import"),
    ("ccoal_bind_yrs",    "m_ccoal_bind"),
    ("ng_bind_yrs",       "m_ng_bind"),
    ("share_bof",         "m_sh_bof"),
    ("share_cdri",        "m_sh_cdri"),
    ("share_ngdri",       "m_sh_ngdri"),
    ("share_h2",          "m_sh_h2"),
    ("share_scrap",       "m_sh_scrap"),
    ("red_h2_2050",       "m_red_h2_2050"),
    ("ccs_2050",          "total_ccs[2050]"),
    ("cap_h2dri_2050",    "cap_h2dri[2050]"),
    ("scrap_use_2050",    "m_scrap_use_2050"),
    ("scrap_limit_2050",  "n8_scrap_limit[2050]"),
    ("eff_capture_cost",  "m_eff_capture_cost"),
    ("cum_captured",      "m_cum_captured"),
    ("boiler_steam_share", "m_boiler_steam_sh"),
    ("whr_power_2050",    "whr_power_generated[2050]"),
]
COLUMNS = COORD_COLUMNS + STATUS_COLUMNS + [c for c, _ in METRIC_COLUMNS]


def cells(axes=None):
    """Enumerate the cross product as dicts of axis label -> level."""
    axes = axes or AX.AXES
    names = list(axes)
    for combo in itertools.product(*(axes[n] for n in names)):
        yield dict(zip(names, combo))


def coord_key(cell):
    """Stable identity for a cell, for --resume."""
    return (cell["ccoal"][0], cell["ng"][0], cell["h2_start"],
            cell["scrap_rate"], cell["grid_ef"], cell["ramp"][0],
            cell["build_cap"][0], cell["legacy"][0], cell["avg_emi"])


def solve_cell(cell, solver="gurobi", verbose=False):
    from amplpy import AMPL

    ccoal_label, ccoal_file = cell["ccoal"]
    ng_label, ng_file = cell["ng"]
    ramp_label, h2_ref = cell["ramp"]
    legacy_label, legacy_flag = cell["legacy"]
    build_label, build_cap = cell["build_cap"]
    grid_ef = cell["grid_ef"]

    # One instance per run -- see INVARIANT in the module docstring.
    ampl = AMPL()
    ampl.cd(str(ROOT))
    if not verbose:
        ampl.set_option("solver_msg", 0)
    # Per-worker scratch so parallel workers cannot collide on .nl/.sol files.
    try:
        ampl.set_option("TMPDIR", tempfile.mkdtemp(prefix="amplwk_"))
    except Exception:
        pass

    ampl.eval("include core/model.mod;")

    # --- availability axes (time-indexed tables; None == core baseline) ---
    if ccoal_file:
        ampl.eval(f"include {CCOAL_NG_AXES.relative_to(ROOT)}/{ccoal_file}.mod;")
    if ng_file:
        ampl.eval(f"include {CCOAL_NG_AXES.relative_to(ROOT)}/{ng_file}.mod;")

    # --- scalar axes ---
    # h2_peak_year and n8_scrap_limit are DERIVED in core/definitions.mod and
    # follow these automatically; assigning them directly is an AMPL error.
    ampl.eval(f"let ng_h2_start_year := {cell['h2_start']};")
    ampl.eval(f"let avg_emi := {cell['avg_emi']};")
    ampl.eval(f"let h2_ref_cap := {h2_ref};")
    ampl.eval(f"let n8_scrap_rate := {cell['scrap_rate']};")
    ampl.eval(f"let legacy_phaseout := {legacy_flag};")
    ampl.eval(f"let cap_add_common := {build_cap};")
    # Constants: held fixed in every cell (see axes.py CONSTANTS for why).
    for name, value in AX.CONSTANTS.items():
        ampl.eval(f"let {name} := {value};")
    # theta_grid is back-solved from the target EF: grid EF and the industrial
    # tariff are coupled outcomes of the same learning parameter, so the EF
    # cannot be set independently of the price.
    ampl.eval(
        f"let theta_grid := ({grid_ef} - grid_ef_end_slow) "
        f"/ (grid_ef_end_fast - grid_ef_end_slow);"
    )

    ampl.eval(f"option solver {solver};")
    if solver == "gurobi":
        ampl.eval("option gurobi_options 'Threads=1';")
    ampl.eval("drop emission_monotonic;")
    ampl.eval("solve;")

    status = ampl.get_value("solve_result")
    try:
        obj = ampl.get_objective("obj").value()
    except Exception:
        obj = float("nan")

    ampl.eval("include scenarios/_matrix/report.mod;")

    lo, hi = AX.GRID_EF_CALIBRATED
    row = {
        "ccoal": ccoal_label, "ng": ng_label, "h2_start": cell["h2_start"],
        "scrap_rate": cell["scrap_rate"], "grid_ef_target": grid_ef,
        "ramp": ramp_label, "build_cap": build_label,
        "legacy": legacy_label, "avg_emi": cell["avg_emi"],
        "solve_result": status, "objective": obj,
        "theta_grid": ampl.get_value("theta_grid"),
        "extrapolated": 0 if lo <= grid_ef <= hi else 1,
    }
    for col, expr in METRIC_COLUMNS:
        try:
            row[col] = ampl.get_value(expr)
        except Exception:
            row[col] = ""
    ampl.close()
    return row


def _worker(cell):
    try:
        return solve_cell(cell, solver=_worker.solver)
    except Exception as exc:                      # keep one bad cell from
        row = {c: "" for c in COLUMNS}            # killing the whole sweep
        row.update({
            "ccoal": cell["ccoal"][0], "ng": cell["ng"][0],
            "h2_start": cell["h2_start"], "scrap_rate": cell["scrap_rate"],
            "grid_ef_target": cell["grid_ef"], "ramp": cell["ramp"][0],
            "build_cap": cell["build_cap"][0],
            "legacy": cell["legacy"][0], "avg_emi": cell["avg_emi"],
            "solve_result": f"ERROR: {type(exc).__name__}: {exc}"[:200],
        })
        return row


def _init(solver):
    _worker.solver = solver


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-j", "--jobs", type=int, default=6,
                   help="worker processes (default 6 = physical cores)")
    p.add_argument("--solver", default="gurobi")
    p.add_argument("--smoke", action="store_true", help="first 20 cells only")
    p.add_argument("--verify", action="store_true",
                   help="solve the baseline cell only and print it")
    p.add_argument("--resume", action="store_true",
                   help="skip cells already present in matrix.csv")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    RESULTS.mkdir(parents=True, exist_ok=True)
    out = pathlib.Path(args.out) if args.out else RESULTS / "matrix.csv"

    if args.verify:
        b = AX.BASELINE
        cell = {
            "ccoal": next(c for c in AX.CCOAL if c[0] == b["ccoal"]),
            "ng": next(c for c in AX.NG if c[0] == b["ng"]),
            "h2_start": b["h2_start"], "avg_emi": b["avg_emi"],
            "ramp": next(r for r in AX.RAMP if r[0] == b["ramp"]),
            "build_cap": next(c for c in AX.BUILD_CAP if c[0] == b["build_cap"]),
            "scrap_rate": b["scrap_rate"], "grid_ef": b["grid_ef"],
            "legacy": next(l for l in AX.LEGACY if l[0] == b["legacy"]),
        }
        row = solve_cell(cell, solver=args.solver, verbose=False)
        for k in COLUMNS:
            print(f"  {k:20s} {row[k]}")
        return 0

    todo = list(cells())
    if args.smoke:
        todo = todo[:20]

    done = set()
    if args.resume and out.exists():
        with open(out) as fh:
            for r in csv.DictReader(fh):
                done.add((r["ccoal"], r["ng"], int(r["h2_start"]),
                          float(r["scrap_rate"]), float(r["grid_ef_target"]),
                          r["ramp"], r["build_cap"], r["legacy"],
                          float(r["avg_emi"])))
        todo = [c for c in todo if coord_key(c) not in done]
        print(f"resume: {len(done):,} done, {len(todo):,} remaining")

    if not todo:
        print("nothing to do")
        return 0

    mode = "a" if (args.resume and out.exists()) else "w"
    t0 = time.time()
    n_solved = n_infeas = n_err = 0

    with open(out, mode, newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        if mode == "w":
            w.writeheader()
        with mp.Pool(args.jobs, initializer=_init, initargs=(args.solver,)) as pool:
            for i, row in enumerate(pool.imap_unordered(_worker, todo, chunksize=8), 1):
                w.writerow(row)
                sr = str(row["solve_result"])
                if sr == "solved":
                    n_solved += 1
                elif sr.startswith("ERROR"):
                    n_err += 1
                else:
                    n_infeas += 1
                if i % 500 == 0 or i == len(todo):
                    el = time.time() - t0
                    rate = i / el
                    eta = (len(todo) - i) / rate / 60
                    print(f"  {i:>7,}/{len(todo):,}  {rate:6.1f} cell/s  "
                          f"ETA {eta:6.1f} min  solved={n_solved:,} "
                          f"infeas={n_infeas:,} err={n_err:,}", flush=True)
                    fh.flush()

    el = time.time() - t0
    print(f"\n{len(todo):,} cells in {el/60:.1f} min "
          f"({len(todo)/el:.1f}/s) -> {out.relative_to(ROOT)}")
    print(f"solved={n_solved:,}  infeasible={n_infeas:,}  errors={n_err:,}")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
