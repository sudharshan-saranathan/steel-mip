#!/usr/bin/env python
"""Fast new-capacity investment sweep per feasible cell -> box-plot.
Reuses one AMPL instance per cell, loops a coarse price grid via `let` (investment
is a smooth, low-variance function of prices). Reads mc_frontier.csv for feasible
cells; writes runs/<RUN>/csv/investment_sweep.csv + runs/<RUN>/plots/fig_investment_box.png."""
import os, csv, itertools
from amplpy import AMPL, add_to_path
import ampl_module_base
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from _runpaths import PLOTS, CSV
add_to_path(os.path.join(os.path.dirname(ampl_module_base.__file__), "bin"))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
ET="1.8"; RAMP="0.20"
NGS=[5,15,25]; H2S=[0.5,1.0,1.5]; CCSS=[25,75,125]   # H2S = green-H2 capex multiplier (was $/t price)
SCRAP=["starved","low","modest","optimistic"]; H2Y=["2030","2035","2040","2045"]
GRID=["bau","moderate_re","aggressive_re"]; GCOL={"bau":"#d62728","moderate_re":"#ff7f0e","aggressive_re":"#2ca02c"}
base=open("template.mod").read()
base="\n".join(l for l in base.splitlines() if "include yreport.mod" not in l and "include report.mod" not in l
               and l.strip()!="solve;" and "gurobi_options" not in l)
feas=[(r["scrap_regime"],r["h2_start_year"],r["grid_ef_scenario"])
      for r in csv.DictReader(open("mc_frontier.csv")) if r["status"]=="solved"]
def model(scrap,h2y,grid):
    s=base
    for tok,val in (("NGVAL",15),("H2CAPXVAL",1.0),("H2YEARVAL",h2y),("CCSVAL",75),
                    ("AVGEMIVAL",ET),("RAMPVAL",RAMP),("SCRAPREGIMEFILE",f"scenarios/scrap_{scrap}.mod"),
                    ("NGAVAILFILE","scenarios/ng_avail_normal.mod"),("GRIDEFFILE",f"scenarios/grid_ef_{grid}.mod"),
                    ("CCOALFILE","scenarios/ccoal_normal.mod")):
        s=s.replace(tok,str(val))
    return s
res={}
for (scrap,h2y,grid) in feas:
    a=AMPL(); a.eval(model(scrap,h2y,grid))
    a.eval("option solver gurobi; option gurobi_options 'Threads=6 mipgap=0.0001 outlev=0';")
    vals=[]
    for ng,h2,ccs in itertools.product(NGS,H2S,CCSS):
        a.eval(f"let {{t in T}} n5_cost_NG[t]:={ng}; let h2_capex_mult:={h2}; let n10_ccs_cost_end:={ccs};")
        a.solve()
        if a.get_value("solve_result")!="solved": continue
        g=lambda e:a.get_value(e)
        inv=g("sum{t in T} discount_factor[t]*capex_cost[t]")+g("sum{t in T} discount_factor[t]*ocapex_ccs[t]*(ccs_mult_bf*build_ccs_bf[t]+ccs_mult_cdri*build_ccs_cdri[t]+ccs_mult_ngdri*build_ccs_ngdri[t])")
        vals.append(inv/1e9)  # absolute NPV, $ billion
    res[(scrap,h2y,grid)]=vals
    a.close()
# save
with open(os.path.join(CSV,"investment_sweep.csv"),"w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["scrap","h2_year","grid","invest_npv_bn_median","n"])
    for k,v in res.items(): w.writerow([*k, round(float(np.median(v)),2), len(v)])
# plot
order=sorted(res, key=lambda k:(SCRAP.index(k[0]),H2Y.index(k[1]),GRID.index(k[2])))
data=[res[k] for k in order]; cols=[GCOL[k[2]] for k in order]
fig,ax=plt.subplots(figsize=(max(12,0.32*len(order)),5.5))
bp=ax.boxplot(data,patch_artist=True,showfliers=False,widths=0.6,medianprops=dict(color="black"))
for p,c in zip(bp["boxes"],cols): p.set_facecolor(c); p.set_alpha(0.75)
x=1
for scrap,grp in itertools.groupby(order,key=lambda k:k[0]):
    grp=list(grp); x0=x; x+=len(grp)
    ax.axvspan(x0-0.5,x-0.5,color="0.95" if SCRAP.index(scrap)%2 else "1.0",zorder=0)
    ax.text((x0+x-1)/2,0.97,scrap,transform=ax.get_xaxis_transform(),ha="center",va="top",fontsize=10,fontweight="bold")
ax.set_xticks(range(1,len(order)+1)); ax.set_xticklabels([f"{k[1]}/{k[2][:3]}" for k in order],rotation=90,fontsize=7)
ax.set_ylabel("New-capacity investment (NPV, $ billion)"); ax.set_xlim(0.5,len(order)+0.5)
ax.legend(handles=[Patch(facecolor=GCOL[g],label=g,alpha=0.75) for g in GRID],title="grid-EF",loc="upper right",fontsize=8)
ax.set_title(f"Capital investment across {len(order)} feasible cells (ET {ET}, 27 price pts/cell); grouped by scrap, x=H2yr/grid")
ax.grid(axis="y",alpha=0.25); fig.tight_layout()
out=os.path.join(PLOTS,"fig_investment_box.png"); fig.savefig(out,dpi=160); print("saved",out,"cells",len(order))
