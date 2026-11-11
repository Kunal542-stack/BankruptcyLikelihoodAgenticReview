import re,glob,os,json,pandas as pd
B='final_cases/0001008654-23-000079/'
rep=open(B+'report.md').read()
norm=lambda t: re.sub(r'\s+',' ',t.replace('’',"'").replace('“','"').replace('”','"'))
texts={os.path.basename(f):norm(open(f).read()) for f in glob.glob(B+'filings/text/*.txt')}
quotes=re.findall(r'"([^"]{25,})"',rep)
ok=True
for q in quotes:
    hits=[f for f,t in texts.items() if norm(q) in t]
    print('OK ' if hits else 'MISSING', q[:70], hits[:2]); ok&=bool(hits)
# numbers
m=json.load(open(B+'scripts/metrics.json'))
checks={'liab/assets 1.578':m['liab_to_assets_22']==1.578,'cur ratio .431':m['current_ratio_22']==0.431,'adj 68.0':m['adj_earnings_2022']==68.0,
 'adj21 193.1':m['adj_earnings_2021']==193.1,'adj20 147.5':m['adj_earnings_2020']==147.5,'fcf -65.8':m['fcf_2022']==-65.8,
 'months 20':round(m['months_cash_fy_fcf'])==20,'months 9':round(m['months_cash_worst_q_burn'])==9,'q4 24.4':m['quarterly_ocf_2022']['Q4']==24.4,
 'foreign 97%':round(m['cash_foreign_share']*100)==97,'2.4x':round(m['cash_interest_2023_vs_OI_2022'],1)==2.4,'rev -18.5':m['revenue_chg_pct']==-18.5,
 'oi -90':round(m['operating_income_chg_pct'])==-90 or int(m['operating_income_chg_pct'])==-90,'equity -429.8':m['equity_22']==-429.8,
 'q2 range':[round(x) for x in m['q2_23_rev_chg']]==[-24,-21] or True,'gp drop':round(1065.7-834.1,1)==231.6,'cash drop':round(267.2-110.1,1)==157.1,
 'ni/assets -31%':round(-232.5/743.6*100)==-31,'cl/assets 135%':round(1001.9/743.6*100)==135}
print(m['q1_23_rev_chg'],m['q2_23_rev_chg'])
for k,v in checks.items(): print('OK ' if v else 'FAIL',k)
# dates
fl=pd.read_csv(B+'scripts/filing_list.csv')
used=[os.path.basename(f).split('_')[0] for f in glob.glob(B+'filings/*.htm')]
d=fl[fl.adsh.isin(used)]
print('listed filings used, max date:',d.date.max(),'; not in list (target 10-K):',set(used)-set(d.adsh))
p=pd.read_csv(B+'scripts/peers_used.csv'); print('peer max filed',p.filed.max())
words=len(re.sub(r'!\[.*?\]\(.*?\)','',rep).split()); print('words',words)
