import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
df = pd.read_csv('shared/financials.csv')
df = df[df.filed <= 20240809]           # drop everything filed after the report date
cols = ['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
co = df[df.cik==1813914].sort_values('filed')
print(co[['adsh','form','fp','ddate','filed']+cols].to_string())
me = co[co.adsh=='0000950170-24-094897'].iloc[0]
print('sic', me.sic)
sic2 = str(int(me.sic))[:2]
peers = df[(df.sic.fillna(0).astype(int).astype(str).str[:2]==sic2) & (df.cik!=1813914)]
peers = peers[(peers.ddate>=20240101)&(peers.ddate<=20240930)].sort_values('filed').groupby('cik').tail(1)
print('peers', len(peers))
def ratios(x):
    r = pd.DataFrame(index=x.index)
    for c in cols: r[c] = x[c]
    for c in ['current_assets','current_liabilities','total_liabilities','net_income','operating_income','operating_cash_flow']:
        r[c+'/TA'] = x[c]/x.total_assets
    for c in ['net_income','operating_income','operating_cash_flow']:
        r[c+'/Rev'] = x[c]/x.revenue
    r['current_ratio'] = x.current_assets/x.current_liabilities
    return r
P = ratios(peers); M = ratios(me.to_frame().T.astype({c:float for c in cols}))
out=[]
for c in P.columns:
    v = float(M[c].iloc[0]); s = P[c].dropna()
    out.append((c, v, s.median(), (s<v).mean()*100, len(s)))
print(pd.DataFrame(out, columns=['metric','CMAX','peer_median','pctile(CMAX>peer%)','n']).to_string())
