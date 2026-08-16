# =====================================================================
# structural-sensitivity/grid study: common backdrop.
#
# "Grid-offset requirement": for each (H2 start year, scrap growth rate),
# sweep the 2050 grid emission factor and find the dirtiest grid that still
# satisfies the emissions-intensity target. Grid EF and the industrial
# tariff are coupled outcomes of the same theta_grid learning parameter
# (see core/definitions.mod: n9_grid_ef_end, ng_cost_power), so the driver
# back-solves theta_grid from the swept target EF rather than setting a
# grid axis file directly -- keep that form (see run.py).
#
# Applied on top of core/model.mod, before the swept ng_h2_start_year /
# n8_scrap_rate / grid_ef_target (all plain scalar overrides, so no
# axes/*.mod files are needed for this study -- unlike import-dependence's
# large time-indexed tables).
#
# Run from the REPOSITORY ROOT (see core/model.mod for the contract).
# =====================================================================

# Fixed emissions-intensity target this study probes grid-offset against
# (readme.md: "the 1.8 tCO2/tCS emissions constraint"). Matches core's own
# default, restated here for clarity.
let avg_emi := 1.8;

# Target 2050 grid EF (tCO2/kWh) the driver is currently solving for; plain
# pass-through so report.mod can echo the SWEPT target next to the derived
# n9_grid_ef[2050] it produces (they coincide by construction at t=2050).
param grid_ef_target default n9_grid_ef_end;
