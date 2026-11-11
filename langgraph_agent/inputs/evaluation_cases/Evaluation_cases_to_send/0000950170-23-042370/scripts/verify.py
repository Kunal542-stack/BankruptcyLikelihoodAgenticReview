"""Check report quotes, numbers, links, dates and length. Usage: python -I verify.py <case_dir>"""
import glob
import json
import re
import sys

case = sys.argv[1]
rep = open(f"{case}/report.md").read()
norm = lambda s: re.sub(r"\s+", " ", s.replace("’", "'").replace("“", '"').replace("”", '"'))
texts = {p.split("/")[-1][:20]: norm(open(p).read()) for p in glob.glob(f"{case}/filings/*.txt")}

# 1 quotes: every *"..."* passage must appear word for word in a saved filing
quotes = re.findall(r'\*"(.+?)"\*', rep)
ok = True
for q in quotes:
    hits = [k for k, t in texts.items() if norm(q) in t]
    print("QUOTE", "OK " if hits else "MISSING", hits[:2], q[:70])
    ok &= bool(hits)

# 2 numbers recomputed
n = json.load(open(f"{case}/scripts/numbers.json"))
c, a = n["calc"], n["adj"]
checks = {
    "NI/TA -0.75": round(n["peers"]["ni_ta"]["value"], 2) == -0.75,
    "OCF/TA -104%": round(n["peers"]["ocf_ta"]["value"] * 100) == -104,
    "TL/TA 2.41": round(c["leverage_tl_ta"], 2) == 2.41,
    "current ratio 0.48": round(c["current_ratio"], 2) == 0.48,
    "Q2 OCF -8.0M": round(c["ocf_q2"] / 1000, 1) == -8.0,
    "burn H1 5.1M/mo": round(c["burn_h1_per_month"] / 1000, 1) == 5.1,
    "burn Q2 2.9M/mo": round(c["burn_q2_per_month"] / 1000, 1) == 2.9,
    "runway 0.6-1.1": (round(c["runway_months_h1"], 1), round(c["runway_months_q2"], 1)) == (0.6, 1.1),
    "cash loss H1-23 25.8M": round(a["H1-2023"]["cash_loss"] / 1000, 1) == -25.8,
    "cash loss H1-22 16.0M": round(a["H1-2022"]["cash_loss"] / 1000, 1) == -16.0,
    "notes 21x cash": round(65.5 / 3.143) == 21,
    "rev H1 -35%": round(c["rev_change_h1"] * 100) == -35,
    "rev Q2 -37%": round(c["rev_change_q2"] * 100) == -37,
    "interest 2.3M": round(c["interest_semiannual"] / 1000, 1) == 2.3,
    "equity -81.4M": round(c["equity"] / 1000, 1) == -81.4,
    "prior NI -41.8": round(n["prior"]["net_income"] / 1e6, 1) == -41.8,
    "prior OI -31.7": round(n["prior"]["operating_income"] / 1e6, 1) == -31.7,
    "prior OCF -26.4": round(n["prior"]["operating_cash_flow"] / 1e6, 1) == -26.4,
    "prior rev 91.1": round(n["prior"]["revenue"] / 1e6, 1) == 91.1,
    "peer NI rank 25": round(n["peers"]["net_income"]["pct_peers_below"]) == 25,
    "peer OCF rank 6": round(n["peers"]["operating_cash_flow"]["pct_peers_below"]) == 6,
    "peer TL/TA 90": round(n["peers"]["tl_ta"]["pct_peers_below"]) == 90,
    "peer NI/TA 17": round(n["peers"]["ni_ta"]["pct_peers_below"]) == 17,
    "peer OCF/TA 91 worse-than": round(100 - n["peers"]["ocf_ta"]["pct_peers_below"]) == 91,
}
for k, v in checks.items():
    print("NUM", "OK " if v else "FAIL", k)
    ok &= v

# 3 links: every SEC link must point to a saved filing with filing date <= 20230814
dates = {"000095017023042370": "20230814", "000095017023009502": "20230323", "000095017023021940": "20230515",
         "000119312523079897": "20230327", "000119312523090983": "20230404", "000119312522298440": "20221205",
         "000119312523187341": "20230714", "000119312522236634": "20220901", "000119312523017792": "20230127"}
saved = {p.split("/")[-1][:20].replace("-", "") for p in glob.glob(f"{case}/filings/*.htm")}
for url in sorted(set(re.findall(r"\((https://www\.sec\.gov[^)]+)\)", rep))):
    acc = url.split("/")[-2]
    good = acc in saved and dates.get(acc, "99999999") <= "20230814"
    print("LINK", "OK " if good else "FAIL", dates.get(acc), url)
    ok &= good
for img in re.findall(r"\]\((charts/[^)]+)\)", rep):
    good = bool(glob.glob(f"{case}/{img}"))
    print("IMG", "OK " if good else "FAIL", img)
    ok &= good

words = len(re.findall(r"\S+", re.sub(r"\(https?://[^)]+\)|\(\.\./[^)]+\)|\(charts/[^)]+\)", "", rep)))
print("WORDS (links excluded)", words)
ok &= words <= 1200
print("ALL OK" if ok else "PROBLEMS")
