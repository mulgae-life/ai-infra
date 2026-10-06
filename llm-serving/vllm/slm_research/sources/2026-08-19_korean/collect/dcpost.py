import re,html,sys,subprocess
UA="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
CUT_B=["개념글 추천하기","추천검색"]
CUT_C=["'ㅇㅇ'는 갤러리에서","갤닉네임입니다","새로고침\n 갤닉네임"]
def clean(s):
    s=re.sub(r'<(script|style)[^>]*>.*?</\1>','',s,flags=re.S)
    s=re.sub(r'<br\s*/?>','\n',s)
    s=re.sub(r'</(p|div|li|dd|dt|h\d|tr)>','\n',s)
    s=re.sub(r'<[^>]+>','',s)
    s=html.unescape(s)
    s=re.sub(r'[ \t]+',' ',s)
    s=re.sub(r'\n\s*\n+','\n',s)
    return s.strip()
def cut(t,marks):
    for m in marks:
        i=t.find(m)
        if i>0: t=t[:i]
    return t.strip()
for arg in sys.argv[1:]:
    if arg.startswith('http'):
        url=arg
    elif ':' in arg:
        gall,no=arg.split(':')
        url="https://m.dcinside.com/board/%s/%s"%(gall,no)
    s=subprocess.run(["curl","-sL","-A",UA,"-H","Referer: https://m.dcinside.com/",url],capture_output=True,text=True).stdout
    print("="*80); print(url)
    t=re.search(r'<title>(.*?)</title>',s,flags=re.S)
    if t: print("TITLE:",clean(t.group(1)))
    d=re.search(r'class="ginfo2".*?</ul>',s,flags=re.S)
    if d: print("INFO:",clean(d.group(0)).replace('class="ginfo2">','').strip())
    i=s.find('thum-txtin')
    if i>=0:
        print("--- BODY ---"); print(cut(clean(s[i:i+30000]).replace('thum-txtin">',''),CUT_B)[:20000])
    ci=s.find('all-comment-lst')
    if ci>=0:
        print("--- COMMENTS ---"); print(cut(clean(s[ci:ci+60000]).replace('all-comment-lst" >',''),CUT_C)[:8000])
