import pandas as pd, numpy as np
df = pd.read_csv('shared/financials.csv')
df = df[df.filed <= 20230809]                      # drop anything filed after the report date
df['sic2'] = (df.sic//100).astype('Int64')
me = df[df.adsh=='0001078207-23-000108'].iloc[0]
peers = df[(df.sic2==39) & (df.cik!=1078207) & (df.filed>=20230301)]
peers = peers.sort_values('filed').groupby('cik').tail(1)   # latest report per peer
print('peers:', len(peers)); print(peers[['name','form','ddate','total_assets','revenue','net_income']].to_string())
v = ['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
def ratios(r):
    return pd.Series({'total_assets':r.total_assets,'current_assets':r.current_assets,'current_liabilities':r.current_liabilities,
      'total_liabilities':r.total_liabilities,'revenue':r.revenue,'net_income':r.net_income,'operating_income':r.operating_income,'operating_cash_flow':r.operating_cash_flow,
      'CA/TA':r.current_assets/r.total_assets,'CL/TA':r.current_liabilities/r.total_assets,'TL/TA':r.total_liabilities/r.total_assets,
      'rev/TA':r.revenue/r.total_assets,'NI/TA':r.net_income/r.total_assets,'OI/TA':r.operating_income/r.total_assets,'OCF/TA':r.operating_cash_flow/r.total_assets,
      'NI/rev':r.net_income/r.revenue,'OI/rev':r.operating_income/r.revenue,'current_ratio':r.current_assets/r.current_liabilities})
P = peers.apply(ratios, axis=1); m = ratios(me)
out = pd.DataFrame({'nautilus':m, 'peer_median':P.median(), 'n':P.notna().sum(),
    'pct_rank':[ (P[c].dropna()<m[c]).mean()*100 for c in P.columns]})
pd.set_option('display.float_format', lambda x: f'{x:,.3f}')
print(out.to_string())
print('missing for nautilus:', [c for c in v if pd.isna(me[c])])
print('\n--- operating peers only (revenue >= $100M) ---')
op = peers[peers.revenue>=1e8]; Po = op.apply(ratios, axis=1)
print('n =', len(op))
for c in ['net_income','NI/TA','OI/TA','OCF/TA','NI/rev','TL/TA','current_ratio','total_assets']:
    s=Po[c].dropna(); print(f"{c:15s} nautilus {m[c]:12.3f}  median {s.median():12.3f}  worse-than-share {(s<m[c]).mean()*100:5.1f}%  rank {int((s<m[c]).sum())+1}/{len(s)+1}")
