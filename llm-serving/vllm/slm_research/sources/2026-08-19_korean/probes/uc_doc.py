# 용도 B: 범용 문서 어시스턴트 — 요약/톤변환/구조화추출/오류검출
import json, urllib.request
URL="http://127.0.0.1:5015/v1/chat/completions"
DOC="""[사내 공지] 2026년 하반기 재택근무 제도 변경 안내

인사팀입니다. 2026년 9월 1일부로 재택근무 제도가 아래와 같이 변경됩니다.

1. 주 2회였던 재택근무 한도를 주 3회로 확대합니다. 단, 신규 입사 후 3개월 미만인 직원은
   기존과 동일하게 주 1회로 제한합니다.
2. 재택근무일은 전주 금요일 오후 6시까지 그룹웨어에서 신청해야 하며, 팀장 승인 후 확정됩니다.
   미신청 시 출근이 원칙입니다.
3. 고객 응대 부서(콜센터, 창구영업)는 이번 확대 대상에서 제외됩니다.
4. 재택근무 중에도 코어타임(오전 10시~오후 4시)에는 즉시 연락이 가능해야 합니다.
5. 월 1회 이상 전사 오프라인 회의가 있는 날은 재택근무를 신청할 수 없습니다.

문의: 인사팀 김지훈 대리 (내선 2317)"""
Q=[("3줄 요약","위 공지를 핵심만 3줄로 요약하세요."),
   ("톤 변환","위 공지를 신입사원도 이해하기 쉽게, 친근한 말투로 다시 쓰세요."),
   ("구조화 추출","위 공지에서 '대상'과 '조건'을 JSON 배열로 추출하세요. 키는 group, limit, note."),
   ("함정 질문","입사 2개월 차 콜센터 직원인데 다음 주에 주 3회 재택 가능한가요?")]
for n,q in Q:
    b=json.dumps({"model":"Qwen3.8-27B-FP8","messages":[{"role":"user","content":f"{DOC}\n\n---\n{q}"}],
        "max_tokens":500,"temperature":0.3,"chat_template_kwargs":{"enable_thinking":False}}).encode()
    r=json.load(urllib.request.urlopen(urllib.request.Request(URL,b,{"Content-Type":"application/json"}),timeout=240))
    print(f"\n━━━ [{n}]\n{r['choices'][0]['message']['content'].strip()[:650]}")
