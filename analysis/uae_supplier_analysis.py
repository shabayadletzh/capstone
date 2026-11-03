"""
UAE import dependence and supplier replacement: data analysis
NYUAD Economics Capstone 2026-27 (Adilet and Sultan, supervisor Prof. Jean Imbs)

What this script does
    1. Loads the datasets we downloaded (CEPII BACI, UN Comtrade, SIPRI) and checks them
    2. Measures how dependent the UAE is on single suppliers
    3. Looks at the dated shocks (Japan 2011, China Feb 2020, India wheat 2022, ...)
    4. Runs the big-supplier screen at 20/30/40/50% and measures replacement
    5. Prints every number we quote and draws the figures and tables

Run it top to bottom, or cell by cell (# %%) in VS Code / Spyder / Jupyter.
Figures are saved to <data folder>/figures and also shown on screen.
"""

# %% 0. Setup ------------------------------------------------------------------
import gzip
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DATA_DIR = Path(r"C:\Users\shaba\Downloads\UAE_trade_data")
if not DATA_DIR.exists():                     # e.g. running from the GitHub copy
    DATA_DIR = Path(__file__).resolve().parents[1]

BACI = DATA_DIR / "data" / "baci"
COMTRADE = DATA_DIR / "data" / "comtrade"
SIPRI = DATA_DIR / "data" / "sipri"
RAW = DATA_DIR / "raw"
FIG_DIR = DATA_DIR / "figures"
FIG_DIR.mkdir(exist_ok=True)

SHOW = True          # set to False to only save the figures

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6"]
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "axes.grid": True,
    "grid.color": "#e6e4df", "axes.edgecolor": "#cccccc", "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 10, "axes.titlesize": 11,
    "axes.titleweight": "bold", "legend.frameon": False, "lines.linewidth": 2,
})

GULF = ["ARE", "SAU", "OMN", "KWT", "QAT", "BHR"]
GULF_NAMES = {"ARE": "UAE", "SAU": "Saudi Arabia", "OMN": "Oman",
              "KWT": "Kuwait", "QAT": "Qatar", "BHR": "Bahrain"}

FACTS = []           # every number we quote ends up here (section 11)


def fact(label, value, unit="", source=""):
    """Print a number and keep it for the summary table at the end."""
    FACTS.append({"fact": label, "value": value, "unit": unit, "source": source})
    print(f"  {label:<70} {value:>10,.2f} {unit}")


def finish(fig, name, source):
    """Add the source line, save the figure, show it."""
    fig.text(0.01, -0.45 / fig.get_size_inches()[1], "Source: " + source,
             fontsize=7.5, color="#52514e", ha="left", va="bottom")
    fig.savefig(FIG_DIR / name, dpi=170, bbox_inches="tight")
    if SHOW:
        plt.show()
    plt.close(fig)


def show_table(df, title, name, col_widths=None, fontsize=9):
    """Draw a DataFrame as a matplotlib table (for slides) and save it."""
    n_rows, n_cols = df.shape
    fig, ax = plt.subplots(figsize=(min(2.2 * n_cols + 1.5, 15), 0.38 * n_rows + 1.1))
    ax.axis("off")
    tab = ax.table(cellText=df.values, colLabels=df.columns, loc="center",
                   cellLoc="left", colLoc="left", colWidths=col_widths)
    tab.auto_set_font_size(False)
    tab.set_fontsize(fontsize)
    tab.scale(1, 1.35)
    for (r, c), cell in tab.get_celld().items():
        cell.set_edgecolor("#dddddd")
        if r == 0:
            cell.set_facecolor("#13232f")
            cell.set_text_props(color="white", weight="bold")
        elif r % 2 == 0:
            cell.set_facecolor("#f4f2ee")
    ax.set_title(title, fontweight="bold", loc="left")
    fig.savefig(FIG_DIR / name, dpi=170, bbox_inches="tight")
    if SHOW:
        plt.show()
    plt.close(fig)


def supplier_share(df, code, supplier, year, code_col="hs4"):
    """Share (%) of one supplier in UAE imports of one product in one year."""
    d = df[(df[code_col] == code) & (df["year"] == year)]
    total = d["value_kusd"].to_numpy().sum()
    own = d.loc[d["exporter_iso3"] == supplier, "value_kusd"].to_numpy().sum()
    return 100 * own / total


# %% 1. Load the data ------------------------------------------------------------
print("\n=== 1. Loading datasets ===")

baci_hs2 = pd.read_csv(BACI / "baci_uae_imports_hs2_all_1995_2024.csv")
baci_hs4 = pd.read_csv(BACI / "baci_uae_imports_hs4_strategic_1995_2024.csv", dtype={"hs4": str})
baci_hs6 = pd.read_csv(BACI / "baci_uae_imports_hs6_strategic_1995_2024.csv.gz", dtype={"hs4": str, "hs6": str})
baci_all = pd.read_csv(BACI / "baci_uae_imports_hs4_ALL_products_1995_2024.csv.gz", dtype={"hs4": str})
baci_gcc = pd.read_csv(BACI / "baci_strategic_hs4_exports_by_exporter_to_world_and_gcc_1995_2024.csv", dtype={"hs4": str})
baci_world = pd.read_csv(BACI / "baci_switch_flagged_pairs_exports_to_world_and_gcc_1995_2024.csv", dtype={"hs4": str})
ct_month = pd.read_csv(COMTRADE / "comtrade_monthly_exports_to_uae_by_reporter.csv", dtype={"cmdCode": str})
ct_totals = pd.read_csv(COMTRADE / "comtrade_monthly_exports_to_uae_new_sectors_and_totals_2010_2026.csv", dtype={"cmdCode": str})
ct_reported = pd.read_csv(COMTRADE / "comtrade_uae_reported_imports_total_by_partner_annual.csv")
sipri = pd.read_csv(SIPRI / "sipri_uae_arms_imports_deliveries_by_year.csv")
with gzip.open(RAW / "sipri_register_uae.txt.gz", "rt", encoding="utf-8", errors="replace") as f:
    sipri_register = f.read().splitlines()

# product codes are text: keep the leading zeros (0207, 0703, ...)
for d in (baci_hs4, baci_all, baci_gcc, baci_world):
    d["hs4"] = d["hs4"].str.zfill(4)

datasets = {
    "BACI, all goods by HS2": (baci_hs2, "year"),
    "BACI, strategic products, HS4": (baci_hs4, "year"),
    "BACI, strategic products, HS6": (baci_hs6, "year"),
    "BACI, every product, HS4": (baci_all, "year"),
    "BACI, exports to the Gulf and world": (baci_gcc, "year"),
    "Comtrade, monthly exports to the UAE": (ct_month, "month"),
    "Comtrade, monthly totals to the UAE": (ct_totals, "month"),
    "Comtrade, UAE-reported annual totals": (ct_reported, "period"),
    "SIPRI, arms deliveries by year": (sipri, "Delivery year"),
}
overview = pd.DataFrame([{
    "Dataset": name,
    "Rows": f"{len(d):,}",
    "Columns": d.shape[1],
    "From": str(d[t].min()).replace(".0", ""),
    "To": str(d[t].max()).replace(".0", ""),
    "Missing cells (%)": f"{100 * d.isna().to_numpy().mean():.1f}",
} for name, (d, t) in datasets.items()])
print(overview.to_string(index=False))
show_table(overview, "Table 1. Datasets used", "table1_datasets.png",
           col_widths=[0.34, 0.12, 0.09, 0.1, 0.1, 0.15])

print("\nFirst rows of the main annual dataset (BACI, strategic HS4):")
print(baci_hs4.head())


# %% 2. Is the data reliable? BACI against the UAE's own customs totals ----------
print("\n=== 2. Reliability: BACI vs UAE-reported totals ===")
baci_tot = baci_hs2.groupby("year")["value_kusd"].sum() / 1e6                     # USD bn
uae_tot = ct_reported[ct_reported["partnerISO"] == "W00"].set_index("period")["primaryValue"] / 1e9
rel = pd.DataFrame({"BACI (USD bn)": baci_tot, "UAE-reported (USD bn)": uae_tot}).dropna()
rel["Ratio"] = rel["BACI (USD bn)"] / rel["UAE-reported (USD bn)"]
print(rel.round(2).to_string())
within10 = np.abs(rel["Ratio"].to_numpy() - 1) <= 0.10
fact("Years where BACI is within 10% of UAE-reported total", within10.sum(), f"of {len(rel)}", "BACI, Comtrade")
fact("BACI / UAE-reported, average 2013-2016", rel.loc[2013:2016, "Ratio"].mean(), "", "BACI, Comtrade")

fig, ax = plt.subplots(figsize=(8.5, 3.8))
ax.plot(rel.index, rel["BACI (USD bn)"], color=COLORS[0], marker="o", ms=3, label="BACI (reconciled)")
ax.plot(rel.index, rel["UAE-reported (USD bn)"], color=COLORS[1], marker="o", ms=3, label="UAE customs (Comtrade)")
ax.axvspan(2012.5, 2016.5, color="#efece6", zorder=0)
ax.text(2014.5, 30, "UAE booked about a third\nof imports as 'unspecified'", ha="center", fontsize=8)
ax.set_ylabel("USD billion"); ax.legend()
ax.set_title("Total UAE goods imports: the two sources move together, with gaps in 2013-16 and after 2020")
finish(fig, "fig0_reliability_baci_vs_uae.png", "CEPII BACI HS92 V202601 and UN Comtrade (UAE as reporter), 1999-2023.")


# %% 3. How dependent is the UAE on single suppliers? ----------------------------
print("\n=== 3. Supplier concentration, strategic products, 2023 ===")
y23 = baci_hs4[baci_hs4["year"] == 2023]
by_sup = y23.groupby(["hs4", "hs4_name", "exporter_iso3"], as_index=False)["value_kusd"].sum()
by_sup["share"] = by_sup["value_kusd"] / by_sup.groupby("hs4")["value_kusd"].transform("sum")
by_sup["share_sq"] = by_sup["share"] ** 2
conc = (by_sup.sort_values("share", ascending=False)
        .groupby(["hs4", "hs4_name"])
        .agg(imports_musd=("value_kusd", lambda x: x.sum() / 1e3),
             top_supplier=("exporter_iso3", "first"),
             top_share=("share", "first"),
             hhi=("share_sq", lambda x: 1e4 * x.sum()))
        .reset_index()
        .sort_values("top_share", ascending=False))
fact("Strategic products with UAE imports in 2023", len(conc), "", "BACI HS4")
fact("Strategic products where one supplier has more than 50%, 2023", (conc["top_share"].to_numpy() > 0.5).sum(), "", "BACI HS4")
fact("China's share of UAE computer imports (8471), 2023", supplier_share(baci_hs4, "8471", "CHN", 2023), "%", "BACI HS4")
fact("China's share of UAE phone imports (8525 in HS92), 2019", supplier_share(baci_hs4, "8525", "CHN", 2019), "%", "BACI HS4")
fact("China's share of UAE phone imports (8525 in HS92), 2023", supplier_share(baci_hs4, "8525", "CHN", 2023), "%", "BACI HS4")

top10 = conc.head(12).copy()
top10["Product"] = top10["hs4"] + " " + top10["hs4_name"].str.slice(0, 38)
top10_tab = pd.DataFrame({
    "Product (HS4)": top10["Product"],
    "Imports 2023 (USD m)": top10["imports_musd"].map("{:,.0f}".format),
    "Top supplier": top10["top_supplier"],
    "Share": (100 * top10["top_share"]).map("{:.0f}%".format),
    "HHI": top10["hhi"].map("{:,.0f}".format),
})
print(top10_tab.to_string(index=False))
show_table(top10_tab, "Table 2. Most concentrated strategic products, 2023", "table2_concentration.png",
           col_widths=[0.45, 0.16, 0.12, 0.08, 0.08])


# %% 4. China's rise as a supplier ------------------------------------------------
print("\n=== 4. China's share of all UAE goods imports ===")
hs2 = baci_hs2[baci_hs2["year"] <= 2023]
total = hs2.groupby("year")["value_kusd"].sum()
share_chn = 100 * hs2[hs2["exporter_iso3"] == "CHN"].groupby("year")["value_kusd"].sum() / total
share_ind = 100 * hs2[hs2["exporter_iso3"] == "IND"].groupby("year")["value_kusd"].sum() / total
fact("UAE goods imports, 2023", total[2023] / 1e6, "USD bn", "BACI HS2")
fact("China's share of UAE goods imports, average 1995-1999", share_chn.loc[1995:1999].mean(), "%", "BACI HS2")
fact("China's share of UAE goods imports, 2023", share_chn[2023], "%", "BACI HS2")

fig, ax = plt.subplots(figsize=(8.5, 4))
for s, lab, col in [(share_chn, "China", COLORS[0]), (share_ind, "India", COLORS[1])]:
    ax.plot(s.index, s.values, color=col, marker="o", ms=3)
    ax.annotate(f"{lab} {s.iloc[-1]:.0f}%", (s.index[-1], s.iloc[-1]), xytext=(6, 0),
                textcoords="offset points", va="center")
ax.set_xlim(1995, 2026); ax.set_ylim(0, 25); ax.set_ylabel("% of all UAE goods imports")
ax.set_title("China's share of UAE goods imports went from about 5% to 20%")
finish(fig, "fig1_china_share.png", "CEPII BACI HS92 V202601, 1995-2023.")


# %% 5. The big suppliers behind our cases ---------------------------------------
print("\n=== 5. Big suppliers in the shock cases ===")
fact("Japan's share of UAE truck imports (870422), 2009", supplier_share(baci_hs6, "870422", "JPN", 2009, "hs6"), "%", "BACI HS6")
fact("Japan's share of UAE truck imports (870422), 2010", supplier_share(baci_hs6, "870422", "JPN", 2010, "hs6"), "%", "BACI HS6")
fact("Iran's share of UAE semi-finished steel (7207), 2018", supplier_share(baci_all, "7207", "IRN", 2018), "%", "BACI HS4")
fact("Iran's share of UAE semi-finished steel (7207), 2019", supplier_share(baci_all, "7207", "IRN", 2019), "%", "BACI HS4")
for yr in (2021, 2022, 2023):
    fact(f"India's share of UAE wheat (1001), {yr}", supplier_share(baci_hs4, "1001", "IND", yr), "%", "BACI HS4")
for yr in (2022, 2023):
    fact(f"Russia's share of UAE wheat (1001), {yr}", supplier_share(baci_hs4, "1001", "RUS", yr), "%", "BACI HS4")
for yr in (2021, 2022):
    fact(f"Ukraine's share of UAE sunflower oil (1512), {yr}", supplier_share(baci_hs4, "1512", "UKR", yr), "%", "BACI HS4")

cases = [(baci_hs4, "hs4", "8471", "CHN", "China, computers (8471)", 2020),
         (baci_hs4, "hs4", "8525", "CHN", "China, phones (8525)", 2020),
         (baci_hs6, "hs6", "870422", "JPN", "Japan, trucks (870422)", 2011),
         (baci_all, "hs4", "7207", "IRN", "Iran, semi-finished steel (7207)", 2019),
         (baci_hs4, "hs4", "1001", "IND", "India, wheat (1001)", 2022),
         (baci_hs4, "hs4", "1512", "UKR", "Ukraine, sunflower oil (1512)", 2022)]
fig, axes = plt.subplots(2, 3, figsize=(13, 6.6), sharey=True)
for ax, (df, col, code, sup, title, shock) in zip(axes.ravel(), cases):
    d = df[(df[col] == code) & (df["year"] <= 2023)]
    tot = d.groupby("year")["value_kusd"].sum()
    own = d[d["exporter_iso3"] == sup].groupby("year")["value_kusd"].sum().reindex(tot.index, fill_value=0)
    share = 100 * own / tot
    ax.axvspan(shock - 0.5, shock + 0.5, color="#efece6", zorder=0)
    ax.axhline(50, color="#b5b3ad", lw=1, ls="--")
    ax.plot(share.index, share.values, color=COLORS[0], marker="o", ms=2.5)
    ax.set_title(title, fontsize=10); ax.set_ylim(0, 100); ax.set_xlim(1995, 2024)
for ax in axes[:, 0]:
    ax.set_ylabel("% of UAE imports")
fig.suptitle("The big supplier's share of UAE imports (shaded: shock year, dashed: 50%)", x=0.01, ha="left", fontweight="bold")
fig.tight_layout(rect=(0, 0.03, 1, 0.96))
finish(fig, "fig2_big_supplier_cases.png", "CEPII BACI HS92 V202601. Trucks at HS6, the rest at HS4.")


# %% 6. Japan earthquake, March 2011: monthly car exports to the UAE -------------
print("\n=== 6. Japan earthquake 2011 (cars, HS 8703) ===")
cars = (ct_month[ct_month["cmdCode"] == "8703"]
        .groupby(["month", "reporterISO"])["primaryValue"].sum()
        .unstack() / 1e6)                                          # USD m, one column per supplier
pre = cars.loc["2010-10":"2011-03"].mean()
during = cars.loc["2011-04":"2011-05"].mean()
japan_tab = pd.DataFrame({"Oct 2010-Mar 2011": pre, "Apr-May 2011": during})
japan_tab["Change (%)"] = 100 * (japan_tab["Apr-May 2011"] / japan_tab["Oct 2010-Mar 2011"] - 1)
japan_tab = japan_tab[japan_tab["Oct 2010-Mar 2011"] > 5].sort_values("Oct 2010-Mar 2011", ascending=False)
print("Monthly car exports to the UAE, USD m:")
print(japan_tab.round(1).to_string())
fact("Japan's car exports to UAE, monthly, Oct 2010-Mar 2011", pre["JPN"], "USD m", "Comtrade monthly")
fact("Japan's car exports to UAE, monthly, Apr-May 2011", during["JPN"], "USD m", "Comtrade monthly")
fact("Japan's car exports to UAE, change (Apr-May 2011 vs Oct-Mar)", japan_tab.loc["JPN", "Change (%)"], "%", "Comtrade monthly")
fact("US car exports to UAE, same windows, change", japan_tab.loc["USA", "Change (%)"], "%", "Comtrade monthly")

c = cars.loc["2010-06":"2012-06"]
x = pd.to_datetime(c.index + "-15")
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.axvspan(pd.Timestamp("2011-04-01"), pd.Timestamp("2011-05-31"), color="#efece6", zorder=0)
for i, (s, lab) in enumerate([("JPN", "Japan"), ("USA", "United States"), ("GBR", "United Kingdom"), ("THA", "Thailand")]):
    ax.plot(x, c[s].to_numpy(), color=COLORS[i], lw=2.4 if s == "JPN" else 1.6, label=lab)
ax.annotate(f"Japan: ${pre['JPN']:.0f}m a month before,\n${during['JPN']:.0f}m in Apr-May 2011 "
            f"({japan_tab.loc['JPN', 'Change (%)']:.0f}%)",
            (pd.Timestamp("2011-04-15"), c.loc["2011-04", "JPN"]), xytext=(pd.Timestamp("2010-09-01"), 320),
            fontsize=8.5, arrowprops=dict(arrowstyle="-", color="#52514e", lw=0.8))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y")); ax.set_ylim(0, 380)
ax.set_ylabel("USD million per month"); ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.1), fontsize=8.5)
ax.set_title("Car exports to the UAE around the March 2011 earthquake")
finish(fig, "fig3_japan_cars_2011.png", "UN Comtrade, monthly exports to the UAE reported by each supplier, HS 8703. Korea not reported monthly before 2013.")


# %% 7. China, February 2020 -------------------------------------------------------
print("\n=== 7. China's exports to the UAE, February 2020 ===")
totals = (ct_totals[ct_totals["cmdCode"] == "TOTAL"]
          .groupby(["month", "reporterISO"])["primaryValue"].sum()
          .unstack() / 1e9)                                         # USD bn
china = totals["CHN"]
rows = []
for yr in range(2011, 2025):
    around = [f"{yr - 1}-12", f"{yr}-01", f"{yr}-03", f"{yr}-04"]
    if f"{yr}-02" in china.index and all(m in china.index for m in around):
        vals = china.loc[around].to_numpy()
        if not np.isnan(vals).any() and not np.isnan(china[f"{yr}-02"]):
            rows.append({"year": yr, "Feb (USD bn)": china[f"{yr}-02"], "Ratio to Dec-Jan-Mar-Apr": china[f"{yr}-02"] / vals.mean()})
feb = pd.DataFrame(rows).set_index("year")
print(feb.round(2).to_string())
others = feb.drop(index=2020)["Ratio to Dec-Jan-Mar-Apr"].to_numpy()
fact("China's exports to the UAE, Feb 2020", china["2020-02"], "USD bn", "Comtrade monthly")
fact("Feb 2020 / average of the two months either side", feb.loc[2020, "Ratio to Dec-Jan-Mar-Apr"], "", "Comtrade monthly")
fact("  same ratio in a normal February: lowest", others.min(), "", "Comtrade monthly")
fact("  same ratio in a normal February: highest", others.max(), "", "Comtrade monthly")

z = totals.loc["2019-01":"2021-12", ["CHN", "IND", "USA", "DEU"]]
x = pd.to_datetime(z.index + "-15")
fig, ax = plt.subplots(figsize=(9, 4.2))
for yr in (2019, 2020, 2021):
    ax.axvspan(pd.Timestamp(f"{yr}-02-01"), pd.Timestamp(f"{yr}-02-28"), color="#efece6", zorder=0)
for i, (s, lab) in enumerate([("CHN", "China"), ("IND", "India"), ("USA", "United States"), ("DEU", "Germany")]):
    ax.plot(x, z[s].to_numpy(), color=COLORS[i], lw=2.4 if s == "CHN" else 1.6, label=lab)
ax.annotate(f"Feb 2020: ${china['2020-02']:.1f}bn, {feb.loc[2020].iloc[1]:.2f} of the months around it\n"
            f"(a normal February: {others.min():.2f} to {others.max():.2f})",
            (pd.Timestamp("2020-02-15"), china["2020-02"]), xytext=(pd.Timestamp("2020-04-15"), 4.6),
            fontsize=8.5, arrowprops=dict(arrowstyle="-", color="#52514e", lw=0.8))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y")); ax.set_ylim(0, 5.6)
ax.set_ylabel("USD billion per month"); ax.legend(ncol=4, loc="upper left", fontsize=8.5)
ax.set_title("China's exports to the UAE collapsed in February 2020 (shaded: Februaries)")
finish(fig, "fig4_china_feb2020.png", "UN Comtrade, total monthly exports to the UAE reported by each supplier.")


# %% 8. Exposure across the Gulf: Indian wheat before the 2022 ban ------------------
print("\n=== 8. India's share of each Gulf country's wheat imports, 2021 ===")
w = baci_gcc[(baci_gcc["hs4"] == "1001") & (baci_gcc["year"] == 2021) & (baci_gcc["destination"].isin(GULF))]
w_tot = w.groupby("destination")["value_kusd"].sum()
w_ind = w[w["exporter_iso3"] == "IND"].groupby("destination")["value_kusd"].sum().reindex(w_tot.index, fill_value=0)
exposure = (100 * w_ind / w_tot).reindex(GULF)
wheat_tab = pd.DataFrame({"Country": [GULF_NAMES[g] for g in GULF],
                          "Wheat imports 2021 (USD m)": (w_tot.reindex(GULF) / 1e3).map("{:,.0f}".format).to_numpy(),
                          "India's share": exposure.map("{:.1f}%".format).to_numpy()})
print(wheat_tab.to_string(index=False))
for g in GULF:
    fact(f"India's share of {GULF_NAMES[g]} wheat imports, 2021", exposure[g], "%", "BACI exports to Gulf")

order = exposure.sort_values()
fig, ax = plt.subplots(figsize=(7.5, 3.6))
ax.barh([GULF_NAMES[g] for g in order.index], order.to_numpy(),
        color=[COLORS[1] if g == "ARE" else COLORS[0] for g in order.index])
for i, v in enumerate(order.to_numpy()):
    ax.text(v + 0.6, i, f"{v:.1f}%", va="center", fontsize=9)
ax.set_xlim(0, 40); ax.grid(axis="y", visible=False)
ax.set_xlabel("India's share of the country's wheat imports, 2021 (%)")
ax.set_title("Before the ban, the UAE relied on Indian wheat far more than its neighbours")
finish(fig, "fig5_india_wheat_gulf.png", "CEPII BACI HS92 V202601, wheat (HS 1001), 2021.")


# %% 9. Big-supplier screen: what happens after a big supplier drops? ------------------
# Rules:
#   big supplier: share >= threshold in the year before the drop and in at least one
#                 of the two years before that (keeps out one-year spikes)
#   drop:         product worth >= USD 30m the year before, share down >= 15 points,
#                 supplier's sales down by a third or more (log change <= -0.4)
#   supplier-wide: the supplier's exports to the rest of the world also fell (log change <= -0.22)
print("\n=== 9. Big-supplier screen, all products (BACI HS4) ===")
a = baci_all[baci_all["year"] <= 2023].groupby(["hs4", "exporter_iso3", "year"])["value_kusd"].sum()
V = a.unstack("year", fill_value=0.0)                 # rows: supplier x product, columns: years
years = V.columns.to_numpy()
prod = V.index.get_level_values("hs4").to_numpy()
sup = V.index.get_level_values("exporter_iso3").to_numpy()
v = V.to_numpy().astype(float).copy()                  # (pairs, years)

T_by_prod = V.groupby(level="hs4").sum()               # UAE total imports of each product
T = T_by_prod.loc[prod].to_numpy().astype(float).copy()
T[T == 0] = np.nan                                     # product not traded that year
S = v / T                                              # supplier share


def lag(m, k):
    """Shift a (pairs, years) matrix k years to the right (k > 0) or left (k < 0)."""
    out = np.full_like(m, np.nan)
    if k > 0:
        out[:, k:] = m[:, :-k]
    else:
        out[:, :k] = m[:, -k:]
    return out


S1, S2, S3 = lag(S, 1), lag(S, 2), lag(S, 3)
T1, v1, Tf, vf = lag(T, 1), lag(v, 1), lag(T, -1), lag(v, -1)

with np.errstate(invalid="ignore", divide="ignore"):
    is_drop = (T1 >= 30000) & ((S - S1) <= -0.15) & ((np.log(np.maximum(v, 1)) - np.log(np.maximum(v1, 1))) <= -0.4)
    replaced = ((Tf - vf) - (T1 - v1)) / (v1 - v)        # share of the loss made up by others, by next year
    total_chg = Tf / T1 - 1                              # change in total UAE imports, by next year
    big50 = (S >= 0.5) & ((S1 >= 0.5) | (S2 >= 0.5))

fact("Products (HS4) in the data", len(np.unique(prod)), "", "BACI HS4")
fact("Products that ever had a big supplier (50%, 2 of 3 years)", len(np.unique(prod[big50.any(axis=1)])), "", "BACI HS4")

i, j = np.nonzero(is_drop)
drops = pd.DataFrame({"hs4": prod[i], "exporter_iso3": sup[i], "year": years[j],
                      "s_l1": S1[i, j], "s_l2": S2[i, j], "s_l3": S3[i, j],
                      "replaced": replaced[i, j], "total_chg": total_chg[i, j]})

# supplier-wide or not: the supplier's exports to the rest of the world, this year vs last
wd = baci_world.pivot_table(index=["hs4", "exporter_iso3", "year"], columns="destination",
                            values="value_kusd", aggfunc="sum").fillna(0)
row = (wd["WLD"] - wd.get("ARE", 0)).rename("row").reset_index()
row_prev = row.assign(year=row["year"] + 1).rename(columns={"row": "row_prev"})
drops = drops.merge(row, how="left").merge(row_prev, how="left")
dlog_row = np.log(np.maximum(drops["row"].fillna(0), 1)) - np.log(np.maximum(drops["row_prev"].fillna(0), 1))
drops["supplier_wide"] = dlog_row <= -0.22
drops = drops[~drops["year"].between(2013, 2016)]      # UAE "unspecified" imports problem

results = []
for th in (20, 30, 40, 50):
    t = th / 100
    big = (drops["s_l1"] >= t) & ((drops["s_l2"] >= t) | (drops["s_l3"] >= t))
    d_all, d_sw = drops[big], drops[big & drops["supplier_wide"]]
    results.append({"Threshold": f"{th}%", "Drops": len(d_all), "Supplier-wide": len(d_sw),
                    "Replaced, all (%)": 100 * np.nanmedian(d_all["replaced"]),
                    "Replaced, supplier-wide (%)": 100 * np.nanmedian(d_sw["replaced"]),
                    "Total imports, all (%)": 100 * np.nanmedian(d_all["total_chg"]),
                    "Total imports, supplier-wide (%)": 100 * np.nanmedian(d_sw["total_chg"])})
res = pd.DataFrame(results)
print("Medians, one year after the drop (1996-2023, excluding 2013-16):")
print(res.round(1).to_string(index=False))
for r in results:
    fact(f"Median share of loss replaced by next year, supplier-wide, {r['Threshold']}", r["Replaced, supplier-wide (%)"], "%", "BACI HS4")

show_table(res.round(1).astype(str), "Table 3. After a big supplier drops: medians one year later",
           "table3_thresholds.png", col_widths=[0.09, 0.08, 0.11, 0.12, 0.17, 0.14, 0.2])

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
th = np.array([20, 30, 40, 50])
panels = [("Drops", "Supplier-wide", "Number of big-supplier drops", ""),
          ("Replaced, all (%)", "Replaced, supplier-wide (%)", "Share of the loss made up by others\nby the next year (median)", "%"),
          ("Total imports, all (%)", "Total imports, supplier-wide (%)", "Change in total UAE imports of the\nproduct by the next year (median)", "%")]
for ax, (ca, cw, title, unit) in zip(axes, panels):
    ax.plot(th, res[ca], marker="o", color=COLORS[0], label="All drops")
    ax.plot(th, res[cw], marker="o", color=COLORS[1], label="Supplier sold less everywhere")
    for col in (ca, cw):
        ax.annotate(f"{res[col].iloc[-1]:.0f}{unit}", (50, res[col].iloc[-1]), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=8.5)
    ax.set_xticks(th); ax.set_xticklabels([f"{t}%" for t in th]); ax.set_xlabel("Threshold for a big supplier")
    ax.set_title(title, fontsize=10.5)
    if unit:
        ax.axhline(0, color="#52514e", lw=0.8)
axes[0].legend(fontsize=8.5)
fig.suptitle("At every threshold, other suppliers make up little of a big supplier's loss within a year", x=0.01, ha="left", fontweight="bold")
fig.tight_layout(rect=(0, 0.04, 1, 0.93))
finish(fig, "fig6_big_supplier_thresholds.png", "CEPII BACI HS92, HS4, 1996-2023 excluding 2013-16.")


# %% 10. Defense: US share of UAE arms deliveries (SIPRI) ----------------------------
print("\n=== 10. SIPRI: US share of UAE arms imports ===")
sipri["tiv"] = pd.to_numeric(sipri["TIV delivery values"], errors="coerce")
sipri["period"] = ((sipri["Delivery year"] - 2001) // 5 * 5 + 2001).astype("Int64")
dl = sipri[sipri["period"].between(2001, 2021)]
us_share = (dl[dl["Supplier"] == "United States"].groupby("period")["tiv"].sum()
            / dl.groupby("period")["tiv"].sum() * 100)
print(us_share.round(1).to_string())
for p in (2006, 2011, 2016):
    fact(f"US share of UAE arms deliveries, {p}-{p + 4}", us_share[p], "%", "SIPRI")

# orders: SIPRI register, one line per deal (TIV of the whole order is column 15)
deals = pd.DataFrame([line.split("\t") for line in sipri_register if line.startswith("United Arab Emirates\t")])
orders = pd.DataFrame({"supplier": deals[1], "order_year": pd.to_numeric(deals[2], errors="coerce"),
                       "tiv": pd.to_numeric(deals[14], errors="coerce")})


def us_order_share(y0, y1):
    o = orders[orders["order_year"].between(y0, y1)]
    return 100 * o.loc[o["supplier"] == "United States", "tiv"].sum() / o["tiv"].sum()


fact("US share of UAE arms orders, 2016-2020", us_order_share(2016, 2020), "%", "SIPRI register")
fact("US share of UAE arms orders, 2021", us_order_share(2021, 2021), "%", "SIPRI register")
print("  (orders only cover deals with at least one delivery by 2025)")

fig, ax = plt.subplots(figsize=(7.5, 3.8))
labels = [f"{p}-{str(p + 4)[2:]}" for p in us_share.index]
bars = ax.bar(labels, us_share.to_numpy(), color=COLORS[0], width=0.6)
for b, val in zip(bars, us_share.to_numpy()):
    ax.text(b.get_x() + b.get_width() / 2, val + 1.5, f"{val:.0f}%", ha="center", fontsize=9)
ax.set_ylim(0, 100); ax.set_ylabel("US share of deliveries (%)"); ax.grid(axis="x", visible=False)
ax.set_title("US share of major arms deliveries to the UAE, by 5-year period")
finish(fig, "fig7_sipri_us_share.png", "SIPRI Arms Transfers Database, trend-indicator values (a volume index, not money).")


# %% 11. Summary: every number we quote -------------------------------------------------
print("\n=== 11. Summary of key facts ===")
summary = pd.DataFrame(FACTS)
summary["value"] = [f"{v:.2f}" if abs(v) < 10 else f"{v:,.1f}" for v in summary["value"]]
print(summary.to_string(index=False))
summary.to_csv(FIG_DIR / "key_facts.csv", index=False)
key = summary[summary["fact"].str.contains("more than 50%|computer|1995-1999|goods imports, 2023|870422\\), 2010|7207\\), 2018|wheat \\(1001\\), 2022|sunflower oil \\(1512\\), 2021|change \\(Apr|same windows|Feb 2020 /|UAE wheat imports|2011-2015")]
show_table(key[["fact", "value", "unit", "source"]].rename(columns=str.capitalize),
           "Table 4. Key facts quoted on the slides", "table4_key_facts.png",
           col_widths=[0.58, 0.1, 0.1, 0.2], fontsize=8.5)
print(f"\nFigures and tables saved in {FIG_DIR}")
