# Handoff — H2 capacity-ramp modes (and current model state)

_Version-controlled working note (the `~/.claude` memory is machine-local and does NOT
travel between machines — this file does, via git). Branch: **`mip-v2`**._

## Current model state (mip-v2)
- Capacity-expansion rebuild; **pure LP** (CCS phase-in switches + all integer vars removed).
- Emissions target is an **upper-bound CAP** (carbon budget; optimiser may over-achieve), not a ±band.
- Green-H2 = explicit sunk capacity: electrolysers (`cap_h2elec`) + dedicated behind-the-meter
  renewables (`cap_h2re`); H2 price reduced to residual `h2_opex`. H2 cost axis = `h2_capex_mult`
  (token `H2CAPXVAL`).
- `summary.md` is the methodology-grade reference (keep in sync with model changes).
- **Prior MC / frontier / regret CSVs are STALE** (emissions cap + green-H2 restructure + axis
  repoint) — re-run before using numbers.

## ⭐ H2 RAMP MODES (added 2026-06-27, committed + pushed)
New `h2_ramp_mode` governs how fast green-H2 **electrolyser capacity** may expand. Three
mutually-exclusive limiters; **model stays pure LP**; **default 0 = original model unchanged**.
Selected via `let` (template tokens NOT wired yet — see TODO).

- **mode 0 (default):** original FIXED ADDITIVE slab on H2 *flow* (`H2_growth_limit`,
  `parameters.mod`). Unchanged behaviour.
- **mode 1:** CONSTANT-COMPOUND ceiling — installed capacity grows ≤ `h2_peak_rate` (25%/yr)
  off last year's capacity.
- **mode 2 (the designed one):** RISING-BASELINE + GAUSSIAN-TRANSITION ceiling on the annual
  capacity **addition** (the *allowed expansion*), off a FIXED reference `h2_ref_cap`=10 MT —
  **not** compounding:
  ```
  build[t]  ≤  h2_ref_cap · ( base(t) + surge_amp · kernel(t) )
  base(t)   = 0.05 + (0.10-0.05)·(t-2025)/25        # 5%→10%, capital efficiency
  kernel(t) = exp( -(t - h2_peak_year)² / (2·σ²) ), σ=5
  surge_amp = h2_peak_rate - base(h2_peak_year)     # pins TOTAL peak rate to 25%
  h2_peak_year = ng_h2_start_year + 5 (coupled in parameters.mod; overridable)
  ```
  Integrates to a smooth **S-step** in installed capacity. Constants fixed by design
  (peak 0.25, σ=5, ref 10 MT, base 0.05→0.10); only `h2_ramp_mode` / `h2_peak_year` settable.
  Inactive limiters relaxed by `H2_BIGM`=1e10 (robust to warm-process `let`).

**Terminology (use consistently):** *allowed expansion* = the ceiling (constraint RHS);
*chosen build* = `build_h2elec` (what the optimiser actually adds, ≤ allowed);
*installed capacity* = `cap_h2elec` (cumulative chosen stock).

### Findings (ET1.75, H2-2030)
- Chosen build sits **below** allowed expansion: utilisation (installed÷allowed) ≈ 3% (2035) →
  39% (2040) → 53% (2045) → 58% (2050). The optimiser skips the early surge (capex high early +
  emissions cap not yet binding), builds more later.
- **Ramp shape only bites near the feasibility frontier.** Under loose targets all three modes
  converge to ~the same economically-chosen (near-linear) path; the Gaussian only shows in the
  *solution* when the target is tight enough to force building into the surge window (verified:
  2035 chosen cap 0.43 → 0.85 → 2.44 as ET 1.75 → 1.65 → 1.58).
- **Mode 2 makes late starts MORE feasible:** ET1.6 / start-2040 is INFEASIBLE under additive &
  compound but FEASIBLE under mode 2 (fixed-reference additions aren't bottlenecked by a small
  late base). This **softens the timing/irreversibility thesis** on the feasibility dimension —
  ⚠️ decide whether that physics is wanted.

### Commits (pushed to origin/mip-v2)
- `88a2ea5` — **forward-ref bugfix**: the green-H2 split (51721b7) declared
  `build_h2elec`/`cap_h2elec`/`build_h2re`/`cap_h2re` *after* `capex_cost_def`/`fixopex_cost_def`
  reference them. AMPL CLI tolerates it but **amplpy raises** → every Python driver run of the
  green-H2 model would have failed at parse. Fixed by moving the declarations up.
- `94bc63c` — the ramp-mode feature (`definitions.mod` params, `v_capacity.mod` ceiling,
  `parameters.mod` flow-slab toggle + peak-year coupling).
- `661433f` — `summary.md` consistency fix (u_lockin.mod deleted, not retained).

## TODO (next session)
1. **Decide mode 1 (constant-compound) keep or drop** — the user reframed the ramp as
   linear+transition; compound was an earlier exploratory idea and may be an unwanted foil.
2. **Wire drivers:** add template tokens (e.g. `H2RAMPVAL`, `H2PEAKVAL`) in `template.mod` and
   `monte_carlo*.py` / `regret*.py` / sweep scripts so modes + peak-year run at scale.
3. **Document:** `summary.md` §8.2 still describes only the old additive flow ramp — add modes 1/2.
4. **Confirm** the mode-2 "late starts feasible" physics is intended before wiring it into regret.

## How to test (amplpy harness — scratchpad scripts did not persist)
```python
# load the model up to (not incl.) main.mod's own `solve;`, then control solving
with open("main.mod") as fh: M = fh.read().split("\nsolve;")[0]
a = AMPL(); a.eval('option solver gurobi; option gurobi_options "outlev=0 mipgap=0.002";')
a.eval(M)                                   # strict default handler parses fine post-bugfix
a.eval("let avg_emi:=1.75; let ng_h2_start_year:=2030; let h2_peak_year:=2035; let h2_ramp_mode:=2;")
a.solve()
# read cap_h2elec[y].value() (installed) and build_h2elec[y].value() (chosen build)
```

## Bigger picture (paper spine) — see machine-local memory for full detail
Paper pivoted to a **stochastic-regret** framework (commit central optimum trajectory → sample
price/capex PATHS → builds sunk → Δcost & Δemissions). Engine: `regret_roll.py` (rolling 5-yr
course-correction) + `regret_stoch.py` (stochastic prototype). Thesis: **"timing &
irreversibility, not cost."** The H2 ramp work above feeds how H2 deployment speed enters that story.
