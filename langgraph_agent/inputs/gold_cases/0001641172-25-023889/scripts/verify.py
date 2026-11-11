import re,glob,sys,pandas as pd
B='final_cases/0001641172-25-023889/'
def norm(t): return re.sub(r'\s+',' ',t.replace('’',"'").replace('“','"').replace('”','"')).strip()
txt={f:norm(open(f).read()) for f in glob.glob(B+'filings/*.txt')}
rep=open(B+'report.md').read()
quotes=[q for q in re.findall(r'"([^"]{25,})"',rep)]
quotes+= re.findall(r'“([^”]{25,})”',rep)
for q in quotes:
    hits=[f.split('/')[-1][:20] for f,t in txt.items() if norm(q) in t]
    print('OK ' if hits else 'MISSING', q[:70], hits[:2])
# filing dates
import subprocess
out=subprocess.run(['/opt/anaconda3/bin/python','sec_tools.py','filings','1643988','20250814'],capture_output=True,text=True).stdout
import csv,io; dates={r[2]:r[0] for r in csv.reader(io.StringIO(out)) if len(r)>2}
for f in glob.glob(B+'filings/*.htm'):
    a=f.split('/')[-1][:20]; print(a, dates.get(a,'(target 10-Q, filed 2025-08-14)'))
print('all listed <= 2025-08-14:', all(dates.get(f.split('/')[-1][:20],'2025-08-14')<='2025-08-14' for f in glob.glob(B+'filings/*.htm')))
print('words', len(re.sub(r'!\[.*?\]\(.*?\)','',rep).split()))
