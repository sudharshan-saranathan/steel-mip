# `parameters.mod` — baseline values, plus two declarations and one constraint

> **Source:** `core/parameters.mod` — 60 lines @ `8c6cb8f`
> Update this doc whenever the source changes.

## Purpose

`model.mod` labels this "baseline input values", and mostly that is what it
is: a block of `let` statements setting the central case. **But it is not
purely data.** It also declares two parameters and one structural constraint:

```ampl
param avg_emi   default 1.8;   # line  9  — declaration, not a `let`
param H2_cap := 1500000;       # line 18  — declaration, not a `let`
s.t. No_H2_Before{t in T: t < ng_h2_start_year}:
    h2dri_h2_in[t] = 0;        # lines 21-23 — a CONSTRAINT
```

That is why the file's position in the include order is load-bearing: it must
come **after** `variables.mod` (it constrains `h2dri_h2_in`) and **before**
the modules that consume `avg_emi` and `H2_cap`. It cannot be treated as a
detachable data file.

## Declares

### `avg_emi` (line 9) — the policy lever

`param avg_emi default 1.8;` — the **cumulative average CO2-intensity cap**
in tCO2/tCS. Consumed by `avg_emis_cap_total` in
`t_additional_constraints.mod`, which is the single constraint that forces
decarbonisation:

```
(Σ_t total_emissions[t]) ≤ avg_emi · (Σ_t total_steel[t])
```

Declared here rather than in `definitions.mod` because it is a *policy*
input, not a technical one. It is the primary sweep axis in the abatement,
scrap and hydrogen-delay studies (typically {1.6, 1.8, 2.0}).

### `H2_cap` (line 18)

`param H2_cap := 1500000;` — "capacity slab per year". Used **only** in
`v_capacity.mod`'s `h2elec_growth` / `h2elec_first` when
`h2_ramp_mode = 1` (linear ramp): the ceiling is `ramp_frac × H2_cap`
= 0.15 × 1.5 Mt = 225 kt/yr. Since `h2_ramp_mode` defaults to **2**
(Gaussian), this parameter is **inert in the baseline**.

Declared with `:=`, so it is a defined param and **cannot be `let`** by a
scenario.

### `No_H2_Before` (lines 21-23) — the H2 debut gate

```ampl
s.t. No_H2_Before{t in T: t < ng_h2_start_year}:
    h2dri_h2_in[t] = 0;
```

Forces zero hydrogen consumption before the debut year. The **indexing set is
a function of `ng_h2_start_year`**, and this is the mechanism that makes the
H2-delay sweeps work: AMPL re-instantiates a constraint's index set whenever
a parameter appearing in it is `let`, **including after a prior `solve`**.
So a driver can loop

```ampl
let ng_h2_start_year := 2035;  solve;
let ng_h2_start_year := 2040;  solve;
```

and each solve sees the correct gate. This was verified explicitly during the
refactor. **Do not "fix" the ordering** by moving the `let` before the model
include — the current form is correct.

`v_capacity.mod` adds the matching capital-side gates
(`h2elec_predebut`, `h2re_predebut`), which use the same mechanism.

## Baseline values set (`let`)

| Line | Setting | Value | Note |
|---|---|---|---|
| 2-4 | `theta_grid`, `theta_tech`, `theta_ccs` | **0.5** each | central case = midpoint of every learning band |
| 7-8 | `base_demand`, `growth_rate` | 152.2 Mt, 0.05 | restates the `definitions.mod` defaults |
| 12 | `n5_cost_NG[t]` | 10 $/MMBtu, all t | flat |
| 17 | `ng_h2_start_year` | **2030** | overrides the `definitions.mod` default of 2040 |
| 26 | `n8_scrap_rate` | 0.06 | restates default |
| 27 | `ng_cost_scrap` | 350 | restates default |
| 28 | `n8_scrap_seed` | 37 Mt | restates default |
| 32 | `n10_ccs_cost_start` | 125 $/tCO2 | restates default |
| 35-60 | `n5_ng_cap[t]` | table, 5.35 → 21.9 Mt | **the only source of these values** |

Two of these are substantive rather than restatements:

- **`ng_h2_start_year := 2030`** — `definitions.mod` defaults it to 2040.
  The baseline case is therefore a *2030* H2 debut, not 2040.
- **`n5_ng_cap[t]`** — `definitions.mod` declares `param n5_ng_cap {T};`
  with **no default**, so this table is the only thing that makes the model
  solvable. It is enforced as a hard cap by `ng_bound`.

### The NG availability table

The header comment calls it "NG cap (Shock case)". The trajectory is not
smooth:

| Years | Shape |
|---|---|
| 2025-2034 | rising 5.35 → 10.93 Mt |
| **2035** | **drops to 7.84 Mt** — a −28% step |
| 2035-2040 | slow recovery 7.84 → 8.71 Mt |
| **2041** | **jumps to 11.72 Mt** — a +35% step |
| 2041-2050 | rising 11.72 → 21.91 Mt |

So the committed baseline has a **six-year natural-gas supply shock built
into it (2035-2040)**. The commented-out price shock on line 14
(`let {t in 2035..2040} n5_cost_NG[t] := 22.5;`) targets exactly the same
window — the price half of the shock is off, the volume half is on. See
Caveats.

At `n5_ng_dri = 0.35` t-NG per t-DRI and a 1.1 metallic ratio, the 2035 cap
of 7.84 Mt limits the NG-DRI route to roughly **24 Mt of crude steel** that
year.

## Depends on

| Symbol | Owner |
|---|---|
| `theta_*`, `base_demand`, `growth_rate`, `n5_cost_NG`, `ng_h2_start_year`, `n8_scrap_rate`, `ng_cost_scrap`, `n8_scrap_seed`, `n10_ccs_cost_start`, `n5_ng_cap` | `definitions.mod` |
| `h2dri_h2_in` | `variables.mod` |

Consumed downstream by:

| Symbol | Consumer |
|---|---|
| `avg_emi` | `modules/t_additional_constraints.mod` (`avg_emis_cap_total`) |
| `H2_cap` | `modules/v_capacity.mod` (`h2elec_growth`, `h2elec_first`; mode 1 only) |

## Caveats

1. **This file is named and described as data but contains structure.** Any
   future "swap in a different parameters file per scenario" design has to
   carry `No_H2_Before` and the two declarations with it, or the H2 gate
   silently disappears — which would *not* make the model infeasible, just
   wrong (H2-DRI available from 2025).

2. **The baseline embeds a 2035-2040 NG supply shock.** It is labelled
   "(Shock case)" but is the committed default, so every study that does not
   override `n5_ng_cap` inherits it. Anyone interpreting NG-DRI's decline in
   the late 2030s as an economic result should check this table first — part
   of it is imposed.

3. **The price shock and volume shock are inconsistent with each other.**
   The commented-out line 14 would raise NG to 22.5 $/MMBtu over exactly the
   window in which the volume cap already falls. Leaving one on and one off
   is a deliberate-looking choice with no recorded rationale.

4. **Six of the ten `let`s are no-ops** (lines 7, 8, 12, 26, 27, 28, 32
   restate `definitions.mod` defaults verbatim). Harmless, but it means the
   file reads as if it defines the baseline when in fact `definitions.mod`
   does, and the two can drift apart silently — a default changed in
   `definitions.mod` will appear to take effect but be overwritten here.

5. **`H2_cap` is dead at the default `h2_ramp_mode = 2`**, and being `:=` it
   cannot be swept. If mode 1 is ever used seriously, the ramp ceiling it
   produces (225 kt/yr) is roughly 4× smaller than the Gaussian mode's peak
   (1.0 Mt/yr at the Low ramp level) — the two modes are not calibrated
   against each other.
