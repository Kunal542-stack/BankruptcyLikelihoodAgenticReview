import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
B='final_cases/0000950170-24-127060/'
df=pd.read_csv('shared/financials.csv'); df=df[df.filed<=20241114]
c=df[df.cik==1580063].sort_values('ddate')
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
t=c[c.adsh=='0000950170-24-127060'].iloc[0]; y=c[c.adsh=='0000950170-23-063022'].iloc[0]
p=df[(df.sic//100==28)&(df.cik!=1580063)&(df.ddate>=20240630)&(df.ddate<=20241031)].sort_values('filed').groupby('cik').tail(1)
print('peers n',len(p),'filed max',df.filed.max())
print('| item | Q3-24 $M | Q3-23 $M | /assets | peer median $M | pct below |')
for k in cols:
    s=p[k].dropna()
    print(k, round(t[k]/1e6,2), round(y[k]/1e6,2), round(t[k]/t.total_assets,2), round(s.median()/1e6,2), round((s<t[k]).mean()*100))
# ratios history
c=c.assign(lev=c.total_liabilities/c.total_assets, cr=c.current_assets/c.current_liabilities, eq=(c.total_assets-c.total_liabilities)/1e6)
print(c[['ddate','lev','cr','eq']].round(2).to_string())
# adjusted loss: net loss + non-cash items from cash flow statements ($K)
adj={'FY2022':-38157-10673+907+7804+2722+1419+543+545-20904-5731,
     'FY2023':-124115-219+555+16475+6363+1601+53198+15+100+3915-18004+3000,
     '9M2023':-108702+438+14929+53198+1126+12+100-5271,
     '9M2024':-16126-3816+326+4393+10890+3216+10-8669-35178}
print('cash-adjusted loss $K',adj)
# burn
ocf={'Q1-24':-12496,'Q2-24':-23448+12496,'Q3-24':-32178+23448}
print('quarterly OCF',ocf)
cash=3196; unr=3.0
q3=-ocf['Q3-24']/3; avg9=32178/9
print('monthly burn Q3',round(q3),'9M avg',round(avg9),'months left Q3',round(cash/q3,2),'9M',round(cash/avg9,2))
pro=cash+500+4000+3000*0.94-25
print('pro forma cash $K',pro,'months',round(pro/q3,2),'above 4.0M covenant',round((pro-4000)/q3,2))
print('lev',t.total_liabilities/t.total_assets,'CR',t.current_assets/t.current_liabilities,'pct lev>1 peers',((p.total_liabilities/p.total_assets)>1).mean())
print('notes face 58.3+4.6=',58.3+4.6,'vs cash 3.2 ->',round(62.9/3.2,1),'x')
print('interest Dec 1 approx 58.3*0.13/2=',round(58.3*.13/2,2))
# chart 1: cash vs current liabilities
q=c[c.ddate>=20221231]
lab=[str(d)[:4]+'-'+str(d)[4:6] for d in q.ddate]
cashs=[30486,None,None,None,15211,10820,5325,3196]
fig,ax=plt.subplots(figsize=(7,4))
ax.bar(np.arange(len(q))-0.2,q.current_liabilities/1e6,0.4,label='Current liabilities',color='indianred')
ax.bar(np.arange(len(q))+0.2,q.current_assets/1e6,0.4,label='Current assets',color='steelblue')
ax.set_xticks(range(len(q))); ax.set_xticklabels(lab,rotation=30); ax.set_ylabel('$ million')
ax.set_title('Biora: all notes moved to current at Sep-2024; current ratio 0.05'); ax.legend(); plt.tight_layout(); plt.savefig(B+'charts/1_current.png',dpi=120); plt.close()
# chart 2: cash and quarterly burn
fig,ax=plt.subplots(figsize=(7,4))
qs=['Dec-23','Mar-24','Jun-24','Sep-24']; cv=[15.211,10.820,5.325,3.196]
ax.plot(qs,cv,'o-',label='Cash incl. restricted ($M)',color='steelblue')
ax.bar(qs[1:],[-v/1000 for v in ocf.values()],alpha=0.4,color='indianred',label='Operating cash burn in quarter ($M)')
ax.axhline(4.0,ls='--',color='k'); ax.text(0.0,4.2,'$4.0M minimum-liquidity covenant',fontsize=8)
ax.set_ylim(0,17); ax.set_title('Cash at Sep-24 ($3.2M) is less than one quarter of burn'); ax.legend(fontsize=8); plt.tight_layout(); plt.savefig(B+'charts/2_cash.png',dpi=120); plt.close()
# chart 3: reported vs cash-adjusted loss
fig,ax=plt.subplots(figsize=(7,4))
names=['FY2022','FY2023','9M2023','9M2024']; rep=[-38157,-124115,-108702,-16126]
x=np.arange(4); ax.bar(x-0.2,np.array(rep)/1000,0.4,label='Reported net loss',color='grey')
ax.bar(x+0.2,np.array([adj[n] for n in names])/1000,0.4,label='Net loss excl. non-cash items',color='indianred')
ax.set_xticks(x); ax.set_xticklabels(names); ax.set_ylabel('$ million'); ax.axhline(0,color='k',lw=0.5)
ax.set_title('2024 net loss is small only because of $44M non-cash fair-value gains'); ax.legend(fontsize=8); plt.tight_layout(); plt.savefig(B+'charts/3_adjloss.png',dpi=120); plt.close()
# chart 4: leverage vs peers
lv=(p.total_liabilities/p.total_assets).clip(upper=10)
fig,ax=plt.subplots(figsize=(7,4)); ax.hist(lv.dropna(),bins=50,color='lightgrey',edgecolor='grey')
ax.axvline(t.total_liabilities/t.total_assets,color='red'); ax.text(t.total_liabilities/t.total_assets-2.6,ax.get_ylim()[1]*0.8,'Biora 8.35x',color='red')
ax.text(9.0,40,'peers >=10x',fontsize=8); ax.set_yscale('log'); ax.set_xlabel('Total liabilities / total assets (capped at 10)'); ax.set_ylabel('peer count (log)')
ax.set_title(f'Leverage vs {len(p)} SIC-28 peers, reports dated Jul-Oct 2024'); plt.tight_layout(); plt.savefig(B+'charts/4_leverage.png',dpi=120); plt.close()
