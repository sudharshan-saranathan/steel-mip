# Handoff — model state & paper results (branch `mip-v2`)

_Version-controlled working note (the `~/.claude` memory is machine-local and does NOT
travel between machines — this file does, via git). Branch: **`mip-v2`**._

_Last updated 2026-06-29. Supersedes the earlier H2-ramp-modes handoff (mode scheme and
H2 supply chain were re-architected since)._

## Current model state (mip-v2)
- Capacity-expansion framework; **pure LP** (no integer vars). Emissions target = cumulative
  **average-intensity CAP** `avg_emi` (`t_additional_constraints.mod`); optimiser may
  over-achieve. Overridable via template `AVGEMIVAL` / `MC_AVG_EMI`.
- Green-H2 = explicit sunk capacity: electrolysers (`cap_h2elec`) + dedicated behind-the-meter
  renewables (`cap_h2re`). H2 cost-uncertainty axis = `h2_capex_mult` (`H2CAPXVAL`).

### H2 ramp modes — RE-ARCHITECTED this session (value-switch, default **mode 2**)
Same formalism in every mode; only the **ceiling VALUE** switches. `h2elec_growth` /
`h2elec_first` (`v_capacity.mod`):
```
cap_h2elec[t] − cap_h2elec[t−1] ≤
   if   mode = 0 then H2_BIGM                         # NO LIMIT (counterfactual)
   else if mode = 1 then ramp_frac · H2_cap           # LINEAR slab
   else h2_ref_cap · ( base(t) + surge·kernel(t) )    # GAUSSIAN (realistic)
```
- **mode 0 = no limits**: ALL ceilings → ∞ (electrolyser AND the four `cap_add_X` route slabs),
  AND the utilisation-floor coefficient → 0. The unphysical counterfactual that isolates "how
  much do the constraints cost". `param h2_ramp_mode default 2`.
- **mode 1 = linear**: additive slab `ramp_frac·H2_cap`. With the tiny `H2_cap` (1.5 Mt) it is
  ~10× too slow → **infeasible at EF 1.6**; re-reference to `h2_ref_cap` before using (parked).
- **mode 2 = gaussian (default)**: peak coupled `h2_peak_year = ng_h2_start_year + 5`.
  Constants `h2_peak_rate 0.25`, σ `2`, base 0→0.05; `h2_ref_cap` = the dial below.
- The four conventional `cap_add_X` slabs are now mode-aware (free in mode 0, slab in 1/2).
  Rates: BF 0.12, coal-DRI 0.20, NG-DRI 0.10, **scrap 0.448 (~15 Mt/yr, raised from 0.15)**.

### `h2_ref_cap` — the H2-led ↔ CCS-led DIAL (currently **10 Mt**, undecided)
Peak electrolyser addition = `h2_peak_rate · h2_ref_cap`. This one number sets the story:

| `h2_ref_cap` | peak add | H2-DRI[2050] | dominant route | EF floor (fav / mod) |
|---|---|---|---|---|
| 10 Mt | 2.5 Mt-H2/yr (~35 GW/yr) | ~115–128 Mt | **hydrogen** | ~1.30 / — |
| 4 Mt  | 1.0 Mt-H2/yr (~14 GW/yr) | ~55 Mt | balanced | ~1.48 / ~1.64 |
| 1.5 Mt| 0.375 Mt-H2/yr (~5 GW/yr)| ~20 Mt | **CCS-on-BF** | ~1.64 / — |
> **OPEN DECISION:** final `h2_ref_cap`. 10 Mt is implausibly fast for one country's steel;
> 4 Mt is the defensible middle; 1.5 Mt makes H2 a bit-player. (committed at 10.)

### Other model changes this session
- **BF-BOF H2 co-injection REMOVED** (`n2_h2_hm_50` 0.013→0 → `bf_h2_in`≡0); lost reduction made
  up by coke (`n2_coke_hm_50` 0.44→0.48, ~3 t-coke/t-H2 equiv). `bf_h2_in` stripped from
  `h2elec_cover`/`h2re_cover`/green capex+opex; BF H2 cost term dropped. **H2-DRI is the SOLE
  hydrogen consumer.** Fixes the artefact where BF capacity was throttled by the scarce early
  electrolyser ramp (BF cliffing 90→45 Mt in 2026).
- **Electrolyser debut gate** (`h2elec_predebut`/`h2re_predebut`): `cap_h2elec = cap_h2re = 0`
  for `t < ng_h2_start_year`. No supply before a consumer → ramp starts cleanly, no idle pre-build.
- **`h2_peak_year` coupling fix** (`template.mod`): re-let `:= ng_h2_start_year + 5` AFTER the
  `H2YEARVAL` override (was stranded at the default-start value → delayed-H2 pre-built idle
  electrolysers that switched on in one jump).
- **Utilisation floor** `prod_X ≥ util_min_X·cap_X` (t>2025): BF 0.85 / coal 0.75 / NG 0.70 /
  H2 0.70 / scrap 0.60. **Mode-gated OFF in mode 0** (coefficient → 0).
- **Coking-coal availability lever** (new): `ccoal_cap` + `coking_coal_bound{t>first(T)}` (caps
  imported coke-making coal only; PCI + thermal DRI coal uncapped; base year exempt). Scenarios
  `ccoal_{scarce,normal,abundant}`; NG `ng_avail_{scarce,abundant}` added.
- **Pruned dead formalisms**: old compound H2 mode, `cost_carbontax`, per-route `scope2_*`,
  `Mccs_*`/`cap_ub_*`, `n9_u`, `h2elec_seed`, and the H2 FLOW slab (`H2_growth_cap/limit`).
- **Legacy retirement** stays the linear-to-2050 ceiling. A gradual-retirement (max-rate/window)
  experiment was tried and REVERTED — infeasible via the BF–H2 coupling, now removed, so BF
  retires gradually on its own. Not needed.

### MC harness (`monte_carlo.py`)
- `MC_LET` passthrough (arbitrary pre-solve `let`s). Mode now ALWAYS injected; `MC_RAMP_MODE`
  default **2**. Trajectory CSV now includes per-route `cap_*`. Parallel runner
  `run_mc_grid_parallel.py` — use ~6 procs (10 concurrent Gurobi starts hit license-hostid
  contention → first-pass chunk failures + serial retry).

## Paper results structure (decided this session)
- **Subsection A — DETERMINISTIC structural sensitivity (no MC).** Feasibility & cost vs each
  structural lever: ramp **mode 0 vs 2**, scrap regime, grid-EF, NG availability, coking
  availability, H2 start year. Per axis: feasibility floor + system cost vs EF (instant solves).
  `mode 0` no-limits = the counterfactual baseline (answers "is the pathway an artefact of the
  caps?"). Central prices = LO/HI midpoints (NG 15, h2_capex_mult 1.05, CCS 75).
- **Subsection B — fix-then-forward REGRET (MC here).** Commit ONE assumed world → solve once for
  the optimal trajectory (builds sunk) → evaluate the frozen plan forward under sampled
  price/capex/scenario paths → Δcost / Δemissions. `regret_roll.py` / `regret_stoch.py`.

## ⭐ Key findings (this session)
- **Mode 0 vs 2 = "cost of the deployment constraints".** Unconstrained the optimiser reaches
  EF ≈ 1.0 by 2050; the realistic ramp holds it at ≈ 1.4. The caps — not economics — bound 2050
  intensity.
- **The mode contrast flips the decarbonisation MECHANISM:** mode 0 = coal-DRI→H2-DRI substitution
  (H2 dominant); mode 2 = CCS-retrofit BF-BOF displacing coal-DRI (H2 ramp-capped). Confirmed via
  CCS trajectory (~200–400 Mt-CO2/yr captured by 2050).
- **`h2_ref_cap` decides H2-led vs CCS-led** (table above). At the EF floor, BOTH H2-DRI AND CCS
  are maxed (CCS at its `ccs_avail` = 50%-of-capturable ceiling) — joint exhaustion sets the floor.
- **In the FAVOURABLE corner, SCRAP (not H2) is the swing factor**: optimistic scrap gives ~137 Mt
  clean scrap-EAF (vs ~85 moderate), +52 Mt clean baseload → lowers the floor (1.64→1.48 at ref 4).
- **Tech envelope (ET-invariant deployment ceiling)** = `legacy_ceiling + build_rate·min(life,t−2025)`.
  Build term plateaus at `cap_add_frac·cap0·life`; declining legacy then drags the ceiling DOWN →
  envelopes **peak at year 2025+life then fall** (scrap ~2035, NG ~2040, coal ~2045; BF rises to
  2050 since life 25 = horizon). Shows which routes are build-bound (NG, H2), resource-bound
  (scrap), or have headroom (BF when H2 is plentiful).
- **The 2035 kink in H2-DRI output**: electrolyser BUILD is ramp-paced (Gaussian peaks at 2035) and
  runs a year ahead of H2-DRI OUTPUT, which is budget-paced (cheaper to surge H2 in 2036) →
  transient idle electrolysers in 2035, output flattens then jumps. Real inter-temporal feature.

## TODO / open decisions
1. **Pick final `h2_ref_cap`** (10 / 4 / 1.5) — the H2-led-vs-CCS-led dial. Top decision.
2. **`ccs_avail`** is 50%-of-capturable by 2050 → with H2 capped, the other binding ceiling.
   Decide whether to bump it (reach EF 1.6 in the moderate regime) or report the floor.
3. **Build subsection A** in full (deterministic sweep over all structural axes × EF, both modes).
4. **Build subsection B** (regret: fix trajectory, MC forward).
5. **Mode 1 (linear)**: re-reference its slab to `h2_ref_cap` so it's feasible, or drop it.
6. Optional: electrolyser utilisation floor to remove the transient idle (the 2035 kink).
7. `paper_results_design.md` (pulled from remote, **not yet read** — reconcile with A/B above).
8. Prior MC/frontier/regret CSVs are **STALE** (H2 supply rework). Re-run before using numbers.

## How to test (deterministic, amplpy)
```python
tpl = open("template.mod").read()
for k,v in {"NGVAL":"15.0","H2CAPXVAL":"1.05","H2YEARVAL":"2030","CCSVAL":"75.0",
            "AVGEMIVAL":"1.6","RAMPVAL":"0.15","SCRAPREGIMEFILE":"scenarios/scrap_modest.mod",
            "NGAVAILFILE":"scenarios/ng_avail_normal.mod",
            "GRIDEFFILE":"scenarios/grid_ef_moderate_re.mod"}.items():
    tpl = tpl.replace(k, v)
tpl = "\n".join(l for l in tpl.splitlines() if "yreport.mod" not in l)   # drop verbose report
a = AMPL(); a.eval('option solver gurobi; option gurobi_options "outlev=0";'); a.eval(tpl)
a.eval("let h2_ramp_mode:=2; let avg_emi:=1.6;"); a.solve()
```
- Plot figures regenerate on demand; `figs/` is **gitignored** (not tracked).
- amplpy raises on infeasible solves — wrap `solve()` in try/except or check `solve_result`.
- Determine the regime via the scenario files: scrap `{starved,low,modest,optimistic}`,
  NG `{scarce,normal,abundant}`, coking `{scarce,normal,abundant}`, grid `{bau,moderate_re,
  aggressive_re}`, H2 start year via `H2YEARVAL`.

## Bigger picture (paper spine)
Stochastic-regret framework (commit central optimum trajectory → sample price/capex PATHS →
builds sunk → Δcost & Δemissions). Thesis: **"timing & irreversibility, not cost."** The H2
deployment-speed work (modes, `h2_ref_cap`, debut gate) feeds how H2 enters that story.
