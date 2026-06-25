#!/usr/bin/env python
"""
Production driver: generate the price-grid table for every FEASIBLE structural
cell (scrap regime × H2 start year), writing one CSV per cell into cells/.

NG availability is fixed at "normal" (not a structural axis). Cells already
present in cells/ with the expected row count are SKIPPED -> resumable.

Env:
  MC_GRID   grid spec (default 25,12,8 = 2400 pts/cell)
"""
import os, csv, subprocess, sys, time

PROJECT   = os.path.dirname(os.path.abspath(__file__))
GRID      = os.environ.get("MC_GRID", "25,12,8")
CELLS_DIR = os.path.join(PROJECT, "cells")
TRAJ_DIR  = os.path.join(PROJECT, "cells_traj")
os.makedirs(CELLS_DIR, exist_ok=True)
os.makedirs(TRAJ_DIR, exist_ok=True)

nh2, nccs, nng = (int(x) for x in GRID.split(","))
EXPECTED      = nh2 * nccs * nng
EXPECTED_TRAJ = EXPECTED * 26   # 26 years (2025-2050) per draw

with open(os.path.join(PROJECT, "mc_frontier.csv")) as fh:
    cells = [r for r in csv.DictReader(fh) if r["status"] == "solved"]
cells.sort(key=lambda r: (r["scrap_regime"], int(r["h2_start_year"])))

if not cells:
    sys.exit("No feasible cells found in mc_frontier.csv")

print(f"{len(cells)} feasible cells | grid {GRID} = {EXPECTED} pts/cell "
      f"(~{len(cells)*170/60:.0f} min)")

def rowcount(path):
    if not os.path.exists(path): return -1
    with open(path) as fh: return sum(1 for _ in fh) - 1

t0 = time.time()
for k, c in enumerate(cells, 1):
    scrap, h2y = c["scrap_regime"], c["h2_start_year"]
    name = f"{scrap}_{h2y}.csv"
    out  = os.path.join(CELLS_DIR, name)
    traj = os.path.join(TRAJ_DIR, name)
    if rowcount(out) == EXPECTED and rowcount(traj) == EXPECTED_TRAJ:
        print(f"[{k}/{len(cells)}] {name}  SKIP (already complete)"); continue
    env = os.environ.copy()
    env.update({"MC_GRID": GRID, "MC_SCRAP_REGIME": scrap,
                "MC_H2YEAR": h2y, "MC_OUT": out, "MC_TRAJ_OUT": traj})
    print(f"[{k}/{len(cells)}] {name}  running...", flush=True)
    subprocess.run([sys.executable, os.path.join(PROJECT, "run_mc_grid_parallel.py")],
                   env=env, check=True)

print(f"\nDone in {(time.time()-t0)/60:.1f} min -> {CELLS_DIR}")
