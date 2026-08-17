# `v_capacity.mod` — capacity, vintaging, build ramps, supply chains

> **Source:** `core/modules/v_capacity.mod` — 235 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

The largest and most consequential module. It converts the model from a
static flowsheet into a **capacity-expansion problem**: plants must be built
before they can produce, builds are capital-charged, capacity retires on a
vintage schedule, incumbent 2025 assets decay, and utilisation must stay
inside a band. It also carries the green-H2 build ramp — the mechanism that
makes "when can hydrogen realistically scale?" a modelled question rather
than an assumption.

Without this module the model would simply pick the cheapest route in every
year independently. With it, the model must pay for transitions.

## Declares

### Variables (30 blocks, all continuous `>= 0`)

Declared here rather than in `variables.mod`:

| Group | Variables |
|---|---|
| Builds | `build_bof`, `build_cdri`, `build_ngdri`, `build_h2dri`, `build_scrap` |
| Surviving incumbents | `legacy_bof`, `legacy_cdri`, `legacy_ngdri`, `legacy_h2dri`, `legacy_scrap` |
| Installed capacity | `cap_bof`, `cap_cdri`, `cap_ngdri`, `cap_h2dri`, `cap_scrap` |
| Cost aggregates | `capex_cost`, `fixopex_cost` |
| Scrap chain | `scrapchain_cap`, `build_scrapchain` |
| Coal chain | `coalchain_cap`, `build_coalchain` |
| NG chain | `ngchain_cap`, `build_ngchain` |
| Green H2 | `build_h2elec`, `cap_h2elec`, `build_h2re`, `cap_h2re` |
| CCS retrofit (line 181+) | `build_ccs_bf/cdri/ngdri`, `ccs_cap_bf/cdri/ngdri` |

The CCS retrofit block sits **mid-file at line 181**, after the cost
equations — easy to miss when scanning declarations.

### Parameters

None. All parameters used here are declared in `definitions.mod`
(`cap0_*`, `life_*`, `util_min_*`, `util_max`, `cap_add_common`, `sunk`,
`ocapex_*`, `acapex_*`, `fopex_*`, `h2_*`, `H2_BIGM`, `ramp_frac`) or
`parameters.mod` (`H2_cap`).

## Equations

### 1. Vintaged capacity accounting (lines 44-58)

```ampl
cap_bof[t] = legacy_bof[t]
    + sum{j in T: ord(j) <= ord(t) and ord(j) >= ord(t)-life_bof+1} build_bof[j];
```

Installed capacity = surviving incumbents + every build still inside its
life window. A build in year *j* contributes to years *j* … *j+L−1* and then
**retires automatically** — there is no explicit retirement variable. Five
identical constraints, one per route, each using its own `life_*`.

Consequence worth noting: with `life_scrap = 15` and a 26-year horizon, a
scrap-EAF built in 2025-2035 retires *within* the horizon and must be
rebuilt (and re-paid) to keep producing. With `life_bof = 25`, a BOF built
in 2026 or later never retires inside the horizon.

### 2. Incumbent fleet decay (lines 63-80)

```ampl
legacy_bof[t]  <= cap0_bof * (2050 - t)/25;      # ceiling: linear to zero at 2050
legacy_bof[t]  <= legacy_bof[prev(t)];           # non-increasing
legacy_bof[first(T)] = cap0_bof;                 # seeded at 2025 capacity
```

Three constraints per route. The 2025 fleet sits under a **linearly declining
ceiling that reaches exactly zero in 2050** — so by construction *none* of
today's plants survive to the end of the horizon, regardless of economics.
The optimiser may retire faster (the ceiling is `<=`, and `legacy` is
non-increasing), never slower.

This is the model's mothballing lever: `legacy` capacity is free of capex but
pays `fopex` in `fixopex_cost_def`, so retiring early saves fixed O&M at the
cost of losing the production headroom.

### 3. Utilisation band (lines 83-87, 103-107)

```ampl
steel_bof[t] <= (if h2_ramp_mode = 0 then 1 else util_max)     * cap_bof[t];
steel_bof[t] >= (if h2_ramp_mode = 0 then 0 else util_min_bof) * cap_bof[t];   # t > 2025
```

Production sits between `util_min_<route>` and `util_max = 0.95` of installed
capacity. The **minimum** is the economically important half: a plant you own
must run at (e.g.) 85% for BOF, or you must retire the capacity. This is what
makes premature transitions expensive and produces stranded-asset behaviour.

Route floors: BOF 0.85, coal-DRI 0.75, NG-DRI 0.70, H2-DRI 0.70,
scrap-EAF 0.60.

**`h2_ramp_mode = 0` switches the entire band off** (max → 1, min → 0). That
is the "no-discipline counterfactual": free capacity, no utilisation floor,
no build ceiling. It is not a hydrogen setting despite the name — the flag
governs three unrelated disciplines at once. See Caveats.

### 4. Build ceilings (lines 90-100)

```ampl
build_bof[t] <= (if h2_ramp_mode = 0 then H2_BIGM else cap_add_common);   # t > 2025
build_bof[first(T)] = 0;
```

At most `cap_add_common` (default 10 Mt/yr) of new capacity per route per
year, and **no new builds at all in 2025** — the first year is the observed
starting point, not a decision.

Note the asymmetry: there are four ceilings (BOF, coal-DRI, NG-DRI, scrap)
and four zero-in-2025 constraints — **`build_h2dri` has neither**. H2-DRI's
build rate is governed indirectly through the electrolyser ramp (§7), as the
`definitions.mod` comment states. So `build_h2dri[2025]` is free, though
`h2elec_predebut` + `h2elec_cover` force `h2dri_h2_in[2025] = 0` at the
baseline debut of 2030, which makes any 2025 H2-DRI capacity useless rather
than forbidden.

### 5. Supply-chain capacity (lines 110-139)

Three near-identical blocks — scrap, coal, natural gas:

```ampl
scrapchain_cap[2025] = <2025 flow>;                          # seeded, equality
scrapchain_cap[t]   >= <flow in t>;                          # must cover use
scrapchain_cap[t]   >= scrapchain_cap[prev(t)];              # ratchet: never shrinks
build_scrapchain[t] >= scrapchain_cap[t] - scrapchain_cap[prev(t)];
```

The **ratchet** (`mono`) is the modelling content: supply infrastructure once
built is never un-built, so a temporary spike in scrap use permanently raises
the capital base. `build_*` is charged at `ocapex_*chain` in `capex_cost_def`.

Only the scrap chain has a non-zero cost (`ocapex_scrapchain = 100`
$/(t/yr)); `ocapex_coalchain` and `ocapex_ngchain` are 0, so the coal and NG
chain blocks are currently **structurally present but economically inert**.

The covered flows:
- scrap: `bof_scrap_in + eaf_scrap_in + scrap_eaf_scrap_in`
- coal: `coking_coal_in + bf_coalpci_in + coaldri_coal_in + eaf_coal_in + scrap_eaf_coal_in`
- NG: `ngdri_ng_in`

### 6. Capital and fixed-opex cost (lines 142-178)

The `sunk` switch selects between two capital-accounting worlds:

```ampl
capex_cost[t] =
    sunk     * ( Σ ocapex_<asset>[t] * build_<asset>[t] )
  + (1-sunk) * ( Σ acapex_<asset>[t] * <production>[t] );

fixopex_cost[t] =
    sunk     * ( Σ fopex_<route> * cap_<route>[t] )
  + (1-sunk) * ( Σ fopex_<route> * <production>[t] );
```

| `sunk` | Capex charged on | Fixed opex charged on | Idle capacity |
|---|---|---|---|
| **1** (default) | builds, at overnight cost, in the build year | installed capacity | **costs money** |
| 0 | production, annualised | production | free |

`sunk = 1` is the realistic mode and the one every study uses: it is what
makes over-building painful and stranding visible. `sunk = 0` reduces the
model to textbook levelised-cost competition where capacity is costless
optionality.

Assets charged under `sunk = 1`: the five routes, the three supply chains,
the electrolyser, and the dedicated renewables. Under `sunk = 0` the
electrolyser and RE are charged per tonne of H2 consumed
(`acapex_h2elec[t]*h2dri_h2_in[t]`, and RE via
`h2dri_h2_in[t]*h2_kwh_per_t/(8760*re_cf)` to convert t-H2 → kW).

Note `capex_cost` books **overnight** cost in a single year rather than
annualising it. Combined with the objective's `discount_factor`, this is a
genuine NPV of cash capital outlays — but it means capital spent late in the
horizon is only partially "used" before 2050, with no terminal value credit.
See Caveats.

### 7. Green-H2 supply chain (lines 199-235)

```ampl
cap_h2elec[t] = Σ_{j in life window} build_h2elec[j];     # 15 yr
cap_h2re[t]   = Σ_{j in life window} build_h2re[j];       # 25 yr
cap_h2elec[t] = 0,  cap_h2re[t] = 0    for t < ng_h2_start_year;
h2dri_h2_in[t] <= cap_h2elec[t];                          # electrolyser sizing
h2_kwh_per_t * h2dri_h2_in[t] <= cap_h2re[t] * 8760 * re_cf;   # RE sizing
```

The RE constraint is the one that keeps the hydrogen *green*: dedicated
renewable capacity must be large enough that its annual generation
(`cap_h2re × 8760 × re_cf`) covers the electrolyser's full annual demand.
Because it is sized on an **annual energy** basis rather than hourly, no
storage or firming is modelled explicitly — the firming residual in
`definitions.mod` §10 is the cost-side stand-in.

`p_power_balance.mod` correspondingly excludes the electrolyser load from
the grid balance, so green H2 draws no grid power and incurs no Scope-2.

**The ramp ceiling** (lines 215-235) is the centrepiece:

```ampl
cap_h2elec[t] - cap_h2elec[prev(t)] <=
    if   h2_ramp_mode = 0 then H2_BIGM
    else if h2_ramp_mode = 1 then ramp_frac * H2_cap
    else h2_ref_cap * ( h2_base[t]
                       + (h2_peak_rate - h2_base[h2_peak_year])
                         * exp( -((t - h2_peak_year)^2) / (2*h2_gauss_sigma^2) ) );
```

(the inner `h2_base[h2_peak_year]` is written out longhand in the source as
`h2_base_start + (h2_base_end - h2_base_start)*(h2_peak_year-2025)/25`.)

Three modes:

| Mode | Ceiling on annual electrolyser additions |
|---|---|
| 0 | `H2_BIGM = 1e10` — effectively unlimited |
| 1 | `ramp_frac × H2_cap` = 0.15 × 1.5 Mt = **225 kt/yr**, flat |
| **2** (default) | rising baseline + Gaussian surge, peaking at **25% of `h2_ref_cap`** in `h2_peak_year` |

Mode 2's shape: a baseline rate rising linearly 0 → 5% of `h2_ref_cap` per
year across the horizon, plus a Gaussian bump of width σ = 2 years centred on
`h2_peak_year = ng_h2_start_year + 5`, with the bump's height set so the
total at the peak is exactly `h2_peak_rate = 0.25`. At the default
`h2_ref_cap = 4 Mt` the peak year permits **1.0 Mt/yr** of new electrolyser.

Because `h2_peak_year` is a *defined* param, moving `ng_h2_start_year` moves
the crest with it — the delay studies sweep the debut year and get a
correctly-shaped ramp each time, with no per-scenario bookkeeping.

`h2elec_first` applies the same expression as an absolute ceiling on
`cap_h2elec[2025]`, not a delta.

### 8. CCS retrofit capacity (lines 188-197)

```ampl
ccs_cap_bf[t] = Σ_{j: ord(t)-life_ccs+1 <= ord(j) <= ord(t)} build_ccs_bf[j];
ccs_bf[t] <= ccs_cap_bf[t];
```

Same vintage pattern, `life_ccs = 15`. Capture is thus limited **four** ways
in total: by installed retrofit capacity (here), by the physical capturable
base and the sector deployment ceiling (both in `q_carbon_capture.mod`), and
by the availability of regeneration steam (`ccs_steam_balance`).

## Depends on

| Symbol | Owner |
|---|---|
| `steel_bof`, `coaldri_output`, `ngdri_output`, `h2dri_output`, `steel_scrap_eaf`, `h2dri_h2_in`, `ccs_bf/cdri/ngdri` | `variables.mod` |
| `bof_scrap_in`, `eaf_scrap_in`, `scrap_eaf_scrap_in`, `coking_coal_in`, `bf_coalpci_in`, `coaldri_coal_in`, `eaf_coal_in`, `scrap_eaf_coal_in`, `ngdri_ng_in` | `variables.mod` |
| all `cap0_*`, `life_*`, `util_*`, `cap_add_common`, `sunk`, `ramp_frac`, `ocapex_*`, `acapex_*`, `fopex_*`, `h2_*`, `H2_BIGM`, `ng_h2_start_year` | `definitions.mod` |
| `H2_cap` | `parameters.mod` |

Provides `capex_cost[t]` and `fixopex_cost[t]` to `r_cost.mod`'s
`total_cost_def`, and the `ccs_cap_*` / `build_ccs_*` variables to
`r_cost.mod`'s `cost_ccs_def`.

## Caveats

1. **`h2_ramp_mode = 0` is a three-in-one switch.** It disables the H2 ramp
   ceiling (its name), *and* the utilisation band (lines 83-87, 103-107),
   *and* the per-route build ceilings (lines 90-93). A reader who sets it
   expecting "unconstrained hydrogen" also silently removes stranded-asset
   pressure and per-route build limits across the whole fleet. These are
   three separate modelling assumptions sharing one flag.

2. **Incumbent capacity is forced to zero by 2050 by construction**
   (`legacy_ceil_*`). No plant built before 2025 may operate in 2050,
   whatever its economics or actual age. For BOF with a 25-year life this is
   roughly defensible; for a 2024-vintage BOF it is not.

3. **`build_h2dri` has no per-year ceiling and no zero-in-2025 constraint**,
   unlike the other four routes. The intent (build rate governed by the
   electrolyser) is documented, but the H2-DRI *shaft* is a separate physical
   asset and is currently free to appear at any rate.

4. **Overnight capex is booked in the build year with no terminal value.**
   A 25-year-life plant built in 2048 is charged in full but only produces
   for 3 years inside the horizon. This biases the model against late
   builds — a well-known horizon effect, unmitigated here (no salvage credit,
   no post-2050 continuation).

5. **The coal and NG supply chains are structurally modelled but cost
   nothing** (`ocapex_coalchain = ocapex_ngchain = 0`). Their ratchet
   constraints are therefore pure overhead: ~150 constraints and 4 variable
   blocks with no effect on the objective. Harmless, but a reader may assume
   supply-chain capital is being priced for all three fuels when only scrap
   is.

6. **The RE sizing constraint is annual-energy, not hourly.** `cap_h2re ×
   8760 × re_cf >= annual demand` permits a 35%-CF solar fleet to supply a
   100%-utilisation electrolyser with no storage. The cost of bridging that
   gap is folded into `h2_firm_capex`, which is a calibration residual rather
   than an engineered figure — so the *physical* feasibility of the green-H2
   build is not actually tested by the model.

7. **`build_scrapchain[t] >= cap[t] − cap[prev(t)]`** is a `>=`, not an
   equality. Only the cost objective keeps it tight; there is no constraint
   preventing an over-declared build if it were ever beneficial. It is not
   beneficial at positive `ocapex_scrapchain`, so this is safe today and
   would break silently if that capex were ever set to zero or negative.

## Constraint index

| Constraints | Covered under |
|---|---|
| `cap_def_bof`, `cap_def_cdri`, `cap_def_ngdri`, `cap_def_h2dri`, `cap_def_scrap` | §1 Vintaged capacity accounting |
| `legacy_ceil_bof`, `legacy_ceil_cdri`, `legacy_ceil_ngdri`, `legacy_ceil_h2dri`, `legacy_ceil_scrap` | §2 Incumbent fleet decay — linear ceiling to zero at 2050 |
| `legacy_noninc_bof`, `legacy_noninc_cdri`, `legacy_noninc_ngdri`, `legacy_noninc_h2dri`, `legacy_noninc_scrap` | §2 — non-increasing |
| `legacy_init_bof`, `legacy_init_cdri`, `legacy_init_ngdri`, `legacy_init_h2dri`, `legacy_init_scrap` | §2 — seeded at `cap0_*` |
| `cap_lim_bof`, `cap_lim_cdri`, `cap_lim_ngdri`, `cap_lim_h2dri`, `cap_lim_scrap` | §3 Utilisation band — `util_max` ceiling |
| `min_util_bof`, `min_util_cdri`, `min_util_ngdri`, `min_util_h2dri`, `min_util_scrap` | §3 — route-specific floors |
| `cap_add_bof`, `cap_add_cdri`, `cap_add_ngdri`, `cap_add_scrap` | §4 Build ceilings — `cap_add_common`; **no `cap_add_h2dri`** |
| `cap_add_bof0`, `cap_add_cdri0`, `cap_add_ngdri0`, `cap_add_scrap0` | §4 — no new builds in 2025; **no `cap_add_h2dri0`** |
| `scrapchain_legacy`, `scrapchain_cover`, `scrapchain_mono`, `scrapchain_build_def` | §5 Supply-chain capacity — scrap (the only priced chain) |
| `coalchain_legacy`, `coalchain_cover`, `coalchain_mono`, `coalchain_build_def` | §5 — coal (zero capex) |
| `ngchain_legacy`, `ngchain_cover`, `ngchain_mono`, `ngchain_build_def` | §5 — natural gas (zero capex) |
| `capex_cost_def`, `fixopex_cost_def` | §6 Capital and fixed-opex cost — the `sunk` switch |
| `cap_def_h2elec`, `cap_def_h2re` | §7 Green-H2 supply chain — vintaging |
| `h2elec_predebut`, `h2re_predebut` | §7 — zero before `ng_h2_start_year` |
| `h2elec_cover`, `h2re_cover` | §7 — electrolyser and annual-energy RE sizing |
| `h2elec_growth`, `h2elec_first` | §7 — the three-mode ramp ceiling (Gaussian by default) |
| `ccs_cap_def_bf`, `ccs_cap_def_cdri`, `ccs_cap_def_ngdri` | §8 CCS retrofit capacity — vintaging |
| `ccs_caplim_bf`, `ccs_caplim_cdri`, `ccs_caplim_ngdri` | §8 — capture bounded by installed retrofit capacity |
