import re,html,sys
def clean(x):
    x=re.sub(r'<br\s*/?>','\n',x)
    x=re.sub(r'</p>','\n',x)
    x=re.sub(r'<[^>]+>','',x)
    return html.unescape(x).strip()
for f in sys.argv[1:]:
    s=open(f,encoding='utf-8',errors='ignore').read()
    s=re.sub(r'<script.*?</script>','',s,flags=re.S)
    s=re.sub(r'<style.*?</style>','',s,flags=re.S)
    print('='*70)
    print('FILE:',f)
    t=re.search(r'<title>(.*?)</title>',s,flags=re.S)
    if t: print('TITLE:',clean(t.group(1)))
    m=re.search(r'<div class="thum-txtin"[^>]*>(.*?)</div>\s*</div>',s,flags=re.S) or \
      re.search(r'<div class="thum-txtin"[^>]*>(.*?)$',s,flags=re.S)
    if m:
        body=clean(m.group(1))
        print('--- BODY ---'); print(body[:4000])
    else:
        print('!! body not found')
    cs=re.findall(r'<p class="txt">(.*?)</p>',s,flags=re.S)
    if cs:
        print('--- COMMENTS (%d) ---'%len(cs))
        for c in cs:
            c=clean(c)
            if c: print(' *',c)
