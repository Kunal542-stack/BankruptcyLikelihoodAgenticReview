import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
C='final_cases/0001083301-25-000061/'
df=pd.read_csv('shared/financials.csv'); df=df[df.filed<=20250808].copy()
assert df.filed.max()<=20250808
cols=['total_assets','current_assets','current_liabilities','total_liabilities','revenue','net_income','operating_income','operating_cash_flow']
co=df[df.cik==1083301].sort_values('ddate')
me=co[co.adsh=='0001083301-25-000061'].iloc[0]; py=co[co.adsh=='0001083301-24-000124'].iloc[0]
df['sic2']=df.sic//100
peers=df[(df.sic2==61)&(df.cik!=1083301)&(df.ddate>=20250101)&(df.ddate<=20250930)].sort_values('filed').groupby('cik').tail(1)
for c in cols:
    base='total_assets' if c in cols[:4] else 'revenue'
    s=peers[c].dropna(); r=(peers[c]/peers[base]).replace([np.inf,-np.inf],np.nan).dropna()
    v=me[c]/me[base]
    print(f"{c:20s} now {me[c]/1e6:8.1f} prior {py[c]/1e6:8.1f} | $pctile {(s<me[c]).mean()*100:4.0f} (n={len(s)}) | ratio {v:6.2f} pctile {(r<v).mean()*100:4.0f} peer med {r.median():.2f}")
r=(peers.net_income/peers.total_assets).dropna(); v=me.net_income/me.total_assets
print('NI/TA',round(v,3),'pctile',round((r<v).mean()*100),'median',round(r.median(),3))
# Chart 1: quarterly net loss split: SBC vs other, showing annualization effect
q=pd.DataFrame({'q':['Q1 25','Q2 25'],'ni':[-61.418,-18.370],'sbc':[38.674,1.304],'dep':[15.574,18.786]})
fig,ax=plt.subplots(figsize=(7,4))
x=np.arange(2); w=0.27
ax.bar(x-w,-q.ni,w,color='grey',label='Net loss (reported)')
ax.bar(x,q.sbc,w,color='tab:red',label='Stock comp (non-cash)')
ax.bar(x+w,q.dep,w,color='tab:orange',label='Depreciation (non-cash)')
for i in range(2):
    for dx,val in [(-w,-q.ni[i]),(0,q.sbc[i]),(w,q.dep[i])]: ax.text(i+dx,val+1,f"{val:.1f}",ha='center',fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(q.q); ax.set_ylabel('$ millions')
ax.set_title('Q1 2025 loss was mostly a one-off stock-comp charge;\nannualizing H1 (x2) feeds the model a -159.6M net income')
ax.legend(fontsize=8); plt.tight_layout(); plt.savefig(C+'charts/1_loss_composition.png',dpi=120); plt.close()
# Chart 2: cash vs capex by quarter (from filings)
d=pd.DataFrame({'p':['Dec 24','Mar 25','Jun 25'],'cash':[274.1,218.2,91.4]})
fig,ax=plt.subplots(figsize=(7,4))
ax.plot(d.p,d.cash,marker='o',label='Cash + restricted cash')
ax.bar(['Mar 25','Jun 25'],[93.7,119.9],alpha=0.4,color='tab:red',label='Capex in quarter')
ax.bar(['Mar 25','Jun 25'],[-0.9,-5.1],alpha=0.8,color='tab:green',label='Operating cash incl. BTC sales, ex prepaid rent')
ax.axhline(0,color='k',lw=0.6); ax.set_ylabel('$ millions')
ax.set_title('Cash fell mainly on HPC capex (plus Q1 buybacks):\n90M left at June 30 vs ~120M capex in Q2 ($ millions)')
ax.legend(fontsize=8); plt.tight_layout(); plt.savefig(C+'charts/2_cash_vs_capex.png',dpi=120); plt.close()
# Chart 3: NI/TA vs miner peers
names=['APPLIED DIGITAL CORP.','BIT DIGITAL, INC','CIPHER MINING INC.','CLEANSPARK, INC.','CORE SCIENTIFIC, INC./TX','GREENIDGE GENERATION HOLDINGS INC.','GRYPHON DIGITAL MINING, INC.','HUT 8 CORP.','MARA HOLDINGS, INC.','MAWSON INFRASTRUCTURE GROUP INC.','RIOT PLATFORMS, INC.','SOLUNA HOLDINGS, INC','SPHERE 3D CORP.','BITMINE IMMERSION TECHNOLOGIES, INC.']
m=df[df.name.isin(names)].sort_values('filed').groupby('cik').tail(1)
m=pd.concat([m,df[df.adsh=='0001083301-25-000061']])
m['x']=m.net_income/m.total_assets; m=m.sort_values('x')
m['lab']=m.name.str.replace(r',? ?(INC\.?|CORP\.?|HOLDINGS|GROUP|TECHNOLOGIES|PLATFORMS|\/TX)','',regex=True).str.strip(' ,').str.title()
fig,ax=plt.subplots(figsize=(7,5))
cl=['tab:red' if n=='TERAWULF INC.' else 'grey' for n in m.name]
ax.barh(m.lab,m.x.clip(lower=-1),color=cl); ax.axvline(0,color='k',lw=0.6)
ax.set_xlabel('Annualized net income / total assets (Gryphon -2.8 clipped at -1)')
ax.set_title('Among listed bitcoin miners (latest report by 8 Aug 2025)\nTeraWulf is mid-pack, not an outlier')
plt.tight_layout(); plt.savefig(C+'charts/3_miner_peers.png',dpi=120); plt.close()
print(m[['lab','x']].to_string())
