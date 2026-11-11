import pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
df=pd.read_csv('../../shared/financials.csv'); df=df[df.filed<=20230814]
c=df[df.cik==1841800].set_index('adsh'); me=c.loc['0000950170-23-042370']; fy=c.loc['0000950170-23-009502']; q1=c.loc['0000950170-23-021940']
print('max filed used',df.filed.max())
# filing figures ($k)
cash={'2022-12-31':15385,'2023-03-31':617,'2023-06-30':3143}
ocf_h1_23=-30215; ocf_q1_23=-22246; ocf_q2_23=ocf_h1_23-ocf_q1_23
print('Q2 OCF',ocf_q2_23,'annualized check',q1.operating_cash_flow/4/1e3, me.operating_cash_flow/2/1e3)
print('months cash, Q2 burn', 3143/(-ocf_q2_23/3), ' H1 burn', 3143/(-ocf_h1_23/6))
print('leverage TL/TA',me.total_liabilities/me.total_assets,'FY22',fy.total_liabilities/fy.total_assets)
print('equity',(me.total_assets-me.total_liabilities)/1e6,'current ratio',me.current_assets/me.current_liabilities,'FY22',fy.current_assets/fy.current_liabilities)
print('WC',(me.current_assets-me.current_liabilities)/1e6)
# non-cash adjustments, same rule each period: all non-working-capital reconciling items in the CF statement
adj={'FY2022':[808,2617,2034,130,-780,4245,717,4561,-4271,-1117,1885,-1611,641],
     'H1 2022':[420,802,0,83,65,1982,509,2566,0,0,0,-1611,82],
     'H1 2023':[437,722,554,370,13,938,-3739,878,-3295,-847,-63,-1]}
nl={'FY2022':-52726,'H1 2022':-20915,'H1 2023':-21732}
for k in adj: print(k,'net loss',nl[k],'noncash',sum(adj[k]),'cash-basis loss',nl[k]+sum(adj[k]))
rev={'Q2 2022':20350,'Q1 2023':16675,'Q2 2023':12742}
print('rev yoy Q2',12742/20350-1,'H1',29419/45548-1)
print('G&A share of rev H1 2023',33139/29419)
# charts
fig,ax=plt.subplots(figsize=(6,4))
ax.bar(list(cash),[v/1e3 for v in cash.values()],color=['#888','#c33','#c33'])
for i,v in enumerate(cash.values()): ax.text(i,v/1e3+0.3,f'${v/1e3:.1f}M',ha='center')
ax.set_ylabel('Cash, $M'); ax.set_title('Cash fell to $0.6M in March; $22M April raise left only $3.1M by June')
ax.annotate('$22M gross equity raise\n(Apr 6) between these dates',xy=(1.5,3.6),xytext=(1.5,8),ha='center',fontsize=8,arrowprops=dict(arrowstyle='->'))
ax.title.set_fontsize(9); plt.tight_layout(); plt.savefig('charts/cash.png',dpi=120); plt.close()
fig,ax=plt.subplots(figsize=(6,4))
q=['Q1 2023','Q2 2023']; ax.bar(q,[-ocf_q1_23/1e3,-ocf_q2_23/1e3],color='#c33',label='Cash used in operations')
ax.axhline(3.143,color='k',ls='--',label='Cash on hand 30 Jun 2023 ($3.1M)')
ax.set_ylabel('$M'); ax.set_title('One quarter of operating cash burn exceeds cash on hand',fontsize=9); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig('charts/burn_vs_cash.png',dpi=120); plt.close()
# peers
p=df[(df.sic//100==73)&(df.cik!=1841800)&(df.ddate>=20230331)&(df.ddate<=20230930)].sort_values('filed').groupby('cik').tail(1)
r={'Net income / assets':(p.net_income/p.total_assets, me.net_income/me.total_assets),
   'Op. cash flow / assets':(p.operating_cash_flow/p.total_assets, me.operating_cash_flow/me.total_assets),
   'Liabilities / assets':(p.total_liabilities/p.total_assets, me.total_liabilities/me.total_assets),
   'Current ratio':(p.current_assets/p.current_liabilities, me.current_assets/me.current_liabilities)}
fig,ax=plt.subplots(figsize=(7,4)); names=list(r); x=range(len(names))
ax.bar([i-0.2 for i in x],[r[n][0].median() for n in names],0.4,label=f'SIC 73 peer median (latest report Mar-Sep 2023, {len(p)} firms)',color='#888')
ax.bar([i+0.2 for i in x],[r[n][1] for n in names],0.4,label='Nogin, Jun 2023',color='#c33')
for n in names: print(n,'me',round(r[n][1],2),'med',round(r[n][0].median(),2),'pct',round((r[n][0]<r[n][1]).mean()*100))
ax.set_xticks(list(x)); ax.set_xticklabels(names,fontsize=8); ax.axhline(0,color='k',lw=0.5); ax.legend(fontsize=8)
ax.set_title('Ratios (size-neutral) are far worse than peers, not just small dollars',fontsize=9)
plt.tight_layout(); plt.savefig('charts/peers.png',dpi=120); plt.close()
fig,ax=plt.subplots(figsize=(6,4)); ax.bar(list(rev),[v/1e3 for v in rev.values()],color='#36c')
for i,v in enumerate(rev.values()): ax.text(i,v/1e3+0.3,f'${v/1e3:.1f}M',ha='center')
ax.set_ylabel('Quarterly revenue, $M'); ax.set_title('Revenue down 37% year on year in Q2 2023',fontsize=9)
plt.tight_layout(); plt.savefig('charts/revenue.png',dpi=120); plt.close()
