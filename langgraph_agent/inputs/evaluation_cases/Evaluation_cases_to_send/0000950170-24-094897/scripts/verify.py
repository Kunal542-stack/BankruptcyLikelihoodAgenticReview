import re, glob
D='final_cases-1/0000950170-24-094897'
rep = open(f'{D}/report.md').read()
texts = {p.split('/')[-1][:20]: re.sub(r'\s+',' ',open(p).read()) for p in glob.glob(f'{D}/filings/*.txt')}
quotes = re.findall(r'"([^"]{6,})"', rep)
for q in quotes:
    qn = re.sub(r'\s+',' ',q)
    hits = [k for k,t in texts.items() if qn in t]
    print('OK ' if hits else 'MISSING', q[:70], hits[:2])
# links: dates of every EDGAR adsh cited must be <= 20240809
filed = {'000095017024094897':'20240809','000095017024057258':'20240509','000095017024032506':'20240318','000095017024032508':'20240318',
 '000095017024003948':'20240111','000095017024073734':'20240614','000095017024082848':'20240711','000095017024060022':'20240515','000095017023008561':'20230317'}
for a in set(re.findall(r'edgar/data/1813914/(\d{18})/', rep)):
    print(a, filed.get(a,'UNKNOWN'), 'ok' if filed.get(a,'99999999')<='20240809' else 'LATE')
words = len(re.sub(r'\(https?://[^)]+\)|\([^)]*\.png\)|\(\.\./[^)]+\)','',rep).split()); print('words', words)
