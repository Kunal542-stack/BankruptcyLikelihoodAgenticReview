import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D='final_cases/0001078207-23-000108'
df = pd.read_csv('shared/financials.csv'); df = df[df.filed <= 20230809]
me = df[df.adsh=='0001078207-23-000108'].iloc[0]
# ---- year-before values (10-Q filed 2022-08-09, $k) and this report ($k), quarter figures x4 = annualized
prev = dict(total_assets=229138, current_assets=157619, current_liabilities=62538, total_liabilities=124291,
            revenue=54817*4, net_income=-60177*4, operating_income=-51185*4, operating_cash_flow=-5980*4)
cur  = dict(total_assets=140181, current_assets=86445, current_liabilities=43333, total_liabilities=81110,
            revenue=41750*4, net_income=-4924*4, operating_income=-10533*4, operating_cash_flow=-2365*4)
for k in cur:
    assert abs(cur[k]*1000 - me[k]) < 2000, (k, cur[k], me[k])
    print(f"{k:22s} now {cur[k]/1e3:8.1f}M  yr-before {prev[k]/1e3:8.1f}M  change {100*(cur[k]-prev[k])/abs(prev[k]):6.1f}%  share_of_TA {cur[k]/cur['total_assets']:.3f}")
# ---- ratios
cash=18280; debt_principal=17300; equity=59071
print('TL/TA', round(81110/140181,3), 'debt principal/equity', round(debt_principal/equity,3), 'current ratio', round(86445/43333,2))
q_ocf=-2365; q_capex=-1178; fcf=q_ocf+q_capex
print('Q1 FCF', fcf, 'months of cash at Q1 FCF burn', round(cash/(-fcf/3),1), 'at Q1 OCF burn', round(cash/(-q_ocf/3),1))
# ---- loss adjusted for non-cash items, same items every period (cash-flow statement lines before working capital)
adj = {
 'FY2022 (10-K)': [-22431, 8615, 414, 0, 6262, 0, 0, 0, -7827, 586],
 'FY2023 (10-K)': [-105399, 11103, 761, 821, 3885, -2, 228, 26965, 8958, 691],
 'Q1 FY23 (10-Q)': [-60177, 2306, 430, 644, 1979, 0, 0, 26965, 8354, -666],
 'Q1 FY24 (10-Q)': [-4924, 3150, 60, 0, 1015, -9021, 352, 0, -182, 832],
}
ocf = {'FY2022 (10-K)':-66566,'FY2023 (10-K)':18846,'Q1 FY23 (10-Q)':-5980,'Q1 FY24 (10-Q)':-2365}
cash_loss={}
for k,v in adj.items():
    cash_loss[k]=sum(v); print(f"{k}: net loss {v[0]/1e3:.1f}M, loss after non-cash items {sum(v)/1e3:.1f}M, working capital {(ocf[k]-sum(v))/1e3:.1f}M, OCF {ocf[k]/1e3:.1f}M")
print('Q1 FY24 pre-tax loss excl. $9.0M asset-sale gain', (-4419-9021)/1e3)
print('Q1 share of FY23 sales', round(54817/286773,3), 'seasonal FY24 run-rate', round(41750/(54817/286773)/1e3,1))
print('sales change Q1 y/y', round(100*(41750/54817-1),1), 'gross margin', round(8649/41750*100,1), 'vs', round(6957/54817*100,1))
print('opex ex impairment/restructuring', 19182-440, 'vs', 58142-26965, round(100*((19182-440)/(58142-26965)-1),1))
print('covenant headroom approx', 9.5-7.0)
# ---- Chart 1 quarterly sales and net loss
q = ['Q1\nFY22','Q2\nFY22','Q3\nFY22','Q4\nFY22','Q1\nFY23','Q2\nFY23','Q3\nFY23','Q4\nFY23','Q1\nFY24']
sales=[184593-0,137959,147258,589534-469810,54817,65458,98079,286773-218354,41750]
sales[0]=322552-137959
nl=[9282+4602,-4602,-13499,-22431+4217,-60177,-13203,-11082,-105399+84461,-4924]
print('quarterly sales',sales); print('quarterly NL',nl)
fig,ax=plt.subplots(figsize=(9,4.5)); x=np.arange(len(q))
ax.bar(x-0.2,np.array(sales)/1e3,0.4,label='Net sales',color='#4C72B0'); ax.bar(x+0.2,np.array(nl)/1e3,0.4,label='Net income (loss)',color='#C44E52')
ax.axhline(0,color='k',lw=0.8); ax.set_xticks(x); ax.set_xticklabels(q); ax.set_ylabel('$ million (quarter)')
ax.set_title('Quarterly sales fell 77% from Q1 FY22 to Q1 FY24 (fiscal year ends March 31)')
ax.annotate('$27.0M impairment\n+ $8.4M deferred tax', (4.2,-60.2),(5.2,-55),fontsize=8,arrowprops=dict(arrowstyle='->'))
ax.annotate('includes $9.0M gain\non asset sales', (8.2,-4.9),(6.6,-45),fontsize=8,arrowprops=dict(arrowstyle='->'))
ax.legend(); fig.tight_layout(); fig.savefig(f'{D}/charts/1_quarterly_sales_loss.png',dpi=130)
# ---- Chart 2 cash loss vs working capital (annual and Q1 periods, quarters not annualized)
keys=list(adj); fig,ax=plt.subplots(figsize=(9,4.5)); x=np.arange(len(keys))
ax.bar(x-0.27,[adj[k][0]/1e3 for k in keys],0.27,label='Net loss',color='#C44E52')
ax.bar(x,[cash_loss[k]/1e3 for k in keys],0.27,label='Loss after non-cash items',color='#DD8452')
ax.bar(x+0.27,[ocf[k]/1e3 for k in keys],0.27,label='Operating cash flow',color='#55A868')
ax.axhline(0,color='k',lw=0.8); ax.set_xticks(x); ax.set_xticklabels(keys); ax.set_ylabel('$ million')
ax.set_title('Cash loss before working capital persists; FY23 cash flow was positive\nonly because inventory and receivables were run down (+$70.8M)')
ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(f'{D}/charts/2_cash_loss_vs_ocf.png',dpi=130)
# ---- Chart 3 revolver availability vs covenant floor
lbl=['Mar 31, 2022','Mar 31, 2023','Jun 30, 2023']; avail=[65.8,14.9,9.5]; cashv=[14.2,18.3,18.3]
fig,ax=plt.subplots(figsize=(7.5,4.5)); x=np.arange(3)
ax.bar(x-0.2,cashv,0.4,label='Cash incl. restricted (MD&A)',color='#4C72B0'); ax.bar(x+0.2,avail,0.4,label='Revolver availability',color='#8172B3')
ax.hlines(7.0,1.6,2.45,color='r',ls='--',lw=1.2); ax.annotate('covenant floor from Apr 2023:\n$7.0M or 12.5% of line cap',(2.3,7.0),(1.55,32),fontsize=8,color='r',arrowprops=dict(arrowstyle='->',color='r'))
for i,v in enumerate(avail): ax.text(i+0.2,v+0.8,f'{v}',ha='center',fontsize=8)
for i,v in enumerate(cashv): ax.text(i-0.2,v+0.8,f'{v}',ha='center',fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(lbl); ax.set_ylabel('$ million'); ax.set_ylim(0,72)
ax.set_title('Borrowing room shrank to near the covenant floor'); ax.legend(fontsize=8,loc='upper right')
fig.tight_layout(); fig.savefig(f'{D}/charts/3_liquidity_headroom.png',dpi=130)
