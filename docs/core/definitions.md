# `definitions.mod` — parameter declarations

> **Source:** `core/definitions.mod` — 368 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

Declares **every parameter** in the model. Nothing here is a variable and
nothing here is a constraint — it is pure symbol declaration plus the
*derived* (defined) parameters that AMPL recomputes automatically.

Two kinds of declaration appear, and the distinction is the single most
important thing in this file:

| Form | Meaning | Overridable by a scenario? |
|---|---|---|
| `param x default 5;` | **mutable**; 5 is the initial value | Yes — `let x := ...` |
| `param x := <expr>;` | **defined**; recomputed from `<expr>` on every read | **No** — `let x` is a hard AMPL error |

A defined param is the right choice whenever the value is a *function* of
other params: it stays consistent when a scenario overrides its inputs. A
mutable param is the right choice for a genuine free input. Getting this
backwards is how the pre-refactor model produced silently wrong sweeps (see
Caveats).

It is included **first** by `model.mod`, before `variables.mod`, because the
variable bounds reference `dem[t]`.

## Declares

### 1. Demand and discounting

| Symbol | Kind | Default | Meaning |
|---|---|---|---|
| `base_demand` | mutable | 152 200 000 | crude steel produced in 2025, t/yr |
| `growth_rate` | mutable | 0.05 | annual demand growth, compounding |
| `dem{t}` | **defined** | — | `base_demand·(1+growth_rate)^(ord(t)−1)` |
| `real_discount_rate` | **defined** | 0.06 | real WACC; drives every CRF and `discount_factor` |

`dem[t]` is the demand trajectory. It is exogenous — the model never chooses
how much steel to make, only *how*. India's 152.2 Mt in 2025 growing at 5%/yr
reaches **515 Mt by 2050**.

> `real_discount_rate` is declared with `:=`, so it is a **defined param and
> cannot be `let`**. A scenario wanting a different discount rate must edit
> this file. See Caveats.

### 2. Technical coefficients (`ng_*`, `n0_`…`n10_`)

The naming convention is positional, following the process chain:

| Prefix | Unit operation |
|---|---|
| `ng_` | global / shared (pellets, gas calorific values, prices) |
| `n0_` | coke oven |
| `n1_` | sinter plant |
| `n2_` | blast furnace |
| `n3_` | BOF |
| `n4_` | coal-DRI |
| `n5_` | NG-DRI |
| `n6_` | H2-DRI |
| `n7_` | DRI-EAF |
| `n8_` | scrap-EAF |
| `n9_` | waste-heat recovery + grid emission factor |
| `n10_` | carbon capture |

Within a prefix the suffix reads `<input>_<output>`: `n2_coke_hm` is *tonnes
of coke per tonne of hot metal*; `n0_cf` is *tonnes of coal per tonne of
coke*. Coefficients carrying a `_25` / `_50` pair (`n2_coke_hm_25`,
`n2_coke_hm_50`, `n1_brz_sint_25/_50`, `n2_coalpci_hm_25/_50`,
`n2_biopci_hm_25/_50`, `n2_h2_hm_25/_50`) are **linearly interpolated inside
their consuming constraint**, not here — the interpolation
`(a25 + (a50−a25)·(t−2025)/25)` is written out in `b_sinter.mod` and
`d_blast_furnace.mod`. This encodes exogenous, non-optimised efficiency
drift: the blast furnace gets better at coke rate whether or not that is
economic.

Gas streams are declared as **volumes** (Nm³) with a separate calorific
value (`ng_cog_cv`, `ng_bfg_cv`, `ng_bofg_cv`, `ng_sintgas_cv`, GJ/Nm³); the
constraints multiply the two, so every gas flow variable in the model is in
**GJ**, not Nm³.

Notable coefficients with embedded modelling decisions:

- `n4_e_dri = 217` kWh/t-DRI — the comment records this as *100 base + 117*,
  the extra 117 being coal-DRI's induction-furnace-heavy secondary melting,
  folded into the DRI shaft's power so the shared EAF coefficient can stay
  route-neutral.
- `n7_e_eaf{t} := 664` and `n8_e_eaf{t} := 785` — declared as **defined
  params indexed over T but constant in t**. `n8` is a 75% IF @825 + 25% EAF
  @664 weighting for the India scrap fleet. Being defined, neither can be
  `let` by a scenario.
- `n6_h2_dri = 0.07` t-H2 per t-DRI — deliberately conservative
  (stoichiometric is ≈0.054); the margin covers shaft and efficiency losses.

### 3. Scrap blending (`phi*`)

Scrap enters the model three ways, and this block governs all of them:

| Symbol | Default | Meaning |
|---|---|---|
| `phi0_bof` | 0.09 | 2025 *observed* scrap share of the BOF metallic charge |
| `phi0_cdri` | 0.382 | 2025 observed share, coal-DRI-EAF/IF charge |
| `phi0_ngdri` | 0.13 | 2025 observed share, NG-DRI-EAF charge |
| `phi_min_bof` | 0.05 | floor on the BF-BOF charge thereafter |
| `phi_min_cdri/ngdri/h2dri` | 0 | no floor on the DRI routes |
| `phi_max_bof` | 0.20 | ceiling, BF-BOF |
| `phi_max_cdri/ngdri/h2dri` | 0.40 | ceiling, each DRI route |
| `blend_ramp` | 0.05 | max year-on-year change in blend share |

The `phi0_*` values *pin* 2025 (equality constraints in `e_bof.mod`,
`i_dri_coal.mod`, `j_dri_ng.mod`); the min/max/ramp trio governs 2026-2050.
`blend_ramp = 0.05` means a route cannot swing its scrap share by more than
5 percentage points in one year — this is what stops the optimiser from
instantaneously flipping the whole fleet onto scrap the moment scrap becomes
cheap.

### 4. Scrap availability

```ampl
param n8_scrap_rate default 0.06;
param n8_scrap_seed default 37000000;
param n8_scrap_limit{t in T} :=
    if ord(t) = 1 then n8_scrap_seed
    else n8_scrap_limit[prev(t)] * (1 + n8_scrap_rate);
```

37 Mt/yr in 2025 compounding at 6%/yr → ≈159 Mt/yr by 2050. This ceiling is
enforced by `scrap_bound` in `t_additional_constraints.mod`.

`n8_scrap_limit` is a **defined param with a self-referential recursion** —
the single most important derived quantity in the file. Before the refactor
it was mutable and populated by a hand-written `let` recursion in each
study's template; a scenario that overrode `n8_scrap_rate` without also
re-running that recursion got the *old* trajectory and a silently wrong
answer. As a defined param it recomputes on every read, so
`let n8_scrap_rate := 0.03;` now propagates correctly — including into
already-built constraints, and including after a prior `solve`.

### 5. Learning axes (`theta_*`) — the scenario dials

Three dimensionless speeds in [0,1], 0 = pessimistic/slow, 1 = optimistic/fast:

| Dial | Governs | Slow (θ=0) → Fast (θ=1) |
|---|---|---|
| `theta_tech` | green-H2 cost | electrolyser capex 550 → 150 $/kW; RE capex 600 → 200 $/kW (both 2050 endpoints) |
| `theta_grid` | India grid | 2050 tariff 0.085 → 0.055 $/kWh; 2050 EF 0.0006 → 0.0003 tCO2/kWh |
| `theta_ccs` | capture plant | 2050 overnight-capex decline vs 2025: 30% → 80% |

Each θ is a **linear interpolation weight between a named slow endpoint and
a named fast endpoint**, and the resulting 2050 value is then linearly
interpolated back to a fixed 2025 anchor. So a θ does two interpolations:
θ picks the 2050 value, then time picks the path to it.

```ampl
param n9_grid_ef_end default
    grid_ef_end_slow + theta_grid*(grid_ef_end_fast - grid_ef_end_slow);
param n9_grid_ef{t in T} :=
    n9_grid_ef_start + (n9_grid_ef_end - n9_grid_ef_start)*(t - 2025)/25;
```

Note the asymmetry: `n9_grid_ef_end` is declared `default` (**mutable**) so a
study can set a *target 2050 EF directly*, while `n9_grid_ef{t}` is
`:=` (**defined**). The grid study exploits this in the opposite direction —
it back-solves θ from a target EF:
`theta_grid := (target − slow)/(fast − slow)`.

The comment on the H2 band records the intended calibration: θ_tech = 0 lands
2050 H2 in the expensive $3-4/kg band (≈$3.7), θ_tech = 1 in the cheap
$1-2/kg band (≈$1.8). **2050 H2 cost is never specified directly** — it
emerges from the capex/CRF build-up in §8.

`core/parameters.mod` sets all three to **0.5** as the baseline, i.e. the
central case is the midpoint of every band.

### 6. Waste heat and grid emission factor

| Symbol | Kind | Value | Meaning |
|---|---|---|---|
| `n9_eta` | mutable | 0.15 | WHR conversion efficiency incl. losses |
| `n9_whr{t}` | **defined** | 0.05 → 0.30 | WHR *penetration*, linear 2025→2050 |
| `n9_grid_ef_start` | mutable | 0.000886 | 2025 grid EF, tCO2/kWh |

`n9_grid_ef_start = 0.000886` is documented as a blend: 0.000757 from the
grid (36% share) and 0.00096 from captive power plants (64% share) — i.e.
it is a *steel-sector* effective EF, not the national grid EF.

The two WHR numbers multiply: by 2050 at most 30% of the accessible pool is
tapped, at 15% conversion efficiency.

### 7. Cost parameters

Flat commodity prices ($/t unless noted), constant over the horizon:
coking coal 184, non-coking coal 98, PCI coal 110, fine ore 65, lump ore 70,
lime 60, biochar 60, breeze (bought) 85, scrap 350, electrode 600.
Credits (revenues) net off cost: breeze 55, tar 20, slag 15, power 0.03/kWh.

Time-varying:

- `ng_cost_power{t}` — **defined**, grid tariff interpolated from
  `grid_price_start = 0.07` to the θ_grid-weighted 2050 endpoint.
- `n5_cost_NG{t}` — **mutable**, $/MMBtu, defaulting to 10. Indexed over T
  specifically so a study can impose a *shock window*; `parameters.mod`
  carries a commented-out `let {t in 2035..2040} n5_cost_NG[t] := 22.5;`.
- `n6_capex_h2{t}` — **defined**, H2-DRI plant capex falling 120 → 90 $/tCS.

Unit-conversion traps live here: `cost_ngdri_def` in `r_cost.mod` multiplies
`n5_cost_NG[t] * 50`, i.e. **50 MMBtu per tonne of NG**, and `ng_co2_gj`
is stated as 0.0521 tCO2/GJ `(= 0.055 t/MMBtu)`.

`carbon_tax` defaults to **0** — it is declared and wired into `yreport.mod`'s
per-route cost decomposition but is **absent from the objective**. See Caveats.

### 8. Capacity, vintaging and capital recovery

The capital block is where most of the derived-param machinery lives.

**Seed fleet (2025 installed capacity)** — `cap0_bof` 90 Mt, `cap0_cdri`
104.1 Mt, `cap0_ngdri` 12.9 Mt, `cap0_h2dri` 0, `cap0_scrap` 0.75 Mt.
Total ≈ 207.75 Mt against 152.2 Mt of 2025 demand: the fleet starts with
substantial idle capacity, which pays fixed opex.

**Lifetimes** — BOF 25 yr, coal-DRI 20, NG-DRI 20, H2-DRI 25, scrap-EAF 15,
CCS retrofit 15, electrolyser 15, renewables 25.

**Utilisation band** — `util_max = 0.95` for all routes; minimum utilisation
is route-specific (BOF 0.85, coal-DRI 0.75, NG-DRI 0.70, H2-DRI 0.70,
scrap-EAF 0.60). The minimum is the discipline that makes stranded assets
expensive: a route you built must keep running.

**Capital recovery.** The chain is:

```
acapex_<route>          annualised capital charge, $/tCS/yr
    = sum of the plant capexes along that route
crf_<route>             = r(1+r)^L / ((1+r)^L − 1)
ocapex_<route>          overnight $ per (t/yr) of capacity
    = acapex / crf
```

So the model's *primitive* input is the **annualised** charge, and the
overnight cost is **back-solved** from it. That is the reverse of the usual
direction and matters for interpretation:

| Route | `acapex` build-up | $/tCS/yr |
|---|---|---|
| BF-BOF | coke 40 + sinter 30 + pellets 10 + BF 80 + BOF 40 | 200 |
| coal-DRI | DRI 110 + pellets 10 + EAF 70 | 190 |
| NG-DRI | DRI 90 + pellets 10 + EAF 70 | 170 |
| H2-DRI | `n6_capex_h2[t]` (120→90) + pellets 10 + EAF 70 | 200→170 |
| scrap-EAF | EAF 70 | 70 |

**Supply-chain capex** — `ocapex_scrapchain = 100` $/(t-scrap/yr) covers
collection, shredding, sorting; `ocapex_coalchain` and `ocapex_ngchain` are
**0**, the comment noting that mine/pipeline capital is considered already
embedded in the fuel price.

**`sunk`** (default 1) selects the capital accounting regime in
`v_capacity.mod`: 1 = overnight capex booked on *builds* and fixed opex on
*installed capacity* (the realistic, stranding-aware mode); 0 = annualised
capex and fixed opex charged on *production* (the textbook levelised mode,
in which idle capacity is free).

### 9. CCS cost build-up

The anchor is a single all-in price, `n10_ccs_cost_start = 125` $/tCO2,
declared as **inclusive of capex, O&M, energy (electricity + steam), solvent,
and transport & storage**. The overnight capex is then *residualised* out of it:

```ampl
param ocapex_ccs_2025 :=
    max( n10_ccs_cost_start
         - ccs_ts_cost            # 20  $/tCO2 transport & storage
         - ccs_vopex_solvent      # 5   $/tCO2 solvent makeup
         - ccs_kwh_bf*ccs_ref_elec    # 130 kWh × 0.07 $/kWh
         - ccs_steam_bf*ccs_ref_steam # 3.0 GJ × 5 $/GJ
       , 10 ) / (crf_ccs + ccs_fom_pct);
```

125 − 20 − 5 − 9.1 − 15 = **75.9 $/tCO2** of annualised capital charge,
divided by (CRF₁₅ ≈ 0.1030 + FOM 4%) ≈ 0.1430 → **≈531 $ per (tCO2/yr)**
overnight. The `max(…, 10)` is a floor guarding against an anchor so low the
residual goes negative.

This is calibrated on the **BF-BOF reference stream**. Other streams are
scaled by explicit multipliers rather than re-derived:

| Stream | `ccs_mult` | kWh/tCO2 | GJ steam/tCO2 | rationale |
|---|---|---|---|---|
| BF (BFG, ~20-25% CO2) | 1.0 | 130 | 3.0 | the reference |
| coal-DRI kiln off-gas | 1.2 | 150 | 3.3 | leaner |
| NG-DRI process stream (60%) | 0.5 | 110 | 0.3 | concentrated, cheap |
| NG-DRI flue (~4-8% CO2, 40%) | 1.3 | 170 | 3.6 | leanest, dearest |

The NG-DRI figures the model actually uses are the
`ccs_ngdri_proc_share`-weighted blends — defined params, so changing the
0.6 split re-derives all three consistently.

Learning: `ccs_capex_fall` interpolates 30% → 80% on θ_ccs, then
`ocapex_ccs{t}` declines **linearly** to that fraction by 2050, and
`fom_ccs{t}` tracks it at 4%.

### 10. Green-H2 supply chain

Green H2 is modelled as an explicit **build**, not a price. Two assets:

- **Electrolyser** — `h2_kwh_per_t = 55 000` kWh/t-H2 (55 kWh/kg incl. BoP),
  capex `h2elec_capex_kw{t}` falling 850 $/kW → the θ_tech endpoint,
  15 yr life, `fopex_h2elec = 400` $/(t-H2/yr)/yr.
- **Dedicated renewable** — `re_cf = 0.35` (India solar/wind hybrid),
  capex `re_capex_kw{t}` falling 800 $/kW → the θ_tech endpoint, 25 yr life,
  `fopex_h2re = 15` $/kW/yr. Sizing: `h2_kw_per_t = h2_kwh_per_t/(8760·re_cf)`
  ≈ **17.9 kW of RE per (t-H2/yr)**.

**The firming term is a calibration residual, not a costed asset.** The bare
electrolyser + RE build-up produces `h2_lcoh_base_2025`; the model is told
2025 LCOH must be `lcoh_2025_target = 5000` $/t (= $5/kg); the gap is
capitalised and called firming:

```ampl
param h2_firm_capex{t in T} :=
    max(lcoh_2025_target - h2_lcoh_base_2025, 0)/crf_h2elec
    * h2elec_capex_kw[t]/h2elec_capex_kw[2025];
```

It then decays *in proportion to electrolyser capex*. So whatever real-world
cost the $5/kg anchor was capturing (storage, curtailment, grid backup,
margin), the model assumes it falls at the electrolyser's learning rate.

`h2_capex_mult` (default 1) is a blunt multiplier on both overnight costs,
for sensitivity work.

### 11. H2 ramp shape

```ampl
param h2_ramp_mode  default 2;    # 0 none | 1 linear | 2 gaussian (default)
param h2_ref_cap    default 4000000;
param h2_peak_rate  := 0.25;
param h2_base_start := 0.00;      param h2_base_end := 0.05;
param h2_gauss_sigma := 2;
param h2_peak_lag   default 5;
param h2_peak_year  := ng_h2_start_year + h2_peak_lag;
```

`h2_ref_cap` is the **envelope scale** — the electrolyser build ceiling in
`v_capacity.mod` is `h2_ref_cap × (rising baseline + Gaussian surge)`, with
the surge pinned so the peak annual addition rate is 25% of `h2_ref_cap`.
At the default 4 Mt that is a **1.0 Mt/yr peak H2 build**. The three "ramp
levels" used across studies pair it with `cap_add_common`:

| Level | `cap_add_common` | `h2_ref_cap` | peak H2 |
|---|---|---|---|
| Low | 10 Mt | 4 Mt | 1.0 Mt/yr |
| Medium | 15 Mt | 6 Mt | 1.5 Mt/yr |
| High | 20 Mt | 8 Mt | 2.0 Mt/yr |

`h2_peak_year` is **defined**, so it follows `ng_h2_start_year` automatically
— the buildout crest sits 5 years after the H2 debut. Pre-refactor this was
a mutable param each template re-`let` by hand; a scenario that moved the
debut year without moving the peak got a Gaussian centred in the wrong place.

`h2_ramp_mode = 0` is a **no-discipline counterfactual**: it swaps in
`H2_BIGM = 1e10` for every ramp ceiling *and* switches off the utilisation
band in `v_capacity.mod`. Modes 1 and 2 both keep the discipline on.

## Depends on

Nothing. This is the root of the include chain — it only needs `set T`,
declared in `model.mod` immediately before the include.

## Caveats

1. **`real_discount_rate` is a defined param (`:=`, line 6).** A discount-rate
   sensitivity is therefore impossible from a scenario file — `let
   real_discount_rate := 0.08;` is an AMPL error. Given that every `crf_*`
   and `discount_factor` derives from it, this is the most consequential
   parameter in the model and the least reachable. Converting it to
   `default 0.06` would make it overridable with no other change.

2. **Same for `n7_e_eaf`, `n8_e_eaf`, `n5_capex_ng`, `h2_peak_rate`,
   `h2_base_start/_end`, `h2_gauss_sigma`, `fc_max`** — all declared `:=`
   despite being plain constants with no derivation. This is `:=` used as
   "constant" rather than as "derived", and it locks them against scenarios
   for no modelling reason.

3. **`n5_ng_cap{T}` is declared with no default (line 91).** It is populated
   only in `core/parameters.mod`, and it is a *hard* cap enforced by
   `ng_bound`. If a future scenario file replaces `parameters.mod` without
   supplying `n5_ng_cap`, AMPL will fail at solve time on an uninitialised
   param rather than defaulting to unbounded. A `default 1e12` would be
   safer, matching the pattern already used for `ccoal_cap`.

4. **`carbon_tax` is declared but never enters the objective.** It appears
   only in `yreport.mod`'s per-route cost decomposition. Setting it non-zero
   changes the *reported* route costs without changing the optimal solution
   — a trap for anyone assuming it prices carbon.

5. **The `_25`/`_50` efficiency drift is exogenous and unconditional.** Coke
   rate falls 0.53 → 0.48 t/thm and biomass PCI rises 0 → 0.053 t/thm
   whether or not the blast furnace is economic, and with no capital charge
   attached. The BF route therefore decarbonises for free along a fixed path.

6. **Commodity prices are flat in real terms for 26 years** — coking coal at
   184 $/t in both 2025 and 2050. Only power, NG (if a study says so), H2
   and CCS have cost trajectories. Route competition is therefore driven
   almost entirely by the three θ dials.

7. **The firming residual (§10) is definitionally whatever makes 2025 LCOH
   equal $5/kg.** If `h2elec_capex_start`, `re_cf` or `h2_kwh_per_t` is
   changed, firming silently absorbs the difference and 2025 LCOH stays at
   $5/kg. That is convenient for calibration and dangerous for sensitivity:
   changing an electrolyser assumption may move 2050 H2 cost while leaving
   2025 pinned.

8. **`ng_biochar_cv`, `ng_coke_cv` and the other commented-out calorific
   values (lines 16-21)** suggest an earlier energy-balance formulation that
   was replaced by direct mass coefficients. They are dead but harmless.
