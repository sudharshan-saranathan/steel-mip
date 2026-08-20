# Unified Section A design matrix

Replaces the six per-study Section A drivers with **one axis registry, one
runner, one output table**. Each former study becomes a *slice* of that table
rather than a separate script with its own backdrop.

- `scenarios/_matrix/axes.py` — axis registry (single source of truth)
- `scenarios/_matrix/report.mod` — post-solve accounting (computes only)
- `scenarios/_matrix/run_matrix.py` — parallel runner
- `scenarios/_matrix/to_parquet.py` — CSV → parquet, stamps provenance metadata
- output: `scenarios/_matrix/results/matrix.{csv,parquet}` (gitignored)

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

## Axes — 46,656 cells

**The selection criterion is that the design sweeps only what policy
controls** — levers a ministry can decide through investment or regulation.
Everything else is either a constant (background condition) or belongs to
Section B, the Monte Carlo over things nobody controls. This is what took the
design from an earlier 524,880 cells down to 46,656: the earlier version swept
everything that *could* vary, this one sweeps what the paper can make a policy
claim about.

| Axis | Levels | Values | Policy it represents |
|---|---|---|---|
| `ccoal` | 2 | abundant (293.6 Mt by 2050), scarce (91.1 Mt) | Import policy, domestic supply |
| `ng` | 2 | policy (32.2 Mm³ by 2050), bau (10.7 Mm³) | Gas allocation to steel |
| `h2_start` | 4 | 2030, 2035, 2040, 2045 | Green-H₂ debut year |
| `scrap_rate` | 6 | 0.00 … 0.10 /yr, step 0.02 | Collection infrastructure, ELV rules |
| `grid_ef` | 9 | 0.00005 … 0.00085 tCO₂/kWh, step 0.0001 | Power-sector decarbonisation |
| `ramp` | 3 | low 4 / medium 6 / high 8 M(t-H₂/yr) | Electrolyser deployment rate |
| `build_cap` | 3 | tight 20 / mid 30 / loose 40 Mt/yr | Shared annual build budget |
| `legacy` | 2 | run-life, mandated-phaseout | Retirement of the 2025 fleet |
| **`avg_emi`** | **3** | **1.6, 1.8, 2.0 tCO₂/t** | **The constraint being tested — not a lever** |

2 × 2 × 4 × 6 × 9 × 3 × 3 × 2 = **15,552 lever combinations**, each solved
against all three targets = **46,656 cells**.

### Held fixed (`CONSTANTS` in `axes.py`)

`theta_tech` = 0.5 and `theta_ccs` = 0.5 are technology learning rates set by
global science, not Indian policy, so they are constants here and sampled in
Section B. `whr_ccs_integration` = 1 is a plant engineering choice.

Both thetas were **measured across their full range before being demoted**:
`theta_ccs` moves LCOP by 3.5 $/t with *zero* effect on feasibility, and
`whr_mode` by 1.3 $/t — against a 36.58 $/t hydrogen-delay penalty. That is a
sensitivity result, not an assumption.

### How the level counts were chosen

Rebalanced against **measured** response, not per-study convention.

| Axis | Old levels | Action |
|---|---|---|
| `h2_start` | 4 / 6 | → **4**. Two studies used 5-yr spacing, one 3-yr, for no documented reason. 5-yr chosen (user decision, 2026-08-17). |
| `scrap_rate` | 11 | → **6**. Response near-linear; interpolation error ~1–2 $/t. |
| `grid_ef` | 18 | → **9**. The output is one *threshold* per cell, not 18 levels; 0.0001 spacing still brackets it. |
| `avg_emi` | 9 | → **3**. The three targets the original studies used. It is the constraint, and three named targets is the right granularity for that role. |
| `ramp` | 3 | unchanged — `medium` is the baseline every other study uses, so dropping it would break the regression oracle. |
| `theta_ccs`, `whr_mode` | 5, 2 | **removed** — not policy levers (see above). |
| `build_cap`, `legacy` | — | **added**. `build_cap` was previously collinear with `ramp` (ratio 2.5), so any effect attributed to "H2 ramp" was partly conventional capacity. |

Two rules constrain any future edit to `axes.py`:

1. **Every level set must contain its baseline value** (see `BASELINE` in
   `axes.py`), so the original studies remain reproducible slices.
2. `grid_ef` is offset by 0.00005 so the 0.0001 grid lands *on* 0.00045, the
   value implied by `theta_grid = 0.5` (`core/definitions.mod:168-169`).

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

Verified on the solved table: `extrapolated` is exactly
`grid_ef_target ∉ {0.00035, 0.00045, 0.00055}` — a pure function of the grid
level. That leaves **10,202 of 30,371 feasible cells (33.6%)** usable for $/t.
Feasibility uses all 46,656.

## Output schema

One row per cell, solved or not. Infeasible rows keep their coordinates and
carry whatever numerics the solver left — filter on `solve_result == 'solved'`
before using any metric.

**Infeasibility can arrive by two paths, and both count.** Most cells return
`solve_result = infeasible` from Gurobi. Some may instead return
`ERROR: AMPLException: presolve: constraint steel_balance[...] cannot hold` —
AMPL's presolve proving infeasibility arithmetically before the solver runs.
These are **genuine infeasibilities, not run failures**: count them as
infeasible. Dropping them would bias the feasibility frontier toward looking
more permissive exactly where it is tightest. Use
`solved = (solve_result == 'solved')` and treat everything else as infeasible,
rather than filtering `ERROR` rows out. (The current design produces **zero**
ERROR rows; the rule stands for future edits that tighten the corner.)

Columns: the 9 axis coordinates, then `solve_result`, `objective`,
`theta_grid`, `extrapolated`, then the metrics (union of the six studies'
reports).

Two additions beyond the union:

- **`grid_ef_2050`, `tariff_2050`** — read back from the solved model, so each
  row *proves* the grid axis propagated (see the invariant below).
- **`ccoal_bind_yrs`, `ng_bind_yrs`** — years in which each availability cap
  binds. These are the companions to `import_bill`, which **inverts**: scarce
  regimes post *lower* import bills while costing *more* per tonne, because a
  binding cap forbids importing. A low bill with a high bind-year count is
  forced scarcity, not a good outcome. `import_bill` itself is unchanged so old
  results stay reproducible.

Per-year output (the abatement decomposition, 26 rows/run) is **deliberately
not** in this table, and not merely for size reasons. The matrix answers a
feasibility question — one bit per cell plus endpoint metrics — and that
question has no time dimension. Year-wise trends answer a different question:
how abatement accrues over time. That needs a handful of scenarios, not the
cross product, so it stays a separate small run (the old study was 7 scenarios
× 26 years = 182 rows) and should not be scaled with the matrix.

## The one invariant

**One AMPL instance per run.** `n9_grid_ef_end` is declared
`param … default <expr involving theta_grid>` (`core/definitions.mod:168`), and
AMPL evaluates a `default` expression once, on first read, then freezes it.
Reusing an instance across cells would pin grid EF at the first cell's value
while every later row still records the *requested* target — a table that looks
plausible and is wrong. `grid_ef_2050` is the tripwire: if it ever goes constant
while `grid_ef_target` varies, this has been violated.

Checked on the current table: 9 distinct `grid_ef_2050` against 9 targets, max
|`grid_ef_2050` − `grid_ef_target`| = 1.0e-16. Clean.

Related: `Threads=1`. Measured, Gurobi gains ~9% from a 10× thread budget on
this LP — it solves by dual simplex (~1,400 iterations, presolved to
1,058 × 950), which does not parallelize. Parallelism belongs across cells.

## Running

```bash
python3 scenarios/_matrix/axes.py                     # print the design + size
python3 scenarios/_matrix/run_matrix.py --verify      # baseline cell only
python3 scenarios/_matrix/run_matrix.py --smoke       # 20 cells
python3 scenarios/_matrix/run_matrix.py -j 12         # full matrix
python3 scenarios/_matrix/run_matrix.py -j 12 --resume  # continue a partial run
python3 scenarios/_matrix/to_parquet.py               # then convert for analysis
```

Throughput is machine-dependent: **35.7 cells/s (21.8 min) at `-j 12` on a
12-core M4 Pro**, against 48–59 cells/s at the same `-j` on a 6-physical-core
box. On Apple silicon the efficiency cores drag the average, so `-j 8` may beat
`-j 12` — untested.

Requires `amplpy` with the `base` and `gurobi` AMPL modules, plus `pandas` and
`pyarrow` for the parquet step.

## Verification

- Row count must equal the product of the axis levels exactly: **46,656**.
- `--verify` solves the baseline coordinate (`BASELINE` in `axes.py`:
  abundant / policy / 2030 / scrap 0.06 / grid 0.00045 / medium ramp / tight
  build / run-life / 1.8) and must give **lcop 516.74 $/t** with
  `avg_emis` 1.800.
- Reference run (model_commit `be8751d`): **30,371 solved, 16,285 infeasible,
  0 errors**; 10,202 calibrated.
- The six per-study drivers are **retained** as the regression oracle. Do not
  delete them until each study's slice has been checked against its own CSV.

## Known open items

- ~~**Per-year table**~~ — closed 2026-08-17: out of scope for a feasibility
  question; stays a separate small run (see Output schema above).
- ~~**Adaptive bisection** on `grid_ef`~~ — declined 2026-08-17. The fixed
  9-level grid resolves the frontier to 0.0001 tCO2/kWh, which is enough;
  keeping the design a clean factorial is worth more than the extra precision.
- **Peak-annual-build readback** missing from `report.mod`. Without it, whether
  `cap_add_total` stops binding above 30 Mt/yr is unevidenced — a small delta
  is not proof of slack.
- **`build_h2dri` has no per-year build cap** (`v_capacity.mod:150`), unlike
  the four conventional routes. This asymmetry limits the strongest reading of
  the build-budget result.
