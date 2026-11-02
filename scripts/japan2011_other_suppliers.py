# [Sultan's coding agent, 2 Nov 2026] New script. Not written by Adilet.
# Purpose: the Japan 2011 car case reports "US share 33% -> 55%" from Comtrade monthly reporters only.
# That group has no Korea (Comtrade monthly starts 2013) and no EU suppliers (they are in Eurostat, in euro).
# This script puts every supplier we can see side by side, in its own currency and source:
#   - Comtrade monthly reporters (USD), Oct 2010-Mar 2011 vs Apr-May 2011 (the windows in REPORT.md)
#   - Eurostat EU27+UK monthly exports (EUR), same windows
#   - BACI annual 2010 vs 2011 for every supplier, including Korea
# Output: output/table_japan2011_other_suppliers.csv
# Run from the repository root: python3 scripts/japan2011_other_suppliers.py
import pandas as pd

PRE, DUR = ("2010-10", "2011-03"), ("2011-04", "2011-05")
rows = []

ct = pd.read_csv("data/comtrade/comtrade_monthly_exports_to_uae_by_reporter.csv", dtype={"cmdCode": str})
c = ct[ct.cmdCode == "8703"].groupby(["reporterISO", "month"]).primaryValue.sum().unstack(fill_value=0)
for r in c.index:
    pre = c.loc[r, PRE[0]:PRE[1]].mean()
    dur = c.loc[r, DUR[0]:DUR[1]].mean()
    if pre > 1e6 or dur > 1e6:
        rows.append({"source": "Comtrade monthly (USD)", "supplier": r, "pre_monthly_m": pre / 1e6,
                     "shock_monthly_m": dur / 1e6, "change_pct": 100 * (dur / pre - 1) if pre else None})

eu = pd.read_csv("data/eurostat/eurostat_comext_monthly_exports_to_UAE_hs4_strategic.csv", dtype={"product": str})
e = eu[eu["product"] == "8703"].groupby(["reporter", "month"]).value_eur.sum().unstack(fill_value=0)
for r in e.index:
    pre = e.loc[r, PRE[0]:PRE[1]].mean()
    dur = e.loc[r, DUR[0]:DUR[1]].mean()
    if pre > 1e6 or dur > 1e6:
        rows.append({"source": "Eurostat monthly (EUR)", "supplier": r, "pre_monthly_m": pre / 1e6,
                     "shock_monthly_m": dur / 1e6, "change_pct": 100 * (dur / pre - 1) if pre else None})
tot_pre = e.loc[:, PRE[0]:PRE[1]].sum(axis=0).mean()
tot_dur = e.loc[:, DUR[0]:DUR[1]].sum(axis=0).mean()
rows.append({"source": "Eurostat monthly (EUR)", "supplier": "EU27+UK total", "pre_monthly_m": tot_pre / 1e6,
             "shock_monthly_m": tot_dur / 1e6, "change_pct": 100 * (tot_dur / tot_pre - 1)})

b = pd.read_csv("data/baci/baci_uae_imports_hs4_strategic_1995_2024.csv", dtype={"hs4": str})
a = b[(b.hs4 == "8703") & b.year.isin([2010, 2011])].pivot_table(index="exporter_iso3", columns="year",
                                                                    values="value_kusd", aggfunc="sum").fillna(0)
for r in a.index:
    if a.loc[r, 2010] > 20000 or a.loc[r, 2011] > 20000:
        rows.append({"source": "BACI annual 2010 vs 2011 (USD)", "supplier": r, "pre_monthly_m": a.loc[r, 2010] / 1e3,
                     "shock_monthly_m": a.loc[r, 2011] / 1e3,
                     "change_pct": 100 * (a.loc[r, 2011] / a.loc[r, 2010] - 1) if a.loc[r, 2010] else None})

t = pd.DataFrame(rows).round(2)
t = t.rename(columns={"pre_monthly_m": "pre_m (monthly mean; BACI: 2010 total)",
                      "shock_monthly_m": "shock_m (monthly mean; BACI: 2011 total)"})
t.to_csv("output/table_japan2011_other_suppliers.csv", index=False)
pd.set_option("display.width", 200)
print(t.to_string(index=False))
