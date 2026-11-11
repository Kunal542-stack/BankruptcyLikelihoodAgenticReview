import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
history = pd.read_csv("data/history.csv")  # the company's reports up to this one: the 8 inputs (per year, 10-Qs annualized)
peers = pd.read_csv("data/peers.csv")      # same-industry peers at about the same date: the same 8 inputs
facts = json.load(open("data/facts.json"))  # case, numbers, cash, assessment (verdict, reasons, timeline)

h = history.sort_values('ddate').iloc[-1]
c_lev = h['total_liabilities'] / h['total_assets']
c_roa = h['net_income'] / h['total_assets']
p = peers.copy()
p = p[~p['name'].astype(str).str.upper().str.contains('CREATD')]
p = p[(p['total_assets'] > 0) & p['total_liabilities'].notna() & p['net_income'].notna()]
p = p[p['total_liabilities'] > 0]
p['lev'] = p['total_liabilities'] / p['total_assets']
p['roa'] = p['net_income'] / p['total_assets']
med_lev = p['lev'].median()
med_roa = p['roa'].median()
n_corner = int(((p['lev'] > 1) & (p['roa'] < -1)).sum())
fig, ax = plt.subplots(figsize=(7.5, 3.8))
ax.scatter(p['lev'], p['roa'] * 100, color='grey', alpha=0.75, s=36, label=f'Peers (n={len(p)})')
ax.scatter([c_lev], [c_roa * 100], color='#d62728', edgecolor='black', s=110, zorder=5, label='Creatd, Sep 2023')
ax.set_xscale('log')
ax.set_yscale('symlog', linthresh=100)
ax.axvline(1, color='black', ls='--', lw=1)
ax.axhline(0, color='black', lw=0.8)
ax.axvline(med_lev, color='grey', ls=':', lw=1)
ax.axhline(med_roa * 100, color='grey', ls=':', lw=1)
ax.text(1.05, 40, 'liabilities = assets', fontsize=8, rotation=90, va='top')
ax.text(med_lev, -300, f'peer median {med_lev:.2f}x', fontsize=7, color='dimgrey', rotation=90, ha='right', va='center')
ax.text(ax.get_xlim()[1] if False else 60, med_roa * 100, f'peer median {med_roa*100:.0f}%', fontsize=7, color='dimgrey', va='bottom', ha='center')
ax.annotate(f'Creatd\nliabilities {c_lev:.1f}x assets\nloss {abs(c_roa)*100:,.0f}% of assets', (c_lev, c_roa * 100), xytext=(-20, 25), textcoords='offset points', ha='right', fontsize=8.5, color='#d62728')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:,.0f}%'))
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:g}x'))
ax.set_xlabel('Total liabilities / total assets (log scale)')
ax.set_ylabel('Net income / total assets\n(annualized, symlog scale)')
ax.set_title(f'Creatd sits in the distressed corner with {n_corner} peers: loss ~{abs(c_roa):.0f}x and debts {c_lev:.1f}x assets', fontsize=9.5)
ax.grid(alpha=0.3)
ax.legend(loc='lower left', fontsize=8)
fig.tight_layout()

plt.savefig('chart_3.png', dpi=110, bbox_inches='tight')
