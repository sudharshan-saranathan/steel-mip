

# -----------------------------
# CCS from Blast Furnace Route
# -----------------------------
s.t. ccs_blastfurnace{t in T}:
    (coking_coal_in[t] * 0.1116* 25 + bf_coalpci_in[t] * 0.113 * 26
      + (sinter_lime_in[t] + bf_lime_in[t] + bof_lime_in[t]) * 0.44 )
    * n10_ccs_eta * fc_bf[t] - ccs_bf[t] = 0;                          # eq84


# -----------------------------
# CCS from Coal-DRI route
# -----------------------------
s.t. ccs_coaldri{t in T}:
    (coaldri_coal_in[t] * 0.110* 24 + eaf_coal_in[t] * f_cdri[t] * 0.110* 24
      + eaf_lime_in[t] * f_cdri[t] * 0.44)
    * n10_ccs_eta * fc_cdri[t] - ccs_cdri[t] = 0;                       # eq85


# -----------------------------
# CCS from NG-DRI route
# -----------------------------
s.t. ccs_naturalgasdri{t in T}:
    (ngdri_ng_in[t] * 0.055 * 50 + eaf_coal_in[t] * f_ngdri[t] * 0.110*24
      + eaf_lime_in[t] * f_ngdri[t] * 0.44)
    * n10_ccs_eta * fc_ngdri[t] - ccs_ngdri[t] = 0;                      # eq86


# -----------------------------
# Total captured CO2
# -----------------------------
s.t. total_captured_co2{t in T}:
   ccs_bf[t] +ccs_cdri[t] +ccs_ngdri[t]  - total_ccs[t] = 0;           # eq87
 
 #+ ccs_cdri[t] + ccs_ngdri[t]
#Power used in capture (kWh/t)
s.t. power_capture{t in T}:
  total_ccs[t] * 800 - power_ccs[t] = 0;                                # eq88
   
   