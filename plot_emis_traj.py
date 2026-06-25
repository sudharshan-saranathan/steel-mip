#!/usr/bin/env python
"""Emissions-intensity and CCS-capture trajectories with Monte-Carlo spread, for
one structural cell. Companion to plot_pathway_spread.py (which does route mix).

Reads a year-by-year trajectory CSV (MC_TRAJ_OUT format: one block of years per
draw, keyed by the price triplet). Plots, per year across draws:
  - emissions intensity  total_emissions/total_steel  (mean + 25-75 / 10-90 bands)
  - CCS capture share     total_ccs/(total_emissions+total_ccs)

Config via env:
  TRAJ_IN   trajectory CSV (required)
  PLOT_OUT  output PNG (default results/fig_emis_traj.png)
  AVG_EMI   draw the cumulative target line if set
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

PROJECT = os.path.dirname(os.path.abspath(__file__)); os.chdir(PROJECT)
TRAJ_IN = os.environ["TRAJ_IN"]
OUT = os.environ.get("PLOT_OUT", os.path.join(PROJECT, "results", "fig_emis_traj.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
AVG_EMI = os.environ.get("AVG_EMI")
YEARS = list(range(2025, 2051))

df = pd.read_csv(TRAJ_IN)
df = df[df["year"].isin(YEARS)].copy()
df["draw_id"] = df.groupby(["ng_cost", "h2_end_cost", "ccs_end_cost"]).ngroup()
n = df["draw_id"].nunique()
print(f"Reading {TRAJ_IN}: {n} draws")

df["ef"]  = df["total_emissions"] / df["total_steel"].replace(0, np.nan)
df["ccs_share"] = df["total_ccs"] / (df["total_emissions"] + df["total_ccs"]).replace(0, np.nan)

def bands(col):
    p = df.pivot_table(index="draw_id", columns="year", values=col).reindex(columns=YEARS).values
    return (np.nanmean(p, 0), np.nanpercentile(p, 10, 0), np.nanpercentile(p, 25, 0),
            np.nanpercentile(p, 75, 0), np.nanpercentile(p, 90, 0))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
for ax, col, title, ylab, color in (
        (ax1, "ef", "Emissions intensity", "tCO₂ / tCS", "#c0392b"),
        (ax2, "ccs_share", "CCS capture share", "captured / gross CO₂", "#2471a3")):
    m, p10, p25, p75, p90 = bands(col)
    ax.fill_between(YEARS, p10, p90, color=color, alpha=0.12, lw=0)
    ax.fill_between(YEARS, p25, p75, color=color, alpha=0.28, lw=0)
    ax.plot(YEARS, m, color=color, lw=2.3, zorder=3)
    ax.set_xlim(2025, 2050); ax.set_xlabel("Year"); ax.set_ylabel(ylab)
    ax.set_title(title, fontsize=11); ax.grid(axis="y", lw=0.4, alpha=0.5)

if AVG_EMI:
    ax1.axhline(float(AVG_EMI), color="0.3", ls="--", lw=1.1)
    ax1.text(2025.5, float(AVG_EMI), f" cumulative target {AVG_EMI}", va="bottom", fontsize=8, color="0.3")
ax2.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
fig.suptitle(f"Emissions & CCS trajectories — {n} draws (mean; bands 25–75 / 10–90 pct)", fontsize=11)
fig.tight_layout()
fig.savefig(OUT, dpi=130, bbox_inches="tight")
print("wrote", OUT)
