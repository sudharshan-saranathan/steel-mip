# ------------------------------------------------------------------
# Post-solve recovery of the DRI route fractions.
# f_cdri / f_ngdri are no longer optimization variables (linearization: the route
# *outputs* are the decisions). They are reconstructed here from the solved route
# outputs purely for reporting:  f_route = route_output / dri_eaf_steel_out.
# ------------------------------------------------------------------
param f_cdri{t in T} default 0;
param f_ngdri{t in T} default 0;
let {t in T} f_cdri[t]  := if dri_eaf_steel_out[t] > 1e-6 then coaldri_output[t]/dri_eaf_steel_out[t] else 0;
let {t in T} f_ngdri[t] := if dri_eaf_steel_out[t] > 1e-6 then ngdri_output[t]/dri_eaf_steel_out[t] else 0;

printf "\nAVERAGE STEEL PRODUCTION COST (2025–2050): %.2f $/ton\n",
    if sum{t in T} total_steel[t] > 0 then
        ( sum{t in T} discount_factor[t] * total_cost[t] )
      / ( sum{t in T} discount_factor[t] * total_steel[t] )
    else 0;
       
printf "2050: Cost = %.3f $/t CS, Emissions = %.3f tCO2/t CS\n",
    if total_steel[2050] > 0 then
        total_cost[2050] / total_steel[2050]
    else 0,
    if total_steel[2050] > 0 then
        total_emissions[2050] / total_steel[2050]
    else 0;      
       
printf "\nCO2 CAPTURED PER TON STEEL OVERALL (2025–2050): %.3f\n",
       if (sum{t in T} total_steel[t]) > 0 then
           ( sum{t in T} total_ccs[t] )
         / ( sum{t in T} total_steel[t] )
       else 0;       
       
printf "\n%-20s %-20s\n", "Route", "Fraction";

printf "%-20s %10.4f\n", "BF-BOF", f_bof[2050];

printf "%-20s %10.4f\n", "Coal DRI-EAF", f_cdri[2050] * f_eaf[2050];

printf "%-20s %10.4f\n", "NG DRI-EAF", f_ngdri[2050] * f_eaf[2050];

printf "%-20s %10.4f\n", "H2 DRI-EAF", 
    (1 - f_cdri[2050] - f_ngdri[2050]) * f_eaf[2050];

printf "%-20s %10.4f\n", "Scrap-EAF", 
    1 - f_bof[2050] 
      - f_cdri[2050] * f_eaf[2050] 
      - f_ngdri[2050] * f_eaf[2050] 
      - (1 - f_cdri[2050] - f_ngdri[2050]) * f_eaf[2050];

printf "\nTOTAL H2 USED IN H2-DRI (2025–2050): %.3f million units\n",
       ( sum{t in T} steel_eaf[t] * (1 - f_cdri[t] - f_ngdri[t]) ) / 1e6;
printf "\n";

printf "\n%-6s %-20s %-37s %-18s %-10s",
       "YEAR",
       "BF-BOF (t/f)",
       "DRI-EAF (t/f split)",
       "Scrap-EAF (t/f)",
       "Total";

printf "\n%-6s %-12s %-15s %-15s %-20s %-10s %-10s",
       "", "", "Coal", "NG", "H2", "", "";

for {t in T} {
    printf "\n%4d %8.0f/%5.2f %8.0f/%5.2f %8.0f/%5.2f %8.0f/%5.2f %10.0f/%5.2f %10.0f",
        t,
        steel_bof[t], f_bof[t],                                  # BF-BOF
        steel_eaf[t] * f_cdri[t], f_cdri[t] * f_eaf[t],                            # Coal DRI
        steel_eaf[t] * f_ngdri[t] , f_ngdri[t] * f_eaf[t],                             # NG DRI
        steel_eaf[t] * (1 - f_cdri[t] - f_ngdri[t]), (1 - f_cdri[t] - f_ngdri[t]) * f_eaf[t],            # H2 DRI
        steel_scrap_eaf[t], 1 - f_bof[t] - f_cdri[t] * f_eaf[t] - f_ngdri[t] * f_eaf[t] - (1 - f_cdri[t] - f_ngdri[t]) * f_eaf[t],            # Scrap-EAF
        total_steel[t];                                          # Total
}

printf "\n";

# TABLE 2: CCS fractions and captured amounts


printf "\n%-6s %-20s %-20s %-20s %-15s %-12s",
       "YEAR",
       "BF-BOF CCS (t/f)",
       "Coal-DRI CCS (t/f)",
       "NG-DRI CCS (t/f)",
       "Total CCS",
       "CCS Fraction";


for {t in T} {
    printf "\n%4d %10.0f/%5.2f %10.0f/%5.2f %10.0f/%5.2f %20.0f %12.3f",
        t,

        # BF–BOF CCS and share
        ccs_bf[t],
        if total_ccs[t] > 0 then ccs_bf[t] / steel_bof[t] else 0,

        # Coal–DRI CCS and share
        ccs_cdri[t],
        if total_ccs[t] > 0 then ccs_cdri[t] / (steel_eaf[t] * f_cdri[t]) else 0,

        # NG–DRI CCS and share
        ccs_ngdri[t],
        if total_ccs[t] > 0 then ccs_ngdri[t] / (steel_eaf[t] * f_ngdri[t])  else 0,

        # Total CCS
        total_ccs[t],

        # Capture rate relative to emissions
        if total_emissions[t] + total_ccs[t] > 0 then
            total_ccs[t] / (total_emissions[t] + total_ccs[t])
        else 0;
}



printf "\n";

printf "\nTOTAL FRACTION OF CO2 CAPTURED (2025–2050): %.3f\n",
       if (sum{t in T} total_emissions[t]) > 0 then
           ( sum{t in T} total_ccs[t] )
         / ( sum{t in T} total_emissions[t] + ( sum{t in T}total_ccs[t]) )
       else 0;


printf "\n";

printf "\nTOTAL FRACTION OF DIRECT CO2 CAPTURED (2025–2050): %.3f\n",
       if (sum{t in T} scope1_emissions[t]) > 0 then
           ( sum{t in T} total_ccs[t] )
         / ( sum{t in T} scope1_emissions[t] )
       else 0;


printf "\n";

printf "\n%-6s %-25s %-25s",
       "YEAR",
       "Avg Emissions (tCO2/ton)",
       "Avg Cost ($/ton)";

for {t in T} {
    printf "\n%4d %25.3f %25.3f",
        t,
        if total_steel[t] > 0 then
            total_emissions[t] / total_steel[t]
        else 0,
        if total_steel[t] > 0 then
            total_cost[t] / total_steel[t]
        else 0;
}

printf "\n";


printf "\nAVG (NON-LEVELIZED) STEEL PRODUCTION COST (2025–2050): %.2f $/ton\n",
       if sum{t in T} total_steel[t] > 0 then
           ( sum{t in T} total_cost[t] )
         / ( sum{t in T} total_steel[t] )
       else 0;

printf "\n";






# route costs per year

printf "\n%-6s %-12s %-15s %-15s %-15s %-15s",
       "YEAR",
       "BF-BOF ($/t)",
       "Coal DRI-EAF ($/t)",
       "NG DRI-EAF ($/t)",
       "H2 DRI-EAF ($/t)",
       "Scrap-EAF ($/t)";

for {t in T} {
    printf "\n%4d %12.2f %15.2f %15.2f %15.2f %15.2f",
        t,

        # BF-BOF
        if steel_bof[t] > 0 then
           (carbon_tax*scope1_bf[t] + n10_ccs_cost[t]*ccs_bf[t]
           + cost_bf[t] + cost_bof[t] + cost_cokeov[t] + cost_sinter[t] + cost_pellet_bf[t]
           + (labor_cost + maintenance_cost + other_opex)*steel_bof[t]
           - (wasteheat_bf_bof[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] *ng_credit_power 
           - wasteheat_bf_bof[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] * n9_whr_capex
           - wasteheat_bf_bof[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] * n9_whr_opex))
           / steel_bof[t]
        else 0,

        # Coal DRI-EAF
        if steel_eaf[t]*f_cdri[t] > 0 then
           (carbon_tax*scope1_cdri[t] + n10_ccs_cost[t]*ccs_cdri[t]
           + cost_coaldri[t] + f_cdri[t]*cost_eaf[t] + cost_pellet_coaldri[t]
           + (labor_cost + maintenance_cost + other_opex)*(steel_eaf[t]*f_cdri[t])
           - (wasteheat_eaf[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] *ng_credit_power 
           - wasteheat_eaf[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] * n9_whr_capex
           - wasteheat_eaf[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] * n9_whr_opex) * f_cdri[t])/ (steel_eaf[t]*f_cdri[t])
        else 0,

        # NG DRI-EAF
        if steel_eaf[t]*f_ngdri[t] > 0 then
           (carbon_tax*scope1_ngdri[t] + n10_ccs_cost[t]*ccs_ngdri[t]
           + cost_ngdri[t] + f_ngdri[t]*cost_eaf[t] + cost_pellet_ngdri[t]
           + (labor_cost + maintenance_cost + other_opex)*(steel_eaf[t]*f_ngdri[t])
           - (wasteheat_eaf[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] *ng_credit_power 
           - wasteheat_eaf[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] * n9_whr_capex
           - wasteheat_eaf[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] * n9_whr_opex) * f_ngdri[t])
           / (steel_eaf[t]*f_ngdri[t])
        else 0,

        # H2 DRI-EAF
        if t >= ng_h2_start_year && steel_eaf[t]*(1-f_cdri[t]-f_ngdri[t]) > 0 then
           (carbon_tax*scope1_h2dri[t] + cost_h2dri[t]
           + (1-f_cdri[t]-f_ngdri[t])*cost_eaf[t] + cost_pellet_h2dri[t]
           + (labor_cost + maintenance_cost + other_opex)*(steel_eaf[t]*(1-f_cdri[t]-f_ngdri[t]))
           - (wasteheat_eaf[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] *ng_credit_power 
           - wasteheat_eaf[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] * n9_whr_capex
           - wasteheat_eaf[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] * n9_whr_opex) * (1- f_cdri[t] - f_ngdri[t]))
           / (steel_eaf[t]*(1-f_cdri[t]-f_ngdri[t]))
        else 0,

        # Scrap-EAF
        if steel_scrap_eaf[t] > 0 then
           (carbon_tax*scope1_scrapeaf[t] + cost_scrap_eaf[t]
           + (labor_cost + maintenance_cost + other_opex)*steel_scrap_eaf[t]
           - (scrap_eaf_wasteheat[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] *ng_credit_power 
           - scrap_eaf_wasteheat[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] * n9_whr_capex
           - scrap_eaf_wasteheat[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] * n9_whr_opex))
           / steel_scrap_eaf[t]
        else 0;
}


# route emissions per year


printf "\n%-6s %-12s %-15s %-15s %-15s %-15s",
       "YEAR",
       "BF-BOF (tCO2/t)",
       "Coal DRI-EAF (tCO2/t)",
       "NG DRI-EAF (tCO2/t)",
       "H2 DRI-EAF (tCO2/t)",
       "Scrap-EAF (tCO2/t)";

for {t in T} {

    printf "\n%4d %12.3f %15.3f %15.3f %15.3f %15.3f",
        t,

        # ------------------ BF-BOF ------------------
        if steel_bof[t] > 0 then
            (scope1_bf[t] 
             + n9_grid_ef[t] * max(coke_power_in[t] + sinter_power_in[t] + bf_power_in[t]
                                    - (cdq_power_out[t] + sinterwaste_power_out[t] + bf_trt_out[t]),
                                    0)
             - ccs_bf[t])
            / steel_bof[t]
        else 0,

        # ------------------ Coal DRI-EAF ------------------
        if steel_eaf[t]*f_cdri[t] > 0 then
            (scope1_cdri[t]
             + n9_grid_ef[t] * (coaldri_power_in[t] + f_cdri[t]*eaf_power_in[t] + pellets_power_coaldri[t])
             - ccs_cdri[t])
            / (steel_eaf[t]*f_cdri[t])
        else 0,

        # ------------------ NG DRI-EAF ------------------
        if steel_eaf[t]*f_ngdri[t] > 0 then
            (scope1_ngdri[t]
             + n9_grid_ef[t] * (ngdri_power_in[t] + f_ngdri[t]*eaf_power_in[t] + pellets_power_ngdri[t])
             - ccs_ngdri[t])
            / (steel_eaf[t]*f_ngdri[t])
        else 0,

        # ------------------ H2 DRI-EAF ------------------
        if t >= ng_h2_start_year && steel_eaf[t]*(1-f_cdri[t]-f_ngdri[t]) > 0 then
            (( eaf_coal_in[t] * (1- f_cdri[t]-f_ngdri[t]) * 0.110*24+ eaf_lime_in[t] * (1- f_cdri[t]-f_ngdri[t]) * 0.44 + eaf_electrode_in[t] *  (1- f_cdri[t]-f_ngdri[t]) * 6)
             + n9_grid_ef[t] * ((1-f_cdri[t]-f_ngdri[t])*eaf_power_in[t] + pellets_power_h2dri[t] + h2dri_power_in[t]))
            / (steel_eaf[t]*(1-f_cdri[t]-f_ngdri[t]))
        else 0,

        # ------------------ Scrap-EAF ------------------
        if steel_scrap_eaf[t] > 0 then
            (scope1_scrapeaf[t]
             + n9_grid_ef[t] * scrap_eaf_power_in[t])
            / steel_scrap_eaf[t]
        else 0;
}

printf "\n";

printf "\n";
       