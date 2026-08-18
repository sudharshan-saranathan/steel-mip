# Section A — analysis of the design matrix

Table: `scenarios/_matrix/results/matrix.parquet`, model_commit `0c3a6f2`,
46,656 cells, **30,371 solved / 16,285 infeasible, 0 errors**, 14.1 min.
Every number here is produced by `scenarios/_matrix/analyse_headlines.py`
(raw output: `analysis_section_a_raw.txt`). Nothing is hand-arithmetic.

Supersedes the pre-ratchet reading of this table. The electrolyser ramp
ceiling now plateaus at its crest instead of decaying (`h2_ramp_ratchet`, see
`docs/core/modules/v_capacity.md`); the previous ceiling let a LATE hydrogen
debut out-build an early one, which made delay come out cheaper in 67.3% of
paired cells. Retained snapshots: `matrix_preratchet.*` (decaying ramp),
`matrix_pre_capfix.*` (before the four capacity fixes).

## Two rules the analysis obeys

1. **Cost claims use calibrated rows only.** `extrapolated == 1` marks rows
   where the coupled electricity tariff runs past its $0.055–0.085/kWh
   anchors. The flag is exactly `grid_ef_target ∉ {0.00035, 0.00045,
   0.00055}` — verified a pure function of the grid level. Feasibility uses
   all 46,656 cells.
2. **Deltas are paired.** Infeasibility runs 14% at `h2_start` 2030 and 62%
   at 2045, so an unpaired mean shrinks any penalty by selection alone — in
   exactly the direction of the headline claim. Every delta reports
   `n_pairs` and `n_dropped`.

## Three invariants that held

- **Monotone in the H2 debut year**: 0 violations in 19,265 paired
  comparisons (residuals ~1e-3 against a 1e12 objective — solver noise). A
  later `No_H2_Before` now only ever removes options, as an LP requires.
  This is the check the previous model failed.
- **The ratchet is a pure relaxation**: 3,272 cells became feasible and
  **zero** became infeasible, which is what raising a ceiling must do.
- **Grid-EF tripwire clean** (one `grid_ef_2050` per target, so the
  one-AMPL-instance-per-cell invariant held) and **the emissions cap binds
  on every solved row** (max slack 0.0000), so cross-target cost comparisons
  compare like with like.

## Headline 1 — the cost of delaying hydrogen

Calibrated rows, abundant coal / policy gas / `avg_emi` 1.8, paired on the
other 8 coordinates. LCOP penalty in $/t against a 2030 debut:

| scrap growth | → 2035 | → 2040 | → 2045 |
|---|---|---|---|
| 0.00 | +15.16 | infeasible | infeasible |
| 0.02 | +10.08 | +41.50 ¹ | infeasible |
| 0.04 | +5.60 | +30.89 ² | infeasible |
| 0.06 | +1.42 | +15.71 | **+36.58** |
| 0.08 | +0.01 | +3.37 | +14.33 |
| 0.10 | 0.00 | +0.19 | +3.96 |

¹ only 6 of 54 pairs survive — the rest are infeasible at 2040.
² 36 of 54.

**The finding, restated.** The penalty is governed by the scrap supply, not
by hydrogen: at 0.10 growth, delaying 15 years costs 3.96 $/t; at 0.06 it
costs 36.58; below 0.06 the 2045 debut is infeasible at every coordinate.
The mechanism is displacement (Headline 5) — delay gets cheap because
hydrogen is *substituted away*, not because timing stops mattering. State it
that way or the claim reads as tautological.

**New, and sharper: the deadline is not 2030.** Read the `→ 2035` column.
With scrap growth at or above 0.08 the first five years of delay are **free**
(+0.01 and 0.00 $/t), and at 0.06 they cost 1.42 $/t against 36.58 for
fifteen. The cost is concentrated in the second and third five-year steps.
Under the pre-ratchet model this column was negative — a spurious delay
dividend — so this statement is new to this run.

Below 0.04 growth the ordering inverts: delay is expensive **immediately**
(+15.16 $/t for five years at zero scrap growth) because there is no
substitute to displace hydrogen with. The scrap-poor world is the one where
the 2030 deadline is real.

## Headline 2 — mandated phase-out of the 2025 fleet: **+38.17 $/t**

n_pairs 5,096, dropped 10. Emissions identical to 4e-08 tCO2 — the
cumulative cap binds either way — so this is pure avoided capex: forced
retirement makes the model rebuild 207.75 Mt it already owns. BOF's 2050
share falls 6.26 pp, H2-DRI's rises 0.48 pp.

**Robust.** Broken out by `h2_start`: 37.49 / 38.43 / 39.01 / 38.27 $/t at
2030 / 2035 / 2040 / 2045 — a 1.5 $/t spread. It also barely moved across
the ramp change itself (37.83 pre-ratchet), so it is the most stable number
in the study.

## Headline 3 — shared annual build budget

| change | LCOP | n_pairs |
|---|---|---|
| tight (20) → mid (30 Mt/yr) | −5.02 $/t | 3,400 |
| tight (20) → loose (40 Mt/yr) | −5.54 $/t | 3,400 |
| mid (30) → loose (40 Mt/yr) | −0.52 $/t | 3,401 |

Zero pairs dropped: the budget never decides feasibility. **90.6% of the
20 → 40 gain is captured by the first 10 Mt/yr.** Whether the constraint
actually stops binding above 30 is NOT established — `report.mod` has no
peak-annual-build readback, and a small delta is not evidence of slack. Add
the readback before claiming it.

**Report the breakout, not the mean.** By `h2_start` the tight → loose delta
is −3.21 / −3.54 / −5.10 / **−16.38** $/t at 2030 / 2035 / 2040 / 2045.
Conventional build capacity is worth **5x more when hydrogen arrives late**,
which is mechanistically clean — with no H2 route available the conventional
fleet must carry the transition — and it means the aggregate −5.54 is an
artifact of how the design weights `h2_start`. This is a policy result in its
own right: *the later the hydrogen programme, the more finance and EPC
capacity matters.*

## Headline 4 — electrolyser ramp

low → medium −4.13 $/t (n 3,048), medium → high −2.32 $/t (n 3,470).
Diminishing, and now a genuinely H2-specific lever since `build_cap` was
separated out. Both pairs hold `h2_start` fixed.

## Headline 5 — mechanism: hydrogen is displaced, not deferred

At `h2_start` 2030, mean 2050 shares against scrap growth:

| scrap growth | H2-DRI | scrap-EAF | BF-BOF | 2050 scrap use |
|---|---|---|---|---|
| 0.00 | 0.496 | 0.056 | 0.187 | 37 Mt |
| 0.02 | 0.467 | 0.099 | 0.168 | 61 Mt |
| 0.04 | 0.418 | 0.167 | 0.149 | 99 Mt |
| 0.06 | 0.340 | 0.273 | 0.141 | 159 Mt |
| 0.08 | 0.223 | 0.440 | 0.133 | 253 Mt |
| 0.10 | 0.110 | 0.635 | 0.120 | 394 Mt |

H2-DRI falls **50% → 11%** as scrap grows, against a near-constant BF-BOF
share: the two zero-carbon routes trade off against each other, not against
the incumbent. The ratchet raised H2-DRI's ceiling substantially (it was
29% → 8% under the decaying ramp), so hydrogen's share is now large enough
that the displacement story carries the paper.

**The retracted 41.5% scrap ceiling stays retracted** — `share_scrap` spans
0.00–0.71 with no pile-up at a constant.

## Headline 6 — the feasibility frontier (all 46,656 cells)

P(solved), scrap growth × emissions target:

| scrap | 1.6 | 1.8 | 2.0 |
|---|---|---|---|
| 0.00 | 0.201 | 0.347 | 0.559 |
| 0.02 | 0.243 | 0.419 | 0.673 |
| 0.04 | 0.315 | 0.532 | 0.803 |
| 0.06 | 0.433 | 0.728 | 0.919 |
| 0.08 | 0.684 | 0.926 | 0.993 |
| 0.10 | 0.942 | 1.000 | 1.000 |

P(solved), scrap growth × H2 debut:

| scrap | 2030 | 2035 | 2040 | 2045 |
|---|---|---|---|---|
| 0.00 | 0.858 | 0.468 | 0.123 | 0.028 |
| 0.04 | 0.957 | 0.704 | 0.355 | 0.185 |
| 0.08 | 1.000 | 0.975 | 0.829 | 0.666 |
| 0.10 | 1.000 | 1.000 | 0.983 | 0.939 |

**This is the headline the ratchet changed most.** Under the decaying ramp
the story was "scrap dominates feasibility" (0.534 solved at zero scrap
growth with a 2030 debut). It is now **either/or**: an early hydrogen
programme reaches 0.858 with *no* scrap growth at all, and abundant scrap
reaches 0.939 with hydrogen delayed to 2045. Neither lever is individually
necessary; the infeasible corner is where **both** fail — late hydrogen and
poor scrap collection. That is a stronger and more useful policy statement
than the single-lever version, and it is the one to lead with.

## Open items

1. **`h2elec_growth` binds** — the ratchet result is strong indirect evidence
   (raising the ceiling moved 3,272 cells into feasibility), but confirm
   directly before claiming H2 uptake is deployment-limited.
2. **Peak-annual-build readback** in `report.mod`, to settle whether
   `cap_add_total` stops binding above 30 Mt/yr.
3. **Parameter provenance table** — coefficients are literature-sourced but
   no citation appears in `core/` or `docs/`. Needed as supplementary
   material; values are already extracted per module in `docs/core/`.
4. **Methods notes** carried over: `build_h2dri` has no per-year build cap
   (unlike the four conventional routes); BF-BOF decarbonises on a calendar
   schedule with no capex or decision; `bf_h2_in` is dead code; the model has
   no carbon price, only the cap; `emission_monotonic` is dropped in every
   run; the ramp ceiling has no saturation roll-over.
5. **Section B** (`MonteCarlo/`, `RegretAnalysis/`) still on the old
   per-study layout. `theta_tech` and `theta_ccs` belong there.
