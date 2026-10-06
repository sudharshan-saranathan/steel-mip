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

## Other routes (evidence so far; no values adopted yet)

| Route | Model before fix | Evidence (2025 USD/t) |
|---|---|---|
| NG-DRI-EAF | 1,950 | IEA 2020: 630–1,620 (global) |
| H₂-DRI-EAF | 2,557 (2025) | IECC 2026: 670; CEEW 2021: 510 (shaft furnace + EAF, from IEA 2010 data) |
| Scrap-EAF | 680 | IEA 2020: 405–690 (global) |
| Coal-DRI-EAF/IF | 2,179 | none found yet |

## Open item

The node split for BF-BOF (`n0` coke, `n1` sinter, `ng` pellet, `n2` BF, `n3` BOF) is still to be decided. IEA (2020, p. 46) puts the blast furnace alone at USD 200–300 million per Mt, which is 20–25 % of its full-plant figure. The current model gives the BF 40 % (80 of 200).
