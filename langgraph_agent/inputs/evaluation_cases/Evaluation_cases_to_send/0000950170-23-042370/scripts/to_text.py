"""Convert saved filings HTML to text, keeping each table row on one line. Usage: python -I to_text.py <filings_dir>"""
import os
import re
import sys

import warnings
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

folder = sys.argv[1]
for name in sorted(os.listdir(folder)):
    if not name.endswith(".htm"):
        continue
    soup = BeautifulSoup(open(os.path.join(folder, name), "rb").read(), "lxml")
    for tag in soup.find_all(["ix:header", "script", "style"]):
        tag.decompose()
    for d in soup.find_all(style=re.compile(r"display:\s*none")):
        d.decompose()
    for t in soup.find_all(re.compile(r"^(ix:|span$|font$|a$|b$|i$|strong$|em$|sup$|u$)")):
        t.unwrap()
    soup.smooth()
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        cells = [c for c in cells if c]
        tr.replace_with(soup.new_string("\n" + " | ".join(cells) + "\n"))
    text = soup.get_text("\n")
    text = re.sub(r"[ \t\xa0]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    open(os.path.join(folder, name[:-4] + ".txt"), "w").write(text)
    print(name, len(text))
