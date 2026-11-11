"""Check quotes, recompute numbers, check dates, count words.
Usage: python -I verify.py <repo_root> <case_dir>"""
import sys, re, os, pandas as pd
root, case = sys.argv[1], sys.argv[2]
rep = open(f'{case}/report.md').read()
norm = lambda t: re.sub(r'\s+', ' ', t.replace('’', "'").replace('“', '"').replace('”', '"')).strip()
corpus = {f: norm(open(f'{case}/text/{f}').read()) for f in os.listdir(f'{case}/text')}

# 1. every quoted passage (>= 15 chars) must appear verbatim in a saved filing
quotes = [q for q in re.findall(r'"([^"]*)"', rep) if len(q) >= 15]
bad = 0
for q in quotes:
    hits = [f for f, t in corpus.items() if norm(q) in t]
    print('OK ' if hits else 'MISSING', q[:70], '->', hits[:1]); bad += not hits
print('quotes:', len(quotes), 'missing:', bad)

# 2. recompute numbers cited
d = pd.read_csv(f'{root}/shared/financials.csv'); d = d[d.filed <= 20230821]
me = d[d.adsh == '0001493152-23-029689'].iloc[0]
chk = {
 'NI/assets -5.8': round(me.net_income / me.total_assets, 1) == -5.8,
 'liab/assets 2.71': round(me.total_liabilities / me.total_assets, 2) == 2.71,
 'current ratio 0.47': round(me.current_assets / me.current_liabilities, 2) == 0.47,
 'equity -11.4M': round((me.total_assets - me.total_liabilities) / 1e6, 1) == -11.4,
 'burn H1 1.36M/mo': round(8157404 / 6 / 1e6, 2) == 1.36,
 'burn Q2 1.37M/mo': round((8157404 - 4037773) / 3 / 1e6, 2) == 1.37,
 'months 0.03': round(35359 / (4119631 / 3), 2) == 0.03,
 'past due 2.17M, 61x': round((1480000 + 692185) / 1e6, 2) == 2.17 and int((1480000 + 692185) / 35359) == 61,
 'rev ann 0.92M': round(me.revenue / 1e6, 2) == 0.92 and 2 * 457753 == me.revenue,
 'NI ann 38.4M': round(-me.net_income / 1e6, 1) == 38.4,
 'prior NI 14.5M': round(2 * 7227936 / 1e6, 1) == 14.5,
 'prior rev 3.87M': round(2 * 1934118 / 1e6, 2) == 3.87,
 'prior OI 14.8M': round(2 * 7378868 / 1e6, 1) == 14.8,
 'prior OCF 18.1M': round(2 * 9037536 / 1e6, 1) == 18.1,
 'cash-adj 13.0 vs 6.7, 29%': round((18376366 - 5388140) / 1e6, 1) == 13.0 and round((6548417 + 124273) / 1e6, 1) == 6.7 and round(5388140 / 18376366, 2) == 0.29,
 '2022 loss 14.5M (deficit change)': round((46472904 - 31993085) / 1e6, 1) == 14.5,
 'insider payments 312k': 102000 + 210424 == 312424,
 'WC deficit BS': 5457032 - 11532773 == -6075741,
 'AP rise 2.87M': round(2871733 / 1e6, 2) == 2.87,
 'warrant+deriv 2.7M': round((1255795 + 1456641) / 1e6, 1) == 2.7,
 'Lind cash 3.5M': 2100000 + 1400000 == 3500000,
}
pt = pd.read_csv(f'{case}/scripts/peer_table.csv').set_index('item')
chk['peer ranks'] = [round(pt.loc[c, 'pct_peers_below']) for c in ['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']] == [10, 13, 19, 18, 6, 29, 27, 33]
chk['ni/assets worse than 95%'] = round(100 - pt.loc['ni_assets', 'pct_peers_below']) == 95
chk['liab/assets worse than 95%'] = round(pt.loc['liab_assets', 'pct_peers_below']) == 95
chk['peer medians'] = round(pt.loc['liab_assets', 'peer_median'], 2) == 0.63 and round(pt.loc['current_ratio', 'peer_median'], 2) == 1.74
for k, v in chk.items(): print('OK ' if v else 'FAIL', k)

# 3. dates: no source after 20230821
fl = os.listdir(f'{case}/filings')
print('max filed in csv rows used:', d.filed.max())
import subprocess
lst = subprocess.run(['/opt/anaconda3/bin/python', f'{root}/sec_tools.py', 'filings', '1855631', '20230821'], capture_output=True, text=True, cwd=root).stdout
dates = {l.split(',')[2]: l.split(',')[0] for l in lst.splitlines()[1:] if l.count(',') >= 3}
print('listed filings:', len(dates))
for f in fl:
    a = f.split('_')[0]; print(a, dates.get(a, 'not in list (this report, filed 2023-08-21)'))
late = [a for a in (f.split('_')[0] for f in fl) if dates.get(a, '2023-08-21') > '2023-08-21']
print('sources after cutoff:', late)

# 4. word count
print('words:', len(re.findall(r'\S+', rep)))
