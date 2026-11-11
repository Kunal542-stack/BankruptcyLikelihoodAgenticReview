"""Charts. Usage: python -I charts.py <repo_root> <case_dir>"""
import sys, pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
root, case = sys.argv[1], sys.argv[2]
out = f'{case}/charts'

# 1. cash runway: cash at each balance-sheet date (10-Q filed 2023-08-21 and 2023-05-23)
dates = ['Jan 1\n2022', 'Jun 30\n2022', 'Dec 31\n2022', 'Mar 31\n2023', 'Jun 30\n2023']
cash = [10020459, 3472010, 1278026, 235741, 35359]
fig, ax = plt.subplots(figsize=(7, 4))
b = ax.bar(dates, [c/1e6 for c in cash], color=['grey']*4 + ['firebrick'])
for r, c in zip(b, cash):
    ax.text(r.get_x()+r.get_width()/2, c/1e6+0.15, f'${c/1e6:.2f}M' if c > 1e5 else f'${c:,.0f}', ha='center')
ax.axhline(1.37, ls='--', color='black', lw=1)
ax.text(4.45, 2.0, 'dashed line: one month of Q2 2023\noperating cash burn ($1.37M)', ha='right', fontsize=8)
ax.set_ylabel('Cash, $ millions'); ax.set_ylim(0, 11)
ax.set_title('Cash fell to $35k, about one day of Q2 burn')
plt.tight_layout(); plt.savefig(f'{out}/1_cash.png', dpi=130); plt.close()

# 2. what is due vs cash at Jun 30 2023 (10-Q balance sheet and Notes 1 and 8)
items = ['Cash', 'Debt already\npast due', 'Accounts payable\n(incl. related)', 'Total current\nliabilities']
vals = [35359, 1480000 + 692185, 6320552 + 312424, 11532773]
fig, ax = plt.subplots(figsize=(7, 4))
b = ax.bar(items, [v/1e6 for v in vals], color=['firebrick', 'darkorange', 'grey', 'black'])
for r, v in zip(b, vals):
    ax.text(r.get_x()+r.get_width()/2, v/1e6+0.2, f'${v/1e6:.2f}M' if v > 1e5 else f'${v:,.0f}', ha='center')
ax.set_ylabel('$ millions (linear scale)'); ax.set_ylim(0, 13)
ax.set_title('June 30, 2023: past-due debt alone is 61x cash')
plt.tight_layout(); plt.savefig(f'{out}/2_due_vs_cash.png', dpi=130); plt.close()

# 3. net income / assets vs SIC-37 peers (all and small)
d = pd.read_csv(f'{root}/shared/financials.csv'); d = d[d.filed <= 20230821]
p = d[((d.sic // 100) == 37) & (d.cik != 1855631) & d.ddate.between(20230331, 20230630)]
p = p.sort_values('ddate').groupby('cik').tail(1)
r = (p.net_income / p.total_assets).dropna()
rs = (p[p.total_assets < 50e6].net_income / p[p.total_assets < 50e6].total_assets).dropna()
me = -38445730 / 6633480
fig, ax = plt.subplots(figsize=(7, 4))
bins = np.linspace(-8, 1, 37)
ax.hist(r.clip(-8, 1), bins=bins, color='lightgrey', label=f'other SIC 37 peers (n={len(r)}, incl. small)')
ax.hist(rs.clip(-8, 1), bins=bins, color='steelblue', label=f'peers with assets < $50M (n={len(rs)})')
ax.axvline(me, color='firebrick', lw=2, label=f'AERWINS {me:.1f}')
ax.set_xlabel('Annualised net income / total assets (values below -8 shown at -8)')
ax.set_ylabel('companies'); ax.legend(fontsize=8)
ax.set_title('Loss vs assets: extreme for the sector, less so among tiny peers')
plt.tight_layout(); plt.savefig(f'{out}/3_peers.png', dpi=130); plt.close()
print('done', (r < me).sum(), (rs < me).sum())
