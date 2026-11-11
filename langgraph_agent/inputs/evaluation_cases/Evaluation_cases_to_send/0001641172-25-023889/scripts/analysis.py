import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
ROOT='/Users/pramukhvenkateshkoushik/Desktop/Data_cap/investigator/'
OUT=ROOT+'final_cases-1/0001641172-25-023889/'
df=pd.read_csv(ROOT+'shared/financials.csv'); df=df[df.filed<=20250814].copy()
assert df.filed.max()<=20250814
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
co=df[df.cik==1643988].sort_values('ddate')
cur=co[co.adsh=='0001641172-25-023889'].iloc[0]; prev=co[co.ddate==20240630].iloc[0]
df['sic2']=df.sic.fillna(0).astype(int).astype(str).str[:2]
peers=df[(df.sic2=='73')&(df.cik!=1643988)&df.ddate.between(20250101,20250930)].sort_values('filed').groupby('cik').tail(1).copy()
print('peers n',len(peers),'missing in this report:',[c for c in cols if pd.isna(cur[c])])
print('\n8 numbers: current | year before | change | peer median | pct of peers below')
for c in cols:
    p=peers[c].dropna()
    print(f"{c:20s} {cur[c]/1e6:8.2f}M {prev[c]/1e6:8.2f}M {(cur[c]/prev[c]-1)*100:+6.0f}% {p.median()/1e6:9.2f}M  pctile {(p<cur[c]).mean()*100:3.0f}")
def ratios(d):
    return pd.DataFrame({'NI/TA':d.net_income/d.total_assets,'TL/TA':d.total_liabilities/d.total_assets,
     'CA/CL':d.current_assets/d.current_liabilities,'OCF/TA':d.operating_cash_flow/d.total_assets,'NI/Rev':d.net_income/d.revenue,'TA':d.total_assets})
pr=ratios(peers).replace([np.inf,-np.inf],np.nan); cr=ratios(cur.to_frame().T.astype({c:float for c in cols})).iloc[0]; pv=ratios(prev.to_frame().T.astype({c:float for c in cols})).iloc[0]
print('\nratios: current | year before | peer median | pctile')
for k in pr.columns:
    print(f"{k:7s} {cr[k]:8.3f} {pv[k]:8.3f} {pr[k].median():8.3f} pctile {(pr[k].dropna()<cr[k]).mean()*100:3.0f}")
# small-peer check: peers with total assets < $10M
sm=pr[pr.TA<10e6]; print('\nsmall peers (<$10M assets) n',len(sm))
for k in ['NI/TA','TL/TA','CA/CL','OCF/TA']: print(f"  {k} small-peer median {sm[k].median():.3f}, co pctile {(sm[k].dropna()<cr[k]).mean()*100:.0f}")
# from filings (10-Q filed 2025-08-14, 10-Qs Feb/May 2025, 10-K Dec 2024)
cash={'2024-09-30':824658,'2024-12-31':323587,'2025-03-31':425646,'2025-06-30':109692}
ocf_ytd={'Q1':cur.operating_cash_flow*0+co[co.ddate==20241231].operating_cash_flow.iloc[0]/4,
         'H1':co[co.ddate==20250331].operating_cash_flow.iloc[0]/2,'9M':cur.operating_cash_flow*3/4}
q3=ocf_ytd['9M']-ocf_ytd['H1']; q2=ocf_ytd['H1']-ocf_ytd['Q1']
print('\nOCF 9M',round(ocf_ytd['9M']),'Q1',round(ocf_ytd['Q1']),'Q2',round(q2),'Q3',round(q3))
m9=-ocf_ytd['9M']/9; m3=-q3/3
print(f"monthly burn 9M avg {m9:,.0f}; last quarter {m3:,.0f}; months of cash: {cash['2025-06-30']/m9:.2f} (9M rate), {cash['2025-06-30']/m3:.2f} (Q3 rate)")
print(f"current ratio {cur.current_assets/cur.current_liabilities:.3f}; TL/TA {cur.total_liabilities/cur.total_assets:.2f}; equity {cur.total_assets-cur.total_liabilities:,.0f}")
debt_cur=700000+2152668+3000000+851291; print('current debt-type lines (non-rev LOC+conv+conv RP+other)',debt_cur)
# non-cash adjustment, same items each period from the cash-flow statement
nc={'9M FY25':(-12178735,[651014,733849,553642,51393,88002,161481,2094857],-4230300),
    '9M FY24':(-18307652,[1635218,1037320,180635,2356717,26274,284065,25424,3371933,124135],-5310707),
    'FY24':(-24495602,[1900269,1414537,633902,3024804,42569,708990,110363,25424,315863,4232673,124132],-7337757),
    'FY23':(-31963679,[6721476,1003502,65497,2946404,76696,630629,7997849,596938],-14595226)}
print('\nnon-cash adjusted loss')
for k,(nl,a,o) in nc.items(): print(f"  {k}: net loss {nl:,} non-cash {sum(a):,} ({sum(a)/-nl*100:.0f}%) adjusted {nl+sum(a):,} OCF {o:,}")
print('revenue 9M', 6696901/18524289-1, 'Q3', 1285262/4350570-1, 'gross margin Q3', 271245/1285262)
print('interest 9M', 3239703, 'cash interest 9M', 1644376, 'AP change', 9438530/6250106-1)
print('defaulted amounts sum', 889000+2000000+286326+1175000+82427+361800+1000476+268035+827825)
# CHARTS
qr=pd.DataFrame({'q':['Q1 FY24\nDec-23','Q2 FY24\nMar-24','Q3 FY24\nJun-24','Q4 FY24*\nSep-24','Q1 FY25\nDec-24','Q2 FY25\nMar-25','Q3 FY25\nJun-25'],
 'rev':[10171256,4002463,4350570,22254959-18524289,3730723,1680916,1285262],'nl':[-5285402,-7570633,-5451617,-24495602+18307652,-4540221,-4233653,-3404861]})
fig,ax=plt.subplots(figsize=(8,4)); ax.bar(qr.q,qr.rev/1e6,color='steelblue',label='Quarterly revenue')
ax.plot(qr.q,-qr.nl/1e6,'o-',color='firebrick',label='Quarterly net loss')
ax.set_ylabel('$ millions'); ax.set_ylim(0,None); ax.set_title('Revenue fell 70% (Q3 vs Q3); since Mar-24 every quarter loses more than it sells')
ax.text(0.01,-0.22,'*Q4 FY24 = FY2024 10-K annual minus 9M FY24 10-Q',transform=ax.transAxes,fontsize=8)
ax.legend(); plt.tight_layout(); plt.savefig(OUT+'charts/1_revenue_vs_loss.png',dpi=120); plt.close()
d=co[co.ddate>=20230331]
fig,ax=plt.subplots(figsize=(8,4)); x=pd.to_datetime(d.ddate.astype(str))
ax.plot(x,d.current_liabilities/1e6,'o-',color='firebrick',label='Current liabilities')
ax.plot(x,d.current_assets/1e6,'o-',color='steelblue',label='Current assets')
cx=pd.to_datetime(list(cash)); ax.plot(cx,np.array(list(cash.values()))/1e6,'s--',color='black',label='Cash (from filings)')
ax.set_ylim(0,None); ax.set_ylabel('$ millions'); ax.set_title('Current liabilities ~14x short-term assets; cash $0.11M at Jun-25')
ax.legend(); plt.tight_layout(); plt.savefig(OUT+'charts/2_liquidity.png',dpi=120); plt.close()
fig,axs=plt.subplots(1,3,figsize=(11,3.6))
for a,(k,lo,hi) in zip(axs,[('TL/TA',0,3),('CA/CL',0,5),('NI/TA',-2,0.5)]):
    v=pr[k].dropna().clip(lo,hi); a.hist(v,bins=40,color='lightgray'); a.axvline(np.clip(cr[k],lo,hi),color='firebrick',lw=2)
    a.set_title(f"{k}: Loop {cr[k]:.2f} vs median {pr[k].median():.2f}",fontsize=9); a.set_yticks([])
axs[0].set_xlabel('clipped at 3'); axs[1].set_xlabel('clipped at 5'); axs[2].set_xlabel('clipped at -2 (Loop is -4.8)')
fig.suptitle(f'Loop vs {len(pr)} SIC-73 peers (2025 reports): Loop in worst 4-8% on each (red line; grey bars at edges are clipped peers)',fontsize=10)
plt.tight_layout(); plt.savefig(OUT+'charts/3_peers.png',dpi=120); plt.close()
