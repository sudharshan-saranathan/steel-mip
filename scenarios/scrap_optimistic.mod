# Scrap-availability regime: OPTIMISTIC
# 2025 base cap 35 Mt (calibrated to actual 2025 route mix; common to all
# regimes), fast growth 6%/yr  (-> ~150 Mt by 2050). Scrap supply expands quickly.
# Included after parameters.mod (overrides the scrap block there), exactly
# like the NG-availability scenario files override n5_ng_cap[t].
let n8_scrap_rate            := 0.06;
let n8_scrap_limit[first(T)] := 35000000;
let {t in T: ord(t) > 1}
    n8_scrap_limit[t] := n8_scrap_limit[prev(t)] * (1 + n8_scrap_rate);
