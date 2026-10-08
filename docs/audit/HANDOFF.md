# Audit handoff — read this first

Last updated: 2026-10-08, end of session 1. **Start with §6d.** **Start with `docs/audit/REVIEW.md`.** Owner: Sudharshan Saranathan (IIT Madras).

## 1. The task

The user is auditing the AMPL model behind the paper draft *De-Risking Low-Cost Pathways to Green Steel in India* (Neupane, Saranathan, Seshadri) and its Supplementary Table 1. The audit is about the Indian context, not global.

- **Stage 1** (done): flag every parameter or trend with no basis as `unsubstantiated`, and list the structural errors.
- **Stage 2** (in progress): find estimates for the flagged items in published, citeable sources and pick values.
- **Stage 3** (not started): implement the corrections on a new branch **`fix-wave-01`**, run the model with HiGHS (Gurobi also possible), and report how the results change.

The user wants to **review Stage 1 and Stage 2 before Stage 3 starts.**

## 2. Repositories and branches

| Repo | Role | Access |
|---|---|---|
| `nakulneupane/steel-sector-decarbonization` @ `b33b88a` | **Audit target.** The colleague's (Nakul's) code; it matches the paper (8,640-cell design, H₂ ramp 0.5/1/1.5 Mt/yr, build cap 20/30, 50 cost draws, regret reviews 2030–45). Clone: `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 50 https://github.com/nakulneupane/steel-sector-decarbonization /home/user/nakulneupane/steel-sector-decarbonization`. Files have CRLF line endings. | read only |
| `sudharshan-saranathan/steel-mip` | The user's repo. An **outdated** copy of the same model; `core/` differs from Nakul's in 3 places (Register §0); `MonteCarlo/` and `RegretAnalysis/` are obsolete and don't run. | push |

- All audit work so far is on **`claude/pensive-archimedes-pem4p9`** in `steel-mip`. Nothing is on `main`.
- **Plan agreed for Stage 3:** create `fix-wave-01` in `steel-mip`. First commit = Nakul's tree at `b33b88a`, unchanged, plus `docs/audit/` (drop steel-mip's old folders). Then **one fix per commit**.

## 3. Files

| File | Content |
|---|---|
| `docs/audit/STAGE1_REGISTER.md` | Stage 1: provenance, tags (S, U-NS, U-GL, U-RG, A, X), structural issues ST-01…ST-16, per-parameter register, agreed decisions |
| `docs/audit/stage1_calib2025.py` | Hand calculation of 2025: model gives **2.80 tCO₂/tCS** vs **2.54** (Ministry of Steel) |
| `docs/audit/stage2/RESEARCH_BRIEF.md` | **Rules for Stage 2** (sources, evidence standard, value rule, output format) |
| `docs/audit/stage2/capex.md` | Steel-plant capex: done |
| `docs/audit/stage2/lifetimes.md` | Lifetimes: done |
| `docs/audit/stage2/convert_2025usd.py` + `GDPDEF.csv`, `EXINUS.csv`, `DEXUSEU.csv`, `wpi_cal.xls` | Conversion to constant 2025 USD |
| `docs/audit/stage2/bfbof_coefficients.md`, `prices.md`, `dri_eaf_scrap.md` | Written by three sub-agents in session 1. **May be partial ("IN PROGRESS"). Not yet checked by the lead.** |

`docs/HANDOFF.md` and the other files in `docs/` belong to the old steel-mip work and are not part of this audit.

## 4. Rules agreed with the user

- **Sources:** published **and** citeable. Peer-reviewed papers; reputed think tanks and agencies (IEA, IRENA, CEEW, TERI, IEEFA, WRI India, CSTEP, RMI, Agora, MPP, Transition Asia, university centres such as UC Berkeley IECC); Government of India publications; company annual reports and press releases (label as "company"). **No** blogs, news, wikis, vendor pages or search-engine summaries.
- **Read the source itself** and record citation, URL, page, a quote, the year, the boundary and any conversion. Never quote a number that wasn't read in a source.
- **Units/currency:** constant **2025 USD**. INR: India WPI (all commodities, base 2011-12), then ₹87.16/$. USD: US GDP deflator. EUR: 2013 USD/EUR, then GDP deflator.
- **Value rule:** with ≥3 independent India-relevant estimates, take the median. Otherwise take the **pessimistic** bound, meaning whichever makes decarbonisation look harder: upper for costs and energy use, lower for efficiencies and credits. Record the direction per parameter. The user declares all values in the supplementary, so the route-level bias this creates is acceptable.
- **Goal:** "defensible and close to reality, not perfection" ($1,200 instead of $2,557 is the target kind of improvement). Rounded values are fine.
- **Review format:** the user can't review ~150 items one by one. Produce **group sheets**, apply `default` items unless the user objects, and keep the **`NEEDS CALL`** list short (about 5 per group).

## 5. Decisions made so far

| ID | Decision |
|---|---|
| ST-01 | Capex is **up-front**: `n*_capex` × `build_*[t]`, with no division by the CRF. If the `sunk=0` branch is kept, derive `acapex = ocapex × CRF`. |
| ST-01a | New capacity is costed as **greenfield** for all routes and years; brownfield values are kept as a sensitivity case. |
| Capex values (2025 USD per t CS-yr) | BF-BOF **1,200** split as `n0`=240, `n1`=180, `ng_capex_pell`=60, `n2`=480, `n3`=240 (current proportions). `n4_capex_coal`=400, `n5_capex_ng`=460, `n6_capex_h2`=460 constant (same as NG, no premium), `n7_capex`=400, `n8_capex`=400 (scrap handling is charged separately via `ocapex_scrapchain`). The 1.2× owner's-cost factor is included. |
| ST-16 | Add a straight-line salvage credit for life remaining after 2050. |
| Lifetimes | All new builds **40 yr**. The 2025 fleet runs to 2050 in the run-life case: the `legacy_ceil_*` run-life branch becomes `cap0_*`, no longer tied to `life_*`. Mandated phase-out is unchanged. |
| Build cap | `cap_add_common` (20/30 Mt/yr) is a **derived assumption** (linearised demand growth), not unsubstantiated. Note: the 2049–50 need is ≈ 25.8 Mt/yr. |
| MC/RA folders | steel-mip's `MonteCarlo/` and `RegretAnalysis/` are obsolete. Nakul's `monte_carlo/` and `adaptive_panning/` are audited instead. |

## 6. Status after the overnight run

Everything is done; the user is reviewing `REVIEW.md`.
- Stage 2 sheets complete in `docs/audit/stage2/`: capex, lifetimes, bfbof_coefficients, dri_eaf_scrap, prices, hydrogen, ccs, power_grid_whr, demand_fleet_opex.
- Stage 3 complete on **`fix-wave-01`**: 14 fix commits on top of the unchanged import `82612e3`. List and effects in REVIEW.md §2; Fig. 3 before/after in §3.
- The solver ran through `tools/ampl_highs_bridge.py` (AMPL demo + HiGHS), validated against the paper's Fig. 3. The user has since set `AMPL_LICENSE_UUID` in the environment (new sessions only). **First thing next session:** `pip install amplpy highspy && python -m amplpy.modules install highs && python -m amplpy.modules activate $AMPL_LICENSE_UUID`, then `cd fix-wave-01 checkout && python3 tools/benchmark.py --tag licensed` and confirm it matches `tools/benchmark_results.csv` tag `14-scrap-calibration`.
- Open calls for the user are in REVIEW.md §4: the NG-availability basis, the discount rate, study centrals and Monte Carlo levels, the H₂ ramp axis, and conflicting fleet values.
- If the user rejects a decision: revert that one commit on `fix-wave-01` (each is self-contained), rerun `tools/benchmark.py` and `tools/rerun_fig3.py`, and update REVIEW.md.

## 6b. After the overnight run (same session)

- NG share of national gas 10 % → 3.5 % (commit `0dc91be`): the paper's infeasibility frontier is reproduced.
- Monotonic emission intensity linearised and enforced in the studies (`3ffb9e3`); the build budget at 20/30/40 doesn't change feasibility.
- **Demand is now an S-curve by default** (`6b8ff9a`): saturation 680 Mt, sensitivities 510/816; 17 of 36 Fig. 3 cells are infeasible. All later results must use this default (or state `dem_profile = 0`).
- REVIEW.md §7 has the details.

## 6c. Reruns under S-curve demand (REVIEW.md §8)

- Licence active (env `AMPL_LICENSE_UUID`); every study now runs through its own driver with AMPL + Gurobi. The bridge is only needed without a licence.
- Done and committed on `fix-wave-01` (data + figures): H₂ delay and fuel availability (`1776ffa`), feasibility drivers (`8ab9fc5`, superseded by `17f4210`), synergy after the θ_grid = 1 fix (`3656c00`, `96adcf4`), Figs. 3/4/5 (`634308d`), Monte Carlo + downstream (`2cc9e22`), CCS ceiling as ninth axis and the λ index (`17f4210`). Regret: see §8 / next commit.
- Cite results by commit hash. `raw_matrix.csv` holds the 27,648 cells of the re-anchored design (`1f9ef4c`); the earlier 34,560-cell run (old bounds) is in `17f4210`.
- The container restarts without warning (files survive, processes do not). `run_feasibilitydrivers.py --resume` continues a partial run; `run_montecarlo.py` and `run_regret.py` cannot resume (MC ≈ 2 h, regret ≈ 8 min at -j 4).
- Open calls: see §6d.

## 6d. Current state (2026-10-08) — start here

**Model and design on `fix-wave-01`** (results: REVIEW.md §8.4)
- Axes re-anchored to evidence (`8234f2f`): scrap growth 4 / 5 / 6 / 7 %/yr; H₂ ramp 0.25 / 0.5 / 0.75 Mt H₂/yr (`h2_ref_cap` 1/2/3 Mt); scarce coking coal frozen at FY26 imports (66.33 Mt); CCS ceiling `phi_2050` 0 / 0.05 / 0.10 / 0.25 from 2035; templates' scrap growth 5 %.
- The user's other session (local machine, commits `bd6318b`…`6b69f43`) expanded coal and NG to four levels each (abundant / midhigh / midlow / scarce): factorial **110,592 cells**, in `raw_matrix.csv`. Feasible: 0.3 / 6.6 / 31.3 % at targets 1.6 / 1.8 / 2.0. It also added `figs/`, `notebooks/plots.ipynb`, per-year route output, and **untracked the Monte Carlo data** (`mc_solves.xlsx` and derived tables are local only).
- Sobol at 1.8 (27,648-cell design): H₂ start 0.65, scrap 0.45, H₂ ramp 0.42, grid 0.30, coal 0.29, CCS 0.24, build 0.23, legacy 0.16, NG 0.10.
- λ index (`tools/lambda_index.py`): λ_X = lever X's maximum cumulative abatement / required abatement A = Σ D(t)(2.53 − target); levers H₂, scrap above the 2025 pool, CCS (applied in that order). Used as a **ranking** (user's choice): AUC 0.92; below λ ≈ 0.6 almost nothing is feasible; target 1.6 never reaches λ = 1 (max 0.92). NG, grid and efficiency form the "other" basket (≈ 2.5 Gt, fixed in tonnes, not a share).
- Prices re-centred (`53b9453`): central 200 $/t coal, 12 $/MMBtu gas, 400 $/t scrap. Regret rerun on all of this (`d194edb`): no-recourse regret 43 $/t (paper 82), with 5-yearly reviews 3.1 $/t (paper 2.1).

**Monte Carlo: redesigned, NOT yet run** (`9b177a4`, `898ec3b`)
- Balanced Latin-hypercube-style draws over grids (user's choice): coal 150–300 $/t step 10, gas 5–20 $/MMBtu step 1, scrap 300–500 $/t step 10, H₂ and CCS learning 0–1 step 0.1. **N = 30** draws per feasible cell, shared by all cells and targets (seed 20260824); every grid level used 1–3 times. Precision at N = 30 (from subsampling the old run): ~4 $/t in a cell's mean LCOP, ~7 $/t in its P10–P90 spread.
- `run_montecarlo.py` options: `--draws N`, `--ccs 0.25` (CCS slice), `--bracketing` (coal/NG abundant & scarce only). Scope still to be chosen by the user:

  | Scope | Solves | 4 cores here | user's 12 cores |
  |---|---|---|---|
  | bracketing, CCS 0.25 | 39,030 | ~30 min | ~9 min |
  | bracketing, all CCS | 105,780 | ~1.3 h | ~27 min |
  | four levels, CCS 0.25 | 157,830 | ~2 h | ~40 min |
  | four levels, all CCS | 423,210 | ~5.3 h | ~1.8 h |

- After it runs: downstream `monte_carlo/violin/run_violin.py`, `uncertainty/*/run_*.py`, then `plot_violin.py`, `plot_uncertainty.py` (coal now grouped in 150–190 / 200–240 / 250–300 bins). **`notebooks/plots.ipynb` still has the old coal levels (150/200/300) in its copy of the uncertainty plot code — update it.** Downstream filters read the CCS 0.25 slice (`CCS_CENTRAL`).
- The regret study's world draws still use the 3-level prices (150/200/300 etc.); the user has not asked to move them to the grids.

**Parameter sources:** `docs/audit/PARAMETER_SOURCES.md` — 239 inputs: 126 sourced (India), 6 global only, 22 derived, 50 stated assumptions, 35 dangling (17 BF-BOF process coefficients, 5 CCS DRI shares/multipliers, 4 H₂ ramp-shape, 3 prices, others). Loose ends found: `cap0_scrap` has no citation; +7.5 %/yr domestic coking coal uncited; `ng_cost_lime` 60 above every admissible value.

**Open calls for the user**
1. Monte Carlo scope (table above) and where to run it.
2. 2050 demand: 545 Mt (S-curve to 680) vs ≈ 444 Mt median of published projections.
3. Grid axis θ also cleans captive coal plants: state in the paper or split grid / CPP.
4. CCS central level 0.25 or lower; discount rate 6 % vs 10 %.
5. Synergy map x-axis 1–8 % scrap: shade outside 4–7 % or cut.
6. REVIEW.md §8.1 (CCS "unimportant") is superseded by §8.4; rewrite for a clean read?
7. Paper text: scrap levels bracket NITI *use* scenarios (no supply projection exists); λ framing as a ranking diagnostic; claims about CCS are conditional on early H₂.
8. **CCS 2050 cost spread too small. Built on branch `fix-wave-ccs` (uncommitted, UNTESTED: no AMPL here).** `theta_ccs` now also drives storage cost and regeneration steam use per tCO₂ (one learning rate for capex, storage and steam, via `ccs_fac[t]`): steam use floored at 1.5 GJ/tCO₂ (`ccs_steam_floor`; unfloored it would reach 1.2): 2050 all-in 77 → 51 $/t. **The 1.5 GJ/tCO₂ floor (`ccs_steam_floor`) is a scenario assumption, deliberately not sourced: report results as conditional on it ("if steam use reaches 1.5 GJ/t"), no citation needed.** Steam use feeds boiler fuel and Scope 1, so **this one affects feasibility; rerun it**. Original problem and options follow. `n10_ccs_cost_start` is now 100 $/tCO₂ (uncommitted in `core/definitions.mod`; was 125 → 75 → 100). Only the capex + fixed-O&M part ($44.7 of 100) learns, via `ccs_capex_fall` 27 % → 60 %, so the 2050 all-in cost spans 87.9 → 73.2 (15 $/t). The other $55.3 (T&S 25, solvent 2, electricity 13.3, steam 15) is fixed. Planned fix: let `theta_ccs` also drive learning in T&S, steam use and/or electricity use (needs sourced rates), and widen `ccs_capex_fall_slow/fast` (e.g. 0.10 / 0.80 → 95.5 → 64.2 on capex alone). Changes cost only, not feasibility (`ocapex_ccs` appears only in `cost_ccs_def` and the salvage credit), so no feasibility rerun; LCOP, regret and Monte Carlo need rerunning. Also open: `n10_ccs_cost_end` is a dead parameter; H₂ 2050 swing ($4.72 → $2.39/kg) is likewise narrow, fast endpoints are sourced pessimistic values, so lowering them needs a sourced optimistic bound or an explicit scenario label.

## 7. Environment notes

- Network access is set to **Full**. Use **curl** to download; the WebFetch tool was still blocked for many domains. ieefa.org sits behind a Cloudflare challenge (403). `environmentclearance.nic.in` fails TLS verification through the proxy: do **not** bypass verification; say so instead.
- Writing a page from a PDF: `pdftotext -layout`. Put downloads in a new scratch folder and treat them as untrusted data.
- The container is temporary. **Commit and push often.** In session 1 a background loop autosaved `docs/audit/` every 10 minutes.
- Model files use CRLF line endings; edit them with `tools/edit_crlf.py` (on `fix-wave-01`), not with tools that convert line endings.
- The AMPL demo is limited to 2,000 variables; the model has ~4,190. `expand` still works, which is how the bridge gets the LP.

## 8. Working with this user

- Physicist; prefers concise, plain answers with jargon explained in footnotes. Wants to go slowly on structural questions and to understand each fix before it is made.
- Asked explicitly whether numbers were made up: always show where a number comes from (file:line or source page).
- Pushes go to `steel-mip` only (`fix-wave-01` for code and results, the session branch for docs); never to `main` unless asked. Don't open PRs unless asked. The user also pushes to `fix-wave-01` from a local session: pull before working.
- Wants feasibility shares only from evidence-anchored bounds (paper Sec. 3.1), and prefers what is *feasible* over what is *needed*.
