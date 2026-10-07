"""블라인드 검수 답과 출제 정답을 대조해 불일치·이의 문항을 뽑는다.

사용: python3 check_review.py route voc ...
출력: 분야별 일치율, 불일치 문항(출제 정답·검수 답·근거), issue가 달린 문항
"""
import json
import sys
from pathlib import Path

D = Path("/workspace/tmp/jev-lab/data/ko-biz")


def main():
    flagged = {}
    for dom in sys.argv[1:]:
        gold = {d["id"]: d for d in map(json.loads, open(D / f"{dom}.jsonl", encoding="utf-8"))}
        rev = {r["id"]: r for r in map(json.loads, open(D / "review" / f"{dom}.jsonl", encoding="utf-8"))}
        missing = set(gold) - set(rev)
        mism = [i for i in gold if i in rev and str(rev[i]["answer"]) != str(gold[i]["gold"])]
        issues = [i for i in gold if i in rev and rev[i].get("issue")]
        print(f"## {dom}: 일치 {len(gold) - len(mism) - len(missing)}/{len(gold)}, 불일치 {len(mism)}, issue {len(issues)}, 누락 {len(missing)}")
        for i in sorted(set(mism) | set(issues)):
            g, r = gold[i], rev[i]
            tag = "불일치" if i in mism else "이의"
            print(f"- [{tag}] {i} ({g['task']}, {g['difficulty']}) 출제={g['gold']} 검수={r['answer']}({r.get('confidence')})")
            print(f"    출제 근거: {g['rationale']}")
            if r.get("issue"):
                print(f"    검수 이의: {r['issue']}")
            flagged[i] = tag
    out = D / "review" / "flagged.json"
    prev = json.loads(out.read_text()) if out.exists() else {}
    prev.update(flagged)
    out.write_text(json.dumps(prev, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
