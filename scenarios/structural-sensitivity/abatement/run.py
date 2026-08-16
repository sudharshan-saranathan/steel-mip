#!/usr/bin/env python3
"""Abatement-anatomy sweep: one frozen-structure baseline + 6 named policy
scenarios (EF1.6, EF1.8, S4, S8, RL, RH), all appending per-year rows to the
same CSV so a downstream decomposition can diff each scenario against the
common baseline.

Replaces the Windows-only abatement.bat + abatement_baseline.mod /
abatement_scenario.mod token substitution. AMPL resolves `include` against
its cwd, so every run is made with the repository root as cwd and every
path below is root-relative.

    python3 scenarios/structural-sensitivity/abatement/run.py                # baseline + 6 scenarios
    python3 scenarios/structural-sensitivity/abatement/run.py --quick        # baseline + 1 scenario
    python3 scenarios/structural-sensitivity/abatement/run.py --solver highs
"""

import argparse
import pathlib
import sys

from amplpy import AMPL

ROOT = pathlib.Path(__file__).resolve().parents[3]
STUDY = "scenarios/structural-sensitivity/abatement"
RESULTS = ROOT / STUDY / "results"

# (label, axis file)
SCENARIOS = [
    ("EF1.6", "ef1.6"),
    ("EF1.8", "ef1.8"),
    ("S4", "s4"),
    ("S8", "s8"),
    ("RL", "rl"),
    ("RH", "rh"),
]

CSV_HEADER = (
    "run,year,solve_result,total_steel,steel_bof,coaldri,ngdri,h2dri,"
    "scrap_eaf,scope1,scope2,ccs,total_emissions,e_h2,bof_scrap,cdri_scrap,"
    "ngdri_scrap,h2dri_scrap,scrapeaf_scrap,scrap_limit,total_cost,"
    "whr_power,gross_bf,gross_cdri,gross_ngdri,gross_scrapeaf"
)


def run_baseline(args, log_path):
    ampl = AMPL()
    ampl.cd(str(ROOT))
    if not args.verbose:
        ampl.set_option("solver_msg", 0)

    ampl.eval("include core/model.mod;")
    ampl.eval(f"include {STUDY}/baseline.mod;")
    ampl.eval('let REGIME := "Baseline";')

    ampl.eval(f"option solver {args.solver};")
    if args.solver == "gurobi":
        ampl.eval(f"option gurobi_options '{args.gurobi_options}';")
    # share pins are exactly collinear with meet_demand: tolerate the
    # ~1e-16 presolve rounding residual (see original abatement_baseline.mod).
    ampl.eval("option presolve_eps 1e-8;")

    ampl.eval("drop emission_monotonic;")
    ampl.eval("solve;")

    status = ampl.get_value("solve_result")
    obj = ampl.get_objective("obj").value()
    ampl.eval(f"include {STUDY}/report.mod;")

    with open(log_path, "w") as fh:
        fh.write(f"Baseline  solver={args.solver}\n")
        fh.write(f"solve_result={status}\nobjective={obj:.6f}\n")

    ampl.close()
    return status, obj


def run_scenario(label, axis, args, log_path):
    ampl = AMPL()
    ampl.cd(str(ROOT))
    if not args.verbose:
        ampl.set_option("solver_msg", 0)

    ampl.eval("include core/model.mod;")
    ampl.eval(f"include {STUDY}/study.mod;")
    ampl.eval(f'let REGIME := "{label}";')
    ampl.eval(f"include {STUDY}/axes/{axis}.mod;")

    ampl.eval(f"option solver {args.solver};")
    if args.solver == "gurobi":
        ampl.eval(f"option gurobi_options '{args.gurobi_options}';")

    ampl.eval("drop emission_monotonic;")
    ampl.eval("solve;")

    status = ampl.get_value("solve_result")
    obj = ampl.get_objective("obj").value()
    ampl.eval(f"include {STUDY}/report.mod;")

    with open(log_path, "w") as fh:
        fh.write(f"{label}  solver={args.solver}\n")
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
                   help="baseline + one scenario, for smoke-testing")
    p.add_argument("--verbose", action="store_true", help="stream solver output")
    args = p.parse_args()

    scenarios = SCENARIOS[1:2] if args.quick else SCENARIOS  # EF1.8

    RESULTS.mkdir(parents=True, exist_ok=True)
    summary = RESULTS / "abatement_yearly.csv"
    summary.write_text(CSV_HEADER + "\n")

    failures = []

    print("=== Baseline                 ", end="", flush=True)
    status, obj = run_baseline(args, RESULTS / "Baseline.txt")
    print(f"{status:12s} obj={obj:.6f}")
    if status != "solved":
        failures.append(("Baseline", status))

    for label, axis in scenarios:
        print(f"=== {label:28s} ", end="", flush=True)
        status, obj = run_scenario(label, axis, args, RESULTS / f"{label}.txt")
        print(f"{status:12s} obj={obj:.6f}")
        if status != "solved":
            failures.append((label, status))

    print(f"\nSummary: {summary.relative_to(ROOT)}")
    if failures:
        print("NOT SOLVED: " + ", ".join(f"{t} ({s})" for t, s in failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
