# Stage 2 — Plant lifetimes

## Evidence

| Source | Statement | Units covered |
|---|---|---|
| IEA (2020) *Iron and Steel Technology Roadmap*, pp. 43–46 | "25-year investment cycles and 40-year typical average lifetimes"; BF relining roughly every 25 years (range 15–30); Indian coal blast furnaces about 15 years old on average | BF, DRI furnaces |
| Transition Asia & TERI (2026), `Model_input_India.xlsx`, sheet Tech | economic life 40 years | shaft furnace, rotary kiln, BOF, EAF |
| Domínguez Bennett et al. (2026), UC Berkeley IECC | "40+-year life" of BF-BOF plants | BF-BOF |
| Vogl, Åhman & Nilsson (2018), *J. Cleaner Production* | 20 years (used for annualising costs) | all plant except the electrolyser |
| Model before the fix | BF-BOF 25, coal-DRI 20, NG-DRI 20, H₂-DRI 25, scrap-EAF 15 | |

## Decisions (2026-10-06)

1. **New builds: `life_bof = life_cdri = life_ngdri = life_h2dri = life_scrap = 40` years.** With a 2026–2050 horizon no new build retires inside the model, so the value matters mainly for the end-of-horizon salvage credit (ST-16).
2. **2025 fleet, run-life case: no retirement before 2050.** No data exist on the remaining life of the Indian fleet. With a 40-year life, the fleet would have to be older than 15 years on average to retire before 2050, and IEA puts Indian blast furnaces at about 15 years. The run-life case therefore keeps the full 2025 capacity available to 2050. This is pessimistic because it keeps the fossil fleet available. The optimizer can still retire plants early, since idle capacity pays fixed opex.
   - Code change (Stage 3): in `legacy_ceil_*` the run-life branch becomes `cap0_*` for all t, instead of being tied to `life_*`. This also separates the legacy fleet from the new-build lifetime.
   - The mandated linear phase-out case (`legacy_phaseout = 1`) is unchanged.
