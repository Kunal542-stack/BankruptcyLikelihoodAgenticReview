import re,glob,os,pandas as pd
B='final_cases/0001159167-25-000011/'
norm=lambda s: re.sub(r'\s+',' ',s.replace('’',"'").replace('“','"').replace('”','"'))
texts={os.path.basename(f):norm(open(f).read()) for f in glob.glob(B+'filings/*.txt')}
rep=open(B+'report.md').read()
quotes=re.findall(r'\*"(.+?)"\*',rep)
for q in quotes:
    hits=[k for k,t in texts.items() if norm(q) in t]
    print('OK ' if hits else 'MISSING', q[:70], hits)
print('words',len(re.findall(r'\S+',rep)))
# dates
import subprocess
import csv,io; fl=subprocess.run(["/opt/anaconda3/bin/python","sec_tools.py","filings","1159167","20250312"],capture_output=True,text=True).stdout
dates={row["adsh"]:row["date"] for row in csv.DictReader(io.StringIO(fl))}
for f in texts:
    a=f.split('_')[0]; print(a, dates.get(a,'(this report, filed 2025-03-12)'))
assert all(d<='2025-03-12' for d in dates.values())
df=pd.read_csv('shared/financials.csv',dtype={'adsh':str}); df=df[df.filed<=20250312]
me=df[df.adsh=='0001159167-25-000011'].iloc[0]; print('filed',me.filed)
print('NI/TA',me.net_income/me.total_assets,'TL/TA',me.total_liabilities/me.total_assets,'equity',(me.total_assets-me.total_liabilities)/1e6,'cur',me.current_assets/me.current_liabilities)
