"""Check report.md: quotes are verbatim in saved filings, links point to saved filings dated <= 20250807,
numbers recompute, and the word count is within 1,200. Run from the investigator folder with python -I."""
import glob
import re

import pandas as pd

C = "final_cases-1/0001628280-25-038860"
CUT = "2025-08-07"
report = open(f"{C}/report.md").read()
norm = lambda t: re.sub(r"\s+", " ", t.replace("’", "'").replace("“", '"').replace("”", '"'))
texts = {p: norm(open(p).read()) for p in glob.glob(f"{C}/filings/*.txt")}

# 1. quotes
print("== quotes")
bad = 0
for q in re.findall(r'"([^"]{12,})"', report):
    hits = [p.split("/")[-1][:20] for p, t in texts.items() if norm(q) in t]
    print("OK " if hits else "MISSING", q[:70], hits[:2])
    bad += not hits
print("missing quotes:", bad)

# 2. links: every EDGAR link must match a saved filing whose filing date <= cut
print("\n== links")
dates = {"000162828025038860": "2025-08-07", "000162828025024650": "2025-05-12", "000162828025013088": "2025-03-17",
         "000162828024010788": "2024-03-13", "000162828024019337": "2024-04-30", "000162828024052579": "2024-12-30",
         "000162828025022664": "2025-05-06", "000162828025031559": "2025-06-16", "000162828024026903": "2024-06-05",
         "000162828023035989": "2023-11-01", "000162828023028200": "2023-08-08"}  # from sec_tools.py filings listing
saved = {re.sub("-", "", p.split("/")[-1].split("_")[0]): p.split("/")[-1].split("_", 1)[1] for p in glob.glob(f"{C}/filings/*.htm")}
for url in sorted(set(re.findall(r"\((https://www\.sec\.gov/[^)]+)\)", report))):
    acc, doc = url.split("/")[-2], url.split("/")[-1]
    ok = saved.get(acc) == doc and dates[acc] <= CUT
    print("OK " if ok else "BAD", dates.get(acc), url)
for img in re.findall(r"\]\((charts/[^)]+)\)", report):
    print("chart exists" if glob.glob(f"{C}/{img}") else "CHART MISSING", img)

# 3. numbers
print("\n== numbers")
df = pd.read_csv("shared/financials.csv")
df = df[df.filed <= 20250807]
print("latest company row filed:", df[df.cik == 1001233].filed.max())
r = df[(df.cik == 1001233) & (df.ddate == 20250630)].iloc[0]
chk = {
    "NI/assets -1.04": r.net_income / r.total_assets,
    "liab/assets 0.80": r.total_liabilities / r.total_assets,
    "current ratio 1.05": r.current_assets / r.current_liabilities,
    "equity 19.6": (r.total_assets - r.total_liabilities) / 1e6,
    "H1 ex-one-off burn 67.3": (44_307 + 18_000 + 5_000) / 1e3,
    "monthly burn 11.2": (44_307 + 23_000) / 6e3,
    "months incl ATM 4.2": (38_344 + 8_900) / ((44_307 + 23_000) / 6),
    "non-cash share H1 2025 17%": (2_013 + 1_808 + 4_822 + 35) / 50_583,
    "non-cash H1 2025 8.7": (2_013 + 1_808 + 4_822 + 35) / 1e3,
    "annualized loss ex one-offs 147": (50_583 + 23_000) * 2 / 1e3,
    "2023 write-downs 155": (89_485 + 65_528) / 1e3,
    "tax credits 19.1": (4_604 + 14_481) / 1e3,
    "Genentech total 50": 40 + 10,
}
for k, v in chk.items():
    print(f"{k:32s} -> {v:.3f}")
peers = pd.read_csv(f"{C}/scripts/peers_sic2.csv")
print("peers:", len(peers), "| latest peer filed:", peers.filed.max(), "| self excluded:", 1001233 not in set(peers.cik))
ta = peers.total_assets.where(peers.total_assets > 0)
print("peer median NI/assets", round((peers.net_income / ta).median(), 2))
print("share of peers with higher liab/assets", round(((peers.total_liabilities / ta) > 0.799).mean() * 100))

# 4. length
body = re.sub(r"\(https?://[^)]+\)|\(charts/[^)]+\)", "", report)
print("\nword count (excluding URLs):", len(re.findall(r"\S+", body)))
