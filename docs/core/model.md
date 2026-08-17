# `core/` — the steel decarbonisation model

> **Source:** `core/model.mod` — 57 lines @ `8c6cb8f`
> **Scope:** this documentation set covers `core/` only. The `.mod` files
> under `scenarios/` (`study.mod`, `axes/*.mod`, `report.mod`) are
> deliberately out of scope.
> Update these docs whenever the corresponding `.mod` changes.

**Start here.** This page is the entry point: what the model is, how it fits
together, what the numbers mean, and where the soft spots are. Each `.mod`
file in `core/` has a paired `.md` in this directory.

---

## 1. What the model does, in one paragraph

Indian crude-steel demand is **exogenous**: 152.2 Mt in 2025 growing 5%/yr to
515 Mt in 2050. The model chooses, for each of 26 years, **how** to make that
steel — across five production routes, with capacity that must be built,
paid for and utilised — so as to **minimise the discounted total system
cost**, subject to a **cumulative CO2 budget** and to hard limits on scrap,
natural gas and coking coal availability. It never chooses *how much* steel
to make. Every result is therefore a statement about the least-cost way to
serve fixed demand under a carbon budget.

## 2. Problem class — it is a pure LP

Measured on the committed baseline (`amplpy` + `option show_stats 1`):

| | variables | constraints |
|---|---|---|
| as written (presolve off) | 4 184 — **52 nonlinear** | 4 911 — **25 nonlinear** |
| as solved (presolve on) | 3 921 — **all linear** | 4 278 — **all linear** |

- **Zero integer or binary variables** anywhere in `core/`. Despite the
  repository name, this is not a mixed-integer program.
- The only nonlinearity is `emission_monotonic` in
  `t_additional_constraints.mod` — a bilinear product of `total_emissions`
  and `total_steel`. `meet_demand` pins `total_steel[t]` to the constant
  `dem[t]`, so presolve linearises all 25 rows.
- **Consequence: `gurobi_options 'mipgap=0.002'` is inert.** There is no
  MIP gap on an LP; objectives are exact simplex optima, not gap-limited
  approximations, and HiGHS/Gurobi agree to ~1e-16 relative.
- This was measured on `core/model.mod`. It holds *a fortiori* for all six
  Section A studies: each one issues `drop emission_monotonic;` in its
  `run.py`, removing the only nonlinear constraint outright, and none of them
  touches `meet_demand`, `base_demand` or `growth_rate`. **Section B is a
  different matter** — `regret-analysis` drops `meet_demand` and adds
  `steel_import`, which unfixes `total_steel`; if it retains
  `emission_monotonic` the model becomes genuinely bilinear. Check that
  before assuming Section B is an LP.

Baseline objective, bit-identical across all eight legacy studies and
`core/model.mod`: **2 008 395 874 830.759766** (discounted $, 2025-2050).

## 3. Structure of `core/`

```
core/
  model.mod            # set T, include order, objective — no solver, no solve, no report
  definitions.mod      # every parameter (incl. derived)
  variables.mod        # 128 variable blocks (v_capacity.mod adds 30 more)
  parameters.mod       # baseline values + avg_emi + H2_cap + No_H2_Before
  yreport.mod          # post-solve printf tables (NOT included by model.mod)
  modules/
    a_coke  b_sinter  c_pellets_bf  d_blast_furnace  e_bof        # BF-BOF chain
    f_pellets_coaldri  g_pellets_ngdri  h_pellets_h2dri           # DRI pellet plants
    i_dri_coal  j_dri_ng  k_dri_h2                                # DRI shafts
    l_eaf_dri  m_scrap_eaf  n_steel_balance                       # melting + totals
    q_carbon_capture  o_waste_heat  p_power_balance               # cross-cutting energy
    v_capacity  r_cost  s_emissions  t_additional_constraints     # capital, cost, CO2, policy
```

`model.mod` itself is only an include list plus:

```ampl
reset;
set T ordered := 2025..2050;

param discount_factor{t in T} := 1 / (1 + real_discount_rate)^(ord(t) - 1);

minimize obj: sum {t in T} discount_factor[t] * total_cost[t];
```

**Include order is load-bearing.** `definitions` → `variables` →
`parameters` (which constrains `h2dri_h2_in`, so it must follow `variables`)
→ process chain → cross-cutting systems → objective.

**Invocation contract:** AMPL resolves `include` against its *current working
directory*, not against the including file. Every path in `model.mod` is
repo-root-relative, so scenarios must run with the repository root as cwd
(`ampl.cd(ROOT)` in amplpy).

## 4. The five routes

All per-tonne figures below were **read off solved runs** (`amplpy` +
HiGHS), not derived by hand — 2025 baseline except where marked 2050, since
the H2 and scrap routes have no 2025 output. Intensities are per tonne of
**crude steel**, so the DRI rows are diluted by their pinned scrap blends.

| Route | Reductant | 2025 share | 2025 capacity | Scope-1 tCO2/tCS | Power kWh/tCS |
|---|---|---|---|---|---|
| **BF-BOF** | coke + PCI coal | 51.0% | 90.0 Mt | **2.654** | 396.5 gross, 112.0 recovered → **284.5 net** |
| **coal-DRI-EAF/IF** | non-coking coal | 44.2% | 104.1 Mt | **1.847** | **1 015** (2.64 tCO2 and 1 194 kWh per *t-DRI*) |
| **NG-DRI-EAF** | natural gas | 4.8% | 12.9 Mt | **0.974** | **1 066** |
| **H2-DRI-EAF** | green hydrogen | 0% | 0 | **0.0528** *(2050)* | **1 115 grid + 4 235 dedicated RE** *(2050)* |
| **scrap-EAF** | none (100% scrap) | 0% | 0.75 Mt | **0.0528** *(2050)* | **785** |

The shared 664 kWh/tCS DRI-EAF dominates all three DRI rows, which is why
their grid-power intensities cluster within ~10% of each other despite very
different shaft coefficients. The BF-BOF route is the *least* electricity-
intensive and the *most* carbon-intensive; the ordering reverses entirely
once Scope 2 is added at a dirty grid — the tension the grid study probes.

The three DRI routes share **one** EAF (`l_eaf_dri.mod`); the dedicated
scrap-EAF is separate (`m_scrap_eaf.mod`). Scrap enters three ways —
blended into the BOF charge, blended into any DRI-EAF charge, or as 100%
charge in the scrap-EAF — and all three draw on one availability pool.

Route shares are reported two-deep: `f_bof` and `f_eaf` are shares of demand;
`f_cdri`, `f_ngdri` and the H2 residual are shares **of the DRI-EAF pool**.
A route's share of demand is the product.

## 5. The decision levers

What the optimiser actually chooses:

| Lever | Where | Bounded by |
|---|---|---|
| route mix (`f_bof`, `f_eaf`, and the DRI split) | `e_bof`, `l_eaf_dri`, `k_dri_h2` | capacity, utilisation, availability |
| build capacity per route per year | `v_capacity` | `cap_add_common` (10 Mt/yr default) |
| retire incumbents faster than the ceiling | `v_capacity` | linear decay to zero by 2050 |
| scrap blend share per route | `e_bof`, `i_dri_coal`, `j_dri_ng`, `k_dri_h2` | `phi_min/max`, 5 pp/yr ramp, scrap pool |
| CO2 captured per stream | `q_carbon_capture` | physical 76.5%, sector ramp, retrofit capacity, steam |
| waste-heat pool → power vs CCS steam | `o_waste_heat` | 0.3 × `n9_whr[t]` of surplus gas |
| electrolyser + dedicated RE build | `v_capacity` | Gaussian ramp around `h2_peak_year` |
| supply-chain capacity (scrap/coal/NG) | `v_capacity` | ratchet, only scrap is priced |

What it does **not** choose: demand, the blast furnace's efficiency drift,
the breeze→biochar switch, the grid emission factor or tariff, the CCS
deployment ceiling, or the WHR penetration curve. All of those are exogenous
trajectories.

## 6. The three scenario dials

`theta_tech`, `theta_grid`, `theta_ccs` ∈ [0,1], each **0.5 in the baseline**.
Each interpolates between a named slow and fast 2050 endpoint, and the result
is then interpolated back to a fixed 2025 anchor:

| Dial | 2025 anchor | 2050 slow (θ=0) | 2050 fast (θ=1) |
|---|---|---|---|
| `theta_tech` | electrolyser 850 $/kW, RE 800 $/kW | 550 / 600 | 150 / 200 |
| `theta_grid` | tariff 0.07 $/kWh, EF 0.000886 | 0.085 / 0.0006 | 0.055 / 0.0003 |
| `theta_ccs` | ≈531 $/(tCO2/yr) overnight | −30% by 2050 | −80% by 2050 |

2050 hydrogen cost is **never specified directly** — it emerges from the
electrolyser/RE capex build-up plus a firming residual calibrated so 2025
LCOH equals $5/kg. The intended bands are ≈$3.7/kg at θ_tech = 0 and
≈$1.8/kg at θ_tech = 1.

Studies also sweep `avg_emi` (the carbon budget), `ng_h2_start_year` (the H2
debut, which drags the build ramp's crest with it), `n8_scrap_rate`, the
three ramp levels (`cap_add_common` / `h2_ref_cap`), and the availability
caps.

## 7. Cost and emissions accounting at a glance

**Objective** = Σ_t `discount_factor[t] × total_cost[t]` at a 6% real rate.

`total_cost[t]` = 13 process cost variables (`r_cost.mod`) + `other_opex ×
total_steel` + `capex_cost` + `fixopex_cost` (`v_capacity.mod`) + `whr_cost`
− the WHR power credit.

Capital regime is selected by `sunk` (default **1**): overnight capex booked
on *builds*, fixed opex on *installed capacity*, so **idle capacity costs
money** and premature transitions strand assets. At `sunk = 0` both are
charged on production and capacity is free optionality.

**Emissions**: Scope 1 from fuel and calcination (`s_emissions.mod`) +
Scope 2 from net grid draw (`p_power_balance.mod` → `n9_grid_ef[t]`) −
captured CO2. Green hydrogen's electricity is **off the grid balance** by
design — it is supplied by dedicated renewables whose capital *is* charged
but whose energy carries no grid EF.

**Emissions pressure** is a single scalar constraint over the whole horizon:
Σ`total_emissions` ≤ `avg_emi` × Σ`total_steel`. At `avg_emi = 1.8` that is a
budget of ≈14.0 GtCO2. **There is no carbon price in the objective** —
`carbon_tax` is declared but never enters it, so the shadow price of this
constraint *is* the implicit carbon price.

## 8. 2025 is fully pinned

Every 2025 quantity is fixed by initialisation constraints — route shares
(51/49/0, and 90.2% of DRI-EAF on coal), scrap blends (`phi0_*`), scrap-EAF
output (0), legacy capacity seeds, and no new builds. **Objective differences
between scenarios come entirely from 2026-2050.** Useful when interpreting
small relative gaps.

---

## 9. Consolidated caveats

The soft spots, gathered from the per-file docs. Ordered by how much they
could change a conclusion.

### Confirmed errors

| # | Issue | Where | Impact |
|---|---|---|---|
| 1 | **WHR route credit uses 0.9 where the physical chain uses 0.3** — a 3× overstatement, and it also ignores the pool's split to CCS steam | [`yreport.md`](yreport.md) 1-2, [`o_waste_heat.md`](modules/o_waste_heat.md) 2-3 | **Reporting only** — objective and optimal solutions unaffected. Every published per-route $/tCS over-credits waste heat. |
| 2 | **BOF power missing from BF-BOF's reported emissions intensity** (174 kWh/tCS, the largest term in that chain) | [`yreport.md`](yreport.md) 4 | Reporting only. Understates BF-BOF Scope 2 by ~40%. |
| 3 | **Pellet ore coefficient divides where the comment says multiply** — 0.909 t ore/t pellet instead of 1.1 | [`c_pellets_bf.md`](modules/c_pellets_bf.md) 1 | Affects the objective. Applied identically in all four pellet modules, so route-neutral; understates ore cost ~17% across the board. |
| 4 | **"TOTAL H2 USED" reports crude steel, not hydrogen** | [`yreport.md`](yreport.md) 10 | Reporting only; header and units both wrong. |

### Structural assumptions that drive results

| # | Issue | Where |
|---|---|---|
| 5 | **BF-BOF decarbonises for free.** Coke rate 0.53→0.48 and biomass PCI 0→0.053 t/thm arrive on a fixed schedule with no capex, no ramp, no dependence on the carbon budget. PCI *coal* meanwhile rises 0.15→0.16. | [`d_blast_furnace.md`](modules/d_blast_furnace.md) 1-2, [`b_sinter.md`](modules/b_sinter.md) 1 |
| 6 | **Green H2's renewables are matched annually, not hourly.** A 35%-CF fleet is deemed to supply a continuous electrolyser; the gap is priced by a *calibration residual* (`h2_firm_capex`), not an engineered cost. | [`p_power_balance.md`](modules/p_power_balance.md) 1, [`v_capacity.md`](modules/v_capacity.md) 6, [`definitions.md`](definitions.md) 7 |
| 7 | **The baseline embeds an undeclared NG supply shock**: `n5_ng_cap` drops 28% in 2035 and jumps 35% in 2041. Any NG-DRI dip in the late 2030s is partly imposed. The matching *price* shock is commented out. | [`parameters.md`](parameters.md) 2-3, [`j_dri_ng.md`](modules/j_dri_ng.md) 1 |
| 8 | **The carbon constraint is a cumulative 26-year budget, not an annual target**, and `emission_monotonic` (the only trajectory shaper) is the constraint scenarios most often drop. | [`t_additional_constraints.md`](modules/t_additional_constraints.md) 1 |
| 9 | **Incumbent capacity is forced to zero by 2050** by construction, regardless of age or economics. | [`v_capacity.md`](modules/v_capacity.md) 2 |
| 10 | **`h2_ramp_mode = 0` is a three-in-one switch** — it disables the H2 ramp *and* the utilisation band *and* the per-route build ceilings. | [`v_capacity.md`](modules/v_capacity.md) 1 |
| 11 | **Scrap-EAF is charged 785 kWh/tCS for all 26 years** (75% induction furnace weighting), so new-build scrap capacity in 2045 is as inefficient as the 2025 fleet. | [`m_scrap_eaf.md`](modules/m_scrap_eaf.md) 1 |
| 12 | **Commodity prices are flat in real terms for 26 years.** Only power, NG, H2 and CCS have trajectories, so route competition is driven almost entirely by the three θ dials. | [`r_cost.md`](modules/r_cost.md) 5, [`definitions.md`](definitions.md) 6 |
| 13 | **Overnight capex is booked in the build year with no terminal value**, biasing against late builds. | [`v_capacity.md`](modules/v_capacity.md) 4 |
| 14 | **H2-DRI has no scrap-blend ramp constraint** while coal- and NG-DRI are held to 5 pp/yr. | [`k_dri_h2.md`](modules/k_dri_h2.md) 1 |
| 15 | **No net-zero pathway exists.** H2 and scrap routes have no capture option; there is no BECCS, no DAC, and `total_emissions >= 0`. | [`q_carbon_capture.md`](modules/q_carbon_capture.md) 4-5, [`s_emissions.md`](modules/s_emissions.md) 3 |
| 16 | **Scope 3 is entirely absent** — no upstream methane, mining or transport emissions. Most material for NG-DRI. | [`s_emissions.md`](modules/s_emissions.md) 5 |

### Reachability and maintainability

| # | Issue | Where |
|---|---|---|
| 17 | **`real_discount_rate` is a defined param (`:=`)** and so cannot be swept from a scenario, despite driving every CRF and the discount factor. Same for `n7_e_eaf`, `n8_e_eaf`, `fc_max`, `phi_2050`, `ccs_avail`, `h2_peak_rate`, `h2_gauss_sigma`. | [`definitions.md`](definitions.md) 1-2, [`q_carbon_capture.md`](modules/q_carbon_capture.md) 2 |
| 18 | **The 0.3 waste-heat recovery factor is a bare literal**, not a declared parameter — the largest single derating in the chain, and unsweepable. | [`o_waste_heat.md`](modules/o_waste_heat.md) 1 |
| 19 | **Emission factors are hardcoded inline and duplicated across six sites** in `s_emissions.mod` and `q_carbon_capture.mod`. Nothing enforces consistency between the emitted amount and the capturable base. | [`s_emissions.md`](modules/s_emissions.md) 2, [`q_carbon_capture.md`](modules/q_carbon_capture.md) 1 |
| 20 | **`core/parameters.mod` is not a data file** — it declares `avg_emi`, `H2_cap` and the constraint `No_H2_Before`. Any "swap the parameters file per scenario" design must carry all three. | [`parameters.md`](parameters.md) 1 |
| 21 | **`n5_ng_cap` has no default** — a scenario that omits it fails on an uninitialised parameter rather than defaulting to unbounded. | [`definitions.md`](definitions.md) 3, [`parameters.md`](parameters.md) |
| 22 | **`carbon_tax` is declared but absent from the objective** — setting it changes reported route costs and nothing else. | [`r_cost.md`](modules/r_cost.md) 1 |
| 23 | **Route costs are not a decomposition of `total_cost`** (different capital convention; incumbent capital excluded). The claimed present-value reconciliation is asserted, not verified. | [`yreport.md`](yreport.md) 3 |
| 24 | **Per-route Scope 1 does not sum to the Scope-1 total** — electrode oxidation and CCS boiler fuel appear only in the total. | [`s_emissions.md`](modules/s_emissions.md) 1 |
| 25 | **`bf_h2_in` is dead** (forced to zero) but still referenced by `yreport.mod`'s H2 capital allocation denominator. | [`d_blast_furnace.md`](modules/d_blast_furnace.md) 3 |
| 26 | **Coal and NG supply chains are modelled but cost zero** — ~150 constraints with no effect on the objective. | [`v_capacity.md`](modules/v_capacity.md) 5 |
| 27 | **Breeze is sold at 55 $/t and bought back at 85 $/t in the same year.** | [`a_coke.md`](modules/a_coke.md) 3 |

---

## 10. File index

| Doc | Source | Lines | Covers |
|---|---|---|---|
| [`definitions.md`](definitions.md) | `core/definitions.mod` | 368 | every parameter; the mutable-vs-defined distinction |
| [`variables.md`](variables.md) | `core/variables.mod` | 169 | 128 variable blocks |
| [`parameters.md`](parameters.md) | `core/parameters.mod` | 60 | baseline values, `avg_emi`, `No_H2_Before` |
| [`yreport.md`](yreport.md) | `core/yreport.mod` | 331 | post-solve reporting |
| [`modules/a_coke.md`](modules/a_coke.md) | | 26 | coke oven |
| [`modules/b_sinter.md`](modules/b_sinter.md) | | 29 | sinter plant |
| [`modules/c_pellets_bf.md`](modules/c_pellets_bf.md) | | 6 | BF pellet plant |
| [`modules/d_blast_furnace.md`](modules/d_blast_furnace.md) | | 47 | blast furnace |
| [`modules/e_bof.md`](modules/e_bof.md) | | 35 | BOF + BF-BOF scrap blend |
| [`modules/f_pellets_coaldri.md`](modules/f_pellets_coaldri.md) | | 7 | coal-DRI pellet plant |
| [`modules/g_pellets_ngdri.md`](modules/g_pellets_ngdri.md) | | 7 | NG-DRI pellet plant |
| [`modules/h_pellets_h2dri.md`](modules/h_pellets_h2dri.md) | | 8 | H2-DRI pellet plant |
| [`modules/i_dri_coal.md`](modules/i_dri_coal.md) | | 33 | coal-DRI route |
| [`modules/j_dri_ng.md`](modules/j_dri_ng.md) | | 37 | NG-DRI route |
| [`modules/k_dri_h2.md`](modules/k_dri_h2.md) | | 27 | H2-DRI route + DRI route split |
| [`modules/l_eaf_dri.md`](modules/l_eaf_dri.md) | | 36 | shared DRI-EAF |
| [`modules/m_scrap_eaf.md`](modules/m_scrap_eaf.md) | | 21 | dedicated scrap-EAF |
| [`modules/n_steel_balance.md`](modules/n_steel_balance.md) | | 4 | total steel balance |
| [`modules/o_waste_heat.md`](modules/o_waste_heat.md) | | 46 | waste-heat pool + CCS steam competition |
| [`modules/p_power_balance.md`](modules/p_power_balance.md) | | 28 | site electricity balance |
| [`modules/q_carbon_capture.md`](modules/q_carbon_capture.md) | | 61 | CO2 capture |
| [`modules/r_cost.md`](modules/r_cost.md) | | 143 | cost equations |
| [`modules/s_emissions.md`](modules/s_emissions.md) | | 46 | CO2 accounting |
| [`modules/t_additional_constraints.md`](modules/t_additional_constraints.md) | | 30 | init, demand, availability, policy |
| [`modules/v_capacity.md`](modules/v_capacity.md) | | 235 | capacity, vintaging, ramps, supply chains |

## 11. Keeping these docs true

Each doc carries a `Source:` line with its `.mod` path, line count and the
commit it was written against. Two cheap checks:

```bash
# 1. Which docs are stale? Compare recorded line counts against the source.
wc -l core/*.mod core/modules/*.mod

# 2. Is every constraint documented? Every `s.t. <name>` in a .mod
#    should appear in its paired .md. NOTE: this checks name PRESENCE only —
#    it cannot verify that the prose is correct, and an equivalent check on
#    `eqNN` tags is near-vacuous (grepping for "18" matches almost any
#    prose). Numeric claims must be verified against a solved model.
for f in core/modules/*.mod; do
  b=$(basename "$f" .mod)
  grep -oP 's\.t\.\s+\K\w+' "$f" | while read -r c; do
    grep -q "$c" "docs/core/modules/$b.md" || echo "MISSING: $b :: $c"
  done
done
```
