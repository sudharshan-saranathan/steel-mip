# Paper — Results section design (working notes)

_Design discussion captured 2026-06-29 (branch `mip-v2` @ `3c40b0b`). Decisions + open questions for the Results section. Not methodology (that's `summary.md`); this is structure/argument._

## Paper shape
Intro → Methodology → **Results (the bulk)**. Results is organised around two driving questions:

1. **What is the impact of structural vs. stochastic parameters on decarbonisation?**
2. **How is least-cost decarbonisation different from least-risk decarbonisation?**

The two questions cut *across* the subsections rather than mapping 1:1: Q1 is answered partly in A (structural sweep) and partly in B (variance decomposition of the cloud); Q2 lives in B (and needs the engine extended — see below).

---

## Subsection A — deterministic backbone (working title: "Build-rate friction and the feasibility frontier")
Mode-0 / mode-1 / mode-2 runs across a range of ETs. Establishes the deterministic frontier and *earns the right* to fix one (ET, mode) cell for B.

- **mode 0** = no limits (all ramp ceilings = ∞, on electrolysers AND the four conventional routes). The idealised baseline: logistics + cap-infra instantly available. NOTE it removes *all* build friction, not just H2.
- **mode 1** = linear additive slab. ⚠️ PARKED — magnitude must be re-referenced to `h2_ref_cap` before a 3-mode comparison is coherent; or drop it and present A as a 2-mode (counterfactual vs realistic) contrast. DECIDE.
- **mode 2** (default) = realistic rising-baseline + Gaussian envelope.

**Organising result (already in hand):** ramp *shape* only matters near the feasibility frontier — under loose ET all modes converge to ~the same economically-chosen path; the modes separate only as ET tightens. So the natural figure is a **mode × ET feasibility map** (tightest feasible ET per mode). Headline: *expansion caps are economically irrelevant until you approach the frontier, where they alone decide feasibility.*

**Comparisons isolate different things:** 0 vs {1,2} = all build friction vs some; 1 vs 2 = pure H2 ramp shape (conventional slabs held identical).

**Blockers before A figures are real:** (1) mode-1 re-reference or drop; (2) everything predates the mode-2 default flip → re-run all MC/frontier under mode 2.

---

## Subsection B — stochastic regret (the novelty)
Fix an ET + mode, take the optimal trajectory, weigh it against the MC cloud (supply shocks, cost dips, alternate fuel-price worlds). B parents thematic sub-subsections — each a thematic "alternate universe."

### Two evaluation variants (they bracket adaptability)
- **(a) Frozen / no course-correction:** plug the committed trajectory into the realized world; forward-compute cost & emissions, subject to physical availability. NOT optimization — a `min(planned, available)` clip in the forward pass.
  - Price-only shock → **cost moves, output/emissions pinned**.
  - Availability dips **below planned usage** → route forcibly curtailed to available supply → its emissions fall **and** steel output falls short → unmet demand / forced curtailment (the rigid-case catastrophe; no substitution possible).
  - = the rigid **upper bound** on regret.
- **(b) Rolling course-correction:** re-optimize the remaining horizon every 5–10 yr with past builds sunk, once observation reveals the world. Post-shock re-opt idles expensive import-dependent plants and leans on domestic coal-DRI / scrap → **both cost and emissions move**, via substitution.
  - = the adaptive **lower bound** on regret.
- **The (a)−(b) gap is a headline:** the value of course-correction = the dollar (and emissions/feasibility) cost of lock-in.

### Supply-shock mechanics (NG + coking coal, India import-dependence)
- A supply shock = a **severe transient price spike** (± a partial availability dip), NOT a hard cutoff to zero (that ~never happens). One mechanism by magnitude.
- **Utilisation floor relaxes** on the affected routes for the shock window — **only in variant (b)** (the post-shock re-optimization node), scoped to shocked routes, so the optimizer can idle them instead of being forced to run at 75%. In (a) there's no re-opt, so the floor never enters. Relax automatically whenever the shock flag is active and let economics set utilisation (agreed).
- Floor-off is the regret mechanism: idle-but-paid capacity (sunk capex + fixed opex, zero output) = **stranded import-dependent capital** = energy-security regret in dollars.
- Catastrophe is **endogenous** (a cost cliff / forced curtailment when no domestic substitute exists), not an imposed switch → more defensible.
- Calibration: coking coal ~3× (2022), LNG worse — finite, empirically anchored.
- India framing: stress *imported* feedstocks (coking coal for BF, NG); *domestic* coal-DRI is the security hedge → energy-security-vs-decarbonisation tension straight from the model.

### Proposed B skeleton
- **B0** — joint cloud + attribution (motivates which drivers deserve a deep-dive). The joint cloud is the honest risk picture; thematic universes are conditional *explanatory* slices of it, not the primary risk measure.
- **B1** — technology-cost bets (H2 capex + CCS cost; incl. the **compound corner** — H2-expensive AND CCS-expensive together, where both clean backstops fail; OFAT misses it). Mechanism: irreversible investment risk.
- **B2** — feedstock-security volatility (NG + coking coal; India import framing; supply-shock mechanics above). Mechanism: recourse/dispatch + security; hedge = fuel diversity.
- **B3** — synthesis: **least-cost vs. least-risk** on the joint cloud (Q2 payoff).
- Run each universe in **both** directions (downside → regret/catastrophe; upside → clawed back by course-correction). The repeated *asymmetry* is irreversibility shown N times.

### Q2 — least-cost vs least-risk (engine gap)
Current engine commits to the *central* plan and measures its regret = **regret of the least-cost plan**, NOT a least-*risk* plan. To answer Q2:
- **(a, recommended) candidate-plan menu:** define archetypal commitments (backloaded/least-cost, balanced, front-loaded H2 hedge, CCS-optionality), evaluate each across the same cloud, plot the (expected cost, risk) Pareto frontier. Least-cost and least-risk are two points; the gap = price of robustness. Reuses `regret_stoch.py`.
- (b) solve a risk objective directly (min-CVaR / min-max-regret) — proper stochastic program, bigger lift, likely overkill.

**Risk metric undecided** (gates the build). Candidates: P(catastrophic/infeasible recourse), CVaR of regret, mean-variance of cost, P(target miss). For an irreversibility thesis, P(catastrophic) or CVaR-of-regret is more defensible than mean-variance (captures the upside/downside asymmetry). **DECIDE before building the menu.**

---

## The A↔B fusion (the paper's argument)
The **ramp friction from A is exactly what limits course-correction in B.** Under mode 0 (instant builds) you rebuild domestic capacity the moment a shock hits → course-correction is free → least-risk = least-cost. Under realistic ramps (mode 2) you can't rebuild fast post-shock → pre-built insurance capacity has value → least-risk diverges. The expansion cap is what gives irreversibility its teeth. State this explicitly — it's what makes A and B one paper.

The Q1→Q2 bridge: Q1 shows the dominant variance is structural and (for timing) resolves *after* you must commit; Q2 shows that exact combination (dominant + irreversible + late-resolving) is *why* least-cost and least-risk diverge.

---

## Open decisions / blockers (carry-over)
1. **mode 1**: re-reference magnitude to `h2_ref_cap`, or drop it (2-mode A).
2. **Re-run** all MC/frontier/regret under the mode-2 default (prior CSVs stale).
3. **Risk metric** for "least-risk" — pick one (gates Q2 build).
4. **H2-timing category convention**: structural (committed policy date) in A vs stochastic (dominant uncertain driver) in B — name it or it reads as double-counting.
5. **`belief_infeasible` drop (16.5%)** is non-random and timing-correlated → biases both the Q1 decomposition and the Q2 tail. Fix the planning-step target-relaxation before any headline number is final.
6. **Coking-coal (and thermal-coal) sampling**: currently unsampled in the LHS; required before B2 can run.
7. **Tooling for supply shocks**: shocked params (`ng_cost`, coking coal, availability caps) must be t-indexed and let-able over `[onset, onset+duration]`; sample shock as (onset, magnitude, duration); onset-year is a discrete uncertainty parallel to the H2 start-year. Same value-switch idiom as the ramp refactor → stays pure LP.

## Next step
Review the proposed A and B together (was about to start when this was checkpointed).
