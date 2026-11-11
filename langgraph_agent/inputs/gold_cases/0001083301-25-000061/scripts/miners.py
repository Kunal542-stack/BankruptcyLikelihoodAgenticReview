import pandas as pd
df=pd.read_csv('shared/financials.csv'); df=df[df.filed<=20250808]
names=['APPLIED DIGITAL CORP.','BIT DIGITAL, INC','CIPHER MINING INC.','CLEANSPARK, INC.','CORE SCIENTIFIC, INC./TX','GREENIDGE GENERATION HOLDINGS INC.','GRYPHON DIGITAL MINING, INC.','HUT 8 CORP.','MARA HOLDINGS, INC.','MAWSON INFRASTRUCTURE GROUP INC.','RIOT PLATFORMS, INC.','SOLUNA HOLDINGS, INC','SPHERE 3D CORP.','BITMINE IMMERSION TECHNOLOGIES, INC.']
m=df[df.name.isin(names)].sort_values('filed').groupby('cik').tail(1).copy()
t=df[df.adsh=='0001083301-25-000061']
m=pd.concat([m,t])
m['lev']=m.total_liabilities/m.total_assets; m['cr']=m.current_assets/m.current_liabilities
m['ni_ta']=m.net_income/m.total_assets; m['ni_rev']=m.net_income/m.revenue; m['ocf_ta']=m.operating_cash_flow/m.total_assets
pd.set_option('display.width',250)
print(m[['name','ddate','total_assets','revenue','net_income','operating_cash_flow','lev','cr','ni_ta','ni_rev','ocf_ta']].sort_values('ni_ta').to_string())
