#!/usr/bin/env python
"""
Heatmaps of 2050 steel cost and emissions over the H2-cost × CCS-cost grid.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

PROJECT = os.path.dirname(os.path.abspath(__file__))
CSV     = os.path.join(PROJECT, os.environ.get("MC_OUT", "mc_2d_results.csv"))
OUTDIR  = os.path.join(PROJECT, "results")
os.makedirs(OUTDIR, exist_ok=True)

df = pd.read_csv(CSV)
df = df[df["status"] == "solved"]

N_H2  = df["i_h2"].nunique()
N_CCS = df["i_ccs"].nunique()
df = df.sort_values(["i_h2", "i_ccs"])

H2_VALS  = df["h2_end_cost"].unique();  H2_VALS.sort()   # $/ton
CCS_VALS = df["ccs_end_cost"].unique(); CCS_VALS.sort()  # $/tCO2

def to_grid(col):
    return df[col].values.reshape(N_H2, N_CCS)

cost_grid = to_grid("cost_2050")     # $/tCS
emis_grid = to_grid("emis_2050")     # tCO2/tCS

# x-axis: CCS cost  |  y-axis: H2 cost (origin bottom-left)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("2050 Steel Outcomes  —  H₂ cost × CCS cost\n"
             f"(NG = 15 $/MMBtu, H₂ start = 2030, scrap growth = 6%/yr, scenario = normal)",
             fontsize=11)

def heatmap(ax, grid, title, cbar_label, cmap, fmt="{:.0f}"):
    im = ax.imshow(grid, origin="lower", aspect="auto", cmap=cmap, interpolation="bicubic",
                   extent=[CCS_VALS[0], CCS_VALS[-1], H2_VALS[0]/1000, H2_VALS[-1]/1000])
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(cbar_label, fontsize=10)
    ax.set_xlabel("CCS cost  ($/tCO₂)", fontsize=10)
    ax.set_ylabel("H₂ end-cost  ($/kg)", fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(5))

heatmap(axes[0], cost_grid, "Levelised steel cost (2050)", "$/t crude steel", "YlOrRd")
heatmap(axes[1], emis_grid, "Emissions intensity (2050)",  "tCO₂ / t steel",  "RdYlGn_r")

plt.tight_layout()
out = os.path.join(OUTDIR, "heatmap_2d.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"Saved -> {out}")
plt.show()
