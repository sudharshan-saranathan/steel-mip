# Parameter Audit — Stage 1 Register

**Audit target:** `nakulneupane/steel-sector-decarbonization` @ `b33b88a` (2026-09-15). This repo matches the paper's design: 8,640 factorial cells, H₂ ramp 0.5/1/1.5 Mt/yr, build cap 20/30 Mt/yr, 50 cost draws, and regret reviews in 2030–2045.

**Reference documents:** the paper draft (*De-Risking Low-Cost Pathways to Green Steel in India*) and its Supplementary Table 1.

**Context:** India only. A global value counts as evidence only where no Indian figure exists.

Line numbers refer to `core/definitions.mod` in the audit target unless another file is named. `steel-mip/core` is identical to the target except for the three items in §0.

---

## 0. Scope and provenance

| Item | Finding |
|---|---|
| `steel-mip/core` vs target `core` | Identical except for: (a) the θ_grid / θ_tech / θ_ccs trend end-points (lines 146–170); (b) the electrode price, $600 vs $3,000/t (206, 208); (c) H₂-DRI plants added to the shared build budget, with no H₂-DRI builds before debut (`v_capacity.mod`). |
| `steel-mip/MonteCarlo`, `steel-mip/RegretAnalysis` | **Obsolete.** These are older copies (CRLF line endings, build cap 10 Mt, no ratchet or `legacy_phaseout`). `RegretAnalysis/main.mod` includes `core/modules/v_capacity.mod`, which uses parameters `RegretAnalysis` never declares. `MonteCarlo/template.mod` includes `modules/*.mod` files that don't exist. The paper's results come from the target repo's `monte_carlo/` and `adaptive_panning/`, so these two folders are excluded from the audit. |
| Central values differ between studies | Coking coal is **$184/t** in `core` (used in Figs 3, 4, 5) but **$250/t** in the regret backdrop. Natural gas is **$10/MMBtu** in `core` but **$15** in the regret backdrop and the Monte Carlo midpoint. The paper's Fig. 6(b) "baseline" is therefore undefined. |
| 2025 calibration check | A hand calculation of 2025, which the model fixes almost entirely through its starting constraints, gives **2.80 tCO₂/tCS**. The paper cites **2.54** (Ministry of Steel, 2024). Script: `stage1_calib2025.py`. |

---

## 1. Classification tags

| Tag | Meaning | Unsubstantiated? |
|---|---|---|
| **S** | Sourced, and the source is India-relevant | no |
| **U-NS** | No source given (Supplementary Table 1 shows "–", and the code comment cites nothing) | **yes** |
| **U-GL** | Only a global or non-Indian source, where Indian data likely exists | **yes** |
| **U-RG** | Value appears to lie outside the Indian range. *Preliminary: this tag is a hypothesis for Stage 2, not a finding.* | **yes** |
| **A** | Modelling or scenario assumption: needs stated reasoning, not a citation | no, if the reasoning is stated |
| **X** | Inconsistent between the code, the supplementary table, the paper, or different studies | fix |

---

## 2. Structural issues

These are errors in equations, units or accounting, not in parameter values. They will be fixed in Stage 3 regardless of what Stage 2 finds.

| ID | Where | Issue | Effect |
|---|---|---|---|
| ST-01 | `definitions.mod:284–295` | **Capex is annualised twice.** The `n*_capex` values (Supp. unit "$/tCS") are summed as *annualised* charges (`acapex_*`, "$/tCS/yr") and then divided by the capital recovery factor¹ to get *overnight* cost. Implied overnight capex: BF-BOF **$2,557/t**, coal-DRI-EAF **$2,179/t**, NG-DRI-EAF **$1,950/t**, H₂-DRI-EAF **$2,557/t** (2025), scrap-EAF **$680/t**. If the supplementary values are overnight, the costs are inflated ~12×; if they are annualised, ~1×. The intended unit has to be settled first. | Investment cost, route choice, stranded capital (Fig. 8). |
| ST-02 | `c_/f_/g_/h_pellets_*.mod` | **Fine ore = pellets ÷ `ng_ore_pell`.** With 1.1 t ore per t pellet this should be pellets × 1.1; ore use is understated ~17 %. | Ore cost. |
| ST-03 | pellet modules; `s_emissions.mod` | **Pellet induration fuel and its CO₂ are missing**, while pellet electricity is 200 kWh/t. In the 2025 hand calculation, pellets take 20 % of all sector electricity. | Emissions (Scope 1 too low, Scope 2 too high). |
| ST-04 | `b_sinter.mod`, `s_emissions.mod`, `r_cost.mod` | **Bought-in coke breeze carbon is not counted.** Sinter uses 0.09 t breeze/t sinter (≈ 0.10 t/tHM); the coke ovens make only ≈ 0.03 t/tHM. The difference is bought at $85/t but carries no CO₂. Own breeze is meanwhile sold at $55/t. | ~0.2 tCO₂/tHM uncounted. |
| ST-05 | `o_waste_heat.mod:13, 29` | **Power from process gases is almost nil.** Leftover COG + BFG + BOFG is multiplied by a hard-coded 0.3, then by `n9_whr` (0.05 → 0.30), then by `n9_eta` = 0.15. In 2025 that converts ~0.2 % of the gas energy to power. Indian integrated plants burn most of this gas in captive power plants. `sg_out` (sinter gas) is computed but never used. | Scope 2 and power cost too high for BF-BOF; the benefit of CCS steam integration is distorted. |
| ST-06 | `definitions.mod:167` | **Grid emission factor boundary.** 0.886 tCO₂/MWh is a blend of 36 % grid and 64 % captive coal plant (CPP). The CPP share is not modelled, and in-plant gas power (ST-05) is not netted out, so the boundary needs restating. | Scope 2. |
| ST-07 | `t_additional_constraints.mod:2–6` | **2025 starting shares.** `f_bof = 0.51` is the BF share of *iron input* (Fig. 1a). The BOF share of *production* is 41 % (Fig. 1b). `init_f_cdri = 0.902` disagrees with Fig. 1a, which implies 25/(25+5) = 0.83. Scrap-EAF output is fixed at 0 in 2025 while 0.75 Mt of capacity is seeded. | The starting point drives the 2.80 vs 2.54 calibration gap. |
| ST-08 | `v_capacity.mod` | `h2_ramp_mode = 0` also removes the build budget, both utilisation limits and the util_max derate. Several unrelated limits hang off one switch. | Only matters if mode 0 is ever used. |
| ST-09 | `v_capacity.mod` (cap_envelope) | The capacity total adds crude-steel capacity (BOF, scrap) to DRI capacity, which is about 1.1 t DRI per t steel. | Minor. Already documented in the code. |
| ST-10 | `q_carbon_capture.mod:31–35` | **CCS is derated twice:** `n10_ccs_eta × fc_max` = 0.85 × 0.90 = 0.765. The capturable base is *all* route CO₂ (all coking coal, PCI and limestone), not the gas stream that can actually be captured. | CCS potential, and the 50 % deployment ceiling. |
| ST-11 | `definitions.mod:270–274` | Fixed operating cost ($20 labour + $15 maintenance per t capacity) is identical for every route. | Route economics. |
| ST-12 | `definitions.mod:362–372` | **H₂ "firming" capex is a plug.** An unexplained capex term closes the gap between the bottom-up cost of H₂ (~$3.66/kg) and a $5/kg target, then falls with electrolyser capex. The electrolyser runs at the renewables capacity factor (`re_cf` 0.35). | Cost of H₂. |
| ST-13 | `s_emissions.mod` | **Emission factors.** Coking coal uses 0.1116 tCO₂/GJ (IPCC default 0.0946; India's national inventory ~0.094). Electrodes use 6 tCO₂/t (burning pure carbon gives 3.67). Non-coking coal uses 2.64 tCO₂/t, which implies 24 GJ/t; Indian thermal coal is ~15–20 GJ/t, so DRI coal use and the emission factor per tonne of coal are inconsistent. | Emissions. |
| ST-14 | `v_capacity.mod` comment vs code | The comment says electrolyser build-up is not tied to the H₂ debut year, but `h2elec_predebut` forces electrolyser capacity to 0 before debut. | Documentation; the intent needs confirming. |
| ST-15 | `core/parameters.mod:35–60` | The default `n5_ng_cap` is the **shock** trajectory. All the studies override it, but a bare `core` run uses the shock case. | Default runs. |
| ST-16 | `v_capacity.mod` (capex_cost_def) | **No end-of-horizon credit.** A build in year t pays its full up-front capex but serves only 2050 − t + 1 years inside the horizon; the life remaining after 2050 earns nothing. This discourages builds in the 2040s. | Late-horizon route mix, LCOP. |

¹ Capital recovery factor (CRF): converts a one-off investment into an equal yearly payment over the asset's life at the discount rate.

---

### Decisions agreed with the user

| ID | Decision (2026-10-06) |
|---|---|
| ST-01 | Capex is **up-front**: `n*_capex` = instant cost of 1 t/yr of crude-steel capacity, multiplied directly by `build_*[t]`. Remove the division by the CRF (`definitions.mod:284–295`). The current values were set as yearly charges, so they are replaced with Stage 2 up-front values in the **same** commit. If the `sunk = 0` branch is kept, derive `acapex = ocapex × CRF`. Plant lifetimes stay in use: builds retire after `life_*` and must be rebuilt (`cap_def_*`). |
| ST-01a | New capacity is costed as **greenfield** for all routes and all years (decision 2026-10-06). The paper states this as a conservative upper bound on investment cost; brownfield values are kept as a sensitivity case. |
| ST-16 | Add a salvage credit for the life remaining after 2050 (straight-line), discounted to 2050. |

## 3. Parameter register

### 3.1 Demand, finance and the 2025 fleet

| Parameter | Line | Value | Tags | Note / Stage-2 action |
|---|---|---|---|---|
| base_demand | 3 | 152.2 Mt | S | FY2024-25 crude steel output (Ministry of Steel / Joint Plant Committee). |
| growth_rate | 4 | 5 %/yr → 515 Mt in 2050 | U-NS, X | Supp. table "–"; the paper cites [31,32] only in the text. Compare with National Steel Policy 2017 (255 Mt by 2030-31), NITI Aayog 2026, CEEW, IEA and TERI 2050 projections. |
| real_discount_rate | 6 | 0.06 | S (partial) | Murty et al. (IEG / NITI) social discount rate. Its use as a *private* investment rate needs a stated reason. |
| cap0_bof / cdri / ngdri / scrap | 222–226 | 90 / 104.1 / 12.9 / 0.75 Mt | U-NS (scrap: S) | Total 207.75 Mt. Check against Ministry of Steel / JPC route-wise capacity. |
| init f_bof / f_eaf | t_add:2–3 | 0.51 / 0.49 | X | See ST-07. |
| init_f_cdri | t_add:6 | 0.902 | U-NS, X | See ST-07. |
| life_bof / cdri / ngdri / h2dri / scrap | 250–254 | 25 / 20 / 20 / 25 / 15 yr | U-NS, U-RG | BF campaigns with relines and EAFs typically run 30–40+ years. 15 years for scrap-EAF is short. |
| util_min_* | 262–266 | 0.85 / 0.75 / 0.70 / 0.70 / 0.60 | U-NS | Compare with Ministry of Steel route-wise utilisation data. |
| util_max | 267 | 0.95 | U-NS | |
| labor / maintenance / other opex | 216–218 | $20 / $15 / $10 per tCS | U-NS | Compare with Indian company annual reports (SAIL, JSW, Tata) and CEEW. |
| cap_buffer | 248 | 0.40 | A | The code shows it is inert. |
| legacy_phaseout | 232 | 0/1 | A | Brackets the case where fleet vintage is unknown. Acceptable. |
| cap_add_common | 259 | 20 / 30 Mt/yr | A, X | Derived assumption (agreed). Averages: 13.4 Mt/yr needed if the 2025 fleet survives, 21.7 if it is phased out; ~25.8 Mt/yr needed in 2049–50. The core comment "per-TECH" is wrong; the budget now covers all five routes. |
| carbon_tax | 215 | 0 | A | |

### 3.2 Coke oven, sinter, BF, BOF

| Parameter | Line | Value | Tags | Note |
|---|---|---|---|---|
| n0_e_c | 24 | 75 kWh/t coke | U-NS | |
| n0_cf | 25 | 1.47 t coal/t coke | U-NS | Indian coal blends have high ash; check against the Ministry of Steel / BEE PAT² benchmarks. |
| n0_br_c, n0_tar_c | 26–27 | 0.056, 0.04 t/t | U-NS | |
| n0_cdq_whr | 28 | 80 kWh/t coke | U-NS, U-RG | Assumes coke dry quenching (CDQ) at every coke oven in 2025. Indian CDQ coverage is partial. |
| n0_cog_c, n0_rec_cog, n0_rec_bfg | 29–31 | 440, 190, 270 Nm³/t | U-NS | Underfiring ≈ 4.3 GJ/t coke: check. |
| n1_e_sint, n1_lime_sint, n1_ore_sint | 35–37 | 50 kWh, 0.04, 0.9 t | U-NS | |
| n1_brz_sint 25→50 | 38, 40 | 0.09 → 0.058 t/t | U-NS | See ST-04. |
| n1_bio_sint 25→50 | 39, 41 | 0 → 0.022 t/t | U-NS | Biochar substitution trend. |
| n1_sintcool_whr | 42 | 30 kWh/t | U-NS | |
| n1_sintgas_sint, ng_sintgas_cv | 43, 15 | 1,800 Nm³, 0.6 MJ/Nm³ | U-NS | Unused (ST-05). |
| n2_* BF burden (sinter 1.15, pellets 0.35, lump 0.15, limestone 0.025, slag 0.3) | 48–53 | | U-NS | Slag 0.3 t/tHM is low for Indian high-alumina ore, which typically gives 0.35–0.45: U-RG. |
| n2_bfg_hm, n2_rec_bfg, n2_rec_cog | 54–56 | 1,500 / 500 / 30 Nm³ | U-NS | |
| n2_trt_whr | 57 | 35 kWh/tHM | U-NS | Assumes top-pressure recovery turbines at 100 % coverage. |
| n2_coalpci 25→50 | 58, 60 | 0.15 → 0.16 t/tHM | U-NS | |
| n2_biopci 25→50 | 59, 61 | 0 → 0.053 t/tHM | U-NS | Trend: the paper cites [6,7] for the concept only. |
| n2_coke 25→50 | 62–63 | 0.53 → 0.48 t/tHM | U-NS | Indian coke rates are ~0.45–0.55 t/tHM (to verify). |
| n3_e_bof | 70 | 174 kWh/tCS | S (Ministry of Steel [2]) | Confirm whether this includes casting and rolling, and check the boundary against EAF and IF. |
| n3_metallic_bof, ls, slag, bofg, rec_cog | 71–75 | 1.1, 0.075, 0.1, 100, 65 | U-NS | BOF slag 0.1 t/t is low (typically 0.12–0.16): U-RG. |
| phi0_bof / phi_max_bof / phi_min_bof | 125, 132, 128 | 0.09 / 0.20 / 0.05 | U-NS | |
| blend_ramp | 136 | 0.05 | A | |

² BEE PAT: the Bureau of Energy Efficiency's Perform-Achieve-Trade scheme, which publishes plant energy benchmarks.

### 3.3 DRI routes, EAF/IF, scrap

| Parameter | Line | Value | Tags | Note |
|---|---|---|---|---|
| n4_e_dri | 81 | 217 kWh/t DRI | U-NS | Includes the extra induction-furnace power (derived in the comment). |
| n4_pel_dri, n4_ore_dri | 82–83 | 1.5, 0.1 t/t | U-NS, U-RG | Indian coal-DRI kilns mostly use **lump ore** (~1.5–1.6 t/t), not pellets. |
| n4_c_dri | 84 | 1.0 t coal/t DRI | U-NS, U-RG | See ST-13. |
| n5_e_dri | 87 | 120 kWh/t DRI | S ([2]) | |
| n5_ng_dri | 90 | 0.35 t NG/t DRI ≈ 17.5 MMBtu | U-NS, U-RG | Midrex/HYL plants use ~10–12 GJ/t; this value is ~70 % high (to verify). |
| n5_pel_dri, n5_ore_dri | 88–89 | 1.5, 0.1 | U-NS | |
| n6_e_dri, n6_pel_dri, n6_ore_dri | 94–96 | 110, 1.5, 0.1 | U-NS | |
| n6_h2_dri | 97 | 0.07 t H₂/t DRI | U-GL | Global literature (54 kg/t stoichiometric; 65–75 kg/t in practice). Acceptable as U-GL. |
| n7_e_eaf | 101 | 664 kWh/tCS | S ([2]) | |
| n7_dri_ratio, eltrd, ls, cs, ss | 103–107 | 1.1, 0.003, 0.06, 0.01, 0.15 | U-NS | |
| n7_eafg / n8_eafg | 108, 118 | 3 GJ/tCS off-gas | U-NS, U-RG | High for EAF; zero for IF. Most Indian secondary steel is IF. |
| n8_e_eaf | 111 | 785 kWh/tCS | U-NS, U-RG | 75 % IF at 825 + 25 % EAF at 664. Both components need sources. |
| n8_* (phi, eltrd, ls, cs, ss) | 113–117 | 1.1, 0.003, 0.06, 0.01, 0.15 | U-NS | Lime and slag in IF practice are lower. |
| phi0_cdri, phi0_ngdri | 126–127 | 0.382, 0.13 | U-NS | Combined with the 2025 shares these give 37.0 Mt of scrap = `n8_scrap_seed` (internally consistent). |
| phi_max_* (DRI) | 133–135 | 0.40 | U-NS | |
| n8_scrap_seed | 138 | 37 Mt | U-NS | Ministry of Steel, Steel Scrap Recycling Policy, MRAI. |
| n8_scrap_rate | 137 | 2–10 %/yr | S (partial) | The paper cites NITI [32] (125–187 Mt by 2050). The implied growth rate needs checking. |

### 3.4 Electricity, grid and waste heat

| Parameter | Line | Value | Tags | Note |
|---|---|---|---|---|
| ng_e_pell | 10 | 200 kWh/t pellet | U-NS, U-RG | Pellet plants typically use 25–40 kWh/t, plus 0.3–0.6 GJ/t fuel (ST-03). |
| ng_ore_pell | 11 | 1.1 | U-NS | See ST-02. |
| ng_cog_cv / bfg_cv / bofg_cv | 12–14 | 18 / 3.3 / 8 MJ/Nm³ | U-GL | Source [3] is a Chinese study. Indian plant data exists (BEE PAT). |
| grid_price_start | 148 | $0.07/kWh | S (partial) | Åhman & Arens 2024. Indian HT industrial tariffs are ~₹7–9/kWh, so check this value. |
| grid_price_end_fast | 149 | $0.055 | U-NS | 2050 tariff at θ_grid = 1. |
| n9_grid_ef_start | 167 | 0.886 tCO₂/MWh | U-NS | CEA CO₂ Baseline Database; source for the CPP share (ST-06). |
| n9_grid_ef_end | 168 | 0.886 × (1 − θ) | A | θ_grid 0.25 / 0.5 / 0.75: the paper cites [32,37] for ~50 %. |
| ng_credit_power | 182 | $0.03/kWh | U-NS | **Unused**: declared but referenced nowhere in `core`. |
| n9_eta | 164 | 0.15 | U-NS, U-RG | See ST-05. |
| n9_whr | 165 | 0.05 → 0.30 | U-NS | |
| hard-coded 0.3 pool factor | o_waste_heat:13 | 0.3 | U-NS | See ST-05. |
| whr_steam_eff | 331 | 0.85 | U-NS | |
| n9_whr_capex / opex | 209–210 | $0.009 / $0.003 per kWh | U-NS | |

### 3.5 Prices and credits (2025, constant real)

| Parameter | Line | Value | Tags | Note |
|---|---|---|---|---|
| ng_cost_ccoal | 178 | $184/t (MC 100/250/400) | S (partial), X | National Coal Index [1]. Central value differs between studies (§0). |
| n5_cost_NG | 201 | $10 (MC 5/15/25) | U-NS, X | Use PPAC landed LNG and APM³ gas prices. |
| ng_cost_scrap | 190 | $350 (MC 250/350/450) | U-NS | Indian heavy-melting-scrap and shredded-scrap prices. |
| ng_cost_fineore / lumpore | 183, 187 | $65 / $70 | U-NS | IBM⁴ and NMDC notified prices. |
| ng_cost_pcoal | 188 | $110 | U-NS, U-RG | PCI coal is imported; check. |
| ng_cost_ncoal | 191 | $98 | U-NS | Coal India notified prices and imported DRI-grade coal. |
| ng_cost_lime | 184 | $60 | U-NS, U-RG | |
| ng_cost_biochar | 185 | $60 | U-NS | |
| n7/n8_cost_electrode | 206, 208 | $3,000 | U-NS | Corrected from $600. Check against Indian UHP electrode prices (Graphite India, HEG). |
| n0_credit_breeze, n1_cost_breeze | 192, 195 | $55 / $85 | U-NS | See ST-04. |
| n0_credit_tar | 193 | $20 | U-NS, U-RG | Coal tar sells for several hundred $/t. |
| ng_credit_slag | 189 | $15 | U-NS | |

³ APM: Administered Price Mechanism, the government-set price for domestic gas from older fields.
⁴ IBM: Indian Bureau of Mines, which publishes monthly ore prices.

### 3.6 Capital costs (see ST-01)

| Parameter | Line | Value | Tags |
|---|---|---|---|
| n0 / n1 / n2 / n3 capex | 194–198 | 40 / 30 / 80 / 40 $/tCS | U-NS |
| n4_capex_coal / n5_capex_ng | 199–200 | 110 / 90 | U-NS |
| n6_capex_h2 (25→50) | 202 | 120 → 90 | U-NS |
| n7 / n8 capex | 205, 207 | 70 / 70 | U-NS |
| ng_capex_pell | 186 | 10 | U-NS |
| ocapex_scrapchain | 296 | $100 per t scrap/yr | U-NS |
| ocapex_coalchain / ngchain | 297–298 | 0 | A (stated: included in fuel price) |

### 3.7 Green hydrogen

| Parameter | Line | Value | Tags | Note |
|---|---|---|---|---|
| h2elec_capex_start | 348 | $850/kW | U-NS | Indian electrolyser tenders (SIGHT⁵), IEA, CEEW. |
| h2elec_capex_end_fast | 156 | $100.31/kW | A, U-RG | Back-solved from a $1.50/kg end-point (scaled ×0.6688 from the US DOE target). The $1.50/kg end-point itself needs a source. |
| re_capex (2025) | 356 (hard-coded 800) | $800/kW | U-NS | Hard-coded, not a parameter. India solar–wind hybrid costs. |
| re_capex_end_fast | 158 | $133.75/kW | A, U-RG | Same back-solve. |
| re_cf | 345 | 0.35 | U-NS | SECI round-the-clock (RTC) / hybrid capacity factors. |
| h2_kwh_per_t | 344 | 55,000 kWh/t | U-GL | |
| h2_opex | 346 | $300/t | U-NS | |
| fopex_h2elec, fopex_h2re | 355, 361 | $400 per (t/yr), $15/kW | U-NS | Marked "placeholder" in the code. |
| life_h2elec / life_re | 353, 359 | 15 / 25 | U-NS | |
| lcoh_2025_target | 362 | $5,000/t | U-NS | Indian tenders: SECI and refinery results ~₹397/kg (to verify). See ST-12. |
| h2_ref_cap (2/4/6 Mt) × h2_peak_rate 0.25 | 378–379 | 0.5 / 1 / 1.5 Mt/yr | A | Paper: built around 0.71 Mt/yr implied by the National Green Hydrogen Mission (NGHM). Acceptable, with that reasoning stated. |
| h2_base_start / end, gauss_sigma, peak_lag | 380–386 | 0 / 0.05, 2 yr, 5 yr | A | Shape of the deployment curve. Needs stated reasoning; the paper gives none. |
| ng_h2_start_year | 98 | 2030–2045 | A | Scenario axis. |

⁵ SIGHT: Strategic Interventions for Green Hydrogen Transition, the NGHM incentive programme for electrolyser manufacturing and hydrogen production.

### 3.8 CCS

| Parameter | Line | Value | Tags | Note |
|---|---|---|---|---|
| n10_ccs_cost_start | 213 / parameters.mod | $125/tCO₂ all-in | U-NS | NITI Aayog CCUS 2022, CEEW, IEA. |
| ccs_capex_fall slow / fast | 160–161 | 0.3165 / 0.8435 | A | Back-solved to $100 / $60 per tCO₂ in 2050. Those end-points need a source. |
| ccs_ts_cost | 309 | $20/tCO₂ | U-NS, U-RG | India has no characterised storage site; transport distances matter. |
| ccs_vopex_solvent | 308 | $5 | U-NS | "placeholder" |
| ccs_fom_pct | 307 | 4 %/yr | U-NS | |
| life_ccs | 305 | 15 yr | U-NS | |
| ccs_kwh_* / ccs_steam_* / ccs_mult_* / ngdri_proc_share | 310–322 | | U-NS | All need sources. The stream-dependence logic is sound. |
| ccs_ref_elec / ref_steam | 326–327 | $0.07/kWh, $5/GJ | A | Used only to back out capex. |
| ccs_boiler_eff | 328 | 0.85 | S (U-GL) | |
| n10_ccs_eta, fc_max | 174; q_cc:11 | 0.85, 0.90 | U-NS | See ST-10. |
| ccs_avail (0 until 2027 → 50 % by 2050) | q_cc:40–42 | | U-NS, U-RG | No CCS before 2027 is optimistic for India. Use the NITI 2022 CCUS roadmap. |

### 3.9 Emission factors

| Factor | Value | Tags | Note |
|---|---|---|---|
| Coking coal | 2.79 tCO₂/t (0.1116 × 25) | U-NS, U-RG | See ST-13. Use India's national inventory (NATCOM / BUR) values. |
| PCI coal | 2.756 | U-NS | |
| Non-coking coal | 2.64 (0.110 × 24) | U-NS, U-RG | See ST-13. |
| Natural gas | 2.75 t/t (0.055 × 50) | U-GL | Correct in order of magnitude. |
| Limestone | 0.44 | S (IPCC) | Calcination factor; same worldwide. |
| Electrodes | 6 tCO₂/t | U-NS, U-RG | See ST-13. |
| ng_co2_gj | 0.0521 t/GJ | U-GL | |

### 3.10 Resource availability and policy axes

| Parameter | Value | Tags | Note |
|---|---|---|---|
| ccoal_cap, abundant / scarce | 60.5 Mt (2025) → 293.6 / 91.1 Mt | S (partial), X | Built from Ministry of Coal data. The comment uses **54.5 Mt** of 2025 imports; the paper cites **66.33 Mt** (FY2025-26). The domestic "~6 Mt model basis" needs a source. |
| n5_ng_cap, BAU / policy | 5.35 → 10.7 / 32.2 Mt | S (partial), U-NS | PNGRB [46]. The 10 % steel share of national gas is unsourced: PPAC sectoral data shows a smaller share (to verify). The comments give the unit as "Mm3" but the values are in tonnes. |
| avg_emi | 1.6 / 1.8 / 2.0 | A | Can be linked to India's Green Steel Taxonomy (Ministry of Steel, Dec 2024) star thresholds (to verify). |
| emission_monotonic | on | A | |

### 3.11 Study-only parameters

| Parameter | File | Value | Tags | Note |
|---|---|---|---|---|
| MC levels: coal 100/250/400, NG 5/15/25, scrap 250/350/450, θ_tech and θ_ccs 0–1 | `run_montecarlo.py:61` | | S (partial) | The paper cites [2,38–40]. These are 3-point grids, not distributions; state that. |
| IMPORT_P | `run_regret.py:239` | $20,000/t steel | A | Penalty for infeasibility. Fine as a numerical device. |
| IMPORT_REPORT | `run_regret.py:285` | $650/t | U-NS | Feeds the *reported* regret. Needs a source (Indian landed price of imported steel). |
| PEN | `run_regret.py:247` | $5,000/tCO₂ | A | Penalty for exceeding the emissions cap. Check that it is non-binding in the reported results. |

---

## 4. Summary counts

- **Structural issues:** 16 (ST-01 to ST-16). ST-01, ST-03, ST-04, ST-05, ST-07, ST-10 and ST-13 directly affect the headline results.
- **Unsubstantiated parameters** (U-NS, U-GL or U-RG): about 120 of the roughly 150 independent inputs. Only base_demand, real_discount_rate, n3_e_bof, n5_e_dri, n7_e_eaf, cap0_scrap, the limestone factor, the coking-coal price and grid tariff anchors, and the availability trajectories carry any citation.
- **Inconsistencies (X):** 8.

## 5. Stage 2 protocol (agreed)

1. Collect at least 3 independent India-specific estimates per parameter where they exist: peer-reviewed papers, think tanks (CEEW, TERI, IEEFA, WRI India, CSTEP), Government of India sources (Ministry of Steel, JPC, CEA, PPAC, BEE, NITI Aayog, Ministry of Coal, IBM), and company disclosures.
2. Record every estimate found, including those that support the current value.
3. Pick the central value as the median of the India-specific estimates, with the range kept for sensitivity runs. Use global values only as a labelled fallback.
4. Record the year, system boundary, unit conversion and exchange rate (₹/$ by year, stated).
5. Order of work: parameters that touch the ST issues and the calibration gap first, then the cost drivers named in Fig. 6(b), then the rest.
