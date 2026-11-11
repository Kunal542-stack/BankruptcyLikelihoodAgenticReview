"""Numbers for Nogin (cik 1841800) 10-Q 2023-06-30. Usage: python -I analyze.py <repo_root> <case_dir>"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

root, case = sys.argv[1], sys.argv[2]
CUT = 20230814
COLS = ["total_assets", "current_assets", "current_liabilities", "total_liabilities", "revenue",
        "net_income", "operating_income", "operating_cash_flow"]

df = pd.read_csv(f"{root}/shared/financials.csv")
df = df[df["filed"] <= CUT]                      # drop everything filed after the report date
co = df[df["cik"] == 1841800].sort_values("filed")
me = co[co["adsh"] == "0000950170-23-042370"].iloc[0]
print(co[["adsh", "form", "ddate", "filed"] + COLS].to_string())
print("missing inputs:", [c for c in COLS if pd.isna(me[c])])

# ---- peers: same 2-digit SIC, latest report with period end Mar-Jun 2023, excluding the company
df["sic2"] = (df["sic"] // 100).astype("Int64")
p = df[(df["sic2"] == 73) & (df["cik"] != 1841800) & df["ddate"].between(20230331, 20230630)]
p = p.sort_values("filed").groupby("cik").tail(1).copy()
print("peer count", len(p))

def ratios(d):
    d = pd.DataFrame(d).copy() if not isinstance(d, pd.DataFrame) else d.copy()
    d["ni_ta"] = d["net_income"] / d["total_assets"]
    d["oi_ta"] = d["operating_income"] / d["total_assets"]
    d["ocf_ta"] = d["operating_cash_flow"] / d["total_assets"]
    d["tl_ta"] = d["total_liabilities"] / d["total_assets"]
    d["cr"] = d["current_assets"] / d["current_liabilities"]
    d["ni_rev"] = d["net_income"] / d["revenue"]
    d["rev_ta"] = d["revenue"] / d["total_assets"]
    return d

p = ratios(p)
m = ratios(pd.DataFrame([me]))[0:1].iloc[0]
out = {}
for c in COLS + ["ni_ta", "oi_ta", "ocf_ta", "tl_ta", "cr", "ni_rev", "rev_ta"]:
    s = p[c].dropna()
    pct = (s < m[c]).mean() * 100  # share of peers below Nogin
    out[c] = dict(value=float(m[c]), peer_median=float(s.median()), pct_peers_below=round(pct, 1), n=int(len(s)))
for k, v in out.items():
    print(f"{k:22s} nogin={v['value']:>16,.3f} peer_med={v['peer_median']:>16,.3f} %peers_below={v['pct_peers_below']:5.1f} n={v['n']}")

# ---- prior-year comparison (from the filings: H1-2022 column of this 10-Q annualized; FY2022 10-K balance sheet)
prior = dict(total_assets=74933e3, current_assets=35228e3, current_liabilities=53722e3, total_liabilities=147957e3,
             revenue=45548e3 * 2, net_income=-20915e3 * 2, operating_income=-15846e3 * 2, operating_cash_flow=-13193e3 * 2)
print("prior-year (H1-2022 x2; balance sheet 2022-12-31):", prior)

# ---- ratios, burn, runway (thousands)
cash_q2, cash_q1, cash_fy = 3143, 617, 15385
ocf_h1, ocf_q1 = -30215, -22246
ocf_q2 = ocf_h1 - ocf_q1
capex_h1, capex_q1 = 613, 21
burn_h1_m = -(ocf_h1 - capex_h1) / 6
burn_q2_m = -(ocf_q2 - (capex_h1 - capex_q1)) / 3
calc = dict(
    leverage_tl_ta=139341 / 57911, equity=57911 - 139341, current_ratio=20174 / 42362,
    working_capital=20174 - 42362, ocf_q2=ocf_q2, burn_h1_per_month=burn_h1_m, burn_q2_per_month=burn_q2_m,
    runway_months_h1=cash_q2 / burn_h1_m, runway_months_q2=cash_q2 / burn_q2_m,
    convert_principal=65500, cash_vs_convert=cash_q2 / 65500,
    rev_change_h1=29419 / 45548 - 1, rev_change_q2=12742 / 20350 - 1,
    interest_semiannual=65500 * 0.07 / 2,
    model_ni_check=-21732 * 2, model_ocf_check=ocf_h1 * 2, model_rev_check=29419 * 2,
)
# ---- loss adjusted for non-cash items, same rule every period: net loss + all non-cash reconciling items
# (items listed above "Changes in operating assets and liabilities" in each cash flow statement)
noncash = {
    "FY2021": (-65, [520, 137, 361, 53, 1174, -4937, -177, -2266, 74]),
    "FY2022": (-52726, [808, 2617, 2034, 130, -780, 4245, 717, 4561, -4271, -1117, 1885, -1611, 641]),
    "H1-2022": (-20915, [420, 802, 0, 83, 65, 1982, 509, 2566, 0, 0, -1611, 0, 82]),
    "Q1-2023": (-9901, [202, 482, 253, -26, 645, 430, 159, -4591, -847, -1]),
    "H1-2023": (-21732, [437, 722, 554, 370, 13, 938, -3739, 878, -3295, -847, -63, -1]),
}
ocf = {"FY2021": -21373, "FY2022": -26588, "H1-2022": -13193, "Q1-2023": -22246, "H1-2023": -30215}
adj = {k: dict(net_loss=v[0], noncash=sum(v[1]), cash_loss=v[0] + sum(v[1]), ocf=ocf[k],
               working_capital=ocf[k] - (v[0] + sum(v[1]))) for k, v in noncash.items()}
adj["Q2-2023"] = {k: adj["H1-2023"][k] - adj["Q1-2023"][k] for k in adj["H1-2023"]}
for k, v in adj.items():
    print(k, v)
for k, v in calc.items():
    print(f"{k}: {v:,.3f}")
json.dump(dict(peers=out, calc=calc, adj=adj, prior=prior), open(f"{case}/scripts/numbers.json", "w"), indent=1, default=float)

# ---- charts
ch = f"{case}/charts"
# 1 cash vs quarterly operating cash burn
fig, ax = plt.subplots(figsize=(7, 4))
q = ["Q4-2022\n(Dec 31)", "Q1-2023\n(Mar 31)", "Q2-2023\n(Jun 30)"]
ax.bar(q, [15385 / 1000, 617 / 1000, 3143 / 1000], color="tab:blue", label="Cash at quarter end")
ax.plot(q[1:], [22246 / 1000, ocf_q2 / -1000], "o-", color="tab:red", label="Cash used in operations that quarter")
for i, v in enumerate([15.385, 0.617, 3.143]):
    ax.text(i, v + 0.5, f"\\${v:.1f}M", ha="center", fontsize=8)
ax.text(0, 20, "Q2 included \\$22M gross equity raise;\nconvertible notes \\$65.5M principal (2026)\nnot shown", fontsize=8, ha="center")
ax.set_ylabel("\\$ millions"); ax.set_ylim(0, 25)
ax.set_title("Cash \\$3.1M at June 30 vs \\$8.0M used in operations in Q2 alone")
ax.legend(loc="center right", fontsize=8); fig.tight_layout(); fig.savefig(f"{ch}/1_cash_vs_burn.png", dpi=120); plt.close()

# 2 net loss vs cash-adjusted loss vs OCF, by half-year
fig, ax = plt.subplots(figsize=(7, 4))
per = ["H1-2022", "H1-2023"]
x = range(len(per)); w = 0.25
ax.bar([i - w for i in x], [adj[k]["net_loss"] / 1000 for k in per], w, label="Net loss (reported)")
ax.bar(list(x), [adj[k]["cash_loss"] / 1000 for k in per], w, label="Loss after removing non-cash items")
ax.bar([i + w for i in x], [adj[k]["ocf"] / 1000 for k in per], w, label="Operating cash flow")
ax.set_xticks(list(x)); ax.set_xticklabels(per); ax.axhline(0, color="black", lw=0.8)
ax.set_ylabel("\\$ millions (6 months)"); ax.set_title("The loss is mostly cash; working-capital paydown made H1-2023 worse")
ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(f"{ch}/2_loss_cash_vs_noncash.png", dpi=120); plt.close()

# 3 peer position on net income / assets and liabilities / assets
fig, axs = plt.subplots(1, 2, figsize=(9, 4))
for a, c, t in [(axs[0], "ni_ta", "Net income / total assets (annualized)"), (axs[1], "tl_ta", "Total liabilities / total assets")]:
    s = p[c].dropna().clip(-3, 5)
    a.hist(s, bins=40, color="lightgrey")
    a.axvline(m[c], color="red"); a.set_title(t, fontsize=9)
    a.text(m[c], a.get_ylim()[1] * 0.85, f" Nogin {m[c]:.2f}\n ({out[c]['pct_peers_below']:.0f}% of peers below)", color="red", fontsize=8)
axs[0].set_ylabel(f"SIC 73 peers (n={len(p)}), clipped to [-3,5]")
fig.suptitle("Nogin vs SIC-73 peers, period ending Mar-Jun 2023 (bars at -3 and 5 collect values beyond the axis)", fontsize=10)
fig.tight_layout(); fig.savefig(f"{ch}/3_peers.png", dpi=120); plt.close()

# 4 revenue trend by quarter
fig, ax = plt.subplots(figsize=(7, 4))
qs = ["Q1-2022", "Q2-2022", "Q1-2023", "Q2-2023"]
rv = [25199, 20350, 16675, 12742]
ax.bar(qs, [r / 1000 for r in rv], color=["grey", "grey", "tab:orange", "tab:orange"])
for i, r in enumerate(rv):
    ax.text(i, r / 1000 + 0.3, f"\\${r/1000:.1f}M", ha="center", fontsize=8)
ax.set_ylabel("Quarterly revenue, \\$ millions"); ax.set_ylim(0, 28)
ax.set_title("Revenue down 37% year on year in Q2-2023 (same quarters a year apart;\nQ3-Q4 2022 not shown)", fontsize=10)
fig.tight_layout(); fig.savefig(f"{ch}/4_revenue.png", dpi=120); plt.close()
