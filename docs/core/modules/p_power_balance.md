# `p_power_balance.mod` — site electricity balance

> **Source:** `core/modules/p_power_balance.mod` — 28 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

One constraint. Sums every electricity consumer on the site, subtracts every
on-site generator, and defines the residual as `grid_power_in[t]` — the
quantity that gets priced at `ng_cost_power[t]` and carries the grid emission
factor into Scope 2.

Small module, large consequence: this is where the model's entire Scope-2
footprint is determined, and it is the reason `theta_grid` moves every route
at once.

## Declares

No parameters, no variables. One equality constraint (eq83).

## Equations

```ampl
s.t. total_power_balance{t in T}:
      coke_power_in + sinter_power_in + bf_power_in
    + coaldri_power_in + ngdri_power_in + h2dri_power_in
    + pellets_bf_power + pellets_power_coaldri + pellets_power_ngdri + pellets_power_h2dri
    + eaf_power_in + bof_power_in + scrap_eaf_power_in
    + power_ccs
    − cdq_power_out − sinterwaste_power_out − bf_trt_out − whr_power_generated
    − grid_power_in
    = 0;
```

### Consumers (13 terms)

| Group | Terms |
|---|---|
| BF-BOF chain | coke oven (75 kWh/t-coke), sinter (50 kWh/t), BF (55 kWh/thm), BOF (174 kWh/tCS), BF pellets (200 kWh/t) |
| DRI shafts | coal 217, NG 120, H2 110 (kWh/t-DRI) |
| DRI pellet plants | 200 kWh/t each, three of them |
| Steelmaking | DRI-EAF 664, scrap-EAF 785 (kWh/tCS) |
| Carbon capture | `power_ccs` — 130/150/134 kWh per tCO2 by stream |

### On-site generation (4 terms)

| Term | Source | Rate |
|---|---|---|
| `cdq_power_out` | coke dry quenching | 80 kWh/t-coke |
| `sinterwaste_power_out` | sinter cooler | 30 kWh/t-sinter |
| `bf_trt_out` | top-pressure recovery turbine | 35 kWh/thm |
| `whr_power_generated` | waste-heat pool | `whr_gas_to_power × 41.67` kWh/GJ |

The first three are **fixed proportional recoveries** — no decision, no
capital charge beyond what is bundled into `acapex_bof`. Only
`whr_power_generated` is a decision, and it is bounded by
`o_waste_heat.mod`'s pool allocation.

### What is deliberately absent: the electrolyser

The module header is explicit:

> the green-H2 electrolyser load is NOT included here. It is supplied by
> dedicated renewables (`cap_h2re`, sized to cover it in `v_capacity.mod`),
> behind the meter, so it draws no grid power and incurs no grid-EF Scope-2 —
> this is what keeps the hydrogen green.

At `h2_kwh_per_t = 55 000` and `n6_h2_dri = 0.07`, the omitted load is
**3 850 kWh per t-DRI** — roughly 30× the H2 shaft's own 110 kWh, and larger
than the entire rest of the site's per-tonne draw. Including it at grid EF
would make H2-DRI the *dirtiest* route in the model rather than the cleanest.

The offsetting discipline is `v_capacity.mod`'s `h2re_cover`:
`55 000 × h2dri_h2_in[t] ≤ cap_h2re[t] × 8760 × re_cf`, i.e. dedicated
renewable capacity must generate at least as much energy annually as the
electrolyser consumes. The capital for that RE **is** charged
(`ocapex_h2re × build_h2re`). So the treatment is: capital explicit, energy
off-balance, additionality asserted by an annual energy constraint.

### Sign convention and the grid-power variable

`grid_power_in >= 0` (from `variables.mod`), so the site can never be a net
exporter — if on-site generation exceeded consumption the constraint would be
infeasible rather than producing a sale. Not reachable at current
coefficients (recovered power is ~150 kWh/tCS against ~1 000+ kWh/tCS of
demand), but see `r_cost.md` caveat 2.

`grid_power_in` is consumed by exactly one other constraint,
`s_emissions.mod`'s `scope2_def`:

```ampl
n9_grid_ef[t] * grid_power_in[t] − scope2_emissions[t] = 0;
```

Note that grid **power cost** is *not* charged here — it is charged
process-by-process in `r_cost.mod`, where each `cost_*_def` multiplies its
own power draw by `ng_cost_power[t]`, and the recovered-power terms are
credited at the same tariff. This module only determines the emissions base.

## Depends on

Every power variable, each pinned by its own process module
(`a_coke`, `b_sinter`, `c_pellets_bf`, `d_blast_furnace`, `e_bof`,
`f/g/h_pellets_*`, `i_dri_coal`, `j_dri_ng`, `k_dri_h2`, `l_eaf_dri`,
`m_scrap_eaf`, `q_carbon_capture`, `o_waste_heat`).

Feeds `s_emissions.mod` (`scope2_def`).

## Caveats

1. **Green H2's electricity is off-balance by design.** The additionality
   test is *annual energy*, not hourly matching — a 35%-capacity-factor solar
   fleet is deemed to supply a continuously-running electrolyser. Whether that
   is defensible is the single biggest interpretive question about the H2
   route's emissions, and it is a modelling choice, not a result. See
   `v_capacity.md` caveat 6.

2. **Power cost and power emissions are computed in different places.** Cost
   is charged per process in `r_cost.mod`; emissions are charged once on the
   net grid draw here. That is consistent *only because* the recovered-power
   credits in `r_cost.mod` use the same `ng_cost_power[t]` and the same
   quantities that are subtracted here. A change to one side must be mirrored
   in the other, and nothing enforces it.

3. **On-site recovered power is emission-free but its fuel is not.** CDQ,
   TRT and sinter-cooler power come from process heat whose CO2 has already
   been counted in `scope1_*` (coal, coke). That is correct — but it means
   these recoveries reduce Scope 2 with no Scope-1 offset, making them
   unambiguously beneficial and always used at full rate.

4. **Captive power plants are not modelled separately.** India's steel sector
   runs largely on captive coal generation; the model folds that into a
   single blended emission factor (`n9_grid_ef_start = 0.000886`, documented
   as 36% grid + 64% CPP). So the model cannot represent a plant switching
   from captive coal to grid renewables independently of the national grid.

5. **No time-of-day, no demand charges, no transmission constraint.** One
   annual energy balance at one tariff.
