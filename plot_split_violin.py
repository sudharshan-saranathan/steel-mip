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

Reads cells/<scrap>_<h2year>_<grid_ef>.csv -> results/. One panel per scrap
regime present; within a panel one violin per (H2 year, grid-EF) combo.
"""
import os, csv, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

PROJECT  = os.path.dirname(os.path.abspath(__file__))
OUT      = os.path.join(PROJECT, "results"); os.makedirs(OUT, exist_ok=True)
NBINS    = 24

# Matrix layout: rows = scrap regimes, columns = H2-start years, at a FIXED grid-EF.
# Cells that are infeasible at the target are drawn as marked empty slots (the
# matrix doubles as a feasibility map). All three configurable via env.
GRID_EF     = os.environ.get("MC_GRID_EF", "aggressive_re")
SCRAP_ROWS  = os.environ.get("MC_VIOLIN_SCRAPS", "low,modest,optimistic").split(",")
H2_COLS     = os.environ.get("MC_VIOLIN_H2", "2030,2035,2040,2045").split(",")
_GLAB       = {"bau": "BAU", "moderate_re": "moderate RE", "aggressive_re": "aggressive RE"}

_PAL = plt.get_cmap("Pastel2").colors      # qualitative palette for tech pathways
ROUTES = [("f_scrap_2050", "scrap-EAF", _PAL[0]),
          ("f_h2_2050",    "H₂-DRI",    _PAL[1]),
          ("f_ng_2050",    "NG-DRI",    _PAL[2]),
          ("f_coal_2050",  "coal-DRI",  _PAL[3]),
          ("f_bof_2050",   "BOF",       _PAL[4])]
KEYS = [r[0] for r in ROUTES]
EMIS_FILL = "0.82"                          # plain fill for the emissions half
EDGE = dict(edgecolor="black", linewidth=1.0)   # black border on every bar

# --- load feasible cells for the chosen grid-EF (filename: scrap_h2_grid.csv) ---
allcells = {}   # (scrap, yr) -> (cost, emis, sh, capfrac)
for scrap in SCRAP_ROWS:
    for yr in H2_COLS:
        f = os.path.join(PROJECT, "cells", f"{scrap}_{yr}_{GRID_EF}.csv")
        if not os.path.exists(f):
            continue
        rows = [r for r in csv.DictReader(open(f)) if r["status"] == "solved"]
        if not rows:
            continue
        cost = np.array([float(r["cost_2050"]) for r in rows])
        emis = np.array([float(r["emis_2050"]) for r in rows])
        cap  = np.array([float(r["capture_per_t"]) for r in rows])
        lae  = np.array([float(r["lifetime_avg_emis"]) for r in rows])
        capfrac = float(np.mean(cap / (cap + lae)))   # sub-domain mean captured / gross CO2
        sh = {k: np.array([float(r[k]) for r in rows]) for k in KEYS}
        tot = sum(sh[k] for k in KEYS); tot[tot == 0] = 1.0
        for k in KEYS:
            sh[k] = sh[k] / tot
        allcells[(scrap, yr)] = (cost, emis, sh, capfrac)

if not allcells:
    raise SystemExit(f"No feasible cells for grid_ef={GRID_EF} among "
                     f"scrap={SCRAP_ROWS} x H2={H2_COLS}")

def rng(arrs, pad=0.04):
    lo = min(a.min() for a in arrs); hi = max(a.max() for a in arrs)
    p = (hi - lo) * pad; return lo - p, hi + p

cost_lo, cost_hi = rng([c[0] for c in allcells.values()])
emis_lo, emis_hi = rng([c[1] for c in allcells.values()])
cedges = np.linspace(cost_lo, cost_hi, NBINS + 1); cbh = cedges[1] - cedges[0]
eedges = np.linspace(emis_lo, emis_hi, NBINS + 1); ebh = eedges[1] - eedges[0]

CAPMAX  = max(c[3] for c in allcells.values())     # for circle-radius scaling
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

# feasible-only: one row per scrap regime that has >=1 feasible cell;
# within a row, only the feasible H2 years, left-packed (no infeasible slots).
rows_data = [(scrap, [yr for yr in H2_COLS if (scrap, yr) in allcells])
             for scrap in SCRAP_ROWS]
rows_data = [rd for rd in rows_data if rd[1]]        # drop empty rows
NCOL = max(len(yrs) for _, yrs in rows_data)         # widest row -> uniform slot width

fig, axes = plt.subplots(len(rows_data), 1, figsize=(2.3 * NCOL + 1.4,
                         3.3 * len(rows_data)), squeeze=False)
axes = axes[:, 0]
fig.suptitle(f"Split composition-violins  —  grid: {_GLAB.get(GRID_EF, GRID_EF)}"
             f"  (ET target 1.6, ramp 0.20)\n"
             "LEFT half = 2050 cost (left axis)   |   RIGHT half = 2050 emissions (right axis)"
             "   |   fill = mean production mix   |   rows = scrap, cols = H₂ year",
             fontsize=11.5, y=0.985)

for irow, (axL, (scrap, yrs)) in enumerate(zip(axes, rows_data)):
    axR = axL.twinx()
    cx, cy, cs = [], [], []
    for xpos, yr in enumerate(yrs, 1):
        axL.axvline(xpos, color="0.75", lw=0.6, zorder=0)
        cost, emis, sh, capfrac = allcells[(scrap, yr)]
        draw_half(axL, xpos, cost, sh, cedges, cbh, "L", stacked=True)
        draw_half(axR, xpos, emis, sh, eedges, ebh, "R", stacked=False)
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
    axL.set_xlim(0.2, NCOL + 0.6)
    axL.set_ylim(cost_lo, cost_hi); axR.set_ylim(emis_lo, emis_hi)
    axL.set_xticks(range(1, len(yrs) + 1))
    axL.set_xticklabels([f"H₂ {yr}" for yr in yrs], fontsize=9)
    axL.set_ylabel("Cost 2050 ($/t)  ◀", fontsize=9)
    axR.set_ylabel("▶  Emissions (tCO₂/t)", fontsize=9)
    axL.grid(axis="y", alpha=0.18)
    axL.set_title(f"{scrap} scrap", fontsize=10, loc="left")

axes[0].legend(handles=[Patch(facecolor=c, label=l, **EDGE) for _, l, c in ROUTES],
               loc="upper right", ncol=5, fontsize=8, frameon=False)
fig.subplots_adjust(left=0.09, right=0.91, top=0.88, bottom=0.06, hspace=0.30)
out = os.path.join(OUT, f"fig_splitviolin_et1.6_{GRID_EF}.png")
fig.savefig(out, dpi=160)
print(f"Saved -> {out}")
