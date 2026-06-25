# ==================================================
# Crude Steel Production
# ==================================================
let base_demand := 152200000;
let growth_rate := 0.05;
param avg_emi   default 1.75;  # uniform cumulative ET across all regimes (overridable via MC_AVG_EMI)
#let emi_limit :=1.5353;

# ==================================================
# NG DRI
# ==================================================
# Normal price
let {t in T} n5_cost_NG[t] := 10;


# Shock period (2035–2040): only for shock case it is 1.5 times
#let {t in 2035..2040} n5_cost_NG[t] := 22.5;

# ==================================================
# H2 DRI
# ==================================================
let ng_cost_h2_start := 4500;        # Cost of hydrogen per ton at 2025
let ng_cost_h2_end := 1000;          # Cost of hydrogen per ton by 2050
let ng_h2_start_year := 2030;
# ==================================================
# EAF (Scrap-Based)
# ==================================================
let n8_scrap_rate := 0.04;      # Assumed annual growth rate of scrap
let ng_cost_scrap :=350;        #Assumed scrap cost
let n8_scrap_limit[first(T)] := 35000000;

let {t in T: ord(t) > 1}
    n8_scrap_limit[t] :=
        n8_scrap_limit[prev(t)] * (1 + n8_scrap_rate);

# ==================================================
# Waste Heat Recovery
# ==================================================
let n9_grid_ef_end := 0.0003;      # Projected Grid emission factor by 2050

# ==================================================
# Carbon Capture
# ==================================================
let n10_ccs_cost_start := 125;   # Carbon capture cost per ton in 2025
let n10_ccs_cost_end := 75;      # Projected carbon capture cost in 2050


#Hydrogen availability cap
param H2_cap := 1500000;
s.t. No_H2_Before{t in T: t < ng_h2_start_year}:
    h2dri_h2_in[t] = 0;
    
s.t. H2_growth_cap{t in T: t = ng_h2_start_year}:
    h2dri_h2_in[t] <= H2_cap;

# H2 availability is a FIXED additive slab (NOT CAGR): hydrogen input starts at the
# initial availability (H2_cap, via H2_growth_cap) and grows by at most ramp_frac *
# H2_cap per year. Replaces the old max(1.15*prev, H2_cap) compounding limiter.
s.t. H2_growth_limit{t in T: t > ng_h2_start_year}:
    h2dri_h2_in[t] - h2dri_h2_in[prev(t)] <= ramp_frac * H2_cap;


#Natural gas cap (10% of availability of national scale)
#Policy case


#BAU Values
#let n5_ng_cap[2025] := 5348550;
#let n5_ng_cap[2026] := 5417100;
#let n5_ng_cap[2027] := 5568150;
#let n5_ng_cap[2028] := 5794875;
#let n5_ng_cap[2029] := 6105525;
#let n5_ng_cap[2030] := 6263250;
#let n5_ng_cap[2031] := 6426450;
#let n5_ng_cap[2032] := 6758475;
#let n5_ng_cap[2033] := 7023225;
#let n5_ng_cap[2034] := 7182600;
#let n5_ng_cap[2035] := 7439175;
#let n5_ng_cap[2036] := 7611600;
#let n5_ng_cap[2037] := 7790250;
#let n5_ng_cap[2038] := 8039325;
#let n5_ng_cap[2039] := 8101350;
#let n5_ng_cap[2040] := 8187450;
#let n5_ng_cap[2041] := 8385525;
#let n5_ng_cap[2042] := 8550600;
#let n5_ng_cap[2043] := 8842950;
#let n5_ng_cap[2044] := 9033300;
#let n5_ng_cap[2045] := 9186600;
#let n5_ng_cap[2046] := 9607350;
#let n5_ng_cap[2047] := 9884775;
#let n5_ng_cap[2048] := 10197600;
#let n5_ng_cap[2049] := 10385400;
#let n5_ng_cap[2050] := 10662075;

#Shock case

let n5_ng_cap[2025] := 5348550;
let n5_ng_cap[2026] := 5856675;
let n5_ng_cap[2027] := 6343875;
let n5_ng_cap[2028] := 6851550;
let n5_ng_cap[2029] := 7526175;
let n5_ng_cap[2030] := 8293950;
let n5_ng_cap[2031] := 8967150;
let n5_ng_cap[2032] := 9523425;
let n5_ng_cap[2033] := 10172625;
let n5_ng_cap[2034] := 10928175;
let n5_ng_cap[2035] := 7842225;
let n5_ng_cap[2036] := 7999125;
let n5_ng_cap[2037] := 8188200;
let n5_ng_cap[2038] := 8300550;
let n5_ng_cap[2039] := 8411025;
let n5_ng_cap[2040] := 8708775;
let n5_ng_cap[2041] := 11721825;
let n5_ng_cap[2042] := 12549000;
let n5_ng_cap[2043] := 13532700;
let n5_ng_cap[2044] := 14522775;
let n5_ng_cap[2045] := 15491025;
let n5_ng_cap[2046] := 16623450;
let n5_ng_cap[2047] := 17940750;
let n5_ng_cap[2048] := 19201050;
let n5_ng_cap[2049] := 20696025;
let n5_ng_cap[2050] := 21911625;


#let carbon_tax :=200;
#let emi_limit   := 0.75;