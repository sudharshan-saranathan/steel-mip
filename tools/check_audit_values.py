#!/usr/bin/env python3
"""Check that headline audited values still match the model files.
Run from the repo root: python3 tools/check_audit_values.py"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# (file, regex capturing the value, expected)
CHECKS = [
    ("core/definitions.mod", r"param n0_capex default (\d+)", 240),
    ("core/definitions.mod", r"param n1_capex default (\d+)", 180),
    ("core/definitions.mod", r"param ng_capex_pell default (\d+)", 60),
    ("core/definitions.mod", r"param n2_capex default (\d+)", 480),
    ("core/definitions.mod", r"param n3_capex default (\d+)", 240),
    ("core/definitions.mod", r"param n4_capex_coal default (\d+)", 400),
    ("core/definitions.mod", r"param n5_capex_ng := (\d+)", 460),
    ("core/definitions.mod", r"param n7_capex default (\d+)", 400),
    ("core/definitions.mod", r"param n8_capex default (\d+)", 400),
    ("core/definitions.mod", r"param life_bof\s+default (\d+)", 40),
    ("core/definitions.mod", r"param n8_scrap_rate default ([\d.]+)", 0.05),
    ("core/definitions.mod", r"param h2_ref_cap\s+default (\d+)", 2000000),
    ("core/parameters.mod", r"let n8_scrap_rate := ([\d.]+)", 0.05),
    ("structural/axes/ccoal_abundant.mod", r"ccoal_cap\[2050\] := (\d+)", 293592451),
    ("structural/axes/ccoal_scarce.mod", r"ccoal_cap\[2050\] := (\d+)", 102920038),
]

bad = 0
for f, rx, want in CHECKS:
    txt = (ROOT / f).read_text(errors="replace")
    m = re.search(rx, txt)
    got = float(m.group(1)) if m else None
    ok = got is not None and abs(got - want) < 1e-9
    bad += not ok
    print(("ok   " if ok else "DIFF ") + f"{f}: {rx[:34]!r} model={got} audit={want}")

sys.path.insert(0, str(ROOT / "structural/feasibility_and_synergy/feasibility_drivers"))
import axes as AX
n = 1
for v in AX.AXES.values():
    n *= len(v)
ok = n == 27648
bad += not ok
print(("ok   " if ok else "DIFF ") + f"feasibility-drivers cells: model={n} audit=27648")
sys.exit(1 if bad else 0)
