# Review document — overnight run of 2026-10-06/07

**Status: COMPLETE** (Stages 1–3). Read §1 first, then the "Needs your call" list (§4). Every model change is its own commit on `fix-wave-01`, so any one can be reverted alone (`git revert <hash>`).

## 1. Summary

- **Solver:** the AMPL licence variable reaches only new sessions, so tonight everything ran on the AMPL **demo** + **HiGHS** through `tools/ampl_highs_bridge.py`. The bridge rebuilds the exact LP from AMPL's `expand` output. On the unchanged model it reproduces the paper's Fig. 3 exactly (524.3 vs 524; 567.7 vs 568; 517.2 vs 517; 555.6 vs 556; the infeasible cell is infeasible). **To confirm tomorrow:** in a new session run `python -m amplpy.modules activate $AMPL_LICENSE_UUID`, then `python3 tools/benchmark.py --tag licensed` and compare with `tools/benchmark_results.csv`.
- **Branch `fix-wave-01`:** Nakul's `b33b88a` imported unchanged, then 14 fix commits (§2). The model solves under every study template (H₂ delay, sectoral synergy, feasibility drivers, Monte Carlo).
- **2025 calibration:** the model's 2025 emission intensity moves from **2.80 to 2.50 tCO₂/tCS** (Ministry of Steel reports 2.54). Nothing was tuned to hit that number. The gap closed through sourced emission factors, BF fuel rates, route shares and in-plant power.
- **Effect on results:** see §3. After the NG-availability correction (commit 15, at your request), **the paper's feasibility frontier is reproduced exactly**: at 1.6 tCO₂/t the same cells are infeasible, and with scarce coal and gas the transition is feasible only if H₂ arrives by 2035, as in Fig. 5(d). LCOP is 50–75 $/t lower throughout. The cost of delaying H₂ is smaller than in the paper (~5 $/t from 2030 to 2045 at 1.8, vs ~30), mainly because corrected capex and gas use make the fallback routes cheaper.

## 2. Commits on `fix-wave-01`

Benchmark cell: EF 1.8, mid H₂ ramp, H₂ from 2030, Fig. 3 backdrop (abundant coal and NG, θ = 0.5, scrap 6 %, build 30 Mt/yr). Full log: `tools/benchmark_results.csv` (8 cells per commit).

| # | Commit | Change | Basis | LCOP $/t | H₂ 2050 | ei_2025 |
|---|---|---|---|---|---|---|
| 0 | `82612e3` | Nakul's code, unchanged | — | 524.3 | 28.7 % | 2.795 |
| – | `dd70d54` | Tools: bridge, benchmark, CRLF edit helper | — | | | |
| 1 | `7f9034a` | ST-01 up-front capex; BF-BOF 1,200, coal-DRI-EAF 860, NG/H₂-DRI-EAF 920, scrap-EAF 400 $/t | agreed with you | 474.6 | 25.5 % | 2.795 |
| 2 | `5d83c50` | Lifetimes 40 yr; 2025 fleet runs to 2050 | agreed | 468.7 | 26.4 % | 2.795 |
| 3 | `65467a7` | ST-02 pellet ore ÷ → × | bug | 479.8 | 26.5 % | 2.795 |
| 4 | `79a79c6` | ST-16 salvage credit | agreed in principle; design ⚑ | 455.9 | 36.6 % | 2.795 |
| 5 | `62b8214` | DRI, EAF/IF, scrap coefficients | ⚑ | 428.8 | 28.5 % | 2.718 |
| – | `c2c90e7` | Stale comments (ST-14, build budget) | no effect | | | |
| 6 | `3f225f8` | ST-13 emission factors as named, sourced parameters | ⚑ | 420.7 | 24.2 % | 2.555 |
| 7 | `9fcfdb8` | ST-03 pellet induration fuel; ST-04 purchased breeze carbon | ⚑ | 424.3 | 26.6 % | 2.620 |
| 8 | `9d70a87` | BF-BOF coefficients (fuel rate 0.68 → 0.58 t/tHM etc.) | ⚑ | 409.9 | 17.6 % | 2.442 |
| 9 | `c376a12` | ST-12 firming plug off; green-H₂ inputs | ⚑ | 410.4 | 12.6 % | 2.442 |
| 10 | `861a6a9` | ST-10 capture limit; CCS from 2035, ceiling 25 %; CCS costs | ⚑ | 410.7 | 12.6 % | 2.442 |
| 11 | `c32b12b` | ST-07 route split 0.411/0.589; utilisation; ST-11 fixed opex | ⚑ | 438.2 | 21.5 % | 2.427 |
| 12 | `f991752` | Prices (coal 200, gas 12, power 0.08, scrap 400 …) | ⚑ | 469.6 | 27.3 % | 2.427 |
| 13 | `9942928` | ST-05 captive power from process gas; real WHR penetration; ST-06 blended EF | ⚑ | 467.1 | 24.7 % | 2.415 |
| 14 | `8d6eb53` | ST-07 2025 scrap share recalibrated (2025 scrap use 42 → 37 Mt) | ⚑ | 466.8 | 25.2 % | 2.501 |
| – | `a30397a` | Fig. 3 grid before/after (`tools/fig3_before.csv`, `fig3_after.csv`) | — | | | |
| 15 | `0dc91be` | NG availability: steel share of national gas 10 % → 3.5 % (your request) | 8.88 Mt gas-DRI × 0.21 t NG/t (PNGRB) ÷ national gas | 473.5 | 30.7 % | 2.501 |

Not changed in code: ST-08 (h2_ramp_mode 0 coupling; unused mode), ST-09 (capacity envelope units; documented), ST-15 (core default NG cap = shock trajectory; every study overrides it).

## 3. Results before and after

### Fig. 3 grid (LCOP $/t / H₂-DRI share 2050 %; X = infeasible), final model incl. commit 15

| EF | H₂ supply | 2030 | 2035 | 2040 | 2045 |
|---|---|---|---|---|---|
| 1.6 | Low | 568/22 → **500/23** | X → X | X → X | X → X |
| 1.6 | Mid | 545/34 → **493/40** | 567/28 → **496/33** | X → X | X → X |
| 1.6 | High | 542/36 → **491/50** | 548/37 → **492/48** | X → X | X → X |
| 1.8 | Low | 530/19 → **475/19** | 537/14 → **475/17** | 548/8 → **477/10** | 556/3 → **479/4** |
| 1.8 | Mid | 524/29 → **474/31** | 527/26 → **474/31** | 542/16 → **475/21** | 554/4 → **478/9** |
| 1.8 | High | 523/29 → **473/39** | 523/30 → **473/39** | 537/23 → **474/32** | 553/6 → **478/13** |
| 2.0 | Low | 510/15 → **457/10** | 512/13 → **457/10** | 516/7 → **457/10** | 518/1 → **457/4** |
| 2.0 | Mid | 508/18 → **457/16** | 508/18 → **457/16** | 514/13 → **457/16** | 517/2 → **457/9** |
| 2.0 | High | 508/19 → **457/21** | 508/19 → **457/21** | 512/18 → **457/21** | 517/3 → **457/13** |

Readings:
- **Infeasibility pattern identical to the paper.** Before the gas correction, the corrected model had made 1.6/2035 and 1.6/2040 feasible. That came entirely from the unsourced 10 % gas share combined with corrected (lower) gas use per t DRI.
- LCOP 50–75 $/t lower everywhere, mostly ST-01 capex (2–3× too high) and prices.
- The cost of delaying H₂ is smaller (≈ 5 $/t from 2030 to 2045 at 1.8, vs ≈ 30 in the paper); H₂ shares at 1.6 are higher (40–50 % vs 34–36 %).

### Sensitivities at EF 1.8, mid ramp (final model; LCOP $/t)

| Case | 2030 | 2035 | 2040 | 2045 |
|---|---|---|---|---|
| Fig. 3 backdrop | 473.5 | 473.5 | 475.0 | 478.5 |
| NG scarce | 475.9 | 475.9 | 478.2 | 483.3 |
| NG + coal scarce | 476.1 | 476.3 | **infeasible** | **infeasible** |
| Discount rate 10 % | 472.1 | 472.1 | 475.8 | 482.8 |

No change was made to restore feasibility; infeasibility is reported as found. Changes that loosen constraints (lower gas use per t DRI, emission factors, BF fuel rate, fleet life) and tighten them (utilisation 0.85, later and smaller CCS, added breeze and pellet emissions) were each made on evidence alone.

## 4. Needs your call (short list)

1. **NG availability, done (commit 15):** steel share 10 % → **3.5 %** (existing gas-DRI fleet on NG: 8.88 Mt × 0.21 t/t ÷ 53.5 Mt national). Pure-NG use today is 1–1.7 % (PPAC, MoS); the route also stands for syngas/COG-based DRI, and a share below ~3.4 % makes 2025 infeasible by construction. 2040 caps 2.9 / 5.6 Mt bracket PNGRB's steel projection (5.0–6.6) from below. Check you are comfortable with the 3.5 % reasoning.
2. **Discount rate.** 6 % (Murty et al., environmental-project rate; social planner) kept. Private WACC evidence is 10 % (IECC, Transition Asia–TERI, Planning Commission). Results above show modest LCOP sensitivity. State the framing in the paper either way.
3. **Study centrals and sampled levels not changed.** Core now uses coal 200 $/t and gas 12 $/MMBtu (evidence). The regret backdrop still uses 250 / 15, and Monte Carlo levels stay at coal 100/250/400, gas 5/15/25, scrap 250/350/450. The prices sheet suggests 150/200/300, 8/12/18 and 300/400/500. Scrap growth in the templates stays 6 % (evidence suggests 5 %; core default now 5 %).
4. **H₂ supply-ramp axis** (0.5/1/1.5 Mt H₂/yr for steel alone). Even the low level is ~70 % of the whole-economy NGHM pace. Keep, or rescale to 0.25/0.5/0.75? Also, the paper's sampled H₂ cost range "1.5–5 $/kg" no longer matches the model (2050 runs 2.4–4.7 $/kg).
5. **Conflicting sheets, values kept:** `init_f_cdri` (0.902 vs 0.84), `cap0_cdri` (104.1 vs 91), `cap0_ngdri` (12.9 vs 11.2). The DRI and demand agents disagree on the data basis.

Smaller items to be aware of:
- Biochar priced at 520 $/t from a Chinese source; the alternative is relabelling the BF input as raw biomass at ~60.
- Kiln waste-heat power for coal-DRI is left out (pessimistic).
- ST-16 salvage covers routes, electrolyser, renewables and CCS, but not supply-chain builds.
- The blended grid factor means θ_grid scales grid + captive coal together; state this in the paper.
- The paper's "66.33 Mt coking coal imports (2025-26)" is FY26; the model's 2025 base is FY25 (~54–58 Mt).

## 5. Decisions made on your behalf (⚑), with reasons

Sheets with sources, quotes and pages are in `docs/audit/stage2/`. I spot-checked key quotes in each sheet against the downloaded documents. I found one omission (the MoS 0.33 t NG/t DRI figure, which supports the old value) and added it; the median was unchanged. Paywalled or certificate-failing sources were not used, and no certificate check was bypassed.

| Area | Decision | Why |
|---|---|---|
| Salvage (ST-16) | straight-line value of life after 2050, discounted from 2051 | standard treatment; recovers late-build economics |
| Coal per t DRI | 0.9 t at 24 GJ/t (21.6 GJ/t DRI) | Indian kilns ~21 GJ/t (median of 4); keeps price and emission-factor basis consistent |
| NG per t DRI | 0.22 t (10.9 GJ) | median of 5 incl. MoS's 0.33 |
| Scrap route | 590 kWh/t, costed as EAF | median of 4 for 100 % scrap |
| Scrap supply | seed 37 Mt; default growth 5 % (125 Mt in 2050 = NITI lower case) | templates still 6 % (call #3) |
| Emission factors | coking 2.67 (IPCC), PCI 2.46, non-coking 2.32 (24 GJ/t × 96.8 kg/GJ, BUR-4), NG 2.69, electrodes 3.67 | 2.64 implied 110 kg/GJ, above every source; pessimistic within the evidence |
| BF fuel rate | 0.58 t/tHM in 2025, 0.59 in 2050 | top of MoS Table 5.4 (505–579) |
| Pellets / breeze | 70 kWh + 1.6 GJ coal per t pellet; purchased breeze carbon counted | pessimistic fuel mix |
| Green H₂ | plug off; re_cf 0.25; 2025 = 4.72 $/kg; 2050 = 4.72/3.55/2.39 at θ = 0/0.5/1 | sourced build-up; tenders 3.0–5.1 $/kg |
| CCS | 75 $/t (2025); capture 0.9 × share; start 2035; ceiling 25 %; decline 27/60 % | NITI, MoS, DST, IEA |
| 2025 fleet | BOF share 0.411 (JPC); util 0.70–0.85; phi0_cdri 0.325 | measured route split; scrap consistency |
| Fixed opex | labour 22 + 3 % of capex per route | company reports; TA–TERI |
| Demand growth | 5 % kept | inside 3.7–5.8 % range; pessimistic |
| Prices | coal 200, gas 12 (+52.6 MMBtu/t), power 0.08 blended, scrap 400, ore 80, electrodes 2,500, tar 430, slag 10, biochar 520 | medians or pessimistic bound |
| In-plant power (ST-05) | CPP η 0.30; share of surplus gas fired 0.33 → 0.5; CDQ/TRT/sinter WHR ramp from real 2025 penetration to full | calibrated to MoS ~133 kWh/tHM (model gives 133.6) |
| Grid EF (ST-06) | blended 0.880, θ_grid scales the blend | CEA weighted average + captive |

## 6. What is still unsourced

Each sheet lists parameters with no admissible source; they keep their current values and should be declared as assumptions in the supplementary:
- BF-BOF: 18 of 61, mostly coke-oven and gas flows, sinter inputs and BFG/BOFG calorific values.
- DRI/EAF: 5 (lump ore in NG/H₂ DRI, off-gas, scrap-chain capex).
- Prices: 3 (PCI, breeze credit and cost).
- H₂: 7 (all ramp-shape parameters).
- CCS: 3 plus 2 new capturable shares.
- Power: 2.
- Demand/opex: 2.

## 7. Follow-up checks (requested after the overnight run)

**Build budget (`cap_add_common`).** Historical pace from JPC (MoS Annual Report 2025-26, p. 16): capacity 154.1 (FY22) → 161.3 → 179.5 → 200.3 Mt (FY25), i.e. +18.2 and +20.8 Mt in the last two years, and +18.0 Mt in Apr–Dec FY26 (provisional). **20 Mt/yr is today's pace, not "double the historical 8–10 Mt/yr"** as the paper states; 30 Mt/yr is ~1.5×. Fig. 3 at 20 / 30 / 40 Mt/yr: **the same 7 cells are infeasible in all three**; LCOP +2–4 $/t at 20. The build budget is not what sets the feasibility frontier.

**Monotonic emission intensity.** The paper (§2.2) says it is enforced, but every study driver dropped it as "bilinear". Since total steel = demand, it is linear when written with `dem[t]`; now done and enforced in the structural and Monte Carlo drivers (commit `3ffb9e3`; still dropped in the regret study, whose demand is elastic). Effect on Fig. 3: **no feasibility change; LCOP +0–1 $/t.**

**Demand profile: S-curve is now the central case (commits `9434f8f`, `6b8ff9a`).** Logistic demand through 152.2 Mt (FY25) with initial growth 8.2 %/yr (FY22–FY25 CAGR, JPC), saturating at **680 Mt** = 400 kg crude steel/capita × 1,701 M (UN WPP 2024 medium peak, 2061). Sensitivities: **510 Mt** (300 kg, EU/US level) and **816 Mt** (NITI 2026's "logistic S-curve with an assumed saturation around 450 kg/capita", verified in the source). Demand 2030/2040/2050: 223/397/545 Mt (exponential: 194/316/515). Sheet: `stage2/demand_saturation.md`. `dem_profile = 0` restores the paper's 5 %/yr.

Fig. 3 grid, monotonic enforced (LCOP $/t / H₂ share %, X = infeasible):

| EF | H₂ supply | 2030 | 2035 | 2040 | 2045 |
|---|---|---|---|---|---|
| 1.6 | Low | X | X | X | X |
| 1.6 | Mid | 506/43 | X | X | X |
| 1.6 | High | 503/47 | X | X | X |
| 1.8 | Low | 486/21 | X | X | X |
| 1.8 | Mid | 483/33 | 484/32 | X | X |
| 1.8 | High | 483/39 | 483/39 | X | X |
| 2.0 | all | 466/4–20 | 466 | 466 | 466–467 |

| Demand profile | Infeasible cells (of 36) |
|---|---|
| Exponential 5 % (paper) | 7 |
| S-curve 510 | 13 |
| **S-curve 680 (central)** | **17** |
| S-curve 816 (NITI) | 17 |

**What it means:** with fast growth now and slowing growth later, most capacity is built in the late 2020s–2030s. Without H₂ by then, that capacity is fossil and the cumulative target becomes unreachable. At 1.8 tCO₂/t, H₂ must be available by **2030 (low ramp) or 2035 (mid/high ramps)**. The cost of delaying H₂ shows up as **infeasibility** rather than as a gradual LCOP rise. This supports the paper's central message more strongly than the original exponential demand did. Costs are 483–486 $/t at 1.8 where feasible.

Open for you: (i) 680 Mt central (400 kg/capita) vs 816 Mt (NITI's level, pessimistic); (ii) the S-curve anchor: the measured 8.2 %/yr initial growth (used) vs "90 % of saturation by 2060" (the sheet's alternative; 2050 = 524 Mt instead of 545).

## 8. Reruns under S-curve demand (licensed AMPL + Gurobi, 2026-10-07)

All paper studies rerun on `fix-wave-01` with the S-curve central case (680 Mt saturation, 545 Mt in 2050), monotonic intensity enforced, and the CCS ceiling of 0.25 from 2035 unless stated. Licensed AMPL + HiGHS and AMPL + Gurobi both reproduce the bridge benchmark exactly (LCOP 483.19).

**Bug found and fixed (`3656c00`).** At θ_grid = 1 the 2050 grid factor came out as −0.0; AMPL presolve then forced grid power to zero and reported the model infeasible. The synergy study tests θ_grid = 1 first, so every case needing grid decarbonisation looked infeasible. Fixed by clamping the factor at 0. The paper is unaffected (Nakul's 0.000886 gives exactly 0); the feasibility-driver and Monte Carlo designs use θ_grid ≤ 0.75 and were never affected.

| Study | Paper | Now | Commit |
|---|---|---|---|
| H₂ delay (Fig. 3) | 7 of 36 cells infeasible | 17 of 36; at 1.8, H₂ must start by 2030 (low ramp) or 2035 (mid/high); LCOP 483–486 | `1776ffa` |
| Fuel availability | scarce coal feasible to 2035; abundant to 2045 | scarce coal: only H₂ 2030; abundant: to 2035; import bills higher | `1776ffa` |
| Feasibility drivers | 41.0 % feasible (27.6 / 41.5 / 54.0 by target) | 34.3 % (17.0 / 34.7 / 51.2) at CCS 0.25 | `8ab9fc5` |
| Sobol ranking at 1.8 | build budget first (0.48) | scrap 0.60, H₂ start 0.38, build 0.26, legacy 0.23, ramp 0.18, coal 0.13, grid 0.12, CCS 0.08, NG 0.04 | `17f4210` |
| Sectoral synergy | small grid offsets needed | much larger (H₂ 2033 / scrap 4 %: 37 % vs 0 %); H₂ from 2036 with scrap ≤ 2 %: infeasible even with a clean grid | `96adcf4` |
| Monte Carlo | 3,544 cells, 177,200 solves | 2,966 cells (490 / 1,000 / 1,476), 148,300 solves, all feasible | `2cc9e22` |
| Regret | — | see below | — |

Earlier statement corrected: the build budget is not what sets the Fig. 3 frontier, but across the full design it matters (third in Sobol; it binds in phase-out and scarce-fuel cells).

**Monte Carlo draws cannot change feasibility.** The five drawn inputs (coal, NG and scrap prices, H₂ and CCS learning) enter only cost definitions, so every one of the 148,300 solves is feasible, as in the paper. `theta_tech` moves the 2050 end of the H₂ cost path (electrolyser 800 → 159 $/kW, renewables 835 → 695 $/kW); the 2025 start is fixed by design.

### 8.1 CCS deployment ceiling as a ninth axis (`17f4210`)

`phi_2050` = 0 / 0.05 / 0.10 / 0.25 of fossil-route CO₂ in 2050 (ramp from 2035). Sources for 0.25: IEA ISTR (25 % of steel direct CO₂, SDS) and NITI 2022 (≈ 26 % of emissions, economy-wide); for the low levels: NITI 2026 Net Zero Scenario rates CCUS "Low" in 2050. The paper's 0.50 has no feasibility-based source: the MoS Roadmap's 53 / 59 / 56 % (p. 221) are what net zero would *require*, reported from literature, not targets.

| CCS ceiling | 0 | 0.05 | 0.10 | 0.25 |
|---|---|---|---|---|
| Feasible share (all targets) | 26.8 % | 28.1 % | 29.6 % | 34.3 % |
| Fig. 3 infeasible cells (of 36) | 23 | 18 | 17 | 17 |

At 1.8 the 0.25 slice reproduces the earlier 8,640-cell run cell for cell. CCS has the second-smallest Sobol index (0.07–0.09).

**When CCS matters.** Target 1.8, mid ramp, audited scrap growth 5 %/yr:
- H₂ from 2030: feasible even without CCS (fast enough ramp).
- H₂ from 2035: needs a ceiling between 0.05 and 0.25.
- H₂ from 2040: needs ≈ 0.50; from 2045: CCS at its physical maximum (≈ 0.60).
- Low CCS survives delayed H₂ only with scrap growth of 8–10 %/yr (250–400 Mt in 2050, 2–3× the evidence).
- With a slow H₂ ramp, CCS is needed even with H₂ from 2030.

So the claim the model supports is conditional: **India's 2050 intensity targets do not need large-scale CCS if H₂ arrives by 2030–35 and scales at mid-to-high speed.** It does not test net zero: these pathways still emit ≈ 0.9–1.1 t/t (≈ 480–600 Mt) in 2050.

### 8.2 λ index (screening diagnostic)

λ_X = (cumulative CO₂ lever X could avoid or capture at its ceiling) / (required abatement against a fleet frozen at 2025 intensity, 2.53 t/t). Levers: H₂ (all output), scrap (only above the 2025 pool of 37 Mt, which is already in the baseline), CCS (ceiling × remaining fossil CO₂). Required abatement: 8.2 / 6.4 / 4.6 Gt at targets 1.6 / 1.8 / 2.0. Code: `tools/lambda_index.py`.

| λ_H₂ + λ_scrap + λ_CCS | ≤ 0.6 | 0.6–0.8 | 0.8–0.9 | 0.9–1.0 | 1.0–1.2 | 1.2–1.7 | > 1.7 |
|---|---|---|---|---|---|---|---|
| Cells | 11,088 | 6,336 | 2,880 | 2,832 | 3,792 | 5,520 | 2,112 |
| Feasible | 0.1 % | 6 % | 25 % | 44 % | 60 % | 74 % | 75 % |

- Ranking power: AUC¹ 0.90 overall (0.94 / 0.90 / 0.83 by target).
- **Used as a ranking (your choice (b)), with the statement that below λ ≈ 0.6 almost nothing is feasible.** No fixed threshold: the other measures (grid, NG growth, efficiency, waste heat) supply a roughly fixed amount (≈ 2.5 Gt without CCS), not a fixed share, and part of the CCS potential substitutes for them rather than adding to them.
- Not sufficient: above 1, feasibility levels off at ~75 %; build budget, legacy retirement, fuel supply and timing decide the rest.
- Policy reading: most of the required cut must be coverable by three capacities India has only at pilot scale (H₂-DRI, CCS) or must build up (scrap collection beyond today's pool).

¹ The probability that a randomly chosen feasible cell has a higher λ than a randomly chosen infeasible one.

### 8.3 Open calls added

1. **Scrap growth in the study templates is 6 %/yr; the audited central value is 5 %** (`definitions.mod:154`). Results at 6 % lean optimistic (e.g. Fig. 3 at 1.8, mid ramp, H₂ 2035 is feasible at CCS 0.05 with 6 % but not with 5 %). Proposed: set templates to 5 %.
2. **2050 demand.** The central S-curve gives 545 Mt, above the median of published projections (≈ 444 Mt: TERI 300, MoS/TERI 374, IEA ≈ 444, NITI 624, TERI-cited 500–760). Option: anchor the S-curve to 444 Mt in 2050 (≈ 500 Mt saturation, close to the 510 sensitivity: 13 infeasible Fig. 3 cells instead of 17).
3. **CCS central level:** keep 0.25 (median of scenario sources, all ambitious) or use a lower central value; the axis now covers 0–0.25 either way.
4. **Monte Carlo at low CCS** (0.05 slice, ~1 h) not yet run.
