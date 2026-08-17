# `k_dri_h2.mod` — hydrogen DRI route, and the DRI route split

> **Source:** `core/modules/k_dri_h2.mod` — 27 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

Two jobs in one module:

1. **`dri_route_split` (eq56)** — the constraint that makes the three DRI
   routes shares of one EAF pool. Belongs to no single route, and lives here.
2. The hydrogen shaft's own balances — structurally the same as coal and NG
   DRI, but with a **deliberately shortened blend block**.

## Declares

No parameters, no variables. Seven constraints (eq56-eq60 plus two blend
constraints).

## Equations

### The DRI route split (eq56)

```ampl
coaldri_output[t] + ngdri_output[t] + h2dri_output[t] - dri_eaf_steel_out[t] = 0;
```

The three DRI routes' crude-steel outputs sum to the DRI-EAF total. Combined
with `l_eaf_dri.mod`'s `dri_eaf_steel_relation` (`steel_eaf = dri_eaf_steel_out`)
and `eaf_steel_fraction` (`f_eaf·dem = steel_eaf`), this is what lets
`yreport.mod` report route shares as `f_cdri × f_eaf` etc.

Note the model has **no `f_h2dri` variable**: the H2 share is computed
residually as `1 − f_cdri − f_ngdri` throughout `yreport.mod`.

### Metallic charge and blend

```ampl
h2dri_dri_out[t] + h2dri_scrap_in[t] = n7_dri_ratio * h2dri_output[t];   # 1.1
h2dri_scrap_in[t] <= phi_max_h2dri * n7_dri_ratio * h2dri_output[t];     # 0.40
```

**That is the entire blend block** — a ceiling and nothing else. Compare
coal-DRI and NG-DRI, which each get five constraints:

| | coal-DRI | NG-DRI | **H2-DRI** |
|---|---|---|---|
| 2025 pin (equality) | ✓ 0.382 | ✓ 0.13 | **absent** |
| max | ✓ 0.40 | ✓ 0.40 | ✓ 0.40 |
| min | ✓ 0 | ✓ 0 | **absent** |
| ramp up / down | ✓ | ✓ | **absent** |

The omissions are defensible: there is no 2025 H2-DRI fleet to pin
(`cap0_h2dri = 0`), `phi_min_h2dri = 0` makes the floor vacuous, and a route
starting from zero has no previous-year blend to ramp from. But the ramp
constraint is *not* vacuous once the route exists — H2-DRI can swing its
scrap blend from 0% to 40% in a single year, which the other two routes
cannot. See Caveats.

Also note the max constraint is indexed `{t in T}` — over the whole horizon,
not `t > first(T)` as in the other routes. Harmless (it is a `<=` and
`h2dri_output[2025]` is effectively zero) but inconsistent.

### Proportional balances

| eq | Constraint | Coefficient (per t DRI) | Defines |
|---|---|---|---|
| 57 | `h2dri_power_balance` | `n6_e_dri` = **110 kWh** | `h2dri_power_in` |
| 58 | `h2dri_pellets_balance` | `n6_pel_dri` = 1.5 t | `h2dri_pellets_in` |
| 59 | `h2dri_lumpore_balance` | `n6_ore_dri` = 0.1 t | `h2dri_lumpore_in` |
| 60 | `h2dri_h2_balance` | `n6_h2_dri` = **0.07 t H2** | `h2dri_h2_in` |

`n6_h2_dri = 0.07` t-H2/t-DRI is deliberately conservative — stoichiometric
reduction of Fe2O3 needs ≈0.054 t-H2/t-Fe, so the extra ~30% covers shaft
losses and excess-hydrogen recirculation.

At `h2_kwh_per_t = 55 000` kWh/t-H2, that is **3 850 kWh of renewable
electricity per t-DRI** — an order of magnitude more than the shaft's own
110 kWh, and the reason the H2 route's economics are dominated by
electrolyser and RE capital rather than by anything in this module.

### `h2dri_h2_in` is the model's H2 hub

It appears in five other modules:

| Consumer | Role |
|---|---|
| `parameters.mod` `No_H2_Before` | forced to 0 before `ng_h2_start_year` |
| `v_capacity.mod` `h2elec_cover` | `<= cap_h2elec[t]` — electrolyser sizing |
| `v_capacity.mod` `h2re_cover` | `55000 × h2dri_h2_in <= cap_h2re × 8760 × re_cf` — RE sizing |
| `r_cost.mod` `cost_h2dri_def` | priced at `h2_opex[t]` = 300 $/t only |
| `v_capacity.mod` (sunk = 0 branch) | annualised electrolyser + RE capex |

### Zero Scope-1 from reduction

There is no CO2 term for hydrogen anywhere. `s_emissions.mod`'s
`scope1_h2dri` counts only the EAF's coal and lime
(`n7_cs × 0.110 × 24 + n7_ls × 0.44` ≈ **0.053 tCO2/tCS**). H2-DRI's
remaining footprint is entirely **Scope 2** — grid power for the shaft
(110 kWh/t-DRI), the pellet plant (300 kWh/t-DRI) and the EAF
(664 kWh/tCS) — since only the electrolyser is behind the renewable meter.

## Depends on

| Symbol | Owner |
|---|---|
| `coaldri_output` | `modules/i_dri_coal.mod` |
| `ngdri_output` | `modules/j_dri_ng.mod` |
| `h2dri_*`, `dri_eaf_steel_out` | `variables.mod` |
| `n6_*`, `n7_dri_ratio`, `phi_max_h2dri` | `definitions.mod` |

## Caveats

1. **H2-DRI has no scrap-blend ramp constraint.** It can move from 0% to 40%
   scrap in one year while coal-DRI and NG-DRI are held to 5 pp/yr. Once
   H2-DRI capacity exists this is a real asymmetry that gives the H2 route an
   unearned flexibility advantage, particularly in scrap-availability
   studies.

2. **`h2dri_scrap_blend_max` is indexed over all of T** while the equivalent
   coal/NG constraints start at `t > first(T)`. Cosmetic today, but it is the
   kind of inconsistency that becomes a bug if `cap0_h2dri` is ever set
   non-zero.

3. **`h2dri_output` carries no `<= dem[t]` bound** while `coaldri_output`
   and `ngdri_output` do. The bound is redundant in all three cases (see
   `variables.md` caveat 1), so this is an inconsistency rather than a defect.

4. **No H2 storage, no hourly matching.** `h2dri_h2_in[t]` is an annual
   quantity matched against annual electrolyser and RE capacity. Real H2-DRI
   needs buffer storage to run a continuous shaft off intermittent
   electrolysis; that cost is folded into the `h2_firm_capex` calibration
   residual in `definitions.mod`, not modelled.

5. **No hydrogen import or merchant purchase option.** H2 can only come from
   the model's own dedicated electrolyser + RE build. A scenario in which
   India buys hydrogen (or hydrogen-based HBI) is not representable.

6. **`n6_h2_dri = 0.07` is a fixed conversion.** Shaft efficiency does not
   improve over the horizon, unlike the blast furnace's coke rate — so the
   BF gets exogenous efficiency gains that the H2 route does not.

## Constraint index

| Constraint | eq | Covered under |
|---|---|---|
| `dri_route_split` | 56 | The DRI route split |
| `h2dri_metallic_balance` | — | Metallic charge and blend |
| `h2dri_scrap_blend_max` | — | Metallic charge and blend — the only blend constraint |
| `h2dri_power_balance` | 57 | Proportional balances |
| `h2dri_pellets_balance` | 58 | Proportional balances |
| `h2dri_lumpore_balance` | 59 | Proportional balances |
| `h2dri_h2_balance` | 60 | Proportional balances / `h2dri_h2_in` is the model's H2 hub |
