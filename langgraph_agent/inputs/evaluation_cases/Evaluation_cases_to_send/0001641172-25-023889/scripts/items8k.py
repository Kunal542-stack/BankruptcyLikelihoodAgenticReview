import sys,re
for f in sys.argv[1:]:
    t = re.sub(r'\s+',' ',open(f).read())
    m = re.search(r'Item\s*(1\.01|1\.02|2\.03|2\.04|3\.01|4\.01|5\.02)', t[1500:])
    print('===', f.split('/')[-1][:20]); print(t[1500+m.start():1500+m.start()+1400] if m else t[1500:2500]); print()
