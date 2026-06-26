#!/usr/bin/env python
"""
Rolling course-correction regret engine.

A planner commits capacity in 5-year blocks. At t=2025 it believes the PUBLISHED
CENTRAL FORECAST (consensus 2050 values for H2 timing/cost, grid-EF, scrap). As
the TRUE world unfolds it observes deviations and re-plans every 5 years
(model-predictive-control style), with all prior builds SUNK. Regret = realised
discounted cost of the rolled path under the true world  -  PF(true world).

Worlds are parameter bundles -> template tokens, so the uncertain axis is just a
selector and deviations can be positive (better than forecast) or negative.

Belief / reveal = NAIVE PERSISTENCE:
  - h2_year (gradual): keep expecting the forecast date until it passes with H2
    still absent -> then assume "not coming" (plan without new H2); if H2 later
    appears, observe it and re-incorporate. (genuine multi-node correction)
  - scenario/price axes (grid, scrap, h2_end, ng, ccs): forecast at the 2025
    commit, then the observed true value from 2030 on (they diverge immediately).

Final realised cost re-optimises DISPATCH under the true world with all builds
fixed. If the committed fleet cannot meet the target under the true world, the
target is relaxed and the EF overshoot is reported ("cost it anyway, report EF
miss", per the agreed no-compliance handling).

Status: NEEDS VALIDATION (diagonal regret must be ~0). Run after the MC sweep
frees the CPU to avoid AMPL contention.
"""
import os, csv
from amplpy import AMPL, add_to_path
import ampl_module_base

add_to_path(os.path.join(os.path.dirname(ampl_module_base.__file__), "bin"))
PROJECT = os.path.dirname(os.path.abspath(__file__)); os.chdir(PROJECT)
YRS  = list(range(2025, 2051))
NODES = [2025, 2030, 2035, 2040, 2045]          # 5-yr commit points
BUILDS = ["build_bof", "build_cdri", "build_ngdri", "build_h2dri", "build_scrap",
          "build_ccs_bf", "build_ccs_cdri", "build_ccs_ngdri"]

RAMP    = os.environ.get("MC_RAMP", "0.20")
AVG_EMI = float(os.environ.get("MC_AVG_EMI", "1.8"))

# published central forecast (the consensus bundle the planner commits to)
CENTRAL = dict(scrap="modest", h2_year=2035, h2_end=2500, grid="moderate_re", ng=15, ccs=75)

# axis -> {below(worse), central, above(better)} deviation levels (trifurcation)
AXES = {
    "h2_year": {"worse": 2045, "central": 2035, "better": 2030},
    "grid":    {"worse": "bau", "central": "moderate_re", "better": "aggressive_re"},
    "scrap":   {"worse": "starved", "central": "modest", "better": "optimistic"},
    "h2_end":  {"worse": 4500, "central": 2500, "better": 1000},
}

_base = open("template.mod").read()
_base = "\n".join(l for l in _base.splitlines()
                  if "include yreport.mod" not in l and "include report.mod" not in l)
_base = _base.replace("option gurobi_options 'Threads=5 TimeLimit=600 mipgap=0.002';",
                      "option gurobi_options 'Threads=8 TimeLimit=120 mipgap=0.0001';")

def model_text(world, avg_emi=AVG_EMI):
    s = _base
    for tok, val in (("NGVAL", world["ng"]), ("H2ENDVAL", world["h2_end"]),
                     ("H2YEARVAL", world["h2_year"]), ("CCSVAL", world["ccs"]),
                     ("AVGEMIVAL", avg_emi), ("RAMPVAL", RAMP),
                     ("SCRAPREGIMEFILE", f"scenarios/scrap_{world['scrap']}.mod"),
                     ("NGAVAILFILE", "scenarios/ng_avail_normal.mod"),
                     ("GRIDEFFILE", f"scenarios/grid_ef_{world['grid']}.mod")):
        s = s.replace(tok, str(val))
    return s

def _new(world, avg_emi=AVG_EMI):
    a = AMPL(); a.eval(model_text(world, avg_emi))
    a.eval("option solver gurobi; option gurobi_options 'Threads=8 mipgap=0.0001 outlev=0';")
    return a

def solve(world, fix_builds=None, fix_years=None, avg_emi=AVG_EMI):
    """Solve `world`. Optionally fix builds (dict (var,yr)->val) for years in fix_years."""
    a = _new(world, avg_emi)
    if fix_builds:
        yrs = fix_years if fix_years is not None else YRS
        for v in BUILDS:
            for y in yrs:
                a.eval(f"fix {v}[{y}] := {fix_builds[(v, y)]};")
    a.solve(); g = lambda e: a.get_value(e)
    if g("solve_result") != "solved":
        return None
    return dict(cost=g("sum{t in T} discount_factor[t]*total_cost[t]"),
                D=g("sum{t in T} discount_factor[t]*total_steel[t]"),
                ef=g("sum{t in T} total_emissions[t]")/g("sum{t in T} total_steel[t]"),
                builds={(v, y): g(f"{v}[{y}]") for v in BUILDS for y in YRS})

def belief_world(central, true, axis, tk):
    """Naive-persistence belief of the world held at node tk."""
    w = dict(central)
    if axis == "h2_year":
        ty = true["h2_year"]
        if tk >= ty:            w["h2_year"] = ty          # H2 has appeared -> known
        elif tk < central["h2_year"]: w["h2_year"] = central["h2_year"]  # not yet due -> still expect forecast
        else:                   w["h2_year"] = 2055        # due but absent -> assume not coming
    else:
        w[axis] = central[axis] if tk == 2025 else true[axis]   # observed from 2030 on
    return w

def rolling(true, axis):
    """MPC roll: commit builds in 5-yr blocks under evolving belief, prior builds sunk."""
    committed = {}
    for k, tk in enumerate(NODES):
        bel = belief_world(CENTRAL, true, axis, tk)
        past = [y for y in YRS if y < tk]
        sol = solve(bel, fix_builds=committed if past else None, fix_years=past)
        if sol is None:
            return None  # planner's own belief-plan infeasible (shouldn't happen for central-ish beliefs)
        end = NODES[k + 1] if k + 1 < len(NODES) else 2051
        for v in BUILDS:
            for y in range(tk, end):
                committed[(v, y)] = sol["builds"][(v, y)]
    # realise: operate the fully-committed fleet under the TRUE world (dispatch free)
    real = solve(true, fix_builds=committed, fix_years=YRS)
    if real is None:                           # can't comply -> relax target, report EF miss
        real = solve(true, fix_builds=committed, fix_years=YRS, avg_emi=99.0)
        real["miss"] = real["ef"] - AVG_EMI
    else:
        real["miss"] = 0.0
    return real

if __name__ == "__main__":
    axis = os.environ.get("REGRET_AXIS", "h2_year")
    print(f"Rolling regret | central={CENTRAL} | axis={axis} | ET={AVG_EMI} ramp={RAMP}\n")
    rows = []
    for level, val in AXES[axis].items():
        true = dict(CENTRAL); true[axis] = val
        pf = solve(true)
        roll = rolling(true, axis)
        if pf is None or roll is None:
            print(f"  {level:8s} {axis}={val}: solve failed"); continue
        reg = (roll["cost"] - pf["cost"]) / pf["D"]
        tag = "(central, expect ~0)" if level == "central" else ""
        miss = f"  EF miss +{roll['miss']:.3f}" if roll["miss"] > 1e-3 else ""
        print(f"  {level:8s} {axis}={str(val):>12s}:  regret = ${reg:6.1f}/t{miss}   {tag}")
        rows.append(dict(axis=axis, level=level, value=val,
                         regret_usd_t=round(reg, 2), ef_miss=round(roll["miss"], 4)))
    with open(f"regret_roll_{axis}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["axis", "level", "value", "regret_usd_t", "ef_miss"])
        w.writeheader(); w.writerows(rows)
    print(f"\n-> regret_roll_{axis}.csv")
