#!/usr/bin/env python3
"""Monte Carlo uncertainty study: the SINGLE shared solve behind every
uncertainty/ and violin/ figure.

Three batches, one per emission target (1.6/1.8/2.0). Each batch solves
every structural cell feasible AT THAT TARGET (read from structural/
feasibility_and_synergy/feasibility_drivers/data/feasibility_drivers.xlsx,
sheet "raw_matrix") x the same 30 shared, balanced cost/tech draws (draw-seed
20260824, grids over ccoal_price/ng_price/scrap_price/theta_tech/
theta_ccs; discount_rate pinned at 0.06 by template_montecarlo.mod).

The SAME draws are reused identically across all three batches -- a
given draw_id always carries the exact same cost/tech values everywhere
it appears, in every batch. This "shared-draw" design is what lets
downstream studies compare matched worlds across targets: cells feasible
at EF=1.6 are also feasible at EF=1.8 and EF=2.0 (feasibility only gets
easier as the target loosens), so those cells appear in all three
batches and can be joined by (structural coords, draw_id) to compare the
SAME world's LCOP under different targets.

Total: 794 (EF1.6) + 1,196 (EF1.8) + 1,554 (EF2.0) = 3,544 cells x 50
draws = 177,200 solves. This one run is sufficient to populate:
  - uncertainty/shares, cost_risk, coking_coal_stochasticity
      -- all three read the EF=1.8 sheet only
  - uncertainty/cost_distribution
      -- joins the EF=1.6-feasible cells (which nest inside 1.8 and 2.0)
         across all three sheets to get lcop_1.6/1.8/2.0 per world
  - violin
      -- reads the EF=1.8 sheet, filtered further to ramp=medium

Every uncertainty/*/run_*.py and violin/run_violin.py is pure filtering
on top of this one workbook -- no AMPL/Gurobi calls of their own.

Output: data/mc_solves.xlsx, one sheet per target ("ef1.6", "ef1.8",
"ef2.0") -- cell_id, draw_id, the 9 structural coordinates (incl. ccs_phi), avg_emi, the
5 cost/tech draw values, solve_result, lcop, the 5 route shares,
emis2050 (the 2050 snapshot emission intensity, needed by violin's
right-hand histogram), and cum_co2/cum_captured (cumulative 2025-2050
emissions and CCS capture, needed by violin's capture-fraction marker).

    python run_montecarlo.py -j 6
"""
import argparse
import multiprocessing as mp
import pathlib
import random
import shutil
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
FEAS_XLSX = (ROOT / "structural" / "feasibility_and_synergy" /
             "feasibility_drivers" / "data" / "feasibility_drivers.xlsx")
OUT_DIR = HERE / "data"
BATCH_SIZE = 40_000  # solves per parquet part file
AMPL_TMP = ROOT / "scratchpad" / "ampl_tmp"  # disk-backed; /tmp is a RAM tmpfs

TARGETS = [1.6, 1.8, 2.0]
N_DRAWS = 30   # [audit] balanced draws (was 50 random picks); see commit message for precision
DRAW_SEED = 20260824
CCS_LEVELS = None   # [audit] None = every ccs_phi level in the feasibility matrix
BRACKETING = False  # [audit] True = coal/NG abundant and scarce only

def _grid(lo, hi, step):
    n = int(round((hi - lo) / step))
    return [round(lo + i * step, 6) for i in range(n + 1)]


# [audit] Sampling grids (user, 2026-10-08). Was 3 or 5 discrete levels per input.
MC_LEVELS = {
    "ccoal_price": _grid(150, 300, 10),   # $/t, 16 levels
    "ng_price": _grid(5, 20, 1),          # $/MMBtu, 16 levels
    "scrap_price": _grid(300, 500, 10),   # $/t, 21 levels
    "theta_tech": _grid(0, 1, 0.1),       # 11 levels
    "theta_ccs": _grid(0, 1, 0.1),        # 11 levels
}

CCOAL_FILE = {"abundant": "ccoal_abundant", "midhigh": "ccoal_midhigh",
              "midlow": "ccoal_midlow", "scarce": "ccoal_scarce"}
NG_FILE = {"abundant": "ng_policy", "midhigh": "ng_midhigh",
           "midlow": "ng_midlow", "scarce": "ng_bau"}
RAMP_H2REF = {"low": 1_000_000, "medium": 2_000_000, "high": 3_000_000}  # [audit] re-anchored
BUILD_CAP_VAL = {"tight": 20_000_000, "mid": 30_000_000}
LEGACY_FLAG = {"run-life": 0, "mandated-phaseout": 1}

STRUCT_COLS = ["ccoal", "ng", "h2_start", "scrap_rate", "theta_grid_target",
               "ramp", "build_cap", "legacy", "ccs_phi", "avg_emi"]
DRAW_COLS = ["ccoal_price", "ng_price", "scrap_price", "theta_tech", "theta_ccs"]
METRIC_COLUMNS = [
    ("lcop", "m_lcop"),
    ("share_bof", "m_sh_bof"), ("share_cdri", "m_sh_cdri"),
    ("share_ngdri", "m_sh_ngdri"), ("share_h2", "m_sh_h2"),
    ("share_scrap", "m_sh_scrap"),
    ("emis2050", "total_emissions[2050]/total_steel[2050]"),
    ("cum_co2", "m_cum_co2"),
    ("cum_captured", "m_cum_captured"),
]
COLUMNS = ["cell_id", "draw_id"] + STRUCT_COLS + DRAW_COLS + \
    ["solve_result"] + [c for c, _ in METRIC_COLUMNS]


def sample_draws(n_draws=N_DRAWS, seed=DRAW_SEED):
    """Balanced (Latin-hypercube style) draws over the discrete grids.

    For each input, its levels are repeated as evenly as n_draws allows (counts
    differ by at most one; the levels that get the extra copy are chosen at
    random) and shuffled independently, so every level is equally represented
    and inputs are paired at random. Seeded, so the draws are identical on
    every run and shared by every cell and target.
    """
    rng = random.Random(seed)
    cols = {}
    for k, levels in MC_LEVELS.items():
        q, r = divmod(n_draws, len(levels))
        col = levels * q + rng.sample(levels, r)
        rng.shuffle(col)
        cols[k] = col
    return [{k: cols[k][i] for k in MC_LEVELS} for i in range(n_draws)]


def feasible_cells(avg_emi):
    import pandas as pd
    df = pd.read_excel(FEAS_XLSX, sheet_name="raw_matrix")
    feas = df[(df.avg_emi == avg_emi) & (df.solve_result == "solved")]
    if CCS_LEVELS is not None:  # [audit] restrict the CCS-ceiling axis
        feas = feas[feas.ccs_phi.isin(CCS_LEVELS)]
    if BRACKETING:  # [audit] only the abundant/scarce supply regimes
        feas = feas[feas.ccoal.isin(["abundant", "scarce"]) & feas.ng.isin(["abundant", "scarce"])]
    return feas.to_dict("records")


def solve_cell(cell, draw, solver="gurobi"):
    from amplpy import AMPL

    ampl = AMPL()
    ampl.cd(str(ROOT))
    ampl.set_option("solver_msg", 0)
    AMPL_TMP.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="amplmc_", dir=AMPL_TMP)
    ampl.set_option("TMPDIR", tmp)

    ampl.eval("include core/model.mod;")
    ampl.eval(f"include structural/axes/{CCOAL_FILE[cell['ccoal']]}.mod;")
    ampl.eval(f"include structural/axes/{NG_FILE[cell['ng']]}.mod;")
    ampl.eval("include monte_carlo/template_montecarlo.mod;")

    ampl.eval(f"let ng_h2_start_year := {int(cell['h2_start'])};")
    ampl.eval(f"let avg_emi := {cell['avg_emi']};")
    ampl.eval(f"let h2_ref_cap := {RAMP_H2REF[cell['ramp']]};")
    ampl.eval(f"let n8_scrap_rate := {cell['scrap_rate']};")
    ampl.eval(f"let legacy_phaseout := {LEGACY_FLAG[cell['legacy']]};")
    ampl.eval(f"let cap_add_common := {BUILD_CAP_VAL[cell['build_cap']]};")
    ampl.eval(f"let theta_grid := {cell['theta_grid_target']};")
    ampl.eval(f"let phi_2050 := {cell['ccs_phi']};")  # [audit] CCS ceiling axis
    ampl.eval(f"let ng_cost_ccoal := {draw['ccoal_price']};")
    ampl.eval(f"let {{t in T}} n5_cost_NG[t] := {draw['ng_price']};")
    ampl.eval(f"let ng_cost_scrap := {draw['scrap_price']};")
    ampl.eval(f"let theta_tech := {draw['theta_tech']};")
    ampl.eval(f"let theta_ccs := {draw['theta_ccs']};")

    ampl.eval(f"option solver {solver};")
    if solver == "gurobi":
        ampl.eval("option gurobi_options 'Threads=1';")
    # [audit] emission_monotonic is now linear and kept active (paper s2.2); was dropped here
    ampl.eval("solve;")

    status = ampl.get_value("solve_result")
    row = {c: cell[c] for c in STRUCT_COLS}
    row.update({c: draw[c] for c in DRAW_COLS})
    row["solve_result"] = status
    if status == "solved":
        ampl.eval("include structural/report.mod;")
        for col, expr in METRIC_COLUMNS:
            row[col] = ampl.get_value(expr)
    else:
        for col, _ in METRIC_COLUMNS:
            row[col] = ""
    ampl.close()
    shutil.rmtree(tmp, ignore_errors=True)  # drop this solve's .nl/.sol files
    return row


def _worker(args):
    ci, di, cell, draw = args
    row = solve_cell(cell, draw)
    return {"cell_id": ci, "draw_id": di, **row}


def _flush(rows, avg_emi, part):
    import pandas as pd
    out = OUT_DIR / f"mc_solves_ef{avg_emi}_part{part:02d}.parquet"
    pd.DataFrame(rows)[COLUMNS].to_parquet(out, index=False, compression="snappy")
    print(f"written: {out.relative_to(ROOT)} ({len(rows):,} rows)", flush=True)


def run_batch(avg_emi, draws, jobs):
    cells = feasible_cells(avg_emi)
    todo = [(ci, di, cell, draw) for ci, cell in enumerate(cells)
            for di, draw in enumerate(draws)]
    print(f"EF={avg_emi}: {len(cells):,} feasible cells x {len(draws)} draws "
          f"= {len(todo):,} solves", flush=True)

    rows, part = [], 0
    t0 = time.time()
    with mp.Pool(jobs) as pool:
        for i, row in enumerate(pool.imap_unordered(_worker, todo, chunksize=8), 1):
            rows.append(row)
            if len(rows) == BATCH_SIZE:  # part file every BATCH_SIZE solves; a crash keeps finished parts
                _flush(rows, avg_emi, part)
                rows, part = [], part + 1
            if i % 2000 == 0 or i == len(todo):
                el = time.time() - t0
                print(f"  {i:>7,}/{len(todo):,}  {i/el:6.1f}/s  "
                      f"ETA {(len(todo)-i)/max(i/el,1e-9)/60:6.1f} min", flush=True)
    if rows:
        _flush(rows, avg_emi, part)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-j", "--jobs", type=int, default=6)
    p.add_argument("--draws", type=int, default=N_DRAWS, help="balanced draws per cell")
    p.add_argument("--bracketing", action="store_true",
                   help="coal/NG abundant and scarce only (skip the intermediate levels)")
    p.add_argument("--ccs", type=float, nargs="+", default=None,
                   help="CCS-ceiling levels (phi_2050) to solve; default all")
    args = p.parse_args()
    global CCS_LEVELS, BRACKETING
    CCS_LEVELS = args.ccs
    BRACKETING = args.bracketing

    draws = sample_draws(args.draws)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for ef in TARGETS:
        run_batch(ef, draws, args.jobs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
