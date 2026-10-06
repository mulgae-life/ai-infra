import re, glob
from transformers import AutoTokenizer
tg = AutoTokenizer.from_pretrained("/models/LLM/google/gemma-4-26B-A4B-it")
tq = AutoTokenizer.from_pretrained("/models/LLM/Qwen/Qwen3.8-27B-FP8")

# 레포 전체 한국어 문서에서 한글 산문만 추출
ko = []
for f in glob.glob("/workspace/docker/**/*.md", recursive=True):
    if ".archive" in f or "node_modules" in f: continue
    try: txt = open(f, encoding="utf-8").read()
    except Exception: continue
    txt = re.sub(r"```.*?```", "", txt, flags=re.S)
    for ln in txt.splitlines():
        ln = re.sub(r"^[\s>*\-#|]+", "", ln).strip()
        if len(ln) < 25: continue
        if len(re.findall(r"[가-힣]", ln)) / len(ln) > 0.55:
            ko.append(ln)
c = "\n".join(ko)
ng, nq = len(tg.encode(c, add_special_tokens=False)), len(tq.encode(c, add_special_tokens=False))
print(f"한국어 산문 코퍼스 {len(c):,}자 / {len(ko):,}줄")
print(f"  Gemma 4  {ng:,} 토큰  ({len(c)/ng:.3f} 자/토큰)")
print(f"  Qwen3.8  {nq:,} 토큰  ({len(c)/nq:.3f} 자/토큰)")
print(f"  → Qwen이 {(ng-nq)/ng*100:.1f}% 적게 사용 (같은 문서를 담는 데 필요한 컨텍스트가 그만큼 적음)\n")

# 어절 단위: 몇 개를 통째로 1토큰에 담는가
words = sorted({w for w in re.findall(r"[가-힣]{2,}", c)})
g1 = sum(1 for w in words if len(tg.encode(w, add_special_tokens=False)) == 1)
q1 = sum(1 for w in words if len(tq.encode(w, add_special_tokens=False)) == 1)
print(f"고유 한글 어절 {len(words):,}개 중 통째로 1토큰:  Gemma {g1:,}개 ({g1/len(words)*100:.1f}%)  |  Qwen {q1:,}개 ({q1/len(words)*100:.1f}%)")
