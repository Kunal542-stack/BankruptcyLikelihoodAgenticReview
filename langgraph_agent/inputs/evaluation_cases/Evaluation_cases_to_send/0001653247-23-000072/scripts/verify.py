"""Check quotes are verbatim in saved filings, links point to saved filings dated <= 20231113, numbers recompute, word count."""
import re, os, glob
BASE = "/Users/pramukhvenkateshkoushik/Desktop/Data_cap/investigator/final_cases-1/0001653247-23-000072"
rep = open(BASE + "/report.md").read()
norm = lambda s: re.sub(r"\s+", " ", s.replace("’", "'")).strip()
texts = {os.path.basename(p).split("_")[0]: norm(open(p).read()) for p in glob.glob(BASE + "/filings/*.txt")}
allt = " ".join(texts.values())

quotes = re.findall(r'\*"(.+?)"\*', rep) + re.findall(r'reads "(.+?)"', rep)
for q in quotes:
    hits = [k for k, t in texts.items() if norm(q) in t]
    print("OK " if hits else "MISSING", hits[:3], q[:70])

# links: every link must map to a saved filing; filing date from the EDGAR list
dates = {}
lst = glob.glob("/Users/pramukhvenkateshkoushik/.claude/projects/*/*/tool-results/bkdwwe4kl.txt")
for line in open(lst[0]):
    p = line.split(",")
    if len(p) > 2: dates[p[2]] = p[0].replace("-", "")
dates["0001653247-23-000072"] = "20231113"
for url in sorted(set(re.findall(r"\((https://www\.sec\.gov[^)]+)\)", rep))):
    a = url.split("/")[7]; adsh = f"{a[:10]}-{a[10:12]}-{a[12:]}"
    print("link", adsh, dates.get(adsh), "saved" if adsh in texts else "NOT SAVED", "OK" if dates.get(adsh, "9") <= "20231113" else "LATE")

# section placement checks
for adsh, phrase in [("0001653247-23-000072", "Jonathan Green, a board member"), ("0001653247-23-000072", "indicators of financial difficulty"),
                     ("0001653247-22-000158", "substantial doubt exists about the Company's ability")]:
    t = texts[adsh]; i = t.find(phrase); notes = re.findall(r"(?:^|\s)(\d{1,2})\. ([A-Z][A-Za-z ,&-]{3,40}?) ", t[:i])
    print(adsh, phrase[:30], "-> last note heading before:", notes[-1] if notes else None)

# numbers
chk = {"cash/debt": 3992 / 57089, "Oct burn months": 3992 / 662, "liab/assets": 80650 / 21585, "cur ratio": 10814 / 79520,
       "NI/assets": -34168 / 21585, "rev yoy": 11480 / 25141 - 1, "orders yoy": 4557 / 14156 - 1, "9M OCF change": 6022 / 21701 - 1,
       "equity": 21585 - 80650, "prior liab/assets": 86816 / 90651, "Q2 cur ratio": 12584 / 78638, "Q1 cur ratio": 15239 / 25452,
       "NI/TA multiple": 34168 / 21585, "CL/CA": 79520 / 10814}
for k, v in chk.items(): print(f"{k}: {v:.3f}")
body = re.sub(r"\(https?://[^)]+\)|!\[[^\]]*\]\([^)]+\)", "", rep)
print("words:", len(re.findall(r"\S+", body)))
