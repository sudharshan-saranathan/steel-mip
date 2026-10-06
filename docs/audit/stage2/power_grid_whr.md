# Stage 2 — Electricity, grid emission factor, captive power and waste-heat recovery

Status: **IN PROGRESS** (skeleton written first so work survives a container loss).

Files audited: `core/definitions.mod`, `core/modules/o_waste_heat.mod` (target repo @ b33b88a). Register refs: ST-05, ST-06, §3.4. Page numbers for the Ministry of Steel roadmap are PDF page numbers (printed page = PDF page − 14).

## Needs your call
IN PROGRESS

## A. Grid emission factor (n9_grid_ef_start, θ_grid trajectory) — DONE

What the model does: one emission factor (EF) for all *net purchased* electricity (`grid_power_in` = process demand − CDQ − TRT − sinter-cooler − pool WHR), all routes. Comment at `definitions.mod:167`: 0.886 = 36 % grid at 0.757 + 64 % captive (CPP) at 0.96. Check: 0.36 × 0.757 + 0.64 × 0.96 = 0.887. The 0.757 is CEA's **combined margin** for FY2023-24 (v20/v22, incl. imports), not the weighted average; for attributional Scope 2 the **weighted average** is the standard CEA figure. The 36/64 split matches the Ministry of Steel (MoS) sector split of net (post-WHR) power, 37.3 % grid / 62.7 % CPP (FY2021-22).

Evidence (2025 start):

| Quantity | Source (short) | Quote / table, page | Value | Year |
|---|---|---|---|---|
| Grid weighted average (WA), incl. RE, incl. imports | CEA CO₂ Baseline Database v22.0 User Guide, Table S (p. 1) and App. C Table B (p. 28) | "Average 0.675 … OM 0.963 … BM 0.446 … CM 0.705" (FY2025-26); Table B WA "0.711 0.716 0.727 0.710 0.675" for FY22–FY26 | 0.675 (FY26), 0.710 (FY25) tCO₂/MWh | 2021-26 |
| Grid combined margin | same, Table B | CM "0.915 0.919 0.757 0.736 0.705" | 0.757 = model's grid value (FY24) | 2023-24 |
| Coal-station EF (proxy for coal CPP) | CEA v22.0, Table 5 (p. 14); v21.0 Table 5 | "Coal 0.971" (FY26); "Coal 0.969" (FY25) | 0.97 | 2024-26 |
| Steel-sector CPP EF | MoS (2024) *Greening the Steel Sector*, Table 6.4 (pdf p. 138) | "CPP CO2 factor (tCO2/MWh) 0.96"; note: "CO2 factor for coal plants (0.968 tCO2/MWh) as per CEA" | 0.96 | 2021-22 |
| Steel-sector CPP fuel mix | MoS (2024) Table 6.3 (pdf p. 137), from CEA General Review 2023 | Coal "56,405" MU of "58,129" (97.03 %) | 97 % coal | 2021-22 |
| Steel-sector grid/CPP split (net of WHR) | MoS (2024) §6.6, pdf p. 146 | "share of CPPs in the net electricity procurement (electricity procurement other than from WHR) is 62.7% … share of the grid … 37.3%" | 63/37 | 2021-22 |
| Split by segment | MoS (2024) Table 6.4 note (pdf p. 138) | "major players meet 85% of their net electricity requirement from captive sources … Other players meet 60% … from the grid" | ISPs 85/15; SSIs 40/60 | 2021-22 |
| Sector blended EF | MoS (2024) Table 6.4 row 14 (pdf p. 138) | "Overall CO2 factor (tCO2/MWh) 0.92 [majors] 0.78 [others] 0.85 [total]" (grid at 0.66) | 0.85 | 2021-22 |
| Old CPP heat rates | MoS (2024) §6.12.2(2), pdf p. 163 | "heat rate of new ultra supercritical plants is 2100 kCal/kWh while that of some of the old captive plants could be as high as 2800 to 3000 kCal/kWh" | context: old CPPs > 0.97 | 2024 |

Recomputed blend, same 36/64 boundary, CEA WA instead of CM: FY2024-25: 0.36 × 0.710 + 0.64 × 0.969 = **0.876**; FY2025-26: 0.36 × 0.675 + 0.64 × 0.971 = 0.864. MoS (FY22): 0.85. Segment blends (FY25 values): ISP 0.85 × 0.969 + 0.15 × 0.710 = **0.93**; SSI 0.40 × 0.969 + 0.60 × 0.710 = **0.81**.

Evidence (2050 trajectory; grid only, not CPP):

| Source | Quote / table, page | 2050 grid EF | Reduction vs ~0.71 |
|---|---|---|---|
| CEA (2023) *National Electricity Plan* Vol. I, Exhibit 10.4 (pdf p. 266) | "average emission factor is expected to reduce to 0.548 kg CO2/kWhnet in the year 2026-27 and to 0.430 kg CO2/kWhnet by the end of 2031-32" | (2031-32: 0.43) | −40 % by 2032. Note: actual FY26 is 0.675 vs. 0.548 projected for FY27, so NEP runs ahead of reality |
| TERI (2024) *India's Electricity Transition Pathways to 2050*, Table 16 (p. 53) | "Grid Emission factor kgCO2/kWh 0.71 … CRES … 0.22 … URES … 0.07 … NFS … 0.00" (2050) | 0.22 / 0.07 / 0.00 | −69 / −90 / −100 % |
| WRI India (Agarwal et al. 2024) EPS working paper, Fig. 11 & p. 15–16 | "even in 2050, India's grid carbon intensity (321 gCO2/kWh)" [REB]; Fig. 11: "0.32 REB, 0.14 NNP, 0.06 AP" tCO₂/MWh | 0.32 / 0.14 / 0.06 | −55 / −80 / −92 % |
| Transition Asia & TERI (2026) model input `Model_input_India.xlsx`, sheet Grid | "Emission intensity: Central Electricity Authority, CO2 Baseline Database (2025 weighted average) and the CEA projection of 0.477 kgCO2/kWh for 2030 … after 2030 an assumed decline to half the 2030 level by 2040 and a quarter by 2050"; 2025 row "0.000719", 2050 row "0.000119" tCO₂/kWh | 0.119 | −83 % |
| MoS (2024) Table ES2 (pdf p. 22) — 2030 grid & CPP | "Grid CO2 factor 0.46 tCO2/MWh"; "CPP CO2 factor 0.96 [BAU] 0.77 [20% RE] 0.68 [30%] 0.55 [43.33%]"; "Overall CO2 factor 0.78 [BAU] … 0.52" | (2030 blend 0.78 BAU) | blend −8 % by 2030 in BAU |

Median of the seven 2050 grid-only values = 0.119 tCO₂/MWh (−83 %); the least optimistic is 0.32 (−55 %, WRI REB). The key point: these are **grid** trajectories. The model's θ_grid scales the **blend**, of which 64 % is coal CPP that decarbonises only if steel firms replace it (MoS Table ES2 BAU keeps CPPs at 0.96 through 2030). Example: grid −80 % with CPPs unchanged gives 0.36 × 0.14 + 0.64 × 0.97 = 0.67, i.e. the blend falls only ~24 % — about θ_grid = 0.25.

| Parameter | file:line | Current | Sources | Value in model units | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| n9_grid_ef_start | definitions.mod:167 | 0.000886 t/kWh | CEA v21/v22 WA and coal EF; MoS Table 6.4 split (above) | 0.000864–0.000876 (blend, CEA WA); 0.00085 (MoS FY22) | **0.000880** (FY2024-25 blend, rounded up; replace the CM-based 0.757 in the comment by WA 0.710) | higher | default |
| n9_grid_ef_end (θ_grid levels 0.25/0.5/0.75) | definitions.mod:168–171; study files | start × (1 − θ) | NEP 2023; TERI 2024; WRI 2024; MoS ES2 | grid-only 2050 reductions 55–100 % (median 83 %); blend reduction depends on CPP retirement | Keep the 0.25/0.5/0.75 grid levels, but state in the paper that θ applies to the grid+CPP blend; θ = 0.25 ≈ "grid decarbonises, CPPs stay coal". Better: split into grid and CPP (see §E) | lower θ | **NEEDS CALL** |

## B. Grid tariff (grid_price_start, grid_price_end_fast, ng_credit_power) — DONE

Note: `prices.md` §F also covers the grid tariff; the evidence below should be reconciled with it.

The tariff applies to the same net purchased electricity as the EF, so the matching price is the **grid + CPP blend**, not the DISCOM tariff alone.

| Quantity | Source (short) | Quote / table, page | INR (yr) | 2025 USD/kWh |
|---|---|---|---|---|
| DISCOM HT tariff, steel states, highest voltage, 50 MW 60 % LF, incl. duty | CEA (2025) *Electricity Tariff & Duty and Average Rates of Electricity Supply in India*, Table 7(h) (pdf p. 231) and Table 8(a) "Power intensive industries" (pdf p. 232) | e.g. "Odisha (AT 132 KV) … 643 46 690"; "Jharkhand (AT 132 KV) 756 103 859"; "Maharashtra … 1135 104 1239"; "Gujarat (AT 132 KV) 549 82 632"; "Chhattisgarh (AT 132 KV) 773 54 837" [Table 8(a)] | 10 steel states/utilities (OR 6.90, JH 8.59, DVC 6.26, CG 8.37, KA 8.33, MH 12.39, GJ 6.32, WB 8.88, AP 7.35, TN 9.18): **median ₹8.35**, range 6.26–12.39 (FY2024-25) | **0.096** (0.072–0.143) |
| DISCOM tariff, 8 steel states | MoS (2024) Table 6.15 row 8 (pdf p. 152) | "DISCOM tariff 6.26 6.15 7.18 7.67 7.97 5.36 7.52 6.69" (OR JH CG KA MH GJ WB AP) | median ₹6.94 (≈2023) | 0.082 |
| Cost of new thermal captive | MoS (2024) Table 6.17 row 1 (pdf p. 155) | "Total cost of thermal captive (INR /kWh) 6.00" ("Landed cost of coal = INR 4000/ton") | ₹6.00 (≈2023) | 0.071 |
| Variable cost of existing captive | MoS (2024) §6.10, pdf p. 140 | "variable cost of thermal-based captive units is in the range of INR 2.5 - 3/kWh" | ₹2.5–3.0 | 0.029–0.035 |
| ISP blend (85 % captive, 15 % grid) | MoS (2024) Table 6.17 row 3 (pdf p. 155) | "Weighted average cost of non-RE power (85% captive and 15% grid) 6.04 6.02 6.18 6.25 6.30 5.90 6.23 6.10" | median ₹6.14 | **0.072** |
| SSI blend (60 % grid, 40 % captive) | MoS (2024) Table 6.18 row 3 (pdf p. 155–156) | "6.16 6.09 6.71 7.00 7.18 5.62 6.91 6.41" | median ₹6.56 | **0.077** |
| Grid electricity for EAF (modelling assumption) | Domínguez Bennett et al. (2026) UC Berkeley IECC, Fig. 5 caption (pdf p. 16) | "grid electricity cost of $60/MWh for EAF"; sensitivity "[40-100 US$/MWh]" | — | 0.060 (nominal ≈ 2025) |
| RE captive open access incl. banking (8 states) | MoS (2024) Table 6.17 row 4 (pdf p. 155) | "RE captive OA including banking (INR /kWh) 7.91 4.00 2.90 2.82 4.36 4.86 6.66 5.31" | median ₹4.61 | **0.054** (0.033–0.093) |
| Intrastate captive RE OA (no banking) | MoS (2024) Table 6.16 row 4 (pdf p. 153) | "Captive RE OA 5.45 3.85 2.88 2.76 4.33 4.07 4.63 5.23" | median ₹4.20 | 0.049 |
| HT industrial tariff trajectory, Andhra Pradesh | Transition Asia & TERI (2026) model input, sheet Grid | "Price: APERC retail tariff for high-tension industrial consumers, real 2025 USD"; 2025 "0.0717", 2030 "0.0745", 2050 "0.0765" $/kWh | — | 0.072 → 0.077 (real tariff *rises* slightly) |
| Firm solar+storage block | IECC (2026) pdf p. 13 | "yielding sub‑60 USD/MWh today in India" | — | < 0.060 |
| Åhman & Arens (2024) *Utilities Policy* 91:101853 (cited by the model) | could not be opened (ScienceDirect blocked by the proxy; CC-BY but no repository copy) | — | — | not used |

Conversion: `convert_2025usd.py` `inr(v, year)` (WPI 2023 = 151.3, 2024 = 154.0, 2025 = 154.95; ₹87.16/$). MoS tables taken as 2023 rupees (report published 2024).

| Parameter | file:line | Current | Sources | Value in model units | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| grid_price_start | definitions.mod:148 | 0.07 $/kWh | CEA tariff book FY25; MoS Tables 6.15–6.18; IECC | blend: ISP 0.072, SSI 0.077; grid-only 0.082–0.096; new captive 0.071 | **0.08** (0.64 × new-captive 0.071 + 0.36 × grid median 0.096 = 0.080; upper end of the blends) — or keep 0.072 (MoS ISP blend) | higher | **NEEDS CALL** |
| grid_price_end_fast | definitions.mod:149 | 0.055 $/kWh (2050, θ = 1) | MoS Table 6.17 row 4 (RE OA + banking, median 0.054); MoS Table 6.16 (0.049); IECC (< 0.060; 0.060 grid for EAF); TA & TERI 2050 grid tariff 0.077 (a no-fall case) | 0.049–0.077 | **0.06** for θ = 1 (the clean-power end: median of the RE-based values is 0.054, rounded up because they exclude 24×7 firming). Note that the TA & TERI grid tariff rises in real terms, so θ = 0 (flat) is not the pessimistic bound | higher | default |
| ng_credit_power | definitions.mod:182 | 0.03 $/kWh | MoS: existing-captive variable cost ₹2.5–3/kWh (0.029–0.035) is the nearest avoided-cost analogue | — | No change; parameter is **unused** in `core` (declared, never referenced). Delete or document | — | default |
## C. Process-gas power / WHR pool (n9_eta, n9_whr, 0.3 factor, whr_steam_eff, n9_whr_capex/opex) — DONE

**What the model does (2025, script `scratchpad/scripts_power/gaspool.py`).** Per tonne of hot metal (tHM), with the model's coefficients: gross off-gas 9.96 GJ (COG 4.20, BFG 4.95, BOFG 0.81), internal uses (coke-oven and BF-stove heating, COG to BF and BOF) 5.66 GJ, surplus **4.30 GJ/tHM** (4.26 GJ/tCS at 0.99 tHM/tCS). Power = surplus × 0.3 × `n9_whr` (0.05) × `n9_eta` (0.15) × 277.78 = **2.7 kWh/tHM**. The same surplus at a real power-plant efficiency of 0.30 with no other haircut would give 358 kWh/tHM.

**What Indian plants actually do.**

| Quantity | Source | Quote / table, page | Value |
|---|---|---|---|
| Sector power from WHR and off-gas | MoS (2024) Table 6.4 row 2 and Table 6.10 (pdf p. 138, 146) | "Power Generated from WHR (MU) 11,266 [major players] 5,315 [others] 16,581 [total]"; p. 137: "off-gas from various processes like – coke dry quenching, blast furnace gas, and coke oven gas, which has heat content and is fired in the boiler to generate power" | 16.6 TWh, 17.6 % of the 94.3 TWh requirement (FY2021-22) |
| Same, per tonne of hot metal (top-down) | MoS (2024) Table 6.2 (pdf p. 136): "Hot Metal & Pig Iron 84.49" Mt | majors' WHR ÷ all hot metal = 11,266 GWh ÷ 84.49 Mt | **≈ 133 kWh/tHM** (all in-plant generation: CDQ + TRT + sinter + off-gas). Rough: majors also run DRI kilns, and some hot metal is made by smaller units |
| 2030 projection | MoS (2024) Table 6.10 (pdf p. 146) | "Power Generated from WHR (MU) … 26,645 [majors] 11,506 [others] 38,151" (2030-31) | majors' WHR share of their requirement 22 % → 26 % |
| JSW Steel (company) | JSW Steel *Climate Action Report 2024*, pdf p. 42 | "Within our captive power plants (where we have capacity to generate over 1,000 megawatts (MW)), almost half of this generation comes from waste gases and heat generated from our steelmaking operations" | ~50 % of captive generation (best-practice plant) |
| JSW, flaring avoided | same, pdf p. 32 | "Power generated by using off-gases from the process that would otherwise have been flared" | qualitative |
| Indian plant BFG export | Tikadar, Swami & Chowdhary (2025) *J. Environ. Manage.* 373:123483, pdf p. 7 | BF produces "7,428,352 thousand cubic meters of BFG" for "4.25 million tons of hot metal"; plant "exports BFG (2,363,692 thousand cubic meters)" | 1,748 Nm³ BFG/tHM; 32 % of BFG leaves the plant (not available to its own CPP) |
| Untapped off-gas in India (2010) | Morrow, Hasanbeigi, Sathaye & Xu (2013) LBNL-6338E, Table 1 (pdf p. 16–19; row 25 on p. 19) | "Cogeneration for the use of untapped coke oven gas, blast furnace gas, and basic oxygen furnace‐gas in integrated steel mills … 97.22 [kWh/tcs] … 20.20 [2010 US$/tcs capex] … 0.00 [O&M] … 50%" | 97 kWh/tCS still untapped on 50 % of capacity in 2010 |
| BOF gas recovery, 7 major Indian ISPs | JISF (2022) *India TCL part 1 BF-BOF v5.0*, list p. 2 (pdf p. 8); reproduced in MoS (2024) Fig. 5.4 (pdf p. 125) | "Converter Gas Recovery Device … 88 [*2]"; "*2) Diffusion rate of OG boiler is Zero" | 88 % recovered (2016) |
| Off-gas use split (global, STEPS 2050) | IEA (2020) *Iron and Steel Technology Roadmap*, p. 72–73 | "with around 250 Mtoe of off-gases being generated in 2050. About 60% of these off-gases are used to fulfil on-site heat requirements … and the remainder is used to produced power"; off-gases "around 6 GJ per tonne of crude steel" (p. 37) | global projection: ~40 % of off-gas to power |
| Power-plant efficiency on steel-mill gas (global) | Collis et al. (2021) *Front. Energy Res.* 9:642162, p. 7 | "The power plants in steel mills have efficiencies that vary from 0.3 to 0.5 … An efficiency of 0.36 is commonly used in literature" | 0.30–0.50 (0.36 typical) |
| Indian captive plant heat rate | MoS (2024) §6.12.2(2), pdf p. 163 | "heat rate of new ultra supercritical plants is 2100 kCal/kWh while that of some of the old captive plants could be as high as 2800 to 3000 kCal/kWh" | η = 860/HR = 0.41 (new), **0.29–0.31** (old captive) |
| Flaring (EU, global fallback) | Collis et al. (2021), p. 4 | "the amount of flared gas ranges from 0.1 to 22 vol%, averaging around 2 vol%" | EU 2 %; no Indian plant-level flaring rate found in an admissible source |

**Reading.** India's in-plant generation is ~130 kWh/tHM in total. The model's unit WHR at full penetration (CDQ 80 × 0.53 + TRT 35 + sinter 30 × 1.15 = **112 kWh/tHM**) already supplies most of this, which is why the near-zero pool power (ST-05) does not show up as a large calibration error. With the penetration-weighted unit WHR from §D (**40 kWh/tHM**), the pool must supply ≈ 133 − 40 = 93 kWh/tHM. At η_cpp = 0.30 this needs 93 / 358 = **0.26** of the model's surplus, close to the hard-coded 0.3. The rest is in reality burnt in reheating furnaces and other utilities outside the model boundary (crude steel), exported (Tikadar: 32 % of BFG), or flared.

| Parameter | file:line | Current | Sources | Value in model units | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| n9_eta | definitions.mod:164 | 0.15 | MoS heat rates (0.29–0.41); Collis 2021 (0.30–0.50, typ. 0.36) | 0.29–0.50 | **0.30** (lower bound; old Indian CPPs) | lower | default (with the ST-05 fix) |
| 0.3 pool factor | o_waste_heat.mod:26 | 0.3 (hard-coded) | MoS Table 6.4 (≈133 kWh/tHM total) minus §D unit WHR, ÷ 358 kWh/tHM | 0.26 in 2025 | Make it a parameter `f_gas_pow[t]`: **0.26 in 2025**; 2050 value see Needs-call #3 | lower | **NEEDS CALL** |
| n9_whr | definitions.mod:165–166 | 0.05 → 0.30 | none (no source for a 5 % penetration of off-gas power: MoS shows 18 % of sector electricity already comes from WHR/off-gas) | — | Drop as a multiplier on the power pool (fold into `f_gas_pow[t]`). If kept for CCS-steam access only, set 1 | — | default |
| whr_steam_eff | definitions.mod:331 | 0.85 | no admissible source found (BEE boiler guide not reachable) | — | keep 0.85 as an assumption (tag A) | lower | default |
| n9_whr_capex | definitions.mod:209 | 0.009 $/kWh | LBNL (2013) cogeneration on untapped gas: 20.20 US$₂₀₁₀/tCS for 97.22 kWh/tCS → 29.0 US$₂₀₂₅/tCS; × CRF(6 %, 25 y) 0.0782 → **0.023 $/kWh** (0.033 at 10 %). JISF (2022) CDQ: ¥3,000 M "【177 Crore】" equipment + ¥500 M "【30 Crore】" construction for "annual coke production : 450000 t" at "150kWh/t-coke" → ₹207 Cr / 67.5 GWh/yr → **0.028 $/kWh** at 6 % | 0.023–0.028 | **0.03** (upper bound, rounded) | higher | default |
| n9_whr_opex | definitions.mod:210 | 0.003 $/kWh | LBNL (2013) Table 1: cogeneration "Change in Annual O&M cost … 0.00" | 0–0.003 | keep **0.003** | higher | default |

Conversions: `usd(20.20, 2010)` = 29.0; `inr(207e7, 2022)` / (450,000 × 150 kWh) = 0.36 $ per annual kWh; CRF at the model's `real_discount_rate` 0.06 and a 25-year life (assumed).

## D. Unit WHR (CDQ, TRT, sinter cooler) — DONE

These are applied in the model to **all** coke, hot metal and sinter (100 % penetration from 2025), at no capex.

| Quantity | Source | Quote / page | Value |
|---|---|---|---|
| CDQ power | JISF (2022) TCL, sheet A-4 (pdf p. 13); same in MoS (2024) Table 5.6 (pdf p. 122) | "Electricity Savings 150kWh/t-coke : electric usage(300KWh/t-steam)( 500kg-steam/t-coke)[NEDO]" | 150 kWh/t coke |
| CDQ heat | LBNL (2013) Table 1 | "Coke dry quenching (CDQ) … 1.41 [GJ/tcs fuel saving] … 85.18 [capex] … 70% [applicable]" | 1.41 GJ/tCS |
| TRT | JISF (2022) sheet A-6 (pdf p. 15); MoS Table 5.6 | "Electricity Savings 50 kWh/t-PI (= (40+60)/2 kWh/t-PI) [SOACT]" | 50 (40–60) kWh/tHM |
| TRT | LBNL (2013) Table 1 | "Top‐pressure recovery turbines (TRT) … 46.00 [kWh/tcs] … 75%" | 46 kWh/tCS |
| Sinter cooler power | JISF (2022) list A-2 (pdf p. 8) | "Sinter Plant Heat Recovery (Power Generation from Sinter Cooler Waste Heat) … 22.1 [kWh/t] … 8 [%]" | 22.1 kWh/t sinter |
| Sinter cooler steam | JISF (2022) A-1; MoS Table 5.6 | "0.25 [GJ/t] … 23 [%]" | 0.25 GJ/t sinter (steam, not power) |
| Diffusion, 7 major Indian ISPs | JISF (2022) list (pdf p. 8, footnote "*1) Diffusion rate is calculated from the answer for questionnaire of 7 major steel companies in 2016"); MoS (2024) Fig. 5.4 (pdf p. 125): "there is no available information about the status of the adoption of BATs in ISPs and SSI" beyond this | CDQ **22 %**, TRT **42 %**, sinter-cooler power **8 %**, sinter steam 23 %, converter gas recovery 88 % | 2016 |
| Diffusion 2010 (cross-check) | LBNL (2013) Table 1 ("share of production … to which measure is applicable") | CDQ 70 %, TRT 75 %, sinter cooler 90 % still applicable | adoption ≤ 30 % / 25 % / 10 % in 2010 |
| Policy | MoS (2024) §5.8 (pdf p. 127) | "The BATs recommended for mandatory implementation are i) Stamp charging, ii) Sinter waste heat recovery, iii) CDQ, iv) TRT, and v) PCI" | basis for 100 % in new builds |

| Parameter | file:line | Current | Sources | Value in model units (2025 fleet = unit × diffusion) | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| n0_cdq_whr | definitions.mod:28 | 80 kWh/t coke | JISF/MoS 150; diffusion 22 % | 150 × 0.22 = 33 | **33 in 2025**, rising to 150 for new coke ovens (or by 2050) | lower | **NEEDS CALL** (with #3) |
| n2_trt_whr | definitions.mod:57 | 35 kWh/tHM | JISF 50 (40–60); LBNL 46; diffusion 42 % | 50 × 0.42 = 21 (40 × 0.42 = 17 at the low end) | **21 in 2025**, rising to 40 (lower bound of 40–60) for new BFs | lower | default |
| n1_sintcool_whr | definitions.mod:42 | 30 kWh/t sinter | JISF 22.1; diffusion 8 % | 22.1 × 0.08 = 1.8 | **2 in 2025**, rising to 22 for new sinter plants | lower | default |

Net effect in 2025: unit WHR falls from 112 to 40 kWh/tHM; with the pool fix (§C) total in-plant generation is ≈ 133 kWh/tHM (MoS) instead of ≈ 115 now.
## E. Structural notes (ST-05 fix, ST-06 boundary) — IN PROGRESS
## Bibliography — IN PROGRESS
