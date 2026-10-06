"""Re-run the paper's Fig. 3 grid (H2 delay study) through the HiGHS bridge.

    python3 tools/rerun_fig3.py MODEL_ROOT OUT.csv [extra AMPL statements]

MODEL_ROOT is a checkout of the model (e.g. this branch, or a worktree of the
unchanged import). Uses the study's own template; drops emission_monotonic as
the study driver does.
"""
import csv
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from amplpy import AMPL                      # noqa: E402
from ampl_highs_bridge import solve_bridge   # noqa: E402

root, out = sys.argv[1], sys.argv[2]
extra = " ".join(sys.argv[3:])
rows = []
for ef in (1.6, 1.8, 2.0):
    for label, ramp in (("Low", 2_000_000), ("Mid", 4_000_000), ("High", 6_000_000)):
        for h2 in (2030, 2035, 2040, 2045):
            a = AMPL()
            a.cd(root)
            a.eval("include core/model.mod; include structural/h2_delay/template_h2delay.mod;")
            a.eval(f"let avg_emi := {ef}; let h2_ref_cap := {ramp}; let ng_h2_start_year := {h2};")
            if extra:
                a.eval(extra)
            a.eval("drop emission_monotonic;")
            st, _ = solve_bridge(a)
            r = {"EF": ef, "H2 supply": label, "H2 start": h2, "status": st}
            if st == "solved":
                a.eval("include structural/report.mod;")
                r.update(LCOP=round(a.get_value("m_lcop"), 1),
                         H2_share=round(100 * a.get_value("m_sh_h2"), 1),
                         BOF_share=round(100 * a.get_value("m_sh_bof"), 1),
                         scrap_share=round(100 * a.get_value("m_sh_scrap"), 1),
                         ccs_Mt=round(a.get_value("m_cum_captured") / 1e6, 1))
            rows.append(r)
            a.close()
            print(r, flush=True)
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["EF", "H2 supply", "H2 start", "status", "LCOP",
                                       "H2_share", "BOF_share", "scrap_share", "ccs_Mt"])
    w.writeheader()
    w.writerows(rows)
