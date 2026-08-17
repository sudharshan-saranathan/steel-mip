# `o_waste_heat.mod` — waste-heat recovery pool

> **Source:** `core/modules/o_waste_heat.mod` — 46 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

Collects the site's surplus process gases into a single energy pool, applies
two exogenous derating factors, and then lets the optimiser **allocate** the
accessible pool between two competing uses:

- **power generation** (offsets grid purchase, cuts Scope 2), and
- **CCS solvent-regeneration steam** (enables carbon capture without burning
  natural gas in the backup boiler).

That allocation is the module's one genuine decision, and it is the tightest
physical coupling in the model between decarbonisation levers: **every GJ
sent to CCS regeneration is a GJ not generating power**.

## Declares

| Symbol | Kind | Default | Note |
|---|---|---|---|
| `whr_ccs_integration` | `param`, mutable | **1** | declared **mid-file at line 36** |

Eight equality/inequality constraints (eq78-eq82b).

## Equations

### 1. Gathering the streams (eq78-eq80)

```ampl
# BF-BOF surplus = gas produced − gas burned internally
  cog_out + bfg_out + bofgas_out
− cokeov_cog_in − bf_cog_in − bof_cog_in − bfg_in − cokeov_bfg_in
= wasteheat_bf_bof;                                      # eq78

eafgas_out        = wasteheat_eaf;                        # eq79
scrap_eaf_gas_out = scrap_eaf_wasteheat;                  # eq80
```

eq78 is a true surplus balance — three production streams less five internal
consumption streams. eq79 and eq80 are pass-throughs (all EAF off-gas is
surplus, at 3 GJ/tCS each).

Per-tonne magnitudes at 2025 coefficients: the BF-BOF chain nets roughly
**3.5 GJ/tCS** of surplus gas; each EAF route contributes exactly 3 GJ/tCS.

Note **`sg_out` (sinter gas) is absent** — deliberately, per the
`definitions.mod` comment that its calorific value is too low to be worth
recovering. CDQ, TRT and sinter-cooler heat are also absent, because those are
already recovered as *power* in their own modules (the header comment says
so).

### 2. Two exogenous deratings (eq81, eq81b)

```ampl
(wasteheat_bf_bof + wasteheat_eaf + scrap_eaf_wasteheat) * 0.3
    − whr_available_gas = 0;                                          # eq81

whr_gas_to_power + whr_gas_to_steam <= whr_available_gas * n9_whr[t];  # eq81b
```

Two multiplicative factors, applied in sequence:

| Factor | Value | Meaning |
|---|---|---|
| **0.3** (hardcoded in eq81) | 30% | fraction of surplus gas that is *technically* recoverable (losses, unrecoverable low-grade streams) |
| **`n9_whr[t]`** | 0.05 → 0.30 | *penetration*: how much of that recoverable pool is actually equipped, rising linearly to 2050 |

Combined, only **1.5% of surplus gas is accessible in 2025, rising to 9% by
2050**. Then power conversion applies a third factor (`n9_eta = 0.15`), so
the end-to-end efficiency from surplus GJ to kWh is 0.3 × 0.30 × 0.15 = 1.35%
in 2050.

The `0.3` is a bare literal with no declared parameter — it cannot be swept.

### 3. The integration switch (lines 36-38)

```ampl
param whr_ccs_integration default 1;
s.t. whr_integration_switch{t in T}:
    whr_gas_to_steam[t] <= whr_ccs_integration * whr_available_gas[t] * n9_whr[t];
```

| Value | Behaviour |
|---|---|
| **1** (default) | constraint is *implied by* eq81b and therefore **inert** — CCS may draw regen steam from the waste-heat pool (the integrated system) |
| **0** | forces `whr_gas_to_steam = 0` — **boiler-only**: all CCS regeneration steam must come from the gas-fired backup boiler, which costs NG and emits CO2 |

This is the `structural-sensitivity/whr` study's entire sweep axis. Before
the refactor it required a forked copy of this module in three study
directories; it is now a one-line `let whr_ccs_integration := 0;` override.

Verified during the refactor: at 1 the objective is unchanged
(2 008 395 874 830.76); at 0 it rises by **$4.65 B, +0.23%**.

### 4. Conversion (eq82, eq82b)

```ampl
whr_gas_to_power[t] * 277.78 * n9_eta − whr_power_generated[t] = 0;   # eq82
whr_steam_eff * whr_gas_to_steam[t]   − ccs_steam_whr[t]      = 0;    # eq82b
```

- `277.78` = kWh per GJ (1 GJ = 277.78 kWh). Times `n9_eta = 0.15` gives
  **41.67 kWh of power per GJ routed to power**.
- `whr_steam_eff = 0.85` GJ of LP steam per GJ routed to steam.

The trade-off the LP resolves: 1 GJ → 41.67 kWh (worth ~$2.9 at the 2025
tariff, less $0.50 of WHR capex+opex) **versus** 1 GJ → 0.85 GJ of steam,
displacing 0.85/0.85 = 1.0 GJ of boiler NG (worth ~$9.5 at 10 $/MMBtu) plus
0.052 tCO2 of avoided boiler emissions. Steam usually wins when CCS is
running — which is why the boiler-only counterfactual costs real money.

## Depends on

| Symbol | Owner |
|---|---|
| `cog_out`, `cokeov_cog_in`, `cokeov_bfg_in` | `modules/a_coke.mod` |
| `bfg_out`, `bfg_in`, `bf_cog_in` | `modules/d_blast_furnace.mod` |
| `bofgas_out`, `bof_cog_in` | `modules/e_bof.mod` |
| `eafgas_out` | `modules/l_eaf_dri.mod` |
| `scrap_eaf_gas_out` | `modules/m_scrap_eaf.mod` |
| `n9_whr`, `n9_eta`, `whr_steam_eff` | `definitions.mod` |

Feeds `p_power_balance.mod` (`whr_power_generated`), `r_cost.mod`
(`cost_wasteheat`, and the WHR credit in `total_cost_def`),
`q_carbon_capture.mod` (`ccs_steam_whr` in `ccs_steam_balance`).

## Caveats

1. **The 0.3 recovery factor is a hardcoded literal** (line 26), not a
   declared parameter. It is the single largest derating in the chain and it
   cannot be swept, overridden, or found by searching `definitions.mod`.
   Promoting it to `param whr_recoverable default 0.3;` would cost nothing.

2. **`yreport.mod` uses 0.9 where this module uses 0.3 — a 3× discrepancy.**
   The per-route cost credits in `yreport.mod` (lines 218, 230, 242, 256,
   266) compute the WHR benefit as
   `wasteheat_X × 0.9 × 277.78 × n9_eta × n9_whr[t]`, but the physical chain
   here caps it at `× 0.3 ×`. The reported credit is **three times the
   physically achievable maximum**. This is reporting-only — the objective
   uses `whr_power_generated`, which obeys eq81/eq81b — so optimal solutions
   are unaffected, but every published per-route $/t figure carries the
   error. See `yreport.md` caveat 1.

3. **`yreport.mod` also assumes the entire pool goes to power**, ignoring
   `whr_gas_to_steam`. So even at the correct 0.3 factor, the route credits
   would over-state the benefit whenever CCS is drawing steam.

4. **WHR has no capacity asset, lifetime or build ramp.** Cost is charged per
   kWh generated (`r_cost.mod` eq102), so recovery equipment appears
   instantly up to the `n9_whr[t]` ceiling. The penetration curve is the only
   thing limiting deployment, and it is exogenous.

5. **`whr_pool_alloc` is a `<=`, not an equality.** Accessible gas may be
   left unused, which is correct (it has no other value) but means
   `whr_available_gas` is not a binding physical balance — the surplus simply
   vanishes.

6. **`whr_integration_switch` is inert at its default** and therefore adds 26
   redundant constraints to every baseline solve. Harmless; noted because it
   can confuse constraint-count comparisons against the pre-refactor forks.

7. **Sinter gas (1.08 GJ/t-sinter) is discarded entirely** — see
   `b_sinter.md` caveat 3. At 1.15 t sinter/thm that is a non-trivial stream
   being written off on calorific grounds without a documented calculation.

## Constraint index

| Constraint | eq | Covered under |
|---|---|---|
| `bf_bof_waste_heat_balance` | 78 | Gathering the streams — surplus BF-BOF gas |
| `eaf_waste_heat_balance` | 79 | Gathering the streams — DRI-EAF off-gas pass-through |
| `scrap_eaf_wasteheat_balance` | 80 | Gathering the streams — scrap-EAF off-gas pass-through |
| `available_waste_stream` | 81 | Two exogenous deratings — the hardcoded 0.3 factor |
| `whr_pool_alloc` | 81b | Two exogenous deratings — the `n9_whr[t]` penetration ceiling |
| `whr_integration_switch` | — | The integration switch — the WHR study's sweep axis |
| `whr_power_balance` | 82 | Conversion — 277.78 kWh/GJ × `n9_eta` |
| `ccs_steam_whr_def` | 82b | Conversion — `whr_steam_eff` = 0.85 GJ steam/GJ |
