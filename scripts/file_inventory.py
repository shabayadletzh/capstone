import pandas as pd, glob, os, numpy as np
out=[]
for f in sorted(glob.glob('data/*/*.csv'))+sorted(glob.glob('output/*.csv'))+sorted(glob.glob('audit/*.csv')):
    d=pd.read_csv(f,low_memory=False)
    num=d.select_dtypes('number')
    valcols=[c for c in d.columns if c.lower() in ('value_kusd','primaryvalue','value_eur','obs_value','tiv_delivery','v_kusd')]
    neg=int((d[valcols]<0).sum().sum()) if valcols else None
    zero=int((d[valcols]==0).sum().sum()) if valcols else None
    yrs=None
    for c in ['year','month','period','Delivery year','TIME_PERIOD']:
        if c in d.columns: yrs=f"{d[c].min()} - {d[c].max()}"; break
    out.append(dict(file=f,rows=len(d),cols=len(d.columns),columns='; '.join(map(str,d.columns)),span=yrs,dup_rows=int(d.duplicated().sum()),
        pct_missing=round(d.isna().mean().mean()*100,1),neg_values=neg,zero_values=zero,mb=round(os.path.getsize(f)/1e6,1)))
t=pd.DataFrame(out); t.to_csv('audit/file_inventory.csv',index=False)
pd.set_option('display.width',300,'display.max_colwidth',200)
print(t.drop(columns=['columns']).to_string(index=False))
for _,r in t.iterrows(): print(r.file,'::',r.columns)
