# `q_carbon_capture.mod` — CO2 capture

> **Source:** `core/modules/q_carbon_capture.mod` — 61 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

Defines how much CO2 each route can capture, and what capturing it costs in
energy. Capture is a genuine decision variable (unlike most of the model's
flows), and it is bounded **four independent ways** — three of them here, one
in `v_capacity.mod`.

Only three streams are capturable: BF-BOF, coal-DRI and NG-DRI. H2-DRI and
scrap-EAF have no capture option (their residual emissions are small and
dilute).

## Declares

| Symbol | Kind | Value |
|---|---|---|
| `fc_max` | `param`, **defined** | 0.9 — max physical capture rate per stream |
| `phi_2050` | `param`, **defined** | 0.50 — sector deployment ceiling in 2050 |
| `ccs_avail{t}` | `param`, **defined** | 0 before 2027, then linear to `phi_2050` |

Eight constraints (eq84-eq88b, plus three `co2_capturable_*_def`).

## Equations

### 1. The capturable base (three `_def` constraints)

What CO2 physically exists in a capture-amenable stream:

```ampl
co2_capturable_bf[t] =
    coking_coal_in[t] * 0.1116 * 25          # = 2.79 tCO2/t coking coal
  + bf_coalpci_in[t]  * 0.106  * 26          # = 2.756 tCO2/t PCI coal
  + (sinter_lime_in + bf_lime_in + bof_lime_in) * 0.44;   # calcination

co2_capturable_cdri[t] =
    coaldri_coal_in[t] * 0.110 * 24          # = 2.64 tCO2/t non-coking coal
  + (n7_cs * coaldri_output[t]) * 0.110 * 24 # EAF carbon injection
  + (n7_ls * coaldri_output[t]) * 0.44;      # EAF lime

co2_capturable_ngdri[t] =
    ngdri_ng_in[t] * 0.055 * 50              # = 2.75 tCO2/t NG
  + (n7_cs * ngdri_output[t]) * 0.110 * 24
  + (n7_ls * ngdri_output[t]) * 0.44;
```

The emission factors are written as `carbon_fraction × calorific_value`
products, inline, with no declared parameters. They match `s_emissions.mod`'s
`scope1_*` constraints exactly — the capturable base is *the whole Scope-1
stream of that route*, not a sub-fraction of it.

Notably `bf_biopci_in` (biomass PCI) appears in **neither** the capturable
base nor `scope1_bf` — biomass is treated as carbon-neutral, so it is neither
emitted nor capturable. There is no BECCS option.

### 2. Per-stream physical limit (eq84-eq86)

```ampl
ccs_bf[t]    <= n10_ccs_eta * fc_max * co2_capturable_bf[t];      # 0.85 × 0.9 = 0.765
```

`n10_ccs_eta = 0.85` (capture efficiency) times `fc_max = 0.9` (maximum
fraction of the stream that is even routed to a capture unit) gives a hard
ceiling of **76.5% of a route's Scope-1 CO2**.

### 3. Sector deployment ceiling

```ampl
param ccs_avail{t in T} :=
    if t < 2027 then 0
    else phi_2050 * (t - 2027) / (2050 - 2027);      # 0 at 2027 → 0.50 at 2050

s.t. ccs_sector_ceiling{t in T}:
    ccs_bf + ccs_cdri + ccs_ngdri
      <= ccs_avail[t] * (co2_capturable_bf + co2_capturable_cdri + co2_capturable_ngdri);
```

An exogenous build-out constraint representing pipelines, storage permits and
capture-module manufacturing. **No capture at all before 2027**, then a
linear ramp to 50% of the sector's total capturable CO2 by 2050.

This is a *sector-wide* limit applied to the *sum*, so the model may
concentrate all available capture on its cheapest stream (NG-DRI, at
`ccs_mult_ngdri = 0.82`) rather than spreading it. The per-stream limits in
§2 are what stop that from going all the way.

Note `ccs_avail` and `phi_2050` are **defined params** — the deployment
trajectory cannot be swept by a scenario without editing this file.

### 4. Totals and energy penalty (eq87-eq88b)

```ampl
ccs_bf + ccs_cdri + ccs_ngdri − total_ccs = 0;                       # eq87

ccs_kwh_bf*ccs_bf + ccs_kwh_cdri*ccs_cdri + ccs_kwh_ngdri*ccs_ngdri
  − power_ccs = 0;                                                   # eq88

ccs_steam_bf*ccs_bf + ccs_steam_cdri*ccs_cdri + ccs_steam_ngdri*ccs_ngdri
  = ccs_steam_whr[t] + ccs_steam_boiler[t];                          # eq88b
```

Stream-specific energy intensities (from `definitions.mod`):

| Stream | kWh/tCO2 | GJ steam/tCO2 | capex mult |
|---|---|---|---|
| BF (BFG, ~20-25% CO2) | 130 | 3.0 | 1.0 |
| coal-DRI (kiln off-gas) | 150 | 3.3 | 1.2 |
| NG-DRI (60% process + 40% flue) | 134 | 1.62 | 0.82 |

`power_ccs` goes into `p_power_balance.mod` and therefore carries grid
Scope-2 — **capturing CO2 emits CO2**. At 130 kWh/tCO2 and the 2025 grid EF
of 0.000886, capture costs 0.115 tCO2 of Scope 2 per tCO2 captured, i.e. the
*net* abatement is ~88% of the gross figure. That falls as the grid cleans up.

eq88b is the coupling to `o_waste_heat.mod`: regeneration steam must come
either from the waste-heat pool (free, but competes with power generation) or
from the gas-fired backup boiler (costs NG in `r_cost.mod` and emits CO2 in
`s_emissions.mod`). This is the mechanism the WHR study switches off.

### The fourth limit (elsewhere)

`v_capacity.mod` adds vintaged retrofit capacity:
`ccs_bf[t] <= ccs_cap_bf[t]`, with 15-year-life builds charged at
`ocapex_ccs[t] × ccs_mult_bf` in `r_cost.mod`. So capture must also be
*built and paid for*, not merely permitted.

## Depends on

| Symbol | Owner |
|---|---|
| `coking_coal_in` | `modules/a_coke.mod` |
| `bf_coalpci_in`, `bf_lime_in` | `modules/d_blast_furnace.mod` |
| `sinter_lime_in` | `modules/b_sinter.mod` |
| `bof_lime_in` | `modules/e_bof.mod` |
| `coaldri_coal_in`, `coaldri_output` | `modules/i_dri_coal.mod` |
| `ngdri_ng_in`, `ngdri_output` | `modules/j_dri_ng.mod` |
| `ccs_steam_whr` | `modules/o_waste_heat.mod` |
| `n10_ccs_eta`, `ccs_kwh_*`, `ccs_steam_*`, `n7_cs`, `n7_ls` | `definitions.mod` |

Feeds `p_power_balance.mod` (`power_ccs`), `s_emissions.mod` (`total_ccs`,
`ccs_steam_boiler`), `r_cost.mod` (`cost_ccs_def`), `v_capacity.mod`
(`ccs_caplim_*`).

## Caveats

1. **Emission factors are hardcoded inline in three separate modules.**
   `0.1116 × 25`, `0.106 × 26`, `0.110 × 24`, `0.055 × 50`, `0.44` appear
   here, in `s_emissions.mod` (twice — once per route, once in the total),
   and nowhere as declared parameters. Changing India's coal carbon content
   means editing six places consistently. This is the model's most fragile
   coefficient duplication.

2. **`fc_max`, `phi_2050` and `ccs_avail` are defined params** (`:=`), so the
   CCS deployment trajectory — arguably the most policy-contingent assumption
   in the model — cannot be swept from a scenario file. Only `theta_ccs`
   (which affects *cost*, not *availability*) is reachable.

3. **The sector ceiling is fractional, not absolute.** `ccs_avail[t] × (total
   capturable)` means that as the sector decarbonises and the capturable base
   shrinks, the absolute CCS ceiling shrinks with it. That is arguably
   backwards: pipeline and storage capacity, once built, does not contract
   because emissions fell.

4. **CCS on the H2 and scrap routes is impossible by construction.** Their
   residual Scope-1 (EAF carbon, lime, electrodes) has no `co2_capturable_*`
   term. Defensible on concentration grounds, but it means the model cannot
   reach net-zero on any pathway.

5. **No BECCS.** Biomass PCI carbon is neither emitted nor capturable, so
   the negative-emissions option that biochar+capture would provide is
   structurally absent.

6. **Capture is a flow decision with no minimum utilisation**, unlike every
   production route. `ccs_cap_bf` is built and paid for, but `ccs_bf` may sit
   at zero with no penalty beyond the fixed O&M. The optimiser therefore
   never over-builds capture, which is realistic but means capture capacity
   is never stranded.

7. **The three streams' capture costs are constant per tonne** across the
   whole capturable base. In reality the concentrated fraction of each stream
   is captured first and marginal cost rises steeply thereafter; the linear
   formulation gives constant marginal cost up to the 76.5% ceiling. This
   most flatters NG-DRI, whose 60/40 process/flue blend is treated as one
   homogeneous stream at the weighted average.

## Constraint index

| Constraint | eq | Covered under |
|---|---|---|
| `co2_capturable_bf_def` | base for 84 | The capturable base |
| `co2_capturable_cdri_def` | base for 85 | The capturable base |
| `co2_capturable_ngdri_def` | base for 86 | The capturable base |
| `ccs_bf_cap` | 84 | Per-stream physical limit (0.85 × 0.9 = 76.5%) |
| `ccs_cdri_cap` | 85 | Per-stream physical limit |
| `ccs_ngdri_cap` | 86 | Per-stream physical limit |
| `ccs_sector_ceiling` | — | Sector deployment ceiling (`ccs_avail[t]`) |
| `total_captured_co2` | 87 | Totals and energy penalty |
| `power_capture` | 88 | Totals and energy penalty — stream-specific kWh/tCO2 |
| `ccs_steam_balance` | 88b | Totals and energy penalty — WHR steam vs backup boiler |
