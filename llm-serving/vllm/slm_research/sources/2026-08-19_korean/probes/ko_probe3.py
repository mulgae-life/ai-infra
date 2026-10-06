import json, urllib.request
URL="http://127.0.0.1:5015/v1/chat/completions"
T=[
 ("문학 번역", "다음을 한국어 소설 문체로 번역하세요. 직역 금지:\n\"It was a bright cold day in April, and the clocks were striking thirteen. Winston Smith, his chin nuzzled into his breast in an effort to escape the vile wind, slipped quickly through the glass doors of Victory Mansions.\""),
 ("일상 대사 번역", "다음 대사를 자연스러운 한국어 구어체로 옮기세요:\n\"Look, I'm not saying you're wrong. I'm just saying maybe we should sleep on it before we do anything stupid.\""),
 ("사물존대 재확인", "'커피 나오셨습니다', '사이즈가 없으십니다', '이 제품은 품절이십니다' — 이 세 문장은 올바른 높임 표현입니까? 그렇다/아니다로 먼저 답하고 이유를 쓰세요."),
]
for n,p in T:
    b=json.dumps({"model":"Qwen3.8-27B-FP8","messages":[{"role":"user","content":p}],
        "max_tokens":400,"temperature":0.7,"chat_template_kwargs":{"enable_thinking":False}}).encode()
    try:
        r=json.load(urllib.request.urlopen(urllib.request.Request(URL,b,{"Content-Type":"application/json"}),timeout=180))
        print(f"\n━━━ [{n}] ━━━\n{r['choices'][0]['message']['content'].strip()}")
    except Exception as e: print(f"\n━━━ [{n}] 실패: {e}")
