# =====================================================================
# structural-sensitivity/abatement study: post-solve accounting and CSV
# rows (one per year -- ALL runs, baseline included, append to the SAME
# file so the abatement decomposition can diff scenario-vs-baseline
# year-by-year).
#
# Included AFTER solve. Appends 26 rows (2025-2050) to
#   scenarios/structural-sensitivity/abatement/results/abatement_yearly.csv
#
# The driver sets `REGIME` (run label: Baseline, EF1.6, EF1.8, S4, S8, RL,
# RH) before including this file. e_h2y[t] evaluates to 0 automatically on
# the baseline run (h2dri_output[t] = 0 there), so one block serves both.
# =====================================================================

param e_h2y{T};
let {t in T} e_h2y[t] :=
    scope1_h2dri[t]
  + n9_grid_ef[t] * ( h2dri_power_in[t] + pellets_power_h2dri[t]
      + (if dri_eaf_steel_out[t] > 0
         then h2dri_output[t]/dri_eaf_steel_out[t] else 0) * eaf_power_in[t] );

# Route-level GROSS emissions (pre-CCS-credit) for consistent process +
# electricity attribution in the abatement decomposition.
param fc{t in T} default 0;
param fn{t in T} default 0;
param gbf{t in T} default 0;
param gcd{t in T} default 0;
param gng{t in T} default 0;
param gsc{t in T} default 0;
let {t in T} fc[t] := if dri_eaf_steel_out[t] > 1e-6 then coaldri_output[t]/dri_eaf_steel_out[t] else 0;
let {t in T} fn[t] := if dri_eaf_steel_out[t] > 1e-6 then ngdri_output[t]/dri_eaf_steel_out[t] else 0;
let {t in T} gbf[t] := scope1_bf[t]
  + n9_grid_ef[t] * max(coke_power_in[t] + sinter_power_in[t] + bf_power_in[t]
        - (cdq_power_out[t] + sinterwaste_power_out[t] + bf_trt_out[t]), 0);
let {t in T} gcd[t] := scope1_cdri[t]
  + n9_grid_ef[t] * (coaldri_power_in[t] + fc[t]*eaf_power_in[t] + pellets_power_coaldri[t]);
let {t in T} gng[t] := scope1_ngdri[t]
  + n9_grid_ef[t] * (ngdri_power_in[t] + fn[t]*eaf_power_in[t] + pellets_power_ngdri[t]);
let {t in T} gsc[t] := scope1_scrapeaf[t] + n9_grid_ef[t] * scrap_eaf_power_in[t];

# CSV row per year: run,year,solve_result,total_steel,steel_bof,coaldri,
# ngdri,h2dri,scrap_eaf,scope1,scope2,ccs,total_emissions,e_h2,bof_scrap,
# cdri_scrap,ngdri_scrap,h2dri_scrap,scrapeaf_scrap,scrap_limit,total_cost,
# whr_power,gross_bf,gross_cdri,gross_ngdri,gross_scrapeaf
for {t in T} {
    printf "%s,%d,%s,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f\n",
        REGIME, t, solve_result,
        total_steel[t], steel_bof[t], coaldri_output[t], ngdri_output[t],
        h2dri_output[t], steel_scrap_eaf[t],
        scope1_emissions[t], scope2_emissions[t], total_ccs[t], total_emissions[t],
        e_h2y[t],
        bof_scrap_in[t], coaldri_scrap_in[t], ngdri_scrap_in[t],
        h2dri_scrap_in[t], scrap_eaf_scrap_in[t], n8_scrap_limit[t],
        total_cost[t],
        whr_power_generated[t],
        gbf[t], gcd[t], gng[t], gsc[t]
        >> "scenarios/structural-sensitivity/abatement/results/abatement_yearly.csv";
}
printf "ABATEMENT %s -> %s\n", REGIME, solve_result;
