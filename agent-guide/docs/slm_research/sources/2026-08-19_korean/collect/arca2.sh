#!/bin/bash
for u in "$@"; do
echo "================================================================"
echo "$u"
curl -s -m 90 "https://r.jina.ai/$u" | python3 -c '
import sys,re
s=sys.stdin.read()
for ln in s.split("\n")[:6]:
    if ln.startswith("Title:"): print(ln)
m=re.search(r"Like \d+ Dislike \d+ Comment \d+ Views [\d,]+ Uploaded date [\d\- :]+",s)
i=m.start() if m else s.find("Markdown Content:")
j=s.find("전체글개념글",i)
seg=s[i:j if j>i else i+20000]
seg=re.sub(r"!\[[^\]]*\]\([^)]*\)","",seg)
seg=re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", seg)
seg=seg.replace("Unfold ▼","").replace("!Image","")
seg=re.sub(r"\n{3,}","\n\n",seg)
print(seg[:12000])
'
done
