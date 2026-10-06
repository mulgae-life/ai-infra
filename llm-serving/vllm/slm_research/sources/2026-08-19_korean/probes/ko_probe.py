import json, urllib.request
URL="http://127.0.0.1:5015/v1/chat/completions"
PROMPTS=[
 ("높임말/응대", "고객이 '보험금 왜 이렇게 늦게 나와요?'라고 화가 난 상태로 물었습니다. 상담사로서 2~3문장으로 응대하세요."),
 ("번역체 검사", "다음을 자연스러운 한국어로 옮기세요: 'The proposed approach leverages a hybrid architecture that enables significant improvements in throughput without compromising latency.'"),
 ("구어체 생성", "친구에게 약속을 미루자고 카톡 보내듯 3문장으로 써줘. 미안한 티는 내되 너무 딱딱하지 않게."),
 ("문법/맞춤법", "다음 문장의 어색한 부분을 고치고 이유를 한 줄로 설명하세요: '이번 회의를 통해 저희는 많은 인사이트를 얻을 수 있었던 것 같습니다.'"),
]
for name, p in PROMPTS:
    body=json.dumps({"model":"Qwen3.8-27B-FP8","messages":[{"role":"user","content":p}],
        "max_tokens":300,"temperature":0.7,
        "chat_template_kwargs":{"enable_thinking":False}}).encode()
    req=urllib.request.Request(URL, body, {"Content-Type":"application/json"})
    try:
        r=json.load(urllib.request.urlopen(req, timeout=180))
        print(f"\n━━━ [{name}] ━━━\n{r['choices'][0]['message']['content'].strip()}")
    except Exception as e:
        print(f"\n━━━ [{name}] 실패: {e}")
