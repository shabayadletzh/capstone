# UAE import sourcing: data check (brief report)

Prepared 29 Oct 2026. Goal: see whether there is enough real data to study which suppliers replace a disrupted exporter in UAE imports, and whether credible supply shocks show up in it.

Short answer: yes. The data exist, I collected them, and at least two shocks show a clear drop in one supplier and a visible rise in others at monthly frequency. The cleanest case is the March 2011 Japan earthquake and UAE car imports.

## 1. What I collected

Everything comes straight from official or academic sources. No values were filled in or estimated.

| Source | What | Frequency | Years | Size |
|---|---|---|---|---|
| CEPII BACI (HS92, v202601) | UAE imports by exporter, HS6, 59 strategic HS4 headings | Annual | 1995-2024 | 271k rows |
| CEPII BACI | UAE imports of all goods by exporter and HS2 chapter | Annual | 1995-2024 | 215k rows |
| CEPII BACI | Every exporter's exports of the same headings to the world and to each GCC country (for checking if a drop is UAE-specific or global) | Annual | 1995-2024 | 664k rows |
| UN Comtrade | Exports to the UAE reported by 29 supplier countries (China, India, US, Japan, Korea, UK, Turkey, Thailand, Pakistan, Malaysia, Indonesia, Brazil and others), 62 headings | **Monthly** | Jan 2010 - Sep 2026 (Korea from 2013, Saudi from 2015, China to Dec 2024) | 147k rows |
| UN Comtrade | UAE-reported imports: totals by partner, by chapter, and selected headings by partner | Annual | 1999-2023 | 15k rows |
| Eurostat Comext | Exports of all 27 EU countries and the UK to the UAE, 62 headings plus all chapters | **Monthly** | Jan 1988 - Aug 2026 | 800k rows |
| SIPRI | Every major arms delivery to the UAE, with supplier and year | Annual | 1970-2025 | 909 delivery records, 437 deals |
| OECD-WTO BaTIS | UAE services imports by partner and service type | Annual | 2005-2024 | 124k rows |

The "strategic" headings cover defense, aerospace, ICT and electronics, vehicles and ships, machinery, metals, refined fuels, gold and diamonds, pharmaceuticals and food staples. Together they are about two thirds of UAE goods imports in 2023 ($265bn of $392bn in BACI). Full list and definitions are in `DATA_DICTIONARY.md`.

Three things I checked and you should know before the meeting:

- **The UAE does not publish monthly bilateral data.** Comtrade's own availability record shows UAE monthly data only for parts of 2010-11 and 2017-19, and no UAE data at all for 2024. So monthly work has to use supplier-reported (mirror) exports, which is what Prof. Imbs suggested.
- **Services data are modelled, not reported.** Every bilateral BaTIS value for the UAE is flagged "imputed". Only the UAE total is reported. Good for context, not for testing shocks.
- **BACI 2024 is mirror-only for the UAE** and distorts some shares (phones especially). I used 1995-2023 for share analysis.

## 2. Where UAE supplier dependence is high

Concentration measured with the HHI of supplier shares, average 2019-2023 (above 2,500 counts as highly concentrated). Chart: `charts/02_hhi_by_product.png`. Table: `output/table_supplier_dependence_summary.csv`.

| Product (HS4) | UAE imports 2023 | Top supplier 2023 | HHI 2019-23 |
|---|---|---|---|
| Diodes, transistors, solar cells (8541) | $0.5bn | China 94% | 7,681 |
| Computers (8471) | $9.4bn | China 79% | 6,173 |
| Poultry (0207) | $1.1bn | Brazil 77% | 5,311 |
| Rice (1006) | $0.6bn | India 74% | 5,337 |
| Alumina (2818) | $1.2bn | Australia 76% | 5,299 |
| Sugar (1701) | $0.7bn | Brazil 72% | 5,038 |
| Mobile phones and transmitters (8525 in HS92) | $36.6bn | China 76% | 5,037 |
| Telecom equipment (8517) | $0.8bn | China 64% | 4,980 |
| Aircraft parts (8803) | $3.3bn | US 54% | 3,452 |
| Turbojets and gas turbines (8411) | $7.0bn | US 52% | 3,083 |
| Hot-rolled steel (7208) | $2.6bn | China 54% | 2,418 |
| Passenger cars (8703) | $24.7bn | Japan 26% | 1,857 |

Other patterns worth mentioning:

- China's share of all UAE goods imports went from about 5% in the late 1990s to about 20% in 2023. India is second at about 8%. Chart: `charts/01_top_supplier_shares_total.png`.
- Dominant suppliers do change. China took over phones and computers from Singapore, Japan and Finland in the 2000s. Russia replaced India as the top wheat supplier. Japan led car imports in every year from 1995 to 2023, but its share fell from 40-50% to 26% (China shows up on top in the 2024 mirror-only numbers). Chart: `charts/03_supplier_shares_selected_products.png`.
- Defense: SIPRI shows the US supplied 55% and France 23% of UAE major arms deliveries since 2000. Chart: `charts/04_sipri_arms_imports_by_supplier.png`. These are lumpy deals chosen by the UAE government, so they are procurement decisions, not supply shocks.

## 3. Shocks: what the monthly data show

I tested six candidate events. For each I compared average monthly shipments to the UAE in the 6 months before with the shock months. Chart: `charts/05_shock_episodes_monthly.png`. Table: `output/table_shock_episodes_pre_vs_during.csv`.

| Event | Affected supplier and product | What the data show | Verdict |
|---|---|---|---|
| Japan earthquake, 11 Mar 2011 | Japan, cars (Japan was ~48% of reported supply) | Japan's car exports to the UAE fell from ~$194m a month to ~$50m in Apr-May 2011 (-74%), then bounced back in June. US shipments held at ~$134m, so the US share jumped from 33% to 55%. Annual BACI: Korean cars to the UAE rose from $327m (2010) to $784m (2011) | **Strongest case.** Natural disaster, big supplier, sharp and short drop, clearly outside UAE control |
| India wheat export ban, 13 May 2022 | India, wheat | India shipped ~82 kt a month in Mar-Aug 2022 (contracts already signed), then zero from Sep 2022 to Aug 2023. Annual: India's share fell from 43% (2022) to 0.5% (2023) and Russia's rose from 16% to 39% | **Strong.** Clear policy shock. Caveat: India allowed some government-to-government sales |
| India onion restrictions (40% duty Aug 2023, ban 8 Dec 2023 - 4 May 2024) | India, onions | India fell from ~20 kt a month to ~6 kt. Pakistan rose from ~2 kt to ~10 kt and China from ~7 to ~10 kt | **Good, but partly endogenous.** India gave the UAE special quotas (14,400 t in Mar 2024, then 10,000 t more), which shows as an India spike in Apr 2024 |
| Indonesia palm oil ban, 28 Apr - 23 May 2022 | Indonesia, palm oil | Indonesia down ~30%, Malaysia more than doubled | Suggestive. Ban lasted under a month and the series is noisy |
| Thailand floods, Oct-Dec 2011 | Thailand, trucks and pickups | Thai shipments fell ~56%, Japanese and US shipments rose | Usable as a second case, but overlaps with Japan's own recovery |
| India rice ban, 20 Jul 2023 | India, non-basmati white rice | India's rice to the UAE barely moved (-6%) | **Negative result.** The UAE got a 75,000 t exemption and basmati was not banned. The shock did not bind for the UAE |

> **[Sultan's coding agent, 2 Nov 2026] Notes on the table above.** Adilet's text is left as it was. Details are in `CHANGES_BY_SULTANS_AGENT.md`.
> - **Japan:** the 33% → 55% US share is a share among the Comtrade reporters only. Korea (monthly data only from 2013) and the EU suppliers are not in it. The new table `output/table_japan2011_other_suppliers.csv` adds them:
>   - EU27+UK car exports to the UAE also fell in Apr-May 2011 (EUR 103m → 81m a month, −21%; Germany −19%).
>   - US shipments were flat (+0.7%).
>   - So the US share rose because Japan fell, not because the US shipped more.
>   - Korea, the biggest annual gainer (USD 327m → 784m), is still unobserved monthly.
> - **Onions:** the shock window in `scripts/charts_shocks.py` is now Dec 2023-Apr 2024, the ban months; it was Dec 2023-May 2024. With it, India falls from 19.6 to 2.1 kt a month (−89%, previously ~6 kt, −71%). Pakistan goes from 2.3 to 10.9 kt and China from 7.1 to 10.3 kt. India was already at 2.5 kt in Nov 2023, after the Aug 2023 duty, so the shock could be dated from August.
> - **Palm oil:** Malaysia's shipments to the UAE rose from about USD 11m a month (Nov 2021-Feb 2022) to 24m in March and 41m in April, before the 28 Apr ban. Part of the replacement predates the ban.
> - **Rice:** −6% uses Feb-Jul 2023 as the base. With Jan-Jun 2023 it is −15%. The conclusion is unchanged.

I also ran a systematic annual screen over all 59 headings and all suppliers with at least 15% share (`output/table_annual_shock_screen.csv`). It flags years when a supplier's exports to the UAE and to the rest of the world both fell sharply. Most hits are 2009 and 2020 (global demand drops) or gold and fuel price swings, which are not what we want. That is a useful filter in itself. It also confirms India wheat 2023 and points to a few cases worth a look later, like India hot-rolled steel in 2023.

What I would not use as the main shock: COVID (it hit every supplier and UAE demand at the same time), defense deals (UAE procurement choices), and gold (price-driven, re-export hub).

## 4. Gaps and limits

- The free Comtrade endpoint allows one month and 500 rows per call with an hourly cap, so I limited the product list to 62 headings. A free Comtrade account with an API key would allow full HS6 detail and more countries. Worth getting one.
- Korea's monthly data start only in 2013 in Comtrade. Korea matters for the Japan 2011 case (Korean cars to the UAE more than doubled in 2011 in the annual data), so we would need Korea's own customs statistics (K-stat / UNIPASS) for the monthly picture.
- China has not yet reported 2025 monthly data. Sri Lanka has almost nothing. Russia stops in 2021. Coverage by country: `output/table_comtrade_monthly_coverage_by_reporter.csv`.
- Mirror data are exports at shipment (FOB) while UAE imports are at arrival (CIF). Expect a 1-2 month lag and level differences. Goods routed through hubs (Singapore, Saudi Arabia) get attributed to the hub.
- HS codes change over time. BACI fixes this by converting to HS92. In Comtrade and Eurostat the code meaning can shift (for example aircraft parts move from 8803 to 8807 in 2022).

## 5. Can we work with this?

I think so. The data support a question like: when a major supplier of a product to the UAE is hit by a supply shock, how much of the lost volume is replaced, by whom, and how fast. The Japan 2011 car case gives one clean natural-disaster shock. The Indian export bans give a set of policy shocks on staples, with the nice twist that the UAE sometimes negotiated exemptions. Comparing the UAE with other GCC importers (already in the BACI file) gives a control group.

## 6. Phase 2 additions (2 Nov 2026)

- Reliability audit (`audit/`). BACI is within about 10% of UAE-reported totals in most years and the partner ranking agrees (log correlation 0.98 or higher, 0.83 in 2010). The 2013-16 gap comes from UAE imports booked as "unspecified" (chapter 99, about 36% of the total in 2013-15). The 29 monthly reporters cover about two thirds of all UAE imports and 83% of strategic imports outside gold and fuel.
- New sectors: energy & chemicals, construction materials, fresh food, medical supplies (56 headings, section 6b of the dictionary). Concentration is high in polyethylene (Saudi 55%), plywood (China 68%), bananas (Ecuador 63%) and eggs (Türkiye 66%).
- All-products switch screen over every HS4 heading. New confirmed cases: Iran sanctions 2012 (polyethylene, Iran 46% to 7%, Saudi up 28 points), Iran 2018-19 (steel 7207, 71% to 11%), Ukraine 2022 (sunflower oil 57% to 36%, pig iron 65% to 4%), and China Feb 2020 in the monthly data. Charts `06`, `07`.
- Rejected candidates: India rice ban (UAE exemption), Shanghai lockdown 2022 (no drop), Qatar blockade (UAE's own decision), Australian alumina 2020 (UAE started its own refinery in 2019).
- Cross-Gulf first look (step 2 of the design). Monthly exports of the shocked and replacing suppliers to all six GCC importers. Japan's car exports fell 54-69% to every Gulf importer in Apr-Jun 2011, and China's Feb 2020 exports were 32-62% below Feb 2019 to every one, so these are supply shocks, not UAE demand. Exposure differs a lot across the Gulf (India had 34% of UAE wheat but almost none of Saudi wheat). In the food cases other suppliers gained more where exposure was higher, onions most clearly. With six importers it is a picture, not a test. Chart `09`.
- Red Sea attacks (from Nov 2023) added as a failed candidate: EU exports to the UAE rose from about EUR 3.2bn a month in 2023 to 3.7bn in 2024.
  - **[Sultan's coding agent, 2 Nov 2026]** This rejection is weak. Values are in euro, with no trend or price control: they also rose to 4.3bn a month in 2025. A route shock also raises costs for every Suez user rather than removing one supplier. A cleaner test compares, within each product, suppliers that ship through Suez with those that do not.
- **[Sultan's coding agent, 2 Nov 2026]** In `scripts/gcc_first_look.py` the onion case now compares 2022 with 2023, not 2024, following the README rule to stop at 2023.
  - In 2023 annual data India's onion exports to the UAE still rose (+10.7% of pre-shock imports). The annual comparison cannot see this ban; the monthly data can.
  - The pooled slope of other suppliers' gain on exposure falls from 19.6 (se 26.4) to 3.9 (se 22.1), n = 36.
- Comtrade monthly data for the new sectors is now complete for Jan 2010 - Sep 2026.
- The meeting prep (question, literature, design, timeline) is in the Claude doc "Capstone meeting prep: UAE supplier substitution". Timeline chart: `charts/08_timeline.png`.

## Sources

- CEPII BACI: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37
- UN Comtrade API: https://comtradeapi.un.org
- Eurostat Comext DS-045409: https://ec.europa.eu/eurostat/databrowser/view/ds-045409
- SIPRI Arms Transfers Database: https://armstransfers.sipri.org
- OECD-WTO BaTIS: https://data-explorer.oecd.org (DSD_BATIS@DF_BATIS)
- India wheat ban (DGFT, 13 May 2022): https://taxguru.in/dgft/amendment-export-policy-wheat.html
- India rice ban: https://www.fas.usda.gov/data/india-india-bans-export-non-basmati-white-rice
- India rice exemption for UAE: https://telanganatoday.com/india-clears-exports-of-75000-tonnes-non-basmati-rice-to-uae
- India onion quota for UAE: https://taxguru.in/dgft/govt-permits-onion-exports-14400-mt-uae-via-ncel.html
- India lifts onion ban: https://www.businesstoday.in/india/story/govt-removes-restrictions-on-onion-exports-sets-minimum-export-price-of-550-per-mt-428256-2024-05-04
- Indonesia palm oil ban lifted 23 May 2022: https://www.spglobal.com/commodityinsights/en/market-insights/latest-news/agriculture/051922-indonesia-to-lift-ban-on-palm-oil-exports-from-may-23-trade-reactions-vary
- Japan car output after the 2011 quake: https://www.european-rubber-journal.com/2011/04/28/japanese-auto-production-sinks-57-percent-in-march
- Thailand floods and supply chains: https://www.insurancejournal.com/news/international/2011/10/28/221972.htm
