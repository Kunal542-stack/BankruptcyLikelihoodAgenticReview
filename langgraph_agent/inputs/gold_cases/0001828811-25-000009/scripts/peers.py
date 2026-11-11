import pandas as pd, numpy as np
df=pd.read_csv('../../shared/financials.csv',dtype={'adsh':str})
df=df[df.filed<=20250331]
df['sic2']=(df.sic//100)
p=df[(df.sic2==49)&(df.cik!=1828811)&(df.ddate>=20240701)&(df.ddate<=20241231)]
p=p.sort_values('filed').groupby('cik').tail(1)   # latest report per peer
print('peers',len(p), 'forms',p.form.value_counts().to_dict())
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
me=df[df.adsh=='0001828811-25-000009'].iloc[0]
rows=[]
for c in cols:
    v=me[c]; s=p[c].dropna()
    pct=(s<v).mean()*100
    r={'var':c,'LICY':v/1e6,'peer_median':s.median()/1e6,'pct_rank':round(pct),'n':len(s)}
    base='revenue' if c in('net_income','operating_income','operating_cash_flow') else 'total_assets'
    sr=(p[c]/p['total_assets']).replace([np.inf,-np.inf],np.nan).dropna()
    r['LICY_/TA']=v/me.total_assets; r['peer_med_/TA']=sr.median(); r['pct_rank_/TA']=round((sr<v/me.total_assets).mean()*100)
    rows.append(r)
print(pd.DataFrame(rows).round(3).to_string())
# ratios
for nm,f in [('liab/assets',lambda d:d.total_liabilities/d.total_assets),('current ratio',lambda d:d.current_assets/d.current_liabilities),('NI/rev',lambda d:d.net_income/d.revenue),('OCF/TA',lambda d:d.operating_cash_flow/d.total_assets),('NI/TA',lambda d:d.net_income/d.total_assets)]:
    s=f(p).replace([np.inf,-np.inf],np.nan).dropna(); v=f(me)
    print(f'{nm}: LICY {v:.3f} peer median {s.median():.3f} LICY pct rank {(s<v).mean()*100:.0f} (n={len(s)})')
print('peers with NI/TA below LICY:', p.assign(r=p.net_income/p.total_assets).query('r < @me.net_income/@me.total_assets')[['name','total_assets','net_income']].to_string())
