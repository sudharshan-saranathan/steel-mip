# =====================================================================
# structural-sensitivity/scrap study: common backdrop.
#
# "Scrap-growth study": as scrap availability increases, does it displace
# hydrogen or CCS? Fixed central config (theta_*, H2 timing, grid EF, Medium
# ramp, NG price) with scrap growth rate and the emissions target swept.
#
# Applied on top of core/model.mod, before the swept avg_emi / n8_scrap_rate
# (both plain scalar overrides -- no axes/*.mod files needed for this study).
#
# Run from the REPOSITORY ROOT (see core/model.mod for the contract).
# =====================================================================

# Central technology/grid/CCS learning (matches core defaults; restated for
# clarity, mirroring the old scrap_template.mod backdrop).
let theta_tech := 0.5;
let theta_grid := 0.5;
let theta_ccs  := 0.5;

# H2 debut year fixed at central 2030 -- h2_peak_year (2035) follows
# automatically as a DERIVED param in core/definitions.mod; do NOT `let` it.
let ng_h2_start_year := 2030;

# Explicit 2050 grid EF target (bypasses the theta_grid back-solve the grid
# study uses -- this param is mutable, so a direct override is valid).
let n9_grid_ef_end := 0.0005;

# Medium build ramp (peak H2 1.5 Mt-H2/yr).
let cap_add_common := 15000000;
let h2_ref_cap     := 6000000;

let {t in T} n5_cost_NG[t] := 10;
