"""Convert saved filings (HTML) to plain text, keeping each table row on one line.
Usage: python -I to_text.py <filings_dir> <out_dir>"""
import sys, os, re
from bs4 import BeautifulSoup

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
for f in sorted(os.listdir(src)):
    if not f.endswith(('.htm', '.html')):
        continue
    soup = BeautifulSoup(open(os.path.join(src, f), 'rb').read(), 'lxml')
    for t in soup.find_all(['script', 'style']):
        t.decompose()
    for t in soup.find_all(lambda x: x.name and ':' in x.name and x.name.startswith('ix:header')):
        t.decompose()
    for d in soup.find_all(style=re.compile(r'display:\s*none', re.I)):
        d.decompose()
    for tr in soup.find_all('tr'):
        cells = [re.sub(r'\s+', ' ', td.get_text(' ', strip=True)) for td in tr.find_all(['td', 'th'])]
        cells = [c for c in cells if c and c not in ('$', ')', '%')]
        tr.replace_with(soup.new_string('\n' + ' | '.join(cells) + '\n'))
    for b in soup.find_all(['p', 'div', 'br', 'li', 'h1', 'h2', 'h3', 'h4', 'table']):
        b.insert_after(soup.new_string('\n'))
    txt = soup.get_text()
    txt = txt.replace('\xa0', ' ')
    txt = re.sub(r'[ \t]+', ' ', txt)
    txt = re.sub(r'\n\s*\n+', '\n', txt)
    open(os.path.join(out, f.rsplit('.', 1)[0] + '.txt'), 'w').write(txt)
    print(f, len(txt))
