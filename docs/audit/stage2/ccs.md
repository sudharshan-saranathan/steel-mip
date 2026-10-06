# Stage 2 — Carbon capture and storage (ST-10, register 3.8)

**STATUS: IN PROGRESS** (skeleton written first so work survives container loss).

Model files (audited repo `nakulneupane/steel-sector-decarbonization` @ b33b88a):
`core/definitions.mod` lines 159–161, 174, 213–214, 305–340; `core/parameters.mod:4, 32`;
`core/modules/q_carbon_capture.mod` (whole file).

## Sub-groups
- A. Cost anchor and trajectory — IN PROGRESS
- B. Cost components (T&S, solvent, FOM, life, multipliers) — IN PROGRESS
- C. Energy use (kWh, steam, boiler) — IN PROGRESS
- D. Capture rate and capturable base (ST-10) — IN PROGRESS
- E. Deployment ceiling and earliest start — IN PROGRESS

## Sources read so far
- Ministry of Steel (2024) *Greening the Steel Sector in India*, ch. 9 (pp. 190–223).
- NITI Aayog (2022) *CCUS Policy Framework and its Deployment Mechanism in India* — Tables 6-1 to 6-5 (pp. 137–141), Fig. 2-14 (p. 46), Fig. 6-5 (p. 145), assumptions table (p. 144).
- IEA (2020) *Iron and Steel Technology Roadmap*, Fig. 2.11 notes (p. 107), pp. 84–85.

## Working notes (raw evidence, to be folded into tables)
- MoS 2024 Table 9.13 (p. 221): capture 37 (35–45), transport 7 (4–10), sequestration 20 (2–37), total 64 (41–92) USD/tCO2; best case 20/4/2/26. Source fn 21: Vishal et al. 2021 IJGGC; Smith et al. 2021 MIT.
- MoS 2024 Table 9.1 (pp. 195–197): Tata BF 5 TPD amine, capture cost INR 3,500–4,000/t, steam 1,000–1,100 kg/t, power 80–90 kWh/t; JSW gas-DRI 100 TPD: steam 1,740 kg/t, 45 kWh/t; JSPL MDEA 1,700 kg steam/t, 25–28 kWh/t.
- MoS 2024 Table 9.5 (p. 203): NTPC 20 TPD: steam 1.29 t/t, 117.6 kWh/t, fixed cost 5 %/yr of project cost.
- MoS 2024 p. 199: "existing CO2 capture technologies have a capture efficiency of 55-60%, while the peak capture efficiencies range from 80 to 85%".
- MoS 2024 p. 200: storage lead times "up to 10 years"; Table 9.12 (p. 219): pilot injection yr 5, 100 kt/yr yr 5–6, up to 1 Mt/yr yr 6–9.
- NITI Table 6-2 (p. 138): steel 2 Mtpa BF-BOF ISP, CCU capacity 2 Mtpa, "Around 50%" capture, capex Rs 1,600–2,000 cr.
- NITI Table 6-3 (p. 139): steel 170–190 kWh/t, steam 1.3–1.5 t/t, cash cost Rs 1,900–2,300/t; T&S "additional US$ 10-15 per tonne".
- NITI Table 6-4 (p. 139): steel total capture cost Rs 2,900–3,600/tCO2 (capital charge 1,000–1,300 + cash 1,900–2,300).
- NITI Table 6-1 (p. 137): "pre-combustion capture from BF gas will ensure at least 50% capture with minimum cost of capture".
- NITI Table 6-5 (p. 141): steel capture 4 (base) / 5 (optimistic) Mtpa in 2030 vs 450 Mtpa emissions.
- NITI Fig. 6-5 (p. 145): economy-wide capture as share of capturable: 2% 2030, 10% 2040, 31% 2050 (747 of 2,410 Mtpa). p. 144: "Capturable CO2 85% of emissions".
- NITI Fig. 2-14 (p. 46), t CO2 / t finished steel (CO2 conc.): sinter 0.43 (8%), coke oven 0.27 (23%), BF stoves 0.39 (23%), BOF 0.03 (7%), calcining 0.23 (66%), captive power 0.63 (25%), mills 0.17 (18%); total 2.15.
- IEA 2020 ISTR Fig. 2.11 notes p. 107: "CO2 transport and storage = USD 20/t CO2 captured. ... 90% capture rate assumed for all CCS routes"; p. 84: 2030 "only 1% of the direct emissions ... captured"; 2050 "25% of direct emissions".
- IEAGHG (2013) 2013/04 *Iron and Steel CCS Study*: ref. mill 2,094 kg CO2/t HRC; hot stoves 415 + power plant 982 (+ coke-oven heaters 191 + lime kiln 72); EOP-L1 captures 1,243 kg/t (50.1 % avoided), EOP-L2 1,533 kg/t (60.3 %) (Table, p. 14); "top 5 sources ... ~90% of the total direct CO2"; "could practically reduce CO2 emission by 50 to 60%" (p. 3); MEA steam demand 3.03 GJ/t CO2, MEA make-up 1.0 kg/t (Annex tables); capture+compression electricity 151.9 kWh/t HRC (L1) and 196.3 (L2) => 122 / 128 kWh/tCO2; avoided cost US$74 (L1) / 81 (L2) /t, excl. T&S, 2010 prices, 10 % / 25 yr (pp. 1, 7).
- IEA (2020) *CCUS in Clean Energy Transitions*: BF CO2 20-27 %; capture "over USD 40/t ... sometimes more than USD 100/t" (p. 100); T&S assumption USD 20/t (p. 73); >half US onshore storage < USD 10/t (p. 114); SDS iron & steel: CCUS share of sector emission reductions 4 % 2030, 25 % 2050 (p. 47).
- DST (2025) *R&D Roadmap ... CCUS* (image PDF, pages read visually): p. xi "A desirable total cost of CCUS (say, not more than 5-10 Rs/kg of CO2 i.e., about 60-120 USD/ton-CO2)"; p. xiii Phase 1 (2025-2030) pilots, "Target capture cost should be aspirational i.e. <$40/t"; p. xiv Phase 2 (2030-2035): "Support pilot-scale CCS injection projects at selected storage sites (small, <30,000 t/y)", FEED for hubs ">500,000 t/y"; Phase 3 (2035-2045): "Develop two commercial scale CCS hubs (>1 Mt/y)"; p. xv outcome "Reduction in CO2 capture cost (< 40 $/ton)", storage hubs "in 3-4 regions".
- Union Budget 2026-27 speech, para 38 (p. 12): CCUS "outlay of ₹20,000 crore is proposed over the next 5 years" for power, steel, cement, refineries, chemicals.
- Not readable (paywalled / egress blocked): Bhardwaj, Seethamraju & Bandyopadhyay (2025) JCP 486:144505; Lau (2024) ACS SCE 10.1021/acssuschemeng.3c08088; Rathore (2025) ESD 10.1016/j.esd.2025.101866. Not used.
