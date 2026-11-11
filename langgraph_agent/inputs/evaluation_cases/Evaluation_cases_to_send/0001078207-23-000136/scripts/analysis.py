"""Cash-adjusted loss, burn, runway and charts. All inputs typed from the saved filings ($ thousands).
Usage: python -I analysis.py <case_dir> <financials.csv>"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

case, csv = sys.argv[1], sys.argv[2]

# --- cash flow statement items, same adjustments in every period -------------------------------
# sources: FY22 & FY23 = 10-K filed 2023-06-01; H1 FY23/H1 FY24 = 10-Q filed 2023-11-14; Q1 FY24 = 10-Q filed 2023-08-09
cf = pd.DataFrame({
    #               net_loss  D&A    SBC   impair  deftax  gain_disp  other_noncash*          OCF     months
    "FY22 (Mar-22)": [-22431, 8615, 6262, 0, -7827, 0, 414 + 0 + 0 + 586, -66566, 12],
    "FY23 (Mar-23)": [-105399, 11103, 3885, 26965, 8958, -2, 761 + 821 + 228 + 691, 18846, 12],
    "H1 FY23 (Sep-22)": [-73380, 4786, 3346, 26965, 8167, 0, 585 + 1832 + 0 - 1276, -9596, 6],
    "H1 FY24 (Sep-23)": [-17467, 6256, 1941, 0, 114, -9021, 88 + 0 + 352 + 138 + 4, -7931, 6],
    "Q1 FY24 (Jun-23)": [-4924, 3150, 1015, 0, -182, -9021, 60 + 0 + 352 + 832 + 8, -2365, 3],
}, index=["net_loss", "da", "sbc", "impair", "deftax", "gain", "other", "ocf", "months"]).T
# *other = doubtful-account provision + inventory NRV + loss on debt extinguishment + other (+ liability SBC)
cf.loc["Q2 FY24 (Sep-23)"] = cf.loc["H1 FY24 (Sep-23)"] - cf.loc["Q1 FY24 (Jun-23)"]
cf.loc["Q2 FY24 (Sep-23)", "months"] = 3
cf["cash_loss"] = cf[["net_loss", "da", "sbc", "impair", "deftax", "gain", "other"]].sum(axis=1)
cf["working_capital"] = cf.ocf - cf.cash_loss
for c in ["net_loss", "cash_loss", "ocf"]:
    cf[c + "_annual"] = cf[c] * 12 / cf.months
print((cf / 1000).round(1).to_string())

# --- liquidity at 2023-09-30 (10-Q filed 2023-11-14) -------------------------------------------
cash_total, cash_unres, avail, debt = 10292, 8134, 29000, 17200
q2_ocf = cf.loc["Q2 FY24 (Sep-23)", "ocf"]; q2_capex = 724
q2_cashloss = cf.loc["Q2 FY24 (Sep-23)", "cash_loss"]
h1_ocf = cf.loc["H1 FY24 (Sep-23)", "ocf"]
burn = {"Q2 OCF": -q2_ocf / 3, "Q2 FCF": -(q2_ocf - q2_capex) / 3, "H1 OCF": -h1_ocf / 6,
        "Q2 cash loss (before working capital)": -q2_cashloss / 3}
print("\nmonthly burn ($m):", {k: round(v / 1000, 2) for k, v in burn.items()})
for k, b in burn.items():
    print(f"months of cash | {k}: total cash {cash_total / b:.1f}, unrestricted {cash_unres / b:.1f}, "
          f"cash+revolver {(cash_total + avail) / b:.1f}, cash+revolver-7m covenant floor {(cash_total + avail - 7000) / b:.1f}")
print("Q2 cash change: 18280 -> 10292 =", 10292 - 18280)

# --- balance-sheet ratios, this report vs year before ------------------------------------------
now = dict(ta=167678, ca=117550, cl=85243, tl=120555, rev=90409 * 2, ni=-17467 * 2, oi=-21741 * 2, ocf=-7931 * 2)
prev = dict(ta=226513, ca=155292, cl=66906, tl=134894, rev=120275 * 2, ni=-73380 * 2, oi=-65526 * 2, ocf=-9596 * 2)
for n, d in [("Sep-23", now), ("Sep-22", prev)]:
    print(n, {k: round(v / 1000, 1) for k, v in d.items()}, "lev", round(d["tl"] / d["ta"], 3),
          "CR", round(d["ca"] / d["cl"], 2), "equity", round((d["ta"] - d["tl"]) / 1000, 1),
          "NI/rev", round(d["ni"] / d["rev"], 3))
print("payables share of CL now", round(63235 / 85243, 2), "; payables up", 63235 - 29378)
print("H2 revenue implied by guidance:", 215000 - 90409, 240000 - 90409, "vs H2 FY23", 286773 - 120275)

# --- charts -------------------------------------------------------------------------------------
# 1. revenue and net income by fiscal year (annual filings) + FY24 guidance
yrs = ["CY2019", "CY2020", "FY22\n(Apr21-Mar22)", "FY23\n(Apr22-Mar23)", "FY24\nguidance"]
rev = [309.3, 552.6, 589.5, 286.8, 227.5]
ni = [-92.8, 59.8, -22.4, -105.4, None]
fig, ax = plt.subplots(figsize=(8, 4.5))
x = range(len(yrs))
bars = ax.bar([i - 0.2 for i in x], rev, 0.4, label="Net sales", color="#4c72b0")
bars[-1].set_hatch("//"); bars[-1].set_alpha(0.6)
ax.errorbar(4 - 0.2, 227.5, yerr=12.5, color="k", capsize=4)
ax.bar([i + 0.2 for i in x[:-1]], ni[:-1], 0.4, label="Net income", color="#c44e52")
ax.axhline(0, color="k", lw=0.8)
ax.set_xticks(list(x)); ax.set_xticklabels(yrs)
ax.set_ylabel("$ millions"); ax.legend()
ax.set_title("Pandemic boom then bust: sales more than halved after FY22;\nFY24 guidance cut to $215-240m (Nov-2023 10-Q)")
for i, v in enumerate(rev):
    ax.text(i - 0.2 + (0.18 if i == 4 else 0), v + (16 if i == 4 else 8), f"{v:.0f}", ha="center", fontsize=8)
for i, v in enumerate(ni[:-1]):
    ax.text(i + 0.2, v + (5 if v > 0 else -15), f"{v:.0f}", ha="center", fontsize=8)
plt.tight_layout(); plt.savefig(f"{case}/charts/1_revenue_netincome.png", dpi=130); plt.close()

# 2. reported vs cash-adjusted loss, annualized, same adjustments
sel = ["FY22 (Mar-22)", "FY23 (Mar-23)", "H1 FY23 (Sep-22)", "H1 FY24 (Sep-23)"]
fig, ax = plt.subplots(figsize=(8, 4.5))
xi = range(len(sel))
ax.bar([i - 0.27 for i in xi], cf.loc[sel, "net_loss_annual"] / 1000, 0.27, label="Net income (reported)", color="#c44e52")
ax.bar(list(xi), cf.loc[sel, "cash_loss_annual"] / 1000, 0.27, label="Net income after non-cash items", color="#dd8452")
ax.bar([i + 0.27 for i in xi], cf.loc[sel, "ocf_annual"] / 1000, 0.27, label="Operating cash flow", color="#55a868")
ax.axhline(0, color="k", lw=0.8)
ax.set_xticks(list(xi)); ax.set_xticklabels([s.replace(" (", "\n(") for s in sel])
ax.set_ylabel("$ millions per year (half-years x2)")
ax.set_title("After non-cash items the loss is smaller but still about -\\$35m a year;\nH1 FY24 'cash loss' is worse than net income because of a \\$9.0m asset-sale gain")
ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig(f"{case}/charts/2_cash_adjusted_loss.png", dpi=130); plt.close()

# 3. liquidity over time
dates = ["Mar-22", "Sep-22", "Mar-23", "Jun-23", "Sep-23"]
cash = [14.2, 6.8, 18.3, 18.3, 10.3]
av = [65.8, 22.2, 14.9, 9.5, 29.0]
dbt = [29.4, 47.3, 30.0, 17.3, 17.2]
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(dates, cash, label="Cash incl. restricted", color="#55a868")
ax.bar(dates, av, bottom=cash, label="Revolver availability (before covenant floor)", color="#8fd19e")
ax.plot(dates, dbt, "ko-", label="Debt outstanding")
ax.axhline(7, color="#c44e52", ls="--", lw=1)
ax.text(4.45, 7.8, "min. availability covenant\n>= \\$7m (SLR loan, from Nov-22)", fontsize=7, color="#c44e52", ha="right")
ax.set_ylabel("$ millions"); ax.legend(fontsize=8)
ax.set_title("Liquidity is thin but not collapsing: \\$39m cash + availability at Sep-23,\ndebt down to \\$17m; revolver cap cut \\$100m -> \\$60m -> \\$40m in 2023")
plt.tight_layout(); plt.savefig(f"{case}/charts/3_liquidity.png", dpi=130); plt.close()

# 4. peer position on two ratios
df = pd.read_csv(csv); df = df[df.filed <= 20231114]
peers = pd.read_csv(f"{case}/scripts/peers_used.csv")
p_ni = (peers.net_income / peers.total_assets).clip(-1.5, 0.5)
p_cl = (peers.current_liabilities / peers.total_assets).dropna().clip(0, 1.5)
fig, axs = plt.subplots(1, 2, figsize=(9, 4))
for a, data, me, t in [(axs[0], p_ni, -34934 / 167678, "Net income / total assets"),
                       (axs[1], p_cl, 85243 / 167678, "Current liabilities / total assets")]:
    a.hist(data, bins=20, color="#aaaaaa")
    a.axvline(me, color="#c44e52", lw=2, label=f"BowFlex {me:.2f}")
    a.axvline(data.median(), color="k", ls="--", lw=1, label=f"peer median {data.median():.2f}")
    a.set_title(t + " (edge bars = clipped tails)", fontsize=9); a.legend(fontsize=8); a.set_ylabel("peers")
fig.suptitle(f"SIC 39 peers (n={len(peers)}, periods Jun-Dec 2023; values clipped for display):\n"
             "the loss is bad but not extreme relative to assets; short-term liabilities are high", fontsize=10)
plt.tight_layout(); plt.savefig(f"{case}/charts/4_peers.png", dpi=130); plt.close()
print("charts saved")
