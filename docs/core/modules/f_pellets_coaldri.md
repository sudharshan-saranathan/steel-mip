# `f_pellets_coaldri.mod` — pellet plant (coal-DRI)

> **Source:** `core/modules/f_pellets_coaldri.mod` — 7 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

Sizes the pellet plant feeding the coal-DRI shaft. Structurally identical to
`c_pellets_bf.mod`, `g_pellets_ngdri.mod` and `h_pellets_h2dri.mod` — only
the driving variable differs.

## Declares

No parameters, no variables. Two equality constraints (eq40-eq41).

## Equations

| eq | Constraint | Relation | Defines |
|---|---|---|---|
| 40 | `pellets_coaldri_fineore_balance` | `coaldri_pellets_in[t] / ng_ore_pell` | `pellets_fineore_coaldri` |
| 41 | `pellets_coaldri_power_balance` | `ng_e_pell × coaldri_pellets_in[t]` = 200 kWh/t | `pellets_power_coaldri` |

`coaldri_pellets_in` is itself pinned by `i_dri_coal.mod`'s
`coaldri_pellets_balance` at `n4_pel_dri = 1.5` t-pellet per t-DRI. Chaining:

```
1 t DRI → 1.5 t pellets → 1.364 t fine ore + 300 kWh
```

The `/ng_ore_pell` division (0.909 t ore per t pellet) is the same
comment/code inconsistency documented in `c_pellets_bf.md` — see its Caveats.

## Depends on

| Symbol | Owner |
|---|---|
| `coaldri_pellets_in` | `variables.mod`; **pinned by `i_dri_coal.mod`** (eq48) |
| `ng_e_pell`, `ng_ore_pell` | `definitions.mod` |

Feeds `r_cost.mod` (`cost_pellet_coaldri_def`) and `p_power_balance.mod`.

## Caveats

1. **`/ng_ore_pell` contradicts the parameter's stated meaning** — see
   `c_pellets_bf.md` caveat 1. Applied identically here, so route-neutral.

2. **DR-grade pellets are not distinguished from BF-grade.** DRI requires
   higher-iron, lower-gangue pellets that cost materially more and are supply
   constrained; the model uses the same 200 kWh/t and the same 65 $/t fine
   ore as the blast-furnace pellet plant. This flatters all three DRI routes
   equally against BF-BOF.

3. **No pellet capacity constraint.** `ng_capex_pell = 10 $/tCS` is bundled
   into `acapex_cdri`; the pellet plant scales instantly with the DRI shaft.
