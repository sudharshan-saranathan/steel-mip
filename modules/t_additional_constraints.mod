# Initialization

s.t. init_f_bof: f_bof[first(T)] = 0.51;
s.t. init_f_eaf: f_eaf[first(T)] = 0.30;
# Linearization: init coal-route share 0.84 expressed on the route output (linear).
s.t. init_f_cdri: coaldri_output[first(T)] = 0.84 * dri_eaf_steel_out[first(T)];

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


#Production ramp
s.t. bof_prod_up {t in T: t != first(T)}:
    steel_bof[t] <= 1.2 * steel_bof[prev(t)];

s.t. bof_prod_down {t in T: t != first(T)}:
    steel_bof[t] >= 0.8 * steel_bof[prev(t)];
    
s.t. cdri_prod_up {t in T: t != first(T)}:
    coaldri_output[t] <= 1.2 * coaldri_output[prev(t)];

s.t. cdri_prod_down {t in T: t != first(T)}:
    coaldri_output[t] >= 0.8 * coaldri_output[prev(t)];
    
# NG-DRI production is governed solely by the n5_ng_cap[t] availability curve;
# no additional up/down ramps are applied.

s.t. h2dri_prod_down{t in T: t > ng_h2_start_year}:
    h2dri_output[t] >= 0.8* h2dri_output[prev(t)];

# Carbon-capture deployment pace is now governed by the sector-wide
# ccs_avail[t] ceiling in q_carbon_capture.mod (infrastructure/logistics ramp),
# which replaces the former per-route |Dccs| <= ramp*eta*capbase + slack limits.

# Binary Constraints for switches
# Linearization: phase-in switches re-expressed on the captured AMOUNT. The big-M
# is route/year specific (Mccs_* = n10_ccs_eta*fc_max*cap_ub_*, defined in
# q_carbon_capture.mod). Semantics unchanged: while dec_switch=0 the captured
# amount is non-decreasing; once the (monotone) switch flips to 1 it is non-increasing.
#BF Carbon Capture
s.t. bf_switch_monotonic {t in T: ord(t) > 1}:
    dec_switch_bf[t] >= dec_switch_bf[prev(t)];

s.t. bf_increase_phase {t in T: ord(t) > 1}:
    ccs_bf[t] - ccs_bf[prev(t)] >= -Mccs_bf[t] * dec_switch_bf[t];

s.t. bf_decrease_phase {t in T: ord(t) > 1}:
    ccs_bf[t] - ccs_bf[prev(t)] <= Mccs_bf[t] * (1 - dec_switch_bf[t]);

#Coal DRI Carbon Capture
s.t. cdri_switch_monotonic {t in T: ord(t) > 1}:
    dec_switch_cdri[t] >= dec_switch_cdri[prev(t)];

s.t. cdri_increase_phase {t in T: ord(t) > 1}:
    ccs_cdri[t] - ccs_cdri[prev(t)] >= -Mccs_cdri[t] * dec_switch_cdri[t];

s.t. cdri_decrease_phase {t in T: ord(t) > 1}:
    ccs_cdri[t] - ccs_cdri[prev(t)] <= Mccs_cdri[t] * (1 - dec_switch_cdri[t]);

# NG DRI Carbon Capture
s.t. ngdri_switch_monotonic {t in T: ord(t) > 1}:
    dec_switch_ngdri[t] >= dec_switch_ngdri[prev(t)];

s.t. ngdri_increase_phase {t in T: ord(t) > 1}:
   ccs_ngdri[t] - ccs_ngdri[prev(t)] >= -Mccs_ngdri[t] * dec_switch_ngdri[t];

s.t. ngdri_decrease_phase {t in T: ord(t) > 1}:
    ccs_ngdri[t] - ccs_ngdri[prev(t)] <= Mccs_ngdri[t] * (1 - dec_switch_ngdri[t]);
   
    
      