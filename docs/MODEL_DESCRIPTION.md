# Model description — India steel decarbonisation capacity-expansion model

Written as a self-contained reference. Every structural statement below was
read from the AMPL source (`core/`) rather than recalled; file and constraint
names are given so any claim can be checked. Where a value is a modelling
assumption rather than an observation, it is labelled as such.

---

## 1. What kind of model this is

A **partial-equilibrium, bottom-up capacity-expansion linear programme** for
the Indian iron and steel sector.

- **Partial equilibrium**: only the steel sector is modelled. Steel demand,
  fuel prices, electricity tariffs and the grid emission factor are exogenous
  inputs, not outcomes. There are no economy-wide feedbacks — if steel
  decarbonisation raises steel prices, demand does not fall in response.
- **Bottom-up**: production is represented as explicit process routes with
  fixed engineering coefficients (tonnes of coke per tonne of hot metal, kWh
  per tonne of hydrogen), not as production functions with substitution
  elasticities. Substitution happens by *switching between routes*, subject to
  capacity and timing constraints — not by sliding continuously along a curve.
- **Capacity expansion**: installed capacity is a state variable tracked by
  vintage. Plants are built, operate for a finite life, and retire. What can
  be produced in a given year depends on what was built in previous years.
- **Linear programme**: continuous variables, linear constraints, single
  objective. One nonlinear constraint exists in the source
  (`emission_monotonic`) and is dropped in every production run.

The consequence that matters analytically: because routes are discrete objects
that exist only after a stated debut year and can only be built at bounded
rates, **the model can return "infeasible" — no combination of available
routes meets the emissions cap.** That outcome is the primary result the study
reports. A model built on smooth substitution cannot produce it, because some
input mix is always attainable at some price.

## 2. Time, scale and objective

- **Horizon**: 2025–2050 inclusive, annual time steps (`set T := 2025..2050`,
  `core/model.mod`).
- **Objective** (`core/model.mod`): minimise the discounted sum of total
  annual system cost,
  `minimize obj: sum{t in T} discount_factor[t] * total_cost[t]`,
  with `discount_factor[t] = 1/(1+r)^(t−2025)` and a real discount rate
  **r = 6%** (`core/definitions.mod`).
- **Demand is exogenous and must be met exactly**
  (`meet_demand`, `t_additional_constraints.mod`):
  `total_steel[t] = base_demand × (1+growth_rate)^(t−2025)`, with
  **base_demand = 152.2 Mt** in 2025 and **growth_rate = 5%/yr**. This implies
  **515.4 Mt of crude steel in 2050** and ~7,780 Mt cumulatively over the
  horizon. Demand is price-inelastic by construction: material efficiency and
  demand reduction are not available mitigation channels in this model.

## 3. Production routes

Five crude-steel routes, each with an explicit upstream chain. Module files in
`core/modules/`:

| Route | Chain |
|---|---|
| **BF-BOF** | coke ovens (`a_coke`) → sinter (`b_sinter`) → BF pellets (`c_pellets_bf`) → blast furnace (`d_blast_furnace`) → basic oxygen furnace (`e_bof`) |
| **Coal-DRI–EAF** | DRI-grade pellets (`f_pellets_coaldri`) → coal-based DRI (`i_dri_coal`) → EAF (`l_eaf_dri`) |
| **NG-DRI–EAF** | pellets (`g_pellets_ngdri`) → gas-based DRI (`j_dri_ng`) → EAF |
| **H₂-DRI–EAF** | pellets (`h_pellets_h2dri`) → hydrogen DRI (`k_dri_h2`) → EAF |
| **Scrap-EAF** | dedicated 100%-scrap EAF (`m_scrap_eaf`) |

Each module is a set of linear mass and energy balances tying inputs to
outputs at fixed coefficients — power, ore, lime, coke, coal, gas, hydrogen,
electrodes, slag, off-gases. The three DRI routes share a common EAF
(`l_eaf_dri`); their split is governed by `dri_route_split` in `k_dri_h2.mod`.

Total crude steel is closed by `steel_balance` (`n_steel_balance.mod`):
`steel_eaf[t] + steel_bof[t] + steel_scrap_eaf[t] = total_steel[t]`.

Scrap can also be charged into the BOF and the DRI-EAF within blend limits,
with year-on-year ramp constraints on how fast blends can change
(`bof_scrap_blend_max/min`, `bof_scrap_ramp_up/dn`, and equivalents in
`i_dri_coal.mod`, `j_dri_ng.mod`, `k_dri_h2.mod`).

**2025 initialisation** (`t_additional_constraints.mod`): BF-BOF holds 51% of
production, the EAF route 49%, dedicated scrap-EAF zero, and 90.2% of DRI-EAF
steel comes from coal-based DRI.

## 4. Capacity, vintages and retirement (`v_capacity.mod`)

This is the module that makes the model a capacity-expansion model rather than
a flow-accounting exercise.

- **Vintaged capacity**: for each route, installed capacity is the sum of
  builds still within their technical life,
  `cap_r[t] = legacy_r[t] + Σ{j : t−life_r+1 ≤ j ≤ t} build_r[j]`.
  Lives: **BF-BOF 25 yr, coal-DRI 20, NG-DRI 20, H₂-DRI 25, scrap-EAF 15**,
  electrolysers 15, CCS retrofits 15.
- **Legacy fleet**: the 2025 stock is **207.75 Mt** (BF-BOF 90.0, coal-DRI
  104.1, NG-DRI 12.9, H₂-DRI 0, scrap-EAF 0.75). It carries **no capital
  cost** — that capital is already sunk — but does incur fixed operating cost.
- **Retirement policy is a lever** (`legacy_phaseout`): 0 = assets run their
  technical life; 1 = mandated linear decay of the 2025 fleet to zero by 2050.
  The fleet's vintage distribution is unknown, so the two settings *bracket*
  the truth rather than estimating it. Under either setting 117.75 Mt retires
  by 2045 anyway; the cases differ mainly over the fate of 90 Mt of BF-BOF.
- **Utilisation**: production ≤ `util_max` × installed capacity, with
  **util_max = 0.95**.
- **Shared annual build budget** (`cap_add_total`): the four conventional
  routes compete for one annual capacity-addition budget,
  `build_bof + build_cdri + build_ngdri + build_scrap ≤ cap_add_common`.
  This represents the finance and EPC capacity the sector can deploy in one
  year. **H₂-DRI is deliberately excluded from this budget and has no
  per-year build cap** — it is throttled only indirectly through electrolyser
  capacity. This asymmetry is inherited and flagged in the source
  (`v_capacity.mod:150`); it should be stated in any write-up.
- **Capacity envelope** (`cap_envelope`): total installed capacity ≤
  (1+`cap_buffer`) × demand, `cap_buffer` = 0.40. In practice inert: fixed
  opex on idle capacity already drives the capacity/demand ratio to
  1/util_max ≈ 1.053 from 2030 onward.

## 5. The green-hydrogen supply chain

Hydrogen is produced by electrolysers powered by **dedicated renewables**, not
by the grid. Two capacity stocks are built and paid for explicitly:
`cap_h2elec` (electrolysers) and `cap_h2re` (dedicated renewable capacity,
sized to cover electrolyser demand at a capacity factor `re_cf` = 0.35).
Electrolyser electricity is **55,000 kWh per tonne of H₂** (~55 kWh/kg
including balance of plant).

Because that load is behind the meter, it is excluded from the grid power
balance and incurs **no Scope-2 emissions** — this is what makes the hydrogen
"green" in the model (`p_power_balance.mod`, header note). The capital is
still charged.

Two timing controls govern hydrogen, and they are linked:

1. **Debut year** (`ng_h2_start_year`): H₂-DRI output and electrolyser
   capacity are forced to zero before this year (`No_H2_Before`,
   `h2elec_predebut`, `h2re_predebut`).
2. **Deployment ramp** (`h2elec_growth`): the *net* annual increase in
   electrolyser capacity is capped by a curve that rises to a crest and then
   **plateaus** at its peak rate. The crest sits five years after the debut
   year (`h2_peak_year = ng_h2_start_year + 5`), and the peak annual addition
   is 25% of a scale parameter `h2_ref_cap`.

The physical reading: the rising phase represents the state building enabling
infrastructure and supply chains — ports, power evacuation, stack
manufacturing, EPC capability, workforce; the crest is the point at which that
scaffolding is complete; the plateau is the finished state, a mature industry
adding capacity steadily at the rate the completed infrastructure supports.
Because the ceiling binds the *net* change, retiring electrolysers can be
replaced freely; only growth is throttled.

**A note on a corrected defect** (relevant to interpreting any earlier
results): the ceiling previously *decayed* back to a low baseline past the
crest, implying that an industry which had achieved 1.5 Mt/yr of additions
could manage only 0.24 Mt/yr five years later — capability expiring on the
calendar. Combined with the crest following the debut year, this made a *late*
hydrogen programme better-resourced in the late years than an early one, and
produced the logically impossible result that delaying hydrogen reduced total
system cost in 67% of otherwise-identical scenario pairs. The plateau
formulation removes this; cost is now monotone in the debut year across all
paired comparisons. The old behaviour is reproducible with
`h2_ramp_ratchet := 0`.

## 6. Resource availability constraints

Three exogenous, time-indexed supply ceilings (`t_additional_constraints.mod`):

- **Scrap** (`scrap_bound`): total scrap use across BOF, DRI-EAF and
  scrap-EAF ≤ `n8_scrap_limit[t]`, which grows from a **37 Mt seed in 2025**
  at an annual rate `n8_scrap_rate`. At the 6%/yr baseline this reaches
  **158.8 Mt in 2050**. This represents collection infrastructure, shredding
  and sorting capacity, and end-of-life-vehicle policy.
- **Natural gas** (`ng_bound`): `ngdri_ng_in[t] ≤ n5_ng_cap[t]`, a
  year-by-year table representing gas allocation to the steel sector.
- **Coking coal** (`coking_coal_bound`): `coking_coal_in[t] ≤ ccoal_cap[t]`,
  representing import policy and domestic supply.

## 7. Emissions accounting (`s_emissions.mod`)

**Scope 1** (`scope1_def`) is computed from physical input flows at fixed
emission factors: coking coal 2.79, PCI coal 2.756, other coal 2.64 and
natural gas 2.75 tCO₂ per tonne of input; limestone/lime calcination 0.44;
graphite electrodes 6.0; plus fuel burned in any CCS reboiler.

**Scope 2** (`scope2_def`) is grid electricity multiplied by a time-varying
grid emission factor: `n9_grid_ef[t] × grid_power_in[t]`. The factor
interpolates linearly from **886 gCO₂/kWh in 2025** to a 2050 endpoint that is
a policy lever.

**Total** (`total_emissions_def`): Scope 1 + Scope 2 − captured CO₂.

**The binding policy constraint** (`avg_emis_cap_total`) is cumulative, not
annual:

```
Σ{t in T} total_emissions[t]  ≤  avg_emi × Σ{t in T} total_steel[t]
```

That is, the emissions-intensity *average over the whole horizon*, weighted by
production, must not exceed the target `avg_emi` (tCO₂ per tonne crude steel).
Nothing forces the annual intensity to decline monotonically — the constraint
that would do so is the model's only nonlinearity and is dropped in every run.
The model may therefore emit more early and less late, or vice versa, provided
the cumulative budget holds.

## 8. Carbon capture (`q_carbon_capture.mod`)

CCS is available as a retrofit on three routes: blast furnace, coal-DRI and
NG-DRI. Capturable CO₂ per route is defined by process-specific capture
fractions with cost multipliers reflecting flue-gas concentration (BF gas is
the most concentrated and cheapest; coal-DRI kiln off-gas leaner and dearer).
Retrofit capacity is itself vintaged with a 15-year life, and capture is
bounded by installed retrofit capacity.

A **sector-wide deployment ceiling** (`ccs_sector_ceiling`) limits total
capture to a fraction `ccs_avail[t]` of all capturable CO₂, rising linearly
from **0 in 2027 to 50% in 2050** — representing transport-and-storage
build-out. Capture consumes power and steam, both charged.

## 9. Waste-heat recovery (`o_waste_heat.mod`)

Recoverable heat from BF-BOF, DRI-EAF and scrap-EAF is pooled and allocated
between power generation and steam for CCS reboilers (`whr_pool_alloc`). A
switch (`whr_ccs_integration`) governs whether recovered heat may serve the
capture plant or whether a fired boiler must be used instead — the latter
carrying its own fuel emissions, which appear in Scope 1.

## 10. Cost structure (`r_cost.mod`, `v_capacity.mod`)

`total_cost[t]` aggregates per-module operating costs, capital cost, fixed
operating cost, waste-heat and CCS costs.

**Capital is treated as sunk** (`sunk = 1`, the default and the setting used
in all reported runs):

- **Overnight capital expenditure is charged in full in the year of
  construction**, on the build variables — not amortised over the asset's
  life.
- **Fixed operating cost is charged on installed capacity**, not on output.
  Idle capacity therefore continues to cost money.

The alternative formulation present in the source (`sunk = 0`, annualised
capital charged against production via capital-recovery factors) is
deliberately unused: amortisation presumes the plant runs for a fixed number
of years, which is precisely the decision the model exists to make.

**No salvage or terminal value** is credited for asset life extending beyond
2050. A plant built in 2048 with a 25-year life pays 100% of its capital cost
for two years of service. This is a stated limitation, quantified: on the
baseline configuration, capital paid for but never used is ~13% of net present
value under a 2030 hydrogen debut and ~8.5% under a 2045 debut. Because the
*earlier* programme bears more unrecovered capital, crediting terminal value
would increase the measured cost of delaying hydrogen, not reduce it.

## 11. Experimental design

The model is solved across a **complete factorial** of eight policy-controlled
levers crossed with three emissions targets — **46,656 independent solves**:

| Lever | Levels | Policy instrument |
|---|---|---|
| Scrap-availability growth | 6 — 0.00 to 0.10 /yr | collection infrastructure, ELV rules |
| Green-H₂ debut year | 4 — 2030/35/40/45 | hydrogen mission timing |
| 2050 grid emission factor | 9 — 50 to 850 gCO₂/kWh | power-sector decarbonisation |
| Coking-coal availability | 2 — abundant / scarce | import policy, domestic supply |
| Electrolyser deployment rate | 3 — 4/6/8 Mt/yr scale | H₂ supply-chain build-out |
| Gas allocation to steel | 2 — policy / BAU | gas allocation |
| Retirement policy | 2 — run-life / mandated phase-out | asset retirement mandate |
| Annual conventional build budget | 3 — 20/30/40 Mt/yr | finance and EPC capacity |
| *Emissions target* (`avg_emi`) | *3 — 1.6 / 1.8 / 2.0 tCO₂/t* | *the constraint being tested* |

The selection criterion is that this design sweeps **only what policy
controls**. Parameters governed by global technology learning rather than
Indian policy — hydrogen and CCS cost learning rates — are held fixed here and
varied separately in a Monte Carlo section.

Three properties make the output analysable: the design is complete, so
feasibility rates across lever levels are balanced without weighting
correction; lever comparisons are computed pairwise over scenarios feasible at
both settings; and cost comparisons are restricted to the subset in which the
electricity tariff lies inside its calibration range, while feasibility uses
the entire design.

## 12. Structural assumptions and limitations

Stated explicitly, because they bound what the results can claim:

1. **Demand is exogenous and price-inelastic.** Material efficiency and demand
   reduction are unavailable as mitigation. Since real demand would fall
   somewhat if steel became more expensive, targets are *harder* in this model
   than in reality.
2. **Prices are exogenous.** The grid emission factor is coupled to the
   industrial electricity tariff through a fixed linear relationship — a
   hand-specified stand-in for a price response the model cannot compute. The
   coupling rate is an untested assumption.
3. **The emissions cap is cumulative**, with no constraint forcing annual
   intensity to decline.
4. **H₂-DRI plant construction has no explicit rate limit**, unlike the four
   conventional routes.
5. **BF-BOF decarbonises on a calendar schedule**: coke rate and bio-PCI
   substitution interpolate over time with no capital cost and no decision
   variable, giving the incumbent route abatement that competing routes must
   build and pay for.
6. **No carbon price.** The only climate instrument is the quantity cap; a
   carbon tax parameter exists but is not in the active constraint set.
7. **No terminal value** for assets outliving the horizon (§10).
8. **Perfect foresight.** A single deterministic optimisation over the whole
   horizon, with no uncertainty and no learning during the run.
9. **National aggregate.** One representative fleet, no plant-level siting,
   no regional resource or grid heterogeneity.
10. **The electrolyser ramp ceiling does not saturate** — it plateaus rather
    than rolling over, since demand, cost and the emissions cap determine when
    hydrogen stops growing.

## 13. Implementation

AMPL, solved with Gurobi 13.0.2 (HiGHS also available), driven through
`amplpy`. The model structure (`core/model.mod`) declares sets, parameters,
variables, constraints and the objective but performs no solve and no
reporting; scenario drivers layer parameter overrides on top and solve.
Presolve typically reduces each instance to roughly 1,000 × 950; solves take
well under a second by dual simplex. Each scenario is solved in a **fresh
model instance** — required for correctness, because a derived parameter in
the grid-emission-factor chain is evaluated once and frozen on first read, so
a reused instance would silently pin the grid emission factor at the first
scenario's value.
