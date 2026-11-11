"""Derived numbers and charts for Waitr 10-Q (adsh 0001653247-23-000072). Figures in $ thousands,
taken from the saved filings (statement lines quoted in comments) and shared/financials.csv."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "/Users/pramukhvenkateshkoushik/Desktop/Data_cap/investigator/final_cases-1/0001653247-23-000072"
CSV = "/Users/pramukhvenkateshkoushik/Desktop/Data_cap/investigator/shared/financials.csv"
df = pd.read_csv(CSV, dtype={"adsh": str}); df = df[df["filed"] <= 20231113]
me = df[df["adsh"] == "0001653247-23-000072"].iloc[0]

# ---- this report vs year before (Q3 2022 10-Q, 9M figures annualized x4/3; balance sheet at 9/30/22)
prior = dict(total_assets=90651, current_assets=29890, current_liabilities=28579, total_liabilities=86816,
             revenue=91352 * 4 / 3, net_income=-162349 * 4 / 3, operating_income=-145583 * 4 / 3,
             operating_cash_flow=-21701 * 4 / 3)
print("8 numbers ($k): now vs Q3-2022")
for k, v in prior.items():
    now = me[k] / 1000
    print(f"  {k:22s} {now:10,.0f} {v:10,.0f} {100*(now/v-1):6.0f}%")

# ---- ratios
ta, ca, cl, tl = 21585, 10814, 79520, 80650
print("liabilities/assets", round(tl / ta, 2), " current ratio", round(ca / cl, 3), " equity", ta - tl)
print("prior-year liab/assets", round(86816 / 90651, 2), " current ratio", round(29890 / 28579, 2))

# ---- loss excluding non-cash items, same method every period: sum of cash-flow-statement adjustments
adj = {
    "FY2021": (-5229, [2258, 0, 7974, 158, 12429, 0, 186, 964, -16715, 253, -111]),
    "FY2022": (-206789, [2323, 9499, 5703, 288, 13296, 121088, 32957, 1358, 0, -1939, -103]),
    "9M2022": (-162349, [1417, 9499, 4588, -33, 9664, 121088, 0, 930, -551, -80]),
    "9M2023": (-25626, [2785, 0, 3513, -32, 1268, 9536, 500, 1178, -135, 0, -47]),
    "6M2023": (-20420, [1835, 0, 2407, -22, 878, 9536, 783, 0, -35]),
}
cashloss = {}
for k, (ni, a) in adj.items():
    cashloss[k] = ni + sum(a)
    print(f"{k}: net loss {ni:,}  non-cash {sum(a):,} ({100*sum(a)/-ni:.0f}% of loss)  loss ex non-cash {cashloss[k]:,}")
q3_ni = -5206; q3_noncash = sum(adj["9M2023"][1]) - sum(adj["6M2023"][1])
print("Q3-2023 net loss", q3_ni, "non-cash", q3_noncash, "loss ex non-cash", q3_ni + q3_noncash)

# ---- burn and runway
ocf = {"Q1-23": -4824, "Q2-23": -5727 + 4824, "Q3-23": -6022 + 5727}
print("quarterly OCF", ocf)
cash = {"2022-09-30": 20118, "2022-12-31": 12066, "2023-03-31": 6289, "2023-06-30": 5066,
        "2023-09-30": 4654, "2023-10-31": 3992}
debt = 57089
m9 = 6022 / 9; mq3 = -ocf["Q3-23"] / 3; mq3_cl = -(q3_ni + q3_noncash) / 3; moct = 4654 - 3992
print(f"monthly burn: 9M OCF {m9:.0f}, Q3 OCF {mq3:.0f}, Q3 loss ex non-cash {mq3_cl:.0f}, October cash drop {moct}")
print(f"months of cash at 9/30: 9M burn {4654/m9:.1f}, Q3 OCF burn {4654/mq3:.1f}, Q3 cash-loss {4654/mq3_cl:.1f}")
print(f"months of cash at 10/31 at October pace: {3992/moct:.1f};  cash/debt due 5/15/24: {3992/debt:.1%}")
print("revenue Q3 yoy", round(100 * (11480 / 25141 - 1)), "%; orders yoy", round(100 * (4557 / 14156 - 1)), "%")
print("Q4-22 revenue", 111801 - 91352)

# ---- peers (same file as numbers.py)
peers = pd.read_csv(BASE + "/scripts/peers.csv")
la = (peers.total_liabilities / peers.total_assets).dropna(); cr = (peers.current_assets / peers.current_liabilities).dropna()

# ---- charts
plt.rcParams.update({"font.size": 10})
# 1 cash vs debt due
fig, ax = plt.subplots(figsize=(7, 4))
d = pd.to_datetime(list(cash)); ax.bar(d, list(cash.values()), width=20, color="tab:blue", label="Cash ($k)")
ax.axhline(debt, color="tab:red", ls="--", label=r"Debt principal due 15 May 2024: \$57,089k")
for x, y in zip(d, cash.values()):
    ax.text(x, y + 800, f"{y:,}", ha="center", fontsize=8)
ax.set_ylim(0, 62000); ax.set_ylabel("$ thousands"); ax.legend(loc="center right", fontsize=8)
ax.set_title(r"Cash fell to \$4.0M by 31 Oct 2023 against \$57.1M due May 2024")
fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(BASE + "/charts/1_cash_vs_debt.png", dpi=130)

# 2 quarterly revenue
rq = {"Q3-22": 25141, "Q4-22": 111801 - 91352, "Q1-23": 16704, "Q2-23": 13951, "Q3-23": 11480}
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(list(rq), list(rq.values()), color="tab:gray")
for i, v in enumerate(rq.values()):
    ax.text(i, v + 600, f"{v:,}", ha="center", fontsize=8)
ax.set_ylim(0, 30000); ax.set_ylabel("Quarterly revenue, $ thousands")
ax.set_title("Revenue per quarter keeps shrinking (Q3-23 down 54% on Q3-22)")
fig.tight_layout(); fig.savefig(BASE + "/charts/2_revenue.png", dpi=130)

# 3 net loss vs loss ex non-cash
lab = ["FY2021", "FY2022", "9M2022", "9M2023"]
fig, ax = plt.subplots(figsize=(7, 4)); x = np.arange(len(lab))
ax.bar(x - 0.2, [adj[k][0] for k in lab], 0.4, label="Net loss", color="tab:red")
ax.bar(x + 0.2, [cashloss[k] for k in lab], 0.4, label="Net loss excl. non-cash items", color="tab:orange")
ax.set_xticks(x); ax.set_xticklabels(lab); ax.axhline(0, color="k", lw=0.8)
for i, k in enumerate(lab):
    ax.text(i + 0.2, cashloss[k] - 4000 if cashloss[k] < 0 else cashloss[k] + 2000, f"{cashloss[k]:,}", ha="center", va="top" if cashloss[k] < 0 else "bottom", fontsize=8)
    ax.text(i - 0.2, adj[k][0] - 4000, f"{adj[k][0]:,}", ha="center", va="top", fontsize=8)
ax.set_ylim(-235000, 15000)
ax.set_ylabel("$ thousands"); ax.legend(fontsize=8)
ax.set_title("Most of the loss is impairments, but the cash loss is still negative")
fig.tight_layout(); fig.savefig(BASE + "/charts/3_cash_loss.png", dpi=130)

# 4 peer comparison
fig, axs = plt.subplots(1, 2, figsize=(9, 3.8))
axs[0].hist(la.clip(upper=5), bins=50, color="lightgray"); axs[0].axvline(tl / ta, color="tab:red")
axs[0].set_title(f"Liabilities / assets: Waitr {tl/ta:.2f}\npeer median {la.median():.2f} (clipped at 5)", fontsize=9)
axs[1].hist(cr.clip(upper=6), bins=50, color="lightgray"); axs[1].axvline(ca / cl, color="tab:red")
axs[1].set_title(f"Current ratio: Waitr {ca/cl:.2f}\npeer median {cr.median():.2f} (clipped at 6)", fontsize=9)
for a in axs: a.set_ylabel("number of SIC-73 peers")
fig.suptitle(f"Waitr vs {len(peers)} SIC-73 peers, period ends Apr-Dec 2023 (red line = Waitr)", fontsize=10)
fig.tight_layout(); fig.savefig(BASE + "/charts/4_peers.png", dpi=130)
print("peer n", len(peers), "la median", round(la.median(), 2), "cr median", round(cr.median(), 2),
      "share peers with la>Waitr", round((la > tl / ta).mean() * 100, 1), "share with cr<Waitr", round((cr < ca / cl).mean() * 100, 1))
