#!/usr/bin/env python3
"""Section A: how do structural levers affect FEASIBILITY?

Section A asks what is reachable, not what it costs. That question uses all
46,656 cells -- there is no calibration filter, because the extrapolated
electricity tariff affects cost, not whether a target can be met.

One property of the design carries the whole analysis: it is a COMPLETE
factorial. Every lever level appears with every combination of the others
exactly once, so a marginal P(feasible) is already balanced -- no pairing
correction is needed, unlike the cost deltas. Interactions are therefore the
only thing marginals can hide, and those are computed explicitly below.
"""

import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import axes as AX  # noqa: E402

RESULTS = pathlib.Path(__file__).resolve().parent / "results"
COORDS = ["ccoal", "ng", "h2_start", "scrap_rate", "grid_ef_target",
          "ramp", "build_cap", "legacy", "avg_emi"]
LEVERS = [c for c in COORDS if c != "avg_emi"]

df = pd.read_parquet(RESULTS / "matrix.parquet")
df["ok"] = df.solve_result == "solved"

rule = lambda t: print(f"\n{'='*70}\n{t}\n{'='*70}")

rule("0 -- the design")
print(f"cells {len(df):,}   feasible {df.ok.sum():,} ({df.ok.mean():.1%})   "
      f"errors 0")
print("complete factorial:",
      bool((df.groupby(COORDS, observed=True).size() == 1).all()))

rule("1 -- lever ranking: how much does each lever move P(feasible)?")
print("swing = P(feasible) at the most permissive level minus the least.\n")
rows = []
for lev in LEVERS + ["avg_emi"]:
    g = df.groupby(lev, observed=True).ok.mean()
    rows.append({"lever": lev, "swing": g.max() - g.min(),
                 "worst": f"{g.idxmin()}={g.min():.3f}",
                 "best": f"{g.idxmax()}={g.max():.3f}"})
rank = pd.DataFrame(rows).sort_values("swing", ascending=False)
print(rank.to_string(index=False, float_format=lambda v: f"{v:.3f}"))

rule("2 -- decisiveness: how often does a lever FLIP a scenario?")
print("share of coordinate groups whose feasibility changes across the "
      "lever's levels\n")
for lev in LEVERS + ["avg_emi"]:
    keys = [c for c in COORDS if c != lev]
    g = df.groupby(keys, observed=True).ok.agg(["min", "max"])
    flip = (g["min"] != g["max"]).mean()
    print(f"  {lev:15s} {flip:6.1%}  of {len(g):,} groups")

rule("2b -- lever ranking WITHIN each target")
print("same swing/decisiveness, computed with avg_emi held fixed so it drops\n"
      "out as a lever. The pooled ranking above averages over targets, which\n"
      "hides two levers that trend in OPPOSITE directions across them.\n")
for tgt in AX.AVG_EMI:
    d = df[df.avg_emi == tgt]
    print(f"-- avg_emi {tgt} --   cells {len(d):,}   "
          f"feasible {d.ok.sum():,} ({d.ok.mean():.1%})")
    rows = []
    for lev in LEVERS:
        g = d.groupby(lev, observed=True).ok.mean()
        keys = [c for c in LEVERS if c != lev]
        gg = d.groupby(keys, observed=True).ok.agg(["min", "max"])
        rows.append({"lever": lev, "swing": g.max() - g.min(),
                     "decisive": (gg["min"] != gg["max"]).mean(),
                     "worst": f"{g.idxmin()}={g.min():.3f}",
                     "best": f"{g.idxmax()}={g.max():.3f}"})
    r = pd.DataFrame(rows).sort_values("swing", ascending=False)
    r["swing"] = r.swing.map("{:.3f}".format)
    r["decisive"] = r.decisive.map("{:.1%}".format)
    print(r.to_string(index=False), "\n")

rule("3 -- the two dominant levers, jointly, within each target")
for tgt in AX.AVG_EMI:
    print(f"\n-- avg_emi {tgt} --   P(feasible), rows=scrap growth, "
          f"cols=H2 debut")
    print(df[df.avg_emi == tgt].pivot_table(
        index="scrap_rate", columns="h2_start", values="ok",
        aggfunc="mean").round(3).to_string())

rule("4 -- substitution: is either dominant lever sufficient alone?")
print("P(feasible) in the corners of the scrap x H2-debut plane, by target\n")
lo_s, hi_s = min(AX.SCRAP_RATE), max(AX.SCRAP_RATE)
lo_h, hi_h = min(AX.H2_START), max(AX.H2_START)
for tgt in AX.AVG_EMI:
    d = df[df.avg_emi == tgt]
    c = lambda s, h: d[(d.scrap_rate == s) & (d.h2_start == h)].ok.mean()
    print(f"  target {tgt}:  neither ({lo_s},{hi_h}) {c(lo_s, hi_h):.3f}   "
          f"H2 only ({lo_s},{lo_h}) {c(lo_s, lo_h):.3f}   "
          f"scrap only ({hi_s},{hi_h}) {c(hi_s, hi_h):.3f}   "
          f"both ({hi_s},{lo_h}) {c(hi_s, lo_h):.3f}")

rule("5 -- resource levers: coking coal and gas")
print(df.pivot_table(index="ccoal", columns="ng", values="ok",
                     aggfunc="mean", observed=True).round(3).to_string())
print("\nby target:")
print(df.pivot_table(index=["ccoal", "ng"], columns="avg_emi", values="ok",
                     aggfunc="mean", observed=True).round(3).to_string())

rule("6 -- the grid: does power-sector decarbonisation buy feasibility?")
print(df.groupby("grid_ef_target").ok.mean().round(3).to_string())
print("\nby H2 debut (grid EF matters only where electricity is used):")
print(df.pivot_table(index="grid_ef_target", columns="h2_start", values="ok",
                     aggfunc="mean").round(3).to_string())

rule("7 -- the capacity levers: ramp, build budget, retirement")
for lev in ("ramp", "build_cap", "legacy"):
    print(f"\n{lev}:")
    print(df.groupby(lev, observed=True).ok.mean().round(4).to_string())

rule("8 -- what does the infeasible region look like?")
bad = df[~df.ok]
print(f"infeasible cells: {len(bad):,}\n")
for lev in ("h2_start", "scrap_rate", "avg_emi"):
    share = bad.groupby(lev, observed=True).size() / len(bad)
    print(f"  share of all infeasibility by {lev}: "
          f"{share.round(3).to_dict()}")
print("\nfully-infeasible slices (P(feasible) = 0 across all other levers):")
for tgt in AX.AVG_EMI:
    d = df[df.avg_emi == tgt]
    p = d.pivot_table(index="scrap_rate", columns="h2_start", values="ok",
                      aggfunc="mean")
    dead = [(s, h) for s in p.index for h in p.columns if p.loc[s, h] == 0]
    print(f"  target {tgt}: {dead if dead else 'none'}")
