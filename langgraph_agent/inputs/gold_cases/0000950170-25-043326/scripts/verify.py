import sys, os, re, glob, pandas as pd
base = sys.argv[1]; case = f'{base}/final_cases/0000950170-25-043326'
norm = lambda s: re.sub(r'\s+', ' ', s.replace('\xa0', ' ')).strip()
texts = {os.path.basename(f): norm(open(f).read()) for f in glob.glob(f'{case}/filings/text/*.txt')}
report = open(f'{case}/report.md').read()
# 1. every quoted passage in the report must appear verbatim in a saved filing
quotes = re.findall(r'"([^"]{25,})"', report)
ok = True
for q in quotes:
    hits = [k for k, t in texts.items() if norm(q) in t]
    print('OK ' if hits else 'MISSING', q[:70], '->', [h[:20] for h in hits])
    ok &= bool(hits)
# 2. recompute cited numbers
df = pd.read_csv(f'{base}/shared/financials.csv'); df = df[df.filed <= 20250321]
co = df[df.cik == 1936224].set_index('adsh'); me = co.loc['0000950170-25-043326']; pr = co.loc['0000950170-24-038767']
q3 = co.loc['0000950170-24-127106']
M = 1e6
chk = {
 'TA 124.1': me.total_assets/M, 'TL 244.1': me.total_liabilities/M, 'rev 119.4': me.revenue/M, 'NI -74.9': me.net_income/M,
 'OCF -54.3': me.operating_cash_flow/M, 'equity -120.0': (me.total_assets-me.total_liabilities)/M,
 'equity23 -77.5': (pr.total_assets-pr.total_liabilities)/M, 'TL/TA 1.97': me.total_liabilities/me.total_assets,
 'CR 0.38': me.current_assets/me.current_liabilities, 'NI/TA -0.60': me.net_income/me.total_assets,
 'OCF/TA -0.44': me.operating_cash_flow/me.total_assets, 'CL/TA 0.72': me.current_liabilities/me.total_assets,
 'CA/TA 0.27': me.current_assets/me.total_assets,
 'Q4 OCF -23.6': (me.operating_cash_flow - q3.operating_cash_flow*3/4)/M,
 'Q4 NI +1.3': (me.net_income - q3.net_income*3/4)/M,
 'burn/mo FY 4.5': -me.operating_cash_flow/12/M, 'burn/mo Q4 7.9': -(me.operating_cash_flow - q3.operating_cash_flow*3/4)/3/M,
 'months FY 4.7': 21.107/(-me.operating_cash_flow/12/M), 'months Q4 2.7': 21.107/(-(me.operating_cash_flow - q3.operating_cash_flow*3/4)/3/M),
 'adj loss 24 -61.3': (-74908+8341-743+0+5690-5398-5976+11732+252-287)/1000,
 'adj loss 23 -89.2': (-250696+3762+0+60045+2147+326+48252+50230+97-3321)/1000,
 'Q4 ex reversal -31': (me.net_income - q3.net_income*3/4)/M - 32.3,
}
chk['adj fall 31%'] = 1 - chk['adj loss 24 -61.3']/chk['adj loss 23 -89.2']
chk['noncash share 18%'] = 1 - chk['adj loss 24 -61.3']/(-74.908)
chk['reported fall 70%'] = 1 - (-74.908)/(-250.696)
for k, v in chk.items(): print(f'{k:22s} {v:.3f}')
# cash figures from filing text
for lab, f, pat in [('cash FY24 21,107', '0000950170-25-043326', 'Cash | 21,107 | 1,720'), ('cash Q3 506', '0000950170-24-127106', 'Cash | 506 | 1,720'),
                    ('related-party 34,522', '0000950170-25-043326', 'Proceeds from borrowings from related parties | 34,522 | 22,502'),
                    ('2025 debt 2,543', '0000950170-25-043326', '2025 | 2,543')]:
    t = [v for k, v in texts.items() if k.startswith(f)][0]; print(lab, pat in t)
# 3. dates: no source after 20250321
print('max filed in data used', co.filed.max(), pd.read_csv(f'{case}/scripts/peers.csv').filed.max())
fil = sorted(os.listdir(f'{case}/filings'))
print('filings saved:', [f[:20] for f in fil if f.endswith('.htm')])
# 4. word count of report (excluding image links)
words = len(re.sub(r'!\[.*?\]\(.*?\)', '', report).split())
print('report words', words, '| all quotes ok', ok)
