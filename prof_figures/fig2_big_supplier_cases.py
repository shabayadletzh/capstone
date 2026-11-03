# Figure 2. The big supplier's share of UAE imports over time, for the cases on the slides.
# Data: CEPII BACI, UAE imports by supplier and product
#   - data/baci/baci_uae_imports_hs4_strategic_1995_2024.csv   (computers, phones, wheat, sunflower oil)
#   - data/baci/baci_uae_imports_hs6_strategic_1995_2024.csv   (Japan's truck line 870422)
#   - data/baci/baci_uae_imports_hs4_ALL_products_1995_2024.csv (Iran's semi-finished steel 7207)
from _common import *

h4 = read('data/baci/baci_uae_imports_hs4_strategic_1995_2024.csv', dtype={'hs4': str})
h6 = read('data/baci/baci_uae_imports_hs6_strategic_1995_2024.csv', dtype={'hs6': str, 'hs4': str})
al = read('data/baci/baci_uae_imports_hs4_ALL_products_1995_2024.csv', dtype={'hs4': str})

print('Facts (slides 2, 3 and 7):')
x = h4[h4.year == 2023].groupby(['hs4', 'exporter_iso3']).value_kusd.sum().reset_index()
x['s'] = x.value_kusd / x.groupby('hs4').value_kusd.transform('sum')
top = x.groupby('hs4').s.max()
fact('Strategic products with UAE imports in 2023', len(top))
fact('  of which the top supplier has more than 50%', (top > 0.5).sum())
fact('China, computers (8471), 2023', share(h4, '8471', 'CHN', 2023), '%')
fact('China, phones (8525 in HS92), 2019', share(h4, '8525', 'CHN', 2019), '%')
fact('China, phones (8525 in HS92), 2023', share(h4, '8525', 'CHN', 2023), '%')
fact('Japan, trucks 870422, 2009', share(h6, '870422', 'JPN', 2009, 'hs6'), '%')
fact('Japan, trucks 870422, 2010', share(h6, '870422', 'JPN', 2010, 'hs6'), '%')
fact('Iran, semi-finished steel 7207, 2018', share(al, '7207', 'IRN', 2018), '%')
fact('Iran, semi-finished steel 7207, 2019', share(al, '7207', 'IRN', 2019), '%')
fact('India, wheat 1001, 2021', share(h4, '1001', 'IND', 2021), '%')
fact('India, wheat 1001, 2022', share(h4, '1001', 'IND', 2022), '%')
fact('India, wheat 1001, 2023', share(h4, '1001', 'IND', 2023), '%')
fact('Russia, wheat 1001, 2022', share(h4, '1001', 'RUS', 2022), '%')
fact('Russia, wheat 1001, 2023', share(h4, '1001', 'RUS', 2023), '%')
fact('Ukraine, sunflower oil 1512, 2021', share(h4, '1512', 'UKR', 2021), '%')
fact('Ukraine, sunflower oil 1512, 2022', share(h4, '1512', 'UKR', 2022), '%')

CASES = [(h4, 'hs4', '8471', 'CHN', 'China, computers (8471)', 2020),
         (h4, 'hs4', '8525', 'CHN', 'China, phones (8525)', 2020),
         (h6, 'hs6', '870422', 'JPN', 'Japan, trucks (870422)', 2011),
         (al, 'hs4', '7207', 'IRN', 'Iran, semi-finished steel (7207)', 2019),
         (h4, 'hs4', '1001', 'IND', 'India, wheat (1001)', 2022),
         (h4, 'hs4', '1512', 'UKR', 'Ukraine, sunflower oil (1512)', 2022)]
fig, axs = plt.subplots(2, 3, figsize=(13, 6.6), sharey=True)
for ax, (df, col, code, sup, title, shock) in zip(axs.ravel(), CASES):
    d = df[(df[col] == code) & (df.year <= 2023)]
    tot = d.groupby('year').value_kusd.sum()
    own = d[d.exporter_iso3 == sup].groupby('year').value_kusd.sum().reindex(tot.index).fillna(0)
    sh = 100 * own / tot
    ax.axvspan(shock - 0.5, shock + 0.5, color='#efece6', zorder=0)
    ax.axhline(50, color=GREY, lw=1, ls='--')
    ax.plot(sh.index, sh.values, color=PAL[0], marker='o', ms=2.5)
    ax.set_title(title, fontsize=10); ax.set_ylim(0, 100); ax.set_xlim(1995, 2024)
for ax in axs[:, 0]:
    ax.set_ylabel('% of UAE imports')
fig.suptitle("The big supplier's share of UAE imports (shaded: shock year, dashed: 50%)", x=0.01, ha='left', fontweight='bold', color=INK)
fig.tight_layout(rect=(0, 0.03, 1, 0.96))
save(fig, 'fig2_big_supplier_cases.png', 'CEPII BACI HS92 V202601. Trucks at HS6, the rest at HS4. 1995-2023.')
