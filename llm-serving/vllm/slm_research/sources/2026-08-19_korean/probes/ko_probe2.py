# 커뮤니티가 지적하는 한국어 약점 축을 그대로 문항화
import json, urllib.request
URL="http://127.0.0.1:5015/v1/chat/completions"
T=[
 ("존댓말 등급", "할머니께 세배하며 드리는 말과, 편의점 알바생에게 하는 말과, 친한 동생에게 하는 말을 각각 한 문장씩 쓰세요. 상황은 모두 '새해 인사'입니다."),
 ("한자 혼입", "'경청'과 '傾聽'처럼 한자어를 쓸 때 한자를 병기해야 할까요? 신문 기사체로 세 문장 쓰세요."),
 ("문학적 표현", "가을 저녁 무렵 시골 버스 정류장 풍경을 소설 도입부처럼 세 문장으로 묘사하세요."),
 ("속담/관용구", "'울며 겨자 먹기'와 '눈치가 빠르다'를 각각 자연스러운 예문에 넣어 쓰세요."),
 ("맞춤법 교정", "다음을 고치세요: '오랫만에 만난 친구와 회포를 풀었다. 왠지 모르게 기분이 좋아져서 몇일 더 머물기로 했다.'"),
 ("높임 오류 탐지", "다음 문장이 어색한 이유를 설명하세요: '고객님, 주문하신 커피 나오셨습니다.'"),
]
for n,p in T:
    b=json.dumps({"model":"Qwen3.8-27B-FP8","messages":[{"role":"user","content":p}],
        "max_tokens":400,"temperature":0.7,"chat_template_kwargs":{"enable_thinking":False}}).encode()
    try:
        r=json.load(urllib.request.urlopen(urllib.request.Request(URL,b,{"Content-Type":"application/json"}),timeout=180))
        print(f"\n━━━ [{n}] ━━━\n{r['choices'][0]['message']['content'].strip()}")
    except Exception as e: print(f"\n━━━ [{n}] 실패: {e}")
