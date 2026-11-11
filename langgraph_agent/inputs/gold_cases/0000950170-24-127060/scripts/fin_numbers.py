import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
df=pd.read_csv('shared/financials.csv')
df=df[df.filed<=20241114]
c=df[df.cik==1580063].sort_values('filed')
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
print(c[['adsh','form','fp','ddate','filed','sic']+cols].to_string())
sic=c.sic.iloc[-1]; print('sic',sic)
p=df[(df.sic//100==sic//100)&(df.cik!=1580063)&(df.ddate>=20240630)&(df.ddate<=20241031)]
p=p.sort_values('filed').groupby('cik').tail(1)
print('peers',len(p))
t=c[c.adsh=='0000950170-24-127060'].iloc[0]
for k in cols:
    s=p[k].dropna(); v=t[k]
    print(f"{k:22s} {v/1e6:10.2f}M  peer median {s.median()/1e6:9.2f}M  pct rank {(s<v).mean()*100:5.1f} n={len(s)}")
for k in cols[1:]:
    r=(p[k]/p.total_assets).replace([np.inf,-np.inf],np.nan).dropna(); v=t[k]/t.total_assets
    print(f"{k:22s}/TA {v:8.2f} peer median {r.median():7.2f} pct rank {(r<v).mean()*100:5.1f}")
p2=p.assign(lev=p.total_liabilities/p.total_assets, cr=p.current_assets/p.current_liabilities)
print('peer lev median',p2.lev.median(),'share lev>1',(p2.lev>1).mean(),'peer CR median',p2.cr.median())
print('company lev',t.total_liabilities/t.total_assets,'CR',t.current_assets/t.current_liabilities, 'equity',(t.total_assets-t.total_liabilities)/1e6)
