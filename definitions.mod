
# Crude Steel Production
param base_demand default 152200000;  # Steel production at year 2025
param growth_rate default 0.05;
# Fixed annual steel demand (total_steel is pinned to this by meet_demand).
# Used to linearize the f_bof/f_eaf * total_steel products and to size route bounds.
param dem{t in T} := base_demand * (1 + growth_rate)^(ord(t) - 1);

# TECHNICAL PARAMETERS 
# Global parameters
param ng_e_pell default 200;         # Electricity (kWh) per ton of pellets   
param ng_ore_pell default 1.1;       # Iron ore (ton) per ton of pellets
param ng_cog_cv default 0.018;       # Calorific value (GJ/Nm3) of COG
param ng_bfg_cv default 0.0033;      # Calorific value (GJ/Nm3) of BFG 
param ng_bofg_cv default 0.008;      # Calorific value (GJ/Nm3) of BOFG
param ng_sintgas_cv default 0.0006;  # Calorific value (GJ/Nm3) of sinter
#param ng_biochar_cv default 18;     # Calorific value (GJ/t) of biochar
#param ng_breeze_cv default 28;      # Calorific value (GJ/t) of breeze
#param ng_coke_cv default 30;        # Calorific value (GJ/t) of coke
#param ng_pci_cv default 26;         # Calorific value (GJ/t) of pulverized coal
#param ng_nccoal_cv default 24;      # Calorific value (GJ/t) of non coking coal
#param ng_ccoal_cv default 25;       # Calorific value (GJ/t) of coking coal

# Coke Oven
param n0_e_c default 75;             # Electricity (kWh) per ton of coke     
param n0_cf default 1.47;            # Coal (ton) required per ton of coke      
param n0_br_c default 0.056;         # Breeze produced (ton) per ton of coke                
param n0_tar_c default 0.04;         # Tar produced (ton) per ton of coke  
param n0_cdq_whr default 80;        # Waste heat power (kWh)produced per ton of coke from CDQ
param n0_cog_c default 440;          # Coke Oven Gas (Nm3) formed per ton of coke (mass eqv gas- 0.2 tons)
param n0_rec_cog default 190;        # Recovered COG as fuel(energy) (Nm3/t coke)
param n0_rec_bfg default 270;        # Recovered BFG as fuel (energy) (Nm3/t coke)
# Remaining COG goes to power plant

# Sinter
param n1_e_sint default 50;          # Electricity (kWh) per ton of sinter    
param n1_lime_sint default 0.04;     # Lime (ton)per ton of sinter                              
param n1_ore_sint default 0.9;       # Iron ore (ton) per ton of sinter      
param n1_brz_sint_25 default 0.09;   # Breeze (ton) per ton sinter in 2025                   
param n1_bio_sint_25 default 0;      # Biochar (ton) per ton sinter in 2025  
param n1_brz_sint_50 default 0.058;  # Breeze (ton) per ton sinter by 2050                   
param n1_bio_sint_50 default 0.022;  # Biochar (ton) per ton sinter by 2050
param n1_sintcool_whr default 30;    # Waste heat power (kWh) produced per ton of sinter from sinter cooler and sinter machine    
param n1_sintgas_sint default 1800;  # Sinter gas (Nm3) per ton sinter
#Remaining sinter gas is waste with very low energy value
#Biochar replacement is limited to 20%


# Blast Furnace
param n2_e_hm default 55;            # Electricity (kWh) per ton hot metal  
param n2_sint_hm default 1.15;       # Sinter (ton) per thm                                              
param n2_lime_hm default 0.025;      # Lime (ton) per thm
param n2_slag_hm default 0.3;        # Slag (ton) per thm    
param n2_pel_hm default 0.35;        # Pellets (ton) per thm   
param n2_ore_hm default 0.15;        # Lump ore (ton) per thm   
param n2_bfg_hm default 1500;        # BFG (Nm3) per thm            
param n2_rec_bfg default 500;        # Recovered BFG as fuel (Nm3/thm)   
param n2_rec_cog default 30;         # Recovered COG as fuel (Nm3/thm) 
param n2_trt_whr default 35;         # Top pressure recovery turbine (kWh/thm)   
param n2_coalpci_hm_25 default 0.15; # PCI (ton) per thm in 2025 
param n2_biopci_hm_25 default 0;     # Biomass injection (ton) per thm in 2025
param n2_coalpci_hm_50 default 0.16; # PCI (ton) per thm by 2050
param n2_biopci_hm_50 default 0.053; # Biomass injection (ton) per thm by 2050
param n2_coke_hm_25 default 0.53;    # Coke (ton) per thm in 2025 
param n2_coke_hm_50 default 0.44;    # Coke (ton) per thm by 2050
param n2_h2_hm_25 default 0;         # Hydrogen in blast furnace in 2025 (t/thm)
param n2_h2_hm_50 default 0.013;     # Hydrogen in blast furnace by 2050 (t/thm)
#Biochar replacement is limited to 20%
#Remaining BFG goes to power plant              


# BOF
param n3_e_bof default 174;         # Electricity (kWh) per ton crude steel from BOF    
param n3_s_bof default 0.1;         # Scrap (ton) per tCS in BOF 
param n3_ls_bof default 0.075;      # Limestone (ton) per tCS in BOF
param n3_sl_bof default 0.1;        # Slag (ton) per tCS in BOF
param n3_bofg_bof default 100;      # BOFG gas (Nm3) formed per tCS in BOF
param n3_rec_cog default 65;        # Recovered COG as fuel (Nm3/tCS)

#All BOFG gas assumed being routed to power plant
#Converting power plant streams to electricity and subtracting from energy input will 
#reduce specific energy consumption

#Coal DRI
param n4_e_dri default 100;         # Electricity (kWh) per ton DRI 
param n4_pel_dri default 1.5;       # Pellets (tons) per ton DRI 
param n4_ore_dri default 0.1;       # Ore (tons) per ton DRI 
param n4_c_dri default 1;           # Coal (tons) per ton DRI                 

# NG DRI
param n5_e_dri default 120;         # Electricity (kWh) per ton DRI 
param n5_pel_dri default 1.5;       # Pellets (tons) per ton DRI  
param n5_ore_dri default 0.1;       # Ore (tons) per ton DRI 
param n5_ng_dri default 0.35;       # Natural gas (tons) per ton DRI      


#H2 DRI
param n6_e_dri default 110;         # Electricity (kWh) per ton DRI 
param n6_pel_dri default 1.5;       # Pellets (tons) per ton DRI 
param n6_ore_dri default 0.1;       # Ore (tons) per ton DRI     
param n6_h2_dri default 0.13;       # Hydrogen (tons) per ton DRI 

# EAF (DRI-Based)    
param n7_e_eaf {t in T} :=
    650 + (500 - 650) * (t - 2025) /25;    # Electricity (kWh) per tCS (650 in 2025 to 500 by 2050)  
param n7_phi_eaf default 0.1;              # Scrap (ton) per tCS 
param n7_eltrd default 0.003;              # Electrode (ton) per tCS  
param n7_ls default 0.06;                  # Limestone (ton) per tCS 
param n7_cs default 0.01;                  # Coal (ton) per tCS  
param n7_ss default 0.15;                  # Slag (ton) per tCS   
param n7_eafg default 3;                   # EAF Gas (GJ) per tCS                           
 

# EAF (Scrap-Based)
param n8_e_eaf {t in T} :=
    820 + (650 - 820) * (t - 2025) / 25; # Electricity (kWh) per tCS (820 in 2025 to 650 by 2050)   
param n8_phi_eaf default 1.1;            # Scrap (ton) per tCS
param n8_eltrd default 0.003;            # Electrode (ton) per tCS  
param n8_ls default 0.06;                # Limestone (ton) per tCS 
param n8_cs default 0.01;                # Coal (ton) per tCS 
param n8_ss default 0.15;                # Slag (ton) per tCS 
param n8_eafg default 3;                 # EAF Gas (GJ) per tCS                          
   

# Waste Heat Recovery
param n9_u default 7884;                               # Utilization hours            
param n9_eta default 0.15;                              # WHRS efficiency including losses                        
param n9_whr {t in T} :=
    0.05 +(0.3 - 0.05) * (t - 2025) / 25;               # WHRS penetration level from 30% in 2025 to 70% by 2050 
param n9_grid_ef_start default 0.000886; #0.000757 from grid having 36% share and 0.00096 from CPP having 64% share
param n9_grid_ef_end default 0.0003; 
param n9_grid_ef{t in T} :=
    n9_grid_ef_start + (n9_grid_ef_end - n9_grid_ef_start) * (t - 2025) /25;   # Grid emission factor from 2025 to 2050

# Carbon capture
param n10_ccs_eta default 0.85;                        # Carbon capture efficiency                      


# COST PARAMETERS 
#Global parameters (all costs are in $)
param ng_cost_ccoal default 184;          # Cost per ton of coking coal
param ng_cost_power default 0.07;         # Cost per kWh of grid power
param ng_credit_power default 0.03;       # Selling cost per kWh of generated power
param ng_cost_fineore default 65;         # Cost per ton of fineore
param ng_cost_lime default 60;            # Cost per ton of lime
param ng_cost_biochar default 60;         # Cost per ton of biomass
param ng_capex_pell default 10;           # CAPEX of pellets plant per tCS production
param ng_cost_lumpore default 70;         # Cost per ton of lumpore
param ng_cost_pcoal default 110;          # Cost per ton of PCI coal
param ng_credit_slag default 15;          # Selling cost per ton of slag
param ng_cost_scrap default 350;          # Cost per ton of scrap
param ng_cost_ncoal default 98;          # Cost per ton of non coking coal


param n0_credit_breeze default 55;        # Selling cost per ton of breeze
param n0_credit_tar default 20;           # Selling cost per ton of tar
param n0_capex default 40;                # CAPEX of cokeoven per tCS rpoduction

param n1_cost_breeze default 85;          # Cost per ton of breeze                         
param n1_capex default 30;                # CAPEX of sinter plant per tCS production

param n2_capex default 80;               # CAPEX of blast furnace per tCS production

param n3_capex default 40;                # CAPEX of BOF per tCS production        
                        
param n4_capex_coal default 110;          # CAPEX of Coal-DRI per tCS production

param n5_capex_ng := 90;                  # CAPEX of NG-DRI per tCS production
param n5_cost_NG {t in T} default 10;     # Cost of natural gas per MMBtu

param ng_cost_h2_start default 4500;
param ng_cost_h2_end default 1500;   
param ng_h2_start_year default 2040;
param ng_cost_h2{t in T} :=
    if t <= 2025
     then ng_cost_h2_start
    else ng_cost_h2_start + (ng_cost_h2_end-ng_cost_h2_start) * (t-2025)/25; # Cost of hydrogen from 2025 to 2050
param n6_capex_h2{t in T} :=
    if t <= 2025 then 120
    else 120+ (90-120) * (t-2025)/25;     # CAPEX of H2-DRI per tCS from 2025 to 2050

param n7_capex default 70;                # CAPEX of EAF plant (DRI based) per tCS
param n7_cost_electrode default 600;      # Cost per ton of electrode

param n8_capex default 70;                # CAPEX of EAF plant (Scrap-based) per tCS     
param n8_cost_electrode default 600;      # Cost per ton of electrode
   
param n9_whr_capex default 0.009;         # CAPEX of WHR system per kWh of power generated
param n9_whr_opex default 0.003;          # OPEX of WHR system per kWh of power generated

param n10_ccs_cost_start default 125;
param n10_ccs_cost_end default 75;                                
param n10_ccs_cost{t in T} :=
    n10_ccs_cost_start + (n10_ccs_cost_end - n10_ccs_cost_start) * (t - 2025) / 25;   # Cost per ton of CO2 captured

param carbon_tax default 0; 
param labor_cost default 20;              # Labor cost per tCS
param maintenance_cost default 15;        # Maintenance cost per tCS
param other_opex default 10;              # Other opex per tCS

# OTHER PARAMETERS
param real_discount_rate := 0.06;
param n8_scrap_rate default 0.06;
param n8_scrap_limit{t in T};
param n5_ng_cap {T};

# ============================================================================
# CAPACITY-EXPANSION PARAMETERS  (branch: capex-opex-framework)
# Overnight-capex + fixed/variable-opex framework; consumed by v_capacity.mod
# and r_cost.mod. See modules/v_capacity.mod for the formulation notes.
# ============================================================================

# --- 2025 installed capacity per route (tonnes), on each route's OUTPUT-var basis.
#     DRI routes carry the 0.9*steel_eaf (crude-steel-equiv) factor (see derivation):
#       BF-BOF 90.0, coal-DRI 70.6, NG-DRI 12.9 (crude-steel MTPA); scrap-EAF 33.5 (mip-v1).
param cap0_bof   default 90.00e6;             # steel_bof
param cap0_cdri  default 63.54e6;             # coaldri_output = 0.9 * 70.6e6
param cap0_ngdri default 11.61e6;             # ngdri_output   = 0.9 * 12.9e6
param cap0_h2dri default 0;                   # h2dri_output   (none in 2025)
param cap0_scrap default 33.50e6;             # steel_scrap_eaf (mip-v1 baseline)

# --- Asset lifetimes (yr) = build lock-in horizon (from former u_lockin horizons).
param life_bof   default 25;
param life_cdri  default 20;
param life_ngdri default 15;
param life_h2dri default 15;
param life_scrap default 10;

# --- Fixed opex per unit CRUDE-STEEL capacity per year (labour + maintenance).
#     Incurred on installed capacity whether or not it runs. Route-indexed so
#     per-route values can be supplied later; defaults to the global figure.
param fopex_bof   default labor_cost + maintenance_cost;
param fopex_cdri  default labor_cost + maintenance_cost;
param fopex_ngdri default labor_cost + maintenance_cost;
param fopex_h2dri default labor_cost + maintenance_cost;
param fopex_scrap default labor_cost + maintenance_cost;

# --- Capital recovery factor CRF(L) at the real discount rate.
param crf_bof   := real_discount_rate*(1+real_discount_rate)^life_bof  /((1+real_discount_rate)^life_bof  -1);
param crf_cdri  := real_discount_rate*(1+real_discount_rate)^life_cdri /((1+real_discount_rate)^life_cdri -1);
param crf_ngdri := real_discount_rate*(1+real_discount_rate)^life_ngdri/((1+real_discount_rate)^life_ngdri-1);
param crf_h2dri := real_discount_rate*(1+real_discount_rate)^life_h2dri/((1+real_discount_rate)^life_h2dri-1);
param crf_scrap := real_discount_rate*(1+real_discount_rate)^life_scrap/((1+real_discount_rate)^life_scrap-1);

# --- Annualised capital charge per unit route output (bundled over the route's
#     process chain; reuses the existing n*_capex levelized figures). DRI routes
#     divide by (1-n7_phi_eaf) to align the DRI plant / pellet / shared-EAF capex
#     with the coaldri/ngdri/h2dri_output basis (each DRI route carries its EAF share).
param acapex_bof   := n0_capex + n1_capex + ng_capex_pell + n2_capex + n3_capex;          # $/tCS/yr
param acapex_cdri  := (n4_capex_coal + ng_capex_pell + n7_capex)/(1 - n7_phi_eaf);
param acapex_ngdri := (n5_capex_ng   + ng_capex_pell + n7_capex)/(1 - n7_phi_eaf);
param acapex_h2dri {t in T} := (n6_capex_h2[t] + ng_capex_pell + n7_capex)/(1 - n7_phi_eaf);
param acapex_scrap := n8_capex;                                                           # $/tCS/yr

# --- Overnight capex per unit capacity = annualised charge / CRF.
param ocapex_bof   := acapex_bof   / crf_bof;
param ocapex_cdri  := acapex_cdri  / crf_cdri;
param ocapex_ngdri := acapex_ngdri / crf_ngdri;
param ocapex_h2dri {t in T} := acapex_h2dri[t] / crf_h2dri;
param ocapex_scrap := acapex_scrap / crf_scrap;

# Scrap supply-chain expansion capex (collection + high-end processing/purification
# yards), overnight $/(t scrap/yr). ~$100/t-cap reflects shredding + sensor-sorting
# + copper/tramp purification (furnace-ready scrap), not just collection. Charged on
# growth in scrap-handling capacity above the 2025 baseline (v_capacity.mod). Operating
# cost + the existing chain are already embedded in the delivered scrap price.
# Plain data param -> sweep with `let ocapex_scrapchain := X;`.
param ocapex_scrapchain default 100;

# (Fixed opex is the labour+maintenance figure declared above as fopex_*,
#  charged on installed capacity in v_capacity.mod; no %-of-capex term.)

# --- Production ramp as a FIXED annual slab (NOT a compounding %): the max YoY
#     change is ramp_frac * the route's pinned 2025 production. Reflects that
#     capacity additions are limited by ~constant annual capital availability,
#     not by current fleet size. Tunable lever (typically 0.15-0.20). H2-DRI is
#     exempt (future entrant; governed by the H2 availability mechanism).
param ramp_frac default 0.15;

# Ablation toggle for the sunk-capital effect:
#   sunk=1 (default, real model): capex on BUILDS, fixed opex on CAPACITY -> capital
#     committed once built; idling/stranding does not recover it.
#   sunk=0 (counterfactual): capex + fixed opex charged on PRODUCTION (old LCOE style),
#     so building-then-idling costs nothing -> the optimizer can switch tech freely.
param sunk default 1;

# --- CCS retrofit: same overnight-capex + fixed/variable-opex structure as routes.
#     n10_ccs_cost ($/tCO2) is the NON-ENERGY capital+O&M figure; energy is charged
#     separately as power_ccs*ng_cost_power (so CCS cost AND emissions both respond
#     to the grid-EF scenario, and the old uncosted-CCS-power gap is closed).
param life_ccs default 15;                       # retrofit asset life (yr)
param crf_ccs := real_discount_rate*(1+real_discount_rate)^life_ccs/((1+real_discount_rate)^life_ccs-1);
param ccs_capex_share default 0.80;              # capex fraction of n10_ccs_cost (rest = fixed O&M)
param ocapex_ccs {t in T} := ccs_capex_share * n10_ccs_cost[t] / crf_ccs;   # overnight $/tCO2-capacity
param fom_ccs    {t in T} := (1 - ccs_capex_share) * n10_ccs_cost[t];       # fixed O&M $/tCO2-cap/yr
param ccs_vopex_solvent default 5;               # non-energy variable opex $/tCO2 (solvent makeup; placeholder)

# --- Stream-specific CCS adjustment: capture cost & energy depend on the stream's
#     CO2 concentration. Multiplier scales the base ocapex_ccs/fom_ccs; ccs_kwh_* is
#     per-stream capture energy (kWh/tCO2, feeds both cost and Scope-2 consistently).
#     NG-DRI typically cheapest (concentrated, already-separated process CO2);
#     coal-DRI dearest (dilute kiln gas); BF-BOF mid (concentrated BFG).
param ccs_mult_bf    default 1.0;    # baseline (concentrated BFG ~20-25% CO2)
param ccs_mult_cdri  default 1.2;    # dilute rotary-kiln off-gas -> dearer
param ccs_mult_ngdri default 0.5;    # near-pure CO2 already separated in process gas -> cheap
param ccs_kwh_bf     default 800;
param ccs_kwh_cdri   default 850;    # dilute -> more capture energy
param ccs_kwh_ngdri  default 200;    # mostly compression of the separated stream

