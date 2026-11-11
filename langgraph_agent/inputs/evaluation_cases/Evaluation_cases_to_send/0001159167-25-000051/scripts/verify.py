import re, glob, os, pandas as pd
rep = open('report.md').read()
norm = lambda s: re.sub(r'\s+', ' ', s.replace('’', "'").replace('“', '"').replace('”', '"'))
texts = {os.path.basename(p): norm(open(p).read()) for p in glob.glob('filings/text/*.txt')}
# 1 quotes (italic *"..."*)
quotes = re.findall(r'\*"(.+?)"\*', rep)
for q in quotes:
    hits = [k for k, t in texts.items() if norm(q) in t]
    print('OK ' if hits else 'MISSING', q[:70], hits[:2])
# 2 links: dates of EDGAR docs
lst = pd.read_csv('scripts/filing_list.csv')
extra = {'0001159167-25-000050': '2025-05-06', '0001159167-25-000051': '2025-05-06'}
for u in sorted(set(re.findall(r'\]\((https?://[^)]+|[^)]+)\)', rep))):
    m = re.search(r'/data/1159167/(\d{18})/', u)
    if m:
        a = m.group(1); a = f'{a[:10]}-{a[10:12]}-{a[12:]}'
        d = extra.get(a) or lst.loc[lst.adsh == a, 'date'].iloc[0]
        saved = any(a in f for f in os.listdir('filings'))
        print('LINK', d, a, 'saved' if saved else 'NOT SAVED', 'AFTER!' if d.replace('-', '') > '20250506' else '')
    else:
        print('LINK other', u, 'exists' if u.startswith('http') or os.path.exists(u) else 'MISSING FILE')
# 3 numbers
df = pd.read_csv('../../shared/financials.csv'); assert (df[df.filed <= 20250506].filed.max() <= 20250506)
chk = {'NI/rev': -349.092/406.276, 'FV/cash': 224084/69922, 'months Q1': 69922/(26460/3), 'months FY24 ex fee': 69922/((33222+75200)/12),
       'months FY24': 69922/(33222/12), 'core': (69922+30804+68968)/1e3, 'payoff': (184231*1.4/1e3, 184231*1.7/1e3),
       'rev chg': 101569/150014-1, 'R&D chg': 14686/33878-1, 'Q1 noncash': (2623+5314+384+25965+11614+292)/1e3,
       'Q1 cash loss x4': (-87273+46192)*4/1e3}
for k, v in chk.items(): print('NUM', k, v)
print(open('scripts/adjusted_loss.csv').read())
words = len(re.sub(r'\(https?://[^)]+\)', '', rep).split()); print('WORDS (excl. URLs)', words, '| raw', len(rep.split()))
