#!/usr/bin/env python3
"""Scrap-growth sweep: emissions target x scrap-availability growth rate.

Replaces the Windows-only scrap.bat + scrap_template.mod token substitution
(EFVAL/SCRAPVAL). AMPL resolves `include` against its cwd, so every run is
made with the repository root as cwd and every path below is root-relative.

n8_scrap_limit is a DERIVED param in core/definitions.mod and follows
n8_scrap_rate automatically -- must NOT be assigned directly.

    python3 scenarios/structural-sensitivity/scrap/run.py                # full 3x11 = 33 runs
    python3 scenarios/structural-sensitivity/scrap/run.py --quick        # 1 run, smoke test
    python3 scenarios/structural-sensitivity/scrap/run.py --solver highs
"""

import argparse
import pathlib
import sys

from amplpy import AMPL

ROOT = pathlib.Path(__file__).resolve().parents[3]
STUDY = "scenarios/structural-sensitivity/scrap"
RESULTS = ROOT / STUDY / "results"

EF_LEVELS = [1.6, 1.8, 2.0]
SCRAP_RATES = [round(0.01 * i, 2) for i in range(11)]  # 0.00 .. 0.10

CSV_HEADER = (
    "avg_emi,scrap_rate,solve_result,h2dri_cap_2050,ccs_2050,red_h2_2050,"
    "lcop,scrap_use_2050,scrap_limit_2050,scrapeaf_share_2050"
)


def run_one(ef, scrap_rate, args, log_path):
    ampl = AMPL()
    ampl.cd(str(ROOT))
    if not args.verbose:
        ampl.set_option("solver_msg", 0)

    ampl.eval("include core/model.mod;")
    ampl.eval(f"include {STUDY}/study.mod;")

    ampl.eval(f"let avg_emi := {ef};")
    ampl.eval(f"let n8_scrap_rate := {scrap_rate};")

    ampl.eval(f"option solver {args.solver};")
    if args.solver == "gurobi":
        ampl.eval(f"option gurobi_options '{args.gurobi_options}';")

    ampl.eval("drop emission_monotonic;")
    ampl.eval("solve;")

    status = ampl.get_value("solve_result")
    obj = ampl.get_objective("obj").value()

    ampl.eval(f"include {STUDY}/report.mod;")

    with open(log_path, "w") as fh:
        fh.write(f"EF={ef}  scrap_rate={scrap_rate}  solver={args.solver}\n")
        fh.write(f"solve_result={status}\nobjective={obj:.6f}\n")

    ampl.close()
    return status, obj


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--solver", default="gurobi",
                   help="gurobi (default; matches the published runs) or highs")
    p.add_argument("--gurobi-options",
                   default="Threads=10 TimeLimit=300 mipgap=0.002")
    p.add_argument("--quick", action="store_true",
                   help="one EF x one scrap rate, for smoke-testing")
    p.add_argument("--verbose", action="store_true", help="stream solver output")
    args = p.parse_args()

    efs = EF_LEVELS[1:2] if args.quick else EF_LEVELS       # 1.8
    rates = SCRAP_RATES[4:5] if args.quick else SCRAP_RATES  # 0.04

    RESULTS.mkdir(parents=True, exist_ok=True)
    summary = RESULTS / "scrap_summary.csv"
    summary.write_text(CSV_HEADER + "\n")

    failures = []
    for ef in efs:
        for scrap_rate in rates:
            tag = f"ef{ef}_scrap{scrap_rate}"
            print(f"=== {tag:20s} ", end="", flush=True)
            status, obj = run_one(ef, scrap_rate, args, RESULTS / f"{tag}.txt")
            print(f"{status:12s} obj={obj:.6f}")
            if status != "solved":
                failures.append((tag, status))

    print(f"\nSummary: {summary.relative_to(ROOT)}")
    if failures:
        print("NOT SOLVED: " + ", ".join(f"{t} ({s})" for t, s in failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
