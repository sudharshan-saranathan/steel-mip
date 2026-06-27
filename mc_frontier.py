#!/usr/bin/env python
"""
Feasibility frontier across the 48 structural cells
(scrap regime x H2-start year x grid-EF scenario; NG held at `normal`).

Feasibility of the avg_emi target is PRICE-INDEPENDENT (it is set by physical
limits: NG availability cap, scrap cap, H2 ramp/timing, CCS capturable base,
grid carbon intensity), so one solve per cell suffices. We solve each cell at a
single representative price point and record solve_result + the achieved
lifetime-average emissions.

Knobs MUST match the production run (run_all_cells.py / monte_carlo.py):
  MC_AVG_EMI  cumulative avg-emissions target (default 1.6)
  MC_RAMP     additive production ramp slab    (default 0.15)

Output: mc_frontier.csv (one row per cell) + a printed feasibility table.
"""
import os, csv, itertools
from amplpy import AMPL, add_to_path
import ampl_module_base

add_to_path(os.environ.get("AMPL_DIR",
            os.path.join(os.path.dirname(ampl_module_base.__file__), "bin")))

PROJECT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT)

# structural axes (match monte_carlo.py); NG is fixed at `normal` (second-order)
SCRAP_REGIMES = ["starved", "low", "modest", "optimistic"]
H2_YEARS      = [2030, 2035, 2040, 2045]
GRID_EFS      = ["bau", "moderate_re", "aggressive_re"]

SCEN_FILE     = "scenarios/ng_avail_normal.mod"
SCRAP_FILE    = {r: f"scenarios/scrap_{r}.mod"   for r in SCRAP_REGIMES}
GRID_EF_FILE  = {g: f"scenarios/grid_ef_{g}.mod" for g in GRID_EFS}

# representative price point (feasibility is price-independent; any point works)
NG_COST, H2_CAPEX_MULT, CCS_COST = 15.0, 1.0, 75.0   # H2 axis = green-H2 capex multiplier
# (feasibility is price/capex-independent -> the H2 value here is immaterial, set to central 1.0)

# structural knobs (template.mod has AVGEMIVAL/RAMPVAL tokens)
AVG_EMI = float(os.environ.get("MC_AVG_EMI", "1.6"))
RAMP    = float(os.environ.get("MC_RAMP", "0.15"))

with open("template.mod") as fh:
    TEMPLATE = fh.read()
TEMPLATE = "\n".join(l for l in TEMPLATE.splitlines()
                     if "include yreport.mod" not in l and "include report.mod" not in l)
TEMPLATE = TEMPLATE.replace(
    "option gurobi_options 'Threads=5 TimeLimit=600 mipgap=0.002';",
    "option gurobi_options 'Threads=10 TimeLimit=120 mipgap=0.0001';")


def model_for(scrap, h2year, grid_ef):
    s = TEMPLATE
    for tok, val in (("NGVAL", NG_COST), ("H2CAPXVAL", H2_CAPEX_MULT),
                     ("H2YEARVAL", h2year), ("CCSVAL", CCS_COST),
                     ("AVGEMIVAL", AVG_EMI), ("RAMPVAL", RAMP),
                     ("SCRAPREGIMEFILE", SCRAP_FILE[scrap]),
                     ("NGAVAILFILE", SCEN_FILE),
                     ("GRIDEFFILE", GRID_EF_FILE[grid_ef])):
        s = s.replace(tok, str(val))
    return s


def main():
    rows = []
    ampl = AMPL()
    print(f"target ET={AVG_EMI}  ramp={RAMP}\n")
    print(f"{'scrap':11s} {'H2yr':>5s} {'grid_ef':>14s} {'status':>11s} {'life_avg_emis':>13s}")
    for i, (scrap, h2y, grid_ef) in enumerate(
            itertools.product(SCRAP_REGIMES, H2_YEARS, GRID_EFS)):
        if i and i % 16 == 0:
            ampl.close(); ampl = AMPL()
        emis = ""
        try:
            ampl.eval(model_for(scrap, h2y, grid_ef))
            status = ampl.get_value("solve_result")
            if status == "solved":
                se = ampl.get_value("sum{t in T} total_emissions[t]")
                ss = ampl.get_value("sum{t in T} total_steel[t]")
                emis = round(se / ss, 4) if ss else ""
        except Exception as e:
            status = "error:" + str(e).splitlines()[0][:40]
        rows.append({"scrap_regime": scrap, "h2_start_year": h2y,
                     "grid_ef_scenario": grid_ef, "status": status,
                     "lifetime_avg_emis": emis})
        flag = "" if status == "solved" else "  <-- INFEASIBLE" if status == "infeasible" else f"  <-- {status}"
        print(f"{scrap:11s} {h2y:>5d} {grid_ef:>14s} {status:>11s} {str(emis):>13s}{flag}")

    with open("mc_frontier.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    n_feas = sum(1 for r in rows if r["status"] == "solved")
    print(f"\nFeasible cells: {n_feas}/{len(rows)}  "
          f"(infeasible: {len(rows)-n_feas})  -> mc_frontier.csv")


if __name__ == "__main__":
    main()
