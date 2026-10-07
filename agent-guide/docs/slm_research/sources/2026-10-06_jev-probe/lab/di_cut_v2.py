"""HLE(45) 없이 재구성한 0.1 행에 0.2 절단을 적용하고, 벤치마크 단위로 공개 매니페스트와 대조한다.

`suite rebuild`(main_v2)는 0.1 행이 lab 해시와 바이트 단위로 같지 않으면 0.2 절단을 건너뛴다.
HLE가 게이트로 막혀 0.1 전체 해시는 맞을 수 없으므로, 같은 패키지 함수(release_v2.cut/gz)를 직접 호출한다.
전체 해시 대신 hub/manifest.json(0.1)에 고정된 벤치마크별 정규화 파일 sha256·선택 그룹·요청 수와 대조한다.

사용: python -I di_cut_v2.py <work 디렉터리> <decision-index 저장소 경로>
"""
import collections
import json
import sys
from pathlib import Path

from decision_index.suite.build import release_v2
from decision_index.suite.io import read_jsonl

MISSING = {45}  # HLE: Hugging Face 게이트 미승인으로 원본 접근 불가


def check_v1(rebuilt_manifest, lab_manifest):
    lab = {b["catalog_id"]: b for b in lab_manifest["benchmarks"]}
    new = {b["catalog_id"]: b for b in rebuilt_manifest["benchmarks"]}
    lab_groups = {int(k): v for k, v in lab_manifest["selected_group_ids"].items()}
    report = {}
    for n in sorted(lab):
        if n in MISSING:
            report[n] = {"dataset": lab[n]["dataset"], "status": "missing (excluded on purpose)", "present": n in new}
            continue
        if n not in new:
            report[n] = {"dataset": lab[n]["dataset"], "status": "MISSING"}
            continue
        a, b = lab[n], new[n]
        diffs = [k for k in ("available_cases", "selected_cases", "requests", "fields") if a[k] != b[k]]
        if [s["sha256"] for s in a["sources"]] != [s["sha256"] for s in b["sources"]]:
            diffs.append("normalized_sha256")
        if sorted(map(str, lab_groups.get(n, []))) != sorted(map(str, b["selected_group_ids"])):
            diffs.append("selected_group_ids")
        report[n] = {"dataset": a["dataset"], "status": "identical" if not diffs else "DIFF", "diffs": diffs, "requests": b["requests"]}
    return report


def main(work, repo):
    work, repo = Path(work), Path(repo)
    v1_dir = work / "artifacts/benchmark-suite/release-v1-rebuilt"
    v2_dir = work / "artifacts/benchmark-suite/release-v2-rebuilt"
    lab_v1 = json.loads((repo / "hub/manifest.json").read_text())
    lab_v21 = json.loads((repo / "hub/0.2.1/manifest.json").read_text())

    v1_report = check_v1(json.loads((v1_dir / "manifest.json").read_text()), lab_v1)
    bad = {n: r for n, r in v1_report.items() if r["status"] not in ("identical", "missing (excluded on purpose)")}

    excluded = set(json.loads((repo / "hub/excluded-questions.json").read_text())["rows"])
    rows = v2_dir / "selected-rows.jsonl"
    cut = release_v2.cut(v1_dir / "selected-rows.jsonl", rows, excluded)
    release_v2.gz(rows)

    counts = collections.Counter(r["_evaluation"]["catalog_id"] for r in read_jsonl(rows))
    expected = {b["catalog_id"]: b["requests"] for b in lab_v21["benchmarks"]}
    count_diffs = {n: {"expected": expected.get(n), "rebuilt": counts.get(n, 0)} for n in sorted(set(expected) | set(counts)) if n not in MISSING and expected.get(n) != counts.get(n, 0)}
    missing_rows = sum(expected[n] for n in MISSING)

    print(json.dumps({
        "v1_per_benchmark_identical": sum(r["status"] == "identical" for r in v1_report.values()),
        "v1_mismatches": bad,
        "v1_missing_on_purpose": {n: r["dataset"] for n, r in v1_report.items() if n in MISSING},
        "v2_cut": cut,
        "v2_rows_expected_without_missing": lab_v21["files"]["selected-rows.jsonl.gz"]["rows"] - missing_rows,
        "v2_per_benchmark_count_diffs": count_diffs,
        "v2_rows_gz": str(rows) + ".gz",
    }, indent=2))
    return 1 if bad or count_diffs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
