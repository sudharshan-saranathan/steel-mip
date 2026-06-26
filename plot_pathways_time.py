#!/usr/bin/env python
"""
Production-pathway mix as a function of time (2025-2050) for one configuration.

The cells/ generator stores only 2050 snapshots, so this solves one model
instance and pulls the route outputs for every year, then plots the normalised
production mix as a stacked area -- the decarbonisation trajectory.

Config via env (defaults give a representative central case):
  MC_SCENARIO   {normal, shock, optimistic}   (default normal)
  MC_SCRAP_REGIME {starved, low, modest, optimistic} (default modest)
  MC_H2YEAR     H2-DRI start year             (default 2030)
  NGVAL H2ENDVAL CCSVAL  market prices        (default 15 / 2500 / 75)

-> results/fig_pathways_<scenario>_<regime>_<h2yr>.png
"""
import os
import numpy as np
from amplpy import AMPL, add_to_path
import ampl_module_base
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

add_to_path(os.environ.get("AMPL_DIR",
            os.path.join(os.path.dirname(ampl_module_base.__file__), "bin")))
PROJECT = os.path.dirname(os.path.abspath(__file__)); os.chdir(PROJECT)
OUT = __import__("_runpaths").PLOTS

SCEN  = os.environ.get("MC_SCENARIO", "normal")
REG   = os.environ.get("MC_SCRAP_REGIME", "modest")
H2YR  = int(os.environ.get("MC_H2YEAR", "2030"))
NG    = float(os.environ.get("NGVAL", "15"))
H2    = float(os.environ.get("H2ENDVAL", "2500"))
CCS   = float(os.environ.get("CCSVAL", "75"))

YEARS = list(range(2025, 2051))
_PAL = plt.get_cmap("Dark2").colors            # saturated -> readable as lines
ROUTES = [("steel_scrap_eaf", "scrap-EAF", _PAL[0]),
          ("h2dri_output",    "H₂-DRI",    _PAL[1]),
          ("ngdri_output",    "NG-DRI",    _PAL[2]),
          ("coaldri_output",  "coal-DRI",  _PAL[3]),
          ("steel_bof",       "BOF",       _PAL[4])]

with open("template.mod") as fh:
    T = fh.read()
T = "\n".join(l for l in T.splitlines() if "include yreport" not in l and "include report" not in l)
for tok, val in (("NGVAL", NG), ("H2ENDVAL", H2), ("H2YEARVAL", H2YR), ("CCSVAL", CCS),
                 ("SCRAPREGIMEFILE", f"scenarios/scrap_{REG}.mod"),
                 ("NGAVAILFILE", f"scenarios/ng_avail_{SCEN}.mod")):
    T = T.replace(tok, str(val))

ampl = AMPL()
ampl.eval(T)
assert ampl.get_value("solve_result") == "solved", "model did not solve"

total = np.array([ampl.get_value(f"total_steel[{t}]") for t in YEARS])
total[total == 0] = 1.0
fracs = []
for key, _, _ in ROUTES:
    fracs.append(np.array([ampl.get_value(f"{key}[{t}]") for t in YEARS]) / total)
fracs = np.array(fracs)
fracs /= fracs.sum(0, keepdims=True)            # normalise to a composition

fig, ax = plt.subplots(figsize=(9, 5))
for i, (key, lbl, col) in enumerate(ROUTES):
    ax.plot(YEARS, fracs[i], color=col, lw=2.2, marker="o", ms=3.5, label=lbl)
if 2025 < H2YR <= 2050:
    ax.axvline(H2YR, color="0.25", ls="--", lw=1.2)
    ax.text(H2YR + 0.2, 0.02, f"H₂ start {H2YR}", fontsize=8, color="0.25")
ax.set_xlim(2025, 2050); ax.set_ylim(0, 1)
ax.set_xlabel("year"); ax.set_ylabel("share of crude-steel production")
ax.set_title(f"Production pathway over time  —  NG {SCEN}, scrap {REG}, H₂ {H2YR}\n"
             f"(NG {NG:.0f} $/MMBtu, H₂ {H2:.0f} $/t, CCS {CCS:.0f} $/tCO₂)", fontsize=11)
ax.legend(loc="upper center", ncol=5, fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.12))
fig.subplots_adjust(bottom=0.18, top=0.86)
out = os.path.join(OUT, f"fig_pathways_{SCEN}_{REG}_{H2YR}.png")
fig.savefig(out, dpi=160)
print(f"Saved -> {out}")
