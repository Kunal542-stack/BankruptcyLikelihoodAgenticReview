import pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, numpy as np
df=pd.read_csv('../../shared/financials.csv'); df=df[df.filed<=20250905]
c=df[df.cik==1749723].sort_values('ddate')
lab=[f"{str(d)[:4]}-{str(d)[4:6]}" for d in c.ddate]
fig,ax=plt.subplots(figsize=(8,4)); x=np.arange(len(c))
ax.bar(x-0.2,c.net_income/1e6,0.4,label='Net income (annualized)'); ax.bar(x+0.2,c.operating_cash_flow/1e6,0.4,label='Operating cash flow (annualized)')
ax.axhline(0,color='k',lw=.8); ax.set_xticks(x); ax.set_xticklabels(lab,rotation=45); ax.set_ylabel('$ millions'); ax.legend(loc='lower left')
ax.set_title('NFE: profits and operating cash flow turned negative in 2025\n(10-Q values annualized year-to-date, as in the model input)')
plt.tight_layout(); plt.savefig('charts/1_income_cashflow.png',dpi=120); plt.close()
# cash vs debt
fig,ax=plt.subplots(figsize=(8,4))
items=[('Unrestricted cash\n6/30/2025',551.1,'tab:green'),('Debt due <1yr\n(balance sheet)',1181.6,'tab:orange'),('2026 Notes\n(due 9/30/2026)',510.9,'tab:red'),('Debt that springs due\nin summer 2026 if 2026\nNotes not refinanced',2730.1+710.4+295.0+1269.3,'tab:red')]
ax.bar([i[0] for i in items],[i[1] for i in items],color=[i[2] for i in items])
for i,(n,v,_) in enumerate(items): ax.text(i,v+60,f"${v:,.0f}m",ha='center')
ax.set_ylabel('$ millions'); ax.set_ylim(0,6000); ax.set_title('Cash covers a small fraction of debt due or springing due by mid-2026\n(Q2 2025 10-Q, Note 2 and balance sheet)')
plt.tight_layout(); plt.savefig('charts/2_cash_vs_debt.png',dpi=120); plt.close()
# peers
p=pd.read_csv('scripts/peer_rows.csv'); r=(p.net_income/p.total_assets).dropna().clip(-0.3,0.15)
me=-1508.4/11957.33
fig,ax=plt.subplots(figsize=(8,4)); ax.hist(r,bins=40,color='grey'); ax.axvline(me,color='red',lw=2,label=f'NFE {me:.1%}')
ax.set_xlabel('Net income / total assets (annualized; clipped at -30% and +15%)'); ax.set_ylabel('number of peer reports')
ax.set_title(f'NFE vs {len(r)} SIC-49 (utilities/energy) peers, periods Apr-Sep 2025'); ax.legend()
plt.tight_layout(); plt.savefig('charts/3_peers_ni_assets.png',dpi=120); plt.close()
# adjusted loss
k=['FY2022','FY2023','FY2024','H1 2025']; ni=[184.8,548.9,-242.4,-754.2]; ce=[459.9,635.4,436.1,-374.0]
fig,ax=plt.subplots(figsize=(8,4)); x=np.arange(4)
ax.bar(x-0.2,ni,0.4,label='Net income'); ax.bar(x+0.2,ce,0.4,label='Net income + all non-cash items\n(cash flow statement, before working capital)')
ax.axhline(0,color='k',lw=.8); ax.set_xticks(x); ax.set_xticklabels(['FY2022','FY2023','FY2024','H1 2025\n(6 months, not annualized)']); ax.set_ylabel('$ millions'); ax.legend(fontsize=8)
ax.set_title('Stripping out impairments and the Jamaica gain, 2025 is still a cash loss')
plt.tight_layout(); plt.savefig('charts/4_cash_earnings.png',dpi=120); plt.close()
