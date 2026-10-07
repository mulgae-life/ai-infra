#!/bin/bash
for u in "$@"; do
echo "================================================================"
echo "$u"
curl -s -m 90 "https://r.jina.ai/$u" | python3 -c "
import sys,re
s=sys.stdin.read()
for ln in s.split('\n')[:6]:
    if ln.startswith('Title:'): print(ln)
i=s.find('Markdown Content:')
s=s[i:] if i>0 else s
s=re.sub(r'!\[[^\]]*\]\([^)]*\)','',s)
s=re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)
s=re.sub(r'\n{3,}','\n\n',s)
print(s[:12000])
"
done
