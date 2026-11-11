"""Derived numbers and charts for AIRSPAN 10-Q 2023-06-30. Run from investigator/ root.
Filing figures ($ thousands) are typed from the saved filings and cited next to each line."""
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "final_cases-1/0001829126-23-005250/charts"
CUT = 20230809
df = pd.read_csv("shared/financials.csv"); df = df[df.filed <= CUT]
me = df[df.adsh == "0001829126-23-005250"].iloc[0]
peers = pd.read_csv("final_cases-1/0001829126-23-005250/scripts/peers.csv")

# --- cash and burn (10-Q Q2 2023 cash flow; 10-Q Q1 2023 cash flow) ---
cash_jun23 = 10137; ocf_h1 = -12172; capex_h1 = -1122
ocf_q1 = -9448 / 4 * 1000 / 1000          # csv Q1 row is annualized x4 -> -2,362k
ocf_q2 = ocf_h1 - ocf_q1
print("Q1 OCF %.0f  Q2 OCF %.0f" % (ocf_q1, ocf_q2))
print("months of cash, Q2 operating burn: %.1f" % (cash_jun23 / (-ocf_q2 / 3)))
print("months of cash, H1 average burn incl capex: %.1f" % (cash_jun23 / (-(ocf_h1 + capex_h1) / 6)))
print("months of cash, FY2022 burn incl capex: %.1f" % (cash_jun23 / ((47164 + 3096) / 12)))

# --- ratios from model inputs ---
print("TL/TA %.2f  CA/CL %.2f  equity %.1fM  NI/TA %.2f  NI/rev %.2f" % (
    me.total_liabilities / me.total_assets, me.current_assets / me.current_liabilities,
    (me.total_assets - me.total_liabilities) / 1e6, me.net_income / me.total_assets, me.net_income / me.revenue))
print("csv annualization check: NI H1 -54,496 x2 =", -54496 * 2, " csv", me.net_income / 1000)

# --- debt stack at 30 Jun 2023 (10-Q balance sheet) ---
debt = {"Senior term loan (Fortress)": 4179 + 59045, "Convertible notes (Fortress)": 47749,
        "Sub. term loan - related party": 43402, "Golden Wayford note (in default)": 11396}
print("debt total %.1fM, Fortress secured %.1fM" % (sum(debt.values()) / 1e3, (4179 + 59045 + 47749) / 1e3))

# --- loss adjusted for non-cash items, same rule each period: net loss + 'Total adjustments' line ---
adj = pd.DataFrame({"period": ["FY2021", "FY2022", "H1 2023 (x2)"],
                    "net_loss": [-70526, -85382, -54496 * 2],
                    "noncash": [5132, 22610, 20153 * 2],
                    "ocf": [-66685, -47164, -12172 * 2]})
adj["adjusted_loss"] = adj.net_loss + adj.noncash
print(adj.to_string())
print("H1 2023 noncash share of loss: %.0f%%" % (20153 / 54496 * 100))

# --- peer ranks ---
pl = peers.assign(lev=peers.total_liabilities / peers.total_assets, roa=peers.net_income / peers.total_assets)
pl = pl.replace([float("inf"), -float("inf")], pd.NA).dropna(subset=["lev", "roa"])
print("peers n", len(pl), "median lev %.2f roa %.3f" % (pl.lev.median(), pl.roa.median()))
print("pct of peers with worse NI/TA: %.1f%%" % ((pl.roa < me.net_income / me.total_assets).mean() * 100))
print("pct of peers with higher TL/TA: %.1f%%" % ((pl.lev > me.total_liabilities / me.total_assets).mean() * 100))

# Chart 1: cash vs debt and burn
fig, ax = plt.subplots(figsize=(7, 4))
d = pd.DataFrame({"date": ["Dec-21", "Jun-22", "Dec-22", "Mar-23", "Jun-23"],
                  "cash": [63.1, 36.4, 7.3, 3.3, 10.1]})
ax.bar(d.date, d.cash, color="tab:blue")
for i, v in enumerate(d.cash): ax.text(i, v + 1, f"\\${v}M", ha="center")
ax.axhline(9.8, color="tab:red", ls="--"); ax.text(2.6, 14, "Q2-23 operating cash burn \\$9.8M", color="tab:red", ha="center", fontsize=8)
ax.set_ylabel("Cash incl. restricted ($M)"); ax.set_ylim(0, 75)
ax.set_title("Cash fell from \\$63M to \\$3M in 15 months; Jun-23 cash ≈ one quarter of Q2 burn\n(Jun-23 cash includes a \\$20M Fortress loan draw)", fontsize=9)
plt.tight_layout(); plt.savefig(f"{OUT}/1_cash_vs_burn.png", dpi=120); plt.close()

# Chart 2: debt stack vs cash + Mimosa price
fig, ax = plt.subplots(figsize=(7, 4))
bottom = 0
for k, v in debt.items():
    ax.bar("Debt at 30 Jun 2023", v / 1e3, bottom=bottom, label=k); bottom += v / 1e3
ax.bar("Cash + Mimosa price", 10.1, color="tab:blue"); ax.bar("Cash + Mimosa price", 60.0, bottom=10.1, color="lightblue", label="Mimosa sale ($60M, not closed)")
ax.text(0, bottom + 3, f"${bottom:.0f}M", ha="center"); ax.text(1, 73, "$70M (best case)", ha="center")
ax.set_ylabel("$M"); ax.set_ylim(0, 190); ax.legend(fontsize=7, loc="upper right")
ax.set_title("Even if the Mimosa sale closes, cash covers well under half the debt\n(Fortress loans mature 30 Dec 2024; Golden Wayford note overdue since June 2020)", fontsize=9)
plt.tight_layout(); plt.savefig(f"{OUT}/2_debt_vs_resources.png", dpi=120); plt.close()

# Chart 3: peers scatter
fig, ax = plt.subplots(figsize=(7, 4))
p = pl[(pl.lev < 4) & (pl.roa > -2)]
ax.scatter(p.lev, p.roa, s=8, alpha=0.4, color="grey", label=f"SIC 36 peers, 2023 reports (n={len(p)}; {len(pl)-len(p)} off-scale)")
ax.scatter([me.total_liabilities / me.total_assets], [me.net_income / me.total_assets], color="red", s=60, label="Airspan Q2-23")
ax.axvline(1, color="k", lw=0.5, ls=":"); ax.axhline(0, color="k", lw=0.5, ls=":")
ax.set_xlabel("Total liabilities / total assets"); ax.set_ylabel("Net income (annualized) / total assets")
ax.set_title("Airspan sits in the worst corner of its peers on both leverage and losses", fontsize=9); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig(f"{OUT}/3_peer_position.png", dpi=120); plt.close()

# Chart 4: reported vs adjusted loss
fig, ax = plt.subplots(figsize=(7, 4))
x = range(len(adj)); w = 0.27
ax.bar([i - w for i in x], adj.net_loss / 1e3, w, label="Net loss (reported)")
ax.bar(x, adj.adjusted_loss / 1e3, w, label="Net loss + non-cash items")
ax.bar([i + w for i in x], adj.ocf / 1e3, w, label="Operating cash flow")
ax.set_xticks(list(x)); ax.set_xticklabels(adj.period); ax.axhline(0, color="k", lw=0.5)
ax.set_ylabel("$M per year"); ax.legend(fontsize=7)
ax.set_title("Excluding non-cash items the loss is still \\$63-69M a year; cash flow looks better in\n2022-23 mainly from collecting receivables and not paying interest in cash (PIK)", fontsize=9)
plt.tight_layout(); plt.savefig(f"{OUT}/4_loss_noncash.png", dpi=120); plt.close()
