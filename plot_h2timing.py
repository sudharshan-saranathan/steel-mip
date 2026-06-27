#!/usr/bin/env python
"""
H2-timing discriminator figure (modest scrap regime).

Compares the H2 x CCUS cost plane for two H2-DRI start years:
    top    : H2 start 2030  (H2 ramps -> strong H2 gradient, inverted CCUS slope)
    bottom : H2 start 2039  (H2 can't ramp by 2050 -> flat, capture-saturated)

Two figures, each two stacked wide heatmaps (shared colour scale):
    results/fig_h2timing_emis.png   -- emissions intensity (2050)
    results/fig_h2timing_cost.png   -- levelised steel cost (2050)

x = H2 end-cost ($/kg), y = CCUS cost ($/tCO2). Infeasible cells masked grey.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

PROJECT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = __import__("_runpaths").PLOTS
os.makedirs(OUT_DIR, exist_ok=True)

PANELS = [("mc_2d_modest.csv",          "H₂ start 2030  (ramps to 2050)"),
          ("mc_2d_modest_h2y2039.csv",  "H₂ start 2039  (capped by 2050)")]

CMAP_NAME = os.environ.get("MC_CMAP", "nipy_spectral")
SUFFIX    = "" if CMAP_NAME == "nipy_spectral" else f"_{CMAP_NAME.lower()}"
CMAP = plt.get_cmap(CMAP_NAME).copy()
CMAP.set_bad(color="0.6")


def load_grid(csv, value_col):
    df = pd.read_csv(os.path.join(PROJECT, csv))
    n_h2, n_ccs = df["i_h2"].nunique(), df["i_ccs"].nunique()
    df = df.sort_values(["i_h2", "i_ccs"])
    vals = pd.to_numeric(df[value_col], errors="coerce").values.astype(float)
    vals = np.where(df["status"].values == "solved", vals, np.nan)
    Z = vals.reshape(n_h2, n_ccs).T               # [i_ccs, i_h2] -> y=CCUS, x=H2
    h2  = df["h2_capex_mult"].values.reshape(n_h2, n_ccs)[:, 0]   # green-H2 capex multiplier
    ccs = df["ccs_end_cost"].values.reshape(n_h2, n_ccs)[0, :]
    return Z, [h2.min(), h2.max(), ccs.min(), ccs.max()]


def make_figure(value_col, title, cbar_label, out_name):
    grids = [(lbl,) + load_grid(csv, value_col) for csv, lbl in PANELS]
    allvals = np.concatenate([Z[np.isfinite(Z)].ravel() for _, Z, _ in grids])
    norm = mcolors.Normalize(*np.nanpercentile(allvals, [1, 99]))

    fig, axes = plt.subplots(2, 1, figsize=(11, 5.4))
    fig.subplots_adjust(left=0.10, right=0.86, top=0.90, bottom=0.11, hspace=0.04)
    fig.suptitle(title, fontsize=13)

    im = None
    for ax, (lbl, Z, extent) in zip(axes, grids):
        im = ax.imshow(Z, origin="lower", extent=extent, aspect="auto",
                       cmap=CMAP, norm=norm, interpolation="bicubic")
        ax.set_ylabel("CCUS\n($/tCO₂)", fontsize=9)
        ax.text(0.012, 0.84, lbl, transform=ax.transAxes, fontsize=10,
                fontweight="bold", color="white",
                bbox=dict(facecolor="black", alpha=0.45, edgecolor="none",
                          boxstyle="round,pad=0.2"))
        if ax is not axes[-1]:
            ax.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    axes[-1].set_xlabel("green-H₂ capex multiplier (× central)", fontsize=11)

    cax = fig.add_axes([0.88, 0.11, 0.022, 0.79])
    fig.colorbar(im, cax=cax, label=cbar_label)
    base, ext = os.path.splitext(out_name)
    out = os.path.join(OUT_DIR, f"{base}{SUFFIX}{ext}")
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print(f"Saved -> {out}")


def main():
    make_figure("emis_2050",
                "Emissions intensity (2050) — H₂-timing effect  (modest scrap, NG 15 $/MMBtu)",
                "tCO₂ / t steel", "fig_h2timing_emis.png")
    make_figure("cost_2050",
                "Levelised steel cost (2050) — H₂-timing effect  (modest scrap, NG 15 $/MMBtu)",
                "$/t crude steel", "fig_h2timing_cost.png")


if __name__ == "__main__":
    main()
