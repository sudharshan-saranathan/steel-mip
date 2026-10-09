#!/usr/bin/env python3
"""Violin study: split composition-violins by scrap-growth band x hydrogen
start year -- one asymmetric violin per (scrap group, h2 year): LEFT half
= whole-path PV LCOP distribution (binned, filled with the mean 2050
route mix per bin), RIGHT half = 2050 emission-intensity distribution
(plain binned), circle at the median = mean CCS capture fraction
(cumulative captured / cumulative gross emitted). P(infeasible) is
computed per cell for annotation under each violin.

Pure filter + bin, no solving: reads the EF sheets of ../data/
mc_solves.xlsx (the single shared Monte Carlo solve -- see
../run_montecarlo.py), one violin set per (avg_emi, ramp) in AVG_EMIS x
RAMPS. Scrap-rate rows
are the 3-band grouping of our 5-level discrete axis:
  Low  = {0.02, 0.04}
  Mid  = {0.06}
  High = {0.08, 0.10}

P_infeasible needs the FULL structural cell population (including
infeasible cells), which mc_solves.xlsx does not carry (it only solves
feasible cells) -- read separately from structural/feasibility_and_
synergy/feasibility_drivers/data/feasibility_drivers.xlsx, sheet
"raw_matrix", filtered to the same avg_emi & ramp.

Binning: LCOP and emis2050 each get their own 24-bin grid spanned over
the range of the whole population (all avg_emi and ramps, not per-cell,
so every panel compares on one grid) --
reconstructed from the original violin_data.xlsx (bin edges shared
exactly across all 12 (scrap_group, h2_year) groups; each group then
keeps only its own non-empty bins, which is why saved bin counts vary
group to group even though the edge grid itself is common).

Output: data/violin.xlsx --
Every sheet carries avg_emi and ramp columns.
  sheet "cells"     one row per (scrap_group, h2_year): grange (display
                    label), P_infeasible, n_solved (draw-rows, not
                    cells), capture_frac, lcop_p50, emis2050_p50
  sheet "lcop_bins" scrap_group, h2_year, lcop_bin_lo/hi, count, and the
                    5 route-share means (Scrap-EAF/H2-DRI/NG-DRI/
                    Coal-DRI/BF-BOF) for that bin -- empty bins dropped
  sheet "emis_bins" scrap_group, h2_year, emis_bin_lo/hi, count --
                    empty bins dropped

    python run_violin.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CCS_CENTRAL = 0.25
MC_SOLVES = ROOT / "data" / "mc_solves.parquet"
FEAS_CSV = (ROOT / "structural" / "feasibility_and_synergy" /
            "feasibility_drivers" / "data" / "raw_matrix.csv")
OUT = HERE / "data" / "violin.xlsx"

RAMPS = ["low", "medium", "high"]
AVG_EMIS = [1.6, 1.8, 2.0]
N_BINS = 24
H2_YEARS = [2030, 2035, 2040, 2045]
SCRAP_GROUPS = {"Low": [0.04], "Mid": [0.05], "High": [0.06, 0.07]}   # [audit] re-anchored axis
GRANGE = {"Low": "4%/yr", "Mid": "5%/yr", "High": "6% & 7%/yr"}
ROUTE_COLS = [("share_scrap", "Scrap-EAF"), ("share_h2", "H2-DRI"),
              ("share_ngdri", "NG-DRI"), ("share_cdri", "Coal-DRI"),
              ("share_bof", "BF-BOF")]


def scrap_group_of(rate):
    for g, levels in SCRAP_GROUPS.items():
        if any(abs(rate - lv) < 1e-9 for lv in levels):
            return g
    return None


def load_population(avg_emi):
    import pandas as pd
    d = pd.read_parquet(MC_SOLVES)
    d = d[d.avg_emi == avg_emi]
    d = d[d.ccs_phi == CCS_CENTRAL] if "ccs_phi" in d else d  # [audit] central CCS slice
    d = d[(d.solve_result == "solved") & d.ramp.isin(RAMPS)].copy()
    d["scrap_group"] = d.scrap_rate.map(scrap_group_of)
    return d


def load_full_structural():
    import pandas as pd
    df = pd.read_csv(FEAS_CSV)
    df = df[df.ccs_phi == CCS_CENTRAL] if "ccs_phi" in df else df  # [audit] central CCS slice
    df = df[df.avg_emi.isin(AVG_EMIS) & df.ramp.isin(RAMPS)].copy()
    # The Monte Carlo samples only the bracketing coal/NG regimes; match that population
    df = df[df.ccoal.isin(["abundant", "scarce"]) & df.ng.isin(["abundant", "scarce"])]
    df["scrap_group"] = df.scrap_rate.map(scrap_group_of)
    return df


def main():
    import numpy as np
    import pandas as pd

    full_all = load_full_structural()
    cells_rows, lcop_rows, emis_rows = [], [], []
    n_pop = 0

    pops = {ef: load_population(ef) for ef in AVG_EMIS}
    pop_all = pd.concat(pops.values())
    lcop_edges = np.histogram_bin_edges(pop_all.lcop, bins=N_BINS)
    emis_edges = np.histogram_bin_edges(pop_all.emis2050, bins=N_BINS)

    for ef, pop_ef in pops.items():
        n_pop += len(pop_ef)
        for ramp in RAMPS:
            pop = pop_ef[pop_ef.ramp == ramp]
            full = full_all[(full_all.avg_emi == ef) & (full_all.ramp == ramp)]
            key = {"avg_emi": ef, "ramp": ramp}
            _cells(key, pop, full, lcop_edges, emis_edges,
                   cells_rows, lcop_rows, emis_rows)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUT) as xw:
        pd.DataFrame(cells_rows).to_excel(xw, sheet_name="cells", index=False)
        pd.DataFrame(lcop_rows).to_excel(xw, sheet_name="lcop_bins", index=False)
        pd.DataFrame(emis_rows).to_excel(xw, sheet_name="emis_bins", index=False)

    print(f"violin: {n_pop:,} solve rows, {len(cells_rows)} cells -> "
          f"{OUT.relative_to(ROOT)}")
    return 0


def _cells(key, pop, full, lcop_edges, emis_edges, cells_rows, lcop_rows, emis_rows):
    """Append the 12 (scrap_group, h2_year) cells of one (avg_emi, ramp)."""
    import numpy as np

    for sg in SCRAP_GROUPS:
        for yr in H2_YEARS:
            fsub = full[(full.scrap_group == sg) & (full.h2_start == yr)]
            n_total = len(fsub)
            n_solved_cells = (fsub.solve_result == "solved").sum()
            p_infeasible = round(1 - n_solved_cells / n_total, 4) if n_total else None

            gsub = pop[(pop.scrap_group == sg) & (pop.h2_start == yr)]
            n_solved_rows = len(gsub)

            if n_solved_rows == 0:
                cells_rows.append({**key, "scrap_group": sg, "grange": GRANGE[sg],
                                   "h2_year": yr, "P_infeasible": p_infeasible,
                                   "n_solved": 0, "capture_frac": None,
                                   "lcop_p50": None, "emis2050_p50": None})
                continue

            capture_frac = round(gsub.cum_captured.mean() /
                                 (gsub.cum_captured.mean() + gsub.cum_co2.mean()), 4)
            cells_rows.append({
                **key, "scrap_group": sg, "grange": GRANGE[sg], "h2_year": yr,
                "P_infeasible": p_infeasible, "n_solved": n_solved_rows,
                "capture_frac": capture_frac,
                "lcop_p50": round(gsub.lcop.median(), 2),
                "emis2050_p50": round(gsub.emis2050.median(), 4),
            })

            lcop_bin = np.digitize(gsub.lcop, lcop_edges[1:-1])
            for b in sorted(set(lcop_bin)):
                bsub = gsub[lcop_bin == b]
                row = {**key, "scrap_group": sg, "h2_year": yr,
                       "lcop_bin_lo": round(lcop_edges[b], 2),
                       "lcop_bin_hi": round(lcop_edges[b + 1], 2),
                       "count": len(bsub)}
                for col, label in ROUTE_COLS:
                    row[label] = round(bsub[col].mean(), 4)
                lcop_rows.append(row)

            emis_bin = np.digitize(gsub.emis2050, emis_edges[1:-1])
            for b in sorted(set(emis_bin)):
                bsub = gsub[emis_bin == b]
                emis_rows.append({
                    **key, "scrap_group": sg, "h2_year": yr,
                    "emis_bin_lo": round(emis_edges[b], 4),
                    "emis_bin_hi": round(emis_edges[b + 1], 4),
                    "count": len(bsub),
                })


if __name__ == "__main__":
    sys.exit(main())
