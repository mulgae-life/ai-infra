import re,html,sys,subprocess,urllib.parse
UA="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
def fetch(url):
    return subprocess.run(["curl","-sL","-A",UA,"-H","Referer: https://m.dcinside.com/",url],capture_output=True,text=True).stdout
q=sys.argv[1]
page=sys.argv[2] if len(sys.argv)>2 else "1"
url="https://search.dcinside.com/post/p/%s/sort/latest/q/%s"%(page,urllib.parse.quote(q))
s=fetch(url)
i=s.find('sch_result_list')
if i<0:
    print("NO RESULTS BLOCK"); sys.exit()
j=s.find('</ul>',i)
seg=s[i:j if j>0 else i+40000]
# each li
for li in re.split(r'<li',seg)[1:]:
    m=re.search(r'href="([^"]*board/view[^"]*)"',li)
    if not m: continue
    txt=html.unescape(re.sub(r'<[^>]+>',' ',li))
    txt=re.sub(r'\s+',' ',txt).strip()
    print(m.group(1))
    print("   ",txt[:400])
    print()
