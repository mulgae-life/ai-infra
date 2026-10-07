"""Jev 한국어 벤치마크(jev-korean-benchmark pilot-v1)에서 Qwen3.8 결과와 Jev 문항별 응답을 짝지어 비교한다.

입력:
  runs/<run>/korean-public-*/{scoring_rows,predictions}.jsonl  (simple-jev eval 출력)
  repos/jev-korean-benchmark/results/responses.jsonl            (Jev 1.13 문항별 원응답, stage 1·2)
출력: 과제·조건별 정확도, 맞힌 문항 교차표, McNemar 정확 검정, Brier, 로그 손실, ECE
"""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

LAB = Path("/workspace/tmp/jev-lab")
RUN = LAB / "runs" / (sys.argv[1] if len(sys.argv) > 1 else "korean-public")
JEV = LAB / "repos/jev-korean-benchmark/results/responses.jsonl"
EPS = 1e-6


def mcnemar_p(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2**n
    return min(1.0, 2 * tail)


def ece(conf: list[float], hit: list[bool], bins: int = 10) -> float:
    total = len(conf)
    acc = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        idx = [i for i, c in enumerate(conf) if (lo < c <= hi) or (b == 0 and c == lo)]
        if idx:
            acc += len(idx) / total * abs(sum(conf[i] for i in idx) / len(idx) - sum(hit[i] for i in idx) / len(idx))
    return acc


def load_qwen():
    out = {}
    for d in sorted(RUN.glob("korean-public-*")):
        rows = {json.loads(l)["id"]: json.loads(l) for l in open(d / "scoring_rows.jsonl")}
        for line in open(d / "predictions.jsonl"):
            p = json.loads(line)
            r = rows[p["id"]]
            probs = p["probabilities"]
            label = r["label"]
            pred = max(range(len(probs)), key=lambda i: probs[i])
            out[p["id"]] = dict(
                task=r["family"], cond=r["condition"], correct=pred == label,
                conf=max(probs), p_gold=probs[label],
                brier=sum((q - (1.0 if i == label else 0.0)) ** 2 for i, q in enumerate(probs)),
                pred_index=pred, n_opt=len(probs),
                ms=p.get("elapsed_seconds", 0) * 1000,
            )
    return out


def load_jev():
    out = {}
    for line in open(JEV):
        d = json.loads(line)
        if d.get("status") != "success" or "score" not in d:
            continue
        s = d["score"]
        probs = s.get("probabilities") or {}
        if probs:
            conf = max(probs.values())
        else:
            conf = 0.5 + s.get("rank_confidence", 0)
        out[d["eval_id"]] = dict(
            correct=bool(s["correct"]), conf=conf, brier=s["brier"],
            log_loss=s["log_loss"], pred=s["prediction"], ms=d.get("latency_ms"),
        )
    return out


def main():
    q, j = load_qwen(), load_jev()
    groups = defaultdict(list)
    for k, v in q.items():
        if k in j:
            groups[(v["task"], v["cond"])].append(k)
    hdr = "| 과제 | 조건 | n | Qwen | Jev | 차이 | Qwen만 | Jev만 | McNemar p | Brier Q/J | 로그손실 Q/J | ECE Q/J |"
    print(hdr)
    print("|" + "---|" * 12)
    total = defaultdict(lambda: [0, 0, 0, 0, 0])
    for (task, cond), ids in sorted(groups.items()):
        n = len(ids)
        qa = sum(q[i]["correct"] for i in ids)
        ja = sum(j[i]["correct"] for i in ids)
        b = sum(q[i]["correct"] and not j[i]["correct"] for i in ids)
        c = sum(j[i]["correct"] and not q[i]["correct"] for i in ids)
        qb = sum(q[i]["brier"] for i in ids) / n
        jb = sum(j[i]["brier"] for i in ids) / n
        ql = sum(-math.log(max(q[i]["p_gold"], EPS)) for i in ids) / n
        jl = sum(min(j[i]["log_loss"], -math.log(EPS)) for i in ids) / n
        qe = ece([q[i]["conf"] for i in ids], [q[i]["correct"] for i in ids])
        je = ece([j[i]["conf"] for i in ids], [j[i]["correct"] for i in ids])
        print(f"| {task} | {cond} | {n} | {qa/n:.3f} | {ja/n:.3f} | {(qa-ja)/n:+.3f} | {b} | {c} | {mcnemar_p(b, c):.3f} | {qb:.3f}/{jb:.3f} | {ql:.3f}/{jl:.3f} | {qe:.3f}/{je:.3f} |")
        t = total[cond]
        t[0] += n; t[1] += qa; t[2] += ja; t[3] += b; t[4] += c
    print()
    print("| 조건 | n | Qwen | Jev | Qwen만 | Jev만 | McNemar p |")
    print("|---|---|---|---|---|---|---|")
    for cond, (n, qa, ja, b, c) in sorted(total.items()):
        print(f"| {cond} | {n} | {qa/n:.3f} | {ja/n:.3f} | {b} | {c} | {mcnemar_p(b, c):.3f} |")


if __name__ == "__main__":
    main()
