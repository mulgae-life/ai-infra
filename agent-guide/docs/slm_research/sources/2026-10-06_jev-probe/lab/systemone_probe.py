"""한국어 업무 문항(kobiz)을 SystemOne 형식으로 실험 엔진(/v1/classifier)에 보내 정확도·지연을 잰다.

choice는 criteria에 선택지 이름과 설명을, noul은 instructions에 예/아니오의 뜻을 붙여 보낸다.
출력 행 형식은 chat_probe.py와 같아(probs, pred, gold, ms) 분석 스크립트를 함께 쓴다.
"""
import argparse
import asyncio
import json
import statistics
import time

import httpx


def to_request(d: dict, model: str) -> tuple[dict, list[str], int]:
    if d["type"] == "noul":
        opts = d["options"] or {}
        extra = []
        if opts.get("true"):
            extra.append(f"예: {opts['true']}")
        if opts.get("false"):
            extra.append(f"아니오: {opts['false']}")
        instr = d["question"] + ("\n" + "\n".join(extra) if extra else "")
        q = {"type": "noul", "instructions": instr}
        names, gold = ["true", "false"], 0 if d["gold"] == "true" else 1
    else:
        names = list(d["options"].keys())
        q = {"type": "choice", "instructions": d["question"], "criteria": {k: d["options"][k] for k in names}}
        gold = names.index(d["gold"])
    return {"model": model, "state": d["state"], "questions": {"q": q}}, names, gold


async def run_one(client, url, model, d):
    req, names, gold = to_request(d, model)
    t0 = time.perf_counter()
    r = await client.post(url, json=req)
    ms = (time.perf_counter() - t0) * 1000
    r.raise_for_status()
    ans = r.json()["answers"]["q"]
    if d["type"] == "noul":
        p = float(ans["noul"])
        probs = [p, 1 - p]
    else:
        probs = [float(ans["probabilities"][k]) for k in names]
    pred = max(range(len(probs)), key=lambda i: probs[i])
    return dict(id=d["id"], task=f'{d["domain"]}/{d["task"]}',
                meta=dict(domain=d["domain"], difficulty=d["difficulty"], tags=d["tags"], type=d["type"]),
                n_opt=len(names), gold=gold, probs=probs, pred=pred, correct=pred == gold, ms=ms)


async def main_async(args):
    items = [json.loads(l) for f in args.input for l in open(f, encoding="utf-8")]
    if args.limit:
        items = items[: args.limit]
    url = args.endpoint.rstrip("/") + "/v1/classifier"
    sem = asyncio.Semaphore(args.concurrency)
    rows = []
    async with httpx.AsyncClient(timeout=600) as client:
        if args.warmup:
            await run_one(client, url, args.model, items[0])

        async def task(d):
            async with sem:
                rows.append(await run_one(client, url, args.model, d))

        t0 = time.perf_counter()
        await asyncio.gather(*(task(d) for d in items))
        wall = time.perf_counter() - t0
    with open(args.output, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    lat = sorted(r["ms"] for r in rows)
    summary = dict(endpoint=args.endpoint, mode="systemone", concurrency=args.concurrency, n=len(rows),
                   accuracy=round(sum(r["correct"] for r in rows) / len(rows), 4),
                   p50_ms=round(statistics.median(lat), 1), p95_ms=round(lat[int(0.95 * (len(lat) - 1))], 1),
                   wall_s=round(wall, 2), items_per_s=round(len(rows) / wall, 2))
    open(args.output + ".summary.json", "w").write(json.dumps(summary, ensure_ascii=False, indent=1))
    print(json.dumps(summary, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--endpoint", default="http://127.0.0.1:8179")
    ap.add_argument("--model", default="qwen3.8-27b-fp8-vllm")
    ap.add_argument("--concurrency", type=int, default=16)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--warmup", action="store_true")
    ap.add_argument("--output", required=True)
    asyncio.run(main_async(ap.parse_args()))


if __name__ == "__main__":
    main()
