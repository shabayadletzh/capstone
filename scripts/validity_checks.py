# Identification checks for the shortlisted cases.
import pandas as pd, numpy as np
out=open('audit/validity_checks_log.txt','w')
def P(*a):
    s=' '.join(str(x) for x in a); print(s); out.write(s+'\n')
m=pd.read_csv('data/comtrade/comtrade_monthly_exports_to_uae_by_reporter.csv',dtype={'cmdCode':str})
m['cmdCode']=m.cmdCode.str[:4]
cov=pd.read_csv('data/comtrade/comtrade_monthly_coverage_reporter_month.csv')
CASES=[('Japan quake, cars','JPN','8703','2011-03',3),('Thailand floods, trucks','THA','8704','2011-10',3),
       ('India wheat ban','IND','1001','2022-09',12),('Indonesia palm oil ban','IDN','1511','2022-05',1),
       ('Ukraine war, sunflower oil','UKR','1512','2022-03',10),('India onion ban','IND','0703','2023-12',5)]
P('== A. Placebo in time: is the shock-window drop unusual for this supplier and product? ==')
P('drop = log(avg monthly value in shock window / avg of the 12 months before). Placebo = the same statistic at every other start month 2010-2026 for the same pair, excluding windows that overlap the shock.')
rows=[]
for name,s,k,start,L in CASES:
    g=m[(m.reporterISO==s)&(m.cmdCode==k)].groupby('month').primaryValue.sum()
    months=cov[cov.reporterISO==s].month.sort_values().tolist()
    g=g.reindex(months).fillna(0)   # reporter reported that month, product absent = 0
    idx=pd.PeriodIndex(g.index,freq='M'); g.index=idx
    full=pd.period_range(idx.min(),idx.max(),freq='M'); g=g.reindex(full)  # months reporter did not report stay NaN
    def stat(t0):
        pre=g[t0-12:t0-1]; post=g[t0:t0+L-1]
        if pre.isna().sum()>2 or post.isna().any() or pre.mean()<=0: return np.nan
        return np.log(max(post.mean(),1)/pre.mean())
    t0=pd.Period(start,freq='M'); obs=stat(t0)
    plac=[stat(t) for t in full[12:len(full)-L] if abs((t-t0).n)>12+L]
    plac=np.array([x for x in plac if not np.isnan(x)])
    pct=(plac<=obs).mean()*100
    # pre-trend: last 6 vs earlier 6 pre-months
    pre=g[t0-12:t0-1]; pt=np.log(pre[-6:].mean()/pre[:6].mean())
    rows.append(dict(case=name,supplier=s,hs4=k,shock_start=start,window_months=L,drop_log=round(obs,2),drop_pct=round((np.exp(obs)-1)*100,0),
        placebo_windows=len(plac),share_of_placebos_as_bad_or_worse_pct=round(pct,1),pre_trend_last6_vs_first6_pct=round((np.exp(pt)-1)*100,0)))
A=pd.DataFrame(rows); P(A.to_string(index=False)); A.to_csv('audit/validity_placebo_and_pretrend.csv',index=False)

P('\n== B. Supply or demand? Shocked supplier exports to the UAE vs to the rest of the world, and total UAE imports of the product (BACI, log changes) ==')
w=pd.read_csv('data/baci/baci_strategic_hs4_exports_by_exporter_to_world_and_gcc_1995_2024.csv',dtype={'hs4':str})
f=pd.read_csv('data/baci/baci_switch_flagged_pairs_exports_to_world_and_gcc_1995_2024.csv',dtype={'hs4':str}); f['hs4']=f.hs4.str.zfill(4)
allp=pd.read_csv('data/baci/baci_uae_imports_hs4_ALL_products_1995_2024.csv',dtype={'hs4':str})
B=[('Japan quake, cars','JPN','8703',2010,2011),('India wheat ban','IND','1001',2021,2023),('Ukraine war, sunflower oil','UKR','1512',2021,2022),
   ('Ukraine war, pig iron','UKR','7201',2021,2022),('Iran sanctions 2012, polyethylene','IRN','3901',2011,2012),('Iran sanctions 2018-19, semi-finished steel','IRN','7207',2018,2019),
   ('India onion ban','IND','0703',2022,2024),('Indonesia palm oil ban','IDN','1511',2021,2022)]
rb=[]
for name,s,k,t0,t1 in B:
    src=w if k in set(w.hs4) else f.rename(columns={'destination':'destination'})
    g=src[(src.hs4==k)&(src.exporter_iso3==s)].pivot_table(index='year',columns='destination',values='value_kusd',aggfunc='sum').fillna(0)
    if g.empty or t0 not in g.index or t1 not in g.index: P('missing',name); continue
    row=lambda y: g.loc[y,'WLD']-g.loc[y,'ARE']
    gcc=lambda y: g.loc[y,[c for c in ['SAU','OMN','KWT','QAT','BHR'] if c in g.columns]].sum()
    tot=allp[allp.hs4==k].groupby('year').value_kusd.sum()
    tot_ex=lambda y: tot[y]-g.loc[y,'ARE']
    rb.append(dict(case=name,supplier=s,hs4=k,years=f'{t0}->{t1}',to_uae_pct=round((g.loc[t1,'ARE']/g.loc[t0,'ARE']-1)*100),
        to_rest_of_world_pct=round((row(t1)/row(t0)-1)*100),to_other_gcc_pct=round((gcc(t1)/gcc(t0)-1)*100) if gcc(t0)>0 else None,
        uae_imports_from_everyone_else_pct=round((tot_ex(t1)/tot_ex(t0)-1)*100)))
Bt=pd.DataFrame(rb); P(Bt.to_string(index=False)); Bt.to_csv('audit/validity_supply_vs_demand.csv',index=False)

P('\n== C. Is it volume or price? Value vs net weight change for the shocked supplier, same windows as A ==')
rc=[]
for name,s,k,start,L in CASES:
    g=m[(m.reporterISO==s)&(m.cmdCode==k)].groupby('month')[['primaryValue','netWgt','qty']].sum()
    g.index=pd.PeriodIndex(g.index,freq='M'); t0=pd.Period(start,freq='M')
    pre=g.loc[(g.index>=t0-12)&(g.index<=t0-1)].sum()/12; post=g.loc[(g.index>=t0)&(g.index<=t0+L-1)].sum()/L
    col='qty' if k in ('8703','8704') else 'netWgt'
    rc.append(dict(case=name,value_change_pct=round((post.primaryValue/pre.primaryValue-1)*100),volume_measure='units' if col=='qty' else 'net weight',
        volume_change_pct=round((post[col]/pre[col]-1)*100) if pre[col]>0 else None))
C=pd.DataFrame(rc); P(C.to_string(index=False)); C.to_csv('audit/validity_value_vs_volume.csv',index=False)

P('\n== D. Balance check for the cross-importer design: does pre-shock exposure predict pre-shock growth of imports from other suppliers? ==')
gm=pd.read_csv('data/comtrade/comtrade_monthly_exports_to_GCC_case_products.csv',dtype={'cmdCode':str})
fl=pd.read_csv('output/table_gcc_cross_importer_monthly_first_look.csv',dtype={'hs4':str})
D=[('Japan quake 2011, cars','8703','JPN','2010-03',['USA','DEU','GBR','THA','CHN']),('India wheat ban 2022','1001','IND','2021-06',['AUS','CAN','TUR','UKR','KAZ','BRA']),
   ('Ukraine war 2022, sunflower oil','1512','UKR','2021-03',['TUR','EGY','IND','MYS','BRA']),('India onion ban 2023-24','0703','IND','2022-12',['PAK','CHN','EGY','TUR'])]
rd=[]
for name,k,s,a,alts in D:
    t=pd.Period(a,freq='M'); h1=[str(t+i) for i in range(0,6)]; h2=[str(t+i) for i in range(6,12)]
    if name.startswith('India onion'):
        h1=[str(t-12+i) for i in range(0,5)]; h2=[str(t+i) for i in range(0,5)]   # same season one year earlier vs pre window (placebo year)
    g=gm[(gm.cmdCode==k)&(gm.reporterISO.isin(alts))]
    x1=g[g.month.isin(h1)].groupby('partnerISO').primaryValue.sum(); x2=g[g.month.isin(h2)].groupby('partnerISO').primaryValue.sum()
    gr=(np.log(x2.clip(lower=1))-np.log(x1.clip(lower=1)))
    e=fl[fl.case==name].set_index('importer').exposure_baci
    j=pd.concat([e,gr.rename('pre_growth')],axis=1).dropna()
    rd.append(dict(case=name,importers=len(j),corr_exposure_vs_pre_growth=round(j.corr().iloc[0,1],2)))
Dd=pd.DataFrame(rd); P(Dd.to_string(index=False)); Dd.to_csv('audit/validity_exposure_balance.csv',index=False)
out.close()
