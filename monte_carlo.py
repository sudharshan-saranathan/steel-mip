#!/usr/bin/env python
"""
Monte-Carlo uncertainty study for the Steel Decarbonisation MILP.

Samples four uncertain inputs from uniform priors (Latin Hypercube) over the
old grid envelopes, solves the (now linear) model for each draw, and writes one
CSV row per draw with the sampled inputs, key outputs, and feasibility status.

Sampled inputs (uniform over [lo, hi]):
    ng_cost      n5_cost_NG       $/MMBtu     [5,   20]
    h2_end_cost  ng_cost_h2_end   $/ton       [1000,4000]
    ccs_end_cost n10_ccs_cost_end $/ton       [25,  125]
    scrap_rate   n8_scrap_rate    1/yr        [0.04,0.08]

Also sampled (discrete, from the original grid years, via a 5th LHS dimension):
    h2_start_year  ng_h2_start_year   {2030,2033,2036,2039,2042,2045}

Fixed (NOT sampled):
    NG-availability scenario          -- supply constraint, fixed to 'normal'
"""
import os, sys, csv, time
import numpy as np
from scipy.stats import qmc
from amplpy import AMPL, add_to_path

# Make the AMPL binary discoverable (override with AMPL_DIR if installed elsewhere).
add_to_path(os.environ.get("AMPL_DIR", "/Applications/AMPL"))

# ----------------------------- configuration -----------------------------
PROJECT      = os.path.dirname(os.path.abspath(__file__))
N_SAMPLES    = int(os.environ.get("MC_N", "20000"))
SEED         = int(os.environ.get("MC_SEED", "20260624"))
YEARS        = [2030, 2033, 2036, 2039, 2042, 2045]   # discrete H2-DRI start years (sampled)
SCENARIO     = os.environ.get("MC_SCENARIO", "normal")     # normal|shock|optimistic
OUT_CSV      = os.path.join(PROJECT, os.environ.get("MC_OUT", "mc_results.csv"))

SCEN_FILE = {"normal":"scenarios/ng_avail_normal.mod",
             "shock":"scenarios/ng_avail_shock.mod",
             "optimistic":"scenarios/ng_avail_optimistic.mod"}[SCENARIO]

# uniform prior bounds: [ng_cost, h2_end_cost, ccs_end_cost, scrap_rate]
LO = np.array([5.0,   1000.0, 25.0,  0.04])
HI = np.array([20.0,  4000.0, 125.0, 0.08])
NAMES = ["ng_cost", "h2_end_cost", "ccs_end_cost", "scrap_rate"]

# ----------------------- build per-draw model script ----------------------
with open(os.path.join(PROJECT, "template.mod")) as fh:
    TEMPLATE = fh.read()
# drop the human-readable report includes (we extract values via the API instead)
TEMPLATE = "\n".join(l for l in TEMPLATE.splitlines()
                     if "include yreport.mod" not in l and "include report.mod" not in l)
# faster, bounded solves for the sweep (linear MILP => sub-second; cap as safety)
TEMPLATE = TEMPLATE.replace(
    "option gurobi_options 'Threads=5 TimeLimit=600 mipgap=0.002';",
    "option gurobi_options 'Threads=4 TimeLimit=120 mipgap=0.002';")

def model_for(ng, h2end, ccs, scrap, h2year):
    s = TEMPLATE
    for tok, val in (("NGVAL", ng), ("H2ENDVAL", h2end), ("H2YEARVAL", h2year),
                     ("CCSVAL", ccs), ("SCRAPVAL", scrap), ("NGAVAILFILE", SCEN_FILE)):
        s = s.replace(tok, str(val))
    return s

# raw AMPL expressions to pull after a solved draw (derived ratios computed in Python)
EXPR = {
    "obj":        "sum{t in T} discount_factor[t]*total_cost[t]",
    "S_cost":     "sum{t in T} total_cost[t]",
    "S_steel":    "sum{t in T} total_steel[t]",
    "Sd_cost":    "sum{t in T} discount_factor[t]*total_cost[t]",
    "Sd_steel":   "sum{t in T} discount_factor[t]*total_steel[t]",
    "S_emis":     "sum{t in T} total_emissions[t]",
    "S_ccs":      "sum{t in T} total_ccs[t]",
    "c2050":      "total_cost[2050]",      "s2050": "total_steel[2050]",
    "e2050":      "total_emissions[2050]",
    "bof2050":    "steel_bof[2050]",       "eaf2050": "steel_eaf[2050]",
    "scrap2050":  "steel_scrap_eaf[2050]",
    "dri2050":    "dri_eaf_steel_out[2050]","coal2050": "coaldri_output[2050]",
    "ng2050":     "ngdri_output[2050]",    "h2_2050": "h2dri_output[2050]",
}

FIELDS = (["draw"] + NAMES + ["h2_start_year","scenario","status",
          "obj","lifetime_avg_cost","levelized_avg_cost","lifetime_avg_emis",
          "capture_per_t","cost_2050","emis_2050",
          "f_bof_2050","f_eaf_2050","f_scrap_2050",
          "f_coal_2050","f_ng_2050","f_h2_2050","solve_s"])

def safe_div(a, b):
    return a / b if b not in (0, 0.0) else 0.0

def extract(ampl):
    v = {k: ampl.get_value(e) for k, e in EXPR.items()}
    s = v["S_steel"]; s50 = v["s2050"]; dri = v["dri2050"]
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
    os.chdir(PROJECT)  # so the model's relative include paths resolve
    # 5-dim Latin Hypercube: dims 0-3 continuous (LO..HI), dim 4 -> discrete start-year
    U = qmc.LatinHypercube(d=5, seed=SEED).random(n=N_SAMPLES)
    X = qmc.scale(U[:, :4], LO, HI)
    YR = [YEARS[min(len(YEARS) - 1, int(u * len(YEARS)))] for u in U[:, 4]]
    RESET_EVERY = 2000   # recreate the AMPL process periodically (memory hygiene)
    ampl = AMPL()
    n_ok = n_inf = n_err = 0
    t0 = time.time()
    with open(OUT_CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader()
        for i in range(N_SAMPLES):
            ng, h2end, ccs, scrap = X[i]; h2year = YR[i]
            if i and i % RESET_EVERY == 0:
                ampl.close(); ampl = AMPL()
            row = {"draw": i, "ng_cost": ng, "h2_end_cost": h2end,
                   "ccs_end_cost": ccs, "scrap_rate": scrap,
                   "h2_start_year": h2year, "scenario": SCENARIO}
            td = time.time()
            try:
                ampl.eval(model_for(ng, h2end, ccs, scrap, h2year))
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
            if (i + 1) % 200 == 0:
                fh.flush()
                el = time.time() - t0
                print(f"{i+1}/{N_SAMPLES}  ok={n_ok} infeas={n_inf} err={n_err}  "
                      f"{el:.0f}s  ({el/(i+1):.2f}s/draw, ETA {el/(i+1)*(N_SAMPLES-i-1)/60:.0f} min)",
                      flush=True)
    print(f"DONE  ok={n_ok} infeasible={n_inf} error={n_err}  "
          f"total {time.time()-t0:.0f}s  -> {OUT_CSV}")

if __name__ == "__main__":
    main()
