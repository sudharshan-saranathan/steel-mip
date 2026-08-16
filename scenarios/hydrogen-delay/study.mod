# =====================================================================
# Hydrogen-delay study: common backdrop.
#
# Applied on top of core/model.mod, before the per-run ramp axis file and
# the swept avg_emi / ng_h2_start_year. Pure parameter overrides -- no
# structure.
#
# The old h2delay_template.mod set no theta_* and no n5_cost_NG, relying
# on the template's own central defaults (theta_tech/grid/ccs = 0.5,
# n5_cost_NG = 10) -- core/parameters.mod already carries those same
# central values, so this backdrop is intentionally close to empty.
#
# Run from the REPOSITORY ROOT (see core/model.mod for the contract).
# =====================================================================

# Label for the CSV row; the driver sets this per run (the ramp level name).
param REGIME symbolic default "unlabelled";

# 6% annual scrap growth (readme.md's stated backdrop; matches core default).
let n8_scrap_rate := 0.06;
