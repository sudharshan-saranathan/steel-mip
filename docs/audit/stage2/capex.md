# Stage 2 — Capital cost (ST-01)

All values are **up-front capex per tonne of yearly crude-steel capacity, in constant 2025 USD**, for **greenfield** builds (ST-01a).
Conversions are done by `convert_2025usd.py`:

- **Rupee sources:** inflated with India's all-commodities WPI (base 2011-12), then converted at the 2025 average rate of ₹87.16/$.
- **Dollar sources:** inflated with the US GDP deflator.

The input data are in this folder: `wpi_cal.xls` (Office of the Economic Adviser), and `GDPDEF.csv` and `EXINUS.csv` (FRED).

## BF-BOF

| Source | Kind | 2025 USD/t | Use |
|---|---|---|---|
| IEA (2020) *Iron and Steel Technology Roadmap*, p. 46, fn 15: "CAPEX for all equipment required to provide 1 Mt of annual capacity (including agglomeration, coke ovens etc.) is around USD 1–1.5 billion" | think tank, global | 1,240–1,860 | context |
| IEA (2020), Fig. 1.3 notes: annualised CAPEX USD 52–94/tCS at 8 %, 25 yr, 90 % utilisation, converted back to up-front | think tank, global | 620–1,120 | context |
| Domínguez Bennett, Jain, Chojkiewicz, Abhyankar & Phadke (2026) *Economic Case for Green Steel Production in India*, UC Berkeley IECC, Table S-4: "BF-BOF CAPEX 800 US$/t" | university report, India | 800 | lower anchor |
| Yadav, Guhan & Biswas (2021) *Greening Steel*, CEEW, p. 7: green plant "USD 3 Billion per MTPA – more than three times the conventional BF-BOF route" | think tank, India | < 1,220 | upper anchor (a ceiling, not an estimate) |
| Tata Steel press release, 12 Nov 2018: Kalinganagar phase II, ₹23,500 cr for +5 Mtpa | company, brownfield | 700 | sensitivity only |
| JSW Steel Integrated Report 2021-22: Vijayanagar +5 Mtpa, ₹20,000 cr (+ ₹5,000 cr sinter and support) | company, brownfield | 530–660 | sensitivity only |
| Model before the fix (200 / CRF) | | 2,557 | — |

**Adopted: $1,200/t** (decision 2026-10-06, replacing an interim $1,000). This is a rounded **upper bound**: just below the CEEW ceiling (< $1,220), above the IECC estimate ($800), and at the bottom of IEA's global full-plant range ($1,240–1,860). There are too few independent Indian estimates to apply the median rule, so the paper should cite these anchors.

**Selection rule (decision 2026-10-06):** where evidence is thin, take the bound that makes decarbonisation look harder, so the bias runs in one known direction. For capex and prices that is the upper bound. For efficiencies and recovery rates it is the lower bound. The direction is recorded per parameter. Caveat for the paper: the bound applies to total cost; route choice can still shift, because routes with wider evidence ranges are penalised more.

Sensitivity: brownfield values ($530–700/t) give a low-capex case.

## DRI and scrap routes (decisions 2026-10-06)

Node evidence (2025 USD):

| Node | Unit | Transition Asia & TERI (2026), India¹ | Vogl, Åhman & Nilsson (2018)² | Yadav et al. (2021), CEEW³ | Pick |
|---|---|---|---|---|---|
| Shaft furnace (NG, H₂) | $/t DRI-yr | 345 (414 with 1.2× owner's cost) | 415 | 328 | 415 |
| Rotary kiln (coal) | $/t DRI-yr | 300 (360 with owner's cost) | — | — | 360 (single source) |
| EAF incl. casting | $/t CS-yr | 337 (404 with owner's cost) | 332 | 183 | 400 |

¹ *Is Green Steel Within Reach in India?* (Transition Asia & TERI, 2026); input workbook `india/data/Model_input_India.xlsx`, sheet Tech, real 2025 USD. Owner's-cost factor `CAPEX_OVERFACTOR = 1.2` (`model/config.py`). Economic life 40 yr for all four units.
² *J. Cleaner Production* 203:736–745. Euro values from Wörtler et al. (2013), converted at the 2013 USD/EUR rate (1.328) and the US GDP deflator (factor 1.806). The same paper gives greenfield BF-BOF at €442/t ≈ $800, consistent with IECC.
³ Values from IEA (2010), USD 2010.

Decisions: include the owner's-cost factor (yes); give H₂-DRI the **same** shaft-furnace cost as NG-DRI (no premium; Vogl and Transition Asia–TERI treat the two as the same unit); cost scrap-EAF at the same EAF unit cost as in the DRI routes, because scrap collection and processing is charged separately through `ocapex_scrapchain`.

Converted to per tonne of crude steel at 1.1 t DRI per tCS (the metallic charge `n7_dri_ratio`, assuming no scrap):

| Parameter | Node | Before (treated as annualised) | Adopted (2025 USD per t CS-yr, up-front) |
|---|---|---|---|
| `n4_capex_coal` | coal rotary kiln | 110 | **400** |
| `n5_capex_ng` | NG shaft furnace | 90 | **460** |
| `n6_capex_h2` | H₂ shaft furnace | 120 → 90 (2025 → 2050) | **460**, constant |
| `n7_capex` | EAF (DRI routes) | 70 | **400** |
| `n8_capex` | EAF (scrap route) | 70 | **400** |
| `ng_capex_pell` | pellet | 10 | **60** (see BF-BOF split) |

Resulting route capex (2025 USD/t CS-yr): coal-DRI-EAF **860**, NG-DRI-EAF **920**, H₂-DRI-EAF **920** (plant only; the electrolyser and renewables are costed separately), scrap-EAF **400**, plus scrap-chain capex. Before the fix: 2,179 / 1,950 / 2,557 / 680.

Route-level checks: IEA (2020) NG-DRI-EAF 630–1,620 and scrap-EAF 405–690 (global); IECC (2026) H₂-DRI-EAF 670; Vogl (2018) H₂-DRI-EAF without electrolyser ≈ 750.

Caveat: Indian coal-DRI is mostly paired with induction furnaces, which cost less than EAFs. Costing it with an EAF is pessimistic, in line with the selection rule.

## BF-BOF node split (decision 2026-10-06)

The current proportions (40 : 30 : 10 : 80 : 40) are kept, scaled to $1,200:

| Parameter | Node | Before | Adopted (2025 USD/t-capacity, up-front) |
|---|---|---|---|
| `n0_capex` | coke oven | 40 | **240** |
| `n1_capex` | sinter | 30 | **180** |
| `ng_capex_pell` | pellet (shared with the DRI routes) | 10 | **60** |
| `n2_capex` | blast furnace | 80 | **480** |
| `n3_capex` | BOF | 40 | **240** |
| | **total** | 200 (treated as annualised) | **1,200** |

Note: IEA (2020, p. 46) puts the blast furnace alone at USD 200–300 million per Mt (≈ $250–370/t in 2025 USD), below the $480 here. Only the total affects route choice. The pellet node also enters the DRI routes.
