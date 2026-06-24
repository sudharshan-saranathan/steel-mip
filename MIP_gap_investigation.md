# Why the MIP gap won't close — diagnosis and fixes

## Summary

For the tested grid point the solver returns the **same incumbent** at 180 s and 600 s
(objective `2.132395865e12`) while the gap barely moves (2.95% → 2.92%). The incumbent is
found almost immediately; what fails to converge is the **lower (dual) bound**. So this is a
*proof* problem, not a *solution-quality* problem.

The dual bound is weak because the model is a **nonconvex** MIQCP whose nonconvexity comes
from products of two decision variables (bilinear), and in three places products of *three*
decision variables (trilinear). Gurobi bounds such products with spatial branching and
McCormick envelopes, which require **finite variable bounds** to be tight. Most of the flow
variables inside these products have **no upper bound** (`var x{T} >= 0;`), so the envelope is
effectively unbounded and the relaxation bound is far below the true optimum. More solve time
cannot fix this — only a tighter formulation can.

## The nonconvex terms (variable × variable)

Route-share fractions (`f_cdri`, `f_ngdri`, `f_eaf`, `f_bof` ∈ [0,1]) and capture fractions
(`fc_bf`, `fc_cdri`, `fc_ngdri` ∈ [0,0.9]) multiply flow/output variables:

**Route output definitions (bilinear)**
- `i_dri_coal.mod` eq46: `f_cdri[t] * dri_eaf_steel_out[t]`
- `j_dri_ng.mod`  eq51: `f_ngdri[t] * dri_eaf_steel_out[t]`
- `k_dri_h2.mod`  eq56: `(1 - f_cdri[t] - f_ngdri[t]) * dri_eaf_steel_out[t]`
- `e_bof.mod` eq38: `f_bof[t] * total_steel[t]`, `l_eaf_dri.mod` eq61: `f_eaf[t] * total_steel[t]`
  — *note:* `total_steel[t]` is pinned to a parameter by `meet_demand`, so after presolve these
  two reduce to fraction × constant (linear). They are **not** the problem.

**Scope-1 emissions (bilinear)** — `s_emissions.mod` eq100/eq101
- `eaf_coal_in[t] * f_cdri[t]`, `eaf_lime_in[t] * f_cdri[t]`, `eaf_electrode_in[t] * f_cdri[t]`
- same three with `f_ngdri[t]`

**Carbon capture (bilinear + trilinear)** — `q_carbon_capture.mod` eq84/85/86
- eq84: `(coking_coal_in, bf_coalpci_in, sinter/bf/bof lime …) * fc_bf[t]`  (bilinear, unbounded flows)
- eq85: `eaf_coal_in[t] * f_cdri[t] * fc_cdri[t]`, `eaf_lime_in[t] * f_cdri[t] * fc_cdri[t]`  (**trilinear**)
- eq86: `eaf_coal_in[t] * f_ngdri[t] * fc_ngdri[t]`, `eaf_lime_in[t] * f_ngdri[t] * fc_ngdri[t]`  (**trilinear**)

**Cost (bilinear)** — `r_cost.mod` eq94/95/96/97/98/99
- `f_cdri[t] * steel_eaf[t]`, `f_ngdri[t] * steel_eaf[t]`, `(1-f_cdri-f_ngdri) * steel_eaf[t]`
  — `steel_eaf` is bounded (= `f_eaf` × constant demand), so these relax more tightly than the
  emissions/CCS terms; lower priority.

**Unbounded flow variables that appear in the products above** (the root cause of the loose
bound): `dri_eaf_steel_out`, `eaf_coal_in`, `eaf_lime_in`, `eaf_electrode_in`, `coking_coal_in`,
`bf_coalpci_in`, `sinter_lime_in`, `bf_lime_in`, `bof_lime_in`, `coaldri_coal_in`.
(`ngdri_ng_in` is already bounded by `ng_bound`.)

## Fixes, in recommended order

### Fix 1 — Bound the flow variables (quick, low risk, do this first)
Add valid finite upper bounds to every flow variable listed above, derived from the (fixed)
steel demand × a generous per-tonne input intensity. Example:

```ampl
# demand is fixed: total_steel[t] = base_demand*(1+growth_rate)^(ord(t)-1)
param ub_factor := 3;                      # generous safety multiple
var eaf_coal_in{t in T} >= 0,
    <= ub_factor * (base_demand*(1+growth_rate)^(ord(t)-1)) * max_coal_intensity;
```

Because the bounds are **valid** (non-binding at the optimum), they don't change the feasible
region or the answer — they only give McCormick a finite envelope, which lifts the dual bound.
This alone often cuts a nonconvex gap by a large factor. Testable in a single run: watch whether
the reported `relmipgap` drops.

### Fix 2 — Re-parameterize routes from fractions to absolute flows (best structural fix)
The fraction × output products encode a *split* of DRI-EAF steel across coal/NG/H2 routes.
Make the **route outputs the decision variables** instead of the fractions:

```ampl
var coaldri_output{T} >= 0;
var ngdri_output{T}   >= 0;
var h2dri_output{T}   >= 0;
s.t. dri_split{t in T}:
    coaldri_output[t] + ngdri_output[t] + h2dri_output[t] = dri_eaf_steel_out[t];
```

Then every per-route input scales linearly with its route output (intensity × output), and the
route fractions `f_cdri`, `f_ngdri` are computed **after** solving, for reporting only. This
removes the `f_* × variable` bilinear terms in emissions, CCS, and cost outright.

### Fix 3 — Model captured CO₂ directly instead of fraction × emissions
The capture terms `emissions × fc` (and the trilinear `flow × f_route × fc`) are inherently
bilinear. Two options:
- **Preferred:** make captured CO₂ a decision variable bounded by the technical limit, which is
  linear once route emissions are linear (after Fix 2):
  ```ampl
  s.t. ccs_bf_cap{t in T}: ccs_bf[t] <= 0.9 * n10_ccs_eta * scope1_bf[t];
  ```
  The optimizer chooses how much to capture (cost/▒carbon-tax driven), no fraction multiply.
  The `fc_* ` ramp constraints would be re-expressed on captured **amount** (or on the
  post-solve ratio).
- **If you must keep `fc` as the decision:** Fix 1 (bounding the emission/flow quantities) makes
  the remaining `fc × bounded-quantity` McCormick envelopes tight enough to converge.

### Minor cleanup (not a gap issue)
`r_cost.mod` defines `cost_ccs[t]` twice — `cost_captured_co2` (eq97) and `cost_captured_co2bf`
— with two equality constraints. They're algebraically equivalent given
`total_ccs = ccs_bf+ccs_cdri+ccs_ngdri`, so one is redundant; drop one to avoid an
over-determined system.

## Suggested sequence
1. Apply **Fix 1** and run the single test point. If the gap drops to an acceptable level,
   you may be done for the sweep.
2. If still loose, apply **Fix 2** (removes most bilinearity) and re-test.
3. Apply **Fix 3** for the capture terms if the CCS bilinear/trilinear terms remain the binding
   source of looseness.
4. Validate that with the fix(es) the dual bound rises toward the (stable) incumbent — that is
   the signal the gap is closing for the right reason.

## Publication note
Report the solver, version, time limit, and final gap regardless. For a comparative scenario
study, aim for the optimality gap to be **smaller than the smallest inter-scenario objective
difference you interpret** — otherwise a reviewer can argue the differences lie inside the gap.
The fixes above are the route to a gap small enough that the scenario comparisons are defensible.
