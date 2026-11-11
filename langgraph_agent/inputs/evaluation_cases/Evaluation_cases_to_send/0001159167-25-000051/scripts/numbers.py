import pandas as pd, numpy as np
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
df = pd.read_csv('../../shared/financials.csv')
df = df[df.filed <= 20250506]          # drop anything filed after the report date
cols = ['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
co = df[df.cik == 1159167].sort_values('filed')
print(co[['adsh','form','fp','ddate','filed']+cols].to_string())
me = co[co.adsh == '0001159167-25-000051'].iloc[0]
sic2 = str(int(me.sic))[:2]; print('sic', me.sic)
peers = df[(df.sic.astype('Int64').astype(str).str[:2] == sic2) & (df.cik != 1159167)]
peers = peers[(peers.ddate >= 20241001) & (peers.ddate <= 20250630)]
peers = peers.sort_values('filed').groupby('cik').tail(1)   # latest report per peer near the date
print('n peers', len(peers))
def pct(col, val, s): s = s.dropna(); return (s < val).mean()*100, len(s)
for c in cols:
    p, n = pct(c, me[c], peers[c])
    print(f"{c:22s} {me[c]/1e6:10.1f}M  peer median {peers[c].median()/1e6:10.1f}M  pctile {p:5.1f} (n={n})")
for c in cols[1:]:
    base = 'revenue' if c in ['net_income','operating_income','operating_cash_flow'] else 'total_assets'
    r = me[c]/me[base]; pr = (peers[c]/peers[base]).replace([np.inf,-np.inf],np.nan)
    p, n = pct(c, r, pr)
    print(f"{c:22s}/{base:12s} {r:7.3f} peer median {pr.median():7.3f} pctile {p:5.1f}")
for nm, s in [('liab/assets', me.total_liabilities/me.total_assets), ('current ratio', me.current_assets/me.current_liabilities)]:
    pr = peers.total_liabilities/peers.total_assets if nm=='liab/assets' else peers.current_assets/peers.current_liabilities
    print(nm, round(s,3), 'peer median', round(pr.median(),3), 'pctile', round((pr.dropna()<s).mean()*100,1))
co['lev'] = co.total_liabilities/co.total_assets; co['cr'] = co.current_assets/co.current_liabilities
print(co[['ddate','form','lev','cr']].to_string())
peers.to_csv('scripts/peers.csv', index=False)
