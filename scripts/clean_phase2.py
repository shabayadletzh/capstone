import pandas as pd, re, sys
sys.path.insert(0,'scripts')
src=open('scripts/new_sectors.py').read()
NEW=eval(re.search(r"NEW=(\{.*?\}\})",src,re.S).group(1))
h4={h:(s,n) for s,d in NEW.items() for h,n in d.items()}
cc=pd.read_csv('raw/baci_country_codes.csv'); cc=cc.set_index('country_code')
pc=pd.read_csv('raw/baci_product_codes_hs92.csv',dtype={'code':str}).set_index('code').description
r=pd.read_csv('raw/baci_uae_newsectors_hs6.csv',dtype={'k':str})
r['hs6']=r.k.str.zfill(6); r['hs4']=r.hs6.str[:4]
r=r[r.hs4.isin(h4)]
o=pd.DataFrame({'year':r.t,'importer_iso3':'ARE','exporter_code':r.i,'exporter_iso3':r.i.map(cc.country_iso3),'exporter_name':r.i.map(cc.country_name),
 'sector':r.hs4.map(lambda h:h4[h][0]),'hs4':r.hs4,'hs4_name':r.hs4.map(lambda h:h4[h][1]),'hs6':r.hs6,'hs6_desc':r.hs6.map(pc),'value_kusd':r.v,'quantity_tonnes':r.q})
o.to_csv('data/baci/baci_uae_imports_hs6_new_sectors_1995_2024.csv',index=False)
print('hs6',len(o),o.hs4.nunique(),o.exporter_iso3.isna().sum())
f=pd.read_csv('raw/baci_flagged_pairs_world_gcc.csv',dtype={'hs4':str})
f['exporter_iso3']=f.i.map(cc.country_iso3); f['exporter_name']=f.i.map(cc.country_name)
f=f.rename(columns={'t':'year','i':'exporter_code','dest':'destination','v_kusd':'value_kusd'})[['year','exporter_code','exporter_iso3','exporter_name','hs4','destination','value_kusd']]
f.to_csv('data/baci/baci_switch_flagged_pairs_exports_to_world_and_gcc_1995_2024.csv',index=False)
print('flag',len(f),f.destination.unique())
