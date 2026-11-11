import pandas as pd, sys
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
df = pd.read_csv('shared/financials.csv')
df = df[df.filed <= 20250814]            # drop everything filed after the report date
cols = ['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
co = df[df.cik==1643988].sort_values('filed')
print(co[['adsh','form','fp','ddate','filed']+cols].to_string())
row = co[co.adsh=='0001641172-25-023889'].iloc[0]
print('\nSIC', row.sic)
sic2 = str(int(row.sic))[:2]
df['sic2'] = df.sic.fillna(0).astype(int).astype(str).str[:2]
peers = df[(df.sic2==sic2)&(df.cik!=1643988)&(df.ddate.between(20250101,20250930))]
peers = peers.sort_values('filed').groupby('cik').tail(1)   # latest report per peer in window
print('peers', len(peers))
for c in cols:
    p = peers[c].dropna()
    pct = (p < row[c]).mean()*100 if pd.notna(row[c]) else float('nan')
    print(f"{c:22s} co={row[c]:>16,.0f} peer_median={p.median():>16,.0f} n={len(p)} pctile={pct:.0f}")
# ratios
peers = peers.copy()
for d in [peers]:
    d['ni_ta']=d.net_income/d.total_assets; d['tl_ta']=d.total_liabilities/d.total_assets
    d['cr']=d.current_assets/d.current_liabilities; d['ocf_ta']=d.operating_cash_flow/d.total_assets
    d['ni_rev']=d.net_income/d.revenue
r = dict(ni_ta=row.net_income/row.total_assets, tl_ta=row.total_liabilities/row.total_assets,
         cr=row.current_assets/row.current_liabilities, ocf_ta=row.operating_cash_flow/row.total_assets, ni_rev=row.net_income/row.revenue)
for k,v in r.items():
    p=peers[k].replace([float('inf'),-float('inf')],float('nan')).dropna()
    print(f"{k:8s} co={v:8.3f} peer_median={p.median():8.3f} pctile={(p<v).mean()*100:.0f} n={len(p)}")
print(peers.name.head(40).tolist())
