# Figure 3. Car exports to the UAE around the March 2011 Japan earthquake, monthly.
# Data: UN Comtrade, monthly exports to the UAE reported by each supplier
#   (data/comtrade/comtrade_monthly_exports_to_uae_by_reporter.csv, HS 8703)
from _common import *
import matplotlib.dates as mdates

m = read('data/comtrade/comtrade_monthly_exports_to_uae_by_reporter.csv', dtype={'cmdCode': str})
c = m[m.cmdCode == '8703'].groupby(['reporterISO', 'month']).primaryValue.sum().unstack(0) / 1e6

jp = c['JPN']
pre, dur = jp.loc['2010-10':'2011-03'].mean(), jp.loc['2011-04':'2011-05'].mean()
us_pre, us_dur = c['USA'].loc['2010-10':'2011-03'].mean(), c['USA'].loc['2011-04':'2011-05'].mean()
print('Facts (slide 7):')
fact('Japan, cars to the UAE, monthly average Oct 2010-Mar 2011 (USD m)', pre)
fact('Japan, cars to the UAE, monthly average Apr-May 2011 (USD m)', dur)
fact('  change', 100 * (dur / pre - 1), '%')
fact('United States, same windows, change', 100 * (us_dur / us_pre - 1), '%')

c = c.loc['2010-06':'2012-06']
c.index = pd.to_datetime(c.index + '-15')   # plot each month at its middle
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.axvspan(pd.Timestamp('2011-04-01'), pd.Timestamp('2011-05-31'), color='#efece6', zorder=0)
for i, (s, lab) in enumerate([('JPN', 'Japan'), ('USA', 'United States'), ('GBR', 'United Kingdom'), ('THA', 'Thailand')]):
    ax.plot(c.index, c[s], color=PAL[i], lw=2.4 if s == 'JPN' else 1.6)
ax.set_ylim(0, 380)
end_labels(ax, [(c.index[-1] + pd.Timedelta(days=12), c[s].iloc[-1], lab) for s, lab in
                [('JPN', 'Japan'), ('USA', 'United States'), ('GBR', 'United Kingdom'), ('THA', 'Thailand')]])
ax.annotate(f'Japan: ${pre:.0f}m a month before,\n${dur:.0f}m in Apr-May 2011 ({100*(dur/pre-1):.0f}%)',
            (pd.Timestamp('2011-04-15'), jp['2011-04']), xytext=(pd.Timestamp('2010-09-01'), 320), fontsize=8.5, color=INK,
            arrowprops=dict(arrowstyle='-', color=INK2, lw=0.8))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
ax.set_ylabel('USD million per month')
ax.set_title('Car exports to the UAE around the March 2011 earthquake')
save(fig, 'fig3_japan_cars_2011.png', 'UN Comtrade, monthly exports to the UAE reported by each supplier, HS 8703. Shaded: Apr-May 2011. Korea is not in the monthly data before 2013.')
