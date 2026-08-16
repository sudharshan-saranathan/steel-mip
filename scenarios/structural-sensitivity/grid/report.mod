# =====================================================================
# structural-sensitivity/grid study: post-solve accounting and CSV row.
#
# Included AFTER solve. Appends one row to
#   scenarios/structural-sensitivity/grid/results/grid_summary.csv
# Reconstructed from the old (not-in-repo) Plots/Grid/gridresult.mod --
# column order matches the old grid_summary.csv contract documented in
# docs/HANDOFF.md; if you change it, change the header in run.py to match.
# =====================================================================

param pv_avg_cost_g;
param ccs_frac_2050_g;

let pv_avg_cost_g :=
    (if (sum{t in T} discount_factor[t]*total_steel[t]) > 0
        then (sum{t in T} discount_factor[t]*total_cost[t])
           / (sum{t in T} discount_factor[t]*total_steel[t]) else 0);

let ccs_frac_2050_g :=
    (if (co2_capturable_bf[2050]+co2_capturable_cdri[2050]+co2_capturable_ngdri[2050]) > 0
        then total_ccs[2050]
           / (co2_capturable_bf[2050]+co2_capturable_cdri[2050]+co2_capturable_ngdri[2050])
        else 0);

# CSV row: h2_start, scrap_rate, grid_ef_end, theta_grid, tariff_2050,
# solve_result, avg_emis, pv_avg_cost, h2_share_2050, ccs_frac_2050,
# scrapeaf_share_2050
printf "%d,%.4f,%.6f,%.4f,%.4f,%s,%.4f,%.2f,%.4f,%.4f,%.4f\n",
    ng_h2_start_year,
    n8_scrap_rate,
    grid_ef_target,
    theta_grid,
    ng_cost_power[2050],
    solve_result,
    (if (sum{t in T} total_steel[t]) > 0
        then (sum{t in T} total_emissions[t]) / (sum{t in T} total_steel[t]) else 0),
    pv_avg_cost_g,
    (if total_steel[2050] > 0 then h2dri_output[2050]/total_steel[2050] else 0),
    ccs_frac_2050_g,
    (if total_steel[2050] > 0 then steel_scrap_eaf[2050]/total_steel[2050] else 0)
    >> "scenarios/structural-sensitivity/grid/results/grid_summary.csv";

printf "GRIDRESULT h2=%d scrap=%.2f grid_ef=%.6f -> %s\n",
    ng_h2_start_year, n8_scrap_rate, grid_ef_target, solve_result;
