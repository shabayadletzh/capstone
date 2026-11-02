import pandas as pd, numpy as np
cc=pd.read_csv('raw/baci_country_codes.csv').set_index('country_code')
pc=pd.read_csv('raw/baci_product_codes_hs92.csv',dtype={'code':str})
a=pd.read_csv('raw/baci_uae_all_hs4.csv',dtype={'hs4':str}); a['hs4']=a.hs4.str.zfill(4)
a['exporter_iso3']=a.i.map(cc.country_iso3); a['exporter_name']=a.i.map(cc.country_name)
a=a.rename(columns={'t':'year','i':'exporter_code','v_kusd':'value_kusd','q_tonnes':'quantity_tonnes'})
a.to_csv('data/baci/baci_uae_imports_hs4_ALL_products_1995_2024.csv',index=False)
NEW={'Energy & chemicals':{'2711':'Natural gas & LPG','2701':'Coal','3901':'Polyethylene','3902':'Polypropylene','3903':'Polystyrene','3904':'PVC','3907':'Polyesters & PET','3102':'Nitrogen fertilizers','3105':'Mixed fertilizers','2814':'Ammonia','2902':'Cyclic hydrocarbons','2905':'Alcohols incl. methanol','3926':'Plastic articles'},
'Construction materials':{'2523':'Cement','6907':'Ceramic tiles (unglazed)','6908':'Ceramic tiles (glazed)','7005':'Float glass','7007':'Safety glass','4407':'Sawn wood','4412':'Plywood','7604':'Aluminium bars & profiles','7610':'Aluminium structures','6802':'Worked stone & marble','2515':'Marble blocks','6810':'Concrete articles','6910':'Sanitary ware','7213':'Steel wire rod'},
'Fresh food':{'0201':'Beef, fresh','0202':'Beef, frozen','0204':'Sheep & goat meat','0104':'Live sheep & goats','0102':'Live cattle','0702':'Tomatoes','0701':'Potatoes','0805':'Citrus','0803':'Bananas','0808':'Apples & pears','0806':'Grapes','0407':'Eggs','0302':'Fish, fresh','0303':'Fish, frozen','0401':'Milk & cream','0406':'Cheese','0405':'Butter','1507':'Soybean oil','1517':'Margarine','1101':'Wheat flour','2009':'Fruit juices'},
'Medical supplies':{'3005':'Bandages & dressings','4015':'Rubber gloves','6307':'Textile articles incl. masks','3822':'Diagnostic reagents','9022':'X-ray equipment','9019':'Therapy & respiration apparatus','9021':'Orthopaedic & implants','3006':'Pharma goods n.e.s.'}}
rows=[]
for s,d in NEW.items():
    for h,n in d.items():
        g=a[(a.hs4==h)&(a.year<=2023)]
        if g.empty or 2023 not in set(g.year): print('skip',h,n); continue
        T=g.groupby('year').value_kusd.sum()
        sh=g.assign(sh=g.value_kusd/g.year.map(T))
        hhi=sh.groupby('year').sh.apply(lambda x:(x**2).sum()*1e4)
        y=sh[sh.year==2023].sort_values('sh',ascending=False)
        lead=sh.loc[sh.groupby('year').sh.idxmax()].set_index('year')
        rows.append({'sector':s,'hs4':h,'product':n,'imports_2023_musd':round(T.get(2023,0)/1e3,0),'top1_2023':y.exporter_iso3.iloc[0],'top1_share_2023':round(y.sh.iloc[0],3),'top2_2023':y.exporter_iso3.iloc[1] if len(y)>1 else None,'top2_share_2023':round(y.sh.iloc[1],3) if len(y)>1 else None,
          'hhi_2019_23':round(hhi.loc[2019:2023].mean()),'hhi_1995_99':round(hhi.loc[1995:1999].mean()) if len(hhi.loc[1995:1999]) else None,'top1_2005':lead.exporter_iso3.get(2005),'top1_2015':lead.exporter_iso3.get(2015),'top1_switches':int((lead.exporter_iso3!=lead.exporter_iso3.shift()).sum()-1),'n_suppliers_2023':len(y)})
t=pd.DataFrame(rows).sort_values(['sector','imports_2023_musd'],ascending=[True,False])
t.to_csv('output/table_new_sectors_dependence.csv',index=False)
pd.set_option('display.width',250); print(t.drop(columns=['hhi_1995_99']).to_string(index=False))
