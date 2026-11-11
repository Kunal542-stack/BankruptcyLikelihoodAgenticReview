import pandas as pd
df = pd.read_csv('../../shared/financials.csv'); df = df[df.filed <= 20250506]
co = df[df.cik == 1159167].set_index('adsh')
now, prev, fy = co.loc['0001159167-25-000051'], co.loc['0001159167-24-000039'], co.loc['0001159167-25-000011']
cols = ['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
for c in cols: print(f"{c:22s} Q1'25 {now[c]/1e6:9.1f}  Q1'24 {prev[c]/1e6:9.1f}  chg {(now[c]-prev[c])/1e6:8.1f}")
print('leverage TL/TA', round(now.total_liabilities/now.total_assets,3), 'prev', round(prev.total_liabilities/prev.total_assets,3))
print('current ratio', round(now.current_assets/now.current_liabilities,3), 'FY24', round(fy.current_assets/fy.current_liabilities,3))
print('equity $M', (now.total_assets-now.total_liabilities)/1e6)
# filing figures ($000) - from 10-Q 2025-05-06 and 10-K 2025-03-12 cash flow statements
cash, restricted = 69922, 40003
q1_ocf = -26460; fy24_ocf = -33222; fee_net = 75200
print('monthly burn Q1:', -q1_ocf/3/1e3, 'months of unrestricted cash:', cash/(-q1_ocf/3))
print('monthly burn FY24:', -fy24_ocf/12/1e3, 'months:', cash/(-fy24_ocf/12))
print('FY24 burn ex Amazon fee:', (-fy24_ocf+fee_net)/12/1e3, 'months:', cash/((-fy24_ocf+fee_net)/12))
print('months incl restricted, Q1 burn:', (cash+restricted)/(-q1_ocf/3))
# non-cash adjustments, same lines every period: D&A, SBC, loss on equity inv, inventory provision, FV change of term loan, debt costs expensed, deferred tax
adj = {
 'FY2022': (-286295, [47869, 31905, 19718, 2888, 0, 0, 18799]),
 'FY2023': (-304710, [32791, 36056, 3910, 6378, 5904, 11837, 6563]),
 'FY2024': (-145518, [21667, 24476, 370, 13489, 24557, 583, -2391]),
 'Q1 2024': (8607, [5812, 7948, 375, 200, -1008, 239, -127]),
 'Q1 2025': (-87273, [2623, 5314, 0, 384, 25965, 11614, 292]),
}
rows = []
for k, (ni, a) in adj.items():
    rows.append([k, ni/1e3, sum(a)/1e3, (ni+sum(a))/1e3, sum(a)/-ni if ni < 0 else None])
out = pd.DataFrame(rows, columns=['period','net_income','noncash_addbacks','adjusted','share_noncash'])
print(out.round(3).to_string())
print('FY24 adjusted ex Amazon fee', (adj['FY2024'][0]+sum(adj['FY2024'][1])-fee_net)/1e3)
print('Q1 24 adjusted ex Amazon fee', (adj['Q1 2024'][0]+sum(adj['Q1 2024'][1])-fee_net)/1e3)
out.to_csv('scripts/adjusted_loss.csv', index=False)
core = 69922+30804+68968; print('core assets ex restricted', core/1e3, 'incl restricted', (core+restricted)/1e3, 'vs covenant 200.0')
print('principal x1.4 / x1.7', 184231*1.4/1e3, 184231*1.7/1e3)
print('term loan FV vs cash', 224084/cash)
print('days 2025-05-06 -> 2026-07-24', (pd.Timestamp('2026-07-24')-pd.Timestamp('2025-05-06')).days)
print('rev decline Q1', 101569/150014-1, 'FY', 681849/890580-1, 890580/1183383-1)
