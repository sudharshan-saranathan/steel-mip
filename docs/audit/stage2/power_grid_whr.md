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
| MoS (2024) Table ES2 (pdf p. 22) — 2030 grid & CPP | "Grid CO2 factor 0.46 tCO2/MWh"; "CPP CO2 factor 0.96 [BAU] 0.77 [20% RE] 0.68 [30%] 0.55 [43.33%]"; "Overall CO2 factor 0.78 [BAU] … 0.52" | (2030 blend 0.78 BAU) | blend −8 % by 2030 in BAU |

Median of the six 2050 grid-only scenario values = 0.105 tCO₂/MWh (−85 %); the least optimistic is 0.32 (−55 %). The key point: these are **grid** trajectories. The model's θ_grid scales the **blend**, of which 64 % is coal CPP that decarbonises only if steel firms replace it (MoS Table ES2 BAU keeps CPPs at 0.96 through 2030). Example: grid −80 % with CPPs unchanged gives 0.36 × 0.14 + 0.64 × 0.97 = 0.67, i.e. the blend falls only ~24 % — about θ_grid = 0.25.

| Parameter | file:line | Current | Sources | Value in model units | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| n9_grid_ef_start | definitions.mod:167 | 0.000886 t/kWh | CEA v21/v22 WA and coal EF; MoS Table 6.4 split (above) | 0.000864–0.000876 (blend, CEA WA); 0.00085 (MoS FY22) | **0.000880** (FY2024-25 blend, rounded up; replace the CM-based 0.757 in the comment by WA 0.710) | higher | default |
| n9_grid_ef_end (θ_grid levels 0.25/0.5/0.75) | definitions.mod:168–171; study files | start × (1 − θ) | NEP 2023; TERI 2024; WRI 2024; MoS ES2 | grid-only 2050 reductions 55–100 % (median 85 %); blend reduction depends on CPP retirement | Keep the 0.25/0.5/0.75 grid levels, but state in the paper that θ applies to the grid+CPP blend; θ = 0.25 ≈ "grid decarbonises, CPPs stay coal". Better: split into grid and CPP (see §E) | lower θ | **NEEDS CALL** |

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
| Firm solar+storage block | IECC (2026) pdf p. 13 | "yielding sub‑60 USD/MWh today in India" | — | < 0.060 |
| Åhman & Arens (2024) *Utilities Policy* 91:101853 (cited by the model) | could not be opened (ScienceDirect blocked by the proxy; CC-BY but no repository copy) | — | — | not used |

Conversion: `convert_2025usd.py` `inr(v, year)` (WPI 2023 = 151.3, 2024 = 154.0, 2025 = 154.95; ₹87.16/$). MoS tables taken as 2023 rupees (report published 2024).

| Parameter | file:line | Current | Sources | Value in model units | Proposed | Pessimistic direction | Flag |
|---|---|---|---|---|---|---|---|
| grid_price_start | definitions.mod:148 | 0.07 $/kWh | CEA tariff book FY25; MoS Tables 6.15–6.18; IECC | blend: ISP 0.072, SSI 0.077; grid-only 0.082–0.096; new captive 0.071 | **0.08** (0.64 × new-captive 0.071 + 0.36 × grid median 0.096 = 0.080; upper end of the blends) — or keep 0.072 (MoS ISP blend) | higher | **NEEDS CALL** |
| grid_price_end_fast | definitions.mod:149 | 0.055 $/kWh (2050, θ = 1) | MoS Table 6.17 row 4 (RE OA + banking, median 0.054); MoS Table 6.16 (0.049); IECC (< 0.060; 0.060 grid for EAF) | 0.049–0.060 | **0.06** (fewer than 3 independent sources → upper bound; RE values exclude 24×7 firming) | higher | default |
| ng_credit_power | definitions.mod:182 | 0.03 $/kWh | MoS: existing-captive variable cost ₹2.5–3/kWh (0.029–0.035) is the nearest avoided-cost analogue | — | No change; parameter is **unused** in `core` (declared, never referenced). Delete or document | — | default |
## C. Process-gas power / WHR pool (n9_eta, n9_whr, 0.3 factor, whr_steam_eff, n9_whr_capex/opex) — IN PROGRESS
## D. Unit WHR (CDQ, TRT, sinter cooler) — IN PROGRESS
## E. Structural notes (ST-05 fix, ST-06 boundary) — IN PROGRESS
## Bibliography — IN PROGRESS
