# UAE supplier substitution: data and first analysis

NYUAD Economics Capstone (2026-27), supervised by Prof. Jean Imbs.
Question: when a major supplier of a product to the UAE is hit by an outside supply shock, how much of the lost supply is replaced, how fast, and by which suppliers?

## Start here
- `DATA_DICTIONARY.md`: every file and column, sources, units, known issues.
- `REPORT.md`: data check, dependence, shock cases, and what has been found so far.
- `audit/`: reliability and identification checks (`validity_checks_log.txt` is the quickest read).
- `CHANGES_BY_SULTANS_AGENT.md`: [Sultan's coding agent, 2 Nov 2026] what Sultan's agent changed in this repository and why, plus its cross-check results. Every edited line is marked `[Sultan's coding agent, 2 Nov 2026]`.

## Layout
| Folder | Content |
|---|---|
| `data/baci/` | CEPII BACI HS92 v202601, annual 1995-2024. UAE imports by supplier and product, and suppliers' exports to the world and each GCC country |
| `data/comtrade/` | UN Comtrade. Monthly exports to the UAE and GCC reported by about 30 supplier countries (2010-2026), plus UAE-reported annual imports |
| `data/eurostat/` | Eurostat Comext DS-045409. Monthly EU (and UK to 2020) exports to the UAE and GCC, 1988-2026 |
| `data/sipri/`, `data/oecd/` | Arms deliveries and services trade, background only |
| `output/` | Analysis tables (dependence, switch screen, shock episodes, cross-Gulf first look) |
| `audit/` | Data quality and identification checks |
| `charts/` | PNG charts 01-09 |
| `scripts/` | Python used to clean and analyse the data |
| `raw/` | Raw extracts as downloaded (gzipped). Run `python3 scripts/unpack_raw.py` once before re-running any script (it also unzips the .csv.gz data files) |

Files ending in `.csv.gz` are gzip-compressed CSVs (`pd.read_csv` reads them directly).

## Sources and terms
All data were downloaded 28 Oct - 2 Nov 2026 from the publishers. Nothing was estimated or filled in.
- CEPII BACI, Etalab 2.0 licence. Cite Gaulier and Zignago (2010), CEPII WP 2010-23. https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37
- UN Comtrade, https://comtradeapi.un.org (subject to UN Comtrade terms of use)
- Eurostat Comext DS-045409, https://ec.europa.eu/eurostat
- SIPRI Arms Transfers Database, non-commercial fair use, https://armstransfers.sipri.org
- OECD-WTO BaTIS, https://data-explorer.oecd.org

## Notes for anyone continuing the work
- Use BACI 1995-2023 for shares. 2024 is built from partner reports only.
- 2013-2016: about a third of UAE-reported imports are booked as "unspecified" (chapter 99). Be careful with product shares in those years.
- Monthly data are supplier-reported (mirror) exports: FOB, at shipment date. Expect 1-2 month lags vs arrival.
- In monthly Comtrade data a missing product in a month the reporter did report means zero. A month the reporter did not report stays missing (see `comtrade_monthly_coverage_reporter_month.csv`).
- Shocks should be dated from official documents, not picked from the data. See `audit/validity_*` for placebo, pre-trend and supply-vs-demand checks.
