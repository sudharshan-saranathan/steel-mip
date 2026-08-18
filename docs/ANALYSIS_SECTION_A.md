# Section A — analysis of the post-capacity-fix matrix

Table: `scenarios/_matrix/results/matrix.parquet`, model_commit `2268de9`,
46,656 cells, 27,099 solved / 19,557 infeasible, 0 errors, 16.1 min.
Every number here is produced by `scenarios/_matrix/analyse_headlines.py`
(raw output: `analysis_section_a_raw.txt`). Nothing below is hand-arithmetic.

## Two rules the analysis obeys

1. **Cost claims use calibrated rows only.** `extrapolated == 1` on 67% of
   solved rows. The flag is exactly `grid_ef_target ∉ {0.00035, 0.00045,
   0.00055}` (verified: it is a pure function of the grid level), because
   those are the only three of nine levels inside the tariff's
   $0.055–0.085/kWh anchors. 9,068 rows are usable for $/t. Feasibility uses
   all 46,656.
2. **Deltas are paired.** Infeasibility is 19.7% at `h2_start` 2030 and 62.2%
   at 2045, so an unpaired mean makes any penalty shrink by selection alone —
   in exactly the direction of the headline claim. Every delta reports
   `n_pairs` and `n_dropped`.

## BLOCKER — the `h2_start` axis is confounded with the ramp crest

`core/definitions.mod:388` defines `h2_peak_year := ng_h2_start_year +
h2_peak_lag` (lag 5). Delaying the H2 debut therefore does **two** things:
it forbids H2-DRI for longer *and* it slides the Gaussian buildout crest —
the 25%/yr surge in `h2elec_growth` — five years later, nearer the end of the
horizon where the cumulative cap binds hardest. This is the same
bundled-axis defect the matrix was built to expose, in the axis carrying the
headline finding.

**Evidence it is not a pure restriction.** In an LP, a later `No_H2_Before`
can only shrink the feasible set, so the objective must be non-decreasing in
`h2_start`. It is not: over paired coordinates, **67.3% of 2030 → 2035 pairs
get CHEAPER with delay** (n = 7,626, largest −₹2.67e10 in objective).

**Controlled test** (`experiments/h2_crest_confound.py`) — same coordinates,
crest pinned at 2035 via `h2_peak_lag := 2035 − start`:

| `h2_start` | LCOP, crest coupled (shipped) | LCOP, crest fixed at 2035 |
|---|---|---|
| 2030 | 527.07 | 527.07 |
| 2035 | **522.28** (cheaper than 2030) | 529.21 |
| 2040 | 533.04 | 550.31 |
| 2045 | 553.55 | 557.37 |

Decoupled, LCOP is monotone in the debut year, as theory requires. Coupled,
2035 shows a spurious −4.8 $/t "delay dividend", and the 2030 → 2045 penalty
reads 26.5 $/t instead of 30.3 $/t.

**Consequence.** Every `h2_start` number below (Headline 1) is contaminated
and must not be published as-is. The fix is a model decision, not an analysis
one: either pin the crest (make `h2_peak_lag` absolute, so the ramp shape is
a technology fact independent of policy timing) or promote the crest to its
own lever. Then re-sweep — only the `h2_start` axis is affected, so the other
levers below stand.

## Headline 1 (CONTAMINATED — for reference only)

Delay penalty, 2030 → 2045, calibrated rows, abundant coal / policy gas /
`avg_emi` 1.8, paired on the other 8 coordinates:

| scrap growth | penalty $/t | n_pairs |
|---|---|---|
| ≤ 0.04 | infeasible at 2045 at every coordinate | 0 |
| 0.06 | +28.36 | 54 |
| 0.08 | +10.43 | 54 |
| 0.10 | +2.52 | 54 |

The shape survives the capacity fixes (pre-fix: +28.6 / +8.5 / +0.4), and the
2030→2045 pair is the least contaminated one — but the intermediate steps go
negative (2030 → 2035 is −2.52 $/t at scrap 0.06), which is the confound
showing through. Re-run after the crest decision.

## Headline 2 — mandated phase-out of the 2025 fleet: **+37.83 $/t**

n_pairs 4,532, dropped 4. Pre-fix estimate was +36.6 $/t from a single
coordinate; the paired mean over the calibrated set confirms it.
Emissions are identical to 1.5e-07 tCO2 — the cumulative cap binds either
way, so this is pure avoided capex: forced retirement makes the model rebuild
207.75 Mt it already owns. BOF's 2050 share falls 4.88 pp and H2-DRI's rises
1.08 pp under the phase-out.

**Correction to an earlier claim.** Aggregate infeasible shares are 0.419 at
both `legacy` levels and at all three `build_cap` levels, which looked like
"no effect on feasibility". Cell-for-cell it is not exactly zero: **15 of
23,328** coordinate groups flip across `legacy`, and **8 of 15,552** across
`build_cap`. The effect is real but confined to ~0.06% of the design — state
it as "feasibility is essentially insensitive", not "identical".

## Headline 3 — shared annual build budget

| change | LCOP | n_pairs |
|---|---|---|
| tight (20) → mid (30 Mt/yr) | −7.24 $/t | 3,021 |
| tight (20) → loose (40 Mt/yr) | −7.96 $/t | 3,021 |
| mid (30) → loose (40 Mt/yr) | −0.72 $/t | 3,023 |

Zero pairs dropped: the budget never decides feasibility. The value is
**concentrated in the first 10 Mt/yr** (91% of the total gain) and nearly
exhausted by 30 Mt/yr — the budget stops binding somewhere in 30–40. The
pre-fix figure of 3.8 $/t for 40 → 20 was measured at one coordinate and
understates it by half.

## Headline 4 — electrolyser ramp

low → medium −4.38 $/t (n 2,610), medium → high −3.42 $/t (n 3,041). Now a
genuinely H2-specific lever, since `build_cap` was separated out. Note these
pairs hold `h2_start` fixed, so the crest confound does not enter.

## Headline 5 — mechanism: hydrogen is displaced, not deferred

At `h2_start` 2030, mean 2050 shares against scrap growth:

| scrap growth | H2-DRI | scrap-EAF | BF-BOF | 2050 scrap use |
|---|---|---|---|---|
| 0.00 | 0.290 | 0.041 | 0.414 | 37 Mt |
| 0.04 | 0.252 | 0.152 | 0.315 | 99 Mt |
| 0.06 | 0.224 | 0.259 | 0.236 | 159 Mt |
| 0.08 | 0.156 | 0.425 | 0.181 | 253 Mt |
| 0.10 | 0.081 | 0.635 | 0.134 | 393 Mt |

H2-DRI's share falls 29% → 8% as scrap grows. The delay penalty collapses
because hydrogen is **displaced by scrap**, not because timing stops
mattering — the claim is near-tautological unless stated that way.

**The retracted 41.5% scrap ceiling is gone.** `share_scrap` now ranges
0.000–0.707 (mean 0.361) with no pile-up at a constant; the shared build
budget removed the per-route artifact. Do not repeat 41.5%.

## Headline 6 — feasibility frontier (all 46,656 cells)

P(solved), scrap growth × emissions target:

| scrap | 1.6 | 1.8 | 2.0 |
|---|---|---|---|
| 0.00 | 0.049 | 0.196 | 0.472 |
| 0.02 | 0.088 | 0.287 | 0.599 |
| 0.04 | 0.162 | 0.440 | 0.766 |
| 0.06 | 0.324 | 0.683 | 0.907 |
| 0.08 | 0.628 | 0.919 | 0.993 |
| 0.10 | 0.942 | 1.000 | 1.000 |

Scrap dominates feasibility more than any other lever: 76.1% infeasible at
zero growth, 1.9% at 0.10. At `avg_emi` 1.6 nothing below 0.08 growth is
comfortably reachable. This is the strongest policy statement in the table
and it is unaffected by both the crest confound and the calibration filter.

## Two invariants that held

- **Grid-EF tripwire clean**: exactly one `grid_ef_2050` per target, so the
  one-AMPL-instance-per-cell invariant was not violated.
- **The emissions cap binds everywhere**: `avg_emis` equals its target on all
  27,099 solved rows, max slack 0.0000. Cross-target cost comparisons are
  therefore comparing like with like.

## Next

1. **Decide the crest**: pin `h2_peak_lag` to an absolute year or promote it
   to a lever. Then re-sweep (only `h2_start` is affected).
2. Verify `h2elec_growth` binds before claiming H2 uptake is
   deployment-limited — the crest result is indirect evidence that it does.
3. Parameter provenance table (no citations anywhere in `core/` yet).
4. Section B (`MonteCarlo/`, `RegretAnalysis/`) — the thetas live there.
