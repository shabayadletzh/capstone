import pandas as pd, numpy as np
h4=pd.read_csv('data/baci/baci_uae_imports_hs4_strategic_1995_2024.csv',dtype={'hs4':str})
def stats(g):
    tot=g.value_kusd.sum(); s=(g.value_kusd/tot).sort_values(ascending=False); gg=g.set_index('exporter_iso3').value_kusd.sort_values(ascending=False)
    return pd.Series({'total_musd':tot/1e3,'n_suppliers':(g.value_kusd>0).sum(),'hhi':(s**2).sum()*10000,'top1':gg.index[0],'top1_share':s.iloc[0],'top2':gg.index[1] if len(gg)>1 else None,'top2_share':s.iloc[1] if len(s)>1 else np.nan,'top3':gg.index[2] if len(gg)>2 else None,'top3_share_cum':s.iloc[:3].sum()})
c=h4.groupby(['sector','hs4','hs4_name','year']).apply(stats).reset_index()
c.to_csv('data/baci/baci_uae_supplier_concentration_hs4_by_year.csv',index=False)
# summary: average 2019-2023 vs 1995-1999, top supplier switches
rows=[]
for (s,h,n),g in c.groupby(['sector','hs4','hs4_name']):
    g=g.set_index('year')
    def avg(a,b,col): return g.loc[a:b,col].mean()
    tops=g.top1.tolist(); switches=sum(1 for i in range(1,len(tops)) if tops[i]!=tops[i-1])
    rows.append({'sector':s,'hs4':h,'product':n,'imports_2023_musd':round(g.loc[2023,'total_musd'],0) if 2023 in g.index else np.nan,
     'top1_2023':g.loc[2023,'top1'],'top1_share_2023':round(g.loc[2023,'top1_share'],3),'top2_2023':g.loc[2023,'top2'],'hhi_2023':round(g.loc[2023,'hhi']),
     'hhi_1995_99':round(avg(1995,1999,'hhi')),'hhi_2019_23':round(avg(2019,2023,'hhi')),'top1_1995':g.loc[1995,'top1'] if 1995 in g.index else None,'top1_2005':g.loc[2005,'top1'],'top1_2015':g.loc[2015,'top1'],
     'top1_switches_1995_2024':switches,'n_suppliers_2023':int(g.loc[2023,'n_suppliers'])})
summ=pd.DataFrame(rows).sort_values(['sector','imports_2023_musd'],ascending=[True,False])
summ.to_csv('output/table_supplier_dependence_summary.csv',index=False)
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
print(summ.drop(columns=['sector']).to_string(index=False))
