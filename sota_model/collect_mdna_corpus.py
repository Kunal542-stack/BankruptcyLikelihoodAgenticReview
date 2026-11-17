"""Get the MD&A (Item 7) of our 10-Ks for fiscal years 2008-2020 from EDGAR-CORPUS on Hugging Face, instead of
downloading the filings.

EDGAR-CORPUS (Loukas et al., 2021, https://huggingface.co/datasets/eloukas/edgar-corpus) has the 10-Ks of 1993 to 2020,
already split into their items. Each record has the company's cik, a year, and section_1 to section_15; section_7 is the
MD&A.

The corpus year is the FISCAL year of the 10-K, not the year it was filed: the record for year 2012 describes fiscal
2012 and was filed in 2013. A first version of this script matched on the filing year, which gave most 10-Ks the next
year's MD&A (future text, so leakage). Its output was moved to data/mdna_leaky_corpus_old/ and is not used.

How it is done now:
1. The corpus files for each year (train, validate and test .jsonl) are read straight from Hugging Face, line by line,
   so the 20 GB of files are never saved.
2. A record is matched to one of our 10-Ks (form 10-K in long_dataframe_2009_to_2026.pkl) by cik and fiscal year,
   where the fiscal year is the year of the 10-K's period end (ddate). If a company has two 10-Ks for the same fiscal
   year, the record goes to the one filed first.
3. A check against future text: the latest year in the text's "year ended <date>, 20XX" phrases must not be after the
   10-K's fiscal year. Records that fail are not used (the 10-K can be filled from the SEC with collect_mdna.py).
4. The MD&A of accepted records is saved as data/mdna_corpus/<adsh>.txt.gz, with one line per matched record in
   data/mdna_corpus_status.csv. Years already done are skipped when it runs again.
"""
import gzip
import json
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
MDNA = os.path.join(HERE, "data", "mdna_corpus")
STATUS = os.path.join(HERE, "data", "mdna_corpus_status.csv")
DONE = os.path.join(HERE, "data", "mdna_corpus_years_done.txt")
URL = "https://huggingface.co/datasets/eloukas/edgar-corpus/resolve/main/{year}/{part}.jsonl"
YEARS = [int(y) for y in sys.argv[1:]] or list(range(2008, 2021))
YEAR_ENDED = re.compile(r"(?:year|years|fiscal year|fiscal years)\s+ended\s+[A-Z][a-z]+\s+\d{1,2},\s+(20\d\d)")
#one process per year (reading the JSON is CPU work, so threads would share one core); 8 of the 11 cores
PROCESSES = 8
wanted = {}


def start_worker(our_10ks):
    global wanted
    wanted = our_10ks


def our_10ks():
    reports = pd.read_pickle(os.path.join(HERE, "long_dataframe_2009_to_2026.pkl"))[["adsh", "cik", "form", "ddate", "filed_date"]]
    reports = reports[reports["form"] == "10-K"].sort_values("filed_date")
    reports["fiscal_year"] = reports["ddate"].astype(int) // 10000
    #(cik, fiscal year) -> the first 10-K filed for that fiscal year
    return reports.drop_duplicates(["cik", "fiscal_year"]).set_index(["cik", "fiscal_year"])["adsh"].to_dict()


def one_year(year):
    rows, records, start = [], 0, time.time()
    for part in ["train", "validate", "test"]:
        with requests.get(URL.format(year=year, part=part), stream=True, timeout=120) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                records += 1
                record = json.loads(line)
                adsh = wanted.get((int(record["cik"]), int(record["year"])))
                if adsh is None:
                    continue
                mdna = (record.get("section_7") or "").strip()
                years_in_text = [int(y) for y in YEAR_ENDED.findall(mdna[:100000])]
                latest = max(years_in_text) if years_in_text else ""
                if latest and latest > int(record["year"]):
                    status = "rejected: text mentions a later year"
                elif len(mdna) < 3000:
                    status = "rejected: short or empty item 7"
                else:
                    status = "ok"
                    with gzip.open(os.path.join(MDNA, adsh + ".txt.gz"), "wt") as f:
                        f.write(mdna[:400000])
                rows.append((adsh, record["filename"], record["year"], latest, status, len(mdna)))
    return year, records, rows, time.time() - start


if __name__ == "__main__":
    os.makedirs(MDNA, exist_ok=True)
    done_years = set(open(DONE).read().split()) if os.path.exists(DONE) else set()
    todo = [y for y in YEARS if str(y) not in done_years]
    with ProcessPoolExecutor(PROCESSES, initializer=start_worker, initargs=(our_10ks(),)) as pool:
        for year, records, rows, seconds in pool.map(one_year, todo):
            new = not os.path.exists(STATUS)
            with open(STATUS, "a") as f:
                if new:
                    f.write("adsh,corpus_file,corpus_year,latest_year_in_text,status,mdna_chars\n")
                for row in rows:
                    f.write(",".join(map(str, row)) + "\n")
            open(DONE, "a").write(f"{year}\n")
            ok = sum(r[4] == "ok" for r in rows)
            print(f"{year}: {records} corpus 10-Ks read, {len(rows)} matched to ours, {ok} accepted, {seconds:.0f}s", flush=True)
    print("all done", flush=True)
