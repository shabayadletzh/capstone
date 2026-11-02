import pandas as pd, numpy as np
c=pd.read_csv('raw/comtrade_all.csv',dtype={'cmdCode':str,'period':str,'reporterCode':str,'partnerCode':str})
keys=['tag','period','reporterISO','flowCode','partnerCode','cmdCode','customsCode','motCode','partner2Code']
c=c.drop_duplicates(keys)
cols=['period','reporterCode','reporterISO','flowCode','partnerCode','partnerISO','cmdCode','classificationCode','primaryValue','cifvalue','fobvalue','netWgt','qty','qtyUnitAbbr','isReported','isQtyEstimated','isNetWgtEstimated']
m=c[c.tag=='MIRROR_X_to_ARE_M'][cols].copy(); m['month']=m.period.str[:4]+'-'+m.period.str[4:]
m.to_csv('data/comtrade/comtrade_monthly_exports_to_uae_by_reporter.csv',index=False)
cov=m.groupby(['reporterISO','month']).size().rename('n_records').reset_index()
cov.to_csv('data/comtrade/comtrade_monthly_coverage_reporter_month.csv',index=False)
c[c.tag=='ARE_M_TOTAL_byPartner'][cols].to_csv('data/comtrade/comtrade_uae_reported_imports_total_by_partner_annual.csv',index=False)
c[c.tag=='ARE_M_AG2_World'][cols].to_csv('data/comtrade/comtrade_uae_reported_imports_by_chapter_annual.csv',index=False)
c[c.tag=='ARE_M_HS4_byPartner'][cols].to_csv('data/comtrade/comtrade_uae_reported_imports_hs4_by_partner_annual.csv',index=False)
print(len(m), m.reporterISO.nunique(), m.month.min(), m.month.max())
