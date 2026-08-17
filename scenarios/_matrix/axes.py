#!/usr/bin/env python3
"""Axis registry for the Section A design matrix.

SINGLE SOURCE OF TRUTH for what gets solved.

ORGANISING PRINCIPLE
--------------------
Section A sweeps ONLY what policy controls -- levers a ministry can decide
through investment or regulation. Everything else is either a constant
(background condition) or belongs to Section B (Monte Carlo over things nobody
controls). Learning rates are the clearest example of the latter: `theta_tech`
and `theta_ccs` depend on global science, not Indian policy, so they are fixed
here and sampled in Section B.

This criterion is what took the design from 524,880 cells to 46,656. The
earlier version swept everything that *could* vary; this one sweeps what the
paper can make a policy claim about.

Emissions targets are the three the original studies used (1.6 / 1.8 / 2.0) --
they are the CONSTRAINT being tested against, not a lever, and three named
targets is the right granularity for that role.
"""

# ---------------------------------------------------------------- levers ---
# (label, axis-file stem). Availability regimes are time-indexed tables.
CCOAL = [
    ("abundant", "ccoal_abundant"),   # imports grow ~6.5%/yr -> 293.6 Mt by 2050
    ("scarce",   "ccoal_scarce"),     # ~0.8%/yr -> 91.1 Mt
]

NG = [
    ("policy", "ng_policy"),          # national gas -> 32.2 Mm3 by 2050
    ("bau",    "ng_bau"),             # -> 10.7 Mm3
]

# Integer switch year for No_H2_Before. 5-year spacing, matching the original
# import-dependence and hydrogen-delay studies.
H2_START = [2030, 2035, 2040, 2045]

# Annual scrap-availability growth -> collection infrastructure, ELV rules.
SCRAP_RATE = [0.00, 0.02, 0.04, 0.06, 0.08, 0.10]

# Target 2050 grid EF, tCO2/kWh (50-850 gCO2/kWh against an 886 g 2025 anchor).
# Offset by 0.00005 so the 0.0001 grid lands ON 0.00045, the value implied by
# theta_grid = 0.5. NOTE: only 0.0003-0.0006 is calibrated; outside that the
# COUPLED electricity tariff extrapolates, so rows carry an `extrapolated`
# flag. Feasibility is usable across the whole band; cost is not.
GRID_EF = [round(0.00005 + 0.0001 * i, 5) for i in range(9)]

# Electrolyser deployment rate: scales the Gaussian growth ceiling in
# v_capacity.mod. Genuinely H2-specific: it scales ONLY the electrolyser ramp.
# In the original studies this axis also moved cap_add_common (collinear, ratio
# 2.5), so any effect attributed to "H2 ramp" was partly conventional capacity.
# Conventional build rate is now its own lever, BUILD_CAP below.
RAMP = [("low", 4_000_000), ("medium", 6_000_000), ("high", 8_000_000)]

# Shared annual build budget across the four conventional routes (Mt/yr).
# Finance and EPC capacity the sector can deploy in one year -- industrial
# policy, so a lever rather than a constant. It BINDS at every level tested
# (peak annual build sits exactly at the cap); 20 -> 40 Mt/yr is worth 3.8 $/t.
# Note the four routes COMPETE for this budget (cap_add_total in
# v_capacity.mod); it is not a per-route allowance.
BUILD_CAP = [("tight", 20e6), ("mid", 30e6), ("loose", 40e6)]

# Retirement policy for the 2025 fleet (207.75 Mt). The fleet's vintage is
# unknown, so these two settings BRACKET it rather than estimating a middle.
# Note "run-life" is not "no retirement": coal-DRI and NG-DRI still go by 2045
# and scrap-EAF by 2040, so 117.75 of 207.75 Mt retires either way. The cases
# differ mainly over the fate of 90 Mt of BOF.
LEGACY = [("run-life", 0), ("mandated-phaseout", 1)]

# ---------------------------------------------------------------- target ---
# The constraint being tested against, not a lever. Matches EF_LEVELS in the
# original hydrogen-delay and scrap studies.
AVG_EMI = [1.6, 1.8, 2.0]


AXES = {
    "ccoal":      CCOAL,
    "ng":         NG,
    "h2_start":   H2_START,
    "scrap_rate": SCRAP_RATE,
    "grid_ef":    GRID_EF,
    "ramp":       RAMP,
    "build_cap":  BUILD_CAP,
    "legacy":     LEGACY,
    "avg_emi":    AVG_EMI,
}

# ------------------------------------------------------------- constants ---
# Held fixed in every cell. Values chosen for the reasons noted; the two thetas
# were measured across their full range before being demoted -- theta_ccs moves
# LCOP by 3.5 $/t with ZERO effect on feasibility, whr_mode by 1.3 $/t, against
# a 28.6 $/t H2-delay penalty. That is a sensitivity result, not an assumption.
CONSTANTS = {
    "theta_tech":          0.5,      # H2/RE learning -- science, not policy (Section B)
    "theta_ccs":           0.5,      # CCS learning   -- science, not policy (Section B)
    "whr_ccs_integration": 1,        # plant engineering choice, not policy
}

# The calibrated theta_grid window; rows outside it extrapolate the EF<->tariff
# coupling beyond its anchors (core/definitions.mod:151-152).
GRID_EF_CALIBRATED = (0.0003, 0.0006)

# Baseline coordinate, for --verify.
BASELINE = {
    "ccoal": "abundant", "ng": "policy", "h2_start": 2030, "scrap_rate": 0.06,
    "grid_ef": 0.00045, "ramp": "medium", "build_cap": "tight",
    "legacy": "run-life", "avg_emi": 1.8,
}


def size(axes=None):
    """Total cell count of the full cross product."""
    axes = axes or AXES
    n = 1
    for levels in axes.values():
        n *= len(levels)
    return n


if __name__ == "__main__":
    print(f"{'axis':12s} {'levels':>6s}  values")
    for name, levels in AXES.items():
        shown = [lv[0] if isinstance(lv, tuple) else lv for lv in levels]
        print(f"{name:12s} {len(levels):6d}  {shown}")
    print(f"\nconstants: {CONSTANTS}")
    n = size()
    print(f"\ntotal cells: {n:,}")
    for w in (6, 12):
        print(f"  {w:2d} workers @ ~47 cells/s total: {n / 47 / 60:.1f} min")
