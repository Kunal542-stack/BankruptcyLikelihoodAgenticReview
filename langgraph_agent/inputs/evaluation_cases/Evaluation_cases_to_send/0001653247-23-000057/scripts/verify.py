import re,glob,os
B='final_cases-1/0001653247-23-000057/'
rep=open(B+'report.md').read()
txt={os.path.basename(f):re.sub(r'\s+',' ',open(f).read()) for f in glob.glob(B+'filings/text/*.txt')}
allt=' '.join(txt.values())
quotes=["As of June 30, 2023, the Company has outstanding debt in the principal amount of $56,355 with a maturity date of May 15, 2024.",
"We believe that we have sufficient cash on hand to fund operations through at least the third fiscal quarter of 2023.",
"commencing a case under the U.S. Bankruptcy Code","substantial doubt",
"Management concluded that there were indicators of financial difficulty for the Company at this date.",
"PIK one hundred percent of the accrued interest",
"had determined that the Company’s common stock will be delisted from the Nasdaq Capital Market",
"The Company does not anticipate utilizing its ATM Program in fiscal 2023.",
"Jonathan Green, a board member of the Company, is a partner at Luxor Capital.",
"Uber Direct will provide the delivery services for the Company’s online ordering of food and other items",
"Waitr Inc. has made a $20 million prepayment with respect to the term loan",
"waive the requirement for the audit report to be unqualified as to going concern",
"Not applicable"]
for q in quotes:
    hits=[k for k,v in txt.items() if q in v]
    print('OK ' if hits else 'MISSING', q[:60], hits[:2])
    assert q in rep or q=='substantial doubt', q
# numbers
print('cash/debt',56355/5066,'TL/TA',80338/25374,'CR',12584/78638,'CL/CA',78638/12584,'margin',-40840/61310)
print('rev y/y',13951/31171-1,'ADO',6559/18070-1,'Q2 OCF',-5727+4824,'months 6M',5066/(5727/6),'months Q2',5066/(903/3))
print('impair FY22',121088+32957,'cash drop',1-5066/60111)
# links and dates
links=re.findall(r'\((https?://[^)]+|\.\./[^)]+|charts/[^)]+)\)',rep)
for l in sorted(set(links)):
    if l.startswith('http'):
        m=re.search(r'/(\d{10})(\d{2})(\d{6})/',l); print(l.split('/')[-2], 'filer',m.group(1))
    else: print(l, os.path.exists(os.path.normpath(os.path.join(B,l))))
import subprocess
out=subprocess.run(['/opt/anaconda3/bin/python','sec_tools.py','filings','1653247','20230818'],capture_output=True,text=True).stdout
dates={l.split(',')[2]:l.split(',')[0] for l in out.splitlines()[1:] if l.count(',')>=3}
for a in sorted(set(re.findall(r'/(\d{18})/',rep))):
    adsh=f'{a[:10]}-{a[10:12]}-{a[12:]}'; print(adsh, dates.get(adsh,'(this report, filed 2023-08-18)'))
print('words',len(rep.split()))
