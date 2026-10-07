"""Decision Index 0.2.1 표본 실행을 표본 자체를 전체로 보고 채점하고, Jev·simple-jev와 같은 조건(HLE 제외)으로 맞댄다.

공식 `decision_index score`는 suite 디렉터리의 전체 행을 분모로 잡아, 표본에 없는 행이 미응답으로 남는다
(벤치마크별 coverage가 약 0.02~0.1이 되어 지수가 0에 가깝게 나온다). 여기서는
1. 표본 행만 담은 suite 디렉터리를 만들어 공식 score_run으로 채점한다(벤치마크별 점수·skill은 공식 계산 그대로).
2. 공식 aggregate로 지수를 다시 합산하되, 우리 표본에 없는 HLE(45)를 영역에서 뺀다.
3. 순위표 index.json의 Jev와 simple-jev(Qwen3.8-27B bf16) 벤치마크별 값을 같은 방식으로 HLE 없이 합산한다.
   HLE를 넣은 합산이 공개 지수(57.91, 55.74)와 같은지 먼저 확인해 합산 방식을 검증한다.

사용: python -I di_score_sample.py <표본 .jsonl.gz> <원 suite 디렉터리> <results.jsonl> <index.json.gz> <출력 디렉터리>
"""
import copy
import gzip
import json
import shutil
import sys
from pathlib import Path

from decision_index import editions
from decision_index.pipeline import score_run
from decision_index.scoring import index02
from decision_index.suite.io import Suite

HLE = 45


def build_sample_suite(sample_path, suite_dir, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in (editions.MANIFEST_FILE, editions.EXCLUSIONS_FILE):
        src = suite_dir / name
        if src.exists():
            shutil.copyfile(src, out_dir / name)
    with gzip.open(sample_path, "rt", encoding="utf-8") as f, gzip.open(out_dir / editions.ROWS_FILE, "wt", encoding="utf-8") as w:
        n = 0
        for line in f:
            w.write(line)
            n += 1
    with gzip.open(out_dir / editions.ADDED_FILE, "wt", encoding="utf-8"):
        pass
    return n


def spec_without(s, drop):
    t = copy.deepcopy(s)
    for a in t["areas"]:
        a["benchmarks"] = [n for n in a["benchmarks"] if n != drop]
    return t


def values_from(benchmarks, s):
    return {n: {k: benchmarks[str(n)][k] for k in ("raw", "skill", "coverage")} for a in s["areas"] for n in a["benchmarks"]}


def main(sample_path, suite_dir, results_path, index_path, out_dir):
    sample_path, suite_dir, out_dir = Path(sample_path), Path(suite_dir), Path(out_dir)
    n = build_sample_suite(sample_path, suite_dir, out_dir / "suite-sample")
    suite = Suite(out_dir / "suite-sample", "0.2.1")
    ours = score_run(suite, Path(results_path), "qwen3.8-27b-fp8-vllm", out_dir / "score")
    s = index02.spec("0.2.1")
    s_no_hle = spec_without(s, HLE)

    board = json.load(gzip.open(index_path))
    jev = board["jev"]
    sj = next(m for m in board["models"] if m["name"].startswith("simple-jev"))
    report = {"sample_rows": n, "counts": ours["counts"], "latency_ms": ours["latency_ms"], "check_full_panel": {}, "no_hle": {}}
    for name, entry in (("jev", jev), ("simple-jev-qwen3.8-27b-bf16", sj)):
        full, _ = index02.aggregate(values_from(entry["benchmarks"], s), s)
        report["check_full_panel"][name] = {"recomputed": round(full["balanced_skill"], 2), "published": entry["scores"]["balanced_skill"]}
        part, areas = index02.aggregate(values_from(entry["benchmarks"], s_no_hle), s_no_hle)
        report["no_hle"][name] = {"scores": {k: round(v, 2) for k, v in part.items()}, "areas": {a["id"]: round(100 * a["skill"], 1) for a in areas}}
    mine = values_from(ours["index_benchmarks"], s_no_hle)
    part, areas = index02.aggregate(mine, s_no_hle)
    report["no_hle"]["ours"] = {"scores": {k: round(v, 2) for k, v in part.items()}, "areas": {a["id"]: round(100 * a["skill"], 1) for a in areas}}

    rows = []
    for a in s_no_hle["areas"]:
        for b in a["benchmarks"]:
            k = str(b)
            nb = ours["benchmarks"].get(k, {})
            rows.append(dict(id=b, area=a["id"], name=board["benchmarks"][k].get("name") or board["benchmarks"][k].get("dataset"), metric=nb.get("metric"),
                             answered=nb.get("answered"), errors=nb.get("errors"), ours_raw=ours["index_benchmarks"][k]["raw"],
                             ours_skill=ours["index_benchmarks"][k]["skill"], sj_raw=sj["benchmarks"][k]["raw"],
                             sj_skill=sj["benchmarks"][k]["skill"], jev_raw=jev["benchmarks"][k]["raw"],
                             jev_skill=jev["benchmarks"][k]["skill"], median_ms=nb.get("median_ms")))
    report["benchmarks"] = rows
    (out_dir / "compare.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))

    print(json.dumps({k: report[k] for k in ("sample_rows", "counts", "latency_ms", "check_full_panel", "no_hle")}, ensure_ascii=False, indent=1))
    print("\n| 영역 | 벤치 | 지표 | 응답 | 우리 raw | simple-jev raw | Jev raw | 우리 skill | simple-jev skill | Jev skill |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['area']} | {r['name']} | {r['metric']} | {r['answered']} | {r['ours_raw']:.3f} | {r['sj_raw']:.3f} | {r['jev_raw']:.3f} | "
              f"{r['ours_skill']:.3f} | {r['sj_skill']:.3f} | {r['jev_skill']:.3f} |")


if __name__ == "__main__":
    main(*sys.argv[1:6])
