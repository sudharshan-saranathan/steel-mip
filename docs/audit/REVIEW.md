# Review document — overnight run of 2026-10-06/07

**Status: IN PROGRESS.** Updated as each step lands. Read top to bottom. Every item marked ⚑ is a decision I made on your behalf; each is a separate commit on `fix-wave-01`, so any one can be reverted alone.

## 0. Where things are

| What | Where |
|---|---|
| Model fixes (Stage 3) | branch **`fix-wave-01`** in `steel-mip`. First commit = Nakul's `b33b88a` unchanged, then one commit per fix |
| Audit documents (Stage 1, Stage 2 sheets, this file) | branch `claude/pensive-archimedes-pem4p9`, folder `docs/audit/` (also copied to `fix-wave-01` at the end) |
| Solver | AMPL **demo** + HiGHS through `tools/ampl_highs_bridge.py`, because the licence variable only reaches new sessions. The bridge reproduces paper Fig. 3 exactly (524.3 $/t vs 524; 567.7 vs 568; 517.2 vs 517; 555.6 vs 556; infeasible cell infeasible). **Tomorrow:** in a new session, `python -m amplpy.modules activate $AMPL_LICENSE_UUID` and rerun `tools/benchmark.py` to confirm. |
| Benchmark | `tools/benchmark.py` solves 8 cells of the Fig. 3 backdrop (EF 1.6/1.8/2.0, mid ramp, H₂ start 2030–45); results in `tools/benchmark_results.csv`, one tag per commit |

## 1. Commits on fix-wave-01 and their effect

Benchmark cell: EF 1.8, mid ramp, H₂ from 2030 (paper Fig. 3: LCOP 524 $/t, H₂-DRI 29 %). "ei_2025" = model 2025 emission intensity (reported: 2.54 tCO₂/tCS).

| # | Commit | What | LCOP $/t | H₂ share 2050 | ei_2025 |
|---|---|---|---|---|---|
| 0 | `82612e3` | Nakul's code, unchanged | 524.3 | 28.7 % | 2.795 |
| 1 | `7f9034a` | ST-01 capex up-front + sourced values (agreed with you) | 474.6 | 25.5 % | 2.795 |
| 2 | `5d83c50` | Lifetimes 40 yr; 2025 fleet to 2050 (agreed) | 468.7 | 26.4 % | 2.795 |
| 3 | `65467a7` | ST-02 pellet ore ÷ → × (plain bug) | 479.8 | 26.5 % | 2.795 |
| 4 | `79a79c6` | ST-16 salvage credit (agreed in principle; design ⚑ below) | 455.9 | 36.6 % | 2.795 |
| 5 | `62b8214` | DRI, EAF/IF, scrap coefficients ⚑ | 428.8 | 28.5 % | 2.718 |
| – | `c2c90e7` | Comment corrections (ST-14, build budget); no effect | – | – | – |
| 6 | `3f225f8` | ST-13 emission factors as sourced parameters ⚑ | 420.7 | 24.2 % | 2.555 |
| 7 | `9fcfdb8` | ST-03 pellet fuel, ST-04 purchased breeze carbon ⚑ | 424.3 | 26.6 % | 2.620 |
| 8 | `9d70a87` | BF-BOF coefficients (fuel rate etc.) ⚑ | 409.9 | 17.6 % | 2.442 |

## 2. Decisions I made on your behalf (⚑)

### ST-16 salvage design
Straight-line credit for life remaining after 2050, valued at the start of 2051 and discounted. Applied to steel routes, electrolyser, dedicated renewables and CCS retrofits. Not applied to supply-chain builds (`scrapchain`, `coalchain`, `ngchain`), which have no lifetime parameter. *Effect:* late investment is no longer penalised; H₂-DRI's 2050 share rises noticeably.

### DRI, EAF/IF and scrap (sheet: `stage2/dri_eaf_scrap.md`)
| Call | My choice | Why |
|---|---|---|
| Coal per t DRI | **0.9 t/t on the existing 24 GJ/t coal basis** (21.6 GJ/t DRI; Indian kilns ~21 GJ/t) | Keeps the coal price and emission factor consistent; switching to Indian 14.7 GJ/t coal would need both rescaled together, which belongs with the emission-factor decision (ST-13) |
| NG per t DRI | **0.22 t/t** (10.9 GJ, median of five) | ≥3 India-relevant sources, so median rule. I added an estimate the sub-agent missed (MoS Table 10.1, 0.33 t), which supports the old value; median unchanged. **Gas availability caps are left as they are** (they describe supply, not DRI efficiency); the same cap now supports more NG-DRI |
| Kiln waste-heat power | **Left out** (pessimistic) | CEEW finds 350–380 kWh/t DRI on 65 % of capacity; including it would make coal-DRI cheaper |
| Scrap-route power | **590 kWh/t, costed as EAF** | median of four for 100 %-scrap charges; consistent with the EAF capex already adopted |
| Scrap supply | **Seed kept at 37 Mt; default growth 6 % → 5 %** (125 Mt in 2050 = NITI lower case) | A 33.4 Mt seed (FY24) contradicts the model's own 2025 scrap use of 37 Mt. **Study templates still use 6 % as central**; I did not change the paper's study design. Your call |

### BF-BOF coefficients and emission factors (sheet: `stage2/bfbof_coefficients.md`)
Verified in the source: Ministry of Steel 2024 Table 5.4 (BF fuel rate 505–579 kg/tHM; coke 350–480; PCI 60–199) and the BF-BOF route range 2.2–2.6 tCO₂/tCS.
| Call | My choice | Why |
|---|---|---|
| Coking-coal factor | **2.67** (IPCC 2006) | Pessimistic bound; supply ~76 % imported. India BUR-4 gives 2.22 for domestic coal |
| BF fuel rate 2025 | **coke 0.47 + PCI 0.11 = 0.58 t/tHM** | Top of the national range; the old 0.68 was ~100 kg above the worst plant |
| Non-coking coal factor | **2.32 t/t** (differs from the sheet's 1.76) | The DRI step kept coal mass on the 24 GJ/t basis, so the factor must be on the same basis: 24 GJ × 96.8 kg/GJ (India BUR-4 carbon content, the highest of BUR-2, BUR-4 and IPCC). 2.64 implied 110 kg/GJ, above every source |
| Pellets (ST-03) | **70 kWh/t + 1.6 GJ/t coal-fired induration** | Pessimistic: Indian fuel mix unsourced |
| Breeze (ST-04) | **2025 sinter breeze 0.05 t/t; purchased breeze carbon counted at 3.04 t/t** | Own breeze carbon is already counted in coking coal, so only the excess is added |

Not changed (noted for later): carbon in sold tar is counted as emitted (small over-count); whether "lime" flows mean limestone or burnt lime; BF slag kept at 0.30 although Indian ore suggests ~0.40 (slag earns a credit, so the lower value is pessimistic). 18 of 61 parameters in this group have no admissible source and keep their current values (sheet §H). SAIL's annual report could not be opened (incomplete TLS chain); I did not bypass certificate checks.

Deferred to the 2025-calibration step (with the demand/fleet sheet): `init_f_cdri` 0.902 → 0.84 and `cap0_cdri` 104.1 → 91.

## 3. Needs your call (short list)

1. Central scrap growth in the study templates: 6 % (paper) or 5 % (evidence)?

*(more to follow as the other sheets land)*
