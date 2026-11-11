import re, os, glob, subprocess, sys
D='final_cases/0001078207-23-000108'
norm=lambda s: re.sub(r'\s+',' ',s.replace('’',"'").replace('“','"').replace('”','"')).strip()
texts={os.path.basename(f)[:20]:norm(open(f).read()) for f in glob.glob(f'{D}/filings/text/*.txt')}
rep=open(f'{D}/report.md').read()
quotes=re.findall(r'\*"([^"]+)"\*', rep) + ['$7.0 million and 12.5% of the Combined Line Cap','to refinance the existing term loan facility with Wells Fargo Bank']
bad=0
for q in quotes:
    hits=[k for k,t in texts.items() if norm(q) in t]
    print('OK ' if hits else 'MISSING', hits[:2], q[:70]); bad+= not hits
# dates: every downloaded filing must be on/before 20230809
out=subprocess.run(['/opt/anaconda3/bin/python','sec_tools.py','filings','1078207','20230809'],capture_output=True,text=True).stdout
import csv, io
dates={r['adsh']:r['date'] for r in csv.DictReader(io.StringIO(out))}
dates['0001078207-23-000108']='2023-08-09 (this report)'
for f in sorted(glob.glob(f'{D}/filings/*.htm')):
    a=os.path.basename(f)[:20]; d=dates.get(a,'?'); print(a,d); assert d!='?' and d[:10]<='2023-08-09'
words=len(re.findall(r'\S+', rep)); print('report words', words); assert words<=1200
print('quote problems', bad)

print('runway at cash loss+capex (months)', round(18280/((8718+1178)/3),1), '| debt/equity', round(17300/59071,2), '| pre-tax ex gain', -4419-9021)
