"""한국어 업무 문항 실험 결과를 분석한다.

- 실행별 정확도(전체·분야·난이도·태그), 지연
- 확신도 보정: ECE, 온도 맞춤(5겹 교차검증) 후 ECE
- 자동 처리율: 확신도 기준별로 자동 처리되는 비율과 그 안의 정확도
- 선택지 순서 편향: 순서를 돌린 실행끼리 답이 같은 비율, 표시 위치별 예측 쏠림
- 합치기: 두 실행의 확률을 평균했을 때 정확도
- 2단계 구성: 확신도가 낮은 문항만 사고 켬으로 넘겼을 때 (조합 계산, 실측)
검수에서 이의가 나온 문항(review/flagged.json)은 뺀다.
사용: python3 analyze_kobiz.py
"""
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

LAB = Path("/workspace/tmp/jev-lab")
R = LAB / "runs" / "kobiz"
FLAG = LAB / "data/ko-biz/review/flagged.json"
TAGS = ["colloquial", "typo", "long", "multi_issue", "implicit", "negation", "injection",
        "calc_date", "calc_amount", "rule", "distractor", "english_mix"]


def load(name):
    p = R / f"{name}.jsonl"
    if not p.exists():
        return None
    flagged = set(json.loads(FLAG.read_text())) if FLAG.exists() else set()
    rows = [json.loads(l) for l in open(p, encoding="utf-8")]
    return {r["id"]: r for r in rows if r["id"] not in flagged}


def ece(conf, hit, bins=10):
    tot, acc = len(conf), 0.0
    for b in range(bins):
        idx = [i for i, c in enumerate(conf) if b / bins < c <= (b + 1) / bins or (b == 0 and c == 0)]
        if idx:
            acc += len(idx) / tot * abs(statistics.fmean(conf[i] for i in idx) - statistics.fmean(hit[i] for i in idx))
    return acc


def scaled(probs, t):
    lg = [math.log(max(p, 1e-12)) / t for p in probs]
    m = max(lg)
    e = [math.exp(x - m) for x in lg]
    s = sum(e)
    return [x / s for x in e]


def nll(rows, t):
    return statistics.fmean(-math.log(max(scaled(r["probs"], t)[r["gold"]], 1e-12)) for r in rows)


def fit_t(rows):
    grid = [0.5 + 0.05 * i for i in range(91)]  # 0.5 ~ 5.0
    return min(grid, key=lambda t: nll(rows, t))


def calib(rows):
    rs = list(rows.values())
    raw = ece([max(r["probs"]) for r in rs], [r["correct"] for r in rs])
    random.Random(5).shuffle(rs)
    folds = [rs[i::5] for i in range(5)]
    conf, hit, ts = [], [], []
    for k in range(5):
        train = [r for j, f in enumerate(folds) if j != k for r in f]
        t = fit_t(train)
        ts.append(t)
        for r in folds[k]:
            p = scaled(r["probs"], t)
            conf.append(max(p))
            hit.append(max(range(len(p)), key=lambda i: p[i]) == r["gold"])
    return raw, ece(conf, hit), statistics.fmean(ts)


def acc(rows, pred=lambda r: True):
    sel = [r for r in rows.values() if pred(r)]
    return (sum(r["correct"] for r in sel) / len(sel), len(sel)) if sel else (float("nan"), 0)


def section_runs(runs):
    print("## 실행별 정확도·지연\n")
    print("| 실행 | n | 정확도 | 지연 p50 ms | 처리량 건/s | 비고 |")
    print("|---|---|---|---|---|---|")
    for name, rows in runs.items():
        s = R / f"{name}.jsonl.summary.json"
        sm = json.loads(s.read_text()) if s.exists() else {}
        a, n = acc(rows)
        note = ""
        if "unparsed" in sm:
            note = f"답 못 읽음 {sm['unparsed']}, 생성 토큰 중앙값 {sm.get('completion_tokens_median')}"
        if "all_labels_in_top20" in sm:
            note = f"모든 기호가 상위 20개 안 {sm['all_labels_in_top20']:.3f}"
        print(f"| {name} | {n} | {a:.3f} | {sm.get('p50_ms', '')} | {sm.get('items_per_s', '')} | {note} |")


def section_breakdown(runs, names):
    names = [n for n in names if n in runs]
    print("\n## 분야·난이도·태그별 정확도\n")
    print("| 묶음 | n | " + " | ".join(names) + " |")
    print("|---|---|" + "---|" * len(names))
    base = runs[names[0]]
    groups = []
    for dom in sorted({r["meta"]["domain"] for r in base.values()}):
        groups.append((f"분야 {dom}", lambda r, d=dom: r["meta"]["domain"] == d))
    for dif in ("easy", "borderline", "hard"):
        groups.append((f"난이도 {dif}", lambda r, d=dif: r["meta"]["difficulty"] == d))
    for tag in TAGS:
        groups.append((f"태그 {tag}", lambda r, t=tag: t in r["meta"]["tags"]))
    groups.append(("형식 noul", lambda r: r["meta"]["type"] == "noul"))
    groups.append(("형식 choice", lambda r: r["meta"]["type"] == "choice"))
    for label, f in groups:
        cells = []
        n = 0
        for name in names:
            a, n = acc(runs[name], f)
            cells.append(f"{a:.3f}")
        print(f"| {label} | {n} | " + " | ".join(cells) + " |")


def section_calib(runs):
    print("\n## 확신도 보정 (ECE, 낮을수록 좋음)\n")
    print("| 실행 | ECE 원본 | ECE 온도 맞춤 후 | 맞춘 온도 |")
    print("|---|---|---|---|")
    for name, rows in runs.items():
        if rows and "probs" in next(iter(rows.values())):
            raw, cal, t = calib(rows)
            print(f"| {name} | {raw:.3f} | {cal:.3f} | {t:.2f} |")


def section_coverage(runs):
    print("\n## 자동 처리율 (확신도 기준 이상만 자동 처리, 나머지는 사람에게)\n")
    ths = [0.5, 0.8, 0.9, 0.95, 0.99, 0.999]
    print("| 실행 | " + " | ".join(f"≥{t}" for t in ths) + " |")
    print("|---|" + "---|" * len(ths))
    for name, rows in runs.items():
        if not rows or "probs" not in next(iter(rows.values())):
            continue
        cells = []
        for t in ths:
            sel = [r for r in rows.values() if max(r["probs"]) >= t]
            if sel:
                cells.append(f"{len(sel) / len(rows):.0%} / {sum(r['correct'] for r in sel) / len(sel):.3f}")
            else:
                cells.append("-")
        print(f"| {name} | " + " | ".join(cells) + " |")
    print("\n칸 = 자동 처리 비율 / 자동 처리분 정확도")


def section_order(runs):
    names = [n for n in ("prob-5015-c1", "prob-5015-shift1", "prob-5015-shift2") if n in runs]
    if len(names) < 2:
        return
    print("\n## 선택지 순서 편향\n")
    ids = set.intersection(*(set(runs[n]) for n in names))
    choice_ids = [i for i in ids if runs[names[0]][i]["meta"]["type"] == "choice"]
    same = sum(len({runs[n][i]["pred"] for n in names}) == 1 for i in choice_ids) / len(choice_ids)
    print(f"- 선택지형 {len(choice_ids)}문항에서 순서를 {len(names)}가지로 돌렸을 때 답이 모두 같은 비율: {same:.3f}")
    for n in names:
        pos_pred, pos_gold = defaultdict(int), defaultdict(int)
        for i in choice_ids:
            r = runs[n][i]
            pos_pred[r["order"].index(r["pred"])] += 1
            pos_gold[r["order"].index(r["gold"])] += 1
        a, _ = acc({i: runs[n][i] for i in choice_ids})
        dist = ", ".join(f"{p + 1}번 {pos_pred[p]}/{pos_gold[p]}" for p in sorted(pos_gold))
        print(f"- {n}: 정확도 {a:.3f}, 표시 위치별 예측/정답 수 {dist}")


def section_ensemble(runs):
    pairs = [("prob-5015-c1", "systemone-lab"), ("prob-5015-c1", "prob-5015-shift1"),
             ("prob-5015-c1", "prob-5015-number")]
    print("\n## 두 실행 확률 평균\n")
    for a, b in pairs:
        if a not in runs or b not in runs:
            continue
        ids = set(runs[a]) & set(runs[b])
        hit = 0
        for i in ids:
            p = [(x + y) / 2 for x, y in zip(runs[a][i]["probs"], runs[b][i]["probs"])]
            hit += max(range(len(p)), key=lambda k: p[k]) == runs[a][i]["gold"]
        both = sum(runs[a][i]["correct"] == runs[b][i]["correct"] for i in ids) / len(ids)
        print(f"- {a} + {b}: 단독 {acc({i: runs[a][i] for i in ids})[0]:.3f} / {acc({i: runs[b][i] for i in ids})[0]:.3f}, "
              f"평균 {hit / len(ids):.3f}, 정오 일치 {both:.3f} (n={len(ids)})")


def section_two_stage(runs, fast="prob-5015-c1", slow="think-5015-c16"):
    """확신도가 기준 미만인 문항만 사고 켬 결과로 바꿨을 때의 정확도와 넘긴 비율, 평균 지연을 계산한다."""
    if fast not in runs or slow not in runs:
        return
    ids = set(runs[fast]) & set(runs[slow])
    fs, ss = runs[fast], runs[slow]
    print("\n## 2단계 구성 (확신도 기준 미만만 사고 켬으로 다시 묻기)\n")
    print("| 기준 | 사고 켬으로 넘긴 비율 | 정확도 | 평균 지연 ms |")
    print("|---|---|---|---|")
    for t in (0.0, 0.8, 0.9, 0.95, 0.99, 0.999, 1.01):
        hit, esc, lat = 0, 0, 0.0
        for i in ids:
            f = fs[i]
            lat += f["ms"]
            if max(f["probs"]) < t:
                esc += 1
                lat += ss[i]["ms"]
                hit += ss[i]["correct"]
            else:
                hit += f["correct"]
        label = "확률 읽기만" if t == 0.0 else ("전부 사고 켬" if t > 1 else f"<{t}")
        print(f"| {label} | {esc / len(ids):.0%} | {hit / len(ids):.3f} | {lat / len(ids):.0f} |")
    print("\n사고 켬 지연은 동시성 16 실행에서 잰 값이라 단건 지연보다 길다.")


def section_two_stage_measured(runs, fast="prob-5015-c1", slow="think-5015-c1-lt09", t=0.9):
    """확신도 t 미만 문항만 동시성 1 사고 켬으로 실제로 다시 물은 실행을 확률 읽기 결과와 합친다."""
    if fast not in runs or slow not in runs:
        return
    fs, ss = runs[fast], runs[slow]
    esc = {i for i in fs if max(fs[i]["probs"]) < t}
    if esc != set(ss):
        raise ValueError(f"사고 켬 실행 문항({len(ss)})이 확신도 {t} 미만 문항({len(esc)})과 다르다")
    hit = sum((ss[i] if i in esc else fs[i])["correct"] for i in fs)
    lat = sorted(fs[i]["ms"] + (ss[i]["ms"] if i in esc else 0) for i in fs)
    fixed = sum(ss[i]["correct"] and not fs[i]["correct"] for i in esc)
    broke = sum(fs[i]["correct"] and not ss[i]["correct"] for i in esc)
    print(f"\n## 2단계 구성 실측 (확신도 < {t}만 동시성 1 사고 켬)\n")
    print(f"- 넘긴 문항 {len(esc)}/{len(fs)}, 전체 정확도 {hit / len(fs):.3f}, 바로잡음 {fixed}, 새로 틀림 {broke}")
    print(f"- 문항당 지연 평균 {statistics.fmean(lat) / 1000:.2f}초, 중앙값 {statistics.median(lat):.0f}ms, "
          f"p95 {lat[int(len(lat) * 0.95) - 1]:.0f}ms")


def main():
    order = ["prob-5015-c1", "systemone-lab", "prob-7080", "prob-5015-nosys", "prob-5015-number",
             "prob-5015-shift1", "prob-5015-shift2", "gen-5015-c1", "think-5015-c16", "think-5015-c1-lt09"]
    runs = {n: load(n) for n in order}
    runs = {n: r for n, r in runs.items() if r}
    section_runs(runs)
    section_breakdown(runs, ["prob-5015-c1", "systemone-lab", "gen-5015-c1", "think-5015-c16"])
    section_calib(runs)
    section_coverage(runs)
    section_order(runs)
    section_ensemble(runs)
    section_two_stage(runs)
    section_two_stage_measured(runs)


if __name__ == "__main__":
    main()
