# `g_pellets_ngdri.mod` — pellet plant (NG-DRI)

> **Source:** `core/modules/g_pellets_ngdri.mod` — 7 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

Sizes the pellet plant feeding the natural-gas DRI shaft. Structurally
identical to the other three pellet modules.

## Declares

No parameters, no variables. Two equality constraints (eq42-eq43).

## Equations

| eq | Constraint | Relation | Defines |
|---|---|---|---|
| 42 | `pellets_ngdri_fineore_balance` | `ngdri_pellets_in[t] / ng_ore_pell` | `pellets_fineore_ngdri` |
| 43 | `pellets_ngdri_power_balance` | `ng_e_pell × ngdri_pellets_in[t]` = 200 kWh/t | `pellets_power_ngdri` |

`ngdri_pellets_in` is pinned by `j_dri_ng.mod` (eq53) at `n5_pel_dri = 1.5`
t-pellet per t-DRI — identical to the coal and H2 routes.

## Depends on

| Symbol | Owner |
|---|---|
| `ngdri_pellets_in` | `variables.mod`; **pinned by `j_dri_ng.mod`** (eq53) |
| `ng_e_pell`, `ng_ore_pell` | `definitions.mod` |

Feeds `r_cost.mod` (`cost_pellet_ngdri_def`) and `p_power_balance.mod`.

## Caveats

1. **`/ng_ore_pell` contradicts the parameter's stated meaning** — see
   `c_pellets_bf.md` caveat 1.

2. **No DR-grade pellet premium** — see `f_pellets_coaldri.md` caveat 2.

3. **All three DRI routes share `1.5 t pellets/t-DRI` and `0.1 t lump
   ore/t-DRI`.** Pellet and ore consumption is therefore identical across
   coal, NG and H2 DRI; the routes differ only in reductant, power and
   capital. That is a reasonable first-order assumption but removes any
   burden-quality distinction between shaft technologies.
