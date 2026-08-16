#!/usr/bin/env python3
"""WHR-CCS integration sweep: joint CCS+grid maturity theta x steam-sourcing mode.

Replaces the Windows-only whr.bat + whr_template.mod token substitution
(THETAVAL/WHRVAL/MODELABEL). AMPL resolves `include` against its cwd, so
every run is made with the repository root as cwd and every path below is
root-relative.

    python3 scenarios/structural-sensitivity/whr/run.py                # full 5x2 = 10 runs
    python3 scenarios/structural-sensitivity/whr/run.py --quick        # 1 run, smoke test
    python3 scenarios/structural-sensitivity/whr/run.py --solver highs
"""

import argparse
import pathlib
import sys

from amplpy import AMPL

ROOT = pathlib.Path(__file__).resolve().parents[3]
STUDY = "scenarios/structural-sensitivity/whr"
RESULTS = ROOT / STUDY / "results"

THETAS = [0, 0.25, 0.5, 0.75, 1]
MODES = [("integrated", 1), ("boiler-only", 0)]

CSV_HEADER = (
    "theta,mode,whr_integration,solve_result,eff_capture_cost,cum_captured,"
    "ccs_2050,boiler_steam_share,lcop"
)


def run_one(theta, mode_label, whr_val, args, log_path):
    ampl = AMPL()
    ampl.cd(str(ROOT))
    if not args.verbose:
        ampl.set_option("solver_msg", 0)

    ampl.eval("include core/model.mod;")
    ampl.eval(f"include {STUDY}/study.mod;")
    ampl.eval(f'let MODE_LABEL := "{mode_label}";')

    # Joint CCS+grid ecosystem-maturity theta.
    ampl.eval(f"let theta_ccs := {theta};")
    ampl.eval(f"let theta_grid := {theta};")
    # whr_ccs_integration is declared in core/modules/o_waste_heat.mod, part
    # of core/model.mod, so this `let` can come any time after that include.
    ampl.eval(f"let whr_ccs_integration := {whr_val};")

    ampl.eval(f"option solver {args.solver};")
    if args.solver == "gurobi":
        ampl.eval(f"option gurobi_options '{args.gurobi_options}';")

    ampl.eval("drop emission_monotonic;")
    ampl.eval("solve;")

    status = ampl.get_value("solve_result")
    obj = ampl.get_objective("obj").value()

    ampl.eval(f"include {STUDY}/report.mod;")

    with open(log_path, "w") as fh:
        fh.write(f"theta={theta}  mode={mode_label}  solver={args.solver}\n")
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
                   help="one theta x one mode, for smoke-testing")
    p.add_argument("--verbose", action="store_true", help="stream solver output")
    args = p.parse_args()

    thetas = THETAS[2:3] if args.quick else THETAS   # 0.5
    modes = MODES[:1] if args.quick else MODES        # integrated

    RESULTS.mkdir(parents=True, exist_ok=True)
    summary = RESULTS / "whr_summary.csv"
    summary.write_text(CSV_HEADER + "\n")

    failures = []
    for theta in thetas:
        for mode_label, whr_val in modes:
            tag = f"theta{theta}_{mode_label}"
            print(f"=== {tag:28s} ", end="", flush=True)
            status, obj = run_one(theta, mode_label, whr_val, args,
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
