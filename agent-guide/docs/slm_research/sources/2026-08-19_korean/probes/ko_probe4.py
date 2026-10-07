# 커뮤니티 최다 지적: 한자/중국어 혼입 — 장문 생성에서 실제로 나오는지 계량
import json, re, urllib.request
URL="http://127.0.0.1:5015/v1/chat/completions"
P=[("에세이","'기다림'을 주제로 한국어 수필을 600자 내외로 쓰세요."),
   ("설명문","한국의 전세 제도를 모르는 사람에게 설명하는 글을 600자 내외로 쓰세요."),
   ("대화문","시장에서 물건값을 흥정하는 상인과 손님의 대화를 20줄 쓰세요."),
   ("사내공지","연말 정산 서류 제출을 안내하는 사내 공지문을 쓰세요.")]
HANJA=re.compile(r'[一-鿿]'); KANA=re.compile(r'[぀-ヿ]')
for n,p in P:
    b=json.dumps({"model":"Qwen3.8-27B-FP8","messages":[{"role":"user","content":p}],
        "max_tokens":900,"temperature":0.8,"chat_template_kwargs":{"enable_thinking":False}}).encode()
    try:
        r=json.load(urllib.request.urlopen(urllib.request.Request(URL,b,{"Content-Type":"application/json"}),timeout=240))
        t=r['choices'][0]['message']['content']
        h=HANJA.findall(t); k=KANA.findall(t)
        print(f"[{n}] {len(t)}자 | 한자 {len(h)}개 {''.join(sorted(set(h)))[:30]} | 가나 {len(k)}개")
        if h: 
            for m in HANJA.finditer(t):
                s=max(0,m.start()-25); print(f"    …{t[s:m.end()+25]}…"); break
    except Exception as e: print(f"[{n}] 실패: {e}")
