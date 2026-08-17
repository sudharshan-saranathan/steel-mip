# `h_pellets_h2dri.mod` — pellet plant (H2-DRI)

> **Source:** `core/modules/h_pellets_h2dri.mod` — 8 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

Sizes the pellet plant feeding the hydrogen DRI shaft. Structurally identical
to the other three pellet modules.

## Declares

No parameters, no variables. Two equality constraints (eq44-eq45).

## Equations

| eq | Constraint | Relation | Defines |
|---|---|---|---|
| 44 | `pellets_h2dri_fineore_balance` | `h2dri_pellets_in[t] / ng_ore_pell` | `pellets_fineore_h2dri` |
| 45 | `pellets_h2dri_power_balance` | `ng_e_pell × h2dri_pellets_in[t]` = 200 kWh/t | `pellets_power_h2dri` |

`h2dri_pellets_in` is pinned by `k_dri_h2.mod` (eq58) at `n6_pel_dri = 1.5`
t-pellet per t-DRI.

## Depends on

| Symbol | Owner |
|---|---|
| `h2dri_pellets_in` | `variables.mod`; **pinned by `k_dri_h2.mod`** (eq58) |
| `ng_e_pell`, `ng_ore_pell` | `definitions.mod` |

Feeds `r_cost.mod` (`cost_pellet_h2dri_def`) and `p_power_balance.mod`.

## Caveats

1. **`/ng_ore_pell` contradicts the parameter's stated meaning** — see
   `c_pellets_bf.md` caveat 1.

2. **Pellet-plant power is drawn from the *grid*, not the dedicated
   renewables.** `pellets_power_h2dri` appears in `p_power_balance.mod` and
   therefore carries the grid emission factor in `scope2_def`. Only the
   electrolyser load is behind the meter. This is correct — pelletising is
   not part of the green-H2 supply chain — but it means "green" H2-DRI steel
   still carries grid Scope-2 from pelletising (300 kWh/t-DRI), the shaft
   (110 kWh/t-DRI) and the EAF (664 kWh/tCS).

3. **No DR-grade pellet premium**, and H2-DRI is the route most dependent on
   high-grade pellets in practice — see `f_pellets_coaldri.md` caveat 2.
