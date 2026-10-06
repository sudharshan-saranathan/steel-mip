# Carbon capture (linear). Two distinct limits:
#
#  1. co2_capturable_X[t]: the gross CO2 in the capture-amenable streams.
#     A route can physically capture at most fc_max x ccs_share_X of its base.
#
#  2. DEPLOYMENT ceiling: ccs_avail[t] is the exogenous fraction of the sector's
#     capturable CO2 that the CCS build-out (capture modules, pipelines, storage permits)
#     can handle in year t. The captured amount is the decision, bounded by-
#     sum_X ccs_X[t] <= ccs_avail[t] * sum_X co2_capturable_X[t].

# [audit ST-10] One capture rate (0.90) applied to the CAPTURABLE share of each
# route's CO2. Previously n10_ccs_eta x fc_max = 0.765 was applied to ALL route
# CO2 (two efficiencies stacked, and a base that included stacks no plant
# captures). Shares: BF-BOF 0.67 -> cap 0.60 of route CO2 (median of NITI 2022
# ~0.50, MoS/CEEW 0.59, NITI Fig 2-14 0.64, IEAGHG 0.59-0.73); coal-DRI 0.67
# (by analogy, unsourced); NG-DRI 0.90 (process stream). See stage2/ccs.md.
param fc_max := 0.9;   # capture rate on the capturable stream
param ccs_share_bf    default 0.67;
param ccs_share_cdri  default 0.67;
param ccs_share_ngdri default 0.90;

# Physical capturable CO2 base per route
s.t. co2_capturable_bf_def{t in T}:
    co2_capturable_bf[t] =
        coking_coal_in[t] * ef_ccoal + bf_coalpci_in[t] * ef_pci
      + (sinter_lime_in[t] + bf_lime_in[t] + bof_lime_in[t]) * ef_lime;        # base for eq84

s.t. co2_capturable_cdri_def{t in T}:
    co2_capturable_cdri[t] =
        coaldri_coal_in[t] * ef_ncoal + (n7_cs*coaldri_output[t]) * ef_ncoal
      + (n7_ls*coaldri_output[t]) * ef_lime;                     # base for eq85

s.t. co2_capturable_ngdri_def{t in T}:
    co2_capturable_ngdri[t] =
        ngdri_ng_in[t] * ef_ng + (n7_cs*ngdri_output[t]) * ef_ncoal
      + (n7_ls*ngdri_output[t]) * ef_lime;                       # base for eq86

# Per-route physical capture limit (cannot capture more than eta*fc_max of base)
s.t. ccs_bf_cap{t in T}:
    ccs_bf[t]    <= fc_max * ccs_share_bf * co2_capturable_bf[t];             # eq84
s.t. ccs_cdri_cap{t in T}:
    ccs_cdri[t]  <= fc_max * ccs_share_cdri * co2_capturable_cdri[t];           # eq85
s.t. ccs_ngdri_cap{t in T}:
    ccs_ngdri[t] <= fc_max * ccs_share_ngdri * co2_capturable_ngdri[t];          # eq86

# Deployment-readiness fraction
# [audit ST-10/ccs_avail] 0 through 2034, then linear to phi_2050 = 0.25 of route
# CO2 in 2050. DST CCUS roadmap 2025: only pilot injection (<30 kt/yr) in
# 2030-35, commercial hubs 2035-45; MoS 2024: 6-9 yr from site identification
# to 1 Mt/yr; IEA: steel capture ~25 % of direct emissions in 2050; NITI 2022
# targets ~26 % of emissions economy-wide. Was 2027 start and 0.50.
param ccs_start default 2035;
param phi_2050 default 0.25;
param ccs_avail{t in T} :=
    if t < ccs_start then 0
    else phi_2050 * (t - ccs_start + 1) / (2050 - ccs_start + 1);

# Sector-wide deployment ceiling
s.t. ccs_sector_ceiling{t in T}:
    ccs_bf[t] + ccs_cdri[t] + ccs_ngdri[t]
      <= ccs_avail[t] * (co2_capturable_bf[t] + co2_capturable_cdri[t] + co2_capturable_ngdri[t]);

# Total captured CO2
s.t. total_captured_co2{t in T}:
   ccs_bf[t] +ccs_cdri[t] +ccs_ngdri[t]  - total_ccs[t] = 0;           # eq87

#Power used in capture (kWh/tCO2), stream-specific (depends on CO2 concentration).
s.t. power_capture{t in T}:
  ccs_kwh_bf*ccs_bf[t] + ccs_kwh_cdri*ccs_cdri[t] + ccs_kwh_ngdri*ccs_ngdri[t]
  - power_ccs[t] = 0;                                                   # eq88

# Solvent-regeneration STEAM balance
s.t. ccs_steam_balance{t in T}:
  ccs_steam_bf*ccs_bf[t] + ccs_steam_cdri*ccs_cdri[t] + ccs_steam_ngdri*ccs_ngdri[t]
  = ccs_steam_whr[t] + ccs_steam_boiler[t];                             # eq88b
