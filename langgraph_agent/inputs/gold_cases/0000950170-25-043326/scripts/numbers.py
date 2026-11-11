import sys, pandas as pd
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
base = sys.argv[1]
df = pd.read_csv(f'{base}/shared/financials.csv', dtype={'filed': int})
df = df[df.filed <= 20250321]          # drop everything filed after the report date
CIK, ADSH = 1936224, '0000950170-25-043326'
cols = ['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
co = df[df.cik == CIK].sort_values('filed')
print(co[['adsh','form','fp','ddate','filed']+cols].to_string())
me = co[co.adsh == ADSH].iloc[0]
sic2 = str(int(me.sic))[:2]
print('sic', me.sic, 'sic2', sic2)
# peers: same 2-digit sic, latest report per company with ddate within +-6 months of 2024-12-31
p = df[(df.sic.fillna(0).astype(int).astype(str).str[:2] == sic2) & (df.cik != CIK)]
p = p[(p.ddate >= 20240630) & (p.ddate <= 20250331)].sort_values('filed').groupby('cik').tail(1)
print('peers', len(p))
def ranks(row, peers, label):
    out = []
    for c in cols:
        v = row[c]
        s = peers[c].dropna()
        pct = (s < v).mean()*100 if pd.notna(v) else float('nan')
        out.append((c, v, s.median(), round(pct, 0), len(s)))
    print(label); print(pd.DataFrame(out, columns=['item','company','peer_median','pctile','n']).to_string())
ranks(me, p, 'dollars')
# ratios
def rat(d):
    r = pd.DataFrame(index=d.index)
    for c in ['current_assets','current_liabilities','total_liabilities','net_income','operating_income','operating_cash_flow']:
        r[c+'/TA'] = d[c]/d.total_assets
    r['revenue/TA'] = d.revenue/d.total_assets
    r['NI/rev'] = d.net_income/d.revenue
    r['OCF/rev'] = d.operating_cash_flow/d.revenue
    r['current_ratio'] = d.current_assets/d.current_liabilities
    return r
pr, mr = rat(p), rat(co)
mrow = mr.loc[co.adsh == ADSH].iloc[0]
out = []
for c in pr.columns:
    s = pr[c].replace([float('inf'), -float('inf')], float('nan')).dropna()
    out.append((c, mrow[c], s.median(), round((s < mrow[c]).mean()*100, 0), len(s)))
print(pd.DataFrame(out, columns=['ratio','company','peer_median','pctile','n']).to_string())
print(mr.assign(filed=co.filed.values, form=co.form.values).to_string())
print('peer names sample:', p.sort_values('total_assets').name.tolist()[:60])
p.to_csv(f'{base}/final_cases/{ADSH}/scripts/peers.csv', index=False)
