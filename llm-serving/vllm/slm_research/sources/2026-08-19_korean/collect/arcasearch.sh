#!/bin/bash
kw=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$1")
p=${2:-1}
curl -s -m 90 "https://r.jina.ai/https://arca.live/b/alpaca?p=$p&target=all&keyword=$kw" | python3 -c "
import sys,re
s=sys.stdin.read()
i=s.find('Markdown Content:')
s=s[i:]
seen=set()
for m in re.finditer(r'\[([^\]]{4,160})\]\((https://arca\.live/b/alpaca/\d+)[^)]*\)', s):
    u=m.group(2)
    if u in seen: continue
    seen.add(u)
    print(u, '|', m.group(1))
"
