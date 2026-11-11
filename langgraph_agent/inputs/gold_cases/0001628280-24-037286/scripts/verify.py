import re,glob,subprocess,pandas as pd
norm=lambda s: re.sub(r'\s+',' ',s.replace('’',"'").replace('\xa0',' ')).strip()
texts={f:norm(open(f).read()) for f in glob.glob('filings/text/*.txt')}
quotes={
'0001628280-24-037286':["As of the date of this report, we believe that our existing cash resources and additional sources of liquidity are not sufficient to support planned operations for the next 12 months.",
  "then the Company is required to make monthly cash payments of amounts outstanding under any Pre-Paid Advance",
  "management cannot conclude as of the date of this filing that its plans are probable of being successfully implemented.",
  "Item 3. Defaults Upon Senior Securities None."],
'0001628280-24-014075':["These matters raise substantial doubt about the Company’s ability to continue as a going concern.",
  "the Company has regained compliance with Nasdaq’s listing rules"],
'0001104659-24-045981':["special purpose vehicles managed by entities affiliated with Mr. Tony Aquila, the Company’s Chief Executive Officer and Executive Chair"]}
for a,qs in quotes.items():
    t=[v for k,v in texts.items() if a in k][0]
    for q in qs: print('OK ' if norm(q) in t else 'MISSING',a,q[:60])
# dates
out=subprocess.run(['/opt/anaconda3/bin/python','../../sec_tools.py','filings','1750153','20240814'],capture_output=True,text=True,cwd='.').stdout
import csv,io; dates={r['adsh']:r['date'] for r in csv.DictReader(io.StringIO(out))}
for f in glob.glob('filings/*.htm'):
    a=f.split('/')[-1][:20]; d=dates.get(a,'2024-08-14' if a=='0001628280-24-037286' else None)
    print(a,d,'OK' if d and d<='2024-08-14' else 'CHECK')
df=pd.read_csv('../../shared/financials.csv'); df=df[df.filed<=20240814]; print('max filed used',df.filed.max())
r=open('report.md').read(); print('words',len(r.split()))
# recompute cited numbers from filing figures ($k)
chk={'unrestricted cash 4.5':4513/1e3,'Q2 burn 35.9':(83419-47519)/1e3,'monthly burn ~12':(83419-47519)/3e3,'months cash 0.4':4513/((83419-47519)/3),
'months incl July 1.6':(4513+14100)/((83419-47519)/3),'Yorkville principal 46.0':31.0+15.0,'with July 61.0':31+15+15,'equity incl pref 196':(543322-347025)/1e3,
'WC -162':(33355-195026)/1e3,'current ratio 0.17':33355/195026,'NI/assets -0.43':-231294/543322,'Q1 23 burn 67':67216/1e3,'Series C 16.5':16500/1e3}
for k,v in chk.items(): print(f'{k:28s} -> {v:.2f}')
