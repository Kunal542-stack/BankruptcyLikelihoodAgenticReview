import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
history = pd.read_csv("data/history.csv")  # the company's reports up to this one: the 8 inputs (per year, 10-Qs annualized)
peers = pd.read_csv("data/peers.csv")      # same-industry peers at about the same date: the same 8 inputs
facts = json.load(open("data/facts.json"))  # case, numbers, cash, assessment (verdict, reasons, timeline)

h = history.copy()
h['ddate'] = h['ddate'].astype(str)
h['filed'] = h['filed'].astype(str)
h = h.sort_values(['ddate', 'filed']).drop_duplicates('ddate', keep='last')
h = h.dropna(subset=['total_assets', 'total_liabilities'])
h['date'] = pd.to_datetime(h['ddate'], format='%Y%m%d')
h = h.sort_values('date')
ta = h['total_assets'] / 1e6
tl = h['total_liabilities'] / 1e6
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(h['date'], ta, marker='o', color='tab:green', label='Total assets')
ax.plot(h['date'], tl, marker='o', color='tab:red', label='Total liabilities')
ax.fill_between(h['date'], ta, tl, where=(tl > ta), color='tab:red', alpha=0.12, interpolate=True, label='Liabilities above assets')
last_a, last_l = ta.iloc[-1], tl.iloc[-1]
ax.annotate(f'${last_l:.1f}M', (h['date'].iloc[-1], last_l), textcoords='offset points', xytext=(-10, 6), ha='right', fontsize=8, color='tab:red')
ax.annotate(f'${last_a:.1f}M', (h['date'].iloc[-1], last_a), textcoords='offset points', xytext=(-10, 6), ha='right', fontsize=8, color='tab:green')
first_a, first_l = ta.iloc[0], tl.iloc[0]
fy = h['date'].iloc[0].year
ax.set_title(f'Liabilities went from {first_l/first_a if first_a else float("nan"):.1f}x assets ({fy}) to {last_l/last_a:.1f}x assets (Sep 2023)', fontsize=10)
ax.set_xlabel('Period end')
ax.set_ylabel('US dollars, millions')
ax.set_ylim(bottom=0)
ax.grid(axis='y', alpha=0.3)
ax.legend(fontsize=8, loc='upper left')
fig.autofmt_xdate()
fig.tight_layout()

plt.savefig('chart_2.png', dpi=110, bbox_inches='tight')
