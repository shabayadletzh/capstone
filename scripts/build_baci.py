import pandas as pd, numpy as np
cc=pd.read_csv('raw/baci_country_codes.csv',dtype={'country_code':int})
cmap=cc.set_index('country_code')
pc=pd.read_csv('raw/baci_product_codes_hs92.csv',dtype={'code':str})
pdesc=pc.set_index('code').description
SECT={ # mutually exclusive strategic groups (HS4, HS92 nomenclature)
 'Defense & military':['9301','9305','9306','8710','8906'],
 'Aerospace':['8802','8803','8411'],
 'ICT & electronics':['8471','8473','8517','8542','8541','8528','8525','8526'],
 'Medical technology':['9018'],
 'Vehicles & ships':['8703','8704','8708','8701','8901','8905','4011'],
 'Machinery & electrical equipment':['8429','8481','8413','8502','8504','8544','8406','8415','8507'],
 'Metals & basic materials':['7208','7210','7214','7304','7306','7308','2601','2818','7601','7403'],
 'Refined fuels':['2710'],
 'Precious metals & stones':['7108','7102','7113'],
 'Pharmaceuticals':['3004','3002'],
 'Food staples':['1001','1006','0703','1511','1512','1701','0207','0902','0402','1005'],
}
h4sect={h:s for s,l in SECT.items() for h in l}
H4NAME={'9301':'Military weapons','9305':'Parts of arms','9306':'Bombs, missiles, ammunition','8710':'Tanks & armoured vehicles','8906':'Warships & other vessels',
'8802':'Aircraft, helicopters, spacecraft','8803':'Aircraft parts','8411':'Turbojets, turbines (gas)','8471':'Computers','8473':'Computer parts','8517':'Telephones & telecom equipment',
'8542':'Integrated circuits','8541':'Diodes, transistors, solar cells','8528':'Monitors & TVs','8525':'Transmitters & cameras','8526':'Radar & navigation','9018':'Medical instruments',
'8703':'Passenger cars','8704':'Trucks','8708':'Vehicle parts','8701':'Tractors','8901':'Cargo & passenger ships','8905':'Drilling platforms & special vessels','4011':'Tyres',
'8429':'Bulldozers, excavators','8481':'Valves & taps','8413':'Pumps','8502':'Generating sets','8504':'Transformers','8544':'Insulated wire & cable','8406':'Steam turbines','8415':'Air conditioners','8507':'Batteries',
'7208':'Hot-rolled steel flat','7210':'Coated steel flat','7214':'Steel bars (rebar)','7304':'Seamless steel tubes','7306':'Other steel tubes','7308':'Steel structures','2601':'Iron ore','2818':'Alumina','7601':'Unwrought aluminium','7403':'Refined copper',
'2710':'Refined petroleum','7108':'Gold','7102':'Diamonds','7113':'Jewellery','3004':'Medicaments','3002':'Vaccines & blood products',
'1001':'Wheat','1006':'Rice','0703':'Onions & garlic','1511':'Palm oil','1512':'Sunflower oil','1701':'Sugar','0207':'Poultry meat','0902':'Tea','0402':'Milk powder','1005':'Maize'}
def addc(df,col='i'):
    df['exporter_iso3']=df[col].map(cmap.country_iso3); df['exporter_name']=df[col].map(cmap.country_name); return df
# HS6 strategic
b6=pd.read_csv('raw/baci_hs92_v202601_uae_imports_hs6_strategic.csv',dtype={'k':str})
b6['k']=b6.k.str.zfill(6); b6['hs4']=b6.k.str[:4]; b6['sector']=b6.hs4.map(h4sect); b6['hs4_name']=b6.hs4.map(H4NAME); b6['hs6_desc']=b6.k.map(pdesc)
b6=addc(b6).rename(columns={'t':'year','i':'exporter_code','k':'hs6','v':'value_kusd','q':'quantity_tonnes'})
b6['importer_iso3']='ARE'
b6=b6[['year','importer_iso3','exporter_code','exporter_iso3','exporter_name','sector','hs4','hs4_name','hs6','hs6_desc','value_kusd','quantity_tonnes']]
b6.to_csv('data/baci/baci_uae_imports_hs6_strategic_1995_2024.csv',index=False)
h4=b6.groupby(['year','exporter_code','exporter_iso3','exporter_name','sector','hs4','hs4_name'],as_index=False).value_kusd.sum()
h4.to_csv('data/baci/baci_uae_imports_hs4_strategic_1995_2024.csv',index=False)
# HS2 all
b2=pd.read_csv('raw/baci_hs92_v202601_uae_imports_hs2.csv',dtype={'hs2':str}); b2['hs2']=b2.hs2.str.zfill(2)
b2=addc(b2).rename(columns={'t':'year','i':'exporter_code','v_kusd':'value_kusd'})
b2.to_csv('data/baci/baci_uae_imports_hs2_all_1995_2024.csv',index=False)
print(b6.shape,h4.shape,b2.shape, b6.exporter_iso3.isna().sum())
