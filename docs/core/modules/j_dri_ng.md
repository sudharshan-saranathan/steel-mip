# `j_dri_ng.mod` — natural-gas DRI + EAF route

> **Source:** `core/modules/j_dri_ng.mod` — 37 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

The gas-based shaft-furnace DRI route (MIDREX/HYL class). Structurally
identical to `i_dri_coal.mod` — metallic-charge balance, five-part scrap
blend block, four proportional input balances — differing only in
coefficients and in the reductant being natural gas.

This is the model's *transitional* route: cleaner than coal-DRI, cheaper than
H2-DRI, and the one whose availability is deliberately restricted by the
`n5_ng_cap` table in `core/parameters.mod`.

## Declares

No parameters, no variables. Nine constraints (eq51-eq55 plus the blend block).

## Equations

### Metallic charge (eq51)

```ampl
ngdri_dri_out[t] + ngdri_scrap_in[t] = n7_dri_ratio * ngdri_output[t];   # 1.1
```

### Scrap blend block

| Bound | Value |
|---|---|
| 2025 pin `phi0_ngdri` | **0.13** (equality) |
| ceiling `phi_max_ngdri` | 0.40 |
| floor `phi_min_ngdri` | 0 |
| ramp `blend_ramp` | 0.05/yr |

Unlike coal-DRI (pinned at 0.382, near its ceiling), NG-DRI starts at 13%
with **27 percentage points of headroom**. It is therefore the DRI route most
able to absorb additional scrap when scrap is cheap and available — reachable
in ~6 years at the 5 pp/yr ramp.

### Proportional balances

| eq | Constraint | Coefficient (per t DRI) | Defines |
|---|---|---|---|
| 52 | `ngdri_power_balance` | `n5_e_dri` = **120 kWh** | `ngdri_power_in` |
| 53 | `ngdri_pellets_balance` | `n5_pel_dri` = 1.5 t | `ngdri_pellets_in` |
| 54 | `ngdri_lumpore_balance` | `n5_ore_dri` = 0.1 t | `ngdri_lumpore_in` |
| 55 | `ngdri_ng_balance` | `n5_ng_dri` = **0.35 t NG** | `ngdri_ng_in` |

Contrast with coal-DRI: 120 kWh vs 217 (no IF penalty — NG-DRI feeds a
proper EAF), and 0.35 t NG vs 1.0 t coal.

### The natural gas chain

`ngdri_ng_in` is the most heavily constrained flow in the model. It is:

| Consumer | Effect |
|---|---|
| `t_additional_constraints.mod` `ng_bound` | `<= n5_ng_cap[t]` — a **hard volume cap**, with a 2035-2040 shock built into the baseline table |
| `r_cost.mod` `cost_ngdri_def` | priced at `n5_cost_NG[t] × 50` = **500 $/t-NG** at the baseline 10 $/MMBtu |
| `s_emissions.mod` `scope1_def` | 2.75 tCO2/t-NG |
| `q_carbon_capture.mod` | `0.055 × 50 = 2.75` capturable base |
| `v_capacity.mod` | NG supply chain (zero capex) |

At 0.35 t-NG/t-DRI and a 1.1 metallic ratio, the 2035 cap of 7.84 Mt limits
NG-DRI to roughly **24 Mt of crude steel** that year — the tightest year in
the baseline.

Emissions: 0.35 × 2.75 = **0.96 tCO2 per t-DRI**, about 36% of coal-DRI's
2.64. Per tonne of crude steel the measured 2025 figure is
**0.97 tCO2/tCS** against coal-DRI's 1.85. That, plus a cheaper capture
stream (see below), is why NG-DRI is the model's bridge technology.

### Why NG-DRI has the cheapest capture

`definitions.mod` splits NG-DRI's capturable CO2 into a **process stream**
(60%, concentrated, `ccs_mult_ng_proc = 0.5`, 0.3 GJ steam/tCO2) and a
**flue stream** (40%, dilute, `ccs_mult_ng_flue = 1.3`, 3.6 GJ steam/tCO2).
The blended multiplier `ccs_mult_ngdri = 0.82` is **below** BF's 1.0 and well
below coal-DRI's 1.2, and the blended steam demand (1.62 GJ/tCO2) is about
half BF's 3.0. NG-DRI + CCS is thus the cheapest abatement option available
to the model per tonne captured.

## Depends on

| Symbol | Owner |
|---|---|
| `ngdri_output`, `ngdri_dri_out`, `ngdri_scrap_in`, and the four input vars | `variables.mod` |
| `n5_*`, `n7_dri_ratio`, `phi0_ngdri`, `phi_min_ngdri`, `phi_max_ngdri`, `blend_ramp` | `definitions.mod` |

Feeds `k_dri_h2.mod` (`dri_route_split`), `l_eaf_dri.mod`
(`eaf_scrap_balance`), `v_capacity.mod`, `q_carbon_capture.mod`,
`s_emissions.mod`, `t_additional_constraints.mod` (`ng_bound`), `r_cost.mod`.

## Caveats

1. **The baseline NG volume cap contains an unannounced supply shock.** The
   `n5_ng_cap` table in `core/parameters.mod` drops 28% in 2035 and jumps 35%
   in 2041. Any NG-DRI trajectory that dips in the late 2030s is partly
   imposed, not derived. See `parameters.md` caveat 2.

2. **`n5_ng_cap` has no default.** If a scenario file supplies its own
   parameters without this table, the model fails on an uninitialised
   parameter rather than defaulting to unbounded.

3. **NG price is flat at 10 $/MMBtu unless a study overrides it**, and the
   commented-out shock (22.5 $/MMBtu for 2035-2040) is *off* while the volume
   shock over the same window is *on*. The two halves of the shock are
   inconsistent.

4. **The `× 50` unit conversion is inline in `r_cost.mod`**, not a declared
   parameter, and the matching `0.055 × 50` appears inline in two other
   modules. A change to the MMBtu/tonne assumption must be made in three
   places.

5. **`ngdri_output` carries a `<= dem[t]` bound** in `variables.mod` that
   `h2dri_output` does not. Redundant — see `variables.md` caveat 1.

6. **The 60/40 process/flue split is fixed**, so NG-DRI's capture cost
   advantage does not vary with capture rate. In reality the concentrated
   process stream would be captured first and the marginal cost would rise
   steeply once it is exhausted; the model's linear blend gives a constant
   marginal cost across the whole capturable base.

## Constraint index

| Constraint | eq | Covered under |
|---|---|---|
| `ngdri_metallic_balance` | 51 | Metallic charge |
| `ngdri_scrap_blend0` | — | Scrap blend block — 2025 pin at 0.13 |
| `ngdri_scrap_blend_max` | — | Scrap blend block — ceiling 0.40 |
| `ngdri_scrap_blend_min` | — | Scrap blend block — floor 0 |
| `ngdri_scrap_ramp_up` | — | Scrap blend block — +5 pp/yr |
| `ngdri_scrap_ramp_dn` | — | Scrap blend block — −5 pp/yr |
| `ngdri_power_balance` | 52 | Proportional balances |
| `ngdri_pellets_balance` | 53 | Proportional balances |
| `ngdri_lumpore_balance` | 54 | Proportional balances |
| `ngdri_ng_balance` | 55 | Proportional balances / the natural gas chain |
