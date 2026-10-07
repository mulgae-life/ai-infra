#!/bin/bash
for u in "$@"; do
echo "================================================================"
echo "$u"
curl -s -m 90 "https://r.jina.ai/$u" | python3 -c "
import sys,re
s=sys.stdin.read()
# 제목/URL 라인
for ln in s.split('\n')[:6]:
    if ln.startswith('Title:') or ln.startswith('URL Source:'): print(ln)
i=s.find('Markdown Content:')
s=s[i:] if i>0 else s
# 본문 시작 추정
m=re.search(r'\n#{1,3} .*\n', s)
if m: s=s[m.start():]
s=re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)
s=re.sub(r'!\[[^\]]*\]', '', s)
s=re.sub(r'\n{3,}','\n\n',s)
print(s[:14000])
"
done
