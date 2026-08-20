# Handoff

## State — Section A is swept, analysed and written

Section A is **feasibility**: how structural levers affect what is reachable.
Cost results exist and are valid but were split into their own document, since
they answer a different question and rest on a third of the design.

| Document | What it is |
|---|---|
| `SECTION_A_NARRATIVE.md` | Results prose, feasibility only |
| `ANALYSIS_SECTION_A.md` | Numbers of record (cost + feasibility) |
| `COST_RESULTS.md` | Cost narrative, section placement undecided |
| `LITREVIEW_INDIA_STEEL.md` | Literature check on the framing |
| `analysis_section_a_raw.txt`, `analysis_section_a_feasibility.txt` | Raw script output |

Table: `scenarios/_matrix/results/matrix.parquet`, model_commit `be8751d`,
46,656 cells, 30,371 solved, 0 errors, 21.8 min at `-j 12`. `core/` is
unchanged since `0c3a6f2`. All results are gitignored — regenerate with
`run_matrix.py` then `to_parquet.py`.

**The `matrix_preratchet.*` and `matrix_pre_capfix.*` snapshots no longer
exist** on any machine reachable from this repo. The pre/post-ratchet
comparisons in `ANALYSIS_SECTION_A.md` (Headline 5, the 3,272-cell relaxation
count) therefore cannot currently be re-derived. To rebuild the pre-ratchet
snapshot, sweep with `h2_ramp_ratchet := 0`; the capacity-fix snapshot predates
the current model and is not recoverable.

**Never hand-derive a number.** `analyse_feasibility.py` and
`analyse_headlines.py` produce everything in the docs.

## What changed this session

1. **Found and fixed a ramp defect that inverted the headline finding.**
   `h2_peak_year = ng_h2_start_year + 5` couples the Gaussian buildout crest to
   the H2 debut — intended, and physically justified (the programme clock
   starts when the programme starts). But the ceiling *decayed* back to
   `h2_base` past the crest, so an industry that added 1.5 Mt/yr at its peak
   was allowed 0.24 Mt/yr five years later. A late debut therefore ended
   better-resourced than an early one, and **delay came out cheaper in 67.3%
   of paired cells** — impossible for a constraint that only forbids. Fix:
   `h2_ramp_ratchet` (default 1) holds the ceiling at `h2_peak_rate` once
   reached. Ramp phase = the state building infrastructure and supply chains;
   plateau = the finished state deploying steadily. Verified: `ratchet=0`
   reproduces the old LCOPs exactly, `ratchet=1` is monotone across all 19,265
   paired comparisons, and the change is a pure relaxation (3,272 cells newly
   feasible, zero newly infeasible).
2. **Fixed a silent data bug.** `to_parquet.py`'s `COORD_COLUMNS` was stale and
   its dedup collapsed 46,656 rows to 7,776. The key now derives from the axis
   registry; a missing axis column is fatal.
3. **Recast Section A as feasibility-only** and split the cost material out.
4. **Literature check**: no evidence anyone has mapped target reachability over
   a lever space for Indian steel.

## Findings that survived review

- **Partial substitution, not either/or.** At the 1.6 target: hydrogen alone
  0.685, scrap alone 0.818, both 1.000, neither 0.000. Either suffices at 1.8
  and 2.0; at 1.6 neither alone is reliable. (An earlier "either/or" phrasing
  was drawn from marginals — the joint contradicts it.)
- **Lever ranking by feasibility swing**: scrap 0.611, H2 debut 0.575, grid EF
  0.316, coking coal 0.123, ramp 0.123, gas 0.064, retirement 0.002, build
  budget 0.000.
- **Build budget and retirement are cost levers, not feasibility levers** —
  0.0% and 0.2% of scenarios flipped. Worth 38.17 $/t and 3.21–16.38 $/t
  respectively.
- **Grid EF is worth 2.5x more feasibility under a 2045 debut than a 2030 one**
  — power-sector decarbonisation partially hedges late hydrogen.
- **Five (scrap, debut) slices at 1.6 are infeasible under every configuration
  of the other six levers.**

## Next

1. **Decide two open framing questions** (raised, not answered):
   - Does the ramp-crest diagnosis stay as one sentence in results, or move
     entirely to methods?
   - Where do the cost results go — their own section, or Section B?
2. **`build_h2dri` has no per-year build cap** (`v_capacity.mod:150`,
   inherited). This is the one asymmetry that undercuts the strongest reading
   of the build-budget result — "we can't afford it" is refuted only for
   *conventional* plant, because H2-DRI construction rate is unconstrained by
   assumption. Putting it under a cap and re-sweeping would close it.
3. **Read two closed-access papers** before any novelty claim:
   [EnConMan 2023](https://doi.org/10.1016/j.enconman.2023.117511) and
   [JCLP 2024](https://doi.org/10.1016/j.jclepro.2024.144505). No browser
   access in this harness — either connect the Claude-in-Chrome extension
   (claude.ai/chrome) or drop the PDFs in the repo.
4. **Figures** — `scenarios/plot_section_a.py` is obsolete (reads the old
   per-study CSVs). Needs rewriting against `matrix.parquet`.
5. **Peak-annual-build readback** in `report.mod`, to settle whether
   `cap_add_total` stops binding above 30 Mt/yr. Currently unevidenced.
6. **Parameter provenance table** — no citation appears anywhere in `core/`.
   Values are extracted per module in `docs/core/`; the route-level
   techno-economic literature is where they should be sourced from.
7. **Section B** (`MonteCarlo/`, `RegretAnalysis/`) still on the old per-study
   layout. `theta_tech` and `theta_ccs` belong there.

## Standing decisions

- **Capital**: `sunk = 1` overnight capex, no salvage credit, amortisation
  branch deliberately unused (it presumes a fixed run-life — the thing the
  model decides). Unrecovered capital is 13.1% of NPV at a 2030 debut vs 8.5%
  at 2045, so the delay penalty is conservative and the phase-out cost likely
  overstated. Stated as a limitation, not corrected.
- **Cost claims use calibrated rows only** (10,202 of 30,371); feasibility uses
  all 46,656.
- **Every delta is paired**; the design is a complete factorial, so feasibility
  marginals are already balanced.
- **One AMPL instance per cell** — see the invariant note in `run_matrix.py`.

## Environment

Conda env `py313-cat`: `amplpy` 0.16.0 with the `base` and `gurobi` AMPL
modules (Gurobi 13.0.2), plus `pandas` and `pyarrow` — `to_parquet.py` and both
analysis scripts need parquet support. AMPL licence is academic, valid to
2027-04-08. Threads=1 per solve, parallelism across cells.

Throughput is machine-dependent: 35.7 cells/s at `-j 12` on a 12-core M4 Pro
(8P+4E), against 48–59 cells/s at the same `-j` on a 6-physical-core box. The
efficiency cores drag the average on Apple silicon, so `-j 8` may beat `-j 12`
there — untested.
