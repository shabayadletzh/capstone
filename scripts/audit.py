import pandas as pd, numpy as np
pd.set_option('display.width',220)
out=[]
def P(*a):
    s=' '.join(str(x) for x in a); print(s); out.append(s)
# 1. BACI totals vs UAE-reported Comtrade totals
b2=pd.read_csv('data/baci/baci_uae_imports_hs2_all_1995_2024.csv',dtype={'hs2':str})
bt=b2.groupby('year').agg(baci_bn=('value_kusd',lambda x:x.sum()/1e6),n_suppliers=('exporter_iso3','nunique'))
ct=pd.read_csv('data/comtrade/comtrade_uae_reported_imports_total_by_partner_annual.csv',dtype={'period':str})
w=ct[ct.partnerCode==0].assign(year=lambda d:d.period.astype(int)).set_index('year').primaryValue/1e9
bt['uae_reported_cif_bn']=w; bt['ratio_baci_to_reported']=bt.baci_bn/bt.uae_reported_cif_bn
# partner count in UAE-reported
bt['uae_reported_n_partners']=ct[ct.partnerCode!=0].assign(year=lambda d:d.period.astype(int)).groupby('year').partnerCode.nunique()
P('== 1. Annual totals: BACI vs UAE-reported (Comtrade) =='); P(bt.round(2).to_string())
bt.round(3).to_csv('audit/audit_annual_totals_baci_vs_uae_reported.csv')
# 2. Bilateral agreement BACI vs UAE-reported by partner, 2019 & 2023
P('\n== 2. Partner-level agreement BACI vs UAE-reported total imports ==')
rows=[]
for y in [2005,2010,2015,2019,2022,2023]:
    a=b2[b2.year==y].groupby('exporter_iso3').value_kusd.sum()/1e6
    c=ct[(ct.period==str(y))&(ct.partnerCode!=0)].groupby('partnerISO').primaryValue.sum()/1e9
    j=pd.concat([a.rename('baci'),c.rename('rep')],axis=1).dropna(); j=j[j.rep>0.5]
    corr=np.corrcoef(np.log(j.baci.clip(lower=1e-3)),np.log(j.rep))[0,1]
    rows.append({'year':y,'partners_over_$0.5bn':len(j),'log_corr':round(corr,3),'median_ratio':round((j.baci/j.rep).median(),2)})
r=pd.DataFrame(rows); P(r.to_string(index=False)); r.to_csv('audit/audit_partner_agreement.csv',index=False)
# 3. Mirror monthly coverage: share of UAE imports (BACI) from the 29 reporters
m=pd.read_csv('data/comtrade/comtrade_monthly_exports_to_uae_by_reporter.csv',dtype={'cmdCode':str,'period':str})
reps=set(m.reporterISO)
h4=pd.read_csv('data/baci/baci_uae_imports_hs4_strategic_1995_2024.csv',dtype={'hs4':str})
P('\n== 3. Share of UAE imports (BACI, all goods) coming from the 29 monthly reporters ==')
cov=[]
for y in [2010,2015,2019,2023]:
    d=b2[b2.year==y]; cov.append({'year':y,'share_all_goods':round(d[d.exporter_iso3.isin(reps)].value_kusd.sum()/d.value_kusd.sum(),3),
      'share_strategic_excl_gold_fuel':round((lambda e:e[e.exporter_iso3.isin(reps)].value_kusd.sum()/e.value_kusd.sum())(h4[(h4.year==y)&(~h4.hs4.isin(['7108','7102','7113','2710']))]),3)})
c=pd.DataFrame(cov); P(c.to_string(index=False))
# 4. Mirror monthly vs BACI annual, reporter x HS4 x year
m['year']=m.period.str[:4].astype(int); m['hs4']=m.cmdCode.str[:4]
mm=m[m.cmdCode.str.len()==4].groupby(['reporterISO','hs4','year']).agg(mirror_musd=('primaryValue',lambda x:x.sum()/1e6),months=('period','nunique')).reset_index()
bb=h4.groupby(['exporter_iso3','hs4','year']).value_kusd.sum().div(1e3).rename('baci_musd').reset_index().rename(columns={'exporter_iso3':'reporterISO'})
j=mm.merge(bb,on=['reporterISO','hs4','year'],how='inner'); j=j[(j.months==12)&(j.baci_musd>=10)&(j.year<=2023)]
j['ratio']=j.mirror_musd/j.baci_musd
P('\n== 4. Monthly mirror (summed to year, full 12 months) vs BACI annual, pairs >= $10m ==')
P('pairs:',len(j),' median ratio:',round(j.ratio.median(),3),' share within +/-20%:',round(((j.ratio>0.8)&(j.ratio<1.2)).mean(),3),' log corr:',round(np.corrcoef(np.log(j.mirror_musd.clip(lower=1e-3)),np.log(j.baci_musd))[0,1],3))
g=j.groupby('reporterISO').ratio.agg(['median','count']).round(2).sort_values('count',ascending=False); P(g.head(20).to_string())
j.to_csv('audit/audit_mirror_monthly_vs_baci.csv',index=False)
# 5. Missing vs zero in monthly
covm=m.groupby(['reporterISO','period']).size().unstack(fill_value=0)
P('\n== 5. Monthly reporter coverage ==')
cr=m.groupby('reporterISO').period.agg(['min','max','nunique']); P(cr.to_string())
# 6. Eurostat vs BACI for EU exporters
e=pd.read_csv('data/eurostat/eurostat_comext_monthly_exports_to_UAE_total_and_hs2.csv',dtype={'product':str})
et=e[e['product']=='TOTAL'].assign(year=lambda d:d.month.str[:4].astype(int)).groupby('year').value_eur.sum()/1e9
P('\n== 6. Eurostat EU27+UK total exports to UAE by year (bn EUR) =='); P(et.round(1).to_string())
open('audit/audit_log.txt','w').write('\n'.join(out))
