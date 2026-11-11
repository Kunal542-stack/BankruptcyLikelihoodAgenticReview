import pandas as pd, numpy as np
df=pd.read_csv('shared/financials.csv')
df=df[df.filed<=20250808].copy()
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
co=df[df.cik==1083301].sort_values('filed')
print(co[['form','ddate','filed']+cols].to_string())
me=co[co.adsh=='0001083301-25-000061'].iloc[0]
df['sic2']=(df.sic//100).astype('Int64')
peers=df[(df.sic2==61)&(df.cik!=1083301)&(df.ddate>=20250101)&(df.ddate<=20250930)]
peers=peers.sort_values('filed').groupby('cik').tail(1)
print('peers n',len(peers))
print(peers[['name','form','ddate']].head(60).to_string())
def pct(s,v):
    s=s.dropna(); return (s<v).mean()*100, len(s)
for c in cols:
    p,n=pct(peers[c],me[c])
    print(f"{c:22s} {me[c]/1e6:10.1f}M  peer median {peers[c].median()/1e6:10.1f}M pctile {p:5.1f} n={n}")
for c in cols[1:]:
    base='revenue' if c in ['net_income','operating_income','operating_cash_flow'] else 'total_assets'
    r=peers[c]/peers[base]; v=me[c]/me[base]
    p,n=pct(r.replace([np.inf,-np.inf],np.nan),v)
    print(f"{c}/{base}: {v:.3f} peer median {r.median():.3f} pctile {p:.1f} n={n}")
r=peers.total_liabilities/peers.total_assets; print('lev peer med',r.median(), 'me',me.total_liabilities/me.total_assets, pct(r,me.total_liabilities/me.total_assets))
cr=peers.current_assets/peers.current_liabilities; print('CR peer med',cr.median(),'me',me.current_assets/me.current_liabilities)
