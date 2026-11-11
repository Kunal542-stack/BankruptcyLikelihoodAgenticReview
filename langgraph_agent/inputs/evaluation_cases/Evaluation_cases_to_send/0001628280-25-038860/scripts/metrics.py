"""Ratios, burn, runway and non-cash adjusted losses for Sangamo (cik 1001233) as of 20250807.
Sources: shared/financials.csv (rows filed <= 20250807) and the saved filings (numbers typed from their statements)."""
import pandas as pd

CUT = 20250807
df = pd.read_csv("shared/financials.csv")
df = df[df.filed <= CUT]
co = df[df.cik == 1001233].sort_values("ddate").set_index("ddate")
me = co.loc[20250630]
yb = co.loc[20240630]

print("== this report vs year before (annualized $m)")
for c in ["total_assets", "current_assets", "current_liabilities", "total_liabilities", "revenue",
          "net_income", "operating_income", "operating_cash_flow"]:
    print(f"{c:22s} {me[c]/1e6:9.1f} {yb[c]/1e6:9.1f}  change {(me[c]-yb[c])/1e6:8.1f}")

print("\n== ratios")
for lab, r in [("Q2 2025", me), ("Q2 2024", yb), ("FY 2024", co.loc[20241231])]:
    print(lab, "liab/assets %.2f" % (r.total_liabilities / r.total_assets),
          "current ratio %.2f" % (r.current_assets / r.current_liabilities),
          "equity $m %.1f" % ((r.total_assets - r.total_liabilities) / 1e6),
          "NI/assets %.2f" % (r.net_income / r.total_assets),
          "OCF/assets %.2f" % (r.operating_cash_flow / r.total_assets))

# --- quarterly operating cash flow, from YTD figures in the csv (annualized: Q1 x4, Q2 x2, Q3 x4/3)
print("\n== quarterly OCF ($m), de-annualized from csv")
q = {}
for y in [2023, 2024, 2025]:
    ytd = {}
    for d, k, m in [(f"{y}0331", "Q1", 3), (f"{y}0630", "Q2", 6), (f"{y}0930", "Q3", 9), (f"{y}1231", "Q4", 12)]:
        if int(d) in co.index:
            ytd[k] = co.loc[int(d)].operating_cash_flow * m / 12
    prev = 0
    for k in ["Q1", "Q2", "Q3", "Q4"]:
        if k in ytd:
            q[f"{y}{k}"] = (ytd[k] - prev) / 1e6
            prev = ytd[k]
for k, v in q.items():
    print(k, round(v, 1))

# --- burn and runway (filing figures, $ thousands)
cash_q2 = 38_344          # 10-Q Q2 2025 balance sheet, cash and cash equivalents (excl. $1.5m restricted)
atm_after = 8_900         # 10-Q Q2 2025 Note 12, ATM net proceeds after June 30
ocf_h1 = -44_307          # 10-Q Q2 2025 cash flow statement, six months
ocf_q1 = -26_149          # 10-Q Q1 2025 cash flow statement
ocf_q2 = ocf_h1 - ocf_q1
lilly, pfizer = 18_000, 5_000   # one-off license receipts in H1 2025 (Note 6)
print("\n== burn")
print("Q2 2025 OCF $m", ocf_q2 / 1e3, "| Q2 ex-Lilly", (ocf_q2 - lilly) / 1e3)
print("H1 2025 OCF $m", ocf_h1 / 1e3, "| H1 ex Lilly+Pfizer", (ocf_h1 - lilly - pfizer) / 1e3)
for lab, monthly in [("H1 reported /6", -ocf_h1 / 6), ("H1 ex one-offs /6", -(ocf_h1 - lilly - pfizer) / 6),
                     ("Q2 reported /3", -ocf_q2 / 3), ("Q2 ex-Lilly /3", -(ocf_q2 - lilly) / 3)]:
    print(f"{lab:20s} burn/month {monthly/1e3:5.2f}  months of cash (38.3) {cash_q2/monthly:4.1f}"
          f"  incl. July ATM (47.2) {(cash_q2+atm_after)/monthly:4.1f}")

# --- non-cash adjustment, same items every period, from the cash flow statements ($ thousands)
print("\n== net loss vs loss after adding back non-cash items (cash flow statement lines)")
periods = {
    "FY2023": dict(nl=-257_831, items=[65_528, 15_065, -2_329, 7_127, 27_363, 0, 1_119, 89_485, -6_335], ocf=-224_842),
    "FY2024": dict(nl=-97_941, items=[5_521, 5_107, -273, 4_254, 12_382, -1_026, 330, 0, 0], ocf=-67_139),
    "H1 2024": dict(nl=-85_217, items=[5_521, 2_648, -273, 2_451, 5_784, 0, -103, 0, 0], ocf=-75_547),
    "H1 2025": dict(nl=-50_583, items=[0, 2_013, 0, 1_808, 4_822, 0, 35, 0, 0], ocf=-44_307),
}
# item order: impairment LLA, D&A, accretion, ROU amortization, SBC, gain on sale, other, goodwill impairment, deferred tax
rows = []
for k, p in periods.items():
    nc = sum(p["items"])
    rows.append([k, p["nl"] / 1e3, nc / 1e3, (p["nl"] + nc) / 1e3, p["ocf"] / 1e3, nc / -p["nl"] * 100])
adj = pd.DataFrame(rows, columns=["period", "net_loss", "non_cash", "cash_loss", "ocf", "noncash_pct_of_loss"])
print(adj.round(1).to_string(index=False))
adj.to_csv("final_cases-1/0001628280-25-038860/scripts/adjusted_loss.csv", index=False)
pd.Series(q).to_csv("final_cases-1/0001628280-25-038860/scripts/quarterly_ocf.csv")
