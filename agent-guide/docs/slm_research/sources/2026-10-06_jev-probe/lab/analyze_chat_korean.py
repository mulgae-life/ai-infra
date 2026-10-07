"""한국어 공개 벤치를 채팅 경로로 돌린 결과를 Jev 문항별 기록, 실험 엔진(simple-jev 형식) 결과와 맞댄다.

정확도, 실험 엔진과 답이 같은 비율, 확신도 보정(ECE), 지연(중앙값·95번째 백분위)을 낸다.
Jev 지연은 한국에서 SDK로 순차 호출한 값이라 네트워크 왕복이 들어 있다.
사용: python3 analyze_chat_korean.py runs/chat/kpub-*.jsonl
"""
import json
import math
import statistics
import sys
from pathlib import Path

LAB = Path("/workspace/tmp/jev-lab")
sys.path.insert(0, str(LAB / "lab"))
import compare_korean  # noqa: E402
from compare_korean import ece, load_jev, load_qwen, mcnemar_p  # noqa: E402

# compare_korean은 첫 명령행 인자를 실험 엔진 결과 폴더로 읽는다. 여기서는 인자가 채팅 결과 파일이라 고정한다.
compare_korean.RUN = LAB / "runs" / "korean-public"


def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, int(q * len(v)))]


def main():
    jev = load_jev()
    lab = load_qwen()
    # "엔진과 정오 일치"는 두 경로가 같은 문항을 함께 맞히거나 함께 틀린 비율이다.
    print("| 실행 | n | 정확도 | Jev | 엔진과 정오 일치 | ECE | 지연 p50/p95 ms | Jev 지연 p50/p95 ms | 처리량 건/s |")
    print("|---|---|---|---|---|---|---|---|---|")
    for path in sys.argv[1:]:
        rows = [json.loads(l) for l in open(path)]
        summ = json.loads(Path(path + ".summary.json").read_text()) if Path(path + ".summary.json").exists() else {}
        n = len(rows)
        acc = sum(r["correct"] for r in rows) / n
        ids = [r["id"] for r in rows if r["id"] in jev]
        jacc = sum(jev[i]["correct"] for i in ids) / len(ids) if ids else float("nan")
        same = [r for r in rows if r["id"] in lab]
        agree = sum(r["correct"] == lab[r["id"]]["correct"] for r in same) / len(same) if same else float("nan")
        if "probs" in rows[0]:
            e = ece([max(r["probs"]) for r in rows], [r["correct"] for r in rows])
        else:
            e = float("nan")
        lat = [r["ms"] for r in rows]
        jl = [jev[i]["ms"] for i in ids if jev[i]["ms"] is not None]
        b = sum(r["correct"] and not jev[r["id"]]["correct"] for r in rows if r["id"] in jev)
        c = sum(jev[r["id"]]["correct"] and not r["correct"] for r in rows if r["id"] in jev)
        print(
            f"| {Path(path).stem} | {n} | {acc:.3f} | {jacc:.3f} (McNemar p {mcnemar_p(b, c):.2f}) | {agree:.3f} | {e:.3f} | "
            f"{statistics.median(lat):.0f}/{pct(lat, .95):.0f} | "
            f"{(statistics.median(jl) if jl else float('nan')):.0f}/{(pct(jl, .95) if jl else float('nan')):.0f} | "
            f"{summ.get('items_per_s', '')} |"
        )


if __name__ == "__main__":
    main()
