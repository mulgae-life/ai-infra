"""채팅 경로(게이트웨이 :5015 또는 vLLM 직접 :7080)로 판단 문항을 보내 정확도와 지연을 잰다.

모드
  prob   max_tokens=1 + top_logprobs=20으로 선택지 기호의 확률을 읽는다 (확률 읽기)
  gen    사고 끔으로 짧게 생성시켜 맨 앞 기호를 답으로 본다
  think  사고 켬으로 생성시켜 최종 답(content)의 기호를 답으로 본다. 사고 과정은
         인스턴스의 reasoning_parser가 reasoning_content로 분리한다

입력 형식 (--format)
  simplejev  simple-jev eval/data/*.jsonl (state, native_question, options, label)
  kobiz      직접 만든 한국어 업무 문항 (SPEC.md)

지연은 클라이언트가 요청을 보낸 순간부터 응답 본문을 다 받을 때까지의 벽시계 시간이다.
"""
import argparse
import asyncio
import json
import math
import random
import re
import statistics
import time
from pathlib import Path

import httpx

KEY_KO = {"passage": "지문", "question": "질문", "sentence1": "문장1", "sentence2": "문장2"}
LETTERS = "ABCDEFGHIJ"
NUMBERS = [str(i) for i in range(1, 11)]
SYSTEM = "당신은 주어진 자료만 근거로 판단하는 분류기입니다. 선택지 기호 하나만 답하세요."
SYSTEM_THINK = "당신은 주어진 자료만 근거로 판단하는 분류기입니다. 충분히 생각한 뒤 최종 답으로 선택지 기호 하나만 쓰세요."


def load_items(path: str, fmt: str) -> list[dict]:
    """문항을 {id, task, state_text, question, options[(이름, 설명)], gold(인덱스), meta}로 맞춘다."""
    items = []
    for line in open(path, encoding="utf-8"):
        d = json.loads(line)
        if fmt == "simplejev":
            st = d["state"]
            state_text = (
                "\n".join(f"{KEY_KO.get(k, k)}: {v}" for k, v in st.items()) if isinstance(st, dict) else str(st)
            )
            nq = d["native_question"]
            if nq["type"] == "noul":
                # simple-jev noul 선택지 순서는 [no, yes]. 사람이 읽는 순서인 예/아니오로 바꾼다.
                options = [("예", None), ("아니오", None)]
                gold = 0 if d["options"][d["label"]]["id"] == "yes" else 1
            else:
                options = [(o["id"], o.get("description")) for o in d["options"]]
                gold = d["label"]
            items.append(dict(id=d["id"], task=d.get("family", ""), state_text=state_text,
                              question=nq["instructions"], options=options, gold=gold, meta={}))
        elif fmt == "kobiz":
            if d["type"] == "noul":
                opts = d["options"] or {}
                options = [("예", opts.get("true")), ("아니오", opts.get("false"))]
                gold = 0 if d["gold"] == "true" else 1
            else:
                keys = list(d["options"].keys())
                options = [(k, d["options"][k]) for k in keys]
                gold = keys.index(d["gold"])
            items.append(dict(id=d["id"], task=f'{d["domain"]}/{d["task"]}', state_text=d["state"],
                              question=d["question"], options=options, gold=gold,
                              meta=dict(domain=d["domain"], difficulty=d["difficulty"], tags=d["tags"], type=d["type"])))
        else:
            raise ValueError(fmt)
    return items


def build_messages(item: dict, order: list[int], labels: list[str], mode: str, system: bool) -> list[dict]:
    lines = []
    for lab, idx in zip(labels, order):
        name, desc = item["options"][idx]
        lines.append(f"{lab}. {name}" + (f" — {desc}" if desc else ""))
    tail = "답(기호 하나):" if mode != "think" else "생각을 마친 뒤 최종 답으로 기호 하나만 쓰세요."
    user = f"[자료]\n{item['state_text']}\n\n[질문]\n{item['question']}\n\n[선택지]\n" + "\n".join(lines) + f"\n\n{tail}"
    msgs = [{"role": "user", "content": user}]
    if system:
        msgs.insert(0, {"role": "system", "content": SYSTEM_THINK if mode == "think" else SYSTEM})
    return msgs


def parse_prob(resp: dict, labels: list[str]) -> tuple[list[float], float, bool]:
    """상위 20개 안에서 기호별 확률을 모은다. 앞뒤 공백·마크다운 변형은 같은 기호로 합친다.

    반환: (선택지별 정규화 확률, 상위 20개 안 기호 확률 합, 모든 기호가 상위 20개 안에 있었는지)
    """
    top = resp["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
    mass = {lab: 0.0 for lab in labels}
    for t in top:
        tok = t["token"].strip().strip("*").strip()
        if tok in mass:
            mass[tok] += math.exp(t["logprob"])
    cover = sum(mass.values())
    complete = all(v > 0 for v in mass.values())
    if cover == 0:
        return [1.0 / len(labels)] * len(labels), 0.0, False
    return [mass[lab] / cover for lab in labels], cover, complete


def parse_letter(text: str, labels: list[str], last: bool) -> int | None:
    pat = r"(?<![A-Za-z0-9])(" + "|".join(re.escape(x) for x in labels) + r")(?![A-Za-z0-9])"
    found = re.findall(pat, text or "")
    if not found:
        return None
    return labels.index(found[-1] if last else found[0])


async def run_one(client, url, model, item, args, rng):
    n = len(item["options"])
    order = list(range(n))
    if args.shift:
        order = order[args.shift % n:] + order[: args.shift % n]
    if args.shuffle:
        rng.shuffle(order)
    labels = (LETTERS if args.labels == "letter" else NUMBERS)[:n]
    msgs = build_messages(item, order, labels, args.mode, not args.no_system)
    body = {"model": model, "messages": msgs}
    if args.mode == "prob":
        body.update(max_tokens=1, temperature=0.0, logprobs=True, top_logprobs=20)
    elif args.mode == "gen":
        body.update(max_tokens=8, temperature=0.0)
    else:
        body.update(max_tokens=args.think_max_tokens, chat_template_kwargs={"enable_thinking": True})
    t0 = time.perf_counter()
    r = await client.post(url, json=body)
    elapsed = (time.perf_counter() - t0) * 1000
    r.raise_for_status()
    resp = r.json()
    row = dict(id=item["id"], task=item["task"], meta=item["meta"], n_opt=n, order=order,
               gold=item["gold"], ms=elapsed, usage=resp.get("usage"))
    msg = resp["choices"][0]["message"]
    if args.mode == "prob":
        probs_by_label, cover, complete = parse_prob(resp, labels)
        probs = [0.0] * n
        for pos, idx in enumerate(order):
            probs[idx] = probs_by_label[pos]
        row.update(probs=probs, cover=cover, complete=complete, pred=max(range(n), key=lambda i: probs[i]))
    else:
        pos = parse_letter(msg.get("content"), labels, last=args.mode == "think")
        row.update(pred=None if pos is None else order[pos], text=(msg.get("content") or "")[:200],
                   reasoning_chars=len(msg.get("reasoning_content") or msg.get("reasoning") or ""),
                   finish=resp["choices"][0].get("finish_reason"))
    row["correct"] = row["pred"] == item["gold"]
    return row


async def main_async(args):
    items = load_items(args.input, args.format)
    if args.tasks:
        keep = set(args.tasks.split(","))
        items = [it for it in items if it["task"] in keep or it["task"].split("/")[0] in keep]
    if args.limit:
        items = items[: args.limit]
    url = args.endpoint.rstrip("/") + "/v1/chat/completions"
    rng = random.Random(args.seed)
    sem = asyncio.Semaphore(args.concurrency)
    out = open(args.output, "w", encoding="utf-8")
    rows = []

    async with httpx.AsyncClient(timeout=args.timeout, limits=httpx.Limits(max_connections=args.concurrency * 2)) as client:
        # 첫 요청의 CUDA 그래프·캐시 준비 시간이 지연 통계에 섞이지 않게 한 번 데운다.
        if args.warmup:
            await run_one(client, url, args.model, items[0], args, random.Random(0))

        async def task(it):
            async with sem:
                row = await run_one(client, url, args.model, it, args, rng)
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
                rows.append(row)

        t0 = time.perf_counter()
        await asyncio.gather(*(task(it) for it in items))
        wall = time.perf_counter() - t0
    out.close()

    lat = sorted(r["ms"] for r in rows)
    acc = sum(r["correct"] for r in rows) / len(rows)
    summary = dict(
        input=args.input, endpoint=args.endpoint, mode=args.mode, concurrency=args.concurrency,
        n=len(rows), accuracy=round(acc, 4),
        p50_ms=round(statistics.median(lat), 1), p95_ms=round(lat[min(len(lat) - 1, int(0.95 * len(lat)))], 1),
        mean_ms=round(statistics.fmean(lat), 1), wall_s=round(wall, 2), items_per_s=round(len(rows) / wall, 2),
        prompt_tokens_median=statistics.median((r["usage"] or {}).get("prompt_tokens", 0) for r in rows),
        shift=args.shift, shuffle=args.shuffle, labels=args.labels, system=not args.no_system,
    )
    if args.mode == "prob":
        summary["cover_mean"] = round(statistics.fmean(r["cover"] for r in rows), 4)
        summary["all_labels_in_top20"] = round(sum(r["complete"] for r in rows) / len(rows), 4)
    else:
        summary["unparsed"] = sum(r["pred"] is None for r in rows)
        summary["completion_tokens_median"] = statistics.median((r["usage"] or {}).get("completion_tokens", 0) for r in rows)
    Path(args.output + ".summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    print(json.dumps(summary, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--format", choices=["simplejev", "kobiz"], required=True)
    ap.add_argument("--endpoint", default="http://127.0.0.1:5015")
    ap.add_argument("--model", default="gemma-4")
    ap.add_argument("--mode", choices=["prob", "gen", "think"], default="prob")
    ap.add_argument("--concurrency", type=int, default=1)
    ap.add_argument("--labels", choices=["letter", "number"], default="letter")
    ap.add_argument("--shift", type=int, default=0, help="선택지를 이만큼 돌려 순서 편향을 잰다")
    ap.add_argument("--shuffle", action="store_true")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--no-system", action="store_true")
    ap.add_argument("--tasks", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--think-max-tokens", type=int, default=8192)
    ap.add_argument("--timeout", type=float, default=900)
    ap.add_argument("--warmup", action="store_true")
    ap.add_argument("--output", required=True)
    asyncio.run(main_async(ap.parse_args()))


if __name__ == "__main__":
    main()
