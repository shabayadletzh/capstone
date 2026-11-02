# Definition of a "big" supplier and robustness across share thresholds.
# Agreed rule (Adilet and Sultan, 2 Nov 2026):
#   - Main definition of big: the supplier had at least 50% of UAE imports of the product.
#   - Candidate screen: 20%, so that weaker cases are seen too.
#   - Every result is shown at 20, 30, 40 and 50% so no conclusion rests on one number.
# Persistence (from Sultan's pre-registered rule): the share must reach the threshold in the year
# before the drop AND in at least one of the two years before that (2 of the 3 pre-years, including
# the last). This keeps one-year spikes out.
# Drop rules are unchanged from the switch screen: product >= $30m in the year before, share falls
# by 15 points or more, and the supplier's value falls by at least 33% (log change <= -0.4).
#
# Inputs: data/baci/baci_uae_imports_hs4_ALL_products_1995_2024.csv(.gz),
#         output/table_supplier_switch_screen_all_products.csv (for the supply-side type of each drop),
#         data/baci/baci_uae_imports_hs6_strategic_1995_2024.csv(.gz), ..._hs6_new_sectors_...
# Outputs: output/table_big_supplier_threshold_summary.csv
#          output/table_big_supplier_flags_by_threshold.csv
#          output/table_big_supplier_event_cases.csv
# Run from the repository root (after python3 scripts/unpack_raw.py).
import pandas as pd, numpy as np

TH = [0.2, 0.3, 0.4, 0.5]
a = pd.read_csv('data/baci/baci_uae_imports_hs4_ALL_products_1995_2024.csv', dtype={'hs4': str})
a = a[a.year <= 2023].groupby(['hs4', 'exporter_iso3', 'year'], as_index=False).value_kusd.sum()
p = a.pivot_table(index=['hs4', 'exporter_iso3'], columns='year', values='value_kusd', aggfunc='sum').fillna(0)
L = p.stack().rename('v').reset_index()
T = a.groupby(['hs4', 'year']).value_kusd.sum().rename('T').reset_index()
L = L.merge(T, on=['hs4', 'year'], how='left')
L['s'] = L.v / L['T']
L = L.sort_values(['hs4', 'exporter_iso3', 'year'])
g = L.groupby(['hs4', 'exporter_iso3'])
for k in (1, 2, 3):
    L[f's_l{k}'] = g.s.shift(k)
    L[f'T_l{k}'] = g['T'].shift(k)
L['v_l1'] = g.v.shift(1)
L['v_f1'] = g.v.shift(-1)
L['T_f1'] = g['T'].shift(-1)

base = L[(L.T_l1 >= 30000) & ((L.s - L.s_l1) <= -0.15) &
         ((np.log(L.v.clip(lower=1)) - np.log(L.v_l1.clip(lower=1))) <= -0.4)].copy()

scr = pd.read_csv('output/table_supplier_switch_screen_all_products.csv', dtype={'hs4': str})
scr = scr.rename(columns={'exporter': 'exporter_iso3'})[['year', 'hs4', 'exporter_iso3', 'product', 'type', 'who_gained']]
base = base.merge(scr, on=['year', 'hs4', 'exporter_iso3'], how='left')

# outcomes for each flag
base['lost'] = base.v_l1 - base.v                                   # loss from the big supplier, t vs t-1
base['others_gain_t'] = (base['T'] - base.v) - (base.T_l1 - base.v_l1)
base['others_gain_t1'] = (base.T_f1 - base.v_f1) - (base.T_l1 - base.v_l1)
base['replaced_t'] = base.others_gain_t / base.lost                  # share of the loss made up by others, same year
base['replaced_t1'] = base.others_gain_t1 / base.lost                # by the next year
base['total_change_t'] = base['T'] / base.T_l1 - 1
base['total_change_t1'] = base.T_f1 / base.T_l1 - 1

rows, flags = [], []
for th in TH:
    big = (base.s_l1 >= th) & ((base.s_l2 >= th) | (base.s_l3 >= th))
    f = base[big].copy()
    f['threshold'] = th
    flags.append(f)
    for label, sub in [('all years 1996-2023', f), ('excluding 2013-2016', f[~f.year.between(2013, 2016)])]:
        for typ, ss in [('all drops', sub), ('supplier-wide drops', sub[sub.type == 'supplier-wide drop'])]:
            if ss.empty: continue
            rows.append({'threshold': f'{int(th*100)}%', 'years': label, 'drops': typ, 'flags': len(ss),
                         'suppliers': ss.exporter_iso3.nunique(), 'products': ss.hs4.nunique(),
                         'lost_bn_usd': round(ss.lost.sum() / 1e6, 1),
                         'median_replaced_same_year_pct': round(ss.replaced_t.median() * 100),
                         'median_replaced_next_year_pct': round(ss.replaced_t1.median() * 100),
                         'share_fully_replaced_next_year_pct': round((ss.replaced_t1 >= 1).mean() * 100),
                         'median_total_imports_change_same_year_pct': round(ss.total_change_t.median() * 100),
                         'median_total_imports_change_next_year_pct': round(ss.total_change_t1.median() * 100)})
S = pd.DataFrame(rows)
S.to_csv('output/table_big_supplier_threshold_summary.csv', index=False)
F = pd.concat(flags)
F['threshold'] = (F.threshold * 100).astype(int).astype(str) + '%'
cols = ['threshold', 'year', 'hs4', 'product', 'exporter_iso3', 's_l3', 's_l2', 's_l1', 's', 'v_l1', 'v', 'lost',
        'replaced_t', 'replaced_t1', 'total_change_t', 'total_change_t1', 'type', 'who_gained']
F[cols].round(4).to_csv('output/table_big_supplier_flags_by_threshold.csv', index=False)

# where do the dated events fall?
# HS6: the supplier's strongest line among lines worth >= $30m in the last pre-year (chosen automatically).
# Wheat is shown twice: the ban came in May 2022, but contracted shipments ran to Aug 2022 and the
# annual drop is in 2023, so pre-years 2019-21 (strict) and 2020-22 (effective) are both reported.
EV = [('Japan earthquake 2011, cars', 'JPN', '8703', 2011),
      ('Japan earthquake 2011, trucks', 'JPN', '8704', 2011),
      ('Thailand floods 2011, trucks', 'THA', '8704', 2011),
      ('Iran sanctions 2012, polyethylene', 'IRN', '3901', 2012),
      ('Iran sanctions 2018-19, semi-finished steel', 'IRN', '7207', 2019),
      ('India wheat ban 2022 (pre-years before the ban)', 'IND', '1001', 2022),
      ('India wheat ban 2022 (pre-years before the annual drop)', 'IND', '1001', 2023),
      ('Indonesia palm oil ban 2022', 'IDN', '1511', 2022),
      ('Ukraine war 2022, sunflower oil', 'UKR', '1512', 2022),
      ('Ukraine war 2022, pig iron', 'UKR', '7201', 2022),
      ('India onion ban 2023-24', 'IND', '0703', 2023)]
h6 = pd.concat([pd.read_csv(f, dtype={'hs6': str, 'hs4': str}) for f in
                ['data/baci/baci_uae_imports_hs6_strategic_1995_2024.csv',
                 'data/baci/baci_uae_imports_hs6_new_sectors_1995_2024.csv']])
h6 = h6[h6.year <= 2023].groupby(['hs6', 'exporter_iso3', 'year']).value_kusd.sum().reset_index()


def shares(df, code_col, code, sup, years):
    d = df[(df[code_col] == code) & (df.year.isin(years))]
    tot = d.groupby('year').value_kusd.sum()
    own = d[d.exporter_iso3 == sup].groupby('year').value_kusd.sum()
    return [round(own.get(y, 0) / tot[y], 3) if y in tot else np.nan for y in years]


def passes(sh):
    if any(np.isnan(sh)): return '-'
    ok = [f'{int(t*100)}' for t in TH if sh[2] >= t and (sh[0] >= t or sh[1] >= t)]
    return ', '.join(ok) if ok else 'none'


h6['hs4'] = h6.hs6.str[:4]


def best_hs6(k4, sup, y):
    d = h6[(h6.hs4 == k4) & (h6.year == y)]
    if d.empty: return None, None
    tot = d.groupby('hs6').value_kusd.sum()
    own = d[d.exporter_iso3 == sup].groupby('hs6').value_kusd.sum().reindex(tot.index).fillna(0)
    sh = (own / tot)[tot >= 30000]
    if sh.empty: return None, None
    k = sh.idxmax()
    return k, tot[k] / 1e3


er = []
for name, sup, k4, yr in EV:
    k6, k6val = best_hs6(k4, sup, yr - 1)
    ys = [yr - 3, yr - 2, yr - 1]
    s4 = shares(a, 'hs4', k4, sup, ys)
    row = {'event': name, 'supplier': sup, 'pre_years': f'{ys[0]}-{ys[2]}', 'hs4': k4,
           'hs4_share_pre_years': ' / '.join(f'{x:.0%}' for x in s4), 'hs4_passes_at': passes(s4)}
    if k6:
        s6 = shares(h6, 'hs6', k6, sup, ys)
        row.update({'strongest_hs6': k6, 'hs6_imports_last_pre_year_musd': round(k6val), 'hs6_share_pre_years': ' / '.join(f'{x:.0%}' for x in s6), 'hs6_passes_at': passes(s6)})
    er.append(row)
E = pd.DataFrame(er)
E.to_csv('output/table_big_supplier_event_cases.csv', index=False)

pd.set_option('display.width', 250, 'display.max_columns', 20)
print(S.to_string(index=False))
print()
print(E.to_string(index=False))
