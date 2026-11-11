import pandas as pd, numpy as np
df=pd.read_csv('../../shared/financials.csv'); df=df[df.filed<=20230816]
me=df[df.adsh=='0001368148-23-000092'].iloc[0]
print('sic',me.sic)
p=df[(df.sic//100==me.sic//100)&(df.cik!=1368148)&(df.ddate==20230630)&(df.form=='10-Q')]
p=p.sort_values('filed').drop_duplicates('cik',keep='last')
print('n peers',len(p), 'sic 2836 peers', (p.sic==2836).sum())
v=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
def pct(s,x):
    s=s.dropna(); return round(100*(s<x).mean(),1), len(s)
rows=[]
for k in v:
    rows.append((k, me[k]/1e6, p[k].median()/1e6, *pct(p[k],me[k])))
print(pd.DataFrame(rows,columns=['var','ATHX $m','peer median $m','pctile','n']).round(2))
# ratios
for d in (p,):
    d=d.copy()
d=p.copy(); 
r={'NI/TA':me.net_income/me.total_assets,'TL/TA':me.total_liabilities/me.total_assets,'CA/CL':me.current_assets/me.current_liabilities,'OCF/TA':me.operating_cash_flow/me.total_assets,'CA/TA':me.current_assets/me.total_assets}
pr={'NI/TA':d.net_income/d.total_assets,'TL/TA':d.total_liabilities/d.total_assets,'CA/CL':d.current_assets/d.current_liabilities,'OCF/TA':d.operating_cash_flow/d.total_assets,'CA/TA':d.current_assets/d.total_assets}
for k in r:
    s=pr[k].replace([np.inf,-np.inf],np.nan).dropna()
    print(k, round(r[k],2),'peer med',round(s.median(),2),'pctile below',round(100*(s<r[k]).mean(),1),len(s))
print('peers TL>TA share', round((d.total_liabilities>d.total_assets).mean()*100,1))
print('peers CA<CL share', round((d.current_assets<d.current_liabilities).mean()*100,1))
print('peers net loss share', round((d.net_income<0).mean()*100,1))
p.to_csv('scripts/peers_q2_2023.csv',index=False)
