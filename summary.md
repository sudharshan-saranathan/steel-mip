# Steel Decarbonisation MIP — Model Documentation (Methodology Precursor)

> **Purpose.** This document is an exhaustive, equation-level description of the
> steel-sector decarbonisation optimisation model on the `mip-v2`
> (capex-opex-framework) branch. It is written to be lifted, condensed and
> formalised into the **Methodology** section of a paper, so it states every set,
> variable, parameter, constraint and modelling assumption, with units, values,
> rationale and the corresponding source file / equation tag.
>
> **Maintenance.** Keep this in sync with the code in the same commit that changes
> the model. Equation tags (`eq1`…`eq112`) match the `# eqN` comments in the
> `.mod` sources. Section headers are stable to keep diffs readable.
>
> **Last synced to code:** 2026-06-27, branch `mip-v2` (capex-opex-framework, plus
> the review fixes in this commit: CO₂ target relaxed to an upper-bound cap;
> per-route reported capex now excludes the free legacy fleet; dead code removed;
> `u_lockin.mod` deleted). Implementation: **AMPL** (GMPL-style `.mod`), solver
> **Gurobi**.

---

## 1. Scope, purpose and modelling paradigm

The model computes the **least-cost transition pathway for a national crude-steel
sector over 2025–2050** subject to a cumulative average CO₂-intensity cap. It is a
**deterministic, multi-period linear program (LP)**. (Historically it carried
binaries for CCS phase-in and an unused `z`; these have been removed during the move
to the capacity-expansion framework, so the current model has **no integer
variables**. The repository and filenames retain the "MIP" label for continuity.)

It answers: *given exogenous, growing steel demand and a binding lifetime
CO₂-intensity budget, how much of each steelmaking route's **capacity** should be
**built** in each year, how much steel should each route **produce**, and how much
CO₂ should be **captured**, so that total discounted system cost is minimised?*

Three design commitments distinguish this branch from a conventional LCOE screening
model:

1. **Capacity stock with vintaging.** Each route carries an explicit installed
   capacity that is *built* (sunk) in discrete vintages and *retires* after a
   route-specific asset life. Production is bounded by installed capacity, not
   chosen freely (§7).
2. **Overnight, fully sunk capital.** Capex is booked in full in the build year with
   **no salvage / resale credit** for residual asset life. Industrial capital has no
   liquid resale market; a salvage credit would make terminal-year capacity nearly
   free and end-load all investment. This *irreversibility* is the paper's thesis,
   and is made falsifiable through the `sunk` ablation toggle (§7.4).
3. **Fixed vs variable cost separation.** Labour + maintenance are charged as
   **fixed O&M on installed capacity** (incurred whether or not the plant runs);
   only feedstock/energy/consumables and a residual "other opex" scale with
   production. Idle capacity therefore costs money — the economic mechanism that
   discourages build-then-strand.

### 1.1 Solver and numerical settings

| Setting | Value | Source |
|---|---|---|
| Solver | Gurobi | `main.mod` |
| MIP gap | `0.002` (0.2 %) | `main.mod` |
| Threads | 10 (sweeps use 5) | `main.mod` / `template.mod` |
| Time limit | none (sweeps: 600 s) | `template.mod` |
| Real discount rate `r` | 0.06 | `definitions.mod` |

---

## 2. Sets, indices and notation

| Symbol | Definition |
|---|---|
| `T` | Ordered set of years, `2025..2050` (26 periods). `first(T)=2025`. |
| `t`, `j`, `s` | Year indices over `T`. `ord(t)` is the 1-based position; `prev(t)` the preceding year. |
| `r` | Real discount rate, 0.06. |
| `dem[t]` | Exogenous crude-steel demand in year `t` (tonnes), §3. |

Discount factor (`main.mod`):
```
discount_factor[t] = 1 / (1 + r)^(ord(t) - 1)        # 1.0 in 2025
```

Naming convention in the source: process technical coefficients are prefixed
`n0_…n10_` by unit (n0 coke oven, n1 sinter, n2 BF, n3 BOF, n4 coal-DRI, n5 NG-DRI,
n6 H₂-DRI, n7 DRI-EAF, n8 scrap-EAF, n9 WHR, n10 CCS); global market prices are
prefixed `ng_…`. Flow variables are named `<unit>_<stream>_<in/out>`.

---

## 3. Demand (exogenous driver)

`definitions.mod`, `parameters.mod`, `t_additional_constraints.mod`:
```
base_demand = 152 200 000 t           # 2025 crude-steel production
growth_rate = 0.05                    # annual
dem[t]      = base_demand * (1 + growth_rate)^(ord(t) - 1)
```
Demand is pinned (`meet_demand`, eq in `t_additional_constraints`):
```
total_steel[t] = base_demand * (1 + growth_rate)^(ord(t) - 1)        # eq, pins total
```
Pinning total steel to a constant `dem[t]` is what linearises the route-share
products `f_bof[t]*dem[t]` and `f_eaf[t]*dem[t]` (they become linear in the
fraction). Demand grows from 152.2 Mt (2025) to ≈516 Mt (2050).

---

## 4. Production routes and the steel balance

Five routes compete to supply `total_steel[t]`:

| # | Route | Output variable | Capacity var | 2025 seed `cap0_*` | Asset life `life_*` |
|---|---|---|---|---|---|
| 1 | **BF-BOF** integrated | `steel_bof` | `cap_bof` | 90.00 Mt | 25 yr |
| 2 | **Coal-DRI → EAF** | `coaldri_output` | `cap_cdri` | 63.54 Mt | 20 yr |
| 3 | **NG-DRI → EAF** | `ngdri_output` | `cap_ngdri` | 11.61 Mt | 15 yr |
| 4 | **H₂-DRI → EAF** (future entrant) | `h2dri_output` | `cap_h2dri` | 0 | 15 yr |
| 5 | **Scrap-EAF** | `steel_scrap_eaf` | `cap_scrap` | 33.50 Mt | 10 yr |

**Crude-steel-equivalent basis.** The three DRI route outputs are expressed on the
crude-steel-equivalent basis `0.9 · steel_eaf` (i.e. divided by `1 − n7_phi_eaf`,
with `n7_phi_eaf = 0.1` the scrap charge fraction of the DRI-EAF), because each DRI
route carries its share of the shared DRI-EAF melt. The 2025 seeds are converted on
the same basis (e.g. coal-DRI 70.6 Mt crude → 63.54 Mt on the output basis).

**Steel balance** (`n_steel_balance`, eq77):
```
steel_eaf[t] + steel_bof[t] + steel_scrap_eaf[t] = total_steel[t]
```
where `steel_eaf` is the **shared DRI-EAF** crude steel (fed by all three DRI
routes plus its own scrap charge).

**Route-share linking variables.** `f_bof[t] ∈ [0,1]` and `f_eaf[t] ∈ [0,1]` are
the BF-BOF and DRI-EAF shares of demand. Scrap-EAF takes the residual. The DRI
route fractions `f_cdri`, `f_ngdri` are **not** variables — the route *outputs* are
the decisions and the fractions are reconstructed post-solve (`yreport.mod`).

---

## 5. Process flowsheet — material & energy balances

Each unit operation is a set of **linear input/output coefficients** tying a stream
to a route's activity level. All balances hold `∀ t ∈ T`. Equation tags match the
`# eqN` comments. Calorific values (CV) convert gas volumes (Nm³) to energy (GJ):
`ng_cog_cv=0.018`, `ng_bfg_cv=0.0033`, `ng_bofg_cv=0.008`, `ng_sintgas_cv=0.0006`
GJ/Nm³.

### 5.1 BF-BOF chain

The BF-BOF chain is driven bottom-up from `steel_bof[t]`; hot metal `bf_hot_metal`
equals `steel_bof` (eq32), and coke/sinter/pellet demands cascade upward.

**Coke oven** (`a_coke`, eq1–eq8), per tonne of coke `bf_coke_in`:
| Eq | Stream | Coefficient |
|---|---|---|
| eq1 | power in | `n0_e_c = 75` kWh/t |
| eq2 | coking coal in | `n0_cf = 1.47` t/t |
| eq3 | breeze out | `n0_br_c = 0.056` t/t |
| eq4 | tar out | `n0_tar_c = 0.04` t/t |
| eq5 | COG produced | `n0_cog_c = 440` Nm³/t |
| eq6 | CDQ waste-heat power out | `n0_cdq_whr = 80` kWh/t |
| eq7 | COG recovered as fuel | `n0_rec_cog = 190` Nm³/t × CV |
| eq8 | BFG recovered as fuel | `n0_rec_bfg = 270` Nm³/t × CV |

**Sinter plant** (`b_sinter`, eq9–eq15), per tonne of sinter `bf_sinter_in`:
power `n1_e_sint=50` kWh; lime `0.04`; fine ore `0.9`; breeze and biochar are
**time-interpolated** 2025→2050 (breeze `0.09→0.058`, biochar `0→0.022` t/t — a
partial biochar substitution); sinter-cooler WHR power `30` kWh; sinter gas `1800`
Nm³ × CV.

**BF pellet plant** (`c_pellets_bf`, eq16–eq17): power `ng_e_pell=200` kWh per t
pellets; fine ore `= pellets / ng_ore_pell` (`ng_ore_pell=1.1`).

**Blast furnace** (`d_blast_furnace`, eq18–eq32), per tonne hot metal:
power `55` kWh; sinter `1.15`; lime `0.025`; slag `0.3`; pellets `0.35`; lump ore
`0.15`; recovered BFG/COG and top-pressure recovery turbine (TRT) power `35` kWh;
and **time-interpolated** injectant rates 2025→2050: PCI coal `0.15→0.16`, biomass
PCI `0→0.053`, coke `0.53→0.44`, in-furnace H₂ `0→0.013` t/thm. Eq32 sets
`steel_bof = bf_hot_metal` (BOF yield folded into coefficients).

**BOF** (`e_bof`, eq33–eq39), per tonne BOF steel: power `n3_e_bof=174` kWh; scrap
`0.10`; lime `0.075`; slag `0.10`; BOF gas `100` Nm³ × CV; recovered COG `65` Nm³.
Eq38 is the share link `f_bof[t]·dem[t] = steel_bof[t]`.

### 5.2 DRI–EAF routes

**DRI pellet plants** (`f/g/h_pellets_*`, eq40–eq45): identical structure per route,
fine ore `= pellets / 1.1`, power `200` kWh/t pellets.

**Coal-DRI** (`i_dri_coal`, eq47–eq50) per t DRI: power `n4_e_dri=100` kWh; pellets
`1.5`; lump ore `0.1`; coal `n4_c_dri=1.0` t/t.

**NG-DRI** (`j_dri_ng`, eq52–eq55) per t DRI: power `120` kWh; pellets `1.5`; lump
ore `0.1`; natural gas `n5_ng_dri=0.35` t/t.

**H₂-DRI** (`k_dri_h2`, eq57–eq60) per t DRI: power `n6_e_dri=110` kWh; pellets
`1.5`; lump ore `0.1`; hydrogen `n6_h2_dri=0.13` t/t.

**DRI route split** (`k_dri_h2`, eq56) — the key linearisation:
```
coaldri_output[t] + ngdri_output[t] + h2dri_output[t] = dri_eaf_steel_out[t]
```
The optimizer chooses the three route outputs directly (replacing the former
bilinear `f_route · dri_eaf_steel_out`); `h2dri_output ≥ 0` implicitly enforces
`f_cdri + f_ngdri ≤ 1`.

**Shared DRI-EAF** (`l_eaf_dri`, eq61–eq69) per tonne `steel_eaf`:
| Eq | Quantity | Coefficient |
|---|---|---|
| eq61 | EAF share of demand | `f_eaf[t]·dem[t] = steel_eaf[t]` |
| eq62 | power | `n7_e_eaf[t]` = **650→500** kWh (linear 2025→2050) |
| eq63 | scrap charge | `n7_phi_eaf = 0.10` t/t |
| eq64 | electrode | `0.003` t/t |
| eq65 | lime | `0.06` t/t |
| eq66 | coal | `0.01` t/t |
| eq67 | slag | `0.15` t/t |
| eq68 | EAF off-gas | `3` GJ/t |
| eq69 | DRI + scrap = EAF steel | `steel_eaf − eaf_scrap_in − dri_eaf_steel_out = 0` |

**Scrap-EAF** (`m_scrap_eaf`, eq70–eq76) per tonne `steel_scrap_eaf`: power
`n8_e_eaf[t]` = **820→650** kWh (linear); scrap `n8_phi_eaf=1.1` t/t; electrode
`0.003`; lime `0.06`; coal `0.01`; slag `0.15`; off-gas `3` GJ/t.

### 5.3 Waste-heat recovery (WHR)

`o_waste_heat`, eq78–eq82. BF-BOF off-gases (COG + BFG + BOF gas, net of internal
fuel recycling) and EAF/scrap-EAF off-gases form waste-heat streams. Only a fixed
fraction is recoverable:
```
whr_available_gas[t] = 0.3 · (wasteheat_bf_bof[t] + wasteheat_eaf[t] + scrap_eaf_wasteheat[t])   # eq81
whr_power_generated[t] = whr_available_gas[t] · 277.78 · n9_eta · n9_whr[t]                       # eq82
```
with WHR efficiency `n9_eta = 0.15`, the factor `277.78` (GJ→kWh), and penetration
`n9_whr[t]` ramping **0.05 → 0.30** linearly over 2025–2050. (CDQ, TRT and sinter
WHR are already credited inside the respective unit balances.)

### 5.4 Power balance

`p_power_balance`, eq83. All electricity demands minus all on-site generation net to
grid imports:
```
Σ(process power draws) + power_ccs[t]
  − cdq_power_out[t] − sinterwaste_power_out[t] − bf_trt_out[t] − whr_power_generated[t]
  = grid_power_in[t]
```
`grid_power_in[t] ≥ 0` (no export of net grid power; sell-back of specific on-site
streams is handled as cost credits, §9).

---

## 6. Carbon capture (CCS)

`q_carbon_capture.mod` (physical + deployment limits) and the CCS-capacity block in
`v_capacity.mod`. CCS is retrofittable on the three primary-CO₂ routes only —
**BF-BOF, Coal-DRI, NG-DRI** (none on H₂-DRI or scrap-EAF). The captured amounts
`ccs_bf`, `ccs_cdri`, `ccs_ngdri` are the decision variables (fully linear).

**(a) Physical capturable base per route** (`co2_capturable_*`, eqs feeding eq84–86)
— the gross CO₂ in the capture-amenable streams, ≈ the route's Scope-1:
```
co2_capturable_bf   = coking_coal·0.1116·25 + bf_coalpci·0.106·26 + (sinter+bf+bof lime)·0.44
co2_capturable_cdri = coaldri_coal·0.110·24 + (n7_cs·coaldri_output/0.9)·0.110·24 + (n7_ls·…)·0.44
co2_capturable_ngdri= ngdri_ng·0.055·50     + (n7_cs·ngdri_output/0.9)·0.110·24   + (n7_ls·…)·0.44
```
(The `(coeff · CV)` products are the same emission factors as in §10.)

**(b) Per-route physical limit** (eq84–eq86): a route can capture at most
`n10_ccs_eta · fc_max` of its base, with capture efficiency `n10_ccs_eta = 0.85` and
max per-stream rate `fc_max = 0.9`:
```
ccs_X[t] ≤ 0.85 · 0.9 · co2_capturable_X[t]
```

**(c) Sector-wide deployment ceiling** (`ccs_sector_ceiling`) — normally the binding
limit, representing pipeline/storage/permit build-out maturity:
```
ccs_bf[t]+ccs_cdri[t]+ccs_ngdri[t] ≤ ccs_avail[t] · Σ_X co2_capturable_X[t]
ccs_avail[t] = 0           for t < 2027
             = 0.50 · (t−2027)/(2050−2027)   otherwise     # 0 → 0.50 linear
```
No capture before 2027 (`no_ccs_*` in `t_additional_constraints`).

**(d) Capture energy** (`power_capture`, eq88) — stream-specific (kWh/tCO₂), feeding
both cost and Scope-2 consistently:
```
power_ccs[t] = 800·ccs_bf[t] + 850·ccs_cdri[t] + 200·ccs_ngdri[t]
```
NG-DRI is cheapest (near-pure, already-separated process CO₂); coal-DRI dearest
(dilute kiln gas); BF-BOF mid.

**(e) Total captured** (eq87): `total_ccs[t] = ccs_bf + ccs_cdri + ccs_ngdri`.

CCS retrofit **capacity** is built and vintaged exactly like route capacity (§7.5),
with `ccs_bf[t] ≤ ccs_cap_bf[t]`, etc.

---

## 7. Capacity-expansion framework (defining feature)

`modules/v_capacity.mod`. This module **supersedes the retired `u_lockin.mod`**
(still in the tree for reference, not included by `main.mod`). It replaces the old
hard production-floor lock-in with a real, costed capacity stock.

### 7.1 Capacity accounting (vintaging)

For each route `X ∈ {bof, cdri, ngdri, h2dri, scrap}`:
```
build_X[t]   ≥ 0      # capacity added (built) in year t
legacy_X[t]  ≥ 0      # surviving 2025 incumbent fleet
cap_X[t]     = legacy_X[t] + Σ_{j: t−life_X+1 ≤ j ≤ t} build_X[j]     # cap_def_X
```
A vintage built in year `j` contributes to capacity until `j + life_X − 1`, then
**retires automatically**.

### 7.2 Legacy fleet retirement

The 2025 incumbent stock is pinned to the seed and then declines:
```
legacy_X[2025] = cap0_X                                   # legacy_init_X
legacy_X[t]   ≤ cap0_X · (2050 − t)/25                    # legacy_ceil_X (linear → 0 in 2050)
legacy_X[t]   ≤ legacy_X[prev(t)]                          # legacy_noninc_X (monotone non-increasing)
```
The ceiling forces a gentle ≈4 %/yr phase-out of incumbent capacity; the optimizer
may retire **faster** (sit below the ceiling) under decarbonisation pressure, never
slower.

### 7.3 Production bounded by capacity

```
steel_bof[t]       ≤ cap_bof[t]        # cap_lim_bof
coaldri_output[t]  ≤ cap_cdri[t]       # cap_lim_cdri
ngdri_output[t]    ≤ cap_ngdri[t]      # cap_lim_ngdri
h2dri_output[t]    ≤ cap_h2dri[t]      # cap_lim_h2dri
steel_scrap_eaf[t] ≤ cap_scrap[t]      # cap_lim_scrap
```
Idle capacity (`cap_X > prod_X`) still pays fixed opex — the economic deterrent to
overbuilding.

### 7.4 Cost pieces and the sunk-capital toggle

```
capex_cost[t]   =  sunk · Σ_X ocapex_X[t]·build_X[t]   +  (1−sunk) · Σ_X acapex_X[t]·prod_X[t]
fixopex_cost[t] =  sunk · Σ_X fopex_X·cap_X[t]/κ_X      +  (1−sunk) · Σ_X fopex_X·prod_X[t]/κ_X
```
where `κ_X = (1−n7_phi_eaf)=0.9` for DRI routes (to recover crude-steel capacity from
the output basis) and `1` otherwise. The **`sunk` parameter** (default `1`) is the
falsifiable ablation:
- `sunk = 1` (real model): capex on **builds**, fixed opex on **capacity** → capital
  is committed once built; idling/stranding does not recover it.
- `sunk = 0` (counterfactual): capex + fixed opex charged on **production** (classic
  LCOE) → building-then-idling is free, so technology can be switched costlessly.

`capex_cost` and `fixopex_cost` enter the total cost (eq104, §9).

### 7.5 CCS retrofit capacity

Mirror of the route framework, `life_ccs = 15` yr, legacy = 0 (no CCS in 2025):
```
ccs_cap_X[t] = Σ_{j: t−life_ccs+1 ≤ j ≤ t} build_ccs_X[j]
ccs_X[t] ≤ ccs_cap_X[t]                                    # for X ∈ {bf, cdri, ngdri}
```

### 7.6 Scrap supply-chain capacity

Collection + sensor-sorting + copper/tramp purification yards that deliver
furnace-ready scrap. 2025 capacity is pinned (free) to that year's total scrap
throughput; growth above baseline pays sunk overnight capex; monotone:
```
scrapchain_cap[2025] = bof_scrap_in + eaf_scrap_in + scrap_eaf_scrap_in        # legacy (free)
scrapchain_cap[t]   ≥ bof_scrap_in + eaf_scrap_in + scrap_eaf_scrap_in         # cover all 3 streams
scrapchain_cap[t]   ≥ scrapchain_cap[prev(t)]                                  # monotone
build_scrapchain[t] ≥ scrapchain_cap[t] − scrapchain_cap[prev(t)]              # builds pay ocapex_scrapchain
```

### 7.7 Capital-cost parameterisation

The per-route **annualised** capital charge `acapex_X` is bundled from the existing
levelized `n*_capex` figures; a **capital recovery factor** converts it to an
**overnight** figure:
```
crf_X    = r·(1+r)^L / ((1+r)^L − 1)          # L = life_X
ocapex_X = acapex_X / crf_X                    # overnight $/(t-capacity/yr)
```
Bundling (`definitions.mod`):
```
acapex_bof   = n0_capex + n1_capex + ng_capex_pell + n2_capex + n3_capex = 40+30+10+80+40 = 200
acapex_cdri  = (n4_capex_coal + ng_capex_pell + n7_capex)/0.9 = (110+10+70)/0.9 ≈ 211.1
acapex_ngdri = (n5_capex_ng   + ng_capex_pell + n7_capex)/0.9 = (90+10+70)/0.9  ≈ 188.9
acapex_h2dri[t] = (n6_capex_h2[t] + ng_capex_pell + n7_capex)/0.9   # n6_capex_h2: 120→90 over horizon
acapex_scrap = n8_capex = 70
ocapex_scrapchain = 100   ($/(t-scrap/yr), overnight)
```
CCS retrofit: `ocapex_ccs[t] = ccs_capex_share · n10_ccs_cost[t] / crf_ccs`
(`ccs_capex_share=0.8`); fixed O&M `fom_ccs[t] = 0.2 · n10_ccs_cost[t]`; non-energy
variable opex `ccs_vopex_solvent = 5` $/tCO₂. Stream multipliers
`ccs_mult_bf=1.0`, `ccs_mult_cdri=1.2`, `ccs_mult_ngdri=0.5` scale both capex and
fixed O&M.

---

## 8. Dynamics, ramps and resource-availability limits

### 8.1 Production ramp (fixed additive slab)

`t_additional_constraints` (`*_prod_up/down`). The max year-on-year change is a
**fixed slab** = `ramp_frac` × the route's **pinned 2025 production** (additive, not
compounding), reflecting roughly constant annual capital availability:
```
|prod_X[t] − prod_X[t−1]| ≤ ramp_frac · prod_X[2025]      # X ∈ {bof, cdri, ngdri, scrap}
ramp_frac = 0.15 (default; tuned 0.15–0.20)
```
H₂-DRI is exempt (future entrant, no 2025 stock) except for a multiplicative
down-floor `h2dri_output[t] ≥ 0.85·h2dri_output[t−1]` once active.

### 8.2 Hydrogen availability

`parameters.mod`. H₂ input is zero before the start year, capped on entry, then
grows by an **additive slab** (not CAGR):
```
h2dri_h2_in[t] = 0                                 for t < ng_h2_start_year   # No_H2_Before
h2dri_h2_in[t] ≤ H2_cap                            at t = ng_h2_start_year    # H2_growth_cap
h2dri_h2_in[t] − h2dri_h2_in[t−1] ≤ ramp_frac·H2_cap  for t > start year      # H2_growth_limit
H2_cap = 1 500 000 t ;  ng_h2_start_year = 2030 (parameters.mod; default 2040 in definitions.mod)
```

### 8.3 Natural-gas availability

`ng_bound`: `ngdri_ng_in[t] ≤ n5_ng_cap[t]`, a year-by-year cap (≈10 % of national
supply). Three profiles exist — **normal / BAU / shock** — selectable; the **shock**
profile (with a 2035–2040 dip) is currently live in `parameters.mod` (the
`param n5_ng_cap{T}` is declared in `definitions.mod`). Full tables in
`parameters.mod` and `ng.mod`; scenario files override them.

### 8.4 Scrap availability

`scrap_bound`: `scrap_eaf_scrap_in[t] ≤ n8_scrap_limit[t]`, where
```
n8_scrap_limit[2025] = 35 000 000 t ;   n8_scrap_limit[t] = n8_scrap_limit[t−1]·(1 + n8_scrap_rate)
n8_scrap_rate = 0.04 (definitions; regime-overridable 0.04–0.06)
```

### 8.5 CO₂-intensity policy target

The single policy driver — a **cumulative lifetime average** CO₂-intensity **cap**
(`avg_emis_cap_total`, an upper bound only), linearised by multiplying through by
`Σ total_steel`:
```
Σ_t total_emissions[t]  ≤  avg_emi · Σ_t total_steel[t]
avg_emi = 1.75 tCO₂/tCS (default; swept per run, e.g. 1.6)
```
This is a genuine carbon budget: the pathway must not *exceed* the lifetime intensity
target, but the optimizer **may overachieve** (emit less) where that is cheaper. It
binds the whole pathway, forcing enough retirement/decarbonisation to stay under
budget while meeting demand each year. *(Earlier versions used a two-sided ±eps band
that pinned emissions exactly at the target — an iso-emission device; this was
deliberately relaxed to an inequality so cleaner pathways are not penalised.)*

---

## 9. Cost equations

`r_cost.mod`, eq89–eq104. Each unit has a cost identity `cost_X[t] = Σ(price·flow) −
Σ(credit·byproduct)`; all are summed in `total_cost` (eq104). Selected forms:

**Per-process operating cost** (eq89–eq101) — examples:
```
cost_cokeov  = 184·coking_coal + 0.07·coke_power − 55·breeze − 20·tar − 0.03·cdq_power
cost_bf      = 70·lumpore + 110·pci_coal + 60·biopci + 0.07·power + 60·lime
               + ng_cost_h2[t]·bf_h2 − 0.03·trt_power − 15·slag
cost_bof     = 350·scrap + 0.07·power + 60·lime − 15·slag
cost_coaldri = 0.07·power + 70·lumpore + 98·coal
cost_ngdri   = 0.07·power + 70·lumpore + (n5_cost_NG[t]·50)·ng
cost_h2dri   = 0.07·power + 70·lumpore + ng_cost_h2[t]·h2
cost_eaf     = 350·scrap + 0.07·power + 60·lime + 98·coal + 600·electrode − 15·slag
cost_scrap_eaf = 350·scrap + 0.07·power + 60·lime + 98·coal + 600·electrode − 15·slag
```
(Power sell-back credit `ng_credit_power = 0.03` $/kWh applies to specific on-site
streams; slag credit `15` $/t; breeze `55`; tar `20`.)

**WHR cost** (eq102): `whr_cost = (n9_whr_capex + n9_whr_opex)·whr_power_generated`
= `(0.009 + 0.003)·whr_power_generated`.

**CCS cost** (eq103) — full overnight-capex + fixed-O&M + energy + solvent:
```
cost_ccs = ocapex_ccs[t]·Σ_X mult_X·build_ccs_X
         + fom_ccs[t]   ·Σ_X mult_X·ccs_cap_X
         + 0.07·power_ccs                       # grid-responsive capture energy
         + 5·total_ccs                          # solvent make-up
```

**Total cost** (eq104):
```
total_cost[t] = Σ cost_X[t]                     # all process + CCS costs above
              + other_opex·total_steel[t]        # = 10·total_steel (variable residual opex)
              + capex_cost[t]                    # overnight capex on builds (§7.4)
              + fixopex_cost[t]                  # fixed labour+maint on capacity (§7.4)
              + whr_cost[t]
```
Note labour (20) + maintenance (15) now enter **only** via `fixopex_cost` on
capacity; `other_opex = 10` is the per-tonne residual. The **objective**
(`main.mod`) is `min Σ_t discount_factor[t]·total_cost[t]`.

---

## 10. Emissions accounting

`s_emissions.mod`, eq105–eq112. Emission factors are expressed as `(carbon-content ·
energy/oxidation factor)` products; the effective tCO₂ per tonne of input are:

| Stream | Effective factor (tCO₂/t input) | Source term |
|---|---|---|
| Coking coal | 2.79 (`0.1116·25`) | scope1, capturable_bf |
| BF PCI coal | 2.756 (`0.106·26`) | scope1, capturable_bf |
| DRI / EAF coal | 2.64 (`0.110·24`) | scope1, capturable_cdri |
| Natural gas (NG-DRI) | 2.75 (`0.055·50`) | scope1, capturable_ngdri |
| Limestone / flux | 0.44 | all routes |
| Electrode | 6 | EAF routes |

**Scope 1** (direct, eq110, total over all routes):
```
scope1_emissions = 2.79·coking_coal + 2.756·bf_pci
                 + 2.64·(coaldri_coal + eaf_coal + scrap_eaf_coal)
                 + 2.75·ngdri_ng
                 + 0.44·(all limes) + 6·(all electrodes)
```
Per-route Scope-1 (`scope1_bf/cdri/ngdri/h2dri/scrapeaf`, eq105–eq109) use the same
factors restricted to each route's streams (with the linearised
`n7_cs·route_output/0.9` and `n7_ls·route_output/0.9` for the shared-EAF coal/lime
attribution).

**Scope 2** (indirect, grid electricity, eq111):
```
scope2_emissions = n9_grid_ef[t] · grid_power_in[t]
n9_grid_ef[t] = 0.000886 → 0.0003 tCO₂/kWh (linear 2025→2050)   # decarbonising grid
```

**Net total** (eq112): `total_emissions = scope1 + scope2 − total_ccs`.

This `total_emissions[t]` is exactly what the §8.5 lifetime-average intensity cap
constrains.

---

## 11. Initialisation and 2025 calibration

`t_additional_constraints.mod` pins the 2025 route mix to observed shares:
```
f_bof[2025]  = 0.38                                   # BF-BOF share
f_eaf[2025]  = 0.43                                   # DRI-EAF share (⇒ scrap-EAF residual 0.19)
coaldri_output[2025] = 0.884 · dri_eaf_steel_out[2025]  # coal:NG = 0.884:0.116 within DRI
```
So 2025 ≈ BF-BOF 0.38 / Coal-DRI 0.38 / NG-DRI 0.05 / Scrap 0.19 of total steel. The
capacity seeds `cap0_*` (§4) are calibrated to this mix on each route's output basis.

---

## 12. Parameter reference tables

### 12.1 Technical coefficients (`definitions.mod`)
Listed inline by unit in §5. Time-interpolated coefficients (linear 2025→2050):
sinter breeze `0.09→0.058`, sinter biochar `0→0.022`; BF PCI `0.15→0.16`, BF biomass
`0→0.053`, BF coke `0.53→0.44`, BF H₂ `0→0.013`; DRI-EAF power `650→500`; scrap-EAF
power `820→650`; WHR penetration `0.05→0.30`; grid EF `0.000886→0.0003`.

### 12.2 Market prices and costs (`definitions.mod`; runtime `let` overrides in `parameters.mod`)

| Parameter | Value | Unit |
|---|---|---|
| Coking coal `ng_cost_ccoal` | 184 | $/t |
| Non-coking coal `ng_cost_ncoal` | 98 | $/t |
| PCI coal `ng_cost_pcoal` | 110 | $/t |
| Grid power `ng_cost_power` | 0.07 | $/kWh |
| Power sell-back `ng_credit_power` | 0.03 | $/kWh |
| Fine ore / lump ore | 65 / 70 | $/t |
| Lime `ng_cost_lime` | 60 | $/t |
| Biochar `ng_cost_biochar` | 60 | $/t |
| Scrap `ng_cost_scrap` | 350 | $/t |
| Electrode `n7/n8_cost_electrode` | 600 | $/t |
| Slag credit `ng_credit_slag` | 15 | $/t |
| Breeze / tar credit | 55 / 20 | $/t |
| Natural gas `n5_cost_NG` | 10 | $/MMBtu (×50 in cost eq) |
| Hydrogen `ng_cost_h2` | 4500 → 1000–1500 | $/t (declining) |
| H₂ start year `ng_h2_start_year` | 2030 | — |
| CCS cost `n10_ccs_cost` | 125 → 75 | $/tCO₂ |
| Carbon tax `carbon_tax` | 0 | $/tCO₂ (lever) |
| Labour / maintenance / other opex | 20 / 15 / 10 | $/tCS |
| Levelized capex `n*_capex` | coke 40, sinter 30, pellet 10, BF 80, BOF 40, coal-DRI 110, NG-DRI 90, H₂-DRI 120→90, EAF 70, scrap-EAF 70 | $/tCS |
| WHR capex / opex | 0.009 / 0.003 | $/kWh |

### 12.3 Capacity-framework parameters (`definitions.mod`)

| Parameter | Value |
|---|---|
| 2025 seeds `cap0_{bof,cdri,ngdri,h2dri,scrap}` | 90.0 / 63.54 / 11.61 / 0 / 33.5 Mt |
| Asset lives `life_*` | 25 / 20 / 15 / 15 / 10 yr |
| Fixed opex `fopex_*` | 35 $/tCS/yr (= labour 20 + maint 15) |
| Overnight scrap-chain capex `ocapex_scrapchain` | 100 $/(t-scrap/yr) |
| Ramp slab `ramp_frac` | 0.15 |
| Sunk toggle `sunk` | 1 |
| CCS life / capex share / solvent opex | 15 yr / 0.80 / 5 $/tCO₂ |
| CCS stream multipliers `ccs_mult_{bf,cdri,ngdri}` | 1.0 / 1.2 / 0.5 |
| CCS capture energy `ccs_kwh_{bf,cdri,ngdri}` | 800 / 850 / 200 kWh/tCO₂ |
| Capture eff. `n10_ccs_eta`, max rate `fc_max`, ceiling `phi_2050` | 0.85 / 0.9 / 0.50 |

---

## 13. Linearisation strategy

The model was deliberately reduced from a nonconvex MINLP to a (near-pure) LP:

1. **Route shares.** Bilinear `f_route·dri_eaf_steel_out` products are removed; the
   route **outputs** are the decisions and `dri_route_split` (eq56) links them
   linearly. Fractions `f_cdri`, `f_ngdri` are reconstructed post-solve only
   (`yreport.mod`).
2. **Demand pinning.** `total_steel[t] = dem[t]` (constant) makes `f_bof·dem` and
   `f_eaf·dem` linear.
3. **Capture.** The capture *amounts* `ccs_X` are the decisions (not
   fraction×base), so every `(capbase · fc)` bilinear vanishes; per-route and
   sector ceilings are linear.
4. **Shared-EAF attribution.** Products such as `eaf_coal_in·f_cdri` are replaced
   exactly by `n7_cs·coaldri_output/(1−n7_phi_eaf)` (the `steel_eaf` cancels).
5. **Intensity target.** The variable-denominator ratio is cleared by multiplying
   through by `Σ total_steel ≥ 0` (§8.5).

Consequently `nonconvex=2` is not required. The former CCS phase-in binaries
(`dec_switch_*`) and the unused integer `z` have been removed, so the model now
contains **no integer variables** and solves as a pure linear program.

---

## 14. Scenario, uncertainty and regret layer (Python / shell)

The `.mod` core is wrapped by an experiment layer (project root + `scenarios/`,
`run_scripts/`). `template.mod` is a token-substituted clone of `main.mod` used by
all drivers (tokens: `NGVAL, H2ENDVAL, H2YEARVAL, CCSVAL, AVGEMIVAL, RAMPVAL,
SCRAPREGIMEFILE, NGAVAILFILE, GRIDEFFILE`).

**Structural axes (discrete policy/deployment levers):**
- NG availability `scenarios/ng_avail_{normal,shock,optimistic}.mod`
- Scrap regime `scenarios/scrap_{starved,low,modest,optimistic}.mod` (base cap 35 Mt,
  growth 0.04–0.06)
- Grid-EF scenario `scenarios/grid_ef_{bau,moderate_re,aggressive_re}.mod`
- H₂-DRI start year (e.g. 2030/2035/2040/2045)

**Uncertain market prices (continuous):** NG cost, H₂ end-cost, CCS end-cost
(sampled), plus coking-coal and H₂-timing in the stochastic engines.

**Drivers:**
| Tool | Role |
|---|---|
| `run_scripts/{linux,macos,windows}/` | parameter sweeps (scenario × H₂-end × H₂-year × CCS × scrap) |
| `monte_carlo.py` | Latin-Hypercube MC over market prices, one structural cell per run |
| `monte_carlo_2d.py` | dense 100×100 H₂-cost × CCS-cost grid |
| `mc_frontier.py` | feasibility frontier across the 48 structural cells (price-independent) |
| `run_all_cells.py` | production driver: price-grid table per feasible cell → `cells/`, `cells_traj/` |
| `capex_sweep.py` | new-capacity investment sweep per cell → box-plot |
| `regret.py` | static regret matrix: commit for assumed world W, realise world G |
| `regret_roll.py` | rolling 5-year course-correction (MPC, prior builds sunk) |
| `regret_stoch.py` | stochastic-regret prototype (perturbed price worlds + rolling recourse) |
| `plot_*.py` | figures (frontier, pathways, emissions trajectories, regret heatmaps, scrap regimes, split-violins, transition cost, H₂ timing) |

**Regret definition** (the research core, `regret.py`): a planner commits sunk
capacity for an assumed future `W`, then a different future `G` arrives;
```
regret(W,G) = cost[ commit W's sunk builds, then re-optimise dispatch under G ] − PF(G)
```
where `PF(G)` is the perfect-foresight optimum for `G`. The diagonal is ≈0;
infeasible recourse = catastrophic regret. The sunk-capital framework (§7) is what
makes regret nonzero and meaningful.

Outputs are organised under `runs/<RUN>/{plots,csv}` plus `cells/`, `cells_traj/`,
`mc_frontier.csv`.

---

## 15. Reporting (`yreport.mod`)

Post-solve console report: lifetime levelized average steel cost ($/t); 2050 cost &
emissions intensity; CO₂ captured per tonne steel; the 2050 route-share table;
year-by-year route production with shares; CCS amounts and capture fractions per
route/year; year-by-year average emissions (tCO₂/t) and cost ($/t); and per-route
levelized cost and emissions trajectories. The per-route levelized capital charge is
`acapex_X·(cap_X − legacy_X)` — annualised capex on **built** capacity only, so the
free 2025 incumbent (legacy) fleet is not billed, matching the objective (which
charges overnight capex on builds, never on legacy). Because the capital-recovery
factor is the annuity factor, the annualised report and the objective's overnight
charge **reconcile in present value** (exactly for vintages whose life fits within
the horizon; late-horizon builds whose annuity tail extends past 2050 are charged
slightly less in the report than the objective's full sunk overnight amount). Fixed
O&M is on full capacity, variable opex on production; the WHR power credit and any
carbon tax are also applied.

---

## 16. Assumptions, simplifications and caveats

- **Single region, annual resolution, perfect foresight** (deterministic core);
  uncertainty is explored externally via the scenario/MC/regret layer, not stochastic
  programming inside the optimisation.
- **Demand is exogenous and price-inelastic** — the model is a cost-minimising supply
  planner, not a market-equilibrium model.
- **The CO₂ target is an upper-bound cap, not a pin** — the optimizer may overachieve;
  it is a carbon budget, not an iso-emission constraint (§8.5).
- **Green hydrogen is assumed** — H₂ for H₂-DRI is a purchased commodity delivered at
  the gate (priced via `ng_cost_h2`). It carries **no point-of-use Scope-1 emissions,
  no electrolyser electricity load in the grid balance, and no upstream/Scope-3
  emissions**. This is valid only under a zero-carbon (green) H₂ supply assumption;
  the result is that H₂-DRI's full decarbonisation benefit is realised at its
  commodity price, with no embedded power demand.
- **Overnight, fully sunk capex; no salvage** — central thesis; isolate via `sunk=0`.
- **Linear** — route shares and capture fractions are recovered post-solve; the model
  has no integer variables (§13).
- **DRI capacities live on the 0.9×crude-steel-equivalent basis** — mind the
  `1/(1−n7_phi_eaf)` factors when reading capacity, fixed-opex, or emission terms.
- **Incumbent (legacy) capacity phases out linearly to zero by 2050, independent of
  asset age** — the real 2025 fleet's age distribution is unknown, so a uniform
  ≈4 %/yr decline ceiling is used as a tractable proxy (the optimizer may retire
  faster). A consequence is that still-young incumbent capacity can be retired and
  rebuilt; this is an accepted simplification given the missing vintage data.
- **CCS limited to BF-BOF / Coal-DRI / NG-DRI**, gated by a sector-wide deployment
  ramp (0→0.5 by 2050) that is usually the binding capture limit.
- **Some coefficients are placeholders / tunable levers** (e.g. `ocapex_scrapchain`,
  `ccs_vopex_solvent`, the CCS stream multipliers, `ramp_frac`) and are intended to
  be swept; carbon tax is off by default.

---

## 17. File / module map

```
main.mod                 # driver: sets, include order, objective, solve, report
template.mod             # token-substituted clone of main.mod for sweeps
definitions.mod          # declarations: demand, ALL technical + cost params (with bounds),
                         #   capacity-expansion (capex/opex) framework, grid EF
variables.mod            # all decision variables (flows, capacity, cost, emissions)
parameters.mod           # runtime `let` overrides + scenario setup: base demand, avg_emi cap,
                         #   H2 caps/constraints, NG-availability profiles, scrap limits
yreport.mod              # post-solve console report
ng.mod                   # NG-availability cap profiles (normal/BAU/shock)

modules/
  a_coke (eq1-8)         b_sinter (eq9-15)      c_pellets_bf (eq16-17)
  d_blast_furnace (18-32) e_bof (33-39)
  f/g/h_pellets_* (40-45)
  i_dri_coal (47-50)     j_dri_ng (52-55)       k_dri_h2 (56-60, route split)
  l_eaf_dri (61-69)      m_scrap_eaf (70-76)    n_steel_balance (77)
  o_waste_heat (78-82)   p_power_balance (83)
  q_carbon_capture (84-88)
  v_capacity             # capacity stock, builds, legacy retirement, CCS capacity
  r_cost (89-104)        s_emissions (105-112)
  t_additional_constraints  # init shares, demand, avg-emissions CAP, ramps

scenarios/   run_scripts/   *.py (monte_carlo, regret*, capex_sweep, plot_*, run_all_cells)
```
