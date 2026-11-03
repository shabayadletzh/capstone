# Figure 4. China's exports to the UAE in February 2020, against other suppliers and other Februaries.
# Data: UN Comtrade, monthly total exports to the UAE reported by each supplier
#   (data/comtrade/comtrade_monthly_exports_to_uae_new_sectors_and_totals_2010_2026.csv, cmdCode TOTAL)
from _common import *
import matplotlib.dates as mdates
import numpy as np

n = read('data/comtrade/comtrade_monthly_exports_to_uae_new_sectors_and_totals_2010_2026.csv', dtype={'cmdCode': str})
t = n[n.cmdCode == 'TOTAL'].groupby(['reporterISO', 'month']).primaryValue.sum().unstack(0) / 1e9
cn = t['CHN']


def feb_ratio(y):
    """February divided by the average of the two months on each side (Dec, Jan, Mar, Apr)."""
    nb = [f'{y-1}-12', f'{y}-01', f'{y}-03', f'{y}-04']
    if f'{y}-02' not in cn or any(k not in cn or np.isnan(cn[k]) for k in nb):
        return np.nan
    return cn[f'{y}-02'] / np.mean([cn[k] for k in nb])


r = {y: feb_ratio(y) for y in range(2011, 2025)}
other = [v for y, v in r.items() if y != 2020 and v == v]
print('Facts (slides 2 and 7):')
fact("China's exports to the UAE, Feb 2020 (USD bn)", cn['2020-02'])
fact('Feb 2020 / average of Dec, Jan, Mar, Apr', r[2020])
fact('  same ratio in other years: lowest', min(other))
fact('  same ratio in other years: highest', max(other))
fact('  number of other years', len(other))

z = t.loc['2019-01':'2021-12', ['CHN', 'IND', 'USA', 'DEU']]
z.index = pd.to_datetime(z.index + '-15')   # plot each month at its middle
fig, ax = plt.subplots(figsize=(9, 4.2))
for y in (2019, 2020, 2021):
    ax.axvspan(pd.Timestamp(f'{y}-02-01'), pd.Timestamp(f'{y}-02-28'), color='#efece6', zorder=0)
for i, (s, lab) in enumerate([('CHN', 'China'), ('IND', 'India'), ('USA', 'United States'), ('DEU', 'Germany')]):
    ax.plot(z.index, z[s], color=PAL[i], lw=2.4 if s == 'CHN' else 1.6)
ax.set_ylim(0, 5.6)
end_labels(ax, [(z.index[-1] + pd.Timedelta(days=12), z[s].iloc[-1], lab) for s, lab in
                [('CHN', 'China'), ('IND', 'India'), ('USA', 'United States'), ('DEU', 'Germany')]])
ax.annotate(f'Feb 2020: ${cn["2020-02"]:.1f}bn, {r[2020]:.2f} of the months around it\n(a normal February: {min(other):.2f} to {max(other):.2f})',
            (pd.Timestamp('2020-02-15'), cn['2020-02']), xytext=(pd.Timestamp('2020-04-15'), 4.6), fontsize=8.5, color=INK,
            arrowprops=dict(arrowstyle='-', color=INK2, lw=0.8))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
ax.set_ylabel('USD billion per month')
ax.set_title("China's exports to the UAE collapsed in February 2020 (shaded: Februaries)")
save(fig, 'fig4_china_feb2020.png', 'UN Comtrade, total monthly exports to the UAE reported by each supplier, 2019-2021.')
