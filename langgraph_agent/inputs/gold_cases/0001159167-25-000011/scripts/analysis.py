import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
C='final_cases/0001159167-25-000011/charts/'
df=pd.read_csv('shared/financials.csv',dtype={'adsh':str}); df=df[df.filed<=20250312]
print('max filed used', df.filed.max())
me=df[df.adsh=='0001159167-25-000011'].iloc[0]; prev=df[df.adsh=='0001159167-24-000008'].iloc[0]
v=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
p=df[(df.sic//100==36)&(df.cik!=1159167)&(df.ddate>=20240630)&(df.ddate<=20250131)].sort_values('filed').groupby('cik').tail(1)
ps=p[(p.total_assets>=250e6)&(p.total_assets<=1.5e9)]
print('peers all',len(p),'size-matched',len(ps))
def rk(s,x): s=s.replace([np.inf,-np.inf],np.nan).dropna(); return (s<x).mean()*100, s.median(), len(s)
for c in v:
    a=rk(p[c],me[c]); b=rk(ps[c],me[c]); ch=(me[c]/prev[c]-1)*100
    print(f"{c:20s} FY24={me[c]/1e6:8.1f} FY23={prev[c]/1e6:8.1f} chg={ch:6.1f}% | all pct={a[0]:5.1f} med={a[1]/1e6:7.1f} | size pct={b[0]:5.1f} med={b[1]/1e6:7.1f} n={b[2]}")
R={'ni_ta':lambda x:x.net_income/x.total_assets,'tl_ta':lambda x:x.total_liabilities/x.total_assets,'cur':lambda x:x.current_assets/x.current_liabilities,
   'ocf_ta':lambda x:x.operating_cash_flow/x.total_assets,'ni_rev':lambda x:x.net_income/x.revenue,'oi_rev':lambda x:x.operating_income/x.revenue}
for k,f in R.items():
    a=rk(f(p),f(me)); b=rk(f(ps),f(me))
    print(f"{k:7s} me={f(me):7.3f} | all pct={a[0]:5.1f} med={a[1]:6.3f} | size pct={b[0]:5.1f} med={b[1]:6.3f}")
# cash-adjusted loss: NI + non-cash items from cash flow statement (10-K FY2024, $k)
cf={2022:dict(ni=-286295,da=47869,eq=19718,sbc=31905,inv=2888,fv=0,dic=0,dt=18799,oth=-1003,ocf=-90021),
    2023:dict(ni=-304710,da=32791,eq=3910,sbc=36056,inv=6378,fv=5904,dic=11837,dt=6563,oth=-17694,ocf=-114793),
    2024:dict(ni=-145518,da=21667,eq=370,sbc=24476,inv=13489,fv=24557,dic=583,dt=-2391,oth=-4140,ocf=-33222)}
adj={}
for y,d in cf.items():
    nc=sum(d[k] for k in ['da','eq','sbc','inv','fv','dic','dt','oth']); adj[y]=d['ni']+nc
    print(y,'noncash',nc/1e3,'cash-adj loss',adj[y]/1e3,'wc',(d['ocf']-adj[y])/1e3)
oneoff=75.2+13.5
print('2024 cash-adj loss ex one-offs', adj[2024]/1e3-oneoff)
# liquidity
cash=134.303; rc=1.259; ar=49.865; inv=76.029
print('equity',me.total_assets/1e6-me.total_liabilities/1e6,'TL/TA',me.total_liabilities/me.total_assets,'cur',me.current_assets/me.current_liabilities)
print('core assets',cash+ar+inv,'(+rc',cash+rc+ar+inv,') headroom vs 200:',cash+ar+inv-200)
q4=-33.222-(-30.476); print('Q4 OCF',q4,'Q3 OCF',-30.476-(-20.233),'Q2',-20.233-1.4,'Q1',1.4)
print('cash+rc Q3',99.447+41.082,'Q4',cash+rc,'chg',cash+rc-(99.447+41.082))
cash_after=cash-40; print('unrestricted after returning 40M',cash_after)
for lbl,burn in [('FY24 OCF',33.222),('FY24 OCF ex net Amazon fee',33.222+75.2),('Q4 OCF x4',-q4*4),('Q2+Q3 avg x4',( (21.633+10.243)/2)*4)]:
    print(f"{lbl}: burn/yr={burn:.1f} months on 134.3={cash/burn*12:.1f} months on 94.3={cash_after/burn*12:.1f}")
print('term loan payments 1-3y',248.344,'<1y interest',19.980,'vs cash',cash)
# charts
h=df[df.cik==1159167].sort_values('ddate'); hk=h[h.form=='10-K']
fig,ax=plt.subplots(figsize=(7,4)); yrs=[2022,2023,2024]; x=np.arange(3); w=0.25
ax.bar(x-w,[cf[y]['ni']/1e3 for y in yrs],w,label='Net loss (model input)',color='firebrick')
ax.bar(x,[adj[y]/1e3 for y in yrs],w,label='Loss after adding back non-cash items',color='darkorange')
ax.bar(x+w,[adj[2022]/1e3,adj[2023]/1e3,adj[2024]/1e3-oneoff],w,label='...and excluding 2024 one-off gains ($88.7M)',color='grey')
ax.axhline(0,color='k',lw=.8); ax.set_xticks(x,[f'FY{y}' for y in yrs]); ax.set_ylabel('$ millions')
ax.set_title('iRobot: smaller loss in 2024, but underlying cash loss barely improved'); ax.legend(fontsize=8,loc='lower right'); plt.tight_layout(); plt.savefig(C+'loss_adjusted.png',dpi=120); plt.close()
fig,ax=plt.subplots(figsize=(7,4))
lab=['Cash\n(Dec 28, 2024)','Cash after\nreturning $40M\n(Mar 2025)','Core assets\n(cash+AR+inventory)','Term loan due\nJul 2026 (principal +\nmin. return, 10-K table)']
val=[cash,cash_after,cash+ar+inv,248.344]; col=['steelblue','steelblue','teal','firebrick']
ax.bar(lab,val,color=col); ax.axhline(200,ls='--',color='k'); ax.text(0.5,205,'$200M minimum core-assets covenant',fontsize=8)
for i,vv in enumerate(val): ax.text(i,vv+3,f'${vv:.0f}M',ha='center',fontsize=9)
ax.set_ylabel('$ millions'); ax.set_title('Cash cannot cover the 2026 term loan; covenant headroom ~$60M'); plt.xticks(fontsize=8); plt.tight_layout(); plt.savefig(C+'cash_vs_debt.png',dpi=120); plt.close()
fig,ax=plt.subplots(figsize=(7,4.5))
xx=R['tl_ta'](ps); yy=R['ni_ta'](ps); m=(xx<2)&(yy>-1)
ax.scatter(xx[m],yy[m],s=12,alpha=.5,label=f'SIC 36 peers, assets \\$250M-\\$1.5B (n={m.sum()})')
ax.scatter([R['tl_ta'](me)],[R['ni_ta'](me)],color='red',s=80,label='iRobot FY2024'); ax.scatter([R['tl_ta'](prev)],[R['ni_ta'](prev)],color='orange',s=60,marker='s',label='iRobot FY2023')
ax.axhline(0,color='k',lw=.6); ax.set_xlabel('Total liabilities / total assets'); ax.set_ylabel('Net income / total assets')
ax.set_title('iRobot sits in the high-leverage, deep-loss corner of its peers'); ax.legend(fontsize=8); plt.tight_layout(); plt.savefig(C+'peer_scatter.png',dpi=120); plt.close()
print('scatter excluded',(~m).sum())
