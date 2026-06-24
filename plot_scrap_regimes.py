#!/usr/bin/env python
"""
Paper figure: scrap-regime comparison across the H2 x CCUS cost plane.

Produces TWO figures, each a vertical stack of FOUR wide heatmaps (one per
scrap regime: starved / low / modest / optimistic):
    1. Levelised steel cost (2050)        -> results/fig_cost_regimes.png
    2. Emissions intensity (2050)         -> results/fig_emis_regimes.png

Axes:  x = H2 end-cost ($/kg),  y = CCUS cost ($/tCO2).
A single shared colour scale per figure makes the four regimes directly
comparable. Infeasible cells (status != 'solved') are masked (shown grey).

Inputs: one CSV per regime, default mc_2d_<regime>.csv (override via MC_CSV_DIR).
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

CSV_DIR  = os.environ.get("MC_CSV_DIR", ".")
OUT_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT_DIR, exist_ok=True)

REGIMES = [("starved",    "Starved  (0.5%/yr)"),
           ("low",        "Low  (2%/yr)"),
           ("modest",     "Modest  (4%/yr)"),
           ("optimistic", "Optimistic  (6%/yr)")]

CMAP = plt.get_cmap("nipy_spectral").copy()
CMAP.set_bad(color="0.6")   # masked / infeasible cells -> grey


def load_grid(regime, value_col):
    """Return (Z, extent) with Z shaped [n_ccs, n_h2] (y=CCUS, x=H2)."""
    path = os.path.join(CSV_DIR, f"mc_2d_{regime}.csv")
    df = pd.read_csv(path)
    n_h2, n_ccs = df["i_h2"].nunique(), df["i_ccs"].nunique()
    df = df.sort_values(["i_h2", "i_ccs"])
    vals = pd.to_numeric(df[value_col], errors="coerce").values.astype(float)
    vals = np.where(df["status"].values == "solved", vals, np.nan)
    # reshape to [i_h2, i_ccs] then transpose -> [i_ccs, i_h2] for (y=CCUS, x=H2)
    Z = vals.reshape(n_h2, n_ccs).T
    h2  = df["h2_end_cost"].values.reshape(n_h2, n_ccs)[:, 0] / 1000.0   # $/t -> $/kg
    ccs = df["ccs_end_cost"].values.reshape(n_h2, n_ccs)[0, :]
    extent = [h2.min(), h2.max(), ccs.min(), ccs.max()]
    return Z, extent


def make_figure(value_col, title, cbar_label, out_name):
    grids = [(lbl,) + load_grid(reg, value_col) for reg, lbl in REGIMES]
    allvals = np.concatenate([Z[np.isfinite(Z)].ravel() for _, Z, _ in grids])
    vmin, vmax = np.nanpercentile(allvals, [1, 99])
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

    n = len(grids)
    fig, axes = plt.subplots(n, 1, figsize=(11, 9), constrained_layout=False)
    fig.subplots_adjust(left=0.10, right=0.86, top=0.93, bottom=0.07, hspace=0.12)
    fig.suptitle(title, fontsize=13)

    im = None
    for ax, (lbl, Z, extent) in zip(axes, grids):
        im = ax.imshow(Z, origin="lower", extent=extent, aspect="auto",
                       cmap=CMAP, norm=norm, interpolation="bicubic")
        ax.set_ylabel("CCUS\n($/tCO₂)", fontsize=9)
        ax.text(0.012, 0.86, lbl, transform=ax.transAxes, fontsize=10,
                fontweight="bold", color="white",
                bbox=dict(facecolor="black", alpha=0.45, edgecolor="none",
                          boxstyle="round,pad=0.2"))
        if ax is not axes[-1]:
            ax.set_xticklabels([])
    axes[-1].set_xlabel("H₂ end-cost ($/kg)", fontsize=11)

    cax = fig.add_axes([0.88, 0.07, 0.022, 0.86])
    fig.colorbar(im, cax=cax, label=cbar_label)

    out = os.path.join(OUT_DIR, out_name)
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print(f"Saved -> {out}")


def main():
    make_figure("cost_2050",
                "Levelised steel cost (2050) — scrap regimes  (NG 15 $/MMBtu, H₂ start 2030)",
                "$/t crude steel", "fig_cost_regimes.png")
    make_figure("emis_2050",
                "Emissions intensity (2050) — scrap regimes  (NG 15 $/MMBtu, H₂ start 2030)",
                "tCO₂ / t steel", "fig_emis_regimes.png")


if __name__ == "__main__":
    main()
