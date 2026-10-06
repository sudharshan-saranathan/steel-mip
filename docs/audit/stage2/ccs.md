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
