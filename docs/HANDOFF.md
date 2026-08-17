# Handoff

## Start here

Section A was rebuilt tonight (2026-08-17/18) from six separate per-study
sweeps into **one design matrix over policy-controlled levers**, and four
model defects were found and fixed along the way. Nothing has been swept under
the new model yet — that is the next action, and it takes ~6 minutes.

**Organising principle (the thing that made the design tractable):**
Section A sweeps ONLY what policy controls. Learning rates (`theta_tech`,
`theta_ccs`) depend on global science, not Indian policy, so they are fixed
here and belong to Section B's Monte Carlo. Applying that criterion cut the
design from 524,880 cells (3.5 h) to 46,656 (~17 min) with no loss of anything
the paper can claim.

## The Section A design

`scenarios/_matrix/axes.py` is the single source of truth.

| Lever | Levels | Policy instrument |
|---|---|---|
| `ccoal` | 2 — abundant / scarce | import policy, domestic coking coal |
| `ng` | 2 — policy / bau | gas allocation to steel |
| `h2_start` | 4 — 2030/35/40/45 | green-H2 mission timing |
| `scrap_rate` | 6 — 0.00…0.10 | collection infra, ELV rules |
| `grid_ef` | 9 — 50…850 gCO2/kWh | power-sector decarbonisation |
| `ramp` (`h2_ref_cap`) | 3 — 4/6/8 Mt/yr | electrolyser deployment rate |
| `build_cap` (`cap_add_common`) | 3 — 20/30/40 Mt/yr | finance + EPC capacity (shared across the 4 conventional routes) |
| `legacy` | 2 — run-life / mandated-phaseout | retirement policy |
| **`avg_emi`** *(target)* | 3 — 1.6 / 1.8 / 2.0 | the constraint being tested |

**46,656 cells (~17 min).** Constants: `theta_tech` 0.5, `theta_ccs` 0.5,
`whr_ccs_integration` 1.

Demotions are measured, not assumed: swept across their full ranges,
`theta_ccs` moves LCOP by **3.5 $/t with zero effect on feasibility** and
`whr_mode` by **1.3 $/t**, against a 28.6 $/t H2-delay penalty.

## Model changes made tonight (all in `core/`, all documented in `docs/core/`)

1. **`legacy_phaseout` (new lever).** Retirement of the 2025 fleet was
   hard-coded as `cap0 * (2050-t)/25` for all five routes — no stated basis,
   ignoring the per-route `life_*` the model already defines, forcing the
   entire 207.75 Mt fleet to zero by 2050. Now a policy parameter: 0 = assets
   run their technical life, 1 = the old mandated phase-out. Vintage data does
   not exist, so the two settings **bracket** the truth; report as bounds.
2. **`cap_add_common` is now a SHARED budget** (`cap_add_total`), 20 Mt/yr
   across BOF, coal-DRI, NG-DRI and scrap-EAF combined. It was four
   independent per-route caps against the same parameter, permitting 4x that
   in aggregate and giving each route a private allowance.
3. **`cap_envelope` (new).** Total installed capacity <= `(1+cap_buffer)`x
   demand, `cap_buffer` = 0.40.
4. **`cap_add_common` raised 10 -> 20 Mt/yr and promoted to a LEVER**
   (`build_cap`, 20/30/40 Mt/yr) — annual build capacity is finance and
   industrial policy, so it passes the Section A criterion.

### Measured effects

- **Mandated phase-out costs +36.6 $/t** (LCOP 559.66 vs 523.11) for
  *identical* emissions, since the cumulative cap binds either way. The
  mechanism is avoided capex — forced retirement makes the model rebuild
  207.75 Mt it already owns — not stranded-asset friction, which is real but
  ~10x smaller. **This is a policy result in its own right**, and it is why
  retirement became the seventh lever.
- **The shared build budget binds** at every value tested (peak build sits
  exactly at the cap). Tightening 40 -> 20 Mt/yr costs 3.8 $/t.
- **`cap_envelope` is inert.** `cap_buffer` must be >= 0.365 (the 2025 fleet
  already exceeds 2025 demand by 36%; 0.35 is infeasible, 0.40 solves), and
  above that floor `fopex` on idle capacity already drives cap/demand to
  exactly `1/util_max` = 1.053 from 2030 on. Kept as a guard, not a shaping
  constraint. To bite it would have to *decline* over time.

## Three bundled axes the matrix disentangled

Each of the six original studies had a headline lever that was secretly two
things, so effects were attributed to whichever lever the study was named for:

| Study | "Axis" | Actually |
|---|---|---|
| hydrogen-delay | ramp | `cap_add_common` **and** `h2_ref_cap` (collinear, ratio 2.5) — so "H2 ramp" also set conventional build rates |
| grid | grid EF | emission factor **and** electricity tariff, both via `theta_grid` |
| whr | theta | `theta_ccs` **and** `theta_grid` — the 26.8 $/t effect was almost entirely grid, not CCS |

`cap_add_common` is now its own lever (`build_cap`), so `ramp` scales only
the electrolyser ramp and is genuinely H2-specific.

## Findings from the 524,880-cell snapshot

Banked at `scenarios/_matrix/results/matrix.parquet` (52 MB, gitignored),
stamped with the git SHA of `core/` and 23 metadata keys. **It predates all
four model changes above** — its structure is valid, its headline numbers are
not. Verified complete: 524,880 rows, 524,880 unique coordinate tuples.

**The candidate headline finding — the cost of delaying hydrogen is a
property of the scrap supply, not of hydrogen.** At `avg_emi` 1.8, abundant
coal, policy gas, delaying H2-DRI from 2030 to 2045 costs:

| Scrap growth | 2050 scrap | Delay penalty |
|---|---|---|
| <= 0.04 | 99 Mt | **infeasible at any delay** |
| 0.06 | 159 Mt | **+28.6 $/t** |
| 0.08 | 253 Mt | +8.5 $/t |
| 0.10 | 401 Mt | +0.4 $/t |

Mechanism: H2-DRI's 2050 share falls 23.6% -> 6-7% as scrap grows. Delay gets
cheap because hydrogen is **displaced**, not because timing stops mattering —
state that explicitly or the claim is near-tautological.

**Related:** halving H2 cost (`theta_tech` 0 -> 1, ~$3.7 -> ~$1.8/kg) buys only
**2.9 percentage points** of H2-DRI share (13.6 $/t on LCOP). Hydrogen uptake
looks **deployment-limited, not cost-limited** — worth confirming that
`h2elec_growth` is the binding constraint before claiming it.

**Retracted:** an earlier "scrap saturates at 41.5% of output" finding was an
artifact of the per-route build cap (`util_max * life_scrap * cap_add_common /
demand[2050]`). The shared budget removes it; `share_scrap` is now ~0.264-0.267
as an economic outcome. Do not repeat the 41.5% number.

## Reading the matrix (traps we hit, all now in the Parquet metadata)

- `ERROR: ...presolve: constraint steel_balance...` rows are **genuine
  infeasibilities** proven by AMPL presolve, concentrated in the
  scarce-coal/bau-gas/late-H2 corner. Count them as infeasible; do not filter.
- `extrapolated == 1` means `theta_grid` left [0,1], so the **coupled tariff**
  is extrapolated past its $0.055-0.085/kWh anchors. Filter for cost claims;
  feasibility is fine across the whole band.
- `import_bill` **inverts** — scarce regimes post lower bills while costing
  more per tonne, because a binding cap forbids importing. Read it with
  `ccoal_bind_yrs` / `ng_bind_yrs`.
- Infeasible rows retain junk numerics. Filter `solve_result == 'solved'`.
- `grid_ef_2050` is the tripwire for the one-instance-per-run invariant.

## Next

1. **Run the 46,656-cell sweep** — `python3 scenarios/_matrix/run_matrix.py -j 12`,
   ~17 min. Then `to_parquet.py`. Baseline `--verify` already solves under the
   new model (objective 1,857,353,828,038.84 at build_cap=tight).
2. **Recompute every headline number** on the new table. The snapshot's
   figures are pre-fix.
3. **Verify `h2elec_growth` binds** before claiming deployment-limited uptake.
4. **Parameter provenance table** — coefficients are literature-sourced but no
   citation appears anywhere in `core/` or `docs/`. Needed as supplementary
   material. Values are already extracted per module in `docs/core/`.
5. **Section B** (`MonteCarlo/`, `RegretAnalysis/`) still on the old per-study
   layout, untouched. The thetas belong there.

## Known open questions

- **`theta_grid` couples grid EF to the electricity tariff** as a fixed linear
  identity. Both are policy-controlled in India (regulated tariffs), so it
  stays in Section A — but the *coupling rate* is an untested assumption, and
  it is what pushes the tariff outside calibration at the ends of the EF band.
- **`build_h2dri` has no per-year build cap at all**, unlike the four
  conventional routes. Inherited asymmetry; state it in methods.
- **BF-BOF decarbonises for free.** `d_blast_furnace.mod` interpolates coke
  0.53 -> 0.48 t/thm and bio-PCI 0 -> 0.053 t/thm on a calendar schedule, with
  no capex and no decision. Literature-sourced values, but the model hands the
  incumbent route abatement that H2-DRI must build and pay for. Methods note.
- **`bf_h2_in` is dead code** — interpolates 0 -> 0.
- **`carbon_tax` exists only in `yreport.mod`**, which is not in the include
  chain. The model has no price instrument, only the cap. A carbon price would
  be a genuine alternative-instrument lever, but it is a model change.
- **`emission_monotonic` is dropped in every run** (the model's only
  nonlinearity), so nothing forces emission intensity to decline over time.

## Environment

- `amplpy` 0.18.0; **Gurobi 13.0.2** and HiGHS installed as AMPL modules.
- **Threads=1 per solve, parallelism across cells.** Measured: Gurobi gains
  ~9% from a 10x thread budget on this LP (dual simplex, ~1,400 iterations,
  presolved to 1,058 x 950 — it does not parallelise). 12 workers on 6 physical
  cores gave 47-52 cells/s; 6 workers gave ~40.
- **One AMPL instance per cell — do not "optimise" this away.**
  `n9_grid_ef_end` is `param ... default <expr in theta_grid>`, and AMPL
  freezes a `default` expression on first read. A reused instance would pin
  grid EF at the first cell's value while still recording the requested target.
- Results are gitignored (`results/`). The Parquet metadata is the only
  provenance that travels with the data.
