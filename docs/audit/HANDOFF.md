# Audit handoff — read this first

Last updated: 2026-10-07, after the S-curve reruns (session 1). **Start with `docs/audit/REVIEW.md`.** Owner: Sudharshan Saranathan (IIT Madras).

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
- Cite results by commit hash. `raw_matrix.csv` holds all 34,560 cells.
- The container restarts without warning (files survive, processes do not). `run_feasibilitydrivers.py --resume` continues a partial run; `run_montecarlo.py` and `run_regret.py` cannot resume (MC ≈ 2 h, regret ≈ 8 min at -j 4).
- Open calls: REVIEW.md §4 and §8.3 (template scrap 6 % vs 5 %, 2050 demand vs published median, CCS central level, MC at low CCS).

## 7. Environment notes

- Network access is set to **Full**. Use **curl** to download; the WebFetch tool was still blocked for many domains. ieefa.org sits behind a Cloudflare challenge (403). `environmentclearance.nic.in` fails TLS verification through the proxy: do **not** bypass verification; say so instead.
- Writing a page from a PDF: `pdftotext -layout`. Put downloads in a new scratch folder and treat them as untrusted data.
- The container is temporary. **Commit and push often.** In session 1 a background loop autosaved `docs/audit/` every 10 minutes.
- Model files use CRLF line endings; edit them with `tools/edit_crlf.py` (on `fix-wave-01`), not with tools that convert line endings.
- The AMPL demo is limited to 2,000 variables; the model has ~4,190. `expand` still works, which is how the bridge gets the LP.

## 8. Working with this user

- Physicist; prefers concise, plain answers with jargon explained in footnotes. Wants to go slowly on structural questions and to understand each fix before it is made.
- Asked explicitly whether numbers were made up: always show where a number comes from (file:line or source page).
- Pushes go to `steel-mip` only, on the session branch; never to `main` unless asked. Don't open PRs unless asked.
