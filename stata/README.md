# Stata: the facts and figures on our slides

`facts_and_figures.do` rebuilds, from the data in this repository, every number on the slides that comes from our own data work, and draws seven figures.

## How to run
1. From the repository root, unzip the compressed files once: `python3 scripts/unpack_raw.py`
2. Open `facts_and_figures.do`, set `global ROOT` to the repository folder, and run it (Stata 16 or newer).
3. Read `stata/stata_facts.csv`. Each number sits next to the value from `verify_facts.py` (a Python copy of the same steps), with OK or CHECK.

## Numbers it reproduces (value from the Python copy)

| Slide | Fact | Value |
|---|---|---|
| 3 | Strategic products where the top supplier has more than 50% (2023) | 20 of 59 |
| 3, 7 | China's share of UAE computer imports (8471), 2023 | 79.4% |
| 3 | China's share of all UAE goods imports, 1995-99 average and 2023 | 4.8% and 19.9% |
| 7 | China's share of UAE phone imports (8525 in HS92), 2019 and 2023 | 59.5% and 75.7% |
| 7 | Japan's share of UAE imports of the truck line 870422, 2009 and 2010 | 79.5% and 81.6% |
| 7 | Iran's share of UAE semi-finished steel (7207), 2018 and 2019 | 70.9% and 10.6% |
| 7 | Japan's car exports to the UAE, Oct 2010-Mar 2011 vs Apr-May 2011 | USD 193.8m to 49.7m a month, -74.3% |
| 7 | China's exports to the UAE in Feb 2020, and Feb vs the two months either side | USD 1.0bn, 0.33 (other years 0.52 to 0.90) |
| 7 | India's share of UAE wheat, 2021, 2022, 2023 | 33.5%, 43.3%, 0.5% |
| 7 | Ukraine's share of UAE sunflower oil, 2021 and 2022 | 56.8% and 36.4% |
| 7 | US share of UAE arms deliveries (SIPRI TIV), 2006-10, 2011-15, 2016-20 | 57.6%, 65.6%, 64.8% |
| 7 | Median share of a big supplier's loss made up by others by the next year, supplier-wide drops, at 20/30/40/50% | 8.3, 10.9, 5.3, 3.9% |
| 9 | India's share of wheat imports in 2021: UAE, Saudi Arabia | 33.5%, 0.0% |

## Not reproduced, or different from the slides
- **"1,394 products have had a big supplier" (slide 7).** With our rule at HS4, 937 of 1,241 products have had one (fact F14). The 1,394 must come from another product level or rule.
- **"US share of new arms orders 66% to 7%, 2021" (slide 7).** Our SIPRI download gives 62% (orders 2016-20) to 1% (orders in 2021), using the TIV of the whole order. It only has deals with at least one delivery by 2025, so undelivered recent orders are missing.
- **"Shipments a third of normal" (slide 7).** Feb 2020 was a third of the two months on either side. A normal February is already 52-90% of those months because of Chinese New Year.
- **CEPII GeoDep counts (slide 3)** and **the 59-point drop in US arms orders in the UAE and Saudi Arabia (slide 9)** come from data we did not download.

## Figures (stata/figures/)
1. `fig1_china_share_of_uae_imports.png`: China's share of UAE goods imports, 1995-2023
2. `fig2_big_supplier_cases.png`: the big supplier's share over time for the six cases
3. `fig3_japan_cars_monthly_2011.png`: car exports to the UAE around the 2011 earthquake
4. `fig4_china_feb2020_monthly.png`: monthly exports to the UAE by supplier, 2019-2021
5. `fig5_india_wheat_share_gulf_2021.png`: India's share of each Gulf country's wheat imports, 2021
6. `fig6_big_supplier_thresholds.png`: what follows a big supplier's drop, at each threshold
7. `fig7_sipri_us_share.png`: US share of UAE arms deliveries by 5-year period
