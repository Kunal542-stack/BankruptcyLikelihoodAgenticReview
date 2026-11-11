import glob, re, pandas as pd
txt = {f: re.sub(r'\s+',' ',open(f).read()) for f in glob.glob('filings/*.txt')}
quotes = ["will be sufficient to meet our liquidity requirements only into the fourth quarter of 2025",
"We have explored, and will continue to explore, whether filing for bankruptcy protection is in the best interest of our Company and our stakeholders.",
"we are engaged in business development discussions with potential counterparties concerning a commercialization agreement for our Fabry disease program, but have been unsuccessful in consummating any such transaction to date",
"management believes that substantial doubt exists about the Company’s ability to continue as a going concern",
"only into the middle of the second quarter of 2025","early into the third quarter","up to $1.4 billion","as early as the first quarter of 2026",
"has stated that substantial doubt exists about the Company’s ability to continue as a going concern","until October 27, 2025","Approximately $168.8 million remained available",
"$220.0 million in remaining milestone payments"]
for q in quotes:
    hits=[f.split('/')[-1][:20] for f,t in txt.items() if q in t]
    print('OK ' if hits else 'MISSING', q[:60], hits)
df=pd.read_csv('../../shared/financials.csv'); df=df[df.filed<=20250807]
print('latest row filed', df.filed.max())
import subprocess
fl=subprocess.run(['/opt/anaconda3/bin/python','../../sec_tools.py','filings','1001233','20250807'],capture_output=True,text=True,cwd='.').stdout
used=['0001628280-25-038860','0001628280-25-024650','0001628280-25-013088','0001628280-25-031559','0001628280-25-022664','0001628280-24-052579','0001628280-24-019337']
for a in used:
    line=[l for l in fl.splitlines() if a in l]; print(a, line[0][:22] if line else 'not in list (this report; filed 2025-08-07)')
w=open('report.md').read(); print('words', len(re.findall(r'\S+', w)))
# recompute key numbers
print('assets drop', 1-97.558/562.509, 'opex', 72.226, 89.447, 'cash+ATM', 38.344+8.9)
