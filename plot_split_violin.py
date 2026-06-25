#!/usr/bin/env python
"""
Split composition-violin: cost on the LEFT half, emissions on the RIGHT half.

Each feasible cell (one NG scenario) is one asymmetric violin:
  - LEFT  half  -> 2050 levelised-cost distribution, read against the LEFT axis
  - RIGHT half  -> 2050 emissions-intensity distribution, read against the RIGHT axis
Each half's width at a level = frequency (violin shape), filled with a stacked
bar of the mean production mix of the draws at that level.

To avoid crowding, cells are split across two stacked panels (configurable):
  top    : starved + modest
  bottom : low + optimistic
Both panels share cost/emissions axes for comparability.

Env: MC_SCENARIO (default normal).  Reads cells/<scenario>_*.csv -> results/.
"""
import os, csv, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

PROJECT  = os.path.dirname(os.path.abspath(__file__))
OUT      = os.path.join(PROJECT, "results"); os.makedirs(OUT, exist_ok=True)
SCENARIO = os.environ.get("MC_SCENARIO", "normal")
NBINS    = 24
GROUPS   = [["starved", "low"], ["modest"], ["optimistic"]]   # one panel each

_PAL = plt.get_cmap("Pastel2").colors      # qualitative palette for tech pathways
ROUTES = [("f_scrap_2050", "scrap-EAF", _PAL[0]),
          ("f_h2_2050",    "H₂-DRI",    _PAL[1]),
          ("f_ng_2050",    "NG-DRI",    _PAL[2]),
          ("f_coal_2050",  "coal-DRI",  _PAL[3]),
          ("f_bof_2050",   "BOF",       _PAL[4])]
KEYS = [r[0] for r in ROUTES]
EMIS_FILL = "0.82"                          # plain fill for the emissions half
EDGE = dict(edgecolor="black", linewidth=1.0)   # black border on every bar

# --- load all feasible cells for this scenario ---
allcells = {}
for f in sorted(glob.glob(os.path.join(PROJECT, "cells", f"{SCENARIO}_*.csv"))):
    _, scrap, yr = os.path.basename(f)[:-4].split("_")
    rows = [r for r in csv.DictReader(open(f)) if r["status"] == "solved"]
    cost = np.array([float(r["cost_2050"]) for r in rows])
    emis = np.array([float(r["emis_2050"]) for r in rows])
    cap  = np.array([float(r["capture_per_t"]) for r in rows])
    lae  = np.array([float(r["lifetime_avg_emis"]) for r in rows])
    capfrac = float(np.mean(cap / (cap + lae)))   # sub-domain mean captured / gross CO2
    sh = {k: np.array([float(r[k]) for r in rows]) for k in KEYS}
    tot = sum(sh[k] for k in KEYS); tot[tot == 0] = 1.0
    for k in KEYS:
        sh[k] = sh[k] / tot
    allcells[(scrap, yr)] = (scrap, yr, cost, emis, sh, capfrac)

def cells_for(regimes):
    cs = [v for k, v in allcells.items() if v[0] in regimes]
    return sorted(cs, key=lambda c: (regimes.index(c[0]), int(c[1])))

def rng(arrs, pad=0.04):
    lo = min(a.min() for a in arrs); hi = max(a.max() for a in arrs)
    p = (hi - lo) * pad; return lo - p, hi + p

cost_lo, cost_hi = rng([c[2] for c in allcells.values()])
emis_lo, emis_hi = rng([c[3] for c in allcells.values()])
cedges = np.linspace(cost_lo, cost_hi, NBINS + 1); cbh = cedges[1] - cedges[0]
eedges = np.linspace(emis_lo, emis_hi, NBINS + 1); ebh = eedges[1] - eedges[0]

CAPMAX  = max(c[5] for c in allcells.values())     # for circle-radius scaling
RMAX    = 17.0                                      # max circle radius (points)
CAP_COL = "#1f78b4"                                 # CCUS capture circle colour
def cap_size(frac):                                 # radius ∝ capture fraction
    return (frac / CAPMAX * RMAX) ** 2

def draw_half(ax, xpos, vals, shares, edges, bh, side, stacked=True, halfw=0.40):
    """Binned half-violin. stacked=True -> pathway composition bars (cost half);
    stacked=False -> plain single-colour frequency bars (emissions half)."""
    counts, _ = np.histogram(vals, bins=edges)
    if counts.max() == 0:
        return
    hw = halfw / counts.max()
    binidx = np.clip(np.digitize(vals, edges) - 1, 0, len(edges) - 2)
    for b in range(len(edges) - 1):
        if counts[b] == 0:
            continue
        w = counts[b] * hw
        x0 = xpos - w if side == "L" else xpos
        if stacked:
            means = [shares[k][binidx == b].mean() for k in KEYS]
            for (key, _, col), m in zip(ROUTES, means):
                ax.add_patch(plt.Rectangle((x0, edges[b]), w * m, bh,
                             facecolor=col, **EDGE))
                x0 += w * m
        else:
            ax.add_patch(plt.Rectangle((x0, edges[b]), w, bh,
                         facecolor=EMIS_FILL, **EDGE))

fig, axes = plt.subplots(3, 1, figsize=(9.5, 12))
fig.suptitle(f"Split composition-violins  —  NG: {SCENARIO}\n"
             f"LEFT half = 2050 cost (left axis)   |   RIGHT half = 2050 emissions (right axis)"
             f"   |   fill = mean production mix",
             fontsize=11.5)

for irow, (axL, regimes) in enumerate(zip(axes, GROUPS)):
    axR = axL.twinx()
    cells = cells_for(regimes)
    cx, cy, cs = [], [], []
    for xpos, (scrap, yr, cost, emis, sh, capfrac) in enumerate(cells, 1):
        draw_half(axL, xpos, cost, sh, cedges, cbh, "L", stacked=True)
        draw_half(axR, xpos, emis, sh, eedges, ebh, "R", stacked=False)
        axL.axvline(xpos, color="0.75", lw=0.6, zorder=0)
        cx.append(xpos - 0.50); cy.append(float(np.median(cost))); cs.append(cap_size(capfrac))
    axL.scatter(cx, cy, s=cs, facecolor=CAP_COL, edgecolor="black",
                linewidth=0.8, alpha=0.9, zorder=5)
    if irow == 0:   # size legend for the capture circles
        from matplotlib.lines import Line2D
        refs = [0.05, 0.10, 0.15]
        h = [Line2D([0], [0], marker="o", linestyle="", markerfacecolor=CAP_COL,
                    markeredgecolor="black", markersize=f / CAPMAX * RMAX,
                    label=f"{f:.2f}") for f in refs]
        leg = axL.legend(handles=h, loc="lower left", fontsize=8, frameon=False,
                         labelspacing=1.4, handletextpad=1.0,
                         title="CCUS capture frac.", title_fontsize=8)
        axL.add_artist(leg)
    axL.set_xlim(0.2, len(cells) + 0.6)
    axL.set_ylim(cost_lo, cost_hi); axR.set_ylim(emis_lo, emis_hi)
    axL.set_xticks(range(1, len(cells) + 1))
    axL.set_xticklabels([f"{c[0]}\n{c[1]}" for c in cells], fontsize=8)
    axL.set_ylabel("Cost 2050 ($/t)  ◀", fontsize=9)
    axR.set_ylabel("▶  Emissions (tCO₂/t)", fontsize=9)
    axL.grid(axis="y", alpha=0.18)
    axL.set_title(" + ".join(regimes), fontsize=10, loc="left")

axes[0].legend(handles=[Patch(facecolor=c, label=l, **EDGE) for _, l, c in ROUTES],
               loc="upper right", ncol=5, fontsize=8, frameon=False)
fig.subplots_adjust(left=0.09, right=0.91, top=0.92, bottom=0.05, hspace=0.14)
out = os.path.join(OUT, f"fig_splitviolin_{SCENARIO}.png")
fig.savefig(out, dpi=160)
print(f"Saved -> {out}")
