# ===================================================================
# Linearization: the captured CO2 amount ccs_* is now the decision variable,
# bounded above by the technical capture limit
#     ccs_X[t] <= n10_ccs_eta * fc_max * capbase_X[t],
# where capbase_X[t] is the (linear) capturable CO2 base for route X and fc_max
# is the maximum capture penetration (formerly the upper bound on the fc_* vars).
# This eliminates the bilinear/trilinear products (capbase_X * fc_X) of eq84-86.
# The realized capture fraction is recovered post-solve in yreport.mod.
#
# The cross-products  eaf_coal_in*f_cdri  and  eaf_lime_in*f_cdri  in the original
# eq85/eq86 are linearized exactly: eaf_coal_in = n7_cs*steel_eaf (eq66),
# eaf_lime_in = n7_ls*steel_eaf (eq65), and f_cdri = coaldri_output/((1-n7_phi_eaf)
# *steel_eaf), so steel_eaf cancels:
#     eaf_coal_in*f_cdri = n7_cs*coaldri_output/(1-n7_phi_eaf), etc.
# ===================================================================
param fc_max := 0.9;   # max capture penetration fraction (was the fc_* upper bound)

# Capturable CO2 base per route (linear in flows; same coefficients as eq84/85/86)
s.t. capbase_bf_def{t in T}:
    capbase_bf[t] =
        coking_coal_in[t] * 0.1116 * 25 + bf_coalpci_in[t] * 0.113 * 26
      + (sinter_lime_in[t] + bf_lime_in[t] + bof_lime_in[t]) * 0.44;        # base for eq84

s.t. capbase_cdri_def{t in T}:
    capbase_cdri[t] =
        coaldri_coal_in[t] * 0.110 * 24 + (n7_cs*coaldri_output[t]/(1-n7_phi_eaf)) * 0.110 * 24
      + (n7_ls*coaldri_output[t]/(1-n7_phi_eaf)) * 0.44;                     # base for eq85

s.t. capbase_ngdri_def{t in T}:
    capbase_ngdri[t] =
        ngdri_ng_in[t] * 0.055 * 50 + (n7_cs*ngdri_output[t]/(1-n7_phi_eaf)) * 0.110 * 24
      + (n7_ls*ngdri_output[t]/(1-n7_phi_eaf)) * 0.44;                       # base for eq86

# Technical capture limit (linear upper bound on captured CO2)
s.t. ccs_bf_cap{t in T}:
    ccs_bf[t]    <= n10_ccs_eta * fc_max * capbase_bf[t];                    # eq84
s.t. ccs_cdri_cap{t in T}:
    ccs_cdri[t]  <= n10_ccs_eta * fc_max * capbase_cdri[t];                  # eq85
s.t. ccs_ngdri_cap{t in T}:
    ccs_ngdri[t] <= n10_ccs_eta * fc_max * capbase_ngdri[t];                 # eq86

# Valid upper bounds on the capturable base, used only to size the big-M in the
# capture phase-in switches (t_additional_constraints.mod). Because
# |ccs_X[t]-ccs_X[t-1]| <= max(ccs_X) = n10_ccs_eta*fc_max*cap_ub_X[t], these are
# valid (non-binding) big-M values.
param cap_ub_bf{t in T} :=
    1.00*dem[t]*0.1116*25 + 0.25*dem[t]*0.113*26 + 3*(0.10*dem[t])*0.44;
param cap_ub_cdri{t in T} :=
    (1-n7_phi_eaf)*dem[t]*0.110*24
  + (n7_cs/(1-n7_phi_eaf))*((1-n7_phi_eaf)*dem[t])*0.110*24
  + (n7_ls/(1-n7_phi_eaf))*((1-n7_phi_eaf)*dem[t])*0.44;
param cap_ub_ngdri{t in T} :=
    (n5_ng_dri*(1-n7_phi_eaf)*dem[t])*0.055*50
  + (n7_cs/(1-n7_phi_eaf))*((1-n7_phi_eaf)*dem[t])*0.110*24
  + (n7_ls/(1-n7_phi_eaf))*((1-n7_phi_eaf)*dem[t])*0.44;

param Mccs_bf{t in T}    := n10_ccs_eta*fc_max*cap_ub_bf[t];
param Mccs_cdri{t in T}  := n10_ccs_eta*fc_max*cap_ub_cdri[t];
param Mccs_ngdri{t in T} := n10_ccs_eta*fc_max*cap_ub_ngdri[t];

# Total captured CO2
s.t. total_captured_co2{t in T}:
   ccs_bf[t] +ccs_cdri[t] +ccs_ngdri[t]  - total_ccs[t] = 0;           # eq87
 
#Power used in capture (kWh/t)
s.t. power_capture{t in T}:
  total_ccs[t] * 800 - power_ccs[t] = 0;                                # eq88
   
   