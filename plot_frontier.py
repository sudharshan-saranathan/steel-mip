#!/usr/bin/env python
"""
Feasibility-frontier figure: can the 1.6 tCO2/t target be met?

Three NG-availability scenarios (columns), each a scrap-regime x H2-start-year
grid. Each cell is feasible (target reachable by some technology mix, at any
price) or infeasible (no mix reaches 1.6). Feasibility is price-independent, so
this is the structural map that the whole study rests on.

Reads mc_frontier.csv -> results/fig_frontier.png
"""
import os, csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

PROJECT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(PROJECT, "results"); os.makedirs(OUT, exist_ok=True)

NG = ["normal", "shock", "optimistic"]
SCRAP = ["starved", "low", "modest", "optimistic"]      # rows, bottom->top
SCRAP_LBL = ["Starved\n(0.5%/yr)", "Low\n(2%)", "Modest\n(4%)", "Optimistic\n(6%)"]
YR = ["2030", "2035", "2040", "2045"]                    # cols

rows = list(csv.DictReader(open(os.path.join(PROJECT, "mc_frontier.csv"))))
feas = {(r["ng_scenario"], r["scrap_regime"], r["h2_start_year"]):
        (r["status"] == "solved") for r in rows}

FEAS_C, INF_C = "#2a9d8f", "#e76f51"   # teal / warm-red

fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
fig.suptitle("Can the 1.6 tCO₂/t target be met?  —  feasibility is structural, not financial",
             fontsize=13, y=1.02)

for ax, ng in zip(axes, NG):
    for i, s in enumerate(SCRAP):          # row (y)
        for j, y in enumerate(YR):         # col (x)
            ok = feas[(ng, s, y)]
            ax.add_patch(plt.Rectangle((j, i), 1, 1,
                         facecolor=FEAS_C if ok else INF_C,
                         edgecolor="white", linewidth=2))
            ax.text(j + 0.5, i + 0.5, "✓" if ok else "✗",
                    ha="center", va="center", color="white",
                    fontsize=15, fontweight="bold")
    ax.set_xlim(0, 4); ax.set_ylim(0, 4)
    ax.set_xticks([k + 0.5 for k in range(4)]); ax.set_xticklabels(YR)
    ax.set_yticks([k + 0.5 for k in range(4)])
    ax.set_yticklabels(SCRAP_LBL if ng == "normal" else [])
    ax.set_xlabel("H₂-DRI start year")
    ax.set_title(f"NG: {ng}", fontsize=11)
    ax.set_aspect("equal"); ax.tick_params(length=0)
    for sp in ax.spines.values(): sp.set_visible(False)

axes[0].set_ylabel("Scrap-recycling regime")
fig.legend(handles=[Patch(facecolor=FEAS_C, label="Feasible — target reachable"),
                    Patch(facecolor=INF_C, label="Infeasible — no pathway to 1.6")],
           loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.13))
fig.subplots_adjust(left=0.13, right=0.98, top=0.82, bottom=0.24, wspace=0.12)

out = os.path.join(OUT, "fig_frontier.png")
fig.savefig(out, dpi=160, bbox_inches="tight")
print(f"Saved -> {out}")
