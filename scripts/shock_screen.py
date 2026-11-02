import pandas as pd, numpy as np
w=pd.read_csv('data/baci/baci_strategic_hs4_exports_by_exporter_to_world_and_gcc_1995_2024.csv',dtype={'hs4':str})
p=w.pivot_table(index=['hs4','exporter_iso3','year'],columns='destination',values='value_kusd',aggfunc='sum').fillna(0).reset_index()
p['ROW']=p.WLD-p.ARE   # supplier exports to everyone except UAE
uae=p.groupby(['hs4','year']).ARE.sum().rename('UAE_TOT').reset_index()
p=p.merge(uae,on=['hs4','year']); p['share']=p.ARE/p.UAE_TOT
# lag = the true previous calendar year (a missing pair-year means no recorded trade = 0)
lag=p[['hs4','exporter_iso3','year','ARE','ROW','share']].copy(); lag['year']+=1
p=p.merge(lag.rename(columns={'ARE':'ARE_lag','ROW':'ROW_lag','share':'share_lag'}),on=['hs4','exporter_iso3','year'],how='left')
tl=uae.copy(); tl['year']+=1; p=p.merge(tl.rename(columns={'UAE_TOT':'UAE_TOT_lag'}),on=['hs4','year'],how='left')
for c in ['ARE_lag','ROW_lag','share_lag']: p.loc[p.UAE_TOT_lag.notna(),c]=p.loc[p.UAE_TOT_lag.notna(),c].fillna(0)
p['dlog_uae']=np.log(p.ARE.clip(lower=1))-np.log(p.ARE_lag.clip(lower=1))
p['dlog_row']=np.log(p.ROW.clip(lower=1))-np.log(p.ROW_lag.clip(lower=1))
p['dlog_uaetot']=np.log(p.UAE_TOT)-np.log(p.UAE_TOT_lag)
p['dlog_uae_others']=np.log((p.UAE_TOT-p.ARE).clip(lower=1))-np.log((p.UAE_TOT_lag-p.ARE_lag).clip(lower=1))
c=p[(p.share_lag>=0.15)&(p.ARE_lag>=20000)&(p.year.between(1996,2023))].copy()
c['flag_supply_side']=(c.dlog_uae<=-0.29)&(c.dlog_row<=-0.22)
c['flag_uae_specific']=(c.dlog_uae<=-0.29)&(c.dlog_row>-0.05)
H4=pd.read_csv('data/baci/baci_uae_imports_hs4_strategic_1995_2024.csv',dtype={'hs4':str})[['hs4','hs4_name','sector']].drop_duplicates()
c=c.merge(H4,on='hs4',how='left')
out=c[c.flag_supply_side|c.flag_uae_specific][['year','sector','hs4','hs4_name','exporter_iso3','share_lag','ARE_lag','ARE','dlog_uae','dlog_row','dlog_uae_others','dlog_uaetot','flag_supply_side','flag_uae_specific']]
out=out.rename(columns={'ARE_lag':'uae_imports_from_supplier_prev_kusd','ARE':'uae_imports_from_supplier_kusd','share_lag':'supplier_share_prev_year'})
out.sort_values(['flag_supply_side','uae_imports_from_supplier_prev_kusd'],ascending=False).to_csv('output/table_annual_shock_screen.csv',index=False)
pd.set_option('display.width',250)
s=out[out.flag_supply_side].sort_values('uae_imports_from_supplier_prev_kusd',ascending=False)
print(len(out), len(s)); print(s.head(40).round(2).to_string(index=False))
p.to_csv('data/baci/baci_panel_supplier_uae_vs_rest_of_world.csv',index=False)
