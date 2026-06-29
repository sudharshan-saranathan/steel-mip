
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
param n2_coke_hm_50 default 0.48;    # Coke (ton) per thm by 2050 (+0.04 vs 0.44: makes up the removed BF H2 co-injection, ~3 t coke / t H2 reduction-equivalent)
param n2_h2_hm_25 default 0;         # Hydrogen in blast furnace in 2025 (t/thm)
param n2_h2_hm_50 default 0;         # Hydrogen in blast furnace by 2050 (t/thm) -- BF H2 co-injection removed; H2-DRI is the only H2 consumer
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

# The former all-in delivered H2 price (ng_cost_h2_start/end -> ng_cost_h2) has been
# REMOVED: hydrogen capital is now explicit sunk electrolyser + renewable builds (see
# the green-H2 block at the end of this file and v_capacity.mod) and only a residual
# variable opex (h2_opex) remains in the price. The uncertainty axis is h2_capex_mult.
param ng_h2_start_year default 2040;
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
# Coking-coal availability ceiling (imported coke-making coal for BF; PCI and indigenous
# thermal DRI coal are NOT capped). Default 1e12 = effectively no limit, so runs without a
# coking scenario file behave as before; scarce/normal/abundant set via scenarios/ccoal_*.
param ccoal_cap {T} default 1e12;

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

# --- Per-route capacity-addition ceiling (max new build/yr as a fraction of the
# 2025 fleet, cap0_*). Fixed slab; replaces the old production ramp. Tech-specific
# supply-chain scale-up rates: BF-BOF slowest (imported coking coal + integrated
# greenfield mills); coal-DRI fastest (indigenous thermal coal); NG-DRI and scrap-EAF
# in between (and further bounded by NG / scrap availability curves). H2-DRI is not
# listed -- its build rate is set by the electrolyser Gaussian envelope (v_capacity.mod).
param cap_add_frac_bof   default 0.12;
param cap_add_frac_cdri  default 0.20;
param cap_add_frac_ngdri default 0.10;
param cap_add_frac_scrap default 0.448;   # ~15 Mt/yr (0.448 * 33.5 Mt 2025 fleet)

# --- Minimum capacity utilisation (private-player discipline): production must be at
# least util_min_X of installed capacity, i.e. the idle capacity-production gap is capped
# at 1-util_min_X. The rationale is ECONOMIC first, technical second:
#   - ECONOMIC: below a break-even utilisation, fixed costs (capital service + labour +
#     maintenance, all charged on capacity via fixopex_cost) spread over too few tonnes,
#     unit cost blows up, and a private operator runs at a loss -> they SHUT rather than
#     limp along. The floor encodes that discrete "operate above break-even or exit"
#     reality (the model already PRICES idling via fixed opex; the floor forbids the
#     loss-making low-utilisation branch a real owner would never choose). The "exit"
#     side is available to incumbents via faster legacy retirement; new builds are
#     committed for their life (the sunk-capital irreversibility), so for them it reads
#     "run above break-even or don't build it".
#   - TECHNICAL: this reinforces the ranking. BF-BOF highest (blast furnace runs baseload,
#     cannot be turned down without damage -> high break-even); scrap-EAF lowest
#     (batch/modular, cheaply idled -> low break-even); DRI shafts in between.
# Applied from 2026 on (the 2025 fleet is calibrated to observed shares and inherits real
# low utilisation, e.g. BF-BOF ~64%, so first(T) exempt).
param util_min_bof   default 0.85;
param util_min_cdri  default 0.75;
param util_min_ngdri default 0.70;
param util_min_h2dri default 0.70;
param util_min_scrap default 0.60;

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

# Fossil supply-network expansion capex (coal mines/transport; NG pipelines/terminals),
# overnight $/(t-fuel/yr), charged on growth in supply capacity above the 2025 baseline
# (v_capacity.mod). DEFAULT 0: these are MATURE networks whose capital is already
# absorbed in the delivered commodity prices (coking/non-coking/PCI coal, NG $/MMBtu),
# so by default they add no cost and the model is unchanged. Set > 0 to charge capex on
# fossil supply GROWTH (e.g. to test new mine/pipeline build-out under demand expansion);
# the framework is then symmetric with scrap and green-H2. Sweep with `let ocapex_* := X;`.
param ocapex_coalchain default 0;     # $/(t-coal/yr)
param ocapex_ngchain   default 0;     # $/(t-NG/yr)

# (Fixed opex is the labour+maintenance figure declared above as fopex_*,
#  charged on installed capacity in v_capacity.mod; no %-of-capex term.)

# --- Mode-1 (linear) electrolyser-capacity ramp coefficient: the additive ceiling on
#     cap_h2elec additions is ramp_frac * H2_cap per year (a fixed annual slab, NOT a
#     compounding %). Reflects ~constant annual capital availability. Sweep token RAMPVAL.
#     Typically 0.15. (Used only in mode 1; modes 0/2 set the ceiling value differently.)
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

# ============================================================================
# GREEN-H2 SUPPLY CHAIN: electrolyser + dedicated renewable (sunk capacity)
# ----------------------------------------------------------------------------
# The former all-in delivered H2 price (ng_cost_h2) dissolved the entire hydrogen
# supply chain into a smooth per-tonne cost, so the model could scale H2 up or down
# with NO capital commitment -- the one part of the transition exempt from the
# sunk-capital logic. This block splits it into:
#   (i)  SUNK CAPITAL, built and vintaged like a production route:
#          - electrolyser stacks         (cap_h2elec, t-H2/yr)
#          - dedicated renewable supply   (cap_h2re,   kW) that powers them
#        both charged on build_* with overnight capex in v_capacity.mod;
#   (ii) a small residual VARIABLE opex h2_opex (water + stack O&M). The green
#        electricity is now supplied by the dedicated renewables (sized to cover
#        the electrolyser load), NOT purchased at a $/t price -- so H2 stays green
#        and its power is behind-the-meter (excluded from the grid balance).
# Total green-H2 demand = DRI use (h2dri_h2_in) + BF injection (bf_h2_in).
# VALUES BELOW ARE PLACEHOLDERS in published 2024-25 ranges -- sweep them. Provenance:
#   electrolyser system capex ~$800-1200/kW (2024, alkaline/PEM) falling to a few
#     hundred $/kW by 2050 (IEA Global Hydrogen Review 2024; DOE PEM cost report);
#   electrolyser electricity ~50-55 kWh/kg incl. balance-of-plant;
#   solar PV $691/kW and onshore wind $1041/kW total installed cost (IRENA,
#     Renewable Power Generation Costs in 2024) -> blended hybrid used here.
# ============================================================================
param h2_kwh_per_t default 55000;     # electrolyser electricity, kWh per t H2 (~55 kWh/kg incl BoP)
param re_cf        default 0.45;      # dedicated renewable capacity factor (solar/wind hybrid)
param h2_opex{t in T} default 300;    # residual H2 variable opex (water + stack O&M), $/t H2
# Uncertainty multiplier on the green-H2 supply-chain overnight capex (electrolyser +
# renewable). This is the sweep/Monte-Carlo "H2 cost" axis now that the delivered-price
# ng_cost_h2 is retired: 1 = central placeholder trajectory, <1 cheaper, >1 dearer.
# Set via `let h2_capex_mult := X;` (template token H2CAPXVAL).
param h2_capex_mult default 1;

# --- Electrolyser: overnight capex $/kW (placeholder decline 2025->2050) ---
param h2elec_capex_kw{t in T} := 1000 + (400 - 1000)*(t-2025)/25;
param life_h2elec default 15;         # electrolyser plant life (incl stack replacement)
param crf_h2elec := real_discount_rate*(1+real_discount_rate)^life_h2elec/((1+real_discount_rate)^life_h2elec-1);
# Convert $/kW -> overnight $ per (t-H2/yr) of nameplate output at the renewable CF:
#   1 kW over a year at re_cf -> 8760*re_cf kWh -> / h2_kwh_per_t  t-H2/yr.
param ocapex_h2elec{t in T} := h2_capex_mult * h2elec_capex_kw[t] / (8760*re_cf/h2_kwh_per_t);
param acapex_h2elec{t in T} := ocapex_h2elec[t] * crf_h2elec;   # annualized (for the 1-sunk branch)
param fopex_h2elec default 400;       # fixed O&M, $/(t-H2/yr)/yr (placeholder ~3% of capex)

# --- Dedicated renewable generation: overnight capex $/kW (placeholder decline) ---
# Blended solar/wind hybrid, between IRENA 2024 solar ($691/kW) and onshore wind
# ($1041/kW) total installed costs, declining toward ~$450/kW by 2050.
param re_capex_kw{t in T} := 800 + (450 - 800)*(t-2025)/25;
param life_re default 25;             # renewable plant life
param crf_re := real_discount_rate*(1+real_discount_rate)^life_re/((1+real_discount_rate)^life_re-1);
param ocapex_h2re{t in T} := h2_capex_mult * re_capex_kw[t];    # overnight $/kW (charged on build, in kW)
param acapex_h2re{t in T} := ocapex_h2re[t] * crf_re;           # annualized $/kW/yr (for the 1-sunk branch)
param fopex_h2re default 15;          # fixed O&M, $/kW/yr (placeholder ~2% of capex)

# --- H2 ramp mode: how fast green H2 may scale. SAME formalism in every mode -- the
# electrolyser-capacity ceiling (and the four route cap_add ceilings) are always present;
# only the ceiling VALUE switches by mode. The model stays a pure LP throughout.
#   0: NO LIMITS -- every ceiling value = H2_BIGM (inf), on electrolysers AND the four
#      conventional routes. Unphysical counterfactual baseline (constraints' total effect).
#   1: LINEAR -- electrolyser-capacity ceiling = ramp_frac * H2_cap per year (fixed
#      additive slab); the four routes keep their cap_add slabs.
#   2 (default): RISING-BASELINE + GAUSSIAN-TRANSITION ceiling on the annual capacity ADDITION
#      (the ALLOWED EXPANSION). The yearly build is bounded by a fixed reference scale
#      times a (rising baseline + Gaussian surge) rate -- it does NOT compound off last
#      year's installed capacity:
#        cap[t] - cap[t-1] <= h2_ref_cap * ( base(t) + h2_gauss_amp * kernel(t) )
#        base(t)   = h2_base_start + (h2_base_end - h2_base_start) * (t-2025)/25
#        kernel(t) = exp( -(t - h2_peak_year)^2 / (2*h2_gauss_sigma^2) )
#      (i)  a RISING baseline: a fixed amount of capital buys MORE capacity over time as
#           logistics/manufacturing mature (the same capital-efficiency that already drives
#           the declining h2elec_capex_kw); so the floor tilts up h2_base_start -> h2_base_end.
#      (ii) a RAPID-TRANSITION surge at the peak year, tapering each side (a Gaussian
#           add-rate -> a smooth S-step in installed capacity). The surge amplitude is
#           PINNED so the TOTAL rate at the peak equals h2_peak_rate (25%):
#               surge_amp = h2_peak_rate - base(h2_peak_year)
#           i.e. base(peak) + surge_amp = h2_peak_rate exactly. A later peak (higher
#           baseline) therefore gets a smaller surge; the total peak is always 25%.
#      Because the baseline rises, the post-transition right tail sits permanently above the
#      pre-transition left tail (the visible "step" = the capital-efficiency gain). The peak
#      YEAR shifts per scenario; reference scale, baseline endpoints, peak rate and width fixed.
param h2_ramp_mode  default 2;          # 0 none (inf ceiling) | 1 linear | 2 gaussian (default, realistic)
param H2_BIGM       := 1e10;            # deactivates whichever limiter is off (~300x max cap)
param h2_ref_cap    := 10000000;        # fixed reference scale for mode-2 add-rates (t-H2/yr); peak add = 0.25*10 = 2.5 Mt-H2/yr
param h2_peak_rate  := 0.25;            # the pinned mode-2 peak rate (base(peak)+surge = 25%)
param h2_base_start := 0.00;            # mode 2 baseline coeff at 2025 (x h2_ref_cap, per yr)
param h2_base_end   := 0.05;            # mode 2 baseline coeff at 2050 (rising -> capital efficiency)
param h2_gauss_sigma := 2;              # Gaussian width (years); narrower -> sharper ramp, surge concentrated at peak
param h2_base{t in T} := h2_base_start + (h2_base_end - h2_base_start)*(t-2025)/25;  # rising baseline rate
# Scenario knob: year the buildout window crests. parameters.mod couples it to the H2
# debut (h2_peak_year := ng_h2_start_year + 5) once the start year is concrete; a driver
# may override it afterwards to treat the peak as a fully independent axis.
param h2_peak_year  default 2035;

