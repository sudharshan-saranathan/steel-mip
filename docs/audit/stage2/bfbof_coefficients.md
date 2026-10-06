# Stage 2: BF-BOF process coefficients and emission factors

Audit target: `nakulneupane/steel-sector-decarbonization` @ b33b88a. Line numbers refer to `core/definitions.mod` unless another file is named. The emission factors are hard-coded in `core/modules/s_emissions.mod`.

**Rules (RESEARCH_BRIEF.md).** India-specific evidence comes first. Where there are 3 or more independent India estimates, the proposed value is their median. Where there are fewer, it is the **pessimistic** bound: the value that makes decarbonisation look harder. For fuel and energy use and emission factors, that is the upper bound. For recovery, credits and achievable scrap share, it is the lower bound.

**Status:** all sub-groups are complete.

---

## Needs your call

1. **Coking-coal emission factor (now 2.79 tCO₂/t).**
   - (a) **2.67, recommended.** IPCC 2006 default: 28.2 GJ/t × 94.6 kgCO₂/GJ. It suits a coal supply that is about 76 % imported, and it is the pessimistic bound.
   - (b) 2.56: an import-weighted blend, 0.76 × 2.67 + 0.24 × 2.22.
   - (c) 2.22: India's national inventory value (BUR-4) for domestic coking coal.

   With the other proposals below, the BF-BOF route comes out at 2.52 tCO₂/tCS under (a) and 2.21 under (c). The Ministry of Steel's range for the BF-BOF route is 2.20–2.60.
2. **Blast-furnace fuel rate in 2025 (now 0.53 t coke + 0.15 t PCI = 0.68 t/tHM).** The Ministry of Steel gives a national range of 505–579 kg/tHM, so the model is about 100 kg above the worst Indian plant.
   - (a) **Coke 0.47 + PCI 0.11 = 0.58, recommended.** This is the upper end of the Ministry of Steel range: pessimistic, but inside the evidence.
   - (b) Keep 0.53 + 0.15. Only one plant study (Tikadar et al., 0.536 + 0.061) supports the coke rate.
   - (c) Coke 0.42 + PCI 0.12: the middle of the Ministry of Steel range.

   Each 0.06 t/tHM of coke moves the 2025 sector intensity by about 0.18 t/tCS.
3. **Non-coking (DRI) coal emission factor (now 2.64 t/t, which implies 24 GJ/t).** Indian non-coking coal gives 1.65–1.76 tCO₂/t on an as-received basis.
   - (a) 1.76: BUR-2, national non-coking coal. This is the pessimistic India value.
   - (b) 1.65: BUR-4, the iron & steel sector factor.
   - (c) Keep 2.64 **only if** the DRI group restates `n4_c_dri` on a 24 GJ/t basis.

   The factor and the coal mass per tonne of DRI must use the same basis. This is the largest single lever on the 2.80 vs 2.54 gap (−0.27 t/tCS).
4. **Pellets (ST-03).** Cut `ng_e_pell` from 200 to **70 kWh/t** and add induration fuel at **1.6 GJ/t**.
   - (a) **Coal firing, 0.16 tCO₂/t pellet, recommended.** No source gives the fuel mix of Indian pellet plants, so the pessimistic choice is coal.
   - (b) Furnace oil, about 0.13 t/t. KIOCL fires furnace oil and is moving to natural gas.
   - (c) Natural gas, 0.09 t/t.

   Under (a) the two changes together add +0.03 t/tCS in 2025.
5. **Sinter fuel and bought breeze (with ST-04).** Cut `n1_brz_sint_25` from 0.09 to **0.05 t/t**. The Ministry of Steel gives 3–5 %; the IPCC/EU range is 38–55 kg/t. Separately, **count the carbon in bought-in breeze** at 3.04 tCO₂/t (IPCC carbon content of coke, 0.83 kgC/kg).
   - (a) **Both, recommended.** This adds +0.04 t/tCS.
   - (b) Breeze rate only: no emissions effect, because bought breeze carries no CO₂ in the model today.
   - (c) Count the carbon at 0.09 t/t: adds +0.12 t/tCS.

**Count of parameters with no admissible source: 18 of 61.** They are listed in §H.

---

## A. Coke oven

| Parameter | Line | Current | Sources (short cite, quote, page) | In model units | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| n0_e_c | 24 | 75 kWh/t coke | No admissible source found for coke-oven electricity alone. Aggregate check: Ministry of Steel 2024 Table 6.2, p.122: "Hot Metal & Pig Iron … 210.17" kWh/t (coke, sinter, pellets and BF together). With the proposals in this sheet, the model's aggregate is about 158 kWh/tHM, below that figure. | — | **75** (keep) | upper | default |
| n0_cf | 25 | 1.47 t coal/t coke | Tikadar et al. 2025, p.8: "The coke-to-coal ratio of ISI-A is approximately 68.93%"; "With an input of 3.38 million tons of coking coal, it produces 2.33 million tons of coke" (Indian integrated plant, about 2022). | 1/0.6893 = **1.45** | **1.47** (keep; one India estimate, current value is the upper) | upper | default |
| n0_br_c | 26 | 0.056 t/t | No admissible source found. | — | 0.056 (keep) | lower (it is a credit) | default |
| n0_tar_c | 27 | 0.04 t/t | No admissible source found. | — | 0.04 (keep) | lower (credit) | default |
| n0_cdq_whr | 28 | 80 kWh/t coke | Ministry of Steel 2024 Table 5.6, p.108 (from JISF 2022): CDQ saves "150 kWh/t- coke". This is the per-plant potential once CDQ is installed. No admissible figure for Indian CDQ coverage: the BAT diffusion chart (Fig. 5.4) cannot be read in the PDF text. | 150 × coverage | **80** (keep; implies about 53 % coverage) | lower | default (coverage unsourced) |
| n0_cog_c | 29 | 440 Nm³/t coke | No admissible India source found. | — | 440 (keep) | — | default |
| n0_rec_cog / n0_rec_bfg | 30–31 | 190 / 270 Nm³/t | No admissible source found. Underfiring check: 190 × 17.6 + 270 × 3.3 MJ ≈ 4.2 GJ/t coke. | — | keep | upper (internal use) | default |

## B. Sinter

| Parameter | Line | Current | Sources | In model units | Proposed | Pessimistic | Flag |
|---|---|---|---|---|---|---|---|
| n1_e_sint | 35 | 50 kWh/t | No admissible source found. | — | 50 (keep) | upper | default |
| n1_lime_sint | 36 | 0.04 t/t | No admissible source found. | — | 0.04 (keep) | upper | default |
| n1_ore_sint | 37 | 0.9 t/t | No admissible source found. | — | 0.9 (keep) | — | default |
| n1_brz_sint_25 | 38 | 0.09 t/t | (1) Ministry of Steel 2024, §11.6.1, p.255: "Coke breeze or coal with low volatiles can be used as fuel for sintering in the amount of 3 – 5 % (kg/kg)". (2) IPCC 2006 Vol 3 Ch 4, p.4.26 (EU plants): "a range of coke input of 38 to 55 kg coke per tonne sinter". | 0.03–0.05 (India); 0.038–0.055 (EU) | **0.05** (upper of the India range) | upper | **NEEDS CALL #5** |
| n1_brz_sint_50 | 40 | 0.058 | Same sources. Biochar can replace breeze "at 20–25 % (kg/kg) … without degrading the properties of the iron ore sinter" (Ministry of Steel, p.255). Total fuel is held at 0.05; the biochar share is set at the 20 % lower bound. | — | **0.04** | upper (fossil) | default |
| n1_bio_sint_25 | 39 | 0 | Ministry of Steel, p.256: biochar use is still at research stage ("research is going on"). | 0 | 0 (keep) | — | default |
| n1_bio_sint_50 | 41 | 0.022 (27.5 % of fuel, above the 25 % ceiling) | Ministry of Steel, p.255, 20–25 % (as above). | 20 % × 0.05 | **0.01** | lower (substitution) | default |
| n1_sintcool_whr | 42 | 30 kWh/t | Ministry of Steel Table 5.6, p.108: sinter-cooler heat recovery "0.251 GJ/t-sinter" of **steam**. No figure in kWh, and no Indian coverage figure. | — | 30 (keep) | lower | default (counted as no source) |

## C. Pellets (including induration fuel, ST-02/ST-03)

| Parameter | Line | Current | Sources | In model units | Proposed | Pessimistic | Flag |
|---|---|---|---|---|---|---|---|
| ng_e_pell | 10 | 200 kWh/t | (1) KIOCL Annual Report 2024-25, p.78 (company, Mangalore, India): "Energy consumption per ton … in Pellet plant unit 2023-24- 68.62 kWh/T … 2024-25 – 64.44 kWh/T". Of this, grinding & filtration is 31.19 / 25.56 kWh/t and the pellet plant alone 34.85 / 36.37 kWh/t. (2) KIOCL AR 2023-24, p.24: 1.906 Mt pellets in FY24, and 130.76 GWh (AR 2024-25, p.78), giving 68.6 kWh/t. (3) Context: IEA 2020 ISTR, p.27, total energy "in the range of 1-3 gigajoule (GJ) per tonne of pellets or sinter" (global). | 64–69 kWh/t including grinding | **70** (upper; one company) | upper | **NEEDS CALL #4** |
| ng_ore_pell | 11 | 1.1 t ore/t pellet | No admissible source found. The structural point stands: ST-02, divide → multiply. | — | 1.1 (keep, after the ST-02 fix) | upper | default |
| *new:* pellet induration fuel (missing, ST-03) | — | 0 | (1) Ministry of Steel 2024, §11.6.2, p.255: "The typical energy consumption for pelletisation ranges from 0.36 to 0.40 Gcal/t output". (2) KIOCL AR 2024-25, p.78: "Heat Consumption in '000 K Calories … 2024-25 - 219.22" per tonne (furnace-oil fired; the unit is ambiguous). (3) Transition Asia & TERI 2026 model inputs (`Emission_Factor` sheet): "127 kg/t induration (straight-grate)". | (1) 1.51–1.67 GJ/t; (2) 0.92 GJ/t; (3) 0.127 tCO₂/t | **1.6 GJ/t, coal-fired → 0.16 tCO₂/t** (1.6 × 96.8 kgCO₂/GJ, BUR-4 iron & steel non-coking coal) | upper | **NEEDS CALL #4** |
| fuel type | — | — | **No admissible source found** for the fuel mix of Indian pellet plants. KIOCL burns furnace oil and is converting to natural gas (AR 2023-24, PDF p.40: "installing dual burner system in the indurating machine of Pellet Plant to utilise Natural Gas as an alternative to the Furnace Oil being used currently"). Coal is assumed as the pessimistic case. | FO: 1.6 × 77.4 = 0.124; NG: 1.6 × 56.1 = 0.090 | coal | upper | (in #4) |

## D. Blast furnace

| Parameter | Line | Current | Sources | In model units | Proposed | Pessimistic | Flag |
|---|---|---|---|---|---|---|---|
| n2_coke_hm_25 | 62 | 0.53 t/tHM | (1) Ministry of Steel 2024 Table 5.4, p.104 (all Indian BF-BOF plants): "BF Coke Rate kg/thm 350-480"; "Total fuel rate kg/thm 505 - 579". (2) Tikadar et al. 2025, p.6: "2.28 million tons of coke … to produce 4.25 million tons of hot metal". (3) Ministry of Steel Table 10.4, p.240, uses a 420 kg/tHM case (scenario, not data). | (1) 0.35–0.48; (2) **0.536**; fuel-rate cap 0.579 | **0.47** (= MoS upper fuel rate 0.579 − PCI 0.11) | upper | **NEEDS CALL #2** |
| n2_coalpci_hm_25 | 58 | 0.15 | (1) MoS Table 5.4, p.104: "BF PCI/CDI kg/thm 60-199". (2) MoS p.105: "low PCI rate of 50-180 kg". (3) MoS p.112: "current level of 50-150 kg PCI/tonne". (4) Tikadar p.6: 0.26 Mt non-coking coal per 4.25 Mt HM. | midpoints 0.13 / 0.115 / 0.10; Tikadar 0.061; median about 0.11 | **0.11** | lower (more coke) | NEEDS CALL #2 |
| n2_coke_hm_50 | 63 | 0.48 | Tata Steel IR 2024-25, p.168: "E Blast Furnace achieving an annual fuel rate of 485 kg per ton of hot metal" (best Indian furnace). MoS p.112: PCI can rise "to 180-200 kg". The pessimistic case keeps the 2050 fuel rate at about 0.59, with no efficiency gain: coke = 0.59 − 0.15 − 0.04. | — | **0.40** | upper | NEEDS CALL #2 |
| n2_coalpci_hm_50 | 60 | 0.16 | MoS p.112 target of 180–200 kg/t total injection. | 0.18–0.20 total | **0.15** | — | default |
| n2_biopci_hm_25 | 59 | 0 | MoS p.256: biochar in the BF is at research stage. | 0 | 0 (keep) | — | default |
| n2_biopci_hm_50 | 61 | 0.053 | MoS p.256: "torrefied biomass limits the replacement of coal in PCI between 20 to 40 %"; "up to 1.8 GJ/thm … commercially in Brazil". | 20 % of 0.19 = 0.038 | **0.04** | lower | default |
| n2_e_hm | 48 | 55 kWh/tHM | Tikadar p.6: "103.34 GWh electricity" for 4.25 Mt HM. | 24.3 | **55** (keep; upper) | upper | default |
| n2_sint_hm | 49 | 1.15 | Tikadar p.6: "3.9 million tons of sinter" for 4.25 Mt HM. | 0.92 | **1.15** (keep). Total burden 1.65 against Tikadar's 1.51. One source; the current value is the higher-burden case. | upper | default |
| n2_pel_hm / n2_ore_hm | 52–53 | 0.35 / 0.15 | Tikadar p.6: "2.52 million tons of iron ore" (lump ore and pellets not split). | 0.59 (pellets + lump combined) | keep | — | default |
| n2_lime_hm | 50 | 0.025 | No admissible source found. | — | keep | upper | default |
| n2_slag_hm | 51 | 0.30 t/tHM | IBM *Indian Minerals Yearbook 2019*, Iron, Steel & Scrap and Slag, p.19: "blast furnace (BF) slag production ranges from about 300 to 540 kg per tonne of pig or crude iron produced". | 0.30–0.54 | **0.30** (keep; lower bound, because slag earns `ng_credit_slag`) | lower (credit) | default. The realistic Indian value is about 0.40. |
| n2_bfg_hm | 54 | 1,500 Nm³/tHM | Tikadar p.6: "7,428,352 thousand cubic meters of BFG as output" for 4.25 Mt HM. | 1,748 | **1,500** (keep; lower recovery) | lower | default |
| n2_rec_bfg | 55 | 500 Nm³/tHM | Tikadar p.6: "2,914,843 thousand cubic meters of BFG" input to the BF (stoves). | 686 | **690** | upper (internal use) | default |
| n2_rec_cog | 56 | 30 Nm³/tHM | Tikadar p.6: "28,308 thousand cubic meter of COG". | 6.7 | **30** (keep; upper) | upper | default |
| n2_trt_whr | 57 | 35 kWh/tHM | MoS Table 5.6, p.108: TRT "50 kWh/t-pig iron" where installed. Tikadar p.8 (citing a global study): "TRTs can generate around 40 to 60 kWh". Indian coverage is unsourced. | 50 × coverage | **35** (keep) | lower | default |

## E. BOF

| Parameter | Line | Current | Sources | In model units | Proposed | Pessimistic | Flag |
|---|---|---|---|---|---|---|---|
| n3_e_bof | 70 | 174 kWh/tCS | MoS 2024 Table 6.2, p.122: "BOF 54.49 [Mt] 174.09 [kWh/t]" (FY2021-22, steelmaking stage only; finishing is a separate 120 kWh/t). Transition Asia & TERI 2026 workbook `Params_BOF`: "E_BOF 130 kWh/tls". | 174; 130 | **174** (keep) | upper | default |
| n3_metallic_bof | 71 | 1.1 | Tikadar p.6–7: 4.25 Mt HM, of which 0.10 Mt pig iron is sold, for 3.83 Mt crude steel (scrap not reported). TA/TERI workbook: 1.0475 t HM/tls at zero scrap. | ≥ 1.08 (HM only) | **1.1** (keep) | upper | default |
| n3_ls_bof | 72 | 0.075 t/tCS | No admissible source found for limestone. TA/TERI workbook uses burnt lime at 0.031 t/tls; as limestone-equivalent CO₂ that is about 0.025 t. | — | keep | upper | default |
| n3_sl_bof | 73 | 0.10 t/tCS | IBM IMYB 2019, p.19: "in steel making 150 to 200 kg per tonne of slag is generated per tonne of liquid steel". | 0.15–0.20 | **0.15** (lower bound; the current value is below the range) | lower (credit) | default |
| n3_bofg_bof | 74 | 100 Nm³/tCS | No admissible source found. Tata Steel IR 2024-25, p.247, gives "LD Gas recovery of 96,725 Nm3/hr" at Jamshedpur, but no matching output figure, so it cannot be converted. | — | keep | lower | default |
| n3_rec_cog | 75 | 65 Nm³/tCS | No admissible source found. | — | keep | upper | default |
| phi0_bof | 125 | 0.09 | MoS 2024, p.102: "scrap utilisation is limited to 10-12% in the BF-BOF route". | 0.10–0.12 | **0.10** (lower bound) | lower (more hot metal) | default |
| phi_max_bof | 132 | 0.20 | MoS p.102: "25-30% in the best operating BF-BOF plants globally". | 0.25–0.30 | **0.25** (lower bound; the current value sits below the evidence) | lower | default. It loosens a constraint, so check that it does not bind in results. |
| phi_min_bof | 128 | 0.05 | No admissible source found. This is a modelling assumption (tag A). | — | keep | — | default |

## F. Gas calorific values

| Parameter | Line | Current | Sources | In model units | Proposed | Pessimistic | Flag |
|---|---|---|---|---|---|---|---|
| ng_cog_cv | 12 | 0.018 GJ/Nm³ | MoS 2024, §10.9, p.240: "The gross calorific value (GCV) of COG is around 4200 Kcal/NM3". IPCC 2006 Vol 2 Table 1.2, p.1.18: 38.7 GJ/t (mass basis only). | 4,200 × 4.1868 kJ = **0.0176** (GCV) | **0.0176** | lower | default |
| ng_bfg_cv | 13 | 0.0033 GJ/Nm³ | No admissible India source found (BEE, CSE and EU BREF were unreachable). IPCC Table 1.2, p.1.18: BFG 2.47 GJ/t on a mass basis; converting needs a gas density, which no source here gives. | — | keep | — | default (counted as no source) |
| ng_bofg_cv | 14 | 0.008 GJ/Nm³ | No admissible India source found. IPCC Table 1.2: oxygen steel furnace gas 7.06 GJ/t (mass basis). | — | keep | — | default (counted as no source) |

Materiality: gas calorific values feed only the ST-05 waste-heat power pool, which converts about 0.2 % of the gas energy into power. Their effect on emissions and cost is close to nil until ST-05 is fixed.

## G. Emission factors (`s_emissions.mod`)

National inventory basis. **BUR-4** (MoEFCC 2024), Table 2.8 (PDF p.107), column "Electricity Power Generation (1A1ai), Iron & Steel (1A2a)":

- Coking coal: NCV 23.66 TJ/kt, CEF 25.55 tC/TJ.
- Non-coking coal: NCV 17.09 TJ/kt, CEF 26.39 tC/TJ.

**BUR-2** (MoEFCC 2018), Table 2.3, p.63, all sectors: non-coking coal 18.26 TJ/kt and 26.28 tC/TJ.

Conversion: tCO₂/t = NCV (GJ/t) × CEF (tC/TJ) × 44/12 / 1000. Oxidation factor 1, as in the IPCC 2006 defaults.

| Factor | Where | Current | Sources | Value (tCO₂/t) | Proposed | Pessimistic | Flag |
|---|---|---|---|---|---|---|---|
| Coking coal | s_emissions eq105 (0.1116 × 25) and eq110 (2.79) | 2.79 | (1) BUR-4 Table 2.8: 23.66 × 25.55 × 44/12. (2) IPCC 2006 Vol 2 Table 1.2, p.1.18: coking coal NCV "28.2"; Table 1.4, p.1.23: "94 600" kg/TJ (range 87,300–101,000). (3) IPCC Vol 3 Table 4.3, p.4.27: coking coal "0.73" kgC/kg. Context: Tikadar p.8, about 76 % of coking coal is imported. | (1) **2.217**; (2) **2.668**; (3) **2.677** | **2.67** | upper | **NEEDS CALL #1** |
| PCI coal | eq105 (0.106 × 26), eq110 (2.756) | 2.756 | (1) IPCC Table 1.2/1.4, other bituminous coal: 25.8 GJ/t × 94.6. (2) IPCC Table 4.3 "Coal 0.67" kgC/kg. (3) BUR-4 iron & steel non-coking coal 1.654 (domestic coal; Indian PCI coal is mostly imported). | 2.441 / 2.457 / 1.654 | **2.46** | upper | default |
| Non-coking coal (DRI, EAF carbon) | eq106–109 (0.110 × 24, 2.64) and eq110 | 2.64 | (1) BUR-4 iron & steel: 17.09 × 26.39 × 44/12. (2) BUR-2 national non-coking coal: 18.26 × 26.28 × 44/12. (3) IPCC sub-bituminous coal, global: 18.9 GJ/t × 96.1. Context: MoS Table 5.5, p.105, "GCV of Indian coal 3,000 – 4,000" kcal/kg (12.6–16.7 GJ/t). | **1.654 / 1.759** / 1.816 | **1.76** (India upper), paired with the DRI coal mass | upper | **NEEDS CALL #3** |
| Natural gas | eq107, eq110 (0.055 × 50) | 2.75 t/t | IPCC Table 1.2, p.1.18: NG NCV "48.0" GJ/t; Table 1.4, p.1.24: "56 100" kg/TJ. TA/TERI workbook uses the same 56.1 kgCO₂/GJ (LHV). | 2.693 | **2.69** | — | default |
| `ng_co2_gj` (CCS steam boiler) | definitions | 0.0521 t/GJ | IPCC Table 1.4, p.1.24: natural gas 56,100 kg/TJ. | 0.0561 | **0.0561**. The current value is 7 % low. | upper | default |
| Limestone | eq105–110 | 0.44 | IPCC Vol 3 Table 4.3, p.4.27: "Limestone 0.12" kgC/kg; "Dolomite 0.13". | 0.44; dolomite 0.477 | **0.44** (keep) | — | default |
| Electrodes | eq110 | 6.0 | (1) IPCC Table 4.3: "EAF Carbon Electrodes 0.82" kgC/kg. (2) TA/TERI workbook: "0.78 production (graphite) plus 3.67 oxidation" (the 0.78 is upstream, Scope 3). | 3.01 (IPCC); 3.67 (pure carbon) | **3.67** (upper Scope 1 bound) | upper | default |
| *new:* bought coke breeze (ST-04) | not in model | 0 | IPCC Table 4.3: "Coke 0.83" kgC/kg. | 3.04 | **3.04** on breeze bought beyond own output | upper | NEEDS CALL #5 |

## H. Parameters with no admissible source (18)

| Group | Parameters |
|---|---|
| Coke oven | n0_e_c, n0_br_c, n0_tar_c, n0_cog_c, n0_rec_cog, n0_rec_bfg |
| Sinter | n1_e_sint, n1_lime_sint, n1_ore_sint, n1_sintcool_whr |
| Pellets | ng_ore_pell |
| Blast furnace | n2_lime_hm |
| BOF | n3_ls_bof, n3_bofg_bof, n3_rec_cog, phi_min_bof (an assumption) |
| Gas calorific values | ng_bfg_cv, ng_bofg_cv |

Partly sourced: n0_cdq_whr and n2_trt_whr. The output per installed unit is sourced, but Indian coverage is not.

Unsourced sub-item: the fuel mix of Indian pellet induration.

Sources I tried but could not reach from this container:

- **BEE PAT documents:** the old URLs now redirect to the BEE home page.
- **SAIL Annual Report 2024-25:** the server sends an incomplete TLS certificate chain. A search snippet says coke rate 421 and CDI 113 kg/tHM, but I did not read the source, so neither figure is used.
- **Blocked or refused:** CSE Green Rating, the EU BREF, Springer (Singh et al. 2026) and ScienceDirect (Bhardwaj et al. 2025).
- **Rejected download:** the worldsteel CO₂ user guide.

Adding them later would chiefly fill the gas-calorific and sinter rows.

---

## I. Calibration: 2.80 vs 2.54 tCO₂/tCS

Method: the 2025 hand calculation of `stage1_calib2025.py`, rerun with each change on its own. Script: scratchpad `bfbof_scripts/gap.py`. The 2025 route shares (ST-07) are unchanged.

| Change | Sector 2025 intensity | Δ |
|---|---|---|
| Current model | 2.797 | — |
| Coking coal 2.67 (IPCC) / 2.22 (BUR-4) | 2.749 / 2.569 | −0.05 / −0.23 |
| PCI coal 2.44 | 2.773 | −0.02 |
| Non-coking coal 1.76 / 1.65 | 2.528 / 2.496 | **−0.27 / −0.30** |
| Coke 0.47 + PCI 0.11 | 2.615 | **−0.18** |
| Pellet power 70 kWh/t only | 2.717 | −0.08 |
| Pellet induration +0.16 tCO₂/t only | 2.910 | +0.11 |
| Pellet power + induration together | 2.830 | +0.03 |
| phi0_bof 0.10 | 2.782 | −0.02 |
| Count bought breeze (0.09 / 0.05 t/t sinter) | 2.912 / 2.840 | +0.12 / +0.04 |
| Natural gas and electrode factors | about 2.79 | < 0.01 |
| **All BF-BOF proposals** (coking coal 2.67, non-coking coal unchanged) | **2.618** | −0.18 |
| All BF-BOF proposals + non-coking coal 1.76 | **2.349** | −0.45 |
| All BF-BOF proposals with BUR-4 coking coal | 2.461 | −0.34 |

The gap has three main causes:

- **The BF fuel rate** is above the Indian range.
- **The DRI-coal emission factor** implies 24 GJ/t, while Indian coal is 13–18 GJ/t.
- **The coking-coal factor** of 0.1116 tCO₂/GJ is 18 % above the IPCC value.

Pellet electricity at 200 kWh/t works the other way on Scope 2, but adding induration fuel offsets it.

At the route level (script `bfbof_scripts/route.py`), the model's BF-BOF route is 2.91 t/tCS today (Scope 1 2.65 + Scope 2 0.25). That is above the Ministry of Steel range of "BF – BOF 2.20 - 2.60" (Table 1.7, p.38). With the proposals it becomes 2.52 using IPCC coking coal, or 2.21 using BUR-4.

For comparison, Tata Steel Ltd reports 2.46 tCO₂/tcs for FY2024-25 (worldsteel method, with slag credit; IR p.58). Tikadar's case-study plant is 3.31, including 0.339 of fugitive emissions and the rolling mills.

If ST-07 (route shares) is fixed and non-coking coal goes to 1.76, the model can land below 2.54. The DRI group's coal-per-tonne value then decides where it ends up.

## J. Structural notes (not fixed here)

1. **Emission factors are hard-coded twice.** Coking and PCI coal appear as `0.1116*25` / `0.106*26` in eq105 and as `2.79` / `2.756` in eq110. Non-coking coal appears as `0.110*24` in eq106–108 and as `2.64` in eq109–110. Turn them into named parameters, so that one edit changes every equation.
2. **Tar carbon counts as emitted.** Applying the coking-coal factor to all coal input counts the carbon in sold tar (0.04 t/t coke × 0.62 kgC/kg, IPCC Table 4.3) as CO₂. That overstates emissions by about 0.09 tCO₂/t coke, or 0.04 t/tHM. Minor; it is offset by uncounting bought breeze (ST-04).
3. **"Lime" versus limestone.** The lime flows (`n1_lime_sint`, `n2_lime_hm`, `n3_ls_bof`) take the limestone calcination factor of 0.44. If the flux is burnt lime, as BOF practice uses, the CO₂ is released at the calcining plant and the 0.44 must apply to the limestone fed to that plant. State the basis in each comment.
4. **Pellet ore (ST-02) and induration fuel (ST-03) confirmed.** Induration needs a fuel flow and an emission term in all four pellet modules, plus a cost.
5. **Gas calorific values have almost no effect until ST-05 is fixed.** BFG, COG and BOFG surplus enters only the 0.3 × `n9_whr` × `n9_eta` pool.
6. **`n1_bio_sint_50` exceeds its own ceiling.** At 0.022 / (0.058 + 0.022) it is 27.5 % of sinter fuel, above both the 20 % comment in `definitions.mod` and the Ministry of Steel range of 20–25 %.
7. **Slag credit direction.** Because `ng_credit_slag` is a revenue, the pessimistic rule keeps BF slag at the low end (0.30). If slag stops being credited, use about 0.40 (the middle of IBM's 0.30–0.54).

---

## Bibliography

- Ministry of Steel (2024). *Greening the Steel Sector in India: Roadmap and Action Plan.* Government of India. https://steel.gov.in. Printed pages are cited; PDF page = printed page + 14. Local text: `scratchpad/src_capex/mos_gsi.txt`.
- Tikadar, B. et al. (2025). Process-level emission analysis and decarbonization pathway for BF-BOF route in Indian iron and steel industry. *J. Environ. Manage.* 373, 123483. doi:10.1016/j.jenvman.2024.123483. Author copy: https://acpet.ashoka.edu.in/wp-content/uploads/2025/12/Process_level-emission_analysis.pdf
- MoEFCC (2024). *India: Fourth Biennial Update Report to the UNFCCC* (BUR-4), Tables 2.6 and 2.8. Mirror: https://cdn.climatepolicyradar.org/navigator/IND/2024/india-biennial-update-report-bur4_530214efdfdb86a675d77a4daf4aee9c.pdf (original: https://unfccc.int/documents/645149)
- MoEFCC (2018). *India: Second Biennial Update Report to the UNFCCC*, Table 2.3, p.63. https://moef.gov.in/uploads/2019/10/BUR-Report-Final-2019-1.pdf
- MoEFCC (2024). *India First Biennial Transparency Report* (BTR-1). Checked; it carries no coal factor tables. https://cdn.climatepolicyradar.org/navigator/IND/2026/india-biennial-transparency-report-btr1_05fd5b2a6bbb71148dd1a064bfc891b1.pdf
- IPCC (2006). *2006 IPCC Guidelines for National GHG Inventories*, Vol. 2 Ch. 1, Tables 1.2 and 1.4. https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_1_Ch1_Introduction.pdf
- IPCC (2006). Vol. 3 Ch. 4, *Metal Industry Emissions*, Tables 4.1 and 4.3, pp.4.25–4.27. https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/3_Volume3/V3_4_Ch4_Metal_Industry.pdf
- Indian Bureau of Mines (2021). *Indian Minerals Yearbook 2019*, Part II, Iron, Steel & Scrap and Slag, p.19. https://ibm.gov.in/writereaddata/files/10082021115122IronSteel_Scrap%20and%20Slag_2019.pdf
- KIOCL Ltd (2025). *49th Annual Report 2024-25*, energy annexure, p.78 (company). https://www.bseindia.com/xml-data/corpfiling/AttachHis/b4adaf9c-8e7b-4b1c-907f-30a198406837.pdf
- KIOCL Ltd (2024). *Annual Report 2023-24*, Performance at a Glance, p.24 (company). https://nsearchives.nseindia.com/annual_reports/AR_25810_KIOCL_2023_2024_0509202415371.pdf
- Tata Steel (2025). *Integrated Report & Annual Accounts 2024-25*, pp.58, 168, 247 (company). https://www.tatasteel.com/media/23971/ir-fy2024-25.pdf
- IEA (2020). *Iron and Steel Technology Roadmap*, p.27. https://www.iea.org/reports/iron-and-steel-technology-roadmap
- Transition Asia & TERI (2026). *Is Green Steel Within Reach in India?*, model input workbook `india/data/Model_input_India.xlsx` (sheets `Emission_Factor`, `Params_BOF`). Local copy: `scratchpad/src_capex/ta_model`.
