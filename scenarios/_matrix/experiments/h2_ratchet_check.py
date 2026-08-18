"""Does the ratcheted ramp restore monotonicity in the H2 debut year?

ratchet=0 must reproduce the pre-change numbers EXACTLY (regression guard);
ratchet=1 must give LCOP non-decreasing in ng_h2_start_year, since a later
debut then only ever removes options.
"""
import sys, pathlib
ROOT = pathlib.Path("/opt/developer/iitm-projects/steel-mip")
sys.path.insert(0, str(ROOT / "scenarios" / "_matrix"))
import run_matrix as RM, axes as AX

CELLS = [("baseline", dict(AX.BASELINE)),
         ("worst-pair", dict(AX.BASELINE, scrap_rate=0.00, grid_ef=0.00005,
                             ramp="high", avg_emi=2.0))]

def cellify(d):
    lut = lambda tab, key: next(x for x in tab if x[0] == key)
    return {"ccoal": lut(AX.CCOAL, d["ccoal"]), "ng": lut(AX.NG, d["ng"]),
            "h2_start": d["h2_start"], "scrap_rate": d["scrap_rate"],
            "grid_ef": d["grid_ef"], "ramp": lut(AX.RAMP, d["ramp"]),
            "build_cap": lut(AX.BUILD_CAP, d["build_cap"]),
            "legacy": lut(AX.LEGACY, d["legacy"]), "avg_emi": d["avg_emi"]}

for name, d in CELLS:
    print(f"\n=== {name} ===")
    for ratchet in (0, 1):
        RM.EXTRA_LETS = f"let h2_ramp_ratchet := {ratchet};"
        prev, mono = None, True
        out = []
        for hs in AX.H2_START:
            row = RM.solve_cell(cellify(dict(d, h2_start=hs)))
            lcop = row["lcop"]
            if prev is not None and lcop < prev - 1e-6:
                mono = False
            prev = lcop
            out.append(f"{hs}:{lcop:8.2f}")
        print(f"  ratchet={ratchet}  " + "  ".join(out) +
              f"   monotone={mono}")
