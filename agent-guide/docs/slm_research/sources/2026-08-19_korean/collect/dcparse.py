import re,sys,html
t=open(sys.argv[1],encoding='utf-8',errors='replace').read()
def clean(s):
    s=re.sub(r'<(br|/p|/div)\s*/?>','\n',s)
    s=re.sub(r'<img[^>]*>','[이미지]',s)
    s=re.sub(r'<[^>]+>','',s)
    s=html.unescape(s).replace('\xa0',' ')
    s=re.sub(r'[ \t]+',' ',s)
    return re.sub(r'\n{3,}','\n\n',s).strip()
def g(p):
    m=re.search(p,t,re.S); return clean(m.group(1)) if m else "?"
print("제목:",g(r'<span class="title_subject">(.*?)</span>'))
print("작성일:",g(r'<span class="gall_date"[^>]*>(.*?)</span>'))
print("갤러리:",g(r'<h2[^>]*>\s*<a[^>]*>(.*?)</a>'))
i=t.find('class="write_div"')
if i>0:
    j=t.find('</div>',i)
    print("\n[본문]\n"+clean(t[i+17:j])[:7000])
