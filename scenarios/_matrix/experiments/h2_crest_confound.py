"""Is the h2_start axis confounded with the ramp CREST (h2_peak_year = start+5)?

Solve the same coordinate at each h2_start twice:
  coupled  -- h2_peak_lag = 5 (as shipped): crest moves with the debut
  fixed    -- h2_peak_lag = 2035 - start:  crest pinned at 2035 for all starts
If delay is a pure restriction, objective must be non-decreasing in h2_start.
"""
import sys, pathlib
ROOT = pathlib.Path("/opt/developer/iitm-projects/steel-mip")
sys.path.insert(0, str(ROOT / "scenarios" / "_matrix"))
import run_matrix as RM, axes as AX

base = dict(AX.BASELINE)
CELLS = [
    ("baseline", dict(base)),
    ("worst-pair", dict(base, scrap_rate=0.00, grid_ef=0.00005, ramp="high", avg_emi=2.0)),
]

def cellify(d):
    lut = lambda tab, key: next(x for x in tab if x[0] == key)
    return {"ccoal": lut(AX.CCOAL, d["ccoal"]), "ng": lut(AX.NG, d["ng"]),
            "h2_start": d["h2_start"], "scrap_rate": d["scrap_rate"],
            "grid_ef": d["grid_ef"], "ramp": lut(AX.RAMP, d["ramp"]),
            "build_cap": lut(AX.BUILD_CAP, d["build_cap"]),
            "legacy": lut(AX.LEGACY, d["legacy"]), "avg_emi": d["avg_emi"]}

_orig = RM.solve_cell

for name, d in CELLS:
    print(f"\n=== {name}: {d} ===")
    for mode in ("coupled", "fixed"):
        print(f"  {mode}:")
        for hs in AX.H2_START:
            c = cellify(dict(d, h2_start=hs))
            RM.EXTRA_LETS = (f"let h2_peak_lag := {2035 - hs};" if mode == "fixed" else "")
            row = _orig(c)
            print(f"    start {hs}  {row['solve_result']:>10}  obj {row['objective']:.6g}"
                  f"  lcop {row.get('lcop', float('nan'))}")
