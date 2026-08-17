# `e_bof.mod` — basic oxygen furnace

> **Source:** `core/modules/e_bof.mod` — 35 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

Converts hot metal (plus a scrap blend) into crude steel, and — via
`bof_steel_fraction` — ties the BF-BOF route's output to the route share
variable `f_bof[t]`. Also carries the **scrap blending policy** for the
BF-BOF route: a pinned 2025 share, a min/max band thereafter, and a
year-on-year ramp limit.

## Declares

No parameters, no variables. Eleven constraints (eq33-eq39, with eq34
split into five parts).

## Equations

### Proportional balances

| eq | Constraint | Coefficient (per tCS) | Defines |
|---|---|---|---|
| 33 | `bof_power_balance` | `n3_e_bof` = 174 kWh | `bof_power_in` |
| 35 | `bof_lime_balance` | `n3_ls_bof` = 0.075 t | `bof_lime_in` |
| 36 | `bof_slag_balance` | `n3_sl_bof` = 0.10 t | `bof_slag_out` |
| 37 | `bof_gas_out` | 100 Nm³ × 0.008 = **0.80 GJ** | `bofgas_out` |
| 39 | `bof_cog_balance` | 65 Nm³ × 0.018 = **1.17 GJ** | `bof_cog_in` |

The BOF is a net gas *consumer*: it makes 0.80 GJ of BOFG and burns 1.17 GJ
of imported COG per tCS.

### Route share (eq38)

```ampl
f_bof[t] * dem[t] - steel_bof[t] = 0;
```

Defines `f_bof[t]` as the BF-BOF share of total demand. This is the model's
headline output variable — the "how much steel still comes from blast
furnaces in 2050?" number. Its 2025 value is pinned at **0.51** by
`init_f_bof` in `t_additional_constraints.mod`.

Note this is an *identity*, not a constraint on behaviour: `f_bof` has no
independent meaning beyond `steel_bof/dem`. Since `dem[t]` is a parameter,
eq38 is linear.

### The scrap blend block (eq34a-e)

Five constraints, and the pattern is repeated verbatim for coal-DRI and
NG-DRI:

```ampl
# a. 2025 pinned to the observed share — an EQUALITY
bof_scrap_in[first(T)] = phi0_bof * n3_metallic_bof * steel_bof[first(T)];

# b,c. band thereafter
bof_scrap_in[t] <= phi_max_bof * n3_metallic_bof * steel_bof[t];   # 0.20
bof_scrap_in[t] >= phi_min_bof * n3_metallic_bof * steel_bof[t];   # 0.05

# d,e. symmetric ramp limit
|bof_scrap_in[t] - bof_scrap_in[prev(t)]| <= blend_ramp * n3_metallic_bof * steel_bof[t];
```

with `phi0_bof = 0.09`, `phi_max_bof = 0.20`, `phi_min_bof = 0.05`,
`blend_ramp = 0.05`, and `n3_metallic_bof = 1.1`.

Reading the ramp: the year-on-year *absolute* change in scrap tonnage is
capped at 5% of the current year's metallic charge. Starting from 9% in
2025, the route can reach the 20% ceiling by 2028 at the earliest — so the
band, not the ramp, is the binding limit over most of the horizon.

Because `d_blast_furnace.mod`'s eq32 sets
`bf_hot_metal = 1.1·steel_bof − bof_scrap_in`, raising the scrap share
directly shrinks the entire ironmaking chain. A move from 9% to 20% scrap
cuts hot metal (and therefore coke, sinter, coking coal and BF CO2) by about
**12%** per tonne of BOF steel.

The min floor of 5% is a *floor*, not a target: the model may not go below
5% scrap in the BOF even if scrap becomes scarce and expensive. Combined with
`scrap_bound` in `t_additional_constraints.mod`, this can in principle make a
scenario infeasible — a scarce-scrap world still has to feed the BOF.

## Depends on

| Symbol | Owner |
|---|---|
| `steel_bof`, `bof_scrap_in`, `f_bof` | `variables.mod` |
| `dem` | `definitions.mod` |
| `n3_*`, `phi0_bof`, `phi_min_bof`, `phi_max_bof`, `blend_ramp` | `definitions.mod` |

`bof_scrap_in` is also read by `d_blast_furnace.mod` (eq32),
`t_additional_constraints.mod` (`scrap_bound`), `v_capacity.mod`
(scrap chain) and `r_cost.mod`.

## Caveats

1. **The 2025 blend is an equality, so 2025 is not optimised.** `phi0_bof`,
   `phi0_cdri` and `phi0_ngdri` pin the first year to observed data. Combined
   with `init_f_bof`, `init_f_eaf`, `init_scrap_eaf`, `init_f_cdri` and the
   `legacy_init_*` seeds, the whole of 2025 is a fixed calibration point.
   Any objective difference between scenarios comes entirely from 2026-2050.

2. **`phi_min_bof = 0.05` is a hard floor with no relief valve.** If a
   scenario tightens `n8_scrap_limit` far enough, the combination of this
   floor and `scrap_bound` becomes infeasible. Note that the scrap-scarcity
   axis is exactly what `structural-sensitivity/scrap` sweeps.

3. **The ramp constraint is scaled by the *current* year's charge**, not the
   previous year's. Under falling BOF output the allowed absolute change
   shrinks, which is the intended direction; under a route collapsing to
   zero, `steel_bof[t] → 0` forces `bof_scrap_in[t] → bof_scrap_in[t−1]`
   only in relative terms, and both go to zero together. No pathology, but
   the asymmetry is worth knowing.

4. **BOFG is produced (0.80 GJ/tCS) and routed to the waste-heat pool**, per
   the `definitions.mod` comment *"All BOFG gas assumed being routed to
   power plant"*. It is not used as a chemical feedstock or exported.

5. **Oxygen is not modelled** — no ASU power, no oxygen cost. At ~50-60
   kWh/tCS for air separation this is a material omission from BF-BOF's
   power draw, and it is not obviously included in the 174 kWh/tCS figure.

## Constraint index

| Constraint | eq | Covered under |
|---|---|---|
| `bof_power_balance` | 33 | Proportional balances |
| `bof_scrap_blend0` | 34a | The scrap blend block — 2025 equality pin |
| `bof_scrap_blend_max` | 34b | The scrap blend block — ceiling 0.20 |
| `bof_scrap_blend_min` | 34c | The scrap blend block — floor 0.05 |
| `bof_scrap_ramp_up` | 34d | The scrap blend block — +5 pp/yr |
| `bof_scrap_ramp_dn` | 34e | The scrap blend block — −5 pp/yr |
| `bof_lime_balance` | 35 | Proportional balances |
| `bof_slag_balance` | 36 | Proportional balances |
| `bof_gas_out` | 37 | Proportional balances |
| `bof_steel_fraction` | 38 | Route share |
| `bof_cog_balance` | 39 | Proportional balances |
