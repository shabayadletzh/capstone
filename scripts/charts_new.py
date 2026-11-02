import pandas as pd, numpy as np, sys
sys.path.insert(0,'scripts'); from charts_common import *; from comtrade_iso import load
import matplotlib.dates as mdates
a=pd.read_csv('data/baci/baci_uae_imports_hs4_ALL_products_1995_2024.csv',dtype={'hs4':str})
cases=[('3901',2007,2016,2012,'Polyethylene (3901): Iran sanctions 2012',['IRN','SAU','QAT','KWT']),
       ('7207',2014,2023,2019,'Semi-finished steel (7207): US sanctions on Iran 2018-19',['IRN','OMN','RUS','IND']),
       ('1512',2016,2023,2022,'Sunflower oil (1512): war in Ukraine 2022',['UKR','TUR','BGR','OMN']),
       ('7201',2016,2023,2022,'Pig iron (7201): war in Ukraine 2022',['UKR','IND','BRA','RUS'])]
fig,axs=plt.subplots(2,2,figsize=(11,7.6)); axs=axs.ravel()
for ax,(h,y0,y1,ys,title,sups) in zip(axs,cases):
    g=a[(a.hs4==h)&a.year.between(y0,y1)].pivot_table(index='year',columns='exporter_iso3',values='value_kusd',aggfunc='sum').fillna(0)
    sh=g.div(g.sum(axis=1),axis=0)*100
    ax.axvspan(ys-0.5,ys+0.5,color='#efece6',zorder=0)
    its=[]
    for i,s in enumerate(sups):
        y=sh[s] if s in sh else pd.Series(0,index=sh.index)
        ax.plot(sh.index,y,color=PAL[i],marker='o',ms=3); its.append((sh.index[-1],y.iloc[-1],s))
    oth=100-sh[[s for s in sups if s in sh]].sum(axis=1); ax.plot(sh.index,oth,color=OTHER,lw=1.5); its.append((sh.index[-1],oth.iloc[-1],'Other'))
    ax.set_ylim(0,100); ax.set_xlim(y0,y1+1.6); end_labels(ax,its); ax.set_title(title,fontsize=10); ax.set_ylabel('% of UAE imports')
    tot=g.sum(axis=1)/1e3; ax.text(0.02,0.97,f"UAE imports {ys-1}: ${tot.get(ys-1,0):.0f}m",transform=ax.transAxes,fontsize=8,color=INK2,va='top')
fig.suptitle('Supplier shares in new-sector cases (shaded = shock year)',fontweight='bold',color=INK,y=1.0); fig.tight_layout()
save(fig,'charts/06_new_sector_cases_shares.png','CEPII BACI HS92 V202601, UAE imports by supplier. Annual values')
# China Feb 2020
c=load('raw/comtrade_new_part1.csv'); t=c[c.cmdCode=='TOTAL'].pivot_table(index='month',columns='reporterISO',values='primaryValue',aggfunc='sum')/1e9
t=t.loc['2019-01':'2021-12']; t.index=pd.to_datetime(t.index+'-01')
fig,ax=plt.subplots(figsize=(9,4.2)); its=[]
for i,s in enumerate(['CHN','IND','USA','DEU']):
    ax.plot(t.index,t[s],color=PAL[i],marker='o',ms=2.5)
    its.append((t.index[-1],t[s].iloc[-1],s))
for y in (2019,2020,2021): ax.axvline(pd.Timestamp(f'{y}-02-01'),color=GRID,lw=6,zorder=0)
ax.annotate('Feb 2020: $1.0bn\n(usual Feb dip is far smaller)',(pd.Timestamp('2020-02-01'),1.0),xytext=(pd.Timestamp('2020-05-15'),0.35),fontsize=8,color=INK,arrowprops=dict(arrowstyle='-',color=INK2,lw=0.8))
ax.set_ylim(0,ax.get_ylim()[1]); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
for x,y,s in its: ax.annotate(s,(x,y),xytext=(5,0),textcoords='offset points',va='center',fontsize=8.5,color=INK)
ax.set_ylabel('USD bn per month'); ax.set_title("Exports to the UAE by supplier, monthly (grey bands = February)")
save(fig,'charts/07_china_feb2020_monthly.png','UN Comtrade monthly, total exports to UAE as reported by each supplier')
