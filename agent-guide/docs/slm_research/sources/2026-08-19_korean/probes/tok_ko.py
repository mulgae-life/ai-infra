# 한국어 토큰 효율 실측: Gemma 4 26B-A4B vs Qwen3.8-27B
from transformers import AutoTokenizer

G = "/models/LLM/google/gemma-4-26B-A4B-it"
Q = "/models/LLM/Qwen/Qwen3.8-27B-FP8"

SAMPLES = {
 "뉴스체": "정부는 어제 국무회의를 열고 내년도 예산안을 확정했다. 총지출 규모는 전년 대비 4.2% 늘어난 728조원으로, 복지와 국방 분야 증액이 두드러졌다.",
 "구어체": "야 그거 어제 봤어? 진짜 웃기더라ㅋㅋ 근데 뒷부분은 좀 억지스럽지 않았냐? 난 중간에 껐잖아 그냥.",
 "보험/금융": "피보험자가 보험기간 중 상해의 직접결과로써 사망한 경우 보험수익자에게 약정한 보험금을 지급합니다. 다만 고지의무 위반 시 계약을 해지할 수 있습니다.",
 "기술문서": "본 시스템은 텐서 병렬화를 적용하여 추론 지연시간을 단축하였으며, 키-값 캐시 사용률을 기준으로 동시성 한계를 산정한다.",
 "고유명사": "김서연 씨는 경기도 성남시 분당구 정자동에 위치한 한화손해보험 판교지점에서 근무한다.",
 "한자어밀집": "당해 사안의 위법성 조각사유 해당 여부는 구체적·개별적으로 판단하여야 하며, 이를 형해화해서는 아니 된다.",
 "혼합체": "이번 Q3 실적은 YoY 기준 12% 성장했고, MAU도 전분기 대비 8% 늘었습니다. 다만 churn rate가 소폭 상승했네요.",
}
EN = "The government finalized next year's budget yesterday, raising total spending by 4.2 percent to a record level, with welfare and defense seeing the largest increases."

def load(p):
    return AutoTokenizer.from_pretrained(p, trust_remote_code=True)

tg, tq = load(G), load(Q)
print(f"{'구분':<12}{'글자수':>6}{'Gemma':>8}{'Qwen':>8}{'G 자/토':>9}{'Q 자/토':>9}{'차이':>8}")
print("-"*62)
tot_g = tot_q = tot_c = 0
for k, v in SAMPLES.items():
    ng, nq, nc = len(tg.encode(v, add_special_tokens=False)), len(tq.encode(v, add_special_tokens=False)), len(v)
    tot_g += ng; tot_q += nq; tot_c += nc
    print(f"{k:<12}{nc:>6}{ng:>8}{nq:>8}{nc/ng:>9.2f}{nc/nq:>9.2f}{(nq-ng)/ng*100:>7.1f}%")
print("-"*62)
print(f"{'합계':<12}{tot_c:>6}{tot_g:>8}{tot_q:>8}{tot_c/tot_g:>9.2f}{tot_c/tot_q:>9.2f}{(tot_q-tot_g)/tot_g*100:>7.1f}%")
eg, eq = len(tg.encode(EN, add_special_tokens=False)), len(tq.encode(EN, add_special_tokens=False))
print(f"\n[영어 대조] 글자 {len(EN)} → Gemma {eg} ({len(EN)/eg:.2f} 자/토), Qwen {eq} ({len(EN)/eq:.2f} 자/토)")
