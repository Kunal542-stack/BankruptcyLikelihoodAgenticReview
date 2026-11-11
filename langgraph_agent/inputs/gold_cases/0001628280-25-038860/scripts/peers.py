import pandas as pd, numpy as np
df = pd.read_csv('../../shared/financials.csv')
df = df[df.filed <= 20250807]
p = df[(df.sic//100==28)&(df.cik!=1001233)&(df.ddate.between(20250331,20250630))]
p = p.sort_values('ddate').groupby('cik').tail(1)
print('peers', len(p), p.ddate.value_counts().to_dict())
me = df[df.adsh=='0001628280-25-038860'].iloc[0]
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
for c in cols:
    s=p[c].dropna(); v=me[c]
    print(f"{c:22s} me={v/1e6:9.1f}M  peer_med={s.median()/1e6:9.1f}M  pctile={(s<v).mean()*100:5.1f}  n={len(s)}")
p=p.copy()
for c in cols[1:]:
    p[c+'_ta']=p[c]/p.total_assets
    s=p[c+'_ta'].replace([np.inf,-np.inf],np.nan).dropna(); v=me[c]/me.total_assets
    print(f"{c+'/TA':26s} me={v:7.2f} peer_med={s.median():7.2f} pctile={(s<v).mean()*100:5.1f}")
p['ni_rev']=p.net_income/p.revenue
s=p.ni_rev.replace([np.inf,-np.inf],np.nan).dropna()
print('NI/rev me', me.net_income/me.revenue, 'peer med', s.median(), 'pctile', (s<me.net_income/me.revenue).mean()*100)
p['cr']=p.current_assets/p.current_liabilities
print('CR me', me.current_assets/me.current_liabilities, 'peer med', p.cr.median(), (p.cr<me.current_assets/me.current_liabilities).mean()*100)
p['lev']=p.total_liabilities/p.total_assets
print('Lev me', me.total_liabilities/me.total_assets, 'peer med', p.lev.median(), (p.lev<me.total_liabilities/me.total_assets).mean()*100)
# biotech subset 2836
b=p[p.sic==2836]
print('2836 peers',len(b),'NI/TA med',(b.net_income/b.total_assets).median(),'pctile',((b.net_income/b.total_assets)<me.net_income/me.total_assets).mean()*100, 'TA med', b.total_assets.median()/1e6)
print('share of 28xx peers with neg NI', (p.net_income<0).mean(), 'with liab>assets',(p.total_liabilities>p.total_assets).mean())
