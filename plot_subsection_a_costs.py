#!/usr/bin/env python
"""
Subsection A — NPV system cost vs emissions target (ET), mode 0 vs mode 2.

One panel per structural axis; one colour per axis value; mode 0 dashed,
mode 2 solid. Each curve terminates at its feasibility floor (marker) —
the "wall" where cost turns vertical is the story: the binding constraint
is deployment speed, not money.

Reads subsection_a_costs.csv + subsection_a_floors.csv
-> runs/<RUN>/plots/fig_subsection_a_costs.png
"""
import os, csv
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT = os.path.dirname(os.path.abspath(__file__))
OUT = __import__("_runpaths").PLOTS

PANELS = [
    ("H₂-DRI start year", "h2_start_year",
     [("2030", "2030"), ("2035", "2035"), ("2040", "2040"), ("2045", "2045")],
     ["#4d7c8a", "#3d647a", "#2d4a63", "#1d2f4d"]),
    ("Scrap regime", "scrap_regime",
     [("starved", "Starved"), ("low", "Low"), ("modest", "Modest"), ("optimistic", "Optimistic")],
     ["#8a4d4d", "#a3603c", "#c07a35", "#d99a3d"]),
    ("NG availability", "ng_availability",
     [("scarce", "Scarce"), ("normal", "Normal"), ("abundant", "Abundant")],
     ["#5b4a7a", "#7a63a3", "#9a85c0"]),
    ("Coking-coal availability", "ccoal_availability",
     [("scarce", "Scarce"), ("normal", "Normal"), ("abundant", "Abundant")],
     ["#3d6b4f", "#5a8a68", "#7aa98a"]),
]

costs = defaultdict(list)   # (axis, value, mode) -> [(et, npv)]
for r in csv.DictReader(open(os.path.join(PROJECT, "subsection_a_costs.csv"))):
    if int(r["feasible"]):
        costs[(r["axis"], r["axis_value"], r["mode"])].append(
            (float(r["et"]), float(r["npv_cost"]) / 1e12))
floors = {}
for r in csv.DictReader(open(os.path.join(PROJECT, "subsection_a_floors.csv"))):
    floors[(r["axis"], r["axis_value"], r["mode"])] = float(r["et_floor"])

fig, axgrid = plt.subplots(2, 2, figsize=(11.5, 8.4), sharex=True, sharey=True)
axes = axgrid.flatten()
fig.suptitle("NPV system cost vs emissions target — mode 0 (dashed) vs mode 2 (solid)\n"
             "h2_ref_cap = 4 Mt · central: NG 15, h2_capex_mult 1.05, CCS 75, scrap modest, grid moderate_re",
             fontsize=12, y=0.99)

for ax, (title, axis, values, colors) in zip(axes, PANELS):
    for (val, label), color in zip(values, colors):
        for mode, style in (("0", "--"), ("2", "-")):
            pts = sorted(costs[(axis, val, mode)])
            if not pts:
                continue
            ets, npvs = zip(*pts)
            ax.plot(ets, npvs, style, color=color, linewidth=1.6,
                    label=label if mode == "2" else None)
            # floor terminus marker on the tight end
            ax.plot(ets[0], npvs[0], "o" if mode == "2" else "s",
                    color=color, markersize=5,
                    markerfacecolor=color if mode == "2" else "white")
    ax.set_title(title, fontsize=11)
    ax.legend(fontsize=8.5, frameon=False, loc="upper right", title=None)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(axis="y", linewidth=0.4, alpha=0.35)

axes[0].invert_xaxis()   # tighter target (more ambitious) to the right
for ax in axgrid[1]:
    ax.set_xlabel("Cumulative avg-EF cap, ET (tCO₂/tCS) — tighter →")
for ax in axgrid[:, 0]:
    ax.set_ylabel("NPV system cost (trillion US$)")
fig.subplots_adjust(left=0.08, right=0.98, top=0.88, bottom=0.08, hspace=0.22, wspace=0.08)

out = os.path.join(OUT, "fig_subsection_a_costs.png")
fig.savefig(out, dpi=160, bbox_inches="tight")
print(f"Saved -> {out}")
