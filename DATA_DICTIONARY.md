# Data dictionary and source notes

All files were downloaded on 28 Oct - 2 Nov 2026 directly from the official sources below. Nothing was filled in or estimated. A missing row means the source had no record for that cell. It does not mean zero trade, unless the source itself reports a 0.

Folder layout:

- `data/baci/` CEPII BACI (annual, reconciled bilateral trade, HS6, 1995-2024)
- `data/comtrade/` UN Comtrade (UAE-reported annual imports, and monthly exports to the UAE reported by 29 partner countries)
- `data/eurostat/` Eurostat Comext (monthly exports of EU countries + UK to the UAE, 1988-2026)
- `data/sipri/` SIPRI Arms Transfers Database (major arms deliveries to the UAE, 1970-2025)
- `data/oecd/` OECD-WTO BaTIS (bilateral services imports of the UAE, 2005-2024)
- `audit/` reliability checks (phase 2)
- `output/` tables computed from the data above
- `charts/` PNG charts
- `scripts/` Python code used to clean and analyse the data

---

## 1. CEPII BACI, version 202601 (HS92 nomenclature)

Source: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37 , file `BACI_HS92_V202601.zip` (released 22 Jan 2026, licence Etalab 2.0). Cite as Gaulier and Zignago (2010), CEPII WP 2010-23.

BACI reconciles what the importer and the exporter each report, so it covers years when the UAE itself did not report. Values are in thousand USD (FOB), quantities in metric tonnes. HS92 codes are kept constant over time, so 1995 and 2024 are comparable. This also means some modern codes do not exist in HS92: smartphones sit in 852520, aircraft parts in 8803, and there is no 8486 or 8807.

Important caveat: the UAE did not report its 2024 trade, so BACI 2024 for the UAE is built only from partner reports. Shares in 2024 look distorted for some products (phones in particular). Use 1995-2023 for share analysis.

| File | Rows | Content |
|---|---|---|
| `baci_uae_imports_hs6_strategic_1995_2024.csv.gz` (gzip, opens in Excel after unzipping, or directly with pandas) | 271,087 | UAE imports by exporter x HS6 product x year, for the 59 strategic HS4 headings listed in section 6. Columns: year, importer_iso3, exporter_code, exporter_iso3, exporter_name, sector, hs4, hs4_name, hs6, hs6_desc, value_kusd, quantity_tonnes |
| `baci_uae_imports_hs4_strategic_1995_2024.csv` | 89,215 | Same, summed to HS4 |
| `baci_uae_imports_hs2_all_1995_2024.csv` | 215,213 | UAE imports of ALL goods by exporter x HS2 chapter x year (value_kusd) |
| `baci_strategic_hs4_exports_by_exporter_to_world_and_gcc_1995_2024.csv` | 664,352 | For every exporter in the world: exports of the strategic HS4 headings to the world (WLD) and to each GCC country (ARE, SAU, OMN, KWT, QAT, BHR). Used to check whether a supplier's drop is specific to the UAE or global |
| `baci_panel_supplier_uae_vs_rest_of_world.csv.gz` | panel | Derived panel: supplier exports to UAE, to rest of world, UAE share, year-on-year log changes |
| `baci_uae_imports_hs4_ALL_products_1995_2024.csv.gz` (phase 2) | 1,218,737 | UAE imports of every HS4 heading by exporter and year. Columns: year, exporter_code, hs4, value_kusd, quantity_tonnes, exporter_iso3, exporter_name. Used for the all-products switch screen |
| `baci_uae_imports_hs6_new_sectors_1995_2024.csv.gz` (phase 2) | 153,806 | HS6 detail for the 56 new-sector headings in section 6b. Same columns as the strategic HS6 file |
| `baci_switch_flagged_pairs_exports_to_world_and_gcc_1995_2024.csv` (phase 2) | 211,848 | For each supplier x HS4 flagged by the switch screen: exports to the world (WLD) and to each GCC country. Used to tell a supplier-wide drop from a UAE-specific one |
| `baci_uae_supplier_concentration_hs4_by_year.csv` | derived | HHI, top 3 suppliers and shares, number of suppliers by HS4 x year |

## 2. UN Comtrade (public preview API)

Source: https://comtradeapi.un.org/public/v1/preview/ (no API key). The public endpoint allows one period and at most 500 records per call, with an hourly quota, which is why collection was slow.

Data availability check for the UAE as reporter (from Comtrade's own availability endpoint): annual data exist for 1991-93 and 1999-2023. Monthly UAE-reported data exist only for parts of 2010-2011 and 2017-2019. So monthly analysis has to rely on partner (mirror) reports.

| File | Content |
|---|---|
| `comtrade_uae_reported_imports_total_by_partner_annual.csv` | UAE-reported total imports by partner country, 1999-2023 |
| `comtrade_uae_reported_imports_by_chapter_annual.csv` | UAE-reported imports from the world by HS2 chapter, 1999-2023 |
| `comtrade_uae_reported_imports_hs4_by_partner_annual.csv` | UAE-reported imports by partner for the strategic HS4 headings, selected years |
| `comtrade_monthly_exports_to_uae_by_reporter.csv` | Monthly exports TO the UAE reported by 29 partner countries, 62 strategic HS4 headings, Jan 2010 - Sep 2026 (147k rows) |
| `comtrade_monthly_exports_to_uae_new_sectors_and_totals_2010_2026.csv` (phase 2) | Monthly exports TO the UAE for 35 new-sector headings plus each reporter's TOTAL, 40 reporters, Jan 2010 - Sep 2026 (98k rows). Columns: month, period, reporterCode, reporterISO, flowCode, partnerISO, cmdCode, classificationCode, primaryValue (USD), fobvalue, netWgt (kg), qty, estimate flags |
| `comtrade_monthly_exports_to_GCC_case_products.csv` (phase 2) | Monthly exports of the shocked and replacing suppliers to all six GCC importers (ARE, SAU, OMN, KWT, QAT, BHR) for the case products: cars and trucks 2010-2012 (8703, 8704), wheat, flour, palm oil, sunflower oil, pig iron and onions 2021 - mid 2025 (1001, 1101, 1511, 1512, 7201, 0703), and total exports 2019 - mid 2021 for the China Feb 2020 check. Column `case` names the block. 8.2k rows |
| `comtrade_monthly_coverage_reporter_month.csv` | Which reporter-months returned data (to separate "not reported" from "zero") |

Main columns: period (YYYY or YYYYMM), reporterISO, partnerISO, flowCode (M import, X export), cmdCode (HS code in the reporter's own HS version), classificationCode (H0-H6 = HS1992-HS2022), primaryValue (USD), cifvalue / fobvalue (USD), netWgt (kg), qty and qtyUnitAbbr, isReported, isQtyEstimated, isNetWgtEstimated.

Monthly reporters requested: CHN, IND, USA, JPN, KOR, GBR, TUR, THA, MYS, VNM, SAU, BRA, CHE, AUS, CAN, PAK, IDN, RUS, EGY, SGP, ZAF, MEX, NZL, ARG, UKR, ISR, PHL, LKA, KEN, OMN. Coverage is Jan 2010 to Sep 2026 overall. Korea starts 2013, Saudi Arabia and Oman 2015, Israel 2016, Indonesia late 2012, China ends Dec 2024 (2025 not yet reported), Russia 2013-2021, Sri Lanka has only 2 months.

## 3. Eurostat Comext, dataset DS-045409 ("EU trade since 1988 by HS2-4-6 and CN8")

Source: https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409 (dataset last updated 16 Oct 2026).

Monthly exports (flow 2) from 27 EU members plus the UK (UK until 2020) to the UAE (partner AE), Jan 1988 to Aug 2026.

| File | Content |
|---|---|
| `eurostat_comext_monthly_exports_to_UAE_hs4_strategic.csv` | 62 HS4 headings. Columns: reporter, partner, product, flow_code, month, value_eur, quantity_100kg, supplementary_qty |
| `eurostat_comext_monthly_exports_to_UAE_new_sectors.csv` (phase 2) | The 55 new-sector headings, Jan 1988 - Aug 2026 (150k rows). Columns: reporter, partner, product, month, quantity_100kg, value_eur |
| `eurostat_comext_monthly_exports_to_GCC_case_products.csv` (phase 2) | EU and UK exports to all six GCC countries for the same case products (8703, 8704, 1001, 1101, 1511, 1512, 7201, 0703), Jan 2009 - Aug 2026. Columns: reporter, partner, product, month, quantity_100kg, value_eur |
| `eurostat_comext_monthly_exports_to_UAE_total_and_hs2.csv` | Total trade and all HS2 chapters (except 98), value_eur |

Codes follow the CN version in force each year, so a code can change meaning when the HS changes (for example 8524 meant recorded media before 2007 and flat-panel modules from 2022). Values are in euro.

## 4. SIPRI Arms Transfers Database

Source: https://armstransfers.sipri.org/ArmsTransfer/TransferRegister (recipient = United Arab Emirates, 1970-2025, register with deliveries broken down by year; generated 28 Oct 2026). SIPRI fair-use, non-commercial.

`sipri_uae_arms_imports_deliveries_by_year.csv` (909 rows): one row per deal x delivery year. Columns include Supplier, Designation, Description, Armament category, Order date, Delivery year, number delivered, TIV per unit, TIV delivery values, and estimate flags. TIV is SIPRI's trend-indicator value (a volume index in millions), not a money value.

## 5. OECD-WTO BaTIS (Balanced Trade in Services)

Source: https://data-explorer.oecd.org dataflow OECD.SDD.TPS / DSD_BATIS@DF_BATIS (SDMX API).

`batis_uae_services_imports_by_partner.csv` (124,434 rows): UAE services imports by partner x EBOPS 2010 service category x year, 2005-2024, million USD, balanced values (adjustment B).

Caveat: every bilateral UAE value carries status "I" (imputed by the receiving agency). Only the UAE world totals are reported (status A). The bilateral split is model-based, so it is fine for context but not for testing shocks.

## 6. Strategic product groups (non-overlapping)

| Group | HS4 headings |
|---|---|
| Defense & military | 9301 military weapons, 9305 parts of arms, 9306 bombs/missiles/ammunition, 8710 tanks and armoured vehicles, 8906 warships and other vessels |
| Aerospace | 8802 aircraft, 8803 (HS2022: 8807) aircraft parts, 8411 turbojets and gas turbines |
| ICT & electronics | 8471 computers, 8473 computer parts, 8517 telephones, 8525 transmitters (incl. mobile phones in HS92), 8526 radar and navigation, 8528 monitors and TVs, 8541 diodes/transistors/solar cells, 8542 integrated circuits, 8486 semiconductor machinery (HS2007+), 8524 flat-panel modules (HS2022+) |
| Medical technology | 9018 |
| Vehicles & ships | 8703 cars, 8704 trucks, 8708 vehicle parts, 8701 tractors, 8901 ships, 8905 drilling platforms, 4011 tyres |
| Machinery & electrical | 8429 earth-moving machinery, 8481 valves, 8413 pumps, 8502 generating sets, 8504 transformers, 8544 cable, 8406 steam turbines, 8415 air conditioners, 8507 batteries |
| Metals & basic materials | 7208 hot-rolled steel, 7210 coated steel, 7214 bars and rebar, 7304 seamless tubes, 7306 other tubes, 7308 steel structures, 2601 iron ore, 2818 alumina, 7601 aluminium, 7403 refined copper |
| Refined fuels | 2710 |
| Precious metals & stones | 7108 gold, 7102 diamonds, 7113 jewellery |
| Pharmaceuticals | 3004 medicaments, 3002 vaccines and blood products |
| Food staples | 1001 wheat, 1006 rice, 0703 onions, 1511 palm oil, 1512 sunflower oil, 1701 sugar, 0207 poultry, 0902 tea, 0402 milk powder, 1005 maize |

## 6b. New sectors added in phase 2

| Group | HS4 headings |
|---|---|
| Energy & chemicals | 2711 natural gas & LPG, 2701 coal, 3901 polyethylene, 3902 polypropylene, 3903 polystyrene, 3904 PVC, 3907 polyesters & PET, 3102 nitrogen fertilizers, 3105 mixed fertilizers, 2814 ammonia, 2902 cyclic hydrocarbons, 2905 alcohols incl. methanol, 3926 plastic articles |
| Construction materials | 2523 cement, 6907 and 6908 ceramic tiles, 7005 float glass, 7007 safety glass, 4407 sawn wood, 4412 plywood, 7604 aluminium bars, 7610 aluminium structures, 6802 worked stone, 2515 marble blocks, 6810 concrete articles, 6910 sanitary ware, 7213 wire rod |
| Fresh food | 0201 and 0202 beef, 0204 sheep & goat meat, 0104 live sheep & goats, 0102 live cattle, 0702 tomatoes, 0701 potatoes, 0805 citrus, 0803 bananas, 0808 apples & pears, 0806 grapes, 0407 eggs, 0302 and 0303 fish, 0401 milk, 0406 cheese, 0405 butter, 1507 soybean oil, 1517 margarine, 1101 wheat flour, 2009 fruit juices |
| Medical supplies | 3005 dressings, 4015 rubber gloves, 6307 textile articles incl. masks, 3822 diagnostic reagents, 9022 X-ray equipment, 9019 respiration apparatus, 9021 orthopaedic & implants, 3006 pharma goods n.e.s. |

Natural gas (2711) in BACI alternates between large values and zero for some suppliers. Do not use it without checking.

## 6c. Audit and screen outputs (phase 2)

| File | Content |
|---|---|
| `audit/audit_annual_totals_baci_vs_uae_reported.csv` | BACI vs UAE-reported total imports by year |
| `audit/audit_partner_agreement.csv` | Partner-level correlation of BACI and UAE-reported imports |
| `audit/audit_uae_reported_unspecified_share.csv` | Share of UAE-reported imports in chapter 99 (unspecified). Explains the 2013-16 gap |
| `audit/audit_mirror_monthly_vs_baci.csv` | Monthly mirror summed to the year vs BACI, by reporter x HS4 x year |
| `audit/audit_log.txt` | Printed summary of all checks |
| `output/table_big_supplier_threshold_summary.csv` | Big-supplier drops and what followed, at 20/30/40/50% thresholds, for all years and excluding 2013-16, all drops and supplier-wide drops. Columns: flags, suppliers, products, lost_bn_usd, median share of the loss replaced by others in the same and next year, share fully replaced by the next year, median change in total UAE imports of the product |
| `output/table_big_supplier_flags_by_threshold.csv` | Every flagged drop at each threshold: shares in the three pre-years (s_l3, s_l2, s_l1) and the drop year (s), values, loss, replacement ratios (replaced_t, replaced_t1), total import change, type, who gained |
| `output/table_big_supplier_event_cases.csv` | For the dated events: the supplier's share in the three pre-years at HS4 and at its strongest HS6 line, and the thresholds it passes |
| `audit/file_inventory.csv` | Rows, columns, years, duplicates, missing share and negative values for every file |
| `audit/validity_placebo_and_pretrend.csv` | Placebo-in-time test and pre-trend for six cases |
| `audit/validity_supply_vs_demand.csv` | Shocked supplier's exports to the UAE vs rest of world, and UAE imports from others |
| `audit/validity_value_vs_volume.csv` | Value vs weight change in the shock window |
| `audit/validity_exposure_balance.csv` | Correlation of pre-shock exposure with pre-shock import growth across Gulf importers |
| `audit/validity_checks_log.txt` | Printed output of the four checks |
| `output/table_new_sectors_dependence.csv` | Supplier concentration for the new-sector headings |
| `output/table_supplier_switch_screen_all_products.csv` | 1,956 supplier x product x year flags where a big supplier lost share (rules: prior share at least 20%, product at least $30m, share down 15 points or more, log change -0.4 or less). Column `type` says whether the drop was supplier-wide, Gulf-wide or UAE-specific. `who_gained` lists the suppliers that gained share |
| `output/table_switch_clusters_supplier_year.csv` | Flags grouped by supplier and year, to spot one event hitting many products |
| `output/table_gcc_cross_importer_monthly_first_look.csv` | For four cases and each GCC importer: pre-shock exposure (BACI), the shocked supplier's monthly exports before and during the shock, and the same for the other suppliers we pulled |
| `output/table_gcc_cross_importer_first_look.csv` | Annual version from BACI for six cases (36 importer-case pairs) |
| `output/table_gcc_feb2020_vs_feb2019_by_supplier.csv` | Change in Feb 2020 vs Feb 2019 exports to each GCC importer, for China and five other large suppliers |
| `charts/09_gcc_first_look_exposure_vs_replacement.png` | Chart of the monthly first look |



1. Mirror vs reported: partner exports (FOB, at shipment date) differ from UAE imports (CIF, at arrival). Expect a one-to-two month lag and level gaps. Re-exports through third countries (for example goods shipped via Singapore or Saudi Arabia) are attributed to the shipper.
2. Missing is not zero. In Comtrade monthly data, check the coverage file before treating an absent value as zero.
3. Gold, diamonds and refined fuels move with prices and with Dubai's re-export hub role. Treat them separately.
4. BACI flags some odd suppliers (for example Saudi Arabia or Oman as top supplier of ships, rebar or drilling platforms). These are likely re-exports or repairs and should be checked before use.
5. The UAE's 2024 data are missing from all UAE-reported sources.
6. In 2013-2016 about a third of UAE-reported imports sit in chapter 99 (unspecified), so BACI is about 28% below UAE-reported totals in those years. Treat 2013-16 product shares with care.
8. The derived panel's `*_lag` columns use the true previous calendar year (0 if BACI has no trade that year). An earlier version took the previous available row. Fixed on 2 Nov 2026, screen results unchanged.
7. Mirror monthly data summed to the year match BACI well in the median (ratio 0.99) but only 43% of pairs are within 20%. Agreement is good for codes that did not change across HS revisions and weak for 8517, 8525 and 8473.
