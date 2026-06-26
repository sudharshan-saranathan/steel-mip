#!/usr/bin/env python
"""
Marginal production-mix plots that ISOLATE each structural parameter.

For each structural axis (scrap regime, H2-start year, grid-EF scenario) draw a
row of stacked-area trajectories, one per level, where the mix is averaged over
the OTHER two structural axes AND all price draws. Reading along a row shows the
marginal effect of that one parameter on the route mix over 2025-2050.

Route shares use the same crude-steel normalisation as plot_pathway_spread.py
(DRI outputs / (1-phi_eaf)), so the five shares sum to 1.

Reads cells_traj/<scrap>_<h2>_<grid>.csv -> runs/<RUN>/plots/.
Caveat: levels with fewer feasible cells average over a smaller other-axis
support (panel titles show n cells); use REGRET_BALANCED=1 to restrict each axis
to the other-axis combos feasible across ALL its levels (apples-to-apples).
"""
import os, glob, itertools
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from _runpaths import PLOTS

PROJECT = os.path.dirname(os.path.abspath(__file__)); os.chdir(PROJECT)
ET    = os.environ.get("MC_AVG_EMI", "1.8")
YEARS = list(range(2025, 2051)); PHI = 0.1
BALANCED = os.environ.get("REGRET_BALANCED") == "1"
ROUTES = [("steel_scrap_eaf", "Scrap-EAF"), ("h2dri_output", "H₂-DRI"),
          ("ngdri_output", "NG-DRI"), ("coaldri_output", "Coal-DRI"), ("steel_bof", "BOF")]
DRI = {"coaldri_output", "ngdri_output", "h2dri_output"}
PAL = plt.get_cmap("Dark2").colors
ORDER = {"scrap": ["starved", "low", "modest", "optimistic"],
         "h2":    ["2030", "2035", "2040", "2045"],
         "grid":  ["bau", "moderate_re", "aggressive_re"]}

# load each feasible cell's per-draw route fractions
cells = {}
for f in glob.glob(os.path.join("cells_traj", "*.csv")):
    name = os.path.basename(f)[:-4]
    scrap, h2, grid = name.split("_", 2)
    df = pd.read_csv(f); df = df[df["year"].isin(YEARS)].copy()
    tot = df["total_steel"].replace(0, np.nan)
    for col, _ in ROUTES:
        s = df[col] / (1 - PHI) if col in DRI else df[col]
        df["f_" + col] = s / tot
    cells[name] = dict(scrap=scrap, h2=h2, grid=grid, df=df)

def mean_mix(dfs):
    big = pd.concat(dfs)
    return {col: big.groupby("year")["f_" + col].mean().reindex(YEARS).values
            for col, _ in ROUTES}

def balanced_keep(axis):
    """other-axis (a,b) combos feasible across ALL levels of `axis`."""
    others = [x for x in ("scrap", "h2", "grid") if x != axis]
    combos = {lv: set() for lv in ORDER[axis]}
    for c in cells.values():
        combos.setdefault(c[axis], set()).add((c[others[0]], c[others[1]]))
    present = [lv for lv in ORDER[axis] if combos.get(lv)]
    common = set.intersection(*(combos[lv] for lv in present)) if present else set()
    return others, common

for axis in ("scrap", "h2", "grid"):
    keep = None
    if BALANCED:
        others, common = balanced_keep(axis)
    bylevel = {lv: [] for lv in ORDER[axis]}
    for c in cells.values():
        if BALANCED and (c[others[0]], c[others[1]]) not in common:
            continue
        bylevel[c[axis]].append(c["df"])
    lvs = [lv for lv in ORDER[axis] if bylevel[lv]]
    fig, axes = plt.subplots(1, len(lvs), figsize=(3.2 * len(lvs), 4.0),
                             sharey=True, squeeze=False)
    for a, lv in zip(axes[0], lvs):
        mix = mean_mix(bylevel[lv])
        a.stackplot(YEARS, np.vstack([mix[c] for c, _ in ROUTES]),
                    colors=PAL[:len(ROUTES)], labels=[l for _, l in ROUTES])
        a.set_title(f"{axis} = {lv}  (n={len(bylevel[lv])})", fontsize=9)
        a.set_xlim(2025, 2050); a.set_ylim(0, 1); a.set_xlabel("year")
    axes[0][0].set_ylabel("mean route share")
    axes[0][-1].legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8, frameon=False)
    bal = " (balanced support)" if BALANCED else ""
    fig.suptitle(f"Production mix vs {axis}  —  ET {ET}, averaged over other axes + price draws{bal}",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 0.93, 0.94])
    out = os.path.join(PLOTS, f"fig_structural_avg_{axis}{'_bal' if BALANCED else ''}.png")
    fig.savefig(out, dpi=160); print("saved", out)
