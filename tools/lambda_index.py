"""Screening index: how much of the required abatement each lever could cover.

    lambda_X = S_X / A

A   = sum_t D(t) * (EF_2025 - target)   required cumulative abatement against a
                                        fleet frozen at 2025 intensity
S_X = the most lever X could abate over 2025-2050 if it ran at its ceiling:
      H2    sum_t min(H2 steel ceiling, D) * dEF_H2
      scrap sum_t (scrap pool above 2025 -> steel) * dEF_SCRAP
      CCS   sum_t ccs_avail(t) * CO2 of the remaining 2025-mix output
Only scrap ABOVE the 2025 pool counts: all 37 Mt of 2025 scrap (in BOF and
DRI-EAF charges) is already inside EF_2025. NG-DRI growth is left out, like
grid learning and efficiency.

Ceilings replicate core/definitions.mod (S-curve demand, Gaussian electrolyser
ramp with ratchet, scrap pool growth, CCS deployment ramp). Rough by design:
it ignores the shared build budget, lock-in of early fossil builds, grid
learning and scrap blending in DRI-EAF. Feasibility should rise with
lambda_total; how sharply it does is the test.

    python3 tools/lambda_index.py [feasibility_drivers.xlsx]
"""
import math
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
XLSX = ROOT / "structural/feasibility_and_synergy/feasibility_drivers/data/feasibility_drivers.xlsx"
YEARS = np.arange(2025, 2051)

EF_2025 = 2.53          # model 2025 intensity, tCO2/tCS (MoS reports 2.54)
DEF_H2 = EF_2025 - 0.4  # H2-DRI-EAF: EAF power, pellets, lime
DEF_SCRAP = EF_2025 - 0.5  # scrap-EAF: EAF power on today's grid

H2_PER_TCS = 0.07 * 1.1  # t H2 per t DRI x t DRI per tCS (n6_h2_dri, n7_dri_ratio)
SCRAP_PER_TCS = 1.1     # n8_phi_eaf
RAMP = {"low": 1e6, "medium": 2e6, "high": 3e6}


def demand(d0=152.2e6, d_sat=680e6, g0=0.082):
    k = g0 / (1 - d0 / d_sat)
    t0 = 2025 + math.log(d_sat / d0 - 1) / k
    return d_sat / (1 + np.exp(-k * (YEARS - t0)))


def h2_steel_ceiling(start, ref_cap):
    peak_rate, b0, b1, sigma = 0.25, 0.0, 0.05, 2.0
    peak = start + 5
    base = b0 + (b1 - b0) * (YEARS - 2025) / 25
    bell = base + (peak_rate - (b0 + (b1 - b0) * (peak - 2025) / 25)) * \
        np.exp(-((YEARS - peak) ** 2) / (2 * sigma ** 2))
    bell = np.where(YEARS > peak, np.maximum(bell, peak_rate), bell)
    add = np.where(YEARS >= start, ref_cap * bell, 0.0)
    return np.cumsum(add) / H2_PER_TCS


def scrap_steel_ceiling(rate, seed=37e6):
    return seed * (1 + rate) ** (YEARS - 2025) / SCRAP_PER_TCS


def ccs_avail(phi, start=2035):
    return np.where(YEARS < start, 0.0, phi * (YEARS - start + 1) / (2050 - start + 1))


def lambdas(h2_start, ramp, scrap_rate, ccs_phi, target, D):
    A = (D * (EF_2025 - target)).sum()
    h2 = np.minimum(h2_steel_ceiling(h2_start, RAMP[ramp]), D)
    s = scrap_steel_ceiling(scrap_rate)
    sc = np.minimum(s - s[0], D - h2)
    rest = np.maximum(D - h2 - sc, 0)
    return {
        "lam_h2": (h2 * DEF_H2).sum() / A,
        "lam_scrap": (sc * DEF_SCRAP).sum() / A,
        "lam_ccs": (ccs_avail(ccs_phi) * rest * EF_2025).sum() / A,
    }


def auc(score, y):
    """Probability a random feasible cell scores above a random infeasible one."""
    r = pd.Series(score).rank().values
    n1, n0 = y.sum(), (~y).sum()
    return (r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def main():
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else XLSX
    df = pd.read_excel(path, sheet_name="raw_matrix")
    if "ccs_phi" not in df:
        df["ccs_phi"] = 0.25
    D = demand()
    keys = ["h2_start", "ramp", "scrap_rate", "ccs_phi", "avg_emi"]
    rows = [{**r, **lambdas(r["h2_start"], r["ramp"], r["scrap_rate"],
                            r["ccs_phi"], r["avg_emi"], D)}
            for r in df[keys].drop_duplicates().to_dict("records")]
    df = df.merge(pd.DataFrame(rows), on=keys)
    df["lam_total"] = df.lam_h2 + df.lam_scrap + df.lam_ccs
    df["feasible"] = df.solve_result == "solved"
    y = df.feasible.values

    print(f"cells {len(df):,}, feasible {y.mean():.1%}")
    for c in ("lam_h2", "lam_scrap", "lam_ccs", "lam_total"):
        print(f"  AUC {c:10s} {auc(df[c].values, y):.3f}")
    bins = [0, 0.6, 0.8, 0.9, 1.0, 1.1, 1.2, 1.4, 1.7, 10]
    df["bin"] = pd.cut(df.lam_total, bins)
    print("\nfeasible share by lambda_total:")
    print(df.groupby("bin", observed=True).feasible.agg(["size", "mean"]).round(3).to_string())
    print("\nby target:")
    for ef, g in df.groupby("avg_emi"):
        f = g[g.feasible]
        print(f"  {ef}: AUC {auc(g.lam_total.values, g.feasible.values):.3f}, "
              f"range {g.lam_total.min():.2f}-{g.lam_total.max():.2f}, "
              f"cells <=1: {(g.lam_total <= 1).sum()} ({g[g.lam_total <= 1].feasible.sum()} feasible), "
              f"min feasible {f.lam_total.min():.3f}")
        print("     mean lambdas:", g[["lam_h2", "lam_scrap", "lam_ccs"]].mean().round(3).to_dict())
    out = ROOT / "tools" / "lambda_index.csv"
    df.drop(columns="bin").to_csv(out, index=False)
    print(f"\nwritten {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
