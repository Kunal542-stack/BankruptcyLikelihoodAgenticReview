import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, pandas as pd, numpy as np
C='final_cases/0001008654-23-000079/charts/'
# 1 quarterly revenue (restated 10-K Note 23; 2023 = NT 10-Q preliminary ranges)
q=['Q1 21','Q2 21','Q3 21','Q4 21','Q1 22','Q2 22','Q3 22','Q4 22*','Q1 23','Q2 23']
v=[413.1,417.7,381.0,388.8,347.1,339.7,303.6,313.6,285,265]
fig,ax=plt.subplots(figsize=(8,4))
cols=['tab:blue']*8+['tab:red']*2
ax.bar(q,v,color=cols)
ax.errorbar([8,9],[285,265],yerr=[[5,5],[5,5]],fmt='none',ecolor='k',capsize=4)
ax.set_ylim(0,450); ax.set_ylabel('$ million')
ax.set_title('Quarterly sales down ~18% in 2022 and another ~20% in H1 2023')
ax.text(0.01,0.02,'Red = preliminary ranges from NT 10-Q (midpoint shown). *Q4 22 is 14 weeks.',transform=ax.transAxes,fontsize=8)
plt.tight_layout(); plt.savefig(C+'1_revenue.png',dpi=120); plt.close()
# 2 net income vs adjusted earnings vs OCF
yrs=['2020','2021','2022']
ni=[123.5,15.6,-232.5]; adj=[147.5,193.1,68.0]; ocf=[179.5,108.8,-34.0]
x=np.arange(3); w=0.27
fig,ax=plt.subplots(figsize=(8,4))
ax.bar(x-w,ni,w,label='Net income (model input)')
ax.bar(x,adj,w,label='Cont. ops income before non-cash items')
ax.bar(x+w,ocf,w,label='Operating cash flow (model input)')
ax.axhline(0,color='k',lw=0.8); ax.set_xticks(x); ax.set_xticklabels(yrs); ax.set_ylabel('$ million')
ax.set_title('2022 loss is mostly a tax write-off, but cash earnings still fell ~65%')
ax.legend(fontsize=8); plt.tight_layout(); plt.savefig(C+'2_loss_vs_cash.png',dpi=120); plt.close()
# 3 peers ratios
p=pd.read_csv('final_cases/0001008654-23-000079/scripts/peers_used.csv')
la=p.total_liabilities/p.total_assets; cr=p.current_assets/p.current_liabilities
fig,axs=plt.subplots(1,2,figsize=(9,3.8))
for a,s,t,lab in [(axs[0],la,1.578,'Liabilities / assets'),(axs[1],cr.clip(upper=6),0.431,'Current ratio (capped at 6)')]:
    a.scatter(np.random.RandomState(0).uniform(-.2,.2,len(s)),s,color='grey',label='SIC 30 peers (n=%d)'%len(s))
    a.scatter([0],[t],color='red',s=80,label='Tupperware FY22'); a.axhline(s.median(),ls='--',color='grey',lw=0.8)
    a.set_xticks([]); a.set_title(lab)
axs[0].legend(fontsize=8)
fig.suptitle('Highest leverage and lowest current ratio of 24 peers (dashed = peer median)')
plt.tight_layout(); plt.savefig(C+'3_peers.png',dpi=120); plt.close()
# 4 liquidity squeeze
fig,ax=plt.subplots(figsize=(7,4))
x=np.arange(3); w=0.38
ax.bar(x[:2]-w/2,[267.2,110.1],w,color='tab:blue',label='Cash (balance sheet)')
ax.bar(x+w/2,[156.5,120.1,16.3],w,color='tab:orange',label='Unused credit lines')
ax.text(2-w/2,8,'not\nreported',ha='center',fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(['Dec 2021','Dec 2022','Sep 2023']); ax.set_ylabel('$ million')
ax.set_ylim(0,320); ax.set_title('Liquidity shrank; all ~$713m of debt was current at Dec 2022')
ax.legend(fontsize=8); plt.tight_layout(); plt.savefig(C+'4_liquidity.png',dpi=120); plt.close()
