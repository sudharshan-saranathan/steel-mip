# Initialization

# 2025 actual production split (pinned): BF-BOF 0.38, DRI-EAF 0.43 (coal:NG = 0.884:0.116
# -> coal 0.38, NG 0.05 of total steel), scrap-EAF 0.19. BF-BOF ~ Coal-DRI by design.
s.t. init_f_bof: f_bof[first(T)] = 0.38;
s.t. init_f_eaf: f_eaf[first(T)] = 0.43;
# Linearization: init coal-route share expressed on the route output (linear).
s.t. init_f_cdri: coaldri_output[first(T)] = 0.884 * dri_eaf_steel_out[first(T)];

# Linearization: no capture before 2027 expressed directly on the captured amount.
s.t. no_ccs_bf {t in T: t < 2027}:
    ccs_bf[t] = 0;

s.t. no_ccs_cdri {t in T: t < 2027}:
    ccs_cdri[t] = 0;

s.t. no_ccs_ngdri {t in T: t < 2027}:
    ccs_ngdri[t] = 0;
    
# Demand and availability Constraints
s.t. meet_demand{t in T}:
    total_steel[t] = base_demand * (1 + growth_rate)^(ord(t) - 1);

s.t. scrap_bound{t in T}:
    scrap_eaf_scrap_in[t] <= n8_scrap_limit[t];

s.t. ng_bound{t in T}:
   ngdri_ng_in[t] <= n5_ng_cap[t];

# Coking-coal availability: imported coke-making coal for BF is capped (ccoal_cap, set by
# scenarios/ccoal_*). PCI (bf_coalpci_in) and indigenous thermal DRI coal stay uncapped.
s.t. coking_coal_bound{t in T: t > first(T)}:
   coking_coal_in[t] <= ccoal_cap[t];

# (H2 deployment is governed by No_H2_Before (parameters.mod) + the electrolyser-capacity
#  ceiling in v_capacity.mod -- a value-switch by h2_ramp_mode: 0 none / 1 linear / 2 gaussian.)

# Policy constraint: cumulative average CO2-intensity CAP (upper bound only).
# The lifetime-average intensity must not EXCEED avg_emi (tCO2/tCS); the optimizer
# MAY overachieve (emit less) if that is cheaper -- this is a genuine carbon budget,
# not an iso-emission pin. Linearised by multiplying through by sum total_steel[t]
# (>= 0), so the feasible region is equivalent and linear.
s.t. avg_emis_cap_total:
    (sum {t in T} total_emissions[t]) <= avg_emi * (sum {t in T} total_steel[t]);


# Production-side ramp constraints REMOVED. Deployment speed is now limited at the
# PHYSICAL build rate instead: per-route capacity-addition ceilings in v_capacity.mod
# (cap_add_* = fixed slab, a tech-specific fraction of 2025 capacity per year),
# mirroring the H2 electrolyser envelope. Dispatch within the installed fleet is left
# free -- the sunk-capital mechanism (overnight capex + fixed O&M on capacity) already
# discourages production fluctuation, so an explicit production ramp was redundant.
# (The old +-ramp_frac*prod[2025] slabs and the 0.85 H2-DRI down-floor are gone.)

# Carbon-capture deployment pace is now governed by the sector-wide
# ccs_avail[t] ceiling in q_carbon_capture.mod (infrastructure/logistics ramp),
# which replaces the former per-route |Dccs| <= ramp*eta*capbase + slack limits.

# CCS phase-in switches REMOVED: the old dec_switch_* binaries forced each route's
# capture to be single-peaked (monotone up then down). That anti-churn role is now
# served economically by the CCS retrofit's sunk capex (build_ccs_* in v_capacity.mod),
# and the unimodality conflicted with capacity aging (it forbade rebuilding capture
# after a dip). Deployment pace is still bounded by ccs_avail (q_carbon_capture.mod).
# Dropping them removes the model's last binaries -> near-pure LP.
   
    
      