# Initialization
# [audit ST-07] FY2024-25 route split (JPC, MoS Annual Report 2025-26 s3.2.3): BOF
# 41.1 %, EAF 20.8 %, IF 38.2 %. Was 0.51/0.49 (the BF share of iron INPUT,
# paper Fig. 1a, not the BOF share of output).
s.t. init_f_bof: f_bof[first(T)] = 0.411;
s.t. init_f_eaf: f_eaf[first(T)] = 0.589;
s.t. init_scrap_eaf: steel_scrap_eaf[first(T)] = 0;
# Linearization: init coal-route share expressed on the route output (linear).
s.t. init_f_cdri: coaldri_output[first(T)] = 0.902 * dri_eaf_steel_out[first(T)];

# Demand and availability Constraints
s.t. meet_demand{t in T}:
    total_steel[t] = dem[t];   # [audit] was the exponential formula repeated; now follows dem_profile

# scrap-availability constraint
s.t. scrap_bound{t in T: t > first(T)}:
    bof_scrap_in[t] + eaf_scrap_in[t] + scrap_eaf_scrap_in[t] <= n8_scrap_limit[t];

s.t. ng_bound{t in T}:
   ngdri_ng_in[t] <= n5_ng_cap[t];

# Coking-coal availability
s.t. coking_coal_bound{t in T: t > first(T)}:
   coking_coal_in[t] <= ccoal_cap[t];

# Policy constraint
s.t. avg_emis_cap_total:
    (sum {t in T} total_emissions[t]) <= avg_emi * (sum {t in T} total_steel[t]);

# [audit] Emission intensity may not rise year on year. Written with the
# exogenous demand dem[t] (= total_steel[t] via meet_demand), which makes it
# LINEAR. The original form multiplied two variables, which is why every study
# driver dropped it, although the paper (s2.2) states it is enforced.
s.t. emission_monotonic {t in T: t > first(T)}:
    total_emissions[t] * dem[t-1]
    <=
    total_emissions[t-1] * dem[t];
