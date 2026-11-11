import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
B='final_cases/0001213900-23-087187/'
d=pd.read_csv('shared/financials.csv',dtype={'adsh':str}); d=d[d.filed<=20231115]
c=d[d.cik==1357671].sort_values('ddate').set_index('ddate')
cur=c.loc[20230930]; prev=c.loc[20221231]
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
print(pd.DataFrame({'Q3_23':cur[cols],'FY22':prev[cols],'chg%':(cur[cols]/prev[cols]-1)*100}).round(1).to_string())
print('lev',cur.total_liabilities/cur.total_assets, 'prev',prev.total_liabilities/prev.total_assets)
print('CR',cur.current_assets/cur.current_liabilities,'prev',prev.current_assets/prev.current_liabilities)
print('equity',cur.total_assets-cur.total_liabilities)
# quarterly from filings (YTD statements of cash flow)
cash={'2022-12':706224,'2023-03':172052,'2023-06':104201,'2023-09':6759}
ytd_ocf={'Q1':-2858058,'H1':-3190572,'9M':-3384288}; ytd_ap={'Q1':3605990,'H1':5056145,'9M':5901097}
q_ocf=[ytd_ocf['Q1'],ytd_ocf['H1']-ytd_ocf['Q1'],ytd_ocf['9M']-ytd_ocf['H1']]
q_ap=[ytd_ap['Q1'],ytd_ap['H1']-ytd_ap['Q1'],ytd_ap['9M']-ytd_ap['H1']]
print('quarterly OCF',q_ocf,'AP increase',q_ap,'OCF excl AP build',[o-a for o,a in zip(q_ocf,q_ap)])
print('annualized OCF check 9M*4/3',ytd_ocf['9M']*4/3,'csv',cur.operating_cash_flow)
m9=-ytd_ocf['9M']/9; m3=-q_ocf[2]/3
print('monthly burn 9M',m9,'months cash',6759/m9,'| Q3 burn',m3,'months',6759/m3)
print('monthly burn excl AP build Q3',-(q_ocf[2]-q_ap[2])/3,'months',6759/(-(q_ocf[2]-q_ap[2])/3))
# consistent non-cash adjustment (all non-working-capital reconciling items in each cash flow statement)
nc={'FY2021':(-37379153,[397440,589461,1038905,688127,3612669,9661174,110805,-1304677,-59692,1096287,100502,82511,-123710,16413]),
    'FY2022':(-35676315,[586109,50000,1433815,2043011,101623,4668039,4183844,40994,398130,832482,265717,-3729,11742,274784,399058]),
    '9M2022':(-25112331,[441943,50000,257117,2531687,3848578,124186,832482,2867,-3729,11646,44305]),
    '9M2023':(-23340137,[118581,4346584,8283267,302005,25198,-25855,51535])}
for k,(nl,a) in nc.items(): print(k,'net loss',nl,'non-cash',sum(a),'share',round(sum(a)/-nl*100,1),'cash loss',nl+sum(a))
print('defaulted note principal (notes table *):',198577+24124+34500+14450+498625+45055+13000)
print('convertible principal total',6096192,'Dec22+Jan23+Feb23 debentures',250000+847500+1387500)
print('Q3 rev',437855,'vs Q3 22',1022851,(437855/1022851-1)*100)
print('AP growth since Dec',13440962-7565720)
# charts
p=pd.read_csv(B+'scripts/peers.csv')
fig,ax=plt.subplots(figsize=(7,4))
x=list(cash.keys()); cl=[c.loc[20221231].current_liabilities,c.loc[20230331].current_liabilities,c.loc[20230630].current_liabilities,c.loc[20230930].current_liabilities]
ax.bar(np.arange(4)-0.2,[v/1e6 for v in cl],0.4,label='Current liabilities',color='tab:red')
ax.bar(np.arange(4)+0.2,[v/1e6 for v in cash.values()],0.4,label='Cash',color='tab:blue')
for i,v in enumerate(cash.values()): ax.text(i+0.2,0.3,f'${v:,.0f}',ha='center',fontsize=8,rotation=90,va='bottom')
ax.set_xticks(range(4)); ax.set_xticklabels(x); ax.set_ylabel('$ millions'); ax.legend()
ax.set_title(r'Cash fell to \$6,759 while current liabilities rose to \$21.7M'); plt.tight_layout(); plt.savefig(B+'charts/cash_vs_cl.png',dpi=120); plt.close()
fig,ax=plt.subplots(figsize=(7,4)); q=['Q1 2023','Q2 2023','Q3 2023']
ax.bar(np.arange(3)-0.2,[v/1e6 for v in q_ocf],0.4,label='Reported operating cash flow')
ax.bar(np.arange(3)+0.2,[(o-a)/1e6 for o,a in zip(q_ocf,q_ap)],0.4,label='Same, without the rise in unpaid payables/accruals',color='tab:orange')
ax.axhline(0,color='k',lw=.8); ax.set_xticks(range(3)); ax.set_xticklabels(q); ax.set_ylabel('$ millions'); ax.legend(fontsize=8)
ax.set_title('Cash burn looks small partly because bills went unpaid'); plt.tight_layout(); plt.savefig(B+'charts/burn_vs_ap.png',dpi=120); plt.close()
p=p[p.total_assets>0].copy(); p['lev']=p.total_liabilities/p.total_assets; p['roa']=p.net_income/p.total_assets
fig,ax=plt.subplots(figsize=(7,4.5))
ax.scatter(p.lev,p.roa,color='grey',label='SIC 78 peers (latest report, period end Jun-Sep 2023)')
ax.scatter([cur.total_liabilities/cur.total_assets],[cur.net_income/cur.total_assets],color='red',s=80,label='Creatd Q3 2023')
ax.set_xscale('symlog',linthresh=1); ax.set_yscale('symlog',linthresh=1)
ax.set_xlabel('Total liabilities / total assets (symlog)'); ax.set_ylabel('Annualized net income / total assets (symlog)')
ax.axvline(1,ls='--',color='k',lw=.7); ax.axhline(0,color='k',lw=.7); ax.legend(fontsize=8)
ax.set_yticks([-10,-1,0,1]); ax.set_yticklabels(['-10','-1','0','1']); ax.set_xticks([0.1,1,10,100]); ax.set_xticklabels(['0.1','1','10','100'])
ax.set_title('Creatd sits with the tiny shells: liabilities 8x assets, loss 11x assets',fontsize=10); plt.tight_layout(); plt.savefig(B+'charts/peers.png',dpi=120); plt.close()
print('peers plotted',len(p), 'peer lev>8:',(p.lev>8.16).sum(),'roa<-10.7:',(p.roa<-10.73).sum())
print(p.sort_values('roa')[['name','lev','roa']].head(5))
