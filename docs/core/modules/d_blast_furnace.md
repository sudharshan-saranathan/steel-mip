# `d_blast_furnace.mod` — blast furnace

> **Source:** `core/modules/d_blast_furnace.mod` — 47 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

The hub of the BF-BOF route. Fifteen constraints size every input and
by-product of the furnace from `bf_hot_metal[t]`, and the last one closes the
loop back to `steel_bof[t]`. This is the module that makes the whole ironmaking
chain a scalar multiple of BOF steel output.

## Declares

No parameters, no variables. Fifteen equality constraints (eq18-eq32).

## Equations

### Proportional to hot metal (eq18-eq31)

| eq | Constraint | Coefficient (per t hot metal) | Defines |
|---|---|---|---|
| 18 | `power_bf_in` | 55 kWh | `bf_power_in` |
| 19 | `sinter_bf_in` | 1.15 t | `bf_sinter_in` |
| 20 | `lime_bf_in` | 0.025 t | `bf_lime_in` |
| 21 | `slag_bf_out` | 0.30 t | `bf_slag_out` |
| 22 | `pellets_bf_in` | 0.35 t | `bf_pellets_in` |
| 23 | `lumpore_bf_in` | 0.15 t | `bf_lumpore_in` |
| 24 | `bfg_bf_in` | 500 Nm³ × 0.0033 = **1.65 GJ** | `bfg_in` |
| 25 | `cog_bf_in` | 30 Nm³ × 0.018 = **0.54 GJ** | `bf_cog_in` |
| 26 | `bfg_bf_out` | 1500 Nm³ × 0.0033 = **4.95 GJ** | `bfg_out` |
| 27 | `trt_power_out` | 35 kWh | `bf_trt_out` |
| 28 | `bf_coal_pci_balance` | **interp.** 0.15 → 0.16 t | `bf_coalpci_in` |
| 29 | `bf_bio_pci_balance` | **interp.** 0.0 → 0.053 t | `bf_biopci_in` |
| 30 | `bf_coke_balance` | **interp.** 0.53 → 0.48 t | `bf_coke_in` |
| 31 | `bf_h2_balance` | **interp.** 0 → 0 t | `bf_h2_in` |

Burden: 1.15 t sinter + 0.35 t pellets + 0.15 t lump ore = **1.65 t of iron
units per thm**, a fixed recipe the optimiser cannot re-mix.

Gas: the furnace produces 4.95 GJ of BFG and consumes 1.65 GJ of it plus
0.54 GJ of COG, so it is a net BFG exporter of 3.30 GJ/thm (before the coke
oven takes its 0.891 GJ/t-coke share).

### The four interpolated coefficients

Same inline `(a25 + (a50−a25)·(t−2025)/25)` form as `b_sinter.mod`:

| Coefficient | 2025 | 2050 | Direction |
|---|---|---|---|
| coke rate | 0.53 | 0.48 | ↓ efficiency gain |
| coal PCI | 0.15 | **0.16** | ↑ partly replaces coke |
| biomass PCI | 0.00 | 0.053 | ↑ decarbonising injectant |
| H2 injection | 0 | **0** | inactive |

The reducing-agent story: coke falls 0.05 t/thm, coal PCI rises 0.01, and
biomass PCI rises 0.053. **This is an exogenous, unconditional efficiency
and fuel-switching path** — the blast furnace decarbonises on a fixed
schedule with no capital cost and no decision attached.

**`bf_h2_in` is identically zero.** Both endpoints `n2_h2_hm_25` and
`n2_h2_hm_50` are 0, so eq31 forces `bf_h2_in[t] = 0` for all t. BF hydrogen
co-injection was removed from the model deliberately (see git history:
*"Remove BF-BOF H2 co-injection"*), but the variable, parameters and
constraint remain as an inert scaffold. `yreport.mod` still divides by
`h2dri_h2_in + bf_h2_in` when allocating H2 supply capital — safe only
because the denominator's second term is always zero.

### Closing the loop (eq32)

```ampl
bf_hot_metal[t] = n3_metallic_bof * steel_bof[t] - bof_scrap_in[t];
```

The BOF metallic charge is 1.1 t per tCS (`n3_metallic_bof`), and scrap
displaces hot metal **1:1** within it. This is the module's only genuine
degree of freedom: more scrap into the BOF means less hot metal, hence less
of the entire upstream chain (sinter, coke, pellets, ore, coal) and less CO2.

`e_bof.mod` bounds `bof_scrap_in` at 5-20% of the charge with a 5 pp/yr ramp,
so the substitution is real but tightly limited.

### Chain arithmetic

Because eq18-eq30 are all equalities with constant (or time-constant)
coefficients, the entire BF-BOF chain collapses. Per tonne of hot metal in
2025:

```
1 thm → 1.15 t sinter → 1.035 t fine ore + 0.1035 t breeze + 0.046 t lime
      → 0.35 t pellets → 0.318 t fine ore
      → 0.15 t lump ore
      → 0.53 t coke → 0.779 t coking coal
      → 0.15 t PCI coal
      → 0.025 t lime
      → 55 (BF) + 57.5 (sinter) + 39.75 (coke) + 70 (pellets) kWh,
        less 35 (TRT) + 42.4 (CDQ) + 34.5 (sinter cooler) kWh recovered
```

And `bf_hot_metal = 1.1·steel_bof − bof_scrap_in`, so at the 2025 pinned
9% scrap blend, 1 tCS of BOF steel needs **1.0010 thm**. Adding the BOF's
own 174 kWh/tCS gives the route totals **396.5 kWh/tCS gross** and
**112.0 kWh/tCS recovered → 284.5 net**.

> All figures in this block were read off a solved 2025 baseline
> (`amplpy` + HiGHS), not derived by hand.

## Depends on

| Symbol | Owner |
|---|---|
| `bf_hot_metal`, `steel_bof`, `bof_scrap_in` | `variables.mod` |
| `n2_*`, `n3_metallic_bof`, `ng_bfg_cv`, `ng_cog_cv` | `definitions.mod` |

Pins (i.e. **owns** these variables' values): `bf_sinter_in` → `b_sinter.mod`,
`bf_coke_in` → `a_coke.mod`, `bf_pellets_in` → `c_pellets_bf.mod`.

Feeds: `coking_coal_in` (via coke), `bf_coalpci_in`, `bf_lime_in` →
`q_carbon_capture.mod` and `s_emissions.mod`; the gas streams →
`o_waste_heat.mod`; `bf_power_in`, `bf_trt_out` → `p_power_balance.mod`.

## Caveats

1. **PCI coal *rises* 0.15 → 0.16 t/thm.** Every other coefficient in the
   decarbonisation drift moves in the emissions-reducing direction; this one
   does not. It is presumably compensating for the falling coke rate
   (coke → PCI substitution is standard practice), but the net effect is that
   fossil injectant grows while the model is nominally decarbonising.

2. **The BF's decarbonisation is free.** Coke rate improvement and biomass
   PCI arrive on a fixed timetable with no capex, no ramp constraint, and no
   dependence on the emissions cap or carbon price. The BF-BOF route
   therefore gets an unearned emissions trajectory that improves its standing
   against the DRI routes, which must *build* their way to lower emissions.

3. **`bf_h2_in` is dead but still referenced.** Forced to zero by eq31, yet
   used in `yreport.mod`'s H2 capital allocation denominator. Removing the
   variable would require touching `yreport.mod`.

4. **The burden recipe is fixed.** Sinter/pellet/lump ratios (1.15/0.35/0.15)
   cannot be re-optimised, so the model cannot represent a shift to
   higher-pellet burdens — a real and relevant BF efficiency lever.

5. **Slag is produced at 0.30 t/thm and credited at 15 $/t**, with no cap on
   the cement market's ability to absorb it. At 2050 BF volumes this implies
   tens of Mt/yr of GGBS sold at a fixed price.

6. **No BF-specific capacity variable.** BF capacity is `cap_bof`, shared with
   the BOF, coke oven, sinter plant and pellet plant. The five assets have
   one lifetime (25 yr) and one utilisation band.

## Constraint index

`power_bf_in` (eq18) · `sinter_bf_in` (eq19) · `lime_bf_in` (eq20) ·
`slag_bf_out` (eq21) · `pellets_bf_in` (eq22) · `lumpore_bf_in` (eq23) ·
`bfg_bf_in` (eq24) · `cog_bf_in` (eq25) · `bfg_bf_out` (eq26) ·
`trt_power_out` (eq27) · `bf_coal_pci_balance` (eq28) ·
`bf_bio_pci_balance` (eq29) · `bf_coke_balance` (eq30) ·
`bf_h2_balance` (eq31) · **`bf_hot_metal_out` (eq32)** — the hot-metal /
scrap substitution closing the loop to `steel_bof`, described under
"Closing the loop" above.
