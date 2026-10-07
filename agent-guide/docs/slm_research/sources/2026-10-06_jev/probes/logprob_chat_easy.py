"""확률 읽기 방식 동작 확인용 단건 요청 (연구계 :5015 게이트웨이)."""
import json
import math
import sys
import time
import urllib.request

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5015/v1/chat/completions"

prompt = (
    "다음 고객 문의의 유형을 고르세요. A, B, C 중 글자 하나로만 답하세요.\n\n"
    '고객 문의: "카드를 잃어버렸는데 새로 받을 수 있나요?"\n\n'
    "A) 분실·재발급\n"
    "B) 결제 오류\n"
    "C) 해지"
)

body = {
    "model": "gemma-4",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 1,
    "temperature": 0,
    "logprobs": True,
    "top_logprobs": 5,
    "chat_template_kwargs": {"enable_thinking": False},
}

req = urllib.request.Request(
    URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}
)
t0 = time.perf_counter()
with urllib.request.urlopen(req, timeout=60) as resp:
    data = json.load(resp)
elapsed_ms = (time.perf_counter() - t0) * 1000

choice = data["choices"][0]
first = choice["logprobs"]["content"][0]

print("=== 응답 원문 (logprobs 부분) ===")
print(json.dumps(choice["logprobs"], ensure_ascii=False, indent=2))
print()
print(f"생성된 글: {choice['message']['content']!r}")
print(f"입력 토큰: {data['usage']['prompt_tokens']} / 출력 토큰: {data['usage']['completion_tokens']}")
print(f"왕복 시간: {elapsed_ms:.0f} ms")
print()

labels = {"A": None, "B": None, "C": None}
for item in first["top_logprobs"]:
    tok = item["token"].strip()
    if tok in labels and labels[tok] is None:
        labels[tok] = item["logprob"]

print("=== 선택지 점수 → 확률 ===")
raw = {k: (math.exp(v) if v is not None else 0.0) for k, v in labels.items()}
total = sum(raw.values())
for k, v in labels.items():
    lp = f"{v:.4f}" if v is not None else "상위 5개 밖"
    print(f"{k}: logprob {lp:>10}  e^x {raw[k]:.4f}  → 정규화 {raw[k] / total:.4f}")
print(f"(A·B·C 원래 확률 합: {total:.4f})")
