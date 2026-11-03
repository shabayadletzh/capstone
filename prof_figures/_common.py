# Shared bits for the figure scripts: paths, file reading, chart style, printing facts.
import os, sys, gzip, io
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'prof_figures', 'png')
os.makedirs(OUT, exist_ok=True)

PAL = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#6250d6']
GREY, INK, INK2, GRID, BG = '#b5b3ad', '#0b0b0b', '#52514e', '#e6e4df', '#fcfcfb'
plt.rcParams.update({'figure.facecolor': BG, 'axes.facecolor': BG, 'axes.edgecolor': GRID, 'axes.grid': True,
                     'grid.color': GRID, 'axes.spines.top': False, 'axes.spines.right': False, 'font.size': 10,
                     'axes.titlesize': 11, 'axes.titleweight': 'bold', 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'legend.frameon': False, 'lines.linewidth': 2})


def path(rel):
    """Return the .csv if it exists, otherwise the .csv.gz next to it (pandas reads both)."""
    p = os.path.join(ROOT, rel)
    if os.path.exists(p):
        return p
    if os.path.exists(p + '.gz'):
        return p + '.gz'
    raise FileNotFoundError(rel)


def read(rel, **kw):
    return pd.read_csv(path(rel), low_memory=False, **kw)


def read_text(rel):
    p = path(rel)
    if p.endswith('.gz'):
        with gzip.open(p, 'rt', encoding='utf-8', errors='replace') as f:
            return f.read()
    with open(p, encoding='utf-8', errors='replace') as f:
        return f.read()


def share(df, code, sup, year, col='hs4'):
    """Supplier's share (%) of UAE imports of one product in one year (BACI files)."""
    d = df[(df[col] == code) & (df.year == year)]
    return 100 * d.loc[d.exporter_iso3 == sup, 'value_kusd'].sum() / d.value_kusd.sum()


def fact(label, value, unit=''):
    print(f'  {label:72s} {value:10.2f} {unit}')


def save(fig, name, source):
    fig.text(0.01, -0.45 / fig.get_size_inches()[1], 'Source: ' + source, fontsize=7.5, color=INK2, ha='left', va='bottom')
    fig.savefig(os.path.join(OUT, name), dpi=170, bbox_inches='tight')
    plt.close(fig)
    print(f'  saved prof_figures/png/{name}')


def end_labels(ax, items, gap_frac=0.06):
    """Label line ends, pushing labels apart so they don't overlap. items: (x, y, text)."""
    lo, hi = ax.get_ylim(); gap = (hi - lo) * gap_frac
    items = sorted(items, key=lambda t: t[1]); ys = []
    for x, y, t in items:
        ys.append(max(y, ys[-1] + gap) if ys else y)
    for (x, y, t), yy in zip(items, ys):
        ax.annotate(t, (x, y), xytext=(x, yy), textcoords='data', va='center', fontsize=8.5, color=INK,
                    annotation_clip=False)
