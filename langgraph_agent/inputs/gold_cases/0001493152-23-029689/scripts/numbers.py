"""Company vs history vs SIC-37 peers. Usage: python -I numbers.py <repo_root> <case_dir>"""
import sys, pandas as pd, numpy as np
root, case = sys.argv[1], sys.argv[2]
CUT = 20230821
d = pd.read_csv(f'{root}/shared/financials.csv')
d = d[d.filed <= CUT].copy()          # drop everything filed after the report date
print('max filed date used:', d.filed.max())
C = ['total_assets','current_assets','current_liabilities','total_liabilities',
     'revenue','net_income','operating_income','operating_cash_flow']
me = d[d.adsh == '0001493152-23-029689'].iloc[0]
print(d[d.cik == 1855631][['form','ddate','filed'] + C].to_string())

# peers: same 2-digit SIC, period ending Apr-Jun 2023 (latest per company), excluding the company
d['sic2'] = (d.sic // 100).astype('Int64')
p = d[(d.sic2 == 37) & (d.cik != 1855631) & d.ddate.between(20230331, 20230630)]
p = p.sort_values('ddate').groupby('cik').tail(1)
print('peers:', len(p))

def ratios(x):
    r = pd.DataFrame(index=x.index)
    r['ni_assets'] = x.net_income / x.total_assets
    r['oi_assets'] = x.operating_income / x.total_assets
    r['ocf_assets'] = x.operating_cash_flow / x.total_assets
    r['rev_assets'] = x.revenue / x.total_assets
    r['liab_assets'] = x.total_liabilities / x.total_assets
    r['current_ratio'] = x.current_assets / x.current_liabilities
    r['ni_rev'] = x.net_income / x.revenue
    return r
pr = ratios(p); mr = ratios(me.to_frame().T.astype({c: float for c in C})).iloc[0]

def pct(series, v):  # share of peers below company value
    s = series.dropna(); return 100 * (s < v).mean()

out = []
for c in C:
    out.append([c, me[c], p[c].median(), pct(p[c], me[c]), p[c].notna().sum()])
for c in pr.columns:
    out.append([c, mr[c], pr[c].median(), pct(pr[c], mr[c]), pr[c].notna().sum()])
t = pd.DataFrame(out, columns=['item', 'company', 'peer_median', 'pct_peers_below', 'n'])
pd.set_option('display.float_format', lambda v: f'{v:,.3f}')
print(t.to_string())
t.to_csv(f'{case}/scripts/peer_table.csv', index=False)

# own history from the 10-Q itself (legacy AERWINS/ALI); H1 figures annualised x2 like the dataset
h1_23 = dict(revenue=457753, net_income=-19222865, operating_income=-17109735, operating_cash_flow=-8157404)
h1_22 = dict(revenue=1934118, net_income=-7227936, operating_income=-7378868, operating_cash_flow=-9037536)
bs_dec22 = dict(total_assets=11779346, current_assets=8226174, current_liabilities=5901145, total_liabilities=9870442)
for k in h1_23: print(k, 'annualised 2023:', 2*h1_23[k], ' 2022:', 2*h1_22[k], ' check dataset:', me[k])

# liquidity
cash_jun, cash_mar, cash_dec = 35359, 235741, 1278026
q1_ocf, h1_ocf = -4037773, -8157404
q2_ocf = h1_ocf - q1_ocf
print('Q2 OCF', q2_ocf, 'monthly burn H1', h1_ocf/6, 'Q2', q2_ocf/3)
print('months of cash (H1 burn)', cash_jun/(-h1_ocf/6), ' (Q2 burn)', cash_jun/(-q2_ocf/3), ' days at Q2 burn', cash_jun/(-q2_ocf/91))
print('current ratio', me.current_assets/me.current_liabilities, ' Dec22', bs_dec22['current_assets']/bs_dec22['current_liabilities'])
print('liab/assets', me.total_liabilities/me.total_assets, ' Dec22', bs_dec22['total_liabilities']/bs_dec22['total_assets'])
print('equity', me.total_assets - me.total_liabilities)
print('working capital', me.current_assets - me.current_liabilities)
# debt past due / due now
past_due = 1480000 + 692185
print('past-due debt', past_due, 'x cash', past_due/cash_jun)
print('AP + AP related', 6320552 + 312424, 'x cash', (6320552 + 312424)/cash_jun)

# non-cash adjustment, same lines both years (continuing operations, cash-flow statement)
adj23 = dict(dep=187054, amort=23541, interest=435072, lease=205103, sbc=3658298, warrant_fv=-1199672,
             deriv_fv=-595673, bad_debt=7256, impair=1565853, disposal=1191, inv_gain=0, equity_inv=11640, deriv_exp=1088477)
adj22 = dict(dep=141406, amort=27060, interest=0, lease=169666, sbc=0, warrant_fv=0,
             deriv_fv=0, bad_debt=-691, impair=0, disposal=176, inv_gain=-451154, equity_inv=-10736, deriv_exp=0)
for yr, ni, a in [('H1 2023', -18376366, adj23), ('H1 2022', -6548417, adj22)]:
    s = sum(a.values())
    print(yr, 'cont. net loss', ni, 'non-cash', s, 'cash-adjusted loss', ni + s, 'non-cash share', s / -ni)

# small peers only (total assets < $50M) - is it just size?
sp = p[p.total_assets < 50e6]; spr = ratios(sp)
print('small peers', len(sp))
for c in ['ni_assets', 'ocf_assets', 'liab_assets', 'current_ratio']:
    print(c, 'small-peer median', round(spr[c].median(), 3), 'company', round(mr[c], 3), 'pct below', round(pct(spr[c], mr[c]), 1))
print('small peers with negative equity:', round(100*(sp.total_liabilities > sp.total_assets).mean(), 1), '%')
