#!/bin/bash
UA="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
fetch(){ curl -sL -m 25 -A "$UA" -H "Accept-Language: ko-KR,ko;q=0.9" -H "Referer: https://m.dcinside.com/" "$1"; }
strip(){ python3 -c "
import re,html,sys
t=sys.stdin.read()
t=re.sub(r'<script.*?</script>','',t,flags=re.S); t=re.sub(r'<style.*?</style>','',t,flags=re.S)
t=html.unescape(re.sub(r'<[^>]+>','\n',t))
t=re.sub(r'\n\s*\n+','\n',t)
print(t)
"; }
fetch "$1" | strip
