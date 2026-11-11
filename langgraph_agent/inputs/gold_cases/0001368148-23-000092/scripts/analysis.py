import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
df=pd.read_csv('../../shared/financials.csv'); df=df[df.filed<=20230816]
me=df[df.adsh=='0001368148-23-000092'].iloc[0]
peers=pd.read_csv('scripts/peers_q2_2023.csv')
# year-ago (10-Q filed 2022-08-12, $k; flows = H1 x2)
ya=dict(total_assets=35204,current_assets=21376,current_liabilities=33221,total_liabilities=33221+8284+5199+238,
        revenue=5228*2,net_income=-45864*2,operating_income=-46636*2,operating_cash_flow=-36606*2)
v=list(ya)
print('var | now $m | year-ago $m | peer median $m | ATHX pctile (share of peers below)')
for k in v:
    s=peers[k].dropna()
    print(k, round(me[k]/1e6,2), round(ya[k]/1e3,2), round(s.median()/1e6,1), round(100*(s<me[k]).mean()), len(s))
# ratios
print('TL/TA',round(me.total_liabilities/me.total_assets,2),'yr ago',round(ya['total_liabilities']/ya['total_assets'],2))
print('CR',round(me.current_assets/me.current_liabilities,3),'yr ago',round(ya['current_assets']/ya['current_liabilities'],3))
print('equity $k', -37419, 'NI/TA', round(me.net_income/me.total_assets,2))
# burn & runway ($k)
q1_ocf=-5966; h1_ocf=-10551; q2_ocf=h1_ocf-q1_ocf
cash_q2=1803; cash_aug9=800
print('Q2 OCF',q2_ocf,'monthly',round(q2_ocf/3),'H1 monthly',round(h1_ocf/6))
print('months cash Jun30 @Q2 burn',round(cash_q2/(-q2_ocf/3),2),'@H1 burn',round(cash_q2/(-h1_ocf/6),2))
print('months cash Aug9 @Q2 burn',round(cash_aug9/(-q2_ocf/3),2))
print('FY22 monthly burn',round(-58950/12),'FY21',round(-76185/12))
print('cash vs current liabs', round(cash_q2/42697,3))
# adjusted loss: add back non-cash items from cash flow statement, same each period
adj={'FY2020':(-78765,{'dep':890,'sbc':7379}),
     'FY2021':(-86955,{'dep':1427,'sbc':8556,'rou':235}),
     'FY2022':(-72534,{'dep':1420,'impair':7240,'sbc':6203,'gain_sale':-32,'warrant_fv':-4197}),
     'H1 2022':(-45864,{'dep':865,'impair':4931,'sbc':3355}),
     'H1 2023':(-20735,{'dep':95,'extinguish_gain':-2612,'impair':7545,'sbc':1275,'pik':185,'note_fv':640,'warrant_fv':2151})}
ocf={'FY2020':-61810,'FY2021':-76185,'FY2022':-58950,'H1 2022':-36606,'H1 2023':-10551}
rows=[]
for p,(ni,a) in adj.items():
    rows.append((p,ni,sum(a.values()),ni+sum(a.values()),ocf[p]))
A=pd.DataFrame(rows,columns=['period','net_loss','noncash','adj_loss','ocf']); print(A)
# peer share with CA/CL<0.1 and TL/TA>4
cr=peers.current_assets/peers.current_liabilities; lev=peers.total_liabilities/peers.total_assets
print('peers CR<0.1',round(100*(cr<0.1).mean(),1),'peers TL/TA>4',round(100*(lev>4).mean(),1), 'peers TA<10.5m', round(100*(peers.total_assets<me.total_assets).mean(),1))
# Chart 1: cash vs current liabilities over time
d=['Dec-21','Jun-22','Dec-22','Mar-23','Jun-23','Aug 9-23']
cash=[37.4,13.4,9.0,3.1,1.8,0.8]; cl=[29.9,33.2,38.4,39.7,42.7,np.nan]
fig,ax=plt.subplots(figsize=(7,4)); x=np.arange(len(d))
ax.bar(x-0.2,cash,0.4,label='Cash'); ax.bar(x[:-1]+0.2,cl[:-1],0.4,label='Current liabilities',color='tab:red')
ax.set_xticks(x); ax.set_xticklabels(d); ax.set_ylabel('$ million'); ax.set_ylim(0,52); ax.legend(loc='upper center',ncol=2)
ax.set_title('Cash ran down while current liabilities kept rising\n(Aug 9 cash from 10-Q MD&A; no balance sheet that day)')
for i,c in enumerate(cash): ax.text(i-0.2,c+0.5,f'{c}',ha='center',fontsize=8)
plt.tight_layout(); plt.savefig('charts/cash_vs_cl.png',dpi=120); plt.close()
# Chart 2: peer distribution of current ratio (log)
fig,ax=plt.subplots(figsize=(7,4)); s=cr.replace([np.inf,-np.inf],np.nan).dropna(); s=s[s>0]
ax.hist(np.log10(s.clip(0.01,1000)),bins=50,color='grey'); ax.axvline(np.log10(me.current_assets/me.current_liabilities),color='red',lw=2,label=f'Athersys {me.current_assets/me.current_liabilities:.2f}')
ax.axvline(0,color='k',ls='--',lw=1,label='1.0')
ax.set_xlabel('Current ratio (log10 scale)'); ax.set_ylabel('Number of SIC-28 peers'); ax.legend()
ax.set_title(f'Current ratio: Athersys vs {len(s)} SIC-28 peers (Jun-30-2023 10-Qs)\n{100*(s<me.current_assets/me.current_liabilities).mean():.1f}% are lower')
plt.tight_layout(); plt.savefig('charts/peer_current_ratio.png',dpi=120); plt.close()
# Chart 3: net loss vs adjusted loss vs OCF
fig,ax=plt.subplots(figsize=(7,4)); x=np.arange(len(A)); w=0.27
ax.bar(x-w,-A.net_loss/1e3,w,label='Net loss'); ax.bar(x,-A.adj_loss/1e3,w,label='Loss excl. non-cash items'); ax.bar(x+w,-A.ocf/1e3,w,label='Operating cash outflow')
ax.set_xticks(x); ax.set_xticklabels(A.period); ax.set_ylabel('$ million (positive = loss / outflow)'); ax.legend()
ax.set_title('Loss is mostly cash; spending was cut hard after mid-2022\n(H1 = six months, not annualized)')
plt.tight_layout(); plt.savefig('charts/loss_vs_cash.png',dpi=120); plt.close()
