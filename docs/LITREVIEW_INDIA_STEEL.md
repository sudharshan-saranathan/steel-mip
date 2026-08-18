# Literature check — has anyone mapped a feasibility frontier for Indian steel?

Session date 2026-08-18. **Every paper cited below was returned by a search
run in this session** (OpenAlex API, keyless; plus two web searches for grey
literature). Nothing is cited from background knowledge. Where I could not
retrieve an abstract, that is stated — several key papers are paywalled and
OpenAlex holds no abstract for them, so their methods are characterised from
publisher/search-engine summaries and should be verified against the PDFs
before citing in the paper.

## The two questions

1. Has anyone mapped a feasibility frontier for Indian steel across the levers
   this study sweeps — scrap growth, H2 debut year, grid EF, coking-coal and
   gas availability, build rate, retirement policy?
2. What are the generic gaps in Indian steel decarbonisation modelling?

## 1. Feasibility frontier — no evidence of one

**Nothing in these searches maps target *reachability* over a lever space.**
The Indian literature is consistent in a different shape: pick a handful of
named technology pathways, compute cost and emissions for each, and rank them
by marginal abatement cost. Feasibility is not an output — the pathways are
assumed available and the question asked is what they cost.

The closest Indian work found:

| Study | What it does |
|---|---|
| [Environmental and economic evaluation of decarbonization strategies for the Indian steel industry](https://doi.org/10.1016/j.enconman.2023.117511) (Energy Conversion & Management, 2023, 41 cites) | Plant- and sector-level cost/emission accounting via the SESAME Industry and Industrial Fleet models; reports levelised cost and MAC per pathway (smelting+CCS lowest at ~$9/tCO2e). **Method characterised from publisher summary — abstract not retrievable.** |
| [Carbon abatement options for large iron and steel plants in India](https://doi.org/10.1016/j.jclepro.2024.144505) (J. Cleaner Production, 2024) | Plant-level abatement options. Abstract not in OpenAlex. |
| [Process-level emission analysis and decarbonization pathway for BF-BOF route](https://doi.org/10.1016/j.jenvman.2024.123483) (J. Environmental Management, 2024) | Single-route process analysis. |
| [The Contribution of CCS to the Decarbonization of India's Steel Industry](https://doi.org/10.1021/acssuschemeng.3c08088) (ACS Sust. Chem. Eng., 2024) | Single-lever (CCS) assessment. |
| [Economic analysis of the hard-to-abate sectors in India](https://doi.org/10.1016/j.eneco.2022.106149) (Energy Economics, 2022) | Cross-sector economic analysis. Abstract not in OpenAlex. |
| [Towards net-zero emissions concrete and steel in India, Brazil and South Africa](https://doi.org/10.1080/14693062.2023.2187750) (Climate Policy, 2023, 38 cites) | Abstract retrieved. In-country models, decomposition and emissions-driver analysis, scenarios "linked to usable policy levers". Reports mitigation *potential* ranges (13–26% demand side, 58–71% production side) — potential under scenarios, not a feasibility surface. |
| [Green transformation in the iron and steel industry in India](https://doi.org/10.1016/j.esr.2022.100968) (Energy Strategy Reviews, 2022, 76 cites) | Innovation-systems, qualitative. |
| [CEEW, *Evaluating Net-zero for the Indian Steel Industry*](https://www.ceew.in/publications/how-can-india-decarbonise-for-net-zero-steel-industry) | MAC curves across four pillars × four steelmaking routes. Fetched: the page does not disclose whether an optimisation underlies it. |

Global work is closer in ambition but still not a lever-space frontier:

- [Rapid implementation of mitigation measures can facilitate decarbonization
  of the global steel sector in 1.5°C-consistent pathways](https://doi.org/10.1016/j.oneear.2023.10.016)
  (One Earth, 2023) — integrated assessment model, global/regional transition
  pathways, explicitly framed around trade-offs between pathways. Pathways,
  not reachability.
- [Global steel decarbonisation roadmaps: Near-zero by 2050](https://doi.org/10.1016/j.eiar.2025.107807)
  (EIA Review, 2025, 46 cites) — critical review of the roadmap literature.
  **Directly relevant**: it finds the consensus is that the sector lands ~10%
  short of net zero, and lists the binding barriers as scrap availability,
  high-grade ore, renewable/hydrogen availability and affordability, demand
  uncertainty and weak policy signals. Those are close to this study's levers
  — but they are catalogued qualitatively across roadmaps, not swept.
- [Scrap endowment and inequalities in global steel decarbonization](https://doi.org/10.1016/j.jclepro.2023.139041)
  (2023) — the single closest framing found: states that the viability of
  scrap-based zero-emission steel "depends on future scrap availability".
  Global and scrap-only.
- [Regional uptake of direct reduction iron production using hydrogen under
  climate policy](https://doi.org/10.1016/j.egycc.2022.100087) (2022) and
  [Decarbonization strategies for steel production with uncertainty in
  hydrogen direct reduction](https://doi.org/10.1016/j.energy.2023.129057)
  (Energy, 2023) — H2-DRI uptake and uncertainty, not Indian, single-lever.

**Method family that does explore spaces, but not this problem.** The energy
system optimisation literature has mature tooling for exactly this kind of
question, and none of the hits applied it to Indian steel:

- [Modelling to generate alternatives with an energy system optimization
  model](https://doi.org/10.1016/j.envsoft.2015.11.019) (2015, 128 cites) and
  [Modelling to generate alternatives: a technique to explore uncertainty in
  energy-environment-economy models](https://doi.org/10.1016/j.apenergy.2017.03.065)
  (2017, 100 cites) — MGA explores *near-optimal solutions at fixed
  constraints*, which is a different object from sweeping policy constraints
  and recording feasibility.
- [A review of approaches to uncertainty assessment in energy system
  optimization models](https://doi.org/10.1016/j.esr.2018.06.003) (2018, 254
  cites) — the review to position against.
- [Global sensitivity analysis to enhance the transparency and rigour of
  energy system optimisation modelling](https://doi.org/10.12688/openreseurope.15461.1)
  (2023) and [Detail or uncertainty? Applying global sensitivity analysis to
  strike a balance in energy system models](https://doi.org/10.1016/j.compchemeng.2023.108287)
  (2023) — factorial/GSA designs over ESOMs, the methodological neighbours.

**Assessment.** On this evidence the framing — a complete factorial over
policy-controlled levers, with *feasibility* as the reported outcome and a
lever ranking by how much each moves it — appears to be unoccupied for Indian
steel. That is a claim about what these searches found, not proof of absence
(see limits below).

## 2. Generic gaps in Indian steel decarbonisation modelling

Four, each supported by what the searches returned rather than by assertion.
The fourth is the weakest and should be checked further.

**a. Feasibility is not treated as a result.** Across the Indian studies found,
the reported quantities are cost, emissions and MAC. None reports which
targets cannot be met, or under what conditions. When infeasibility appears at
all it is qualitative — the roadmap review's "barriers" list. A model that
returns infeasible answers is reporting information that MAC curves cannot
express.

**b. Scrap is an input assumption, not a swept lever.** Both the global scrap
paper and the roadmap review name scrap availability as decisive, and the
Indian studies take a scrap trajectory as given. Nothing found sweeps it and
reports what its variation does to target reachability — which in this study
is the single largest feasibility effect (swing 0.611).

**c. Single-lever attribution.** The Indian papers found are organised by
technology — CCS, BF-BOF process, H2 — with one lever moving at a time. That
design cannot detect interactions, and this study's results are substantially
interactions: grid decarbonisation is worth 2.5x more under a late H2 debut,
and build capacity 5x more.

**d. Uncertainty methods exist but appear unused here.** MGA and global
sensitivity analysis are established in energy-system modelling; none of the
Indian steel hits used them. Stated with low confidence — my searches were
aimed at feasibility framing, not at uncertainty methods in Indian industry
models, and grey-literature reports are poorly indexed in OpenAlex.

**Not a gap:** technology characterisation. Route-level techno-economics for
H2-DRI, CCS and scrap-EAF are well covered globally and in India. This study
should cite that work rather than re-derive it — which is also the honest
place to source the parameter provenance table that remains open.

## Limits of this check — read before citing

- **~11 searches, one session.** OpenAlex + two web searches. A systematic
  review this is not.
- **OpenAlex relevance ranking is poor for this query.** Broad searches
  returned generic industrial-decarbonisation reviews and, worse, materials-
  science papers matching "steel" and "optimization". The filtered
  title/abstract queries worked; the earlier ones wasted budget.
- **Paywalled abstracts.** The 2023 Energy Conversion & Management paper, the
  2022 Energy Economics paper and the 2024 J. Cleaner Production paper are the
  three most likely to contain an optimisation model, and I could not read
  any of their abstracts directly (ScienceDirect returns 403). **Read these
  three before making a novelty claim in print.**
- **Grey literature is thin in OpenAlex.** Much Indian sectoral modelling
  lives in TERI, CEEW, NITI Aayog, IEA and IEEFA reports. The one CEEW page
  fetched did not disclose its method. If a lever sweep exists anywhere, a
  ministry-facing report is where it would be.
- **No claim of exhaustiveness.** "No evidence found" is the finding; "nobody
  has done this" is not established.
