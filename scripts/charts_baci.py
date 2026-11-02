import pandas as pd, numpy as np, sys
sys.path.insert(0,'scripts'); from charts_common import *
b2=pd.read_csv('data/baci/baci_uae_imports_hs2_all_1995_2024.csv',dtype={'hs2':str})
# 1. top suppliers' share of total UAE imports
tot=b2.groupby('year').value_kusd.sum()
by=b2.groupby(['year','exporter_iso3']).value_kusd.sum().unstack(fill_value=0)
sh=by.div(tot,axis=0)
top=['CHN','IND','USA','JPN','DEU']
fig,ax=plt.subplots(figsize=(8,4.4))
sh=sh.loc[:2023]; its=[]
for i,c in enumerate(top):
    ax.plot(sh.index,sh[c]*100,color=PAL[i]); its.append((sh.index[-1],sh[c].iloc[-1]*100,c))
end_labels(ax,its)
ax.set_title("Share of UAE goods imports by top suppliers, 1995-2023"); ax.set_ylabel('% of total imports'); ax.set_xlim(1995,2026)
save(fig,'charts/01_top_supplier_shares_total.png','CEPII BACI HS92 V202601, UAE as importer (all HS chapters)')
# 2. HHI by product 2019-23
s=pd.read_csv('output/table_supplier_dependence_summary.csv',dtype={'hs4':str})
s=s[~s.sector.isin(['Defense & military'])].sort_values('hhi_2019_23')
fig,ax=plt.subplots(figsize=(8,11))
y=np.arange(len(s)); ax.barh(y,s.hhi_2019_23,color=PAL[0],height=0.7)
ax.set_yticks(y); ax.set_yticklabels([f"{r.product} ({r.hs4})" for r in s.itertuples()],fontsize=8)
for yi,r in zip(y,s.itertuples()): ax.text(r.hhi_2019_23+60,yi,f"{r.top1_2023} {r.top1_share_2023*100:.0f}%",va='center',fontsize=7.5,color=INK)
ax.axvline(2500,color=INK2,lw=1,ls='--'); ax.text(2560,-0.9,'HHI 2,500 = "highly concentrated"',fontsize=7.5,color=INK2,va='top')
ax.set_xlabel('Herfindahl-Hirschman Index of supplier shares (avg 2019-2023)'); ax.set_title('How concentrated is UAE sourcing? (label = top supplier 2023)'); ax.grid(axis='y',visible=False)
save(fig,'charts/02_hhi_by_product.png','CEPII BACI HS92 V202601; HHI on exporter value shares')
# 3. small multiples supplier shares
h6=pd.read_csv('data/baci/baci_uae_imports_hs6_strategic_1995_2024.csv',dtype={'hs6':str,'hs4':str})
cases=[('8703','Passenger cars (8703)',None),('852520','Mobile phones & transmitters (852520)','hs6'),('1006','Rice (1006)',None),('1001','Wheat (1001)',None),('0703','Onions & garlic (0703)',None),('7208','Hot-rolled steel (7208)',None)]
fig,axs=plt.subplots(3,2,figsize=(10,10.5)); axs=axs.ravel()
for ax,(code,title,lvl) in zip(axs,cases):
    d=h6[h6.hs6==code] if lvl=='hs6' else h6[h6.hs4==code]
    p=d.groupby(['year','exporter_iso3']).value_kusd.sum().unstack(fill_value=0); p=p.div(p.sum(axis=1),axis=0)*100
    tops=p.loc[2015:2023].mean().sort_values(ascending=False).index[:4]
    p=p.loc[:2023]; oth=100-p[list(tops)].sum(axis=1); ax.set_ylim(0,100); its=[]
    for i,c in enumerate(tops):
        ax.plot(p.index,p[c],color=PAL[i]); its.append((p.index[-1],p[c].iloc[-1],c))
    ax.plot(p.index,oth,color=OTHER,lw=1.5); its.append((p.index[-1],oth.iloc[-1],'Other'))
    end_labels(ax,its); ax.set_title(title,fontsize=10.5); ax.set_xlim(1995,2026.5); ax.set_ylabel('% of UAE imports')
fig.suptitle('Supplier shares for selected products, 1995-2023',fontweight='bold',color=INK,y=1.0); fig.tight_layout()
save(fig,'charts/03_supplier_shares_selected_products.png','CEPII BACI HS92 V202601. 2024 omitted: UAE did not report, mirror-only values distort shares')
# 4. SIPRI
sp=pd.read_csv('data/sipri/sipri_uae_arms_imports_deliveries_by_year.csv')
sp['tiv']=pd.to_numeric(sp['TIV delivery values'],errors='coerce'); sp=sp[sp['Delivery year']>=1990]
sp['period']=(sp['Delivery year']//5*5).astype(int)
top=['United States','France','Russia','United Kingdom']
sp['sup']=np.where(sp.Supplier.isin(top),sp.Supplier,'Other')
pv=sp.pivot_table(index='period',columns='sup',values='tiv',aggfunc='sum',fill_value=0)[top+['Other']]
fig,ax=plt.subplots(figsize=(8,4.4)); bottom=np.zeros(len(pv)); x=np.arange(len(pv))
for i,c in enumerate(top+['Other']):
    ax.bar(x,pv[c],bottom=bottom,color=PAL[i] if c!='Other' else OTHER,width=0.7,edgecolor=SURF,linewidth=1.5,label=c); bottom+=pv[c].values
ax.set_xticks(x); ax.set_xticklabels([f"{p}-{str(p+4)[2:]}" if p<2025 else "2025" for p in pv.index],fontsize=9); ax.set_ylabel('SIPRI TIV (millions)'); ax.legend(ncol=5,loc='lower left',bbox_to_anchor=(0,1.0),fontsize=8.5)
ax.set_title('UAE major arms imports by supplier (SIPRI TIV, deliveries)',pad=28); ax.grid(axis='x',visible=False)
save(fig,'charts/04_sipri_arms_imports_by_supplier.png','SIPRI Arms Transfers Database, register with deliveries by year (generated 28 Oct 2026)')
print(pv.round(0))
