"""Cash-adjusted loss (same method every period, from the cash flow statements), burn, runway, charts."""
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
C = "final_cases-1/0001628280-24-047749"
# $ thousands, copied from the cash flow statements (10-K FY2023 for 2022/2023; 10-Q Q2 and Q3 2024)
# non-cash adjustments = every line between "Net loss" and "Changes in assets and liabilities"
periods = {
 "FY2022":  dict(nl=-487694, adj=[11554,2355,582,5532,79573,-26044,4626,900,1430], ocf=-400475, months=12),
 "FY2023":  dict(nl=-302021, adj=[13843,3362,2182,30206,-2972,-57816,-10873,30717,5966,61551,2571,3619,1046], ocf=-251134, months=12),
 "H1 2024": dict(nl=-115647, adj=[6845,1752,12082,-41,-22046,-16790,-24462,67116,3142,3410,910,658], ocf=-83419, months=6),
 "9M 2024": dict(nl=-112389, adj=[10597,2647,16055,13730,-41,-60463,-40144,-22650,62226,3142,4220,1820,849], ocf=-109938, months=9),
}
rows = []
for k, v in periods.items():
    a = sum(v["adj"]); rows.append([k, v["nl"], a, v["nl"] + a, v["ocf"], v["months"]])
t = pd.DataFrame(rows, columns=["period","net_loss","noncash_adj","cash_adj_loss","ocf","months"]).set_index("period")
q3 = t.loc["9M 2024"] - t.loc["H1 2024"]; q3["months"] = 3; t.loc["Q3 2024"] = q3
t["cash_adj_loss_per_month"] = t.cash_adj_loss / t.months
t["ocf_per_month"] = t.ocf / t.months
print(t.round(0).to_string())

# quarterly operating cash flow from the 10-Qs (Q1: 47,519; H1: 83,419; 9M: 109,938)
q = {"Q1 2024": -47519, "Q2 2024": -83419 + 47519, "Q3 2024": -109938 + 83419}
print("quarterly OCF", q)
cash, restricted = 1533, 3936 + 10600
for name, burn in [("9M avg", 109938 / 9), ("Q3", -q["Q3 2024"] / 3)]:
    print(f"{name}: burn/month {burn:,.0f}K  months of unrestricted cash {cash/burn:.2f}  incl. restricted {(cash+restricted)/burn:.2f}")
# burn incl. capex
print("Q3 OCF+capex per month", (-q['Q3 2024'] + (9730 - 0)) / 3, "(capex is 9M total, upper bound)")
print("current ratio", 28979 / 202344, "TL/TA", 301330 / 523289, "working capital", 28979 - 202344)
print("Q3 pre-FV result: op loss -59,192; FV gains 61,771+4,890; net +3,258")

# ---- charts
df = pd.read_csv("shared/financials.csv"); df = df[df.filed <= 20241114]
me = df[df.cik == 1750153].sort_values("ddate")
lab = [f"{r.form} {str(r.ddate)[:6]}" for r in me.itertuples()]
fig, ax = plt.subplots(figsize=(8, 4))
x = range(len(me))
ax.plot(x, me.net_income / 1e6, "o-", label="Net income (annualised)")
ax.plot(x, me.operating_income / 1e6, "s-", label="Operating income (annualised)")
ax.plot(x, me.operating_cash_flow / 1e6, "^-", label="Operating cash flow (annualised)")
ax.axhline(0, color="k", lw=0.8); ax.set_xticks(list(x)); ax.set_xticklabels(lab, rotation=35, ha="right", fontsize=8)
ax.set_ylabel("$ million per year"); ax.legend(fontsize=8)
ax.set_title("Annualised YTD figures: in 2024 net loss improved past operating loss\nbecause of fair-value gains on Yorkville instruments, not operations")
fig.tight_layout(); fig.savefig(f"{C}/charts/1_income_vs_cash.png", dpi=130)

fig, ax = plt.subplots(figsize=(8, 4))
cashq = {"Dec 2022": 36589, "Dec 2023": 6394, "Mar 2024": 3656, "Jun 2024": 4513, "Sep 2024": 1533}
ax.bar(list(cashq), [v / 1e3 for v in cashq.values()], color="tab:blue", label="Unrestricted cash")
burns = {"Mar 2024": 47519, "Jun 2024": 35900, "Sep 2024": 26519}
ax.plot(list(burns), [v / 3 / 1e3 for v in burns.values()], "ro-", label="Operating cash burn per month (that quarter)")
for k, v in cashq.items(): ax.text(k, v / 1e3 + 0.5, f"{v/1e3:.1f}", ha="center", fontsize=8)
ax.set_ylabel("$ million"); ax.legend(fontsize=8)
ax.set_title(r"Unrestricted cash at Sep 2024 (\$1.5M) covered about 5 days of Q3 burn (\$8.8M/month)")
fig.tight_layout(); fig.savefig(f"{C}/charts/2_cash_vs_burn.png", dpi=130)

# peers: current ratio vs cash-flow/assets, same SIC-2, period ending Jun-Dec 2024
p = df[(df.sic.astype("Int64").astype(str).str[:2] == "37") & (df.cik != 1750153) & (df.ddate.between(20240630, 20241231))]
p = p.sort_values("filed").groupby("cik").tail(1)
p = p[(p.total_assets > 0) & (p.current_liabilities > 0)]
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.scatter((p.current_assets / p.current_liabilities).clip(upper=10), (p.operating_cash_flow / p.total_assets).clip(-1, 0.5), s=12, alpha=.5, label=f"SIC 37 peers (n={len(p)})")
ax.scatter([28979 / 202344], [-146584 / 523289], color="red", s=60, label="Canoo Q3 2024")
ax.axvline(1, color="grey", lw=.7, ls="--"); ax.axhline(0, color="grey", lw=.7, ls="--")
ax.set_xlabel("Current ratio (clipped at 10)"); ax.set_ylabel("Operating cash flow / total assets (clipped -1..0.5)")
ax.set_title("Canoo: current ratio 0.14 (lowest ~5% of SIC-37 peers)\nwhile burning cash equal to 28% of assets a year")
ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(f"{C}/charts/3_peers.png", dpi=130)
