#!/usr/bin/env python
"""Subsection A -- NPV system cost vs emissions target (ET), above the floor.

For each paper axis (h2_start_year, scrap_regime, ng_availability,
ccoal_availability) x mode {0,2}: sweep ET on a fixed grid 1.4 -> 2.4
(step 0.1), skipping points below that cell's known floor
(subsection_a_floors.csv), plus one extra point at floor+0.01 to capture
the terminal steepness. Central values per subsection_a_sweep.CENTRAL.

Writes subsection_a_costs.csv: one row per (axis, axis_value, mode, et).
"""
import csv
from subsection_a_sweep import AXES, MODES, solve_cell

ET_GRID = [round(1.0 + 0.1 * i, 2) for i in range(15)]   # 1.0 .. 2.4
FLOOR_EPS = 0.01

PAPER_AXES = ["h2_start_year", "scrap_regime", "ng_availability", "ccoal_availability"]

floors = {}
for r in csv.DictReader(open("subsection_a_floors.csv")):
    floors[(r["axis"], r["axis_value"], int(r["mode"]))] = float(r["et_floor"])


def main():
    rows = []
    for axis in PAPER_AXES:
        for val in AXES[axis]["values"]:
            for mode in MODES:
                floor = floors[(axis, str(val), mode)]
                ets = sorted({round(floor + FLOOR_EPS, 4)} |
                             {et for et in ET_GRID if et >= floor + FLOOR_EPS})
                print(f"[{axis}={val}, mode={mode}] floor={floor} -> {len(ets)} ET points", flush=True)
                for et in ets:
                    r = solve_cell(axis, val, et, mode)
                    row = {"axis": axis, "axis_value": val, "mode": mode, "et": et,
                           "feasible": int(r["feasible"]),
                           "npv_cost": r.get("npv_cost"),
                           "h2dri_2050": r.get("h2dri_2050"),
                           "ccs_2050": r.get("ccs_2050")}
                    print("  ->", row, flush=True)
                    rows.append(row)

    with open("subsection_a_costs.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["axis", "axis_value", "mode", "et", "feasible",
                                           "npv_cost", "h2dri_2050", "ccs_2050"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {len(rows)} rows -> subsection_a_costs.csv")


if __name__ == "__main__":
    main()
