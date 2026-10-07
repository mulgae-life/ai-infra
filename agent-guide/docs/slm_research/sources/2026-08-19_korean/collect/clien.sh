#!/bin/bash
for u in "$@"; do
echo "================================================================"
echo "$u"
curl -s -m 90 "https://r.jina.ai/$u" | python3 -c '
import sys,re
s=sys.stdin.read()
for ln in s.split("\n")[:6]:
    if ln.startswith("Title:"): print(ln)
i=s.find("\n### ")
if i<0: i=s.find("Markdown Content:")
j=s.find("새로운 댓글이 없습니다",i)
seg=s[i:j if j>i else i+30000]
seg=re.sub(r"!\[[^\]]*\]\([^)]*\)","",seg)
seg=re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", seg)
seg=seg.replace("1 2 3 4 5 입력","").replace("메모동기화","").replace("을 누르면 회원메모를 할 수 있습니다.","")
seg=re.sub(r"대댓글 _·_ 공감 신고|언급 _·_ 공감 신고|LINK","",seg)
seg=re.sub(r"IP [0-9]+\.♡\.[0-9.]+","",seg)
seg=re.sub(r"#\d{6,}","",seg)
seg=re.sub(r"\n{3,}","\n\n",seg)
print(seg[:14000])
'
done
