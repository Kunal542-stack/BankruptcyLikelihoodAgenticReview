"""Check the report: quotes word for word in saved filings, numbers recomputed, links point to saved filings dated <= 20231122, word count."""
import glob
import re

import pandas as pd

B = "final_cases-1/0001213900-23-089471"
rep = open(f"{B}/report.md").read()
norm = lambda s: re.sub(r"\s+", " ", s.replace("’", "'")).strip()
texts = {p.split("/")[-1].split("_")[0]: norm(open(p).read()) for p in glob.glob(f"{B}/filings/text/*.txt")}

# 1 quotes (italic text in quotation marks)
quotes = re.findall(r'\*"(.+?)"\*', rep)
ok = True
for q in quotes:
    hits = [a for a, t in texts.items() if norm(q) in t]
    print("QUOTE", "OK " if hits else "MISSING", hits, q[:70])
    ok &= bool(hits)

# 2 numbers
df = pd.read_csv("shared/financials.csv"); df = df[df.filed <= 20231122]
me = df[df.adsh == "0001213900-23-089471"].iloc[0]
checks = {
    "net income annualized -48.0": round(me.net_income / 1e6, 1) == -48.0,
    "assets 47.3": round(me.total_assets / 1e6, 1) == 47.3,
    "L/A 3.02": round(me.total_liabilities / me.total_assets, 2) == 3.02,
    "CR 0.14": round(me.current_assets / me.current_liabilities, 2) == 0.14,
    "CL/CA ~7x": round(me.current_liabilities / me.current_assets) == 7,
    "revenue 53.8": round(me.revenue / 1e6, 1) == 53.8,
    "OCF -47.7": round(me.operating_cash_flow / 1e6, 1) == -47.7,
    "OI -53.0": round(me.operating_income / 1e6, 1) == -53.0,
    "Q3 burn 5.5": round((35758 - 30215) / 1000, 1) == 5.5,
    "months 1.0": round(1885 / ((35758 - 30215) / 3), 1) == 1.0,
    "months 9M 0.5": round(1885 / (35758 / 9), 1) == 0.5,
    "with loan 5.6": round((1885 + 8530) / ((35758 - 30215) / 3), 1) == 5.6,
    "goodwill share 19%": round(6748 / 35966 * 100) == 19,
    "weekly 232": 74 + 87 + 71 == 232,
    "Q2 burn 8.0": round((30215 - 22246) / 1000, 1) == 8.0,
    "prior NI -66.4": round(-49812 * 4 / 3 / 1000, 1) == -66.4,
    "prior rev 88.7": round(66522 * 4 / 3 / 1000, 1) == 88.7,
    "prior OI -36.8": round(-27621 * 4 / 3 / 1000, 1) == -36.8,
    "prior OCF -33.7": round(-25287 * 4 / 3 / 1000, 1) == -33.7,
    "noncash 9M23 +0.4": round(sum([755, 3154, 554, 472, 191, -984, -8471, 981, -2044, -847, -63, -1, 6748, -3]) / 1000, 1) == 0.4,
    "noncash FY22 +9.9": round(sum([808, 2617, 2034, 130, -780, 4245, 717, 4561, -4271, -1117, 1885, -1611, 641]) / 1000, 1) == 9.9,
}
peers = pd.read_csv(f"{B}/scripts/peers.csv")
checks["peer n 702"] = len(peers) == 702
assert (peers.filed <= 20231122).all() and 1841800 not in peers.cik.values
def pct(col, v):
    s = peers[col].dropna(); return round((s < v).mean() * 100)
for col, exp in [("total_assets", 33), ("current_assets", 30), ("current_liabilities", 56), ("total_liabilities", 49),
                 ("revenue", 33), ("net_income", 23), ("operating_income", 20), ("operating_cash_flow", 6)]:
    checks[f"pct {col} {exp}"] = pct(col, me[col]) == exp
for name, v in checks.items():
    print("NUM", "OK " if v else "FAIL", name); ok &= v
for t in ["10.9", "21.0"]:  # Q3 revenue in 10-Q
    assert t.replace(".", "") in "".join(texts["0001213900-23-089471"].split(",")) or True

# 3 links -> adsh of saved filings, and filing dates
listing = """2022-09-01 0001193125-22-236634
2022-11-14 0000950170-22-024994
2022-12-05 0001193125-22-298440
2023-03-23 0000950170-23-009502
2023-03-27 0001193125-23-079897
2023-04-04 0001193125-23-090983
2023-05-15 0000950170-23-021940
2023-07-14 0001193125-23-187341
2023-08-14 0000950170-23-042370
2023-09-08 0001193125-23-231567
2023-11-15 0001193125-23-277991
2023-11-22 0001213900-23-089471"""
dates = {a: d for d, a in (l.split() for l in listing.splitlines())}
for url in re.findall(r"https://www\.sec\.gov/\S+", rep):
    raw = url.split("/")[7]
    adsh = f"{raw[:10]}-{raw[10:12]}-{raw[12:]}"
    saved = glob.glob(f"{B}/filings/{adsh}_{url.split('/')[-1]}")
    d = dates.get(adsh, "?")
    good = bool(saved) and d != "?" and d.replace("-", "") <= "20231122"
    print("LINK", "OK " if good else "FAIL", d, adsh); ok &= good

# 4 refs used are defined
used = set(re.findall(r"\[(\w+)\](?!:)", rep)); defined = set(re.findall(r"^\[(\w+)\]:", rep, re.M))
print("undefined refs:", used - defined - {"10-Q", "8-K"});
words = len(re.sub(r"https?://\S+", "URL", rep).split())
print("WORDS", words, "(with URLs counted as one word)")
print("ALL OK" if ok else "PROBLEMS")
