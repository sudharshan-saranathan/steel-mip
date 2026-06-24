#!/usr/bin/env python
"""
Parallel launcher for the deterministic price-grid generator (monte_carlo.py
with MC_GRID set). Splits the flat grid index range into N_PROCS contiguous
chunks, runs each as a separate subprocess (own AMPL instance, 1 Gurobi thread),
then concatenates the chunk CSVs into one per-cell generator table.

The structural cell (NG scenario / scrap regime / H2 year) is taken from the
environment (MC_SCENARIO, MC_SCRAP_REGIME, MC_H2YEAR) and passed through.

Env:
  MC_GRID        "nH2,nCCS,nNG"  (required; e.g. 25,12,8 -> 2400 pts)
  MC_PROCS       parallel processes (default 12)
  MC_OUT         final CSV (default mc_results.csv)
  plus MC_SCENARIO / MC_SCRAP_REGIME / MC_H2YEAR for the cell.
"""
import os, sys, subprocess, csv, time

PROJECT  = os.path.dirname(os.path.abspath(__file__))
GRID     = os.environ["MC_GRID"]                       # required
N_PROCS  = int(os.environ.get("MC_PROCS", "12"))
FINAL    = os.path.join(PROJECT, os.environ.get("MC_OUT", "mc_results.csv"))
SCRIPT   = os.path.join(PROJECT, "monte_carlo.py")

nh2, nccs, nng = (int(x) for x in GRID.split(","))
TOTAL = nh2 * nccs * nng

# contiguous ceiling-division chunks (tile the full grid exactly, no overlap)
sz = (TOTAL + N_PROCS - 1) // N_PROCS
chunks = [(i * sz, min((i + 1) * sz, TOTAL)) for i in range(N_PROCS)]
chunks = [c for c in chunks if c[0] < c[1]]

cell = f"NG={os.environ.get('MC_SCENARIO','normal')} " \
       f"scrap={os.environ.get('MC_SCRAP_REGIME','modest')} " \
       f"H2yr={os.environ.get('MC_H2YEAR','2030')}"
print(f"Grid generator | {cell} | {nh2}x{nccs}x{nng} = {TOTAL} pts | {len(chunks)} procs")
t0 = time.time()

procs, chunk_csvs = [], []
for p, (a, b) in enumerate(chunks):
    out = os.path.join(PROJECT, f"mc_grid_chunk_{p}.csv")
    chunk_csvs.append(out)
    env = os.environ.copy()
    env.update({"MC_GRID": GRID, "MC_GRID_START": str(a), "MC_GRID_END": str(b),
                "MC_THREADS": "1", "MC_OUT": out})
    proc = subprocess.Popen([sys.executable, SCRIPT], env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    procs.append((p, proc))

for p, proc in procs:
    proc.wait()

elapsed = time.time() - t0
rows, fieldnames = [], None
for path in chunk_csvs:
    if not os.path.exists(path):
        print(f"  WARNING: {path} missing"); continue
    with open(path, newline="") as fh:
        r = csv.DictReader(fh)
        if fieldnames is None: fieldnames = r.fieldnames
        rows.extend(r)
    os.remove(path)

# renumber draw column for a clean concatenated table
for i, row in enumerate(rows):
    if "draw" in row: row["draw"] = i

with open(FINAL, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames); w.writeheader(); w.writerows(rows)

n_ok = sum(1 for r in rows if r["status"] == "solved")
print(f"Done in {elapsed:.0f}s. Merged {len(rows)} rows (ok={n_ok}) -> {FINAL}")
