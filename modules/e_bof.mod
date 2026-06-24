# ============================
# BOF balances 
# ============================
s.t. bof_power_balance{t in T}:
    n3_e_bof * steel_bof[t] - bof_power_in[t] = 0;      # eq33
    
s.t. bof_scrap_balance{t in T}:
    n3_s_bof * steel_bof[t] - bof_scrap_in[t] = 0;      # eq34

s.t. bof_lime_balance{t in T}:
    n3_ls_bof * steel_bof[t] - bof_lime_in[t] = 0;      # eq35

s.t. bof_slag_balance{t in T}:
    n3_sl_bof * steel_bof[t] - bof_slag_out[t] = 0;     # eq36

s.t. bof_gas_out{t in T}:
    n3_bofg_bof * ng_bofg_cv * steel_bof[t] - bofgas_out[t] = 0;     # eq37
    
s.t. bof_steel_fraction{t in T}:
    f_bof[t] * total_steel[t] - steel_bof[t] = 0;                    # eq38

s.t. bof_cog_balance{t in T}:
    n3_rec_cog * ng_cog_cv * steel_bof[t] - bof_cog_in[t] = 0;       # eq39




    