import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
df=pd.read_csv('../../shared/financials.csv',dtype={'adsh':str}); df=df[df.filed<=20250331]
assert df.filed.max()<=20250331
me=df[df.adsh=='0001828811-25-000009'].iloc[0]; prev=df[df.adsh=='0001628280-24-011518'].iloc[0]
m=lambda x:x/1e6
print('leverage TL/TA %.3f prev %.3f'%(me.total_liabilities/me.total_assets, prev.total_liabilities/prev.total_assets))
print('equity %.1f'%m(me.total_assets-me.total_liabilities))
print('current ratio %.3f prev %.3f'%(me.current_assets/me.current_liabilities, prev.current_assets/prev.current_liabilities))
print('NI/rev %.2f'%(me.net_income/me.revenue))
# from filings (millions): cash flow statements
cash_unres=22.6; restricted=9.3; jan_raise=17.3; covenant=10.0
ocf={'Q1':-29.1,'H1':-72.0,'9M':-92.5,'FY':-106.4}; capex={'Q1':-6.2,'H1':-15.4,'9M':-20.6,'FY':-23.9}
q4_ocf=ocf['FY']-ocf['9M']; q4_capex=capex['FY']-capex['9M']
q_ocf=[ocf['Q1'],ocf['H1']-ocf['Q1'],ocf['9M']-ocf['H1'],q4_ocf]; print('quarterly OCF',[round(x,1) for x in q_ocf])
q4_burn=-(q4_ocf+q4_capex); fy_burn=-(ocf['FY']+capex['FY'])
print('Q4 burn %.1f (%.2f/mo); FY burn %.1f (%.2f/mo)'%(q4_burn,q4_burn/3,fy_burn,fy_burn/12))
for lbl,c in [('unrestricted cash only',cash_unres),('cash + Jan-2025 gross raise',cash_unres+jan_raise),('headroom above $10M covenant',cash_unres+jan_raise-covenant)]:
    print('%s %.1f -> months at Q4 rate %.1f, at FY rate %.1f'%(lbl,c,c/(q4_burn/3),c/(fy_burn/12)))
# non-cash adjustment same both years: pre-working-capital cash result from CF statement
adj={'2024':(-137.7,-102.5),'2023':(-138.0,-117.9)}
for y,(ni,pre) in adj.items(): print(y,'net loss',ni,'cash loss before WC',pre,'net non-cash addback %.1f'%(pre-ni))
print('2024 ex fair-value gain: %.1f'%(-137.7-105.1))
# chart 1 cash path
plt.figure(figsize=(7,4))
d=['Dec-23','Mar-24','Jun-24','Sep-24','Dec-24']; c=[70.6+9.7,109.1+9.6,57.0+9.6,32.2+9.9,22.6+9.3]; u=[70.6,109.1,57.0,32.2,22.6]
plt.bar(d,u,color='tab:blue',label='Unrestricted cash'); plt.bar(d,np.array(c)-np.array(u),bottom=u,color='lightgray',label='Restricted cash')
plt.axhline(10,color='red',ls='--',label='$10M Glencore minimum liquidity')
plt.annotate('+$75M Glencore note',(1,119),ha='center',va='bottom',fontsize=8)
plt.ylabel('$ millions'); plt.ylim(0,135); plt.title(r'Cash fell from \$119M to \$32M over the last nine months of 2024'); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig('charts/cash_path.png',dpi=120)
# chart 2 loss composition
plt.figure(figsize=(7,4)); x=np.arange(2); w=0.25
plt.bar(x-w,[-138.0,-137.7],w,label='Net loss (model input)'); plt.bar(x,[-162.6,-125.5],w,label='Operating loss')
plt.bar(x+w,[-117.9,-102.5],w,label='Cash loss before working capital')
plt.xticks(x,['FY2023','FY2024']); plt.axhline(0,color='k',lw=.8); plt.ylabel('$ millions')
plt.title(r'Losses persist in cash terms; FY2024 net loss includes a \$105M non-cash gain',fontsize=10); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig('charts/loss_composition.png',dpi=120)
# chart 3 peer percentile
p=df[(df.sic//100==49)&(df.cik!=1828811)&(df.ddate>=20240701)&(df.ddate<=20241231)].sort_values('filed').groupby('cik').tail(1)
r={'Net income / assets':lambda d:d.net_income/d.total_assets,'Op. cash flow / assets':lambda d:d.operating_cash_flow/d.total_assets,'Revenue / assets':lambda d:d.revenue/d.total_assets,'Current ratio':lambda d:d.current_assets/d.current_liabilities,'Equity / assets':lambda d:1-d.total_liabilities/d.total_assets,'Total assets ($)':lambda d:d.total_assets}
names=[];pcts=[]
for k,f in r.items():
    s=f(p).replace([np.inf,-np.inf],np.nan).dropna(); v=f(me); names.append(k); pcts.append((s<v).mean()*100); print(k,'pct',round(pcts[-1]),'n',len(s))
plt.figure(figsize=(7,4)); plt.barh(names,pcts,color=['tab:red' if q<15 else 'tab:gray' for q in pcts]); plt.axvline(50,color='k',ls=':')
plt.xlim(0,100); plt.xlabel('Percentile among %d SIC-49 peers (0 = worst/smallest)'%len(p)); plt.title('Li-Cycle is bottom-decile on profit and cash, not on size or leverage',fontsize=10)
plt.tight_layout(); plt.savefig('charts/peer_percentiles.png',dpi=120)
