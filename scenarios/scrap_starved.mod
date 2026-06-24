# Scrap-availability regime: STARVED
# 2025 base cap 35 Mt (calibrated to actual 2025 route mix; common to all
# regimes), near-stagnant growth 0.5%/yr  (-> ~40 Mt by 2050). Scrap supply
# barely grows while steel demand grows 5%/yr, so the scrap share shrinks.
# NOTE: this regime stresses the avg_emi target hardest. Combined with a
# delayed H2 start (2040/2045), honouring 1.6 tCO2/t can become INFEASIBLE
# -- no technology mix satisfies the target.
# Included after parameters.mod (overrides the scrap block there), exactly
# like the NG-availability scenario files override n5_ng_cap[t].
let n8_scrap_rate            := 0.005;
let n8_scrap_limit[first(T)] := 35000000;
let {t in T: ord(t) > 1}
    n8_scrap_limit[t] := n8_scrap_limit[prev(t)] * (1 + n8_scrap_rate);
