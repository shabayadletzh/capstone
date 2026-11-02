import pandas as pd, numpy as np
pd.set_option('display.width',260); pd.set_option('display.max_colwidth',40)
a=pd.read_csv('data/baci/baci_uae_imports_hs4_ALL_products_1995_2024.csv',dtype={'hs4':str})
a=a[a.year<=2023].groupby(['hs4','exporter_iso3','year'],as_index=False).value_kusd.sum()
pc=pd.read_csv('raw/baci_product_codes_hs92.csv',dtype={'code':str}); pc['hs4']=pc.code.str[:4]
h4n=pc.groupby('hs4').description.first().str.split(r'[:;,]').str[0].str[:45]
cc=pd.read_csv('raw/baci_country_codes.csv').set_index('country_code')
T=a.groupby(['hs4','year']).value_kusd.sum().rename('T').reset_index()
# balanced panel of pairs x years 
p=a.pivot_table(index=['hs4','exporter_iso3'],columns='year',values='value_kusd',aggfunc='sum').fillna(0)
L=p.stack().rename('v').reset_index()
L=L.merge(T,on=['hs4','year'],how='left'); L['s']=L.v/L['T']
L=L.sort_values(['hs4','exporter_iso3','year'])
g=L.groupby(['hs4','exporter_iso3'])
L['v_prev']=g.v.shift(); L['T_prev']=g['T'].shift(); L['s_prev']=g.s.shift()
f=L[(L.T_prev>=30000)&(L.s_prev>=0.2)&((L.s-L.s_prev)<=-0.15)&((np.log(L.v.clip(lower=1))-np.log(L.v_prev.clip(lower=1)))<=-0.4)].copy()
f=f.rename(columns={'exporter_iso3':'exporter','T':'uae_total','T_prev':'uae_total_prev','s':'share','s_prev':'share_prev'})
f['lost_musd']=(f.v_prev-f.v)/1e3
w=pd.read_csv('raw/baci_flagged_pairs_world_gcc.csv',dtype={'hs4':str}); w['hs4']=w.hs4.str.zfill(4); w['exporter']=w.i.map(cc.country_iso3)
wp=w.pivot_table(index=['hs4','exporter','t'],columns='dest',values='v_kusd',aggfunc='sum').fillna(0)
for c in ['SAU','OMN','KWT','QAT','BHR','ARE','WLD']:
    if c not in wp: wp[c]=0
wp['ROW']=wp.WLD-wp.ARE; wp['GCC']=wp[['SAU','OMN','KWT','QAT','BHR']].sum(axis=1)
wp=wp[['ROW','GCC']].reset_index().rename(columns={'t':'year'})
f=f.merge(wp,on=['hs4','exporter','year'],how='left')
f=f.merge(wp.assign(year=wp.year+1).rename(columns={'ROW':'row_prev','GCC':'gcc_prev'}),on=['hs4','exporter','year'],how='left')
Lg=lambda x,y:np.log(np.maximum(x.fillna(0),1))-np.log(np.maximum(y.fillna(0),1))
f['dlog_row']=Lg(f.ROW,f.row_prev); f['dlog_gcc']=Lg(f.GCC,f.gcc_prev); f['dlog_uae_total']=np.log(f.uae_total)-np.log(f.uae_total_prev)
f['type']=np.where(f.dlog_row<=-0.22,'supplier-wide drop',np.where((f.gcc_prev>1000)&(f.dlog_gcc<=-0.4),'Gulf-specific drop','UAE-specific drop'))
f['uae_demand']=np.where(f.dlog_uae_total<=-0.3,'fell','held')
# gainers
ds=L.assign(ds=L.s-L.s_prev)[['hs4','exporter_iso3','year','ds']]
ds=ds[ds.ds>0.02].sort_values('ds',ascending=False)
top=ds.groupby(['hs4','year']).apply(lambda d:list(zip(d.exporter_iso3,d.ds))[:4]).rename('gl')
f=f.join(top,on=['hs4','year'])
f['who_gained']=[ '; '.join(f"{k} +{v*100:.0f}pp" for k,v in (gl if isinstance(gl,list) else []) if k!=e)[:60] for gl,e in zip(f.gl,f.exporter)]
f['product']=f.hs4.map(h4n)
f=f.drop(columns=['gl']).sort_values('lost_musd',ascending=False)
cols=['year','exporter','hs4','product','share_prev','share','v_prev','v','lost_musd','uae_total_prev','uae_total','dlog_row','dlog_gcc','dlog_uae_total','type','uae_demand','who_gained']
f[cols].to_csv('output/table_supplier_switch_screen_all_products.csv',index=False)
print('flags',len(f)); print(f.type.value_counts()); print(f.uae_demand.value_counts())
c=f[~f.hs4.str[:2].isin(['71','27'])|f.hs4.isin(['2711','2701'])].groupby(['exporter','year']).agg(n_products=('hs4','count'),lost_musd=('lost_musd','sum'),n_supplier_wide=('type',lambda x:(x=='supplier-wide drop').sum()),n_uae_specific=('type',lambda x:(x=='UAE-specific drop').sum())).sort_values('lost_musd',ascending=False)
c.to_csv('output/table_switch_clusters_supplier_year.csv')
print(c.head(45).round(0).to_string())
