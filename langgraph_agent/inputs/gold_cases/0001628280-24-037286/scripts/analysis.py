import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
df=pd.read_csv('../../shared/financials.csv'); df=df[df.filed<=20240814]
assert df.filed.max()<=20240814
c=df[df.cik==1750153].set_index('adsh')
cur=c.loc['0001628280-24-037286']; prev=c.loc['0001628280-23-029426']
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
p=df[(df.sic//100==37)&(df.cik!=1750153)&(df.filed>=20240401)].sort_values('filed').groupby('cik').tail(1)
print('n peers',len(p))
print('\n8 numbers ($M) cur | year before | change | peer median | Canoo pct rank (share below)')
for k in cols:
    v=p[k].dropna()
    print(f"{k:20s} {cur[k]/1e6:8.1f} {prev[k]/1e6:8.1f} {(cur[k]-prev[k])/1e6:8.1f} {v.median()/1e6:8.1f} {(v<cur[k]).mean()*100:5.0f}% n={len(v)}")
# ratios
for lab,d in [('cur',cur),('prev',prev)]:
    print(lab,'liab/assets %.2f'%(d.total_liabilities/d.total_assets),'curr ratio %.2f'%(d.current_assets/d.current_liabilities),
          'NI/assets %.2f'%(d.net_income/d.total_assets),'OCF/assets %.2f'%(d.operating_cash_flow/d.total_assets),'WC $M %.1f'%((d.current_assets-d.current_liabilities)/1e6))
pr=pd.DataFrame({'cr':p.current_assets/p.current_liabilities,'ni':p.net_income/p.total_assets,'lev':p.total_liabilities/p.total_assets}).replace([np.inf,-np.inf],np.nan)
print('peer pct below Canoo: cr %.0f ni/a %.0f lev %.0f'%(((pr.cr<cur.current_assets/cur.current_liabilities).mean()*100),((pr.ni<cur.net_income/cur.total_assets).mean()*100),((pr.lev<cur.total_liabilities/cur.total_assets).mean()*100)))
# equity
print('equity incl pref $M', (543322-347025)/1e3)
# cash & burn ($k from filings)
cash=4513; restr=3983+10600
q1_ocf=-47519; h1_ocf=-83419; q2_ocf=h1_ocf-q1_ocf
capex_h1=-6923
print('Q2 OCF',q2_ocf,'H1 OCF',h1_ocf,'FY23 OCF',-251134)
print('months cash (unrestricted) at Q2 burn: %.2f ; at H1 avg burn: %.2f'%(cash/(-q2_ocf/3),cash/(-h1_ocf/6)))
pf=cash+14100
print('pro forma cash incl July PPA net 14.1M: %.1fM -> months at Q2 burn %.2f'%(pf/1e3,pf/(-q2_ocf/3)))
print('Q2 burn incl capex? capex Q1 unknown; H1 OCF+capex',h1_ocf+capex_h1,'per month %.1f'%((h1_ocf+capex_h1)/6/1e3))
print('Yorkville principal outstanding 6/30: 31.0+15.0 = 46.0M; plus July 15.0 -> 61.0M; vs cash 4.5M')
# adjusted loss: net loss + non-cash items (= OCF before working-capital changes), same method each period
per={'FY2022':(-487694,-400475,[-2954,5672,879,3114]),'FY2023':(-302021,-251134,[-5381,-6750,-2691,-17693]),
     'H1 2023':(-161602,-129544,[-2358,-2060,-2614,5619]),'H1 2024':(-115647,-83419,[-3149,543,764,1494]),
     'Q1 2024':(-110687,-47519,[-652,-1847,-58,770])}
adj={}
for k,(nl,ocf,wc) in per.items():
    a=ocf-sum(wc); adj[k]=a; print(f"{k}: net loss {nl/1e3:.1f}M, non-cash items {(a-nl)/1e3:+.1f}M, cash-adjusted loss {a/1e3:.1f}M")
q2=(-4960, q2_ocf, None); print('Q2 2024 net loss -5.0M; cash-adjusted loss %.1fM'%((adj['H1 2024']-adj['Q1 2024'])/1e3))
# CHARTS
# 1 quarterly burn vs cash
q=['Q4 22','Q1 23','Q2 23','Q3 23','Q4 23','Q1 24','Q2 24']
ocfq=[None,-67216,-129544+67216,-191435+129544,-251134+191435,-47519,q2_ocf]
cashq=[36589,None,4993,8260,6394,3656,4513]
fig,ax=plt.subplots(figsize=(8,4.5))
x=np.arange(len(q))
ax.bar(x,[-(v or 0)/1e3 for v in ocfq],color='indianred',label='Cash used in operations in the quarter ($M)')
ax.plot(range(len(cashq)),[v/1e3 if v else np.nan for v in cashq],'o-',color='navy',label='Unrestricted cash at quarter end ($M)')
for i,v in enumerate(cashq):
    if v: ax.annotate(f'{v/1e3:.1f}',(i,v/1e3),textcoords='offset points',xytext=(0,6),ha='center',color='navy')
ax.set_xticks(x); ax.set_xticklabels(q); ax.set_ylabel('$ millions'); ax.set_ylim(0,80)
ax.set_title('Canoo burns 36-67 \\$M a quarter but ends each quarter with under 10 \\$M cash\n(Q1 2023 cash not in the filings used; Q4 22 burn not shown)',fontsize=10)
ax.legend(fontsize=8,loc='upper right'); plt.tight_layout(); plt.savefig('charts/burn_vs_cash.png',dpi=130); plt.close()
# 2 reported vs cash-adjusted loss
ks=['FY2022','FY2023','H1 2023','H1 2024']; nl=[per[k][0]/1e3 for k in ks]; ad=[adj[k]/1e3 for k in ks]
fig,ax=plt.subplots(figsize=(7,4)); w=0.38; x=np.arange(len(ks))
ax.bar(x-w/2,nl,w,label='Reported net loss',color='grey'); ax.bar(x+w/2,ad,w,label='Loss after removing non-cash items',color='indianred')
for i in range(len(ks)): ax.text(x[i]-w/2,nl[i]-15,f'{nl[i]:.0f}',ha='center',fontsize=8); ax.text(x[i]+w/2,ad[i]-15,f'{ad[i]:.0f}',ha='center',fontsize=8)
ax.axhline(0,color='k',lw=.8); ax.set_xticks(x); ax.set_xticklabels(ks); ax.set_ylabel('$ millions'); ax.set_ylim(-540,20)
ax.set_title('Most of the loss is real cash, not accounting charges\n(same cash-flow-statement adjustment applied to each period)',fontsize=10)
ax.legend(fontsize=8,loc='lower right'); plt.tight_layout(); plt.savefig('charts/loss_cash_vs_reported.png',dpi=130); plt.close()
# 3 peers
fig,ax=plt.subplots(figsize=(7,4.5))
m=pr.dropna(subset=['cr','ni'])
ax.scatter(m.cr.clip(0,6),m.ni.clip(-1.5,0.5),s=12,color='grey',alpha=.6,label=f'SIC 37 peers, latest report Apr-Aug 2024 (n={len(m)})')
ax.scatter(cur.current_assets/cur.current_liabilities,cur.net_income/cur.total_assets,s=80,color='red',label='Canoo 10-Q Jun 2024')
ax.axvline(1,ls='--',color='k',lw=.7); ax.axhline(0,ls='--',color='k',lw=.7)
ax.set_xlabel('Current ratio (clipped at 6)'); ax.set_ylabel('Annualized net income / total assets (clipped)')
ax.set_title('Canoo sits in the low-liquidity, loss-making corner of its peer group',fontsize=10); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig('charts/peers.png',dpi=130); plt.close()
# 4 funding sources H1 2024
lab=['Yorkville advances\n(net of repayments)','Series C preferred\n(CEO-affiliated)','Employee retention\ncredit sale','Cash used in\noperations','Capex']
val=[97347-33007,16500,9013,-83419,-6923]
fig,ax=plt.subplots(figsize=(7.5,4))
ax.bar(lab,[v/1e3 for v in val],color=['seagreen','seagreen','seagreen','indianred','indianred'])
for i,v in enumerate(val): ax.text(i,v/1e3+(2 if v>0 else -7),f'{v/1e3:.1f}',ha='center',fontsize=9)
ax.axhline(0,color='k',lw=.8); ax.set_ylabel('$ millions, H1 2024'); ax.set_ylim(-100,80)
ax.set_title('H1 2024: survival funded mainly by one lender (Yorkville) and the CEO',fontsize=10)
plt.xticks(fontsize=8); plt.tight_layout(); plt.savefig('charts/funding_h1_2024.png',dpi=130); plt.close()
