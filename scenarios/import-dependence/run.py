#!/usr/bin/env python3
"""Import-dependence sweep: coking-coal x NG availability regimes x H2 debut year.

Replaces the Windows-only impdep.bat and its placeholder-substitution
mechanism. AMPL resolves `include` against its cwd, so every run is made
with the repository root as cwd and every path below is root-relative.

    python3 scenarios/import-dependence/run.py                  # full 4x4 sweep
    python3 scenarios/import-dependence/run.py --quick          # 1 run, smoke test
    python3 scenarios/import-dependence/run.py --solver highs   # no gurobi licence
"""

import argparse
import pathlib
import sys

from amplpy import AMPL

ROOT = pathlib.Path(__file__).resolve().parents[2]
STUDY = "scenarios/import-dependence"
RESULTS = ROOT / STUDY / "results"

# (label, coking-coal axis file, NG axis file)
REGIMES = [
    ("HiCoal-HiNG", "ccoal_abundant", "ng_policy"),
    ("HiCoal-LoNG", "ccoal_abundant", "ng_bau"),
    ("LoCoal-HiNG", "ccoal_scarce", "ng_policy"),
    ("LoCoal-LoNG", "ccoal_scarce", "ng_bau"),
]
H2_YEARS = [2030, 2035, 2040, 2045]

# Column order is the contract report.mod's printf writes; keep them in step.
CSV_HEADER = (
    "regime,h2_start,solve_result,ccoal_bill,ng_import_bill,import_bill,"
    "ng_import_qty,cum_co2,lcop,share_bof,share_cdri,share_ngdri,share_h2,"
    "share_scrap,red_h2_2050,ccs_2050"
)


def run_one(label, coal, ng, h2_year, args, log_path):
    ampl = AMPL()
    ampl.cd(str(ROOT))
    if not args.verbose:
        ampl.set_option("solver_msg", 0)

    ampl.eval("include core/model.mod;")
    ampl.eval(f"include {STUDY}/study.mod;")
    ampl.eval(f'let REGIME := "{label}";')
    ampl.eval(f"include {STUDY}/axes/{coal}.mod;")
    ampl.eval(f"include {STUDY}/axes/{ng}.mod;")

    # The swept axis. h2_peak_year is a DERIVED param in core/definitions.mod
    # and follows this automatically -- it must not be assigned here.
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
        fh.write(f"{label}  h2_start={h2_year}  solver={args.solver}\n")
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
                   help="one regime x one H2 year, for smoke-testing")
    p.add_argument("--verbose", action="store_true", help="stream solver output")
    args = p.parse_args()

    regimes = REGIMES[:1] if args.quick else REGIMES
    years = H2_YEARS[:1] if args.quick else H2_YEARS

    RESULTS.mkdir(parents=True, exist_ok=True)
    summary = RESULTS / "impdep_summary.csv"
    summary.write_text(CSV_HEADER + "\n")   # report.mod appends to this

    failures = []
    for label, coal, ng in regimes:
        for year in years:
            tag = f"{label}_h2{year}"
            print(f"=== {tag:24s} ", end="", flush=True)
            status, obj = run_one(label, coal, ng, year, args,
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
