# =====================================================================
# structural-sensitivity/whr study: common backdrop.
#
# "WHR-CCS integration": across joint CCS+grid ecosystem maturity (ONE
# theta applied to BOTH theta_ccs and theta_grid), what does integrating
# waste-heat-recovery steam into CCS regen save vs boiler-only steam?
# whr_ccs_integration (1=integrated/0=boiler-only, core/modules/o_waste_heat.mod)
# is now `let whr_ccs_integration := 0;` for the boiler-only mode instead of
# a forked module copy.
#
# Applied on top of core/model.mod, before the swept theta_ccs/theta_grid
# (joint) and whr_ccs_integration -- both plain scalar overrides, no
# axes/*.mod files needed for this study.
#
# Run from the REPOSITORY ROOT (see core/model.mod for the contract).
# =====================================================================

# Label for the CSV row ("integrated"/"boiler-only"); the driver sets this.
param MODE_LABEL symbolic default "unlabelled";

let theta_tech := 0.5;

# H2 debut year fixed at central 2030 -- h2_peak_year (2035) follows
# automatically as a DERIVED param in core/definitions.mod; do NOT `let` it.
let ng_h2_start_year := 2030;

let n8_scrap_rate := 0.06;
let cap_add_common := 15000000;   # Medium ramp
let h2_ref_cap     := 6000000;    # Medium H2 envelope
let {t in T} n5_cost_NG[t] := 10;

# avg_emi := 1.8 matches core's own default; not restated as a let since
# the old whr_template.mod also relied on the default rather than setting it.
