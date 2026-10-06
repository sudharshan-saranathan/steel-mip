# Stage 2 — Green hydrogen supply chain (ST-12, register §3.7)

Status: IN PROGRESS (sections A–C done; D, E, structural notes, call list in progress).

Model: `core/definitions.mod` @ b33b88a, lines 6, 98, 146–158, 344–414. Real discount rate in the model is 6 % (`real_discount_rate`, line 6); every LCOH figure below that is computed by me uses the model's own formula (replicated in `scratchpad/h2_scripts/lcoh.py`) at 6 % unless stated.
Conversions: `convert_2025usd.py` (US GDP deflator factors to 2025: 2020 ×1.2233, 2022 ×1.0921, 2023 ×1.0526, 2024 ×1.0263; INR 2025 values ÷ ₹87.16/$).
Units in the model: electrolyser capacity is in t H₂/yr **of actual output** (it runs at `re_cf`), so a $/kW figure becomes $/(t/yr) by dividing by `8760·re_cf/h2_kwh_per_t` (t H₂ per kW-yr).

## Needs your call

IN PROGRESS

## A. Electrolyser: capex, fixed O&M, life

| Parameter | file:line | Current | Sources (short cite, quote, page) | Value in model units (2025 USD) | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| `h2elec_capex_start` | definitions.mod:348 | 850 $/kW (2025) | (1) Transition Asia & TERI (2026) workbook, sheet Tech, row Electrolyser: CAPEX_2025 "672", CAPEX_2030 "525" USD/kW, "anonymised project data from Andhra Pradesh (Rs 56,000/kW at Rs 83.3 per USD)" — real 2025 USD, alkaline system installed. (2) IECC (2026) Fig. 4 caption p. 12: "alkaline electrolyzer capex of $550/kW" [range 250–1000], "Costs are in 2025 US$" — this is their 2030 base case (Table S-2 p. 31: 0.55 MUS$/MW 2030, 0.35 in 2035). (3) IEA GHR 2025, Fig. 3.10 notes p. 99: "For China, electrolyser CAPEX is USD 900/kW in 2024 … for the rest of the world, it is USD 2 300/kW in 2024 … includes the electrolyser system, balance of plant, engineering, procurement and construction (EPC) and contingencies". (4) NITI Aayog & RMI (2022) *Harnessing Green Hydrogen*, Exhibit 10 note p. 29: "electrolzyer capex price: $500 - 969/kW". (5) Context, not used: IEEFA (2024) p. 16: system "excluding installation costs averages Rs30,000/kW (US$366/kW) for Alkaline" (equipment only). | 672; 550; 924 (China, ×1.0263); 2,360 (RoW); 802 (NITI mid 734.5 ×1.0921) | **800 $/kW** (median of 550, 672, 802, 924, 2,360) | upper | default |
| `fopex_h2elec` | definitions.mod:355 | 400 $/(t/yr)/yr ("placeholder ~3% of capex") | (1) IEA GHR 2025 Assumptions annex p. 6, water electrolysis: "Annual OPEX % of CAPEX 3.0%" (2024 and 2030). (2) TA–TERI workbook Tech/Electrolyser `om_to_capex` = 0.03. (3) IECC (2026) Table S-2 p. 31: "OPEX Electrolyzer (inc. stack replacement) % of CAPEX 3.5%" plus "OPEX Electrolyzer 2%" (= 5.5 %). | 3 %, 3 %, 5.5 % of capex per year | **3 % of `h2elec_capex_kw[t]` per year** = 25.5 $/kW-yr now → 457 $/(t/yr)/yr at current 850/0.35/55; 581 at proposed 800/0.25/53 | upper | default (and see structural note S3: make it follow capex) |
| `life_h2elec` | definitions.mod:353 | 15 yr ("incl stack replacement") | (1) TA–TERI Tech/Electrolyser `economic_life_yr` = 10. (2) IECC (2026) p. 30: "plant life of 25 years, stack replacement every 10 years" (stack cost carried in the 3.5 % OPEX). (3) IEA GHR 2025 annex p. 6: "Stack lifetime (operating hours) 50000"; "can reach up to 95000 hr". At the model's utilisation 50,000 h = 16.3 yr (cf 0.35) or 22.8 yr (cf 0.25). | 10; 25; ~16–23 | **15 (keep)** — at the median (16) rounded down; no separate stack charge is needed because 15 yr × 8760 × 0.35 ≈ 46,000 h < 50,000 h stack life | lower | default |
| `h2elec_capex_end_slow` | definitions.mod:155 | 850 $/kW in 2050 (= 2025, i.e. no learning) | No source projects flat electrolyser capex to 2050. Sourced slow case: IRENA (2020) *Green Hydrogen Cost Reduction*, Fig. ES2 note p. 11: "Electrolyser costs reach USD 130-307/kW as a result of 1-5 TW of capacity deployed by 2050" (2020 USD). IEA GHR 2025 p. 108: in STEPS the non-China capital cost "declines by around 30% by 2030". | 376 (IRENA 307 @1 TW ×1.2233) | see Needs-your-call #3 (376, or keep 850 as an explicit "no-learning" bound) | upper | NEEDS CALL (#3) |
| `h2elec_capex_end_fast` | definitions.mod:156 | 100.31 $/kW ("scaled ×0.6688 off 150 DOE-optimistic") | IRENA (2020) p. 11 (as above): USD 130/kW at 5 TW by 2050; same report p. 66, alkaline/PEM system target "< USD 200/kW". NITI–RMI (2022) p. 31: aggressive case "Electrolyzer Capex ($/kW): 500(2020) , 125 (2030)". The DOE figure and the 0.6688 scaling are a back-solve to $1.50/kg, not a source. | 159 (IRENA 130 ×1.2233); 137 (NITI 125 ×1.0921) | **159 $/kW** (IRENA best case; pessimistic of the two) | upper | NEEDS CALL (#3) |

## B. Dedicated renewables: capex, capacity factor, O&M, life

The model calls this an "India solar/wind hybrid". I read that as a co-located portfolio, and evaluate costs and capacity factors for a 50/50 solar/wind mix by capacity (the mix that reproduces the current 800 $/kW). A different mix changes all three together; the mix is part of call #2.

| Parameter | file:line | Current | Sources | Value in model units | Proposed | Pessimistic | Flag |
|---|---|---|---|---|---|---|---|
| RE capex 2025 (hard-coded `800`) | definitions.mod:357 | 800 $/kW | (1) TA–TERI workbook, Tech: Solar "617.4" USD/kW ("Rs 49,800/kW at Rs 83.3 per USD"), Wind "1047.5" ("Rs 91,300/kW"), real 2025 USD. (2) IRENA (2025) *Renewable Power Generation Costs in 2024*, Table 3.1 p. 95: India utility PV weighted average 2024 "525" (2024 USD/kW); Table 2.1 p. 71: India onshore wind "1 110". (3) IEA WEO 2024 Table B.4a p. 333, India STEPS 2023: Solar PV "710", Wind onshore "1 210" (2023 USD). (4) MoS (2024) Table 6.21 p. 150: "Average capex requirement = INR 5.07 crore/MW" for "Average of solar and wind power". | 50/50: TA–TERI 832; IRENA 839; IEA 1,011; MoS 585 | **835 $/kW** (median); also make it a parameter (`re_capex_start`) | upper | default |
| `re_cf` | definitions.mod:345 | 0.35 (RE capacity factor **and** electrolyser utilisation) | (1) IEA WEO 2024 Table B.4a p. 333, India capacity factor 2023 / 2030 / 2050: solar "20 21 22", onshore wind "26 28 30" %. (2) IRENA RPGC 2024 Table 2.2 p. 76: India onshore wind weighted average "32" (2023), "39" (2024); p. 31: "Solar PV remained stable, at around 17%–19% in the United States and India". (3) TA–TERI workbook `data/renewable/` hourly profiles (single-axis PV and Anantapur wind, 2019): mean 0.208 (PV) and 0.281 (wind) — computed by me from their CSVs. (4) MoS (2024) Table 6.21 p. 150: "Average of solar and wind power CUF … considered Average CUF = 31%". (5) MNRE (2023) NGHM p. 23: "at least 5 MMT per annum, with an associated renewable energy capacity addition of about 125 GW" → 25 kW per t/yr → CF 0.251 at 55 kWh/kg (my derivation). (6) IECC (2026) Table S-1 p. 31: "Solar Capacity Factor (AC) 25%". | 50/50 mix: IEA 0.23; IRENA 0.285; TA–TERI 0.245; MoS 0.31; NGHM 0.25; IECC (solar) 0.25 | **0.25** (median). None of the six reaches 0.35. | lower | NEEDS CALL (#2) |
| `fopex_h2re` | definitions.mod:361 | 15 $/kW/yr ("placeholder ~2%") | (1) IEA WEO 2024 Table B.4a p. 333, India 2023 "Fuel, CO2, O&M (USD/MWh)": solar "5", wind "15" (→ 8.8 and 34.2 $/kW-yr at 20 % / 26 % CF). (2) TA–TERI Tech `om_to_capex`: solar 0.015, wind 0.025 (→ 9.3 and 26.2 $/kW-yr). Solar-only context: IRENA RPGC 2024 fn 34 p. 100: "USD 10.95/kW per year for non-OECD countries"; IECC Table S-1: "OPEX (PV and BESS) 2%". | 50/50: IEA 22.6 (2025 $); TA–TERI 17.7 | **22 $/kW-yr** (only two hybrid estimates → upper) | upper | default |
| `life_re` | definitions.mod:359 | 25 yr | IEA WEO 2024 p. 336: "Economic lifetime assumptions are 25 years for solar PV, and onshore and offshore wind." IECC Table S-1: "Lifespan 25". TA–TERI Tech: solar and wind `economic_life_yr` 30. | 25; 25; 30 | **25 (keep)** | lower | default |
| `re_capex_end_slow` | definitions.mod:157 | 800 (flat) | IEA WEO 2024 Table B.4a p. 333 (STEPS) India 2050: solar "300", wind onshore "1 090" (2023 USD). | 50/50: 732 | 732 (or keep 800 as no-learning bound) | upper | NEEDS CALL (#3) |
| `re_capex_end_fast` | definitions.mod:158 | 133.75 ("scaled ×0.6688 off 200 IRENA-optimistic") | IEA WEO 2024 Table B.4c p. 335 (NZE) India 2050: solar "280", wind onshore "1 040". No source found below 280 $/kW for India in 2050, even for solar alone. | 50/50: 695; solar only: 295 | 695 (hybrid) or 295 (if the 2050 mix is solar-led) | upper | NEEDS CALL (#3) |

## C. Electricity use and variable opex

| Parameter | file:line | Current | Sources | Value in model units | Proposed | Pessimistic | Flag |
|---|---|---|---|---|---|---|---|
| `h2_kwh_per_t` | definitions.mod:344 | 55,000 kWh/t | (1) IEA GHR 2025 annex p. 6: "Efficiency (LHV) 63%" (2024, global), "58%" (China). (2) IECC Table S-2 p. 31: "Electrolyzer efficiency kWh/kg 52" (range 48–55, Fig. 4c). (3) TA–TERI Params_H2: "E_H2_kWh 51.23 … 33.3 kWh/kg (LHV) / 0.65 system efficiency" plus "E_H2_comp_Storage 2 kWh/kg". (4) IRENA (2020) p. 11: "Efficiency at nominal capacity is 65%, with a LHV of 51.2 kWh/kg". IEA % converted with LHV 33.3 kWh/kg. | 52,900 (IEA); 57,400 (IEA China); 52,000; 53,200; 51,200 | **53,000 kWh/t** (median 52,900) | upper | default |
| `h2_opex` | definitions.mod:346 | 300 $/t ("water + stack O&M") | Water: IRENA (2020) p. 40: purification cost "starting from desalinated sea water (well below USD 1/cubic metre (m3) of water)", "assuming 20 kg of water use per kilo of hydrogen" → < 20 $/t H₂. TA–TERI: Params_H2 "H2_Water 0.0315 tH2O/kg-H2"; Commodities "Water … Including treatment opex … 0.5 $/t" → 15.75 $/t H₂; Params_H2 "Labor 0.00047 h/kgH2" × Commodities "Labor … 20 $/h" → 9.4 $/t H₂. Stack replacement is already in fixed O&M (IEA 3 %, IECC 3.5 %) and in `life_h2elec`. No source supports 300. | 15.75–20 (water) + 9.4 (labour) | **30 $/t** (upper of water + labour) | upper | default |

## D. LCOH anchor (2025), firming plug, 2050 end-point, sampled range

### D1. What the model does now

At the current values the bare build-up (electrolyser at 35 % utilisation, no storage, no firming) costs **3,662 $/t** in 2025: electrolyser annuity 1,570 + electrolyser O&M 400 + RE annuity 1,123 + RE O&M 269 + opex 300. `h2_firm_capex` (line 368) adds an overnight **12,998 $ per (t/yr)** so that the 2025 LCOH equals `lcoh_2025_target` = 5,000 $/t (plug worth 1,338 $/t). The plug then falls in proportion to electrolyser capex, so at `theta_tech` = 1 it is 158 $/t in 2050. Reproduced 2050 LCOH: 5,000 (θ = 0), 3,250 (θ = 0.5), 1,500 (θ = 1).

### D2. Evidence on the near-term delivered cost of green H₂ in India

| Source | Kind | Quote (page) | Basis | 2025 $/kg |
|---|---|---|---|---|
| Ministry of Steel (2024) *Greening the Steel Sector*, §8.4.1 | GoI | "Based on the industry inputs, the starting point is assumed to be USD 5 per kg for the year 2024-25" (p. 175) | MNRE preliminary NGHM estimates | 5.13 (5.0 × 1.0263) |
| IEA GHR 2025, Table 2.2 | agency | IOCL Panipat, 10 kt: "Awarded to L&T Energy Green Tech with a bid of INR 397/kg H2 (~USD 4.6/kg H2), with the project already in FID" (p. 46) | 25-yr BOO supply, RE-only | 4.56 |
| IEA GHR 2025, Table 2.2 | agency | BPCL (Bina) and HPCL (Visakh), 5 kt each: "Awarded to Ocior Energy with a bid of INR 328/kg H2 (~USD 3.8/kg H2)" (p. 46) | same bidder, counted once | 3.76 |
| IECC (2026) Table S-5 | univ. | "Numaligarh Refinery 2029 3.2 … 279" (Rs/kg H₂) (p. 33) | refinery tender, 2026 | 3.20 |
| IECC (2026) Table S-5; PIB/MNRE (6 Aug 2025); IEA GHR 2025 p. 39 | univ. / GoI / agency | SECI green-ammonia lots, H₂-equivalent "2.8"–"3.7" $/kg (p. 33); PIB: "record low price discovery of ₹55.75/kg"; IEA: "INR 49.75-64.74/kg NH3" | IECC converts at 190 kg H₂/t NH₃, deducts 50 $/t NH₃ Haber–Bosch cost, nets a 0.12 $/kg SIGHT credit | ~3.0 (median of 13 lots) |
| IECC (2026) Fig. 1 note | univ. | "the lowest unsubsidized costs of electrolytic hydrogen discovered in India auctions are near 3.5 US$/kg" (p. 9) | | 3.5 |
| IECC (2026) Fig. 4 | univ. | "off-grid LCOH is at $3.0/kg" (p. 11), solar + 15 h BESS, electrolyser at 95 %, 10 % WACC, 2030 costs | bottom-up, 2030 | 3.0 (context: 2030) |
| NITI Aayog & RMI (2022) Exh. 10 | GoI / think tank | reference RTC price "5.3 - 5.9", "Aggressive Hydrogen Price 3.2 - 3.7" $/kg (p. 29) | 2020 costs, RTC RE at ₹3.6/kWh | context (older) |

Median of the six 2024–26 near-term India figures (5.13, 4.56, 3.76, 3.5, 3.2, 3.0) = **3.6 $/kg**; range 3.0–5.1.
Caveats: the tender prices are winning bids for supply from 2027–2029, fixed in nominal rupees for 10–25 years, and backed by SIGHT payments and transmission waivers. IEA (GHR 2025, p. 87) warns that in India "projects that are operational, almost certain or have a very strong potential to be available by 2030 account for less than 20% of their target". They are evidence of price, not proof of cost.

### D3. With sourced component values the plug disappears

The model's own formula, with the values proposed in A–C (capex 800, RE 835, `re_cf` 0.25, 53 kWh/kg, electrolyser O&M 3 %, RE O&M 22, opex 30), gives a bare 2025 build-up of **4,710 $/t** at the model's 6 % rate (electrolyser 1,993 + its O&M 581 + RE 1,571 + RE O&M 532 + opex 30). Most of the gap to 5,000 closes because a 0.25 capacity factor needs 24.2 kW of renewables per t/yr instead of 17.9, and the electrolyser runs fewer hours. That is:

- above the tender median (3.6), between the IOCL bid (4.56) and the Ministry of Steel anchor (5.13), so it is on the pessimistic side of the evidence;
- 5,900 $/t at the 10 % WACC that IECC and TA–TERI use, so the 6 % model rate is doing a lot of work (see S5).

The only sourced explicit firming estimate is IECC Fig. 4a (p. 12): a "BESS (15h)" bar of 1.0 $/kg in a 3.0 $/kg total (electrolyser 0.4, OPEX 0.1, solar 1.3, BESS 1.0, grid 0.2). Scaled to the 2025 battery cost in the TA–TERI workbook (Tech/Battery "125" USD/kWh in 2025, "86" in 2030, citing Indian storage tenders), that is ≈1.45 $/kg at 10 % or ≈1.1 $/kg at 6 %. That is the same size as the current plug (1.34 $/kg), so the plug's 2025 *magnitude* has a plausible physical meaning. But in IECC's configuration the battery lets the electrolyser run at 95 %. Adding battery firming on top of an electrolyser that follows the renewables at 25–35 % counts firming twice. The two consistent options are (i) the electrolyser follows the renewables, plus a small H₂ buffer (TA–TERI: H₂ storage "394 USD/kg … Near-zero materiality: the model builds 0-125 t"), or (ii) oversized solar plus about 15 h of battery with the electrolyser at about 95 %.

| Parameter | file:line | Current | Proposed | Pessimistic | Flag |
|---|---|---|---|---|---|
| `lcoh_2025_target` | definitions.mod:362 | 5,000 $/t | Keep 5,000 only as a reporting check (MoS 2024 anchor, 5.13 in 2025 $); evidence range 3,000–5,130, median 3,600 | upper | NEEDS CALL (#1) |
| `h2_firm_capex` (plug) | definitions.mod:368–372 | 12,998 $/(t/yr) overnight in 2025, × `h2elec_capex_kw[t]/h2elec_capex_kw[2025]` | **Set to 0 (drop)** once A–C are adopted: the sourced build-up (4,710) already exceeds the tender median, and is 0.29 $/kg short of the MoS anchor. If firming is kept, cost it explicitly as battery storage that follows the battery cost path (125 → 86 → 74 $/kWh in 2025/2030/2035; TA–TERI, IECC Table S-1) and raise electrolyser utilisation to ~0.95 at the same time. No source supports tying the plug to electrolyser capex. | — | NEEDS CALL (#1) |
| 2050 LCOH at θ = 1 (1.50 $/kg, via the back-solved ends) | definitions.mod:156, 158 | 1,500 $/t | Let it emerge from sourced ends: **≈2,390** (hybrid RE at IEA NZE 695 $/kW, electrolyser 159), or ≈1,850 for a solar-led mix (295 $/kW, cf 0.22). Sources quoting ≤1.5: MoS p. 175 base case "USD 1.5 per kg by 2030-31" (a price assumption from MNRE, not a build-up); NITI–RMI p. 30 "$1.60/kg by 2030 and $0.70/kg by 2050" (best case). IECC p. 12: "$2.5/kg within the mid-term, i.e., by 2035". | upper | NEEDS CALL (#3) |
| Sampled 2050 range 1.5–5 $/kg (θ_tech 1 → 0) | paper; definitions.mod:155–158 | 1.5–5.0 | Sourced ends give ≈1.9–2.4 (θ = 1) to ≈3.2 (θ = 0 with IRENA 1 TW / IEA STEPS ends), or 4.7 if θ = 0 keeps "no learning". No source projects zero learning to 2050, so 4.7–5 is an explicit pessimistic bound. | upper | NEEDS CALL (#3) |

## E. Deployment ramp (`h2_ref_cap` × `h2_peak_rate`)

The ramp caps the **year-on-year increase in steel-sector electrolyser output capacity** (t H₂/yr). At `n6_h2_dri` = 0.07 t H₂/t DRI, 1 Mt H₂/yr ≈ 14 Mt DRI/yr of new H₂-DRI.

| Parameter | file:line | Current | Sources | Proposed | Pessimistic | Flag |
|---|---|---|---|---|---|---|
| `h2_ref_cap` levels × `h2_peak_rate` | definitions.mod:378–379 (studies set 2/4/6 Mt) | peak additions 0.5 / 1.0 / 1.5 Mt H₂/yr (steel only) | MNRE (2023) NGHM p. 4: "at least 5 Million Metric Tonne (MMT) of Green Hydrogen per annum by 2030" (all sectors); p. 13 (steel): "Steel plants can begin by blending a small percentage of Green Hydrogen in their processes". 5 Mt over 2023–2030 ≈ **0.71 Mt/yr nationally** (paper's anchor; my arithmetic). MoS (2024) p. 184: "green hydrogen use in the gas-based DRI-EAF process will create a demand for 1.1 MTPA of green hydrogen by 2030-31", and only in MNRE's ambitious cost case (Fig. 8.10 shaft-furnace potential 0.38 → 1.10 MTPA over 2022–2030, ≈ +0.09 Mt/yr). IEA GHR 2025 p. 87: India's projects that are firm by 2030 are "less than 20% of their target"; p. 211: refinery tenders "for more than 40 ktpa"; p. 217: SIGHT Mode 2 supply of "724 ktpa of ammonia". No source gives a steel-specific build rate after 2030. | Keep as a scenario axis, but state that even the **low** level (0.5 Mt/yr for steel alone) is 70 % of the whole-economy NGHM pace, and the high level is 2.1×. Evidence-bracketed alternative: **0.25 / 0.5 / 0.75 Mt/yr** (low ≈ 2.5× the MoS steel-specific path; high = the full NGHM national pace). | lower | NEEDS CALL (#4) |
| `h2_peak_rate` | definitions.mod:379 | 0.25 (fixed) | no admissible source found (shape choice) | keep; it only scales `h2_ref_cap` | — | default |
| `h2_base_start` / `h2_base_end` | 380–381 | 0 / 0.05 | no admissible source found | keep; document as an assumption | lower | default |
| `h2_gauss_sigma` | 382 | 2 yr | no admissible source found | keep; document | — | default |
| `h2_peak_lag` | 386 | 5 yr | no admissible source found. NGHM gives 2023→2030 (7 yr) from launch to its 5 Mt goal, which only supports "several years". | keep; document | — | default |

## Structural notes (not fixed; code untouched)

- **S1 — One number for two things.** `re_cf` is both the renewables' capacity factor (kW of renewables per t/yr) and the electrolyser's utilisation (line 365 and `v_capacity.mod:285–287`). That ties the electrolyser to the renewable output with no storage. The DRI shaft furnace needs a steady H₂ flow, but the model only balances annual energy, so the cost of firming (storage or oversizing) appears only through the plug. Splitting it into `re_cf` and `elec_util` (with an explicit storage cost when `elec_util` > `re_cf`) would let option (ii) in D3 be represented.
- **S2 — The plug falls with the wrong cost.** `h2_firm_capex` falls in step with *electrolyser* capex (−88 % by 2050 at θ = 1). If it stands for firming, its cost driver is battery or H₂-storage cost.
- **S3 — Fixed O&M does not fall.** `fopex_h2elec` (400 $/(t/yr)) and `fopex_h2re` (15 $/kW) stay constant while capex falls. At θ = 1 in 2050, fixed O&M is 669 of the 1,500 $/t LCOH (45 %), and electrolyser O&M (400) is more than twice the electrolyser annuity (185). Expressing O&M as a share of the year's capex (IEA, TA–TERI 3 %; IECC 2 %) would fix this.
- **S4 — Hard-coded RE capex.** The 2025 RE capex is a literal `800` in two places (line 357). It should be a parameter.
- **S5 — Discount rate.** The H₂ annuities use the economy-wide `real_discount_rate` = 6 %. IECC and TA–TERI use a 10 % WACC for Indian H₂ projects. At 10 % the sourced build-up is 5.90 $/kg instead of 4.71. This belongs with whoever audits the discount rate, but it affects H₂ more than any other route because H₂ is almost all capex.
- **S6 — The "slow" ends are not a slow case.** θ_tech = 0 means *no* learning (2050 = 2025). Every source surveyed projects some decline (IEA STEPS solar 710 → 300 $/kW; IRENA electrolyser 307 $/kW at 1 TW). This is a deliberate pessimistic bound, and the paper should say so.
- **S7 — Year-one electrolyser capacity.** `cap_h2elec` is counted in t/yr of output at `re_cf`, so changing `re_cf` rescales the meaning of the ramp ceiling in kW terms (a lower `re_cf` means more MW of electrolyser per Mt/yr allowed). That is fine, but it should be stated alongside the ramp levels.
- **S8 — `parameters.mod:18` `H2_cap` 1.5 Mt** is used only in ramp mode 1. The default is mode 2, so it is inert in the default runs.

## Bibliography

IN PROGRESS
