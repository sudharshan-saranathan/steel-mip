# `t_additional_constraints.mod` — initialisation, demand, availability, policy

> **Source:** `core/modules/t_additional_constraints.mod` — 30 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

The model's boundary conditions. Thirty lines containing four different kinds
of constraint that share nothing except being global:

1. **Initialisation** — pins 2025 to observed data
2. **Demand** — forces production to meet `dem[t]`
3. **Availability** — hard caps on scrap, natural gas and coking coal
4. **Policy** — the emissions cap and the monotonicity requirement

Despite the "additional" name this is the module that determines what the
model is actually solving. It is included **last**, which matters: the
`drop emission_monotonic;` that several scenarios issue must come after it.

## Declares

No parameters, no variables. Nine constraints.

## Equations

### 1. Initialisation (lines 2-6)

```ampl
s.t. init_f_bof:      f_bof[first(T)] = 0.51;
s.t. init_f_eaf:      f_eaf[first(T)] = 0.49;
s.t. init_scrap_eaf:  steel_scrap_eaf[first(T)] = 0;
s.t. init_f_cdri:     coaldri_output[first(T)] = 0.902 * dri_eaf_steel_out[first(T)];
```

The 2025 route split, pinned to observed Indian data: **51% BF-BOF, 49%
DRI-EAF, 0% dedicated scrap-EAF**, and within the DRI-EAF pool **90.2%
coal-DRI**. So 2025 is 51% BF-BOF, 44.2% coal-DRI, 4.8% NG-DRI, 0% H2, 0%
scrap-EAF.

The comment on `init_f_cdri` records a deliberate linearisation: the share is
expressed on the route *output* (`coaldri_output = 0.902 × dri_eaf_steel_out`)
rather than as a ratio, which would be nonlinear.

Together with the `phi0_*` blend pins (`e_bof.mod`, `i_dri_coal.mod`,
`j_dri_ng.mod`) and `legacy_init_*` (`v_capacity.mod`), **the entire 2025
solution is fixed**. Scenario differences arise only from 2026-2050.

### 2. Demand (lines 9-10)

```ampl
s.t. meet_demand{t in T}:
    total_steel[t] = base_demand * (1 + growth_rate)^(ord(t) - 1);
```

Note the RHS is written out longhand rather than as `dem[t]`, though it is
algebraically identical. Production equals demand exactly — no imports, no
exports, no inventory.

This constraint has an important side effect: it **fixes `total_steel[t]` to
a constant**, which is what lets AMPL's presolve linearise
`emission_monotonic` (below) and turn the whole model into an LP.

`regret-analysis` drops this constraint and replaces it with
`total_steel + steel_import = dem` — which is why the H2-DRI/regret variant
is a genuinely different model, not a parameterisation.

### 3. Availability caps (lines 13-21)

```ampl
s.t. scrap_bound{t in T: t > first(T)}:
    bof_scrap_in[t] + eaf_scrap_in[t] + scrap_eaf_scrap_in[t] <= n8_scrap_limit[t];

s.t. ng_bound{t in T}:
    ngdri_ng_in[t] <= n5_ng_cap[t];

s.t. coking_coal_bound{t in T: t > first(T)}:
    coking_coal_in[t] <= ccoal_cap[t];
```

| Cap | Source | Default | Binding? |
|---|---|---|---|
| `n8_scrap_limit[t]` | derived: 37 Mt @ +6%/yr → 159 Mt by 2050 | — | yes, in scrap studies |
| `n5_ng_cap[t]` | table in `core/parameters.mod` | **no default** | yes, esp. 2035-2040 |
| `ccoal_cap[t]` | `definitions.mod` | **1e12** (i.e. off) | only when a study sets it |

The three caps are the model's supply-side levers, and the import-dependence
study drives all three.

`scrap_bound` and `coking_coal_bound` skip 2025 (`t > first(T)`) because that
year is pinned by initialisation and might otherwise be infeasible; `ng_bound`
does not skip it, and the 2025 cap of 5.35 Mt is consistent with the pinned
4.8% NG-DRI share.

Note `scrap_bound` pools **all three** scrap uses against one limit: BOF
blending, DRI-EAF blending, and the dedicated scrap-EAF. They compete
directly.

### 4. The emissions cap (lines 24-25)

```ampl
s.t. avg_emis_cap_total:
    (sum {t in T} total_emissions[t]) <= avg_emi * (sum {t in T} total_steel[t]);
```

**A single scalar constraint over the whole horizon** — not one per year.
This is the model's only emissions pressure, and its form has three
consequences:

- It is a **cumulative budget**, not an annual target. The model may emit
  freely early and abate hard late (or vice versa) as long as the 26-year
  average intensity clears `avg_emi`.
- Because `total_steel[t] = dem[t]` is fixed, the RHS is a **constant**:
  `avg_emi × Σ dem[t]`. At `avg_emi = 1.8` and 26 years of 5% growth from
  152.2 Mt (Σ dem ≈ 7 779 Mt), that is a budget of ≈**14.0 GtCO2**.
- It is a hard cap with no price. There is no carbon tax in the objective
  (`carbon_tax` is declared but unused — see `r_cost.md` caveat 1), so the
  shadow price of this constraint *is* the model's implicit carbon price.

`avg_emi` is declared in `core/parameters.mod` (default 1.8) and is the
primary sweep axis of the abatement, scrap and hydrogen-delay studies,
typically over {1.6, 1.8, 2.0}.

### 5. Monotonicity (lines 27-30)

```ampl
s.t. emission_monotonic{t in T: t > first(T)}:
    total_emissions[t] * total_steel[t-1] <= total_emissions[t-1] * total_steel[t];
```

Emission *intensity* must never increase:
`total_emissions[t]/total_steel[t] ≤ total_emissions[t−1]/total_steel[t−1]`,
cross-multiplied to avoid a division.

This is the **only nonlinear constraint in the model** — a product of two
variables. It is also the only reason the model is not trivially an LP as
written. Because `meet_demand` fixes both `total_steel` terms to constants,
AMPL's presolve reduces it to a linear inequality and the solved problem is a
pure LP. Measured: without presolve, 25 nonlinear constraints and 52
nonlinear variables; with presolve, "all linear".

Note the indexing uses `t-1` and `t` arithmetic on the year value rather than
`prev(t)` as the rest of the model does. Equivalent for a contiguous
`2025..2050` set, but stylistically inconsistent and would break if `T`
became non-contiguous.

**Several scenarios `drop emission_monotonic;`** — `import-dependence` does,
because a supply shock can legitimately force intensity up in one year. The
drop must come *after* `core/model.mod` since the constraint is declared here.

## Depends on

| Symbol | Owner |
|---|---|
| `f_bof` | `modules/e_bof.mod` (eq38) |
| `f_eaf` | `modules/l_eaf_dri.mod` (eq61) |
| `steel_scrap_eaf` | `modules/m_scrap_eaf.mod` |
| `coaldri_output`, `dri_eaf_steel_out` | `modules/i_dri_coal.mod`, `modules/k_dri_h2.mod` |
| `total_steel` | `modules/n_steel_balance.mod` |
| `bof_scrap_in`, `eaf_scrap_in`, `scrap_eaf_scrap_in`, `ngdri_ng_in`, `coking_coal_in` | various process modules |
| `total_emissions` | `modules/s_emissions.mod` |
| `base_demand`, `growth_rate`, `n8_scrap_limit`, `ccoal_cap` | `definitions.mod` |
| `n5_ng_cap` | `definitions.mod` (declared), `core/parameters.mod` (populated) |
| **`avg_emi`** | **`core/parameters.mod`** |

## Caveats

1. **The emissions cap is cumulative and horizon-wide.** A scenario meeting
   `avg_emi = 1.8` may follow wildly different annual paths. `emission_monotonic`
   is the only thing shaping the trajectory — and it is the constraint most
   often dropped. Read any `avg_emi` result as a carbon *budget*, not a target.

2. **`avg_emi` is owned by `core/parameters.mod`, not `definitions.mod`.**
   The one parameter that drives the model's central question is declared in
   the file that looks like data. Anyone regenerating `parameters.mod` must
   carry it.

3. **`meet_demand` restates `dem[t]`'s formula longhand** instead of using
   `dem[t]`. If `dem` is ever redefined the two will silently diverge.

4. **`emission_monotonic` is nonlinear as written**, and only presolve saves
   it. Any variant that unfixes `total_steel` — `regret-analysis` does — makes
   the model genuinely nonlinear (bilinear) unless it also drops this
   constraint. Worth checking whenever a new overlay touches demand.

5. **`init_*` pins mean 2025 contributes an identical constant to every
   scenario's objective.** Objective *differences* between scenarios are
   therefore differences over 2026-2050 only — useful when interpreting small
   relative gaps.

6. **`ccoal_cap` defaults to 1e12, i.e. effectively off**, while
   `n5_ng_cap` has no default at all. Two supply caps, two different failure
   modes: forgetting to set the first is silent, forgetting the second is a
   hard AMPL error.

7. **The four constraint families in this file have nothing to do with each
   other.** Initialisation, demand, resource availability and climate policy
   are separate modelling concerns sharing a file because none was big enough
   to warrant its own. Splitting would make the policy levers easier to find.
