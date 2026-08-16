# =====================================================================
# structural-sensitivity/abatement study: common frozen-structure BASELINE.
#
# The single reference run every named policy scenario (axes/*.mod) is
# compared against. Self-contained -- does NOT include study.mod, since its
# H2/CCS/emissions-target/build-rate assumptions are deliberately different
# (H2 and CCS disabled, target non-binding, build unconstrained) so that
# the 2025 production structure is frozen through the whole horizon.
#
# Applied on top of core/model.mod, adds structural constraints (base_*,
# no_ccs) on top of it -- unlike a normal study.mod, this is NOT pure `let`.
#
# Run from the REPOSITORY ROOT (see core/model.mod for the contract).
# =====================================================================

param REGIME symbolic default "unlabelled";

let theta_tech := 0.5;
let theta_grid := 0.5;
let theta_ccs  := 0.5;
let n8_scrap_rate := 0.06;
let {t in T} n5_cost_NG[t] := 10;

# H2 and the emissions/build limits pushed far outside the 2025-2050
# horizon/feasible range -- h2_peak_year follows ng_h2_start_year
# automatically as a DERIVED param; do NOT `let` it.
let ng_h2_start_year := 2100;
let avg_emi          := 1e6;
let cap_add_common   := 1e12;

# Freeze the calibrated 2025 production structure through the study period.
s.t. base_f_bof     {t in T: ord(t) > 1}: f_bof[t] = 0.51;
s.t. base_f_eaf     {t in T: ord(t) > 1}: f_eaf[t] = 0.49;
s.t. base_scrap_eaf {t in T: ord(t) > 1}: steel_scrap_eaf[t] = 0;
s.t. base_cdri_split{t in T: ord(t) > 1}: coaldri_output[t] = 0.902 * dri_eaf_steel_out[t];
s.t. no_ccs{t in T}: total_ccs[t] = 0;

param base_scrap_share :=
    n3_metallic_bof * ( phi0_bof   * 0.51
                      + phi0_cdri  * 0.902 * 0.49
                      + phi0_ngdri * 0.098 * 0.49 );
s.t. base_scrap_total{t in T: ord(t) > 1}:
    bof_scrap_in[t] + eaf_scrap_in[t] + scrap_eaf_scrap_in[t]
      = base_scrap_share * total_steel[t];
