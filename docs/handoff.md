# Handoff

- **Current task:** the feasibility rerun on branch **`fix-wave-ccs`** is running detached. It covers the full 110,592-cell factorial, launched at about 17:21 IST on 2026-10-08, at about 38 cells/s, with an ETA around 18:10. The script is `scratchpad/run_feas.sh` (old session), which keeps the AMPL lease renewed and retries up to 5 times with `--resume`; the log is `scratchpad/feas_run.log`. It is needed because on this branch θ_CCS also drives steam use per tCO₂, and steam use affects Scope 1 emissions and therefore feasibility (`docs/audit/HANDOFF.md` §6d item 8).
- **Next step:**
  1. Check that `structural/feasibility_and_synergy/feasibility_drivers/data/raw_matrix.csv` has 110,592 rows and that `yearly.parquet` was written. If the run died, rerun `run_feasibilitydrivers.py -j 12 --resume` after renewing the AMPL lease.
  2. Compare the feasible shares against the old ones: 0.3 / 6.6 / 31.3 % at targets 1.6 / 1.8 / 2.0, or 14,107 feasible runs. The old `raw_matrix.csv` is in git (`fix-wave-01`); the old per-year data was saved as `data/yearly_fixwave01.csv`.
  3. Then the Monte Carlo (and probably the regret analysis) needs rerunning on this branch's feasible set, which also lowers the H₂ RE capex end point (695 → 400) and the biochar price (520 → 300).
- **Done on `fix-wave-01` (commit `f2f87fa`, not pushed):**
  - Monte Carlo at CCS anchor 100 vs 75: all 315,660 solved; the draws are identical, so the comparison is paired.
  - LCOP rose by +1.4 / +1.5 / +1.5 $/t at ef 1.6 / 1.8 / 2.0. New medians are 510.7 / 496.7 / 482.2. The sampling SE on the median is about ±4.
  - Cumulative captured CO₂ fell by 2 / 8 / 14 % at ef 1.6 / 1.8 / 2.0. Shares and feasibility are essentially unchanged.
  - Variance drivers of LCOP: scrap price 45 %, coal price 35 %, everything else 7 % or less; θ_tech (H₂ learning) contributes 1.7 %.
  - The readers and notebook cells 20/22/24 were **not** rerun on the new run.
- **Flags:**
  - **`f2f87fa` committed `tex/`, `monte_carlo/data/*.parquet` and `yearly.parquet`**, which the earlier handoff said should stay local. Ask the user whether to amend that commit before pushing. The large CSVs were left untracked.
  - Local `fix-wave-01` has diverged from `origin/fix-wave-01`: the remote has 4 commits not present locally (up to `691c17a`, from another session). Merge or rebase before pushing.
  - Still open from before:
    - Which violin figure goes in the paper.
    - Whether to delete the alternate and old figures.
    - Stale lines in `tex/steel-v3.tex` (around lines 160, 335 and 358).
    - The CCS anchor of 100 is above the cited range of 45–92, so the paper needs a justification (the user writes it).
    - Plot issues in `uncertainty-risk` panels (b) and (d).
- Full history: `.remember/recent.md`, `.remember/archive.md`.
