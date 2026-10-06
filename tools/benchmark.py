"""Benchmark cells used to measure the effect of each fix-wave-01 commit.

Solves a fixed set of H2-delay cells (paper Fig. 3 backdrop) plus a
calibration readout of 2025, and writes one CSV row per cell.

    python3 tools/benchmark.py --tag <label> [--out tools/benchmark_results.csv]

Uses AMPL with HiGHS when a full AMPL licence is active; otherwise the
expand-based bridge in tools/ampl_highs_bridge.py (validated against Fig. 3).
"""
import argparse
import csv
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

CELLS = [  # (avg_emi, h2_ref_cap, h2_start)
    (1.6, 4_000_000, 2030), (1.6, 4_000_000, 2035),
    (1.8, 4_000_000, 2030), (1.8, 4_000_000, 2035),
    (1.8, 4_000_000, 2040), (1.8, 4_000_000, 2045),
    (2.0, 4_000_000, 2030), (2.0, 4_000_000, 2045),
]
METRICS = ["m_lcop", "m_avg_emis", "m_sh_bof", "m_sh_cdri", "m_sh_ngdri",
           "m_sh_h2", "m_sh_scrap", "m_cum_captured"]
EXTRA = {
    "ei_2025": "total_emissions[2025]/total_steel[2025]",
    "ei_2050": "total_emissions[2050]/total_steel[2050]",
    "capex_pv_bn": "sum{t in T} discount_factor[t]*capex_cost[t]/1e9",
    "grid_twh_2025": "grid_power_in[2025]/1e9",
}


def full_licence(ampl):
    try:
        ampl.eval("option solver highs;")
        out = ampl.get_output("option version;")
        return "Demo license" not in out and "demo" not in out.lower()
    except Exception:
        return False


def solve_cell(ef, ramp, h2):
    from amplpy import AMPL
    from ampl_highs_bridge import solve_bridge
    a = AMPL()
    a.cd(str(ROOT))
    a.set_option("solver_msg", 0)
    a.eval("include core/model.mod;")
    a.eval("include structural/h2_delay/template_h2delay.mod;")
    a.eval(f"let avg_emi := {ef}; let h2_ref_cap := {ramp}; "
           f"let ng_h2_start_year := {h2};")
    a.eval("drop emission_monotonic;")
    status, _ = solve_bridge(a)
    row = {"avg_emi": ef, "h2_ref_cap": ramp, "h2_start": h2, "status": status}
    if status == "solved":
        a.eval("include structural/report.mod;")
        for m in METRICS:
            row[m] = round(a.get_value(m), 4)
        for k, expr in EXTRA.items():
            row[k] = round(a.get_value(expr), 4)
    a.close()
    return row


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tag", required=True)
    p.add_argument("--out", default=str(ROOT / "tools" / "benchmark_results.csv"))
    args = p.parse_args()
    cols = ["tag", "avg_emi", "h2_ref_cap", "h2_start", "status"] + METRICS + list(EXTRA)
    out = pathlib.Path(args.out)
    new = not out.exists()
    with out.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        if new:
            w.writeheader()
        for ef, ramp, h2 in CELLS:
            row = {"tag": args.tag, **solve_cell(ef, ramp, h2)}
            w.writerow(row)
            print({k: row.get(k) for k in ("tag", "avg_emi", "h2_start", "status",
                                             "m_lcop", "m_sh_h2", "ei_2025")}, flush=True)


if __name__ == "__main__":
    main()
