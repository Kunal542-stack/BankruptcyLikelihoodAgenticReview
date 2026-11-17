#!/bin/zsh
# downloads the SEC Financial Statement Data Sets 2009q1 to 2022q4 into data/zips (put the 2023+ zips we already have there too)
cd "$(dirname $0)/data/zips"
for y in {2009..2022}; do for q in 1 2 3 4; do
  f=${y}q${q}.zip
  [ -s $f ] && continue
  curl -sf -A "Pavanchytanya Dharmapuri dharmapuri.p@northeastern.edu" -o $f.part "https://www.sec.gov/files/dera/data/financial-statement-data-sets/$f" && mv $f.part $f && echo "got $f $(du -h $f | cut -f1)" || echo "FAILED $f"
  sleep 1
done; done
echo "all done"
