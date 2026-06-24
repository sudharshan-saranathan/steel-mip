# ============================================
# H2 DRI 
# ============================================

# H2 DRI output based on DRI-EAF fraction
s.t. h2dri_fraction{t in T}:
    (1-f_cdri[t] - f_ngdri[t]) * dri_eaf_steel_out[t]- h2dri_output[t] = 0;        # eq56

# Power consumption for H2 DRI
s.t. h2dri_power_balance{t in T}:
    n6_e_dri * h2dri_output[t] - h2dri_power_in[t] = 0;         # eq57
    
# Pellets required for H2 DRI
s.t. h2dri_pellets_balance{t in T}:
    n6_pel_dri * h2dri_output[t] - h2dri_pellets_in[t] = 0;      # eq58

# Lump ore requirement
s.t. h2dri_lumpore_balance{t in T}:
    n6_ore_dri * h2dri_output[t] - h2dri_lumpore_in[t] = 0;     # eq59
    
# Hydrogen consumption
s.t. h2dri_h2_balance{t in T}:
    n6_h2_dri * h2dri_output[t] - h2dri_h2_in[t] = 0;           # eq60


