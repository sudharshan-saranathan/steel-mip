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

IN PROGRESS

## D. Fluxes, biochar, electrodes

IN PROGRESS

## E. By-product credits

IN PROGRESS

## F. Grid electricity tariff

IN PROGRESS

## Structural notes

IN PROGRESS

## Bibliography

IN PROGRESS
