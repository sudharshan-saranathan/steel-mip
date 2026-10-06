# Stage 2 — Fuel, material and by-product prices (2025, constant real)

Status: IN PROGRESS. Sub-groups are filled in as they are finished.

## Needs your call

IN PROGRESS

## A. Coal (coking, PCI, non-coking)

Conversions: rupee prices for calendar 2025 are divided by ₹87.16/$ (2025 average, FRED EXINUS); FY 2024-25 rupee values are first inflated with WPI 2025/2024 = 155.0/154.0, as in `convert_2025usd.py` (`inr(value, 2024)`).

**Coking coal evidence (2025 USD/t)**

| # | Source | Quote / data (page, table) | Data year, boundary | 2025 USD/t |
|---|---|---|---|---|
| C1 | Ministry of Coal, Nominated Authority, *National Coal Index* OM of 06.03.2026, Annexure Table B "Representative Prices", grade **S1** (ST-I, "Coking, top grade (STI-STII or imported)") | Monthly ₹/t, Jan–Dec 2025: 18155, 17278, 16908, 15955, 15413, 16171, 16113, 15862, 16374, 18142, 17253, 17892 (pdf p. 10; Apr 25–Dec 25 marked provisional). Mean ₹16,793/t | CY 2025; representative price of top-grade coking coal incl. imports (landed/pithead, before inland freight) | **193** (monthly 177–208) |
| C2 | Ministry of Coal, *Coal Directory of India 2024-25*, Table 8.7 "Month Wise Import…" (p. 177), Total row | Coking coal "57.576" MT, "1032104.44" million ₹, "12227.03" million $ → ₹17,926/t, $212/t. Jan/Feb/Mar 2025 months: $185, $183, $176/t | FY 2024-25 imports, CIF unit value (customs category "coking", may include PCI) | **207** (inr(17,926, 2024)) |
| C3 | Domínguez Bennett et al. (2026), UC Berkeley IECC, Table S-4 (pdf p. 34): "Coking Coal Cost 200 US$/t"; p. 10: "seaborne coking coal has averaged 212 US$/t in fiscal year 2024-25, with 2022 peaks near 344 US$/t" | | Model input, India; the 212 is the same customs data as C2 (not independent) | **200** |
| C4 | Ministry of Coal, *Monthly Statistical Report* Mar 2025, Tables 8.8 and 8.9 (pp. 86–88) | Port/origin CIF prices $112–207/t; quantity-weighted by origin ≈ $177/t (my calculation) | Mar 2025, CIF at port | 177 (cross-check, same customs data) |
| C5 | Ministry of Steel (2024) *Greening the Steel Sector in India*, Executive summary (pdf p. 24): "for a coking coal price of USD 180-260/tonne" | | Analysis range | 180–260 (context) |

Three independent central estimates (C1 193, C2 207, C3 200): **median 200**. Range for Monte Carlo: about 175–260 for 2024–25 conditions (2022 spike 344). The evidence supports the **core central (184 → 200)**, not the regret-study 250. 250 lies between the 2025 level and the 2023-24 level (C1 FY 2023-24 S1 average ₹24,735/t ≈ $300 at that year's ₹82.6/$), not 2025. The Monte Carlo low of $100 is below every monthly NCI value since 2020 (lowest S1 since Apr 2020 is ₹8,340/t in Jul 2020, ≈ $113 at that year's ₹74/$, a pandemic trough).

**Non-coking coal for DRI (ng_cost_ncoal) evidence**

| # | Source | Quote / data | Boundary | 2025 USD/t |
|---|---|---|---|---|
| N1 | Coal Directory of India 2024-25, Table 8.7 (p. 177), Total row | Non-coking imports "186.046" MT, "1463233.35" million ₹, "17322.26" million $ → ₹7,865/t, $93/t. Jan–Mar 2025: $90, $90, $84/t | FY 2024-25 import CIF, all users (mostly power) | **91** |
| N2 | Ministry of Coal Monthly Statistical Report Mar 2025, Table 8.6 (p. 79): South Africa origin $79–100/t by port; Indonesia $43–86 | | Mar 2025, port price | 79–100 |
| N3 | NCI OM 06.03.2026, Table B, grades G4/G5/G6 (top non-coking incl. imported), Jan–Dec 2025 means ₹5,448 / 5,278 / 4,699 per t | | CY 2025, representative price, excludes rail freight to plant | **62 / 61 / 54** |

Indian coal-DRI kilns use low-ash imported (South African) or high-grade domestic coal. The model's emission factor (2.64 tCO₂/t, ≈24 GJ/t) matches import-grade coal, whose price is N1/N2 ($84–100). Domestic G4–G6 coal is cheaper ($54–62 before freight) but has lower calorific value (see ST-13). Fewer than three independent estimates for the import-grade coal the model implies → pessimistic upper bound ≈ $100; the current **98 is supported — keep**.

**PCI coal:** no admissible source found that prices PCI coal for India. The Ministry of Coal reports give PCI import *quantities* only (Mar 2025 report, Table 8.1: PCI 19.16 MT in FY 2024-25). The only bound from admissible data: PCI (a low-volatile coal sold below hard coking coal) lies between non-coking imports ($91) and top coking coal ($193–207). The current 110 is inside that bracket.

| Parameter | file:line | Current | Evidence (2025 USD/t) | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|
| ng_cost_ccoal | definitions.mod:178 | 184 (MC 100/250/400; regret central 250) | C1 193, C2 207, C3 200; range 175–260 | **200** central; MC levels **150 / 200 / 300** (or keep 100–400 as a stress range, but say so) | upper (cost) | NEEDS CALL (central differs between studies) |
| ng_cost_pcoal | definitions.mod:188 | 110 | no admissible source; bracket 91–207 | keep **110**, marked unsourced | upper | default (no admissible source) |
| ng_cost_ncoal | definitions.mod:191 | 98 | N1 91, N2 79–100 (import grade); N3 54–62 (domestic, ex-freight) | keep **98** | upper | default |

## B. Natural gas

Steel plants do not get APM gas (the government-priced domestic gas goes to city gas and fertiliser first). They buy regasified LNG (RLNG) or market-priced domestic gas, then pay regasification, pipeline tariff and taxes. The model parameter should be the **delivered** price.

| # | Source | Quote / data (page, table) | Boundary | 2025 USD/MMBtu |
|---|---|---|---|---|
| G1 | PPAC, *Ready Reckoner FY 2025-26*, Table 3.10 "Import of Liquefied Natural Gas" (p. 43) | "2024-25 … 14,908 [Mn USD] … 10.6 [USD/MMBtu]"; "2025-26 (P) … 13,356 … 9.8" | LNG import CIF unit value (DGCIS); **before** regas, transport, taxes | 10.9 (FY24-25), 9.8 (FY25-26) |
| G2 | PPAC Ready Reckoner FY 2025-26, Table 3.11 (pp. 44–45) | HP-HT gas price ceiling "April 2025 - September 2025 10.04", "October 2025- March 2026 9.72"; APM domestic gas capped at 6.75 | Ex-field domestic gas price; APM gas not allocated to steel | 9.7–10.0 (ceiling); 6.75 (APM) |
| G3 | Transition Asia & TERI (2026), input workbook `Model_input_India.xlsx`, sheet Commodities, row NG | "Delivered regasified LNG at the plant, anchored so that 2030 = USD 13.0/MMBtu, the middle of the USD 12-14 delivered term-contract band (PPAC, Argus)"; price_ref 11.7745, year 2025 | Delivered to plant, real 2025 USD | **11.8** |
| G4 | Ministry of Steel (2024) *Greening the Steel Sector*, Executive summary (pdf p. 26, printed p. 12) | "the average landed price of liquefied natural gas (LNG) in India is between 6-16 USD/MMBtu; the delivered price will be significantly higher"; pdf p. 24: "incumbent natural gas at 9.5 USD/MMBtu" | Landed LNG range; 9.5 = incumbent gas in their H₂ analysis (taken as USD 2023) | **10.0** (9.5 inflated); range 6–16 landed |
| G5 | Yadav, Guhan & Biswas (2021) *Greening Steel*, CEEW, pdf p. 16: "We consider an NG price of 13.5 USD/MMBtu"; pdf p. 37: "variation of NG price (6.7 to 13.5 $/MMBtu)" | | Delivered to plant (Karnataka case), USD 2021 | **15.8** (range 7.8–15.8) |

Three independent delivered estimates (G3 11.8, G4 10.0, G5 15.8): **median 11.8 → 12**. G1 (CIF ≈ 10–11) plus regasification and pipeline tariff supports a delivered price a little above 11. Range: **8–16** (low: domestic HP-HT gas at ~10 less a discount; high: G4 landed upper bound and G5).

The evidence supports **neither study central exactly**: core $10 is about the LNG import price *before* delivery costs; the regret study's $15 is in the upper part of the range. Proposed central **$12**. The Monte Carlo low of $5 is below any price an Indian steel plant pays (below even APM gas at $6.75, which steel cannot get); $25 is above anything in 2024–25 data.

| Parameter | file:line | Current | Evidence | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|
| n5_cost_NG | definitions.mod:201 | 10 (MC 5/15/25; regret central 15) | G3 11.8, G4 10.0, G5 15.8; CIF 9.8–10.9 | **12** central; MC levels **8 / 12 / 18** | upper (cost) — but note: higher gas price also makes NG-DRI less attractive vs coal, so "pessimistic for decarbonisation" is upper | NEEDS CALL (central differs between studies) |

## C. Ores and scrap

**Iron ore.** IBM's Average Sale Price (ASP) is the ex-mine price that royalty is charged on. Royalty and other levies, rail freight and GST come on top, so a delivered plant-gate price is higher than the ASP.

| # | Source | Quote / data | Boundary | 2025 USD/t |
|---|---|---|---|---|
| O1 | Indian Bureau of Mines, *Monthly Statistics of Mineral Production*, Table 6(a) "State wise Average Sale Price of minerals by Grades", India, Iron Ore, January 2025 issue (p. 2–3) | "62% To Below 65% Fe,Lumps 6,714"; "65% And Above Fe,Lumps 6,714"; "62% To Below 65% Fe,Fines 4,805"; "58% To Below 60% Fe,Fines 3,786"; "65% And Above Fe,Fines 5,605" (₹/t) | Jan 2025, all-India, ex-mine | lumps 77; fines 62–65 % 55; 58–60 % 43; ≥65 % 64 |
| O2 | IBM, same table, December 2025 issue | "62% To Below 65% Fe,Lumps 6,705"; "62% To Below 65% Fe,Fines 4,883"; "58% To Below 60% Fe,Fines 3,935"; "65% And Above Fe,Fines 5,125" | Dec 2025, all-India, ex-mine | lumps 77; fines 62–65 % 56; 58–60 % 45; ≥65 % 59 |
| O3 | Domínguez Bennett et al. (2026), IECC, pdf p. 15: "Iron ore fines 80 US$/t" (citing Pellet Manufacturers Association of India market prices, Sep 2025); international reference "101 US$/t for 62%Fe" | | 2025, India, purchased fines | **80** |
| O4 | Transition Asia & TERI (2026) workbook, sheet Ore_Price, Fines-Low: "CEIC, Odisha fines 58% Fe (about Rs 3,800/t) plus USD 10/t for grinding"; 53.52 | | 2025, low-grade fines, ex-mine + grinding | 54 |
| O5 | IEA (2020) *Iron and Steel Technology Roadmap*, pdf pp. 32 and 109 (figure notes): "Iron ore = USD 60-100/t" | | 2019, global | 74–124 (global context) |

Fine ore: three India estimates (O1/O2 IBM 55–56 for 62–65 % Fe, O3 80, O4 54) → median **56** ex-mine, but O1/O2/O4 exclude royalty, levies and freight while O3 is a market (purchase) price. The model value should be at the plant gate. The current **65** sits between the ex-mine median and IECC's purchase price — **keep 65**.
Lump ore: one source (IBM, 62 %+ Fe lumps ₹6,705–6,714 = **$77 ex-mine**, stable through 2025). The current $70 is below the ex-mine price alone. Pessimistic (upper) with one source: **$80** (ex-mine price rounded up; delivered would be higher still).

**Scrap.**

| # | Source | Quote / data | Boundary | 2025 USD/t |
|---|---|---|---|---|
| S1 | Ministry of Commerce, DGCIS Export-Import Data Bank (tradestat.commerce.gov.in), commodity-wise import, HS 72044900 "OTHER WASTE AND SCRAP" | FY 2024-25: US$ 3,060.79 million, 7,373,530,112 kg → $415/t | Import CIF unit value (heavy melting / shredded) | **426** (US GDP deflator 2024→25) |
| S2 | Same, FY 2025-26 | US$ 2,407.79 million, 6,360,790,016 kg → $379/t | Import CIF | **379** |
| S3 | Transition Asia & TERI (2026) workbook, sheet Commodities, Scrap: price_ref 402, "JPC and BigMint price assessments, 2025" | | 2025, India, delivered steel scrap | **402** |
| S4 | IEA (2020), pdf pp. 32 and 109: "Scrap = USD 200-300/t" | | 2019, global | 248–372 (global context) |

S1 and S2 are the same series in two years, so they count as one estimate (2025 ≈ $400). Median of S1/S2 average (~400) and S3 (402): **400**. Domestic heavy-melting scrap in India trades at about import parity, so the import value is a fair proxy. Range for Monte Carlo: **300 / 400 / 500** (the S1–S3 spread is 379–426; 2022 was higher).

| Parameter | file:line | Current | Evidence (2025 USD/t) | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|
| ng_cost_fineore | definitions.mod:183 | 65 | O1/O2 55–56 ex-mine; O3 80; O4 54 | keep **65** | upper | default |
| ng_cost_lumpore | definitions.mod:187 | 70 | O1/O2 77 ex-mine | **80** | upper | default |
| ng_cost_scrap | definitions.mod:190 | 350 (MC 250/350/450) | S1 426, S2 379, S3 402 | **400**; MC **300 / 400 / 500** | upper (costlier scrap hurts scrap-EAF) | NEEDS CALL (moves scrap-EAF economics and the Monte Carlo) |

## D. Fluxes, biochar, electrodes

**Lime / limestone.** The model uses one price for "lime" in sinter (0.04 t/t), BF (0.025 t/tHM), BOF (`n3_ls_bof` 0.075, commented "Limestone") and EAF (`n7_ls`/`n8_ls` 0.06, "Limestone"). In practice sinter and BF take raw limestone/dolomite and BOF/EAF take burnt lime, which costs several times more per tonne.

| # | Source | Quote / data | Boundary | 2025 USD/t |
|---|---|---|---|---|
| L1 | IBM *Monthly Statistics of Mineral Production*, Table 6(a), India, Limestone, Jan 2025 | "LD Grade (Less Than 1.5% Silica Content) 2,921"; "SMS 614"; "BF 703" (₹/t) | Ex-mine | LD 34; SMS 7; BF 8 |
| L2 | IBM, same, Dec 2025 | "LD Grade … 3,553"; "SMS 606"; "BF 887" | Ex-mine | LD 41; SMS 7; BF 10 |
| L3 | Transition Asia & TERI (2026) workbook, Commodities, "Burnt Limestone" 33.5 $/t, "India, Q2 2025 (IMARC Group price report)" | | 2025 | 33.5 (equals IBM LD-grade ex-mine, so probably limestone, not burnt lime) |

No admissible source found for a delivered **burnt-lime** price in India. All admissible values (7–41) are ex-mine limestone and lie below the current $60, which leaves room for freight and some calcination. Keep **60** (it is already the upper bound of the evidence). The burnt-lime/limestone mix is a structural point (below).

**Biochar / biomass.** The parameter is commented "Cost per ton of biomass", but it prices `sinter_biochar_in` (biochar) and `bf_biopci_in` ("Biomass injection"). The quantities are fixed paths (0 in 2025 → 0.022 t/t sinter and 0.053 t/tHM in 2050), so the price changes BF-BOF cost in later years but not route choice directly.

| # | Source | Quote | Boundary | 2025 USD/t |
|---|---|---|---|---|
| B1 | Ibitoye et al. (2024) "An overview of biochar production techniques and application in iron and steel industries", *Bioresources and Bioprocessing* 11:65, doi:10.1186/s40643-024-00779-z (text beside Fig. 12, citing Meng et al. 2024) | "Steel-used coke and coal cost about 1322 yuan/t in China, while wood-based and straw-based biochar cost 3500 yuan/t and 3787 yuan/t, respectively." | China, ~2023, biochar | **520–563** (CNY at 2023 FRED AEXCHUS 7.0809, then US GDP deflator) — global fallback |

No admissible Indian source found for biochar or pulverised biomass for injection. With one (non-Indian) source the pessimistic rule gives about **$520/t** for biochar. $60 is plausible only for raw biomass, which cannot be injected or sintered as is.

**Graphite electrodes.**

| # | Source | Quote / data | Boundary | 2025 USD/t |
|---|---|---|---|---|
| E1 | DGCIS Export-Import Data Bank, HS 85451100 "ELECTRODES OF A KIND USED FOR FURNACES", **exports** | FY24-25: US$ 217.12 million, 78,328,890 kg ($2,772/t); FY25-26: US$ 252.81 million, 95,013,147 kg ($2,661/t) | FOB unit value of Indian-made electrodes (Graphite India, HEG) | 2,845 / 2,661 → ~2,750 |
| E2 | DGCIS, same HS code, **imports** | FY24-25: US$ 35.30 million, 14,379,100 kg ($2,455/t); FY25-26: US$ 25.86 million, 10,774,200 kg ($2,400/t) | CIF unit value | 2,520 / 2,400 → ~2,460 |
| E3 | Transition Asia & TERI (2026) workbook, Commodities, Electrode 2500, "UHP graphite electrode, 2025 (IMARC Group price report)" | | 2025 | 2,500 |

Three estimates (≈2,750, 2,460, 2,500): **median 2,500**. The current 3,000 is above the range; the effect is small (0.003 t/tCS × $500 ≈ $1.5/tCS).

| Parameter | file:line | Current | Evidence (2025 USD/t) | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|
| ng_cost_lime | definitions.mod:184 | 60 | L1/L2 ex-mine limestone 7–41; L3 33.5; no burnt-lime source | keep **60** | upper | default |
| ng_cost_biochar | definitions.mod:185 | 60 | B1 520–563 (China, biochar); no Indian source | **520** if the input is biochar; keep 60 only if it is raw biomass | upper | NEEDS CALL |
| n7_cost_electrode | definitions.mod:206 | 3,000 | E1 ~2,750, E2 ~2,460, E3 2,500 | **2,500** | upper | default |
| n8_cost_electrode | definitions.mod:208 | 3,000 | same | **2,500** | upper | default |

## E. By-product credits

All trade figures below are from the DGCIS Export-Import Data Bank (Ministry of Commerce, tradestat.commerce.gov.in, "Commodity-wise" import/export, 8-digit ITC-HS), FY 2024-25 and FY 2025-26 (the latter as published on 6 Oct 2026). Unit value = US$ value ÷ quantity; FY 2024-25 is inflated with the US GDP deflator.

| # | HS code, flow | Data | 2025 USD/t |
|---|---|---|---|
| T1 | 27060010 "COAL TAR", exports | FY24-25: US$ 3.43 million, 6,090,495 kg; FY25-26: US$ 3.03 million, 5,023,029 kg | 578; 603 |
| T2 | 27060010 "COAL TAR", imports | FY24-25: US$ 0.24 million, 504,390 kg; FY25-26: US$ 0.10 million, 232,640 kg | 488; 430 |
| K1 | 26180000 "GRNULATD SLAG(SLAG SAND) FROM IRON/STEEL", imports | FY24-25: US$ 9.31 million, 644,280,000 kg; FY25-26: US$ 10.61 million, 795,795,008 kg | 14.8; 13.3 |
| K2 | 26180000, exports | FY24-25: US$ 11.87 million, 1,079,361,401 kg; FY25-26: US$ 15.36 million, 1,634,187,640 kg | 11.3; 9.4 |
| M1 | 27040090 "OTHER COKES OF COAL" (metallurgical coke), imports | FY24-25: US$ 1,421.06 million, 4,606,790,144 kg; FY25-26: US$ 1,107.31 million, 4,351,370,240 kg | 317; 255 (upper bound for coke breeze, which is undersize coke) |

- **Coal tar.** The current credit of $20/t is about 20–30 times below every trade unit value ($430–603). Tar volumes in trade are small, but buyers (tar distillers) pay these prices. There are two flows (fewer than three independent estimates), so the pessimistic lower bound applies: **$430**. Effect: 0.04 t tar/t coke, so roughly +$6/tHM credit to BF-BOF. Note that a larger by-product credit makes BF-BOF cheaper. "Pessimistic" here follows the brief (lower bound for credits), but it does not make decarbonisation look harder.
- **Slag.** Granulated BF slag (sold to cement) trades at $9–15/t. The current $15 is at the top. Lower bound **$10**. The model applies the same credit to BF, BOF and EAF slag. BOF/EAF slag sells for less than granulated BF slag, so one price for all three flatters BOF and EAF slightly.
- **Coke breeze (credit 55, purchase 85).** No admissible source found that prices coke breeze in India. The only bound: metallurgical coke imports at $255–317/t, of which breeze is the low-value undersize fraction. Keep both values, marked unsourced. The 85/55 spread (buy dearer than sell) can be justified by handling and logistics, but it is undocumented. See ST-04: the bought-in breeze also carries no CO₂.

| Parameter | file:line | Current | Evidence (2025 USD/t) | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|
| n0_credit_tar | definitions.mod:193 | 20 | T1 578–603; T2 430–488 | **430** | lower (credit) | default (large relative change, small absolute effect) |
| ng_credit_slag | definitions.mod:189 | 15 | K1 13–15; K2 9–11 | **10** | lower (credit) | default |
| n0_credit_breeze | definitions.mod:192 | 55 | no admissible source; bound < 255–317 (met coke) | keep **55** | lower (credit) | default (no admissible source) |
| n1_cost_breeze | definitions.mod:195 | 85 | no admissible source; bound < 255–317 | keep **85** | upper (cost) | default (no admissible source) |

## F. Grid electricity tariff

| # | Source | Quote / data | Boundary | 2025 USD/kWh |
|---|---|---|---|---|
| P1 | CEA (2026) *Electricity Tariff & Duty and Average Rates of Electricity Supply in India*, as on 31 March 2025, Table 7(h) "LARGE INDUSTRIES 50000 KW 60% LF (21900000 Unit/Month) (AT 33 KV)" (pdf p. 231) | Total (paise/kWh, incl. duty) in the main steel states: Odisha (132 kV) 690, Chhattisgarh 939, Jharkhand (132 kV) 859, Karnataka 836, Maharashtra 1239, Gujarat 632, West Bengal (132 kV) 888, Andhra Pradesh 830. Median 847.5 (incl. duty), 764 (average rate, excl. duty) | HT industrial grid supply, tariffs effective 2024 (inflated with WPI 2024→25) | **0.098** incl. duty (range 0.073–0.143); 0.088 excl. duty |
| P2 | CEA (2026), same, Table 8(b) "POWER INTENSIVE INDUSTRIES 50000 KW 80% LF" (pdf p. 232) | Odisha (11/33 kV) 561, Chhattisgarh (132 kV) 813, Andhra Pradesh 707, Maharashtra 1202 | Power-intensive category, where a state has one | 0.065–0.139 (context) |
| P3 | Transition Asia & TERI (2026) workbook, sheet Grid: "APERC retail tariff for high-tension industrial consumers, real 2025 USD"; 2025 0.0717, 2030 0.0745, 2050 0.0765 | | Andhra Pradesh HT, real 2025 | **0.072** |
| P4 | Domínguez Bennett et al. (2026), IECC, Table S-1 (pdf p. 33): "Grid electricity (dry hours) US$/MWh 90" for 2030 and 2035 | | India, grid top-up for H₂/EAF | **0.090** |
| P5 | Yadav, Guhan & Biswas (2021), CEEW, pdf p. 16: "a grid power cost of 7.6 INR/kWh" (Bellary, Karnataka) | | Karnataka HT, 2021 | **0.100** |
| — | Åhman & Arens (2024), *Utilities Policy* 91 (cited by the paper) | Paywalled; not read, so no number is used | | — |

Four estimates (P1 0.098, P3 0.072, P4 0.090, P5 0.100): **median 0.094 → 0.095 $/kWh**. The current 0.07 is at the bottom of the range (only Gujarat and Odisha tariffs, or the AP-based P3, are that low). Caveat: about two-thirds of the electricity of Indian integrated plants comes from captive coal plants, which cost less than grid power (register ST-06). The model prices all purchased power at the grid tariff, so a grid tariff is the right input for *new* electric routes.

**2050 "fast" end-point (0.055).** No admissible source projects a falling real industrial tariff: P3 rises slightly (0.072 → 0.077 by 2050), and P4 holds 90 $/MWh flat to 2035. 0.055 is a scenario assumption (tag A). If it is kept, the same −21 % relative fall from the new start gives **0.075**.

| Parameter | file:line | Current | Evidence | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|
| grid_price_start | definitions.mod:148 | 0.07 | P1 0.098, P3 0.072, P4 0.090, P5 0.100 | **0.095** | upper (cost; also penalises the electric routes) | NEEDS CALL |
| grid_price_end_fast | definitions.mod:149 | 0.055 | no source for a decline; P3 0.077 in 2050 | **0.075** (keeps the −21 % scenario) or = start (no decline) | upper | NEEDS CALL (part of the grid-tariff call) |

## Structural notes

IN PROGRESS

## Bibliography

IN PROGRESS
