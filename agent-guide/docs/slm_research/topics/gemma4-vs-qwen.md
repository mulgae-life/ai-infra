# Gemma 4 vs Qwen 3.6 — 운영 관점 비교

> 조사일: 2026-04-20
> 대상: L40S 46GB × 2 (chatbot-poc 현재 운영 프로필) 기준 모델 선택 가이드
> 비교 버전
>   - **Qwen 3.6-35B-A3B-FP8** (2026-04-16 출시) — 조사 당시 운영 모델
>   - **Gemma 4 31B-it** (2026-04-02 출시) — 주 비교 대상 (Dense 플래그십)
>   - **Gemma 4 26B-A4B-it** (2026-04-02 출시) — 보조 비교 대상 (MoE)
>
> ⚠️ **현행 모델은 이 표와 다르다** (2026-08-20 기준). 연구계 `qwen.yaml`은 **Qwen3.8-27B-FP8**,
> 운영계 `prd-gemma.yaml`은 **Gemma 4 26B-A4B-it**이다. Qwen 쪽 세대 갱신분은 [2.6](#26-qwen38-27b-갱신-2026-08-20)에 정리했다.
>
> 상세 스펙 원문: [qwen3.8.md](../models/qwen3.8.md) · [qwen3.6.md](../models/qwen3.6.md) · [gemma4.md](../models/gemma4.md)

---

## 📌 TL;DR (3줄 요약)

1. **Qwen 3.6은 에이전트·코딩·멀티모달 모두에서 Gemma 4 대비 우세**. 특히 Tool calling·HLE·SWE-bench Multilingual에서 격차가 큼.
2. **Gemma 4는 다국어(MMMLU)와 경쟁 코딩(CodeForces ELO)에서 우위**. 단, Qwen 3.6도 현저히 따라붙었고 Mamba-hybrid 구조로 **KV 메모리 효율이 월등**.
3. **운영 안정성은 Qwen 3.6이 우세** — FP8 사전 양자화 체크포인트, Apache 2.0, MTP 지원, vLLM 공식 레시피 보유. Gemma 4는 라이선스·의존성 면에서 더 까다로움.

---

## 1. 모델 스펙 한눈에 보기

| 항목 | **Qwen 3.6-35B-A3B (조사 당시)** | Gemma 4 31B-it | Gemma 4 26B-A4B-it |
|------|:---------------------------:|:--------------:|:------------------:|
| **출시일** | 2026-04-16 | 2026-04-02 | 2026-04-02 |
| **총 파라미터** | 35B | 30.7B | ~45B |
| **활성 파라미터** | **3B** (MoE) | 30.7B (Dense) | 3.8B (MoE) |
| **아키텍처** | Hybrid MoE: Gated DeltaNet 75% + Gated Attention 25% (**Mamba-hybrid**) | Dense + Hybrid Attention (Sliding+Global) | MoE + Hybrid Attention |
| **레이어** | 40 | 60 | 30 |
| **어휘** | 248,320 | 262,144 | 262,144 |
| **컨텍스트 (네이티브)** | **262K** | 256K | 256K |
| **컨텍스트 (YaRN)** | **1.01M** | — | — |
| **멀티모달** | **텍스트 + 이미지 + 비디오** | 텍스트 + 이미지 | 텍스트 + 이미지 |
| **기본 dtype** | **FP8 사전 양자화** (E4M3 block 128) | BF16 | BF16 |
| **라이선스** | **Apache 2.0** | Gemma (제한 有) | Gemma (제한 有) |
| **HF 토큰** | 불필요 | 불필요 | 불필요 |

> **핵심 차이**
> - **Qwen 3.6은 MoE**지만 활성 파라미터가 3B에 불과해 추론 비용이 극히 낮습니다. 반면 총 가중치는 35GB로 Dense 31B(~29GB)와 크게 다르지 않아 **VRAM 예산은 비슷**합니다.
> - **Mamba-hybrid**는 Full-Attention 대비 KV 캐시 요구량이 낮습니다 — 긴 컨텍스트/대형 배치에 유리.
> - **멀티모달 범위**: Qwen 3.6은 비디오까지 공식 지원. Gemma 4는 이미지만.

---

## 2. 벤치마크 직접 비교

> 출처: Qwen 3.6 HF 모델 카드, Gemma 4 공식 모델 카드. Thinking 모드 활성화 기준.

### 2.1 언어 / 지식 / 추론

| 벤치마크 | Qwen 3.6-35B-A3B | Gemma 4 31B | 우세 |
|----------|:---------------:|:-----------:|:----:|
| **MMLU-Pro** | 85.2 | 85.2 | ⚖️ 동률 |
| **MMLU-Redux** | 93.3 | — | — |
| **GPQA Diamond** | 86.0 | 84.3 | 🟢 **Qwen** (+1.7) |
| **SuperGPQA** | 64.7 | — | — |
| **BigBench Extra Hard** | — | 74.4 | — |
| **AIME 2026** | 92.7 | 89.2 | 🟢 **Qwen** (+3.5) |
| **HMMT Feb 26** | 83.6 | — | — |
| **IMOAnswerBench** | 78.9 | — | — |

### 2.2 코딩 / 에이전트 (Qwen 3.6 핵심 개선 영역)

| 벤치마크 | Qwen 3.6-35B-A3B | Gemma 4 31B | 우세 |
|----------|:---------------:|:-----------:|:----:|
| **LiveCodeBench v6** | **80.4** | 80.0 | 🟢 Qwen (+0.4) |
| **Codeforces ELO** | — | **2150** | 🟡 Gemma (Qwen 미공개) |
| **SWE-bench Verified** | **73.4** | — | 🟢 Qwen (데이터 공개) |
| **SWE-bench Multilingual** | **67.2** | — | 🟢 Qwen |
| **SWE-bench Pro** | **49.5** | — | 🟢 Qwen |
| **Terminal-Bench 2.0** | **51.5** | — | 🟢 Qwen |
| **Tau2-Bench (에이전트)** | — | 76.9 | 🟡 Gemma (데이터 공개) |

### 2.3 비전 / 멀티모달

| 벤치마크 | Qwen 3.6-35B-A3B | Gemma 4 31B | 우세 |
|----------|:---------------:|:-----------:|:----:|
| **MMMU** | 81.7 | — | — |
| **MMMU-Pro** | **75.3** | 76.9 | 🟡 Gemma (+1.6) |
| **MathVista (mini)** | 86.4 | — | — |
| **MATH-Vision** | — | 85.6 | — |
| **RealWorldQA** | 85.3 | — | — |
| **MMBench EN-DEV-v1.1** | 92.8 | — | — |
| **OmniDocBench 1.5** | 89.9 | — | — |
| **VideoMME (w sub)** | 86.6 | — | 🟢 Qwen (비디오 고유) |
| **VideoMMMU** | 83.7 | — | 🟢 Qwen |

### 2.4 다국어 / 한국어

| 벤치마크 | Qwen 3.6-35B-A3B | Gemma 4 31B | 우세 |
|----------|:---------------:|:-----------:|:----:|
| **MMMLU (다국어)** | — | **88.4** | 🟡 **Gemma** |
| **SWE-bench Multilingual** | **67.2** | — | 🟢 Qwen |
| **LogicKor / KMMLU (한국어)** | 공식 미공개 | 공식 미공개 | — |

> ⚠️ **한국어 단독 벤치마크는 두 모델 모두 공식 수치 없음**. 아키텍처·어휘·학습 레시피 기반 추정만 가능.
> - Qwen 3.6: Qwen3.5와 어휘(248K padded)·학습 레시피 공유. 커뮤니티 한국어 벤치 갱신 대기 중.
> - Gemma 4: 262K 어휘, MMMLU 88.4로 다국어 기본기 우수. 한국어 LogicKor 미공개.
> - **운영 검증 필요** — 실제 프롬프트로 A/B 비교 권장.

### 2.5 벤치마크 요약

- **Qwen 3.6 강점**: 수학(AIME, HMMT), SWE-bench·Terminal-Bench 계열 에이전트 코딩, 비디오 멀티모달, MoE 활성 3B 효율.
- **Gemma 4 강점**: 다국어(MMMLU), 경쟁 코딩(Codeforces ELO), 비전 일부(MMMU-Pro).
- **비교 불가 영역**: Qwen 3.6이 Tau2/HLE 수치 미공개, Gemma 4가 SWE-bench 수치 미공개. **동일 벤치 직접 비교 가능한 항목에서는 대부분 Qwen 3.6 우세**.

### 2.6 Qwen3.8-27B 갱신 (2026-08-20)

연구계 인스턴스가 Qwen3.8-27B-FP8로 교체되면서 위 표의 Qwen 열은 두 세대 뒤처진 값이 됐다. **두 모델카드가 같은 이름으로 싣는 벤치마크는 세 개뿐이다.**

| 벤치마크 | **Qwen3.8-27B** | Gemma 4 31B | Gemma 4 26B-A4B |
|------|:---:|:---:|:---:|
| **GPQA Diamond** | **89.2** | 84.3 | 82.3 |
| **LiveCodeBench v6** | **90.3** | 80.0 | 77.1 |
| **HLE** | **30.8** | 19.5 (검색 사용 26.5) | 8.7 (검색 사용 17.2) |

Qwen3.8 카드에만 있는 항목은 SWE-bench Pro 61.7, Terminal Bench 2.1 73.0, IFBench 79.5이고, Gemma 4 카드에만 있는 항목은 MMLU-Pro 85.2, AIME 2026 89.2, Tau2 76.9, MMMLU 88.4다. 서로 비는 칸이 많아 종합 우열은 위 세 항목 밖으로 넓힐 수 없다.

> ⚠️ **세 가지를 함께 볼 것.**
> - **측정 조건이 다르다.** Qwen 쪽 코딩·에이전트 수치는 Claude Code 하네스에 256K 컨텍스트, `temperature=1.0` 기준이고 HLE는 GPT-4o가 채점했다. 두 자릿수 격차만 신호로 본다.
> - **thinking을 켠 기준이다.** 현행 `qwen.yaml`은 `enable_thinking: false`라 위 수치가 그대로 재현되지 않는다.
> - **한국어는 방향이 반대다.** 디노티시아 한국어 0.9000(Gemma 31B) 대 0.8775(Qwen3.5-27B), NOLLI 거시평균 48.3 대 44.4로 Gemma가 앞선다. 상세는 [korean-ability.md](korean-ability.md).
>
> 아키텍처·서빙 설정은 [qwen3.8.md](../models/qwen3.8.md) 참조. 27B 계열은 3.5·3.6·3.8의 `config.json`이 `transformers_version`만 다를 정도로 동일해 서빙 프로필을 다시 잡을 필요가 없다.

---

## 3. 서빙 관점 (L40S 46GB × 2, `tensor_parallel_size: 2` 기준)

| 항목 | Qwen 3.6-35B-A3B-FP8 | Gemma 4 31B (FP8 온라인) | Gemma 4 26B-A4B (FP8 온라인) |
|------|:---:|:---:|:---:|
| **가중치 (rank당)** | ~17.5 GB | ~14.5 GB | ~12.5 GB |
| **KV Cache 가용** | 넉넉 (Mamba-hybrid로 절감) | ~58.4 GB | 중간 (MoE ~45B 기준) |
| **권장 `max_model_len`** | **262144** (실기동 확인) | 65536 ~ 131072 | 32768 ~ 65536 |
| **FP8 방식** | **사전 양자화 체크포인트** (E4M3) | 온라인 양자화 (`quantization: fp8`) | 온라인 양자화 |
| **양자화 오차** | 원본 대비 거의 동일 (모델 카드) | 가중치 FP8 직접 할당 → 레이어별 변환 | 동일 |
| **vLLM 최소 버전** | **0.19.0** | 0.19.0 | 0.19.0 |
| **transformers 최소** | ≥4.56.0 | ≥5.5.0 (pip 충돌 우회 필요) | ≥5.5.0 |
| **설치 복잡도** | **낮음** | 높음 (의존성 충돌) | 높음 |
| **공식 vLLM 레시피** | **있음** (Qwen3.5/3.6 페이지) | 있음 | 있음 |

### 3.1 양자화 전략 차이

- **Qwen 3.6 FP8**: HuggingFace에 이미 FP8로 공개된 체크포인트(`Qwen/Qwen3.6-35B-A3B-FP8`). `quantization` 설정 불필요. **로딩이 빠르고 일관적**.
- **Gemma 4 FP8**: BF16 체크포인트를 vLLM이 **로딩 중 FP8로 온라인 양자화**. `quantization: fp8` 필수. 가중치를 FP8로 직접 할당 후 레이어별 변환하므로 BF16 전체 로드보다 메모리 효율적.

### 3.2 아키텍처에 따른 KV 캐시 차이

- **Qwen 3.6 (Mamba-hybrid)**: 40 레이어 중 30개(75%)가 Gated DeltaNet(O(1) state), 10개(25%)만 Full Attention(O(n) KV). **Full-Attention 모델 대비 KV 요구량 현저히 낮음** — 긴 컨텍스트·대형 배치에 유리.
- **Gemma 4 (Hybrid Attention)**: Sliding Window(1024) + Global 교대 배치. 슬라이딩은 KV 상한이 윈도우 크기에 고정되므로 KV 부담이 Dense보다 낮음. 하지만 Mamba-hybrid만큼 극단적으로 절감되지는 않음.

> ⚠️ vLLM KV cache profiler가 Mamba-hybrid 구조에서 **~7배 과잉추정**(vllm-project/vllm [#37121](https://github.com/vllm-project/vllm/issues/37121)) 이슈가 있어, Qwen 3.6은 실제 `num_gpu_blocks`를 기동 로그로 재확인해야 합니다.

### 3.3 Speculative Decoding (MTP)

| 항목 | Qwen 3.6 | Gemma 4 |
|------|:--------:|:-------:|
| **MTP 지원** | ✅ (공식 학습에 MTP 포함) | ❌ |
| **설정** | `--speculative-config '{"method":"mtp","num_speculative_tokens":2}'` | N/A |
| **실측 효과** | B200 기준 ~96K tokens/s, 수락률 90% | — |

> Qwen 3.6은 MTP로 2토큰 예측 → 처리량 큰 폭 향상. Gemma 4는 현재 공식 지원 없음.

---

## 4. 기능 비교 표

| 기능 | Qwen 3.6-35B-A3B | Gemma 4 31B | 비고 |
|------|:---------------:|:-----------:|------|
| **Thinking 기본값** | ON (서버 config로 OFF 덮음) | OFF | 운영 서버는 둘 다 OFF로 통일 |
| **Thinking 형식** | `<think>...</think>` (일반 토큰) | `<\|channel>thought...<channel\|>` (스페셜 토큰) | |
| **`reasoning_parser`** | `qwen3` | `gemma4` | 모델별 설정 |
| **Thinking reasoning 분리 조건** | 기본 지원 | `skip_special_tokens: false` **요청 바디에 필수** | Gemma 4 non-streaming 특이점 |
| **`preserve_thinking`** | ✅ (Qwen 3.6 신규) | ❌ | 멀티턴 reasoning 히스토리 유지 |
| **`/think`·`/nothink` 소프트 스위치** | ❌ (Qwen 3.6 제거) | ❌ | Qwen 3 계열과의 분기점 |
| **Tool Calling** | ✅ `qwen3_xml` 또는 `qwen3_coder` | ✅ `gemma4` | 파서 차이 |
| **Tool call 형식** | XML (`<tool_call>...</tool_call>`) | `<\|tool_call>call:func{...}<tool_call\|>` | |
| **이미지 지원** | ✅ | ✅ | |
| **비디오 지원** | ✅ (네이티브) | ❌ | `temporal_patch_size` config 포함 |
| **오디오 지원** | ❌ (Qwen3.5-Omni 별도 모델) | ❌ | |
| **MCP 서버 통합** | ✅ (모델 카드 명시) | — | |

---

## 5. 운영 관점 주의사항

### 5.1 Qwen 3.6 Mamba-hybrid 제약 (현재 운영 중)

- **`disable_chunked_mm_input: true` 절대 금지**
  - `enable_prefix_caching: true` → `mamba_cache_mode='align'` 자동 활성 → attention block_size가 1056 같은 큰 값으로 확장.
  - `vllm/config/vllm.py:1730`의 `validate_block_size()`가 `disable_chunked_mm_input=True`를 **AssertionError로 거부**.
  - 일반 VL 모델 가이드에서 권장하는 옵션이지만 Mamba-hybrid에서는 반대로 동작.
- **`async_scheduling: false` 필수**
  - Scheduler ↔ Worker 1-step 시차로 encoder cache race → `AssertionError: Encoder cache miss` 발생 (2026-04-18 재현).
  - TPS 5~15% 감수하고 안정성 선택.
- **`mm_encoder_tp_mode: data` / `mm_processor_cache_type: shm`** — 공식 Qwen3.5/3.6 레시피 권장.

### 5.2 Gemma 4 주의사항

- **`skip_special_tokens: false`가 요청 바디에 필수**
  - `<|channel>...<channel|>` 경계 토큰이 스페셜 토큰 → 기본값 `true`면 경계 토큰이 제거되어 `reasoning_content` 분리 실패.
  - 요청마다 `"skip_special_tokens": false` 명시해야 reasoning 분리가 작동.
- **의존성 충돌**
  - `transformers >= 5.5.0` 필요. 기존 `transformers 4.x` 환경과 pip 충돌 가능.
- **Mamba-hybrid 제약 없음** — 일반 Transformer 모델처럼 운영 가능.

### 5.3 각 모델의 알려진 vLLM 이슈

| 이슈 | 영향 모델 | 요약 |
|------|:---------:|------|
| [vllm #37121](https://github.com/vllm-project/vllm/issues/37121) | **Qwen 3.6** | Hybrid Mamba/Attention KV cache ~7배 과잉추정 → `num_gpu_blocks` 로그 확인 필요 |
| [vllm #37602](https://github.com/vllm-project/vllm/issues/37602) | **Qwen 3.5/3.6** | Qwen 3.5 계열 동시 이미지 10+에서 EngineCore 크래시 → `max_num_seqs: 5` 상한으로 방어 |
| [vllm #38643](https://github.com/vllm-project/vllm/issues/38643) | **Qwen 3.5/3.6** | FLA linear attention 포맷 불일치 gibberish → 0.19.0 수정 여부 확인 필요 |
| [vllm #40124](https://github.com/vllm-project/vllm/issues/40124) | Qwen 3.x Ampere | TurboQuant KV + Hybrid MoE 조합이 Ampere(SM 80-86)에서 실패. **L40S(SM 89) 영향 없음** |
| 자체 Bug 2026-04-18 | **Qwen 3.6** | `Encoder cache miss` assertion (async_scheduling race) → 운영 config에 반영됨 |
| 의존성 충돌 | **Gemma 4** | `transformers 5.5.0` 요구 |

---

## 6. 용도별 권장

### 6.1 chatbot-poc RAG + Tool Calling 파이프라인 (현재 주요 유스케이스)

| 요구사항 | 권장 | 이유 |
|----------|:----:|------|
| **Tool calling 중심** | 🟢 **Qwen 3.6** | SWE-bench·Terminal-Bench·에이전트 벤치 전반 우세. MCP 통합 지원 |
| **에이전트 반복 루프** | 🟢 **Qwen 3.6** | `preserve_thinking` 고유 지원 → reasoning 재사용 효율 |
| **빠른 응답 (Thinking OFF)** | 🟢 **Qwen 3.6** | MoE 활성 3B → 추론 지연 극히 낮음 |
| **복잡한 수학·코딩 정밀도** | 🟢 **Qwen 3.6** | AIME·HMMT·SWE-bench Pro 우세 |

### 6.2 이미지 / 비디오 멀티모달

| 요구사항 | 권장 | 이유 |
|----------|:----:|------|
| **비디오 이해** | 🟢 **Qwen 3.6** | 네이티브 지원. Gemma 4는 미지원 |
| **이미지 단일 모드 고해상도** | 🟡 **Gemma 4 31B** | MMMU-Pro 76.9 vs Qwen 75.3 — 근소 우세 |
| **문서 OCR·차트 해석** | 🟢 **Qwen 3.6** | OmniDocBench 89.9, CC-OCR 81.9 |
| **멀티모달 동시 요청 안정성** | 🟢 **Qwen 3.6** | `async_scheduling: false` + encoder cache 설계 이미 최적화 |

### 6.3 다국어 / 한국어

| 요구사항 | 권장 | 이유 |
|----------|:----:|------|
| **범용 다국어 기초** | 🟡 **Gemma 4 31B** | MMMLU 88.4 — Qwen 수치 미공개이나 Gemma 강점 영역 |
| **한국어 운영** | ⚠️ **A/B 검증 필수** | 두 모델 모두 공식 한국어 벤치 없음 |
| **다국어 에이전트 코딩** | 🟢 **Qwen 3.6** | SWE-bench Multilingual 67.2 |

### 6.4 운영 안정성·간편함

| 요구사항 | 권장 | 이유 |
|----------|:----:|------|
| **빠른 도입** | 🟢 **Qwen 3.6** | FP8 사전 양자화, 낮은 설치 복잡도, Apache 2.0 |
| **라이선스 제약** | 🟢 **Qwen 3.6** | Gemma 4는 Gemma 라이선스(사용 조건 有), Qwen은 Apache 2.0 |
| **vLLM 공식 레시피** | 🟡 둘 다 있음 | Qwen3.6은 Qwen3.5와 같은 페이지에 합쳐져 있음 |

### 6.5 종합 추천

**chatbot-poc의 RAG + Tool Calling + 이미지 입력 파이프라인** 검토 결론은 **Qwen 3.6-35B-A3B-FP8이 최적**이었습니다 (현재 운영은 동일 Qwen3.6 계열 **27B-FP8**로 교체).

- ✅ MoE 3B 활성 → 지연 최소, 처리량 최대
- ✅ Mamba-hybrid → KV 메모리 효율
- ✅ 에이전트·코딩·Tool calling 벤치에서 Gemma 4 우세
- ✅ 비디오까지 네이티브 지원
- ✅ Apache 2.0, FP8 체크포인트, MTP 지원

**Gemma 4는 다음 상황에서 고려**:
- 한국어·다국어 정확도가 중요한 고객 응대에서 Qwen 3.6이 부족하다고 검증될 때
- Mamba-hybrid 이슈(#37121, #38643)가 장애로 이어질 때 — Transformer 기반 안정성 필요 시
- CodeForces 스타일 경쟁 코딩 특화 유스케이스

---

## 7. 모델 교체 퀵 가이드

`instances/<name>.yaml`에서 아래 부분만 바꾸면 됩니다 (현 운영은 `instances/qwen.yaml`).

```yaml
# ─────────────────────────────────────────────
# Qwen 3.6-35B-A3B-FP8 (조사 당시; 현재 운영은 27B-FP8)
# ─────────────────────────────────────────────
model: Qwen/Qwen3.6-35B-A3B-FP8
# quantization 생략 (사전 양자화라 자동 감지)
served_model_name: [Qwen3.6-35B-A3B-FP8]
tool_call_parser: qwen3_xml              # 또는 qwen3_coder (카드 권장)
reasoning_parser: qwen3
# Mamba-hybrid 운영 필수
async_scheduling: false
mm_encoder_tp_mode: data
mm_processor_cache_type: shm
# disable_chunked_mm_input 설정 금지!

# ─────────────────────────────────────────────
# Gemma 4 31B-it (Dense 플래그십)로 교체 시
# ─────────────────────────────────────────────
# model: google/gemma-4-31B-it
# quantization: fp8                      # BF16 → FP8 온라인 양자화
# served_model_name: [gemma-4-31B-it]
# tool_call_parser: gemma4
# reasoning_parser: gemma4
# async_scheduling: true                 # Gemma 4는 기본값 유지 가능
# mm_encoder_tp_mode: weights            # 기본값
# mm_processor_cache_type: lru           # 기본값

# ─────────────────────────────────────────────
# Gemma 4 26B-A4B-it (MoE)로 교체 시
# ─────────────────────────────────────────────
# model: google/gemma-4-26B-A4B-it
# quantization: fp8
# served_model_name: [gemma-4-26B-A4B-it]
# tool_call_parser: gemma4
# reasoning_parser: gemma4
```

> 교체 후:
> 1. `.env`의 `CHAT_MODEL`·`RERANKER_MODEL`을 새 `served_model_name`과 일치시킬 것.
> 2. Gemma 4로 교체 시 클라이언트 요청에 `"skip_special_tokens": false`를 추가해야 `reasoning_content` 분리 가능.
> 3. `./start.sh restart <인스턴스명>`(예: `gemma`)으로 재기동. (무인자 호출은 [y/N] 전체 재시작 프롬프트가 뜬다.)

---

## 8. 결론

| 관점 | 우위 |
|------|------|
| **벤치마크 전반** | 🟢 Qwen 3.6 (에이전트·코딩·비디오) / 🟡 Gemma 4 (다국어·Codeforces) |
| **서빙 효율** | 🟢 **Qwen 3.6 압도** — 활성 3B + Mamba-hybrid + FP8 사전 양자화 |
| **운영 안정성** | 🟢 **Qwen 3.6** — 라이선스·의존성·공식 레시피 모두 유리 |
| **특수 케이스** | Gemma 4는 다국어·경쟁 코딩에서 선택지로 남겨둘 가치 |

chatbot-poc는 현재 Qwen 3.6로 운영 중이며, Mamba-hybrid 전용 방어선(`async_scheduling: false`, `disable_chunked_mm_input` 금지 등)이 `instances/qwen.yaml`에 반영되어 있습니다. 모델 교체 시 위 플래그 차이를 체크하세요.

> 📌 **2026-08-20 갱신** — 연구계는 Qwen3.8-27B-FP8, 운영계 메인 챗은 Gemma 4 26B-A4B-it입니다. 위 표는 조사 시점(Qwen3.6-35B-A3B) 기준이라 서빙 효율 항목의 "활성 3B" 근거가 27B Dense에는 적용되지 않습니다. 방어 플래그는 아키텍처 클래스가 같아 그대로 유효합니다. 상세는 [qwen3.8.md](../models/qwen3.8.md)를 보세요.

---

## 부록: 원본 조사 문서

- [korean-ability.md](korean-ability.md) — 한국어 능력 전용 비교 (Gemma 4 26B/31B vs Qwen3.8 27B, 2026-08-19)
- [qwen3.8.md](../models/qwen3.8.md) — **현행 연구계 모델**. Qwen3.8-27B 벤치마크·아키텍처·Thinking 제어·서빙
- [qwen3.6.md](../models/qwen3.6.md) — Qwen 3.6 벤치마크·아키텍처·서빙·알려진 이슈 전문
- [qwen3.5.md](../models/qwen3.5.md) — Qwen 3.5 전 라인업 (Qwen 3.6 전신)
- [gemma4.md](../models/gemma4.md) — Gemma 4 전 라인업·Thinking 모드·운영 플래그
- [VLLM_API_GUIDE.md](../../../../llm-serving/VLLM_API_GUIDE.md) — 사용자용 API 가이드 (호출 예시)
- [VLLM_OPS_GUIDE.md](../../../../llm-serving/VLLM_OPS_GUIDE.md) — 현재 운영 가이드 (Qwen 3.6 기반)
