# -----------------------------------
#        Initialization
# -----------------------------------
s.t. init_f_bof: f_bof[first(T)] = 0.51;
s.t. init_f_eaf: f_eaf[first(T)] = 0.30;
s.t. init_f_cdri: f_cdri[first(T)] = 0.84;

s.t. no_ccs_bf {t in T: t < 2027}:
    fc_bf[t] = 0;

s.t. no_ccs_cdri {t in T: t < 2027}:
    fc_cdri[t] = 0;

s.t. no_ccs_ngdri {t in T: t < 2027}:
    fc_ngdri[t] = 0;
    
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
s.t. bf_ramp {t in T: ord(t) > 1}:
    abs(fc_bf[t] - fc_bf[prev(t)]) <= ramp[t];    

s.t. cdri_ramp {t in T: ord(t) > 1}:
    abs(fc_cdri[t] - fc_cdri[prev(t)]) <= ramp[t];      

s.t. ngdri_ramp {t in T: ord(t) > 1}:
    abs(fc_ngdri[t] - fc_ngdri[prev(t)]) <= ramp[t];   
# -------------------------------------------------------------------
#              Binary Constratints for switches
# -------------------------------------------------------------------
param M := 1;
#BF Carbon Capture
s.t. bf_switch_monotonic {t in T: ord(t) > 1}:
    dec_switch_bf[t] >= dec_switch_bf[prev(t)];

s.t. bf_increase_phase {t in T: ord(t) > 1}:
    fc_bf[t] - fc_bf[prev(t)] >= -M * dec_switch_bf[t];

s.t. bf_decrease_phase {t in T: ord(t) > 1}:
    fc_bf[t] - fc_bf[prev(t)] <= M * (1 - dec_switch_bf[t]);  

#Coal DRI Carbon Capture    
s.t. cdri_switch_monotonic {t in T: ord(t) > 1}:
    dec_switch_cdri[t] >= dec_switch_cdri[prev(t)];

s.t. cdri_increase_phase {t in T: ord(t) > 1}:
    fc_cdri[t] - fc_cdri[prev(t)] >= -M * dec_switch_cdri[t];

s.t. cdri_decrease_phase {t in T: ord(t) > 1}:
    fc_cdri[t] - fc_cdri[prev(t)] <= M * (1 - dec_switch_cdri[t]);     

# NG DRI Carbon Capture

s.t. ngdri_switch_monotonic {t in T: ord(t) > 1}:
    dec_switch_ngdri[t] >= dec_switch_ngdri[prev(t)];

s.t. ngdri_increase_phase {t in T: ord(t) > 1}:
   fc_ngdri[t] - fc_ngdri[prev(t)] >= -M * dec_switch_ngdri[t];

s.t. ngdri_decrease_phase {t in T: ord(t) > 1}:
    fc_ngdri[t] - fc_ngdri[prev(t)] <= M * (1 - dec_switch_ngdri[t]);  
   
#BF-BOF PRODUCTION
#s.t. bof_switch_monotonic {t in T: ord(t) > 1}:
    #dec_switch_bof[t] >= dec_switch_bof[prev(t)];

#s.t. bof_increase_phase {t in T: ord(t) > 1}:
    #f_bof[t] - f_bof[prev(t)] >= -M * dec_switch_bof[t];

#s.t. bof_decrease_phase {t in T: ord(t) > 1}:
    #f_bof[t] - f_bof[prev(t)] <= M * (1 - dec_switch_bof[t]);
    
      