# Python mirror of stata/facts_and_figures.do.
# Same files, same definitions. Use it to check the Stata numbers line by line.
# Run from the repository root after: python3 scripts/unpack_raw.py
#   python3 stata/verify_facts.py      -> writes stata/expected_facts.csv
import pandas as pd, numpy as np
R = []
def fact(fid, label, value, unit=''):
    R.append({'id': fid, 'fact': label, 'value': round(float(value), 2) if value == value else None, 'unit': unit})
    print(f'{fid:9s} {label:75s} {value:10.2f} {unit}')

def shares(df, code, sup, years, col='hs4'):
    g = df[(df[col] == code) & df.year.isin(years)]
    t = g.groupby('year').value_kusd.sum()
    o = g[g.exporter_iso3 == sup].groupby('year').value_kusd.sum()
    return (o / t * 100).reindex(years).fillna(0)

# ---------- BACI, strategic HS4 ----------
h4 = pd.read_csv('data/baci/baci_uae_imports_hs4_strategic_1995_2024.csv', dtype={'hs4': str})
x = h4[h4.year == 2023].groupby(['hs4', 'exporter_iso3']).value_kusd.sum().reset_index()
x['s'] = x.value_kusd / x.groupby('hs4').value_kusd.transform('sum')
top = x.groupby('hs4').s.max()
fact('F01a', 'Strategic HS4 products with UAE imports in 2023', len(top))
fact('F01b', 'Of which top supplier has more than 50% (2023)', (top > 0.5).sum())
fact('F02', 'China share of UAE computer imports (8471), 2023', shares(h4, '8471', 'CHN', [2023])[2023], '%')
s = shares(h4, '8525', 'CHN', [2019, 2023])
fact('F04a', 'China share of UAE phone imports (8525 in HS92), 2019', s[2019], '%')
fact('F04b', 'China share of UAE phone imports (8525 in HS92), 2023', s[2023], '%')
s = shares(h4, '1001', 'IND', [2021, 2022, 2023])
fact('F09a', 'India share of UAE wheat imports (1001), 2021', s[2021], '%')
fact('F09b', 'India share of UAE wheat imports (1001), 2022', s[2022], '%')
fact('F09c', 'India share of UAE wheat imports (1001), 2023', s[2023], '%')
s = shares(h4, '1001', 'RUS', [2022, 2023])
fact('F09d', 'Russia share of UAE wheat imports, 2022', s[2022], '%')
fact('F09e', 'Russia share of UAE wheat imports, 2023', s[2023], '%')
s = shares(h4, '1512', 'UKR', [2021, 2022])
fact('F10a', 'Ukraine share of UAE sunflower oil imports (1512), 2021', s[2021], '%')
fact('F10b', 'Ukraine share of UAE sunflower oil imports (1512), 2022', s[2022], '%')

# ---------- BACI, all goods by HS2 ----------
h2 = pd.read_csv('data/baci/baci_uae_imports_hs2_all_1995_2024.csv')
t = h2.groupby('year').value_kusd.sum(); c = h2[h2.exporter_iso3 == 'CHN'].groupby('year').value_kusd.sum()
sh = c / t * 100
fact('F03a', 'China share of all UAE goods imports, average 1995-1999', sh.loc[1995:1999].mean(), '%')
fact('F03b', 'China share of all UAE goods imports, 2023', sh[2023], '%')
fact('F03c', 'UAE goods imports, 2023', t[2023] / 1e6, 'USD bn')

# ---------- BACI, strategic HS6 ----------
h6 = pd.read_csv('data/baci/baci_uae_imports_hs6_strategic_1995_2024.csv', dtype={'hs6': str, 'hs4': str})
s = shares(h6, '870422', 'JPN', [2009, 2010], col='hs6')
fact('F05a', 'Japan share of UAE imports of trucks 870422, 2009', s[2009], '%')
fact('F05b', 'Japan share of UAE imports of trucks 870422, 2010', s[2010], '%')

# ---------- BACI, all HS4 ----------
a = pd.read_csv('data/baci/baci_uae_imports_hs4_ALL_products_1995_2024.csv', dtype={'hs4': str})
s = shares(a, '7207', 'IRN', [2018, 2019])
fact('F06a', 'Iran share of UAE semi-finished steel imports (7207), 2018', s[2018], '%')
fact('F06b', 'Iran share of UAE semi-finished steel imports (7207), 2019', s[2019], '%')

# ---------- BACI, exports to GCC: India's share of each Gulf importer's wheat, 2021 ----------
g = pd.read_csv('data/baci/baci_strategic_hs4_exports_by_exporter_to_world_and_gcc_1995_2024.csv', dtype={'hs4': str})
g = g[(g.hs4 == '1001') & (g.year == 2021) & (g.destination != 'WLD')]
tot = g.groupby('destination').value_kusd.sum(); ind = g[g.exporter_iso3 == 'IND'].groupby('destination').value_kusd.sum()
for d in ['ARE', 'SAU', 'OMN', 'KWT', 'QAT', 'BHR']:
    fact(f'F11{d}', f'India share of {d} wheat imports, 2021', ind.get(d, 0) / tot[d] * 100, '%')

# ---------- Comtrade monthly ----------
m = pd.read_csv('data/comtrade/comtrade_monthly_exports_to_uae_by_reporter.csv', dtype={'cmdCode': str})
j = m[(m.reporterISO == 'JPN') & (m.cmdCode == '8703')].groupby('month').primaryValue.sum()
pre = j.loc['2010-10':'2011-03'].mean(); dur = j.loc['2011-04':'2011-05'].mean()
fact('F07a', 'Japan car exports to UAE, monthly avg Oct 2010-Mar 2011', pre / 1e6, 'USD m')
fact('F07b', 'Japan car exports to UAE, monthly avg Apr-May 2011', dur / 1e6, 'USD m')
fact('F07c', 'Change', (dur / pre - 1) * 100, '%')
n = pd.read_csv('data/comtrade/comtrade_monthly_exports_to_uae_new_sectors_and_totals_2010_2026.csv', dtype={'cmdCode': str})
cs = n[(n.reporterISO == 'CHN') & (n.cmdCode == 'TOTAL')].groupby('month').primaryValue.sum()
def febratio(y):
    nb = [f'{y-1}-12', f'{y}-01', f'{y}-03', f'{y}-04']
    if f'{y}-02' not in cs or any(k not in cs for k in nb): return np.nan
    return cs[f'{y}-02'] / np.mean([cs[k] for k in nb])
fact('F08a', 'China exports to UAE, Feb 2020', cs['2020-02'] / 1e9, 'USD bn')
fact('F08b', 'Feb 2020 / avg of Dec, Jan, Mar, Apr', febratio(2020))
other = [r for r in (febratio(y) for y in range(2011, 2025) if y != 2020) if r == r]
fact('F08c', 'Same ratio in other years: lowest', min(other))
fact('F08d', 'Same ratio in other years: highest', max(other))
fact('F08e', 'Same ratio in other years: number of years', len(other))

# ---------- SIPRI ----------
sp = pd.read_csv('data/sipri/sipri_uae_arms_imports_deliveries_by_year.csv')
sp['tiv'] = pd.to_numeric(sp['TIV delivery values'], errors='coerce'); sp['yr'] = sp['Delivery year']
for a0, b0 in [(2006, 2010), (2011, 2015), (2016, 2020)]:
    z = sp[sp.yr.between(a0, b0)]
    fact(f'F13_{a0}', f'US share of UAE arms deliveries (TIV), {a0}-{b0}', z[z.Supplier == 'United States'].tiv.sum() / z.tiv.sum() * 100, '%')
L = open('raw/sipri_register_uae.txt', encoding='utf-8', errors='replace').read().splitlines()
o = pd.DataFrame([l.split('\t') for l in L if l.startswith('United Arab Emirates\t')])
o['sup'] = o[1]; o['oy'] = pd.to_numeric(o[2], errors='coerce'); o['tiv'] = pd.to_numeric(o[14], errors='coerce')   # column 15 of 16 = SIPRI TIV for total order
for a0, b0 in [(2016, 2020), (2021, 2021)]:
    z = o[o.oy.between(a0, b0)]
    fact(f'F13o_{a0}', f'US share of UAE arms orders (TIV of order), {a0}-{b0}', z[z.sup == 'United States'].tiv.sum() / z.tiv.sum() * 100, '%')

# ---------- Big-supplier screen (same rules as scripts/big_supplier_thresholds.py) ----------
b = a[a.year <= 2023].groupby(['hs4', 'exporter_iso3', 'year'], as_index=False).value_kusd.sum()
p = b.pivot_table(index=['hs4', 'exporter_iso3'], columns='year', values='value_kusd', aggfunc='sum').fillna(0)
P = p.stack().rename('v').reset_index()
T = b.groupby(['hs4', 'year']).value_kusd.sum().rename('T').reset_index()
P = P.merge(T, on=['hs4', 'year'], how='left'); P['s'] = P.v / P['T']
P = P.sort_values(['hs4', 'exporter_iso3', 'year']); gp = P.groupby(['hs4', 'exporter_iso3'])
for k in (1, 2, 3): P[f's_l{k}'] = gp.s.shift(k)
P['T_l1'] = gp['T'].shift(1); P['v_l1'] = gp.v.shift(1); P['v_f1'] = gp.v.shift(-1); P['T_f1'] = gp['T'].shift(-1)
big50 = (P.s >= 0.5) & ((P.s_l1 >= 0.5) | (P.s_l2 >= 0.5))
fact('F14', 'HS4 products with a big supplier (50%, 2 of 3 years) at least once', P[big50].hs4.nunique())
fact('F14b', 'HS4 products in the data', P.hs4.nunique())
D = P[(P.T_l1 >= 30000) & ((P.s - P.s_l1) <= -0.15) & ((np.log(P.v.clip(lower=1)) - np.log(P.v_l1.clip(lower=1))) <= -0.4)].copy()
scr = pd.read_csv('output/table_supplier_switch_screen_all_products.csv', dtype={'hs4': str}).rename(columns={'exporter': 'exporter_iso3'})
D = D.merge(scr[['year', 'hs4', 'exporter_iso3', 'type']], on=['year', 'hs4', 'exporter_iso3'], how='left')
D['repl1'] = ((D.T_f1 - D.v_f1) - (D.T_l1 - D.v_l1)) / (D.v_l1 - D.v)
D['tot1'] = D.T_f1 / D.T_l1 - 1
D = D[~D.year.between(2013, 2016)]
for th in (20, 30, 40, 50):
    f = D[(D.s_l1 >= th / 100) & ((D.s_l2 >= th / 100) | (D.s_l3 >= th / 100))]
    w = f[f.type == 'supplier-wide drop']
    fact(f'F12n{th}', f'Big-supplier drops at {th}% (1996-2023 excl. 2013-16)', len(f))
    fact(f'F12ra{th}', f'  median share of loss replaced by next year, all drops', f.repl1.median() * 100, '%')
    fact(f'F12ta{th}', f'  median change in total UAE imports by next year, all drops', f.tot1.median() * 100, '%')
    fact(f'F12w{th}', f'  of which supplier-wide', len(w))
    fact(f'F12r{th}', f'  median share of loss replaced by next year, supplier-wide', w.repl1.median() * 100, '%')
    fact(f'F12t{th}', f'  median change in total UAE imports by next year, supplier-wide', w.tot1.median() * 100, '%')

pd.DataFrame(R).to_csv('stata/expected_facts.csv', index=False)
print('\nWrote stata/expected_facts.csv')
