import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
B='final_cases-1/0001159167-25-000011/'
d=pd.read_csv('shared/financials.csv',dtype={'adsh':str}); d=d[d.filed<=20250312]
c=d[d.cik==1159167].sort_values('filed').set_index('ddate')
M=1e6
# --- quarterly values de-annualized from YTD (10-Q rows are YTD x 4/n)
def q(col,yr):
    f={1:1/4,2:2/4,3:3/4}
    ytd=[c.loc[int(f'{yr}{m}'),col]*f[i] for i,m in [(1,'0331'),(2,'0630'),(3,'0930')]]+[c.loc[int(f'{yr}1231'),col]]
    return np.diff([0]+ytd)/M
qs={col:{yr:q(col,yr) for yr in (2023,2024)} for col in ['revenue','net_income','operating_income','operating_cash_flow']}
for col in qs: print(col, {k:np.round(v,1).tolist() for k,v in qs[col].items()})
# --- ratios by year
for y in (20221231,20231231,20241231):
    r=c.loc[y]; print(y,'liab/assets %.3f'%(r.total_liabilities/r.total_assets),'CR %.2f'%(r.current_assets/r.current_liabilities),
      'NI/rev %.3f'%(r.net_income/r.revenue),'OCF %.1f'%(r.operating_cash_flow/M),'rev chg %.1f%%'%0)
print('rev change 24 vs 23 %.1f%%'%((c.loc[20241231].revenue/c.loc[20231231].revenue-1)*100))
for col in ['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']:
    print(col, round(c.loc[20231231,col]/M,1), round(c.loc[20241231,col]/M,1), '%+.1f%%'%((c.loc[20241231,col]/c.loc[20231231,col]-1)*100))
# --- cash loss: net income + non-cash items from cash flow statement (10-K FY2024, same lines each year)
noncash={2024:[21.667,.370,24.476,13.489,24.557,.583,-2.391,-4.140],2023:[32.791,3.910,36.056,6.378,5.904,11.837,6.563,-17.694],
         2022:[47.869,19.718,31.905,2.888,0,0,18.799,-1.003]}
ni={2024:-145.518,2023:-304.710,2022:-286.295}
for y in ni: print(y,'noncash %.1f'%sum(noncash[y]),'cash loss %.1f'%(ni[y]+sum(noncash[y])))
fee_net=94.0-18.8
print('2024 NI ex Amazon fee net of deal fees %.1f'%(ni[2024]-fee_net), ' cash loss ex fee %.1f'%(ni[2024]+sum(noncash[2024])-fee_net))
print('2024 OCF ex fee %.1f'%(-33.222-fee_net))
# --- months of cash
cash=134.303; pf=cash-40.0
for lab,burn in [('FY24 OCF',33.222),('FY24 OCF ex fee',33.222+fee_net),('Q4 OCF x4',-qs['operating_cash_flow'][2024][3]*4),('Q3 OCF x4',-qs['operating_cash_flow'][2024][2]*4)]:
    print(f'{lab}: burn {burn:.1f}/yr -> months on 134.3: {cash/burn*12:.1f}; on pro forma 94.3: {pf/burn*12:.1f}')
core={'2023-12':185.121+79.387+152.469,'2024-03':118.356+39.318+133.318,'2024-06':108.513+68.132+101.365,'2024-09':99.447+101.326+149.156,'2024-12':134.303+49.865+76.029}
print('core assets',{k:round(v,1) for k,v in core.items()})
print('tangible equity %.1f'%(61.239-167.288-3.212), 'goodwill share of assets %.3f'%(167.288/516.137))
print('Term loan due 1-3y 248.3 vs cash 134.3 ratio %.2f'%(248.344/134.303))
# ---------------- charts
fig,ax=plt.subplots(figsize=(8,4)); lab=['Q1-23','Q2-23','Q3-23','Q4-23','Q1-24','Q2-24','Q3-24','Q4-24']
rev=np.r_[qs['revenue'][2023],qs['revenue'][2024]]; oi=np.r_[qs['operating_income'][2023],qs['operating_income'][2024]]
x=np.arange(8); ax.bar(x-0.2,rev,0.4,label='Revenue'); ax.bar(x+0.2,oi,0.4,label='Operating income',color='tab:red')
ax.axhline(0,color='k',lw=.8); ax.set_xticks(x); ax.set_xticklabels(lab); ax.set_ylabel('$ million (single quarter)')
ax.annotate('Q1-24 includes $94M\nAmazon termination fee',(4.2,oi[4]),(4.6,200),arrowprops=dict(arrowstyle='->'),fontsize=8)
ax.set_title('Holiday quarter collapsed: Q4-24 revenue %.0f vs %.0f a year earlier'%(rev[7],rev[3])); ax.legend(); fig.tight_layout(); fig.savefig(B+'charts/1_quarterly.png',dpi=120)
fig,ax=plt.subplots(figsize=(8,4)); k=list(core); ax.plot(k,list(core.values()),'o-',label='Core assets (cash+receivables+inventory)')
ax.plot(k,[185.121,118.356,108.513,99.447,134.303],'s-',label='Unrestricted cash'); ax.axhline(200,color='r',ls='--',label='Covenant floor $200M')
ax.axhline(248.344,color='purple',ls=':',label='Term loan payments due in 1-3 yrs ($248M)')
ax.set_ylim(0,450); ax.set_ylabel('$ million'); ax.set_title('Covenant headroom shrinking; loan due July 2026 exceeds cash'); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(B+'charts/2_covenant.png',dpi=120)
fig,ax=plt.subplots(figsize=(8,4)); yrs=['FY2022','FY2023','FY2024','FY2024 ex net\nAmazon fee']
vals=[ni[2022],ni[2023],ni[2024],ni[2024]-fee_net]; cl=[ni[y]+sum(noncash[y]) for y in (2022,2023,2024)]+[ni[2024]+sum(noncash[2024])-fee_net]
x=np.arange(4); ax.bar(x-0.2,vals,0.4,label='Net income (reported)'); ax.bar(x+0.2,cl,0.4,label='Net income + non-cash items (cash loss)')
ax.axhline(0,color='k',lw=.8); ax.set_xticks(x); ax.set_xticklabels(yrs); ax.set_ylabel('$ million'); ax.legend()
ax.set_title('Loss is mostly cash; 2024 improvement is largely the one-off fee'); fig.tight_layout(); fig.savefig(B+'charts/3_cashloss.png',dpi=120)
