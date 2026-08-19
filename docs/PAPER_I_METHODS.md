# Paper I — Methods (draft)

Target: ~900 words of main text. Everything marked *(SI)* is deferred to
supplementary material, which `MODEL_DESCRIPTION.md` and `RESULTS_TABLES.md`
already cover. Tense follows the convention: present for the model and the
claims, past for what was done on this occasion.

---

## Methods

### Model

We develop from scratch a bottom-up, intertemporal capacity-expansion linear
programme of the Indian iron and steel sector, solved over 2025–2050 at annual
resolution. The model minimises the discounted sum of annual system cost at a
6% real discount rate, subject to physical mass and energy balances, capacity
dynamics, resource availability, and a cumulative emissions constraint.

The model is partial equilibrium: steel demand, fuel prices, electricity
tariffs and the grid emission factor are exogenous. It is bottom-up in that
production is represented as discrete process routes with fixed engineering
coefficients rather than as production functions with substitution
elasticities — substitution occurs by switching between routes subject to
capacity and timing constraints, not by continuous movement along a
substitution curve. This choice is deliberate and is what makes the central
question answerable: because routes exist only after a stated debut year and
can be built only at bounded rates, some parameter combinations admit no
feasible solution. Models built on smooth substitution cannot return that
result, since some input mix is always attainable at some price.

Five crude-steel routes are represented, each with its full upstream chain:
blast furnace–basic oxygen furnace (coke ovens, sinter, pelletising); coal-
based direct reduction with electric arc furnace; natural-gas-based direct
reduction; hydrogen-based direct reduction; and dedicated scrap-based EAF.
Carbon capture is available as a retrofit on the blast furnace and both
fossil DRI routes, subject to a sector-wide deployment ceiling rising linearly
from zero in 2027 to 50% of capturable CO₂ in 2050. Waste heat is recovered
and allocated between power generation and capture-plant steam. Full process
stoichiometry and coefficients are given in the SI *(SI Table S1–S3)*.

Steel demand is exogenous and must be met exactly, growing at 5% per year from
152.2 Mt in 2025 to 515.4 Mt in 2050. Because demand does not respond to
price, material efficiency and demand reduction are unavailable as mitigation
channels, and targets are correspondingly harder to meet than they would be
with elastic demand.

### Capacity dynamics

Installed capacity is a state variable tracked by vintage: capacity in any
year is the sum of builds still within their technical life, plus the
surviving 2025 fleet. Technical lives are 25 years for BF-BOF and H₂-DRI, 20
for both fossil DRI routes, 15 for scrap-EAF, electrolysers and CCS retrofits.
The 2025 fleet totals 207.75 Mt and carries no capital charge — that capital is
already sunk — but does incur fixed operating cost.

Capital is treated as sunk throughout: overnight capital expenditure is charged
in full in the year of construction, and fixed operating cost is charged on
installed capacity rather than on output, so idle capacity continues to cost.
We do not amortise capital against production, because amortisation presumes an
asset runs for a fixed number of years, which is the decision the model makes.
No residual value is credited for asset life extending beyond 2050; we quantify
the resulting bias and its direction in the SI *(SI §4)*.

Hydrogen is produced by electrolysers powered by dedicated renewables, which
are built and paid for explicitly and sit outside the grid balance, so green
hydrogen incurs no Scope-2 emissions. Two controls govern hydrogen deployment:
a debut year, before which the route and its electrolysers are held at zero;
and a ceiling on the annual net increase in electrolyser capacity that rises to
a crest five years after debut and then plateaus at its peak rate. The rising
phase represents the state building enabling infrastructure and supply chains;
the plateau represents a mature industry deploying at the rate that completed
infrastructure supports.

### Emissions constraint

Scope-1 emissions are computed from physical input flows at fixed emission
factors; Scope-2 from grid electricity at a time-varying grid emission factor
interpolating from 886 gCO₂/kWh in 2025 to a 2050 endpoint that is a policy
lever. Captured CO₂ is subtracted. The binding constraint is cumulative rather
than annual: total emissions over the horizon must not exceed a target average
intensity multiplied by total production. No constraint forces annual intensity
to decline monotonically.

### Experimental design

We solved the model across a complete factorial of eight policy-controlled
levers crossed with three emissions-intensity targets — 46,656 scenarios in
total (Table 1). The levers are scrap-availability growth, green-hydrogen debut
year, 2050 grid emission factor, coking-coal availability, gas allocation to
steel, electrolyser deployment rate, the shared annual build budget across the
four conventional routes, and retirement policy for the 2025 fleet.

The selection criterion is that the design varies only what policy controls.
Parameters governed by global technology learning rather than domestic policy
are held fixed here and treated separately.

Each scenario was solved as an independent model instance. We report
feasibility — whether a scenario admits any solution — as the primary outcome.
Because the design is a complete factorial, every lever level appears with
every combination of the others exactly once, so feasibility shares are
balanced across levers and directly comparable without weighting correction.
Such a share is the fraction of remaining lever combinations that admit a
solution; it is a property of the design, not a probability of real-world
success, and the design weights each level of each lever equally.

### Implementation

The model is written in AMPL and solved with Gurobi 13.0.2. Each instance
presolves to approximately 1,000 constraints by 950 variables and solves in
well under a second by dual simplex; the full design solves in 14 minutes on
six cores. Source code, scenario definitions and the complete results table are
available at [repository].

### Limitations

The model assumes perfect foresight, so investment timing is optimal in a way
real decisions are not; feasibility results are therefore an upper bound — a
target infeasible under perfect foresight is infeasible under any weaker
information assumption. Demand and prices are exogenous, the sector is
represented as a single national fleet without regional or plant-level
detail, and blast-furnace efficiency improvements follow a calendar schedule
rather than an investment decision. Remaining assumptions are enumerated in
the SI *(SI §12)*.
