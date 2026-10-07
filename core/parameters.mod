# Technology learning
let theta_grid := 0.5;    # 1 means clean/mature grid ecosystem
let theta_tech := 0.5;    # 1 means cheap/matured hydrogen ecosystem
let theta_ccs  := 0.5;    # 1 means cheap/matured CCS ecosystem

# Crude Steel Production
let base_demand := 152200000;
let growth_rate := 0.05;
param avg_emi   default 1.8;  # cumulative average CO2-intensity CAP, tCO2/tCS

# NG DRI
let {t in T} n5_cost_NG[t] := 12;   # [audit] was 10
# Shock period (2035–2040): only for shock case it is 1.5 times
# let {t in 2035..2040} n5_cost_NG[t] := 22.5;

# H2 DRI
let ng_h2_start_year := 2030;
param H2_cap := 1500000; # Capacity slab per year
# AMPL re-instantiates this indexing set whenever ng_h2_start_year is `let`,
# including after a prior solve -- so scenarios may override the debut year freely.
s.t. No_H2_Before{t in T: t < ng_h2_start_year}:
    h2dri_h2_in[t] = 0;
# h2_peak_year is derived in definitions.mod; it follows ng_h2_start_year.

# Scrap
let n8_scrap_rate := 0.05;   # [audit] was 0.06      # Assumed annual growth rate of scrap
let ng_cost_scrap :=400;        # [audit] was 350
let n8_scrap_seed := 37000000;  # scrap availability in 2025, t/yr
# n8_scrap_limit is derived in definitions.mod from the seed and the rate.

# CCS
let n10_ccs_cost_start := 75;    # [audit CCS] India all-in 2025 (see definitions.mod). Was 125

# NG cap (Shock case) [audit] scaled x 0.35: steel share of national gas 10 % -> 3.5 % (see structural/axes/ng_bau.mod)
let n5_ng_cap[2025] := 1871993;
let n5_ng_cap[2026] := 2049836;
let n5_ng_cap[2027] := 2220356;
let n5_ng_cap[2028] := 2398042;
let n5_ng_cap[2029] := 2634161;
let n5_ng_cap[2030] := 2902883;
let n5_ng_cap[2031] := 3138503;
let n5_ng_cap[2032] := 3333199;
let n5_ng_cap[2033] := 3560419;
let n5_ng_cap[2034] := 3824861;
let n5_ng_cap[2035] := 2744779;
let n5_ng_cap[2036] := 2799694;
let n5_ng_cap[2037] := 2865870;
let n5_ng_cap[2038] := 2905193;
let n5_ng_cap[2039] := 2943859;
let n5_ng_cap[2040] := 3048071;
let n5_ng_cap[2041] := 4102639;
let n5_ng_cap[2042] := 4392150;
let n5_ng_cap[2043] := 4736445;
let n5_ng_cap[2044] := 5082971;
let n5_ng_cap[2045] := 5421859;
let n5_ng_cap[2046] := 5818208;
let n5_ng_cap[2047] := 6279263;
let n5_ng_cap[2048] := 6720368;
let n5_ng_cap[2049] := 7243609;
let n5_ng_cap[2050] := 7669069;
