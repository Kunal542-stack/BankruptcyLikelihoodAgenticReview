# all $ thousands, from saved filings (cash flow statements / balance sheets)
# Non-cash adjustment applied identically to each period: SBC + depreciation + debt-cost amortization + loss on PP&E disposals + related-party stock expense
P={
 'FY2023':dict(ni=-73421,sbc=5859,dep=28350,amort=19515,disp=1209,rp=2917,ocf=4263,btc_inv=0,prepaid=0,capex=75168,months=12),
 'FY2024':dict(ni=-72418,sbc=30927,dep=59808,amort=11382,disp=17824,rp=0,ocf=-24422,btc_inv=67371,prepaid=0,capex=267940,months=12),
 'Q1 2025':dict(ni=-61418,sbc=38674,dep=15574,amort=607,disp=0,rp=0,ocf=56487,btc_inv=32623,prepaid=90000,capex=93687,months=3),
 'H1 2025':dict(ni=-79788,sbc=39978,dep=34360,amort=1215,disp=3831,rp=2375,ocf=1677,btc_inv=82382,prepaid=90000,capex=213629,months=6),
}
q1,h1=P['Q1 2025'],P['H1 2025']
P['Q2 2025']={k:(h1[k]-q1[k]) for k in h1}; P['Q2 2025']['months']=3
for k,v in P.items():
    adj=v['ni']+v['sbc']+v['dep']+v['amort']+v['disp']+v['rp']
    econ=v['ocf']+v['btc_inv']-v['prepaid']   # operating cash incl. bitcoin sales, excl. one-off prepaid rent
    print(f"{k:8s} NI {v['ni']/1e3:7.1f}M  noncash-adj {adj/1e3:7.1f}M  OCF {v['ocf']/1e3:7.1f}M  econ OCF {econ/1e3:7.1f}M  capex {v['capex']/1e3:6.1f}M  FCF(econ) {(econ-v['capex'])/1e3:7.1f}M  /month {(econ-v['capex'])/v['months']/1e3:6.1f}M")
# balance sheet 6/30/25
ta,ca,cl,tl=869408,99115,151304,695076; cash=89993; rcash=1425
print('leverage TL/TA',round(tl/ta,3),' current ratio',round(ca/cl,3),' equity',ta-tl)
cl_x_def=cl-47716-30000
print('current ratio excl deferred rent & contingent consideration',round(ca/cl_x_def,3))
q2=P['Q2 2025']; q2fcf=(q2['ocf']+q2['btc_inv']-q2['prepaid']-q2['capex'])/3
print('Q2 monthly burn incl capex',round(q2fcf/1e3,1),'M -> months of cash', round(cash/-q2fcf,1))
q2op=(q2['ocf']+q2['btc_inv'])/3
print('Q2 monthly operating (incl BTC sales) ',round(q2op/1e3,2),'M')
print('Q2 change in total cash', (91418-218162)/1e3)
h1fcf=(h1['ocf']+h1['btc_inv']-h1['prepaid']-h1['capex'])/6
print('H1 monthly burn incl capex (excl prepaid)',round(h1fcf/1e3,1),'-> months',round(cash/-h1fcf,1))
print('reported Q2 OCF',q2['ocf'],' annualized H1 OCF',h1['ocf']*2,' annualized NI',h1['ni']*2)
print('interest: 500M*2.75% =',500000*0.0275)
