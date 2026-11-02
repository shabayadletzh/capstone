# First descriptive look at H2 (product type) and H3 (who replaces) using the big-supplier flags.
# Sample: flags from table_big_supplier_flags_by_threshold.csv, 1996-2023 excluding 2013-16.
# Output: output/table_hypotheses_first_look.csv
import pandas as pd, numpy as np
F = pd.read_csv('output/table_big_supplier_flags_by_threshold.csv', dtype={'hs4': str})
F = F[~F.year.between(2013, 2016)].copy()
ch = F.hs4.str[:2].astype(int)
F['product_group'] = np.select([ch <= 24, ch.between(25, 29) | ch.between(39, 40) | ch.between(72, 81),
                                ch.between(84, 93)],
                               ['food (HS 01-24)', 'fuels, metals, basic chemicals and plastics', 'machinery, vehicles, electronics'],
                               'other manufactures')
a = pd.read_csv('data/baci/baci_uae_imports_hs4_ALL_products_1995_2024.csv', dtype={'hs4': str})
a = a.groupby(['hs4', 'exporter_iso3', 'year']).value_kusd.sum()
tot = a.groupby(['hs4', 'year']).sum()
F['top_gainer'] = F.who_gained.str.split(' ').str[0]
F['top_gainer_share_prev'] = [a.get((h, c, y - 1), 0) / tot.get((h, y - 1), np.nan) if isinstance(c, str) else np.nan
                              for h, c, y in zip(F.hs4, F.top_gainer, F.year)]
rows = []
for th in ['20%', '30%', '40%', '50%']:
    for drops, d0 in [('all drops', F[F.threshold == th]), ('supplier-wide drops', F[(F.threshold == th) & (F.type == 'supplier-wide drop')])]:
        for grp, d in list(d0.groupby('product_group')) + [('all products', d0)]:
            g = d[d.top_gainer.notna()]
            rows.append({'threshold': th, 'drops': drops, 'product_group': grp, 'flags': len(d),
                         'median_replaced_next_year_pct': round(d.replaced_t1.median() * 100),
                         'top_gainer_already_supplied_pct': round((g.top_gainer_share_prev > 0).mean() * 100) if len(g) else None,
                         'top_gainer_median_prev_share_pct': round(g.top_gainer_share_prev.median() * 100, 1) if len(g) else None})
T = pd.DataFrame(rows)
T.to_csv('output/table_hypotheses_first_look.csv', index=False)
pd.set_option('display.width', 220)
print(T[(T.drops == 'supplier-wide drops')].to_string(index=False))
