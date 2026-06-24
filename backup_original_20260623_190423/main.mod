#Mixed-Integer Quadratically Constrained Programming
reset;
set T ordered := 2025..2050;
 
include definitions.mod;
include parameters.mod;
include variables.mod;
include modules/a_coke.mod;
include modules/b_sinter.mod;
include modules/c_pellets_bf.mod;
include modules/d_blast_furnace.mod;
include modules/e_bof.mod;
include modules/f_pellets_coaldri.mod;
include modules/g_pellets_ngdri.mod;
include modules/h_pellets_h2dri.mod;
include modules/i_dri_coal.mod;
include modules/j_dri_ng.mod;
include modules/k_dri_h2.mod;
include modules/l_eaf_dri.mod;
include modules/m_scrap_eaf.mod;
include modules/n_steel_balance.mod;
include modules/q_carbon_capture.mod;
include modules/o_power_balance.mod;
include modules/p_waste_heat.mod;
include modules/r_cost.mod;
include modules/s_emissions.mod;
include modules/t_additional_constraints.mod;

param discount_factor{t in T} :=
    1 / (1 + real_discount_rate)^(ord(t) - 1);
minimize obj:
    sum {t in T}
        discount_factor[t] *(total_cost[t]);
        #+total_emissions[t] * carbon_tax

# =====================================================
option solver gurobi;
option gurobi_options 'Threads=20';
option gurobi_options 'outlev=1 nonconvex=2'; #checking for nonconvex problem and also type of problem
option show_stats 1; #Detailed information 

solve;
# =====================================================
# Reports
# =====================================================
include yreport.mod;


