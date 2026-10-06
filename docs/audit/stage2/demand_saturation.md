# Stage 2: Logistic crude-steel demand curve (population × per-capita saturation)

Status: complete (2026-10-06). Purpose: parametrise `D(t) = D_sat / (1 + A·e^(−k(t−2025)))`, with `A = D_sat/D_2025 − 1`, for India over 2025–2050, so that demand levels off after 2050. This sheet sits next to `demand_fleet_opex.md` §A, which holds the constant-growth evidence. "Finished" means finished-steel apparent use and "crude" means crude-steel production. Every value I computed is marked *(calc)*.

## Needs your call

1. **D_sat level.** (a) Central: **680 Mt** (400 kg crude/cap × 1,701 M); (b) low: **510 Mt** (300 kg/cap); (c) high: **816 Mt** (480 kg/cap, NITI-consistent). The rule for the 2050 projections (≥3 estimates → median) gives roughly the central value. The pessimistic bound (higher demand = harder) is the high value.
2. **Curve steepness k.** (a) Anchor k so that demand reaches 90 % of D_sat in **2060** (around the UN population peak, 2061). The first-year growth this implies (6–9 %) matches FY22–FY25 actuals (8.2 %/yr). (b) Anchor k on 7 %/yr initial growth. That plateaus later (90 % only in 2056–2068), and for the high and central cases demand is still climbing steeply in 2050.

## 1. Population: UN World Population Prospects 2024, India (LocID 356)

Source P1: UN DESA (2024), file `WPP2024_TotalPopulationBySex.csv.gz`, column `PopTotal` (thousands, 1 July), variants Medium/Low/High. Read directly from the CSV. Boundary: de facto population of India.

| Year | Medium (million) | Low (million) | High (million) |
|---|---|---|---|
| 2025 | 1,463.9 | 1,459.5 | 1,468.2 |
| 2030 | 1,525.1 | 1,503.6 | 1,546.7 |
| 2035 | 1,578.7 | 1,532.0 | 1,625.4 |
| 2040 | 1,622.6 | 1,547.2 | 1,697.9 |
| 2045 | 1,656.1 | 1,552.9 | 1,759.3 |
| 2047 | 1,666.6 | — | — |
| 2050 | 1,679.6 | 1,548.0 | 1,812.4 |
| 2060 | 1,701.0 | 1,502.1 | 1,913.7 |
| 2070 | 1,689.2 | 1,411.9 | 2,005.1 |
| **Peak** | **2061: 1,701.3** (1,701.0 in 2060) | 2045: 1,552.9 | no peak by 2100 (2,196.9 in 2100) |

Cross-check against Government of India figures, which are lower:

| Source | Quote (page) | Value |
|---|---|---|
| NITI Aayog (2026), Annexure I, Table I.1 | "Population (millions) 1347 [2020] 1411 [2025] 1596 [2050] 1621 [2075]" (p. 124) | 2050: 1,596 M, which is 5 % below UN medium |
| MoS *Annual Report 2025-26* | 152.129 Mt ÷ 108.0 kg/cap (pp. 15, 78) | MoS's per-capita figure implies 1,409 M *(calc)* |

Using UN medium for D_sat is the pessimistic choice: more people means more demand.

## 2. India now: consumption vs crude-steel production (JPC)

| # | Source | Quote (page) | Value |
|---|---|---|---|
| N1 | MoS *Annual Report 2025-26*, §3.2.1 (JPC) | "2024-25 146.688 [production] 9.551 [import] 4.858 [export] 152.129 [consumption]" (finished steel, alloy + non-alloy) (p. 15) | FY25 finished consumption **152.129 Mt**; production 146.688 Mt |
| N2 | MoS *Annual Report 2025-26*, §3.2.2 (JPC) | Crude steel production "2021-22 … 120.293; 2022-23 … 127.197; 2023-24 … 144.299; 2024-25 … 152.180" (p. 16) | FY22–FY25 crude steel |
| N3 | PIB (5 May 2026) | "India has already achieved 168 MTPA of crude steel production in FY 2025-26" (p. 7) | FY26 ≈ 168 Mt |
| N4 | MoS *Annual Report 2025-26*, §10.2.1 | "The per capita consumption for 2023-24 and 2024-25 is 97.7 kg and 108.0 kg respectively" (p. 78); "India was a net importer of Finished Steel in 2024-25" (p. 16) | **108.0 kg finished/cap** (FY25) |
| N5 | NITI Aayog (2026) *Industry*, ch. 2 | "per capita finished steel consumption in India remains modest at about 98 kg in 2023–24 (rising to 102.6 kg in 2024–25)" (p. 13) | 102.6 kg (this matches the worldsteel calendar-2024 figure) |
| N6 | worldsteel (2025) *World Steel in Figures 2025*, "Apparent steel use per capita" | "kilograms, finished steel products … India 64.0 75.5 82.0 93.0 102.6" (2020–2024) (p. 17) | 102.6 kg (CY2024) |

Ratios for FY2024-25 *(calc)*:
- Finished consumption ÷ crude production = 152.129 / 152.180 = **1.00**. The match is a coincidence of net imports (+4.7 Mt finished) offsetting the yield loss.
- Finished production ÷ crude production = 146.688 / 152.180 = **0.964**. So a closed economy needs ≈ **1.037 t crude per t finished use**. World 2024: 1,742.4 Mt finished ASU (WSIF p. 17) ÷ 1,884.6 Mt crude (WSIF p. 9) = 0.925, or 1.08 crude per finished.
- FY25 consumption per head on UN population: 152.129 / 1,463.9 (2025) = **104 kg** *(calc)*. The MoS's 108 kg uses a lower population.
- Crude-steel CAGR: FY22–FY25 **8.2 %/yr**; FY22–FY26 8.7 %/yr; FY25–FY26 +10.4 % *(calc)*.

## 3. Per-capita saturation evidence

### 3.1 Apparent steel use per capita today (finished steel, kg/cap; worldsteel WSIF 2025, p. 17)

| Economy | 2020 | 2021 | 2022 | 2023 | 2024 | Crude-equivalent 2024 (×1.037) *(calc)* | Note |
|---|---|---|---|---|---|---|---|
| World | 228.4 | 233.1 | 223.1 | 221.1 | 214.7 | 223 | |
| United States | 238.3 | 288.1 | 279.4 | 266.3 | 260.6 | 270 | mature; net indirect importer |
| European Union (27) | 293.7 | 346.1 | 318.8 | 289.0 | 290.7 | 301 | mature |
| Germany | 376.1 | 425.7 | 390.4 | 339.7 | 312.7 | 324 | net indirect exporter |
| Japan | 420.2 | 460.7 | 443.6 | 433.4 | 419.0 | 435 | net indirect exporter |
| Türkiye | 350.4 | 393.7 | 380.8 | 443.2 | 443.6 | 460 | |
| China | 707.9 | 669.3 | 649.9 | 634.9 | 601.1 | 623 | past peak; largest net indirect exporter |
| South Korea | 948.9 | 1,081.2 | 990.0 | 1,012.6 | 923.5 | 958 | shipbuilding/export outlier |
| India | 64.0 | 75.5 | 82.0 | 93.0 | 102.6 | 106 | |

Quote: "Apparent steel use per capita 2020 to 2024 … kilograms, finished steel products" (WSIF 2025, p. 17). On indirect trade, WSIF ranks the net indirect exporters (2019): "China 86.4 … Japan 13.9 … South Korea 12.7 … Mexico 9.1 … Germany* 7.2" Mt (p. 28). The apparent-use figures for these countries therefore overstate domestic need.

### 3.2 Stock-saturation and other literature

| # | Source | Quote (page) | Implication |
|---|---|---|---|
| S1 | Pauliuk, Wang & Müller (2013) *Resour. Conserv. Recycl.* 71:22–30 (self-archived revision) | "We identify the range of saturation to be 13±2 tonnes for the total per capita stock, which includes 10±2 tonnes for construction, 1.3±0.5 tonnes for machinery, 1.5±0.7 tonnes for transportation, and 0.6±0.2 tonnes for appliances and containers" (abstract, p. 3); Table 6, "Total 13± 2 (rounded from 13.4±2)" (p. 20) | saturated in-use stock 11–15 t/cap |
| S2 | Pauliuk et al. (2013), Table 4 | Base lifetimes "Transportation 20, Machinery 30, Construction 75, Products 15 … base value (Müller et al. 2011)"; alternatives with construction 50 or 100 years (p. 13) | Replacement flow at saturation = Σ stock/lifetime ≈ **292 kg/cap·yr** of end-use steel (base); 258 (construction 100 yr) to 358 (construction 50 yr) *(calc)*. End-use excludes fabrication scrap, so crude need is higher |
| S3 | IEA (2020) *Iron and Steel Technology Roadmap*, ch. 1 | "the stock of steel in society tends to increase markedly until it reaches a level of 8-16 tonnes per capita (Pauliuk and Müller, 2013). At this level, the stock of steel in advanced economies tends to saturate" (p. 32) | 8–16 t/cap |
| S4 | IEA (2020), ch. 2 | "in-use stock per capita remaining relatively constant at around 10-15 t/capita on average in, for example, the United States and many European countries" (p. 57); "Korea's annual apparent use is more than 1 t/capita – compared to a global average of 0.25 t/capita and around 0.35 t/capita in the European Union"; "advanced economies saturate at much more consistent levels" on a true-use basis (p. 58). The note to the 2019 figure says "All data are shown in terms of crude steel equivalent" (p. 33) | EU ≈ 350 kg crude-eq/cap (2018); world 250 |
| S5 | NITI Aayog (2026) *Industry*, §3.1 and §3.2.1 | "A saturation-growth (logistic S-curve) is used for stock-building materials — steel …" (p. 61); "Using a logistic S-curve with an assumed saturation around 450 kg/capita (peak levels observed in developed economies), India's total crude steel production is projected to rise from 144.29 Mt in 2024 to 624 Mt by 2050 and 821 Mt by 2070" (p. 63); "per-capita use is projected to converge toward high-income norms, reaching ~356 kg steel … by 2050" (p. xxi) | **450 kg/cap saturation**, the only Indian GoI saturation parameter found. Its basis (crude or finished) is not stated |
| S6 | National Steel Policy 2017, in MoS *Annual Report 2025-26* | "Per Capita Finished Steel Consumption (in KGS) 158" for 2030-31 (p. 23). IEA (2020) quotes it as "160 kilogrammes (kg)" (p. 127); PIB (2026) as "158 kg from the current 61 kg" (p. 7) | target, finished, 2030-31 |
| S7 | Ministry of Steel (2024) *Roadmap*, §1.3.3 | "Developed countries have reached a plateau in their per capita steel consumption … Conversely, India has a lower per capita steel consumption" (p. 40) | qualitative only; no number |

No India-specific peer-reviewed saturation study could be downloaded and read: OpenAlex and Crossref searches gave none, and the OpenAlex quota ran out. Müller et al. (2011, *ES&T* 45:182) is closed access, so it is cited only through S2. No admissible MPP, BNEF or CEEW India 2050 crude-steel number was found in the sources I read. The CEEW (2021) *Greening Steel* report gives only a statement about present capacity: "~130 million tonnes (MT) … can only support a per capita steel consumption of ~70 kilograms compared with a global average of 224".

## 4. Indian 2047/2050/2070 projections and their implied per-capita level

Per-capita values divide by UN medium population: 2047 1,666.6 M; 2050 1,679.6 M; 2070 1,689.2 M *(calc)*.

| # | Source | Quote (page) | Year | Crude Mt | kg crude/cap *(calc)* |
|---|---|---|---|---|---|
| J1 | MoS (2024) *Roadmap* (TERI) §15 | "197 MT by 2030, 374 MT by 2050 and 540MT by 2070" (p. 347) | 2050 / 2070 | 374 / 540 | 223 / 320 |
| J2 | IEA (2020) ISTR, STEPS | "almost doubling by 2030 and quadrupling by 2050" (p. 118), from 111 Mt in 2019 | 2050 | ≈ 444 | 264 |
| J3 | IEA (2021) *India Energy Outlook 2021*, STEPS | "steel and cement production in India in the STEPS nearly triples by 2040" (p. 84); "demand for steel nearly triples" (p. 69) | 2040 | ≈ 3 × 2019 | — |
| J4 | NITI Aayog (2026) *Industry* | 624 Mt in 2050 and 821 Mt in 2070 (p. 63, quoted in S5) | 2050 / 2070 | 624 / 821 | 372 (391 on NITI's own 1,596 M) / 486 |
| J5 | TERI (2021) *DRI* report (citing others; pages carried over from `demand_fleet_opex.md`) | "steel demand projected to reach between 500 and 760 million tonne (Mt) by 2050" (p. 37) | 2050 | 500–760 | 298–452 |
| J6 | TERI (2021), low-carbon (page carried over) | "the steel demand will rise to around 300 million tonne by 2050" (p. 53) | 2050 | 300 | 179 |
| J7 | PIB (5 May 2026) | "India is working towards achieving 500 MT of steel production capacity by 2047" (p. 2). GEM (2026) gives the same: "500 MT in 2047" (p. 28) | 2047 capacity | 500 cap (≈ 400 at 80 % utilisation) | 300 cap / 240 production |
| J8 | MoS *Annual Report 2025-26* §10.3 | "India's total steel demand is expected to reach ~230 MT by FY 31" (p. 79) | FY31 finished | ≈ 239 crude (×1.037) | 157 |
| — | Current model (5 %/yr) | `definitions.mod:4` | 2050 | 515 | 307 |

Median of the three independent 2050 projections (J1, J2, J4) is 444 Mt, or 264 kg/cap. The 2070 values show where the producers expect the plateau: MoS/TERI 320 kg/cap and NITI 486 kg/cap, both still rising in 2070.

## 5. Proposal

D_sat = per-capita saturation (crude steel) × plateau population. The plateau population is the UN medium peak, **1,701 M (2061)**. The logistic is calibrated with D(2025) = 152.2 Mt (JPC FY25) and k set so that D reaches 90 % of D_sat in 2060 (`k = ln(9A)/35`) *(calc)*.

| Case | kg crude/cap | D_sat (Mt) | k (/yr) | Implied growth, 2025→26 | D 2030 | D 2040 | D 2047 | **D 2050** | D 2060 |
|---|---|---|---|---|---|---|---|---|---|
| Low | 300 | **510** | 0.087 | 6.2 % | 202 | 312 | 379 | **403** | 459 |
| Central | 400 | **680** | 0.098 | 7.8 % | 218 | 379 | 486 | **524** | 612 |
| High | 480 | **816** | 0.105 | 8.8 % | 228 | 428 | 569 | **620** | 734 |

Why these levels:
- **Low, 300 kg (510 Mt).** This is today's mature-economy level without the export-driven outliers: EU-27 at 291 kg finished (301 crude-eq) and the US at 261 (270). It is also the stock-replacement flow at saturation (S1 + S2: ≈ 290 kg/cap end-use, base lifetimes) and the MoS/TERI 2070 level (J1: 320 kg/cap). India is a large, dense, construction-heavy economy, so this is the floor of the plausible range.
- **Central, 400 kg (680 Mt).** This sits between Germany and Japan today (313–419 kg finished, 324–435 crude-eq). It equals the upper stock-replacement case (358 kg end-use with 50-year building life) plus fabrication losses. It brackets NITI's 2050 per-capita figure (372–391 kg). Its 2050 value (524 Mt) is close to the current model's 515 Mt and between the IEA (444) and NITI (624). Its initial growth (7.8 %) matches FY22–FY25 actuals (8.2 %/yr).
- **High, 480 kg (816 Mt).** This is NITI's stated 450 kg/cap saturation, raised by the India finished-to-crude yield of 1.037 to 467 kg and rounded up to match NITI's own 2070 figure (821 Mt = 486 kg/cap). Its 2050 value (620 Mt) reproduces NITI's 624 Mt. This is the pessimistic bound: higher demand makes decarbonisation harder.

**Implied 2050 demand range: 403–620 Mt (central 524 Mt).** This matches the independent projections (374–624 Mt) closely, apart from the MoS/TERI 374 Mt, which is still on the steep part of its curve in 2050.

Sensitivities *(calc)*:
- Anchoring k on 7 %/yr initial growth instead gives 2050 = 427 / 499 / 541 Mt, and the 90 % point moves to 2056 / 2063 / 2068.
- Using the UN low population (1,553 M peak, 2045) cuts D_sat by 9 %.
- Using NITI's population (1,596 M in 2050) cuts D_sat by about 6 %.

## Structural notes

- Under the logistic form, `growth_rate` is replaced by (D_sat, k). The two-parameter fit above pins k through the 2060 plateau assumption, not through a historical regression. NITI regresses on GDP per capita (p. 61); that would need a GDP path, which this sheet does not supply.
- Apparent-use benchmarks (WSIF) are finished steel and include indirect-trade effects. The ×1.037 crude conversion uses India's FY25 yield; the world's 1.08 would raise every crude-equivalent value by about 4 %.

## Bibliography

- IEA (2020). *Iron and Steel Technology Roadmap: Towards more sustainable steelmaking.* https://iea.blob.core.windows.net/assets/eb0c8ec1-3665-4959-97d0-187ceca189a8/Iron_and_Steel_Technology_Roadmap.pdf
- IEA (2021). *India Energy Outlook 2021* (World Energy Outlook Special Report). https://iea.blob.core.windows.net/assets/1de6d91e-e23f-4e02-b1fb-51fdd6283b22/India_Energy_Outlook_2021.pdf
- Global Energy Monitor (2026). *Pedal to the Metal 2026.* https://globalenergymonitor.org/sites/default/files/2026-05/Pedal%20to%20the%20Metal%202026.pdf
- Ministry of Steel (2024). *Greening the Steel Sector in India: Roadmap and Action Plan.* https://steel.gov.in/green-steel-initiative
- Ministry of Steel (2026). *Annual Report 2025-26.* https://steel.gov.in/sites/default/files/2026-04/Final%20Annual%20Report%202025-26%20(English%20Version).pdf
- NITI Aayog (2026). *Scenarios Towards Viksit Bharat and Net Zero — Sectoral Insights: Industry.* https://niti.gov.in/sites/default/files/2026-02/Scenarios-Towards-Viksit-Bharat-and-Net-Zero-Sectoral-Insights-Industry.pdf
- Pauliuk, S., Wang, T. & Müller, D. B. (2013). Steel all over the world: Estimating in-use stocks of iron for 200 countries. *Resources, Conservation and Recycling* 71, 22–30. https://doi.org/10.1016/j.resconrec.2012.11.008 (self-archived revision, NTNU Open: http://hdl.handle.net/11250/284060)
- PIB (5 May 2026). *India's Steel Sector Advances Towards Self-Reliance.* https://static.pib.gov.in/WriteReadData/specificdocs/documents/2026/may/doc202655864101.pdf
- TERI (2021). Ghosh, Vasudevan & Kumar, *Energy-efficient technology options for direct reduction of iron process.* https://www.teriin.org/sites/default/files/2021-08/Direct%20Reduction%20of%20Iron%20Process.pdf
- UN DESA Population Division (2024). *World Population Prospects 2024*, `WPP2024_TotalPopulationBySex.csv.gz`. https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/WPP2024_TotalPopulationBySex.csv.gz
- worldsteel (2025). *World Steel in Figures 2025* (data finalised 4 June 2025). https://worldsteel.org/wp-content/uploads/World-Steel-in-Figures-2025.pdf
- Yadav, D., Guhan, A. & Biswas, T. (2021). *Greening Steel: Moving to Clean Steelmaking Using Hydrogen and Renewable Energy.* CEEW, New Delhi (quote in §3.2 only). https://www.ceew.in
