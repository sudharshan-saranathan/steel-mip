# Fix 2: route fractions recovered post-solve from route outputs (share_coal/share_ng
# are no longer model variables). share_coal == old share_coal, share_ng == old share_ng.
# Declared empty, then populated post-solve via let (a param := definition may
# not reference variables, but a let assignment after solve may).
param share_coal{t in T} default 0;
param share_ng{t in T}   default 0;
let {t in T} share_coal[t] := if dri_eaf_steel_out[t] > 1e-6 then coaldri_output[t]/dri_eaf_steel_out[t] else 0;
let {t in T} share_ng[t]   := if dri_eaf_steel_out[t] > 1e-6 then ngdri_output[t]/dri_eaf_steel_out[t] else 0;

# Fix 3: realized capture fraction recovered post-solve (fc_* are no longer
# model variables). fc_X = ccs_X / (n10_ccs_eta * capbase_X).
param fc_bf_real{t in T}    default 0;
param fc_cdri_real{t in T}  default 0;
param fc_ngdri_real{t in T} default 0;
let {t in T} fc_bf_real[t]    := if capbase_bf[t]    > 1e-6 then ccs_bf[t]   /(n10_ccs_eta*capbase_bf[t])    else 0;
let {t in T} fc_cdri_real[t]  := if capbase_cdri[t]  > 1e-6 then ccs_cdri[t] /(n10_ccs_eta*capbase_cdri[t])  else 0;
let {t in T} fc_ngdri_real[t] := if capbase_ngdri[t] > 1e-6 then ccs_ngdri[t]/(n10_ccs_eta*capbase_ngdri[t]) else 0;

printf "\nAVERAGE STEEL PRODUCTION COST (2025–2050): %.2f $/ton\n",
    if sum{t in T} total_steel[t] > 0 then
        ( sum{t in T} discount_factor[t] * total_cost[t] )
      / ( sum{t in T} discount_factor[t] * total_steel[t] )
    else 0;
       
printf "2050: Cost = %.3f $/t CS, Emissions = %.3f tCO2/t CS\n",
    if total_steel[2050] > 0 then
        total_cost[2050] / total_steel[2050]
    else 0,
    if total_steel[2050] > 0 then
        total_emissions[2050] / total_steel[2050]
    else 0;      
       
printf "\nCO2 CAPTURED PER TON STEEL OVERALL (2025–2050): %.3f\n",
       if (sum{t in T} total_steel[t]) > 0 then
           ( sum{t in T} total_ccs[t] )
         / ( sum{t in T} total_steel[t] )
       else 0;       
       
printf "\n%-20s %-20s\n", "Route", "Fraction";

printf "%-20s %10.4f\n", "BF-BOF", f_bof[2050];

printf "%-20s %10.4f\n", "Coal DRI-EAF", share_coal[2050] * f_eaf[2050];

printf "%-20s %10.4f\n", "NG DRI-EAF", share_ng[2050] * f_eaf[2050];

printf "%-20s %10.4f\n", "H2 DRI-EAF", 
    (1 - share_coal[2050] - share_ng[2050]) * f_eaf[2050];

printf "%-20s %10.4f\n", "Scrap-EAF", 
    1 - f_bof[2050] 
      - share_coal[2050] * f_eaf[2050] 
      - share_ng[2050] * f_eaf[2050] 
      - (1 - share_coal[2050] - share_ng[2050]) * f_eaf[2050];

printf "\nTOTAL H2 USED IN H2-DRI (2025–2050): %.3f million units\n",
       ( sum{t in T} steel_eaf[t] * (1 - share_coal[t] - share_ng[t]) ) / 1e6;
printf "\n";

       