import sys, pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
base = sys.argv[1]
case = f'{base}/final_cases/0000950170-25-043326'
df = pd.read_csv(f'{base}/shared/financials.csv')
df = df[df.filed <= 20250321]
co = df[df.cik == 1936224].sort_values('filed').set_index('adsh')
me = co.loc['0000950170-25-043326']; prev = co.loc['0000950170-24-038767']
M = 1e6

# ---- ratios from the model inputs
print('TL/TA', me.total_liabilities/me.total_assets, 'prev', prev.total_liabilities/prev.total_assets)
print('equity', (me.total_assets-me.total_liabilities)/M, 'prev', (prev.total_assets-prev.total_liabilities)/M)
print('current ratio', me.current_assets/me.current_liabilities, 'prev', prev.current_assets/prev.current_liabilities)
for c in ['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']:
    print(f'{c:22s} {me[c]/M:9.1f} {prev[c]/M:9.1f} chg {100*(me[c]/prev[c]-1):6.0f}%')

# ---- quarterly values derived from annualized rows (10-Q rows annualized: Q1 x4, Q2 x2, Q3 x4/3)
num = ['net_income','operating_income','operating_cash_flow']; q3 = co.loc['0000950170-24-127106', num].astype(float); q2 = co.loc['0000950170-24-097145', num].astype(float); q1 = co.loc['0000950170-24-060529', num].astype(float)
ytd = {'Q1': q1*1/4, 'Q2': q2*2/4, 'Q3': q3*3/4, 'FY': me}
quarter = {}
for k in ['net_income','operating_income','operating_cash_flow']:
    v = [ytd['Q1'][k], ytd['Q2'][k]-ytd['Q1'][k], ytd['Q3'][k]-ytd['Q2'][k], ytd['FY'][k]-ytd['Q3'][k]]
    quarter[k] = v
    print(k, 'quarterly 2024 ($M):', [round(x/M, 2) for x in v])

# ---- cash and runway (cash from balance sheets in filings, $K)
cash = {'2023-12-31': 1720, '2024-03-31': 1278, '2024-06-30': 1460, '2024-09-30': 506, '2024-12-31': 21107}
restricted = 568
fy_burn = -me.operating_cash_flow/12/M
q4_burn = -quarter['operating_cash_flow'][3]/3/M
fcf_fy = (-54322 - 3609)/1000/12   # OCF + net investing, $M per month (10-K cash flow statement)
print('monthly burn FY', fy_burn, 'Q4', q4_burn, 'FY incl. investing', fcf_fy)
print('months of cash: FY', 21.107/fy_burn, 'Q4', 21.107/q4_burn, 'FY incl inv', 21.107/fcf_fy)

# ---- cash-adjusted loss, same adjustments both years (10-K cash flow statement, $K)
adj = pd.DataFrame({
  '2024': {'net_loss': -74908, 'D&A': 8341, 'gain_sale_fa': -743, 'goodwill_impairment': 0, 'noncash_lease': 5690,
           'debt_extinguishment': -5398, 'stock_comp': -5976, 'fair_value_changes': 11732, 'debt_disc_amort': 252, 'deferred_tax': -287},
  '2023': {'net_loss': -250696, 'D&A': 3762, 'gain_sale_fa': 0, 'goodwill_impairment': 60045, 'noncash_lease': 2147,
           'debt_extinguishment': 326, 'stock_comp': 48252, 'fair_value_changes': 50230, 'debt_disc_amort': 97, 'deferred_tax': -3321}})
print(adj); tot = adj.sum(); print('cash-adjusted loss $K', tot.to_dict())
print('non-cash share of loss', {k: 1 - tot[k]/adj.loc['net_loss', k] for k in tot.index})
print('Q4 stock comp ($K):', -5976 - 14643, ' Q4 NI ex SBC reversal 32.3M:', quarter['net_income'][3]/M - 32.3)

# ---- peers
p = pd.read_csv(f'{case}/scripts/peers.csv')
p['tl_ta'] = p.total_liabilities/p.total_assets; p['ocf_ta'] = p.operating_cash_flow/p.total_assets
p['ni_ta'] = p.net_income/p.total_assets; p['cr'] = p.current_assets/p.current_liabilities
p['ni_rev'] = p.net_income/p.revenue
small = p[p.total_assets < 2e9]
print(small[['name','filed','total_assets','revenue','net_income','tl_ta','ocf_ta','ni_ta','cr']].sort_values('total_assets').to_string())
mine = dict(tl_ta=me.total_liabilities/me.total_assets, ocf_ta=me.operating_cash_flow/me.total_assets,
            ni_ta=me.net_income/me.total_assets, cr=me.current_assets/me.current_liabilities, ni_rev=me.net_income/me.revenue)
for k, v in mine.items():
    print(k, round(v, 3), 'all-peer median', round(p[k].median(), 3), 'rank worse-than', int((p[k] > v).sum() if k != 'tl_ta' else (p[k] < v).sum()), 'of', p[k].notna().sum(),
          '| small-peer median', round(small[k].median(), 3), 'n', len(small))

# ---- charts
plt.rcParams.update({'font.size': 10})
# 1 cash vs burn
fig, ax = plt.subplots(figsize=(7, 4))
qs = ['Q1 24', 'Q2 24', 'Q3 24', 'Q4 24']
ax.bar(qs, [-x/M for x in quarter['operating_cash_flow']], color='firebrick', label='Operating cash burn in quarter')
ax.plot(qs, [cash[d]/1000 for d in ['2024-03-31', '2024-06-30', '2024-09-30', '2024-12-31']], 'o-k', label='Cash at quarter end')
for i, d in enumerate(['2024-03-31', '2024-06-30', '2024-09-30', '2024-12-31']):
    ax.annotate(f"${cash[d]/1000:.1f}M", (i, cash[d]/1000), textcoords='offset points', xytext=(0, 8), ha='center')
ax.set_ylabel('$ million'); ax.set_title('Cash was near zero until the Nov-2024 refinancing; Q4 burn was the highest of the year')
ax.title.set_fontsize(9); ax.legend(loc='upper left'); fig.tight_layout(); fig.savefig(f'{case}/charts/cash_vs_burn.png', dpi=130)
# 2 reported vs cash-adjusted loss
fig, ax = plt.subplots(figsize=(6, 4))
x = np.arange(2); w = 0.35
ax.bar(x-w/2, [-250.696, -74.908], w, label='Reported net loss', color='grey')
ax.bar(x+w/2, [tot['2023']/1000, tot['2024']/1000], w, label='Loss after removing non-cash items', color='firebrick')
ax.bar(x+w/2+0.0, [0, 0], w)
ax.set_xticks(x, ['2023', '2024']); ax.axhline(0, color='k', lw=.8); ax.set_ylabel('$ million')
for i, (a, b) in enumerate(zip([-250.696, -74.908], [tot['2023']/1000, tot['2024']/1000])):
    ax.text(i-w/2, a-8, f'{a:.0f}', ha='center'); ax.text(i+w/2, b-8, f'{b:.0f}', ha='center')
ax.set_ylim(-280, 10)
ax.set_title('Reported loss fell 70%; the cash-adjusted loss fell about 31%'); ax.title.set_fontsize(9)
ax.legend(loc='lower right'); fig.tight_layout(); fig.savefig(f'{case}/charts/loss_reported_vs_cash.png', dpi=130)
# 3 peers scatter
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.scatter(p.tl_ta, p.ocf_ta, color='steelblue', label='Air transport peers (SIC 45)')
for _, r in small.iterrows():
    ax.annotate(' '.join(r['name'].replace(',', '').split()[:2]).title(), (r.tl_ta, r.ocf_ta), fontsize=7, xytext=(3, 3), textcoords='offset points')
ax.scatter([mine['tl_ta']], [mine['ocf_ta']], color='red', s=80, label='Surf Air FY2024')
ax.annotate('Surf Air', (mine['tl_ta'], mine['ocf_ta']), color='red', xytext=(5, -10), textcoords='offset points')
ax.axvline(1, ls='--', color='grey', lw=.8); ax.axhline(0, ls='--', color='grey', lw=.8)
ax.set_xlabel('Total liabilities / total assets'); ax.set_ylabel('Operating cash flow / total assets')
ax.set_title('Surf Air is among the most indebted and fastest cash-burning air transport filers'); ax.title.set_fontsize(9)
ax.legend(loc='lower left', fontsize=8); fig.tight_layout(); fig.savefig(f'{case}/charts/peers_leverage_burn.png', dpi=130)
print('peer filed max', p.filed.max(), 'company rows filed max', co.filed.max())
