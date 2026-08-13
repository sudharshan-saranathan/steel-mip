# =====================================================================
# Import-dependence study: common backdrop.
#
# Applied on top of core/model.mod, before the per-run axis files and the
# swept H2 debut year. Pure parameter overrides -- no structure.
#
# Run from the REPOSITORY ROOT (see core/model.mod for the contract).
# =====================================================================

# Label for the CSV row; the driver sets this per run.
param REGIME symbolic default "unlabelled";

# Mid-range technology/grid/CCS learning on every axis
let theta_tech := 0.5;
let theta_grid := 0.5;
let theta_ccs  := 0.5;

# Cumulative-average CO2-intensity cap, tCO2/tCS
let avg_emi := 1.8;

# Medium build ramp
let cap_add_common := 15000000;
let h2_ref_cap     := 6000000;

# Scrap growth. n8_scrap_limit is DERIVED from this in core/definitions.mod
# and recomputes automatically -- do not re-run the recursion here.
let n8_scrap_rate := 0.06;

# NG price, $/MMBtu-equivalent basis used by the cost module
let {t in T} n5_cost_NG[t] := 10;
