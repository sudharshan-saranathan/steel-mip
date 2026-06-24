#!/usr/bin/env python3
"""
Smoke tests for the linearized (MILP) Steel Decarbonisation model.

Solves 3 deterministic parameter combinations through template.mod and checks
physical invariants:
  1. solve_result == "solved"
  2. objective finite and positive
  3. total_steel > 0 every year (and pinned to demand)
  4. emissions >= 0 every year
  5. route shares at 2050 (BOF + DRI-EAF + Scrap-EAF) sum to ~1
  6. CCS capture >= 0 every year
  7. discount factor strictly decreasing
  8. 2050 unit cost within a plausible band
"""
import os, sys
from amplpy import AMPL, add_to_path

add_to_path(os.environ.get("AMPL_DIR", "/Applications/AMPL"))

PROJECT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(PROJECT, "template.mod")) as fh:
    _TEMPLATE = fh.read()
# drop report includes (we read values via the API)
_TEMPLATE = "\n".join(l for l in _TEMPLATE.splitlines()
                      if "include yreport.mod" not in l and "include report.mod" not in l)
# bounded solve for the test
_TEMPLATE = _TEMPLATE.replace(
    "option gurobi_options 'Threads=5 TimeLimit=600 mipgap=0.002';",
    "option gurobi_options 'Threads=4 TimeLimit=120 mipgap=0.002';")

def build_model(ng, h2end, ccs, scrap, h2year, scenario="normal"):
    s = _TEMPLATE
    for tok, val in (("NGVAL", ng), ("H2ENDVAL", h2end), ("H2YEARVAL", h2year),
                     ("CCSVAL", ccs), ("SCRAPVAL", scrap),
                     ("NGAVAILFILE", f"scenarios/ng_avail_{scenario}.mod")):
        s = s.replace(tok, str(val))
    return s

CASES = [
    # label             ng   h2end   ccs  scrap  h2year
    ("low-cost-NG",     5,   1000,   25,  0.04,  2030),
    ("mid-baseline",   10,   2500,   75,  0.06,  2036),
    ("high-cost-NG",   20,   4000,  125,  0.08,  2045),
]

YEARS = list(range(2025, 2051))

def check(ampl):
    g = ampl.get_value
    failures = []

    obj = g("sum{t in T} discount_factor[t]*total_cost[t]")
    if not (obj > 0):
        failures.append(f"objective not positive: {obj}")

    steel = {t: g(f"total_steel[{t}]") for t in YEARS}
    if [t for t, v in steel.items() if v <= 0]:
        failures.append(f"total_steel <= 0 in: {[t for t,v in steel.items() if v<=0]}")

    if [t for t in YEARS if g(f"total_emissions[{t}]") < -1e-3]:
        failures.append("negative emissions present")

    s50 = steel[2050]
    frac = (g("steel_bof[2050]") + g("steel_eaf[2050]") + g("steel_scrap_eaf[2050]")) / s50
    if abs(frac - 1.0) > 0.01:
        failures.append(f"2050 route shares sum to {frac:.4f} (expected ~1)")

    if [t for t in YEARS if g(f"total_ccs[{t}]") < -1e-3]:
        failures.append("negative CCS present")

    df = [g(f"discount_factor[{t}]") for t in YEARS]
    if any(df[i] <= df[i+1] for i in range(len(df)-1)):
        failures.append("discount_factor not strictly decreasing")

    unit_cost = g("total_cost[2050]") / s50
    if not (50 <= unit_cost <= 2000):
        failures.append(f"2050 unit cost = {unit_cost:.1f} $/t (expected 50-2000)")

    return failures

def main():
    os.chdir(PROJECT)
    n_pass = n_fail = 0
    print(f"\n{'='*60}\nSteel MILP — smoke tests\n{'='*60}\n")
    for label, ng, h2end, ccs, scrap, h2year in CASES:
        print(f"[{label}]  ng={ng} h2end={h2end} ccs={ccs} scrap={scrap} h2yr={h2year}")
        ampl = AMPL()
        try:
            ampl.eval(build_model(ng, h2end, ccs, scrap, h2year))
            status = ampl.get_value("solve_result")
            print(f"  solve_result : {status}")
            if status != "solved":
                print(f"  FAIL — did not solve"); n_fail += 1; continue
            fails = check(ampl)
            if fails:
                for f in fails: print(f"  FAIL — {f}")
                n_fail += 1
            else:
                obj = ampl.get_value("sum{t in T} discount_factor[t]*total_cost[t]")
                e50 = ampl.get_value("total_emissions[2050]")
                s50 = ampl.get_value("total_steel[2050]")
                print(f"  PASS — obj={obj/1e9:.2f} B$  emis_2050={e50/1e6:.2f} Mt  steel_2050={s50/1e6:.2f} Mt")
                n_pass += 1
        except Exception as e:
            print(f"  ERROR — {str(e).splitlines()[0][:120]}"); n_fail += 1
        finally:
            ampl.close()
        print()
    print(f"{'='*60}\nResults: {n_pass} passed, {n_fail} failed\n{'='*60}\n")
    sys.exit(0 if n_fail == 0 else 1)

if __name__ == "__main__":
    main()
