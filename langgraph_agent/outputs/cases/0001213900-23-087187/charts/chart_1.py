import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
history = pd.read_csv("data/history.csv")  # the company's reports up to this one: the 8 inputs (per year, 10-Qs annualized)
peers = pd.read_csv("data/peers.csv")      # same-industry peers at about the same date: the same 8 inputs
facts = json.load(open("data/facts.json"))  # case, numbers, cash, assessment (verdict, reasons, timeline)

cl = 21.69e6
try:
    v = history.sort_values('ddate').iloc[-1]['current_liabilities']
    if pd.notna(v) and v > 0:
        cl = float(v)
except Exception:
    pass
monthly = 45416.67*4 + 47142.85*3 + 11021*4
labels = ['Cash at 9/30/2023', 'Raised after quarter\n(equity line + PIPE + note)', 'Monthly note payments\nNov 2023 - Feb 2024', 'Senior secured notes\nalready in default', 'Debentures due\nFeb 28, 2024', 'Total current liabilities\nat 9/30/2023']
vals = [6759, 195500, monthly, 2265447, 2485000 + 2267140, cl]
colors = ['#2ca02c', '#98df8a', '#ff9896', '#d62728', '#d62728', 'grey']
texts = ['\\$6,759 (too small to see)', '\\$195,500', '\\$%s' % format(int(round(monthly)), ','), '\\$2.27M', '\\$4.75M', '\\$%.2fM' % (cl/1e6)]
fig, ax = plt.subplots(figsize=(7, 3.5))
y = np.arange(len(vals))[::-1]
ax.barh(y, np.array(vals)/1e6, color=colors)
for yi, v, t in zip(y, vals, texts):
    ax.text(v/1e6 + 0.25, yi, t, va='center', fontsize=8)
ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=8)
ax.set_xlabel('US dollars, millions')
ax.set_xlim(0, max(vals)/1e6 * 1.2)
ax.grid(axis='x', alpha=0.3)
ax.set_axisbelow(True)
handles = [plt.Rectangle((0, 0), 1, 1, color='#2ca02c'), plt.Rectangle((0, 0), 1, 1, color='#d62728'), plt.Rectangle((0, 0), 1, 1, color='grey')]
ax.legend(handles, ['cash available or raised', 'cash demanded', 'all current liabilities'], fontsize=7, loc='upper right', frameon=False)
ax.set_title('Creatd had \\$6,759 of cash against \\$4.75M of debentures due Feb 2024', fontsize=10)
fig.tight_layout()

plt.savefig('chart_1.png', dpi=110, bbox_inches='tight')
