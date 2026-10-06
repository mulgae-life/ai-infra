# 한글 음절 11,172자 전수 조사: 음절당 토큰 수 분포
from collections import Counter
from transformers import AutoTokenizer
tg = AutoTokenizer.from_pretrained("/models/LLM/google/gemma-4-26B-A4B-it")
tq = AutoTokenizer.from_pretrained("/models/LLM/Qwen/Qwen3.8-27B-FP8")
syll = [chr(c) for c in range(0xAC00, 0xD7A4)]

def dist(tok):
    c = Counter(len(tok.encode(s, add_special_tokens=False)) for s in syll)
    return c

dg, dq = dist(tg), dist(tq)
print(f"한글 음절 총 {len(syll):,}자 — 음절 1개를 몇 토큰으로 쪼개는가")
print(f"{'토큰수':>6}{'Gemma 4':>14}{'Qwen3.8':>14}")
for n in sorted(set(dg) | set(dq)):
    print(f"{n:>6}{dg.get(n,0):>10,}자{dq.get(n,0):>10,}자")
print(f"\n평균 토큰/음절  Gemma {sum(k*v for k,v in dg.items())/len(syll):.3f}  |  Qwen {sum(k*v for k,v in dq.items())/len(syll):.3f}")

# 상용 음절(KS X 1001 2,350자)로 좁혀서 재확인
import unicodedata
common = [s for s in syll if unicodedata.name(s, '')]
