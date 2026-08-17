# `i_dri_coal.mod` — coal-DRI + EAF/IF route

> **Source:** `core/modules/i_dri_coal.mod` — 33 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

The coal-based direct-reduction route — India's dominant "secondary" steel
pathway and, at `cap0_cdri = 104.1 Mt`, **the largest single block of
incumbent capacity in the model** (larger than BF-BOF's 90 Mt). Rotary-kiln
sponge iron melted in induction furnaces and EAFs.

Nine constraints: a metallic-charge balance, a five-part scrap blend block
identical in form to the BOF's, and four proportional input balances.

## Declares

No parameters, no variables. Nine constraints (eq46-eq50 plus the blend block).

## Equations

### Metallic charge (eq46)

```ampl
coaldri_dri_out[t] + coaldri_scrap_in[t] = n7_dri_ratio * coaldri_output[t];
```

`n7_dri_ratio = 1.1` t of metallic charge per tCS. **DRI and scrap are 1:1
substitutes inside that charge** — the same structure as the BOF's hot
metal/scrap trade-off, and the reason `_output` (crude steel) and `_dri_out`
(sponge iron) must be kept distinct.

### Scrap blend block

```ampl
coaldri_scrap_in[2025] = phi0_cdri * 1.1 * coaldri_output[2025];   # 0.382, equality
coaldri_scrap_in[t]   <= phi_max_cdri * 1.1 * coaldri_output[t];   # 0.40
coaldri_scrap_in[t]   >= phi_min_cdri * 1.1 * coaldri_output[t];   # 0
|Δ coaldri_scrap_in|  <= blend_ramp * 1.1 * coaldri_output[t];     # 0.05/yr
```

The 2025 pin is **0.382** — the coal-DRI route already runs at 38% scrap,
against a ceiling of 40%. So unlike the BOF (9% → 20%, plenty of headroom)
this route has essentially **no scrap-blending headroom left**: it can move
1.8 percentage points and no more. The floor is 0, so it can shed scrap
freely.

This asymmetry matters for reading scrap-scarcity results: when scrap
tightens, coal-DRI is the route that gives scrap up, because it is the only
one whose floor is zero *and* whose current share is high.

### Proportional balances

| eq | Constraint | Coefficient (per t DRI) | Defines |
|---|---|---|---|
| 47 | `coaldri_power_balance` | `n4_e_dri` = **217 kWh** | `coaldri_power_in` |
| 48 | `coaldri_pellets_balance` | `n4_pel_dri` = 1.5 t | `coaldri_pellets_in` |
| 49 | `coaldri_lumpore_balance` | `n4_ore_dri` = 0.1 t | `coaldri_lumpore_in` |
| 50 | `coaldri_coal_balance` | `n4_c_dri` = **1.0 t coal** | `coaldri_coal_in` |

Two figures carry embedded modelling decisions:

- **217 kWh/t-DRI.** `definitions.mod` records this as *100 base + 117*, the
  117 being the extra power of coal-DRI's induction-furnace-heavy secondary
  melting (129 kWh/tCS ÷ 1.1 t-DRI/tCS). Folding it into the shaft's
  coefficient lets `n7_e_eaf` stay route-neutral at 664 kWh/tCS. The
  often-quoted `217 + 664/1.1 ≈ 821 kWh/t-DRI` holds only at a **zero**
  scrap blend; at the 2025 pinned 38.2% blend the ratio is 0.68 t-DRI/tCS,
  so the measured figure is **1 194 kWh/t-DRI**, or **1 015 kWh/tCS**
  including the pellet plant. Against NG-DRI's 1 066 kWh/tCS and H2-DRI's
  1 115 kWh/tCS of *grid* power, the route is not the outlier the raw
  shaft coefficients suggest — the shared 664 kWh/tCS EAF dominates all
  three.
- **1.0 t non-coking coal per t-DRI.** Coal is both reductant and fuel in a
  rotary kiln, and this is the dominant emissions term: at 2.64 tCO2/t-coal
  (`scope1_def`) that is **2.64 tCO2 per t-DRI**. Per tonne of *crude steel*
  the 2025 figure is **1.85 tCO2/tCS**, the scrap blend diluting it — still
  the dirtiest route in the model, but the per-t-DRI and per-tCS figures
  differ by more than the scrap share alone would suggest, so quote the
  basis.

> Both measured figures above were read off a solved 2025 baseline
> (`amplpy` + HiGHS), not derived by hand.

The coal is priced as `ng_cost_ncoal = 98 $/t` in `r_cost.mod`.

## Depends on

| Symbol | Owner |
|---|---|
| `coaldri_output`, `coaldri_dri_out`, `coaldri_scrap_in`, and the four input vars | `variables.mod` |
| `n4_*`, `n7_dri_ratio`, `n7_cs`, `n7_ls`, `phi0_cdri`, `phi_min_cdri`, `phi_max_cdri`, `blend_ramp` | `definitions.mod` |

Feeds:
- `coaldri_output` → `k_dri_h2.mod` (`dri_route_split`), `v_capacity.mod`
  (`cap_lim_cdri`, `min_util_cdri`), `q_carbon_capture.mod`,
  `s_emissions.mod`, `t_additional_constraints.mod` (`init_f_cdri`)
- `coaldri_scrap_in` → `l_eaf_dri.mod` (`eaf_scrap_balance`)
- `coaldri_coal_in` → `s_emissions.mod`, `q_carbon_capture.mod`, `r_cost.mod`,
  `v_capacity.mod` (coal chain)

## Caveats

1. **Coal-DRI is the largest incumbent block (104.1 Mt) and the dirtiest
   route.** How fast it can be displaced is governed by `legacy_ceil_cdri`
   (linear to zero by 2050), `min_util_cdri = 0.75`, and `life_cdri = 20`.
   Those three parameters largely determine the model's headline
   decarbonisation trajectory, and none of them is swept by any Section A
   study.

2. **The 2025 scrap pin (0.382) sits 1.8 pp below the ceiling (0.40).** The
   route's scrap flexibility is essentially exhausted at the start of the
   horizon. Anyone sweeping `phi_max_cdri` should know it is currently a
   near-binding constraint, not slack.

3. **Emissions and capture use a *different* coal emission factor than the
   cost equations use a price.** `s_emissions.mod`'s `scope1_cdri` applies
   `0.110 × 24 = 2.64 tCO2/t-coal`, while `scope1_def` (the total) applies
   `2.64` directly to the same variable — consistent. But
   `q_carbon_capture.mod` uses `0.110 × 24` for the capturable base while
   `co2_capturable_bf` uses `0.1116 × 25 = 2.79` for coking coal. Different
   coals, consistent within themselves; just note the factors are hardcoded
   inline in three separate modules rather than declared as parameters.

4. **The IF/EAF power split is a hardcoded allocation.** The `100 + 117`
   decomposition is documented only in a comment. Changing `n7_e_eaf` (the
   shared EAF coefficient) would silently break the calibration that makes
   `n4_e_dri = 217` correct.

5. **No coal quality or supply constraint on non-coking coal.**
   `ccoal_cap` constrains *coking* coal only (`t_additional_constraints.mod`);
   `coaldri_coal_in` is unbounded except through the coal supply chain in
   `v_capacity.mod`, which is priced at zero.

## Constraint index

| Constraint | eq | Covered under |
|---|---|---|
| `coaldri_metallic_balance` | 46 | Metallic charge |
| `coaldri_scrap_blend0` | — | Scrap blend block — 2025 pin at 0.382 |
| `coaldri_scrap_blend_max` | — | Scrap blend block — ceiling 0.40 |
| `coaldri_scrap_blend_min` | — | Scrap blend block — floor 0 |
| `coaldri_scrap_ramp_up` | — | Scrap blend block — +5 pp/yr |
| `coaldri_scrap_ramp_dn` | — | Scrap blend block — −5 pp/yr |
| `coaldri_power_balance` | 47 | Proportional balances |
| `coaldri_pellets_balance` | 48 | Proportional balances |
| `coaldri_lumpore_balance` | 49 | Proportional balances |
| `coaldri_coal_balance` | 50 | Proportional balances |
