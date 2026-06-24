reset;
set T ordered := 2025..2050;

include definitions.mod;
include variables.mod;
include parameters.mod;

let {t in T} n5_cost_NG[t] := NGVAL;
#let {t in 2035..2040} n5_cost_NG[t] := NGVAL*1.5;
let ng_cost_h2_end := H2ENDVAL;
let ng_h2_start_year := H2YEARVAL;
let n10_ccs_cost_end := CCSVAL;

let n8_scrap_rate := SCRAPVAL;
let n8_scrap_limit[first(T)] := 32000000;

let {t in T: ord(t) > 1}
n8_scrap_limit[t] := n8_scrap_limit[prev(t)] * (1 + n8_scrap_rate);

let n6_h2_avail[H2YEARVAL] := 1500000;

# NG-availability scenario profile (overrides n5_ng_cap set in parameters.mod)
include NGAVAILFILE;

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
discount_factor[t] * total_cost[t];

option solver gurobi;
option gurobi_options 'Threads=5 TimeLimit=600 nonconvex=2 mipgap=0.002';

solve;

include yreport.mod;
include report.mod;
