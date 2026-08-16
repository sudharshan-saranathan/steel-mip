#!/usr/bin/env python3
"""Hydrogen-delay sweep: H2 debut year x emissions cap x infrastructure ramp.

Replaces the token-substitution mechanism in the old h2delay_template.mod
(RAMPVAL/H2REFVAL/EFVAL/H2YRVAL/RAMPLABEL). AMPL resolves `include` against
its cwd, so every run is made with the repository root as cwd and every path
below is root-relative.

    python3 scenarios/hydrogen-delay/run.py                  # full 4x3x3 sweep
    python3 scenarios/hydrogen-delay/run.py --quick          # 1 run, smoke test
    python3 scenarios/hydrogen-delay/run.py --solver highs   # no gurobi licence
"""

import argparse
import pathlib
import sys

from amplpy import AMPL

ROOT = pathlib.Path(__file__).resolve().parents[2]
STUDY = "scenarios/hydrogen-delay"
RESULTS = ROOT / STUDY / "results"

RAMPS = ["ramp_low", "ramp_medium", "ramp_high"]
RAMP_LABELS = {"ramp_low": "Low", "ramp_medium": "Medium", "ramp_high": "High"}
EF_LEVELS = [1.6, 1.8, 2.0]
H2_YEARS = [2030, 2035, 2040, 2045]

# Column order is the contract report.mod's printf writes; keep them in step.
CSV_HEADER = (
    "avg_emi,ramp_label,cap_add_common,h2_ref_cap,ng_h2_start_year,"
    "solve_result,cap_h2dri_2050,total_ccs_2050,lcop,red_h2_2050"
)


def run_one(ramp, ef, h2_year, args, log_path):
    ampl = AMPL()
    ampl.cd(str(ROOT))
    if not args.verbose:
        ampl.set_option("solver_msg", 0)

    ampl.eval("include core/model.mod;")
    ampl.eval(f"include {STUDY}/study.mod;")
    ampl.eval(f'let REGIME := "{RAMP_LABELS[ramp]}";')
    ampl.eval(f"include {STUDY}/axes/{ramp}.mod;")

    # The swept axes. h2_peak_year is a DERIVED param in core/definitions.mod
    # and follows ng_h2_start_year automatically -- it must not be assigned here.
    ampl.eval(f"let avg_emi := {ef};")
    ampl.eval(f"let ng_h2_start_year := {h2_year};")

    ampl.eval(f"option solver {args.solver};")
    if args.solver == "gurobi":
        ampl.eval(f"option gurobi_options '{args.gurobi_options}';")

    ampl.eval("drop emission_monotonic;")
    ampl.eval("solve;")

    status = ampl.get_value("solve_result")
    obj = ampl.get_objective("obj").value()

    # Appends the CSV row and prints the one-line result banner.
    ampl.eval(f"include {STUDY}/report.mod;")

    with open(log_path, "w") as fh:
        fh.write(f"{ramp}  EF={ef}  h2_start={h2_year}  solver={args.solver}\n")
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
                   help="one ramp x one EF x one H2 year, for smoke-testing")
    p.add_argument("--verbose", action="store_true", help="stream solver output")
    args = p.parse_args()

    ramps = RAMPS[1:2] if args.quick else RAMPS
    efs = EF_LEVELS[1:2] if args.quick else EF_LEVELS
    years = H2_YEARS[:1] if args.quick else H2_YEARS

    RESULTS.mkdir(parents=True, exist_ok=True)
    summary = RESULTS / "h2delay_summary.csv"
    summary.write_text(CSV_HEADER + "\n")   # report.mod appends to this

    failures = []
    for ramp in ramps:
        for ef in efs:
            for year in years:
                tag = f"{ramp}_ef{ef}_h2{year}"
                print(f"=== {tag:28s} ", end="", flush=True)
                status, obj = run_one(ramp, ef, year, args,
                                      RESULTS / f"{tag}.txt")
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
