"""Ratios, cash runway, non-cash-adjusted losses and charts for Nogin (cik 1841800), as of 20231122.
All filing figures are in $ thousands and copied from the saved filings (line refs in comments)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE = "final_cases-1/0001213900-23-089471"
CUT = 20231122
df = pd.read_csv("shared/financials.csv")
df = df[df["filed"] <= CUT]
co = df[df.cik == 1841800].sort_values("filed")
me = co[co.adsh == "0001213900-23-089471"].iloc[0]

# --- this report vs a year earlier (Q3 2022 10-Q filed 2022-11-14; balance sheet lines 85-104, 9M income/OCF from the Q3 2023 10-Q comparatives) ---
prior = dict(total_assets=60_940e3, current_assets=43_080e3, current_liabilities=37_298e3, total_liabilities=131_080e3,
             revenue=66_522e3 * 4 / 3, net_income=-49_812e3 * 4 / 3, operating_income=-27_621e3 * 4 / 3,
             operating_cash_flow=-25_287e3 * 4 / 3)
print("8 inputs ($m): this report | Q3 2022 annualized")
for k, v in prior.items():
    print(f"  {k:22s} {me[k]/1e6:9.2f} | {v/1e6:9.2f}")

# --- ratios ---
cash = 1_885
print("liabilities/assets", round(me.total_liabilities / me.total_assets, 2))
print("current ratio", round(me.current_assets / me.current_liabilities, 2))
print("equity ($k)", 47_263 - 142_815)
print("working capital ($k)", 15_528 - 111_237)

# --- cash burn: quarterly operating cash flow from cumulative YTD figures ---
ytd = {"Q1": -22_246, "Q2": -30_215, "Q3": -35_758}   # 10-Qs filed 2023-05-15, 2023-08-14, 2023-11-22
q = {"Q1": ytd["Q1"], "Q2": ytd["Q2"] - ytd["Q1"], "Q3": ytd["Q3"] - ytd["Q2"]}
print("quarterly OCF", q)
fcf_q3 = q["Q3"] - (773 - 0)  # 9M capex 773; Q3 share unknown -> use OCF only for runway
burn_9m = -ytd["Q3"] / 9
burn_q3 = -q["Q3"] / 3
print(f"monthly burn 9M avg {burn_9m:.0f}k -> {cash/burn_9m:.2f} months; last quarter {burn_q3:.0f}k -> {cash/burn_q3:.2f} months")
print(f"with Nov-16 B. Riley $8,530k loan: {(cash+8530)/burn_q3:.1f} months at Q3 burn")
# merchant/short-term loans weekly repayments (Note 7): 74+87+71 = 232k/week
print("weekly MCA repayments ($k)", 74 + 87 + 71, "-> per month approx", round((74 + 87 + 71) * 52 / 12))

# --- non-cash-adjusted loss, same method every period: net loss + all non-cash reconciling items on the cash flow statement (before working capital) ---
periods = {
    "FY2021": (-65, [520, 137, 361, 53, 1174, -4937, -177, -2266, 74]),
    "FY2022": (-52_726, [808, 2617, 2034, 130, -780, 4245, 717, 4561, -4271, -1117, 1885, -1611, 641]),
    "9M2022": (-49_812, [614, 2154, 2034, 100, 134, 1895, 717, 4561, 9182, -64, 1885, -1611, -321]),
    "9M2023": (-35_966, [755, 3154, 554, 472, 191, -984, -8471, 981, -2044, -847, -63, -1, 6748, -3]),
}
ocf = {"FY2021": -21_373, "FY2022": -26_588, "9M2022": -25_287, "9M2023": -35_758}
rows = []
for p, (ni, adj) in periods.items():
    rows.append([p, ni, sum(adj), ni + sum(adj), ocf[p]])
adj = pd.DataFrame(rows, columns=["period", "net_loss", "noncash_total", "cash_loss_before_wc", "ocf"])
print(adj.to_string())
print("goodwill impairment share of 9M23 loss", round(6748 / 35_966, 3))

# --- peers ---
peers = pd.read_csv(f"{BASE}/scripts/peers.csv")
for c in ["net_income", "operating_cash_flow", "total_assets", "revenue"]:
    print(c, "peer median", round(peers[c].median() / 1e6, 2), "nogin pct", round((peers[c] < me[c]).mean() * 100))
peers["cr"] = peers.current_assets / peers.current_liabilities
peers["la"] = peers.total_liabilities / peers.total_assets
peers["nia"] = peers.net_income / peers.total_assets
small = peers[(peers.total_assets > 20e6) & (peers.total_assets < 100e6)]
print("small peers ($20-100m assets) n", len(small),
      "median L/A", round(small.la.median(), 2), "median CR", round(small.cr.median(), 2),
      "median NI/A", round(small.nia.median(), 3),
      "share with L/A>3", round((small.la > 3).mean(), 3), "share CR<0.2", round((small.cr < 0.2).mean(), 3))
print("all peers share with L/A>=3.02", round((peers.la >= 3.02).mean(), 3), "CR<=0.14", round((peers.cr <= 0.14).mean(), 3))

# ===== charts =====
C = f"{BASE}/charts"
# 1 cash vs current liabilities over time
lab = ["Sep-22", "Dec-22", "Mar-23", "Jun-23", "Sep-23"]
cash_s = [15_827, 15_385, 617, 3_143, 1_885]  # 10-Q 2022-11-14, 10-K 2023-03-23, 10-Q 2023-05-15, 10-Q 2023-08-14, 10-Q 2023-11-22
cl = [37_298, 53_722, 52_631, 42_362, 111_237]
fig, ax = plt.subplots(figsize=(7, 4))
x = range(len(lab))
ax.bar([i - 0.2 for i in x], cl, 0.4, label="Current liabilities", color="#c0504d")
ax.bar([i + 0.2 for i in x], cash_s, 0.4, label="Cash", color="#4f81bd")
for i, v in enumerate(cash_s):
    ax.text(i + 0.2, v + 1500, f"{v/1000:.1f}", ha="center", fontsize=8)
for i, v in enumerate(cl):
    ax.text(i - 0.2, v + 1500, f"{v/1000:.1f}", ha="center", fontsize=8)
ax.set_xticks(list(x)); ax.set_xticklabels(lab)
ax.set_ylabel("$ thousands"); ax.set_ylim(0, 125_000)
ax.set_title(r"Cash fell to \$1.9m while \$60m of convertible notes became current")
ax.legend(); fig.tight_layout(); fig.savefig(f"{C}/1_cash_vs_current_liabilities.png", dpi=130); plt.close(fig)

# 2 quarterly operating cash burn vs cash at quarter end
fig, ax = plt.subplots(figsize=(7, 4))
qs = ["Q1-23", "Q2-23", "Q3-23"]
burn = [-q["Q1"], -q["Q2"], -q["Q3"]]
ax.bar(qs, burn, color="#c0504d", label="Operating cash used in quarter")
ax.plot(qs, [cash_s[2], cash_s[3], cash_s[4]], "o-", color="#4f81bd", label="Cash at quarter end")
for i, v in enumerate(burn):
    ax.text(i, v + 400, f"{v/1000:.1f}", ha="center", fontsize=8)
ax.set_ylabel("$ thousands"); ax.set_ylim(0, 25_000)
ax.set_title(r"Burn slowed, but Q3 burn (\$5.5m) was ~3x the cash left (\$1.9m)")
ax.legend(); fig.tight_layout(); fig.savefig(f"{C}/2_quarterly_burn.png", dpi=130); plt.close(fig)

# 3 peer position: liabilities/assets vs current ratio
fig, ax = plt.subplots(figsize=(7, 4.5))
pp = peers[(peers.la.between(0, 4)) & (peers.cr.between(0, 5))]
ax.scatter(pp.la, pp.cr, s=8, alpha=0.35, color="grey", label=f"SIC 73 peers, Jun-Dec 2023 (n={len(pp)} shown)")
ax.scatter([me.total_liabilities / me.total_assets], [me.current_assets / me.current_liabilities], color="red", s=60, label="Nogin Q3-23")
ax.axvline(1, ls="--", lw=0.8, color="k"); ax.axhline(1, ls="--", lw=0.8, color="k")
ax.set_xlabel("Total liabilities / total assets"); ax.set_ylabel("Current ratio")
ax.set_title("Nogin sits in the corner peers rarely occupy (axes clipped at 4 and 5)")
ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(f"{C}/3_peer_position.png", dpi=130); plt.close(fig)

# 4 net loss vs cash loss before working capital, same method each period
fig, ax = plt.subplots(figsize=(7, 4))
xs = range(len(adj))
ax.bar([i - 0.2 for i in xs], -adj.net_loss, 0.4, label="Net loss", color="#c0504d")
ax.bar([i + 0.2 for i in xs], -adj.cash_loss_before_wc, 0.4, label="Loss after removing non-cash items", color="#9bbb59")
ax.axhline(0, color="k", lw=0.8)
ax.set_xticks(list(xs)); ax.set_xticklabels(["FY2021 (12m)", "FY2022 (12m)", "9M2022 (9m)", "9M2023 (9m)"]); ax.set_ylim(0, 70_000)
ax.set_ylabel("$ thousands (positive = loss)")
ax.legend(loc="upper left")
ax.set_title(r"Most of the loss is cash: non-cash items net to only \$0.4m in 9M-23")
ax.legend(); fig.tight_layout(); fig.savefig(f"{C}/4_noncash_adjusted_loss.png", dpi=130); plt.close(fig)
print("charts saved")
