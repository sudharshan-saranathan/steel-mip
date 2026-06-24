# Waste Heat/Power Balances 
# CDQ, TRT, and Sinter WHR are already accounted in material/energy flows of respective processes
# BF-BOF waste heat 
s.t. bf_bof_waste_heat_balance{t in T}:
      cog_out[t]
    + bfg_out[t]
    + bofgas_out[t]
    - cokeov_cog_in[t]
    - bf_cog_in[t]
    - bof_cog_in[t]
    - bfg_in[t]
    - cokeov_bfg_in[t]
    - wasteheat_bf_bof[t]
    = 0;                                                          # eq78

# DRI–EAF and Scrap-EAF waste heat
s.t. eaf_waste_heat_balance{t in T}:
    eafgas_out[t] - wasteheat_eaf[t] = 0;                         # eq79

s.t. scrap_eaf_wasteheat_balance{t in T}:
    scrap_eaf_gas_out[t] - scrap_eaf_wasteheat[t] = 0;            # eq80

# Available waste stream after accounting for losses and unrecoverable wastes
s.t. available_waste_stream{t in T}:
    (wasteheat_bf_bof[t] + wasteheat_eaf[t]
      + scrap_eaf_wasteheat[t])*0.3  - whr_available_gas[t] = 0;  #eq81

# WHR power from all waste-heat sources
s.t. whr_power_balance{t in T}:
    (whr_available_gas[t] * 277.78 * n9_eta * n9_whr[t]) - whr_power_generated[t] = 0; #eq82                                                    # eq79

     
      
 