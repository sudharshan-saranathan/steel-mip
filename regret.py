#!/usr/bin/env python
"""
Regret matrix over an uncertain structural axis (default: scrap-availability regime).

Concept: a planner commits capacity expansion for an ASSUMED future W, sinks the
investment, then a DIFFERENT future G actually arrives. Regret(W->G) is the extra
discounted cost of having planned for W instead of having had perfect foresight of G:

    regret(W,G) = cost[ commit W's sunk builds, then optimise under G ]  -  PF(G)

where PF(G) is the perfect-foresight optimum for G. The diagonal (W=G) is ~0.

Recourse (what may still adapt after the sunk commitment):
  - SUNK_SET  = builds that are locked at W's levels (the committed clean-tech bet).
  - everything else (scrap-EAF / BF capacity, all dispatch) re-optimises under G.
  Set SUNK_SET = ALL_BUILDS for the rigid "no-adaptation" upper bound.

Infeasible recourse = catastrophic regret (committed too little clean capacity to
meet the target in the realised world); reported as 'INFEAS'.

Env knobs (all optional): MC_H2YEAR, MC_GRID_EF, MC_RAMP, MC_AVG_EMI, NG/H2/CCS prices,
REGRET_AXIS (only 'scrap' implemented), REGRET_SUNK ('clean' | 'all').
Output: regret_matrix.csv + printed table.
"""
import os, csv
from amplpy import AMPL, add_to_path
import ampl_module_base

add_to_path(os.path.join(os.path.dirname(ampl_module_base.__file__), "bin"))
PROJECT = os.path.dirname(os.path.abspath(__file__)); os.chdir(PROJECT)
YRS = list(range(2025, 2051))

ALL_BUILDS  = ["build_bof", "build_cdri", "build_ngdri", "build_h2dri", "build_scrap",
               "build_ccs_bf", "build_ccs_cdri", "build_ccs_ngdri"]
CLEAN_BUILDS = ["build_h2dri", "build_ccs_bf", "build_ccs_cdri", "build_ccs_ngdri"]
SUNK = ALL_BUILDS if os.environ.get("REGRET_SUNK") == "all" else CLEAN_BUILDS

SCRAPS  = ["starved", "low", "modest", "optimistic"]
H2YEAR  = os.environ.get("MC_H2YEAR", "2030")
GRID_EF = os.environ.get("MC_GRID_EF", "aggressive_re")
RAMP    = os.environ.get("MC_RAMP", "0.20")
AVG_EMI = os.environ.get("MC_AVG_EMI", "1.6")
NG, H2, CCS = os.environ.get("NG", "15"), os.environ.get("H2", "2500"), os.environ.get("CCS", "75")

_base = open("template.mod").read()
_base = "\n".join(l for l in _base.splitlines()
                  if "include yreport.mod" not in l and "include report.mod" not in l)
_base = _base.replace("option gurobi_options 'Threads=5 TimeLimit=600 mipgap=0.002';",
                      "option gurobi_options 'Threads=8 TimeLimit=120 mipgap=0.0001';")

def model_for(scrap):
    s = _base
    for tok, val in (("NGVAL", NG), ("H2ENDVAL", H2), ("H2YEARVAL", H2YEAR), ("CCSVAL", CCS),
                     ("AVGEMIVAL", AVG_EMI), ("RAMPVAL", RAMP),
                     ("SCRAPREGIMEFILE", f"scenarios/scrap_{scrap}.mod"),
                     ("NGAVAILFILE", "scenarios/ng_avail_normal.mod"),
                     ("GRIDEFFILE", f"scenarios/grid_ef_{GRID_EF}.mod")):
        s = s.replace(tok, str(val))
    return s

def solve(scrap, fix_builds=None):
    a = AMPL(); a.eval(model_for(scrap))
    if fix_builds is not None:
        for v in SUNK:
            for y in YRS:
                a.eval(f"fix {v}[{y}] := {fix_builds[(v, y)]};")
    a.eval("option solver gurobi; option gurobi_options 'Threads=8 mipgap=0.0001 outlev=0';")
    a.solve(); g = lambda e: a.get_value(e)
    if g("solve_result") != "solved":
        return None
    return dict(cost=g("sum{t in T} discount_factor[t]*total_cost[t]"),
                D=g("sum{t in T} discount_factor[t]*total_steel[t]"),
                builds={(v, y): g(f"{v}[{y}]") for v in ALL_BUILDS for y in YRS})

print(f"Regret matrix | cell H2-{H2YEAR}/{GRID_EF}, prices {NG}/{H2}/{CCS}, ramp {RAMP}, ET {AVG_EMI}")
print(f"sunk set = {'ALL builds (no adaptation)' if SUNK is ALL_BUILDS else 'clean-tech only (adaptive)'}\n")

# perfect-foresight optimum for each world (also the planning solution we commit from)
PF = {s: solve(s) for s in SCRAPS}
feas = [s for s in SCRAPS if PF[s]]
print("Standalone feasibility:", {s: ("ok" if PF[s] else "INFEAS") for s in SCRAPS}, "\n")

rows = []
hdr = f"{'plan\\realize':>14s} " + " ".join(f"{g:>11s}" for g in feas)
print(hdr); print("-" * len(hdr))
for w in feas:
    cells = []
    for gg in feas:
        com = solve(gg, fix_builds=PF[w]["builds"])
        if com is None:
            cells.append("INFEAS"); rows.append(dict(plan=w, realize=gg, regret_usd_t="INFEAS"))
        else:
            reg = (com["cost"] - PF[gg]["cost"]) / PF[gg]["D"]
            cells.append(f"{reg:+.1f}"); rows.append(dict(plan=w, realize=gg, regret_usd_t=round(reg, 2)))
    print(f"{w:>14s} " + " ".join(f"{c:>11s}" for c in cells))

_mode = "rigid" if SUNK is ALL_BUILDS else "adaptive"
_out = f"regret_matrix_{_mode}.csv"
with open(_out, "w", newline="") as fh:
    wtr = csv.DictWriter(fh, fieldnames=["plan", "realize", "regret_usd_t"])
    wtr.writeheader(); wtr.writerows(rows)
print(f"\n$/t-steel. rows=planning world, cols=realised world. diagonal~0. -> {_out}")
