# `r_cost.mod` — cost equations and the objective's cost aggregate

> **Source:** `core/modules/r_cost.mod` — 143 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

Turns physical flows into money. One equality per unit operation defines that
operation's annual cost as `Σ (price × input) − Σ (credit × output)`, and
`total_cost_def` sums them with the capital and waste-heat terms into
`total_cost[t]` — the single quantity the objective discounts and minimises.

Every constraint here is an **equality that pins a cost variable**. None of
them is a decision; the module contributes no degrees of freedom, only
accounting.

## Declares

No parameters, no variables. Sixteen constraints, all equalities:

| Constraint | Pins | eq |
|---|---|---|
| `cost_cokeov_def` | `cost_cokeov` | 89 |
| `cost_sinter_def` | `cost_sinter` | 90 |
| `cost_pellet_bf_def` | `cost_pellet_bf` | 91 |
| `cost_bf_def` | `cost_bf` | 92 |
| `cost_bof_def` | `cost_bof` | 93 |
| `cost_pellet_coaldri_def` | `cost_pellet_coaldri` | 94 |
| `cost_pellet_ngdri_def` | `cost_pellet_ngdri` | 95 |
| `cost_pellet_h2dri_def` | `cost_pellet_h2dri` | 96 |
| `cost_coaldri_def` | `cost_coaldri` | 97 |
| `cost_ngdri_def` | `cost_ngdri` | 98 |
| `cost_h2dri_def` | `cost_h2dri` | 99 |
| `cost_eaf_def` | `cost_eaf` | 100 |
| `cost_scrap_eaf_def` | `cost_scrap_eaf` | 101 |
| `cost_wasteheat` | `whr_cost` | 102 |
| `cost_ccs_def` | `cost_ccs` | 103 |
| `total_cost_def` | `total_cost` | 104 |

## Equations

### The general pattern

Every process cost has the same shape, e.g. the BOF (eq93):

```ampl
  ng_cost_scrap    * bof_scrap_in[t]        # scrap purchase
+ ng_cost_power[t] * bof_power_in[t]        # electricity
+ ng_cost_lime     * bof_lime_in[t]         # flux
− ng_credit_slag   * bof_slag_out[t]        # by-product revenue
− cost_bof[t] = 0;
```

`ng_cost_power[t]` is time-varying (θ_grid-driven); every other price is
flat. Credits (`n0_credit_breeze`, `n0_credit_tar`, `ng_credit_slag`, and
`ng_cost_power[t]` applied to recovered power) reduce cost.

### Which inputs each route pays for

| Constraint | Pays for | Credits |
|---|---|---|
| coke oven (89) | coking coal, power | breeze, tar, **CDQ power** |
| sinter (90) | breeze, fine ore, power, lime, biochar | sinter-cooler power |
| BF pellets (91) | fine ore, power | — |
| blast furnace (92) | lump ore, PCI coal, biochar PCI, power, lime | **TRT power**, slag |
| BOF (93) | scrap, power, lime | slag |
| DRI pellet plants (94-96) | fine ore, power | — |
| coal-DRI (97) | power, lump ore, **non-coking** coal | — |
| NG-DRI (98) | power, lump ore, natural gas | — |
| H2-DRI (99) | power, lump ore, **H2 variable opex only** | — |
| DRI-EAF (100) | scrap, power, lime, non-coking coal, electrode | slag |
| scrap-EAF (101) | scrap, power, lime, non-coking coal, electrode | slag |

Three details that are easy to misread:

- **Recovered-power credits are valued at the grid tariff, not the sale
  price.** `cdq_power_out`, `sinterwaste_power_out` and `bf_trt_out` are
  credited at `ng_cost_power[t]`, i.e. as *avoided purchase*, and they also
  appear as negative terms in `p_power_balance.mod`. `ng_credit_power = 0.03`
  ($/kWh, the export price) is declared in `definitions.mod` and **never
  used**.
- **Natural gas:** `n5_cost_NG[t] * 50 * ngdri_ng_in[t]` — the `50` is
  MMBtu per tonne of NG. At the baseline 10 $/MMBtu that is **500 $/t-NG**.
- **Hydrogen:** eq99 charges only `h2_opex[t]` (300 $/t-H2, water + stack
  O&M). The *entire* capital cost of H2 — electrolyser and dedicated
  renewables — is carried in `capex_cost` and `fixopex_cost` from
  `v_capacity.mod`, not here. Reading eq99 alone makes hydrogen look almost
  free.

### Waste heat (eq102)

```ampl
n9_whr_capex * whr_power_generated[t] + n9_whr_opex * whr_power_generated[t]
  − whr_cost[t] = 0;
```

Capex and opex are both charged **per kWh generated** (0.009 + 0.003 =
0.012 $/kWh), not per kW installed. There is no WHR capacity variable and no
vintaging — WHR is the one asset in the model treated as pay-as-you-go.
The offsetting credit is applied in `total_cost_def`, not here.

### Carbon capture (eq103)

The only cost equation written in `lhs = rhs` form, and the most structured:

```ampl
cost_ccs[t] =
    ocapex_ccs[t] * (ccs_mult_bf*build_ccs_bf[t] + ccs_mult_cdri*build_ccs_cdri[t]
                     + ccs_mult_ngdri*build_ccs_ngdri[t])   # overnight capex on builds
  + fom_ccs[t]    * (ccs_mult_bf*ccs_cap_bf[t]   + …)       # fixed O&M on capacity
  + ng_cost_power[t] * power_ccs[t]                          # capture electricity
  + ccs_vopex_solvent * total_ccs[t]                         # 5 $/tCO2
  + ccs_ts_cost       * total_ccs[t]                         # 20 $/tCO2 transport+storage
  + (n5_cost_NG[t]/ng_gj_per_mmbtu) * ccs_steam_boiler[t]/ccs_boiler_eff;
```

Five of the six components of the 125 $/tCO2 anchor reappear here explicitly;
the sixth (regeneration steam) is priced **only when it comes from the backup
boiler**. Steam drawn from the waste-heat pool (`ccs_steam_whr`) is charged
nothing directly — its cost is the opportunity cost of the WHR power
foregone, which the LP handles correctly through `whr_pool_alloc`.

The stream multipliers `ccs_mult_*` scale capex and fixed O&M (a leaner gas
needs a bigger, dearer plant per tCO2) but **not** the variable terms.
Stream-specific energy is handled instead through `ccs_kwh_*` and
`ccs_steam_*` inside `q_carbon_capture.mod`.

Boiler fuel: `n5_cost_NG[t]/ng_gj_per_mmbtu` converts $/MMBtu → $/GJ, and
`/ccs_boiler_eff` grosses up steam GJ to fuel GJ at 85% efficiency. The
matching CO2 is charged in `s_emissions.mod`'s `scope1_def`.

### Total cost (eq104)

```ampl
  Σ (the 13 process costs)
+ other_opex * total_steel[t]                 # 10 $/tCS
+ capex_cost[t]                               # from v_capacity.mod
+ fixopex_cost[t]                             # from v_capacity.mod
+ whr_cost[t]
− ng_cost_power[t] * whr_power_generated[t]   # WHR displaces purchased power
− total_cost[t] = 0;
```

`labor_cost` (20) and `maintenance_cost` (15) are **not** here — they are in
`fopex_*` and charged on installed capacity by `v_capacity.mod`. Only
`other_opex` (10 $/tCS) is charged per tonne produced. The source comment
records this deliberately: *"variable other-opex (labour+maint now fixed)"*.

The WHR credit is applied here rather than inside `cost_wasteheat` so that
`whr_cost` can stay `>= 0` as declared while the *net* effect of WHR is
negative whenever `ng_cost_power[t] > 0.012 $/kWh` — which it always is.

## Depends on

| Symbol | Owner |
|---|---|
| every physical flow variable | `variables.mod` |
| `build_ccs_*`, `ccs_cap_*`, `capex_cost`, `fixopex_cost` | `modules/v_capacity.mod` |
| `whr_power_generated` | `variables.mod`, pinned by `modules/o_waste_heat.mod` |
| `power_ccs`, `total_ccs`, `ccs_steam_boiler` | `variables.mod`, pinned by `modules/q_carbon_capture.mod` |
| all `ng_cost_*`, `n*_cost_*`, `*_credit_*`, `ocapex_ccs`, `fom_ccs`, `ccs_mult_*`, `h2_opex`, `other_opex`, `n5_cost_NG`, `ng_gj_per_mmbtu`, `ccs_boiler_eff`, `n9_whr_capex/opex` | `definitions.mod` |

`total_cost[t]` is consumed by `model.mod`'s objective.

## Caveats

1. **`carbon_tax` does not appear in this file.** It is declared in
   `definitions.mod` (default 0) and used only in `yreport.mod`'s per-route
   decomposition. **Setting it non-zero changes reported route costs but not
   the optimum** — there is no carbon price in the objective. The only
   emissions pressure in the model is the hard cap `avg_emis_cap_total`.

2. **`ng_credit_power` is dead.** Declared at 0.03 $/kWh but never
   referenced; all recovered power is credited at the full grid tariff
   `ng_cost_power[t]` (0.07 $/kWh in 2025). Since `p_power_balance.mod`
   nets recovered power against grid draw, valuing it at the purchase price
   is internally consistent *provided* the site never becomes a net
   exporter — which nothing in the model prevents. `grid_power_in >= 0`
   makes net export infeasible rather than merely unprofitable, so the
   inconsistency is currently unreachable.

3. **Waste-heat capital is charged per kWh generated, with no capacity
   asset.** WHR is therefore infinitely and instantly scalable up to the
   `n9_whr[t]` penetration ceiling, unlike every other technology in the
   model. Since `n9_whr[t]` is exogenous (5% → 30%), the effect is bounded —
   but WHR faces no build ramp, no lifetime, and no stranding risk.

4. **The H2 route's cost equation looks cheap in isolation.** eq99 charges
   power + lump ore + 300 $/t-H2. A reader comparing eq97/98/99 side by side
   will conclude hydrogen is competitive today; the capital that dominates
   green H2 lives two modules away in `v_capacity.mod`. Any per-route cost
   comparison must go through `yreport.mod`'s decomposition, not these
   equations.

5. **Flat real prices mean this module's relative ordering barely changes
   over 26 years.** Coking coal, non-coking coal, scrap, ore, lime and
   electrode are constant 2025→2050; only power, NG, H2 and CCS move. Route
   switching is therefore driven almost entirely by the θ dials, the
   emissions cap and the capacity dynamics — not by fuel-price evolution.

6. **CCS stream multipliers scale capex but not solvent or T&S.** That is
   defensible (transport and storage costs depend on tonnes, not stream
   concentration) but means a leaner stream is penalised only through capex,
   fixed O&M, power and steam — the model never charges more per tonne for
   *handling* harder CO2.
