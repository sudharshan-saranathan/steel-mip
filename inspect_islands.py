import pandas as pd
import numpy as np
from scipy.ndimage import median_filter

import os
df = pd.read_csv(os.environ.get("MC_OUT", "mc_2d_tight.csv"))
df = df[df["status"] == "solved"].sort_values(["i_h2", "i_ccs"])

N_H2, N_CCS = df["i_h2"].nunique(), df["i_ccs"].nunique()
grid = df["emis_2050"].values.reshape(N_H2, N_CCS)

med  = median_filter(grid, size=3)
diff = grid - med

threshold = 0.04
outliers  = np.argwhere(np.abs(diff) > threshold)

print(f"Outlier points (|deviation from local median| > {threshold} tCO2/t):\n")
cols = ["i_h2","i_ccs","h2_end_cost","ccs_end_cost","emis_2050","f_h2_2050","f_bof_2050","f_scrap_2050","f_coal_2050","f_ng_2050","solve_s"]
print(f"{'i_h2':>5} {'i_ccs':>5} {'H2$/t':>7} {'CCS$/t':>7} {'emis':>7} {'loc_med':>7} {'dev':>7} {'f_h2':>7} {'f_bof':>7} {'f_scrap':>7} {'f_coal':>7} {'f_ng':>7}")
for ih2, ics in outliers:
    row = df[(df.i_h2 == ih2) & (df.i_ccs == ics)].iloc[0]
    print(f"{ih2:>5} {ics:>5} {row.h2_end_cost:>7.0f} {row.ccs_end_cost:>7.1f} "
          f"{row.emis_2050:>7.4f} {med[ih2,ics]:>7.4f} {diff[ih2,ics]:>7.4f} "
          f"{row.f_h2_2050:>7.4f} {row.f_bof_2050:>7.4f} {row.f_scrap_2050:>7.4f} "
          f"{row.f_coal_2050:>7.4f} {row.f_ng_2050:>7.4f}")
