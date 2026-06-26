# ============================================================================
# Capacity-expansion framework  (branch: capex-opex-framework)
# ----------------------------------------------------------------------------
# Replaces the LCOE-style per-tonne capital charge (n*_capex * production) with
# a real capacity stock:
#   - capacity per route is built (build_X) and bounds production (prod <= cap),
#   - CAPEX is OVERNIGHT, charged on the build in the year it is made (sunk;
#     never refunded by idling),  see capex_cost_def in r_cost.mod,
#   - FIXED OPEX is charged on installed capacity each year (fom_*),
#   - the 2025 incumbent fleet (legacy_X) is a non-increasing stock under a
#     linearly declining ceiling that reaches 0 in 2050 (gentle ~4%/yr phase-out;
#     optimizer may retire FASTER under decarbonisation pressure, never slower).
#
# This module SUPERSEDES u_lockin.mod: a build commits capex + fixed opex for the
# asset life, which discourages build-then-strand economically rather than via a
# forced production floor.
#
# Capacity is tracked on each route's primary OUTPUT variable (the same five the
# old lock-in proxy used).  Note the DRI routes' variables (coaldri_output,
# ngdri_output, h2dri_output) are on the crude-steel-equivalent (0.9*steel_eaf)
# basis; the 2025 seeds (parameters.mod) are converted accordingly.
# ============================================================================

# --- build (capacity added in year t) ---
var build_bof   {T} >= 0;
var build_cdri  {T} >= 0;
var build_ngdri {T} >= 0;
var build_h2dri {T} >= 0;
var build_scrap {T} >= 0;

# --- surviving incumbent (2025) fleet ---
var legacy_bof   {T} >= 0;
var legacy_cdri  {T} >= 0;
var legacy_ngdri {T} >= 0;
var legacy_h2dri {T} >= 0;
var legacy_scrap {T} >= 0;

# --- total installed capacity ---
var cap_bof   {T} >= 0;
var cap_cdri  {T} >= 0;
var cap_ngdri {T} >= 0;
var cap_h2dri {T} >= 0;
var cap_scrap {T} >= 0;

# --- annual cost pieces fed to total_cost_def (r_cost.mod) ---
var capex_cost   {T} >= 0;   # overnight capex booked on this year's builds
var fixopex_cost {T} >= 0;   # fixed O&M on installed capacity

# --- scrap supply-chain (collection + processing yards) ---
# Operating cost and the EXISTING chain are already in the delivered scrap price
# (ng_cost_scrap). Here we charge only the SUNK capital to GROW scrap-handling
# capacity above the 2025 baseline (overnight ocapex_scrapchain, $/t-scrap/yr).
# Capacity is monotone -> once built it cannot be un-built (sunk, strandable).
var scrapchain_cap   {T} >= 0;   # scrap-handling capacity (t scrap/yr)
var build_scrapchain {T} >= 0;   # capacity added this year (t scrap/yr)

# ----------------------------------------------------------------------------
# Capacity stock:  cap = surviving legacy + builds still within their life L.
# A build in year j contributes until year j+L-1, then retires automatically.
# ----------------------------------------------------------------------------
s.t. cap_def_bof{t in T}:
    cap_bof[t] = legacy_bof[t]
      + sum{j in T: ord(j) <= ord(t) and ord(j) >= ord(t)-life_bof+1}   build_bof[j];
s.t. cap_def_cdri{t in T}:
    cap_cdri[t] = legacy_cdri[t]
      + sum{j in T: ord(j) <= ord(t) and ord(j) >= ord(t)-life_cdri+1}  build_cdri[j];
s.t. cap_def_ngdri{t in T}:
    cap_ngdri[t] = legacy_ngdri[t]
      + sum{j in T: ord(j) <= ord(t) and ord(j) >= ord(t)-life_ngdri+1} build_ngdri[j];
s.t. cap_def_h2dri{t in T}:
    cap_h2dri[t] = legacy_h2dri[t]
      + sum{j in T: ord(j) <= ord(t) and ord(j) >= ord(t)-life_h2dri+1} build_h2dri[j];
s.t. cap_def_scrap{t in T}:
    cap_scrap[t] = legacy_scrap[t]
      + sum{j in T: ord(j) <= ord(t) and ord(j) >= ord(t)-life_scrap+1} build_scrap[j];

# ----------------------------------------------------------------------------
# Legacy retirement: non-increasing, under a linearly declining ceiling that
# hits 0 in 2050.  Optimizer may sit below the ceiling (retire faster).
# ----------------------------------------------------------------------------
s.t. legacy_ceil_bof  {t in T}: legacy_bof[t]   <= cap0_bof   * (2050 - t)/25;
s.t. legacy_ceil_cdri {t in T}: legacy_cdri[t]  <= cap0_cdri  * (2050 - t)/25;
s.t. legacy_ceil_ngdri{t in T}: legacy_ngdri[t] <= cap0_ngdri * (2050 - t)/25;
s.t. legacy_ceil_h2dri{t in T}: legacy_h2dri[t] <= cap0_h2dri * (2050 - t)/25;
s.t. legacy_ceil_scrap{t in T}: legacy_scrap[t] <= cap0_scrap * (2050 - t)/25;

s.t. legacy_noninc_bof  {t in T: ord(t)>1}: legacy_bof[t]   <= legacy_bof[prev(t)];
s.t. legacy_noninc_cdri {t in T: ord(t)>1}: legacy_cdri[t]  <= legacy_cdri[prev(t)];
s.t. legacy_noninc_ngdri{t in T: ord(t)>1}: legacy_ngdri[t] <= legacy_ngdri[prev(t)];
s.t. legacy_noninc_h2dri{t in T: ord(t)>1}: legacy_h2dri[t] <= legacy_h2dri[prev(t)];
s.t. legacy_noninc_scrap{t in T: ord(t)>1}: legacy_scrap[t] <= legacy_scrap[prev(t)];

# --- pin the 2025 incumbent stock to the seed: the fleet physically exists, so
#     2025 capacity = seed (production runs below it; idle capacity pays fixed opex).
s.t. legacy_init_bof:   legacy_bof[first(T)]   = cap0_bof;
s.t. legacy_init_cdri:  legacy_cdri[first(T)]  = cap0_cdri;
s.t. legacy_init_ngdri: legacy_ngdri[first(T)] = cap0_ngdri;
s.t. legacy_init_h2dri: legacy_h2dri[first(T)] = cap0_h2dri;
s.t. legacy_init_scrap: legacy_scrap[first(T)] = cap0_scrap;

# ----------------------------------------------------------------------------
# Production bounded by installed capacity.
# ----------------------------------------------------------------------------
s.t. cap_lim_bof  {t in T}: steel_bof[t]       <= cap_bof[t];
s.t. cap_lim_cdri {t in T}: coaldri_output[t]  <= cap_cdri[t];
s.t. cap_lim_ngdri{t in T}: ngdri_output[t]    <= cap_ngdri[t];
s.t. cap_lim_h2dri{t in T}: h2dri_output[t]    <= cap_h2dri[t];
s.t. cap_lim_scrap{t in T}: steel_scrap_eaf[t] <= cap_scrap[t];

# ----------------------------------------------------------------------------
# Cost pieces (consumed by total_cost_def in r_cost.mod).
#   capex_cost   = overnight capex on this year's builds (full amount, at build
#                  year; the residual-life salvage credit is taken in the
#                  objective, see main.mod).
#   fixopex_cost = fixed O&M (fraction of overnight capex) on installed capacity.
# ----------------------------------------------------------------------------
# scrap-chain capacity must cover total scrap throughput (all 3 streams: scrap-EAF
# charge + BOF scrap + DRI-EAF scrap charge). 2025 capacity is pinned to that
# year's throughput (legacy, free); growth above it pays sunk capex. Monotone.
s.t. scrapchain_legacy{t in T: ord(t) = 1}:
    scrapchain_cap[t] = bof_scrap_in[t] + eaf_scrap_in[t] + scrap_eaf_scrap_in[t];
s.t. scrapchain_cover{t in T: ord(t) > 1}:
    scrapchain_cap[t] >= bof_scrap_in[t] + eaf_scrap_in[t] + scrap_eaf_scrap_in[t];
s.t. scrapchain_mono{t in T: ord(t) > 1}:
    scrapchain_cap[t] >= scrapchain_cap[prev(t)];
s.t. scrapchain_build_def{t in T: ord(t) > 1}:
    build_scrapchain[t] >= scrapchain_cap[t] - scrapchain_cap[prev(t)];

s.t. capex_cost_def{t in T}:
    capex_cost[t] =
      sunk * (   ocapex_bof      * build_bof[t]          # sunk: overnight capex on builds
               + ocapex_cdri     * build_cdri[t]
               + ocapex_ngdri    * build_ngdri[t]
               + ocapex_h2dri[t] * build_h2dri[t]
               + ocapex_scrap    * build_scrap[t]
               + ocapex_scrapchain * build_scrapchain[t] )  # scrap collection+yard expansion
    + (1-sunk) * ( acapex_bof    * steel_bof[t]          # not sunk: annualized capex on production
               + acapex_cdri     * coaldri_output[t]
               + acapex_ngdri    * ngdri_output[t]
               + acapex_h2dri[t] * h2dri_output[t]
               + acapex_scrap    * steel_scrap_eaf[t] );

# Fixed opex (labour + maintenance) on installed capacity, crude-steel basis.
# DRI-route capacities are on the 0.9*steel_eaf basis, so divide by (1-n7_phi_eaf)
# to recover crude-steel capacity before applying the per-tCS fixed-opex rate.
s.t. fixopex_cost_def{t in T}:
    fixopex_cost[t] =
      sunk * (   fopex_bof   * cap_bof[t]                          # sunk: fixed opex on capacity
               + fopex_cdri  * cap_cdri[t]  / (1 - n7_phi_eaf)
               + fopex_ngdri * cap_ngdri[t] / (1 - n7_phi_eaf)
               + fopex_h2dri * cap_h2dri[t] / (1 - n7_phi_eaf)
               + fopex_scrap * cap_scrap[t] )
    + (1-sunk) * ( fopex_bof   * steel_bof[t]                      # not sunk: fixed opex on production
               + fopex_cdri  * coaldri_output[t]  / (1 - n7_phi_eaf)
               + fopex_ngdri * ngdri_output[t] / (1 - n7_phi_eaf)
               + fopex_h2dri * h2dri_output[t] / (1 - n7_phi_eaf)
               + fopex_scrap * steel_scrap_eaf[t] );

# ============================================================================
# CCS retrofit capacity (sunk capex; legacy = 0, no CCS in 2025). Mirrors the
# route framework: capture <= installed capture capacity, built via build_ccs_X
# over a life_ccs-year retrofit life. Cost lives in r_cost.mod (cost_ccs_def);
# the physical-capture and deployment-ceiling limits stay in q_carbon_capture.mod.
# ============================================================================
var build_ccs_bf   {T} >= 0;
var build_ccs_cdri {T} >= 0;
var build_ccs_ngdri{T} >= 0;
var ccs_cap_bf     {T} >= 0;
var ccs_cap_cdri   {T} >= 0;
var ccs_cap_ngdri  {T} >= 0;

s.t. ccs_cap_def_bf{t in T}:
    ccs_cap_bf[t]    = sum{j in T: ord(j)<=ord(t) and ord(j)>=ord(t)-life_ccs+1} build_ccs_bf[j];
s.t. ccs_cap_def_cdri{t in T}:
    ccs_cap_cdri[t]  = sum{j in T: ord(j)<=ord(t) and ord(j)>=ord(t)-life_ccs+1} build_ccs_cdri[j];
s.t. ccs_cap_def_ngdri{t in T}:
    ccs_cap_ngdri[t] = sum{j in T: ord(j)<=ord(t) and ord(j)>=ord(t)-life_ccs+1} build_ccs_ngdri[j];

s.t. ccs_caplim_bf{t in T}:    ccs_bf[t]    <= ccs_cap_bf[t];
s.t. ccs_caplim_cdri{t in T}:  ccs_cdri[t]  <= ccs_cap_cdri[t];
s.t. ccs_caplim_ngdri{t in T}: ccs_ngdri[t] <= ccs_cap_ngdri[t];
