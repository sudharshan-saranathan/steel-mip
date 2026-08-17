# Unified Section A design matrix

Replaces the six per-study Section A drivers with **one axis registry, one
runner, one output table**. Each former study becomes a *slice* of that table
rather than a separate script with its own backdrop.

- `scenarios/_matrix/axes.py` — axis registry (single source of truth)
- `scenarios/_matrix/report.mod` — post-solve accounting (computes only)
- `scenarios/_matrix/run_matrix.py` — parallel runner
- output: `scenarios/_matrix/results/matrix.csv` (gitignored)

## Why

The six studies were not mutually comparable. Each pinned the axes it did not
sweep to its own values, and those values disagreed — `ss/scrap` ran
`n9_grid_ef_end := 0.0005` while every other study ran `theta_grid := 0.5`
→ 0.00045, and five of six ran with coking coal effectively unbounded
(`ccoal_cap` default 1e12) without saying so. Under one matrix every
non-swept parameter takes one declared value, and the differences that used
to hide in per-study backdrops become axes you can slice on.

`ss/abatement` is the proof this was always the right shape: it had no axes of
its own at all. Its six "named scenarios" are points in this space — EF1.6/EF1.8
are `avg_emi`, S4/S8 are scrap 0.04/0.08, and RL/RH are byte-identical to
`ramp_low`/`ramp_high`.

## Axes — 524,880 cells

| Axis | Levels | Values |
|---|---|---|
| `ccoal` | 3 | abundant, scarce, **unbounded** (core default) |
| `ng` | 3 | policy, bau, **baseline** (core's own series) |
| `h2_start` | 4 | 2030, 2035, 2040, 2045 |
| `avg_emi` | 9 | 1.60 … 2.00, step 0.05 |
| `ramp` | 3 | low, medium, high |
| `scrap_rate` | 6 | 0.00 … 0.10, step 0.02 |
| `grid_ef` | 9 | 0.00005 … 0.00085, step 0.0001 |
| `theta_ccs` | 5 | 0, 0.25, 0.5, 0.75, 1 |
| `whr_mode` | 2 | integrated, boiler-only |

### How the level counts were chosen

Rebalanced against **measured** response, not per-study convention. Swing in
LCOP across each axis's sampled range, others held at baseline:

| Axis | Old levels | $/t per step | Action |
|---|---|---|---|
| `avg_emi` | 3 | **20.0** | 3 → **9**. Coarsest axis, and the one that decides feasibility — every scrap infeasibility and most of hydrogen-delay's sit at 1.6. |
| `h2_start` | 4 / 6 | 11.9 | → **4**. Two studies used 5-yr spacing, one used 3-yr, for no documented reason. 5-yr chosen (user decision, 2026-08-17). |
| `scrap_rate` | 11 | 9.2 | 11 → **6**. Response near-linear (mean 2nd difference 1.2 $/t vs ~9 $/t first differences); interpolation error ~1–2 $/t. |
| `theta_ccs` | 5 | 6.7 | unchanged. |
| `ramp` | 3 | 4.0 | unchanged at 3 — weakest axis, but `medium` is the baseline every other study uses and dropping it would break the regression oracle. |
| `grid_ef` | 18 | — | 18 → **9**. The study's output is one *threshold* per cell, not 18 levels; 0.0001 spacing still brackets it. A bisection would need ~5 adaptive solves, at the cost of making the runner non-factorial — deferred. |

Two rules constrain any future edit to `axes.py`:

1. **Every level set must contain its baseline value** (see `BASELINE` in
   `axes.py`), so the original studies remain reproducible slices.
2. `grid_ef` is offset by 0.00005 so the 0.0001 grid lands *on* 0.00045, the
   value implied by `theta_grid = 0.5`.

### Grid EF band and extrapolation

The band is 0.00005–0.00085 tCO₂/kWh = **50–850 gCO₂/kWh**, against a 2025
anchor of 886 g. It is deliberately wider than the calibrated window: the
slow/fast anchors (`grid_ef_end_slow` 600 g, `grid_ef_end_fast` 300 g) span
only θ ∈ [0,1], but measured frontier thresholds reach both ends of the wider
band, so narrowing to 300–600 g would censor most cells.

Outside 300–600 g, θ is extrapolated — and because grid EF and the industrial
tariff are coupled outcomes of the *same* θ, the electricity price is
extrapolated with it, out to $0.025–0.110/kWh against a fitted $0.055–0.085.
Every row carries `theta_grid` and an `extrapolated` flag so this is
queryable rather than hidden. **Filter on `extrapolated == 0` for any claim
about cost.**

## Output schema

One row per cell, solved or not. Infeasible rows keep their coordinates and
carry whatever numerics the solver left — filter on `solve_result == 'solved'`
before using any metric.

**Infeasibility arrives by two paths, and both count.** Most cells return
`solve_result = infeasible` from Gurobi. A minority return
`ERROR: AMPLException: presolve: constraint steel_balance[...] cannot hold` —
AMPL's presolve proving infeasibility arithmetically before the solver runs.
These are concentrated in the tightest corner (`scarce` coal + `bau` gas +
late H2 debut), where no route combination can physically meet demand. They
are **genuine infeasibilities, not run failures**: count them as infeasible.
Dropping them biases the feasibility frontier toward looking more permissive
exactly where it is tightest. Use
`solved = (solve_result == 'solved')` and treat everything else as infeasible,
rather than filtering `ERROR` rows out. Columns: the 9 axis coordinates, then
`solve_result`, `objective`, `theta_grid`, `extrapolated`, then the metrics
(union of the six studies' reports).

Two additions beyond the union:

- **`grid_ef_2050`, `tariff_2050`** — read back from the solved model, so each
  row *proves* the grid axis propagated (see the invariant below).
- **`ccoal_bind_yrs`, `ng_bind_yrs`** — years in which each availability cap
  binds. These are the companions to `import_bill`, which **inverts**: scarce
  regimes post *lower* import bills (LoCoal-LoNG 288 B$ vs HiCoal-HiNG 363 B$)
  while costing *more* per tonne (568.5 vs 559.7 $/t), because a binding cap
  forbids importing. A low bill with a high bind-year count is forced
  scarcity, not a good outcome. `import_bill` itself is unchanged so old
  results stay reproducible.

Per-year output (the abatement decomposition, 26 rows/run) is **deliberately
not** in this table, and not merely for size reasons (524,880 × 26 = 13.6M
rows). The matrix answers a feasibility question — one bit per cell plus
endpoint metrics — and that question has no time dimension. Year-wise trends
answer a different question: how abatement accrues over time. That needs a
handful of scenarios, not the cross product, so it stays a separate small run
(the old study was 7 scenarios x 26 years = 182 rows) and should not be scaled
with the matrix.

## The one invariant

**One AMPL instance per run.** `n9_grid_ef_end` is declared
`param … default <expr involving theta_grid>` (`core/definitions.mod:168`), and
AMPL evaluates a `default` expression once, on first read, then freezes it.
Reusing an instance across cells would pin grid EF at the first cell's value
while every later row still records the *requested* target — a table that looks
plausible and is wrong. `grid_ef_2050` is the tripwire: if it ever goes constant
while `grid_ef_target` varies, this has been violated.

Related: `Threads=1`. Measured, Gurobi gains ~9% from a 10× thread budget on
this LP — it solves by dual simplex (~1,400 iterations, presolved to
1,058 × 950), which does not parallelize. Parallelism belongs across cells.

## Running

```bash
python3 scenarios/_matrix/axes.py                    # print the design + size
python3 scenarios/_matrix/run_matrix.py --verify     # baseline cell only
python3 scenarios/_matrix/run_matrix.py --smoke      # 20 cells
python3 scenarios/_matrix/run_matrix.py -j 6         # full matrix, ~4.2 h
python3 scenarios/_matrix/run_matrix.py -j 6 --resume # continue a partial run
```

Measured throughput: **34.7 cells/s on 6 workers** (6 physical cores).

## Verification

- Row count must equal the product of the axis levels exactly: **524,880**.
- The import-dependence anchor reproduces **bit-identically**: cell
  (abundant, policy, 2030, 1.8, medium, 0.06, 0.00045, 0.5, integrated) gives
  objective `1972188578542.0989` vs the stored `1972188578542.098877`
  (relative delta 0.0), `import_bill` 362.8 B$, `lcop` 559.66 — all matching
  the old `impdep_summary.csv` row.
- The six per-study drivers are **retained** as the regression oracle. Do not
  delete them until each study's slice has been checked against its own CSV.

## Known open items

- ~~**Per-year table**~~ — closed 2026-08-17: out of scope for a feasibility
  question; stays a separate small run (see Output schema above).
- ~~**Adaptive bisection** on `grid_ef`~~ — declined 2026-08-17. The fixed
  9-level grid resolves the frontier to 0.0001 tCO2/kWh, which is enough;
  keeping the design a clean factorial is worth more than the extra precision.
- **Solved fraction will drop sharply** versus the old studies: `avg_emi` now
  samples 1.65/1.70/1.75, i.e. *into* the infeasible region. That is the design
  working — the boundary is the result — but the table will be mostly
  infeasible, and slices must filter accordingly.
