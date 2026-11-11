import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
df=pd.read_csv('shared/financials.csv',dtype={'adsh':str})
df=df[df.filed<=20230818]                      # drop anything filed after the report date
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
me=df[df.adsh=='0001653247-23-000057'].iloc[0]
# year-before (Q2 2022 10-Q, in $ thousands, 6M flows annualized x2) from filing 0001653247-22-000126
yb=dict(total_assets=154508e3,current_assets=38025e3,current_liabilities=32512e3,total_liabilities=96890e3,
        revenue=66211e3*2,net_income=-88887e3*2,operating_income=-82755e3*2,operating_cash_flow=-13829e3*2)
# peers: SIC 73xx, latest report with period end 2023-03-31..2023-06-30, excluding company
p=df[(df.sic//100==73)&(df.cik!=1653247)&(df.ddate.between(20230331,20230630))]
p=p.sort_values('filed').groupby('cik').tail(1)
print('peers',len(p))
def pct(s,v): s=s.dropna(); return round(100*(s<v).mean(),1), len(s)
rows=[]
for c in cols:
    v=me[c]; pr=pct(p[c],v)
    sh = v/me.total_assets if c in cols[:4] else v/me.revenue
    ps = (p[c]/p.total_assets) if c in cols[:4] else (p[c]/p.revenue.where(p.revenue>0))
    rows.append([c,v/1e6,yb[c]/1e6,(v/yb[c]-1)*100,pr[0],p[c].median()/1e6,round(sh,3),pct(ps.replace([np.inf,-np.inf],np.nan),sh)[0],round(ps.median(),3)])
t=pd.DataFrame(rows,columns=['item','this_$m','yr_before_$m','chg%','peer_pctile_$','peer_median_$m','share','peer_pctile_share','peer_median_share'])
print(t.round(2).to_string())
# ratios
print('leverage TL/TA', me.total_liabilities/me.total_assets, 'peer median', (p.total_liabilities/p.total_assets).median(), 'pctile',pct(p.total_liabilities/p.total_assets,me.total_liabilities/me.total_assets))
print('current ratio', me.current_assets/me.current_liabilities, 'peer median', (p.current_assets/p.current_liabilities).median(),'pctile',pct(p.current_assets/p.current_liabilities,me.current_assets/me.current_liabilities))
print('equity $m', (me.total_assets-me.total_liabilities)/1e6)
cash=5066; ocf6=-5727; ocfq1=-4824; ocfq2=ocf6-ocfq1
print('Q2 OCF',ocfq2,'monthly 6M burn',ocf6/6,'months cash 6M',cash/(-ocf6/6),'months cash Q2',cash/(-ocfq2/3))
print('FY22 burn months', 12066/(28716/12))
print('debt 56355 / cash', 56355/cash)
# adjusted (cash-flow non-cash addbacks), same items each period
adj={'FY2022':(-206789, 2323+9499+5703+288+13296+121088+32957+1358-1939-103),
     'FY2021':(-5229, 2258+7974+158+12429+186+964-16715+253-111),
     '6M2022':(-88887, 577+930+3250-88+6065+67190+629+104-58),
     '6M2023':(-20420, 1835+2407-22+878+9536+783-35)}
for k,(nl,a) in adj.items(): print(k,'net loss',nl,'non-cash',a,'adjusted',nl+a)
print('revenue Q2 vs Q2', 13951/31171-1, 'ADO', 6559/18070-1)
print('company rows'); print(df[df.cik==1653247][['form','ddate','filed']+cols].to_string())
p.to_csv('final_cases-1/0001653247-23-000057/scripts/peers.csv',index=False)
