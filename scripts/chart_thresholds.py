# Chart 10: results of the big-supplier screen at 20, 30, 40 and 50% (years 1996-2023 excluding 2013-16).
import pandas as pd, sys
sys.path.insert(0, 'scripts'); from charts_common import *
S = pd.read_csv('output/table_big_supplier_threshold_summary.csv')
S = S[S.years == 'excluding 2013-2016']
x = [20, 30, 40, 50]
fig, axs = plt.subplots(1, 3, figsize=(14, 4))
panels = [('flags', 'Number of big-supplier drops', ''),
          ('median_replaced_next_year_pct', 'Share of the loss made up by others\nby the next year (median)', '%'),
          ('median_total_imports_change_next_year_pct', 'Change in total UAE imports of the\nproduct by the next year (median)', '%')]
for ax, (col, title, unit) in zip(axs, panels):
    for i, typ in enumerate(['all drops', 'supplier-wide drops']):
        y = S[S.drops == typ].sort_values('threshold')[col].values
        ax.plot(x, y, marker='o', color=PAL[i], label=typ)
        ax.annotate(f'{y[-1]:.0f}{unit}', (50, y[-1]), xytext=(6, 0), textcoords='offset points', va='center', fontsize=8.5, color=INK)
    ax.set_xticks(x); ax.set_xticklabels([f'{v}%' for v in x]); ax.set_xlabel('Threshold for a "big" supplier (share of UAE imports)')
    ax.set_title(title, fontsize=10.5)
    if unit: ax.axhline(0, color=INK2, lw=0.8)
axs[0].legend(loc='upper right', fontsize=8.5)
fig.suptitle("At every threshold, other suppliers make up little of a big supplier's loss within a year",
             x=0.01, ha='left', fontsize=11.5, fontweight='bold', color=INK)
fig.tight_layout(rect=(0, 0.03, 1, 0.93))
save(fig, 'charts/10_big_supplier_thresholds.png', 'CEPII BACI HS92 annual, HS4, 1996-2023 excluding 2013-16. A drop: share down 15+ points and value down 33%+, product >= $30m. Big: share >= threshold in the year before and one of the two years before that.')
