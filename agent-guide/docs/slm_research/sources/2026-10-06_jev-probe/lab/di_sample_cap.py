"""`suite sample` 출력에서 0.2.1 지수 벤치마크만 남기고 벤치마크별 요청 수 상한을 적용한다.

`suite sample --n`은 전체 요청 수 상한이다(벤치마크별 아님). 벤치마크를 돌아가며 해시 순위
sha256(f"{seed}:{catalog_id}:{group_id}") 순으로 연결 그룹을 하나씩 추가하므로, 출력 안에서 각
벤치마크의 그룹 순서는 그 해시 순위의 앞부분이다. 여기서는 그 순서를 유지한 채 그룹 단위로
누적 요청 수가 상한을 넘지 않을 때까지 담는다(연결 그룹은 쪼개지 않음, 순위를 건너뛰지 않음).
입력 표본이 충분히 크지 않아 상한 전에 끊긴 벤치마크가 있으면 실패한다.

사용: python -I di_sample_cap.py <suite sample 출력> <결과 .jsonl.gz> <상한> <suite 디렉터리> <요약 json>
"""
import collections
import gzip
import hashlib
import json
import sys
from pathlib import Path

from decision_index import editions
from decision_index.suite.io import Suite, dumps, read_jsonl


def index_benchmarks(edition):
    panel = editions.data(f"index-{edition}.json")
    return {n for area in panel["areas"] for n in area["benchmarks"]}


def main(full_sample, out_path, cap, suite_dir, summary_path):
    suite = Suite(suite_dir)
    edition = suite.edition["id"]
    in_index = index_benchmarks(edition)

    available = collections.Counter()
    names = {}
    for r in suite.rows(apply_exclusions=True):
        e = r["_evaluation"]
        available[e["catalog_id"]] += 1
        names[e["catalog_id"]] = e["dataset"]

    rows = list(read_jsonl(full_sample))
    groups = collections.defaultdict(list)  # (catalog_id, group_id) -> rows, 첫 등장 순서 유지
    order = collections.defaultdict(list)  # catalog_id -> 그룹 키 순서
    for r in rows:
        e = r["_evaluation"]
        key = (e["catalog_id"], e["group_id"])
        if key not in groups:
            order[e["catalog_id"]].append(key)
        groups[key].append(r)

    keep = set()
    per = {}
    problems = []
    for n in sorted(in_index):
        if available[n] == 0:
            per[n] = {"dataset": None, "requests": 0, "groups": 0, "available": 0, "note": "not in rebuilt suite"}
            continue
        sampled_rows = sum(len(groups[k]) for k in order[n])
        taken = taken_groups = 0
        stopped_by_cap = False
        for k in order[n]:
            if taken + len(groups[k]) > cap:
                stopped_by_cap = True
                break
            keep.add(k)
            taken += len(groups[k])
            taken_groups += 1
        exhausted = sampled_rows == available[n]
        if taken < cap and not stopped_by_cap and not exhausted:
            problems.append(f"{n} {names[n]}: input sample ends at {sampled_rows} rows before the cap; raise --n")
        per[n] = {"dataset": names[n], "requests": taken, "groups": taken_groups, "available": available[n], "all_taken": taken == available[n]}

    chosen = [r for r in rows if (r["_evaluation"]["catalog_id"], r["_evaluation"]["group_id"]) in keep]
    digest = hashlib.sha256()
    with gzip.open(out_path, "wt", encoding="utf-8") as f:
        for r in chosen:
            line = dumps(r) + "\n"
            f.write(line)
            digest.update(line.encode())

    summary = {
        "edition": edition,
        "input_sample": str(full_sample),
        "input_rows": len(rows),
        "cap_per_benchmark": cap,
        "rule": "0.2.1 index benchmarks only; per benchmark, whole linked groups in the sampler's hash order while the running total stays <= cap",
        "out": str(out_path),
        "rows": len(chosen),
        "uncompressed_sha256": digest.hexdigest(),
        "benchmarks_in_index": len(in_index),
        "benchmarks_sampled": sum(1 for v in per.values() if v["requests"]),
        "per_benchmark": {str(n): v for n, v in per.items()},
        "problems": problems,
    }
    Path(summary_path).write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "per_benchmark"}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]))
