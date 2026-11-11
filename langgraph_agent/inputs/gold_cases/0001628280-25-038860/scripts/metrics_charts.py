import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
df = pd.read_csv('../../shared/financials.csv'); df = df[df.filed <= 20250807]
c = df[df.cik==1001233].sort_values('ddate').copy()
cur = c[c.adsh=='0001628280-25-038860'].iloc[0]; prev = c[c.ddate==20240630].iloc[0]
print('max filed used', df.filed.max())
for k in ['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']:
    print(f"{k:20s} {cur[k]/1e6:8.1f} {prev[k]/1e6:8.1f} chg {(cur[k]-prev[k])/abs(prev[k])*100:6.0f}%  /TA {cur[k]/cur.total_assets:5.2f}")
print('leverage TL/TA', cur.total_liabilities/cur.total_assets, 'equity', (cur.total_assets-cur.total_liabilities)/1e6)
print('current ratio', cur.current_assets/cur.current_liabilities)
cash=38.344
h1=-44.307; q1=-26.149; q2=h1-q1
print('Q1 OCF',q1,'Q2 OCF',q2)
for lab,b in [('H1 avg',-h1/6),('Q2',-q2/3),('Q1',-q1/3)]:
    print(lab,'burn/mo',round(b,2),'months',round(cash/b,1),'with ATM 8.9', round((cash+8.9)/b,1))
# cash-adjusted loss, same method every period (NI + D&A + ROU amort + SBC + impairment)
adj={'FY2023':(-257.831,65.528+15.065+7.127+27.363),'FY2024':(-97.941,5.521+5.107+4.254+12.382),
     'H1 2024':(-85.217,5.521+2.648+2.451+5.784),'H1 2025':(-50.583,2.013+1.808+4.822)}
for k,(ni,a) in adj.items(): print(k,'NI',ni,'noncash',round(a,1),'share',round(a/-ni*100,0),'% cash loss',round(ni+a,1))
print('Q2 rev 18.306 of which Lilly upfront 18.0; H1 rev ex Lilly&Pfizer', 24.743-18-5)
# charts
c['d']=pd.to_datetime(c.ddate.astype(str))
r=c[c.ddate>=20220101]
fig,ax=plt.subplots(figsize=(7,4))
ax.plot(r.d,r.total_assets/1e6,'o-',label='Total assets')
ax.plot(r.d,r.total_liabilities/1e6,'s-',label='Total liabilities')
ax.plot(r.d,r.net_income/1e6,'^--',label='Net income (annualized; 10-Q x4 or x2)')
ax.axhline(0,color='k',lw=0.8)
ax.set_xlabel('Period end'); ax.set_ylabel('$ million'); ax.legend(); ax.set_title('Sangamo: assets fell 83% since Dec-2022; annual loss ~ total assets')
fig.tight_layout(); fig.savefig('charts/1_assets_vs_loss.png',dpi=120)
# cash chart from filings
q=pd.DataFrame({'q':['Q4-23','Q1-24','Q2-24','Q3-24','Q4-24','Q1-25','Q2-25'],
 'ocf':[None,None,None,None,None,-26.1,-18.2]})
fig,ax=plt.subplots(figsize=(7,4))
labels=['Cash 30 Jun 25','+ ATM July','Q1-25 burn','Q2-25 burn\n(incl. $18M Lilly)']
vals=[38.3,8.9,26.1,18.2]
ax.bar(labels,vals,color=['tab:blue','tab:cyan','tab:red','tab:orange'])
for i,v in enumerate(vals): ax.text(i,v+0.5,f'${v}M',ha='center')
ax.set_ylabel('$ million'); ax.set_title('Cash + July ATM ($47.2M) vs quarterly operating cash burn')
fig.tight_layout(); fig.savefig('charts/2_cash_vs_burn.png',dpi=120)
# peer chart
p = df[(df.sic//100==28)&(df.cik!=1001233)&(df.ddate.between(20250331,20250630))].sort_values('ddate').groupby('cik').tail(1)
x=(p.net_income/p.total_assets).replace([np.inf,-np.inf],np.nan).dropna().clip(-3,1)
fig,ax=plt.subplots(figsize=(7,4))
ax.hist(x,bins=60,color='grey'); me=cur.net_income/cur.total_assets
ax.axvline(me,color='red',label=f'Sangamo {me:.2f}'); ax.axvline(x.median(),color='k',ls='--',label=f'Peer median {x.median():.2f}')
ax.set_xlabel('Annualized net income / total assets (clipped at -3 and 1)'); ax.set_ylabel('SIC 28 peers'); ax.legend()
ax.set_title(f'Loss/assets worse than {(1-(x<me).mean())*100:.0f}% of {len(x)} peers')
fig.tight_layout(); fig.savefig('charts/3_peer_ni_ta.png',dpi=120)
