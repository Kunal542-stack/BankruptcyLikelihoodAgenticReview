import pandas as pd, numpy as np
d=pd.read_csv('shared/financials.csv'); d=d[d.filed<=20250814]
d['sic2']=(d.sic//100).astype('Int64')
me=d[d.adsh=='0001641172-25-023889'].iloc[0]
p=d[(d.sic2==73)&(d.cik!=1643988)&(d.ddate>=20250331)&(d.ddate<=20250930)]
p=p.sort_values('filed').groupby('cik').tail(1)
print('peers',len(p))
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
for c in cols:
    s=p[c].dropna(); v=me[c]
    print(f"{c:22s} me={v:14,.0f} peer_med={s.median():14,.0f} pct={(s<v).mean()*100:5.1f} n={len(s)}")
p=p.assign(lev=p.total_liabilities/p.total_assets, cr=p.current_assets/p.current_liabilities,
  ni_a=p.net_income/p.total_assets, ocf_a=p.operating_cash_flow/p.total_assets, ni_r=p.net_income/p.revenue)
mev=dict(lev=me.total_liabilities/me.total_assets, cr=me.current_assets/me.current_liabilities,
  ni_a=me.net_income/me.total_assets, ocf_a=me.operating_cash_flow/me.total_assets, ni_r=me.net_income/me.revenue)
for k,v in mev.items():
    s=p[k].replace([np.inf,-np.inf],np.nan).dropna()
    print(f"{k:6s} me={v:8.2f} peer_med={s.median():8.2f} pct={(s<v).mean()*100:5.1f}")
