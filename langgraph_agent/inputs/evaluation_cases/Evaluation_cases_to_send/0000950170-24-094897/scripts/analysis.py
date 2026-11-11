import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
D='final_cases-1/0000950170-24-094897'
df = pd.read_csv('shared/financials.csv'); df = df[df.filed <= 20240809]
cols = ['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
co = df[df.cik==1813914].sort_values('ddate')
me = co[co.adsh=='0000950170-24-094897'].iloc[0]; prev = co[co.adsh=='0000950170-23-040743'].iloc[0]
peers = df[(df.sic.fillna(0).astype(int).astype(str).str[:2]=='80') & (df.cik!=1813914)]
peers = peers[(peers.ddate>=20240101)&(peers.ddate<=20240930)].sort_values('filed').groupby('cik').tail(1)
print('peer n', len(peers))
print('\n8 numbers ($M): this, year before, peer median, share of peers below CMAX')
for c in cols:
    s = peers[c].dropna()
    print(f"{c:22s} {me[c]/1e6:9.1f} {prev[c]/1e6:9.1f} {s.median()/1e6:9.1f}  rank {(s<me[c]).mean()*100:5.1f}% (n={len(s)})")
# ratios
def r(x):
    x = x[cols].astype(float).replace(0, np.nan)
    return dict(TL_TA=x.total_liabilities/x.total_assets, CR=x.current_assets/x.current_liabilities,
                      NI_TA=x.net_income/x.total_assets, NI_Rev=x.net_income/x.revenue, OCF_TA=x.operating_cash_flow/x.total_assets)
pr = pd.DataFrame([r(x) for _,x in peers.iterrows()])
for k,v in r(me).items(): print(f"{k:7s} CMAX {v:7.3f} prev {r(prev)[k]:7.3f} peer median {pr[k].median():7.3f} rank {(pr[k]<v).mean()*100:5.1f}%")
# from filings ($K)
cash = 16430; ocf_h1 = -48114; ocf_q1 = -23802; ocf_q2 = ocf_h1-ocf_q1
print('equity', (me.total_assets-me.total_liabilities)/1e6)
print('Q2 OCF', ocf_q2, 'monthly burn H1', -ocf_h1/6, 'Q2', -ocf_q2/3)
print('months of cash: H1 rate', cash/(-ocf_h1/6), 'Q2 rate', cash/(-ocf_q2/3))
print('cash over minimum liquidity 10M at Q2 rate (months)', (cash-10000)/(-ocf_q2/3))
print('cash / current debt', cash/403321)
# non-cash adjustment, same items every period, from cash flow statements ($K)
adj = {
 'FY2022': dict(ni=-37796, items=[21719,2382,10271,-19542,-4401,-76295,6172,5277,0,1243,70000,0,853], ocf=-68216),
 'FY2023': dict(ni=-683348, items=[27787,8314,10599,-863,-3952,-19916,0,12064,419,-1588,547200,11527,1488], ocf=-46913),
 'H1 2023': dict(ni=-114458, items=[13404,4086,0,4762,355,-1540,-19916,5500,0,57,98000,5842,1213], ocf=-43263),
 'H1 2024': dict(ni=-213966, items=[13218,1821,132990,4761,354,26,0,21955,293,-307,0,5325,33], ocf=-48114),
}
rows=[]
for k,v in adj.items():
    cl = v['ni']+sum(v['items']); rows.append((k, v['ni']/1e3, cl/1e3, v['ocf']/1e3)); print(k, 'NI', v['ni'], 'loss before non-cash', cl, 'OCF', v['ocf'])
# impairments share of H1 2024 loss
print('impairment share H1 2024', 132990/213966, 'Q2', 132990/170558)
# Chart 1: reported loss vs cash loss vs OCF
t = pd.DataFrame(rows, columns=['period','Net loss','Loss after adding back non-cash items','Operating cash flow']).set_index('period')
ax = t.plot.bar(figsize=(8,4.5), color=['#c0392b','#e67e22','#2c3e50']); ax.axhline(0,color='k',lw=.8)
ax.set_ylabel('$ millions (not annualized)'); ax.set_title('Most of the reported loss is non-cash write-downs,\nbut the business still burns cash every period')
plt.xticks(rotation=0); plt.tight_layout(); plt.savefig(f'{D}/charts/1_loss_vs_cash.png', dpi=120); plt.close()
# Chart 2: cash vs current debt
pts = pd.DataFrame({'date':['Dec 2022','Jun 2023','Dec 2023','Mar 2024','Jun 2024'], 'cash':[41.626,54.605,65.528,41.479,16.430]})
fig,ax = plt.subplots(figsize=(8,4.5)); ax.bar(pts.date, pts.cash, color='#2c3e50', label='Cash and equivalents')
ax.axhline(10,color='#e67e22',ls='--',label='Waiver minimum liquidity ($10M)')
for i,v in enumerate(pts.cash): ax.text(i, v+1, f'${v:.1f}M', ha='center')
ax.set_ylabel('$ millions'); ax.set_ylim(0,75)
ax.set_title('Cash fell 75% in six months; $403.3M of debt sits in current liabilities (Jun 2024)')
ax.legend(); plt.tight_layout(); plt.savefig(f'{D}/charts/2_cash.png', dpi=120); plt.close()
# Chart 3: peer position
fig,ax = plt.subplots(figsize=(8,4.5))
p = peers.copy(); p['lev']=p.total_liabilities/p.total_assets; p['ni']=p.net_income/p.total_assets
p = p[np.isfinite(p.lev)&np.isfinite(p.ni)]
ax.scatter(p.lev.clip(0,3), p.ni.clip(-2,0.5), s=15, alpha=.5, color='grey', label=f'SIC 80 peers, 2024 reports (n={len(p)}), clipped to axes')
ax.scatter([me.total_liabilities/me.total_assets],[me.net_income/me.total_assets], s=90, color='#c0392b', label='CareMax Q2 2024')
ax.axvline(1,color='k',lw=.6,ls=':'); ax.axhline(0,color='k',lw=.6,ls=':')
ax.set_xlabel('Total liabilities / total assets'); ax.set_ylabel('Net income (annualized) / total assets')
ax.set_title('CareMax: liabilities exceed assets and losses are deep vs health-services peers'); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig(f'{D}/charts/3_peers.png', dpi=120); plt.close()
# Chart 4: waiver lengths
w = [('Mar 15','2024-03-15','2024-05-15'),('May 14','2024-05-14','2024-06-17'),('Jun 17','2024-06-17','2024-06-24'),
     ('Jun 21','2024-06-21','2024-06-28'),('Jun 28','2024-06-28','2024-07-08'),('Jul 8','2024-07-08','2024-07-10'),('Jul 10','2024-07-10','2024-08-15')]
days = [(pd.Timestamp(b)-pd.Timestamp(a)).days for _,a,b in w]; print('waiver days', days)
fig,ax = plt.subplots(figsize=(8,4.5)); ax.bar([x[0] for x in w], days, color='#7f8c8d')
for i,d in enumerate(days): ax.text(i, d+1, f'{d}d', ha='center')
ax.set_ylabel('Days of covenant waiver granted'); ax.set_xlabel('Date waiver signed (2024)')
ax.set_title('Lenders kept CareMax alive on short waivers, some lasting 2-10 days')
plt.tight_layout(); plt.savefig(f'{D}/charts/4_waivers.png', dpi=120); plt.close()
