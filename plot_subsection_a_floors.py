#!/usr/bin/env python
"""
Subsection A — mode x ET feasibility floor per structural axis.

Headline: expansion caps (mode 2) are economically irrelevant until you
approach the frontier; mode 0 (no build-rate limits) barely moves across
axes, while mode 2's floor spreads widely — showing which axis actually
decides feasibility once realistic ramp friction is in play.

Reads subsection_a_floors.csv -> results/plots/fig_subsection_a_floors.png
"""
import os, csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT = os.path.dirname(os.path.abspath(__file__))
OUT = __import__("_runpaths").PLOTS

MODE0_C, MODE2_C = "#264653", "#e76f51"   # no-limits counterfactual / realistic ramp

# Panel spec: (title, [(axis, value, label), ...], divider index for grouped panels)
PANELS = [
    ("H₂-DRI start year", [("h2_start_year", v, l) for v, l in
        [("2030", "2030"), ("2035", "2035"), ("2040", "2040"), ("2045", "2045")]], None),
    ("Scrap regime", [("scrap_regime", v, l) for v, l in
        [("starved", "Starved"), ("low", "Low"), ("modest", "Modest"), ("optimistic", "Optimistic")]], None),
    ("Import dependence", [("ng_availability", v, l) for v, l in
        [("scarce", "NG\nscarce"), ("normal", "NG\nnormal"), ("abundant", "NG\nabundant")]] +
        [("ccoal_availability", v, l) for v, l in
        [("scarce", "Coal\nscarce"), ("normal", "Coal\nnormal"), ("abundant", "Coal\nabundant")]], 3),
]

rows = list(csv.DictReader(open(os.path.join(PROJECT, "subsection_a_floors.csv"))))
data = {}   # (axis, axis_value, mode) -> et_floor
for r in rows:
    data[(r["axis"], r["axis_value"], r["mode"])] = float(r["et_floor"])

fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), sharey=True,
                         gridspec_kw={"width_ratios": [len(p[1]) for p in PANELS]})
fig.suptitle("Feasibility-EF floor by structural axis (mode 0 vs mode 2)\n"
             "h2_ref_cap = 4 Mt · central: NG 15, h2_capex_mult 1.05, CCS 75, scrap modest, grid moderate_re",
             fontsize=12, y=1.02)

for ax, (title, entries, divider) in zip(axes, PANELS):
    x = range(len(entries))
    m0 = [data[(a, v, "0")] for a, v, _ in entries]
    m2 = [data[(a, v, "2")] for a, v, _ in entries]
    w = 0.36
    ax.bar([i - w/2 for i in x], m0, width=w, color=MODE0_C, label="Mode 0 (no limits)")
    ax.bar([i + w/2 for i in x], m2, width=w, color=MODE2_C, label="Mode 2 (realistic ramp)")
    ax.set_xticks(list(x))
    ax.set_xticklabels([l for _, _, l in entries], fontsize=9)
    ax.set_title(title, fontsize=11)
    ax.axhline(1.0, color="#999", linewidth=0.7, linestyle=":")
    if divider is not None:
        ax.axvline(divider - 0.5, color="#bbb", linewidth=1.0, linestyle="-")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)

axes[0].set_ylabel("Feasibility-EF floor (tCO₂/tCS)")
axes[0].set_ylim(0.9, 2.4)
fig.legend(handles=[plt.Rectangle((0,0),1,1, color=MODE0_C, label="Mode 0 (no limits)"),
                    plt.Rectangle((0,0),1,1, color=MODE2_C, label="Mode 2 (realistic ramp)")],
           loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.04))
fig.subplots_adjust(left=0.06, right=0.98, top=0.82, bottom=0.14, wspace=0.08)

out = os.path.join(OUT, "fig_subsection_a_floors.png")
fig.savefig(out, dpi=160, bbox_inches="tight")
print(f"Saved -> {out}")
