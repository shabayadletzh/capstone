# Figure 7. US share of UAE arms deliveries and new orders.
# Data: SIPRI Arms Transfers Database
#   - deliveries by year: data/sipri/sipri_uae_arms_imports_deliveries_by_year.csv
#   - orders (register):  raw/sipri_register_uae.txt(.gz). Only deals with at least one delivery by 2025
#     are in this download, so recent orders not yet delivered are missing.
# SIPRI TIV is a volume index, not money.
from _common import *

d = read('data/sipri/sipri_uae_arms_imports_deliveries_by_year.csv')
d['tiv'] = pd.to_numeric(d['TIV delivery values'], errors='coerce')
d['period'] = ((d['Delivery year'] - 2001) // 5 * 5 + 2001).astype('Int64')         # 2001-05, 2006-10, ...
dp = d[d.period.between(2001, 2021)].groupby('period').apply(
    lambda z: 100 * z.loc[z.Supplier == 'United States', 'tiv'].sum() / z.tiv.sum())

lines = read_text('raw/sipri_register_uae.txt').splitlines()
o = pd.DataFrame([l.split('\t') for l in lines if l.startswith('United Arab Emirates\t')])
o = pd.DataFrame({'supplier': o[1], 'year': pd.to_numeric(o[2], errors='coerce'), 'tiv': pd.to_numeric(o[14], errors='coerce')})


def us_order_share(a, b):
    z = o[o.year.between(a, b)]
    return 100 * z.loc[z.supplier == 'United States', 'tiv'].sum() / z.tiv.sum()


print('Facts (slide 7):')
for p0 in (2006, 2011, 2016):
    fact(f'US share of UAE arms deliveries, {p0}-{p0+4}', dp[p0], '%')
fact('US share of UAE arms orders (TIV of the whole order), 2016-2020', us_order_share(2016, 2020), '%')
fact('US share of UAE arms orders, 2021', us_order_share(2021, 2021), '%')

fig, ax = plt.subplots(figsize=(7.5, 3.8))
labels = [f'{int(p)}-{str(int(p)+4)[2:]}' for p in dp.index]
bars = ax.bar(labels, dp.values, color=PAL[0], width=0.6)
for b, v in zip(bars, dp.values):
    ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f'{v:.0f}%', ha='center', fontsize=9, color=INK)
ax.set_ylim(0, 100); ax.set_ylabel('US share of deliveries (%)'); ax.grid(axis='x', visible=False)
ax.set_title('US share of major arms deliveries to the UAE, by 5-year period')
save(fig, 'fig7_sipri_arms.png', 'SIPRI Arms Transfers Database, trend-indicator values (a volume index, not money). 2021-25 is partial for recent orders.')
