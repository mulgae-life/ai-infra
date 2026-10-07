"""한 문서에 질문 N개를 물을 때의 지연을 잰다 (동시성 1, 반복 측정).

  systemone  실험 엔진 /v1/classifier에 질문 N개를 한 요청으로 보낸다 (Jev 방식, 공통 앞부분 공유)
  chat       채팅 경로에 질문마다 요청을 하나씩, N개를 동시에 보낸다. 지연은 마지막 응답까지의 시간이다
문서는 반복마다 새로 만들어 이전 반복의 캐시가 맞지 않게 한다.
"""
import argparse
import asyncio
import json
import random
import statistics
import time

import httpx

SRC = "/workspace/tmp/jev-lab/repos/simple-jev/eval/data/korean-public-ko-ko.jsonl"
QS = [
    ("이 문서에 의료 관련 내용이 포함되어 있습니까?", None),
    ("이 문서에 숫자로 된 날짜가 하나 이상 나옵니까?", None),
    ("이 문서를 고객에게 그대로 보내도 되는 공개 자료로 볼 수 있습니까?", None),
    ("이 문서에 특정 인물의 실명이 나옵니까?", None),
    ("이 문서에 금액이나 가격 정보가 나옵니까?", None),
    ("이 문서에 부정적인 사건(사고·질병·분쟁)이 언급됩니까?", None),
    ("이 문서가 한국 안의 일만 다룹니까?", None),
    ("이 문서에 과학·기술 내용이 포함되어 있습니까?", None),
    ("이 문서의 전반적인 성격은 무엇입니까?", ["뉴스·설명문", "개인 서신", "광고", "법률 문서"]),
    ("이 문서의 주된 언어는 무엇입니까?", ["한국어", "영어", "일본어", "중국어"]),
    ("이 문서의 분량은 어느 정도입니까?", ["한 문단", "몇 문단", "여러 쪽"]),
    ("이 문서를 다룰 부서로 가장 알맞은 곳은?", ["홍보", "법무", "고객지원", "연구"]),
    ("이 문서에 나온 일의 시점은?", ["과거", "현재", "미래", "알 수 없음"]),
    ("이 문서의 어조는?", ["중립", "긍정", "부정"]),
    ("이 문서에 질문 형식의 문장이 있습니까?", None),
    ("이 문서에 외국 지명이 나옵니까?", None),
]


def make_doc(pool, chars, rng):
    parts, n = [f"[문서번호 {rng.randrange(10**9)}]"], 0
    while n < chars:
        p = rng.choice(pool)
        parts.append(p)
        n += len(p)
    return "\n\n".join(parts)


def so_request(model, doc, qs):
    questions = {}
    for i, (q, opts) in enumerate(qs):
        if opts:
            questions[f"q{i}"] = {"type": "choice", "instructions": q, "criteria": {o: None for o in opts}}
        else:
            questions[f"q{i}"] = {"type": "noul", "instructions": q}
    return {"model": model, "state": doc, "questions": questions}


def chat_body(model, doc, q, opts):
    opts = opts or ["예", "아니오"]
    lines = "\n".join(f"{'ABCD'[i]}. {o}" for i, o in enumerate(opts))
    return {"model": model, "max_tokens": 1, "temperature": 0.0, "logprobs": True, "top_logprobs": 20,
            "messages": [{"role": "system", "content": "당신은 주어진 자료만 근거로 판단하는 분류기입니다. 선택지 기호 하나만 답하세요."},
                         {"role": "user", "content": f"[자료]\n{doc}\n\n[질문]\n{q}\n\n[선택지]\n{lines}\n\n답(기호 하나):"}]}


async def main_async(args):
    rng = random.Random(23)
    pool = []
    for line in open(SRC, encoding="utf-8"):
        st = json.loads(line)["state"]
        if isinstance(st, dict):
            pool.append(" ".join(str(v) for v in st.values()))
    results = []
    async with httpx.AsyncClient(timeout=600) as client:
        for n in map(int, args.n.split(",")):
            lat = []
            for rep in range(args.reps + 1):
                doc = make_doc(pool, args.chars, rng)
                qs = QS[:n]
                t0 = time.perf_counter()
                if args.mode == "systemone":
                    r = await client.post(args.endpoint + "/v1/classifier", json=so_request(args.model, doc, qs))
                    r.raise_for_status()
                else:
                    rest = qs
                    if args.warm_first:
                        # 첫 질문으로 문서를 캐시에 올린 뒤 나머지를 동시에 보낸다.
                        r = await client.post(args.endpoint + "/v1/chat/completions", json=chat_body(args.model, doc, *qs[0]))
                        r.raise_for_status()
                        rest = qs[1:]
                    rs = await asyncio.gather(*(client.post(args.endpoint + "/v1/chat/completions",
                                                            json=chat_body(args.model, doc, q, o)) for q, o in rest))
                    for r in rs:
                        r.raise_for_status()
                if rep:  # 첫 회는 준비 운동
                    lat.append((time.perf_counter() - t0) * 1000)
            row = dict(mode=args.mode + ("-warmfirst" if args.warm_first else ""), n_questions=n, chars=args.chars, p50_ms=round(statistics.median(lat), 1),
                       min_ms=round(min(lat), 1), max_ms=round(max(lat), 1), reps=args.reps)
            results.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
    json.dump(results, open(args.output, "w"), ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["systemone", "chat"], required=True)
    ap.add_argument("--endpoint", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--n", default="1,4,8,16")
    ap.add_argument("--chars", type=int, default=2000)
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--warm-first", action="store_true", help="chat: 첫 질문을 먼저 보내 문서를 캐시에 올린다")
    ap.add_argument("--output", required=True)
    asyncio.run(main_async(ap.parse_args()))


if __name__ == "__main__":
    main()
