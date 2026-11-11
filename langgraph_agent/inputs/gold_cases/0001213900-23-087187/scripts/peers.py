import pandas as pd, numpy as np
d=pd.read_csv('shared/financials.csv',dtype={'adsh':str})
d=d[d.filed<=20231115]
d['sic2']=(d.sic//100).astype('Int64')
p=d[(d.sic2==78)&(d.cik!=1357671)&(d.ddate>=20230601)&(d.ddate<=20231231)]
p=p.sort_values('filed').groupby('cik').tail(1)
print(len(p),'peers'); print(p[['name','sic','form','ddate','total_assets','revenue','net_income']].to_string())
me=d[d.adsh=='0001213900-23-087187'].iloc[0]
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
for c in cols:
    s=p[c].dropna(); v=me[c]
    pct=(s<v).mean()*100
    print(f"{c:22s} co={v:>14,.0f} peer_med={s.median():>14,.0f} n={len(s)} pctile={pct:5.1f} missing_co={pd.isna(v)}")
for c in cols[1:]:
    r=(p[c]/p.total_assets).dropna(); v=me[c]/me.total_assets
    print(f"{c:22s}/TA co={v:8.2f} peer_med={r.median():8.2f} pctile={(r<v).mean()*100:5.1f}")
for c in ['net_income','operating_income','operating_cash_flow']:
    q=p[p.revenue>0]; r=(q[c]/q.revenue).dropna(); v=me[c]/me.revenue
    print(f"{c:22s}/Rev co={v:8.2f} peer_med={r.median():8.2f} pctile={(r<v).mean()*100:5.1f}")
p['cr']=p.current_assets/p.current_liabilities; p['lev']=p.total_liabilities/p.total_assets
print('CR co',me.current_assets/me.current_liabilities,'peer med',p.cr.median(),'pct',(p.cr<me.current_assets/me.current_liabilities).mean())
print('Lev co',me.total_liabilities/me.total_assets,'peer med',p.lev.median(),'pct',(p.lev<me.total_liabilities/me.total_assets).mean())
p.to_csv('final_cases/0001213900-23-087187/scripts/peers.csv',index=False)
