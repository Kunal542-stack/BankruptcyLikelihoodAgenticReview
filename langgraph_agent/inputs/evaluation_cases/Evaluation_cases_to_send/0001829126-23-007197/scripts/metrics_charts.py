"""Ratios, burn, months of cash, adjusted loss, peer ranks and charts. Values in $000 from the filings unless noted."""
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CUT = 20231108
df = pd.read_csv("../../shared/financials.csv")
df = df[df["filed"] <= CUT]
co = df[df["cik"] == 1823882].set_index("adsh")
r = co.loc["0001829126-23-007197"]
peers = pd.read_csv("scripts/peers.csv")
assert peers["filed"].max() <= CUT and (peers["cik"] != 1823882).all()

# --- model inputs (CSV) ---
print("total_liabilities/total_assets", round(r.total_liabilities / r.total_assets, 2))
print("current ratio", round(r.current_assets / r.current_liabilities, 2))
print("equity $m", (r.total_assets - r.total_liabilities) / 1e6)
for c, d in [("net_income", "total_assets"), ("operating_cash_flow", "total_assets"), ("total_liabilities", "total_assets"), ("net_income", "revenue")]:
    s = (peers[c] / peers[d]).replace([float("inf"), -float("inf")], pd.NA).dropna()
    v = r[c] / r[d]
    print(f"{c}/{d}: co={v:.2f} peer median={s.median():.3f} pct={(s < v).mean()*100:.0f}")
ca = (peers.current_assets / peers.current_liabilities).dropna()
print(f"current ratio peer median={ca.median():.2f}")
fy22 = co.loc["0001829126-23-002099"]
for c in ["total_assets", "current_assets", "current_liabilities", "total_liabilities", "revenue", "net_income", "operating_income", "operating_cash_flow"]:
    print(f"{c:22s} Q3-23(ann) {r[c]/1e6:8.1f}  FY22 {fy22[c]/1e6:8.1f}  chg {100*(r[c]/fy22[c]-1):6.0f}%")

# --- from filings ($000) ---
# 9M-2023 and 9M-2022 from Q3 10-Q; FY2022 from 10-K; H1-2023 OCF from Q2 10-Q; Q1-2023 OCF from Q1 10-Q
ocf_9m23, ocf_h1_23, ocf_q1_23 = -29374, -12172, -2362
ocf_q3_23 = ocf_9m23 - ocf_h1_23
ocf_q2_23 = ocf_h1_23 - ocf_q1_23
cash_q3 = 8186  # cash + restricted cash, 30 Sep 2023
print("quarterly OCF Q1,Q2,Q3 2023:", ocf_q1_23, ocf_q2_23, ocf_q3_23)
print("months of cash at Q3 burn:", round(cash_q3 / (-ocf_q3_23 / 3), 1))
print("months of cash at 9M avg burn:", round(cash_q3 / (-ocf_9m23 / 9), 1))
debt = {"Senior term loan": 41545, "Convertible debt (Fortress)": 31706, "Subordinated term loan - related party": 44386, "Subordinated debt (Golden Wayford)": 11540}
print("debt total", sum(debt.values()), "senior secured", 41545 + 31706, "debt/cash", round(sum(debt.values()) / cash_q3, 1))
# same non-cash adjustment each period: net loss + 'Total adjustments' line of the cash flow statement
adj = {"FY2022": (-85382, 22610, 12), "9M 2022": (-74069, 20431, 9), "9M 2023": (-44608, -7369, 9)}
for k, (ni, a, m) in adj.items():
    print(f"{k}: net loss {ni}, total non-cash adj {a}, cash-basis loss {ni+a}, annualized {(ni+a)*12/m:.0f}")
print("9M 2023 loss excl. Mimosa gain:", -44608 - 28631)
print("Q3 revenue y/y:", round(100 * (14259 / 41094 - 1)), "%; 9M revenue y/y:", round(100 * (71155 / 125603 - 1)), "%")
rev_q = {"Q3 2022": 41094, "Q1 2023": round(co.loc["0001829126-23-003233"].revenue / 4 / 1000),
         "Q2 2023": round((co.loc["0001829126-23-005250"].revenue / 2 - co.loc["0001829126-23-003233"].revenue / 4) / 1000), "Q3 2023": 14259}
print("quarterly revenue", rev_q)

# --- charts ---
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(list(rev_q), [v / 1000 for v in rev_q.values()], color=["grey", "steelblue", "steelblue", "firebrick"])
for i, v in enumerate(rev_q.values()):
    ax.text(i, v / 1000 + 0.5, f"\\${v/1000:.1f}m", ha="center")
ax.set_ylabel("Quarterly revenue, $ millions"); ax.set_ylim(0, 48)
ax.set_title("Revenue fell 65% year on year in Q3 2023\n(Q3 2023 includes Mimosa only to Aug 11)")
plt.tight_layout(); plt.savefig("charts/1_quarterly_revenue.png", dpi=120); plt.close()

fig, ax = plt.subplots(figsize=(7, 4))
labels = ["Cash +\nrestricted", "Senior\nterm loan", "Convertible\nnotes", "Sub. term loan\n(related party)", "Sub. debt\n(Golden Wayford)"]
vals = [cash_q3] + list(debt.values())
ax.bar(labels, [v / 1000 for v in vals], color=["green"] + ["firebrick"] * 2 + ["darkorange"] * 2)
for i, v in enumerate(vals):
    ax.text(i, v / 1000 + 0.8, f"\\${v/1000:.1f}m", ha="center")
ax.set_ylabel("$ millions, 30 Sep 2023"); ax.set_ylim(0, 52)
ax.set_title("\\$8.2m of cash against \\$129m of debt, all classified current\n(red = senior secured, Fortress; orange = subordinated)")
plt.xticks(fontsize=8); plt.tight_layout(); plt.savefig("charts/2_cash_vs_debt.png", dpi=120); plt.close()

fig, axes = plt.subplots(1, 2, figsize=(9, 4))
lev = (peers.total_liabilities / peers.total_assets).dropna().clip(upper=4)
axes[0].hist(lev, bins=40, color="lightgrey"); axes[0].axvline(r.total_liabilities / r.total_assets, color="red")
axes[0].set_title("Liabilities / assets\n(peers clipped at 4)"); axes[0].set_xlabel("ratio"); axes[0].set_ylabel("number of peers")
axes[0].text(r.total_liabilities / r.total_assets, axes[0].get_ylim()[1] * 0.8, " Airspan 3.0", color="red")
cr = ca.clip(upper=10)
axes[1].hist(cr, bins=40, color="lightgrey"); axes[1].axvline(r.current_assets / r.current_liabilities, color="red")
axes[1].set_title("Current ratio\n(peers clipped at 10)"); axes[1].set_xlabel("ratio")
axes[1].text(r.current_assets / r.current_liabilities, axes[1].get_ylim()[1] * 0.8, " Airspan 0.28", color="red")
fig.suptitle(f"Airspan vs {len(peers)} SIC-36 peers (latest report, period Mar-Dec 2023, filed by 8 Nov 2023)", fontsize=9)
plt.tight_layout(); plt.savefig("charts/3_peer_balance_sheet.png", dpi=120); plt.close()
print("charts saved")
