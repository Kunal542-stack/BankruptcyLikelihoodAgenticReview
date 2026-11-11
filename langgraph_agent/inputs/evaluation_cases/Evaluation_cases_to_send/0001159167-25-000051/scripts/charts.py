import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
df = pd.read_csv('../../shared/financials.csv'); df = df[df.filed <= 20250506]
co = df[df.cik == 1159167].sort_values('ddate'); peers = pd.read_csv('scripts/peers.csv')
me = co[co.adsh == '0001159167-25-000051'].iloc[0]
# rank table
cols = ['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
for c in cols:
    s = peers[c].dropna(); print(c, 'rank from lowest', int((s < me[c]).sum())+1, 'of', len(s)+1)
# 1 cash vs debt
fig, ax = plt.subplots(figsize=(7,4))
labels = ['Unrestricted\ncash', 'Restricted cash\n(lender-controlled)', 'Term loan\nprincipal', 'Term loan\nfair value', 'Payoff at 1.4x-1.7x\n(my estimate)']
vals = [69.9, 40.0, 184.2, 224.1, 257.9]
b = ax.bar(labels, vals, color=['tab:green','tab:olive','tab:red','tab:red','tab:red'])
ax.bar(labels[4], 313.2-257.9, bottom=257.9, color='tab:red', alpha=0.35)
for i, v in enumerate(vals[:4]): ax.text(i, v+4, f'${v:.1f}M', ha='center')
ax.text(4, 317, '$258-313M', ha='center')
ax.set_ylabel('$ millions, at 29 Mar 2025'); ax.set_ylim(0, 350)
ax.set_title('Debt that could be accelerated after 6 Jun 2025 is 3x unrestricted cash')
plt.xticks(fontsize=8); plt.tight_layout(); plt.savefig('charts/1_cash_vs_debt.png', dpi=130); plt.close()
# 2 history: revenue and net income (FY rows + Q1'25 annualized)
h = co[(co.form == '10-K') | (co.adsh == '0001159167-25-000051')]
lab = [f"FY{str(d)[:4]}" if f == '10-K' else "Q1'25\n(x4)" for d, f in zip(h.ddate, h.form)]
x = np.arange(len(h)); fig, ax = plt.subplots(figsize=(7,4))
ax.bar(x-0.2, h.revenue/1e6, 0.4, label='Revenue'); ax.bar(x+0.2, h.net_income/1e6, 0.4, label='Net income', color='tab:red')
ax.axhline(0, color='k', lw=0.8); ax.set_xticks(x); ax.set_xticklabels(lab); ax.set_ylabel('$ millions per year')
ax.set_title('Revenue fell three years running; losses never stopped'); ax.legend()
plt.tight_layout(); plt.savefig('charts/2_revenue_netincome.png', dpi=130); plt.close()
# 3 adjusted loss
a = pd.read_csv('scripts/adjusted_loss.csv'); a = a[a.period.str.startswith('FY') | (a.period == 'Q1 2025')].copy()
a.loc[a.period == 'Q1 2025', ['net_income', 'adjusted']] *= 4; a.loc[a.period == 'Q1 2025', 'period'] = "Q1'25 (x4)"
fee = [0, 0, 75.2, 0]
x = np.arange(len(a)); fig, ax = plt.subplots(figsize=(7,4))
ax.bar(x-0.2, a.net_income, 0.4, label='Reported net loss', color='tab:red')
ax.bar(x+0.2, a.adjusted - np.array(fee), 0.4, label='Loss after non-cash add-backs,\nexcl. $75.2M Amazon fee (FY24)', color='tab:orange')
ax.axhline(0, color='k', lw=0.8); ax.set_xticks(x); ax.set_xticklabels(a.period); ax.set_ylabel('$ millions per year')
ax.set_title('About half the loss is non-cash, but the cash loss is still large'); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig('charts/3_adjusted_loss.png', dpi=130); plt.close()
# 4 peers current ratio
cr = (peers.current_assets/peers.current_liabilities).replace([np.inf,-np.inf], np.nan).dropna().clip(upper=10)
fig, ax = plt.subplots(figsize=(7,4)); ax.hist(cr, bins=40, color='grey')
ax.axvline(me.current_assets/me.current_liabilities, color='red', lw=2, label=f'iRobot {me.current_assets/me.current_liabilities:.2f}')
ax.axvline(cr.median(), color='k', ls='--', label=f'Peer median {cr.median():.2f}')
ax.set_xlabel('Current ratio (capped at 10)'); ax.set_ylabel('Number of SIC-36 peers'); ax.legend()
ax.set_title(f'Current ratio: bottom {round((cr < me.current_assets/me.current_liabilities).mean()*100)}% of {len(cr)} SIC-36 peers')
plt.tight_layout(); plt.savefig('charts/4_peer_current_ratio.png', dpi=130); plt.close()
print('peer date range', peers.ddate.min(), peers.ddate.max(), 'n', len(peers))
