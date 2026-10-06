# Stage 2 — Carbon capture and storage (ST-10, register §3.8)

**Status: complete** (2026-10-06).

Model files (audited repo `nakulneupane/steel-sector-decarbonization` @ b33b88a): `core/definitions.mod` (lines 159–161, 174, 213–214, 305–340), `core/parameters.mod` (lines 4 and 32), and `core/modules/q_carbon_capture.mod` (whole file).

Costs are in **constant 2025 USD per tonne of CO₂ captured** unless stated otherwise. They were converted with `convert_2025usd.py`. Factors used: US GDP deflator to 2025 = 1.438 (2010), 1.312 (2016), 1.240 (2019), 1.092 (2022), 1.053 (2023). For INR in 2022 and 2023: × WPI ratio ÷ ₹87.16/$, which gives $11.75 per ₹1,000. The script is at `scratchpad/ccs_scripts/conv.py`.

**Steam conversion.** Indian sources give regeneration steam in **t steam/t CO₂**. These were converted to GJ using the latent heat of low-pressure saturated steam: about **2.15 GJ/t** at 3–3.5 bar(a), from the IAPWS-IF97 steam tables (h_fg = 2,163 kJ/kg at 3 bar and 2,148 kJ/kg at 3.5 bar). The plants that state a steam pressure use 3–3.5 bar (MoS 2024, Table 9.1).

---

## Needs your call

1. **The 2025 all-in cost anchor `n10_ccs_cost_start` (now 125 $/t).** Indian estimates of the full cost (capture + compression + transport and storage) are much lower: NITI 2022 gives 45–59, MoS 2024 gives 67 (range 43–97), and the Tata BF pilot gives 66–72 once T&S is added. Their median is about 67.
   - (a) **75**: India median, rounded up. It back-solves to a capex of about $154/(tCO₂/yr), close to NITI's $94–118.
   - (b) **100**: consistent with DST's 2025 capex *target* of "< ₹1 Cr per t/day", about $314/(t/yr). That target implies today's large-scale capex is higher than NITI assumes.
   - (c) Keep **125**, close to the European IEAGHG cost per tonne avoided plus T&S ($131–141).
   - Recommendation: **(a) 75**, with (b) as the high-cost sensitivity.
2. **Fixing ST-10: the per-route physical capture cap.** Replace `n10_ccs_eta × fc_max` (0.85 × 0.90 = 0.765 of *all* route CO₂) with `capture_rate (0.90) × capturable_share`. For BF-BOF the capturable share is 0.67, so the cap becomes **0.60 of route CO₂**. That is the median of NITI (~0.50), MoS/CEEW (0.59), NITI Fig. 2-14 × 0.9 (0.64) and IEAGHG (0.59–0.73).
   - Options: 0.60 (recommended), 0.50 (pessimistic, NITI's single-point BF-gas capture), or keep 0.765.
3. **Earliest CCS start year.** The model now allows CCS from 2027. Recommend **0 until 2034, first capture in 2035**:
   - DST 2025 roadmap: Phase 2 (2030–35) covers only pilot injection below 30 kt/yr; the first commercial hubs above 1 Mt/yr come in Phase 3 (2035–45).
   - MoS: storage projects take 6–9 years to reach 1 Mt/yr.
   - Options: 2035 (recommended), 2032 (MoS lead time counted from the 2026 budget scheme), or 2030 (NITI's 2030 demonstration aspiration).
4. **Deployment ceiling in 2050 (`phi_2050`, now 0.50).** Recommend **0.25 of route CO₂, rising linearly from 0 in 2034 to 0.25 in 2050**:
   - NITI 2022, economy-wide: 31 % of capturable CO₂ in 2050 (≈ 26 % of emissions).
   - NITI 2026 Net Zero Scenario: CCUS deployment "Low" in 2050.
   - IEA SDS: 25 % of steel-sector direct CO₂ captured in 2050.
   - CEEW via MoS: 56 % is a *requirement* for net zero, not a feasibility estimate.
   - The median of these is about 0.28.
   - Options: 0.25 (recommended), 0.30, or keep 0.50.
5. **The 2050 cost axis (`ccs_capex_fall_slow`/`_fast`, now 0.3165/0.8435, back-solved to $100/$60).** Recommend setting the capex decline directly: **slow 0.27** (NITI's subsidy path ₹4,100 → ₹3,000/t, −27 %) and **fast 0.60** (MoS: capture cost $50 → $20, −60 %).
   - With anchor 75, the 2050 all-in cost becomes 70 (slow) or 63 (fast); with anchor 100 it becomes 88 or 73.
   - The old 2050 end-points of $100/$60 cannot be reached under anchor (a), because energy and T&S alone already cost $55/t.
   - Options: these two decline rates (recommended), or keep the current ones.

**Parameters with no admissible source:** 3 existing (`ccs_ngdri_proc_share`, `ccs_mult_cdri`, `ccs_mult_ng_proc`), plus the 2 new capturable-share parameters for coal-DRI and NG-DRI that the ST-10 fix introduces. They are kept, or set by analogy, as pessimistic placeholders.

---

## A. Cost anchor and 2050 trajectory

| Parameter | file:line | Current | Sources (cite, quote, page) | Model units (2025 $) | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| `n10_ccs_cost_start` (all-in 2025 cost; capex is back-solved from it, `definitions.mod:332–336`) | definitions.mod:213; parameters.mod:32 | 125 $/tCO₂ | **NITI 2022**, Table 6-4 (p. 139): iron & steel "Total Cost (A+B), Rs./TCO2 2,900-3,600" (capture + compression to 100 bar + capital charges, 2 Mtpa BF-BOF ISP). Table 6-3 note (p. 139): T&S "an additional US$ 10-15 per tonne".<br>**MoS 2024**, Table 9.13 (p. 221): "Total CCS cost 64 (41 - 92)" USD/tCO₂, of which capture 37, transport 7, sequestration 20.<br>**MoS 2024**, Table 9.1 (p. 196): Tata Steel BF pilot (5 TPD, amine) "CO₂ Capture cost (INR/tCO₂) 3,500-4,000"; OPEX the same, i.e. opex only.<br>**MoS 2024** (p. 203): NTPC 20 TPD capture "approximately INR 2.74/Kg CO₂, i.e., approximately USD 35/Ton".<br>**DST 2025** (p. xi): "A desirable total cost of CCUS (say, not more than 5-10 Rs/kg of CO₂ i.e., about 60-120 USD/ton-CO₂)" — a target.<br>**NITI 2026** (p. 96): CCUS "cost between 45-60 USD/tCO₂ (Ministry of Steel, 2024)" — secondary.<br>**IEAGHG 2013/04** (p. 7): "US$ 74/t CO2 ... 50% CO2 avoided ... US$81/t CO2 ... 60%" (2010 USD, per t avoided, excluding T&S).<br>**IEAGHG 2018-TR03** (p. 1): chemical absorption in steel "56-93 $2016/tCO2" avoided.<br>**IEA 2020 CCUS** (p. 100): BF "over USD 40/t of CO2 and sometimes more than USD 100/t" (capture only). | NITI: 34–42 capture + 11–16 T&S = **45–59**. MoS: **67** (43–97). Tata: 41–47 + 25 T&S = **66–72**. NTPC: 32 (capture only, power plant). DST target: 60–120. IEAGHG 2013: 106–117 per t avoided (≈ 89 per t captured) + 25 T&S. IEAGHG 2018: 73–122 per t avoided. | **75** (India median ≈ 67, rounded up). Back-solves to capex ≈ **154 $/(tCO₂/yr)**, against NITI capex of 94–118 (see B). | Upper | **NEEDS CALL** (1) |
| `ccs_capex_fall_slow` | definitions.mod:160 | 0.3165 (back-solved to $100 in 2050) | **NITI 2022** (pp. 25, 144): subsidy for storage "Rs. 4,100/tonne till 2040 and Rs. 3,000/tonne till 2050", "Based on the average CCUS cost" → −27 %. **MoS 2024**, Table 9.13 (p. 221): capture 37 → 20 "Best case" (−46 %). | Capex decline 27 % to 2050 | **0.27** | Smaller decline | **NEEDS CALL** (5) |
| `ccs_capex_fall_fast` | definitions.mod:161 | 0.8435 (back-solved to $60) | **MoS 2024** (p. 203): "Internationally, the cost of CO₂ capture is around 50 USD/ton, which is expected to reduce to 30 USD/Ton CO₂ by FY 2030-31 and subsequently stabilise at around 20 USD/Ton" (−60 %). **DST 2025** (p. xv): outcome "Reduction in CO₂ capture cost (< 40 $/ton)". | Capex decline 60 % | **0.60** | — | **NEEDS CALL** (5) |
| `theta_ccs` | definitions.mod:159; parameters.mod:4 | 0 default; 0.5 in runs | Scenario axis; no source needed. | — | keep | — | default |
| `n10_ccs_cost_end` | definitions.mod:214 | 75 | Not used anywhere in the model (dead parameter). | — | delete or ignore | — | default |
| `ccs_ref_elec`, `ccs_ref_steam` (used only in the back-solve) | definitions.mod:326–327 | 0.07 $/kWh, 5 $/GJ | **NITI 2022**, Table 6-3 (p. 139): steel electricity 170–190 kWh costs Rs 510–570, i.e. Rs 3/kWh; steam 1.3–1.5 t costs Rs 975–1,125, i.e. Rs 750 per t steam. | 0.035 $/kWh; 4.1 $/GJ | keep 0.07 / 5 (pessimistic: a higher reference energy cost gives a smaller back-solved capex, but the anchor dominates) | — | default |

## B. Cost components

| Parameter | file:line | Current | Sources | Model units | Proposed | Pessimistic | Flag |
|---|---|---|---|---|---|---|---|
| `ccs_ts_cost` (transport + storage) | definitions.mod:309 | 20 $/t | **NITI 2022**, Table 6-3 note (p. 139): "transportation, sequestration, monitoring, etc. will be an additional US$ 10-15 per tonne" (2022 USD).<br>**MoS 2024**, Table 9.13 (p. 221): transport "7 (4 - 10)", sequestration "20 (2 - 37)"; source Vishal et al. 2023 and Smith et al. 2021.<br>**MoS 2024** (p. 221): Gandhar EOR GS-4 storage "USD 12.4 per metric ton ... does not include the cost of capture, compression, and transport".<br>**IEA 2020 ISTR**, Fig. 2.11 notes (p. 107): "CO2 transport and storage = USD 20/t CO2 captured".<br>**IEA 2020 CCUS** (p. 73): "USD 20/tCO2". | NITI 11–16; MoS 28 (6–50); Gandhar EOR storage 13 (+ MoS transport 7 = 20); IEA 25 | **25** (median of NITI 16, MoS 28, IEA 25) | Upper | default |
| `ccs_vopex_solvent` | definitions.mod:308 | 5 $/t ("placeholder") | **MoS 2024**, Table 9.5 (p. 203), NTPC: "Sp. Solvent Consumption kg/tonne CO₂ 0.204"; "Cost of Solvent INR/kg 650" → ₹133/t.<br>**IEAGHG 2013**, Annex C Table C-1: "MEA Make Up kg/t CO2 captured 1.0" (no price given).<br>**NITI 2022**, Table 6-3 (p. 139): "Other costs" for steel Rs 400–600/t, which also covers R&M, manpower and water. | NTPC 1.6; NITI "other" 4.7–7.1 (overlaps with FOM) | **2** (single solvent-specific source, rounded up) | Upper | default |
| `ccs_fom_pct` | definitions.mod:307 | 4 %/yr | **MoS 2024**, Table 9.5 (p. 203): NTPC "Annual Fixed Cost % of project cost 5%".<br>**NITI 2022**, Table 6-3: "Other costs" Rs 400–600/t ÷ capex Rs 8,000–10,000 per (t/yr) → about 5–7 %/yr.<br>**IEA 2020 CCUS** (p. 73): "SMR with CCS – 3.0 %" of capex (whole plant). | 3 %, 5 %, 5–7 % | **5 %** (median) | Upper | default |
| `life_ccs` | definitions.mod:305 | 15 yr | **NITI 2022** (p. 156): "the economic life of the project, considered as 25 years of operations".<br>**IEAGHG 2013** (p. 1): "a 25 year economics plant life".<br>**IEA 2020 ISTR** (p. 107): "25-year lifetime ... for all equipment". | 25, 25, 25 | **25** | Shorter | default (see ST-16 note) |
| Capex check (not a parameter) | `ocapex_ccs_2025` (definitions.mod:332) | ≈ 531 $/(t/yr) | **NITI 2022**, Table 6-2 (p. 138): steel "2 mtpa" capture, "Rs. 1,600-2,000 Crore" (including owner's cost and financing).<br>**DST 2025** (p. xi): R&D aim "entire capital cost of the system under 1 Cr/ton per day of CO₂ when the scale of capture is in million tons per annum".<br>Pilots: NTPC "Project Cost (20 TPD Plant) INR lakhs 1500" (MoS Table 9.5); Tata "5-6 crores" for 5 TPD (MoS Table 9.1). | NITI 94–118; DST target 314; NTPC pilot 267; Tata pilot 322–386 | Anchor 75 → 154; anchor 100 → 349 | Upper | (feeds call 1) |
| `ccs_mult_bf` | definitions.mod:310 | 1.0 | Reference stream. | — | 1.0 | — | default |
| `ccs_mult_cdri` | definitions.mod:311 | 1.2 | **No admissible source specific to rotary kilns.** Nearest analogue: NITI Table 6-2, coal power capex Rs 3,500–4,000 cr per 5 Mtpa = 0.83 × steel. Indian coal-DRI kilns are small (100–500 t/d), and the pilot data above show capex per (t/yr) at small scale is 2–3 × NITI's. | — | keep **1.2** | Upper | default (no source) |
| `ccs_mult_ng_proc` | definitions.mod:321 | 0.5 | **No DRI-specific source.** Analogues from NITI Table 6-2 capex per t/yr: gasification process stream (~90 % CO₂, already separated) Rs 80–100 cr/Mtpa = 0.10 × steel; SMR tail gas (~65 % CO₂) Rs 1,000–1,143 cr/Mtpa = 1.19 × steel. MoS Table 9.1: JSW Midrex 100 TPD needs a separate amine/carbonate unit (1,740 kg steam/t). | 0.10–1.19 | **1.0** (a Midrex top-gas retrofit needs a full solvent unit, like BF gas) | Upper | default (no source) |
| `ccs_mult_ng_flue` | definitions.mod:322 | 1.3 | NITI Table 6-2 analogues: refinery flue (7–20 % CO₂) Rs 1,100–1,300 cr/Mtpa = 1.33 × steel; coal power 0.83. | 0.83–1.33 | keep **1.3** | Upper | default |

## C. Energy use

| Parameter | file:line | Current | Sources | Model units | Proposed | Pessimistic | Flag |
|---|---|---|---|---|---|---|---|
| `ccs_kwh_bf` | definitions.mod:312 | 130 kWh/t | **NITI 2022**, Table 6-3 (p. 139): iron & steel "170-190" kWh/TCO₂ (delivery at 100 bar).<br>**IEAGHG 2013**, Table C-3: capture + compression 151.9 kWh/t HRC for 1,243 kg captured (EOP-L1) and 196.3 for 1,533 kg (EOP-L2), compression to 110 bar.<br>**IEAGHG 2018**, Table 1 (p. 7): MEA electricity 0.47 GJ/t (Ho 2013), MDEA 0.54 (NETL 2014).<br>Pilots without pipeline compression (MoS Table 9.1): Tata BF "80-90"; NTPC "117.6" (Table 9.5). | NITI 170–190; IEAGHG 122–128; 131–150 | **190** (only Indian estimate on a comparable boundary, upper end) | Upper | default |
| `ccs_kwh_cdri` | definitions.mod:313 | 150 | No kiln-specific source. Analogue: NITI Table 6-3, coal-based power flue (8–15 % CO₂) "250-300" kWh/t. | 250–300 | **300** | Upper | default (analogue) |
| `ccs_kwh_ng_proc` | definitions.mod:317 | 110 | **MoS 2024**, Table 9.1: JSW gas-DRI "45" kWh/t; JSPL MDEA "25-28 kWh/T". **NITI**, Table 6-3: gasification process stream (polish + compress) "70-90". | 25–90 | keep **110** (above the evidence; covers compression) | Upper | default |
| `ccs_kwh_ng_flue` | definitions.mod:318 | 170 | Analogues, NITI Table 6-3: refinery flue "110-130"; coal power "250-300". NG flue (4–8 % CO₂) is leaner than both. | 110–300 | **300** | Upper | default (analogue) |
| `ccs_steam_bf` | definitions.mod:314 | 3.0 GJ/t | **NITI 2022**, Table 6-3: steel steam "1.3-1.5" t/t.<br>**MoS 2024**, Table 9.1: Tata BF "1,000-1,100" kg/t; JSW gas-DRI "1,740"; JSPL MDEA "Approximately 1,700 kg".<br>NTPC "1.29" t/t (Table 9.5).<br>**IEAGHG 2013**, Table C-1: MEA "Steam demand 3.03" GJ/t. | NITI 2.8–3.2; Tata 2.2–2.4; NTPC 2.8; JSW 3.7; JSPL 3.7; IEAGHG 3.0 | keep **3.0** (India median) | Upper | default |
| `ccs_steam_cdri` | definitions.mod:315 | 3.3 | Analogue, NITI Table 6-3: coal power "1.3-1.55" t/t → 2.8–3.3 GJ. | 2.8–3.3 | keep **3.3** | Upper | default (analogue) |
| `ccs_steam_ng_proc` | definitions.mod:319 | 0.3 | **MoS 2024**, Table 9.1: JSW gas-DRI CO₂ capture "1,740" kg steam/t; JSPL DRI MDEA "Approximately 1,700 kg per tonne of CO₂". Both are Indian NG/syngas DRI process-stream units. | 3.7 | **3.7** | Upper | **default — large change**: the "negligible regeneration" assumption is contradicted by both Indian DRI units |
| `ccs_steam_ng_flue` | definitions.mod:320 | 3.6 | Analogues, NITI Table 6-3: refinery 1.2–1.5 t; coal power 1.3–1.55 t → up to 3.3 GJ. | 2.6–3.3 | keep **3.6** (slightly above the analogues; a leaner stream) | Upper | default |
| `ccs_boiler_eff` | definitions.mod:328 | 0.85 | **IEAGHG 2013**, Table C-5: steam generation plant "Boiler Efficiency 89.2%" (EOP-L1), 89.3 % (EOP-L2); 90.2 % (OBF case). | 0.89–0.90 | **0.89** (lower bound of the single source) | Lower | default |

## D. Capture rate and capturable base (ST-10)

**What the model does now.** `q_carbon_capture.mod:14–35` sets the capturable base equal to the **whole scope-1 CO₂ of each route**: all coking coal, PCI and limestone for BF-BOF, and all non-coking coal, NG and limestone for the DRI routes. Each route may capture `n10_ccs_eta × fc_max` = 0.85 × 0.90 = **0.765** of that base. Two separate errors combine here:

- **Derating the capture rate twice.** The 0.85 and 0.90 both stand for "capture rate on a treated stream". The evidence puts that rate at about 0.90 on its own.
- **Base too broad.** Several sources are not amenable to capture: sinter strand flue (~8 % CO₂), BOF, mill reheating and flares. Treating them as capturable overstates the base.

| Parameter | file:line | Current | Sources | Model units | Proposed | Pessimistic | Flag |
|---|---|---|---|---|---|---|---|
| Capture rate on a treated stream (`n10_ccs_eta`, `fc_max`) | definitions.mod:174; q_cc:11 | 0.85 × 0.90 = 0.765 | **IEA 2020 ISTR** (p. 107): "90% capture rate assumed for all CCS routes".<br>**IEA 2020 CCUS** (p. 73): "SMR with CCS – 95%, coal with CCS – 90%".<br>**IEAGHG 2018**, Table 1 (p. 7): steel studies at 90 % (one at 95 %).<br>**NITI 2022**, Table 6-2 (p. 138): cement, power and refinery "Around 90%".<br>**MoS 2024** (p. 199): "existing CO₂ capture technologies have a capture efficiency of 55-60%, while the peak capture efficiencies range from 80 to 85%". | 0.80–0.95 | **one parameter, 0.90** (median); remove the double derating | — | **NEEDS CALL** (2) |
| Capturable share, BF-BOF (new parameter; multiplies the base) | q_cc:14–17, 30–31 | 1.0 (implicit) | **NITI 2022**, Fig. 2-14 (p. 46), tCO₂/t finished steel (CO₂ %): sinter 0.43 (8 %), coke oven 0.27 (23 %), BF stoves 0.39 (23 %), BOF 0.03 (7 %), calcining 0.23 (66 %), captive power plant 0.63 (25 %), mills 0.17 (18 %); total 2.15. Streams with ≥ 23 % CO₂ = 1.52/2.15 = **0.71**.<br>**IEAGHG 2013** (p. 14): of 2,094 kg/t HRC, hot stoves 415 + power plant 982 = **0.67**; adding coke-oven heaters 191 and lime kiln 72 gives **0.79**. P. 3: "could practically reduce CO2 emission by 50 to 60%".<br>**NITI 2022**, Table 6-1 (p. 137): "pre-combustion capture from BF gas will ensure at least 50% capture"; Table 6-2: steel "CO2 capture percentage Around 50%".<br>**MoS 2024** (p. 221, citing CEEW 2023): "for the BF-BoF steelmaking pathway alone, nearly 59% of emissions will need to be abated through CCUS". | Maximum captured share of route CO₂: NITI single point 0.50; MoS/CEEW 0.59; NITI Fig. 2-14 × 0.9 = 0.64; IEAGHG gross captured 0.59 (L1) / 0.73 (L2) | **share 0.67 → cap 0.90 × 0.67 = 0.60** of route CO₂ (median ≈ 0.59–0.60) | Lower | **NEEDS CALL** (2) |
| Capturable share, coal-DRI (new) | q_cc:19–22, 32–33 | 1.0 | **No admissible source found.** Rotary-kiln off-gas passes through the WHRB to a single stack, so most kiln CO₂ is in one stream. But Indian kilns are small, and dolochar or captive-coal power plants are separate stacks. | — | **0.67** (same as BF, pessimistic placeholder) → cap 0.60 | Lower | default (no source) |
| Capturable share, NG-DRI (new), and `ccs_ngdri_proc_share` | definitions.mod:316; q_cc:24–27, 34–35 | 1.0; proc share 0.6 | **No admissible number found.** IEA 2020 ISTR (p. 95) gives only a qualitative account: Ternium DRI captures "5% of emissions"; at Finmet, capture "achieving close to 100% concentrations of CO2 is also occurring ... as an integral part of the process". | — | share **0.90** (both the process stream and the reformer flue can be treated) → cap 0.81; keep proc share **0.6** | Lower | default (no source) |

**Proposed equation (Stage 3 to implement; not done here):**
`ccs_X[t] <= ccs_capture_rate * ccs_share_X * co2_capturable_X[t]`, with `ccs_capture_rate = 0.90`, `ccs_share_bf = 0.67`, `ccs_share_cdri = 0.67` and `ccs_share_ngdri = 0.90`. This removes `n10_ccs_eta` and `fc_max`.

Effect: the BF-BOF cap falls from 0.765 to **0.60** of route CO₂; NG-DRI rises slightly, to 0.81.

## E. Deployment ceiling and earliest start

| Parameter | file:line | Current | Sources | Proposed | Pessimistic | Flag |
|---|---|---|---|---|---|---|
| Earliest year (`ccs_avail = 0` before) | q_cc:40–42 | 2027 | **DST 2025** (p. xiv): Phase 2 (2030–2035) "Support pilot-scale CCS injection projects at selected storage sites (small, <30,000 t/y)" and "Initiate FEED studies for creating two semi-commercial scale CCS hubs ... (>500,000 t/y)"; Phase 3 (2035–2045) "Develop two commercial scale CCS hubs (>1 Mt/y)".<br>**MoS 2024** (p. 200): "The lead times required for pre-feasibility and site assessment studies are up to 10 years"; Table 9.12 (p. 219): pilot injection in year 5, 100 kt/yr in years 5–6, "Gradually upto 1 Mt-CO₂/year" in years 6–9. P. 216: ONGC plans Gandhar EOR injection "from 2026-27" (refinery CO₂, not steel).<br>**Union Budget 2026-27**, para 38 (p. 12): CCUS "outlay of ₹20,000 crore is proposed over the next 5 years".<br>**NITI 2022**, Table 6-5 (p. 141): steel capture 4 (base) / 5 (optimistic) Mtpa in 2030 out of 450 Mtpa emitted (≈ 1 %), including utilisation.<br>**IEA 2020 ISTR** (p. 84): "By 2030 only 1% of the direct emissions ... are captured for storage". | **0 until 2034; first capture 2035** | Later | **NEEDS CALL** (3) |
| `phi_2050` (2050 ceiling) and ramp shape | q_cc:39–42 | 0.50 of base, linear from 2027 | **NITI 2022**, Fig. 6-5 (p. 145): economy-wide capture as share of capturable CO₂: 2 % (2030), 10 % (2040), **31 % (2050)**; "Capturable CO2 85% of emissions" (p. 144).<br>**NITI 2026**, Table E1 (p. 25): "CCUS Deployment" "Low" in the 2050 Net Zero Scenario (~1,000 Mt only by 2070); p. 99 (cement): "CCUS is deployed at scale from the 2040s onward"; p. 94: by 2070 NZS "only about 10% from coal-based BF–BOF equipped with CCS".<br>**IEA 2020 ISTR** (p. 84): 2050 "400 Mt ... captured ..., or 25% of direct emissions". **IEA 2020 CCUS** (p. 47): CCUS gives 25 % of steel emission reductions in 2050.<br>**MoS 2024** (p. 221, CEEW): "56 % will need to be abated through CCUS" (a requirement for net zero). | **0.25 of route CO₂ in 2050, linear from 0 in 2034** (gives ≈ 0.08 in 2040, close to NITI's 10 %) | Lower | **NEEDS CALL** (4) |

---

## Structural notes (not fixed)

1. **ST-10, double derating and over-broad base.** See D. Two smaller related points:
   - Hard-coded duplicates: `q_carbon_capture.mod:14–27` repeats the emission factors (0.1116 × 25 and so on) instead of referencing `scope1_*`, so the ST-13 emission-factor fix must be made in both places.
   - The BF-route base includes BOF lime, which is not capturable.
2. **Back-solving capex from an all-in anchor is fragile.** `ocapex_ccs_2025` (definitions.mod:332–336) subtracts T&S, solvent and energy priced at fixed reference values. If those components are raised, as proposed, the residual capex shrinks, and the `max(...,10)` floor can bind silently.
   - Under the proposals, energy plus T&S alone is about $55/t, so the 2050 end-points of $60 or $100 cannot be reached through capex decline alone.
   - Better: give the overnight capex directly, for example NITI's $94–118/(t/yr), or $154 back-solved at anchor 75. The all-in cost then follows from model prices.
3. **Dead parameter.** `n10_ccs_cost_end` (definitions.mod:214) is not used anywhere.
4. **ST-16 interaction.** With `life_ccs` 25 and no end-of-horizon credit, CCS builds after about 2035 are penalised even more, because their lifetime runs far past 2050.
5. **Units.** `ccs_steam_*` are in GJ per tCO₂, but Indian sources report tonnes of steam. The 2.15 GJ/t conversion assumes condensing LP steam. If the model's waste-heat pool (`whr_steam_eff`) is in GJ of steam enthalpy (≈ 2.7 GJ/t), the steam need is about 25 % understated by comparison.
6. **The NG-DRI process stream needs regeneration energy.** The model sets `ccs_steam_ng_proc` to 0.3, but both operating Indian DRI capture units report about 1.7 t steam per tCO₂ (see C).

## Bibliography

- Ministry of Steel (2024). *Greening the Steel Sector in India: Roadmap and Action Plan*. Ch. 9 "Carbon capture, utilisation and storage", pp. 190–223 (Tables 9.1, 9.5, 9.12, 9.13). https://steel.gov.in/green-steel-initiative
- NITI Aayog (2022). *Carbon Capture, Utilization and Storage (CCUS) – Policy Framework and its Deployment Mechanism in India* (prepared by M. N. Dastur). Fig. 2-14 (p. 46); Tables 6-1 to 6-5 (pp. 137–141); p. 144; Fig. 6-5 (p. 145); p. 156. https://www.niti.gov.in/sites/default/files/2022-12/CCUS-Report.pdf
- NITI Aayog (2026). *Scenarios Towards Viksit Bharat and Net Zero – Sectoral Insights: Industry*. Table E1 (p. 25); pp. 94, 96, 99. https://niti.gov.in/sites/default/files/2026-02/Scenarios-Towards-Viksit-Bharat-and-Net-Zero-Sectoral-Insights-Industry.pdf
- Department of Science & Technology (2025). *R&D Roadmap to enable India's Net Zero Targets through CCUS*. Executive summary, pp. xi, xiii–xv (image PDF, read visually). https://dst.gov.in/sites/default/files/DST-CCUS-Roadmap-2025.pdf
- Ministry of Finance (2026). *Budget 2026-2027, Speech of the Finance Minister*, 1 Feb 2026, para 38 (p. 12). https://www.indiabudget.gov.in/doc/budget_speech.pdf
- IEA (2020). *Iron and Steel Technology Roadmap*. Pp. 84, 95; Fig. 2.11 notes (p. 107). https://www.iea.org/reports/iron-and-steel-technology-roadmap
- IEA (2020). *CCUS in Clean Energy Transitions* (Energy Technology Perspectives 2020 special report). Pp. 47, 73, 100, 114. https://iea.blob.core.windows.net/assets/181b48b4-323f-454d-96fb-0bb1889d96a9/CCUS_in_clean_energy_transitions.pdf
- IEAGHG (2013). *Iron and Steel CCS Study (Techno-Economics Integrated Steel Mill)*, Report 2013/04. Overview pp. 1, 3, 6–7, 14; Annex C, Tables C-1, C-3, C-5. https://ieaghg.org/publications/2013-04%20Iron%20and%20Steel%20CCS%20Study%20(Techno-Economics%20Integrated%20Steel%20Mill).pdf
- IEAGHG (2018). *Cost of CO2 Capture in the Industrial Sector: Cement and Iron and Steel Industries*, 2018-TR03. Summary (p. 1), Table 1 (p. 7). https://ieaghg.org/publications/2018-TR03%20Cost%20of%20CO2%20capture%20in%20the%20industrial%20sector%20cement%20and%20iron%20and%20steel%20industries.pdf
- Wagner, W. & Kretzschmar, H.-J. (2008). *International Steam Tables: IAPWS-IF97*. Springer. Used only for the latent heat in the steam conversion.

**Identified but not read** (paywalled or blocked by the egress proxy; not used): Bhardwaj, Seethamraju & Bandyopadhyay (2025), *J. Cleaner Production* 486:144505, doi:10.1016/j.jclepro.2024.144505; Lau (2024), *ACS Sustainable Chem. Eng.*, doi:10.1021/acssuschemeng.3c08088; Rathore (2025), *Energy for Sustainable Development*, doi:10.1016/j.esd.2025.101866. CEEW (2023) *Evaluating Net-zero for the Indian Steel Industry* and CEEW (2023) *Assessing India's CO₂ Storage Potential* are blocked by Cloudflare; they are cited here only through MoS 2024.
