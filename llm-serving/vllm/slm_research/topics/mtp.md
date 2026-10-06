# Multi-Token Prediction (MTP) — Gemma 4 / Qwen 3.6 (vLLM 기준)

> 조사일: 2026-05-12
> 대상: 두 신규 오픈웨이트 모델 패밀리(Gemma 4, Qwen 3.6)의 MTP 도입 형태와 **vLLM 서빙** 차이
> 관련 문서: [gemma4.md](../models/gemma4.md) · [qwen3.6.md](../models/qwen3.6.md) · [qwen3.5.md](../models/qwen3.5.md) · [gemma4-vs-qwen.md](gemma4-vs-qwen.md)

---

## 📌 TL;DR

1. **MTP**는 한 번의 forward에서 여러 토큰을 동시에 예측하는 학습·추론 기법. DeepSeek-V3(2024-12)가 학습 시그널 + speculative decoding 양쪽으로 정착시킨 후, 2026년 오픈웨이트 표준으로 자리잡음.
2. **Qwen 3.6은 native MTP** — 사전·사후 학습에 MTP 모듈을 포함, 추론 시 메인 모델 자기 자신의 MTP head로 draft. 별도 drafter 다운로드 불필요. vLLM method 문자열: `qwen3_next_mtp` (또는 `mtp`).
3. **Gemma 4는 external drafter** — 2026-05-05 Google이 `*-it-assistant` 4종을 별도 체크포인트로 Apache 2.0 공개. KV 캐시·임베딩을 target과 공유하는 specialized draft model. vLLM `--speculative-config`의 `model` 키에 assistant ID 지정.
4. **vLLM 0.19.0+에서 양쪽 모두 활성화 가능**. 구버전은 Gemma 4 assistant를 일반 draft model로 오인하여 init 실패.
5. **실측 결과는 워크로드 의존성이 큼** — Qwen3.6-35B-A3B-FP8 / GB10 측정: 동시성 16에서 +24.2% throughput, TTFT −56.7%. 반면 prefill-bound 워크로드에서는 TPOT +30.7% 회귀.

---

## 1. MTP 기본 개념

### 1.1 무엇이 MTP인가

표준 autoregressive 학습은 위치 t에서 t+1 토큰 한 개를 예측. MTP는 같은 위치에서 t+2, t+3 …도 추가 head로 동시에 예측하도록 학습. 학습 시그널 밀도↑, **추론 시 draft 토큰 생성기로 재사용**하여 speculative decoding 가속.

### 1.2 두 가지 구현 패턴

| 패턴 | 대표 모델 | head 구조 | 학습 통합 | drafter 배포 |
|------|-----------|----------|----------|-------------|
| **Native (sequential)** | DeepSeek-V3, Qwen3-Next, Qwen3.5/3.6 | 메인 모델 임베딩·출력 head를 공유하는 transformer layer를 t+1, t+2 … 인과 체인 | 사전·사후 학습에 포함 | 메인 모델 weight에 포함 |
| **External drafter** | Gemma 4, EAGLE/Medusa 계열 | 작은 별도 모델이 target의 마지막 layer activation을 받아 다음 토큰 예측 | target 학습 완료 **후** drafter만 별도 학습 | `*-assistant` 별도 체크포인트 |

DeepSeek-V3 원논문 표현 (arxiv 2412.19437 §2.2):
> *"Different from prior approaches which parallelly predict additional tokens using independent output heads, DeepSeek sequentially predicts additional tokens and keeps the complete causal chain at each prediction depth."*

### 1.3 가속 원리

draft 토큰을 target이 한 번의 forward로 검증 — 일치하면 일괄 수락. 분포 일치 검증을 사용하므로 **출력 분포가 base AR 생성과 수학적으로 동일** (Gemma 4 공식: "guaranteeing the exact same quality"). DeepSeek-V3 자체 보고: MTP-1 acceptance >80%, throughput ~1.8×.

---

## 2. Qwen 3.6 — Native MTP

### 2.1 라인업 (2026-05-12 기준)

Qwen3.6 네임스페이스에는 현재 두 종이 공개됨:

| 모델 | 아키텍처 | 총 파라미터 | 활성 파라미터 | 출시 | MTP 학습 |
|------|----------|-----------|-------------|------|---------|
| **Qwen3.6-35B-A3B** | Hybrid MoE (Gated DeltaNet 75% + Gated Attention 25%) | 35B | 3B | 2026-04-16 | ✅ Pre + Post |
| **Qwen3.6-27B** | Dense (Gated DeltaNet:Gated Attention = 3:1) | 27B | 27B | 2026-04 (HF citation) | ✅ Pre + Post |

> 두 모델 모두 Apache 2.0, 컨텍스트 262K native / YaRN 1.01M. 두 모델 모두 모델 카드에 *"Pre-training & Post-training with Multi-Token Prediction (MTP)"* 명시.

### 2.2 vLLM 서빙 (모델 카드 직접 인용)

**Qwen 3.6-35B-A3B-FP8**
```bash
vllm serve Qwen/Qwen3.6-35B-A3B-FP8 \
  --port 8000 --tensor-parallel-size 8 \
  --max-model-len 262144 --reasoning-parser qwen3 \
  --speculative-config '{"method":"qwen3_next_mtp","num_speculative_tokens":2}'
```

**Qwen 3.6-27B**
```bash
vllm serve Qwen/Qwen3.6-27B \
  --port 8000 --tensor-parallel-size 8 \
  --max-model-len 262144 --reasoning-parser qwen3 \
  --speculative-config '{"method":"qwen3_next_mtp","num_speculative_tokens":2}'
```

### 2.3 method 문자열: `qwen3_next_mtp` vs `mtp`

| 출처 | method 표기 |
|------|------------|
| Qwen 3.6 HF 모델 카드 | `"method":"qwen3_next_mtp"` |
| vLLM recipes (Qwen3.5/3.6 페이지) | `"method":"mtp"` |

두 문자열 모두 같은 경로를 가리키지만 vLLM 버전에 따라 한쪽만 허용될 수 있음 → 실제 환경에서 reject 여부 확인 필요.

### 2.4 실측 — Qwen3.6-35B-A3B-FP8 / DGX Spark GB10

> 출처: docai.hu 2026-05 측정. 환경: NVIDIA DGX Spark GB10 (SM 12.1), 128GB LPDDR5x, NVIDIA 580.142, CUDA 13.0, **vLLM 0.19.1rc1.dev328**, `num_speculative_tokens=2`, method `qwen3_next_mtp`.

| 테스트 | 워크로드 | Baseline tok/s | MTP tok/s | Δ throughput | TTFT Δ | TPOT Δ |
|--------|---------|:------:|:------:|:------:|:------:|:------:|
| A | 단일 decode (512→512, batch 1) | 50.51 | 54.92 | **+8.7%** | — | — |
| B | prefill-bound (8192→256, 동시 4) | 73.98 | 68.68 | **−7.2%** | −39% | **+30.7%** |
| C | 동시성 스트레스 (2048→512, 동시 16) | 214.28 | 266.25 | **+24.2%** | **−56.7%** | −17.1% |
| D | 채팅 (2048→256, 동시 2) | 73.88 | 77.60 | +5.0% | — | — |

**acceptance**: 평균 acceptance length 2.50, 평균 draft acceptance rate **74.9%** (Test A 기준). 전역 72.53%. 위치별: 0번 81.57% · 1번 63.48%.

**해석 (출처 동일 글)**: prefill-bound 워크로드(B)에서는 P99 ITL이 1053ms로 튀고 TPOT 회귀. **동시성 스트레스(C)에서는 MTP가 가장 큰 이득**.

### 2.5 실측 — Qwen3.5-27B / 8× B200 (참고치)

> 출처: qwen3.5.md §7.3 (Google Cloud GKE 측정). 아키텍처 동일 계열, vLLM 동일 method `mtp` / `qwen3_next_mtp`.

- MTP-1 활성화 시 decode step당 **~1.9 토큰** 생성 (acceptance rate **~90%**)
- 단일 노드 최대 throughput: **96,023 tokens/s**
- 12 노드 × 96 B200: **1,103,941 tokens/s** (96.5% 스케일링 효율)
- TPOT 중앙값: **~46 ms**
- 핵심 플래그: `--data-parallel-size=8`, `--kv-cache-dtype=fp8_e4m3`, `--gpu-memory-utilization=0.92`

### 2.6 알려진 vLLM 이슈 (Qwen 3.5/3.6 공통, native MTP)

| 이슈 | 번호 | 상태 | 영향 |
|------|------|:----:|------|
| MTP 활성화 시 prefix cache hit 92% → 71% | [#38182](https://github.com/vllm-project/vllm/issues/38182) | Open | 35B-A3B 기준 |
| 122B-NVFP4 0% acceptance | [#36331](https://github.com/vllm-project/vllm/issues/36331) | Closed | 35B-FP8은 정상 |
| FA3 backend 8.5× 회귀 (Hopper) | [#39323](https://github.com/vllm-project/vllm/issues/39323) | Open (nightly 수정) | FLASHINFER 백엔드 권장 |

---

## 3. Gemma 4 — External Drafter (2026-05-05 신규)

### 3.1 발표

- **2026-05-05** Google 공식 블로그: *"Accelerating Gemma 4: faster inference with multi-token prediction drafters."*
- 동일 일자 `ai.google.dev/gemma/docs/mtp/overview` 공식 가이드 공개.
- 라이선스: **drafter Apache 2.0** (Gemma 4 본체 라이선스와 별개).
- 헤드라인: **최대 3× decoding speedup, 품질 무손실** (4개 모델 카드 동일 문구).
- 공식 overview·블로그 전반에 **사이즈별 acceptance rate 및 정량 speedup 수치는 미공개** (직접 확인 완료, 2026-05-12 기준).

### 3.2 drafter 체크포인트 4종 (HF 모델 카드 직접 확인)

| Target | Drafter | Drafter 파라미터 | dtype | 라이선스 |
|--------|---------|:---------------:|:-----:|:-------:|
| `google/gemma-4-E2B-it` | `google/gemma-4-E2B-it-assistant` | **78M** | BF16 | Apache 2.0 |
| `google/gemma-4-E4B-it` | `google/gemma-4-E4B-it-assistant` | **78.8M** | BF16 | Apache 2.0 |
| `google/gemma-4-26B-A4B-it` | `google/gemma-4-26B-A4B-it-assistant` | **0.4B** | BF16 | Apache 2.0 |
| `google/gemma-4-31B-it` | `google/gemma-4-31B-it-assistant` | **0.5B** | BF16 | Apache 2.0 |

### 3.3 핵심 기술 (공식 overview 인용)

1. **Shared Input Embeddings** — drafter가 target의 input embedding table을 공유.
2. **Target Activations** — drafter가 target의 **마지막 layer activation**을 token embedding과 concat 후 down-project. → context 재계산 없음.
3. **Efficient Embedder (E2B/E4B 전용)** — 토큰을 cluster 단위로 묶고 최종 계산을 선택된 cluster 내부 토큰으로만 제한. 엣지 디바이스 가속용 (vLLM 서빙 시에는 부가 효과 제한적).

> *"The draft model shares the input embedding table with the target model."* / *"uses the activations from the last layer of the target model, concatenates them with the token embeddings, and down-projects them."* / *"groups similar tokens into clusters … restricts its final calculations to only the tokens within those selected clusters (E2B and E4B only)."* — ai.google.dev/gemma/docs/mtp/overview 원문.

### 3.4 vLLM 사이즈별 권장 (공식 recipes 직접 인용)

| Model | `num_speculative_tokens` | TP |
|-------|:------------------------:|:--:|
| E2B | 2 | 1 |
| E4B | 4 | 1 |
| 26B-A4B | 4 | 2 |
| 31B | **4–8** | 2 |

**31B 온라인 서빙 (recipes 원문)**
```bash
vllm serve google/gemma-4-31B-it \
  --tensor-parallel-size 2 \
  --max-model-len 8192 \
  --speculative-config '{"model": "google/gemma-4-31B-it-assistant", "num_speculative_tokens": 4}'
```

**E4B 오프라인 추론 (recipes 원문, `--speculative-config` 부분만)**
```bash
--speculative-config '{"model": "google/gemma-4-E4B-it-assistant", "num_speculative_tokens": 4}'
```

> recipes 노트: *"Higher `num_speculative_tokens` increases draft overhead per cycle. Optimal value depends on target model speed."* 느린 target(31B)일수록 큰 값, 빠른 target(E2B)일수록 작은 값.

### 3.5 vLLM 버전 요구사항

- vLLM 0.19.0 미만은 assistant 모델을 일반 draft model로 오인 → init 실패.
- vLLM MTP 기능 페이지 원문: *"Gemma 4 assistants are not generic draft models"*, *"Upgrade to a version with Gemma 4 MTP support instead."*
- 내부적으로 `model_type: gemma4_assistant`를 인식해 specialized draft 경로로 처리.

### 3.6 모델별 특이사항 (공식 overview 명시)

- **26B-A4B (MoE)** — *"the 26B A4B drafter may not yield speedups on hardware platforms without good parallelism"* at batch size 1. 매 토큰이 다른 expert를 활성화시켜 expert weight 로딩 비용 발생. *"At higher batch sizes, there is typically more overlap in activated experts across sequences."* → vLLM 서빙에서는 동시성 4–8 이상 권장.
- **E2B / E4B** — drafter 자체가 ~78M로 매우 작음. vLLM에서는 KV 캐시 부담 거의 없음.
- **31B** — Dense이므로 MoE 라우팅 비용 없음. `num_speculative_tokens` 범위가 가장 넓음 (4–8).
- **사이즈별 정량 speedup 수치는 공식 미공개**. 헤드라인 "최대 3×"가 4개 모두에 동일 적용됨.

---

## 4. 두 모델 직접 비교 (vLLM 관점)

### 4.1 핵심 차이

| 항목 | Qwen 3.6 (native) | Gemma 4 (external) |
|------|:-----------------:|:------------------:|
| **MTP 패러다임** | Sequential native head | External drafter |
| **drafter 체크포인트** | 불필요 (메인 모델 내장) | `*-it-assistant` 4종 별도 다운로드 |
| **drafter 크기** | n/a | E2B 78M / E4B 78.8M / 26B-A4B 0.4B / 31B 0.5B |
| **MTP 학습 시점** | Pre-training + Post-training | target 학습 후 drafter만 별도 학습 |
| **vLLM `--speculative-config` 필드** | `method` (+`num_speculative_tokens`) | `model` (+`num_speculative_tokens`) |
| **method 문자열** | `qwen3_next_mtp` (카드) / `mtp` (recipes) | (assistant model ID 자체로 식별) |
| **권장 `num_speculative_tokens`** | 2 (recipes 기본) | 사이즈별: E2B 2 / E4B 4 / 26B-A4B 4 / 31B 4–8 |
| **vLLM 최소 버전** | 0.19.0+ | 0.19.0+ (`gemma4_assistant` 인식) |
| **공식 acceptance / speedup** | 미공개. GB10 실측 74.9% (35B-A3B-FP8) / B200 ~90% (27B Qwen3.5) | 미공개. 헤드라인 "최대 3×"만 |
| **라이선스** | Apache 2.0 (메인 포함) | drafter Apache 2.0 + target Gemma 라이선스 |
| **KV 캐시 공유** | 내장 head이므로 자연스럽게 공유 | 공식 설계 — drafter가 target과 share |

### 4.2 운영 트레이드오프

**Native (Qwen 3.6) 장점**
- 단일 체크포인트, 단일 가중치 → vLLM에서 모델 로딩 단순.
- 학습 시점부터 MTP 포함 → head 품질이 target과 동기화.
- 라이선스 단일.

**External drafter (Gemma 4) 장점**
- target은 MTP 없이도 정상 서빙 가능 — 옵션이 결합되지 않음.
- drafter만 별도 업데이트/교체 가능.
- MoE target에 dense drafter를 붙여 expert routing 비용을 drafter에서 회피.

**공통 함정 (vLLM 운영)**
- **워크로드 의존성이 매우 큼**. 동일 모델·동일 설정도 prefill-bound vs decode-bound에 따라 ±30% 이상 정반대 효과 (Qwen3.6 GB10 측정 Test B vs C).
- prefix caching과 MTP 동시 사용 시 cache hit 저하 (vLLM #38182, Qwen 측 보고). Gemma 4는 신규라 실측 부족.
- 양자화 조합에 따라 acceptance 0%로 떨어지는 사례 (Qwen3.5-122B-NVFP4 #36331). Gemma 4의 양자화 + MTP 조합은 출시 1주일 차로 검증 거의 없음.
- 고동시성 vs 저동시성은 정답이 다름. Qwen3.6 GB10 실측 기준 **동시성 16이 sweet spot** (+24.2%), 동시성 4 prefill-bound는 회귀 (−7.2%).

---

## 5. vLLM 운영 권장 (현재 운영 환경 L40S 46GB × 2 기준)

> 주의: 아래 권장의 실측 근거는 GB10·B200 환경이라 **L40S에서는 직접 검증되지 않음**. 도입 시 사내 벤치 필수.

### 5.1 Qwen 3.6-35B-A3B-FP8 (조사 당시 운영 모델; 현재는 27B-FP8)

```bash
vllm serve Qwen/Qwen3.6-35B-A3B-FP8 \
  --tensor-parallel-size 2 \
  --max-model-len 262144 \
  --reasoning-parser qwen3 \
  --speculative-config '{"method":"qwen3_next_mtp","num_speculative_tokens":1}'
```

- L40S의 메모리 여유를 고려해 우선 `num_speculative_tokens: 1`부터 시작 (recipes 기본 2보다 보수적).
- prefix caching 활성화 시 hit rate 모니터링 필수 (#38182).
- FA3 backend 회귀(#39323) 회피 위해 FLASHINFER 백엔드 병용.

### 5.2 Gemma 4 31B-it 도입 시

```bash
vllm serve google/gemma-4-31B-it \
  --tensor-parallel-size 2 \
  --max-model-len 8192 \
  --speculative-config '{"model":"google/gemma-4-31B-it-assistant","num_speculative_tokens":4}'
```

- vLLM 0.19.0 미만은 `gemma4_assistant` 미인식 → 최신 본관 필수.
- L40S×2로 31B Dense는 BF16 약 62GB → KV 캐시 여유 빠듯. 보수적으로 `--max-model-len 8192`로 시작 후 OOM 없으면 점진 확대.
- 26B-A4B drafter는 batch size 작을 때 효과 제한적 (공식 경고) → 동시성 4–8 이상에서만 의미.

### 5.3 도입 결정 가이드

| 워크로드 | 추천 |
|----------|------|
| **저지연 단발 호출** (대화·번역·요약, 동시성 1–4) | MTP 활성. Qwen 3.6 우선 (현 운영). Test A 측정 +8.7%. |
| **중간 동시성 채팅** (동시성 2–8) | MTP 활성. GB10 Test D 측정 +5.0%. |
| **고동시성 배치** (동시성 16+) | Qwen 3.6 MTP가 가장 큰 이득 — GB10 Test C +24.2%. |
| **긴 prompt + 짧은 응답** (RAG, 분류) | **MTP 비활성** 권장. GB10 Test B에서 −7.2% throughput / TPOT +30.7% 회귀 확인. |
| **장문맥 응답** (>128K) | Qwen 3.6 (262K native, YaRN 1M). MTP는 짧은 출력에서 이득이 크므로 효과 제한. |

### 5.4 본 환경 실측 (2026-07-21, L40S×2 TP2 — 사후 추가)

§5의 "L40S 직접 검증되지 않음" 주의에 대한 사내 실측 결과. 설정·운영 노하우 원본은 `instances/gemma-26b.yaml` 및 `instances/_SCHEMA.txt`, 속도 수치 원본은 `tests/results/speed_results.md`.

- **Gemma 4 31B-it + assistant drafter** (`num_speculative_tokens: 4`): acceptance **70~85% 관찰** — GB10 계열 이슈 #41789(저 acceptance)는 본 환경에서 재현되지 않음.
- **Gemma 4 26B-A4B-it (MoE) + assistant drafter** (fp8, `num_speculative_tokens: 4`): 저동시성에서 acceptance **32~47% 관찰** — MoE의 저동시성 drafter 이득 제한(공식 경고, §5.2)과 부합. 동시성 4+ 실측 후 `num_speculative_tokens` 4→2 하향 검토(백로그).
- 그래도 절대 속도는 26B-A4B가 우위: 동시성 1에서 TPS 168.5~171.2 / TTFT ~49ms로 31B(70.5~72.5 / ~88ms) 대비 **약 2.4배**, 동시성 10에서도 81.0 vs 43.2로 약 1.9배.
- drafter `model`은 인스턴스 yaml에서 `${model}-assistant`로 쓰면 런처가 본체 model을 자동 치환한다. ⚠️ Gemma 4는 `method` 키 명시 금지(자동 감지, 명시 시 NotImplementedError).

---

## 6. Sources

### 공식 1차 자료 (직접 fetch 검증)
- [Qwen3.6-35B-A3B HF 모델 카드](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) — `qwen3_next_mtp` 서빙 명령
- [Qwen3.6-27B HF 모델 카드](https://huggingface.co/Qwen/Qwen3.6-27B) — 27B Dense + MTP 학습 명시
- [Qwen3.5 & Qwen3.6 vLLM Recipes](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen3.5.html) — `method:mtp` 표기
- [vLLM MTP 기능 페이지](https://docs.vllm.ai/en/latest/features/speculative_decoding/mtp/) — Gemma 4 assistant 지원, *"not generic draft models"* 경고
- [Gemma 4 vLLM Recipes](https://docs.vllm.ai/projects/recipes/en/latest/Google/Gemma4.html) — 사이즈별 권장 표
- [Google 공식 블로그 — Accelerating Gemma 4 (2026-05-05)](https://blog.google/innovation-and-ai/technology/developers-tools/multi-token-prediction-gemma-4/)
- [ai.google.dev Gemma MTP Overview](https://ai.google.dev/gemma/docs/mtp/overview) — shared embeddings / target activations / efficient embedder
- [google/gemma-4-E2B-it-assistant HF](https://huggingface.co/google/gemma-4-E2B-it-assistant) — 78M params Apache 2.0
- [google/gemma-4-E4B-it-assistant HF](https://huggingface.co/google/gemma-4-E4B-it-assistant) — 78.8M params
- [google/gemma-4-26B-A4B-it-assistant HF](https://huggingface.co/google/gemma-4-26B-A4B-it-assistant) — 0.4B params
- [google/gemma-4-31B-it-assistant HF](https://huggingface.co/google/gemma-4-31B-it-assistant) — 0.5B params

### 학술 / 해설
- [DeepSeek-V3 Technical Report (arxiv 2412.19437)](https://arxiv.org/html/2412.19437v1) — sequential MTP head, MTP-1 acceptance >80%, ~1.8× throughput
- [Sebastian Raschka — LLM Architecture Gallery: MTP](https://sebastianraschka.com/llm-architecture-gallery/mtp/)
- [NVIDIA Megatron-Bridge MTP](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/multi-token-prediction.html)

### 검증된 vLLM 실측 (수치 인용)
- [docai.hu — Qwen3.6-35B-A3B-FP8 MTP on DGX Spark GB10 (2026-05)](https://docai.hu/en/blog/qwen36-mtp-gb10) — vLLM 0.19.1rc1, 4가지 워크로드 baseline vs MTP, acceptance 74.9%

### vLLM 이슈
- [#38182 — MTP reduces prefix cache hit rate (Open)](https://github.com/vllm-project/vllm/issues/38182)
- [#36331 — 122B NVFP4 MTP 0% acceptance (Closed)](https://github.com/vllm-project/vllm/issues/36331)
- [#39323 — FA3 backend 회귀 (Open, nightly 수정)](https://github.com/vllm-project/vllm/issues/39323)

### 내부 문서
- [gemma4.md](../models/gemma4.md) — Gemma 4 본체 스펙 / 벤치
- [qwen3.6.md](../models/qwen3.6.md) — Qwen 3.6-35B-A3B 본체 스펙
- [qwen3.5.md](../models/qwen3.5.md) §7.3 — Qwen3.5-27B B200 MTP 실측 (96k tok/s)
- [gemma4-vs-qwen.md](gemma4-vs-qwen.md) §3.3 — ⚠ 2026-05-05 이전 작성으로 "Gemma 4 MTP 미지원" 표기가 outdated
