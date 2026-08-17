# `variables.mod` — decision variables

> **Source:** `core/variables.mod` — 169 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

Declares 128 variable blocks, each indexed over `T` (2025-2050), numbered
`X[1]`…`X[128]` in trailing comments. Every one is **continuous and
non-negative**; there are no integer or binary variables anywhere in
`variables.mod`, and none are added by any module. The model is a **pure
linear program** (see `model.md` for the measured confirmation).

Included second, after `definitions.mod` — it needs `dem[t]` for two bounds.

Note this file is *not* the complete variable list: `v_capacity.mod` declares
another 30 blocks (builds, legacy fleet, installed capacity, supply chains,
electrolyser/RE, CCS retrofit capacity) mid-file. See `modules/v_capacity.md`.

## The 128 blocks by group

### Ironmaking chain (BF-BOF)

| Group | Vars | Notes |
|---|---|---|
| Coke oven | `X[1]`–`X[8]` | `coke_power_in`, `coking_coal_in`, `coke_breeze_out`, `tar_out`, `cog_out`, `cdq_power_out`, `cokeov_cog_in`, `cokeov_bfg_in` |
| Sinter plant | `X[9]`–`X[15]` | incl. `sinterwaste_power_out`, `sg_out` |
| BF pellet plant | `X[16]`–`X[17]` | |
| Blast furnace | `X[18]`–`X[32]` | `bf_hot_metal` is the driver; the other 14 are proportional to it |
| BOF | `X[33]`–`X[39]` | `steel_bof` is the route output |

The whole BF-BOF chain is driven backwards from `steel_bof[t]`:
`steel_bof` → `bf_hot_metal` → `bf_sinter_in`, `bf_coke_in`, `bf_pellets_in`
→ their own inputs. Every link is an equality with a fixed coefficient, so
the entire chain collapses to a scalar multiple of `steel_bof[t]` — see the
"chain arithmetic" note in `modules/d_blast_furnace.md`.

### DRI routes

Each of the three routes has an identical variable shape:

| | coal | NG | H2 |
|---|---|---|---|
| pellet plant | `X[40]`–`X[41]` | `X[42]`–`X[43]` | `X[44]`–`X[45]` |
| route steel output | `coaldri_output` `X[46]` | `ngdri_output` `X[53]` | `h2dri_output` `X[60]` |
| DRI from the shaft | `coaldri_dri_out` `X[47]` | `ngdri_dri_out` `X[54]` | `h2dri_dri_out` `X[61]` |
| scrap into the charge | `coaldri_scrap_in` `X[48]` | `ngdri_scrap_in` `X[55]` | `h2dri_scrap_in` `X[62]` |
| pellets, reductant, power, lump ore | `X[49]`–`X[52]` | `X[56]`–`X[59]` | `X[63]`–`X[66]` |

The `_output` / `_dri_out` distinction is easy to misread and matters
everywhere:

- **`<route>_output`** = **crude steel** attributable to that route (tCS)
- **`<route>_dri_out`** = **DRI** produced by that route's shaft (t-DRI)

They are linked by the metallic-charge balance
`dri_out + scrap_in = 1.1 × output`, so DRI and scrap are substitutes at 1:1
inside a fixed 1.1 t charge per tCS.

Two bounds are declared here and nowhere else:

```ampl
var coaldri_output{t in T} >= 0, <= dem[t];   # X[46]
var ngdri_output{t in T}   >= 0, <= dem[t];   # X[53]
```

`h2dri_output` deliberately carries **no** such bound. The two that do have
it are **provably redundant** — see Caveats.

### Steelmaking and totals

| Group | Vars |
|---|---|
| DRI-EAF | `X[67]`–`X[75]`; `steel_eaf` is the route output, `dri_eaf_steel_out` its alias |
| Scrap-EAF | `X[76]`–`X[83]`; `steel_scrap_eaf` is the route output |
| Steel balance | `total_steel` `X[84]` |
| Power balance | `grid_power_in` `X[85]` |

`steel_eaf` and `dri_eaf_steel_out` are held equal by
`dri_eaf_steel_relation` in `l_eaf_dri.mod`. The duplication is historical:
one name is the EAF's *output*, the other is the *sum of the three DRI
routes*. See Caveats.

### Waste heat

`X[86]`–`X[92]`. The pool has a two-stage structure:

```
wasteheat_bf_bof + wasteheat_eaf + scrap_eaf_wasteheat   (raw GJ)
        ↓ ×0.3
whr_available_gas                                        (accessible GJ)
        ↓ × n9_whr[t], split by the optimiser
whr_gas_to_power   +   whr_gas_to_steam
        ↓ ×277.78×n9_eta       ↓ ×whr_steam_eff
whr_power_generated            ccs_steam_whr
```

`whr_gas_to_power` and `whr_gas_to_steam` are the only genuine *allocation*
decision in the waste-heat block — everything upstream is proportional.

### Carbon capture

`X[93]`–`X[99]`. `ccs_bf`, `ccs_cdri`, `ccs_ngdri` are tonnes of CO2
captured per route (free decisions, bounded three ways); `total_ccs` is
their sum; `power_ccs` and the two steam variables (`ccs_steam_whr`,
`ccs_steam_boiler`) are the energy penalty.

### Cost accounting

`X[100]`–`X[115]`. One variable per unit operation plus `total_cost`. These
are **not decisions** — every one is pinned by an equality in `r_cost.mod`.
They exist so the report can decompose cost by process without re-deriving
it. Declaring them `>= 0` is a modelling assertion, not an accounting one:
see Caveats.

### Emissions

`X[116]`–`X[123]`. Per-route Scope 1, plus `scope1_emissions` (total),
`scope2_emissions` (grid), and `total_emissions` = Scope1 + Scope2 − captured.
All pinned by equalities in `s_emissions.mod`.

### Route-share and capture-base auxiliaries

`X[124]`–`X[128]`:

- `co2_capturable_bf/cdri/ngdri` — the physical CO2 base available to capture
  on each route, defined in `q_carbon_capture.mod`.
- **`f_bof{t} ∈ [0,1]`** and **`f_eaf{t} ∈ [0,1]`** — the route shares of
  demand. These carry the only non-trivial upper bound in the file, and they
  are the model's headline outputs: `f_bof[t]·dem[t] = steel_bof[t]` and
  `f_eaf[t]·dem[t] = steel_eaf[t]`.

Note there is **no `f_scrap`** — the scrap-EAF share is whatever is left,
and the report computes it as `1 − f_bof − f_eaf`.

## Depends on

- `dem{t}` from `definitions.mod` (the two `<= dem[t]` bounds).
- `set T` from `model.mod`.

## Caveats

1. **`coaldri_output` and `ngdri_output` carry a redundant `<= dem[t]`
   bound.** The chain
   `coaldri_output ≤ coaldri+ngdri+h2dri = dri_eaf_steel_out = steel_eaf
   ≤ total_steel = dem[t]` (via `k_dri_h2:4`, `l_eaf_dri:36`,
   `n_steel_balance:4`, `t_additional_constraints:10`) makes it implied, all
   intermediates being `>= 0`. It was present in five of the eight legacy
   studies and absent in three; core keeps it. Harmless, but it means the two
   coal/NG routes and the H2 route are declared asymmetrically for no reason.
   It also *silently becomes non-redundant* if a variant model drops
   `meet_demand` — `regret-analysis` does exactly that, replacing it with
   `total_steel + steel_import = dem`, which happens to preserve
   `total_steel ≤ dem` and so keeps the bound inert.

2. **All 16 cost variables are declared `>= 0`.** For most that is safe, but
   `cost_cokeov` nets off breeze, tar and CDQ power credits, and `cost_bf`
   nets off TRT power and slag credits. A parameterisation with high credits
   and low input costs would make a genuinely negative process cost
   infeasible rather than negative — the LP would report infeasibility from
   a *variable bound*, which is very hard to diagnose. Not triggered at
   current prices; worth knowing before anyone raises the credit values.

3. **`steel_eaf` and `dri_eaf_steel_out` are the same quantity under two
   names**, joined by an equality constraint. Presolve eliminates one, so
   there is no numerical cost — but every downstream expression has to pick
   one, and both are used in different places (`l_eaf_dri.mod` uses
   `steel_eaf`, `k_dri_h2.mod` uses `dri_eaf_steel_out`, `yreport.mod` uses
   both). Collapsing them would remove a class of copy-paste error.

4. **The `X[n]` numbering is decorative** — nothing in the model indexes by
   it. If variables are added or removed the numbering will drift out of
   sync with any external document that relies on it.

5. **No variable has an upper bound reflecting physical plant capacity here**
   — all capacity limits arrive later, in `v_capacity.mod`. Reading this file
   alone gives the impression the model is unbounded above; it is not.
