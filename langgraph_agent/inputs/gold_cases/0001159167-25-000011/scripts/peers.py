import pandas as pd, numpy as np
df=pd.read_csv('shared/financials.csv',dtype={'adsh':str})
df=df[df.filed<=20250312]
df['sic2']=(df.sic//100).astype('Int64')
p=df[(df.sic2==36)&(df.cik!=1159167)&(df.ddate>=20240630)&(df.ddate<=20250131)]
p=p.sort_values('filed').groupby('cik').tail(1)  # latest report per peer in window
print('peers',len(p))
me=df[df.adsh=='0001159167-25-000011'].iloc[0]
v=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
for c in v:
    s=p[c].dropna()
    print(f"{c:22s} me={me[c]/1e6:9.1f}M  peer median={s.median()/1e6:9.1f}M  pct_rank={(s<me[c]).mean()*100:5.1f}  n={len(s)}")
p=p.copy()
for d,num in [('ta',['current_assets','current_liabilities','total_liabilities','net_income','operating_income','operating_cash_flow']),]:
    pass
r={}
def rat(x):
    return dict(ca_ta=x.current_assets/x.total_assets, cl_ta=x.current_liabilities/x.total_assets, tl_ta=x.total_liabilities/x.total_assets,
                rev_ta=x.revenue/x.total_assets, ni_ta=x.net_income/x.total_assets, oi_rev=x.operating_income/x.revenue,
                ni_rev=x.net_income/x.revenue, ocf_ta=x.operating_cash_flow/x.total_assets, cur=x.current_assets/x.current_liabilities)
pr=pd.DataFrame(rat(p)); mr=rat(me)
for k in mr:
    s=pr[k].replace([np.inf,-np.inf],np.nan).dropna()
    print(f"{k:8s} me={mr[k]:7.3f} peer median={s.median():7.3f} pct_rank={(s<mr[k]).mean()*100:5.1f}")
# company ratio history
c=df[df.cik==1159167].sort_values('filed')
h=pd.DataFrame(rat(c)); h.index=c.ddate.values
print(h.round(3).tail(9))
