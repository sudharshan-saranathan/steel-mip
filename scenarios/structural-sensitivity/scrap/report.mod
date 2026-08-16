# =====================================================================
# structural-sensitivity/scrap study: post-solve accounting and CSV row.
#
# Included AFTER solve. Appends one row to
#   scenarios/structural-sensitivity/scrap/results/scrap_summary.csv
# =====================================================================

# H2 emission reduction in 2050 -- identical block to import-dependence/
# hydrogen-delay.
param e_h2_2050;
param red_h2_2050;

let e_h2_2050 :=
    scope1_h2dri[2050]
  + n9_grid_ef[2050] * ( h2dri_power_in[2050] + pellets_power_h2dri[2050]
      + (if dri_eaf_steel_out[2050] > 0
         then h2dri_output[2050]/dri_eaf_steel_out[2050] else 0) * eaf_power_in[2050] );

let red_h2_2050 :=
    if h2dri_output[2050] > 1 and total_steel[2050] > h2dri_output[2050]
    then h2dri_output[2050]
         * (scope1_emissions[2050] + scope2_emissions[2050] - e_h2_2050)
         / (total_steel[2050] - h2dri_output[2050])
         - e_h2_2050
    else 0;

# CSV row: avg_emi, scrap_rate, solve_result, h2dri_cap_2050, ccs_2050,
# red_h2_2050, lcop, scrap_use_2050, scrap_limit_2050, scrapeaf_share_2050
printf "%.2f,%.2f,%s,%.0f,%.0f,%.0f,%.2f,%.0f,%.0f,%.4f\n",
    avg_emi,
    n8_scrap_rate,
    solve_result,
    cap_h2dri[2050],
    total_ccs[2050],
    red_h2_2050,
    (if (sum{t in T} discount_factor[t]*total_steel[t]) > 0
        then (sum{t in T} discount_factor[t]*total_cost[t])
           / (sum{t in T} discount_factor[t]*total_steel[t]) else 0),
    bof_scrap_in[2050] + eaf_scrap_in[2050] + scrap_eaf_scrap_in[2050],
    n8_scrap_limit[2050],
    (if steel_scrap_eaf[2050] > 0 and total_steel[2050] > 0
        then steel_scrap_eaf[2050]/total_steel[2050] else 0)
    >> "scenarios/structural-sensitivity/scrap/results/scrap_summary.csv";

printf "SCRAPRESULT EF=%.2f scrap=%.2f -> %s\n", avg_emi, n8_scrap_rate, solve_result;
