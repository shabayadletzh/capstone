# Figure 5. Before the 2022 ban, how much each Gulf country relied on Indian wheat.
# Data: CEPII BACI, every supplier's exports of wheat to each Gulf country
#   (data/baci/baci_strategic_hs4_exports_by_exporter_to_world_and_gcc_1995_2024.csv, HS 1001)
from _common import *

g = read('data/baci/baci_strategic_hs4_exports_by_exporter_to_world_and_gcc_1995_2024.csv', dtype={'hs4': str})
g = g[(g.hs4 == '1001') & (g.year == 2021) & (g.destination != 'WLD')]
tot = g.groupby('destination').value_kusd.sum()
ind = g[g.exporter_iso3 == 'IND'].groupby('destination').value_kusd.sum().reindex(tot.index).fillna(0)
sh = (100 * ind / tot).sort_values()
names = {'ARE': 'UAE', 'SAU': 'Saudi Arabia', 'OMN': 'Oman', 'KWT': 'Kuwait', 'QAT': 'Qatar', 'BHR': 'Bahrain'}

print('Facts (slide 9):')
for d in ['ARE', 'SAU', 'OMN', 'KWT', 'QAT', 'BHR']:
    fact(f"India's share of {names[d]} wheat imports, 2021", sh[d], '%')

fig, ax = plt.subplots(figsize=(7.5, 3.6))
ax.barh([names[d] for d in sh.index], sh.values, color=[PAL[1] if d == 'ARE' else PAL[0] for d in sh.index])
for i, v in enumerate(sh.values):
    ax.text(v + 0.6, i, f'{v:.1f}%', va='center', fontsize=9, color=INK)
ax.set_xlim(0, 40); ax.set_xlabel("India's share of the country's wheat imports, 2021 (%)"); ax.grid(axis='y', visible=False)
ax.set_title('Before the ban, the UAE relied on Indian wheat far more than its neighbours')
save(fig, 'fig5_india_wheat_gulf.png', 'CEPII BACI HS92 V202601, wheat (HS 1001), 2021.')
