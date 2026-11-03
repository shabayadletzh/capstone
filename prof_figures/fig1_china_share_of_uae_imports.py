# Figure 1. China's share of all UAE goods imports, 1995-2023.
# Data: CEPII BACI, UAE imports by supplier and HS2 chapter (data/baci/baci_uae_imports_hs2_all_1995_2024.csv)
from _common import *

h2 = read('data/baci/baci_uae_imports_hs2_all_1995_2024.csv')
h2 = h2[h2.year <= 2023]
tot = h2.groupby('year').value_kusd.sum()
chn = h2[h2.exporter_iso3 == 'CHN'].groupby('year').value_kusd.sum()
ind = h2[h2.exporter_iso3 == 'IND'].groupby('year').value_kusd.sum()
s_chn, s_ind = 100 * chn / tot, 100 * ind / tot

print('Facts (slide 3):')
fact('UAE goods imports, 2023 (USD bn)', tot[2023] / 1e6)
fact("China's share of UAE goods imports, average 1995-1999", s_chn.loc[1995:1999].mean(), '%')
fact("China's share of UAE goods imports, 2023", s_chn[2023], '%')
fact("India's share of UAE goods imports, 2023", s_ind[2023], '%')

fig, ax = plt.subplots(figsize=(8.5, 4.2))
ax.plot(s_chn.index, s_chn.values, color=PAL[0], marker='o', ms=3)
ax.plot(s_ind.index, s_ind.values, color=PAL[1], marker='o', ms=3)
ax.annotate(f'China {s_chn[2023]:.0f}%', (2023, s_chn[2023]), xytext=(6, 0), textcoords='offset points', va='center', color=INK)
ax.annotate(f'India {s_ind[2023]:.0f}%', (2023, s_ind[2023]), xytext=(6, 0), textcoords='offset points', va='center', color=INK)
ax.set_xlim(1995, 2026); ax.set_ylim(0, 25); ax.set_ylabel('% of all UAE goods imports')
ax.set_title("China's share of UAE goods imports went from about 5% to 20%")
save(fig, 'fig1_china_share_of_uae_imports.png', 'CEPII BACI HS92 V202601, UAE imports from all suppliers, 1995-2023.')
