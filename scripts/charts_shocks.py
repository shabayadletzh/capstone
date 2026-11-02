import pandas as pd, numpy as np, sys
sys.path.insert(0,'scripts'); from charts_common import *
import matplotlib.dates as mdates
m=pd.read_csv('data/comtrade/comtrade_monthly_exports_to_uae_by_reporter.csv',dtype={'cmdCode':str,'period':str})
m['date']=pd.to_datetime(m.month+'-01')
CODES=["9301","9305","9306","8710","8802","8803","8807","8411","8526","8906","8471","8473","8517","8542","8541","8528","8525","9018","8486","8524","8703","8704","8708","8701","8429","8481","8413","8502","8504","8544","8406","8415","8901","8905","8507","4011","7208","7210","7214","7304","7306","7308","2601","2818","7601","7403","2710","7108","7102","7113","3004","3002","1001","1006","0703","1511","1512","1701","0207","0902","0402","1005"]
G1=set(CODES[:31]); grp=lambda c: 1 if c in G1 else 2
m['grp']=m.cmdCode.map(grp)
cov=set(zip(m.reporterISO,m.date,m.grp))  # reporter-month-request group with any record
EP=[ # code, title, start, end, shock_start, shock_end, suppliers, measure, ylabel
 ('8703','Japan earthquake (11 Mar 2011): passenger cars','2010-06','2012-06','2011-04','2011-05',['JPN','USA','GBR','THA'],'primaryValue','USD million'),
 ('8704','Thailand floods (Oct-Dec 2011): trucks & pickups','2010-06','2012-06','2011-10','2011-12',['JPN','THA','USA'],'primaryValue','USD million'),
 ('1001','India wheat export ban (13 May 2022; shipments stop Sep 2022)','2021-01','2024-06','2022-09','2023-08',['IND','CAN','AUS','RUS'],'netWgt','thousand tonnes'),
 ('0703','India onion export ban (8 Dec 2023 - 4 May 2024)','2023-01','2025-06','2023-12','2024-05',['IND','PAK','CHN','TUR'],'netWgt','thousand tonnes'),
 ('1511','Indonesia palm oil export ban (28 Apr - 23 May 2022)','2021-06','2023-06','2022-04','2022-05',['IDN','MYS'],'netWgt','thousand tonnes'),
 ('1006','India non-basmati white rice ban (20 Jul 2023)','2022-06','2024-12','2023-08','2024-07',['IND','PAK','THA','VNM'],'netWgt','thousand tonnes'),
]
fig,axs=plt.subplots(3,2,figsize=(11,11.5)); axs=axs.ravel(); rows=[]
for ax,(code,title,a,b,s0,s1,sups,meas,yl) in zip(axs,EP):
    d=m[(m.cmdCode==code)&(m.month>=a)&(m.month<=b)]
    p=d.pivot_table(index='date',columns='reporterISO',values=meas,aggfunc='sum')
    div=1e6 if meas=='primaryValue' else 1e6  # USD->m ; kg->thousand t
    p=p/div; idx=pd.date_range(a+'-01',b+'-01',freq='MS'); p=p.reindex(idx)
    for col in p.columns:  # absent product record but reporter reported other goods that month -> 0
        for dt in p.index:
            if pd.isna(p.at[dt,col]) and (col,dt,grp(code)) in cov: p.at[dt,col]=0.0
    ax.axvspan(pd.Timestamp(s0+'-01'),pd.Timestamp(s1+'-01')+pd.offsets.MonthEnd(0),color='#efece6',zorder=0)
    hs=[]
    for i,s in enumerate(sups):
        if s in p: h,=ax.plot(p.index,p[s],color=PAL[i],marker='o',ms=3,label=s); hs.append(h)
    ax.set_title(title,fontsize=10); ax.set_ylabel(yl); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y')); ax.tick_params(axis='x',labelsize=8)
    ax.set_ylim(bottom=0); ax.legend(handles=hs,fontsize=8,loc='upper left',ncol=4)
    pre=p.loc[pd.Timestamp(s0+'-01')-pd.DateOffset(months=6):pd.Timestamp(s0+'-01')-pd.DateOffset(months=1)]
    dur=p.loc[pd.Timestamp(s0+'-01'):pd.Timestamp(s1+'-01')]
    for s in p.columns:
        rows.append({'episode':title,'hs4':code,'measure':meas,'reporter':s,'pre6m_monthly_avg':pre[s].mean(),'during_monthly_avg':dur[s].mean(),'pre_months_reported':int(pre[s].notna().sum()),'during_months_reported':int(dur[s].notna().sum())})
fig.suptitle('Candidate supply shocks: monthly exports to the UAE reported by suppliers',fontweight='bold',color=INK,y=1.0); fig.tight_layout()
save(fig,'charts/05_shock_episodes_monthly.png','UN Comtrade monthly data, partner (mirror) exports to UAE. Shaded = shock period. Missing month = not reported')
t=pd.DataFrame(rows); t['change_pct']=(t.during_monthly_avg/t.pre6m_monthly_avg-1)*100
t=t[t.pre6m_monthly_avg.notna()|t.during_monthly_avg.notna()]
t['pre_share']=t.groupby('episode').pre6m_monthly_avg.transform(lambda x:x/x.sum()); t['during_share']=t.groupby('episode').during_monthly_avg.transform(lambda x:x/x.sum())
t=t.sort_values(['episode','pre6m_monthly_avg'],ascending=[True,False])
t.to_csv('output/table_shock_episodes_pre_vs_during.csv',index=False)
pd.set_option('display.width',220)
print(t.groupby('episode').head(6).round(2).to_string(index=False))
