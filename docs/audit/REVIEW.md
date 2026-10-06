# Review document — overnight run of 2026-10-06/07

**Status: COMPLETE** (Stages 1–3). Read §1 first, then the "Needs your call" list (§4). Every model change is its own commit on `fix-wave-01`, so any one can be reverted alone (`git revert <hash>`).

## 1. Summary

- **Solver:** the AMPL licence variable reaches only new sessions, so tonight everything ran on the AMPL **demo** + **HiGHS** through `tools/ampl_highs_bridge.py`. The bridge rebuilds the exact LP from AMPL's `expand` output. On the unchanged model it reproduces the paper's Fig. 3 exactly (524.3 vs 524; 567.7 vs 568; 517.2 vs 517; 555.6 vs 556; the infeasible cell is infeasible). **To confirm tomorrow:** in a new session run `python -m amplpy.modules activate $AMPL_LICENSE_UUID`, then `python3 tools/benchmark.py --tag licensed` and compare with `tools/benchmark_results.csv`.
- **Branch `fix-wave-01`:** Nakul's `b33b88a` imported unchanged, then 14 fix commits (§2). The model solves under every study template (H₂ delay, sectoral synergy, feasibility drivers, Monte Carlo).
- **2025 calibration:** the model's 2025 emission intensity moves from **2.80 to 2.50 tCO₂/tCS** (Ministry of Steel reports 2.54). Nothing was tuned to hit that number. The gap closed through sourced emission factors, BF fuel rates, route shares and in-plant power.
- **Effect on results:** see §3. The biggest change for the paper: **delaying H₂ now costs almost nothing when gas or coal is available** (LCOP flat at ~467 $/t for H₂ starts 2030–2045 at 1.8 tCO₂/t, against 524 → 554 in the paper). The double-scarcity infeasibility survives. This weakens the paper's "cost of delaying green H₂" message and strengthens the role of NG-DRI. The result leans heavily on the NG-availability axis, whose basis (10 % of national gas) is unsourced; see §4.

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

Not changed in code: ST-08 (h2_ramp_mode 0 coupling; unused mode), ST-09 (capacity envelope units; documented), ST-15 (core default NG cap = shock trajectory; every study overrides it).

## 3. Results before and after

### Fig. 3 grid (LCOP $/t / H₂-DRI share 2050 %; X = infeasible)

| EF | H₂ supply | 2030 | 2035 | 2040 | 2045 |
|---|---|---|---|---|---|
| 1.6 | Low | 568/22 → **487/21** | X → **489/17** | X → X | X → X |
| 1.6 | Mid | 545/34 → **485/34** | 567/28 → **485/33** | X → **490/21** | X → X |
| 1.6 | High | 542/36 → **484/35** | 548/37 → **484/35** | X → **488/28** | X → X |
| 1.8 | Low | 530/19 → **467/14** | 537/14 → **467/14** | 548/8 → **468/10** | 556/3 → **468/4** |
| 1.8 | Mid | 524/29 → **467/25** | 527/26 → **467/25** | 542/16 → **467/21** | 554/4 → **468/9** |
| 1.8 | High | 523/29 → **467/29** | 523/30 → **467/29** | 537/23 → **467/28** | 553/6 → **468/13** |
| 2.0 | Low | 510/15 → **452/5** | 512/13 → **452/5** | 516/7 → **452/5** | 518/1 → **452/4** |
| 2.0 | Mid | 508/18 → **452/9** | 508/18 → **452/9** | 514/13 → **452/9** | 517/2 → **452/8** |
| 2.0 | High | 508/19 → **452/9** | 508/19 → **452/9** | 512/18 → **452/9** | 517/3 → **452/9** |

Readings:
- LCOP falls 55–85 $/t everywhere, mostly because capex was 2–3× too high (ST-01) and NG-DRI used 60 % too much gas.
- **The cost of delaying H₂ almost vanishes** when coal and gas are abundant: NG-DRI (now 10.9 GJ/t DRI, sourced) and BF-BOF fill the gap at similar cost.
- At 1.6, feasibility extends to a 2040 start (mid/high ramps).

### Sensitivities at EF 1.8, mid ramp (corrected model)

| Case | H₂ 2030 | H₂ 2045 |
|---|---|---|
| Fig. 3 backdrop (coal and NG abundant) | 466.8 | 468.2 |
| NG scarce (BAU axis) | 472.6 (before: 532.2) | 475.8 (before: **infeasible**) |
| NG scarce + coal scarce | 472.7 (before: 532.3) | **infeasible** (before: infeasible) |
| Discount rate 10 % instead of 6 % | 465.5 (before: 476.1) | 468.1 (before: 509.1) |

Smoke tests: sectoral-synergy and Monte Carlo templates solve. A feasibility-drivers case (scarce coal and NG, 20 Mt/yr build, H₂ 2035) is infeasible both before and after under mandated phase-out. Under run-life it was infeasible before and solves after.

## 4. Needs your call (short list)

1. **NG availability axis.** The basis "10 % of national gas to steel" has no source. PPAC shows sponge iron used ~1 % of national gas in FY26, and the 2025 cap (5.35 Mt) is 6–10× actual steel use. Now that gas use per t DRI is corrected, the same cap supports ~60 % more NG-DRI, and the "H₂ delay is cheap" result depends on it. Options: rebase to PNGRB's steel projections; keep and label as an assumption; or add a lower case.
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
