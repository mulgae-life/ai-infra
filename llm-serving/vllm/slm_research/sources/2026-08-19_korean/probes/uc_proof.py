# 용도 C: 한국어 교정 — 정답이 명확한 10문항 채점
import json, urllib.request, re
URL="http://127.0.0.1:5015/v1/chat/completions"
ITEMS=[("몇일 더 머물기로 했다.","며칠"),("오랫만에 만난 친구.","오랜만"),
 ("금새 어두워졌다.","금세"),("설겆이를 했다.","설거지"),
 ("일이 잘 됬다.","됐"),("문을 잠구고 나왔다.","잠그"),
 ("그는 나에게 어의없다고 했다.","어이없"),("갯수를 세어 보았다.","개수"),
 ("않 좋은 결과가 나왔다.","안 좋"),("바램대로 되었다.","바람")]
ok=0
for bad, want in ITEMS:
    p=f"다음 문장에서 맞춤법이 틀린 곳을 고쳐 문장만 출력하세요. 설명 금지.\n{bad}"
    b=json.dumps({"model":"Qwen3.8-27B-FP8","messages":[{"role":"user","content":p}],
        "max_tokens":100,"temperature":0.0,"chat_template_kwargs":{"enable_thinking":False}}).encode()
    r=json.load(urllib.request.urlopen(urllib.request.Request(URL,b,{"Content-Type":"application/json"}),timeout=120))
    out=r['choices'][0]['message']['content'].strip().replace('\n',' ')[:70]
    hit = want in out
    ok += hit
    print(f"{'✅' if hit else '❌'} {bad:<24} → {out}")
print(f"\n한국어 맞춤법 교정 정확도: {ok}/{len(ITEMS)}")
