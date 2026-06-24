
# ============================================
# NG DRI (time-series)
# ============================================
# NG DRI output based on DRI-EAF fraction
s.t. ngdri_fraction{t in T}:
    f_ngdri[t] * dri_eaf_steel_out[t] - ngdri_output[t] = 0;    # eq51


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
    








    
 




