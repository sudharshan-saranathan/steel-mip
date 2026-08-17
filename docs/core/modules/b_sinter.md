# `b_sinter.mod` — sinter plant

> **Source:** `core/modules/b_sinter.mod` — 29 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

Agglomerates fine iron ore into sinter for the blast furnace burden, fired by
coke breeze with a rising biochar substitution. Recovers sensible heat from
the sinter cooler as power, and vents sinter gas.

Like the coke oven, every flow is **proportional to `bf_sinter_in[t]`** — the
sinter the blast furnace demands. The plant has no autonomy.

## Declares

No parameters, no variables. Seven equality constraints (eq9-eq15).

## Equations

| eq | Constraint | Coefficient | Defines |
|---|---|---|---|
| 9 | `sinter_power_balance` | `n1_e_sint` = 50 kWh/t-sinter | `sinter_power_in` |
| 10 | `sinter_lime_balance` | `n1_lime_sint` = 0.04 t/t | `sinter_lime_in` |
| 11 | `sinter_fineore_balance` | `n1_ore_sint` = 0.9 t/t | `sinter_fineore_in` |
| 12 | `sinter_breeze_balance` | **interpolated** 0.09 → 0.058 | `sinter_breeze_in` |
| 13 | `sinter_biochar_balance` | **interpolated** 0.0 → 0.022 | `sinter_biochar_in` |
| 14 | `sinter_whr_balance` | `n1_sintcool_whr` = 30 kWh/t | `sinterwaste_power_out` |
| 15 | `sinter_gas_balance` | `n1_sintgas_sint × ng_sintgas_cv` = 1800 × 0.0006 = **1.08 GJ/t** | `sg_out` |

### The fuel-switching interpolation (eq12, eq13)

These two are the only non-constant coefficients in the module, and they are
written out inline rather than using a defined param:

```ampl
(n1_brz_sint_25 + (n1_brz_sint_50 - n1_brz_sint_25) * (t - 2025)/(2050 - 2025))
    * bf_sinter_in[t] - sinter_breeze_in[t] = 0;
```

| Year | breeze (t/t-sinter) | biochar (t/t-sinter) |
|---|---|---|
| 2025 | 0.090 | 0.000 |
| 2050 | 0.058 | 0.022 |

Coke breeze falls by 0.032 while biochar rises by 0.022 — a **partial**
substitution, roughly 0.69 t biochar per t breeze displaced, consistent with
biochar's lower calorific value. The source comment caps the intent at
*"Biochar replacement is limited to 20%"*; 0.022/0.09 ≈ 24% of the 2025
breeze rate, so the coded path sits marginally above the stated cap.

**This substitution is exogenous and unconditional.** It happens on a fixed
schedule regardless of biochar price (60 $/t), breeze price (85 $/t), or the
emissions cap. It is not a decision the optimiser makes — it is a
fuel-switching assumption baked into the BF-BOF route.

### Sinter gas

`sg_out` is defined (1.08 GJ/t-sinter) but **never consumed by any other
constraint**. It does not appear in `o_waste_heat.mod`'s pool, in
`p_power_balance.mod`, or in any cost or emissions equation. The
`definitions.mod` comment explains why: *"Remaining sinter gas is waste with
very low energy value"* — at 0.0006 GJ/Nm³ it is roughly 1/30th the
calorific value of COG. It is computed and discarded.

## Depends on

| Symbol | Owner |
|---|---|
| `bf_sinter_in` | `variables.mod`; **pinned by `d_blast_furnace.mod`** (eq19) |
| `n1_*`, `ng_sintgas_cv` | `definitions.mod` |

Feeds:
- `sinter_lime_in` → `q_carbon_capture.mod`, `s_emissions.mod` (calcination CO2)
- `sinter_fineore_in`, `sinter_breeze_in`, `sinter_biochar_in` → `r_cost.mod`
- `sinter_power_in`, `sinterwaste_power_out` → `p_power_balance.mod`
- `sg_out` → **nothing**

## Caveats

1. **Biochar is unpriced against its alternative.** The breeze→biochar switch
   is on a fixed schedule, so the model never compares the 60 $/t biochar
   cost against the 85 $/t breeze it replaces, nor against the emissions
   benefit. Biochar carries **no emission factor at all** in
   `s_emissions.mod` (implicitly biogenic/net-zero), which makes the switch a
   free emissions reduction the optimiser neither chooses nor pays for.

2. **The coded biochar path slightly exceeds the documented 20% cap** (24%
   of the 2025 breeze rate by 2050). Minor, but the comment and the numbers
   disagree.

3. **`sg_out` is a dead variable.** It is fully determined by eq15 and read
   by nothing. Harmless (presolve removes it) but misleading — a reader may
   assume sinter gas is recovered somewhere.

4. **No sinter capacity or capex.** `n1_capex` (30 $/tCS) is folded into
   `acapex_bof`; the plant cannot be built, retired or utilised
   independently of the BF-BOF route.

5. **Sinter is BF-only.** There is no pellet/sinter trade-off — the blast
   furnace burden split (1.15 t sinter, 0.35 t pellets, 0.15 t lump ore per
   thm) is fixed in `d_blast_furnace.mod` and never optimised.
