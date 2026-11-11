import pandas as pd, numpy as np
pd.set_option('display.width',250)
df=pd.read_csv('../../shared/financials.csv'); df=df[df.filed<=20240814]
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
p=df[(df.sic//100==37)&(df.cik!=1750153)&(df.filed>=20240401)]
p=p.sort_values('filed').groupby('cik').tail(1)
print('peers',len(p))
me=df[df.adsh=='0001628280-24-037286'].iloc[0]
for k in cols:
    v=p[k].dropna(); print(f"{k:22s} me={me[k]/1e6:9.1f}M  peer median={v.median()/1e6:9.1f}M  pct_rank={(v<me[k]).mean()*100:5.1f} n={len(v)}")
r=lambda d: pd.DataFrame({'liab/assets':d.total_liabilities/d.total_assets,'curr_ratio':d.current_assets/d.current_liabilities,
  'ni/assets':d.net_income/d.total_assets,'ocf/assets':d.operating_cash_flow/d.total_assets,'oi/assets':d.operating_income/d.total_assets,'ca/assets':d.current_assets/d.total_assets})
pr=r(p); mr=r(me.to_frame().T.astype({k:float for k in cols}))
for k in pr: 
    v=pr[k].replace([np.inf,-np.inf],np.nan).dropna(); m=float(mr[k].iloc[0]); print(f"{k:12s} me={m:7.3f} peer median={v.median():7.3f} pct_rank={(v<m).mean()*100:5.1f}")
# small loss-making peers
s=p[(p.revenue.fillna(0)<50e6)&(p.net_income<0)]
print(s[['name','filed','total_assets','revenue','net_income','operating_cash_flow']].assign(**{c:lambda d,c=c:(d[c]/1e6).round(1) for c in ['total_assets','revenue','net_income','operating_cash_flow']}).to_string())
