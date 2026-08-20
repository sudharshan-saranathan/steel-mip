#!/usr/bin/env python3
"""Recompute every Section A headline number on the post-capacity-fix matrix.

Every number in docs/ must come from this script, not from arithmetic in prose.

Two rules govern the whole file:

1. COST CLAIMS USE CALIBRATED ROWS ONLY. `extrapolated == 1` means theta_grid
   left [0,1] and the COUPLED electricity tariff is extrapolated past its
   $0.055-0.085/kWh anchors. That is 67% of solved rows, so a table computed
   over "all solved" is mostly extrapolated cost. Feasibility is fine
   everywhere; $/t is not.

2. DIFFERENCES ARE PAIRED. A delta between two levels of one lever is only
   meaningful over coordinates feasible at BOTH levels. Infeasibility runs
   4.8% at h2_start=2030 and 62.2% at 2045, so averaging over whatever
   survives makes any penalty shrink by selection alone -- in exactly the
   direction of the headline claim. Every delta below reports n_pairs and
   n_dropped.
"""

import pathlib
import pandas as pd
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import axes as AX

RESULTS = pathlib.Path(__file__).resolve().parent / "results"
COORDS = ["ccoal", "ng", "h2_start", "scrap_rate", "grid_ef_target",
          "ramp", "build_cap", "legacy", "avg_emi"]

# Baseline anchor for the new axes, so pre/post comparisons against the
# pre-fix snapshot isolate the model change instead of the added variation.
ANCHOR = {"ramp": "medium", "build_cap": "tight", "legacy": "run-life",
          "grid_ef_target": 0.00045}

df = pd.read_parquet(RESULTS / "matrix.parquet")
df["solved"] = df.solve_result == "solved"
sol = df[df.solved]
cal = sol[sol.extrapolated == 0]

rule = lambda t: print(f"\n{'='*70}\n{t}\n{'='*70}")


def paired(frame, lever, lo, hi, metric="lcop", by=None):
    """Mean metric(hi) - metric(lo) over coordinates feasible at BOTH levels."""
    keys = [c for c in COORDS if c != lever]
    a = frame[frame[lever] == lo].set_index(keys)[metric]
    b = frame[frame[lever] == hi].set_index(keys)[metric]
    a, b = a[~a.index.duplicated()], b[~b.index.duplicated()]
    joined = pd.concat({"lo": a, "hi": b}, axis=1).dropna()
    n_lo = len(a)
    d = (joined.hi - joined.lo)
    if by is None:
        return dict(delta=d.mean(), n_pairs=len(d), n_dropped=n_lo - len(d))
    g = joined.assign(d=d).groupby(by, observed=True)
    return g.agg(delta=("d", "mean"), n_pairs=("d", "size")).assign(
        lo_feasible=frame[frame[lever] == lo].groupby(by, observed=True).size())


# --------------------------------------------------------------- checks ---
rule("CHECK 1 -- is `extrapolated` exactly the uncalibrated grid levels?")
by_ef = sol.groupby("grid_ef_target").extrapolated.agg(["min", "max"])
print(by_ef)
inside = set(by_ef[(by_ef["max"] == 0)].index)
print(f"\ncalibrated levels: {sorted(inside)}")
print(f"flag is a pure function of grid_ef_target: "
      f"{bool((by_ef['min'] == by_ef['max']).all())}")
print(f"solved rows: {len(sol):,}   calibrated: {len(cal):,} "
      f"({len(cal)/len(sol):.1%})")

rule("CHECK 2 -- do `legacy` / `build_cap` change feasibility cell-for-cell?")
for lever in ("legacy", "build_cap"):
    keys = [c for c in COORDS if c != lever]
    g = df.groupby(keys, observed=True).solved.agg(["min", "max"])
    disagree = int((g["min"] != g["max"]).sum())
    print(f"  {lever:10s}: {disagree:,} of {len(g):,} coordinate groups "
          f"disagree across its levels")

rule("CHECK 3 -- does the emissions cap bind? (avg_emis vs target)")
print(sol.groupby("avg_emi").avg_emis.agg(["min", "max", "mean"]).round(4))
slack = (sol.avg_emi - sol.avg_emis)
print(f"\nrows with slack > 0.01 tCO2/t: {(slack > 0.01).sum():,} "
      f"of {len(sol):,}   max slack {slack.max():.4f}")

rule("CHECK 4 -- is `share_scrap` pinned at a constant (the 41.5% artifact)?")
print(sol.share_scrap.describe().round(4).to_dict())
top = sol.share_scrap.round(4).value_counts().head(3)
print(f"\nmost common values: {top.to_dict()}")

# ------------------------------------------------------------ headlines ---
rule("HEADLINE 1 -- cost of delaying H2-DRI, by scrap growth")
print("calibrated rows only; paired on the other 8 coordinates\n")
base = cal[(cal.ccoal == "abundant") & (cal.ng == "policy") & (cal.avg_emi == 1.8)]
for lo, hi in ((2030, 2045), (2030, 2035), (2030, 2040)):
    t = paired(base, "h2_start", lo, hi, by="scrap_rate")
    t["delta"] = t.delta.round(2)
    print(f"-- {lo} -> {hi} --")
    print(t.to_string(), "\n")

rule("HEADLINE 1b -- same, at the full baseline anchor (one pair per row)")
b = base.copy()
for k, v in ANCHOR.items():
    b = b[b[k] == v]
print(b.set_index(["scrap_rate", "h2_start"]).lcop.round(2).unstack().to_string())

rule("HEADLINE 2 -- mandated phase-out of the 2025 fleet")
r = paired(cal, "legacy", "run-life", "mandated-phaseout")
print(f"  LCOP  +{r['delta']:.2f} $/t   (n_pairs {r['n_pairs']:,}, "
      f"dropped {r['n_dropped']:,})")
for m in ("cum_co2", "share_bof", "share_h2"):
    r = paired(cal, "legacy", "run-life", "mandated-phaseout", metric=m)
    print(f"  {m:10s} {r['delta']:+.6g}")

rule("HEADLINE 2b -- is the phase-out cost stable across h2_start?")
print("(if it is, the number survives whatever the ramp-crest decision is)")
t = paired(cal, "legacy", "run-life", "mandated-phaseout", by="h2_start")
print(t.round(2).to_string())

rule("HEADLINE 3 -- shared annual build budget")
for lo, hi in (("tight", "mid"), ("tight", "loose"), ("mid", "loose")):
    r = paired(cal, "build_cap", lo, hi)
    print(f"  {lo:6s} -> {hi:6s}  {r['delta']:+.2f} $/t   "
          f"(n_pairs {r['n_pairs']:,}, dropped {r['n_dropped']:,})")

print("\n  share of the 20->40 gain captured by the first 10 Mt/yr: "
      f"{paired(cal,'build_cap','tight','mid')['delta']/paired(cal,'build_cap','tight','loose')['delta']:.1%}")

rule("HEADLINE 3b -- is the build-budget value stable across h2_start?")
t = paired(cal, "build_cap", "tight", "loose", by="h2_start")
print(t.round(2).to_string())

rule("HEADLINE 4 -- electrolyser ramp")
for lo, hi in (("low", "medium"), ("medium", "high")):
    r = paired(cal, "ramp", lo, hi)
    print(f"  {lo:6s} -> {hi:6s}  {r['delta']:+.2f} $/t   "
          f"(n_pairs {r['n_pairs']:,}, dropped {r['n_dropped']:,})")

rule("HEADLINE 5 -- mechanism: H2-DRI share is displaced by scrap")
print(base[base.h2_start == 2030].groupby("scrap_rate", observed=True)[
    ["share_h2", "share_scrap", "share_bof", "scrap_use_2050"]].mean().round(4).to_string())

rule("HEADLINE 4b -- does the ramp still bind? share_h2 by ramp level")
print("(if flat, H2 uptake is cost-limited, not deployment-limited)")
kk = [c for c in COORDS if c != "ramp"]
piv = cal.pivot_table(index=kk, columns="ramp", values="share_h2",
                      observed=True).dropna()
print(f"  paired (n={len(piv):,}):  low->medium {(piv['medium']-piv['low']).mean():+.4f}"
      f"   medium->high {(piv['high']-piv['medium']).mean():+.4f}")
print(cal.groupby("ramp", observed=True)[["share_h2", "cap_h2dri_2050"]]
         .mean().round(4).to_string())

rule("HEADLINE 6 -- feasibility frontier (all 46,656 cells)")
print("infeasible share by h2_start: "
      f"{(1 - df.groupby('h2_start').solved.mean()).round(3).to_dict()}\n")
piv = df.pivot_table(index="scrap_rate", columns="avg_emi", values="solved",
                     aggfunc="mean").round(3)
print("P(solved) by scrap growth x emissions target\n", piv.to_string())
print("\nP(solved) by h2_start x scrap growth\n",
      df.pivot_table(index="scrap_rate", columns="h2_start", values="solved",
                     aggfunc="mean").round(3).to_string())

# The either/or reading must be checked in the JOINT, not the marginal: the
# table above averages over avg_emi, including the easy 2.0 target.
for tgt in AX.AVG_EMI:
    print(f"\n  -- within avg_emi {tgt} --")
    print(df[df.avg_emi == tgt].pivot_table(
        index="scrap_rate", columns="h2_start", values="solved",
        aggfunc="mean").round(3).to_string())
