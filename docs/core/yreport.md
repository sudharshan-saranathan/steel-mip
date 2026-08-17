# `yreport.mod` — post-solve reporting

> **Source:** `core/yreport.mod` — 331 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

Prints the human-readable summary of a solved model: cost and emission
headlines, the LCOH build-up, route shares, scrap allocation, CCS deployment,
and per-route $/tCS and tCO2/tCS decompositions.

**Nothing here is part of the optimisation.** It is `printf` and two `let`
statements, executed after `solve`. It is *not* included by `core/model.mod`
— a scenario includes it explicitly if it wants the console tables. The
machine-readable CSV rows that the studies actually consume are written by
each scenario's own `report.mod`, not by this file.

It is nonetheless the most-read file in the repository, because it is where
the per-route numbers people quote come from — and it contains the model's
one confirmed reporting error (see Caveats 1).

## Declares

| Symbol | Kind | Note |
|---|---|---|
| `f_cdri{t}` | `param`, mutable, default 0 | coal-DRI share **of the DRI-EAF pool** |
| `f_ngdri{t}` | `param`, mutable, default 0 | NG-DRI share of the DRI-EAF pool |

```ampl
let {t in T} f_cdri[t]  := if dri_eaf_steel_out[t] > 1e-6 then coaldri_output[t]/dri_eaf_steel_out[t] else 0;
let {t in T} f_ngdri[t] := if dri_eaf_steel_out[t] > 1e-6 then ngdri_output[t]/dri_eaf_steel_out[t] else 0;
```

These are computed *after* solve, from solved variable values — that is why
they can be a nonlinear ratio without making the model nonlinear. The H2
share is always the residual `1 − f_cdri − f_ngdri`.

**Shares of demand** are therefore `f_cdri × f_eaf`, `f_ngdri × f_eaf`, and
`(1 − f_cdri − f_ngdri) × f_eaf`. Getting this two-level nesting wrong is the
commonest misreading of the output.

## Output blocks, in order

| Lines | Block | Content |
|---|---|---|
| 6-24 | Headlines | discounted average cost $/tCS; 2050 cost and intensity; CO2 captured per tonne |
| 26-44 | **LCOH breakdown** | for 2025/2035/2050: electrolyser, RE, firming, other, total $/kg, plus electricity and electrolyser shares |
| 46-58 | **Power scenario** | for six years: grid tariff, grid EF, LCOH $/kg, CCS all-in $/tCO2 — the derived cost paths implied by the three θ dials |
| 60-75 | 2050 route fractions | the five routes' shares of demand |
| 78-91 | **Scrap allocation** | per year: blend share by route, scrap-EAF tonnes, total scrap use, and the limit |
| 93-114 | Production table | per year: tonnes and fraction for each of the five routes |
| 117-164 | CCS table | per year: captured tonnes and share by route; horizon capture fractions |
| 168-189 | Intensity/cost by year | tCO2/tCS and $/tCS; non-levelised average |
| 194-269 | **Per-route cost** ($/tCS) | the decomposition described below |
| 274-326 | **Per-route emissions** (tCO2/tCS) | Scope 1 + allocated Scope 2 − capture |

### The LCOH build-up (lines 26-44)

Reconstructs hydrogen's levelised cost from `definitions.mod`'s parameters —
not from any solved variable — so it is a *parameter diagnostic*, not a
result:

```
LCOH = ocapex_h2elec[t]·crf_h2elec + fopex_h2elec        (electrolyser)
     + h2_kw_per_t·(ocapex_h2re[t]·crf_re + fopex_h2re)  (dedicated RE)
     + h2_opex[t]                                        (water, stack O&M)
```

with the firming component shown separately as
`h2_firm_capex[t]·crf_h2elec`. Useful for checking that a θ_tech setting
lands H2 in the intended $/kg band, since 2050 H2 cost is never specified
directly (see `definitions.md` §5, §10).

### The per-route cost decomposition (lines 194-269)

Each route's $/tCS is assembled as:

```
  acapex_<route> × (cap_<route>[t] − legacy_<route>[t])    capital on BUILT capacity
+ fopex_<route>  × cap_<route>[t]                          fixed O&M on ALL capacity
+ <that route's process cost variables>
+ other_opex × <route output>
+ carbon_tax × scope1_<route>                              (zero by default)
+ CCS capital and variable terms (BF, coal-DRI, NG-DRI only)
− <WHR credit>
────────────────────────────────────────────────
÷ <route output>
```

Three things about this block:

1. **It is not a decomposition of `total_cost`.** The objective books
   `ocapex_* × build_*` (overnight, in the build year); this books
   `acapex_* × (cap − legacy)` (annualised, on standing built capacity). The
   source comment asserts *"the CRF=annuity identity makes the two reconcile
   in present value"* — that is asserted, not verified, and it holds only
   under assumptions about the build profile and horizon end effects. Route
   costs will **not** sum to `total_cost[t]` in any given year.
2. **The incumbent fleet is deliberately not billed capital** — hence
   `(cap − legacy)`. So 2025-vintage assets appear free of capital charge in
   the route costs, which is consistent with the objective (they were never
   `build`) but makes early-year route costs look artificially low.
3. **The shared DRI-EAF's cost is allocated proportionally** — `f_cdri ×
   cost_eaf[t]` etc. There is no modelled per-route EAF cost; see
   `l_eaf_dri.md` caveat 1.

The H2 route additionally allocates the green-H2 supply capital
(electrolyser + RE, annualised + fixed O&M) by `h2dri_h2_in/(h2dri_h2_in +
bf_h2_in)`. Since `bf_h2_in ≡ 0` (see `d_blast_furnace.md`), that ratio is
always 1 — the whole supply capital lands on H2-DRI, which is correct but
makes the guard vestigial.

### The per-route emissions decomposition (lines 274-326)

`scope1_<route> + n9_grid_ef[t] × <allocated power> − ccs_<route>`, over
route output. Power allocation:

| Route | Power charged |
|---|---|
| BF-BOF | coke + sinter + BF power, **less** CDQ + sinter-cooler + TRT recovery, floored at 0 — but **not** BOF power |
| coal-DRI | `coaldri_power_in + f_cdri × eaf_power_in + pellets_power_coaldri` |
| NG-DRI | `ngdri_power_in + f_ngdri × eaf_power_in + pellets_power_ngdri` |
| H2-DRI | `(1−f_cdri−f_ngdri) × eaf_power_in + pellets_power_h2dri + h2dri_power_in` |
| scrap-EAF | `scrap_eaf_power_in` |

`power_ccs` is charged to no route, and `whr_power_generated` is netted off
no route. See Caveats.

The H2 row also re-derives its Scope 1 inline
(`eaf_coal × share × 0.110×24 + eaf_lime × share × 0.44 + eaf_electrode ×
share × 6`) instead of using `scope1_h2dri[t]` — and in doing so it **adds**
the electrode term that eq108 omits. So the H2 row and `scope1_h2dri` disagree
by design.

## Depends on

Every solved variable and most parameters. Requires a **solved** model —
running it before `solve` prints zeros or fails on uninitialised values.

Not included by `core/model.mod`; a scenario must include it explicitly and
must do so after solving.

## Caveats

1. **The WHR credit uses 0.9 where the physical model uses 0.3 — a 3×
   overstatement.** Lines 218, 230, 242, 256 and 266 all compute the route
   WHR benefit as

   ```
   wasteheat_X[t] * 0.9 * 277.78 * n9_eta * n9_whr[t] * (ng_cost_power[t] − capex − opex)
   ```

   but `o_waste_heat.mod`'s chain caps power generation at
   `wasteheat_X × 0.3 × n9_whr[t] × 277.78 × n9_eta`. **Verified against the
   source; the 0.9 does not reconcile with any factor in the physical chain.**
   Consequences: reporting-only (the objective uses `whr_power_generated`,
   which obeys the physical constraints), so *optimal solutions and objective
   values are unaffected* — but every published per-route $/tCS figure
   over-credits waste heat by 3×.

2. **The same credit assumes the entire pool goes to power**, ignoring
   `whr_gas_to_steam`. So even with the factor corrected to 0.3, the route
   credits would over-state the benefit whenever CCS is drawing regeneration
   steam from the pool — i.e. in exactly the scenarios where CCS matters.

3. **Route costs do not sum to `total_cost`.** Different capital convention
   (annualised-on-standing vs overnight-on-build) plus the excluded incumbent
   capital. The reconciliation the source comment claims is asserted, not
   demonstrated. Do not present route costs as a breakdown of the objective.

4. **BOF power is missing from the BF-BOF emissions row** (line 290-292
   charges coke + sinter + BF power only). At `n3_e_bof = 174` kWh/tCS that
   is the single largest power term in the chain, and omitting it understates
   BF-BOF's Scope 2 by roughly 40%.

5. **`power_ccs` is charged to no route in the emissions rows**, even though
   `ccs_<route>` is subtracted from each. So capture's own Scope-2 penalty
   (130-150 kWh/tCO2) appears in `total_emissions` but in no route's
   intensity — routes that capture look better than they are.

6. **`whr_power_generated` is netted off no route's emissions**, though it
   *is* credited in every route's cost. The cost and emissions decompositions
   use inconsistent WHR treatments.

7. **The CCS table divides by route output without guarding it.** Lines 132,
   136, 140 compute e.g. `ccs_bf[t]/steel_bof[t]` guarded only by
   `if total_ccs[t] > 0` — if a route's output is zero while another route is
   capturing, this divides by zero.

8. **The scrap-EAF share on line 67-71 is written in a long residual form**
   that algebraically reduces to `1 − f_bof[2050] − f_eaf[2050]`. Correct,
   but the expansion obscures it and invites transcription errors.

9. **`f_cdri`/`f_ngdri` are mutable params set by `let` after solve.** If
   `yreport.mod` is included twice, or included before a re-solve, it reports
   stale shares. Each scenario driver must include it exactly once per solve.

10. **"TOTAL H2 USED IN H2-DRI" (line 73) reports steel, not hydrogen.** It
    prints `Σ steel_eaf[t] × (1 − f_cdri − f_ngdri) / 1e6`, which is H2-DRI
    *crude steel* in Mt — the header and the units label ("million units")
    are both wrong. The actual H2 consumption is `Σ h2dri_h2_in[t]`.
