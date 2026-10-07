# Parameter source inventory

This inventory lists every independent input of the model on branch `fix-wave-01` (the audited and corrected version of `nakulneupane/steel-sector-decarbonization`) and states where its current value comes from. Values are the ones the `fix-wave-01` code holds today. Citations are copied from the Stage 1 register (`STAGE1_REGISTER.md`), the Stage 2 sheets (`stage2/*.md`) and `REVIEW.md`; no source has been added here. Page numbers are given as the sheets give them: the Ministry of Steel (MoS) 2024 *Roadmap* is cited by printed page in some sheets and by PDF page in others (PDF = printed + 14), and "PDF p." marks the latter. Pure intermediate expressions (`:=` definitions such as `crf_*`, `ocapex_*`, `fopex_*` defaults, `ng_cost_power`, `n9_grid_ef`, `h2_bell`, `ccs_avail`) are not inputs and are not listed; their inputs are. Inactive or dead parameters are listed at the end and not counted. A "?" in a note marks a status that is unclear, with the reason.

**File abbreviations.** `def` = `core/definitions.mod`; `par` = `core/parameters.mod`; `t_add` = `core/modules/t_additional_constraints.mod`; `q_cc` = `core/modules/q_carbon_capture.mod`; `o_wh` = `core/modules/o_waste_heat.mod`; `v_cap` = `core/modules/v_capacity.mod`; `axes.py` = `structural/feasibility_and_synergy/feasibility_drivers/axes.py`; `run_mc` = `monte_carlo/run_montecarlo.py`; `run_regret` = `adaptive_panning/run_regret.py`.

**Common short cites.** MoS 2024 = Ministry of Steel, *Greening the Steel Sector in India: Roadmap and Action Plan*; MoS AR 2025-26 = Ministry of Steel *Annual Report 2025-26* (JPC data); TA–TERI 2026 = Transition Asia & TERI, *Is Green Steel Within Reach in India?*, workbook `Model_input_India.xlsx` (sheet named); IECC 2026 = Domínguez Bennett et al., *Economic Case for Green Steel Production in India*, UC Berkeley IECC; CEEW 2021 = Yadav, Guhan & Biswas, *Greening Steel*; CEEW 2024 = Nitturu et al., *Decarbonising Coal-based DRI*; TERI 2021 = Ghosh et al., DRI compendium; Tikadar 2025 = Tikadar et al., *J. Environ. Manage.* 373:123483; IBM IMYB 2019 = Indian Minerals Yearbook 2019, Iron, Steel & Scrap and Slag; IBM MSMP = IBM *Monthly Statistics of Mineral Production* Table 6(a); DGCIS = Ministry of Commerce Export-Import Data Bank; NITI 2022 = NITI Aayog CCUS report; NITI 2026 = NITI Aayog *Scenarios Towards Viksit Bharat and Net Zero: Industry*; JISF 2022 = JISF *Technologies Customized List for Indian Steel Industry, BF-BOF v5.0*; LBNL 2013 = Morrow et al., LBNL-6338E.

## Category legend

| Category | Meaning |
|---|---|
| **SOURCED-IN** | Value taken from India-relevant published source(s): the median of ≥ 3 estimates, or the pessimistic bound of fewer. |
| **SOURCED-GL** | Only a global or non-Indian source supports the value. |
| **DERIVED** | Computed from other parameters, stoichiometry, a unit conversion or a 2025 calibration (the note says from what). |
| **ASSUMPTION** | Scenario, policy or modelling choice with stated reasoning (axis levels, targets, discount framing, solver penalties, switches, shape parameters with a stated rationale). |
| **DANGLING** | No admissible source and no derivation; the value is kept as a placeholder. |

## Summary counts

| Group | SOURCED-IN | SOURCED-GL | DERIVED | ASSUMPTION | DANGLING | Total |
|---|---|---|---|---|---|---|
| Demand/finance/fleet | 14 | 0 | 4 | 8 | 1 | 27 |
| Coke oven-sinter-BF-BOF | 28 | 0 | 2 | 1 | 17 | 48 |
| DRI-EAF-scrap | 25 | 1 | 2 | 8 | 0 | 36 |
| Power-grid-WHR | 5 | 0 | 1 | 2 | 1 | 9 |
| Prices | 11 | 1 | 2 | 0 | 3 | 17 |
| Capex | 3 | 0 | 7 | 2 | 1 | 13 |
| Lifetimes | 8 | 0 | 1 | 1 | 0 | 10 |
| H2 | 10 | 0 | 0 | 7 | 4 | 21 |
| CCS | 19 | 1 | 0 | 3 | 5 | 28 |
| Emission factors | 2 | 3 | 3 | 0 | 0 | 8 |
| Resource/policy axes | 0 | 0 | 0 | 13 | 0 | 13 |
| Study-only | 1 | 0 | 0 | 5 | 3 | 9 |
| **Total** | **126** | **6** | **22** | **50** | **35** | **239** |

The register's "~150" grouped several inputs per row (for example the BF burden, the five lifetimes or the `ccs_kwh_*` set). Here each input has its own row, and the audit's additions are included (`dem_profile`, `dem_sat`, `dem_g0`, `ng_pell_fuel`, `ng_mmbtu_per_t`, `maint_pct`, `ef_*`, `fc_max`, `ccs_share_*`, `ccs_start`, `phi_2050`, `legacy_life`, `re_capex_start`, `h2_firm_on`, `salv_frac`). Sixteen of the 35 DANGLING inputs are BF-BOF process flows; `n1_sintcool_whr`, unsourced in the BF-BOF sheet, is sourced in the power sheet (JISF 2022) and is counted as SOURCED-IN.

## 1. Demand, finance and the 2025 fleet

| Parameter | file:line | Current value | Category | Source(s) or derivation | Note |
|---|---|---|---|---|---|
| base_demand | def:3; par:7 | 152.2 Mt crude steel (2025) | SOURCED-IN | MoS AR 2025-26 Table 3.2.2 p.16 (JPC FY2024-25: 152.180 Mt) | measured base year |
| dem_profile | def:10 | 1 (logistic) | ASSUMPTION | REVIEW §7: S-curve is the central demand case | switch; 0 restores the paper's 5 %/yr |
| dem_sat | def:11 | 680 Mt | ASSUMPTION | 400 kg crude/cap (between Germany and Japan, worldsteel WSIF 2025 p.17; stock-replacement flow, Pauliuk et al. 2013 Table 4) × 1,701 M (UN WPP 2024 medium peak, 2061) | sensitivities 510 / 816 Mt (NITI 2026 p.63: ~450 kg/cap); NEEDS CALL pending (REVIEW §7 (i), §8.3 #2) |
| dem_g0 | def:12 | 0.082 /yr | DERIVED | FY22–FY25 crude-steel CAGR, 120.29 → 152.18 Mt (MoS AR 2025-26 §3.2.2 p.16) | NEEDS CALL pending (REVIEW §7 (ii): alternative anchor "90 % of D_sat by 2060") |
| growth_rate | def:4; par:8 | 0.05 /yr | SOURCED-IN | MoS 2024 §15 p.347 (374 Mt in 2050); IEA 2020 ISTR pp.118, 123 (≈ 444 Mt); NITI 2026 §3.2.1 p.63 (624 Mt) | inactive at dem_profile = 1; inside the 3.7–5.8 % range, above the 4.4 % median (pessimistic) |
| real_discount_rate | def:18 | 0.06 | SOURCED-IN | Murty, Panda & Joe 2018 (IEG for NITI) exec. summary PDF pp.13–14 (6 % for environmental projects); Murty et al. 2020 IEG WP 388 p.1 | social-planner rate; private WACC evidence is 10 % (Murty 2018 PDF p.15; IECC 2026 Fig. 4c p.12; TA–TERI Params_Finance); MC level fixed at 0.06 (run_mc:68); NEEDS CALL pending (REVIEW §4 #2) |
| sunk | def:349 | 1 | ASSUMPTION | ST-01 decision: capex charged up front on builds | structural switch |
| carbon_tax | def:244 | 0 $/tCO₂ | ASSUMPTION | register §3.1, tag A | no carbon price in any study |
| cap0_bof | def:252 | 90 Mt | SOURCED-IN | GEM 2026 *Pedal to the Metal* pp.26–27 (86 Mtpa BOF); MoS AR 2025-26 Annex IV p.182 | upper of two kept (larger coal lock-in) |
| cap0_cdri | def:253 | 104.1 Mt | SOURCED-IN | MoS 2024 §5.4.2 pp.106–107 (EAF 36.6 + IF 68.8 Mt); MoS AR 2025-26 Annex IV p.182 (residual 97–103 Mt) | ? DRI sheet proposes 91 Mt (MoS AR 2025-26 Annex IV PDF p.188, melt-shop basis); NEEDS CALL pending (REVIEW §4 #5) |
| cap0_ngdri | def:254 | 12.9 Mt CS | DERIVED | 12.3 Mt DRI capacity (MoS 2024 Table 1.3 PDF p.45) ÷ (1.1 × (1 − 0.13)) | demand sheet proposes 11.2 (lower bound); NEEDS CALL pending (REVIEW §4 #5) |
| cap0_h2dri | def:255 | 0 | ASSUMPTION | no H₂-DRI plant operating in India in 2025 | trivially zero |
| cap0_scrap | def:256 | 0.75 Mt | SOURCED-IN | Stage 1 register §3.1 (tag S) | ? the register tags it S but no citation text appears in the register or the sheets; verify |
| init f_bof | t_add:5 | 0.411 | SOURCED-IN | MoS AR 2025-26 §3.2.3 p.17 (BOF 41.1 %) and Annex V p.183 (JPC FY2024-25) | ST-07 fix (was 0.51) |
| init f_eaf | t_add:6 | 0.589 | DERIVED | 1 − f_bof (JPC: EAF 20.8 % + IF 38.2 %) | |
| init_f_cdri | t_add:9 | 0.902 | DERIVED | output-basis calibration: coal route = EAF+IF steel − gas sponge iron ÷ 1.1 ≈ 0.91 (MoS AR 2025-26 pp.18, 181, 183) | ? derivation gives 0.910 for FY25, code keeps the original 0.902; DRI sheet proposes 0.84 (DRI-metallic share); NEEDS CALL pending (REVIEW §4 #5) |
| init_scrap_eaf | t_add:7 | 0 Mt | ASSUMPTION | original model | ? reasoning not stated; ~30 Mt of scrap-based steel is booked to the DRI routes in 2025 (ST-07; demand sheet S-1) |
| util_min_bof | def:304 | 0.70 | SOURCED-IN | MoS AR 2025-26 Annex IV p.182 (BOF route 0.66–0.73; integrated plants 0.70–1.00); GEM 2026 | consistent with f_bof = 0.411 |
| util_min_cdri | def:305 | 0.70 | SOURCED-IN | MoS AR 2025-26 Annex IV p.182 (other IF 0.69–0.74); MoS 2024 p.107 (EIF 73 %) | |
| util_min_ngdri | def:306 | 0.70 | SOURCED-IN | MoS AR 2025-26 Annex III/IV (gas DRI 0.65–0.80; AM/NS 0.70–0.80) | median 0.72 |
| util_min_h2dri | def:307 | 0.70 | ASSUMPTION | same as the NG shaft furnace; no Indian H₂-DRI fleet | demand sheet: no admissible source |
| util_min_scrap | def:308 | 0.60 | SOURCED-IN | MoS AR 2025-26 Annex IV p.182 (other EAF 0.55–0.70); MoS 2024 p.106 (EAF 77 %) | inside range (median 0.65) |
| util_max | def:309 | 0.85 | SOURCED-IN | MoS AR 2025-26 Table 3.2.2 p.16 (all-India 0.76–0.80, FY22–25); Annex IV p.182 (best plants 0.93–1.00) | between sector and plant evidence |
| labor_cost | def:245 | 22 $/t-cap/yr | SOURCED-IN | Tata Steel IR 2024-25 PDF pp.134, 352 (44.6); JSW IR 2024-25 Standalone FS PDF p.36 (12.8); TA–TERI 2026 Commodities (15–30) | median |
| maint_pct | def:247 | 0.03 of up-front capex /yr | SOURCED-IN | TA–TERI 2026 Tech `om_to_capex` 0.03; brackets: Tata IR 2024-25 PDF p.353 (33.8 $/t), JSW (9.0 $/t) | single source for the %; ST-11 fix |
| other_opex | def:248 | 10 $/tCS | DANGLING | none matches the boundary (Tata/JSW insurance + rates + rent bracket 2–14 $/t) | placeholder |
| cap_buffer | def:278 | 0.40 | ASSUMPTION | code comment: guard above the 0.365 floor; inert | |

## 2. Coke oven, sinter, pellets, blast furnace, BOF

| Parameter | file:line | Current value | Category | Source(s) or derivation | Note |
|---|---|---|---|---|---|
| ng_e_pell | def:22 | 70 kWh/t pellet | SOURCED-IN | KIOCL AR 2024-25 p.78 (64.4 / 68.6 kWh/t); KIOCL AR 2023-24 p.24 | one company; upper |
| ng_pell_fuel | def:23 | 1.6 GJ/t pellet | SOURCED-IN | MoS 2024 §11.6.2 p.255 (0.36–0.40 Gcal/t); KIOCL AR 2024-25 p.78; TA–TERI Emission_Factor (127 kg CO₂/t) | ST-03; fuel mix (coal) unsourced, pessimistic |
| ng_ore_pell | def:24 | 1.1 t ore/t pellet | DANGLING | none | placeholder (ST-02 operator fixed) |
| ng_cog_cv | def:25 | 0.0176 GJ/Nm³ | SOURCED-IN | MoS 2024 §10.9 p.240 (COG GCV ~4,200 kcal/Nm³) | single source |
| ng_bfg_cv | def:26 | 0.0033 GJ/Nm³ | DANGLING | none (IPCC 2006 Vol.2 Table 1.2 p.1.18 gives a mass basis only) | placeholder |
| ng_bofg_cv | def:27 | 0.008 GJ/Nm³ | DANGLING | none (IPCC Table 1.2: mass basis only) | placeholder |
| n0_e_c | def:37 | 75 kWh/t coke | DANGLING | none (aggregate check only: MoS 2024 Table 6.2 p.122) | placeholder |
| n0_cf | def:38 | 1.47 t coal/t coke | SOURCED-IN | Tikadar 2025 p.8 (coke-to-coal 68.93 % → 1.45) | one estimate; current value is the upper |
| n0_br_c | def:39 | 0.056 t/t coke | DANGLING | none | placeholder |
| n0_tar_c | def:40 | 0.04 t/t coke | DANGLING | none | placeholder |
| n0_cdq_whr | def:41 | 33 → 150 kWh/t coke (2025 → 2050) | SOURCED-IN | JISF 2022 sheet A-4 (pdf p.13) / MoS 2024 Table 5.6 (150 kWh/t coke) × 22 % diffusion (JISF 2022 list pdf p.8; MoS 2024 Fig. 5.4) | 2016 diffusion; linear rise to full by 2050 is an assumption |
| n0_cog_c | def:43 | 440 Nm³/t coke | DANGLING | none | placeholder |
| n0_rec_cog | def:44 | 190 Nm³/t coke | DANGLING | none | placeholder |
| n0_rec_bfg | def:45 | 270 Nm³/t coke | DANGLING | none | placeholder |
| n1_e_sint | def:49 | 50 kWh/t sinter | DANGLING | none | placeholder |
| n1_lime_sint | def:50 | 0.04 t/t sinter | DANGLING | none | placeholder |
| n1_ore_sint | def:51 | 0.9 t/t sinter | DANGLING | none | placeholder |
| n1_brz_sint_25 | def:52 | 0.05 t/t sinter | SOURCED-IN | MoS 2024 §11.6.1 p.255 (3–5 %); IPCC 2006 Vol.3 Ch.4 p.4.26 (EU 38–55 kg/t) | upper of India range; ST-04 |
| n1_brz_sint_50 | def:54 | 0.04 t/t sinter | DERIVED | total sinter fuel 0.05 held − biochar 0.01 | |
| n1_bio_sint_25 | def:53 | 0 | SOURCED-IN | MoS 2024 p.256 (biochar at research stage) | |
| n1_bio_sint_50 | def:55 | 0.01 t/t sinter | SOURCED-IN | MoS 2024 p.255 (biochar 20–25 % of fuel) | lower bound × 0.05 |
| n1_sintcool_whr | def:56 | 2 → 22 kWh/t sinter | SOURCED-IN | JISF 2022 list A-2 pdf p.8 (22.1 kWh/t; 8 % diffusion) | linear rise to full by 2050 is an assumption |
| n2_e_hm | def:63 | 55 kWh/tHM | SOURCED-IN | Tikadar 2025 p.6 (103.34 GWh / 4.25 Mt = 24.3) | ? kept above the single source (pessimistic), not taken from it |
| n2_sint_hm | def:64 | 1.15 t/tHM | SOURCED-IN | Tikadar 2025 p.6 (0.92) | ? kept above the single source (higher burden) |
| n2_lime_hm | def:65 | 0.025 t/tHM | DANGLING | none | placeholder |
| n2_slag_hm | def:66 | 0.30 t/tHM | SOURCED-IN | IBM IMYB 2019 p.19 (300–540 kg/t) | lower bound (slag earns a credit); realistic ≈ 0.40 |
| n2_pel_hm | def:67 | 0.35 t/tHM | SOURCED-IN | Tikadar 2025 p.6 (pellet + lump 0.59 t/tHM) | ? pellet/lump split unsourced |
| n2_ore_hm | def:68 | 0.15 t/tHM | SOURCED-IN | Tikadar 2025 p.6 (as above) | ? split unsourced |
| n2_bfg_hm | def:69 | 1,500 Nm³/tHM | SOURCED-IN | Tikadar 2025 p.6 (1,748) | kept lower (less gas) |
| n2_rec_bfg | def:70 | 690 Nm³/tHM | SOURCED-IN | Tikadar 2025 p.6 (686) | single source |
| n2_rec_cog | def:71 | 30 Nm³/tHM | SOURCED-IN | Tikadar 2025 p.6 (6.7) | ? kept above the single source (more internal use) |
| n2_trt_whr | def:72 | 21 → 40 kWh/tHM | SOURCED-IN | JISF 2022 sheet A-6 pdf p.15 / MoS 2024 Table 5.6 (50; 40–60); LBNL 2013 Table 1 (46); × 42 % diffusion (JISF 2022 pdf p.8) | 2050 = lower end of 40–60 |
| n2_coalpci_hm_25 | def:74 | 0.11 t/tHM | SOURCED-IN | MoS 2024 Table 5.4 p.104 (60–199 kg), p.105 (50–180), p.112 (50–150); Tikadar 2025 p.6 (0.061) | median |
| n2_coalpci_hm_50 | def:76 | 0.15 t/tHM | SOURCED-IN | MoS 2024 p.112 (180–200 kg/t total injection) | |
| n2_biopci_hm_25 | def:75 | 0 | SOURCED-IN | MoS 2024 p.256 (research stage) | |
| n2_biopci_hm_50 | def:77 | 0.04 t/tHM | SOURCED-IN | MoS 2024 p.256 (20–40 % of PCI) | lower bound |
| n2_coke_hm_25 | def:78 | 0.47 t/tHM | SOURCED-IN | MoS 2024 Table 5.4 p.104 (fuel rate 505–579 kg/tHM) − PCI 0.11; Tikadar 2025 p.6 (0.536) | top of the MoS fuel-rate range (pessimistic) |
| n2_coke_hm_50 | def:79 | 0.40 t/tHM | DERIVED | 2050 fuel rate held at 0.59 − PCI 0.15 − biomass 0.04 (no efficiency gain); context Tata IR 2024-25 p.168 (best furnace 485 kg) | |
| n3_e_bof | def:86 | 174 kWh/tCS | SOURCED-IN | MoS 2024 Table 6.2 p.122 (174.09); TA–TERI Params_BOF (130) | upper |
| n3_metallic_bof | def:87 | 1.1 t/tCS | SOURCED-IN | Tikadar 2025 pp.6–7 (≥ 1.08 HM only); TA–TERI (1.0475) | upper |
| n3_ls_bof | def:88 | 0.075 t/tCS | DANGLING | none (TA–TERI burnt lime 0.031 t/tls as context) | placeholder |
| n3_sl_bof | def:89 | 0.15 t/tCS | SOURCED-IN | IBM IMYB 2019 p.19 (150–200 kg/t) | lower bound (credit) |
| n3_bofg_bof | def:90 | 100 Nm³/tCS | DANGLING | none (Tata IR 2024-25 p.247 hourly figure not convertible) | placeholder |
| n3_rec_cog | def:91 | 65 Nm³/tCS | DANGLING | none | placeholder |
| phi0_bof | def:141 | 0.10 | SOURCED-IN | MoS 2024 p.102 (scrap 10–12 % in BF-BOF) | lower bound |
| phi_min_bof | def:145 | 0.05 | DANGLING | none | sheet calls it a modelling assumption but states no reasoning |
| phi_max_bof | def:149 | 0.25 | SOURCED-IN | MoS 2024 p.102 (25–30 % in the best BF-BOF plants globally) | lower bound |
| blend_ramp | def:153 | 0.05 /yr | ASSUMPTION | register §3.2, tag A | ? no reasoning recorded |

## 3. DRI, EAF/IF and scrap

| Parameter | file:line | Current value | Category | Source(s) or derivation | Note |
|---|---|---|---|---|---|
| n4_e_dri | def:97 | 310 kWh/t DRI | SOURCED-IN | kiln 70 = median of MoS 2024 Table 6.2 PDF p.136 (100), CEEW 2024 PDF p.2 (55–65), TERI 2021 PDF p.27 (70); IF step 237 = (IF 825, median of MoS Table 6.2 PDF p.136, CEEW 2024 PDF p.14, MoS §5.4.2.2 PDF p.121) − 664, ÷ 0.68 t DRI/tCS | kiln waste-heat power omitted (pessimistic; REVIEW §4) |
| n4_pel_dri | def:98 | 1.05 t/t DRI | SOURCED-IN | CEEW 2024 PDF pp.2, 13 (70 % pellet at 1.4–1.6 t); TERI 2021 PDF pp.27–28 (1.55 t ore) | one survey gives the split |
| n4_ore_dri | def:99 | 0.55 t/t DRI | SOURCED-IN | CEEW 2024 PDF p.2 (lump 1.8–2.0 t) × 30 % | as above |
| n4_c_dri | def:100 | 0.9 t coal/t DRI | SOURCED-IN | 21 GJ/t DRI = median of TERI 2021 PDF p.27, MoS 2024 Table 5.5 PDF p.119, MoS Table 10.3 PDF p.246, CEEW 2021 PDF pp.24, 37; ÷ the model's 24 GJ/t coal basis | tonnage on the 24 GJ/t basis (ST-13) |
| n5_e_dri | def:103 | 120 kWh/t DRI | SOURCED-IN | MoS 2024 Table 6.2 PDF p.136; CEEW 2021 PDF p.24; TA–TERI Params_DRI-SF (100) | median |
| n5_pel_dri | def:104 | 1.5 t/t DRI | SOURCED-IN | TA–TERI Params_DRI-SF (1.414); Vogl et al. 2018 p.739; IECC 2026 Table S-3 PDF p.33 | upper |
| n5_ore_dri | def:105 | 0 | ASSUMPTION | no admissible source for lump ore in Indian shaft furnaces; all sources are pellet-only and 1.5 t pellet is already the upper total feed | DRI sheet lists it as no-source |
| n5_ng_dri | def:106 | 0.22 t NG/t DRI (≈ 10.9 GJ) | SOURCED-IN | median of 5: MoS 2024 Table 10.3 PDF p.246; CEEW 2021 PDF p.24; TA–TERI Params_DRI-SF; MoS §8.4.3 PDF pp.195–196; MoS Table 10.1 PDF p.230 (0.33) | was 0.35 |
| n6_e_dri | def:110 | 125 kWh/t DRI | SOURCED-IN | TA–TERI Params_DRI-SF (123); CEEW 2021 (120) | upper of two |
| n6_pel_dri | def:111 | 1.5 t/t DRI | SOURCED-IN | as n5_pel_dri | |
| n6_ore_dri | def:112 | 0 | ASSUMPTION | as n5_ore_dri | DRI sheet lists it as no-source |
| n6_h2_dri | def:113 | 0.07 t H₂/t DRI | SOURCED-IN | TA–TERI Params_DRI-SF (58 kg + heating ≈ 75); CEEW 2021 PDF p.25 (47–68); IECC 2026 Table S-3 (66); MoS 2024 Fig. 8.13 PDF p.200 (46) | inside 66–75 when heating is H₂-fired |
| n7_e_eaf | def:117–118 | 664 kWh/tCS | SOURCED-IN | MoS 2024 Table 6.2 PDF p.136; IECC 2026 Table S-3; TA–TERI Params_EAF (680); Vogl 2018 p.740 | median 672 |
| n7_dri_ratio | def:119 | 1.1 t/tCS | SOURCED-IN | TA–TERI Params_EAF (1.0958); MoS 2024 PDF p.195 (1.11) | |
| n7_eltrd | def:120 | 0.002 t/tCS | SOURCED-IN | Vogl 2018 p.739 (2 kg/tLS); TA–TERI Params_EAF (0.002) | also charged to IF steel (SN-1) |
| n7_ls | def:121 | 0.09 t/tCS | SOURCED-IN | Vogl 2018 p.738 (50 kg CaO); TA–TERI Params_EAF (0.0369) | limestone-equivalent (× 100/56) of the upper value |
| n7_cs | def:122 | 0.02 t/tCS | SOURCED-IN | MoS 2024 PDF p.275 (EAF coal 20 kg/ts) | single source |
| n7_ss | def:123 | 0.15 t/tCS | SOURCED-IN | IBM IMYB 2019 PDF p.19 (150–200 kg/t) | lower bound (credit) |
| n7_eafg | def:124 | 0 GJ/tCS | ASSUMPTION | no admissible source; a credit set to its lower bound (Indian EAFs rarely recover off-gas power, power sheet §E1) | DRI sheet lists it as no-source |
| n8_e_eaf | def:127–128 | 590 kWh/tCS | SOURCED-IN | CEEW 2024 PDF p.14 (550); Vogl 2018 p.740 (667); TA–TERI Params_EAF (600); IEA 2020 ISTR PDF p.43 (≤ 583) | median of 4 |
| n8_phi_eaf | def:129 | 1.1 t/tCS | SOURCED-IN | TA–TERI (1.096); MoS 2024 (1.11) | |
| n8_eltrd | def:130 | 0.002 t/tCS | SOURCED-IN | Vogl 2018; TA–TERI | route costed as an EAF |
| n8_ls | def:131 | 0.06 t/tCS | SOURCED-GL | Vogl 2018 (50 kg CaO ≈ 0.089 limestone-eq, EAF) | ? kept between IF and EAF; IF value unsourced |
| n8_cs | def:132 | 0.02 t/tCS | SOURCED-IN | MoS 2024 p.260 (EAF 20 kg/ts) | EAF basis |
| n8_ss | def:133 | 0.15 t/tCS | SOURCED-IN | IBM IMYB 2019 (150–200 kg/t) | lower bound |
| n8_eafg | def:134 | 0 GJ/tCS | ASSUMPTION | as n7_eafg | DRI sheet lists it as no-source |
| phi0_cdri | def:142 | 0.325 | DERIVED | calibrated so 2025 scrap use = n8_scrap_seed (37 Mt) under f_eaf = 0.589 (REVIEW §2 commit 14) | context: MoS 2024 Table 1.2(b) PDF p.44, IF scrap 38 % |
| phi0_ngdri | def:144 | 0.13 | SOURCED-IN | MoS 2024 Table 1.2(b) PDF p.44 (EAF 12 %); §8.4.3 PDF p.195 (15 %) | |
| phi_min_cdri | def:146 | 0 | ASSUMPTION | no minimum scrap share in the DRI charge | ? reasoning not recorded (natural default) |
| phi_min_ngdri | def:147 | 0 | ASSUMPTION | as phi_min_cdri | ? as above |
| phi_min_h2dri | def:148 | 0 | ASSUMPTION | as phi_min_cdri | ? as above |
| phi_max_cdri | def:150 | 0.40 | SOURCED-IN | MoS 2024 PDF p.120 (EAF scrap 40–80 %); MoS Table 1.2(b) PDF p.44; CEEW 2024 PDF p.14 | lower end of the technical range |
| phi_max_ngdri | def:151 | 0.40 | SOURCED-IN | as phi_max_cdri | |
| phi_max_h2dri | def:152 | 0.40 | SOURCED-IN | as phi_max_cdri | |
| n8_scrap_seed | def:155; par:28 | 37 Mt (2025) | ASSUMPTION | kept as FY2024-25 scrap use; no admissible FY25 figure; latest is 33.4 Mt FY2023-24 incl. imports (MoS 2024 Table 1.1 PDF p.42) | ? sits above the latest data; the 2025 shares are calibrated to it (REVIEW §5) |
| n8_scrap_rate | def:154; par:26 | 0.05 /yr | DERIVED | 37 Mt × 1.05²⁵ = 125 Mt in 2050 = NITI 2026 Table E1 PDF p.25 lower case (20 % × 624 Mt) | NITI's figure is a use scenario, not supply (PDF p.136); axis 4/5/6/7 % (axes.py:39), study templates 5 % (REVIEW §8.4) |

## 4. Electricity, grid and waste-heat recovery

| Parameter | file:line | Current value | Category | Source(s) or derivation | Note |
|---|---|---|---|---|---|
| grid_price_start | def:165 | 0.08 $/kWh | SOURCED-IN | 0.64 × new captive 0.071 (MoS 2024 Table 6.17 PDF p.155) + 0.36 × HT tariff median 0.096 (CEA tariff book 2025 Tables 7(h), 8(a) pdf pp.231–232); split from MoS 2024 §6.6 PDF p.146 | blend matching the blended EF; prices sheet proposed 0.095 (grid only) |
| grid_price_end_fast | def:166 | 0.063 $/kWh (2050, θ_grid = 1) | ASSUMPTION | keeps the original −21 % fall at θ_grid = 1 | no source projects a real decline (TA–TERI Grid 0.072 → 0.077) |
| n9_grid_ef_start | def:196 | 0.000880 tCO₂/kWh | SOURCED-IN | CEA CO₂ Baseline Database v21/v22 Table B (weighted average 0.710, FY25) and Table 5 (coal 0.969); MoS 2024 §6.6 PDF p.146 (grid 37.3 % / captive 62.7 %) | blended grid + captive; θ_grid scales the blend (state in paper, REVIEW §4) |
| n9_eta | def:186 | 0.30 | SOURCED-IN | MoS 2024 §6.12.2(2) PDF p.163 (old captive plants 2,800–3,000 kcal/kWh); Collis et al. 2021 p.7 (0.30–0.50, global) | lower bound |
| n9_whr | def:194–195 | 0.33 → 0.5 | DERIVED | 2025 share calibrated to MoS 2024 Tables 6.2, 6.4 PDF pp.136–138 (≈ 133 kWh/tHM in-plant generation; model 133.6) | 2050 end 0.5 is an assumption (MoS Table 6.10 PDF p.146: majors' WHR share 22 → 26 % by 2030; kept below BF-route demand) |
| whr_steam_eff | def:389 | 0.85 | DANGLING | none (BEE boiler guide unreachable) | placeholder |
| n9_whr_capex | def:238 | 0.03 $/kWh | SOURCED-IN | LBNL 2013 Table 1 (0.023 at 6 %); JISF 2022 CDQ cost (0.028) | upper, rounded |
| n9_whr_opex | def:239 | 0.003 $/kWh | SOURCED-IN | LBNL 2013 Table 1 (O&M change 0.00) | ? kept above the single source |
| whr_ccs_integration | o_wh:36 | 1 | ASSUMPTION | study toggle: CCS regeneration steam may draw on the gas pool | switch |

## 5. Prices and credits (constant 2025 USD)

| Parameter | file:line | Current value | Category | Source(s) or derivation | Note |
|---|---|---|---|---|---|
| ng_cost_ccoal | def:208 | 200 $/t | SOURCED-IN | MoC National Coal Index OM 06.03.2026 Annex Table B pdf p.10 (193); Coal Directory 2024-25 Table 8.7 p.177 (207); IECC 2026 Table S-4 pdf p.34 (200) | median; regret backdrop still 250 (NEEDS CALL pending, REVIEW §4 #3) |
| n5_cost_NG | def:231; par:12 | 12 $/MMBtu | SOURCED-IN | TA–TERI Commodities (11.8); MoS 2024 exec. summary pdf pp.24, 26 (10.0); CEEW 2021 pdf p.16 (15.8) | median, delivered RLNG; regret backdrop 15 |
| ng_mmbtu_per_t | def:232 | 52.6 MMBtu/t NG | DERIVED | PPAC Ready Reckoner FY2025-26 conversions (1 MMT = 1,325 MMSCM; 1 MMBtu = 25.2 SCM) | replaces hard-coded 50 |
| ng_gj_per_mmbtu | def:376 | 1.055 | DERIVED | unit conversion | |
| ng_cost_scrap | def:220; par:27 | 400 $/t | SOURCED-IN | DGCIS HS 72044900 FY25 / FY26 import unit values (426 / 379); TA–TERI Commodities (402) | regret backdrop 350 |
| ng_cost_fineore | def:213 | 65 $/t | SOURCED-IN | IBM MSMP Table 6(a) Jan & Dec 2025 (55–56 ex-mine); IECC 2026 pdf p.15 (80); TA–TERI Ore_Price (54) | ? kept between the ex-mine median (56) and the purchase price (80); not the median |
| ng_cost_lumpore | def:217 | 80 $/t | SOURCED-IN | IBM MSMP Table 6(a) Jan & Dec 2025 (lumps 77 ex-mine) | one source; upper |
| ng_cost_pcoal | def:218 | 110 $/t | DANGLING | none (bracket 91–207 from MoC import data) | placeholder |
| ng_cost_ncoal | def:221 | 98 $/t | SOURCED-IN | Coal Directory 2024-25 Table 8.7 p.177 (91); MoC Monthly Statistical Report Mar 2025 Table 8.6 p.79 (79–100) | import grade; upper ≈ 100 |
| ng_cost_lime | def:214 | 60 $/t | SOURCED-IN | IBM MSMP Table 6(a) limestone (7–41 ex-mine); TA–TERI Commodities (33.5) | ? above every admissible value; no burnt-lime price found |
| ng_cost_biochar | def:215 | 520 $/t | SOURCED-GL | Ibitoye et al. 2024, *Bioresour. Bioprocess.* 11:65 (China, 3,500–3,787 CNY/t) | pessimistic; alternative is relabelling the BF input as raw biomass (REVIEW §4) |
| n7_cost_electrode | def:235 | 2,500 $/t | SOURCED-IN | DGCIS HS 85451100 exports (~2,750) and imports (~2,460); TA–TERI Commodities (2,500) | median |
| n8_cost_electrode | def:237 | 2,500 $/t | SOURCED-IN | as n7_cost_electrode | |
| n0_credit_tar | def:223 | 430 $/t | SOURCED-IN | DGCIS HS 27060010 exports (578–603) and imports (430–488) | lower bound (credit) |
| ng_credit_slag | def:219 | 10 $/t | SOURCED-IN | DGCIS HS 26180000 imports (13–15) and exports (9–11) | lower bound (credit) |
| n0_credit_breeze | def:222 | 55 $/t | DANGLING | none (bound: met-coke imports 255–317, DGCIS HS 27040090) | placeholder |
| n1_cost_breeze | def:225 | 85 $/t | DANGLING | none (same bound) | placeholder |

## 6. Capital costs (up-front, 2025 USD per t/yr of capacity)

The BF-BOF route total of **$1,200/t** is a sourced pessimistic upper bound: IECC 2026 Table S-4 (800); CEEW 2021 p.7 (< 1,220, ceiling); IEA 2020 ISTR p.46 fn 15 (1,240–1,860, global). Its split across nodes is derived (rows below).

| Parameter | file:line | Current value | Category | Source(s) or derivation | Note |
|---|---|---|---|---|---|
| n0_capex | def:224 | 240 | DERIVED | share of the BF-BOF total 1,200 in the original 40:30:10:80:40 proportions | proportions unsourced; only the total affects route choice |
| n1_capex | def:226 | 180 | DERIVED | as n0_capex | |
| ng_capex_pell | def:216 | 60 | DERIVED | as n0_capex | also enters the DRI routes |
| n2_capex | def:227 | 480 | DERIVED | as n0_capex | IEA 2020 p.46: BF alone ≈ 250–370 |
| n3_capex | def:228 | 240 | DERIVED | as n0_capex | |
| n4_capex_coal | def:229 | 400 | SOURCED-IN | TA–TERI 2026 Tech (rotary kiln 300 $/t DRI × 1.2 owner's cost × 1.1 t DRI/tCS) | single source |
| n5_capex_ng | def:230 | 460 | SOURCED-IN | shaft furnace 415 $/t DRI: TA–TERI Tech (345; 414 with owner's cost), Vogl 2018 (415), CEEW 2021 (328); × 1.1 | |
| n6_capex_h2 | def:233 | 460 | DERIVED | = n5_capex_ng (same unit; Vogl 2018, TA–TERI) | |
| n7_capex | def:234 | 400 | SOURCED-IN | EAF incl. casting: TA–TERI Tech (337; 404 with owner's cost), Vogl 2018 (332), CEEW 2021 (183) | |
| n8_capex | def:236 | 400 | DERIVED | = EAF unit cost (n7_capex); scrap handling via ocapex_scrapchain | |
| ocapex_scrapchain | def:343 | 100 $/(t scrap/yr) | DANGLING | none (Scrap Recycling Policy 2019 PDF p.18 sizes the build-out but gives no cost) | placeholder; state as an assumption in the paper |
| ocapex_coalchain | def:344 | 0 | ASSUMPTION | included in the fuel price (code comment) | |
| ocapex_ngchain | def:345 | 0 | ASSUMPTION | included in the fuel price (code comment) | |

## 7. Lifetimes and salvage

| Parameter | file:line | Current value | Category | Source(s) or derivation | Note |
|---|---|---|---|---|---|
| life_bof | def:284 | 40 yr | SOURCED-IN | IEA 2020 ISTR pp.43–46 ("40-year typical average lifetimes", global); TA–TERI 2026 Tech (40); IECC 2026 ("40+-year life") | |
| life_cdri | def:285 | 40 yr | SOURCED-IN | as life_bof | |
| life_ngdri | def:286 | 40 yr | SOURCED-IN | as life_bof | |
| life_h2dri | def:287 | 40 yr | SOURCED-IN | as life_bof | |
| life_scrap | def:288 | 40 yr | SOURCED-IN | as life_bof | |
| legacy_life | def:294 | 25 yr (fleet runs to 2050) | ASSUMPTION | no vintage data; with a 40-yr life and Indian BFs ~15 yr old (IEA 2020 pp.43–46) the fleet outlasts the horizon | pessimistic (keeps fossil fleet available) |
| life_h2elec | def:412 | 15 yr | SOURCED-IN | TA–TERI Tech (10); IECC 2026 p.30 (25 yr plant, stack every 10); IEA GHR 2025 annex p.6 (stack 50,000 h ≈ 16–23 yr) | median rounded down |
| life_re | def:418 | 25 yr | SOURCED-IN | IEA WEO 2024 p.336; IECC 2026 Table S-1; TA–TERI Tech (30) | |
| life_ccs | def:352 | 25 yr | SOURCED-IN | NITI 2022 p.156; IEAGHG 2013/04 p.1; IEA 2020 ISTR p.107 | |
| salv_frac | v_cap:308–309 | straight-line unused life after 2050, discounted from 2051 | DERIVED | from life_* and real_discount_rate (ST-16, REVIEW §5); no new inputs | covers routes, electrolyser, RE and CCS, not supply-chain builds (REVIEW §4) |

## 8. Green hydrogen

| Parameter | file:line | Current value | Category | Source(s) or derivation | Note |
|---|---|---|---|---|---|
| h2elec_capex_start | def:406 | 800 $/kW (2025) | SOURCED-IN | median of 5: TA–TERI Tech (672); IECC 2026 Fig. 4 p.12 (550); IEA GHR 2025 Fig. 3.10 p.99 (924 China, 2,360 RoW); NITI–RMI 2022 Exh. 10 p.29 (802) | |
| h2elec_capex_end_slow | def:177 | 800 $/kW (2050, θ_tech = 0) | ASSUMPTION | no learning: explicit pessimistic bound | no source projects flat capex; sourced slow case 376 (IRENA 2020 p.11) |
| h2elec_capex_end_fast | def:178 | 159 $/kW (2050, θ_tech = 1) | SOURCED-IN | IRENA 2020 p.11 (130 $/kW, 2020 USD, global); NITI–RMI 2022 p.31 (125 → 137) | pessimistic of two |
| re_capex_start | def:407 | 835 $/kW | SOURCED-IN | median: TA–TERI Tech (832); IRENA RPGC 2024 Tables 3.1 p.95, 2.1 p.71 (839); IEA WEO 2024 Table B.4a p.333 (1,011); MoS 2024 Table 6.21 p.150 (585) | 50/50 solar/wind; was hard-coded 800 |
| re_capex_end_slow | def:179 | 835 $/kW | ASSUMPTION | no learning: explicit pessimistic bound | sourced alternative 732 (IEA WEO 2024 Table B.4a, STEPS) |
| re_capex_end_fast | def:180 | 695 $/kW | SOURCED-IN | IEA WEO 2024 Table B.4c p.335 (India NZE 2050: solar 280, wind 1,040; 50/50) | single source |
| re_cf | def:403 | 0.25 | SOURCED-IN | median of 6: IEA WEO 2024 Table B.4a p.333; IRENA RPGC 2024 Table 2.2 p.76, p.31; TA–TERI hourly profiles; MoS 2024 Table 6.21 p.150 (0.31); MNRE NGHM 2023 p.23 (derived 0.25); IECC 2026 Table S-1 | also the electrolyser utilisation (H₂ sheet S1) |
| h2_kwh_per_t | def:402 | 53,000 kWh/t H₂ | SOURCED-IN | IEA GHR 2025 annex p.6 (52,900); IECC 2026 Table S-2 p.31 (52,000); TA–TERI Params_H2 (53,200); IRENA 2020 p.11 (51,200) | median |
| h2_opex | def:404 | 30 $/t H₂ | SOURCED-IN | IRENA 2020 p.40 (water < 20 $/t H₂); TA–TERI Params_H2 and Commodities (water 15.75, labour 9.4) | upper of water + labour |
| fopex_h2elec (3 % rate) | def:414 | 0.03 × electrolyser capex /yr | SOURCED-IN | IEA GHR 2025 annex p.6 (3 %); TA–TERI `om_to_capex` 0.03; IECC 2026 Table S-2 p.31 (5.5 %) | median; rate hard-coded in the formula |
| fopex_h2re | def:420 | 22 $/kW/yr | SOURCED-IN | IEA WEO 2024 Table B.4a p.333 (22.6); TA–TERI Tech (17.7) | upper of two |
| lcoh_2025_target | def:421 | 5,000 $/t H₂ | SOURCED-IN | MoS 2024 §8.4.1 p.175 (USD 5/kg for 2024-25) | reporting check only (h2_firm_on = 0) |
| h2_firm_on | def:422 | 0 | ASSUMPTION | ST-12: firming plug off; sourced build-up gives 4.72 $/kg (Indian tenders 3.0–5.1) | switch |
| h2_ref_cap | def:438; axes.py:70 | 2 Mt (axis 1 / 2 / 3 Mt) | ASSUMPTION | peak steel H₂ additions 0.25 / 0.5 / 0.75 Mt/yr: high = whole NGHM pace (MNRE 2023 p.4, ≈ 0.71 Mt/yr); low ≈ 3× MoS steel path (MoS 2024 p.184) | re-anchored (REVIEW §8.4); paper's "1.5–5 $/kg" range text still open (REVIEW §4 #4) |
| h2_peak_rate | def:439 | 0.25 | ASSUMPTION | normalisation: only scales h2_ref_cap; the product is what is anchored | |
| h2_base_start | def:440 | 0 | DANGLING | none | ramp-shape placeholder; rationale not stated |
| h2_base_end | def:441 | 0.05 | DANGLING | none (comment "rising → capital efficiency" only) | ramp-shape placeholder |
| h2_gauss_sigma | def:442 | 2 yr | DANGLING | none | ramp-shape placeholder |
| h2_peak_lag | def:446 | 5 yr | DANGLING | none (NGHM 2023 → 2030 supports only "several years") | ramp-shape placeholder |
| h2_ramp_mode | def:436 | 2 (Gaussian) | ASSUMPTION | structural switch; mode 0 also drops other limits (ST-08, unchanged) | |
| h2_ramp_ratchet | def:473 | 1 | ASSUMPTION | reasoning in code comment: holding the crest rate makes an earlier H₂ debut dominate pointwise | |

## 9. Carbon capture and storage

| Parameter | file:line | Current value | Category | Source(s) or derivation | Note |
|---|---|---|---|---|---|
| n10_ccs_cost_start | def:242; par:32 | 75 $/tCO₂ all-in (2025) | SOURCED-IN | NITI 2022 Table 6-4 p.139 (Rs 2,900–3,600) + Table 6-3 note p.139 (T&S 10–15); MoS 2024 Table 9.13 p.221 (64, range 41–92); MoS 2024 Table 9.1 p.196 (Tata pilot) | India median ≈ 67, rounded up; capex back-solves to ≈ 154 $/(t/yr) |
| ccs_capex_fall_slow | def:182 | 0.27 | SOURCED-IN | NITI 2022 pp.25, 144 (storage subsidy Rs 4,100 → 3,000/t) | |
| ccs_capex_fall_fast | def:183 | 0.60 | SOURCED-IN | MoS 2024 p.203 (capture cost 50 → 20 $/t) | |
| ccs_ts_cost | def:356 | 25 $/tCO₂ | SOURCED-IN | NITI 2022 Table 6-3 note p.139 (10–15 → 16); MoS 2024 Table 9.13 p.221 (7 + 20); IEA 2020 ISTR Fig. 2.11 p.107 (20 → 25) | median |
| ccs_vopex_solvent | def:355 | 2 $/tCO₂ | SOURCED-IN | MoS 2024 Table 9.5 p.203 (NTPC: 0.204 kg/t at INR 650/kg) | single source, rounded up |
| ccs_fom_pct | def:354 | 0.05 /yr | SOURCED-IN | MoS 2024 Table 9.5 p.203 (5 %); NITI 2022 Table 6-3 (5–7 %); IEA 2020 CCUS p.73 (3 %) | median |
| ccs_mult_bf | def:357 | 1.0 | ASSUMPTION | reference stream (normalisation) | |
| ccs_mult_cdri | def:358 | 1.2 | DANGLING | none (nearest analogue NITI 2022 Table 6-2, coal power 0.83) | placeholder |
| ccs_mult_ng_proc | def:368 | 1.0 | DANGLING | none (analogues NITI 2022 Table 6-2: 0.10–1.19) | set by analogy (Midrex top gas needs a full solvent unit); was 0.5 |
| ccs_mult_ng_flue | def:369 | 1.3 | SOURCED-IN | NITI 2022 Table 6-2 (refinery flue 1.33 × steel; coal power 0.83) | analogue |
| ccs_ngdri_proc_share | def:363 | 0.6 | DANGLING | none | placeholder |
| ccs_kwh_bf | def:359 | 190 kWh/tCO₂ | SOURCED-IN | NITI 2022 Table 6-3 p.139 (170–190); context IEAGHG 2013 Table C-3, IEAGHG 2018 Table 1 | upper of the only comparable Indian estimate |
| ccs_kwh_cdri | def:360 | 300 kWh/tCO₂ | SOURCED-IN | NITI 2022 Table 6-3 (coal power flue 250–300) | analogue; upper |
| ccs_kwh_ng_proc | def:364 | 110 kWh/tCO₂ | SOURCED-IN | MoS 2024 Table 9.1 (JSW 45; JSPL 25–28); NITI 2022 Table 6-3 (70–90) | kept above the evidence (covers compression) |
| ccs_kwh_ng_flue | def:365 | 300 kWh/tCO₂ | SOURCED-IN | NITI 2022 Table 6-3 (refinery 110–130; coal power 250–300) | analogue; upper |
| ccs_steam_bf | def:361 | 3.0 GJ/tCO₂ | SOURCED-IN | NITI 2022 Table 6-3 (1.3–1.5 t steam); MoS 2024 Table 9.1 (Tata 1,000–1,100 kg) and Table 9.5 (NTPC 1.29 t); IEAGHG 2013 Table C-1 (3.03) | India median |
| ccs_steam_cdri | def:362 | 3.3 GJ/tCO₂ | SOURCED-IN | NITI 2022 Table 6-3 (coal power 1.3–1.55 t → 2.8–3.3 GJ) | analogue; upper |
| ccs_steam_ng_proc | def:366 | 3.7 GJ/tCO₂ | SOURCED-IN | MoS 2024 Table 9.1 (JSW gas-DRI 1,740 kg; JSPL ~1,700 kg steam/tCO₂) | was 0.3 |
| ccs_steam_ng_flue | def:367 | 3.6 GJ/tCO₂ | SOURCED-IN | NITI 2022 Table 6-3 (refinery and coal power, up to 3.3 GJ) | analogue; slightly above |
| ccs_ref_elec | def:373 | 0.07 $/kWh | ASSUMPTION | used only to back out capex; NITI 2022 Table 6-3 implies 0.035 | kept (the anchor dominates) |
| ccs_ref_steam | def:374 | 5 $/GJ | ASSUMPTION | used only to back out capex; NITI 2022 Table 6-3 implies 4.1 | kept |
| ccs_boiler_eff | def:375 | 0.89 | SOURCED-GL | IEAGHG 2013/04 Table C-5 (89.2–90.2 %) | lower bound of a single source |
| fc_max | q_cc:17 | 0.90 | SOURCED-IN | IEA 2020 ISTR p.107; IEA 2020 CCUS p.73; IEAGHG 2018 Table 1 p.7; NITI 2022 Table 6-2 p.138 (~90 %); MoS 2024 p.199 (80–85 % peak) | median; replaces 0.85 × 0.90 (ST-10) |
| ccs_share_bf | q_cc:18 | 0.67 | SOURCED-IN | NITI 2022 Fig. 2-14 p.46 (0.71); IEAGHG 2013 p.14 (0.67–0.79); NITI 2022 Tables 6-1, 6-2 pp.137–138 (~50 %); MoS 2024 p.221 fn 20 (59 %) | cap 0.90 × 0.67 = 0.60 of route CO₂ (median) |
| ccs_share_cdri | q_cc:19 | 0.67 | DANGLING | none (same as BF by analogy) | pessimistic placeholder (audit addition) |
| ccs_share_ngdri | q_cc:20 | 0.90 | DANGLING | none (IEA 2020 ISTR p.95 qualitative only) | placeholder (audit addition) |
| ccs_start | q_cc:52 | 2035 | SOURCED-IN | DST 2025 CCUS roadmap p.xiv (commercial hubs in 2035–45); MoS 2024 p.200 and Table 9.12 p.219 (6–9 yr to 1 Mt/yr); Union Budget 2026-27 para 38 p.12 | was 2027 |
| phi_2050 | q_cc:53; axes.py:92 | 0.25 (axis 0 / 0.05 / 0.10 / 0.25) | SOURCED-IN | IEA 2020 ISTR p.84 (25 % of steel direct CO₂); NITI 2022 Fig. 6-5 p.145 (31 % of capturable ≈ 26 %); NITI 2026 Table E1 p.25 (CCUS "Low" in 2050, low levels) | was 0.50 (no feasibility source); NEEDS CALL pending (REVIEW §8.3 #3: 0.25 vs a lower central) |

## 10. Emission factors

| Parameter | file:line | Current value | Category | Source(s) or derivation | Note |
|---|---|---|---|---|---|
| ef_ccoal | def:382 | 2.67 tCO₂/t | SOURCED-IN | IPCC 2006 Vol.2 Table 1.2 p.1.18 (28.2 GJ/t) × Table 1.4 p.1.23 (94.6 kg/GJ); IPCC Vol.3 Table 4.3 p.4.27 (2.68); India BUR-4 Table 2.8 (2.22) | pessimistic bound (IPCC over BUR-4); ~76 % imported (Tikadar 2025 p.8) |
| ef_pci | def:383 | 2.46 tCO₂/t | SOURCED-IN | IPCC 2006 Tables 1.2/1.4 (2.44); IPCC Table 4.3 (2.46); BUR-4 iron & steel (1.65, domestic) | pessimistic bound; Indian PCI mostly imported |
| ef_ncoal | def:384 | 2.32 tCO₂/t | DERIVED | the model's 24 GJ/t coal basis × 96.8 kgCO₂/GJ (BUR-4 Table 2.8 PDF p.107, 26.39 tC/TJ) | keeps tonnage, price and EF on one basis (ST-13) |
| ef_ng | def:385 | 2.69 tCO₂/t | SOURCED-GL | IPCC 2006 Table 1.2 p.1.18 (48.0 GJ/t) × Table 1.4 p.1.24 (56.1 kg/GJ); TA–TERI uses the same | |
| ef_lime | def:386 | 0.44 tCO₂/t | DERIVED | CaCO₃ calcination stoichiometry (IPCC 2006 Vol.3 Table 4.3 p.4.27: 0.12 kgC/kg) | |
| ef_eltrd | def:387 | 3.67 tCO₂/t | DERIVED | full oxidation of carbon, 44/12 (IPCC Table 4.3 gives 3.01; TA–TERI 3.67) | upper Scope 1 bound |
| ef_breeze | def:388 | 3.04 tCO₂/t | SOURCED-GL | IPCC 2006 Table 4.3 (coke 0.83 kgC/kg) | ST-04: purchased breeze only |
| ng_co2_gj | def:377 | 0.0561 tCO₂/GJ | SOURCED-GL | IPCC 2006 Table 1.4 p.1.24 (56,100 kg/TJ) | CCS backup boiler |

## 11. Resource availability and policy axes

| Parameter | file:line | Current value | Category | Source(s) or derivation | Note |
|---|---|---|---|---|---|
| ccoal_cap, abundant | structural/axes/ccoal_abundant.mod:6–31 | 60.5 → 293.6 Mt | ASSUMPTION | 2025 = 54.5 Mt imports (≈ ICMW 54.08, MoC MSR Mar 2025 Table 8.1) + ~6 Mt washed domestic (Coal Directory 2024-25 Table 4.23 p.113: 5.86); imports +6.4 %/yr; floored at the scarce path | ? sheet call on the 2025 base (63.4 or 72 Mt) not recorded in REVIEW; the 2025 value is inert (coking_coal_bound skips 2025) |
| ccoal_cap, scarce | structural/axes/ccoal_scarce.mod:5–30 | 60.5 → 102.9 Mt | ASSUMPTION | imports frozen at FY2025-26 66.33 Mt (MoC *Production and Supplies*); domestic +7.5 %/yr from 6 Mt | re-anchored (REVIEW §8.4); ? the +7.5 %/yr domestic CAGR has no citation in the sheets; axes.py:21 comment ("91.1 Mt") is stale |
| n5_ng_cap, BAU | structural/axes/ng_bau.mod:9–34 | 1.87 → 3.73 Mt NG | ASSUMPTION | steel share 3.5 % = gas-DRI output 8.88 Mt (MoS AR 2025-26 PDF p.24) × 0.21 t NG/t DRI (PNGRB 2024 PDF p.18) ÷ 53.5 Mt national; national trajectory unchanged | actual pure-NG share 1–1.7 % (PPAC Ready Reckoner FY2025-26 PDF p.59; MoS 2024 Table 1.1 p.28); NEEDS CALL pending (REVIEW §4 #1) |
| n5_ng_cap, policy | structural/axes/ng_policy.mod:9–34 | 1.87 → 11.27 Mt NG | ASSUMPTION | same 3.5 % share of the government-target gas path (PIB 18 Dec 2023: 15 % gas by 2030; PNGRB 2024 optimistic 6.6 Mt in 2040) | NEEDS CALL pending (REVIEW §4 #1) |
| n5_ng_cap, core default | par:35–60 | 1.87 → 7.67 Mt NG (shock path) | ASSUMPTION | shock trajectory × 0.35 | ST-15 unchanged; every study overrides it |
| avg_emi | par:9; axes.py:97 | 1.8 (axis 1.6 / 1.8 / 2.0) tCO₂/tCS, 2025–50 average | ASSUMPTION | targets tested; ≈ 3-, 4- and 4/5-star bands of India's Green Steel Taxonomy (PIB 12 Dec 2024) at × 1.037 tCS/tfs (MoS AR 2025-26 PDF p.9) | plant-level, finished-steel basis differs (demand sheet H) |
| emission_monotonic | t_add:34–37 | on | ASSUMPTION | paper §2.2; linear form (REVIEW §7) | still dropped in the regret study (elastic demand) |
| cap_add_common | def:301; axes.py:77 | 20 Mt/yr (axis 20 / 30) | ASSUMPTION | JPC capacity pace +18.2 and +20.8 Mt in FY24–FY25 (MoS AR 2025-26 p.16, REVIEW §7) | 20 = today's pace, not "double historical" as the paper says |
| legacy_phaseout | def:262; axes.py:84 | 0 (axis 0 / 1) | ASSUMPTION | brackets unknown fleet vintage (register §3.1) | |
| ng_h2_start_year | def:114; par:17; axes.py:31 | 2030 in par (def default 2040); axis 2030 / 2035 / 2040 / 2045 | ASSUMPTION | scenario axis (register §3.7) | ? def default 2040 is overridden by par:17 |
| theta_grid | def:164; par:2; axes.py:46 | 0.5 (axis 0.25 / 0.5 / 0.75) | ASSUMPTION | grid-outcome speed; grid-only 2050 evidence −55 to −100 % (CEA NEP 2023; TERI 2024 Table 16; WRI India 2024) | scales the grid + captive blend; axes.py:43 comment ("$0.055") is stale |
| theta_tech | def:163; par:3; run_mc:66 | 0.5 (MC 0–1) | ASSUMPTION | H₂ learning speed (global science) | 2050 ends set by the h2elec/re end-point rows |
| theta_ccs | def:181; par:4; run_mc:67 | 0.5 (MC 0–1) | ASSUMPTION | CCS learning speed | |

## 12. Study-only values

| Parameter | file:line | Current value | Category | Source(s) or derivation | Note |
|---|---|---|---|---|---|
| MC coking-coal price levels | run_mc:63; run_regret:104 | 100 / 250 / 400 $/t | ASSUMPTION | stress range (register §3.11: paper cites [2,38–40]) | ? evidence 175–260 (prices sheet); suggested 150 / 200 / 300; NEEDS CALL pending (REVIEW §4 #3) |
| MC gas price levels | run_mc:64; run_regret:105 | 5 / 15 / 25 $/MMBtu | ASSUMPTION | stress range (as above) | ? evidence 8–16; suggested 8 / 12 / 18; NEEDS CALL pending |
| MC scrap price levels | run_mc:65; run_regret:106 | 250 / 350 / 450 $/t | ASSUMPTION | stress range (as above) | ? evidence 379–426; suggested 300 / 400 / 500; NEEDS CALL pending |
| Regret backdrop coking coal | run_regret:96 | 250 $/t | DANGLING | none; evidence supports 200 (prices sheet §A) | NEEDS CALL pending (REVIEW §4 #3) |
| Regret backdrop gas | run_regret:96 | 15 $/MMBtu | DANGLING | none; evidence supports 12 | NEEDS CALL pending |
| Regret backdrop scrap | run_regret:97 | 350 $/t | DANGLING | none; evidence supports 400 | NEEDS CALL pending |
| IMPORT_REPORT | run_regret:285 | 760 $/t | SOURCED-IN | DGTR 2025 safeguard final findings PDF p.141 (HRC CIF reference 675) + 12 % safeguard duty; MoS AR 2025-26 PDF p.8 (all imports ≈ 1,057) | basic customs duty not added |
| IMPORT_P | run_regret:239 | 20,000 $/t | ASSUMPTION | numerical penalty for infeasibility | |
| PEN | run_regret:247 | 5,000 $/tCO₂ | ASSUMPTION | numerical penalty on the emissions cap | check emis_slack = 0 in reported cells (not verified) |

## Not counted: inactive, dead or neutral inputs

| Parameter | file:line | Value | Why not counted |
|---|---|---|---|
| maintenance_cost | def:246 | 15 | replaced by maint_pct; unused |
| n10_ccs_eta | def:204 | 0.85 | no longer referenced (ST-10 fix; only in a comment of q_cc) |
| n10_ccs_cost_end | def:243 | 75 | dead parameter |
| ng_credit_power | def:212 | 0.03 | declared, never referenced (no power export) |
| n1_sintgas_sint, ng_sintgas_cv | def:58, 28 | 1,800; 0.0006 | feed `sg_out`, which is unused (ST-05) |
| n2_h2_hm_25, n2_h2_hm_50 | def:80–81 | 0 | H₂ in the BF is zero throughout |
| H2_cap, ramp_frac | par:18; def:348 | 1.5 Mt; 0.15 | ramp mode 1 only (default mode 2) |
| H2_BIGM | def:437 | 1e10 | numerical big-M |
| h2_capex_mult | def:405 | 1 | neutral sensitivity multiplier |
| constants in equations | o_wh:42 (277.78 kWh/GJ); r_cost / s_emissions (÷ 24 GJ/t for pellet fuel) | — | unit conversions |

## DANGLING parameters

35 parameters keep a placeholder value with no admissible source and no derivation:

- `other_opex` (Demand/finance/fleet): 10 $/tCS
- `ng_ore_pell` (Coke oven-sinter-BF-BOF): 1.1 t ore/t pellet
- `ng_bfg_cv` (Coke oven-sinter-BF-BOF): 0.0033 GJ/Nm³
- `ng_bofg_cv` (Coke oven-sinter-BF-BOF): 0.008 GJ/Nm³
- `n0_e_c` (Coke oven-sinter-BF-BOF): 75 kWh/t coke
- `n0_br_c` (Coke oven-sinter-BF-BOF): 0.056 t/t coke
- `n0_tar_c` (Coke oven-sinter-BF-BOF): 0.04 t/t coke
- `n0_cog_c` (Coke oven-sinter-BF-BOF): 440 Nm³/t coke
- `n0_rec_cog` (Coke oven-sinter-BF-BOF): 190 Nm³/t coke
- `n0_rec_bfg` (Coke oven-sinter-BF-BOF): 270 Nm³/t coke
- `n1_e_sint` (Coke oven-sinter-BF-BOF): 50 kWh/t sinter
- `n1_lime_sint` (Coke oven-sinter-BF-BOF): 0.04 t/t sinter
- `n1_ore_sint` (Coke oven-sinter-BF-BOF): 0.9 t/t sinter
- `n2_lime_hm` (Coke oven-sinter-BF-BOF): 0.025 t/tHM
- `n3_ls_bof` (Coke oven-sinter-BF-BOF): 0.075 t/tCS
- `n3_bofg_bof` (Coke oven-sinter-BF-BOF): 100 Nm³/tCS
- `n3_rec_cog` (Coke oven-sinter-BF-BOF): 65 Nm³/tCS
- `phi_min_bof` (Coke oven-sinter-BF-BOF): 0.05
- `whr_steam_eff` (Power-grid-WHR): 0.85
- `ng_cost_pcoal` (Prices): 110 $/t
- `n0_credit_breeze` (Prices): 55 $/t
- `n1_cost_breeze` (Prices): 85 $/t
- `ocapex_scrapchain` (Capex): 100 $/(t scrap/yr)
- `h2_base_start` (H2): 0
- `h2_base_end` (H2): 0.05
- `h2_gauss_sigma` (H2): 2 yr
- `h2_peak_lag` (H2): 5 yr
- `ccs_mult_cdri` (CCS): 1.2
- `ccs_mult_ng_proc` (CCS): 1.0
- `ccs_ngdri_proc_share` (CCS): 0.6
- `ccs_share_cdri` (CCS): 0.67
- `ccs_share_ngdri` (CCS): 0.90
- `Regret backdrop coking coal` (Study-only): 250 $/t
- `Regret backdrop gas` (Study-only): 15 $/MMBtu
- `Regret backdrop scrap` (Study-only): 350 $/t

## NEEDS CALL items still open

1. **NG availability: 3.5 % steel share of national gas** (`ng_bau.mod`, `ng_policy.mod`, `par:35–60`). Confirm the reasoning (REVIEW §4 #1).
2. **Discount rate** 6 % social vs 10 % private (`real_discount_rate`, REVIEW §4 #2); state the framing in the paper.
3. **Study centrals and sampled price levels** (REVIEW §4 #3): regret backdrop coal 250 / gas 15 / scrap 350 and Monte Carlo levels 100/250/400, 5/15/25, 250/350/450 versus core 200 / 12 / 400 and suggested 150/200/300, 8/12/18, 300/400/500.
4. **Paper's sampled H₂ cost range "1.5–5 $/kg"** no longer matches the model (2050: 2.4–4.7 $/kg) (REVIEW §4 #4). The ramp levels themselves were re-anchored in §8.4.
5. **Conflicting sheets, values kept**: `init_f_cdri` 0.902 vs 0.84, `cap0_cdri` 104.1 vs 91, `cap0_ngdri` 12.9 vs 11.2 (REVIEW §4 #5).
6. **Demand saturation level** 680 vs 816 Mt, and the S-curve anchor (8.2 %/yr initial growth vs 90 % of D_sat by 2060) (`dem_sat`, `dem_g0`; REVIEW §7).
7. **2050 demand**: central S-curve 545 Mt vs the ≈ 444 Mt median of published projections (REVIEW §8.3 #2).
8. **CCS central ceiling** `phi_2050` = 0.25 or lower (REVIEW §8.3 #3).

Smaller items REVIEW §4 lists for awareness: biochar at 520 $/t vs relabelling the BF input as raw biomass; coal-DRI kiln waste-heat power left out; salvage excludes supply-chain builds; θ_grid scales grid + captive together (state in paper); the paper's 66.33 Mt coking-coal imports are FY26, the model base is FY25. Not a parameter call but still open: Monte Carlo at low CCS and the Monte Carlo and regret reruns under the §8.4 axis bounds (REVIEW §8.3 #4, §8.4).
