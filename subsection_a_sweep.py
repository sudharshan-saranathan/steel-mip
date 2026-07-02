#!/usr/bin/env python
"""Subsection A -- deterministic structural sensitivity (mode 0 vs mode 2), no MC.

For each structural axis (scrap regime, grid-EF, NG availability, coking-coal
availability, H2 start year), hold every other axis at its CENTRAL value and
bisect the feasibility floor (tightest avg_emi that still solves) for both
ramp modes 0 (no-limits counterfactual) and 2 (realistic Gaussian ramp,
h2_ref_cap=4Mt, definitions.mod).

Central scenario: NG=15, h2_capex_mult=1.05, CCS=75, scrap=modest,
NG avail=normal, coking avail=normal, grid=moderate_re, H2 start=2030.
(Central prices per HANDOFF.md; central axis values = the model's own defaults.)

Writes subsection_a_floors.csv: one row per (axis, axis_value, mode) cell with
the ET floor, NPV system cost at the floor, and 2050 H2-DRI output / CCS capture
(the two headline mechanism indicators -- H2-led vs CCS-led).
"""
import os, csv
from amplpy import AMPL, add_to_path
import ampl_module_base
add_to_path(os.path.join(os.path.dirname(ampl_module_base.__file__), "bin"))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

MODES = [0, 2]
ET_LO, ET_HI = 1.0, 2.5          # bisection bracket; widened automatically if HI infeasible
BISECT_ITERS = 8                  # -> resolution (ET_HI-ET_LO)/2^8 ~= 0.006
GUROBI_OPTS = "Threads=6 TimeLimit=120 mipgap=0.0001 outlev=0"

CENTRAL = dict(ng=15.0, h2capex=1.05, ccs=75.0, scrap="modest",
               ngavail="normal", ccoal="normal", grid="moderate_re", h2year=2030)

AXES = {
    "scrap_regime":   {"values": ["starved", "low", "modest", "optimistic"], "central": "modest"},
    "grid_ef":        {"values": ["bau", "moderate_re", "aggressive_re"],    "central": "moderate_re"},
    "ng_availability":{"values": ["scarce", "normal", "abundant"],           "central": "normal"},
    "ccoal_availability": {"values": ["scarce", "normal", "abundant"],       "central": "normal"},
    "h2_start_year":  {"values": [2030, 2035, 2040, 2045],                   "central": 2030},
}

with open("template.mod") as fh:
    _template = fh.read()
_template = "\n".join(
    l for l in _template.splitlines()
    if "include yreport.mod" not in l and l.strip() != "solve;" and "gurobi_options" not in l
)


def build_model(axis_name, axis_value, avg_emi, mode):
    cfg = dict(CENTRAL)
    key = {"scrap_regime": "scrap", "grid_ef": "grid", "ng_availability": "ngavail",
           "ccoal_availability": "ccoal", "h2_start_year": "h2year"}[axis_name]
    cfg[key] = axis_value
    tok = {
        "NGVAL": cfg["ng"], "H2CAPXVAL": cfg["h2capex"], "H2YEARVAL": cfg["h2year"],
        "CCSVAL": cfg["ccs"], "AVGEMIVAL": avg_emi, "RAMPVAL": 0.15,
        "SCRAPREGIMEFILE": f"scenarios/scrap_{cfg['scrap']}.mod",
        "NGAVAILFILE": f"scenarios/ng_avail_{cfg['ngavail']}.mod",
        "CCOALFILE": f"scenarios/ccoal_{cfg['ccoal']}.mod",
        "GRIDEFFILE": f"scenarios/grid_ef_{cfg['grid']}.mod",
    }
    s = _template
    for k, v in tok.items():
        s = s.replace(k, str(v))
    return s


def solve_cell(axis_name, axis_value, avg_emi, mode):
    a = AMPL()
    a.eval(f"option solver gurobi; option gurobi_options '{GUROBI_OPTS}';")
    a.eval(build_model(axis_name, axis_value, avg_emi, mode))
    a.eval(f"let h2_ramp_mode := {mode};")
    a.solve()
    ok = a.get_value("solve_result") == "solved"
    out = {"feasible": ok}
    if ok:
        out["npv_cost"] = a.get_value("obj")
        out["h2dri_2050"] = a.get_value("h2dri_output[2050]")
        out["ccs_2050"] = a.get_value("total_ccs[2050]")
    return out


def find_floor(axis_name, axis_value, mode):
    lo, hi = ET_LO, ET_HI
    hi_res = solve_cell(axis_name, axis_value, hi, mode)
    tries = 0
    while not hi_res["feasible"] and tries < 3:
        hi += 0.5
        hi_res = solve_cell(axis_name, axis_value, hi, mode)
        tries += 1
    if not hi_res["feasible"]:
        return {"floor": None, "note": f"infeasible even at ET={hi}", **hi_res}
    lo_res = solve_cell(axis_name, axis_value, lo, mode)
    if lo_res["feasible"]:
        return {"floor": lo, "note": f"feasible even at ET={lo} (floor <= {lo})", **lo_res}
    best = hi_res
    for _ in range(BISECT_ITERS):
        mid = (lo + hi) / 2
        res = solve_cell(axis_name, axis_value, mid, mode)
        if res["feasible"]:
            hi, best = mid, res
        else:
            lo = mid
    return {"floor": round(hi, 4), "note": "", **best}


def main():
    rows = []
    for axis_name, spec in AXES.items():
        for val in spec["values"]:
            for mode in MODES:
                print(f"[{axis_name}={val}, mode={mode}] bisecting...", flush=True)
                r = find_floor(axis_name, val, mode)
                row = {"axis": axis_name, "axis_value": val, "mode": mode,
                       "et_floor": r.get("floor"), "npv_cost": r.get("npv_cost"),
                       "h2dri_2050": r.get("h2dri_2050"), "ccs_2050": r.get("ccs_2050"),
                       "note": r.get("note", "")}
                print("  ->", row, flush=True)
                rows.append(row)

    with open("subsection_a_floors.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["axis", "axis_value", "mode", "et_floor",
                                            "npv_cost", "h2dri_2050", "ccs_2050", "note"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {len(rows)} rows -> subsection_a_floors.csv")


if __name__ == "__main__":
    main()
