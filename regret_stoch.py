#!/usr/bin/env python
"""
Stochastic-regret prototype (the pivoted paper core).

Commit to the optimum for a central world A, then realise STOCHASTIC worlds:
each draw perturbs the price/cost params (NG, H2 cost, CCS cost, coking coal,
H2 timing) around A. Under each realised world the planner course-corrects every
5 years (rolling MPC, prior builds sunk -- reuses the VALIDATED regret_roll
machinery), then we score REGRET PROPER = realised rolled cost - PF(realised).

Hard cumulative emissions target (AVG_EMI binds): emissions are pinned at the
target for feasible recourse and only deviate as an EF "miss" when the committed
fleet cannot comply (target_miss), or blow up entirely (catastrophic). So the
(Dcost, Demis) map here is a smooth cost-regret cloud + a feasibility cliff.
A soft carbon-price variant (continuous emissions tradeoff) is the next build.

Calibration of the per-param volatility follows this session's sensitivities:
coking coal wide (dominant, import volatility), H2 cost wide, CCS/NG narrower.
Capex is NOT yet sampled here (needs permanent capex_mult knobs) -- TODO.

Env: STOCH_N (draws, default 150), STOCH_SEED (default 20260626).
"""
import os, csv
import numpy as np
import regret_roll as rr   # validated engine: solve(), model_text(), BUILDS, NODES, YRS, CENTRAL

PROJECT = rr.PROJECT
AVG_EMI = rr.AVG_EMI
N    = int(os.environ.get("STOCH_N", "150"))
SEED = int(os.environ.get("STOCH_SEED", "20260626"))

# ---- realised-world sampler: per-param dist centred on CENTRAL, vol from sensitivities ----
H2_YEARS = [2030, 2035, 2040, 2045]
def sample_world(rng):
    w = dict(rr.CENTRAL)
    w["ng"]     = float(np.clip(rng.normal(15,   4),    5, 25))     # 2nd-order
    w["h2_end"] = float(np.clip(rng.normal(1.05, 0.25), 0.5, 1.6))  # green-H2 capex mult (was $/t price)
    w["ccs"]    = float(np.clip(rng.normal(75,   20),   25, 125))   # moderate
    w["ccoal"]  = float(np.clip(rng.normal(190,  60),  120, 450))   # DOMINANT, right-skew via clip
    # central (2030, on-time) most likely; probability decays with delay length
    w["h2_year"]= int(rng.choice(H2_YEARS, p=[0.40, 0.30, 0.20, 0.10]))
    return w

# ---- multi-param belief + rolling (mirrors regret_roll, but ALL params may deviate) ----
def belief_multi(central, true, tk):
    w = dict(central)
    for ax in ("ng", "h2_end", "ccs", "ccoal", "h2_year", "scrap", "grid"):
        if ax == "h2_year":
            ty, exp = true["h2_year"], central["h2_year"]
            if tk >= ty:            w["h2_year"] = ty            # observed
            elif tk < exp:          w["h2_year"] = exp            # not yet due
            elif tk < exp + 5:      w["h2_year"] = exp + 5         # one grace node: "just late"
            else:                   w["h2_year"] = 2055           # grace exhausted -> cancelled
        else:
            w[ax] = central[ax] if tk == 2025 else true[ax]   # observed from 2030 on
    return w

def rolling_multi(true):
    committed = {}
    for k, tk in enumerate(rr.NODES):
        bel = belief_multi(rr.CENTRAL, true, tk)
        past = [y for y in rr.YRS if y < tk]
        sol = rr.solve(bel, fix_builds=committed if past else None, fix_years=past)
        if sol is None:
            return {"status": "belief_infeasible"}
        end = rr.NODES[k+1] if k+1 < len(rr.NODES) else 2051
        for v in rr.BUILDS:
            for y in range(tk, end):
                committed[(v, y)] = sol["builds"][(v, y)]
    real = rr.solve(true, fix_builds=committed, fix_years=rr.YRS)
    if real is not None:
        real["miss"] = 0.0; real["status"] = "ok"; return real
    real = rr.solve(true, fix_builds=committed, fix_years=rr.YRS, avg_emi=99.0)
    if real is not None:
        real["miss"] = real["ef"] - AVG_EMI; real["status"] = "target_miss"; return real
    return {"status": "catastrophic"}

# ---- per-draw evaluation (top-level + picklable so multiprocessing workers can run it).
# Each worker process gets its own regret_roll module + its own warm AMPL instance, so
# concurrent solves are fully isolated (no shared file/lock contention).
FIELDS = ["draw","ng","h2_end","ccs","ccoal","h2_year","status",
          "pf_cost_t","realised_cost_t","regret_t","ef_miss"]

def evaluate(world):
    """Solve one realised world: PF + rolling MPC -> a result row. `world` carries 'draw'."""
    i = world["draw"]
    pf   = rr.solve(world)
    roll = rolling_multi(world)
    row = dict(draw=i, ng=round(world["ng"],1), h2_end=round(world["h2_end"],3),
               ccs=round(world["ccs"],1), ccoal=round(world["ccoal"]), h2_year=world["h2_year"])
    if pf is None:
        row.update(status="pf_infeasible", pf_cost_t="", realised_cost_t="", regret_t="", ef_miss="")
    elif roll.get("status") in ("catastrophic", "belief_infeasible"):
        row.update(status=roll["status"], pf_cost_t=round(pf["cost"]/pf["D"],1),
                   realised_cost_t="", regret_t="", ef_miss="")
    elif roll["status"] == "target_miss":
        # roll["cost"] here is priced under a RELAXED target (avg_emi=99) -- not
        # comparable to pf["cost"], which is priced under the real, met target.
        # Reporting (roll-pf)/D as "regret" would read a compliance FAILURE as a
        # cost SAVING (skipping abatement looks cheap). Report the realised cost
        # for reference but leave regret_t blank; the outcome is the ef_miss, not
        # a $/t number -- a compliance-failure category, like catastrophic.
        row.update(status="target_miss", pf_cost_t=round(pf["cost"]/pf["D"],1),
                   realised_cost_t=round(roll["cost"]/pf["D"],1),
                   regret_t="", ef_miss=round(roll["miss"],4))
    else:
        reg = (roll["cost"] - pf["cost"]) / pf["D"]
        row.update(status=roll["status"], pf_cost_t=round(pf["cost"]/pf["D"],1),
                   realised_cost_t=round(roll["cost"]/pf["D"],1),
                   regret_t=round(reg,2), ef_miss=round(roll["miss"],4))
    return row

def main():
    import multiprocessing as mp
    from collections import Counter
    # Parent pre-samples ALL worlds from the master seed (sequential draws) and tags each
    # with its index -> results are independent of pool scheduling => reproducible, and
    # serial vs parallel give bit-identical numbers.
    rng = np.random.default_rng(SEED)
    worlds = []
    for i in range(N):
        w = sample_world(rng); w["draw"] = i; worlds.append(w)
    procs = int(os.environ.get("STOCH_PROCS", "8"))   # core budget = 8 (1 gurobi thread each)
    # give each worker FEW gurobi threads so P workers don't oversubscribe the cores
    # (P x 8 threads >> cores thrashes). Set before the pool spawns -> workers inherit.
    if procs > 1 and "MC_THREADS" not in os.environ:
        os.environ["MC_THREADS"] = str(max(1, ((os.cpu_count() or 4) - 2) // procs))
    print(f"Stochastic regret prototype | N={N} seed={SEED} procs={procs} "
          f"threads/worker={os.environ.get('MC_THREADS','8')} | central A | ET={AVG_EMI} ramp={rr.RAMP}")
    print(f"sampled: ng~N(15,4) h2_capexmult~N(1.05,0.25) ccs~N(75,20) ccoal~N(190,60) h2_year~cat\n")
    if procs <= 1:
        rows = [evaluate(w) for w in worlds]
    else:
        with mp.Pool(procs) as pool:
            rows = []
            for k, row in enumerate(pool.imap_unordered(evaluate, worlds, chunksize=4)):
                rows.append(row)
                if (k+1) % 20 == 0:
                    print(f"  {k+1}/{N} done", flush=True)
        rows.sort(key=lambda r: r["draw"])   # restore draw order (imap_unordered)

    with open(os.path.join(PROJECT, "regret_stoch.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)

    # ---- summary + attribution ----
    status_ct = Counter(r["status"] for r in rows)
    reg_rows = [r for r in rows if r["regret_t"] != ""]
    regs = np.array([r["regret_t"] for r in reg_rows], float)
    print(f"\n--- status breakdown ---")
    for s, c in status_ct.most_common():
        print(f"  {s:18s} {c:4d}  ({100*c/len(rows):.0f}%)")
    if len(regs):
        print(f"\n--- regret (USD/t), {len(regs)}'ok' (target-compliant) draws ---")
        print(f"  mean {regs.mean():.1f}  median {np.median(regs):.1f}  "
              f"p90 {np.percentile(regs,90):.1f}  max {regs.max():.1f}")
        print(f"\n--- attribution (corr of param with regret) ---")
        for p in ("ccoal","h2_end","ccs","ng","h2_year"):
            x = np.array([r[p] for r in reg_rows], float)
            c = np.corrcoef(x, regs)[0,1] if x.std() > 0 else 0.0
            print(f"  {p:8s} corr {c:+.2f}")
    # target_miss is a COMPLIANCE FAILURE, not a $/t regret number (see evaluate()) --
    # report its ef_miss separately rather than folding it into the regret distribution.
    miss_rows = [r for r in rows if r["status"] == "target_miss"]
    if miss_rows:
        misses = np.array([r["ef_miss"] for r in miss_rows], float)
        print(f"\n--- target_miss (compliance failure), {len(miss_rows)} draws ---")
        print(f"  EF overshoot: mean +{misses.mean():.3f}  max +{misses.max():.3f} tCO2/t")
    print(f"\n-> regret_stoch.csv")

if __name__ == "__main__":
    main()
