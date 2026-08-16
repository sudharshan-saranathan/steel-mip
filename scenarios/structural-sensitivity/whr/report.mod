# =====================================================================
# structural-sensitivity/whr study: post-solve accounting and CSV row.
#
# Included AFTER solve. Appends one row to
#   scenarios/structural-sensitivity/whr/results/whr_summary.csv
#
# The driver sets `MODE_LABEL` (symbolic: "integrated"/"boiler-only")
# before including this file.
# =====================================================================

param pv_captured;      # PV-weighted captured CO2 (t)
param eff_capture_cost; # $/tCO2, incl. foregone WHR power value
param cum_captured;     # plain cumulative captured CO2 (t)
param boiler_steam_sh;  # share of regen steam that came from the boiler

let pv_captured := sum{t in T} discount_factor[t]*total_ccs[t];
let eff_capture_cost :=
    (sum{t in T} discount_factor[t]*
        ( cost_ccs[t]
        + whr_gas_to_steam[t]*277.78*n9_eta*ng_cost_power[t] ))
    / max(pv_captured, 1);
let cum_captured := sum{t in T} total_ccs[t];
let boiler_steam_sh :=
    (sum{t in T} ccs_steam_boiler[t])
    / max(sum{t in T} (ccs_steam_whr[t] + ccs_steam_boiler[t]), 1);

# CSV row: theta, mode, whr_integration, solve_result, eff_capture_cost,
# cum_captured, ccs_2050, boiler_steam_share, lcop
printf "%.2f,%s,%.0f,%s,%.2f,%.0f,%.0f,%.4f,%.2f\n",
    theta_ccs,
    MODE_LABEL,
    whr_ccs_integration,
    solve_result,
    eff_capture_cost,
    cum_captured,
    total_ccs[2050],
    boiler_steam_sh,
    (if (sum{t in T} discount_factor[t]*total_steel[t]) > 0
        then (sum{t in T} discount_factor[t]*total_cost[t])
           / (sum{t in T} discount_factor[t]*total_steel[t]) else 0)
    >> "scenarios/structural-sensitivity/whr/results/whr_summary.csv";

printf "WHRRESULT theta=%.2f mode=%s -> %s (eff cost %.2f)\n",
    theta_ccs, MODE_LABEL, solve_result, eff_capture_cost;
