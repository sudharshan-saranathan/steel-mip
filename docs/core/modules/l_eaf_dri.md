# `l_eaf_dri.mod` — DRI-based EAF

> **Source:** `core/modules/l_eaf_dri.mod` — 36 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

The **shared** electric arc furnace that melts the output of all three DRI
shafts. There is one EAF pool, not three: coal, NG and H2 DRI feed a common
`steel_eaf[t]`, and the EAF's consumables (power, electrode, lime, coal,
slag, off-gas) are charged on that aggregate.

Also defines `f_eaf[t]`, the second of the model's two route-share variables.

## Declares

No parameters, no variables. Nine equality constraints (eq61-eq69).

## Equations

### Route share (eq61)

```ampl
f_eaf[t] * dem[t] - steel_eaf[t] = 0;
```

`f_eaf[t]` is the DRI-EAF share of total demand — the counterpart to
`f_bof[t]` in `e_bof.mod`. Pinned to **0.49** in 2025 by `init_f_eaf`.
Together with `init_f_bof = 0.51` and `init_scrap_eaf = 0`, the 2025 split is
fully determined: 51% BF-BOF, 49% DRI-EAF, 0% dedicated scrap-EAF.

### Consumables, proportional to `steel_eaf` (eq62, 64-68)

| eq | Constraint | Coefficient (per tCS) | Defines |
|---|---|---|---|
| 62 | `eaf_power_balance` | `n7_e_eaf[t]` = **664 kWh** | `eaf_power_in` |
| 64 | `eaf_electrode_balance` | `n7_eltrd` = 0.003 t | `eaf_electrode_in` |
| 65 | `eaf_lime_balance` | `n7_ls` = 0.06 t | `eaf_lime_in` |
| 66 | `eaf_coal_balance` | `n7_cs` = 0.01 t | `eaf_coal_in` |
| 67 | `eaf_slag_balance` | `n7_ss` = 0.15 t | `eaf_slag_out` |
| 68 | `eaf_gas_out` | `n7_eafg` = 3 GJ | `eafgas_out` |

`n7_e_eaf` is declared in `definitions.mod` as a *defined* param indexed over
T but constant at 664 — the DRI-EAF/IF weighted figure on a gas-DRI all-EAF
basis. Coal-DRI's extra induction-furnace power is **not** here; it is
carried in `n4_e_dri = 217` (see `i_dri_coal.md`). That decomposition is
recorded only in comments and is easy to break.

### Scrap aggregation (eq63)

```ampl
coaldri_scrap_in[t] + ngdri_scrap_in[t] + h2dri_scrap_in[t] - eaf_scrap_in[t] = 0;
```

`eaf_scrap_in` is a pure roll-up of the three routes' blend decisions — no
new degree of freedom. It exists so `scrap_bound`
(`t_additional_constraints.mod`), `v_capacity.mod`'s scrap chain, and
`r_cost.mod` can each reference one variable rather than three.

### The alias (eq69)

```ampl
steel_eaf[t] - dri_eaf_steel_out[t] = 0;
```

Ties the EAF's output to `k_dri_h2.mod`'s route split. The two names are the
same quantity — see `variables.md` caveat 3.

## Depends on

| Symbol | Owner |
|---|---|
| `coaldri_scrap_in` | `modules/i_dri_coal.mod` |
| `ngdri_scrap_in` | `modules/j_dri_ng.mod` |
| `h2dri_scrap_in` | `modules/k_dri_h2.mod` |
| `dri_eaf_steel_out` | `modules/k_dri_h2.mod` (eq56) |
| `dem` | `definitions.mod` |
| `n7_*` | `definitions.mod` |

Feeds `n_steel_balance.mod`, `o_waste_heat.mod` (`eafgas_out`),
`p_power_balance.mod`, `s_emissions.mod`, `r_cost.mod`, `v_capacity.mod`.

## Caveats

1. **One EAF for three DRI routes means the EAF's cost and emissions cannot
   be attributed to a route from the model's variables.** `yreport.mod`
   works around this by allocating `cost_eaf[t]` and `eaf_power_in[t]` by the
   route share `f_cdri`/`f_ngdri`/`(1−f_cdri−f_ngdri)` — a proportional
   allocation, not a modelled split. Per-route $/tCS and tCO2/tCS numbers
   inherit that approximation.

2. **The 664 vs 217 power decomposition is comment-only.** If `n7_e_eaf` is
   ever changed, `n4_e_dri` must be changed in step or coal-DRI's power
   double-counts (or under-counts). Nothing in the model enforces the
   relationship.

3. **The EAF is not a capacity asset.** There is no `cap_eaf` — EAF capital
   (`n7_capex = 70 $/tCS`) is folded into each DRI route's `acapex_*` in
   `definitions.mod`, and `cap_cdri`/`cap_ngdri`/`cap_h2dri` are the
   route-level constraints. So three DRI routes each carry their own notional
   EAF, but the *physical* melting is pooled. That is inconsistent, though
   the effect is only on how capital is booked, not on flows.

4. **EAF off-gas is 3 GJ/tCS with no route distinction**, and
   `o_waste_heat.mod` routes all of it into the recovery pool. An H2-DRI EAF
   and a coal-DRI/IF melt shop produce very different off-gas; the model
   averages them.

5. **`n7_cs = 0.01` t coal/tCS is charcoal/carbon injection** and carries
   2.64 tCO2/t in `scope1_def` — so even the H2 route emits ≈0.026 tCO2/tCS
   from EAF carbon, plus lime calcination and electrode oxidation. Correct,
   and the reason `scope1_h2dri` is non-zero.

## Constraint index

| Constraint | eq | Covered under |
|---|---|---|
| `eaf_steel_fraction` | 61 | Route share |
| `eaf_power_balance` | 62 | Consumables |
| `eaf_scrap_balance` | 63 | Scrap aggregation |
| `eaf_electrode_balance` | 64 | Consumables |
| `eaf_lime_balance` | 65 | Consumables |
| `eaf_coal_balance` | 66 | Consumables |
| `eaf_slag_balance` | 67 | Consumables |
| `eaf_gas_out` | 68 | Consumables |
| `dri_eaf_steel_relation` | 69 | The alias |
