"""Clean the MD&A texts we cut out of the SEC filings ourselves (data/mdna_sec/) so they look like the EDGAR-CORPUS ones.

Compared with the corpus on the 9,229 10-Ks that have both kinds of text, about 1 in 5 of our cuts ran too long: they
started at the table of contents' "Item 7" line instead of the real heading, or went on past Item 7A into Item 8. And
some are not the MD&A at all (the start of the whole 10-K, kept when no MD&A was found). So:

1. Start: the LAST "Item 7. Management's Discussion..." heading in the text that is followed by at least 3,000
   characters before the end (this skips the table of contents).
2. End: the first heading after that, at the start of a line, that is Item 7A, "Quantitative and Qualitative
   Disclosures About Market Risk" or "Item 8. Financial Statements".
3. Texts kept as "whole document" (no MD&A found) are dropped, so those 10-Ks have no text instead of the wrong text.

Tested on 400 of the shared 10-Ks: the share of texts more than 1.5 times longer than the corpus one fell from 19% to
6%, and in the worst 10% the share of our words that are also in the corpus text rose from 43% to 90%.
The result is saved as data/mdna_sec_clean/<adsh>.txt.gz, with one line per text in data/mdna_sec_clean_status.csv.
"""
import glob
import gzip
import os
import re
from concurrent.futures import ProcessPoolExecutor

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "data", "mdna_sec")
OUT = os.path.join(HERE, "data", "mdna_sec_clean")
START = re.compile(r"item\s*7\s*[\.\:\-–—]?\s*management[’'`s]*\s*discussion", re.I)
END = re.compile(r"(?m)^[ \t]*(?:item\s*7a\b|quantitative\s+and\s+qualitative\s+disclosures?\s+about\s+market\s+risk"
                 r"|item\s*8\s*[\.\:\-–—]?\s*(?:consolidated\s+)?financial\s+statements)", re.I)


def cut(text):
    starts = [m.start() for m in START.finditer(text)] or [0]
    for start in reversed(starts):
        end = END.search(text, start + 3000)
        piece = text[start:end.start()] if end else text[start:]
        if len(piece) >= 3000:
            return piece, "cut from the last heading"
    return text, "unchanged"


def clean(path):
    adsh = os.path.basename(path)[:-7]
    with gzip.open(path, "rt") as f:
        text = f.read()
    if how.get(adsh) == "whole document":
        return adsh, "dropped: whole document", len(text), 0
    cleaned, result = cut(text)
    with gzip.open(os.path.join(OUT, adsh + ".txt.gz"), "wt") as f:
        f.write(cleaned)
    return adsh, result, len(text), len(cleaned)


status = pd.read_csv(os.path.join(HERE, "data", "mdna_status.csv"))
status = status[status["adsh"].str.match(r"^\d{10}-\d{2}-\d{6}$", na=False)].drop_duplicates("adsh", keep="last")
how = status.set_index("adsh")["source"].to_dict()

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for old in glob.glob(os.path.join(OUT, "*.txt.gz")):
        os.remove(old)
    with ProcessPoolExecutor(8) as pool:
        rows = list(pool.map(clean, sorted(glob.glob(os.path.join(IN, "*.txt.gz"))), chunksize=200))
    out = pd.DataFrame(rows, columns=["adsh", "result", "chars_before", "chars_after"])
    out.to_csv(os.path.join(HERE, "data", "mdna_sec_clean_status.csv"), index=False)
    print(out["result"].value_counts().to_string(), flush=True)
    print("median length before", int(out["chars_before"].median()), "after", int(out.loc[out["chars_after"] > 0, "chars_after"].median()), flush=True)
    print("all done", flush=True)
