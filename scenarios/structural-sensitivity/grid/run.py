#!/usr/bin/env python3
"""Grid-offset-requirement sweep: H2 start year x scrap growth x target 2050 grid EF.

Replaces the Windows-only grid.bat + grid_template.mod token substitution
(H2ENDVAL/SCRAPVAL/GRIDVAL). AMPL resolves `include` against its cwd, so
every run is made with the repository root as cwd and every path below is
root-relative.

theta_grid is back-solved from the swept target grid EF (see study.mod) --
n8_scrap_limit and h2_peak_year are DERIVED params in core/definitions.mod
and must NOT be assigned directly (AMPL rejects `let` on a defined param).

    python3 scenarios/structural-sensitivity/grid/run.py                # full 6x8x18 = 864 runs
    python3 scenarios/structural-sensitivity/grid/run.py --quick        # 1 run, smoke test
    python3 scenarios/structural-sensitivity/grid/run.py --solver highs
"""

import argparse
import pathlib
import sys

from amplpy import AMPL

ROOT = pathlib.Path(__file__).resolve().parents[3]
STUDY = "scenarios/structural-sensitivity/grid"
RESULTS = ROOT / STUDY / "results"

H2_YEARS = [2030, 2033, 2036, 2039, 2042, 2045]
SCRAP_RATES = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
GRID_EF_TARGETS = [round(0.00005 * i, 5) for i in range(18)]  # 0.0000 .. 0.00085

CSV_HEADER = (
    "h2_start,scrap_rate,grid_ef_end,theta_grid,tariff_2050,solve_result,"
    "avg_emis,pv_avg_cost,h2_share_2050,ccs_frac_2050,scrapeaf_share_2050"
)


def run_one(h2_year, scrap_rate, grid_target, args, log_path):
    ampl = AMPL()
    ampl.cd(str(ROOT))
    if not args.verbose:
        ampl.set_option("solver_msg", 0)

    ampl.eval("include core/model.mod;")
    ampl.eval(f"include {STUDY}/study.mod;")

    ampl.eval(f"let ng_h2_start_year := {h2_year};")
    ampl.eval(f"let n8_scrap_rate := {scrap_rate};")
    ampl.eval(f"let grid_ef_target := {grid_target};")
    ampl.eval(
        f"let theta_grid := ({grid_target} - grid_ef_end_slow) "
        f"/ (grid_ef_end_fast - grid_ef_end_slow);"
    )

    ampl.eval(f"option solver {args.solver};")
    if args.solver == "gurobi":
        ampl.eval(f"option gurobi_options '{args.gurobi_options}';")

    ampl.eval("drop emission_monotonic;")
    ampl.eval("solve;")

    status = ampl.get_value("solve_result")
    obj = ampl.get_objective("obj").value()

    ampl.eval(f"include {STUDY}/report.mod;")

    with open(log_path, "w") as fh:
        fh.write(f"h2={h2_year}  scrap={scrap_rate}  grid_ef={grid_target}  "
                  f"solver={args.solver}\n")
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
                   help="one H2 year x one scrap rate x one grid target, for smoke-testing")
    p.add_argument("--verbose", action="store_true", help="stream solver output")
    args = p.parse_args()

    years = H2_YEARS[:1] if args.quick else H2_YEARS
    rates = SCRAP_RATES[3:4] if args.quick else SCRAP_RATES     # 0.04, central-ish
    targets = GRID_EF_TARGETS[6:7] if args.quick else GRID_EF_TARGETS  # 0.0003, ~mid

    RESULTS.mkdir(parents=True, exist_ok=True)
    summary = RESULTS / "grid_summary.csv"
    summary.write_text(CSV_HEADER + "\n")

    failures = []
    n_total = len(years) * len(rates) * len(targets)
    n_done = 0
    for h2_year in years:
        for scrap_rate in rates:
            for grid_target in targets:
                n_done += 1
                tag = f"h2{h2_year}_scrap{scrap_rate}_grid{grid_target}"
                print(f"=== [{n_done}/{n_total}] {tag:34s} ", end="", flush=True)
                status, obj = run_one(h2_year, scrap_rate, grid_target, args,
                                      RESULTS / f"{tag}.txt")
                print(f"{status:12s} obj={obj:.6f}")
                if status != "solved":
                    failures.append((tag, status))

    print(f"\nSummary: {summary.relative_to(ROOT)}")
    if failures:
        print(f"NOT SOLVED ({len(failures)}): " + ", ".join(f"{t} ({s})" for t, s in failures[:20]))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
