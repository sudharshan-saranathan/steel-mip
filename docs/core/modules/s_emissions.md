# `s_emissions.mod` — CO2 accounting

> **Source:** `core/modules/s_emissions.mod` — 46 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

Computes Scope 1 (direct, from fuel combustion and process chemistry),
Scope 2 (indirect, from purchased electricity), and the net total after
capture. `total_emissions[t]` is the quantity the policy constraint
`avg_emis_cap_total` binds, so this module is where every decarbonisation
lever in the model ultimately registers.

Eight constraints: five per-route Scope-1 attributions, one Scope-1 total,
one Scope-2, one net total.

## Declares

No parameters, no variables. Eight equality constraints (eq105-eq112).

## Equations

### Per-route Scope 1 (eq105-eq109)

These are **attribution** constraints — they exist for reporting and for
`yreport.mod`'s per-route emission intensities. They do *not* sum to
`scope1_emissions`; eq110 is computed independently.

| eq | Route | Terms |
|---|---|---|
| 105 | BF-BOF | coking coal × 2.79 + PCI coal × 2.756 + (sinter + BF + BOF lime) × 0.44 |
| 106 | coal-DRI | DRI coal × 2.64 + EAF carbon × 2.64 + EAF lime × 0.44 |
| 107 | NG-DRI | NG × 2.75 + EAF carbon × 2.64 + EAF lime × 0.44 |
| 108 | H2-DRI | EAF carbon × 2.64 + EAF lime × 0.44 **only** |
| 109 | scrap-EAF | scrap-EAF coal × 2.64 + scrap-EAF lime × 0.44 |

The factors are written as products (`0.1116 × 25`, `0.110 × 24`,
`0.055 × 50`) — carbon fraction × calorific value — inline, never as
declared parameters.

Note eq106-eq108 apply the EAF terms **per route** using `n7_cs` and `n7_ls`
against that route's `_output`. So the shared DRI-EAF's consumables are split
proportionally across the three routes here, consistent with
`l_eaf_dri.md` caveat 1.

Per-tonne intensities at 2025 coefficients:

| Route | Scope-1 (tCO2/tCS) | dominant term |
|---|---|---|
| BF-BOF | ≈ **2.4** | coking coal (0.78 t/tCS × 2.79) |
| coal-DRI | ≈ **2.7** | non-coking coal (1.0 t/t-DRI × 2.64) |
| NG-DRI | ≈ **1.0** | natural gas (0.35 t/t-DRI × 2.75) |
| H2-DRI | ≈ **0.053** | EAF carbon + lime |
| scrap-EAF | ≈ **0.053** | EAF carbon + lime |

### Scope 1 total (eq110)

Computed from the raw input flows, not from the five route attributions:

```ampl
  coking_coal_in    * 2.79
+ bf_coalpci_in     * 2.756
+ (coaldri_coal_in + eaf_coal_in + scrap_eaf_coal_in) * 2.64
+ ngdri_ng_in       * 2.75
+ (sinter_lime_in + bf_lime_in + bof_lime_in + eaf_lime_in + scrap_eaf_lime_in) * 0.44
+ (eaf_electrode_in + scrap_eaf_electrode_in) * 6
+ (ccs_steam_boiler / ccs_boiler_eff) * ng_co2_gj
− scope1_emissions = 0;
```

Two terms appear **only** here, in no route attribution:

- **Electrode oxidation, × 6 tCO2/t.** At 0.003 t electrode/tCS that is
  **0.018 tCO2/tCS** on every EAF route — about a third of the H2 route's
  entire Scope 1.
- **CCS backup-boiler fuel.** `ccs_steam_boiler / ccs_boiler_eff` grosses
  steam GJ up to fuel GJ at 85%, times `ng_co2_gj = 0.0521` tCO2/GJ. This is
  what makes the WHR boiler-only counterfactual (`whr_ccs_integration = 0`)
  emit as well as cost.

`bf_biopci_in` (biomass PCI) appears nowhere — biomass is implicitly
carbon-neutral.

### Scope 2 (eq111)

```ampl
n9_grid_ef[t] * grid_power_in[t] − scope2_emissions[t] = 0;
```

One term, applied to the **net** grid draw from `p_power_balance.mod` (after
CDQ, TRT, sinter-cooler and WHR generation are subtracted). The electrolyser
load is excluded upstream — see `p_power_balance.md`.

`n9_grid_ef[t]` falls from 0.000886 (2025) to a θ_grid-weighted 2050 endpoint
(0.00045 at the baseline θ_grid = 0.5). Scope 2 therefore decarbonises
exogenously for every route at once.

### Net total (eq112)

```ampl
scope1_emissions + scope2_emissions − total_ccs − total_emissions = 0;
```

Captured CO2 is subtracted from the total. Because `total_emissions >= 0`
(declared in `variables.mod`), capture can at most bring the total to zero,
never negative.

## Depends on

Every fuel, flux, electrode and coal flow variable, plus `grid_power_in`
(`p_power_balance.mod`), `total_ccs` and `ccs_steam_boiler`
(`q_carbon_capture.mod`), `n9_grid_ef`, `ng_co2_gj`, `ccs_boiler_eff`
(`definitions.mod`).

Feeds `t_additional_constraints.mod` (`avg_emis_cap_total`,
`emission_monotonic`) and `yreport.mod`.

## Caveats

1. **The five route attributions do not sum to the Scope-1 total.** eq110
   includes electrode oxidation (0.018 tCO2/tCS on both EAF routes) and CCS
   boiler fuel; eq105-eq109 include neither. The gap is small but real, and
   it means `yreport.mod`'s per-route intensities systematically understate —
   `Σ scope1_route < scope1_emissions` always. Any figure claiming route
   emissions "add up to" the total is wrong by construction.

2. **Emission factors are hardcoded inline and duplicated.** `2.79`,
   `2.756`, `2.64`, `2.75`, `0.44`, `6` appear in eq105-eq110 and again as
   factored products in `q_carbon_capture.mod`. Six edit sites for one
   change; nothing enforces consistency between the capturable base and the
   emitted amount. (They currently agree.)

3. **`total_emissions >= 0` forbids net-negative emissions.** With no BECCS
   and no DAC this is not currently reachable, but it is a hard bound rather
   than a modelling result — if biomass were ever given a negative factor,
   the model would report infeasibility rather than negative emissions.

4. **Biomass is carbon-neutral with no supply constraint and no land-use
   accounting.** `bf_biopci_in` rises to 0.053 t/thm and
   `sinter_biochar_in` to 0.022 t/t-sinter, both exogenously, both free of
   CO2 and both priced at only 60 $/t. At 2050 BF volumes this implies tens
   of Mt/yr of sustainable biomass with no availability limit.

5. **Scope 3 is entirely absent** — no upstream methane from natural gas, no
   mining or transport emissions for coal or ore, no embodied carbon in
   electrolysers or renewables. For NG-DRI in particular, upstream methane
   leakage is a material omission that would narrow its advantage over
   coal-DRI.

6. **Electrode CO2 at 6 tCO2/t is applied only to the two EAF routes.** BF-BOF
   has no electrode term, correctly — but note this is one of the few places
   where the model's route comparison depends on a factor that appears in
   just one equation.

## Constraint index

| Constraint | eq | Covered under |
|---|---|---|
| `scope1_blastf` | 105 | Per-route Scope 1 — BF-BOF |
| `scope1_coaldri` | 106 | Per-route Scope 1 — coal-DRI |
| `scope1_natgasdri` | 107 | Per-route Scope 1 — NG-DRI |
| `scope1_h2dri_` | 108 | Per-route Scope 1 — H2-DRI (EAF terms only) |
| `scope1_scrapeaf_` | 109 | Per-route Scope 1 — scrap-EAF |
| `scope1_def` | 110 | Scope 1 total — adds electrode oxidation + CCS boiler fuel |
| `scope2_def` | 111 | Scope 2 — `n9_grid_ef[t] × grid_power_in[t]` |
| `total_emissions_def` | 112 | Net total — Scope 1 + Scope 2 − captured |

Note the trailing underscores on `scope1_h2dri_` and `scope1_scrapeaf_` —
they are part of the constraint names in the source, presumably to avoid
colliding with the variables `scope1_h2dri` and `scope1_scrapeaf`.
