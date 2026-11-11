# all figures $ thousands from cash flow statements (10-K FY2024 filed 2025-03-10; 10-Q Q1 filed 2025-06-30; 10-Q Q2 filed 2025-09-05)
ni={'FY2022':184786,'FY2023':548876,'FY2024':-242387,'H1 2025':-754200,'Q1 2025':-197373}
adj={'FY2022':[2536,143589,472219,869,-279536,30382,-49686,0,0,14997,-60243],
     'FY2023':[6589,187324,-9972,203,14938,1573,-156997,37401,-29378,0,34819],
     'FY2024':[33173,162525,0,13959,5466,50625,-95487,7222,77562,270063,153338],
     'H1 2025':[124531,590,582172,117558,20787,-472699,-23329,30549],
     'Q1 2025':[63353,-4740,0,-13082,0,-6635]}
ocf={'FY2022':355111,'FY2023':824756,'FY2024':586742,'H1 2025':-384156,'Q1 2025':-31705}
res={}
for k in ni:
    a=sum(adj[k]); res[k]=ni[k]+a
    print(f"{k}: net income {ni[k]/1e3:,.1f}m, non-cash adj {a/1e3:,.1f}m, cash earnings before WC {res[k]/1e3:,.1f}m, OCF {ocf[k]/1e3:,.1f}m")
q2ni=ni['H1 2025']-ni['Q1 2025']; q2ce=res['H1 2025']-res['Q1 2025']; q2ocf=ocf['H1 2025']-ocf['Q1 2025']
print(f"Q2 2025: NI {q2ni/1e3:,.1f}m cash earnings {q2ce/1e3:,.1f}m OCF {q2ocf/1e3:,.1f}m")
capex_h1=652798; capex_q1=340470; capex_q2=capex_h1-capex_q1
cash=551109; restr=270298
print('Q2 capex',capex_q2/1e3,'Q2 FCF',(q2ocf-capex_q2)/1e3)
print('months of cash (unrestricted) at Q2 OCF burn:', round(cash/(-q2ocf/3),1), ' at H1 OCF burn:', round(cash/(-ocf['H1 2025']/6),1),
      ' at Q2 OCF+capex burn:', round(cash/(-(q2ocf-capex_q2)/3),1))
TA=11957330; TL=10563982; CA=1482499; CL=2201304
print('leverage TL/TA',round(TL/TA,3),'equity',(TA-TL)/1e3,'current ratio',round(CA/CL,3))
debt=1181559+7805260; print('debt total $m',debt/1e3,'debt/assets',round(debt/TA,3))
print('Q2 interest 206.4m vs Q2 operating income', -387328/1e3, '; H1 interest', 420102/1e3,' H1 op income', -405807/1e3)
print('Q2 op loss excl goodwill/asset impairment and gain on sale:', (-387328+582172+117312-472699)/1e3)
print('goodwill+asset impairment H1 share of H1 net loss', round((582172+117558)/754200,3))
print('accrued deficit change', (-558397-196363)/1e3)
print('springing debt total 2029 notes+RCF+TLA+TLB', (2730127+710400+295000+1269259)/1e3,'+2026 notes',510879/1e3)
