import pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
C='final_cases-1/0001653247-23-000057/charts/'
# 1 cash vs debt due May 2024 ($m) - from 10-K FY22, 10-Q Q2'22, Q1'23, Q2'23
d=['Dec-21','Jun-22','Dec-22','Mar-23','Jun-23','Jul-23*']; cash=[60.111,28.203,12.066,6.289,5.066,5.187]
fig,ax=plt.subplots(figsize=(7,4)); ax.bar(d,cash,color='tab:blue',label='Cash')
ax.axhline(56.355,color='red',ls='--',label='Luxor debt principal at Jun-23 ($56.4m), due 15 May 2024')
for i,v in enumerate(cash): ax.text(i,v+1,f'{v:.1f}',ha='center')
ax.set_ylabel('$ millions'); ax.set_ylim(0,70); ax.set_title('Cash fell 92% in 18 months; debt due May 2024 is 11x cash')
ax.legend(loc='upper right',fontsize=8); fig.text(0.01,0.01,'*Jul-23 = management estimate in Q2 2023 10-Q MD&A',fontsize=7)
fig.tight_layout(); fig.savefig(C+'cash_vs_debt.png',dpi=120)
# 2 net loss vs loss after non-cash add-backs (cash-flow statement, same items each period)
lab=['FY2021','FY2022','H1 2022','H1 2023']; nl=[-5.229,-206.789,-88.887,-20.420]; adj=[2.167,-22.319,-10.288,-5.038]
import numpy as np; x=np.arange(4)
fig,ax=plt.subplots(figsize=(7,4)); ax.bar(x-0.2,nl,0.4,label='Reported net loss',color='grey'); ax.bar(x+0.2,adj,0.4,label='Net loss + non-cash items (impairments, D&A, SBC, PIK...)',color='tab:orange')
for i in range(4): ax.text(x[i]-0.2,nl[i]-8,f'{nl[i]:.1f}',ha='center',fontsize=8); ax.text(x[i]+0.2,min(adj[i],0)-8,f'{adj[i]:.1f}',ha='center',fontsize=8)
ax.set_xticks(x,lab); ax.set_ylabel('$ millions'); ax.set_ylim(-230,15); ax.axhline(0,color='k',lw=0.5)
ax.set_title('Most of the loss is non-cash write-offs; the cash-basis loss\npersists since 2022 (FY = 12 months, H1 = 6 months)'); ax.legend(fontsize=8,loc='lower right')
fig.tight_layout(); fig.savefig(C+'loss_noncash.png',dpi=120)
# 3 peers leverage
p=pd.read_csv('final_cases-1/0001653247-23-000057/scripts/peers.csv'); lev=(p.total_liabilities/p.total_assets).clip(upper=4)
fig,ax=plt.subplots(figsize=(7,4)); ax.hist(lev.dropna(),bins=40,color='lightgrey',edgecolor='k')
ax.axvline(3.166,color='red',lw=2,label='Waitr 3.17 (liabilities / assets)'); ax.axvline(lev.median(),color='blue',ls='--',label=f'Peer median {lev.median():.2f}')
ax.set_xlabel('Total liabilities / total assets (capped at 4)'); ax.set_ylabel('Number of SIC 73 peers'); ax.set_title(f'Waitr owes 3x its assets: top {100-91.7:.0f}% of {lev.notna().sum()} peers')
ax.legend(); fig.tight_layout(); fig.savefig(C+'peer_leverage.png',dpi=120)
# 4 revenue collapse
q=['Q2-21','Q2-22','Q1-23','Q2-23']; rev=[49.167,31.171,16.704,13.951]
fig,ax=plt.subplots(figsize=(7,4)); ax.bar(q,rev,color='tab:green')
for i,v in enumerate(rev): ax.text(i,v+0.8,f'{v:.1f}',ha='center')
ax.set_ylabel('Quarterly revenue, $ millions'); ax.set_ylim(0,55); ax.set_title('Quarterly revenue down 72% in two years (orders -64% y/y in Q2-23)')
fig.tight_layout(); fig.savefig(C+'revenue.png',dpi=120)
