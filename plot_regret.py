#!/usr/bin/env python
"""Regret heatmaps: plan-world (rows) x realised-world (cols), $/t-steel.
Reads regret_matrix_adaptive.csv + regret_matrix_rigid.csv -> results/.
INFEAS cells (catastrophic regret: committed too little clean capacity) are hatched."""
import os, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

PROJECT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(PROJECT, "results"); os.makedirs(OUT, exist_ok=True)
ORDER = ["starved", "low", "modest", "optimistic"]   # pessimistic -> optimistic

def load(path):
    rows = list(csv.DictReader(open(path)))
    worlds = [w for w in ORDER if any(r["plan"] == w for r in rows)]
    M = np.full((len(worlds), len(worlds)), np.nan)
    infeas = np.zeros_like(M, dtype=bool)
    for r in rows:
        i, j = worlds.index(r["plan"]), worlds.index(r["realize"])
        if r["regret_usd_t"] == "INFEAS":
            infeas[i, j] = True
        else:
            M[i, j] = float(r["regret_usd_t"])
    return worlds, M, infeas

panels = [("adaptive recourse", "regret_matrix_adaptive.csv"),
          ("no adaptation (rigid)", "regret_matrix_rigid.csv")]
vmax = 0
for _, f in panels:
    if os.path.exists(os.path.join(PROJECT, f)):
        _, M, _ = load(os.path.join(PROJECT, f)); vmax = max(vmax, np.nanmax(M))

cmap = LinearSegmentedColormap.from_list("reg", ["#f7fbff", "#fdae61", "#d73027"])
fig, axes = plt.subplots(1, len(panels), figsize=(5.6 * len(panels), 5.0), squeeze=False)
for ax, (title, f) in zip(axes[0], panels):
    path = os.path.join(PROJECT, f)
    if not os.path.exists(path):
        ax.set_visible(False); continue
    worlds, M, infeas = load(path)
    n = len(worlds)
    im = ax.imshow(M, cmap=cmap, vmin=0, vmax=vmax, origin="upper")
    for i in range(n):
        for j in range(n):
            if infeas[i, j]:
                ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, facecolor="0.85",
                             edgecolor="0.5", hatch="xxx"))
                ax.text(j, i, "INFEAS\n(catastrophic)", ha="center", va="center",
                        fontsize=7.5, color="0.25")
            elif not np.isnan(M[i, j]):
                ax.text(j, i, f"${M[i, j]:.0f}/t", ha="center", va="center", fontsize=10,
                        color="white" if M[i, j] > vmax * 0.55 else "black")
    ax.set_xticks(range(n)); ax.set_xticklabels(worlds, fontsize=9)
    ax.set_yticks(range(n)); ax.set_yticklabels(worlds, fontsize=9)
    ax.set_xlabel("realised world (scrap)", fontsize=10)
    ax.set_ylabel("planned-for world (scrap)", fontsize=10)
    ax.set_title(title, fontsize=11)
    ax.set_xticks(np.arange(-.5, n, 1), minor=True); ax.set_yticks(np.arange(-.5, n, 1), minor=True)
    ax.grid(which="minor", color="white", lw=1.5); ax.tick_params(which="minor", length=0)
fig.colorbar(im, ax=axes[0].tolist(), shrink=0.8, label="regret ($/t-steel)")
fig.suptitle("Regret of mis-planned capacity — cell H₂-2030 / aggressive-RE, ET 1.6\n"
             "upper triangle = plan pessimistic, get lucky (bounded);  "
             "lower triangle = plan optimistic, get unlucky (infeasible)",
             fontsize=11)
fig.subplots_adjust(left=0.10, right=0.90, top=0.84, bottom=0.12, wspace=0.35)
out = os.path.join(OUT, "fig_regret_matrix.png")
fig.savefig(out, dpi=160)
print("Saved ->", out)
