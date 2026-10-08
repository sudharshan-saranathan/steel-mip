# Handoff

- **Current task:** set up and launch the **overnight Monte Carlo**: all 14,107 feasible factorial runs × 50 shared draws (seed 20260824) = 705,350 solves, about 2.5–3 h at roughly 75/s on 12 workers.
- **Next step:**
  1. Commit and push the pending radar-figure changes (`notebooks/plots.ipynb`, `figs/feasibility-bias*.png`; fetch first, because session `01GVt5c2…` also pushes to `fix-wave-01`; PNGs need `git add -f`).
  2. Change `monte_carlo/run_montecarlo.py`:
     - Map the `midhigh`/`midlow` coal and NG levels (`CCOAL_FILE`/`NG_FILE` only know abundant/scarce; the files are listed in `axes.py`).
     - Append each solve to a CSV and add `--resume`.
     - Write `mc_solves.parquet` instead of the xlsx.
  3. Update the readers (`violin/run_violin.py` and the four `uncertainty/*/run_*.py`), and remove the bracketing-regime filter in `run_violin.py`'s `load_full_structural`.
  4. Smoke-test a few cells, check that `--resume` works, then launch with the lease-renew loop plus automatic `--resume` retries (`run_yearly.sh` pattern: start AMPL every 15 min).
  5. Afterwards, regenerate every Monte Carlo-derived figure (`uncertainty-risk`, `cost-violin-*`, possibly `regret-ladder`) and flag any paper numbers that go stale.
- **Open decisions (the user's):**
  - Which violin figure goes in the paper: `cost-violin-ef1.8`/`ef2.0` (ramp rows) or `cost-violin-by-ef` (EF rows).
  - Delete the old `cost-violin.png` and the accidental `cost-violin-ef1.6.png`? Cell 22 loops over every EF in `violin.xlsx`.
  - Keep or delete the alternates (`feasibility-bias-rank`, `import-dependence`, `import-tradeoff-linear`); rounded regret bars; borders on the risk (d) boxes.
- **Paper (`tex/steel-v3.tex`, untracked; the user edits the text, Claude only flags stale numbers):**
  - Factorial table rewritten in chat (symbol, units, levels, description; 36,864 scenarios per target, 110,592 runs).
  - B = 10 Mt/yr confirmed infeasible: the most favourable scenario is infeasible, so all others are too.
  - Build-rate citation: Lok Sabha Unstarred Q. 1426 (29.07.2025). The record is +20.8 Mt in FY2024-25; the 2013–25 average is 8.9 Mt/yr.
  - Still stale: violin caption at line 335, `% CHECK` at line 358, `\includegraphics` names.
- **Flags:**
  - Feasible: 14,107 of 110,592 runs, or 11,537 of 36,864 unique combinations (the sets nest by EF).
  - No nbconvert: render by `exec()`-ing the cells after registering JetBrains Mono from `~/.local/share/fonts`.
  - `yearly.parquet`, `violin.xlsx` and `mc_solves.*` stay local. `structural/axes/ng_high.mod` stays untracked on purpose.
  - Audit reviewer-proofing plan still open (`docs/audit/HANDOFF.md`).
- Full history: `.remember/recent.md`, `.remember/archive.md`.
