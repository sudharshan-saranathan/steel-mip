# Stage 2 — Demand, 2025 fleet, utilisation, fixed opex, resource availability, study-only values

Status: IN PROGRESS. Sub-groups are filled in as they are finished.

## Needs your call

IN PROGRESS

## A. Demand (base_demand, growth_rate)

`dem[t] = base_demand × (1 + growth_rate)^(ord(t) − 1)`, so 2050 is 25 growth years after 2025. At 5 %/yr: 194 Mt (2030), 445 Mt (2047), 515 Mt (2050).

Evidence on India's crude-steel production (implied 2025–2050 growth rate computed from 152.18 Mt in FY2024-25):

| # | Source | Kind | Quote (page) | Year / boundary | 2050 Mt | Implied %/yr |
|---|---|---|---|---|---|---|
| 1 | Ministry of Steel (2026) *Annual Report 2025-26*, Table 3.2.2 | GoI (JPC data) | "2024-25 … 200.333 [capacity] … 152.180 [production] … 76 [%]" (p. 16) | FY2024-25, crude steel, all routes | — (base) | — |
| 2 | PIB (5 May 2026) *India's Steel Sector Advances Towards Self-Reliance* | GoI | "India has already achieved 168 MTPA of crude steel production in FY 2025-26" (p. 7) | FY2025-26 | — | +10 % in one year |
| 3 | National Steel Policy 2017, as tabulated in MoS *Annual Report 2025-26* | GoI target | "Total crude steel demand/production (in MTPA) … 255" for 2030-31 (p. 23) | 2030-31 target | — | 9.0 (to 2031; a policy target, not a projection) |
| 4 | MoS *Annual Report 2025-26* §10.3 | GoI | "India's total steel demand is expected to reach ~230 MT by FY 31" (p. 79) | finished-steel demand, FY2030-31 | — | ≈7 (to 2031) |
| 5 | Ministry of Steel (2024) *Greening the Steel Sector in India: Roadmap and Action Plan* (with CEEW/TERI), §15 | GoI / TERI | "estimated production of crude steel at 197 MT by 2030, 374 MT by 2050 and 540MT by 2070" (p. 347) | crude steel | **374** | 3.7 |
| 6 | IEA (2020) *Iron and Steel Technology Roadmap*, ch. 3 highlights | agency (STEPS) | "production is expected to continue growing rapidly, almost doubling by 2030 and quadrupling by 2050"; India output "111 Mt" in 2019 (pp. 118, 123) | crude steel, Stated Policies | **≈ 444** (4 × 111) | 4.4 |
| 7 | NITI Aayog (2026) *Scenarios Towards Viksit Bharat and Net Zero — Sectoral Insights: Industry*, §3.2.1 | GoI | "India's total crude steel production is projected to rise from 144.29 Mt in 2024 to 624 Mt by 2050 and 821 Mt by 2070" (p. 63) | crude steel, both CPS and NZS | **624** | 5.8 |
| 8 | TERI (2021) *Energy-efficient technology options for DRI*, §3 | think tank (citing others) | "steel demand projected to reach between 500 and 760 million tonne (Mt) by 2050" (p. 37) | demand | 500–760 | 4.9–6.6 |
| 9 | TERI (2021), §4.4 | think tank, low-carbon scenario | "the steel demand will rise to around 300 million tonne by 2050" (p. 53) | demand, low-carbon | 300 | 2.8 |
| 10 | PIB (5 May 2026) | GoI target | "India is working towards achieving 500 MT of steel production capacity by 2047" (p. 2) | capacity, 2047 | ≈ 400 in 2047 at 80 % utilisation | ≈4.4 (to 2047) |

Summary: the three independent, India-specific 2050 projections (MoS/TERI 374, IEA ≈444, NITI 624) have a median of **≈444 Mt (4.4 %/yr)**, range 3.7–5.8 %/yr. The model's 515 Mt (5 %/yr) sits between IEA and NITI and is inside the range. Including the TERI-cited 500–760 Mt range, the median of six values is ≈472 Mt (4.6 %/yr).

| Parameter | file:line | Current | Sources | Value in model units | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| base_demand | `definitions.mod:3`; `parameters.mod:7` | 152.2 Mt | #1 (JPC via MoS AR 2025-26, p. 16) | 152.18 Mt | **152.2 Mt** (keep) | — | default |
| growth_rate | `definitions.mod:4`; `parameters.mod:8` | 0.05 | #5, #6, #7 (median), #8, #9 (range); #2–#4, #10 context | 3.7 %–5.8 %/yr; median 4.4 % | **0.044** by the median rule, sensitivity 0.037–0.058. Keeping 0.05 is defensible (newest GoI figure, NITI 2026, is higher; FY26 growth was +10 %) | higher demand = harder | **NEEDS CALL** |

Note: cite #5–#7 in Supp. Table 1 whichever value is chosen. The NSP 2017 target (255 Mt by 2030-31) is a target, not a projection; the model reaches 194 Mt in 2030.

## B. 2025 fleet and starting route split

### B.1 Evidence

| # | Source | Quote / data (page) | Year |
|---|---|---|---|
| F1 | MoS *Annual Report 2025-26*, §3.2.3 (JPC) | Crude steel by route, 2024-25: "Basic Oxygen Furnace (BOF) 41.1 … Electric Arc Furnace (EAF) 20.8 … Induction Furnace (IF) 38.2" (p. 17) | FY2024-25 |
| F2 | MoS *Annual Report 2025-26*, Annex V (JPC) | "TOTAL OXYGEN ROUTE: … 62,488 … TOTAL ELECTRIC ARC FURNACE: … 31,611 … ELECTRIC INDUCTION FURNACE … 58,080 … GRAND TOTAL … 1,52,180" ('000 t, 2024-25) (p. 183) | FY2024-25 |
| F3 | MoS *Annual Report 2025-26*, §3.2.4 and Annex III (JPC) | Sponge iron 2024-25: "Coal based … 46.883 … Gas based … 8.880 … Total 55.764"; "% share by Process (Coal Based) … 84%" (pp. 18, 181) | FY2024-25 |
| F4 | MoS (2024) *Roadmap*, Fig. 1.8 | Crude steel by metallic input FY2023-24: BF 71.8 (50 %), coal DRI 33.4 (23 %), gas DRI 8.8 (6 %), scrap 30.1 (21 %); by route BOF 61.61 (43 %), EAF 31.6 (22 %), IF 51.1 (35 %) (p. 30) | FY2023-24 |
| F5 | MoS (2024) *Roadmap*, Table 1.5 | "Coal-based DRI Plants 339 … 48.2; Gas-based DRI Plants 5 … 12.3 [MT/yr]: AMNS (NG) Hazira 6.8; JSPL (through coal gasification) Angul 1.8; JSW (NG) Dolvi 1.6" (pp. 33–34) | c. 2023 |
| F6 | MoS (2024) *Roadmap*, §5.4.2 | "34 EAFs with a total installed capacity of 36.61 Mt … 28.20 Mt in 2022-23, registering about 77% capacity utilisation"; "around 1032 EIF units … total installed capacity of 68.8 Mt … 50.4 Mt registered a capacity utilisation of 73%" (pp. 106–107) | FY2022-23 |
| F7 | Global Energy Monitor (2026) *Pedal to the Metal 2026*, India profile | "India operates a total steel capacity of 140 mtpa … 61% BOF (86 mtpa), 19% EAF (27 mtpa), and 10% IF (14 mtpa)"; "119 mtpa of operating BF capacity"; IF undercounted because plants < 0.5 Mtpa are excluded (pp. 26–27); "62% of India's overall DRI fleet relying on coal"; India DRI "22%, 37 mtpa" of global (pp. 17, 19) | March 2026, plants ≥ 0.5 Mtpa |
| F8 | MoS *Annual Report 2025-26*, Table 3.2.2 and Annex IV | Total crude-steel capacity 200.333 Mt (FY25), 218.296 Mt (Dec 2025); "OTHER IF 81,920 … OTHER EAF 9,323 … OTHER BOF 3,177" working capacity, '000 t, FY25 (pp. 16, 182) | FY2024-25 |

### B.2 Parameters

| Parameter | file:line | Current | Sources | Value in model units | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| init f_bof | `t_additional_constraints.mod:2` | 0.51 | F1, F2 (JPC FY25 41.1 %); F4 (FY24 43 %) | 0.411 (FY25); 0.427 (FY24) | **0.411** (FY2024-25, matches base year) | n/a (calibration) | **NEEDS CALL** (resolves ST-07, interacts with util_min_bof; see C) |
| init f_eaf | `t_additional_constraints.mod:3` | 0.49 | F1, F2 | 0.589 | **0.589** (= 1 − f_bof) | n/a | with f_bof |
| init_f_cdri | `t_additional_constraints.mod:6` | 0.902 | F3 (coal share of sponge iron 84 %); F4 (coal DRI / all DRI metallics 0.79); F5 (coal share of DRI capacity 0.80); F3 + F2 on output basis (see note) | 0.79–0.84 on DRI share; **0.91** on crude-steel output basis | **0.91** (keep ≈ 0.902) if the coal route continues to carry all scrap-based IF/EAF steel; **0.84** only if scrap-based steel gets its own route in 2025 | higher = harder | default (see note) |
| cap0_bof | `definitions.mod:222` | 90.0 Mt | F7 (86 Mtpa BOF, Mar 2026); F8 (integrated producers' capacity ≤ 99.5 Mt incl. their EAFs) | 86–90 Mt | **90 Mt** (keep; single direct source, keep the higher bound = larger coal lock-in) | higher = harder | default |
| cap0_cdri | `definitions.mod:223` | 104.1 Mt | F6 (EAF 36.6 + IF 68.8 = 105.4 Mt, FY23); F8 (total 200.3 Mt FY25 − BOF 86–90 − gas 11–13 ⇒ 97–103 Mt) | 97–105 Mt | **104.1 Mt** (keep) | higher = harder | default |
| cap0_ngdri | `definitions.mod:224` | 12.9 Mt CS | F5 (12.3 Mt DRI/yr incl. 1.8 syngas); F7 (38 % of 37 Mtpa = 14.1 Mt DRI/yr) ÷ 1.1 t DRI/tCS | 11.2–12.8 Mt CS | **11.2 Mt** (lower bound) | lower = harder | default |
| cap0_scrap | `definitions.mod:226` | 0.75 Mt | Stage 1 tag S | — | keep | — | — |

Note on init_f_cdri. The model books all EAF + IF steel (89.7 Mt in FY25) to the DRI routes, because scrap-EAF output is fixed at 0 in 2025. If gas-DRI steel is taken as gas sponge iron ÷ 1.1 t DRI/tCS, it is 8.88/1.1 = 8.1 Mt, so the coal route carries 89.7 − 8.1 = 81.6 Mt and f_cdri = **0.910** (FY24: 9.785/1.1 = 8.9 of 82.7 Mt, 0.892). The model's 0.902 matches this output-based calibration. The 0.83 in the paper's Fig. 1a, and 0.79–0.84 here, are shares of *DRI metallics*, a different quantity. Setting f_cdri = 0.84 with f_eaf = 0.589 would put 14.3 Mt on the gas route, above its capacity (12.9 × 0.95 = 12.3 Mt), so 2025 would be infeasible. The real calibration problem is the boundary: about 30 Mt of scrap-based IF/EAF steel (F4) is modelled as coal-DRI steel. That is structural (see Structural notes, S-1) and feeds the 2.80 vs 2.54 tCO₂/tCS gap.

Fleet total: 90 + 104.1 + 11.2 + 0.75 = 206 Mt, against JPC 200.3 Mt (Mar 2025) and 218.3 Mt (Dec 2025).

## C. Capacity utilisation

Evidence (JPC working capacity and production, MoS *Annual Report 2025-26*, Annex IV, p. 182, unless noted):

| Route proxy | FY22 | FY23 | FY24 | FY25 | Note |
|---|---|---|---|---|---|
| All India | 78 | 79 | 80 | 76 | Table 3.2.2, p. 16 |
| Integrated BOF producers: SAIL / TSL / JSW / JSPL / RINL / NMDC | 84 / 94 / 78–92 / 92 / 84 / – | 89 / 96 / 92 / 93 / 57 / – | 93 / 97 / 91 / 80 / 60 / 18 | 93 / 100 / 78 / 70 / 49 / 49 | groups include some EAF capacity |
| Other BOF | 65 | 67 | 69 | 66 | |
| BOF route (oxygen-route output ÷ GEM BOF capacity) | | | | 62.5 / 86 = **73** | F2, F7 |
| Other IF (≈ coal-DRI + scrap IF fleet) | 69 | 70 | 74 | 71 | MoS Roadmap: EIF 73 % FY23 (p. 107) |
| Other EAF | 70 | 55 | 65 | 61 | MoS Roadmap: all EAFs 77 % FY23 (p. 106) |
| Gas DRI (sponge output ÷ 12.3 Mt capacity, F5) | 72 | 65 | 80 | 72 | AM/NS (gas-DRI-EAF) 76 / 70 / 80 / 74 |

| Parameter | file:line | Current | Sources | Value in model units | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| util_min_bof | `definitions.mod:262` | 0.85 | Annex IV; F2 + F7 | route average 0.66–0.73; large integrated plants 0.70–1.00 | **0.70** | higher = harder (keeps BF-BOF running) | **NEEDS CALL** |
| util_min_cdri | `definitions.mod:263` | 0.75 | Annex IV other IF 0.69–0.74; Roadmap EIF 0.73 | 0.69–0.74 | **0.70** | higher = harder | default |
| util_min_ngdri | `definitions.mod:264` | 0.70 | gas DRI 0.65–0.80; AM/NS 0.70–0.80 | median 0.72 | **0.70** (keep) | — | default |
| util_min_h2dri | `definitions.mod:265` | 0.70 | no Indian fleet | — | **0.70** (keep, assumption A, same as NG-DRI shaft furnace) | — | default |
| util_min_scrap | `definitions.mod:266` | 0.60 | other EAF 0.55–0.70; Roadmap EAF 0.77 | median of 5 values 0.65 | **0.60** (keep; within range) | — | default |
| util_max | `definitions.mod:267` | 0.95 | all-India 0.76–0.80 (FY22–25); best plants 0.93–1.00 (SAIL, TSL) | sector max 0.80; plant max 1.00 | **0.85** suggested (between sector and plant evidence); 0.80 would be strictly evidence-based | lower = harder (more capacity and capex) | **NEEDS CALL** |

Why util_min_bof matters: with f_bof = 0.411, 2025 BOF output is 62.5 Mt, or 0.69 of 90 Mt. At 0.85 the model must then lift BOF output to ≥ 76.5 Mt in 2026 (+22 %) and keep it there while the fleet lives. Today, 0.51 × 152.2 = 77.6 Mt (0.86 of 90 Mt) hides this conflict.

Why util_max matters: the model settles at capacity/demand = 1/0.95 = 1.05 (comment at `definitions.mod:241–243`). India runs at 200.3/152.2 = 1.32. At 0.85 the ratio is 1.18, so about 12 % more capacity (and capex) is needed.

## D. Fixed and other opex

IN PROGRESS

## E. Discount rate

IN PROGRESS

## F. Coking-coal availability

IN PROGRESS

## G. Natural-gas availability

IN PROGRESS

## H. Emission-intensity targets vs Green Steel Taxonomy

IN PROGRESS

## I. Study-only values

IN PROGRESS

## Structural notes

IN PROGRESS

## Bibliography

IN PROGRESS
