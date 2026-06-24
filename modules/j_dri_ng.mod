
# ============================================
# NG DRI (time-series)
# ============================================
# Fix 2: ngdri_output is now a primary decision variable; enforced by
# dri_route_split (k_dri_h2.mod), replacing the old bilinear
#   f_ngdri[t] * dri_eaf_steel_out[t] = ngdri_output[t]  (eq51).

# Power consumption for NG DRI
s.t. ngdri_power_balance{t in T}:
    n5_e_dri * ngdri_output[t] - ngdri_power_in[t] = 0;        # eq52
    
# Pellet requirement for NG DRI
s.t. ngdri_pellets_balance{t in T}:
    n5_pel_dri * ngdri_output[t] - ngdri_pellets_in[t] = 0;     # eq53
    
# Lump ore consumption
s.t. ngdri_lumpore_balance{t in T}:
    n5_ore_dri * ngdri_output[t] - ngdri_lumpore_in[t] = 0;    # eq54   
    
# Natural gas consumption
s.t. ngdri_ng_balance{t in T}:
    n5_ng_dri * ngdri_output[t] - ngdri_ng_in[t] = 0;          # eq55
    








    
 




