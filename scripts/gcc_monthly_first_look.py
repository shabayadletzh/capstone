# Monthly first look at the cross-importer comparison (step 2 of the design).
# For each case: the shocked supplier's exports to each GCC importer in the shock window
# vs a pre-window, and the same for the other reporters we have. Exposure = shocked
# supplier's share of the importer's imports of the product in the pre-year (BACI).
import pandas as pd, numpy as np, sys
sys.path.insert(0,'scripts'); from charts_common import *
c=pd.read_csv('data/comtrade/comtrade_monthly_exports_to_GCC_case_products.csv',dtype={'cmdCode':str})
b=pd.read_csv('data/baci/baci_strategic_hs4_exports_by_exporter_to_world_and_gcc_1995_2024.csv',dtype={'hs4':str})
b=b[b.destination!='WLD']
def expo(k,s,y):
    g=b[(b.hs4==k)&(b.year==y)]; t=g.groupby('destination').value_kusd.sum()
    return (g[g.exporter_iso3==s].groupby('destination').value_kusd.sum()/t).reindex(t.index).fillna(0)
CASES=[('Japan quake 2011, cars','8703','JPN',('2010-03','2011-02'),('2011-04','2011-06'),2010,['USA','DEU','GBR','THA','CHN']),
       ('India wheat ban 2022','1001','IND',('2021-06','2022-05'),('2022-09','2023-08'),2021,['AUS','CAN','TUR','UKR','KAZ','BRA']),
       ('Ukraine war 2022, sunflower oil','1512','UKR',('2021-03','2022-02'),('2022-03','2022-12'),2021,['TUR','EGY','IND','MYS','BRA']),
       ('India onion ban 2023-24','0703','IND',('2022-12','2023-04'),('2023-12','2024-04'),2022,['PAK','CHN','EGY','TUR'])]
rows=[]
for name,k,s,pre,post,y0,alts in CASES:
    g=c[c.cmdCode==k]; e=expo(k,s,y0)
    npre=len(pd.period_range(pre[0],pre[1],freq='M')); npost=len(pd.period_range(post[0],post[1],freq='M'))
    def avg(df,w,n): return df[(df.month>=w[0])&(df.month<=w[1])].groupby('partnerISO').primaryValue.sum()/n
    sp=avg(g[g.reporterISO==s],pre,npre); sq=avg(g[g.reporterISO==s],post,npost)
    op=avg(g[g.reporterISO.isin(alts)],pre,npre); oq=avg(g[g.reporterISO.isin(alts)],post,npost)
    for d in ['ARE','SAU','OMN','KWT','QAT','BHR']:
        a,bq,o0,o1=sp.get(d,0),sq.get(d,0),op.get(d,0),oq.get(d,0)
        base=a+o0
        rows.append({'case':name,'hs4':k,'shocked':s,'pre_window':f'{pre[0]} to {pre[1]}','shock_window':f'{post[0]} to {post[1]}','importer':d,
          'exposure_baci':round(e.get(d,np.nan),3),'shocked_pre_musd_month':round(a/1e6,2),'shocked_post_musd_month':round(bq/1e6,2),
          'shocked_change_pct':round((bq/a-1)*100,1) if a>0 else np.nan,
          'others_pre_musd_month':round(o0/1e6,2),'others_post_musd_month':round(o1/1e6,2),
          'others_change_pct':round((o1/o0-1)*100,1) if o0>0 else np.nan,
          'others_gain_pct_of_pre_total':round((o1-o0)/base*100,1) if base>0 else np.nan,'alternatives_counted':' '.join(alts)})
t=pd.DataFrame(rows); t.to_csv('output/table_gcc_cross_importer_monthly_first_look.csv',index=False)
pd.set_option('display.width',250); print(t.drop(columns=['pre_window','shock_window','alternatives_counted','hs4']).to_string(index=False))
# China Feb 2020 across GCC: Feb 2020 vs Feb 2019, China vs other big suppliers
z=c[c.cmdCode=='TOTAL']
f=z[z.month.isin(['2019-02','2020-02'])].pivot_table(index=['reporterISO','partnerISO'],columns='month',values='primaryValue',aggfunc='sum')
f['change_pct']=((f['2020-02']/f['2019-02']-1)*100).round(1)
ch=f['change_pct'].unstack('partnerISO'); ch.to_csv('output/table_gcc_feb2020_vs_feb2019_by_supplier.csv')
print(ch.to_string())
# chart: others' gain vs exposure, one panel per case
fig,axs=plt.subplots(1,4,figsize=(15,4),sharey=False)
for ax,(name,*_ ) in zip(axs,CASES):
    q=t[t.case==name].dropna(subset=['exposure_baci','others_gain_pct_of_pre_total'])
    xs=q.exposure_baci*100; ys=q.others_gain_pct_of_pre_total
    xr=(xs.max()-xs.min()) or 1; yr=(ys.max()-ys.min()) or 1; placed=[]
    for _,r in q.sort_values('others_gain_pct_of_pre_total',ascending=False).iterrows():
        col=PAL[1] if r.importer=='ARE' else PAL[0]
        x,y=r.exposure_baci*100,r.others_gain_pct_of_pre_total
        ax.scatter(x,y,s=60,color=col,zorder=3)
        near=sum(1 for (a,b) in placed if abs(a-x)/xr<0.12 and abs(b-y)/yr<0.12)
        ax.annotate(r.importer,(x,y),xytext=(6,3-12*near),textcoords='offset points',fontsize=8.5,color=INK)
        placed.append((x,y))
    ax.axhline(0,color=INK2,lw=0.8)
    ax.set_title(name,fontsize=10.5); ax.set_xlabel("Shocked supplier's pre-shock share (%)")
axs[0].set_ylabel("Gain by other suppliers\n(% of pre-shock monthly imports)")
fig.suptitle('Across GCC importers: did other suppliers gain more where the shocked supplier mattered more?',x=0.01,ha='left',fontsize=12,fontweight='bold',color=INK)
fig.tight_layout(rect=(0,0.03,1,0.95))
save(fig,'charts/09_gcc_first_look_exposure_vs_replacement.png','UN Comtrade monthly supplier-reported exports (alternatives = reporters listed in the table); exposure from CEPII BACI. UAE in orange.')
