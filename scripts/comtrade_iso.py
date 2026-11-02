import pandas as pd
CM={156:'CHN',699:'IND',842:'USA',392:'JPN',410:'KOR',826:'GBR',792:'TUR',764:'THA',458:'MYS',704:'VNM',682:'SAU',76:'BRA',757:'CHE',36:'AUS',124:'CAN',586:'PAK',360:'IDN',643:'RUS',818:'EGY',702:'SGP',710:'ZAF',484:'MEX',554:'NZL',32:'ARG',804:'UKR',376:'ISR',608:'PHL',144:'LKA',404:'KEN',512:'OMN',634:'QAT',414:'KWT',48:'BHR',251:'FRA',276:'DEU',380:'ITA',528:'NLD',724:'ESP',616:'POL',56:'BEL'}
def load(path):
    c=pd.read_csv(path,dtype={'cmdCode':str,'period':str})
    c['reporterISO']=c.reporterCode.map(CM); c['partnerISO']='ARE'
    c=c.drop_duplicates(['period','reporterCode','cmdCode','flowCode','partnerCode','customsCode','motCode','partner2Code'])
    c['month']=c.period.str[:4]+'-'+c.period.str[4:]
    return c
