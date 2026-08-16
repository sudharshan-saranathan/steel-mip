#!/usr/bin/env python3
"""Section A (structural feasibility) figures, one per migrated study.

Reads each study's results/*.csv (see docs/HANDOFF.md for the migration that
produced them) and writes one PNG per study to scenarios/figs/. Run from the
repository root:

    python3 scenarios/plot_section_a.py

Regret-analysis and monte-carlo (Section B) are not covered here -- they are
still on the old per-study layout, not yet migrated.
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(ROOT, "figs")
os.makedirs(FIGS, exist_ok=True)

# Palette + house style, matching the mip-v2 branch's Subsection A figures
# for visual continuity across the paper.
C1, C2, C3 = "#264653", "#e76f51", "#2a9d8f"
INFEAS = "#cccccc"


def style(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def savefig(fig, name):
    out = os.path.join(FIGS, name)
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved -> {out}")


# ---------------------------------------------------------------------------
# 1. import-dependence: total import bill vs H2 start year, by coal/NG regime
# ---------------------------------------------------------------------------
def plot_import_dependence():
    df = pd.read_csv(os.path.join(ROOT, "import-dependence/results/impdep_summary.csv"))
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = {"HiCoal-HiNG": C1, "HiCoal-LoNG": C2, "LoCoal-HiNG": C3, "LoCoal-LoNG": "#e9c46a"}
    for regime, g in df.groupby("regime"):
        g = g.sort_values("h2_start")
        feas = g[g.solve_result == "solved"]
        infeas = g[g.solve_result != "solved"]
        ax.plot(feas.h2_start, feas.import_bill / 1e9, "o-", color=colors.get(regime, "#999"),
                 label=regime, linewidth=2)
        if len(infeas):
            ax.scatter(infeas.h2_start, [ax.get_ylim()[1]] * len(infeas), marker="x",
                       color=INFEAS, zorder=5)
    ax.set_xlabel("H2-DRI start year")
    ax.set_ylabel("Cumulative import bill, $B (coking coal + NG)")
    ax.set_title("Import-dependence: cost of delaying H2 by coal/NG availability regime")
    ax.legend(frameon=False, fontsize=9)
    style(ax)
    savefig(fig, "fig_import_dependence.png")


# ---------------------------------------------------------------------------
# 2. hydrogen-delay: LCOP vs H2 start year, panel per EF, line per ramp level
# ---------------------------------------------------------------------------
def plot_hydrogen_delay():
    df = pd.read_csv(os.path.join(ROOT, "hydrogen-delay/results/h2delay_summary.csv"))
    efs = sorted(df.avg_emi.unique())
    ramps = ["Low", "Medium", "High"]
    colors = {"Low": C1, "Medium": C2, "High": C3}
    fig, axes = plt.subplots(1, len(efs), figsize=(4 * len(efs), 4.5), sharey=True)
    for ax, ef in zip(axes, efs):
        sub = df[df.avg_emi == ef]
        for ramp in ramps:
            g = sub[sub.ramp_label == ramp].sort_values("ng_h2_start_year")
            feas = g[g.solve_result == "solved"]
            ax.plot(feas.ng_h2_start_year, feas.lcop, "o-", color=colors[ramp],
                     label=ramp, linewidth=2)
        ax.set_title(f"ET = {ef}")
        ax.set_xlabel("H2-DRI start year")
        style(ax)
    axes[0].set_ylabel("Levelised cost of production, $/t")
    axes[0].legend(frameon=False, fontsize=9, title="Ramp")
    fig.suptitle("Hydrogen-delay: cost of postponing H2 by emissions target and build ramp", y=1.03)
    savefig(fig, "fig_hydrogen_delay.png")


# ---------------------------------------------------------------------------
# 3. scrap: H2-DRI and CCS 2050 capacity vs scrap growth rate, panel per EF
# ---------------------------------------------------------------------------
def plot_scrap():
    df = pd.read_csv(os.path.join(ROOT, "structural-sensitivity/scrap/results/scrap_summary.csv"))
    efs = sorted(df.avg_emi.unique())
    fig, axes = plt.subplots(1, len(efs), figsize=(4 * len(efs), 4.5), sharey=True)
    for ax, ef in zip(axes, efs):
        g = df[(df.avg_emi == ef) & (df.solve_result == "solved")].sort_values("scrap_rate")
        ax.plot(g.scrap_rate, g.h2dri_cap_2050 / 1e6, "o-", color=C1, label="H2-DRI capacity", linewidth=2)
        ax.plot(g.scrap_rate, g.ccs_2050 / 1e6, "o-", color=C2, label="CCS captured", linewidth=2)
        ax.set_title(f"ET = {ef}")
        ax.set_xlabel("Scrap growth rate, %/yr")
        style(ax)
    axes[0].set_ylabel("2050 capacity/capture, Mt")
    axes[0].legend(frameon=False, fontsize=9)
    fig.suptitle("Scrap-growth study: does scrap displace hydrogen or CCS?", y=1.03)
    savefig(fig, "fig_scrap.png")


# ---------------------------------------------------------------------------
# 4. abatement: 2050 total emissions by scenario vs the frozen-structure baseline
# ---------------------------------------------------------------------------
def plot_abatement():
    df = pd.read_csv(os.path.join(ROOT, "structural-sensitivity/abatement/results/abatement_yearly.csv"))
    y2050 = df[df.year == 2050].set_index("run")
    order = ["Baseline", "EF1.6", "EF1.8", "S4", "S8", "RL", "RH"]
    order = [r for r in order if r in y2050.index]
    vals = y2050.loc[order, "total_emissions"] / 1e6
    colors = [C1 if r == "Baseline" else C2 for r in order]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(order, vals, color=colors)
    for i, v in enumerate(vals):
        ax.text(i, v, f"{v:.0f}", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("2050 total emissions, MtCO2")
    ax.set_title("Abatement anatomy: 2050 emissions by scenario vs frozen-structure baseline")
    style(ax)
    savefig(fig, "fig_abatement.png")


# ---------------------------------------------------------------------------
# 5. whr: effective CCS capture cost vs joint CCS+grid maturity theta
# ---------------------------------------------------------------------------
def plot_whr():
    df = pd.read_csv(os.path.join(ROOT, "structural-sensitivity/whr/results/whr_summary.csv"))
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for mode, color in [("integrated", C1), ("boiler-only", C2)]:
        g = df[(df["mode"] == mode) & (df.solve_result == "solved")].sort_values("theta")
        ax.plot(g.theta, g.eff_capture_cost, "o-", color=color, label=mode, linewidth=2)
    ax.set_xlabel("Joint CCS+grid ecosystem maturity, theta")
    ax.set_ylabel("Effective capture cost, $/tCO2")
    ax.set_title("WHR-CCS integration: value of waste-heat steam vs boiler-only")
    ax.legend(frameon=False, fontsize=9)
    style(ax)
    savefig(fig, "fig_whr.png")


# ---------------------------------------------------------------------------
# 6. grid: feasibility frontier -- dirtiest feasible 2050 grid EF vs scrap
#    growth rate, one line per H2 start year
# ---------------------------------------------------------------------------
def plot_grid():
    df = pd.read_csv(os.path.join(ROOT, "structural-sensitivity/grid/results/grid_summary.csv"))
    feas = df[df.solve_result == "solved"]
    frontier = feas.groupby(["h2_start", "scrap_rate"])["grid_ef_end"].max().reset_index()
    fig, ax = plt.subplots(figsize=(7, 5))
    cmap = plt.get_cmap("viridis")
    h2_years = sorted(frontier.h2_start.unique())
    for i, h2 in enumerate(h2_years):
        g = frontier[frontier.h2_start == h2].sort_values("scrap_rate")
        ax.plot(g.scrap_rate, g.grid_ef_end * 1000, "o-",
                 color=cmap(i / max(len(h2_years) - 1, 1)), label=str(h2), linewidth=2)
    ax.set_xlabel("Scrap growth rate, %/yr")
    ax.set_ylabel("Dirtiest feasible 2050 grid EF, kg-CO2/kWh")
    ax.set_title("Grid-offset requirement: how clean must the grid be, by H2 timing and scrap")
    ax.legend(frameon=False, fontsize=8, title="H2 start", ncol=2)
    style(ax)
    savefig(fig, "fig_grid.png")


if __name__ == "__main__":
    plot_import_dependence()
    plot_hydrogen_delay()
    plot_scrap()
    plot_abatement()
    plot_whr()
    plot_grid()
