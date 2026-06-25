# Initialization

# 2025 actual production split (pinned): BF-BOF 0.38, DRI-EAF 0.43 (coal:NG = 0.884:0.116
# -> coal 0.38, NG 0.05 of total steel), scrap-EAF 0.19. BF-BOF ~ Coal-DRI by design.
s.t. init_f_bof: f_bof[first(T)] = 0.38;
s.t. init_f_eaf: f_eaf[first(T)] = 0.43;
# Linearization: init coal-route share expressed on the route output (linear).
s.t. init_f_cdri: coaldri_output[first(T)] = 0.884 * dri_eaf_steel_out[first(T)];

# Linearization: no capture before 2027 expressed directly on the captured amount.
s.t. no_ccs_bf {t in T: t < 2027}:
    ccs_bf[t] = 0;

s.t. no_ccs_cdri {t in T: t < 2027}:
    ccs_cdri[t] = 0;

s.t. no_ccs_ngdri {t in T: t < 2027}:
    ccs_ngdri[t] = 0;
    
# Demand and availability Constraints
s.t. meet_demand{t in T}:
    total_steel[t] = base_demand * (1 + growth_rate)^(ord(t) - 1);

s.t. scrap_bound{t in T}:
    scrap_eaf_scrap_in[t] <= n8_scrap_limit[t];

s.t. ng_bound{t in T}:
   ngdri_ng_in[t] <= n5_ng_cap[t];
               
#s.t. No_H2_Before_startyear_bf{t in T: t < ng_h2_start_year}:
    #n6_h2_avail[t] = 0;
        
#s.t. H2_Availability_Constraint{t in T: t >= ng_h2_start_year}:
    #h2dri_h2_in[t] <= n6_h2_avail[t];
    
#s.t. H2_Ramp{t in T: t > ng_h2_start_year}:
    #h2dri_h2_in[t] <= 1.15 * h2dri_h2_in[prev(t)] + n6_h2_avail[ng_h2_start_year];        

# Policy inclined Constraints
# Linearization: cleared the variable-denominator ratio by multiplying through by
# sum total_steel[t] (>= 0). Equivalent feasible region, now linear.
s.t. avg_emis_lower_total:
    (sum {t in T} total_emissions[t]) >= (avg_emi - eps) * (sum {t in T} total_steel[t]);

s.t. avg_emis_upper_total:
    (sum {t in T} total_emissions[t]) <= (avg_emi + eps) * (sum {t in T} total_steel[t]);


# Production ramp: +-15%/yr off the prior year, anchored to the pinned 2025 actual.
# Applied to the four incumbent routes (BF-BOF, Coal-DRI, NG-DRI, Scrap). H2-DRI is
# a future entrant with no 2025 stock, so its growth stays governed by the H2
# availability mechanism (parameters.mod); only its down-ramp is aligned to 0.85.
# Fixed annual slab: max YoY change = ramp_frac * the pinned 2025 production of
# the route (additive, not compounding). steel_*[first(T)] is fixed by the init_f
# constraints above, so the RHS is effectively constant.
s.t. bof_prod_up {t in T: t != first(T)}:
    steel_bof[t] - steel_bof[prev(t)] <= ramp_frac * steel_bof[first(T)];
s.t. bof_prod_down {t in T: t != first(T)}:
    steel_bof[prev(t)] - steel_bof[t] <= ramp_frac * steel_bof[first(T)];

s.t. cdri_prod_up {t in T: t != first(T)}:
    coaldri_output[t] - coaldri_output[prev(t)] <= ramp_frac * coaldri_output[first(T)];
s.t. cdri_prod_down {t in T: t != first(T)}:
    coaldri_output[prev(t)] - coaldri_output[t] <= ramp_frac * coaldri_output[first(T)];

# NG-DRI: fixed-slab ramp in addition to the n5_ng_cap[t] availability curve.
s.t. ngdri_prod_up {t in T: t != first(T)}:
    ngdri_output[t] - ngdri_output[prev(t)] <= ramp_frac * ngdri_output[first(T)];
s.t. ngdri_prod_down {t in T: t != first(T)}:
    ngdri_output[prev(t)] - ngdri_output[t] <= ramp_frac * ngdri_output[first(T)];

s.t. scrap_prod_up {t in T: t != first(T)}:
    steel_scrap_eaf[t] - steel_scrap_eaf[prev(t)] <= ramp_frac * steel_scrap_eaf[first(T)];
s.t. scrap_prod_down {t in T: t != first(T)}:
    steel_scrap_eaf[prev(t)] - steel_scrap_eaf[t] <= ramp_frac * steel_scrap_eaf[first(T)];

# H2-DRI: future entrant, governed by the H2 availability mechanism; keep only a
# modest multiplicative down-floor once it is active.
s.t. h2dri_prod_down{t in T: t > ng_h2_start_year}:
    h2dri_output[t] >= 0.85 * h2dri_output[prev(t)];

# Carbon-capture deployment pace is now governed by the sector-wide
# ccs_avail[t] ceiling in q_carbon_capture.mod (infrastructure/logistics ramp),
# which replaces the former per-route |Dccs| <= ramp*eta*capbase + slack limits.

# CCS phase-in switches REMOVED: the old dec_switch_* binaries forced each route's
# capture to be single-peaked (monotone up then down). That anti-churn role is now
# served economically by the CCS retrofit's sunk capex (build_ccs_* in v_capacity.mod),
# and the unimodality conflicted with capacity aging (it forbade rebuilding capture
# after a dip). Deployment pace is still bounded by ccs_avail (q_carbon_capture.mod).
# Dropping them removes the model's last binaries -> near-pure LP.
   
    
      