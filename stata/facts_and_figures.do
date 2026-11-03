*==============================================================================
* facts_and_figures.do
*
* Reproduces, from our own downloaded data, every number on the slides that
* comes from our data work, and draws the figures behind them.
*
* NYUAD Economics Capstone 2026-27, Adilet and Sultan, Prof. Jean Imbs.
* Repository: https://github.com/shabayadletzh/capstone
*
* BEFORE RUNNING
*   1. Unzip the compressed data once, from the repository root:
*        python3 scripts/unpack_raw.py
*      (or unzip every data/*/*.csv.gz and raw/*.gz by hand, next to itself)
*   2. Set the path to the repository root on the line "global ROOT" below.
*   3. Stata 16 or newer.
*
* WHAT IT PRODUCES
*   stata/facts_and_figures.log   the log with every number
*   stata/stata_facts.csv         every number in one table, next to the value
*                                 our Python mirror (stata/verify_facts.py)
*                                 gives, with OK or CHECK in the last column
*   stata/figures/fig1 ... fig7   the figures, as PNG
*
* NOT REPRODUCED HERE (not from our data, the numbers came from Sultan's side):
*   - CEPII GeoDep counts (361 products, USD 47bn, China leads 190)
*   - "1,394 products have had a big supplier". With our rule at HS4 the count
*     is 937 of 1,241 products (fact F14 below). 1,394 must use another
*     product level or rule. Check before presenting.
*   - "US share of new arms orders fell 59 points in the UAE and in Saudi
*     Arabia". We have no Saudi SIPRI data.
*   - "US share of new orders 66% to 7%, 2021". Our SIPRI download gives 62%
*     (orders 2016-2020) to 1% (orders in 2021), using the TIV of each whole
*     order, and it only has deals with at least one delivery by 2025.
*==============================================================================

version 16
clear all
set more off
set type double

* >>> EDIT THIS LINE: the folder that holds README.md, data/, output/ ... <<<
global ROOT "C:/Users/shaba/Downloads/capstone"
cd "$ROOT"

capture mkdir "stata/figures"
capture log close
log using "stata/facts_and_figures.log", text replace

* stop early if the zipped files were not unpacked
foreach f in "data/baci/baci_uae_imports_hs4_ALL_products_1995_2024.csv" ///
             "data/baci/baci_uae_imports_hs6_strategic_1995_2024.csv" ///
             "raw/sipri_register_uae.txt" {
    capture confirm file "`f'"
    if _rc {
        di as error "Missing `f'. Run  python3 scripts/unpack_raw.py  from the repository root first."
        exit 601
    }
}

* colours used in every figure
local c1 "42 120 214"
local c2 "235 104 52"
local c3 "27 175 122"
local c4 "237 161 0"
local grey "181 179 173"

*------------------------------------------------------------------------------
* Helper programs
*------------------------------------------------------------------------------

* Product codes lose their leading zero if Stata reads them as numbers.
capture program drop fixcode
program define fixcode
    args var width
    capture confirm numeric variable `var'
    if !_rc {
        tostring `var', replace format(%0`width'.0f)
    }
end

* Every fact goes into one table so it can be checked at the end.
postfile facts str12 id str90 fact double value str10 unit ///
    using "stata/stata_facts.dta", replace

capture program drop addfact
program define addfact
    syntax , id(string) label(string) value(real) [unit(string)]
    post facts ("`id'") ("`label'") (`value') ("`unit'")
    di as text %-10s "`id'" %-78s "`label'" as result %10.2f `value' as text " `unit'"
end

* Share (%) of one supplier in UAE imports of one product in one year.
* Works on whatever BACI file is in memory (needs value_kusd, exporter_iso3, year).
capture program drop getshare
program define getshare, rclass
    syntax , codevar(name) code(string) sup(string) year(integer)
    quietly summarize value_kusd if `codevar' == "`code'" & year == `year', meanonly
    local tot = r(sum)
    quietly summarize value_kusd if `codevar' == "`code'" & year == `year' & exporter_iso3 == "`sup'", meanonly
    local own = r(sum)
    return scalar share = 100 * `own' / `tot'
end

* Builds the yearly share series for one case and adds it to $PANELS (figure 2).
global PANELS "stata/figures/_panels.dta"
clear
gen year = .
gen share = .
gen str60 case = ""
gen shock = .
save "$PANELS", emptyok replace

capture program drop sharets
program define sharets
    syntax , codevar(name) code(string) sup(string) case(string) shock(integer)
    preserve
    keep if `codevar' == "`code'" & inrange(year, 1995, 2023)
    gen own = value_kusd * (exporter_iso3 == "`sup'")
    collapse (sum) own value_kusd, by(year)
    gen share = 100 * own / value_kusd
    gen str60 case = "`case'"
    gen shock = `shock'
    keep year share case shock
    append using "$PANELS"
    save "$PANELS", replace
    restore
end


*==============================================================================
* 1. BACI, strategic products at HS4 (slides 3 and 7)
*==============================================================================
import delimited using "data/baci/baci_uae_imports_hs4_strategic_1995_2024.csv", ///
    clear case(lower) encoding("utf-8")
fixcode hs4 4

* F01: in how many of the 59 strategic products does one supplier hold > 50%?
preserve
keep if year == 2023
collapse (sum) value_kusd, by(hs4 exporter_iso3)
bysort hs4: egen tot = total(value_kusd)
gen s = value_kusd / tot
collapse (max) top = s, by(hs4)
quietly count
addfact, id(F01a) label("Strategic HS4 products with UAE imports in 2023") value(`r(N)')
quietly count if top > 0.5
addfact, id(F01b) label("Of which top supplier has more than 50% (2023)") value(`r(N)')
restore

* F02, F04: China in computers and phones
getshare, codevar(hs4) code(8471) sup(CHN) year(2023)
addfact, id(F02) label("China share of UAE computer imports (8471), 2023") value(`r(share)') unit(pct)
getshare, codevar(hs4) code(8525) sup(CHN) year(2019)
addfact, id(F04a) label("China share of UAE phone imports (8525 in HS92), 2019") value(`r(share)') unit(pct)
getshare, codevar(hs4) code(8525) sup(CHN) year(2023)
addfact, id(F04b) label("China share of UAE phone imports (8525 in HS92), 2023") value(`r(share)') unit(pct)

* F09: India and Russia in wheat
foreach y in 2021 2022 2023 {
    getshare, codevar(hs4) code(1001) sup(IND) year(`y')
    local l = cond(`y' == 2021, "a", cond(`y' == 2022, "b", "c"))
    addfact, id(F09`l') label("India share of UAE wheat imports (1001), `y'") value(`r(share)') unit(pct)
}
getshare, codevar(hs4) code(1001) sup(RUS) year(2022)
addfact, id(F09d) label("Russia share of UAE wheat imports, 2022") value(`r(share)') unit(pct)
getshare, codevar(hs4) code(1001) sup(RUS) year(2023)
addfact, id(F09e) label("Russia share of UAE wheat imports, 2023") value(`r(share)') unit(pct)

* F10: Ukraine in sunflower oil
getshare, codevar(hs4) code(1512) sup(UKR) year(2021)
addfact, id(F10a) label("Ukraine share of UAE sunflower oil imports (1512), 2021") value(`r(share)') unit(pct)
getshare, codevar(hs4) code(1512) sup(UKR) year(2022)
addfact, id(F10b) label("Ukraine share of UAE sunflower oil imports (1512), 2022") value(`r(share)') unit(pct)

* series for figure 2
sharets, codevar(hs4) code(8471) sup(CHN) case("China, computers (8471)") shock(2020)
sharets, codevar(hs4) code(8525) sup(CHN) case("China, phones (8525)") shock(2020)
sharets, codevar(hs4) code(1001) sup(IND) case("India, wheat (1001)") shock(2022)
sharets, codevar(hs4) code(1512) sup(UKR) case("Ukraine, sunflower oil (1512)") shock(2022)


*==============================================================================
* 2. BACI, all goods by HS2: China's share of UAE imports (slide 3)
*==============================================================================
import delimited using "data/baci/baci_uae_imports_hs2_all_1995_2024.csv", ///
    clear case(lower) encoding("utf-8")
keep if year <= 2023
gen chn = value_kusd * (exporter_iso3 == "CHN")
collapse (sum) chn value_kusd, by(year)
gen share = 100 * chn / value_kusd

quietly summarize share if inrange(year, 1995, 1999)
addfact, id(F03a) label("China share of all UAE goods imports, average 1995-1999") value(`r(mean)') unit(pct)
quietly summarize share if year == 2023
addfact, id(F03b) label("China share of all UAE goods imports, 2023") value(`r(mean)') unit(pct)
quietly summarize value_kusd if year == 2023
addfact, id(F03c) label("UAE goods imports, 2023") value(`=r(mean)/1e6') unit(USD bn)

* Figure 1
twoway (line share year, lcolor("`c1'") lwidth(medthick)), ///
    ytitle("% of all UAE goods imports") xtitle("") ylabel(0(5)25, angle(0)) ///
    xlabel(1995(5)2020 2023) ///
    title("China's share of UAE goods imports, 1995-2023", size(medium)) ///
    note("Source: CEPII BACI HS92 V202601, UAE imports from all suppliers.", size(vsmall)) ///
    graphregion(color(white)) plotregion(color(white)) legend(off)
graph export "stata/figures/fig1_china_share_of_uae_imports.png", replace width(2000)


*==============================================================================
* 3. BACI, strategic products at HS6: Japan's truck line (slides 2 and 7)
*==============================================================================
import delimited using "data/baci/baci_uae_imports_hs6_strategic_1995_2024.csv", ///
    clear case(lower) encoding("utf-8")
fixcode hs6 6
getshare, codevar(hs6) code(870422) sup(JPN) year(2009)
addfact, id(F05a) label("Japan share of UAE imports of trucks 870422, 2009") value(`r(share)') unit(pct)
getshare, codevar(hs6) code(870422) sup(JPN) year(2010)
addfact, id(F05b) label("Japan share of UAE imports of trucks 870422, 2010") value(`r(share)') unit(pct)
sharets, codevar(hs6) code(870422) sup(JPN) case("Japan, trucks (870422)") shock(2011)


*==============================================================================
* 4. BACI, every product at HS4: Iran's steel, and the big-supplier screen
*==============================================================================
import delimited using "data/baci/baci_uae_imports_hs4_ALL_products_1995_2024.csv", ///
    clear case(lower) encoding("utf-8")
fixcode hs4 4

getshare, codevar(hs4) code(7207) sup(IRN) year(2018)
addfact, id(F06a) label("Iran share of UAE semi-finished steel imports (7207), 2018") value(`r(share)') unit(pct)
getshare, codevar(hs4) code(7207) sup(IRN) year(2019)
addfact, id(F06b) label("Iran share of UAE semi-finished steel imports (7207), 2019") value(`r(share)') unit(pct)
sharets, codevar(hs4) code(7207) sup(IRN) case("Iran, semi-finished steel (7207)") shock(2019)

* --- The big-supplier screen (same rules as scripts/big_supplier_thresholds.py)
*   Big:  share >= threshold in the year before the drop, and in at least one
*         of the two years before that.
*   Drop: product worth >= USD 30m the year before, share down >= 15 points,
*         supplier's value down >= a third (log change <= -0.4).
keep if year <= 2023
collapse (sum) v = value_kusd, by(hs4 exporter_iso3 year)

* balanced panel: every supplier-product pair in every year, zero if no trade
egen long pair = group(hs4 exporter_iso3)
fillin pair year
bysort pair (hs4): replace hs4 = hs4[_N]
bysort pair (exporter_iso3): replace exporter_iso3 = exporter_iso3[_N]
replace v = 0 if missing(v)
drop _fillin

* total UAE imports of the product (missing in years with no trade at all)
bysort hs4 year: egen T = total(v)
replace T = . if T == 0
gen s = v / T

xtset pair year
gen s_l1 = L.s
gen s_l2 = L2.s
gen s_l3 = L3.s
gen T_l1 = L.T
gen v_l1 = L.v
gen v_f1 = F.v
gen T_f1 = F.T

* F14: how many products ever had a big supplier at 50%
gen byte big50 = !missing(s) & s >= 0.5 & ((!missing(s_l1) & s_l1 >= 0.5) | (!missing(s_l2) & s_l2 >= 0.5))
preserve
keep if big50
bysort hs4: keep if _n == 1
quietly count
addfact, id(F14) label("HS4 products with a big supplier (50%, 2 of 3 years) at least once") value(`r(N)')
restore
preserve
bysort hs4: keep if _n == 1
quietly count
addfact, id(F14b) label("HS4 products in the data") value(`r(N)')
restore

* keep the drops
gen byte isdrop = !missing(T_l1) & T_l1 >= 30000 & !missing(s) & !missing(s_l1) ///
    & (s - s_l1) <= -0.15 & (ln(max(v, 1)) - ln(max(v_l1, 1))) <= -0.4
keep if isdrop

* supplier-wide or not (from the switch screen, which compares with exports to
* the rest of the world)
preserve
import delimited using "output/table_supplier_switch_screen_all_products.csv", ///
    clear case(lower) encoding("utf-8")
fixcode hs4 4
rename exporter exporter_iso3
keep year hs4 exporter_iso3 type
tempfile scr
save `scr'
restore
merge m:1 year hs4 exporter_iso3 using `scr', keep(master match) nogen

* outcomes: share of the loss made up by other suppliers by the next year,
* and the change in total UAE imports of the product by the next year
gen repl1 = ((T_f1 - v_f1) - (T_l1 - v_l1)) / (v_l1 - v)
gen tot1  = T_f1 / T_l1 - 1
drop if inrange(year, 2013, 2016)     // years the UAE booked a third of imports as "unspecified"

tempname thr
tempfile thrres
postfile `thr' th n nsw med_all med_sw tot_all tot_sw using `thrres', replace
foreach th in 20 30 40 50 {
    local t = `th' / 100
    gen byte big = !missing(s_l1) & s_l1 >= `t' & ((!missing(s_l2) & s_l2 >= `t') | (!missing(s_l3) & s_l3 >= `t'))
    gen byte sw = big & type == "supplier-wide drop"
    quietly count if big
    local n = r(N)
    quietly count if sw
    local nsw = r(N)
    quietly summarize repl1 if big, detail
    local ma = 100 * r(p50)
    quietly summarize tot1 if big, detail
    local ta = 100 * r(p50)
    quietly summarize repl1 if sw, detail
    local ms = 100 * r(p50)
    quietly summarize tot1 if sw, detail
    local ts = 100 * r(p50)
    addfact, id(F12n`th') label("Big-supplier drops at `th'% (1996-2023 excl. 2013-16)") value(`n')
    addfact, id(F12ra`th') label("  median share of loss replaced by next year, all drops") value(`ma') unit(pct)
    addfact, id(F12ta`th') label("  median change in total UAE imports by next year, all drops") value(`ta') unit(pct)
    addfact, id(F12w`th') label("  of which supplier-wide") value(`nsw')
    addfact, id(F12r`th') label("  median share of loss replaced by next year, supplier-wide") value(`ms') unit(pct)
    addfact, id(F12t`th') label("  median change in total UAE imports by next year, supplier-wide") value(`ts') unit(pct)
    post `thr' (`th') (`n') (`nsw') (`ma') (`ms') (`ta') (`ts')
    drop big sw
}
postclose `thr'

* Figure 6: results at each threshold
use `thrres', clear
twoway (connected med_all th, lcolor("`c1'") mcolor("`c1'")) ///
       (connected med_sw th, lcolor("`c2'") mcolor("`c2'")), ///
    xlabel(20 "20%" 30 "30%" 40 "40%" 50 "50%") ylabel(0(5)30, angle(0)) ///
    xtitle("Threshold for a big supplier (share of UAE imports)") ///
    ytitle("% of the loss made up by others") yline(0, lcolor(gs10)) ///
    legend(order(1 "All drops" 2 "Supplier-wide drops") rows(1) position(6)) ///
    title("Share of a big supplier's loss made up by others by the next year (median)", size(medsmall)) name(g6a, replace) nodraw ///
    graphregion(color(white)) plotregion(color(white))
twoway (connected tot_all th, lcolor("`c1'") mcolor("`c1'")) ///
       (connected tot_sw th, lcolor("`c2'") mcolor("`c2'")), ///
    xlabel(20 "20%" 30 "30%" 40 "40%" 50 "50%") ylabel(-60(10)0, angle(0)) ///
    xtitle("Threshold for a big supplier (share of UAE imports)") ///
    ytitle("% change") yline(0, lcolor(gs10)) ///
    legend(order(1 "All drops" 2 "Supplier-wide drops") rows(1) position(6)) ///
    title("Change in total UAE imports of the product by the next year (median)", size(medsmall)) name(g6b, replace) nodraw ///
    graphregion(color(white)) plotregion(color(white))
graph combine g6a g6b, cols(2) xsize(12) ysize(5) graphregion(color(white)) ///
    note("Source: CEPII BACI HS92, HS4, 1996-2023 excluding 2013-16. Drop: share down 15+ points and value down a third or more, product >= USD 30m.", size(vsmall))
graph export "stata/figures/fig6_big_supplier_thresholds.png", replace width(2400)


*==============================================================================
* 5. BACI, exports to each Gulf country: India's share of Gulf wheat (slide 9)
*==============================================================================
import delimited using "data/baci/baci_strategic_hs4_exports_by_exporter_to_world_and_gcc_1995_2024.csv", ///
    clear case(lower) encoding("utf-8")
fixcode hs4 4
keep if hs4 == "1001" & year == 2021 & destination != "WLD"
gen ind = value_kusd * (exporter_iso3 == "IND")
collapse (sum) ind value_kusd, by(destination)
gen share = 100 * ind / value_kusd
foreach d in ARE SAU OMN KWT QAT BHR {
    quietly summarize share if destination == "`d'"
    addfact, id(F11`d') label("India share of `d' wheat imports, 2021") value(`r(mean)') unit(pct)
}
* Figure 5
graph hbar share, over(destination, sort(share) descending) ///
    bar(1, color("`c1'")) blabel(bar, format(%4.1f)) ///
    ytitle("India's share of the country's wheat imports, 2021 (%)") ///
    title("Before the ban, the UAE relied on Indian wheat far more than its neighbours", size(medsmall)) ///
    note("Source: CEPII BACI HS92, wheat (1001), 2021.", size(vsmall)) ///
    graphregion(color(white)) plotregion(color(white))
graph export "stata/figures/fig5_india_wheat_share_gulf_2021.png", replace width(2000)


*==============================================================================
* 6. UN Comtrade monthly: Japan earthquake 2011, cars (slides 2 and 7)
*==============================================================================
import delimited using "data/comtrade/comtrade_monthly_exports_to_uae_by_reporter.csv", ///
    clear case(lower) encoding("utf-8")
fixcode cmdcode 4
keep if cmdcode == "8703"
gen m = monthly(month, "YM")
format m %tm
collapse (sum) primaryvalue, by(reporteriso m)
gen vm = primaryvalue / 1e6

quietly summarize vm if reporteriso == "JPN" & inrange(m, tm(2010m10), tm(2011m3))
local pre = r(mean)
quietly summarize vm if reporteriso == "JPN" & inrange(m, tm(2011m4), tm(2011m5))
local dur = r(mean)
addfact, id(F07a) label("Japan car exports to UAE, monthly avg Oct 2010-Mar 2011") value(`pre') unit(USD m)
addfact, id(F07b) label("Japan car exports to UAE, monthly avg Apr-May 2011") value(`dur') unit(USD m)
addfact, id(F07c) label("Change") value(`=100*(`dur'/`pre'-1)') unit(pct)

* Figure 3
keep if inrange(m, tm(2010m6), tm(2012m6))
twoway (line vm m if reporteriso == "JPN", lcolor("`c1'") lwidth(medthick)) ///
       (line vm m if reporteriso == "USA", lcolor("`c2'")) ///
       (line vm m if reporteriso == "GBR", lcolor("`c3'")) ///
       (line vm m if reporteriso == "THA", lcolor("`c4'")), ///
    xline(`=tm(2011m4)' `=tm(2011m5)', lcolor(gs13) lwidth(vthick)) ///
    ytitle("USD million per month") xtitle("") ylabel(, angle(0)) ///
    legend(order(1 "Japan" 2 "United States" 3 "United Kingdom" 4 "Thailand") rows(1) position(6)) ///
    title("Car exports to the UAE around the March 2011 earthquake", size(medium)) ///
    note("Source: UN Comtrade, monthly exports to the UAE reported by each supplier (HS 8703). Shaded: Apr-May 2011." ///
         "Korea is not in the monthly data before 2013.", size(vsmall)) ///
    graphregion(color(white)) plotregion(color(white))
graph export "stata/figures/fig3_japan_cars_monthly_2011.png", replace width(2000)


*==============================================================================
* 7. UN Comtrade monthly: China, February 2020 (slides 2 and 7)
*==============================================================================
import delimited using "data/comtrade/comtrade_monthly_exports_to_uae_new_sectors_and_totals_2010_2026.csv", ///
    clear case(lower) encoding("utf-8")
keep if cmdcode == "TOTAL"
gen m = monthly(month, "YM")
format m %tm
collapse (sum) primaryvalue, by(reporteriso m)
gen vb = primaryvalue / 1e9
tempfile totals
save `totals'

* February compared with the two months on each side (Dec, Jan, Mar, Apr).
* A normal February is already lower because of Chinese New Year.
keep if reporteriso == "CHN"
tsset m
gen ratio = vb / ((L2.vb + L1.vb + F1.vb + F2.vb) / 4)
gen yr = year(dofm(m))
keep if month(dofm(m)) == 2
quietly summarize vb if yr == 2020
addfact, id(F08a) label("China exports to UAE, Feb 2020") value(`r(mean)') unit(USD bn)
quietly summarize ratio if yr == 2020
addfact, id(F08b) label("Feb 2020 / avg of Dec, Jan, Mar, Apr") value(`r(mean)')
quietly summarize ratio if yr != 2020 & inrange(yr, 2011, 2024)
local lo = r(min)
local hi = r(max)
local ny = r(N)
addfact, id(F08c) label("Same ratio in other years: lowest") value(`lo')
addfact, id(F08d) label("Same ratio in other years: highest") value(`hi')
addfact, id(F08e) label("Same ratio in other years: number of years") value(`ny')

* Figure 4
use `totals', clear
keep if inrange(m, tm(2019m1), tm(2021m12)) & inlist(reporteriso, "CHN", "IND", "USA", "DEU")
twoway (line vb m if reporteriso == "CHN", lcolor("`c1'") lwidth(medthick)) ///
       (line vb m if reporteriso == "IND", lcolor("`c2'")) ///
       (line vb m if reporteriso == "USA", lcolor("`c3'")) ///
       (line vb m if reporteriso == "DEU", lcolor("`c4'")), ///
    xline(`=tm(2019m2)' `=tm(2020m2)' `=tm(2021m2)', lcolor(gs14) lwidth(vthick)) ///
    ytitle("USD billion per month") xtitle("") ylabel(, angle(0)) ///
    legend(order(1 "China" 2 "India" 3 "United States" 4 "Germany") rows(1) position(6)) ///
    title("Exports to the UAE by supplier, monthly (shaded: February)", size(medium)) ///
    note("Source: UN Comtrade, total exports to the UAE reported by each supplier.", size(vsmall)) ///
    graphregion(color(white)) plotregion(color(white))
graph export "stata/figures/fig4_china_feb2020_monthly.png", replace width(2000)


*==============================================================================
* 8. SIPRI: US share of UAE arms deliveries and orders (slide 7)
*    SIPRI TIV is a volume index, not money.
*==============================================================================
* deliveries by year (columns by position: 2 supplier, 11 delivery year, 16 TIV)
import delimited using "data/sipri/sipri_uae_arms_imports_deliveries_by_year.csv", ///
    clear varnames(nonames) rowrange(2) encoding("utf-8")
rename v2 supplier
rename v11 dyear
rename v16 tiv
destring dyear tiv, replace force
gen us = tiv * (supplier == "United States")
gen period = .
replace period = 2006 if inrange(dyear, 2006, 2010)
replace period = 2011 if inrange(dyear, 2011, 2015)
replace period = 2016 if inrange(dyear, 2016, 2020)
replace period = 2021 if inrange(dyear, 2021, 2025)
replace period = 2001 if inrange(dyear, 2001, 2005)
keep if !missing(period)
collapse (sum) us tiv, by(period)
gen share = 100 * us / tiv
foreach p in 2006 2011 2016 {
    quietly summarize share if period == `p'
    addfact, id(F13_`p') label("US share of UAE arms deliveries (TIV), `p'-`=`p'+4'") value(`r(mean)') unit(pct)
}
* Figure 7
gen str9 lab = string(period) + "-" + substr(string(period + 4), 3, 2)
graph bar share, over(lab) bar(1, color("`c1'")) blabel(bar, format(%4.0f)) ///
    ytitle("US share of UAE arms deliveries (%)") ylabel(0(20)100, angle(0)) ///
    title("US share of major arms deliveries to the UAE, by 5-year period", size(medium)) ///
    note("Source: SIPRI Arms Transfers Database, trend-indicator values (a volume index, not money).", size(vsmall)) ///
    graphregion(color(white)) plotregion(color(white))
graph export "stata/figures/fig7_sipri_us_share.png", replace width(2000)

* orders, from the register (columns by position: 1 recipient, 2 supplier,
* 3 year of order, 15 SIPRI TIV for the total order, 16 TIV delivered so far). Only deals with at least one delivery by 2025 are
* in our download, so recent orders not yet delivered (for example the 80
* Rafale jets ordered in Dec 2021) are missing. Treat order shares as partial.
* the data rows start on line 17 of the file (lines 1-16 are SIPRI's notes and the header)
import delimited using "raw/sipri_register_uae.txt", clear delimiters(tab) ///
    varnames(nonames) rowrange(17) bindquotes(nobind) stripquotes(no) encoding("utf-8")
keep if v1 == "United Arab Emirates"
rename v2 supplier
destring v3 v15, replace force
rename v3 oyear
rename v15 tiv
gen us = tiv * (supplier == "United States")
quietly summarize us if inrange(oyear, 2016, 2020)
local u = r(sum)
quietly summarize tiv if inrange(oyear, 2016, 2020)
addfact, id(F13o_2016) label("US share of UAE arms orders (TIV of order), 2016-2020") value(`=100*`u'/r(sum)') unit(pct)
quietly summarize us if oyear == 2021
local u = r(sum)
quietly summarize tiv if oyear == 2021
addfact, id(F13o_2021) label("US share of UAE arms orders (TIV of order), 2021-2021") value(`=100*`u'/r(sum)') unit(pct)


*==============================================================================
* 9. Figure 2: supplier share over time for the six cases on the slides
*==============================================================================
use "$PANELS", clear
levelsof case, local(cases)
local i = 0
local names ""
foreach c of local cases {
    local ++i
    quietly summarize shock if case == "`c'", meanonly
    local sy = r(mean)
    twoway (line share year if case == "`c'", lcolor("`c1'") lwidth(medthick)), ///
        xline(`sy', lcolor(gs13) lwidth(vthick)) ///
        ylabel(0(20)100, angle(0)) xlabel(1995(10)2015 2023) ///
        ytitle("% of UAE imports") xtitle("") title("`c'", size(medsmall)) ///
        name(p`i', replace) nodraw graphregion(color(white)) plotregion(color(white))
    local names "`names' p`i'"
}
graph combine `names', cols(3) xsize(12) ysize(7) graphregion(color(white)) ///
    title("The big supplier's share of UAE imports (shaded: shock year)", size(medium)) ///
    note("Source: CEPII BACI HS92 V202601. Trucks at HS6, the rest at HS4.", size(vsmall))
graph export "stata/figures/fig2_big_supplier_cases.png", replace width(2400)
erase "$PANELS"


*==============================================================================
* 10. One table with every number, checked against the Python mirror
*==============================================================================
postclose facts
import delimited using "stata/expected_facts.csv", clear case(lower) encoding("utf-8") stringcols(1)
keep id value
rename value expected
tempfile exp
save `exp'
use "stata/stata_facts.dta", clear
merge 1:1 id using `exp', nogen
gen str10 check = "no expected"
replace check = "OK"    if !missing(expected) & abs(value - expected) <= 0.011
replace check = "CHECK" if !missing(expected) & abs(value - expected) >  0.011
replace value = round(value, 0.01)
list id fact value unit expected check, noobs sep(0) abbreviate(12) string(70)
export delimited using "stata/stata_facts.csv", replace
erase "stata/stata_facts.dta"

quietly count if check == "CHECK"
if r(N) > 0 di as error "`r(N)' numbers differ from the Python mirror. Look at the CHECK rows."
else di as result "All numbers match the Python mirror."

log close
