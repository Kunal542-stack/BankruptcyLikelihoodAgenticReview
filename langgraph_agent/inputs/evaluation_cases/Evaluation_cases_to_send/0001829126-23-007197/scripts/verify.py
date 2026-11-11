"""Check quotes word for word, recompute cited numbers, check links and dates, count words."""
import os, re, glob
import pandas as pd

os.chdir(os.path.join(os.path.dirname(__file__), ".."))
rep = open("report.md").read()
norm = lambda s: re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()
texts = {os.path.basename(f).split("_")[0]: norm(open(f).read()) for f in glob.glob("filings/*.txt")}

# 1. every quote in "..." (>= 25 chars) in the report must appear in some saved filing
quotes = [q for q in re.findall(r'"([^"]*)"', rep) if len(q) >= 12]
bad = 0
for q in quotes:
    hits = [a for a, t in texts.items() if norm(q) in t]
    print(("OK  " if hits else "MISS"), hits[:2], q[:80])
    bad += not hits
print(f"quotes: {len(quotes)} checked, {bad} missing\n")

# 2. links: every link is an SEC archive URL for this CIK whose accession was saved
links = re.findall(r"\((https?://[^)]+)\)", rep) + re.findall(r"^\[\w+\]: (\S+)", rep, re.M)
refs = set(re.findall(r"\]\[(\w+)\]", rep)); defs = set(re.findall(r"^\[(\w+)\]:", rep, re.M)); print("undefined refs:", refs - defs, "unused defs:", defs - refs)
saved = {a.replace("-", "") for a in texts}
for u in sorted(set(links)):
    m = re.search(r"/data/1823882/(\d{18})/", u)
    print("OK  " if m and m.group(1) in saved else "BAD ", u)
print()

# 3. no source after 20231108: accession filing dates from filings list (saved names) + CSV rows
dates = {"0001829126-23-007197": "20231108", "0001829126-23-005250": "20230809", "0001829126-23-003233": "20230510",
         "0001829126-23-002099": "20230316", "0001829126-23-005668": "20230825", "0001829126-23-005342": "20230811",
         "0001829126-23-004960": "20230727", "0001829126-23-004861": "20230725", "0001829126-23-004627": "20230711",
         "0001829126-23-004588": "20230707", "0001829126-23-004149": "20230614", "0001829126-23-003784": "20230526",
         "0001829126-23-003579": "20230518", "0001829126-23-003322": "20230512", "0001829126-23-001923": "20230309",
         "0001829126-23-000694": "20230110", "0001829126-22-013803": "20220623", "0001829126-22-006198": "20220316",
         "0001829126-22-007174": "20220331"}
assert set(dates) == set(texts), set(texts) ^ set(dates)
print("latest filing date used:", max(dates.values()), "<= 20231108:", max(dates.values()) <= "20231108")

# 4. recompute numbers
df = pd.read_csv("../../shared/financials.csv"); df = df[df["filed"] <= 20231108]
r = df[df["adsh"] == "0001829126-23-007197"].iloc[0]
peers = pd.read_csv("scripts/peers.csv")
print("peers n", len(peers), "max filed", peers.filed.max())
chk = {
    "L/A 3.0": r.total_liabilities / r.total_assets,
    "CL/CA 3.6": r.current_liabilities / r.current_assets,
    "current ratio 0.28": r.current_assets / r.current_liabilities,
    "NI ann -59.5m": r.net_income / 1e6, "rev 94.9m": r.revenue / 1e6,
    "NI ex gain ann -97.7": (-44608 - 28631) * 4 / 3 / 1000,
    "9M rev chg -43%": 71155 / 125603 - 1, "Q3 rev chg -65%": 14259 / 41094 - 1,
    "Q3 OCF -17.2": (-29374 + 12172) / 1000, "Q2 OCF -9.8": (-12172 + 2362) / 1000,
    "months Q3 1.4": 8186 / (17202 / 3), "months 9M 2.5": 8186 / (29374 / 9),
    "debt 129.2": (41545 + 31706 + 44386 + 11540) / 1000, "secured 73.3": (41545 + 31706) / 1000,
    "sub 55.9": (44386 + 11540) / 1000, "debt/cash 15.8": 129177 / 8186, "cash/debt 6%": 8186 / 129177,
    "adj FY22 -62.8": (-85382 + 22610) / 1000, "adj 9M22 -53.6": (-74069 + 20431) / 1000, "adj 9M23 -52.0": (-44608 - 7369) / 1000,
    "NI/A -1.01": r.net_income / r.total_assets, "OCF/A -0.66": r.operating_cash_flow / r.total_assets,
}
for k, v in chk.items():
    print(f"{k:22s} {v:10.3f}")
def pct(s, v): s = s.replace([float('inf'), -float('inf')], pd.NA).dropna(); return round((s < v).mean() * 100), round(s.median(), 3), len(s)
print("L/A pct,median", pct(peers.total_liabilities / peers.total_assets, r.total_liabilities / r.total_assets))
print("CR pct,median", pct(peers.current_assets / peers.current_liabilities, r.current_assets / r.current_liabilities))
print("NI/A pct,median", pct(peers.net_income / peers.total_assets, r.net_income / r.total_assets))
print("OCF/A pct,median", pct(peers.operating_cash_flow / peers.total_assets, r.operating_cash_flow / r.total_assets))
for c in ["total_assets", "current_assets", "current_liabilities", "total_liabilities", "revenue", "net_income", "operating_income", "operating_cash_flow"]:
    print(c, "pct", pct(peers[c], r[c])[0])

# 5. word count
print("\nreport words:", len(re.findall(r"\S+", rep)))
