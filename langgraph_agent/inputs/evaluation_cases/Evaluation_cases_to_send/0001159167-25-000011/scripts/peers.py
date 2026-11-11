import pandas as pd, numpy as np
d=pd.read_csv('shared/financials.csv',dtype={'adsh':str})
d=d[d.filed<=20250312]   # drop anything filed after the report date
me=d[d.adsh=='0001159167-25-000011'].iloc[0]
p=d[(d.sic//100==36)&(d.cik!=1159167)&(d.filed>=20240913)&(d.filed<=20250312)]
p=p.sort_values('filed').groupby('cik').tail(1)   # latest report per peer
print('peers',len(p), 'forms',p.form.value_counts().to_dict())
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
for c in cols:
    s=p[c].dropna(); v=me[c]
    print(f"{c:20s} {v/1e6:9.1f}M  peer median {s.median()/1e6:9.1f}M  pct_rank {(s<v).mean()*100:5.1f}  n={len(s)}")
def ratios(x):
    return pd.DataFrame({'liab/assets':x.total_liabilities/x.total_assets,'current_ratio':x.current_assets/x.current_liabilities,
      'NI/assets':x.net_income/x.total_assets,'NI/rev':x.net_income/x.revenue,'OI/rev':x.operating_income/x.revenue,
      'OCF/assets':x.operating_cash_flow/x.total_assets,'rev/assets':x.revenue/x.total_assets})
r=ratios(p); m=ratios(me.to_frame().T.astype({c:float for c in cols})).iloc[0]
for c in r:
    s=r[c].replace([np.inf,-np.inf],np.nan).dropna()
    print(f"{c:14s} iRobot {m[c]:7.3f}  peer median {s.median():7.3f}  pct_rank {(s<m[c]).mean()*100:5.1f} n={len(s)}")
