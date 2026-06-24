# Scrap-availability regime: LOW
# 2025 base cap 35 Mt (calibrated to actual 2025 route mix; common to all
# regimes), slow growth 2%/yr  (-> ~57 Mt by 2050). Scrap supply stays tight.
# Included after parameters.mod (overrides the scrap block there), exactly
# like the NG-availability scenario files override n5_ng_cap[t].
let n8_scrap_rate            := 0.02;
let n8_scrap_limit[first(T)] := 35000000;
let {t in T: ord(t) > 1}
    n8_scrap_limit[t] := n8_scrap_limit[prev(t)] * (1 + n8_scrap_rate);
