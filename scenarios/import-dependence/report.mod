# =====================================================================
# Import-dependence study: post-solve accounting and CSV row.
#
# Included AFTER solve. Appends one row to
#   scenarios/import-dependence/results/impdep_summary.csv
# whose column order is the contract the plotting scripts expect --
# if you change it, change the header in run.py to match.
#
# The driver sets `REGIME` before including this file.
# =====================================================================

# REGIME is declared in study.mod and set by the driver before this include.

# Import bills -------------------------------------------------------
param ng_domestic    := 0.5 * 5348550;                     # flat domestic NG to steel, t/yr (50% of 2025 cap)
param ccoal_domestic{t in T} := 6000000 * 1.075^(t-2025);  # domestic coking coal, +7.5%/yr (FY18-25 CAGR)

param cum_ccoal_bill;
param cum_ng_import;
param cum_ng_bill;

let cum_ccoal_bill := sum{t in T} max(0, coking_coal_in[t] - ccoal_domestic[t]) * ng_cost_ccoal;
let cum_ng_import  := sum{t in T} max(0, ngdri_ng_in[t] - ng_domestic);
let cum_ng_bill    := sum{t in T} max(0, ngdri_ng_in[t] - ng_domestic) * n5_cost_NG[t] * 50;

# H2 emission reduction in 2050 --------------------------------------
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

# CSV row ------------------------------------------------------------
printf "%s,%d,%s,%.0f,%.0f,%.0f,%.0f,%.0f,%.2f,%.4f,%.4f,%.4f,%.4f,%.4f,%.0f,%.0f\n",
    REGIME,
    ng_h2_start_year,
    solve_result,
    cum_ccoal_bill,
    cum_ng_bill,
    cum_ccoal_bill + cum_ng_bill,
    cum_ng_import,
    sum{t in T} total_emissions[t],
    (if (sum{t in T} discount_factor[t]*total_steel[t]) > 0
        then (sum{t in T} discount_factor[t]*total_cost[t])
           / (sum{t in T} discount_factor[t]*total_steel[t]) else 0),
    steel_bof[2050]/total_steel[2050],
    coaldri_output[2050]/total_steel[2050],
    ngdri_output[2050]/total_steel[2050],
    h2dri_output[2050]/total_steel[2050],
    steel_scrap_eaf[2050]/total_steel[2050],
    red_h2_2050,
    total_ccs[2050]
    >> "scenarios/import-dependence/results/impdep_summary.csv";

printf "IMPDEPRESULT %s h2=%d -> %s (bill %.1f B$)\n",
    REGIME, ng_h2_start_year, solve_result, (cum_ccoal_bill+cum_ng_bill)/1e9;
