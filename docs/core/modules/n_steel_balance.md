# `n_steel_balance.mod` — total crude steel balance

> **Source:** `core/modules/n_steel_balance.mod` — 4 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

The one-line constraint that joins the model's three top-level routes into a
single production total. Smallest module in the model, and structurally one
of the most important: it is the junction through which `meet_demand`
propagates back into every route.

## Declares

No parameters, no variables. One equality constraint (eq77).

## Equations

```ampl
s.t. steel_balance{t in T}:
    steel_eaf[t] + steel_bof[t] + steel_scrap_eaf[t] - total_steel[t] = 0;
```

| Term | Route | Share variable |
|---|---|---|
| `steel_bof` | BF-BOF | `f_bof[t]` (eq38) |
| `steel_eaf` | DRI-EAF (coal + NG + H2 pooled) | `f_eaf[t]` (eq61) |
| `steel_scrap_eaf` | dedicated scrap-EAF | *(residual — no variable)* |

### Why this constraint carries so much weight

`total_steel[t]` is pinned to `dem[t]` by `meet_demand` in
`t_additional_constraints.mod`. Substituting:

```
f_bof[t]·dem[t] + f_eaf[t]·dem[t] + steel_scrap_eaf[t] = dem[t]
⇒ f_bof[t] + f_eaf[t] + steel_scrap_eaf[t]/dem[t] = 1
```

So the route shares are forced to sum to one, and **the model's entire
decision is a reallocation, never an expansion**. Demand is exogenous; the
only question is which routes serve it.

This also makes the redundancy noted in `variables.md` explicit: since
`steel_eaf ≤ total_steel = dem[t]` and `coaldri_output ≤ dri_eaf_steel_out =
steel_eaf`, the `<= dem[t]` bounds on `coaldri_output` and `ngdri_output`
can never bind.

Two AMPL-level consequences worth knowing:

1. **`total_steel[t]` is fixed by presolve** to the constant `dem[t]`. That
   is what linearises `emission_monotonic` (the only nonlinear constraint in
   the model) — see `t_additional_constraints.md` and `model.md`.
2. Because `total_steel` is a *variable* rather than a parameter, variant
   models can relax it. `regret-analysis` does exactly this: it drops
   `meet_demand` and replaces it with `total_steel + steel_import = dem`
   plus `steel_import >= 0`, giving elastic demand met partly by imports.
   `steel_balance` itself is unchanged in that variant — it is the seam the
   overlay attaches to.

## Depends on

| Symbol | Owner |
|---|---|
| `steel_eaf` | `modules/l_eaf_dri.mod` (eq61, eq69) |
| `steel_bof` | `modules/e_bof.mod` (eq38) |
| `steel_scrap_eaf` | `modules/m_scrap_eaf.mod` |
| `total_steel` | `variables.mod`; **pinned by `t_additional_constraints.mod`** (`meet_demand`) |

Feeds `t_additional_constraints.mod` (`meet_demand`, `avg_emis_cap_total`,
`emission_monotonic`), `r_cost.mod` (`other_opex × total_steel`), and every
per-tonne figure in `yreport.mod`.

## Caveats

1. **There is no import, export or inventory term.** Production equals demand
   exactly, every year. India cannot import steel to ride out a tight year,
   nor build stock ahead of a constraint. `regret-analysis` adds imports as a
   local overlay precisely because the core cannot represent this.

2. **No demand elasticity.** Since `dem[t]` is exogenous and must be met at
   any cost, the model has no way to express "this decarbonisation pathway is
   so expensive that demand would fall". Cost results should be read as *cost
   of serving fixed demand*, not as welfare.

3. **The three routes are the only options.** No HBI/DRI trade, no smelting
   reduction (HIsarna, COREX), no scrap preheating variants, no molten-oxide
   electrolysis. The route set is closed at three.
