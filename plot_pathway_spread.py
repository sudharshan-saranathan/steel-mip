#!/usr/bin/env python
"""
Pathway-fraction trend lines with Monte-Carlo spread for one structural cell.

Reads cells_traj/<scrap_regime>_<h2year>_<grid_ef>.csv (year-by-year
trajectory data produced by run_all_cells.py with MC_TRAJ_OUT set).

For each route, plots:
  - solid line  : mean fraction across all draws
  - dark band   : 25th–75th percentile
  - light band  : 10th–90th percentile

Config via env:
  MC_SCRAP_REGIME  {starved, low, modest, optimistic}   (default modest)
  MC_H2YEAR        H2-DRI start year                   (default 2035)
  MC_GRID_EF       {bau, moderate_re, aggressive_re}   (default moderate_re)
  TRAJ_IN          override trajectory CSV path
  PLOT_OUT         override output PNG path
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

PROJECT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT)

REG   = os.environ.get("MC_SCRAP_REGIME", "modest")
H2YR  = int(os.environ.get("MC_H2YEAR",  "2035"))
GRID_EF = os.environ.get("MC_GRID_EF", "moderate_re")

TRAJ_IN  = os.environ.get("TRAJ_IN",
    os.path.join(PROJECT, "cells_traj", f"{REG}_{H2YR}_{GRID_EF}.csv"))
OUT_DIR  = __import__("_runpaths").PLOTS
os.makedirs(OUT_DIR, exist_ok=True)
PLOT_OUT = os.environ.get("PLOT_OUT",
    os.path.join(OUT_DIR, f"fig_pathway_spread_{REG}_{H2YR}_{GRID_EF}.png"))

ROUTES = [
    ("steel_scrap_eaf", "Scrap-EAF"),
    ("h2dri_output",    "H₂-DRI"),
    ("ngdri_output",    "NG-DRI"),
    ("coaldri_output",  "Coal-DRI"),
    ("steel_bof",       "BOF"),
]
PALETTE = plt.get_cmap("Dark2").colors   # matches plot_pathways_time.py
YEARS   = list(range(2025, 2051))

# ── Load trajectories ────────────────────────────────────────────────────────
print(f"Reading {TRAJ_IN} …")
df = pd.read_csv(TRAJ_IN)
df = df[df["year"].isin(YEARS)].copy()

# Compute fractions: each route's CRUDE-STEEL output / total_steel.
# The DRI route variables (coaldri/ngdri/h2dri_output) are on the 0.9*steel_eaf
# basis (DRI-derived part only), so divide by (1-n7_phi_eaf) to recover the route's
# full crude-steel line output (incl. its EAF scrap charge). With this the five
# route shares sum to 100%. BF-BOF and scrap-EAF are already crude-steel.
PHI_EAF  = 0.1                      # n7_phi_eaf
DRI_COLS = {"coaldri_output", "ngdri_output", "h2dri_output"}
total = df["total_steel"].replace(0, np.nan)
route_cols = [r for r, _ in ROUTES]
for col in route_cols:
    series = df[col] / (1 - PHI_EAF) if col in DRI_COLS else df[col]
    df[f"f_{col}"] = series / total

# Identify unique draws by price triplet
draw_id = df.groupby(["ng_cost", "h2_capex_mult", "ccs_end_cost"]).ngroup()
df["draw_id"] = draw_id
n_draws = df["draw_id"].nunique()
print(f"  {n_draws} draws × {df['year'].nunique()} years")

# ── Compute per-year statistics ──────────────────────────────────────────────
# Shape: (n_routes, n_years, n_draws)  → easier to vectorise
years_arr = np.array(YEARS)
stats = {}   # route -> dict of arrays indexed by year position
for col in route_cols:
    fcol = f"f_{col}"
    pivot = (df.pivot_table(index="draw_id", columns="year", values=fcol)
               .reindex(columns=YEARS)
               .values)          # (n_draws, n_years), NaN for missing years
    stats[col] = {
        "mean": np.nanmean(pivot, axis=0),
        "p10":  np.nanpercentile(pivot, 10, axis=0),
        "p25":  np.nanpercentile(pivot, 25, axis=0),
        "p75":  np.nanpercentile(pivot, 75, axis=0),
        "p90":  np.nanpercentile(pivot, 90, axis=0),
    }

# ── Plot ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5.5))

for i, (col, label) in enumerate(ROUTES):
    color = PALETTE[i]
    s = stats[col]
    # 10–90 band (light)
    ax.fill_between(YEARS, s["p10"], s["p90"],
                    color=color, alpha=0.12, linewidth=0)
    # 25–75 band (dark)
    ax.fill_between(YEARS, s["p25"], s["p75"],
                    color=color, alpha=0.28, linewidth=0)
    # mean line
    ax.plot(YEARS, s["mean"], color=color, lw=2.2, label=label, zorder=3)

# H2 start-year marker
if 2025 < H2YR <= 2050:
    ax.axvline(H2YR, color="0.30", ls="--", lw=1.1)
    ax.text(H2YR + 0.25, 0.97, f"H₂ start {H2YR}",
            va="top", fontsize=8, color="0.30")

ax.set_xlim(2025, 2050)
ax.set_ylim(0, 1)
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Share of crude-steel production", fontsize=11)
ax.set_title(
    f"Production-pathway fractions  —  scrap {REG}, H₂ {H2YR}, grid EF {GRID_EF}\n"
    f"Solid line = mean across {n_draws} draws  |  "
    f"bands = 25th–75th (dark) and 10th–90th (light) percentile",
    fontsize=10,
)
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
ax.legend(loc="upper center", ncol=5, fontsize=9, frameon=False,
          bbox_to_anchor=(0.5, -0.13))
ax.grid(axis="y", lw=0.4, alpha=0.5)
fig.subplots_adjust(bottom=0.18, top=0.86)

fig.savefig(PLOT_OUT, dpi=160, bbox_inches="tight")
print(f"Saved -> {PLOT_OUT}")
