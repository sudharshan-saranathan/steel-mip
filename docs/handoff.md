# Handoff

- **Current task:** set up and launch the **overnight Monte Carlo**: all 14,107 feasible factorial runs × N shared draws (N still to decide, see below), at roughly 75 solves/s on 12 workers. Fetch first: session `01GVt5c2…` also pushes to `fix-wave-01`.
- **Decide first (ask the user):** how many draws. The current 50 are random and uneven (coal $300 appears in 20 % of draws, not 33 %; θ_CCS=0 in 10 %, not 20 %), which shifts every cell the same way. I recommended a balanced design: replace `sample_draws` with Latin-hypercube-style draws in which every level appears equally, in multiples of 15. 45 draws = 635k solves (about 2.5–3 h), 60 = 846k (about 3–4 h), 75 = 1.06M (about 4–5 h). P50 is stable from about 30 draws; P90 and CVaR95 still move 3–5 USD/t.
- **Next step:**
  1. Change `monte_carlo/run_montecarlo.py`:
     - Map the `midhigh`/`midlow` coal and NG levels (`CCOAL_FILE`/`NG_FILE` only know abundant/scarce; the files are listed in `axes.py`).
     - Append each solve to a CSV and add `--resume`.
     - Write `mc_solves.parquet` instead of the xlsx.
  2. Update the readers (`violin/run_violin.py` and the four `uncertainty/*/run_*.py`), and remove the bracketing-regime filter in `run_violin.py`'s `load_full_structural`.
  3. Smoke-test a few cells, check that `--resume` works, then launch with the lease-renew loop plus automatic `--resume` retries (`run_yearly.sh` pattern: start AMPL every 15 min).
  4. Afterwards, regenerate every Monte Carlo-derived figure (`uncertainty-risk`, `cost-violin-*`, possibly `regret-ladder`) and flag any paper numbers that go stale.
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
