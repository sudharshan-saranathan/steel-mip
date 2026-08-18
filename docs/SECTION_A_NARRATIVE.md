# Section A — results narrative (draft)

Draft prose for the results section. Numbers of record live in
`ANALYSIS_SECTION_A.md`; every figure quoted here traces to
`scenarios/_matrix/analyse_headlines.py` against `matrix.parquet`
(model_commit `0c3a6f2`). Nothing here is hand-arithmetic.

---

## Scope of the reported quantities

All results come from a single design over eight policy-controlled levers and
one emissions target: coking-coal availability (2 regimes), gas allocation
(2), green-H2 debut year (4: 2030–2045), scrap-availability growth (6:
0.00–0.10/yr), 2050 grid emission factor (9: 50–850 gCO2/kWh), electrolyser
deployment rate (3), the shared annual build budget across the four
conventional routes (3: 20/30/40 Mt/yr), and retirement policy for the 2025
fleet (2). The cross product is **46,656 scenarios**, each solved as an
independent linear programme; 30,371 (65.1%) are feasible and none errored.
Learning rates for hydrogen and CCS are held fixed: they depend on global
science rather than Indian policy, and are sampled in Section B.

Two conventions apply throughout and should be read into every number below.
First, **all cost figures are drawn from the 9,068 feasible scenarios in which
the grid emission factor lies inside the calibrated band** (350–550
gCO2/kWh). Outside that band the coupled industrial electricity tariff is
extrapolated beyond its $0.055–0.085/kWh anchors; feasibility remains
interpretable across the full range, cost does not. Second, **every reported
difference is paired**: it is computed only over scenarios feasible at both
settings of the lever in question, because infeasibility is itself strongly
patterned (4.8% of scenarios at a 2030 hydrogen debut against 62.2% at 2045),
and an unpaired average would shrink every penalty by selection alone.

## Feasibility: hydrogen and scrap are substitutes, not complements

The clearest result is about what is reachable at all, and it does not depend
on the cost conventions above.

Meeting an average emissions intensity of 1.6 tCO2/t crude steel requires
either an early hydrogen programme or an aggressive scrap supply — but not
both. With **no growth at all in scrap availability**, a 2030 hydrogen debut
still reaches the 1.6 target in 68.5% of scenarios. Conversely, with scrap
availability growing at 10%/yr, the target is reached in 81.8% of scenarios
**even if hydrogen is delayed to 2045**. Neither lever is individually
necessary. What the model rules out is the corner where both fail: at 2040 or
later hydrogen debut combined with scrap growth of 0.04/yr or less, the 1.6
target is unreachable in essentially every configuration of the remaining six
levers (P(feasible) ≤ 0.009).

The substitution is not an artefact of averaging across targets. It holds at
1.8 (0.898 for early hydrogen at zero scrap growth; 1.000 for high scrap with
a 2045 debut) and at 2.0, where it is close to unconstrained. It does weaken
as the target tightens: relying on either lever alone carries a real
probability of failure at 1.6 (0.685 and 0.818) that it does not carry at 1.8.
The policy statement is therefore not "hydrogen or scrap, freely
interchangeable" but **"either route is sufficient at 1.8 and 2.0, and either
is still viable at 1.6 at a measurable cost in success probability."**

## The cost of delay is a property of the scrap supply

Conditional on feasibility, the cost of postponing the hydrogen programme is
governed almost entirely by how much scrap the economy collects. Against a
2030 debut, at an emissions target of 1.8 with abundant coking coal and policy
gas allocation:

| Scrap growth | 2050 scrap use | Delay to 2035 | to 2040 | to 2045 |
|---|---|---|---|---|
| 0.00 | 37 Mt | +15.16 | infeasible | infeasible |
| 0.02 | 61 Mt | +10.08 | +41.50 * | infeasible |
| 0.04 | 99 Mt | +5.60 | +30.89 * | infeasible |
| 0.06 | 159 Mt | +1.42 | +15.71 | **+36.58** |
| 0.08 | 253 Mt | +0.01 | +3.37 | +14.33 |
| 0.10 | 394 Mt | 0.00 | +0.19 | +3.96 |

$/t crude steel, paired. \* rests on 6 and 36 surviving pairs respectively of
54, the remainder being infeasible at that delay; the other cells use all 54.

A fifteen-year delay costs 36.58 $/t in a world of moderate scrap growth and
3.96 $/t in a scrap-rich one — an order of magnitude apart, driven by a lever
that has nothing to do with hydrogen. Below 0.06/yr growth the delay is not
priced at all: the target simply cannot be met without hydrogen by 2045.

**The deadline is not 2030.** Reading across the first delay column, the
initial five years are essentially free wherever scrap growth reaches 0.08/yr
(+0.01 and 0.00 $/t) and cost 1.42 $/t at 0.06, against 36.58 $/t for the full
fifteen. The cost is concentrated in the second and third five-year steps, not
the first. The exception is the scrap-poor world, where the ordering inverts
and delay is expensive immediately: +15.16 $/t for five years at zero scrap
growth, because there is no substitute available to absorb the deferral.

These penalties are, if anything, conservative. The model charges capital as
overnight expenditure in the year of construction and credits no residual
value for asset life extending beyond 2050. On the baseline configuration,
capital paid for but never used amounts to 13.1% of net present value under a
2030 debut against 8.5% under a 2045 debut — the *earlier* programme bears
more unrecovered capital, so crediting terminal value would widen rather than
narrow the gap.

## Mechanism: hydrogen is displaced, not merely deferred

The delay penalty collapses at high scrap growth because hydrogen is
substituted away, not because timing ceases to matter. At a 2030 debut, the
2050 production shares move as follows:

| Scrap growth | H2-DRI | Scrap-EAF | BF-BOF |
|---|---|---|---|
| 0.00 | 0.496 | 0.056 | 0.187 |
| 0.04 | 0.418 | 0.167 | 0.149 |
| 0.08 | 0.223 | 0.440 | 0.133 |
| 0.10 | 0.110 | 0.635 | 0.120 |

Hydrogen's share falls from 50% to 11% as scrap grows, while the incumbent
blast-furnace route stays nearly flat at 12–19%. **The two low-carbon routes
displace one another; neither displaces the incumbent much beyond a floor.**
This is what makes the delay result non-tautological — postponing hydrogen is
cheap in a scrap-rich world precisely because the model was going to build
little hydrogen there anyway. Stated without the mechanism, the finding would
reduce to "delaying something you do not use is inexpensive."

Deployment capacity still constrains hydrogen, but with diminishing force.
Raising the electrolyser ramp from low to medium adds 3.86 percentage points
of hydrogen share, while medium to high adds only 1.40 (installed H2-DRI
capacity in 2050: 119.6, 154.1 and 169.6 Mt). Hydrogen uptake is therefore
**deployment-limited at a low ramp and approaching cost-limited at a high
one**, and should not be characterised as one or the other without that
qualification.

## Two independent policy levers

**Retirement policy.** Mandating a linear phase-out of the 2025 fleet by 2050,
rather than letting assets run their technical lives, costs **38.17 $/t** for
*identical* cumulative emissions — the cumulative cap binds either way. The
cost is avoided capital expenditure, not stranded-asset friction: forced
retirement compels the model to rebuild 207.75 Mt of capacity it already owns,
shifting 6.3 percentage points of 2050 share out of blast-furnace steel. This
is the most stable result in the study, varying only between 37.49 and 39.01
$/t across all four hydrogen debut years. It is also the one figure likely to
be *overstated* by the absence of terminal value, since the forced rebuilds
land late in the horizon and receive no residual credit.

**Annual build capacity.** The shared budget across the four conventional
routes — finance and EPC capacity, 20 to 40 Mt/yr — never determines
feasibility: no scenario pair was lost to it. Its cost value depends
sharply on when hydrogen arrives, and should be reported that way rather than
averaged. Raising the budget from 20 to 40 Mt/yr is worth **3.21 $/t under a
2030 hydrogen debut and 16.38 $/t under a 2045 debut**, a five-fold
difference. The mechanism is direct: with no hydrogen route available, the
conventional fleet must carry the entire transition, and the rate at which it
can be rebuilt becomes the binding industrial constraint. **The later the
hydrogen programme, the more finance and construction capacity matters** — a
policy complementarity that a single averaged figure would conceal. Within any
given debut year, roughly 90% of the available gain is captured by the first
10 Mt/yr of additional budget.

---

## Note on the corrected ramp

The delay penalties above are monotone in the debut year by construction: a
later debut only removes options, verified across all 19,265 paired
comparisons. This required correcting the electrolyser ramp ceiling, which
previously decayed after its crest and allowed a *later* hydrogen programme to
out-build an earlier one. The diagnosis belongs in methods; the single
sentence above is what results needs.
