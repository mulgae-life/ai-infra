"""입력 길이별 확률 읽기 지연을 잰다 (채팅 경로, 동시성 1).

문서 길이를 늘려 가며 두 경우를 잰다.
  cold  요청마다 문서 앞에 고유 번호를 붙여 접두사 캐시가 맞지 않게 한다 (처음 보는 문서)
  warm  같은 문서에 질문만 바꿔 보낸다 (한 문서에 여러 판단을 묻는 경우, 캐시 재사용)
문서는 한국어 공개 벤치 지문을 이어 붙여 만든다.
"""
import argparse
import json
import random
import statistics
import time

import httpx

SRC = "/workspace/tmp/jev-lab/repos/simple-jev/eval/data/korean-public-ko-ko.jsonl"
QUESTIONS = [
    ("이 문서에 의료 관련 내용이 포함되어 있습니까?", ["예", "아니오"]),
    ("이 문서의 전반적인 성격은 무엇입니까?", ["뉴스·설명문", "개인 서신", "광고", "법률 문서"]),
    ("이 문서를 고객에게 그대로 보내도 되는 공개 자료로 볼 수 있습니까?", ["예", "아니오"]),
    ("이 문서에 숫자로 된 날짜가 하나 이상 나옵니까?", ["예", "아니오"]),
    ("이 문서의 주된 언어는 무엇입니까?", ["한국어", "영어", "일본어", "중국어"]),
]


def passages():
    out = []
    for line in open(SRC, encoding="utf-8"):
        st = json.loads(line)["state"]
        if isinstance(st, dict):
            out.append(" ".join(str(v) for v in st.values()))
    return out


def make_doc(pool, target_chars, rng):
    parts, n = [], 0
    while n < target_chars:
        p = rng.choice(pool)
        parts.append(p)
        n += len(p)
    return "\n\n".join(parts)


def body(model, doc, q, opts, tag):
    lines = "\n".join(f"{'ABCD'[i]}. {o}" for i, o in enumerate(opts))
    user = f"{tag}[자료]\n{doc}\n\n[질문]\n{q}\n\n[선택지]\n{lines}\n\n답(기호 하나):"
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": "당신은 주어진 자료만 근거로 판단하는 분류기입니다. 선택지 기호 하나만 답하세요."},
            {"role": "user", "content": user},
        ],
        "max_tokens": 1, "temperature": 0.0, "logprobs": True, "top_logprobs": 20,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:5015")
    ap.add_argument("--model", default="gemma-4")
    ap.add_argument("--chars", default="500,2000,8000,20000,40000,80000")
    ap.add_argument("--reps", type=int, default=8)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    rng = random.Random(11)
    pool = passages()
    url = args.endpoint.rstrip("/") + "/v1/chat/completions"
    results = []
    with httpx.Client(timeout=600) as client:
        client.post(url, json=body(args.model, "준비", *QUESTIONS[0], "")).raise_for_status()
        for chars in map(int, args.chars.split(",")):
            for kind in ("cold", "warm"):
                doc = make_doc(pool, chars, rng)
                lat, toks = [], []
                for i in range(args.reps):
                    q, opts = QUESTIONS[i % len(QUESTIONS)]
                    # cold는 문서 맨 앞을 매번 바꿔 캐시가 맞지 않게 하고, warm은 같은 문서를 그대로 쓴다.
                    tag = f"[문서번호 {rng.randrange(10**9)}]\n" if kind == "cold" else ""
                    if kind == "warm" and i == 0:
                        client.post(url, json=body(args.model, doc, q, opts, "")).raise_for_status()
                    t0 = time.perf_counter()
                    r = client.post(url, json=body(args.model, doc, q, opts, tag))
                    lat.append((time.perf_counter() - t0) * 1000)
                    r.raise_for_status()
                    toks.append(r.json()["usage"]["prompt_tokens"])
                row = dict(chars=chars, kind=kind, prompt_tokens=int(statistics.median(toks)),
                           p50_ms=round(statistics.median(lat), 1), max_ms=round(max(lat), 1), reps=args.reps)
                results.append(row)
                print(json.dumps(row, ensure_ascii=False), flush=True)
    json.dump(results, open(args.output, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
