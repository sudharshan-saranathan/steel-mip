# Scope 1 Emissions (Blast furnace)
s.t. scope1_blastf{t in T}:
    (coking_coal_in[t] * ef_ccoal + bf_coalpci_in[t] * ef_pci
     + (sinter_lime_in[t] + bf_lime_in[t] + bof_lime_in[t]) * ef_lime)
    - scope1_bf[t] = 0;                      # eq105


# Scope 1 Emissions (Coal DRI)
s.t. scope1_coaldri{t in T}:
      (coaldri_coal_in[t] * ef_ncoal + (n7_cs*coaldri_output[t]) * ef_ncoal
      + (n7_ls*coaldri_output[t]) * ef_lime)  - scope1_cdri[t] = 0;         # eq106


# Scope 1 Emissions (NG DRI)
s.t. scope1_natgasdri{t in T}:
      (ngdri_ng_in[t] * ef_ng + (n7_cs*ngdri_output[t]) * ef_ncoal
      + (n7_ls*ngdri_output[t]) * ef_lime) - scope1_ngdri[t] = 0;         # eq107

# Scope 1 Emissions (H2 DRI)
s.t. scope1_h2dri_{t in T}:
      ( (n7_cs*h2dri_output[t]) * ef_ncoal
      + (n7_ls*h2dri_output[t]) * ef_lime) - scope1_h2dri[t] = 0;        # eq108

# Scope 1 Emissions (scrap EAF)
s.t. scope1_scrapeaf_{t in T}:
      ( scrap_eaf_coal_in[t] * ef_ncoal + scrap_eaf_lime_in[t] * ef_lime) - scope1_scrapeaf[t] = 0;   #eq109


# Scope 1 Emissions (Total)
s.t. scope1_def{t in T}:
    (coking_coal_in[t] * ef_ccoal + bf_coalpci_in[t] * ef_pci
        + (coaldri_coal_in[t] + eaf_coal_in[t]+ scrap_eaf_coal_in[t]) * ef_ncoal
        + ngdri_ng_in[t] * ef_ng
        + (sinter_lime_in[t] + bf_lime_in[t] + bof_lime_in[t] + eaf_lime_in[t] + scrap_eaf_lime_in[t]) * ef_lime)
        + (eaf_electrode_in[t]+ scrap_eaf_electrode_in[t]) * ef_eltrd
        + (ccs_steam_boiler[t]/ccs_boiler_eff) * ng_co2_gj
        - scope1_emissions[t] = 0;                         # eq110

# Scope 2 Emissions (Total)
s.t. scope2_def{t in T}:
    n9_grid_ef[t] * grid_power_in[t] - scope2_emissions[t] = 0;                         # eq111


# Total Emissions (Scope 1  + Scope 2)
s.t. total_emissions_def{t in T}:
    scope1_emissions[t] + scope2_emissions[t]- total_ccs[t]- total_emissions[t] = 0;           # eq112
