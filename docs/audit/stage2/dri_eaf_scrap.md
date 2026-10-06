# Stage 2 — DRI, EAF/induction-furnace and scrap coefficients (register §3.3)

Status: IN PROGRESS (skeleton written first; sub-groups are filled one by one).

Model: `nakulneupane/steel-sector-decarbonization` @ b33b88a, `core/definitions.mod` unless stated.

## Needs your call
IN PROGRESS

## Conventions used in this sheet

- 1 Gcal = 4.1868 GJ; 1 kcal/kg = 4.1868 kJ/kg (so 5,200 kcal/kg = 21.8 GJ/t); 1 MMBtu = 1.055 GJ.
- The model's own energy bases (read from the code, not from sources): non-coking coal is costed per tonne (`ng_cost_ncoal`) and emits 0.110 × 24 = 2.64 tCO₂/t (`s_emissions.mod:10,32`), so 1 t coal is treated as **24 GJ**. NG is costed as `n5_cost_NG × 50` per tonne (`r_cost.mod:76`) and emits 0.055 × 50 per tonne (`s_emissions.mod:16`), so 1 t NG is treated as **50 GJ = 50 MMBtu**. The "value in model units" columns below use these bases.
- "DRI" = tonne of sponge iron; "tCS" = tonne of crude (liquid) steel.

## A. Coal DRI (rotary kiln) — `i_dri_coal.mod`

| Parameter | file:line | Current | Sources (short cite, quote, page) | Value in model units | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| **Coal-DRI thermal energy** (implied by `n4_c_dri` × 24 GJ/t) | `definitions.mod:84` | 1.0 t × 24 GJ = **24 GJ/t DRI** | (1) TERI 2021 compendium PDF p. 27: "SEC of coal-based DRI production using rotary kiln varies from 4.10 to 5.26 Gcal/t-DRI (average: 4.51 Gcal/t-DRI)" (plant data, India). (2) MoS 2024 roadmap Table 5.5 (source BEE), PDF p. 119: "Specific Thermal Energy (Gcal/t) 4.5 - 6.0" (100 TPD), "4.5 - 5.85" (350/500 TPD). (3) MoS 2024 Table 10.3, PDF p. 246: "Coal based ~17-23.4 GJ/t of product DRI". (4) Yadav, Guhan & Biswas 2021 (CEEW) PDF p. 24: "thermal SEC of the RK process is estimated to be 23 GJ/T-DRI (Agrawal, Sahoo, and Mohanty 2015)"; Box 2, PDF p. 37: "SEC (18.70 to 26.11 GJ/tDRI)". | (1) 18.9 (17.2–22.0); (2) 18.8–25.1, mid 22.0; (3) 17–23.4, mid 20.2; (4) 23 (18.7–26.1) GJ/t DRI | **21 GJ/t DRI** (median of the four central values; range 17–26) | upper (more fuel) — not needed, ≥3 estimates | see next row |
| n4_c_dri (t coal/t DRI) | `definitions.mod:84` | 1.0 | (1) TERI 2021 PDF p. 27 table: "Sponge iron production tpd 110 / Coal consumption tpd 110 / Calorific value of coal kcal/kg 5200". Mass balance PDF p. 28: "Coal (4.2 tph) … Sponge Iron (4.2 tph)". (2) MoS 2024 Table 5.5 (BEE), PDF p. 119: "Specific coal consumption, t/t 0.8 - 1.5"; "GCV of imported coal, Kcal/kg 5,500"; "GCV of Indian coal, kcal/kg 3,000 – 4,000". (3) Nitturu et al. 2024 (CEEW) PDF p. 10: "In the case of domestic coal, consumption ranges from 1.4 to 1.6 t-coal/t-DRI. However, with imported coal, consumption is notably lower, ranging from 0.9 to 1.1 t-coal/t-DRI." | TERI 1.0 t at 21.8 GJ/t; BEE 0.8–1.5 t; imported coal 23.0 GJ/t, Indian coal 12.6–16.7 GJ/t; CEEW domestic 1.4–1.6, imported 0.9–1.1 t | **0.9 t/t at the model's 24 GJ/t** (= 21 GJ/t DRI). If the coal basis is changed to a blended Indian+imported coal (~18 GJ/t, see call 1), **1.2 t/t** | upper | **NEEDS CALL** (ties to ST-13 and the coal price per tonne) |
| n4_e_dri (kWh/t DRI) | `definitions.mod:81` | 217 (= 100 kiln + 117 "IF extra") | **Kiln:** (1) MoS 2024 Table 5.5 (BEE) p. 105: "Specific Electrical energy (kWh/t) 120 / 100 / 80" for 100/350/500 TPD; MoS Table 6.2 PDF p. 136 (FY 2021-22): "Sponge Iron - Coal DRI … 100.00". (2) Nitturu et al. 2024 (CEEW) PDF p. 2: "average electrical consumption is in the range of 55 kWh/t-DRI to 65 kWh/t-DRI"; PDF p. 12: "some consumed 80 to 100 kWh/t-DRI". (3) TERI 2021 PDF p. 27: "Electricity consumption* kWh/t 70". **IF increment** (coal-DRI steel is melted in IFs): (4) MoS 2024 Table 6.2 PDF p. 136: "IF … 825.00" kWh/t vs "EAF … 664.00"; (5) CEEW 2024 PDF p. 14: IF "power consumption in these plants varies from 800 to 900 kWh per tonne of crude steel"; (6) MoS 2024 §5.4.2.2 PDF p. 121: "average specific electricity consumption of EIFs is about 680 kWh per tonne of liquid steel, with SEC ranging from 580 kWh to 800 kWh". | Kiln: 100, 60, 70 → median **70**. IF with DRI charge: 825, 850, 680 → median **825 kWh/tCS**, i.e. 161 kWh/tCS above `n7_e_eaf` (664). The model attaches this to DRI, not steel; at the 2025 charge (38.2 % scrap) DRI = 1.1 × 0.618 = 0.68 t/tCS, so 161 / 0.68 = **237 kWh/t DRI**. (Current 117 = 129/1.1 assumes no scrap.) | **310 kWh/t DRI** (70 + 237, rounded) | upper | default (but see call 3 on kiln waste-heat power) |
| n4_pel_dri (t pellet/t DRI) | `definitions.mod:82` | 1.5 | (1) Nitturu et al. 2024 (CEEW) PDF p. 2: "consumption rates of 1.8 to 2 t-ore/t-DRI for lump ore compared to 1.4 to 1.6 t-pellets/t-DRI for pellets"; PDF p. 13: "pellet use has an adoption rate above 70 per cent" (share of surveyed capacity). (2) TERI 2021 PDF p. 27: "about 1.55 tonne of iron ore, with 64% iron content, will produce a maximum of 1 tonne of sponge iron"; mass balance PDF p. 28: "Iron Ore (6.5 tph) … Sponge Iron (4.2 tph)" (= 1.55 t/t). | 70 % pellet × 1.5 = 1.05 t pellet; 30 % lump × 1.9 = 0.57 t lump; total 1.62 t/t (TERI 1.55) | **1.05** | upper total iron-bearing input | default (one survey gives the split) |
| n4_ore_dri (t lump/t DRI) | `definitions.mod:83` | 0.1 | as above | 0.57 | **0.55** | upper | default |

## B. NG DRI (shaft furnace) — `j_dri_ng.mod`

| Parameter | file:line | Current | Sources | Value in model units | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| n5_ng_dri (t NG/t DRI) | `definitions.mod:90` | 0.35 t = **17.5 GJ (≈17.5 MMBtu in the cost)** | (1) MoS 2024 Table 10.3 PDF p. 246: "Gas based 11-11.5 GJ/t of product DRI". (2) Yadav et al. 2021 (CEEW) PDF p. 24: "NG-based shaft furnace consumes approximately 267 normal cubic metres of NG/T-DRI (Fan and Friedmann 2021), which implies an SEC of 10.9 GJ/T-DRI" (HHV). (3) Transition Asia & TERI 2026 workbook, sheet Params_DRI-SF: "NG MMBtu/tDRI 9.5 … About 10 GJ/tDRI on high-grade pellet: 7.04 reduction plus 2.46 heating". (4) MoS 2024 §8.4.3, PDF pp. 195–196: "198 kg (261 scm) per tcs of natural gas", "for a charge mix of 85% DRI, 15% scrap, and an iron-to-steel conversion ratio of 1.11" → 0.94 t DRI/tCS. | (1) 11.25; (2) 10.9; (3) 10.0; (4) 198/0.94 = 211 kg NG/t DRI ≈ 10.5 GJ at 50 GJ/t | **0.22 t NG/t DRI** (≈ 11 GJ/t, median of four) | upper | **NEEDS CALL** (−37 %; `n5_ng_cap` is in tonnes, so the same cap would support ~60 % more NG-DRI) |
| n5_e_dri (kWh/t DRI) | `definitions.mod:87` | 120 | (1) MoS 2024 Table 6.2 PDF p. 136: "Sponge Iron - Gas DRI … 120.00". (2) Yadav et al. 2021 PDF p. 24: "typical power consumption in a shaft furnace is 120 kWh/T-DRI (Chatterjee 2012)". (3) TA & TERI 2026, Params_DRI-SF: "E_aux kWh/tDRI 100" (NG column has no heating term). | 120, 120, 100 | **120** (keep) | upper | default |
| n5_pel_dri (t pellet/t DRI) | `definitions.mod:88` | 1.5 | (1) TA & TERI 2026, Params_DRI-SF: "DR-grade pellet (Fe 67) per tonne of DRI" = 1.414. (2) Vogl, Åhman & Nilsson 2018 p. 739 (PDF p. 4): "the production of one tonne of steel requires 1504 kg of iron ore pellets" (100 % HBI; per t steel). (3) Domínguez Bennett et al. 2026 (IECC) Table S-3 (PDF p. 33): "Iron ore pellets required H2DRI 1.6 / 1.6 / 1.6 / 1.5 … 1.52 t iron/t steel" (per t steel). | per t DRI only (1) is direct: 1.41. (2),(3) are per t steel (≥ the per-DRI value). | **1.5** (keep; upper end) | upper | default |
| n5_ore_dri (t lump/t DRI) | `definitions.mod:89` | 0.1 | no admissible source found for lump ore in Indian shaft furnaces; all three sources above are pellet-only | — | **0** (total iron-bearing feed 1.5 t/t, already the upper end) | upper | default |

## C. H₂ DRI (shaft furnace) — `k_dri_h2.mod`

| Parameter | file:line | Current | Sources | Value in model units | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| n6_h2_dri (t H₂/t DRI) | `definitions.mod:97` | 0.07 | (1) TA & TERI 2026, Params_DRI-SF: "58 kg/tDRI for a hydrogen shaft furnace", plus electric gas heating "E_heating 576.8 kWh/tDRI". (2) Yadav et al. 2021 (CEEW) PDF p. 25: "hydrogen consumption in the shaft furnace ranges from 47-68 kg of H2/T-DRI (IEA 2020a)". (3) IECC 2026 Table S-3 (PDF p. 33): "H2-DRI-EAF efficiency 73.3 / 56.7 / 67-76 / 59.5 … 66 kg H₂/t steel"; sensitivity "[55-75 kg H2/tls]". (4) MoS 2024 Fig. 8.13 PDF p. 200: "DRI route = 46 kg/tDRI". | The model has no electric heater, so its H₂ must also cover gas heating. (1) 58 kg + 576.8 kWh ÷ 33.3 kWh/kg H₂ (LHV) ≈ 75 kg; (2) 47–68; (3) 66 per t steel (55–75); (4) 46 | **0.07** (keep; within 66–75 when heating is fired with H₂) | upper | default |
| n6_e_dri (kWh/t DRI) | `definitions.mod:94` | 110 | (1) TA & TERI 2026, Params_DRI-SF: "E_aux kWh/tDRI 100", "E_H2_recirc 23.2" (excluding heating). (2) Yadav et al. 2021: shaft furnace "120 kWh/T-DRI" (NG). | 123; 120 | **125** (fewer than 3 → upper) | upper | default |
| n6_pel_dri, n6_ore_dri | `definitions.mod:95–96` | 1.5, 0.1 | as for n5 (TA & TERI uses the same pellet rate for H₂ and NG) | 1.41–1.5 | **1.5, 0** | upper | default |

## D. DRI-EAF/IF steelmaking (`n7_*`, `l_eaf_dri.mod`)

| Parameter | file:line | Current | Sources | Value in model units | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| n7_e_eaf (kWh/tCS) | `definitions.mod:101` | 664 | (1) MoS 2024 Table 6.2 PDF p. 136 (FY 2021-22): "EAF 30.50 [Mt] 664.00" (Indian EAFs, mixed charge; the model value comes from here). (2) IECC 2026 Table S-3 (PDF p. 33): "Electricity EAF 0.53 / 0.78 / 0.55 / ~0.6 … 0.6 MWh/t steel". (3) TA & TERI 2026, Params_EAF: "E_base 600 kWh/tcs" + "E_slope_per_tDRI 80 kWh/tDRI" with "Full HBI 0.997 t/tcs" → 680. (4) Vogl et al. 2018 p. 740 (PDF p. 5): "producing steel in the EAF from scrap requires less energy (0.667 MWh/tLS) than from pure DRI (0.753 MWh/tLS)"; "using cold HBI requires 159 kWh/tLS more". | 664; 600; 680; 753 (hot) | **664** (keep; median 672) | upper | default |
| n7_dri_ratio (t metallics/tCS) | `definitions.mod:103` | 1.1 | (1) TA & TERI 2026, Params_EAF: "Metallic Charge t/tcs 1.0958". (2) MoS 2024 PDF p. 195: "iron-to-steel conversion ratio of 1.11". | 1.10; 1.11 | **1.1** (keep) | upper | default |
| n7_eltrd (t/tCS) | `definitions.mod:104` | 0.003 | (1) Vogl et al. 2018 p. 739 (PDF p. 4): "graphite electrodes are consumed at a rate of 2 kg/tLS (Remus et al., 2013)". (2) TA & TERI 2026, Params_EAF: "Electrode t/tcs 0.002". | 0.002; 0.002 | **0.002** | upper | default |
| n7_ls (t limestone-eq/tCS) | `definitions.mod:105` | 0.06 | (1) Vogl et al. 2018 p. 738 (PDF p. 3): "a lime consumption in the EAF of 50 kg/tLS". (2) TA & TERI 2026, Params_EAF: "Burnt Limestone t/tHBI 0.0369". The model treats this flow as limestone (0.44 tCO₂/t, `s_emissions.mod:11`) and prices it at `ng_cost_lime`. | as CaO: 0.050; 0.037. As limestone equivalent (× 100/56): 0.089; 0.066 | **0.09** (limestone-equivalent of the upper value) | upper | default |
| n7_cs (t coal/tCS) | `definitions.mod:106` | 0.01 | (1) MoS 2024, biochar table PDF p. 275: "Typical coal consumption in EAF, kg/ts 20.00". | 0.02 | **0.02** (single source) | upper | default |
| n7_ss (t slag/tCS) | `definitions.mod:107` | 0.15 | (1) IBM, *Indian Minerals Yearbook 2019*, "Iron, Steel & Scrap and Slag", PDF p. 19: "in steel making 150 to 200 kg per tonne of slag is generated per tonne of liquid steel". | 0.15–0.20 | **0.15** (keep; slag earns `ng_credit_slag`, so the lower bound is pessimistic) | lower (credit) | default |
| n7_eafg (GJ/tCS) | `definitions.mod:108` | 3 | no admissible source found for recoverable EAF/IF off-gas energy in Indian practice | — | **0** (no source; lower bound of a credit) | lower (credit) | default (effect is small: the pool is cut by 0.3 × `n9_whr` × `n9_eta`) |

## E. Scrap route (`n8_*`, `m_scrap_eaf.mod`)

| Parameter | file:line | Current | Sources | Value in model units | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| n8_e_eaf (kWh/tCS) | `definitions.mod:111` | 785 (= 0.75 × IF 825 + 0.25 × EAF 664) | The 825 and 664 are MoS Table 6.2 fleet averages for furnaces charged mostly with DRI/hot metal, not scrap. For a 100 %-scrap charge: (1) Nitturu et al. 2024 (CEEW) PDF p. 14: "when 100 per cent scrap is used in the IF, the electricity consumption could be reduced significantly to around 550 kWh/tcs" (industry representatives). (2) Vogl et al. 2018 p. 740 (PDF p. 5): "from scrap requires less energy (0.667 MWh/tLS)". (3) TA & TERI 2026, Params_EAF: "E_base 600 kWh/tcs — Electricity at a pure-scrap charge". (4) IEA 2020 ISTR PDF p. 43 box "Energy intensities of main production routes": "Scrap-based EAF … 2.1 GJ/t" (final energy, global; 2.1 GJ = 583 kWh if all electric). Context: MoS 2024 PDF p. 121: Indian EAFs "about 480 kWh per tonne" with 40–80 % scrap. | 550; 667; 600; ≤583 | **590 kWh/tCS** (median of four) | upper | **NEEDS CALL** (−25 % power on the scrap route) |
| n8_phi_eaf (t scrap/tCS) | `definitions.mod:113` | 1.1 | TA & TERI 2026 metallic charge 1.096 t/tcs; MoS 2024 conversion ratio 1.11 | 1.10 | **1.1** (keep) | upper | default |
| n8_eltrd (t/tCS) | `definitions.mod:114` | 0.003 | Vogl 2018 and TA & TERI 2026: 0.002 t/tCS in an EAF. An induction furnace has no graphite electrodes (MoS 2024 PDF p. 121: "Electrical energy is the source of energy input in EIF"; IBM 2019 PDF p. 10: heat "generated through electro magnetic induction"). | EAF 0.002; IF 0 | **0.002** if the route is costed as an EAF (as capex is, see capex.md); **0.0005** if the 75 % IF share in the comment is kept | upper | default (follow the call on n8_e_eaf) |
| n8_ls (t/tCS) | `definitions.mod:115` | 0.06 | Vogl 2018: 50 kg CaO/tLS (any charge). No admissible source found for lime use in Indian induction furnaces. | 0.089 limestone-eq (EAF) | **0.06** (keep; between IF and EAF; unsourced for IF) | upper | default |
| n8_cs (t/tCS) | `definitions.mod:116` | 0.01 | MoS 2024 p. 260: EAF "20.00" kg/ts. No admissible source for IF. | 0.02 (EAF) | **0.02** if costed as EAF; **0.01** (keep) if IF-heavy | upper | default |
| n8_ss (t/tCS) | `definitions.mod:117` | 0.15 | IBM 2019: 150–200 kg/tLS in steelmaking | 0.15 | **0.15** (keep) | lower | default |
| n8_eafg (GJ/tCS) | `definitions.mod:118` | 3 | no admissible source found | — | **0** | lower | default |

## F. Scrap shares, scrap supply, scrap chain
IN PROGRESS

## G. 2025 route split and starting capacity
IN PROGRESS

## Structural notes
IN PROGRESS

## Bibliography
IN PROGRESS
