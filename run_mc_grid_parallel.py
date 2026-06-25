#!/usr/bin/env python
"""
Parallel launcher for the deterministic price-grid generator (monte_carlo.py
with MC_GRID set). Splits the flat grid index range into N_PROCS contiguous
chunks, runs each as a separate subprocess (own AMPL instance, 1 Gurobi thread),
then concatenates the chunk CSVs into one per-cell generator table.

The structural cell (scrap regime / H2 year / grid EF scenario) is taken from the
environment (MC_SCRAP_REGIME, MC_H2YEAR, MC_GRID_EF) and passed through.

Env:
  MC_GRID        "nH2,nCCS,nNG"  (required; e.g. 25,12,8 -> 2400 pts)
  MC_PROCS       parallel processes (default 12)
  MC_OUT         final CSV (default mc_results.csv)
  MC_SCRAP_REGIME {starved, low, modest, optimistic} (default modest)
  MC_H2YEAR      H2-DRI start year (default 2030)
  MC_GRID_EF     {bau, moderate_re, aggressive_re} (default moderate_re)
"""
import os, sys, subprocess, csv, time

PROJECT  = os.path.dirname(os.path.abspath(__file__))
GRID     = os.environ["MC_GRID"]                       # required
N_PROCS  = int(os.environ.get("MC_PROCS", "12"))
FINAL    = os.path.join(PROJECT, os.environ.get("MC_OUT", "mc_results.csv"))
TRAJ     = os.path.join(PROJECT, os.environ["MC_TRAJ_OUT"]) if os.environ.get("MC_TRAJ_OUT") else ""
SCRIPT   = os.path.join(PROJECT, "monte_carlo.py")

nh2, nccs, nng = (int(x) for x in GRID.split(","))
TOTAL = nh2 * nccs * nng

# contiguous ceiling-division chunks (tile the full grid exactly, no overlap)
sz = (TOTAL + N_PROCS - 1) // N_PROCS
chunks = [(i * sz, min((i + 1) * sz, TOTAL)) for i in range(N_PROCS)]
chunks = [c for c in chunks if c[0] < c[1]]

cell = f"scrap={os.environ.get('MC_SCRAP_REGIME','modest')} H2yr={os.environ.get('MC_H2YEAR','2030')} grid_ef={os.environ.get('MC_GRID_EF','moderate_re')}"
print(f"Grid generator | {cell} | {nh2}x{nccs}x{nng} = {TOTAL} pts | {len(chunks)} procs")
t0 = time.time()

def run_chunk(p, a, b, out, traj_out=""):
    """Spawn one monte_carlo.py subprocess for the slice [a:b]; return exit code."""
    env = os.environ.copy()
    env.update({"MC_GRID": GRID, "MC_GRID_START": str(a), "MC_GRID_END": str(b),
                "MC_THREADS": "1", "MC_OUT": out,
                "MC_SCRAP_REGIME": os.environ.get("MC_SCRAP_REGIME", "modest"),
                "MC_H2YEAR": os.environ.get("MC_H2YEAR", "2030"),
                "MC_GRID_EF": os.environ.get("MC_GRID_EF", "moderate_re")})
    if traj_out:
        env["MC_TRAJ_OUT"] = traj_out
    stderr_path = os.path.join(PROJECT, f"mc_grid_err_{p}.txt")
    with open(stderr_path, "w") as ef:
        proc = subprocess.Popen([sys.executable, SCRIPT], env=env,
                                stdout=subprocess.DEVNULL, stderr=ef)
        proc.wait()
    rc = proc.returncode
    if rc != 0 or not os.path.exists(out):
        with open(stderr_path) as ef:
            tail = ef.read()[-800:]
        print(f"  chunk {p} failed (rc={rc}):\n{tail}")
    if os.path.exists(stderr_path):
        os.remove(stderr_path)
    return rc

procs, chunk_csvs, chunk_trajs = [], [], []
for p, (a, b) in enumerate(chunks):
    out = os.path.join(PROJECT, f"mc_grid_chunk_{p}.csv")
    tout = os.path.join(PROJECT, f"mc_grid_traj_{p}.csv") if TRAJ else ""
    chunk_csvs.append(out)
    chunk_trajs.append(tout)
    proc_env = os.environ.copy()
    proc_env.update({"MC_GRID": GRID, "MC_GRID_START": str(a), "MC_GRID_END": str(b),
                     "MC_THREADS": "1", "MC_OUT": out,
                     "MC_SCRAP_REGIME": os.environ.get("MC_SCRAP_REGIME", "modest"),
                     "MC_H2YEAR": os.environ.get("MC_H2YEAR", "2030"),
                     "MC_GRID_EF": os.environ.get("MC_GRID_EF", "moderate_re")})
    if TRAJ:
        proc_env["MC_TRAJ_OUT"] = tout
    stderr_path = os.path.join(PROJECT, f"mc_grid_err_{p}.txt")
    ef = open(stderr_path, "w")
    proc = subprocess.Popen([sys.executable, SCRIPT], env=proc_env,
                            stdout=subprocess.DEVNULL, stderr=ef)
    procs.append((p, proc, chunks[p], out, tout, ef, stderr_path))

# Per-chunk wall-clock budget: 200 draws × 120s solver TimeLimit = 24 000s
# theoretical max, but healthy solves finish in ~1s each so 300s is generous.
CHUNK_TIMEOUT = int(os.environ.get("MC_CHUNK_TIMEOUT", "300"))

for p, proc, (a, b), out, tout, ef, stderr_path in procs:
    try:
        proc.wait(timeout=CHUNK_TIMEOUT)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        print(f"  chunk {p} timed out after {CHUNK_TIMEOUT}s, retrying…")
    ef.close()
    if proc.returncode != 0 or not os.path.exists(out):
        with open(stderr_path) as sf:
            tail = sf.read()[-800:]
        if tail:
            print(f"  chunk {p} failed (rc={proc.returncode}):\n{tail}")
        run_chunk(p, a, b, out, tout)
    if os.path.exists(stderr_path):
        os.remove(stderr_path)

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

# merge the year-by-year trajectory chunks (line-concat; prices are the key,
# so no draw renumbering is needed)
if TRAJ:
    n_traj, header_done = 0, False
    with open(TRAJ, "w", newline="") as tout_fh:
        for tp in chunk_trajs:
            if not os.path.exists(tp):
                print(f"  WARNING: traj {tp} missing"); continue
            with open(tp, newline="") as tfh:
                lines = tfh.readlines()
            if lines:
                if not header_done:
                    tout_fh.write(lines[0]); header_done = True
                tout_fh.writelines(lines[1:]); n_traj += len(lines) - 1
            os.remove(tp)
    print(f"  trajectory: {n_traj} rows -> {TRAJ}")
