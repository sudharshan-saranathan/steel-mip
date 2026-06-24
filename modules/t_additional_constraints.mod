# -----------------------------------
#        Initialization
# -----------------------------------
s.t. init_f_bof: f_bof[first(T)] = 0.51;
s.t. init_f_eaf: f_eaf[first(T)] = 0.30;
# Fix 2: init coal-route share 0.84 expressed on the route output (linear).
s.t. init_f_cdri: coaldri_output[first(T)] = 0.84 * dri_eaf_steel_out[first(T)];

# Fix 3: no capture before 2027 expressed directly on the captured amount.
s.t. no_ccs_bf {t in T: t < 2027}:
    ccs_bf[t] = 0;

s.t. no_ccs_cdri {t in T: t < 2027}:
    ccs_cdri[t] = 0;

s.t. no_ccs_ngdri {t in T: t < 2027}:
    ccs_ngdri[t] = 0;
    
# -------------------------------------------------------------------
#              Demand and availability Constraints
# -------------------------------------------------------------------
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
# -------------------------------------------------------------------
#              Policy inclined Constraints
# -------------------------------------------------------------------
s.t. scrap_eaf_monotonic {t in T: ord(t) > 1}:
    steel_scrap_eaf[t] >= steel_scrap_eaf[prev(t)];

s.t. non_increasing_avg_emissions {t in T: ord(t) > 1}:
    total_emissions[t] * total_steel[prev(t)]
    <= total_emissions[prev(t)] * total_steel[t];    
    
#s.t. avg_emis_lower_2050:
    #total_emissions[2050] >= (emi_limit - eps) * total_steel[2050];
#s.t. avg_emis_upper_2050:
    #total_emissions[2050] <= (emi_limit + eps) * total_steel[2050];   

s.t. avg_emis_lower_total:
    (sum {t in T} total_emissions[t]) / (sum {t in T} total_steel[t]) >= avg_emi - eps;
s.t. avg_emis_upper_total:
    (sum {t in T} total_emissions[t]) / (sum {t in T} total_steel[t]) <= avg_emi + eps;   

# -------------------------------------------------------------------
#              Ramping Constraints
# -------------------------------------------------------------------
#Production ramp
s.t. bof_prod_up {t in T: t != first(T)}:
    steel_bof[t] <= 1.15 * steel_bof[prev(t)];

s.t. bof_prod_down {t in T: t != first(T)}:
    steel_bof[t] >= 0.85 * steel_bof[prev(t)];
    
s.t. cdri_prod_up {t in T: t != first(T)}:
    coaldri_output[t] <= 1.15 * coaldri_output[prev(t)];

s.t. cdri_prod_down {t in T: t != first(T)}:
    coaldri_output[t] >= 0.85 * coaldri_output[prev(t)];
    
s.t. ngdri_prod_up {t in T: t != first(T)}:
    ngdri_output[t] <= 1.15 * ngdri_output[prev(t)];

s.t. ngdri_prod_down {t in T: t != first(T)}:
    ngdri_output[t] >= 0.85 * ngdri_output[prev(t)];



#s.t. h2dri_prod_up{t in T: t > ng_h2_start_year}:
     #n6_h2_avail[t] = 1.15 * n6_h2_avail[prev(t)];
     
     
    
#s.t. h2dri_prod_up{t in T: t > ng_h2_start_year}:
    #h2dri_output[t] <= 1.15 * h2dri_output[prev(t)];

s.t. h2dri_prod_down{t in T: t > ng_h2_start_year}:
    h2dri_output[t] >= 0.85* h2dri_output[prev(t)];


    
#Carbon capture ramp
param ramp{t in T} :=
    if t < 2035 then 0.03
    else if t < 2045 then 0.05
    else 0.07;
# Fix 3 (Option A): capture ramp on captured AMOUNT, with a base-growth slack.
# The original fraction ramp |fc[t]-fc[t-1]| <= ramp[t] permits, in amount terms,
#   |ccs[t]-ccs[t-1]| <= ramp[t]*eta*capbase[t] + fc[t-1]*eta*(capbase[t]-capbase[t-1]).
# The 2nd (base-growth) term has no exact linear form once fc is dropped (penetration
# fc = ccs/(eta*capbase) is a ratio of variables). We replace it with the valid linear
# upper bound  ccs_growth_slack * ccs[t-1], where ccs_growth_slack bounds the year-on-year
# growth of the capturable base. Every route's output is ramp-limited to +/-15%
# (bof/cdri/ngdri_prod_up|down) and the BF emission intensity declines over time, so the
# base grows by at most ~15%/yr; hence ccs_growth_slack = 0.15 is a valid bound that makes
# this ramp never STRICTER than the original fraction ramp (no feasible point is cut). It
# is a slightly-more-permissive linear surrogate -- documented as such for the paper.
param ccs_growth_slack := 0.15;   # = production-ramp headroom (1.15 - 1)

s.t. bf_ccs_ramp_up {t in T: ord(t) > 1}:
    ccs_bf[t] - ccs_bf[prev(t)] <= ramp[t] * n10_ccs_eta * capbase_bf[t] + ccs_growth_slack * ccs_bf[prev(t)];
s.t. bf_ccs_ramp_dn {t in T: ord(t) > 1}:
    ccs_bf[prev(t)] - ccs_bf[t] <= ramp[t] * n10_ccs_eta * capbase_bf[t] + ccs_growth_slack * ccs_bf[prev(t)];

s.t. cdri_ccs_ramp_up {t in T: ord(t) > 1}:
    ccs_cdri[t] - ccs_cdri[prev(t)] <= ramp[t] * n10_ccs_eta * capbase_cdri[t] + ccs_growth_slack * ccs_cdri[prev(t)];
s.t. cdri_ccs_ramp_dn {t in T: ord(t) > 1}:
    ccs_cdri[prev(t)] - ccs_cdri[t] <= ramp[t] * n10_ccs_eta * capbase_cdri[t] + ccs_growth_slack * ccs_cdri[prev(t)];

s.t. ngdri_ccs_ramp_up {t in T: ord(t) > 1}:
    ccs_ngdri[t] - ccs_ngdri[prev(t)] <= ramp[t] * n10_ccs_eta * capbase_ngdri[t] + ccs_growth_slack * ccs_ngdri[prev(t)];
s.t. ngdri_ccs_ramp_dn {t in T: ord(t) > 1}:
    ccs_ngdri[prev(t)] - ccs_ngdri[t] <= ramp[t] * n10_ccs_eta * capbase_ngdri[t] + ccs_growth_slack * ccs_ngdri[prev(t)];
# -------------------------------------------------------------------
#              Binary Constratints for switches
# -------------------------------------------------------------------
# Fix 3: capture phase-in switches re-expressed on captured AMOUNT. The big-M is
# now route/year specific (Mccs_* = n10_ccs_eta*fc_max*cap_ub_*, defined in
# modules/q_carbon_capture.mod), since ccs_* is an emission magnitude rather than
# a [0,0.9] fraction. Semantics unchanged: while dec_switch=0 the captured amount
# is non-decreasing; once the (monotone) switch flips to 1 it is non-increasing.
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
   
#BF-BOF PRODUCTION
#s.t. bof_switch_monotonic {t in T: ord(t) > 1}:
    #dec_switch_bof[t] >= dec_switch_bof[prev(t)];

#s.t. bof_increase_phase {t in T: ord(t) > 1}:
    #f_bof[t] - f_bof[prev(t)] >= -M * dec_switch_bof[t];

#s.t. bof_decrease_phase {t in T: ord(t) > 1}:
    #f_bof[t] - f_bof[prev(t)] <= M * (1 - dec_switch_bof[t]);
    
      