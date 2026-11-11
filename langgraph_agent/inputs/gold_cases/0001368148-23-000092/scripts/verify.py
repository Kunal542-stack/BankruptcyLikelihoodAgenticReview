import re,glob,os,subprocess,sys
from bs4 import BeautifulSoup
import pandas as pd
os.chdir(os.path.dirname(os.path.abspath(__file__))+'/..')
def norm(t): return re.sub(r'\s+',' ',t.replace('\xa0',' ')).strip()
texts={}
for f in glob.glob('filings/*.htm'):
    s=BeautifulSoup(open(f,encoding='utf-8',errors='ignore').read(),'html.parser')
    texts[os.path.basename(f)]=norm(s.get_text(' '))
rep=open('report.md').read()
quotes=re.findall(r"\"([^\"]+)\"",rep)
ok=True
for q in quotes:
    qn=norm(q); hits=[k for k,t in texts.items() if qn in t or qn in re.sub(r'\$ ','$',t) or qn in re.sub(r' (?=[,.%])','',re.sub(r'\$ ','$',t))]
    print('OK ' if hits else 'MISSING', q[:70], hits[:2]); ok&=bool(hits)
# dates of sources
out=subprocess.run(['/opt/anaconda3/bin/python','../../sec_tools.py','filings','1368148','20230816'],capture_output=True,text=True,cwd='.').stdout
dates={l.split(',')[2]:l.split(',')[0] for l in out.splitlines()[1:] if l.count(',')>2}
for f in sorted(texts):
    a=f.split('_')[0]; d=dates.get(a,'2023-08-16 (this report)' if a=='0001368148-23-000092' else '??')
    print(a,d,'LATE!' if d[:10]>'2023-08-16' else '')
# numbers
df=pd.read_csv('../../shared/financials.csv'); df=df[df.filed<=20230816]
me=df[df.adsh=='0001368148-23-000092'].iloc[0]; print('max filed used',df.filed.max())
chk={'TL/TA':(me.total_liabilities/me.total_assets,4.57),'CR':(me.current_assets/me.current_liabilities,0.09),'NI/TA':(me.net_income/me.total_assets,-3.96),
 'Q2 OCF $m':((-10551+5966)/1e3,-4.6),'months Jun30':(1803/(4585/3),1.2),'months Aug9':(800/(4585/3),0.5),'cash/CL':(1803/42697,0.04),
 'adj FY22':((-72534+1420+7240+6203-32-4197)/1e3,-61.9),'adj H1 23':((-20735+95-2612+7545+1275+185+640+2151)/1e3,-11.5),
 'adj FY20':((-78765+890+7379)/1e3,-70.5),'adj FY21':((-86955+1427+8556+235)/1e3,-76.7),'adj H1 22':((-45864+865+4931+3355)/1e3,-36.7),
 'yrago TL':((33221+8284+5199+238)/1e3,46.9),'NI ann':(me.net_income/1e6,-41.5)}
for k,(a,b) in chk.items(): print(k,round(a,2),b,'OK' if abs(a-b)<0.06*max(1,abs(b)) else 'CHECK')
body=re.sub(r'!\[.*?\]\(.*?\)','',rep); print('words',len(body.split()))
print('ALL QUOTES OK' if ok else 'QUOTE PROBLEM')
