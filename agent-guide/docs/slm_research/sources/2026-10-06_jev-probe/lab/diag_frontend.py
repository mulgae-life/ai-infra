""":7080 vLLM의 처리량 병목이 엔진 앞단(API 서버 전처리)인지 가린다.

같은 문항(한국어 공개 벤치 ko-ko 300개, chat_probe와 같은 메시지)을 세 방식으로 보낸다.
  tokens     /v1/completions에 토큰 ID를 바로 넣는다 (채팅 템플릿·토큰화·멀티모달 전처리 생략)
  chat       /v1/chat/completions, top_logprobs 20 (chat_probe prob과 같음)
  chat-nolp  /v1/chat/completions, 점수 반환 없음
각 방식을 동시성 1과 16으로 재서 처리량(건/s)을 비교한다.
"""
import asyncio
import json
import statistics
import sys
import time

import httpx
from transformers import AutoTokenizer

sys.path.insert(0, "/workspace/tmp/jev-lab/lab")
from chat_probe import LETTERS, build_messages, load_items  # noqa: E402

URL = "http://127.0.0.1:7080"
MODEL = "gemma-4"
SRC = "/workspace/tmp/jev-lab/repos/simple-jev/eval/data/korean-public-ko-ko.jsonl"


async def run(kind, items, prompts, conc):
    sem = asyncio.Semaphore(conc)
    lat = []

    async def one(client, i):
        it = items[i]
        if kind == "tokens":
            url, body = URL + "/v1/completions", {"model": MODEL, "prompt": prompts[i], "max_tokens": 1,
                                                 "temperature": 0.0, "logprobs": 20}
        else:
            msgs = build_messages(it, list(range(len(it["options"]))), LETTERS[: len(it["options"])], "prob", True)
            body = {"model": MODEL, "messages": msgs, "max_tokens": 1, "temperature": 0.0}
            if kind == "chat":
                body.update(logprobs=True, top_logprobs=20)
            url = URL + "/v1/chat/completions"
        async with sem:
            t0 = time.perf_counter()
            r = await client.post(url, json=body)
            r.raise_for_status()
            lat.append((time.perf_counter() - t0) * 1000)

    async with httpx.AsyncClient(timeout=600) as client:
        await one(client, 0)
        lat.clear()
        t0 = time.perf_counter()
        await asyncio.gather(*(one(client, i) for i in range(len(items))))
        wall = time.perf_counter() - t0
    return dict(kind=kind, concurrency=conc, n=len(items), items_per_s=round(len(items) / wall, 2),
                p50_ms=round(statistics.median(lat), 1))


def main():
    items = load_items(SRC, "simplejev")[:300]
    tok = AutoTokenizer.from_pretrained("/models/LLM/Qwen/Qwen3.8-27B-FP8")
    prompts = []
    for it in items:
        msgs = build_messages(it, list(range(len(it["options"]))), LETTERS[: len(it["options"])], "prob", True)
        text = tok.apply_chat_template(msgs, add_generation_prompt=True, enable_thinking=False, tokenize=False)
        prompts.append(tok.encode(text, add_special_tokens=False))
    out = []
    for kind in ("tokens", "chat", "chat-nolp"):
        for conc in (1, 16):
            row = asyncio.run(run(kind, items, prompts, conc))
            out.append(row)
            print(json.dumps(row), flush=True)
    json.dump(out, open(sys.argv[1], "w"), indent=1)


if __name__ == "__main__":
    main()
