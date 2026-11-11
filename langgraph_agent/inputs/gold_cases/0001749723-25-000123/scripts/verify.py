import glob,re,datetime as dt
txt={f:re.sub(r'\s+',' ',open(f).read()) for f in glob.glob('filings/text/*.txt')}
rep=open('report.md').read()
quotes=re.findall(r'"([^"]{15,})"',rep)
for q in quotes:
    qn=re.sub(r'\s+',' ',q)
    hits=[f.split('/')[-1][:20] for f,t in txt.items() if qn in t]
    print('OK ' if hits else 'MISSING',hits[:2],q[:70])
print('words:',len(re.findall(r'\S+',rep)))
# dates of filings used (from list), all must be <= 2025-09-05
import subprocess
dates=re.findall(r'20\d\d-\d\d-\d\d',rep.split('## Filings used')[1])
print('max filing date cited', max(dates), 'ok' if max(dates)<='2025-09-05' else 'LATE')
