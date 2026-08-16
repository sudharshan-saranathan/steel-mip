# =====================================================================
# structural-sensitivity/abatement study: scenario-run backdrop.
#
# "Abatement anatomy": decomposes decarbonisation into H2/CCS/scrap/NG/
# grid/residual wedges by comparing 6 named policy scenarios against ONE
# common frozen-structure baseline (baseline.mod -- NOT this file; the
# baseline does not share this backdrop, see its own header).
#
# Applied on top of core/model.mod, before the per-run axes/*.mod (one per
# named scenario: ef1.6, ef1.8, s4, s8, rl, rh).
#
# Run from the REPOSITORY ROOT (see core/model.mod for the contract).
# =====================================================================

param REGIME symbolic default "unlabelled";

let theta_tech := 0.5;
let theta_grid := 0.5;
let theta_ccs  := 0.5;

# H2 debut year fixed at central 2030 -- h2_peak_year (2035) follows
# automatically as a DERIVED param in core/definitions.mod; do NOT `let` it.
let ng_h2_start_year := 2030;

let {t in T} n5_cost_NG[t] := 10;
