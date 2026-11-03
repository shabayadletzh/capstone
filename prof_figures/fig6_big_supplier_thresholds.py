# Figure 6. What happens after a big supplier's sales to the UAE drop, at 20, 30, 40 and 50%.
# Data: CEPII BACI, UAE imports of every product by supplier (data/baci/baci_uae_imports_hs4_ALL_products_1995_2024.csv)
#       and the switch screen, for whether the supplier's exports fell everywhere
#       (output/table_supplier_switch_screen_all_products.csv)
# Rules (agreed 2 Nov 2026):
#   Big:  share >= threshold in the year before the drop and in at least one of the two years before that.
#   Drop: product worth >= USD 30m the year before, share down >= 15 points, value down >= a third (log <= -0.4).
from _common import *
import numpy as np

a = read('data/baci/baci_uae_imports_hs4_ALL_products_1995_2024.csv', dtype={'hs4': str})
a = a[a.year <= 2023].groupby(['hs4', 'exporter_iso3', 'year'], as_index=False).value_kusd.sum()
p = a.pivot_table(index=['hs4', 'exporter_iso3'], columns='year', values='value_kusd', aggfunc='sum').fillna(0)
P = p.stack().rename('v').reset_index()                                     # every pair in every year, 0 if no trade
P = P.merge(a.groupby(['hs4', 'year']).value_kusd.sum().rename('T').reset_index(), on=['hs4', 'year'], how='left')
P['s'] = P.v / P['T']
P = P.sort_values(['hs4', 'exporter_iso3', 'year'])
g = P.groupby(['hs4', 'exporter_iso3'])
for k in (1, 2, 3):
    P[f's_l{k}'] = g.s.shift(k)
P['T_l1'], P['v_l1'], P['v_f1'], P['T_f1'] = g['T'].shift(1), g.v.shift(1), g.v.shift(-1), g['T'].shift(-1)

big50 = (P.s >= 0.5) & ((P.s_l1 >= 0.5) | (P.s_l2 >= 0.5))
D = P[(P.T_l1 >= 30000) & ((P.s - P.s_l1) <= -0.15) &
      ((np.log(P.v.clip(lower=1)) - np.log(P.v_l1.clip(lower=1))) <= -0.4)].copy()
scr = read('output/table_supplier_switch_screen_all_products.csv', dtype={'hs4': str}).rename(columns={'exporter': 'exporter_iso3'})
D = D.merge(scr[['year', 'hs4', 'exporter_iso3', 'type']], on=['year', 'hs4', 'exporter_iso3'], how='left')
D['replaced_next_year'] = ((D.T_f1 - D.v_f1) - (D.T_l1 - D.v_l1)) / (D.v_l1 - D.v)
D['total_change_next_year'] = D.T_f1 / D.T_l1 - 1
D = D[~D.year.between(2013, 2016)]          # years the UAE booked a third of imports as "unspecified"

print('Facts (slide 7):')
fact('Products (HS4) in the data, 1995-2023', P.hs4.nunique())
fact('Products that had a big supplier (50%, 2 of 3 years) at least once', P[big50].hs4.nunique())
rows = []
for th in (20, 30, 40, 50):
    t = th / 100
    f = D[(D.s_l1 >= t) & ((D.s_l2 >= t) | (D.s_l3 >= t))]
    w = f[f.type == 'supplier-wide drop']
    rows.append(dict(th=th, n=len(f), nw=len(w), ra=100 * f.replaced_next_year.median(), rw=100 * w.replaced_next_year.median(),
                     ta=100 * f.total_change_next_year.median(), tw=100 * w.total_change_next_year.median()))
    print(f'  Threshold {th}%')
    fact('    drops (1996-2023, excluding 2013-16)', len(f))
    fact('    of which the supplier sold less everywhere (supplier-wide)', len(w))
    fact('    median share of the loss made up by others by next year, all drops', rows[-1]['ra'], '%')
    fact('    same, supplier-wide drops', rows[-1]['rw'], '%')
    fact('    median change in total UAE imports by next year, all drops', rows[-1]['ta'], '%')
    fact('    same, supplier-wide drops', rows[-1]['tw'], '%')
R = pd.DataFrame(rows)

fig, axs = plt.subplots(1, 3, figsize=(14, 4))
x = R.th
for ax, (ca, cw, title, unit) in zip(axs, [('n', 'nw', 'Number of big-supplier drops', ''),
                                           ('ra', 'rw', 'Share of the loss made up by others\nby the next year (median)', '%'),
                                           ('ta', 'tw', 'Change in total UAE imports of the\nproduct by the next year (median)', '%')]):
    ax.plot(x, R[ca], marker='o', color=PAL[0], label='All drops')
    ax.plot(x, R[cw], marker='o', color=PAL[1], label='Supplier sold less everywhere')
    for col in (ca, cw):
        ax.annotate(f'{R[col].iloc[-1]:.0f}{unit}', (50, R[col].iloc[-1]), xytext=(6, 0), textcoords='offset points', va='center', fontsize=8.5)
    ax.set_xticks(x); ax.set_xticklabels([f'{v}%' for v in x]); ax.set_xlabel('Threshold for a big supplier')
    ax.set_title(title, fontsize=10.5)
    if unit:
        ax.axhline(0, color=INK2, lw=0.8)
axs[0].legend(fontsize=8.5)
fig.suptitle("At every threshold, other suppliers make up little of a big supplier's loss within a year", x=0.01, ha='left', fontweight='bold', color=INK)
fig.tight_layout(rect=(0, 0.04, 1, 0.93))
save(fig, 'fig6_big_supplier_thresholds.png', 'CEPII BACI HS92, HS4, 1996-2023 excluding 2013-16. Drop: share down 15+ points, value down a third or more, product >= USD 30m.')
