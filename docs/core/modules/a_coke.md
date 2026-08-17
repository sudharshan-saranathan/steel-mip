# `a_coke.mod` — coke oven

> **Source:** `core/modules/a_coke.mod` — 26 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

The first unit operation of the BF-BOF chain. Converts coking coal into
metallurgical coke, with four by-product streams: breeze, tar, coke oven gas
(COG), and coke dry-quenching (CDQ) waste-heat power.

Everything in this module is **proportional to `bf_coke_in[t]`** — the tonnes
of coke the blast furnace demands. The coke oven has no autonomy: it is a
pass-through sized by downstream demand.

## Declares

No parameters, no variables. Eight equality constraints (eq1-eq8).

## Equations

All eight have the form `coefficient × bf_coke_in[t] − <var>[t] = 0`.

| eq | Constraint | Coefficient | Defines |
|---|---|---|---|
| 1 | `coke_power_balance` | `n0_e_c` = 75 kWh/t-coke | `coke_power_in` |
| 2 | `coke_coal_balance` | `n0_cf` = 1.47 t-coal/t-coke | `coking_coal_in` |
| 3 | `coke_breeze_out_balance` | `n0_br_c` = 0.056 t/t-coke | `coke_breeze_out` |
| 4 | `coke_tar_balance` | `n0_tar_c` = 0.04 t/t-coke | `tar_out` |
| 5 | `coke_cog_out_balance` | `n0_cog_c × ng_cog_cv` = 440 × 0.018 = **7.92 GJ/t-coke** | `cog_out` |
| 6 | `coke_dry_quenching` | `n0_cdq_whr` = 80 kWh/t-coke | `cdq_power_out` |
| 7 | `coke_cog_recovered` | `n0_rec_cog × ng_cog_cv` = 190 × 0.018 = **3.42 GJ/t-coke** | `cokeov_cog_in` |
| 8 | `coke_bfg_recovered` | `n0_rec_bfg × ng_bfg_cv` = 270 × 0.0033 = **0.891 GJ/t-coke** | `cokeov_bfg_in` |

### Reading the gas streams

The `_out` / `_in` naming is directional and worth stating explicitly:

- `cog_out` — COG **produced** by the oven (7.92 GJ/t-coke)
- `cokeov_cog_in` — COG **burned back inside** the oven as underfiring fuel
  (3.42 GJ/t-coke)
- `cokeov_bfg_in` — blast-furnace gas **imported into** the oven as fuel
  (0.891 GJ/t-coke)

So the oven is a net COG *exporter* (7.92 − 3.42 = 4.50 GJ/t-coke available
to the rest of the site) and a BFG *importer*. The source comment records the
intent: *"Remaining COG goes to power plant"* — in this model, to the
waste-heat pool via `o_waste_heat.mod`.

Note that gas variables are in **GJ**, not Nm³: the Nm³ coefficient and the
calorific value are multiplied together inside the constraint. The `440 Nm³`
comment adds *"mass eqv gas ≈ 0.2 tons"*, which is not used anywhere.

### CDQ

Coke dry quenching recovers sensible heat from red-hot coke as power
(80 kWh/t-coke). `cdq_power_out` enters `p_power_balance.mod` as a negative
term (it offsets grid draw) and is credited at the grid tariff in
`r_cost.mod`'s `cost_cokeov_def`. It is **not** routed through the waste-heat
pool — the `o_waste_heat.mod` header notes CDQ, TRT and sinter WHR are
already accounted in their own process flows.

## Depends on

| Symbol | Owner |
|---|---|
| `bf_coke_in` | `variables.mod`; **pinned by `d_blast_furnace.mod`** (eq30) |
| `n0_*`, `ng_cog_cv`, `ng_bfg_cv` | `definitions.mod` |

Feeds:
- `coking_coal_in` → `q_carbon_capture.mod`, `s_emissions.mod`, `r_cost.mod`,
  `v_capacity.mod` (coal chain), `t_additional_constraints.mod` (`coking_coal_bound`)
- `cog_out`, `cokeov_cog_in`, `cokeov_bfg_in` → `o_waste_heat.mod`
- `coke_power_in`, `cdq_power_out` → `p_power_balance.mod`

## Caveats

1. **Coke rate is set downstream, not here.** `bf_coke_in` is defined by
   `bf_coke_balance` in `d_blast_furnace.mod` as an exogenously declining
   function of hot metal (0.53 → 0.48 t/thm). The coke oven cannot choose to
   run at a different rate, and there is no coke import/export option.

2. **No coke oven capacity, lifetime or build decision exists.** `n0_capex`
   (40 $/tCS) is folded into `acapex_bof` and charged against BOF capacity,
   so the oven is treated as an inseparable part of the BF-BOF route. A
   scenario cannot retire coke ovens independently of blast furnaces.

3. **Breeze is simultaneously produced and purchased.** eq3 credits
   `coke_breeze_out` at 55 $/t (`n0_credit_breeze`) while `b_sinter.mod`
   buys `sinter_breeze_in` at 85 $/t (`n1_cost_breeze`). The two are never
   netted — the model sells its own breeze and buys breeze back at a 30 $/t
   markup, in the same year. At current volumes (0.056 t/t-coke produced vs
   ~0.09 t/t-sinter consumed) the site is a net buyer, so the direction is
   plausible, but the double transaction is an accounting artefact rather
   than a modelled market.

4. **All eight coefficients are fixed for 26 years.** Unlike the blast
   furnace and sinter plant, the coke oven gets no `_25`/`_50` efficiency
   drift — coal-to-coke yield, COG make and CDQ recovery are static.
