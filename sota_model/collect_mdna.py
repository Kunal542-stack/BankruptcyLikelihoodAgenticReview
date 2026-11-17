"""Download every 10-K in long_dataframe_2009_to_2026.pkl and keep only its MD&A (Item 7) as text.

1. The main document of each 10-K, from the SEC submissions API (one request per company), saved in
   data/primary_documents.json.
2. Each 10-K's main document is downloaded, turned into plain text, and Item 7 (Management's Discussion and
   Analysis) is cut out and saved as data/mdna/<adsh>.txt.gz. The whole filing is not kept.

It can stop and start again: whatever is saved already is skipped. The SEC allows 10 requests a second, this
stays at about 8.

The 2009-2020 MD&A comes from EDGAR-CORPUS instead (collect_mdna_corpus.py), so this is run for the later years only:
python collect_mdna.py 2021 2022 2023 2024 2025 (no years = every 10-K).
"""
import gzip
import html
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

HEADERS = {"User-Agent": "Pavanchytanya Dharmapuri dharmapuri.p@northeastern.edu"}
HERE = os.path.dirname(os.path.abspath(__file__))
DOCS_PATH = os.path.join(HERE, "data", "primary_documents.json")
MDNA = os.path.join(HERE, "data", "mdna_sec")
LOG = os.path.join(HERE, "data", "mdna_status.csv")
os.makedirs(MDNA, exist_ok=True)

#at most 8 requests a second over all threads
lock, last = threading.Lock(), [0.0]


def get(url):
    for attempt in range(10):
        with lock:
            wait = last[0] + 0.125 - time.time()
            if wait > 0:
                time.sleep(wait)
            last[0] = time.time()
        try:
            r = requests.get(url, headers=HEADERS, timeout=90)
            if r.status_code == 200:
                return r
            if r.status_code == 404:
                return None
        except Exception:
            pass
        time.sleep(5 + 10 * attempt)
    return None


reports = pd.read_pickle(os.path.join(HERE, "long_dataframe_2009_to_2026.pkl"))[["adsh", "cik", "form", "filed_date"]]
reports = reports[reports["form"].str.startswith("10-K")]
#python collect_mdna.py --fill <file>: only the 10-Ks listed in the file (one adsh a line), saved again even if a file
#exists. Used for the 10-Ks EDGAR-CORPUS doesn't have or has with a short Item 7.
#Otherwise, only the filing years given on the command line, if any
FILL = set(open(sys.argv[2]).read().split()) if sys.argv[1:2] == ["--fill"] else set()
YEARS = [] if FILL else [int(y) for y in sys.argv[1:]]
if FILL:
    reports = reports[reports["adsh"].isin(FILL)]
elif YEARS:
    reports = reports[reports["filed_date"].dt.year.isin(YEARS)]
print(len(reports), "10-Ks from", reports["cik"].nunique(), "companies", flush=True)

#1. the main document of each filing
documents = json.load(open(DOCS_PATH)) if os.path.exists(DOCS_PATH) else {}
done_companies = set(documents.pop("_companies", []))
wanted = set(reports["adsh"])


def company_documents(cik):
    found = {}
    r = get(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json")
    if r is None:
        return found
    j = r.json()
    #the newest filings are in "recent", older ones in extra pages
    pages = [j["filings"]["recent"]]
    for f in j["filings"].get("files", []):
        older = get(f"https://data.sec.gov/submissions/{f['name']}")
        if older is not None:
            pages.append(older.json())
    for page in pages:
        for adsh, doc in zip(page["accessionNumber"], page["primaryDocument"]):
            if adsh in wanted:
                found[adsh] = doc
    return found


#companies not looked up yet, or (in --fill) any company with a wanted 10-K whose document isn't known yet
todo = [c for c in reports["cik"].unique() if str(c) not in done_companies]
if FILL:
    todo = list(reports.loc[~reports["adsh"].isin(documents), "cik"].unique())
start = time.time()
with ThreadPoolExecutor(6) as pool:
    for i, (cik, found) in enumerate(zip(todo, pool.map(company_documents, todo))):
        documents.update(found)
        done_companies.add(str(cik))
        if i % 500 == 0 or i == len(todo) - 1:
            json.dump({**documents, "_companies": sorted(done_companies)}, open(DOCS_PATH, "w"))
            print(f"companies {i + 1}/{len(todo)}  documents {len(documents)}  {time.time() - start:.0f}s", flush=True)
json.dump({**documents, "_companies": sorted(done_companies)}, open(DOCS_PATH, "w"))

#2. download and cut out the MD&A
TAG = re.compile(r"<[^>]+>")
HIDDEN = re.compile(r"<(script|style|ix:header)[^>]*>.*?</\1>", re.S | re.I)
START = re.compile(r"item\s*7\s*[\.\:\-–—]?\s*management[’'`s]*\s*discussion", re.I)
END = re.compile(r"item\s*7a\s*[\.\:\-–—]?\s*quantitative|item\s*8\s*[\.\:\-–—]?\s*financial\s+statements", re.I)
MDA_WORDS = re.compile(r"management[’'`s]*\s*discussion\s+and\s+analysis", re.I)


def to_text(raw):
    text = HIDDEN.sub(" ", raw)
    text = re.sub(r"<(br|p|div|tr|li|h\d)[^>]*>", "\n", text, flags=re.I)
    text = html.unescape(TAG.sub(" ", text))
    return re.sub(r"[ \t\xa0]+", " ", text)


def cut_mdna(text):
    #the table of contents also says "Item 7. Management's Discussion", so the longest stretch from a start to
    #the next end is the real section
    ends = [m.start() for m in END.finditer(text)]
    best = ""
    for m in START.finditer(text):
        after = [e for e in ends if e > m.end()]
        piece = text[m.start(): after[0] if after else m.start() + 400000]
        if len(piece) > len(best):
            best = piece
    if len(best) >= 3000:
        return best, "item 7"
    #some 10-Ks put the MD&A in another place (for example an exhibit), then the longest stretch after
    #"management's discussion and analysis"
    for m in MDA_WORDS.finditer(text):
        piece = text[m.start(): m.start() + 200000]
        after = [e for e in ends if e > m.end()]
        if after:
            piece = text[m.start(): after[0]]
        if len(piece) > len(best):
            best = piece
    if len(best) >= 3000:
        return best, "md&a words"
    return text[:200000], "whole document"


def one(row):
    adsh, cik = row
    path = os.path.join(MDNA, adsh + ".txt.gz")
    if os.path.exists(path) and adsh not in FILL:
        return None
    doc = documents.get(adsh)
    if not doc:
        return adsh, "no document", 0, 0
    r = get(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/{doc}")
    if r is None:
        return adsh, "download failed", 0, 0
    raw = r.content.decode("utf-8", errors="ignore") if not doc.lower().endswith(".txt") else r.text
    mdna, source = cut_mdna(to_text(raw))
    mdna = re.sub(r"\s*\n\s*", "\n", mdna)[:400000]
    with gzip.open(path, "wt") as f:
        f.write(mdna)
    return adsh, source, len(r.content), len(mdna)


rows = list(zip(reports["adsh"], reports["cik"]))
start, seen, status = time.time(), 0, []
log_exists = os.path.exists(LOG)
with open(LOG, "a") as log, ThreadPoolExecutor(8) as pool:
    if not log_exists:
        log.write("adsh,source,bytes,mdna_chars\n")
    for result in pool.map(one, rows):
        seen += 1
        if result:
            log.write(",".join(map(str, result)) + "\n")
            status.append(result)
        if seen % 1000 == 0:
            log.flush()
            got = sum(s[2] for s in status)
            print(f"10-Ks {seen}/{len(rows)}  downloaded {got / 1e9:.1f} GB  {time.time() - start:.0f}s", flush=True)
print("all done", flush=True)
