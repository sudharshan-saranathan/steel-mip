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

printf "%-20s %10.4f\n", "Coal DRI-EAF", f_cdri[2050] * f_eaf[2050];

printf "%-20s %10.4f\n", "NG DRI-EAF", f_ngdri[2050] * f_eaf[2050];

printf "%-20s %10.4f\n", "H2 DRI-EAF", 
    (1 - f_cdri[2050] - f_ngdri[2050]) * f_eaf[2050];

printf "%-20s %10.4f\n", "Scrap-EAF", 
    1 - f_bof[2050] 
      - f_cdri[2050] * f_eaf[2050] 
      - f_ngdri[2050] * f_eaf[2050] 
      - (1 - f_cdri[2050] - f_ngdri[2050]) * f_eaf[2050];

printf "\nTOTAL H2 USED IN H2-DRI (2025–2050): %.3f million units\n",
       ( sum{t in T} steel_eaf[t] * (1 - f_cdri[t] - f_ngdri[t]) ) / 1e6;
printf "\n";

       