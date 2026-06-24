# COAL DRI
# Linearization: coaldri_output is now a primary decision variable; the coal/NG/H2
# split is enforced linearly by dri_route_split (k_dri_h2.mod), replacing the old
# bilinear  f_cdri[t] * dri_eaf_steel_out[t] = coaldri_output[t]  (eq46).

# Power consumption (Coal DRI)
s.t. coaldri_power_balance{t in T}:
    n4_e_dri * coaldri_output[t] - coaldri_power_in[t] = 0;       # eq47

# Pellet requirement for Coal DRI
s.t. coaldri_pellets_balance{t in T}:
    n4_pel_dri * coaldri_output[t] - coaldri_pellets_in[t] = 0;      # eq48
    
# Lump ore requirement (Coal DRI)
s.t. coaldri_lumpore_balance{t in T}:
    n4_ore_dri * coaldri_output[t] - coaldri_lumpore_in[t] = 0;   # eq49

# Coal consumption in Coal DRI
s.t. coaldri_coal_balance{t in T}:
    n4_c_dri * coaldri_output[t] - coaldri_coal_in[t] = 0;        # eq50
    












