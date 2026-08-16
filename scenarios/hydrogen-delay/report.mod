# =====================================================================
# Hydrogen-delay study: post-solve accounting and CSV row.
#
# Included AFTER solve. Appends one row to
#   scenarios/hydrogen-delay/results/h2delay_summary.csv
# whose column order is the contract the plotting scripts expect --
# if you change it, change the header in run.py to match.
#
# The driver sets `REGIME` (the ramp-level label) before including this file.
# =====================================================================

# H2 emission reduction in 2050 -- identical block to import-dependence/scrap.
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

# CSV row -- column order matches the old h2delay_summary.csv contract
# (avg_emi, ramp_label, cap_add_common, h2_ref_cap, ng_h2_start_year,
#  solve_result, cap_h2dri_2050, total_ccs_2050, lcop, red_h2_2050).
printf "%.2f,%s,%.0f,%.0f,%d,%s,%.0f,%.0f,%.2f,%.0f\n",
    avg_emi,
    REGIME,
    cap_add_common,
    h2_ref_cap,
    ng_h2_start_year,
    solve_result,
    cap_h2dri[2050],
    total_ccs[2050],
    (if (sum{t in T} discount_factor[t]*total_steel[t]) > 0
        then (sum{t in T} discount_factor[t]*total_cost[t])
           / (sum{t in T} discount_factor[t]*total_steel[t]) else 0),
    red_h2_2050
    >> "scenarios/hydrogen-delay/results/h2delay_summary.csv";

printf "H2DELAYRESULT EF=%.2f ramp=%s h2start=%d -> %s\n",
    avg_emi, REGIME, ng_h2_start_year, solve_result;
