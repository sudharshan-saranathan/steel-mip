reset;
set T ordered := 2025..2050;

include definitions.mod;
include variables.mod;
include parameters.mod;
include ../core/modules/a_coke.mod;
include ../core/modules/b_sinter.mod;
include ../core/modules/c_pellets_bf.mod;
include ../core/modules/d_blast_furnace.mod;
include ../core/modules/e_bof.mod;
include ../core/modules/f_pellets_coaldri.mod;
include ../core/modules/g_pellets_ngdri.mod;
include ../core/modules/h_pellets_h2dri.mod;
include ../core/modules/i_dri_coal.mod;
include ../core/modules/j_dri_ng.mod;
include ../core/modules/k_dri_h2.mod;
include ../core/modules/l_eaf_dri.mod;
include ../core/modules/m_scrap_eaf.mod;
include ../core/modules/n_steel_balance.mod;
include ../core/modules/q_carbon_capture.mod;
include modules/o_waste_heat.mod;
include ../core/modules/p_power_balance.mod;
include ../core/modules/v_capacity.mod;         
include ../core/modules/r_cost.mod;
include ../core/modules/s_emissions.mod;
include ../core/modules/t_additional_constraints.mod;

param discount_factor{t in T} :=
    1 / (1 + real_discount_rate)^(ord(t) - 1);
minimize obj:
    sum {t in T} discount_factor[t] * total_cost[t];

option solver gurobi;
solve;
include yreport.mod;
