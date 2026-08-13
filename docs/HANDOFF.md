# Handoff

## Start here

**Done:** `core/` is complete and verified; Gurobi installed; the repo is under
git and pushed; 1 of 8 studies migrated to `scenarios/`.
**Next:** migrate `hydrogen-delay`, copying the shape of
`scenarios/import-dependence/` (see "Step 5" below), then the remaining 6.
Source material for three of them is already worked out under "Per-study sweep
definitions" — start there rather than re-reading the templates.

**Agreed plan:** finish porting all 7 remaining studies first, *then* run every
sweep together. Do not stop to reproduce individual sweeps along the way.

Nothing has been deleted. Every original study directory (`HydrogenDelay/`,
`ImportDependency/`, `MonteCarlo/`, `RegretAnalysis/`,
`StructuralSensitivity/{Abatement,Grid,Scrap,WHR}/`) is still in place and
untouched. The deletion sweep needs the user's explicit go-ahead, and no study
should be removed until its `scenarios/` replacement is validated against it.

### Recipe for the next study

1. Read the study's `*_template.mod` and `*.bat` — the `.bat` defines the sweep
   axes and the CSV column order; the template defines the backdrop.
2. Patch `include modules/` → `include ../core/modules/` before running the old
   template as a baseline (see the broken-template note below).
3. Capture the old objective for one representative scenario (Gurobi is now
   installed, so the old template runs as originally configured).
4. Write `study.mod` (backdrop, pure `let`), `axes/*.mod` (one per axis level),
   `report.mod` (post-solve + CSV printf), `run.py` (cross-product driver).
5. Delete the study's `let h2_peak_year` / `let n8_scrap_limit` lines — AMPL
   rejects `let` on the now-derived params (see below).
6. Re-run through the new driver and compare objectives; agreement to ~1e-15
   relative is solver noise and counts as equivalent.

### Environment

- `amplpy` 0.18.0; AMPL binary at
  `~/miniconda3/lib/python3.13/site-packages/ampl_module_base/bin/ampl`.
- AMPL licence is activated locally (`python3 -m amplpy.modules activate <uuid>`).
  The UUID is deliberately not recorded here — this repository is public.
- **Solvers: HiGHS and Gurobi 13.0.2**, both installed as AMPL modules
  (`python3 -m amplpy.modules install gurobi`). The drivers' default
  `--solver gurobi` + `mipgap=0.002` now works out of the box and matches the
  published-run configuration. `--solver highs` remains available for
  cross-checking. Gurobi reproduces the baseline objective bit-identically
  (`2008395874830.759766`).
- Gurobi emits a `Tolerance violations` warning (MaxAbs 4E+01 on algebraic
  constraints) on the baseline solve. Absolute-scale only, against flows of
  1e6–1e8, so it is rounding noise rather than a modelling fault — but if
  results ever look off, re-check with `--solver highs` before trusting them.

## State — `core/` is complete and verified

`core/` now holds the entire model structure:

| File | Source | Notes |
|---|---|---|
| `core/definitions.mod` | MonteCarlo's copy (richest comments) | + derived-param conversion, see below |
| `core/variables.mod` | HydrogenDelay's copy | keeps the `<= dem[t]` bound |
| `core/parameters.mod` | HydrogenDelay's copy | hand-rolled recursions removed |
| `core/yreport.mod` | HydrogenDelay's copy | mojibake `â€“` → ASCII `-` |
| `core/model.mod` | new | structure only: no solver, no `solve`, no report |
| `core/modules/*.mod` | 21 shared modules | + `whr_ccs_integration` folded in |

**Invocation contract:** AMPL resolves `include` against its *cwd*, not the
including file. All paths in `core/model.mod` are repo-root-relative, so
scenarios must be run from the repository root (`ampl.cd(ROOT)` in amplpy).

### Derived-param conversion ("option b")

`n8_scrap_limit` and `h2_peak_year` were mutable params populated by `let`,
so a scenario that overrode `n8_scrap_rate` or `ng_h2_start_year` silently
did nothing unless it also re-ran the recursion by hand — which every
template does. They are now *defined* params in `core/definitions.mod`:

```ampl
param n8_scrap_seed default 37000000;
param n8_scrap_limit{t in T} :=
    if ord(t) = 1 then n8_scrap_seed
    else n8_scrap_limit[prev(t)] * (1 + n8_scrap_rate);

param h2_peak_lag  default 5;
param h2_peak_year := ng_h2_start_year + h2_peak_lag;
```

## Verified (amplpy 0.18 + HiGHS)

1. **Defined params re-evaluate after instantiation**, including after a prior
   `solve` — overriding `n8_scrap_rate` or the seed propagates into already-built
   constraints. This is what makes scenario overrides composable.
2. **`<= dem[t]` is provably redundant**, so promoting it is safe:
   `coaldri_output ≤ coaldri+ngdri+h2dri = dri_eaf_steel_out = steel_eaf
   ≤ total_steel = dem` (k_dri_h2:4, l_eaf_dri:36, n_steel_balance:4,
   t_additional_constraints:10), all intermediates `>= 0`. RegretAnalysis drops
   `meet_demand` but replaces it with `total_steel + steel_import = dem`,
   `steel_import >= 0`, so `total_steel ≤ dem` still holds.
3. **`No_H2_Before`'s index set re-instantiates** after a later
   `let ng_h2_start_year`, even post-solve. The existing H2-year sweeps are
   correct — do NOT "fix" the ordering.
4. **Baseline objective is bit-identical across all 8 studies** and
   `core/model.mod`: `2008395874830.759766`.
5. **`whr_ccs_integration`** is inert at its default of 1 (objective unchanged)
   and active at 0 (+$4.65B, +0.23%). WHR's boiler-only sweep is now a
   one-line override instead of a forked module.

## Known issue found (pre-existing) — FIXED

`MonteCarlo/modules/v_capacity.mod:71` contained a stray `.` on its own line —
a genuine syntax error, so `MonteCarlo/main.mod` could not have run in its
committed state. The line has been deleted. Verified: `MonteCarlo/main.mod` now
parses and solves end-to-end to the baseline objective
`2008395874830.759766`.

That file otherwise differs from `core/modules/v_capacity.mod` only in
comments, so it still belongs on the dead-file list once MonteCarlo migrates.

## Step 5 — `scenarios/` migration: 1 of 8 done

Agreed layout: composable axis files + a Python driver (the `.bat` files are
Windows-only and call `*_pivot.py` / `*_plot.py` scripts that are not in the repo).

`scenarios/import-dependence/` is the **reference implementation** — copy its shape:

```
scenarios/import-dependence/
  study.mod        # common backdrop: pure `let` overrides, no structure
                   # also declares `param REGIME symbolic` for the CSV label
  axes/*.mod       # one file per axis level (ccoal_abundant, ng_policy, ...)
  report.mod       # post-solve accounting + the CSV row printf
  run.py           # sweeps the cross-product; sets REGIME before including report.mod
  results/         # <tag>.txt per run + impdep_summary.csv
```

Gotchas that shaped it:

- `report.mod`'s `printf` fires at include time, so `REGIME` must be **set
  before** the include — hence its declaration lives in `study.mod`.
- `run.py` writes the CSV header, `report.mod` appends rows. The column order
  in the two files is one contract; change both together.
- `drop emission_monotonic;` must come after `core/model.mod` (it is declared
  in `t_additional_constraints.mod`).
- Driver defaults to `gurobi` + `mipgap=0.002`; `--solver highs` is for
  verification only and will not reproduce published MIP numbers.

Validated: `HiCoal-HiNG_h2-2030` via the new driver gives
`1972188578542.099609` under HiGHS vs the old `impdep_template.mod`
mechanism's `1972188578542.098877` — 3.7e-16 relative, i.e. solver noise.
Under Gurobi the new driver reproduces `1972188578542.098877` exactly.

Also found: `ImportDependency/impdep_template.mod` still says
`include modules/...`, but that directory was removed by last session's dedup —
so the old template has been broken since then and must be patched to
`../core/modules/` to run at all. Same class of breakage may affect the other
templates; check before trusting any "old" baseline.

### Per-study sweep definitions (already extracted — do not re-derive)

Read from the templates/`.bat`s in the session that ended here. **Not yet
written into `scenarios/`.** The remaining four studies (MonteCarlo,
RegretAnalysis, Abatement, WHR) still need their sources read.

**Ramp levels** are shared vocabulary across studies. `h2_ref_cap` is the
envelope scale and the electrolyser peak is `0.25 x h2_ref_cap`:

| Level | `cap_add_common` | `h2_ref_cap` | peak H2 |
|---|---|---|---|
| Low | 10000000 | 4000000 | 1.0 Mt/yr |
| Medium | 15000000 | 6000000 | 1.5 Mt/yr |
| High | 20000000 | 8000000 | 2.0 Mt/yr |

**`hydrogen-delay`** — 36 runs = 4 x 3 x 3. No `.bat`; driven by tokens in
`h2delay_template.mod` (`RAMPVAL`, `H2REFVAL`, `EFVAL`, `H2YRVAL`,
`RAMPLABEL`). Axes: `ng_h2_start_year` in {2030, 2035, 2040, 2045};
`avg_emi` in {1.6, 1.8, 2.0}; ramp in {Low, Medium, High}. The template sets
*no* `theta_*` and no `n5_cost_NG`, so the backdrop is core defaults — its
`study.mod` is nearly empty. CSV columns:
`avg_emi, ramp_label, cap_add_common, h2_ref_cap, ng_h2_start_year,
solve_result, cap_h2dri_2050, total_ccs_2050, lcop, red_h2_2050`.
Note the old output path `Plots/H2_Delay/results/h2delay_summary.csv` does not
exist in this repo; write to `scenarios/hydrogen-delay/results/` instead.

**`structural-sensitivity/grid`** — 864 runs = 6 x 8 x 18. Axes:
`ng_h2_start_year` in {2030, 2033, 2036, 2039, 2042, 2045}; `n8_scrap_rate` in
0.01..0.08 step 0.01; `n9_grid_ef_end` in 0.0000..0.00085 step 0.00005.
The grid axis is applied *indirectly* — the template sets
`theta_grid := (GRIDVAL - grid_ef_end_slow)/(grid_ef_end_fast - grid_ef_end_slow)`,
i.e. it back-solves the interpolation weight from a target end-EF. Keep that
form. CSV columns: `h2_start, scrap_rate, grid_ef_end, theta_grid, tariff_2050,
solve_result, avg_emis, pv_avg_cost, h2_share_2050, ccs_frac_2050,
scrapeaf_share_2050`. It also includes a `Plots/Grid/gridresult.mod` that is
**not in this repo** — those columns must be reconstructed in `report.mod`.
864 Gurobi runs at `TimeLimit=300` is the largest sweep here; budget for it.

**`structural-sensitivity/scrap`** — 33 runs = 3 x 11. Axes: `avg_emi` in
{1.6, 1.8, 2.0}; `n8_scrap_rate` in 0.00..0.10 step 0.01. Backdrop:
`theta_tech/grid/ccs := 0.5`, `ng_h2_start_year := 2030`,
`n9_grid_ef_end := 0.0005`, Medium ramp, `n5_cost_NG := 10`. CSV columns:
`avg_emi, scrap_rate, solve_result, h2dri_cap_2050, ccs_2050, red_h2_2050,
lcop, scrap_use_2050, scrap_limit_2050, scrapeaf_share_2050`.

The `red_h2_2050` / `e_h2_2050` accounting block is **identical** in
import-dependence, hydrogen-delay and scrap. Consider hoisting it to a shared
`scenarios/_common/red_h2.mod` rather than copying it a fourth time.

### Remaining 7 studies

`hydrogen-delay`, `monte-carlo`, `regret-analysis`, and the four under
`structural-sensitivity` (Abatement, Grid, Scrap, WHR). WHR's boiler-only sweep
is now `let whr_ccs_integration := 0;` instead of a forked module.

### Old `let` sites that MUST be deleted during migration

**AMPL rejects `let` on a defined param** ("`bb` has an `=` assignment in the
model"). So the derived-param conversion requires deleting, in the same pass as
each study's migration:

- ~21 `let h2_peak_year := ...` sites
- 8 `let n8_scrap_limit[first(T)] := ...` + recursion pairs
  (replace with `let n8_scrap_seed := ...`)
- the hand-rolled recursions in `ImportDependency/impdep_template.mod:16-17`
  and `StructuralSensitivity/Grid/grid_template.mod:11-12`

Carry forward deliberately when writing scenario files:

- each study's `option solver gurobi;` + `gurobi_options 'mipgap=0.002'` — a MIP
  at 0.2% gap will not match a HiGHS default-gap solve, so keep HiGHS out of the
  committed scenario files (it was only used for verification here)
- the `printf ... >> "results/....csv"` blocks — that CSV is the contract the
  plotting scripts expect

`ImportDependency/scenarios/{ccoal_abundant,ccoal_scarce,ng_bau,ng_policy}.mod`
are live (driven by `impdep.bat`) and are the working prototype for what a
scenario override file should look like: pure `let` data, no structure.
`ng_avail_{abundant,scarce}.mod` in that directory are unreferenced.

## Caveat on equivalence claims

`impdep.bat` hardcodes a Windows `WORKDIR` and calls `impdep_pivot.py` /
`impdep_plot.py`, neither of which is in the repo. So per-study *objective*
equivalence is verified, but the *sweeps* have not been reproduced end-to-end
against previously published numbers.

## Dead files noted, NOT yet deleted

Awaiting the user's confirmation on a cleanup sweep:

- `ng.mod` (×7 — one per study dir, unreferenced by any template or main.mod)
- `ImportDependency/template.mod`, `StructuralSensitivity/Abatement/template.mod`
- `ImportDependency/scenarios/ng_avail_{abundant,scarce}.mod` (unreferenced;
  the four files `impdep.bat` actually drives have been copied to
  `scenarios/import-dependence/axes/`)
- `MonteCarlo/modules/v_capacity.mod` and the three local
  `modules/o_waste_heat.mod` copies (MonteCarlo, RegretAnalysis, WHR) — all now
  superseded by `core/modules/`

Do NOT fold `RegretAnalysis/commit_mc_case.mod`, `commit_mc_front.mod`, or
`commit_plan.mod` into core. They carry genuinely different structure (elastic
demand via `steel_import`, commitment constraints, regret accounting) and stay
as a RegretAnalysis-local overlay.

## Version control

This tree is now a git repository, pushed to
`github.com/sudharshan-saranathan/steel-mip` (**public** — keep licence keys
and any unpublished data out of it).

The reorg was grafted onto the four pre-existing commits rather than replacing
them, so the history reads:

```
503df38  Add correctness audit report (AUDIT.md)      <- the old flat layout
93529e3  Restructure into per-study directories       <- snapshot: post module-dedup
8c7f032  Add core/ model + scenarios/ mechanism       <- this session's reorg
```

Commit `93529e3` is the pre-reorg undo point, so the old `docs/_backup/`
directory has been deleted — `git show 93529e3:<path>` recovers any file from
it. Beware that the old repo's `modules/o_power_balance.mod` and
`p_waste_heat.mod` correspond to today's `p_power_balance.mod` and
`o_waste_heat.mod`; the names were swapped during the per-study restructure.

Generated outputs (`results/`, `*.nl`, `*.sol`, `temp_*.mod`) and local agent
state (`.remember/`, `.claude/settings.local.json`) are gitignored.
