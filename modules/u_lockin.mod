# ============================================================================
# Capacity lock-in (hard constraint; no cost term)
# ----------------------------------------------------------------------------
# Newly built capacity must stay online for a route-specific lock-in horizon and
# cannot be retired early. Capacity is proxied by the route production level;
# a "build" in year t is the positive year-on-year increase in that level.
#
#   expand_X[t] >= X[t] - X[t-1]        (capacity added in year t; >= 0)
#
# expand_X carries no cost and appears only (with a negative sign) in the lock-in
# floor below, so the optimizer keeps it pinned at the positive part of the change.
#
# Lock-in floor: the level must stay at least as large as the sum of builds that
# are still inside their L-year window:
#
#   X[s] >= sum_{ j : s-L+1 <= j <= s-1 } expand_X[j]
#
# This permits retiring OLDER capacity (level may fall) but never the locked-in
# new builds themselves (retire-oldest-first). Legacy capacity (the first-year
# level) is never a "build", so the incumbent fleet can still be phased out; only
# increases from 2026 onward are locked. A late rebuild therefore commits for L
# years, which discourages build-then-strand behaviour.
#
# Horizons reflect capital longevity / flexibility (all tunable):
# ============================================================================
param lockin_bof   default 25;   # BF-BOF (integrated, longest-lived capital)
param lockin_cdri  default 20;   # Coal-DRI
param lockin_ngdri default 15;   # NG-DRI
param lockin_h2dri default 15;   # H2-DRI
param lockin_scrap default 10;   # Scrap-EAF (modular, most flexible)

# --- builds (capacity added) per route ---
var expand_bof   {t in T} >= 0;
var expand_cdri  {t in T} >= 0;
var expand_ngdri {t in T} >= 0;
var expand_h2dri {t in T} >= 0;
var expand_scrap {t in T} >= 0;

s.t. build_bof   {t in T: ord(t) > 1}: expand_bof[t]   >= steel_bof[t]       - steel_bof[prev(t)];
s.t. build_cdri  {t in T: ord(t) > 1}: expand_cdri[t]  >= coaldri_output[t]  - coaldri_output[prev(t)];
s.t. build_ngdri {t in T: ord(t) > 1}: expand_ngdri[t] >= ngdri_output[t]    - ngdri_output[prev(t)];
s.t. build_h2dri {t in T: ord(t) > 1}: expand_h2dri[t] >= h2dri_output[t]    - h2dri_output[prev(t)];
s.t. build_scrap {t in T: ord(t) > 1}: expand_scrap[t] >= steel_scrap_eaf[t] - steel_scrap_eaf[prev(t)];

# --- lock-in floors: keep all builds still inside their L-year window ---
s.t. lockin_bof_floor {s in T: ord(s) > 1}:
    steel_bof[s] >=
        sum{j in T: ord(j) >= ord(s)-lockin_bof+1 and ord(j) <= ord(s)-1 and ord(j) > 1} expand_bof[j];

s.t. lockin_cdri_floor {s in T: ord(s) > 1}:
    coaldri_output[s] >=
        sum{j in T: ord(j) >= ord(s)-lockin_cdri+1 and ord(j) <= ord(s)-1 and ord(j) > 1} expand_cdri[j];

s.t. lockin_ngdri_floor {s in T: ord(s) > 1}:
    ngdri_output[s] >=
        sum{j in T: ord(j) >= ord(s)-lockin_ngdri+1 and ord(j) <= ord(s)-1 and ord(j) > 1} expand_ngdri[j];

s.t. lockin_h2dri_floor {s in T: ord(s) > 1}:
    h2dri_output[s] >=
        sum{j in T: ord(j) >= ord(s)-lockin_h2dri+1 and ord(j) <= ord(s)-1 and ord(j) > 1} expand_h2dri[j];

s.t. lockin_scrap_floor {s in T: ord(s) > 1}:
    steel_scrap_eaf[s] >=
        sum{j in T: ord(j) >= ord(s)-lockin_scrap+1 and ord(j) <= ord(s)-1 and ord(j) > 1} expand_scrap[j];
