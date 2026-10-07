"""simple-jev 평가 결과를 Jev 1.13 공개 결과(2026-09-20, OpenRouter 경유)와 벤치마크별로 맞댄다.

짝짓기 기준은 스위트 매니페스트의 (project, project_configuration)와 Jev 결과의
(project, configuration)다. 행 수가 다르면 같은 데이터가 아니므로 표시한다.
사용: python3 compare_suites.py <run_dir> [<run_dir> ...]
"""
import json
import sys
from pathlib import Path

REF = Path("/workspace/tmp/jev-lab/repos/simple-jev/eval/benchmarks/jev-1.13/2026-09-20")


def load_ref():
    ref = {}
    for f in REF.glob("*/results.json"):
        for x in json.load(open(f))["by_project"]:
            ref[(x["project"], x["configuration"])] = x
    return ref


def main():
    ref = load_ref()
    print("| 벤치 | 설정 | 행 | Qwen3.8 FP8 | Jev 1.13 | 차이 | 비고 |")
    print("|---|---|---|---|---|---|---|")
    pairs = []
    for run in sys.argv[1:]:
        for sdir in sorted(Path(run).iterdir()):
            sm, mf = sdir / "summary.json", sdir / "manifest.json"
            if not (sdir.is_dir() and sm.exists() and mf.exists()):
                continue
            s, m = json.load(open(sm)), json.load(open(mf))["suite"]
            key = (m.get("project"), m.get("project_configuration"))
            r = ref.get(key)
            if r is None:
                print(f"| {sdir.name} | - | {s.get('rows')} | {s.get('accuracy')} | - | - | 기준 없음 |")
                continue
            # 지표는 Jev 결과가 쓴 것(정확도, 묶음 정답률 등)에 맞춘다.
            metric = r["metric"]
            q = s.get(metric)
            rr = r["metrics"].get("rows")
            note = ("" if metric == "accuracy" else metric) + ("" if rr == s.get("rows") else f" 행 수 다름(Jev {rr})")
            if s.get("failed_rows"):
                note += f" 실패 {s['failed_rows']}"
            print(f"| {key[0]} | {key[1]} | {s.get('rows')} | {q:.4f} | {r['score']:.4f} | {q - r['score']:+.4f} | {note} |")
            pairs.append((q, r["score"]))
    if pairs:
        mq = sum(p[0] for p in pairs) / len(pairs)
        mj = sum(p[1] for p in pairs) / len(pairs)
        print(f"\n벤치 {len(pairs)}개 단순 평균: Qwen3.8 {mq:.4f} / Jev {mj:.4f} / 차이 {mq - mj:+.4f}")


if __name__ == "__main__":
    main()
