# First look at the cross-importer comparison: across the six GCC importers, did imports
# from other suppliers rise more where the shocked supplier had a bigger pre-shock share?
import pandas as pd, numpy as np
b=pd.read_csv('data/baci/baci_strategic_hs4_exports_by_exporter_to_world_and_gcc_1995_2024.csv',dtype={'hs4':str})
b=b[b.destination!='WLD']
CASES=[('Japan quake 2011, cars','8703','JPN',2010,2011),
       ('Japan quake 2011, trucks','8704','JPN',2010,2011),
       ('India wheat ban 2022','1001','IND',2021,2023),
       ('Ukraine war 2022, sunflower oil','1512','UKR',2021,2022),
       ('Indonesia palm oil ban 2022','1511','IDN',2021,2022),
       # [Sultan's coding agent, 2 Nov 2026] Post year changed from 2024 to 2023. The README rule is to stop
       # share analysis at 2023 because BACI 2024 is built from partner reports only. Restrictions began with
       # the 40% duty on 19 Aug 2023, so 2023 already has five restricted months. Case label kept unchanged.
       ('India onion ban 2023-24','0703','IND',2022,2023)]
rows=[]
for name,k,s,t0,t1 in CASES:
    g=b[(b.hs4==k)&(b.year.isin([t0,t1]))]
    p=g.assign(grp=np.where(g.exporter_iso3==s,'shocked','others')).pivot_table(index='destination',columns=['grp','year'],values='value_kusd',aggfunc='sum').fillna(0)
    for d in p.index:
        tot0=p.loc[d,('shocked',t0)]+p.loc[d,('others',t0)]
        rows.append({'case':name,'hs4':k,'shocked':s,'pre_year':t0,'post_year':t1,'importer':d,
          'imports_pre_musd':round(tot0/1e3,1),'exposure_pre':round(p.loc[d,('shocked',t0)]/tot0,3),
          'loss_pct_of_pre':round((p.loc[d,('shocked',t1)]-p.loc[d,('shocked',t0)])/tot0*100,1),
          'others_gain_pct_of_pre':round((p.loc[d,('others',t1)]-p.loc[d,('others',t0)])/tot0*100,1),
          'total_change_pct':round(((p.loc[d,('shocked',t1)]+p.loc[d,('others',t1)])/tot0-1)*100,1)})
t=pd.DataFrame(rows)
t.to_csv('output/table_gcc_cross_importer_first_look.csv',index=False)
print(t.to_string(index=False))
# pooled slope with case fixed effects (demeaned within case)
d=t.copy()
for c in ['exposure_pre','others_gain_pct_of_pre','loss_pct_of_pre']:
    d[c+'_dm']=d[c]-d.groupby('case')[c].transform('mean')
for y in ['loss_pct_of_pre','others_gain_pct_of_pre']:
    x=d['exposure_pre_dm']; yy=d[y+'_dm']
    bh=(x*yy).sum()/(x*x).sum(); res=yy-bh*x; n=len(d); k=len(CASES)+1
    se=np.sqrt((res**2).sum()/(n-k)/(x*x).sum())
    print(y,'slope per 1.0 exposure:',round(bh,1),'se',round(se,1),'n',n)
