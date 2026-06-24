#!/usr/bin/env python
"""
High-density 2-D grid sweep: H2 cost × CCS cost.

Sweeps a 100×100 full grid (10,000 points) over the two axes; all other
uncertain inputs are fixed at their mid-range values.

Grid axes:
    h2_end_cost  ng_cost_h2_end   $/ton       linspace(1000, 4500, 100)
    ccs_end_cost n10_ccs_cost_end $/tCO2      linspace(  25,  125, 100)

Fixed at mid-range:
    ng_cost      n5_cost_NG       $/MMBtu     15
    h2_start_year ng_h2_start_year            2030
    scrap_rate   n8_scrap_rate    1/yr        0.06
"""
import os, csv, time
import numpy as np
from amplpy import AMPL, add_to_path
import ampl_module_base

_default_ampl_dir = os.path.join(os.path.dirname(ampl_module_base.__file__), "bin")
add_to_path(os.environ.get("AMPL_DIR", _default_ampl_dir))

# ----------------------------- configuration -----------------------------
PROJECT   = os.path.dirname(os.path.abspath(__file__))
N_H2      = int(os.environ.get("MC2D_NH2",  "100"))
N_CCS     = int(os.environ.get("MC2D_NCCS", "100"))
H2_START  = int(os.environ.get("MC2D_H2_START", "0"))
H2_END    = int(os.environ.get("MC2D_H2_END",   str(N_H2)))
SCENARIO  = os.environ.get("MC_SCENARIO", "normal")
SCRAP_REGIME = os.environ.get("MC_SCRAP_REGIME", "modest")
OUT_CSV   = os.path.join(PROJECT, os.environ.get("MC_OUT", "mc_2d_results.csv"))

SCEN_FILE = {"normal":     "scenarios/ng_avail_normal.mod",
             "shock":      "scenarios/ng_avail_shock.mod",
             "optimistic": "scenarios/ng_avail_optimistic.mod"}[SCENARIO]

# Scrap-availability regime (discrete axis, mirrors the NG scenario above).
# Common 35 Mt 2025 base; regimes differ by growth: 0/2/4/6 %/yr.
SCRAP_FILE = {"starved":    "scenarios/scrap_starved.mod",     # 0%/yr
              "low":        "scenarios/scrap_low.mod",          # 2%/yr
              "modest":     "scenarios/scrap_modest.mod",       # 4%/yr
              "optimistic": "scenarios/scrap_optimistic.mod"}[SCRAP_REGIME]  # 6%/yr

NG_FIXED      = 15.0    # $/MMBtu
H2YEAR_FIXED  = int(os.environ.get("MC_H2YEAR", "2030"))   # H2-DRI start year (structural axis)

H2_GRID  = np.linspace(1000.0, 4500.0, N_H2)
CCS_GRID = np.linspace(  25.0,  125.0, N_CCS)

# ----------------------- build per-draw model script ----------------------
with open(os.path.join(PROJECT, "template.mod")) as fh:
    TEMPLATE = fh.read()
TEMPLATE = "\n".join(l for l in TEMPLATE.splitlines()
                     if "include yreport.mod" not in l and "include report.mod" not in l)
TEMPLATE = TEMPLATE.replace(
    "option gurobi_options 'Threads=5 TimeLimit=600 mipgap=0.002';",
    f"option gurobi_options 'Threads={os.environ.get('MC2D_THREADS','10')} TimeLimit=120 mipgap={os.environ.get('MC2D_MIPGAP','0.002')}';")

def model_for(h2end, ccs):
    s = TEMPLATE
    for tok, val in (("NGVAL", NG_FIXED), ("H2ENDVAL", h2end),
                     ("H2YEARVAL", H2YEAR_FIXED), ("CCSVAL", ccs),
                     ("SCRAPREGIMEFILE", SCRAP_FILE), ("NGAVAILFILE", SCEN_FILE)):
        s = s.replace(tok, str(val))
    return s

EXPR = {
    "obj":      "sum{t in T} discount_factor[t]*total_cost[t]",
    "S_cost":   "sum{t in T} total_cost[t]",
    "S_steel":  "sum{t in T} total_steel[t]",
    "Sd_cost":  "sum{t in T} discount_factor[t]*total_cost[t]",
    "Sd_steel": "sum{t in T} discount_factor[t]*total_steel[t]",
    "S_emis":   "sum{t in T} total_emissions[t]",
    "S_ccs":    "sum{t in T} total_ccs[t]",
    "c2050":    "total_cost[2050]",   "s2050": "total_steel[2050]",
    "e2050":    "total_emissions[2050]",
    "bof2050":  "steel_bof[2050]",    "eaf2050": "steel_eaf[2050]",
    "scrap2050":"steel_scrap_eaf[2050]",
    "dri2050":  "dri_eaf_steel_out[2050]", "coal2050": "coaldri_output[2050]",
    "ng2050":   "ngdri_output[2050]", "h2_2050": "h2dri_output[2050]",
}

FIELDS = (["i_h2", "i_ccs", "h2_end_cost", "ccs_end_cost", "scenario", "scrap_regime", "status",
           "obj", "lifetime_avg_cost", "levelized_avg_cost", "lifetime_avg_emis",
           "capture_per_t", "cost_2050", "emis_2050",
           "f_bof_2050", "f_eaf_2050", "f_scrap_2050",
           "f_coal_2050", "f_ng_2050", "f_h2_2050", "solve_s"])

def safe_div(a, b):
    return a / b if b not in (0, 0.0) else 0.0

def extract(ampl):
    v = {k: ampl.get_value(e) for k, e in EXPR.items()}
    s = v["S_steel"]; s50 = v["s2050"]
    return {
        "obj":               v["obj"],
        "lifetime_avg_cost": safe_div(v["S_cost"], s),
        "levelized_avg_cost":safe_div(v["Sd_cost"], v["Sd_steel"]),
        "lifetime_avg_emis": safe_div(v["S_emis"], s),
        "capture_per_t":     safe_div(v["S_ccs"], s),
        "cost_2050":         safe_div(v["c2050"], s50),
        "emis_2050":         safe_div(v["e2050"], s50),
        "f_bof_2050":        safe_div(v["bof2050"], s50),
        "f_eaf_2050":        safe_div(v["eaf2050"], s50),
        "f_scrap_2050":      safe_div(v["scrap2050"], s50),
        "f_coal_2050":       safe_div(v["coal2050"], s50),
        "f_ng_2050":         safe_div(v["ng2050"], s50),
        "f_h2_2050":         safe_div(v["h2_2050"], s50),
    }

# ------------------------------- run sweep --------------------------------
def main():
    os.chdir(PROJECT)
    H2_SLICE = H2_GRID[H2_START:H2_END]
    N_TOTAL = len(H2_SLICE) * N_CCS
    RESET_EVERY = 2000
    ampl = AMPL()
    n_ok = n_inf = n_err = 0
    t0 = time.time()
    draw = 0
    with open(OUT_CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader()
        for i_h2, h2end in zip(range(H2_START, H2_END), H2_SLICE):
            for i_ccs, ccs in enumerate(CCS_GRID):
                if draw and draw % RESET_EVERY == 0:
                    ampl.close(); ampl = AMPL()
                row = {"i_h2": i_h2, "i_ccs": i_ccs,
                       "h2_end_cost": round(h2end, 4),
                       "ccs_end_cost": round(ccs, 4),
                       "scenario": SCENARIO, "scrap_regime": SCRAP_REGIME}
                td = time.time()
                try:
                    ampl.eval(model_for(h2end, ccs))
                    status = ampl.get_value("solve_result")
                    row["status"] = status
                    if status == "solved":
                        row.update(extract(ampl)); n_ok += 1
                    else:
                        n_inf += 1
                except Exception as e:
                    row["status"] = "error:" + str(e).splitlines()[0][:60]; n_err += 1
                row["solve_s"] = round(time.time() - td, 3)
                w.writerow(row)
                draw += 1
                if draw % 200 == 0:
                    fh.flush()
                    el = time.time() - t0
                    print(f"{draw}/{N_TOTAL}  ok={n_ok} infeas={n_inf} err={n_err}  "
                          f"{el:.0f}s  ({el/draw:.2f}s/draw, ETA {el/draw*(N_TOTAL-draw)/60:.0f} min)",
                          flush=True)
    print(f"DONE  ok={n_ok} infeasible={n_inf} error={n_err}  "
          f"total {time.time()-t0:.0f}s  -> {OUT_CSV}")

if __name__ == "__main__":
    main()
