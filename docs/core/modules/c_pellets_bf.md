# `c_pellets_bf.mod` — pellet plant (blast furnace)

> **Source:** `core/modules/c_pellets_bf.mod` — 6 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

Sizes the pellet plant that feeds the blast furnace burden. Two proportional
balances: electricity, and the fine ore consumed to make the pellets.

One of four near-identical pellet modules — see also
`f_pellets_coaldri.md`, `g_pellets_ngdri.md`, `h_pellets_h2dri.md`.

## Declares

No parameters, no variables. Two equality constraints (eq16-eq17).

## Equations

| eq | Constraint | Relation | Defines |
|---|---|---|---|
| 16 | `pellets_bf_power_balance` | `ng_e_pell × bf_pellets_in[t]` = 200 kWh/t-pellet | `pellets_bf_power` |
| 17 | `pellets_bf_fineore_balance` | `bf_pellets_in[t] / ng_ore_pell` | `pellets_fineore_bf` |

### The ore coefficient is a division, not a multiplication

```ampl
bf_pellets_in[t] / ng_ore_pell - pellets_fineore_bf[t] = 0;
```

`ng_ore_pell = 1.1` is documented in `definitions.mod` as *"Iron ore (ton)
per ton of pellets"*. Dividing by it gives **0.909 t ore per t pellet** —
i.e. the code treats 1.1 as *pellets per tonne of ore* (a yield), the
reciprocal of what the comment says.

This is a genuine inconsistency between the comment and the arithmetic, and
it points the wrong way physically: pelletising has mass losses, so ore input
should **exceed** pellet output, not fall short of it. The same division
appears in all four pellet modules, so at least it is consistent across
routes and cannot distort the route comparison — it understates ore purchase
cost by ~17% uniformly (0.909 vs 1.1 t/t). See Caveats.

## Depends on

| Symbol | Owner |
|---|---|
| `bf_pellets_in` | `variables.mod`; **pinned by `d_blast_furnace.mod`** (eq22, 0.35 t/thm) |
| `ng_e_pell`, `ng_ore_pell` | `definitions.mod` |

Feeds:
- `pellets_fineore_bf` → `r_cost.mod` (`cost_pellet_bf_def`, at 65 $/t)
- `pellets_bf_power` → `p_power_balance.mod`, `r_cost.mod`

## Caveats

1. **The ore/pellet ratio contradicts its own comment.** `/ng_ore_pell`
   yields 0.909 t ore per t pellet, while the declaration reads *"Iron ore
   (ton) per ton of pellets" = 1.1*, which would require `× ng_ore_pell`.
   Applied identically in all four pellet modules, so it is route-neutral —
   but it understates iron-ore consumption and cost across the board by
   about 17%, and it makes pelletising appear to *create* mass.

2. **No pellet plant capacity, build decision or lifetime.**
   `ng_capex_pell = 10 $/tCS` is added into every route's `acapex_*` in
   `definitions.mod`, so pellet capacity is implicitly bundled with whichever
   steelmaking route consumes it.

3. **Four separate pellet modules for identical physics.** The BF, coal-DRI,
   NG-DRI and H2-DRI pellet plants differ only in which variable feeds them.
   They exist as separate variables so the report can attribute pellet cost
   and power by route; the duplication means a coefficient change must be
   made in four places.

4. **No pellet-grade distinction.** DRI requires higher-grade (DR-grade)
   pellets than the blast furnace, with materially different ore
   requirements and cost. The model uses one `ng_e_pell` and one
   `ng_ore_pell` for all four.
