"""Ratios, cash burn, runway, non-cash adjusted loss and charts. Figures in $ thousands are taken from the filings
(cited in report); CSV rows from shared/financials.csv filed <= 20250807."""
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

co = pd.read_csv("scripts/company_rows.csv")
peers = pd.read_csv("scripts/peer_rows.csv")
assert co["filed"].max() <= 20250807 and peers["filed"].max() <= 20250807
me = co[co.adsh == "0001159167-25-000069"].iloc[0]
prior = co[co.adsh == "0001159167-24-000064"].iloc[0]   # Q2 2024 10-Q, a year earlier

print("== 8 numbers: this report vs year before ($M) and as share of assets/revenue")
for c in ["total_assets", "current_assets", "current_liabilities", "total_liabilities", "revenue",
          "net_income", "operating_income", "operating_cash_flow"]:
    base = "revenue" if c in ("net_income", "operating_income", "operating_cash_flow") else "total_assets"
    print(f"{c:22s} {me[c]/1e6:9.1f} {prior[c]/1e6:9.1f}  share {me[c]/me[base]:.3f} vs {prior[c]/prior[base]:.3f}")

# ---- ratios at 2025-06-28 ($k, from 10-Q balance sheet)
cash, restricted, restricted_nc = 40568, 36000, 2409
term_loan, tl, ta, ca, cl = 203186, 488012, 480320, 244779, 456603
equity = ta - tl
print("\nliabilities/assets", round(tl / ta, 3), "equity $k", equity, "current ratio", round(ca / cl, 3))
print("term loan / cash", round(term_loan / cash, 2), "term loan/(cash+restricted)", round(term_loan / (cash + restricted), 2))

# ---- burn: operating cash flow (10-Q H1 2025 = -56,617; Q1 2025 10-Q annualised in CSV -105.84M -> Q1 = -26,460)
ocf_h1 = -56617
ocf_q1 = round(co[co.adsh == "0001159167-25-000051"].operating_cash_flow.iloc[0] / 4 / 1000)
ocf_q2 = ocf_h1 - ocf_q1
print("\nOCF Q1", ocf_q1, "Q2", ocf_q2, "H1", ocf_h1)
for label, q in [("H1 average", ocf_h1 / 2), ("Q2 only", ocf_q2)]:
    m = -q / 3
    print(f"{label}: burn/month {m:.0f}k; months of unrestricted cash {cash/m:.1f}; incl. restricted {(cash+restricted)/m:.1f}")
# cash fall in Q2: 69,922 -> 40,568
print("unrestricted cash fall in Q2", 69922 - 40568)

# ---- non-cash adjusted loss, same method every period: net loss + all non-cash items in the cash flow
# statement (D&A, equity inv., SBC, inventory provision, FV change of loan, debt issuance costs, deferred tax, other)
periods = {
    "FY2022": (-286295, [47869, 19718, 31905, 2888, 0, 0, 18799, -1003], -90021),
    "FY2023": (-304710, [32791, 3910, 36056, 6378, 5904, 11837, 6563, -17694], -114793),
    "FY2024": (-145518, [21667, 370, 24476, 13489, 24557, 583, -2391, -4140], -33222),
    "H1 2024": (-62039, [11116, 375, 12458, 11715, 4746, 477, -1682, -3858], -20233),
    "H1 2025": (-110081, [4385, -394, 9076, 1015, 2687, 16828, 292, 3112], -56617),
}
rows = []
for k, (ni, adj, ocf) in periods.items():
    rows.append([k, ni, sum(adj), ni + sum(adj), ocf, ocf - ni - sum(adj)])
t = pd.DataFrame(rows, columns=["period", "net_loss", "non_cash", "cash_loss", "OCF", "working_capital"])
print("\n", t.to_string(index=False))
# H1 2024 included $75.2M one-off Amazon fee net benefit (10-Q, Note 1)
print("H1 2024 cash loss excl. Amazon fee", -62039 + sum(periods["H1 2024"][1]) - 75200)

# ---- peer facts
p = peers.copy()
p["liab_assets"] = p.total_liabilities / p.total_assets
p["cur"] = p.current_assets / p.current_liabilities
p["ni_rev"] = p.net_income / p.revenue
print("\npeers n", len(p), "median liab/assets", round(p.liab_assets.median(), 3), "median current ratio",
      round(p.cur.median(), 2), "median NI", p.net_income.median())
print("share of peers with NI below iRobot", round((p.net_income < me.net_income).mean() * 100, 1))
print("share of peers with liab/assets above iRobot", round((p.liab_assets > tl / ta).mean() * 100, 1))
print("share of peers with current ratio below iRobot", round((p.cur < ca / cl).mean() * 100, 1))
print("share of peers with larger total assets", round((p.total_assets > me.total_assets).mean() * 100, 1))

# ================= charts
c = co.copy(); c["date"] = pd.to_datetime(c.ddate.astype(str))
# 1: net income and OCF over time (annualised, $M)
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(c.date, c.net_income / 1e6, "o-", label="Net income (annualised)")
ax.plot(c.date, c.operating_cash_flow / 1e6, "s-", label="Operating cash flow (annualised)")
ax.axhline(0, color="k", lw=0.7)
ax.set_ylabel("$ millions per year"); ax.set_xlabel("Report period end"); ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2)
ax.set_title("iRobot has lost money in every report but one since 2022\n(Q1 2024 boosted by one-off $94M Amazon fee)")
fig.text(0.01, 0.01, "Source: shared/financials.csv, iRobot 10-K/10-Q rows filed 2023-02-14 to 2025-08-07; 10-Q values annualised", fontsize=7)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("charts/1_losses.png", bbox_inches="tight", dpi=130)

# 2: term loan vs cash at each quarter-end in 2025 ($M, from 10-K/10-Qs)
fig, ax = plt.subplots(figsize=(7, 4))
lab = ["Dec 28, 2024", "Mar 29, 2025", "Jun 28, 2025"]
cash_s = [134.3, 69.9, 40.6]; loan_s = [200.6, 224.1, 203.2]
ax.bar([0, 1, 2], cash_s, width=0.35, label="Unrestricted cash", color="tab:blue")
ax.bar([0.35, 1.35, 2.35], loan_s, width=0.35, label="Term loan (fair value)", color="tab:red")
for x, v in zip([0, 1, 2], cash_s): ax.text(x, v + 3, f"{v}", ha="center")
for x, v in zip([0.35, 1.35, 2.35], loan_s): ax.text(x, v + 3, f"{v}", ha="center")
ax.set_xticks([0.17, 1.17, 2.17]); ax.set_xticklabels(lab); ax.set_ylabel("$ millions"); ax.set_ylim(0, 270)
ax.set_title("Cash fell by 70% in six months while the $203M loan\nwas moved to current liabilities")
ax.legend(loc="upper left", ncol=2)
fig.text(0.01, 0.01, "Source: 10-K filed 2025-03-12, 10-Qs filed 2025-05-06 and 2025-08-07 balance sheets (loan current from Mar 29)", fontsize=7)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("charts/2_cash_vs_loan.png", dpi=130)

# 3: peers: liabilities/assets vs current ratio
fig, ax = plt.subplots(figsize=(7, 4.5))
pp = p[(p.liab_assets < 3) & (p.cur < 10)]
ax.scatter(pp.liab_assets, pp.cur, s=10, alpha=0.4, label=f"SIC 36 peers (n={len(pp)} shown)")
ax.scatter([tl / ta], [ca / cl], color="red", s=60, label="iRobot Q2 2025")
ax.axvline(1, color="grey", ls="--", lw=0.8); ax.axhline(1, color="grey", ls="--", lw=0.8)
ax.set_xlabel("Total liabilities / total assets"); ax.set_ylabel("Current ratio")
ax.set_title("iRobot sits in the weak corner: liabilities > assets and\ncurrent ratio 0.54 (only ~9% of peers lower)")
ax.legend()
fig.text(0.01, 0.01, f"Source: shared/financials.csv, latest report per SIC-36 company with period Jan-Jun 2025, filed <= 2025-08-07; {len(p)-len(pp)} outliers off-scale", fontsize=7)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("charts/3_peers.png", dpi=130)
print("charts saved")
