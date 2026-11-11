import re,glob,sys
from bs4 import BeautifulSoup
import pandas as pd
def norm(t): return re.sub(r'\s+',' ',t.replace('’',"'").replace('\xa0',' ')).strip()
docs={}
for f in glob.glob('filings/*.htm'):
    s=BeautifulSoup(open(f,'rb').read(),'html.parser')
    for t in s.find_all('ix:header'): t.decompose()
    docs[f]=norm(s.get_text(' '))
rep=open('report.md').read()
quotes=re.findall(r"\"([^\"\n]{20,}?)\"",rep)
ok=True
for q in quotes:
    hits=[f for f,t in docs.items() if norm(q) in t]
    print('OK ' if hits else 'MISSING',q[:70],'->',[h.split('/')[-1][:20] for h in hits][:2]); ok&=bool(hits)
# dates
fl=pd.read_csv('../../shared/financials.csv'); fl=fl[fl.adsh.isin([f.split('/')[-1][:20] for f in docs])]
dates=re.findall(r'(\d{4}-\d{2}-\d{2}),(?:8-K|10-K|10-Q)',open('filings_list.txt').read()) if False else []
import subprocess
out=subprocess.run(['/opt/anaconda3/bin/python','../../sec_tools.py','filings','1841800','20230814'],capture_output=True,text=True,cwd='.').stdout
idx={l.split(',')[2]:l.split(',')[0] for l in out.splitlines()[1:] if l.count(',')>=3}
for f in docs:
    a=f.split('/')[-1][:20]; d=idx.get(a,'(not in list: this report, filed 2023-08-14 per task)'); print(a,d)
    if a in idx and idx[a]>'2023-08-14': ok=False; print('  LATE!')
print('ALL QUOTES FOUND' if ok else 'PROBLEM')
