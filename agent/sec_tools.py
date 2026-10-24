

# %%
import os
import sys
import time

import pandas as pd
import requests

HEADERS = {"User-Agent": "Pavanchytanya Dharmapuri dharmapuri.p@northeastern.edu"}  # SEC asks for a name and email


def company_filings(cik):
    # the SEC keeps a list of every filing a company made, with the name of each filing's main document
    time.sleep(0.15)  # SEC allows at most 10 requests a second
    recent = requests.get(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json", headers=HEADERS, timeout=60).json()
    recent = recent["filings"]["recent"]
    return pd.DataFrame({"date": recent["filingDate"], "form": recent["form"], "adsh": recent["accessionNumber"],
                         "items": recent["items"], "document": recent["primaryDocument"]})


# %%
def filings(cik, before):
    # the company's filings made before the date, oldest first
    table = company_filings(cik)
    table = table[table["date"].str.replace("-", "") < str(before)]
    print(table.sort_values("date").to_csv(index=False))


def download(cik, adsh, folder):
    # save the filing's main document (the 10-K, 10-Q or 8-K itself) in the folder
    table = company_filings(cik)
    document = table.loc[table["adsh"] == adsh, "document"].iloc[0]
    time.sleep(0.15)
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/{document}"
    os.makedirs(folder, exist_ok=True)
    path = f"{folder}/{adsh}_{document}"
    with open(path, "wb") as f:
        f.write(requests.get(url, headers=HEADERS, timeout=60).content)
    print("saved", path)


# %%
if __name__ == "__main__":
    if sys.argv[1] == "filings":
        filings(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "download":
        download(sys.argv[2], sys.argv[3], sys.argv[4])
