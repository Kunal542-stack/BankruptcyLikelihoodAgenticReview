import pandas as pd
df=pd.read_csv('../../shared/financials.csv')
df=df[df.filed<=20230814]
c=df[df.cik==1841800].sort_values('filed'); pd.set_option('display.width',250,'display.max_columns',30)
print(c.drop(columns=['cik','name']).to_string())
sic=c.sic.iloc[0]; print('sic',sic)
p=df[(df.sic//100==sic//100)&(df.cik!=1841800)&(df.ddate>=20230331)&(df.ddate<=20230930)]
p=p.sort_values('filed').groupby('cik').tail(1)
print('peers',len(p))
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
me=c[c.adsh=='0000950170-23-042370'].iloc[0]
for k in cols:
    s=p[k].dropna(); print(f"{k:22s} me={me[k]/1e6:9.2f}M  peer median={s.median()/1e6:9.2f}M  pct rank={(s<me[k]).mean()*100:5.1f}  n={len(s)}")
p=p.copy()
for k in ['net_income','operating_income','operating_cash_flow','total_liabilities','current_assets']:
    r=p[k]/p.total_assets; m=me[k]/me.total_assets
    print(f"{k}/TA me={m:.2f} peer median={r.median():.2f} pct rank={(r<m).mean()*100:.0f}")
for k in ['net_income','operating_cash_flow']:
    r=(p[k]/p.revenue).replace([float('inf'),-float('inf')],pd.NA).dropna(); m=me[k]/me.revenue
    print(f"{k}/rev me={m:.2f} peer median={r.median():.2f} pct rank={(r<m).mean()*100:.0f}")
cr=p.current_assets/p.current_liabilities; print('current ratio me',me.current_assets/me.current_liabilities,'peer med',cr.median(),'rank',(cr<me.current_assets/me.current_liabilities).mean())
print('TL/TA me',me.total_liabilities/me.total_assets)
