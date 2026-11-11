# All inputs are from the FY2022 10-K (filed 2023-10-13) statements, NT 10-Qs (2023-05-08, 2023-08-03).
import json
cur=dict(total_assets=743.6,current_assets=431.6,current_liabilities=1001.9,total_liabilities=1173.4,revenue=1304.0,net_income=-232.5,operating_income=23.6,operating_cash_flow=-34.0)
prev=dict(total_assets=1240.1,current_assets=651.9,current_liabilities=545.1,total_liabilities=1458.8,revenue=1600.6,net_income=15.6,operating_income=247.2,operating_cash_flow=108.8)
out={}
for k in cur: out[k+'_chg_pct']=round((cur[k]-prev[k])/abs(prev[k])*100,1)
out['liab_to_assets_22']=round(cur['total_liabilities']/cur['total_assets'],3)
out['liab_to_assets_21']=round(prev['total_liabilities']/prev['total_assets'],3)
out['current_ratio_22']=round(cur['current_assets']/cur['current_liabilities'],3)
out['current_ratio_21']=round(prev['current_assets']/prev['current_liabilities'],3)
out['equity_22']=round(cur['total_assets']-cur['total_liabilities'],1)
out['equity_21']=round(prev['total_assets']-prev['total_liabilities'],1)
# Non-cash adjustment, same items every year, from the cash flow statement (continuing ops)
cf={2022:dict(cont=-246.9,da=37.3,sbc=6.0,debtcost=10.4,disposal=9.3,extinguish=0.0,invwd=3.8,impair=36.8,deftax=211.3,capex=-31.8,ocf=-34.0),
    2021:dict(cont=151.0,da=39.5,sbc=8.6,debtcost=5.5,disposal=-32.3,extinguish=19.9,invwd=14.9,impair=9.1,deftax=-23.1,capex=-37.8,ocf=108.8),
    2020:dict(cont=122.8,da=41.2,sbc=8.9,debtcost=1.8,disposal=-11.9,extinguish=-40.2,invwd=14.1,impair=0.0,deftax=10.8,capex=-27.6,ocf=179.5)}
for y,d in cf.items():
    adj=d['cont']+sum(d[k] for k in ['da','sbc','debtcost','disposal','extinguish','invwd','impair','deftax'])
    out[f'adj_earnings_{y}']=round(adj,1); out[f'fcf_{y}']=round(d['ocf']+d['capex'],1)
out['noncash_share_of_2022_cont_loss']=round((cf[2022]['deftax']+cf[2022]['impair'])/-cf[2022]['cont'],3)
cash=110.1
out['cash_end22']=cash
fcf=out['fcf_2022']; out['months_cash_fy_fcf']=round(cash/(-fcf/12),1)
out['months_cash_fy_ocf']=round(cash/(34.0/12),1)
# quarterly OCF (restated cumulative): Q1 -36.4, H1 -51.1, 9M -58.4, FY -34.0
q={'Q1':-36.4,'Q2':-51.1+36.4,'Q3':-58.4+51.1,'Q4':-34.0+58.4}
out['quarterly_ocf_2022']={k:round(v,1) for k,v in q.items()}
out['months_cash_worst_q_burn']=round(cash/(-q['Q1']/3),1)
out['months_cash_q3_burn']=round(cash/(-q['Q3']/3),1)
out['cash_foreign_share']=round(107.2/cash,3)
out['debt_to_cash']=round(712.9/cash,2)
out['cash_interest_2023_vs_OI_2022']=round(56.8/23.6,2)
out['interest_coverage_2022_OI']=round(23.6/40.7,2)
# 2023 preliminary revenue vs restated 2022 quarters
out['q1_23_rev_chg']=[round((280/347.1-1)*100,1),round((290/347.1-1)*100,1)]
out['q2_23_rev_chg']=[round((260/339.7-1)*100,1),round((270/339.7-1)*100,1)]
out['unused_lines']={'2022-12-31':120.1,'2023-09-30':16.3}
print(json.dumps(out,indent=1))
json.dump(out,open('final_cases/0001008654-23-000079/scripts/metrics.json','w'),indent=1)
