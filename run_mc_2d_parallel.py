#!/usr/bin/env python
"""
Parallel launcher for monte_carlo_2d.py.

Splits the H2-cost axis into N_PROCS chunks, runs each as a separate
subprocess (each with its own AMPL instance), then merges and sorts
the output into a single CSV.

Each subprocess uses MC2D_THREADS Gurobi threads so that
N_PROCS * MC2D_THREADS <= physical core count.
"""
import os, sys, subprocess, csv, time, glob

PROJECT    = os.path.dirname(os.path.abspath(__file__))
N_H2       = int(os.environ.get("MC2D_NH2",   "100"))
N_CCS      = int(os.environ.get("MC2D_NCCS",  "100"))
N_PROCS    = int(os.environ.get("MC2D_PROCS", "12"))
THREADS    = int(os.environ.get("MC2D_THREADS", "1"))
SCENARIO   = os.environ.get("MC_SCENARIO", "normal")
FINAL_CSV  = os.path.join(PROJECT, os.environ.get("MC_OUT", "mc_2d_results.csv"))
SCRIPT     = os.path.join(PROJECT, "monte_carlo_2d.py")

# split H2 axis into CONTIGUOUS chunks (ceiling division).
# Round-robin is wrong here: each subprocess receives a [h2_start, h2_end)
# RANGE, so non-contiguous index lists would overlap and re-solve rows.
chunk_size = (N_H2 + N_PROCS - 1) // N_PROCS
chunks = [list(range(i * chunk_size, min((i + 1) * chunk_size, N_H2)))
          for i in range(N_PROCS)]
chunks = [c for c in chunks if c]  # drop empty chunks when N_PROCS > N_H2

chunk_csvs = []
procs      = []

print(f"Launching {N_PROCS} processes  |  {N_H2}×{N_CCS} grid  |  {THREADS} Gurobi threads each")
t0 = time.time()

for p, chunk in enumerate(chunks):
    if not chunk:
        continue
    h2_start = chunk[0]
    h2_end   = chunk[-1] + 1
    out_csv  = os.path.join(PROJECT, f"mc_2d_chunk_{p}.csv")
    chunk_csvs.append(out_csv)

    env = os.environ.copy()
    env.update({
        "MC2D_NH2":       str(N_H2),
        "MC2D_NCCS":      str(N_CCS),
        "MC2D_H2_START":  str(h2_start),
        "MC2D_H2_END":    str(h2_end),
        "MC2D_THREADS":   str(THREADS),
        "MC_SCENARIO":    SCENARIO,
        "MC_OUT":         out_csv,
    })
    proc = subprocess.Popen([sys.executable, SCRIPT], env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    procs.append((p, proc))
    print(f"  chunk {p}: H2 rows {h2_start}–{h2_end-1}  (pid {proc.pid})")

print("All processes launched. Waiting...")
for p, proc in procs:
    proc.wait()
    print(f"  chunk {p} done (exit {proc.returncode})")

elapsed = time.time() - t0
print(f"\nAll done in {elapsed:.0f}s. Merging...")

# merge + sort by i_h2, i_ccs
rows = []
fieldnames = None
for csv_path in chunk_csvs:
    if not os.path.exists(csv_path):
        print(f"  WARNING: {csv_path} missing — chunk may have failed")
        continue
    with open(csv_path, newline="") as fh:
        reader = csv.DictReader(fh)
        if fieldnames is None:
            fieldnames = reader.fieldnames
        rows.extend(reader)
    os.remove(csv_path)

rows.sort(key=lambda r: (int(r["i_h2"]), int(r["i_ccs"])))

with open(FINAL_CSV, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

n_ok    = sum(1 for r in rows if r["status"] == "solved")
n_draws = N_H2 * N_CCS
print(f"Merged {len(rows)} rows  (ok={n_ok})  -> {FINAL_CSV}")

# Wall-clock per draw, and speed-up vs the measured single-solve cost
# (SEQ_PER_DRAW, default 1.1s with lock-in on; override via MC2D_SEQ_S).
seq_per_draw = float(os.environ.get("MC2D_SEQ_S", "1.1"))
speedup      = (n_draws * seq_per_draw) / elapsed if elapsed else 0.0
eff          = speedup / N_PROCS * 100.0
print(f"Avg {elapsed / n_draws:.2f}s/draw  |  "
      f"Speed-up vs sequential: {speedup:.1f}×  "
      f"(parallel efficiency: {eff:.0f}%)")
