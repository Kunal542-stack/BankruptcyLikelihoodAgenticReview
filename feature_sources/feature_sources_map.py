import json
E,I,O="E","I","O"
G=[]
def grp(name,rows): G.append([name,rows])
grp("A. Base numbers",[[n,"dollar",E,"DJ09","raw financial variables used unstandardized as predictors (p.5); inputs of every classic ratio"] for n in
 ["total_assets","current_assets","current_liabilities","total_liabilities","revenue","net_income","operating_income","operating_cash_flow"]])
grp("B. Ratios and scores",[
["cash_to_current_liabilities","ratio",I,"DJ09","liquidity ratio family (p.4); Beaver 1966 liquid-asset ratios"],
["months_of_cash","ratio",I,"ZH26","\"cash burn; burn rate\" (Table 14) turned into a number"],
["retained_earnings_to_assets","ratio",E,"A68","Altman X2 (also AL22 p.5)"],
["equity_to_assets","ratio",I,"A00","ZETA X6 capitalization; Ohlson OENEG"],
["interest_coverage","ratio",E,"A00","ZETA X3: EBIT / total interest payments"],
["working_capital_to_assets","ratio",E,"A68","Altman X1 (also AL22 p.5)"],
["ebit_to_assets","ratio",E,"A68","Altman X3 (also AL22 p.5)"],
["sales_to_assets","ratio",E,"A68","Altman X5 (also AL22 p.5)"],
["equity_to_liabilities","ratio",E,"A00","Z'' X4: book equity / total liabilities"],
["log_assets","ratio",E,"O80","SIZE; ZH26 Table 2 size"],
["liabilities_to_assets","ratio",E,"O80","TLTA; Zmijewski 1984; AL22 p.5"],
["current_liabilities_to_current_assets","ratio",E,"O80","CLCA"],
["liabilities_exceed_assets","binary",E,"O80","OENEG"],
["net_income_to_assets","ratio",E,"O80","NITA; Zmijewski; Shumway; ZH26 Table 2"],
["cash_flow_to_liabilities","ratio",E,"O80","FUTL (funds from operations / TL)"],
["current_ratio","ratio",E,"Z84","CACL; ZH26 Table 2 liquidity"],
["cash_to_assets","ratio",I,"CHS08","CASHMTA uses market assets; ours uses book"],
["quick_ratio","ratio",E,"DJ09","\"current and quick ratios\" (p.4)"],
["debt_due_to_cash","ratio",I,"ZH26","\"debt maturities; notes due\" (Table 15)"],
["debt_to_assets","ratio",E,"ZH26","Table 2 leverage = total debt / total assets"],
["lease_liabilities_to_assets","ratio",I,"A00","ZETA counts capitalized leases as debt"],
["interest_paid_to_cash_flow","ratio",I,"A00","ZETA X3 debt service, cash version"],
["ebitda_to_liabilities","ratio",I,"B66","Beaver's cash flow (NI + depreciation) / total debt"],
["payables_to_assets","ratio",E,"DJ09","\"accounts payable/total assets\" (p.4)"],
["gross_margin","ratio",E,"AL22","Gross Profit/Sales (Table 1)"],
["operating_margin","ratio",E,"DJ09","\"net operating margin\" (p.4)"],
["net_margin","ratio",E,"DJ09","\"sales margin\" (p.4)"],
["cash_flow_to_assets","ratio",E,"ZH26","Table 2 cash flow = OCF / total assets"],
["sga_to_revenue","ratio",I,"DJ09","\"production costs\" indicator family (§3, Bardos 1995)"],
["rnd_to_assets","ratio",I,"BCM12","R&D intensity changes how ratios predict bankruptcy"],
["stock_comp_to_assets","ratio",O,"-","no paper found"],
["goodwill_to_assets","ratio",I,"ZH26","\"goodwill impairment\" (Table 16)"],
["tangible_equity_to_assets","ratio",I,"ZH26","equity without goodwill; Table 16 impairment"],
["receivables_to_revenue","ratio",I,"DJ09","activity / turnover ratios (p.4)"],
["capex_to_assets","ratio",O,"-","no paper found"],
["has_revenue","binary",I,"A68","sales/assets; ZH26 \"decline in sales\" (Table 16)"],
["financing_cash_flow_to_assets","ratio",I,"WW19","distressed firms raise outside money"],
["investing_cash_flow_to_assets","ratio",I,"ZH26","\"asset sale to raise liquidity\" (Table 17)"],
["stock_issued_to_assets","ratio",I,"WW19","~40% of equity issues come from distressed firms"],
["debt_issued_to_assets","ratio",I,"ZH26","refinancing stress (Table 15)"],
["debt_repaid_to_assets","ratio",I,"ZH26","\"repaid debt; deleveraging\" (Table 15)"],
["pays_dividends","binary",I,"DD90","distressed firms cut dividends; DJ09 p.2"],
["debt_extinguishment_to_assets","ratio",I,"ZH26","\"debt restructuring; distressed exchange\" (Table 15)"],
["altman_z2_risk","score",E,"A00","Z'' = 6.56X1+3.26X2+6.72X3+1.05X4"],
["ohlson_o_score","score",E,"O80","O-score formula (also ZH26 App. A)"],
["zmijewski_score","score",E,"Z84","Zmijewski formula (also ZH26 App. A)"]])
grp("C. Trends and history",[
*[[n,"ratio",I,"DJ09","\"variation variables\": year-on-year changes (p.5); DJ15"] for n in
 ["revenue_growth","asset_growth","cash_change_to_assets","equity_change_to_assets","liabilities_to_assets_change","net_income_to_assets_change"]],
["share_growth","ratio",I,"WW19","share issuance by distressed firms (closest found)"],
["loss_two_years","binary",E,"O80","INTWO"],
["net_income_change","ratio",E,"O80","CHIN, same formula"],
*[[n,"ratio",I,"DJ15","failure as a process over time; DJ09 p.5"] for n in
 ["cash_to_assets_change_since_last","net_income_to_assets_change_since_last","liabilities_to_assets_change_since_last","cash_flow_to_assets_change_since_last"]],
["losses_in_last_4","count",I,"O80","INTWO extended to 4 reports"],
["reports_so_far","count",I,"SH01","firm age (years listed), counted in reports"],
["years_since_first_report","days",E,"SH01","ln(age), years since listing"],
["days_since_last_report","days",I,"BK17","late or missing filings signal poor performance"]])
grp("D. Industry comparison",[[n,"pct",I,"PP91","industry-relative ratios (ratio / industry average); ours is a percentile rank. AL22 industry-year medians"] for n in
 ["net_income_to_assets_industry_percentile","liabilities_to_assets_industry_percentile","cash_to_assets_industry_percentile","cash_flow_to_assets_industry_percentile","equity_to_assets_industry_percentile","log_assets_industry_percentile","revenue_growth_industry_percentile"]])
grp("E. Filing facts",[
["filer_status","cat",I,"O80","size class (Ohlson SIZE); no paper uses the SEC filer category"],
["filing_delay_days","days",I,"WZ84","distressed firms report later; Alford et al. 1994"],
["late_filer","binary",I,"BK17","filing after the deadline; Alford et al. 1994"],
["is_10k","binary",O,"-","control for annual vs quarterly report"],
["industry","cat",E,"CJ04","industry effects in the hazard model; AL22 industry dummies"]])
grp("F. NT late-filing notices",[
["late_filing_notice_last_year","count",I,"BK17","NT 10-K/10-Q \"signal continued poor performance\""],
["days_since_late_filing_notice","days",I,"BK17","same; Alford et al. 1994 (Form 12b-25)"]])
P=[["going_concern",E,"ZH26","\"substantial doubt\", \"going concern\" (Table 14); MSV15"],
["forbearance",E,"ZH26","\"forbearance agreement\" (Table 15)"],
["minimum_bid_price",I,"RW12","Nasdaq $1 bid-price rule; CHS08 low price"],
["chapter_11",I,"MAI19","10-K text features; ZH26 leaves Chapter 11 out"],
["strategic_alternatives",E,"ZH26","\"strategic alternatives\" (Table 17)"],
["material_weakness",E,"ZH26","\"material weakness in internal control\" (Table 17)"],
["identified_material_weakness",E,"ZH26","same phrase, stricter match (Table 17)"],
["not_in_compliance",I,"NSS12","covenant violations found in SEC filings"],
["covenant_not_in_compliance",E,"ZH26","\"breach / violation of covenant\" (Table 15); NSS12"],
["reverse_stock_split",I,"NT16","~80% of failed reverse-split firms delisted"],
["restructuring_support_agreement",I,"ZH26","\"debt restructuring\" (Tables 15, 17)"],
["notice_of_default",E,"ZH26","\"notice of default\" (Table 15)"],
["debtor_in_possession",I,"EL23","DIP loans to Chapter 11 firms"],
["cease_operations",E,"ZH26","\"ceased operations\" (Table 16)"],
["wind_down",I,"ZH26","\"going out of business\" (Table 16)"]]
rows=[]
for p,s,r,g in P:
    rows+= [[p+"_in_report","binary",s,r,g],
            [p+"_before_last_year","count",I,"MSV15","same language in earlier filings (signal up to 3 years ahead)"],
            ["days_since_"+p+"_before","days",I,"MSV15","time since earlier filings had it"]]
grp("G. Warning phrases",rows)
allf=[r for g in G for r in g[1]]
assert len(allf)==130, len(allf)
from collections import Counter
print(Counter(r[2] for r in allf)); print(Counter(r[3] for r in allf).most_common())
json.dump(G,open("feature_sources_map.json","w"))
