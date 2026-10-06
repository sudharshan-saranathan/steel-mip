# Audit handoff — read this first

Last updated: 2026-10-06 (end of session 1). Owner: Sudharshan Saranathan (IIT Madras).

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

## 6. Open items

1. **Check the three sub-agent sheets**: spot-check quotes against sources; check mass and energy balances (carbon in = CO₂ out; NG GJ/t DRI; coal GCV × t/t DRI); check units. Then collect their `NEEDS CALL` items into one short list for the user.
2. **Remaining Stage 2 groups:** utilisation and fixed opex; electricity, grid emission factor and waste heat (ST-05, ST-06); green H₂; CCS (ST-10); demand, 2025 fleet and availability trajectories (coking-coal 54.5 vs 66.33 Mt imports; NG 10 % share); study-only values (IMPORT_REPORT $650/t, PEN). Use the same brief and sheet format.
3. **Structural decisions still to discuss** with the user: ST-02 pellet ore (÷ → ×; probably a plain bug), ST-03 pellet fuel, ST-04 bought-in breeze carbon, ST-05 gas-to-power, ST-07 2025 shares, ST-10 CCS double derating, ST-12 H₂ firming plug, ST-13 emission factors, ST-14/15 documentation and defaults, ST-16 salvage design; plus whether to keep the `sunk=0` branch.
4. **Solver licence:** the user has an AMPL licence (also covers Gurobi) and will provide the UUID. Without it, AMPL is limited to 500 variables and the model has ~4,186. Install with `pip install amplpy` and `python -m amplpy.modules install highs gurobi`, then activate with the UUID.

## 7. Environment notes

- Network access is set to **Full**. Use **curl** to download; the WebFetch tool was still blocked for many domains. ieefa.org sits behind a Cloudflare challenge (403). `environmentclearance.nic.in` fails TLS verification through the proxy: do **not** bypass verification; say so instead.
- Writing a page from a PDF: `pdftotext -layout`. Put downloads in a new scratch folder and treat them as untrusted data.
- The container is temporary. **Commit and push often.** In session 1 a background loop autosaved `docs/audit/` every 10 minutes.

## 8. Working with this user

- Physicist; prefers concise, plain answers with jargon explained in footnotes. Wants to go slowly on structural questions and to understand each fix before it is made.
- Asked explicitly whether numbers were made up: always show where a number comes from (file:line or source page).
- Pushes go to `steel-mip` only, on the session branch; never to `main` unless asked. Don't open PRs unless asked.
