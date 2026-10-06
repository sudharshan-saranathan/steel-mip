"""Convert source capex figures to constant 2025 USD.

INR: inflate with India WPI (all commodities, base 2011-12, Office of the
Economic Adviser, calendar-year index), then convert at the 2025 average
INR/USD rate (FRED EXINUS).  USD: inflate with the US GDP deflator (FRED GDPDEF).
Run from this directory:  python3 convert_2025usd.py
"""
import csv, collections
import pandas as pd

def annual(series):
    d = collections.defaultdict(list)
    for row in list(csv.reader(open(f"{series}.csv")))[1:]:
        try:
            d[int(row[0][:4])].append(float(row[1]))
        except ValueError:
            pass
    return {y: sum(v) / len(v) for y, v in d.items()}

GDPDEF = annual("GDPDEF")
INRUSD = annual("EXINUS")
_w = pd.read_excel("wpi_cal.xls", header=None)
WPI = {int(str(k)[5:]): float(v) for k, v in zip(_w.iloc[0, 3:], _w.iloc[1, 3:])}

def usd(value, year):
    return value * GDPDEF[2025] / GDPDEF[year]

def inr(value, year):
    return value * WPI[2025] / WPI[year] / INRUSD[2025]

# IEA annualised capex -> overnight: annualised = overnight * CRF / utilisation
CRF_8_25 = 0.08 * 1.08**25 / (1.08**25 - 1)
iea_overnight = lambda a: a * 0.90 / CRF_8_25

ROWS = [
    ("BF-BOF  IEA 2020 full plant (low)",         usd(1000, 2019)),
    ("BF-BOF  IEA 2020 full plant (high)",        usd(1500, 2019)),
    ("BF-BOF  IEA 2020 from annualised (low)",    usd(iea_overnight(52), 2019)),
    ("BF-BOF  IEA 2020 from annualised (high)",   usd(iea_overnight(94), 2019)),
    ("BF-BOF  IECC 2026",                         800.0),
    ("BF-BOF  CEEW 2021 upper bound",             usd(1000, 2020)),
    ("BF-BOF  Tata KPO-II 2018 (brownfield)",     inr(23500e7 / 5e6, 2018)),
    ("BF-BOF  JSW Vijayanagar 2021 (brownfield, low)",  inr(20000e7 / 5e6, 2021)),
    ("BF-BOF  JSW Vijayanagar 2021 (brownfield, high)", inr(25000e7 / 5e6, 2021)),
    ("NG-DRI-EAF IEA 2020 (low)",                 usd(iea_overnight(53), 2019)),
    ("NG-DRI-EAF IEA 2020 (high)",                usd(iea_overnight(136), 2019)),
    ("H2-DRI-EAF IECC 2026",                      670.0),
    ("H2-DRI-EAF CEEW 2021 (IEA 2010 data)",      usd(228 + 127, 2010)),
    ("Scrap-EAF IEA 2020 (low)",                  usd(iea_overnight(34), 2019)),
    ("Scrap-EAF IEA 2020 (high)",                 usd(iea_overnight(58), 2019)),
]

if __name__ == "__main__":
    for name, v in ROWS:
        print(f"{name:<50s} {v:8.0f}  USD2025/t-capacity")
