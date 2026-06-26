#!/usr/bin/env python
"""Box-plot of transition cost (levelised $/t steel) per structural cell.
One box = one cell's distribution over the 2400 price draws. Cells grouped by
scrap regime, coloured by grid-EF. Reads cells/*.csv -> runs/<RUN>/plots/."""
import os, csv, glob
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from _runpaths import PLOTS
os.chdir(os.path.dirname(os.path.abspath(__file__)))
ET = os.environ.get("MC_AVG_EMI", "1.8")
METRIC = os.environ.get("COST_METRIC", "levelized_avg_cost")
SCRAP=["starved","low","modest","optimistic"]; H2=["2030","2035","2040","2045"]
GRID=["bau","moderate_re","aggressive_re"]; GCOL={"bau":"#d62728","moderate_re":"#ff7f0e","aggressive_re":"#2ca02c"}
GORD={g:i for i,g in enumerate(GRID)}
cells={}
for f in glob.glob("cells/*.csv"):
    scrap,h2,grid=os.path.basename(f)[:-4].split("_",2)
    rows=[float(r[METRIC]) for r in csv.DictReader(open(f)) if r["status"]=="solved"]
    if rows: cells[(scrap,h2,grid)]=rows
order=sorted(cells, key=lambda k:(SCRAP.index(k[0]),H2.index(k[1]),GORD[k[2]]))
data=[cells[k] for k in order]; cols=[GCOL[k[2]] for k in order]
fig,ax=plt.subplots(figsize=(max(12,0.32*len(order)),5.5))
bp=ax.boxplot(data,patch_artist=True,showfliers=False,widths=0.6,medianprops=dict(color="black"))
for patch,c in zip(bp["boxes"],cols): patch.set_facecolor(c); patch.set_alpha(0.75)
# scrap-group separators + labels
x=1
import itertools
for scrap,grp in itertools.groupby(order,key=lambda k:k[0]):
    grp=list(grp); x0=x; x+=len(grp)
    ax.axvspan(x0-0.5,x-0.5,color="0.95" if SCRAP.index(scrap)%2 else "1.0",zorder=0)
    ax.text((x0+x-1)/2,0.97,scrap,transform=ax.get_xaxis_transform(),ha="center",va="top",fontsize=10,fontweight="bold")
ax.set_xticks(range(1,len(order)+1))
ax.set_xticklabels([f"{k[1]}/{k[2][:3]}" for k in order],rotation=90,fontsize=7)
ax.set_ylabel(f"Transition cost — {METRIC} ($/t steel)"); ax.set_xlim(0.5,len(order)+0.5)
ax.legend(handles=[Patch(facecolor=GCOL[g],label=g,alpha=0.75) for g in GRID],title="grid-EF",loc="upper right",fontsize=8)
ax.set_title(f"Transition cost across {len(order)} feasible cells (ET {ET}, 2400 draws each); grouped by scrap, x=H2yr/grid")
ax.grid(axis="y",alpha=0.25)
fig.tight_layout()
out=os.path.join(PLOTS,"fig_transition_cost_box.png"); fig.savefig(out,dpi=160); print("saved",out,"| cells:",len(order))
