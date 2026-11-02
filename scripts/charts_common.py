import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
PAL=['#2a78d6','#eb6834','#1baf7a','#eda100','#e87ba4','#008300','#6250d6','#e34948']
OTHER='#b5b3ad'; INK='#0b0b0b'; INK2='#52514e'; GRID='#e6e4df'; SURF='#fcfcfb'
plt.rcParams.update({'figure.facecolor':SURF,'axes.facecolor':SURF,'axes.edgecolor':GRID,'axes.labelcolor':INK2,'xtick.color':INK2,'ytick.color':INK2,
 'axes.grid':True,'grid.color':GRID,'grid.linewidth':0.8,'axes.spines.top':False,'axes.spines.right':False,'font.size':10,'axes.titlesize':12,'axes.titleweight':'bold','axes.titlecolor':INK,'legend.frameon':False,'lines.linewidth':2})
def label_end(ax,x,y,text,color=INK2,dy=0):
    ax.annotate(text,(x,y),xytext=(4,dy),textcoords='offset points',va='center',fontsize=8.5,color=INK)
def save(fig,path,src):
    fig.text(0.01,0.005,'Source: '+src,fontsize=7.5,color=INK2,ha='left',va='bottom')
    fig.savefig(path,dpi=160,bbox_inches='tight'); plt.close(fig)

def end_labels(ax,items,min_gap=None):
    """items: list of (x,y,text,color). Spread labels vertically to avoid overlap."""
    if not items: return
    lo,hi=ax.get_ylim(); gap=min_gap or (hi-lo)*0.045
    items=sorted(items,key=lambda t:t[1]); ys=[]
    for it in items:
        y=it[1]
        if ys and y-ys[-1]<gap: y=ys[-1]+gap
        ys.append(y)
    # shift down if overflow
    over=ys[-1]-hi*0.99
    if over>0: ys=[y-over for y in ys]
    for it,y in zip(items,ys):
        ax.annotate(it[2],(it[0],it[1]),xytext=(it[0]+0.4,y),textcoords='data',va='center',fontsize=8.5,color=INK,annotation_clip=False)
