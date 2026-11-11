import pandas as pd, numpy as np
df=pd.read_csv('../../shared/financials.csv'); df=df[df.filed<=20250905]
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
df['sic2']=(df.sic//100).astype('Int64')
me=df[df.adsh=='0001749723-25-000123'].iloc[0]
p=df[(df.sic2==49)&(df.cik!=1749723)&(df.ddate>=20250401)&(df.ddate<=20250930)&(df.form.str.startswith('10-'))]
p=p.sort_values('filed').groupby('cik').tail(1)
print('peers n=',len(p), 'missing in report:', [c for c in cols if pd.isna(me[c])])
rows=[]
for c in cols:
    s=p[c].dropna(); v=me[c]
    pct=(s<v).mean()*100
    ra = p[c]/p.total_assets if c!='total_assets' else None
    rv = v/me.total_assets
    pr = (ra.dropna()<rv).mean()*100 if ra is not None else np.nan
    rows.append([c,v/1e6,s.median()/1e6,round(pct),rv if c!='total_assets' else np.nan,(ra.median() if ra is not None else np.nan),pr, p[c].isna().sum()])
out=pd.DataFrame(rows,columns=['item','NFE_$m','peer_median_$m','NFE_pctile_$','NFE_/assets','peer_med_/assets','NFE_pctile_/assets','peers_missing'])
print(out.round(3).to_string())
# ratios
def r(x): return dict(lev=x.total_liabilities/x.total_assets, cr=x.current_assets/x.current_liabilities, ni_ta=x.net_income/x.total_assets, ocf_ta=x.operating_cash_flow/x.total_assets)
pr_=pd.DataFrame([r(x) for _,x in p.iterrows()])
for k,v in r(me).items(): print(k, round(v,3),'peer median',round(pr_[k].median(),3),'pctile',round((pr_[k]<v).mean()*100))
print('peers net income<0 share', (p.net_income<0).mean().round(3), ' NI/TA <= NFE share', (pr_.ni_ta<=r(me)['ni_ta']).mean().round(3))
p.to_csv('scripts/peer_rows.csv',index=False)
