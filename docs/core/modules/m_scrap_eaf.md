# `m_scrap_eaf.mod` — dedicated scrap-EAF route

> **Source:** `core/modules/m_scrap_eaf.mod` — 21 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

The 100%-scrap secondary route: scrap melted directly to crude steel with no
iron-ore reduction step at all. This is the third and simplest of the three
top-level routes (BF-BOF, DRI-EAF, scrap-EAF), and the only one whose
emissions come almost entirely from electricity.

Seven proportional balances, all driven by `steel_scrap_eaf[t]`.

## Declares

No parameters, no variables. Seven equality constraints (eq70-eq76).

## Equations

| eq | Constraint | Coefficient (per tCS) | Defines |
|---|---|---|---|
| 70 | `scrap_eaf_power_balance` | `n8_e_eaf[t]` = **785 kWh** | `scrap_eaf_power_in` |
| 71 | `scrap_eaf_scrap_balance` | `n8_phi_eaf` = **1.1 t scrap** | `scrap_eaf_scrap_in` |
| 72 | `scrap_eaf_electrode_balance` | `n8_eltrd` = 0.003 t | `scrap_eaf_electrode_in` |
| 73 | `scrap_eaf_lime_balance` | `n8_ls` = 0.06 t | `scrap_eaf_lime_in` |
| 74 | `scrap_eaf_coal_balance` | `n8_cs` = 0.01 t | `scrap_eaf_coal_in` |
| 75 | `scrap_eaf_slag_balance` | `n8_ss` = 0.15 t | `scrap_eaf_slag_out` |
| 76 | `scrap_eaf_gas_balance` | `n8_eafg` = 3 GJ | `scrap_eaf_gas_out` |

### 785 vs 664 kWh

`n8_e_eaf = 785` is higher than the DRI-EAF's 664. `definitions.mod` records
the derivation: **75% induction furnace @ 825 kWh + 25% EAF @ 664 kWh**,
reflecting India's IF-heavy secondary sector. So the model's "scrap route" is
not a modern scrap EAF — it is the existing Indian secondary fleet, and its
power intensity is ~18% worse than the DRI-EAF's.

Like `n7_e_eaf`, it is a **defined param indexed over T but constant in t**,
so it cannot be `let` by a scenario and does not improve over the horizon.

### Emissions profile

`scope1_scrapeaf` (in `s_emissions.mod`) counts only
`scrap_eaf_coal_in × 2.64 + scrap_eaf_lime_in × 0.44` ≈ **0.053 tCO2/tCS**.
Everything else is Scope 2: 785 kWh × `n9_grid_ef[t]`, which at the 2025 EF
of 0.000886 is **0.70 tCO2/tCS** and at the θ_grid = 0.5 2050 EF of 0.00045
is **0.35 tCO2/tCS**.

So scrap-EAF's decarbonisation is entirely a function of the grid, and it is
the route most sensitive to `theta_grid`. It is also, at high grid EF, *not*
obviously cleaner than NG-DRI+CCS — which is precisely what the
`structural-sensitivity/grid` study probes.

### What limits this route

Nothing in this module. The three real constraints live elsewhere:

| Limit | Location |
|---|---|
| scrap availability | `t_additional_constraints.mod` `scrap_bound` (shared with BOF and DRI-EAF blends) |
| installed capacity | `v_capacity.mod` `cap_lim_scrap` / `min_util_scrap` (0.60) / `cap_add_scrap` |
| 2025 output = 0 | `t_additional_constraints.mod` `init_scrap_eaf` |

`cap0_scrap = 0.75 Mt` is the smallest incumbent fleet in the model, and
`life_scrap = 15` is the shortest lifetime — so scrap-EAF capacity built
early in the horizon retires and must be rebuilt before 2050.

Scrap is consumed at **1.1 t/tCS** here versus a *blend* elsewhere, so a
tonne of steel made on this route consumes 1.1 t of the same `n8_scrap_limit`
pool that the BOF and DRI-EAF blends draw on. The three uses compete
directly.

## Depends on

| Symbol | Owner |
|---|---|
| `steel_scrap_eaf` and its six input/output vars | `variables.mod` |
| `n8_*` | `definitions.mod` |

Feeds `n_steel_balance.mod`, `o_waste_heat.mod` (`scrap_eaf_gas_out`),
`p_power_balance.mod`, `s_emissions.mod`, `r_cost.mod`,
`t_additional_constraints.mod` (`scrap_bound`), `v_capacity.mod`
(`cap_lim_scrap`, scrap chain, coal chain).

## Caveats

1. **785 kWh/tCS locks in today's IF-heavy fleet for 26 years.** New
   scrap-EAF capacity built in 2045 is charged the same 75%-IF blended power
   intensity as the 2025 fleet, even though a new-build would be a modern EAF
   at ~500-600 kWh/tCS. This systematically penalises the scrap route, and
   because `n8_e_eaf` is a defined param it cannot be swept without editing
   `definitions.mod`.

2. **There is no `f_scrap` variable.** The scrap-EAF share is computed
   residually in `yreport.mod` as
   `1 − f_bof − f_cdri·f_eaf − f_ngdri·f_eaf − (1−f_cdri−f_ngdri)·f_eaf`,
   which algebraically reduces to `1 − f_bof − f_eaf`. The long form in the
   report is arithmetically correct but obscures that.

3. **Scrap quality is not modelled.** All scrap is one grade at one price
   (350 $/t), usable interchangeably as 100% charge here or as a blend
   elsewhere. Real secondary steelmaking is constrained by residuals (copper,
   tin), which is the main physical reason 100%-scrap steel cannot simply
   scale to meet all demand.

4. **`init_scrap_eaf: steel_scrap_eaf[2025] = 0`** while
   `cap0_scrap = 0.75 Mt`. So the route starts with capacity it is forbidden
   to use, which pays `fopex_scrap` in 2025 for nothing. Minor, but it makes
   `min_util_scrap = 0.60` inconsistent in the first year — the floor is only
   applied for `t > first(T)`, which is why this does not make the model
   infeasible.

5. **Slag from the scrap-EAF is credited at 15 $/t like BF slag.** EAF slag
   has materially lower value than granulated BF slag; the model treats them
   identically.
