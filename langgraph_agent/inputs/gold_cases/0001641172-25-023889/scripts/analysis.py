import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
B='final_cases/0001641172-25-023889/'
d=pd.read_csv('shared/financials.csv'); d=d[d.filed<=20250814]
c=d[d.cik==1643988].sort_values('ddate')
me=c[c.adsh=='0001641172-25-023889'].iloc[0]; prev=c[c.ddate==20240630].iloc[0]
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
print("max filed in used rows", d.filed.max())
for k in cols: print(f"{k:22s} now={me[k]:14,.0f} yr_before={prev[k]:14,.0f} chg={(me[k]/prev[k]-1)*100:6.1f}%  /assets now={me[k]/me.total_assets:6.2f} before={prev[k]/prev.total_assets:6.2f}")
print("lev", me.total_liabilities/me.total_assets, prev.total_liabilities/prev.total_assets)
print("CR", me.current_assets/me.current_liabilities, prev.current_assets/prev.current_liabilities)
print("equity", me.total_assets-me.total_liabilities)
# burn
cash=109692; ocf9=4230300; ocf6=3233491; ocf3m=2621353 if False else None
q3=ocf9-ocf6; print("Q3 OCF burn",q3,"monthly",q3/3,"months left",cash/(q3/3),"9M avg months",cash/(ocf9/9))
print("Q1 burn", -14922894/4*0 if False else None)
# non-cash adjustments from cash flow statements
nc={'FY2023':(-31963679,[6721476,1003502,65497,2946404,76696,630629,7997849,596938],-14595226),
    'FY2024':(-24495602,[1900269,1414537,633902,3024804,42569,708990,110363,25424,315863,4232673,124132],-7337757),
    '9M FY2024':(-18307652,[1635218,1037320,180635,2356717,26274,284065,25424,3371933,124135],-5310707),
    '9M FY2025':(-12178735,[651014,733849,553642,51393,88002,161481,2094857],-4230300)}
for k,(ni,a,o) in nc.items(): print(k,"NI",ni,"noncash",sum(a),"adj loss",ni+sum(a),"share noncash",round(sum(a)/-ni,2),"OCF",o)
print("Q3 rev yoy", 1285262/4350570-1, "9M rev yoy", 6696901/18524289-1)
dem={'Bellino $2.0M note (now Cassidy)':2000000,'ASCAP settlement':1175000,'Agile Lending':1000476,'NRS confession of judgment':827825,
 'Cara Comm. licence':361800,'May-2023 line, lender 1':300000,'1800 Diagonal (150% demand)':286326,'AFG equipment':268035,'Balboa equipment':82427}
tot=sum(dem.values()); print("demands total",tot,"ex Bellino",tot-2000000, "x cash", (tot-2000000)/cash)
# peers
d['sic2']=d.sic//100
p=d[(d.sic2==73)&(d.cik!=1643988)&(d.ddate>=20250331)&(d.ddate<=20250930)].sort_values('filed').groupby('cik').tail(1)
print("n peers",len(p))
for k in cols:
    s=p[k].dropna(); print(f"peer {k:22s} med={s.median():14,.0f} share_below_me={(s<me[k]).mean()*100:5.1f}%")
p=p.assign(lev=p.total_liabilities/p.total_assets,cr=p.current_assets/p.current_liabilities,nia=p.net_income/p.total_assets,ocfa=p.operating_cash_flow/p.total_assets,nir=p.net_income/p.revenue)
mv=dict(lev=me.total_liabilities/me.total_assets,cr=me.current_assets/me.current_liabilities,nia=me.net_income/me.total_assets,ocfa=me.operating_cash_flow/me.total_assets,nir=me.net_income/me.revenue)
for k,v in mv.items():
    s=p[k].replace([np.inf,-np.inf],np.nan).dropna(); print(f"ratio {k} me={v:.2f} med={s.median():.2f} share_below_me={(s<v).mean()*100:.1f}%")
small=p[p.total_assets<20e6]; print("small peers (<$20M assets)",len(small),"median NI/assets",(small.net_income/small.total_assets).median(),"lev med",(small.total_liabilities/small.total_assets).median(),
  "share small with lev>me",(small.total_liabilities/small.total_assets>mv['lev']).mean())
# charts
c['dt']=pd.to_datetime(c.ddate.astype(str))
fig,ax=plt.subplots(figsize=(7,4))
ax.plot(c.dt,c.total_assets/1e6,'o-',label='Total assets'); ax.plot(c.dt,c.current_liabilities/1e6,'o-',label='Current liabilities'); ax.plot(c.dt,c.total_liabilities/1e6,'o--',label='Total liabilities')
ax.set_ylabel('$ million'); ax.set_ylim(0); ax.set_title('Loop Media: assets shrank while liabilities kept rising'); ax.legend(); fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(B+'charts/balance_sheet.png',dpi=120)
fig,ax=plt.subplots(figsize=(7,4))
qc=pd.DataFrame({'q':['Q3 FY24\n(Jun-24)','Q4 FY24\n(Sep-24)','Q1 FY25\n(Dec-24)','Q2 FY25\n(Mar-25)','Q3 FY25\n(Jun-25)'],'cash':[1546089,824658,323587,425646,109692]})
ax.bar(qc.q,qc.cash/1e3,color='tab:blue'); ax.set_ylabel('$ thousand'); ax.set_title('Cash at quarter end (from the filings)')
for i,v in enumerate(qc.cash): ax.text(i,v/1e3+20,f"{v/1e3:,.0f}",ha='center')
fig.tight_layout(); fig.savefig(B+'charts/cash.png',dpi=120)
fig,ax=plt.subplots(figsize=(7,4.2))
items=list(dem.items()); ax.barh([k for k,_ in items][::-1],[v/1e3 for _,v in items][::-1],color=['tab:orange' if 'Cassidy' in k else 'tab:red' for k,_ in items][::-1])
ax.axvline(cash/1e3,color='k',ls='--'); ax.text(cash/1e3+30,0,f'Cash on 30 Jun 2025: ${cash/1e3:,.0f}K',va='center')
ax.set_xlabel('$ thousand'); ax.set_title(f'Demands Jun–Aug 2025: ${(tot-2e6)/1e6:.1f}M from outsiders\n+ $2.0M note now held by the majority owner (orange)',fontsize=10); fig.tight_layout(); fig.savefig(B+'charts/demands_vs_cash.png',dpi=120)
fig,ax=plt.subplots(figsize=(7,4))
s=p.lev.replace([np.inf,-np.inf],np.nan).dropna().clip(upper=10)
ax.hist(s,bins=50,color='grey'); ax.axvline(min(mv['lev'],10),color='r',lw=2); ax.text(mv['lev']-0.2,ax.get_ylim()[1]*0.8,f"Loop Media {mv['lev']:.1f}x",color='r',ha='right')
ax.set_xlabel('Total liabilities / total assets (values above 10 shown in the 10 bin)'); ax.set_ylabel('SIC 73 peers'); ax.set_title(f'Leverage vs {len(s)} SIC-73 peers (Mar–Sep 2025 periods)'); fig.tight_layout(); fig.savefig(B+'charts/peer_leverage.png',dpi=120)
