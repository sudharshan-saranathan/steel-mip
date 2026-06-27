# Steel Decarbonisation MIP — Model Summary

> **Maintenance note:** This file is a living description of the current model on
> the `mip-v2` (capex-opex-framework) branch. When the formulation, parameters,
> module list, or tooling change, update the relevant section here in the same
> commit. Section headers are kept stable so diffs stay readable.
>
> **Last synced to code:** 2026-06-27 (capex-opex-framework framework, commit `3026a11`).

---

## 1. What the model is

A **multi-period mixed-integer linear program** (effectively a near-pure LP — the
only binaries, `z` and the old CCS phase-in switches, are dead/retired) that finds
the **least-cost decarbonisation pathway for a national steel sector from 2025 to
2050**, subject to a cumulative-average CO₂-intensity target.

- **Horizon:** `set T := 2025..2050` (26 annual periods).
- **Objective (`main.mod`):** minimise the discounted sum of total system cost,
  `sum_t discount_factor[t] * total_cost[t]`, where
  `discount_factor[t] = 1/(1+r)^(ord(t)-1)` and `r = real_discount_rate = 0.06`.
- **Capex is overnight and fully sunk** — no residual-life salvage/resale credit.
  This is deliberate (the "irreversibility thesis"): industrial capital has no
  resale market, and a salvage credit would make terminal-year builds nearly free
  and end-load all investment.
- **Solver:** Gurobi (`option solver gurobi`), `mipgap=0.002`. The model is
  linearized, so `nonconvex=2` is no longer needed.
- **Decision drivers:** how much steel to make on each production route each year,
  how much route/CCS **capacity to build** each year, how much CO₂ to capture, and
  the resulting energy, material, cost and emission flows.

The crude-steel demand it must meet is exogenous and fixed:
`dem[t] = base_demand * (1+growth_rate)^(ord(t)-1)` with `base_demand = 152.2 Mt`
(2025) and `growth_rate = 0.05`. `meet_demand` pins `total_steel[t] = dem[t]`,
which is what makes the route-share products linear.

## 2. Production routes

Five competing steelmaking routes share the fixed annual demand:

| Route | Capacity var | Output var | 2025 seed (`cap0_*`) | Asset life |
|---|---|---|---|---|
| **BF-BOF** (integrated blast-furnace / basic-oxygen) | `cap_bof` | `steel_bof` | 90.0 Mt | 25 yr |
| **Coal-DRI → EAF** | `cap_cdri` | `coaldri_output` | 63.54 Mt | 20 yr |
| **NG-DRI → EAF** | `cap_ngdri` | `ngdri_output` | 11.61 Mt | 15 yr |
| **H₂-DRI → EAF** (future entrant) | `cap_h2dri` | `h2dri_output` | 0 | 15 yr |
| **Scrap-EAF** | `cap_scrap` | `steel_scrap_eaf` | 33.5 Mt | 10 yr |

The three DRI route outputs are on a **crude-steel-equivalent basis**
(`0.9 * steel_eaf`, i.e. divided by `1 - n7_phi_eaf`), because each DRI route
carries its share of the shared DRI-EAF. The 2025 seeds are converted accordingly.

Process chains are modelled module-by-module (each `s.t.` ties an input/output flow
linearly to a route's activity level):

- **BF-BOF chain:** coke oven (`a_coke`) → sinter (`b_sinter`) → BF pellets
  (`c_pellets_bf`) → blast furnace (`d_blast_furnace`) → BOF (`e_bof`). The BF
  carries time-varying coke/PCI/biochar/H₂ injection rates (2025→2050 ramps).
- **DRI chains:** dedicated pellet plants (`f/g/h_pellets_*`) feed coal-/NG-/H₂-DRI
  reactors (`i_dri_coal`, `j_dri_ng`, `k_dri_h2`), all of which feed a shared
  **DRI-EAF** (`l_eaf_dri`).
- **Scrap-EAF** (`m_scrap_eaf`) is a standalone melting route.
- `dri_route_split` (in `k_dri_h2`) is the key linearization: the coal/NG/H₂ route
  *outputs* are the decision variables and must sum to DRI-EAF steel — replacing the
  former bilinear share×total products. Realized fractions `f_cdri`, `f_ngdri` are
  reconstructed post-solve for reporting only (`yreport.mod`).

`steel_balance`: `steel_eaf + steel_bof + steel_scrap_eaf = total_steel`.

## 3. Capacity-expansion framework (the defining feature of this branch)

`modules/v_capacity.mod` **supersedes the old `u_lockin.mod`** (retired). Instead of
charging a per-tonne LCOE capital term on production, the model now tracks a real
**capacity stock**:

- **Builds** `build_X[t]` add capacity in year `t`. A build contributes to capacity
  from year `j` until `j + life_X - 1`, then retires automatically (`cap_def_*`).
- **Legacy (2025 incumbent) fleet** `legacy_X[t]` is a non-increasing stock under a
  **linearly declining ceiling that hits 0 in 2050** (`legacy_ceil_*`,
  `legacy_noninc_*`) — a gentle ~4%/yr phase-out the optimizer may *beat* (retire
  faster under decarbonisation pressure) but never slow. 2025 is pinned to the seed
  (`legacy_init_*`).
- **Production ≤ installed capacity** (`cap_lim_*`). Idle capacity still pays fixed
  opex — that is what discourages build-then-strand, replacing the old forced
  production floor.
- **Scrap supply-chain capacity** (`scrapchain_cap`): collection + sensor-sorting +
  copper/tramp purification yards. 2025 capacity is pinned free to that year's scrap
  throughput; growth above baseline pays sunk overnight capex
  (`ocapex_scrapchain ≈ $100/t`). Monotone (strandable, never un-built).

**Cost structure (`capex_cost_def`, `fixopex_cost_def`):**

- `capex_cost[t]` = **overnight capex booked on this year's builds**
  (`ocapex_X * build_X`), summed over routes + scrap chain.
- `fixopex_cost[t]` = **fixed O&M (labour + maintenance) on installed capacity**
  (`fopex_X * cap_X`), on a crude-steel basis.
- A **`sunk` toggle** switches the whole model between two worlds:
  - `sunk=1` (default, real model): capex on *builds*, fixed opex on *capacity* →
    capital is committed once built; idling/stranding does not recover it.
  - `sunk=0` (counterfactual): capex + fixed opex charged on *production* (old LCOE
    style) → building-then-idling is free, so tech can be switched costlessly. This
    is the ablation that isolates the sunk-capital effect.

**Cost parameter derivation (`parameters.mod`):** the per-route annualised capital
charge `acapex_X` is bundled from the existing `n*_capex` levelized figures; the
capital recovery factor `crf_X = r(1+r)^L / ((1+r)^L − 1)` converts it to an
**overnight** figure `ocapex_X = acapex_X / crf_X`. DRI routes divide by
`(1 - n7_phi_eaf)` to align plant/pellet/shared-EAF capex with the crude-steel-equiv
output basis.

## 4. Carbon capture (CCS)

`modules/q_carbon_capture.mod` + the CCS retrofit-capacity block in `v_capacity.mod`.
CCS is retrofittable on the three primary-CO₂ routes: **BF-BOF, Coal-DRI, NG-DRI**
(no CCS on H₂-DRI or scrap-EAF). Captured amounts `ccs_bf/ccs_cdri/ccs_ngdri` are the
decision variables (linear — no bilinears). Two distinct limits apply:

1. **Physical capturable CO₂** per route (`co2_capturable_*`, ≈ route Scope-1): a
   route can capture at most `n10_ccs_eta * fc_max` (= 0.85 × 0.9) of its own base.
2. **Sector-wide deployment ceiling** (`ccs_sector_ceiling`) — usually the binding
   one: `sum_X ccs_X ≤ ccs_avail[t] * sum_X co2_capturable_X`, where `ccs_avail`
   ramps linearly **0 before 2027 → 0.50 by 2050** (infrastructure/logistics
   maturity). No capture before 2027 (`no_ccs_*` in `t_additional_constraints`).

CCS retrofit follows the **same overnight-capex + fixed-O&M + variable-opex
structure** as routes (`build_ccs_X`, `ccs_cap_X`, `life_ccs = 15 yr`). Cost
(`cost_ccs_def` in `r_cost.mod`) =
overnight capex on builds + fixed O&M on capacity + **energy** (`power_ccs *
ng_cost_power`, grid-responsive — closes the old uncosted-CCS-power gap) + solvent
make-up (`ccs_vopex_solvent`).

**Stream-specific multipliers** scale cost and capture energy by CO₂ concentration:
NG-DRI cheapest (`ccs_mult_ngdri = 0.5`, near-pure separated CO₂, 200 kWh/tCO₂),
BF-BOF baseline (`1.0`, 800 kWh), Coal-DRI dearest (`1.2`, dilute kiln gas, 850 kWh).

## 5. Energy and emissions accounting

- **Power balance** (`p_power_balance`): every process's electricity draw, minus
  on-site generation (CDQ, sinter cooler, BF top-pressure recovery turbine, waste-heat
  recovery), nets to `grid_power_in`.
- **Waste-heat recovery** (`o_waste_heat`): BF-BOF off-gases (COG/BFG/BOFG) and EAF
  gases feed a WHR system whose penetration `n9_whr` ramps 5%→30% over 2025–2050.
- **Emissions** (`s_emissions`):
  - **Scope 1** (direct) — from coking coal, PCI, DRI coal, NG, limestone/flux,
    electrodes, per route and in total (`scope1_emissions`).
  - **Scope 2** (indirect) — `n9_grid_ef[t] * grid_power_in[t]`, where the grid
    emission factor declines `0.000886 → 0.0003 tCO₂/kWh` over the horizon.
  - **Total** = Scope 1 + Scope 2 − `total_ccs` (captured CO₂).
- **Policy target** (`t_additional_constraints`): a **cumulative average
  CO₂-intensity** band, `avg_emi ± eps`, applied to lifetime totals
  (`sum_t total_emissions` vs `avg_emi * sum_t total_steel`). `avg_emi` default 1.75
  tCO₂/tCS (overridable per run / Monte-Carlo cell).

## 6. Key dynamics, ramps and availability limits

- **Production ramp** (`*_prod_up/down`): a **fixed additive annual slab**, max YoY
  change = `ramp_frac * the route's pinned-2025 production` (not compounding).
  `ramp_frac` default 0.15 (tunable 0.15–0.20). Applies to the four incumbent routes;
  H₂-DRI is exempt (governed by H₂ availability) but has a 0.85 down-floor.
- **H₂ availability** (`definitions.mod`): hydrogen input is zero before
  `ng_h2_start_year`, capped at `H2_cap` (1.5 Mt) in the start year, then grows by an
  additive slab `≤ ramp_frac * H2_cap` per year (not CAGR).
- **NG availability** (`ng_bound`): `ngdri_ng_in ≤ n5_ng_cap[t]`, a year-by-year cap
  with normal/BAU/shock profiles (active profile set in `definitions.mod`; shock case
  is currently live, with a 2035–2040 dip).
- **Scrap availability** (`scrap_bound`): `scrap_eaf_scrap_in ≤ n8_scrap_limit[t]`,
  a base cap (35 Mt in 2025) growing at `n8_scrap_rate` (default 0.04, regime-overridable).

## 7. Cost and price parameters (selected, `parameters.mod` / `definitions.mod`)

- Coking coal `$184/t`, grid power `$0.07/kWh` (sell-back `$0.03`), scrap `$350/t`,
  pellet/lump/fine ore, lime, electrodes, etc.
- **Natural gas** `n5_cost_NG` `$/MMBtu` (default 10; shocked ×1.5 in some cases).
- **Hydrogen** `ng_cost_h2` declines `$4500/t (2025) → ng_cost_h2_end` (1000–1500)
  over the horizon; `ng_h2_start_year` controls when H₂-DRI may begin (e.g. 2030).
- **CCS** `n10_ccs_cost` `$125 → $75 /tCO₂`, split into capex share
  (`ccs_capex_share = 0.8`) and fixed O&M.
- **Carbon tax** default 0 (a lever, not active in the base case).
- Variable other-opex `$10/tCS` on production; labour `$20` + maintenance `$15` now
  enter as **fixed** opex on capacity (not per-tonne).

## 8. File / module map

```
main.mod                 # driver: sets, include order, objective, solve, report
template.mod             # parameterized clone of main.mod for sweeps (token subst.)
definitions.mod          # demand, technical params with bounds, H2/NG/scrap caps
variables.mod            # all decision variables (flows, capacity, cost, emissions)
parameters.mod           # cost params + capacity-expansion (capex/opex) framework
yreport.mod              # post-solve console report (route mix, CCS, $/t, tCO2/t)

modules/
  a_coke .. e_bof        # BF-BOF process chain
  f/g/h_pellets_*        # DRI pellet plants
  i_dri_coal,j_dri_ng,k_dri_h2   # DRI reactors (+ dri_route_split linearization)
  l_eaf_dri, m_scrap_eaf # EAF routes
  n_steel_balance        # route outputs = total steel
  o_waste_heat, p_power_balance  # energy balances
  q_carbon_capture       # CCS physical + deployment limits
  v_capacity             # capacity stock, builds, legacy retirement, CCS capacity
  r_cost                 # per-process + total cost equations
  s_emissions            # Scope 1 / Scope 2 / net emissions
  t_additional_constraints  # init shares, demand, avg-emissions band, ramps
  u_lockin.mod           # RETIRED (kept for reference; not included by main.mod)
```

## 9. Scenario and analysis tooling (Python / shell)

The `.mod` model is wrapped by a scenario + uncertainty layer:

- **`scenarios/`** — drop-in `let` overrides included after `parameters.mod`:
  NG availability (`ng_avail_{normal,shock,optimistic}`), scrap regime
  (`scrap_{starved,low,modest,optimistic}`), grid EF
  (`grid_ef_{bau,moderate_re,aggressive_re}`).
- **`run_scripts/{linux,macos,windows}/`** — parameter-sweep drivers
  (scenario × H₂-end × H₂-year × CCS × scrap). See `run_scripts/README.md`.
- **`monte_carlo.py` / `monte_carlo_2d.py`** — Latin-Hypercube and dense 2-D grid
  uncertainty studies over market prices (NG, H₂-end, CCS-end), one structural cell
  per run.
- **`mc_frontier.py`** — feasibility frontier across the 48 structural cells
  (scrap × H₂-year × grid-EF); feasibility is price-independent.
- **`run_all_cells.py`** — production driver: price-grid table per feasible cell →
  `cells/`, `cells_traj/`.
- **Regret engines** — the research core:
  - `regret.py` — static regret matrix (commit for assumed world W, realise world G).
  - `regret_roll.py` — rolling 5-year course-correction (MPC-style, prior builds sunk).
  - `regret_stoch.py` — stochastic-regret prototype (perturbed price worlds + rolling
    recourse against a hard cumulative-emissions target).
- **`capex_sweep.py`** — new-capacity investment sweep per feasible cell → box-plot.
- **`plot_*.py`** — figures (frontier, pathways, emissions trajectories, regret
  heatmaps, scrap regimes, split-violins, transition cost, H₂ timing).
- Outputs are organised under `runs/<RUN>/{plots,csv}` (and `cells/`, `cells_traj/`).

## 10. Notable modelling choices / gotchas

- **Everything is linearized.** Bilinear share×total and capture-fraction×base
  products were removed; route *outputs* and captured *amounts* are the decisions,
  and realized fractions are reconstructed only for reporting.
- **Sunk capital is the central thesis** — see the `sunk` toggle (§3) for the
  counterfactual that isolates its effect.
- **DRI capacities live on the 0.9×crude-steel-equiv basis** — watch the
  `1/(1-n7_phi_eaf)` factors when reading capacity, fixed-opex, or emission terms.
- **`u_lockin.mod` is dead code** — the capacity stock in `v_capacity.mod` now
  provides asset-life lock-in economically.
- The only remaining integer var (`z`) and the former CCS phase-in binaries are
  unused/retired, so the solved problem is effectively an LP.
