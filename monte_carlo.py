#!/usr/bin/env python
"""
Monte-Carlo uncertainty study for the Steel Decarbonisation MILP.

Samples three uncertain MARKET-PRICE inputs from uniform priors (Latin Hypercube),
solves the (now linear) model for each draw, and writes one CSV row per draw with
the sampled inputs, key outputs, and feasibility status. Run once per structural
cell (see below); the three discrete structural axes are fixed per run.

Sampled inputs -- the three market prices (uniform over [lo, hi]):
    ng_cost      n5_cost_NG       $/MMBtu     [5,   25]
    h2_end_cost  ng_cost_h2_end   $/ton       [1000,4500]
    ccs_end_cost n10_ccs_cost_end $/ton       [25,  125]

Discrete STRUCTURAL axes (policy/deployment levers, fixed per run -> one "cell"):
    NG-availability scenario  {normal, shock, optimistic}        via MC_SCENARIO
    scrap-availability regime {starved, low, modest, optimistic} via MC_SCRAP_REGIME
    H2-DRI start year         {e.g. 2030, 2036, 2039}            via MC_H2YEAR
The full ensemble is the product of the three axes (e.g. 3 x 4 x 3 = 36 cells),
each an MC of N draws over the market prices.
"""
import os, sys, csv, time
import numpy as np
from scipy.stats import qmc
from amplpy import AMPL, add_to_path
import ampl_module_base

# Resolve AMPL binary from installed package; AMPL_DIR env var overrides if needed.
_default_ampl_dir = os.path.join(os.path.dirname(ampl_module_base.__file__), "bin")
add_to_path(os.environ.get("AMPL_DIR", _default_ampl_dir))

# ----------------------------- configuration -----------------------------
PROJECT      = os.path.dirname(os.path.abspath(__file__))
N_SAMPLES    = int(os.environ.get("MC_N", "20000"))
SEED         = int(os.environ.get("MC_SEED", "20260624"))
SCENARIO     = "normal"                                          # NG availability fixed; not a structural axis
SCRAP_REGIME = os.environ.get("MC_SCRAP_REGIME", "modest")      # starved|low|modest|optimistic
H2YEAR       = int(os.environ.get("MC_H2YEAR", "2030"))         # H2-DRI start year (discrete axis)
AVG_EMI      = float(os.environ.get("MC_AVG_EMI", "1.6"))       # cumulative avg-emissions target (tCO2/tCS)
RAMP         = float(os.environ.get("MC_RAMP", "0.15"))         # additive production ramp slab (frac of 2025 level/yr)
GRID_EF      = os.environ.get("MC_GRID_EF", "moderate_re")      # bau|moderate_re|aggressive_re
GRID         = os.environ.get("MC_GRID", "")   # "nH2,nCCS,nNG" -> deterministic price grid; "" -> LHS
OUT_CSV      = os.path.join(PROJECT, os.environ.get("MC_OUT", "mc_results.csv"))
TRAJ_OUT     = os.environ.get("MC_TRAJ_OUT", "")   # if set, also write a year-by-year trajectory CSV

# year-indexed entities archived for the full-trajectory store (one batched
# get_data call per solve -> a 26-year x len rows DataFrame).
TRAJ_ENTS = ["total_steel", "steel_bof", "steel_scrap_eaf", "coaldri_output",
             "ngdri_output", "h2dri_output", "total_cost", "total_emissions", "total_ccs"]

SCEN_FILE    = "scenarios/ng_avail_normal.mod"
GRID_EF_FILE = {"bau":           "scenarios/grid_ef_bau.mod",
                "moderate_re":   "scenarios/grid_ef_moderate_re.mod",
                "aggressive_re": "scenarios/grid_ef_aggressive_re.mod"}[GRID_EF]

# Scrap-availability regime: discrete structural axis (see scrap_*.mod). Common
# 35 Mt 2025 base; regimes differ
# by growth: starved 0%, low 2%, modest 4%, optimistic 6% per year.
SCRAP_FILE = {"starved":"scenarios/scrap_starved.mod",
              "low":"scenarios/scrap_low.mod",
              "modest":"scenarios/scrap_modest.mod",
              "optimistic":"scenarios/scrap_optimistic.mod"}[SCRAP_REGIME]

# uniform prior bounds: [ng_cost, h2_end_cost, ccs_end_cost]
LO = np.array([5.0,   1000.0, 25.0])
HI = np.array([25.0,  4500.0, 125.0])
NAMES = ["ng_cost", "h2_end_cost", "ccs_end_cost"]

# ----------------------- build per-draw model script ----------------------
with open(os.path.join(PROJECT, "template.mod")) as fh:
    TEMPLATE = fh.read()
# drop the human-readable report includes (we extract values via the API instead)
TEMPLATE = "\n".join(l for l in TEMPLATE.splitlines()
                     if "include yreport.mod" not in l and "include report.mod" not in l)
# faster, bounded solves for the sweep (linear MILP => sub-second; cap as safety)
TEMPLATE = TEMPLATE.replace(
    "option gurobi_options 'Threads=5 TimeLimit=600 mipgap=0.002';",
    f"option gurobi_options 'Threads={os.environ.get('MC_THREADS','10')} "
    f"TimeLimit=120 mipgap={os.environ.get('MC_MIPGAP','0.0001')}';")

def model_for(ng, h2end, ccs, h2year):
    s = TEMPLATE
    for tok, val in (("NGVAL", ng), ("H2ENDVAL", h2end), ("H2YEARVAL", h2year),
                     ("CCSVAL", ccs), ("AVGEMIVAL", AVG_EMI), ("RAMPVAL", RAMP),
                     ("SCRAPREGIMEFILE", SCRAP_FILE),
                     ("NGAVAILFILE", SCEN_FILE), ("GRIDEFFILE", GRID_EF_FILE)):
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

FIELDS = (["draw"] + NAMES + ["h2_start_year","scrap_regime","grid_ef_scenario","avg_emi_target","status",
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
def build_inputs():
    """Return (X, mode) where X is an (n,3) array of [ng, h2, ccs] price points.

    Two modes over the three market prices (NG/H2/CCS cost); the discrete
    structural axes (H2 year, NG availability, scrap regime) are fixed per run.
      - MC_GRID="nH2,nCCS,nNG": deterministic asymmetric grid (a reweightable
        "generator" -- denser on the more sensitive axes, H2 > CCS > NG).
      - default: 3-dim Latin Hypercube of N_SAMPLES draws.
    """
    if GRID:
        nh2, nccs, nng = (int(x) for x in GRID.split(","))
        h2v  = np.linspace(LO[1], HI[1], nh2)
        ccsv = np.linspace(LO[2], HI[2], nccs)
        ngv  = np.linspace(LO[0], HI[0], nng)
        NG, H2, CCS = np.meshgrid(ngv, h2v, ccsv, indexing="ij")
        X = np.column_stack([NG.ravel(), H2.ravel(), CCS.ravel()])
        # optional contiguous slice for parallel chunking (price grid is fixed,
        # so any slice is reproducible and the chunks tile the full grid exactly)
        start = int(os.environ.get("MC_GRID_START", "0"))
        end   = int(os.environ.get("MC_GRID_END", str(len(X))))
        total = len(X)
        X = X[start:end]
        return X, f"grid {nh2}x{nccs}x{nng} = {total} pts, slice [{start}:{end}]"
    U = qmc.LatinHypercube(d=3, seed=SEED).random(n=N_SAMPLES)
    return qmc.scale(U, LO, HI), f"LHS n={N_SAMPLES} (seed {SEED})"


def main():
    os.chdir(PROJECT)  # so the model's relative include paths resolve
    X, mode = build_inputs()
    n = len(X)
    print(f"cell: scrap={SCRAP_REGIME} H2yr={H2YEAR} grid_ef={GRID_EF} avg_emi={AVG_EMI}  |  {mode}", flush=True)
    RESET_EVERY = 2000   # recreate the AMPL process periodically (memory hygiene)
    ampl = AMPL()
    n_ok = n_inf = n_err = 0
    t0 = time.time()
    traj_fh = open(TRAJ_OUT, "w", newline="") if TRAJ_OUT else None
    traj_w = None
    if traj_fh is not None:
        traj_w = csv.writer(traj_fh)
        traj_w.writerow(["ng_cost", "h2_end_cost", "ccs_end_cost", "year"] + TRAJ_ENTS)
    n_retry = 0
    with open(OUT_CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader()
        for i in range(n):
            ng, h2end, ccs = X[i]
            if i and i % RESET_EVERY == 0:
                ampl.close(); ampl = AMPL()
            row = {"draw": i, "ng_cost": ng, "h2_end_cost": h2end,
                   "ccs_end_cost": ccs,
                   "h2_start_year": H2YEAR, "scrap_regime": SCRAP_REGIME,
                   "grid_ef_scenario": GRID_EF, "avg_emi_target": AVG_EMI}
            td = time.time()
            try:
                ampl.eval(model_for(ng, h2end, ccs, H2YEAR))
                status = ampl.get_value("solve_result")
                if status == "infeasible":
                    # Feasibility is price-independent (prices enter only the
                    # objective); an "infeasible" report in a frontier-feasible
                    # cell is a stale-instance artifact -> retry on a fresh AMPL.
                    ampl.close(); ampl = AMPL()
                    ampl.eval(model_for(ng, h2end, ccs, H2YEAR))
                    status = ampl.get_value("solve_result")
                    n_retry += 1
                row["status"] = status
                if status == "solved":
                    row.update(extract(ampl)); n_ok += 1
                    if traj_w is not None:
                        tdf = ampl.get_data(*TRAJ_ENTS).to_pandas()
                        for yr, vr in tdf.iterrows():
                            traj_w.writerow([ng, h2end, ccs, int(yr)]
                                            + [float(vr[e]) for e in TRAJ_ENTS])
                else:
                    n_inf += 1
            except Exception as e:
                row["status"] = "error:" + str(e).splitlines()[0][:60]; n_err += 1
            row["solve_s"] = round(time.time() - td, 3)
            w.writerow(row)
            if (i + 1) % 200 == 0:
                fh.flush()
                if traj_fh is not None:
                    traj_fh.flush()
                el = time.time() - t0
                print(f"{i+1}/{n}  ok={n_ok} infeas={n_inf} err={n_err} retry={n_retry}  "
                      f"{el:.0f}s  ({el/(i+1):.2f}s/draw, ETA {el/(i+1)*(n-i-1)/60:.0f} min)",
                      flush=True)
    if traj_fh is not None:
        traj_fh.close()
    print(f"DONE  ok={n_ok} infeasible={n_inf} error={n_err} retry={n_retry}  "
          f"total {time.time()-t0:.0f}s  -> {OUT_CSV}")

if __name__ == "__main__":
    main()
