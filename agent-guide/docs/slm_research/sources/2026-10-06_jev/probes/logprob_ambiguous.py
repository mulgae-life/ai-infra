"""애매한 문항으로 선택지별 확률 읽기 (vLLM /generative_scoring, 연구계 Qwen3.8 인스턴스 직결).

/generative_scoring은 요청 하나에 label_token_ids 첫 번째 토큰의 확률만 돌려주므로
선택지 순서를 돌려 가며 선택지 수만큼 호출한다.
비교용으로 같은 문항을 게이트웨이 채팅 경로(top_logprobs 5)로도 한 번 보낸다.
"""
import json
import math
import time
import urllib.request

from transformers import AutoTokenizer

MODEL_DIR = "/models/LLM/Qwen/Qwen3.8-27B-FP8"
SCORING_URL = "http://127.0.0.1:7080/generative_scoring"
CHAT_URL = "http://127.0.0.1:5015/v1/chat/completions"

prompt = (
    "다음 고객 문의의 유형을 고르세요. A, B, C 중 글자 하나로만 답하세요.\n\n"
    '고객 문의: "어제 분실 신고한 카드를 오늘 찾았어요. 그런데 마트에서 결제하려니까 승인이 거절돼요."\n\n'
    "A) 분실·재발급\n"
    "B) 결제 오류\n"
    "C) 해지"
)
messages = [{"role": "user", "content": prompt}]
labels = ["A", "B", "C"]


def post(url: str, body: dict) -> tuple[dict, float]:
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    return data, (time.perf_counter() - t0) * 1000


tok = AutoTokenizer.from_pretrained(MODEL_DIR)
query_text = tok.apply_chat_template(
    messages, add_generation_prompt=True, enable_thinking=False, tokenize=False
)
query_ids = tok.encode(query_text, add_special_tokens=False)
label_ids = {}
for lab in labels:
    ids = tok.encode(lab, add_special_tokens=False)
    assert len(ids) == 1, f"{lab}가 토큰 하나가 아니다: {ids}"
    label_ids[lab] = ids[0]
print(f"선택지 토큰 ID: {label_ids}")
print(f"프롬프트 끝부분: {tok.decode(query_ids[-12:])!r}")
print()

print("=== ② 전용 경로 /generative_scoring (선택지 순서를 돌려 3회) ===")
probs = {}
for i, lab in enumerate(labels):
    order = labels[i:] + labels[:i]
    body = {
        "query": query_ids,
        "items": [""],
        "label_token_ids": [label_ids[x] for x in order],
        "apply_softmax": True,
    }
    data, ms = post(SCORING_URL, body)
    probs[lab] = data["data"][0]["score"]
    print(f"첫 선택지 {lab}: score {probs[lab]:.4f}  ({ms:.0f} ms, 입력 {data['usage']['prompt_tokens']} 토큰)")
print(f"합계: {sum(probs.values()):.4f}")
print()

print("=== 비교: 게이트웨이 채팅 경로 top_logprobs 5 ===")
body = {
    "model": "gemma-4",
    "messages": messages,
    "max_tokens": 1,
    "temperature": 0,
    "logprobs": True,
    "top_logprobs": 5,
    "chat_template_kwargs": {"enable_thinking": False},
}
data, ms = post(CHAT_URL, body)
for item in data["choices"][0]["logprobs"]["content"][0]["top_logprobs"]:
    print(f"{item['token']!r:>14}  logprob {item['logprob']:9.4f}  → {math.exp(item['logprob']):.4f}")
print(f"({ms:.0f} ms)")
