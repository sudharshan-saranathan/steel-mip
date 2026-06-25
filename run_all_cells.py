#!/usr/bin/env python
"""
Production driver: generate the price-grid table for every FEASIBLE structural
cell, writing one CSV per cell into cells/.

By default runs ALL NG scenarios on this machine (~1.8 h for the 38 feasible
cells). Set MC_SCENARIO={normal,shock,optimistic} to restrict to one scenario
(e.g. to split across machines).

Each cell runs via run_mc_grid_parallel.py (12 procs x 1 thread). Cells already
present in cells/ with the expected row count are SKIPPED -> resumable.

Env:
  MC_SCENARIO   NG scenario to run, or "all" (default all)
  MC_GRID       grid spec (default 25,12,8 = 2400 pts/cell)
"""
import os, csv, subprocess, sys, time

PROJECT   = os.path.dirname(os.path.abspath(__file__))
SCENARIO  = os.environ.get("MC_SCENARIO", "all")
GRID      = os.environ.get("MC_GRID", "25,12,8")
CELLS_DIR = os.path.join(PROJECT, "cells")
TRAJ_DIR  = os.path.join(PROJECT, "cells_traj")    # year-by-year trajectory store
os.makedirs(CELLS_DIR, exist_ok=True)
os.makedirs(TRAJ_DIR, exist_ok=True)

nh2, nccs, nng = (int(x) for x in GRID.split(","))
EXPECTED      = nh2 * nccs * nng
EXPECTED_TRAJ = EXPECTED * 26                       # 26 years (2025-2050) per draw

# feasible cells from the frontier map (optionally restricted to one NG scenario)
with open(os.path.join(PROJECT, "mc_frontier.csv")) as fh:
    cells = [r for r in csv.DictReader(fh)
             if r["status"] == "solved"
             and (SCENARIO == "all" or r["ng_scenario"] == SCENARIO)]
cells.sort(key=lambda r: (r["ng_scenario"], r["scrap_regime"], int(r["h2_start_year"])))

if not cells:
    sys.exit(f"No feasible cells for NG scenario '{SCENARIO}' "
             f"(check MC_SCENARIO / mc_frontier.csv)")

print(f"NG scenario '{SCENARIO}': {len(cells)} feasible cells "
      f"| grid {GRID} = {EXPECTED} pts/cell  (~{len(cells)*170/60:.0f} min)")

def rowcount(path):
    if not os.path.exists(path): return -1
    with open(path) as fh: return sum(1 for _ in fh) - 1

t0 = time.time()
for k, c in enumerate(cells, 1):
    scen, scrap, h2y = c["ng_scenario"], c["scrap_regime"], c["h2_start_year"]
    name = f"{scen}_{scrap}_{h2y}.csv"
    out  = os.path.join(CELLS_DIR, name)
    traj = os.path.join(TRAJ_DIR, name)
    if rowcount(out) == EXPECTED and rowcount(traj) == EXPECTED_TRAJ:
        print(f"[{k}/{len(cells)}] {name}  SKIP (already complete)"); continue
    env = os.environ.copy()
    env.update({"MC_GRID": GRID, "MC_SCENARIO": scen, "MC_SCRAP_REGIME": scrap,
                "MC_H2YEAR": h2y, "MC_OUT": out, "MC_TRAJ_OUT": traj})
    print(f"[{k}/{len(cells)}] {name}  running...", flush=True)
    subprocess.run([sys.executable, os.path.join(PROJECT, "run_mc_grid_parallel.py")],
                   env=env, check=True)

print(f"\nNG '{SCENARIO}' done in {(time.time()-t0)/60:.1f} min -> {CELLS_DIR}")
