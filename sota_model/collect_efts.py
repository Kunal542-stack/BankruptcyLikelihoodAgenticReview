"""Collect warning signs from SEC full text search (EDGAR FTS), one month at a time, 2007 to 2026.

For each search and month it saves the filings that match (adsh, cik, form, date, 8-K items) to
data/efts/<search>/<YYYY-MM>.json, so it can stop and start again without asking twice.
"""
import json
import os
import sys
import time

import pandas as pd
import requests

HEADERS = {"User-Agent": "Pavanchytanya Dharmapuri dharmapuri.p@northeastern.edu"}
URL = "https://efts.sec.gov/LATEST/search-index"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "efts")

SEARCHES = {
    #8-K items: the label (1.03 bankruptcy) and warning events
    "item_1.03": {"q": '"Item 1.03"', "forms": "8-K"},   # bankruptcy or receivership
    "item_2.04": {"q": '"Item 2.04"', "forms": "8-K"},   # triggering events that speed up a debt (default)
    "item_3.01": {"q": '"Item 3.01"', "forms": "8-K"},   # notice of delisting or failing a listing rule
    "item_4.02": {"q": '"Item 4.02"', "forms": "8-K"},   # earlier financial statements can't be relied on
    "item_5.02": {"q": '"Item 5.02"', "forms": "8-K"},   # a director or officer leaves
    "item_2.06": {"q": '"Item 2.06"', "forms": "8-K"},   # material impairments
    #late filing notices
    "nt_filing": {"q": None, "forms": "NT 10-K,NT 10-Q"},
    #words in the 10-K and 10-Q text
    "going_concern": {"q": '"substantial doubt" "going concern"', "forms": "10-K,10-Q"},
    "forbearance": {"q": '"forbearance agreement"', "forms": "10-K,10-Q"},
    "minimum_bid_price": {"q": '"minimum bid price"', "forms": "10-K,10-Q"},
    "chapter_11": {"q": '"chapter 11"', "forms": "10-K,10-Q"},
    "strategic_alternatives": {"q": '"strategic alternatives"', "forms": "10-K,10-Q"},
    "material_weakness": {"q": '"material weakness"', "forms": "10-K,10-Q"},
    "not_in_compliance": {"q": '"not in compliance"', "forms": "10-K,10-Q"},
    "reverse_stock_split": {"q": '"reverse stock split"', "forms": "10-K,10-Q"},
    "restructuring_support_agreement": {"q": '"restructuring support agreement"', "forms": "10-K,10-Q"},
    #stricter phrases: "material weakness" alone also finds "we did not identify any material weakness"
    "identified_material_weakness": {"q": '"identified a material weakness"', "forms": "10-K,10-Q"},
    "covenant_not_in_compliance": {"q": '"not in compliance with" "covenants"', "forms": "10-K,10-Q"},
    "notice_of_default": {"q": '"notice of default"', "forms": "10-K,10-Q"},
    "debtor_in_possession": {"q": '"debtor-in-possession"', "forms": "10-K,10-Q"},
    "cease_operations": {"q": '"cease operations"', "forms": "10-K,10-Q"},
    "wind_down": {"q": '"wind down"', "forms": "10-K,10-Q"},
}


def get(params):
    #the search sometimes fails for a few minutes, so it waits longer each time (up to about 10 minutes in all)
    for attempt in range(12):
        try:
            r = requests.get(URL, params=params, headers=HEADERS, timeout=60)
            if r.status_code == 200:
                return r.json()["hits"]
        except Exception:
            pass
        time.sleep(5 + 10 * attempt)
    raise RuntimeError(f"failed: {params}")


def month_hits(search, start, end):
    params = {"forms": search["forms"], "startdt": start, "enddt": end, "dateRange": "custom"}
    if search["q"]:
        params["q"] = search["q"]
    rows, position = {}, 0
    while True:
        hits = get({**params, "from": position})
        for h in hits["hits"]:
            s = h["_source"]
            #a filing can be for a parent company and its subsidiaries together, so it can have more than one cik
            rows[s["adsh"]] = {"adsh": s["adsh"], "ciks": [int(c) for c in s["ciks"]], "form": s["form"],
                               "file_date": s["file_date"], "items": s.get("items", [])}
        position += len(hits["hits"])
        if len(hits["hits"]) == 0 or position >= hits["total"]["value"] or position >= 10000:
            if position >= 10000:
                print("  over 10000 hits, some missing:", start, file=sys.stderr)
            return list(rows.values())
        time.sleep(0.12)


months = pd.date_range("2007-01-01", "2026-10-31", freq="MS")
names = sys.argv[1:] or list(SEARCHES)
for name in names:
    os.makedirs(os.path.join(OUT, name), exist_ok=True)
    start_time, count = time.time(), 0
    for m in months:
        path = os.path.join(OUT, name, m.strftime("%Y-%m") + ".json")
        if os.path.exists(path):
            continue
        end = (m + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d")
        rows = month_hits(SEARCHES[name], m.strftime("%Y-%m-%d"), end)
        json.dump(rows, open(path, "w"))
        count += len(rows)
        time.sleep(0.12)
    print(f"{name}: {count} filings in {time.time() - start_time:.0f}s", flush=True)
print("all done", flush=True)
