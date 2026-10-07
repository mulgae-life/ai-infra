# 대량 실문서 기반 한국어 토큰 효율 재확인
import re, glob
from transformers import AutoTokenizer
tg = AutoTokenizer.from_pretrained("/models/LLM/google/gemma-4-26B-A4B-it")
tq = AutoTokenizer.from_pretrained("/models/LLM/Qwen/Qwen3.8-27B-FP8")

files = ["/workspace/ai-infra/llm-serving/VLLM_API_GUIDE.md",
         "/workspace/ai-infra/llm-serving/VLLM_OPS_GUIDE.md",
         "/workspace/ai-infra/llm-serving/DEPLOY_GUIDE.md",
         "/workspace/ai-infra/agent-guide/docs/slm_research/topics/gemma4-vs-qwen.md",
         "/workspace/ai-infra/agent-guide/docs/slm_research/models/qwen3.5.md"]

# 코드블록·표 제거 후 한글 비중 높은 줄만 추출 (순수 한국어 산문 근사)
ko_lines = []
for f in files:
    txt = open(f, encoding="utf-8").read()
    txt = re.sub(r"```.*?```", "", txt, flags=re.S)
    for ln in txt.splitlines():
        ln = ln.strip()
        if len(ln) < 20 or ln.startswith(("|", "#", "-", ">", "*")):
            continue
        ko = len(re.findall(r"[가-힣]", ln))
        if ko / len(ln) > 0.5:
            ko_lines.append(ln)
corpus = "\n".join(ko_lines)
ng, nq = len(tg.encode(corpus, add_special_tokens=False)), len(tq.encode(corpus, add_special_tokens=False))
print(f"실문서 한국어 산문 {len(corpus):,}자 ({len(ko_lines)}줄)")
print(f"  Gemma 4  : {ng:,} 토큰  ({len(corpus)/ng:.3f} 자/토큰)")
print(f"  Qwen3.8  : {nq:,} 토큰  ({len(corpus)/nq:.3f} 자/토큰)")
print(f"  → Qwen이 {(ng-nq)/ng*100:.1f}% 적은 토큰 사용")

# 순수 한글 음절 단위 분해 정도 확인
for w in ["안녕하세요", "보험계약", "피보험자", "췌장암", "괜찮으시겠어요", "김서연", "성남시"]:
    a = tg.tokenize(w); b = tq.tokenize(w)
    print(f"  {w:<10} Gemma {len(a)}개 {a}  |  Qwen {len(b)}개 {b}")
