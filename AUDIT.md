# Correctness Audit Report — AMPL MILP Steel-Decarbonisation Model

**Date:** 2026-06-24
**Scope:** Full module-level and cross-module correctness audit of the AMPL MILP model backing the steel-decarbonisation paper. All findings below were adversarially verified against source; false positives and intentional LCOE conventions have been removed.

---

## 1. Executive Summary

After de-duplication (several module-level and cross-module reports describe the same underlying defect), the audit identifies **14 distinct defects**:

| Severity | Count | De-duplicated IDs |
|----------|-------|-------------------|
| **High** | 8 | H1–H8 |
| **Medium** | 4 | M1–M4 |
| **Low** | 4 | L1–L4 (one is a no-defect verification) |

**Verdict: The model is NOT publication-ready in its current state.** Eight high-severity defects materially bias the optimization and the reported results, and several of them push the optimum in the same direction — toward the BF-BOF + CCS configuration — by simultaneously (a) inflating the waste-heat-recovery credit ~56×, (b) over-stating the capturable CO₂ base, (c) giving CCS electricity away for free, (d) giving DRI-EAF a free 100% metallic yield, and (e) leaving scrap effectively unlimited for two of three consumers. These are not offsetting errors; they compound. Any headline result (LCOE by route, optimal technology mix, abatement cost, emissions trajectory) computed with the current model must be regarded as unreliable until the high-severity items are fixed and the model is re-run.

**What must be fixed first (blocking):** the unit error in the COG waste-heat stream (H1), the inverted fine-ore mass balance across all four pellet modules (H2), the PCI capture-base/Scope-1 coefficient mismatch (H3), the missing WHR term in the power balance (H4), the uncosted CCS electricity (H5), the DRI-EAF 100% yield (H6), the un-pooled scrap cap (H7), and the inverted H₂ growth-limit logic (H8). These eight changes are prerequisites for re-running and re-reporting.

---

## 2. Findings by Severity

### HIGH

---

#### H1 — COG waste-heat stream is a raw volume (Nm³) summed against energy (GJ) terms
**Severity:** High · **Category:** units
**Location:** `modules/a_coke.mod:17` (`coke_cog_out_balance`, eq5); consumed in `modules/p_waste_heat.mod:7` (`bf_bof_waste_heat_balance`, eq80)
*(De-duplicates the two separate reports keyed on `a_coke.mod` and `p_waste_heat.mod` — same defect, root cause in eq5, symptom in eq80.)*

**Issue.** `cog_out` is defined as a gas **volume**, not energy:
```ampl
n0_cog_c * bf_coke_in[t] - cog_out[t] = 0;   # = 470 Nm3/t-coke * t-coke = Nm3
```
But `cog_out` is consumed *only* in `bf_bof_waste_heat_balance` (eq80), where every other term is an **energy in GJ**: `bfg_out = n2_bfg_hm*ng_bfg_cv*hm`, `bofgas_out = n3_bofg_bof*ng_bofg_cv*steel`, and all consumed terms (`cokeov_cog_in` eq7, `bf_cog_in` eq25, `bof_cog_in` eq39, `bfg_in` eq24, `cokeov_bfg_in` eq8) multiply a calorific value `ng_*_cv` and are GJ. With `ng_cog_cv = 0.018 GJ/Nm³` (`definitions.mod:15`) and `n0_cog_c = 470 Nm³/t` (`definitions.mod:32`), the term enters at ~470×production where it should be ~8.46×production — **inflated ~56×**. The subtraction `cog_out − cokeov_cog_in − bf_cog_in − bof_cog_in` mixes Nm³ with GJ and is not physically meaningful. Notably `cog_out` is the total-COG counterpart of `cokeov_cog_in` (eq7), which *does* apply `ng_cog_cv`; the two must share a calorific basis.

**Impact.** Massively inflates `wasteheat_bf_bof`, hence `whr_available_gas`, `whr_power_generated`, and the WHR sales credit. Biases the optimum toward BF-BOF and understates system cost.

**Fix (exact edit).** Change `modules/a_coke.mod:17` to carry energy, matching eq26/eq37:
```ampl
n0_cog_c * ng_cog_cv * bf_coke_in[t] - cog_out[t] = 0;
```
(470 Nm³/t × 0.018 GJ/Nm³ = 8.46 GJ/t-coke.) Equivalently, multiply `cog_out[t]` by `ng_cog_cv` inside eq80 — **do exactly one, not both.** This also resolves the broader Nm³-vs-GJ mismatch flagged in M3 for the BF-BOF inputs to `available_waste_stream`; once eq5 carries CV, that stream is GJ-consistent.

---

#### H2 — Fine-ore mass balance is inverted (divides instead of multiplies) in all four pellet modules
**Severity:** High · **Category:** mass_balance
**Location:** `modules/c_pellets_bf.mod:8` (`pellets_bf_fineore_balance`, eq17); same pattern at `f_pellets_coaldri.mod:6`, `g_pellets_ngdri.mod:6`, `h_pellets_h2dri.mod:6`
*(Consolidates the high-severity `c_pellets_bf` report and the medium-severity `f_pellets_coaldri` report — same inversion, same root cause; rated High because it violates iron-mass conservation across the entire pellet supply chain.)*

**Issue.**
```ampl
bf_pellets_in[t] / ng_ore_pell - pellets_fineore_bf[t] = 0;
```
`ng_ore_pell` is declared `default 1.1; # Iron ore (ton) per ton of pellets` (`definitions.mod:14`), i.e. 1.1 t ore per t pellets. The balance must therefore read `fineore = ng_ore_pell * pellets`. As written it yields `pellets_fineore_bf = bf_pellets_in / 1.1 = 0.909 * bf_pellets_in`, so the model produces **more pellets (1 t) than iron-bearing ore fed in (0.909 t)** — violating conservation of iron-bearing mass and contradicting the parameter's own comment and the physical mass loss (LOI/beneficiation). The same inverted form appears in the three DRI pellet modules.

**Impact.** Iron-mass non-conservation for every pellet-consuming route. Propagates into cost: `cost_pellet_bf_def` (`r_cost.mod:29`) and the DRI analogue (`r_cost.mod:58`) multiply the understated `pellets_fineore_bf` by `ng_cost_fineore`, so fine-ore quantity, ore demand, and ore cost are understated by ~1.1²≈1.21×.

**Fix (exact edit).** Replace division with multiplication in all four modules:
```ampl
ng_ore_pell * bf_pellets_in[t] - pellets_fineore_bf[t] = 0;
```
and likewise at `f_pellets_coaldri.mod:6`, `g_pellets_ngdri.mod:6`, `h_pellets_h2dri.mod:6` (using the respective `*_pellets_in` variable). Alternatively redefine `ng_ore_pell` as "pellets per ton of ore" (<1) and keep the division — but the multiply matches the existing comment.

---

#### H3 — BF PCI-coal emission factor differs between the capture base and Scope-1 emissions
**Severity:** High · **Category:** cross_module_consistency
**Location:** `modules/q_carbon_capture.mod:22` (`capbase_bf_def`) vs `modules/s_emissions.mod:6` (`scope1_blastf`) and `s_emissions.mod:45` (`scope1_def`)
*(De-duplicates **five** separate verified reports — q_carbon_capture, s_emissions, t_additional_constraints, and two cross:emissions-vs-capture entries — all describing the identical 0.113-vs-0.106 PCI coefficient mismatch. The big-M variant is split out as L2.)*

**Issue.** For the same physical stream `bf_coalpci_in`:
- Capture base (`q_carbon_capture.mod:22`): `bf_coalpci_in[t] * 0.113 * 26` = 2.938 tCO₂/t
- Scope-1 emission (`s_emissions.mod:6`): `bf_coalpci_in[t] * 0.106 * 26` = 2.756 tCO₂/t
- Aggregated Scope-1 (`s_emissions.mod:45`): `bf_coalpci_in[t] * 2.756`

All other routes agree between base and Scope-1 (coking coal 0.1116×25=2.79, lime 0.44, coal-DRI 0.110×24=2.64, NG 0.055×50=2.75); **only PCI diverges.** Since CCS captures a fraction of *emitted* CO₂ (`ccs_bf <= n10_ccs_eta*fc_max*capbase_bf`, eq84/87) and `total_emissions = scope1 + scope2 − total_ccs` (`total_emissions_def`, line 63), an over-large base lets the model credit capturing ~6.6% (0.113/0.106−1) more PCI-derived CO₂ than was ever emitted.

**Impact.** Net BF-BOF emissions biased artificially low; the average-emissions targets (`avg_emis_*_total`, `t_additional_constraints.mod:54-57`) become easier to meet than physics allows; CCS feasibility/credit biased toward the BF route. The defect flows into the CCS ramp / big-M switch constraints in `t_additional_constraints.mod` (e.g. `bf_ccs_ramp_up`, line 115) via `capbase_bf`.

**Fix (exact edit).** In `modules/q_carbon_capture.mod:22` change `bf_coalpci_in[t] * 0.113 * 26` to `bf_coalpci_in[t] * 0.106 * 26`, matching `scope1_blastf` and the 2.756 aggregate. The two Scope-1 expressions already agree on 0.106, so the base is the outlier. (If 0.113 is the intended carbon fraction instead, fix both Scope-1 expressions — but the value must be identical in emission and capture base.) **Recommended:** replace the literals with a shared named parameter (e.g. `ef_pci`) consumed by both modules to prevent future divergence. Also update the big-M at line 53 (see L2).

---

#### H4 — On-site WHR electricity is credited but never offsets grid power (missing balance term)
**Severity:** High · **Category:** cross_module_consistency / energy_balance
**Location:** `modules/o_power_balance.mod:5-24` (`total_power_balance`, eq79); generator in `modules/p_waste_heat.mod:32-33` (`whr_power_balance`, eq83); credited in `modules/r_cost.mod:124` (`credit_from_wasteheat`, eq102)
*(Consolidates the high-severity `o_power_balance` report and the high-severity `cross:energy-power-balance` report — same missing term. The "two-ledger" framing is retained as M2.)*

**Issue.** `whr_power_generated[t]` is on-site WHR generation in kWh (eq83: `whr_available_gas[t]*277.78*n9_eta*n9_whr[t]`). It is sold at `ng_credit_power` via eq102 — the **same** rate applied to the three other on-site generators `cdq_power_out`, `sinterwaste_power_out`, `bf_trt_out` (`r_cost.mod:12,23,42`). Those three are subtracted in `total_power_balance` (lines 20–22), displacing `grid_power_in`. But `whr_power_generated` is **never added or subtracted in the power balance** and has no other sink (grep confirms it appears only in eq83 and eq102). So WHR electricity earns the sales credit *and* the plant still buys the same kWh from the grid — a double-credit. The author flagged exactly this risk in `s_emissions.mod:58`.

**Impact.** `grid_power_in` is overstated; its Scope-2 emissions (`s_emissions.mod:56`, `n9_grid_ef*grid_power_in`) and grid cost are overstated; WHR power is effectively double-counted (free process electricity + a sale). Inconsistent with the model's own convention for the three sensible-heat recoveries. Units are consistent (all kWh, and 277.78 = 1000/3.6 kWh/GJ is correct — see L4); this is purely a missing balance term.

**Fix (exact edit).** In `modules/o_power_balance.mod`, insert between line 22 (`- bf_trt_out[t]`) and line 23 (`- grid_power_in[t]`):
```ampl
    - whr_power_generated[t]
```
**Caveat:** `grid_power_in` is bounded ≥ 0 (`variables.mod:113`). Once WHR offsets demand the model can become infeasible if on-site generation exceeds total consumption; either add a net-export variable / allow `grid_power_in` < 0, or cap WHR self-supply at demand.

---

#### H5 — CCS electricity consumption is never charged in the objective
**Severity:** High · **Category:** cost
**Location:** `modules/r_cost.mod` (`cost_captured_co2` / `total_cost_def`); `power_ccs` defined in `modules/q_carbon_capture.mod:77` (`power_capture`, eq88)
*(De-duplicates the module-level `r_cost` report and the `cross:cost-completeness` report — same omission. Confirmed not an LCOE convention.)*

**Issue.** The cost module prices power **per-process** by multiplying each process's gross consumption variable by `ng_cost_power` (e.g. `r_cost.mod:9` `ng_cost_power*coke_power_in`, line 30 `*pellets_bf_power`, etc.), and never costs `grid_power_in`. The CCS block consumes `power_ccs[t] = total_ccs[t]*800` kWh/tCO₂ (`q_carbon_capture.mod:77`), and `power_ccs` *does* enter the power balance (`o_power_balance.mod:19`) so it raises grid draw and Scope-2 — **but `power_ccs` is never multiplied by `ng_cost_power` in any cost constraint** (grep-confirmed), and `grid_power_in` is never costed either. So the ~800 kWh per tonne CO₂ captured is **free in the objective.**

**Impact.** Understates the true cost of capture; biases the optimizer toward over-capturing CO₂. Genuine internal-consistency gap (every one of the 13 other processes charges its own power), not a formulation choice.

**Fix (exact edit).** Add a CCS electricity cost term, e.g. in `cost_captured_co2`:
```ampl
+ ng_cost_power * power_ccs[t]
```
(equivalently `+ ng_cost_power * total_ccs[t] * 800`). Alternatively switch the whole model to charging `grid_power_in[t]*ng_cost_power` once, which would capture `power_ccs` automatically.

---

#### H6 — DRI-EAF metallic balance assumes 100% yield (no Fe loss), inconsistent with the other two melt routes
**Severity:** High · **Category:** mass_balance
**Location:** `modules/l_eaf_dri.mod:15` (`eaf_scrap_balance`, eq63) and `:39` (`dri_eaf_steel_relation`, eq69)

**Issue.** eq69 gives `steel_eaf = eaf_scrap_in + dri_eaf_steel_out`; eq63 gives `eaf_scrap_in = n7_phi_eaf*steel_eaf = 0.1*steel_eaf`. Hence `dri_eaf_steel_out = 0.9*steel_eaf`, and metallic-in per tCS = 0.9 (DRI) + 0.1 (scrap) = **1.000 t with zero yield loss**, even though the EAF emits 0.15 t/tCS slag (`n7_ss`) carrying FeO. By contrast: BOF takes 1.0 thm + 0.1 scrap = 1.1 t metal per 1.0 t steel (~91% yield, eq32+eq34); scrap-EAF takes 1.1 t scrap per 1.0 t steel (`n8_phi_eaf=1.1`, ~91% yield, eq72). **DRI-EAF alone assumes perfect conversion.**

**Impact.** Silently understates DRI + scrap consumption — and therefore pellet/ore demand and material cost — for the entire DRI route relative to BF-BOF and scrap-EAF, biasing route economics in favour of DRI-EAF.

**Fix.** Introduce an explicit EAF metallic yield < 1 so charge > steel out. Make `dri_eaf_steel_out + eaf_scrap_in = steel_eaf / yield` (yield ≈ 0.90–0.92, consistent with 0.15 t slag) instead of `= steel_eaf`. Keep `n7_phi_eaf` as the scrap fraction of the charge, but ensure (scrap + DRI metal) > `steel_eaf`. Align the yield with BOF and scrap-EAF (1.1 in / 1.0 out) so all three routes use a consistent metallic yield.

---

#### H7 — Scrap availability is capped on only one of three scrap consumers
**Severity:** High · **Category:** cross_module_consistency
**Location:** `modules/t_additional_constraints.mod:25-26` (`scrap_bound`) vs `e_bof.mod:8` (eq34), `l_eaf_dri.mod:15` (eq63), `m_scrap_eaf.mod:9` (eq72)

**Issue.** `scrap_bound` caps only `scrap_eaf_scrap_in[t] <= n8_scrap_limit[t]`. But `bof_scrap_in` (0.1 t/tCS BOF, eq34) and `eaf_scrap_in` (0.1 t/tCS DRI-EAF, eq63) draw from the **same physical scrap pool** with no constraint, and there is no aggregate scrap balance. All three are priced identically at `ng_cost_scrap` (`r_cost.mod:49,103,114`), confirming a single shared pool. Total scrap demand can therefore exceed national availability while the model reports the cap as satisfied.

**Impact.** BF-BOF and DRI-EAF can consume effectively unlimited, unconstrained scrap, biasing their feasibility and metal balance and distorting the route mix.

**Fix (exact edit).** Add an aggregate constraint (replacing or supplementing the single-stream `scrap_bound`):
```ampl
bof_scrap_in[t] + eaf_scrap_in[t] + scrap_eaf_scrap_in[t] <= n8_scrap_limit[t];
```
If the three pools are intentionally distinct, document and cap each separately.

---

#### H8 — Post-2045 H₂ growth limiter uses `max()` where `min()` is required (defeats both bounds)
**Severity:** High · **Category:** sign_error
**Location:** `parameters.mod:56-57` (`H2_growth_limit`)

**Issue.**
```ampl
h2dri_h2_in[t] <= max(1.15 * h2dri_h2_in[prev(t)], H2_cap);
```
A year-on-year growth limiter combined with an absolute availability cap must take the **binding (smaller)** of the two upper-bound candidates, i.e. `min(...)`. As written it takes the **larger**, so **both intended limits are defeated**: the absolute 1.5M availability cap (`H2_cap`) is never binding for t>2045 (input can grow at 15%/yr far beyond 1.5M), and the 15% growth limit binds only once `1.15*prev` exceeds 1.5M. The two limits are never simultaneously enforced.

**Impact.** Unconstrained H₂-DRI input growth post-2045; H₂ availability and ramp policy are not actually enforced, inflating the achievable H₂-route share.

**Fix (exact edit).** Change `max` to `min`:
```ampl
h2dri_h2_in[t] <= min(1.15 * h2dri_h2_in[prev(t)], H2_cap);
```

---

### MEDIUM

---

#### M1 — H₂-DRI route has no defining Scope-1 constraint (free/undefined variable)
**Severity:** Medium · **Category:** cross_module_consistency
**Location:** `modules/s_emissions.mod:30-32` (`scope1_h2dri_` commented out); variable `scope1_h2dri` declared `variables.mod:152`; route defined by `dri_route_split` in `modules/k_dri_h2.mod:8-9`

**Issue.** The coal and NG sibling routes each have an active per-route Scope-1 constraint (`scope1_coaldri` line 16-18, `scope1_natgasdri` line 23-25) capturing the EAF-side coal/lime/electrode carbon apportioned via `n7_cs/n7_ls/n7_eltrd * output/(1-n7_phi_eaf)`. The H₂ analogue `scope1_h2dri_` is **fully commented out**, leaving `scope1_h2dri` (declared `>=0`, no upper bound) **free with no defining equation**. It is read in `report.mod:165` as `carbon_tax*scope1_h2dri[t]` in the H₂-route LCOE.

**Impact.** With `carbon_tax = 0` (`definitions.mod:199`, override commented in `parameters.mod:147`) the optimized objective and the aggregate `scope1_def` are unaffected today. But (a) per-route H₂ emission reporting is undefined/wrong, and (b) if `carbon_tax` is ever enabled, the H₂-route LCOE uses an arbitrary unconstrained value. Latent reproducibility defect.

**Fix.** Add a per-route constraint mirroring `scope1_coaldri` but for H₂ (no reductant carbon; only apportioned EAF coal/lime/electrode), using the linear `h2dri_output` rather than the old bilinear form in the commented code:
```ampl
s.t. scope1_h2dri_{t in T}:
  (n7_cs*h2dri_output[t]/(1-n7_phi_eaf))*0.110*24
+ (n7_ls*h2dri_output[t]/(1-n7_phi_eaf))*0.44
+ (n7_eltrd*h2dri_output[t]/(1-n7_phi_eaf))*6
- scope1_h2dri[t] = 0;
```

---

#### M2 — Recovered-power streams accounted on two different ledgers
**Severity:** Medium · **Category:** cross_module_consistency
**Location:** `modules/o_power_balance.mod:20-23` vs `modules/p_waste_heat.mod:33`

**Issue.** The three sensible-heat recoveries (`cdq_power_out` 80 kWh/t coke, `sinterwaste_power_out` 30 kWh/t sinter, `bf_trt_out` 35 kWh/thm) enter the power balance directly as grid-offsetting generation, while the fuel-gas-derived `whr_power_generated` is routed only to the cost module. Two physically equivalent classes of on-site electricity are accounted on two different ledgers, so the system electricity balance is internally inconsistent and reported grid import is not the true residual after on-site generation.

**Impact.** Same root cause as H4; this is the "consistency" framing. The reported grid import is not the true net.

**Fix.** Put all recovered-power streams on one ledger — preferably by including `whr_power_generated` in `total_power_balance` per **H4** (every on-site kWh reduces `grid_power_in` exactly once). Fixing H4 resolves M2.

---

#### M3 — BF-BOF volumetric streams (Nm³) summed with GJ streams in `available_waste_stream`
**Severity:** Medium · **Category:** cross_module_consistency
**Location:** `modules/p_waste_heat.mod:26-33` (`available_waste_stream`, `whr_power_balance`) interacting with `modules/m_scrap_eaf.mod:23-24` (`scrap_eaf_gas_balance`, eq77)

**Issue.** `available_waste_stream` (lines 26-29) sums `wasteheat_bf_bof + wasteheat_eaf + scrap_eaf_wasteheat`. `wasteheat_bf_bof` is built from `cog_out/bfg_out/bofgas_out` — gas volumes in Nm³ with no CV applied — while `wasteheat_eaf` and `scrap_eaf_wasteheat` are in GJ (`n8_eafg=3 GJ/tCS`, `definitions.mod:124`). `whr_power_balance` (line 33) then multiplies the sum by 277.78 kWh/GJ. So the GJ EAF streams convert correctly but the Nm³ BF-BOF volumes are treated as GJ.

**Impact.** Dimensional error in the BF-BOF contribution to recovered power. Same calorific-basis root cause as **H1**.

**Fix.** Apply CV to the BF-BOF volumetric streams before they enter `wasteheat_bf_bof`: use `cog_out*ng_cog_cv + bfg_out*ng_bfg_cv + bofgas_out*ng_bofg_cv` (and convert the corresponding recovered/inlet Nm³ terms) with `ng_cog_cv=0.018`, `ng_bfg_cv=0.0033`, `ng_bofg_cv=0.008` (`definitions.mod:15-17`). **Note:** fixing **H1** at `a_coke.mod:17` already makes `cog_out` a GJ quantity; ensure `bfg_out`/`bofgas_out` carry CV likewise so all three inputs are GJ and the 277.78 factor applies uniformly. No change needed inside `m_scrap_eaf.mod`.

---

#### M4 — H₂-DRI production ramp is asymmetric (down-ramp only; up-ramp commented out)
**Severity:** Medium · **Category:** asymmetry / missing-constraint
**Location:** `modules/t_additional_constraints.mod:83-92` (h2dri up-ramp commented; only `h2dri_prod_down` active)

**Issue.** For the H₂-DRI route only the down ramp is active (line 91-92: `h2dri_output[t] >= 0.85*h2dri_output[prev(t)]`, t>2045); the matching up-ramp (lines 83-89) is commented out. `bof/cdri/ngdri` all have both up- and down-ramps (lines 63-79). So the H₂ route has a 0.85× decline floor but no +15% output growth ceiling, leaving H₂ expansion governed only by the (broken — see H8) input gate. The down-ramp itself is correctly signed.

**Impact.** Design-dependent. Combined with H8, H₂ growth is effectively unconstrained on the output side.

**Fix.** If symmetric ramping is intended, re-enable:
```ampl
h2dri_output[t] <= 1.15*h2dri_output[prev(t)]   for t > ng_h2_start_year+1
```
(start one year after the first active year, since `prev` points at the all-zero pre-start year 2045 and would otherwise pin output to 0). If asymmetry is intentional, document it.

---

### LOW

---

#### L1 — `sinter_gas_balance` defines a dead/decorative variable (`sg_out`)
**Severity:** Low · **Category:** redundancy
**Location:** `modules/b_sinter.mod:29-30` (`sinter_gas_balance`); `sg_out` declared `variables.mod:22`

**Issue.** `sinter_gas_balance` pins `sg_out[t] = n1_sintgas_sint * ng_sintgas_cv * bf_sinter_in[t]` (≈1.08 GJ/t-sinter). Grep shows `sg_out` appears in **no other constraint** — it is absent from the waste-heat balance, power balance, cost block, and emissions. Bounded only `>= 0`, the constraint defines a value that never feeds the objective or any balance. It is consistent with the `definitions.mod` note that remaining sinter gas is unrecovered waste. No bias, but it is a dangling GJ term and an unused variable+constraint pair.

**Fix.** Either (a) remove `sinter_gas_balance` and `sg_out` entirely if sinter gas is intentionally unrecovered waste, or (b) route `sg_out` into a GJ-based waste-heat/energy stream (mirroring `cog_out`/`bfg_out`) so the GJ is actually credited. No numeric coefficient change either way.

---

#### L2 — Big-M `cap_ub_bf` propagates the inflated 0.113 PCI factor
**Severity:** Low · **Category:** cross_module_consistency
**Location:** `modules/q_carbon_capture.mod:53` (`cap_ub_bf` / `Mccs_bf`)

**Issue.** `cap_ub_bf` reuses `0.25*dem[t]*0.113*26` instead of `0.106*26`. As a big-M it only needs to be a valid over-estimate, so an inflated value is not unsafe for the switch logic — but it propagates the same 0.113 (see **H3**) and would silently become wrong if these bounds are later tightened or `cap_ub_bf` is reused as an actual ceiling.

**Fix.** For one-source-of-truth consistency with the corrected H3 coefficient, change to `0.25*dem[t]*0.106*26`. Functionally optional, recommended.

---

#### L3 — Duplicate equation-number comment tags in `r_cost.mod`
**Severity:** Low · **Category:** traceability
**Location:** `r_cost.mod:132` (`cost_captured_co2`) and `:163` (`total_cost_def`)

**Issue.** `cost_captured_co2` is tagged `# eq97`, colliding with `cost_coaldri_def` (line 82, `# eq97`); `total_cost_def` is tagged `# eq98`, colliding with `cost_ngdri_def` (line 90, `# eq98`). Comments only; no effect on math, but hurts traceability for a paper.

**Fix.** Renumber the comment tags so each constraint has a unique `eqNN` label (give `cost_captured_co2` and `total_cost_def` distinct numbers). Cosmetic.

---

#### L4 — GJ→kWh conversion spot-check (no defect; recorded for completeness)
**Severity:** Low · **Category:** units (verification)
**Location:** `modules/p_waste_heat.mod:33`; CVs `definitions.mod:15-18`

**Finding.** Dimensional check of the on-site gas→power conversion: recovered gas streams are GJ (e.g. `cokeov_cog_in = 190*0.018`, `bfg_out = 1500*0.0033`, `bofgas_out = 100*0.008`), so `whr_available_gas` is GJ, and 277.78 = 1000/3.6 kWh/GJ is the correct factor; `whr_power_generated` is kWh, consistent with the kWh consumer terms in eq79. **The COG/BFG/BOFG calorific conversions and the 277.78 factor are correct.** The only problem in this area is the missing power-balance linkage (**H4**), not the unit math. No change to the conversion factor.

---

## 3. Recommended Fix Order

Ordered so that root-cause edits land before the consistency items they resolve, and so the model can be re-run as early as possible.

1. **H8** — `parameters.mod:57` `max`→`min`. One-character logic fix; unblocks H₂ policy.
2. **H2** — Invert the fine-ore balance in all four pellet modules (`c/f/g/h_pellets_*`). Restores iron-mass conservation; affects ore demand and cost broadly.
3. **H3** — Reconcile the PCI factor (0.113→0.106) in `q_carbon_capture.mod:22`; introduce shared `ef_pci`. **Then L2** (big-M at line 53) in the same pass.
4. **H1** — Add `ng_cog_cv` to `cog_out` (`a_coke.mod:17`). Root-cause unit fix. **This also resolves M3**; while here, ensure `bfg_out`/`bofgas_out` inputs to `wasteheat_bf_bof` are CV-converted.
5. **H4** — Insert `- whr_power_generated[t]` into `total_power_balance`; handle the `grid_power_in ≥ 0` infeasibility (net-export variable or self-supply cap). **This also resolves M2.**
6. **H5** — Add `ng_cost_power * power_ccs[t]` to the CCS cost.
7. **H6** — Introduce an explicit DRI-EAF metallic yield < 1.
8. **H7** — Add the aggregate scrap-availability constraint over all three consumers.
9. **M1** — Add the H₂-route Scope-1 constraint (`scope1_h2dri_`).
10. **M4** — Re-enable (or document) the H₂ output up-ramp.
11. **L1, L3** — Remove/route the dead `sg_out`; fix duplicate `eqNN` tags. (Cosmetic; do before paper submission.)
12. **Re-run** the full model after steps 1–8 and re-validate all headline results before drafting any quantitative claims.

---

## 4. What Was Checked and Looks Correct

The audit covered every module (`a_coke` through `t_additional_constraints`), the shared `definitions.mod`/`parameters.mod`/`variables.mod`, and the `report.mod` LCOE block, with both module-local and cross-module passes. The following were checked and found correct (or are intentional conventions, not defects):

- **GJ→kWh conversion factor** (277.78 = 1000/3.6) and the COG/BFG/BOFG calorific-value math in the WHR power chain are dimensionally sound (L4).
- **Coking-coal, coal-DRI, NG, and lime emission factors** agree between their Scope-1 and capture-base expressions across all routes (only the PCI factor diverges — H3).
- **BOF and scrap-EAF metallic balances** correctly embed ~91% yield (1.1 t in / 1.0 t out); only DRI-EAF was anomalous (H6).
- **Down-ramp signs** for all production routes (including the active H₂ down-ramp) are correct; the issue is a *missing* H₂ up-ramp, not a wrong sign (M4).
- **Per-process power costing** is internally consistent for all 13 non-CCS processes (each charges its own `*_power_in`); the gap is specifically CCS (H5).
- **Scrap pricing** is identical (`ng_cost_scrap`) across the three consumers, confirming a single shared pool (the basis for the H7 aggregate-cap recommendation).
- **`carbon_tax` default = 0** was verified, which is why M1 (free `scope1_h2dri`) does not perturb the current optimum — it is correctly classified latent, not active.
- **LCOE/report conventions** previously flagged as suspect were confirmed intentional and excluded from this report, as were the verified false positives.

**Bottom line:** the structural skeleton (route splits, ramp framework, emissions aggregation, costing pattern) is sound, but eight high-severity numerical/logic defects — several pushing the optimum the same way — make current quantitative results unreliable. Fix items 1–8 above, re-run, and re-validate before publication.
