#!/bin/bash
UA="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
while read -r u; do
  out=$(curl -sL -m 20 -A "$UA" -H "Referer: https://m.dcinside.com/" "https://m.dcinside.com/board/$u" | python3 -c "
import re,html,sys
t=sys.stdin.read()
t=re.sub(r'<script.*?</script>','',t,flags=re.S); t=re.sub(r'<style.*?</style>','',t,flags=re.S)
t=html.unescape(re.sub(r'<[^>]+>','\n',t))
lines=[l.strip() for l in t.split('\n') if l.strip()]
# 제목은 [일반] 뒤, 본문은 조회수 이후
try: s=next(i for i,l in enumerate(lines) if l.startswith('[')and len(l)<12)
except StopIteration: s=0
print('\n'.join(lines[s:s+70]))
")
  # 한국어 품질 관련 키워드가 있는 글만 출력
  if echo "$out" | grep -qE "한국어|번역|문장력|말투|어투|한글"; then
     echo "########## $u"; echo "$out" | grep -vE "^(삭제|닫기|갤러리|마이너|설정|new|연관|글쓰기|스크랩|갤로그 가기|추천검색|목록보기|공유|신고|펌 0|실베추|새로고침|본문|최신순|등록순|답글순|이미지|등록|만두|보이스리플|댓글 위로|비추천하기|개념글 추천하기|고정닉 추천수|디시콘|이벤트|게임|더보기|인물갤|미니갤|뒤로가기|최근 검색어|전체 삭제|검색어 저장|메인에서|이용자 메모|차단 설정|자동 짤방|머리말|AI 이미지|외부 링크|신뢰할 수 있는|수정|미니|추천$|[0-9]+$)" | head -30; echo
  fi
done
