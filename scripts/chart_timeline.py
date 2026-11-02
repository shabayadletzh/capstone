import sys; sys.path.insert(0,'scripts'); from charts_common import *
import matplotlib.patches as mp
tasks=[ # (label, start_month_index, end, owner)  index 0 = Nov 2026
 ('Finalize topic with Prof. Imbs, get Comtrade API key',0,0.6,'Both'),
 ('Full monthly HS6 pull: shortlisted products + GCC comparison importers',0.4,2,'Adilet'),
 ('Date every shock from primary sources (DGFT, OFAC, GSDB, IFPRI)',0.4,2,'Teammate'),
 ('Literature review and research proposal',0.6,1.6,'Teammate'),
 ('Descriptive event studies for 6 cases',1.6,3.2,'Adilet'),
 ('Proposal submitted (fall deliverable)',1.6,1.75,'Both'),
 ('Difference-in-differences across importers',3,4.6,'Adilet'),
 ('Who-replaces cross-section, gravity controls',3,4.6,'Teammate'),
 ('Robustness: lags, PPML, quarterly, rerouting checks',4.4,5.4,'Both'),
 ('Write results and draft thesis',4.6,6.2,'Teammate'),
 ('Figures, data appendix, replication files',4.6,6.2,'Adilet'),
 ('Final thesis and presentation',6.2,6.9,'Both')]
col={'Adilet':PAL[0],'Teammate':PAL[1],'Both':PAL[2]}
fig,ax=plt.subplots(figsize=(10,5.2))
for i,(l,s,e,o) in enumerate(tasks):
    y=len(tasks)-1-i; ax.barh(y,e-s,left=s,color=col[o],height=0.55)
    ax.text(-0.05,y,l,ha='right',va='center',fontsize=8.5,color=INK)
months=['Nov 26','Dec 26','Jan 27','Feb 27','Mar 27','Apr 27','May 27']
ax.set_xticks(range(7)); ax.set_xticklabels(months,fontsize=8.5); ax.set_xlim(0,7); ax.set_yticks([]); ax.grid(axis='y',visible=False)
ax.axvline(2,color=INK2,lw=1,ls='--'); ax.text(2.03,len(tasks)-0.4,'Spring semester',fontsize=8,color=INK2)
ax.legend(handles=[mp.Patch(color=col[k],label=k) for k in col],ncol=3,loc='lower left',bbox_to_anchor=(0,1.0),fontsize=8.5)
ax.set_title('Who does what when',pad=26)
save(fig,'charts/08_timeline.png','Proposed plan. Exact NYUAD deadlines to be confirmed')
