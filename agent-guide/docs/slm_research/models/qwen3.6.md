# Alibaba Qwen 3.6 모델 패밀리 종합 조사

> 조사일: 2026-04-20 | 출시: 2026-04-16
> Qwen3.6-35B-A3B는 Qwen3.5 하이브리드(Gated DeltaNet + Gated Attention) 아키텍처 위에 에이전틱 코딩·프론트엔드 워크플로우·Thinking preservation을 강화한 MoE 개정판

---

## 1. 모델 라인업

### 릴리즈 타임라인

| 날짜 | 릴리즈 |
|------|--------|
| 2026-04-16 | Qwen3.6-35B-A3B, Qwen3.6-35B-A3B-FP8 (동시 공개) |

> 현재 Qwen3.6 네임스페이스에 공개된 모델은 35B-A3B **한 종**뿐. Qwen3.5 전 라인업(0.8B~397B)이 그대로 생존. Qwen3.6은 "Qwen3.5 시리즈의 커뮤니티 피드백을 반영한 첫 오픈 웨이트 변종(first open-weight variant)"으로 공식 포지셔닝됨 (HF 모델 카드).

### 전체 모델 목록

| 모델 | 총 파라미터 | 활성 파라미터 | 아키텍처 | 레이어 | Hidden |
|------|-----------|-------------|---------|--------|--------|
| **Qwen3.6-35B-A3B** | 35B | **3B** | Hybrid MoE (Gated DeltaNet 75% + Gated Attention 25%) | 40 | 2,048 |

### HuggingFace 모델 ID

| 모델 | IT (BF16) | FP8 |
|------|-----------|-----|
| 35B-A3B | `Qwen/Qwen3.6-35B-A3B` | `Qwen/Qwen3.6-35B-A3B-FP8` |

### Qwen3.5 → Qwen3.6 핵심 차이

Qwen3.5와 Qwen3.6은 **거시 아키텍처 파라미터가 완전히 동일**하다 (레이어 40, Hidden 2048, MoE 256 total / 8 routed + 1 shared, 어휘 248,320, 컨텍스트 262K, Gated DeltaNet:Gated Attention = 3:1). 차이는 포스트 트레이닝과 운영 UX 영역.

| 항목 | Qwen3.5-35B-A3B | Qwen3.6-35B-A3B |
|------|:---------------:|:---------------:|
| **아키텍처 파라미터** | 동일 | 동일 |
| **Thinking 기본값** | API 기본 on | **기본 on, 추가로 `preserve_thinking` 옵션 도입** (히스토리 메시지의 reasoning 유지) |
| **`/think`, `/nothink` 소프트 스위치** | 지원(Qwen3 계열) | **미지원** (공식 명시) |
| **SWE-bench Verified** | 70.0 | **73.4** (+3.4p) |
| **SWE-bench Multilingual** | 60.3 | **67.2** (+6.9p) |
| **Terminal-Bench 2.0** | 40.5 | **51.5** (+11.0p) |
| **LiveCodeBench v6** | 74.6 | **80.4** (+5.8p) |
| **HMMT Feb 26** | 78.7 | **83.6** (+4.9p) |
| **에이전틱 코딩 포커스** | 범용 | **프론트엔드 워크플로우 + 레포지토리 수준 추론 강화** |

> 포지셔닝 요약 (HF 모델 카드 원문): "Qwen3.6 prioritizes stability and real-world utility ... the model now handles frontend workflows and repository-level reasoning with greater fluency and precision."

---

## 2. 벤치마크 성능

> Thinking 모드 활성화 기준. 출처: `Qwen/Qwen3.6-35B-A3B-FP8` HuggingFace 모델 카드 (2026-04 시점).
> 좌측 두 컬럼은 Qwen3.5 기준점, 우측이 Qwen3.6.

### 언어 / 지식 / 수학

| 벤치마크 | Qwen3.5-27B | Qwen3.5-35B-A3B | **Qwen3.6-35B-A3B** |
|----------|:-----------:|:---------------:|:-------------------:|
| **MMLU-Pro** | 86.1 | 85.3 | **85.2** |
| **MMLU-Redux** | 93.2 | 93.3 | **93.3** |
| **SuperGPQA** | 65.6 | 63.4 | **64.7** |
| **C-Eval** | 90.5 | 90.2 | **90.0** |
| **GPQA** | 85.5 | 84.2 | **86.0** |
| **AIME 26** | 92.6 | 91.0 | **92.7** |
| **HMMT Feb 25** | 92.0 | 89.0 | **90.7** |
| **HMMT Nov 25** | 89.8 | 89.2 | **89.1** |
| **HMMT Feb 26** | 84.3 | 78.7 | **83.6** |
| **IMOAnswerBench** | 79.9 | 76.8 | **78.9** |

### 에이전틱 코딩 (Qwen3.6의 핵심 개선 영역)

| 벤치마크 | Qwen3.5-27B | Qwen3.5-35B-A3B | **Qwen3.6-35B-A3B** |
|----------|:-----------:|:---------------:|:-------------------:|
| **SWE-bench Verified** | 75.0 | 70.0 | **73.4** |
| **SWE-bench Multilingual** | 69.3 | 60.3 | **67.2** |
| **SWE-bench Pro** | 51.2 | 44.6 | **49.5** |
| **Terminal-Bench 2.0** | 41.6 | 40.5 | **51.5** |
| **LiveCodeBench v6** | 80.7 | 74.6 | **80.4** |

> 주목: 활성 파라미터 3B임에도 Dense 27B와 동급 이상. Terminal-Bench 2.0에서 27B를 10p 상회.

### 비전 / 멀티모달

| 벤치마크 | Qwen3.5-27B | **Qwen3.6-35B-A3B** |
|----------|:-----------:|:-------------------:|
| **MMMU** | 82.3 | **81.7** |
| **MMMU-Pro** | 75.0 | **75.3** |
| **MathVista (mini)** | 87.8 | **86.4** |
| **RealWorldQA** | 83.7 | **85.3** |
| **MMBench EN-DEV-v1.1** | 92.6 | **92.8** |
| **OmniDocBench 1.5** | 88.9 | **89.9** |
| **CharXiv (RQ)** | 79.5 | **78.0** |
| **CC-OCR** | 81.0 | **81.9** |
| **RefCOCO (avg)** | 90.9 | **92.0** |
| **ODInW13** | 41.1 | **50.8** |
| **VideoMME (w sub.)** | 87.0 | **86.6** |
| **VideoMMMU** | 82.3 | **83.7** |
| **MLVU** | 85.9 | **86.2** |

---

## 3. 아키텍처 특징

### 하이브리드 어텐션 (3:1 구조, Qwen3.5 계승)

```
10 x (3 x (Gated DeltaNet → MoE) → 1 x (Gated Attention → MoE))
```

총 40 레이어 = 10 블록 × 4 레이어 (DeltaNet 3 + Attention 1). Qwen3.5-35B-A3B와 **완전 동일**.

### Gated DeltaNet 상세

| 항목 | 값 |
|------|-----|
| Linear Attention V 헤드 | 32 |
| Linear Attention QK 헤드 | 16 |
| Head Dimension | 128 |

### Gated Attention 상세 (GQA)

| 항목 | 값 |
|------|-----|
| Q 헤드 | 16 |
| KV 헤드 | **2** (8:1 GQA 비율) |
| Head Dimension | 256 |
| Rotary Position Embedding Dim | 64 |

### Mixture of Experts

| 항목 | 값 |
|------|-----|
| 총 Experts | **256** |
| 활성 Experts | **8 routed + 1 shared** |
| Expert Intermediate Dim | 512 |

### 멀티모달 네이티브 (Vision encoder 포함)

- vLLM 클래스: `Qwen3_5MoeForConditionalGeneration` → `Qwen3_5ForConditionalGeneration` → `Qwen3VLForConditionalGeneration` (MRO 상속)
- `config.json`에 `video_token_id`, `temporal_patch_size` 포함 → **비디오 공식 지원**
- **오디오는 미지원** (Qwen3.5-Omni 별도 모델이 오디오 담당)
- 비디오 기본 프로파일은 추론 효율을 위해 `video_preprocessor_config.json`의 `size`가 보수적으로 설정됨. 장면 기반 비디오가 필요하면 `longest_edge`를 `469,762,048` (≈224K video tokens)까지 확장 가능 (모델 카드 권장).

### 기타 사양

| 항목 | 값 |
|------|-----|
| 어휘 크기 | 248,320 (padded) |
| 컨텍스트 (네이티브) | **262,144** |
| 컨텍스트 (확장, YaRN) | **1,010,000** |
| 학습 | Pre-training + Post-training w/ Multi-Token Prediction (MTP) |

---

## 4. 주요 기능

### Thinking / Reasoning 모드

- **기본 활성화**. 출력 형식: `<think>\n...(reasoning)...\n</think>\n\n(final answer)`
- 비활성화: API 호출에 `"chat_template_kwargs": {"enable_thinking": False}` 전달
- **`/think`, `/nothink` 소프트 스위치는 공식 미지원** (Qwen3 계열과 분기점)
- **신규: `preserve_thinking`** — 히스토리 메시지의 reasoning context를 유지하여 반복적 에이전트 루프 비용 감소. API: `"chat_template_kwargs": {"preserve_thinking": True}`
- vLLM: `reasoning_parser: qwen3` (Qwen3.5와 동일 파서 재사용)

### 권장 샘플링 파라미터 (모델 카드)

| 모드 | 용도 | temperature | top_p | top_k | min_p | presence_penalty |
|------|------|:----------:|:-----:|:-----:|:-----:|:----------------:|
| Thinking | 일반 | 1.0 | 0.95 | 20 | 0.0 | 1.5 |
| Thinking | 코딩(WebDev) | 0.6 | 0.95 | 20 | 0.0 | 0.0 |
| Instruct | 일반 | 0.7 | 0.8 | 20 | 0.0 | 1.5 |
| Instruct | 추론 | 1.0 | 0.95 | 20 | 0.0 | 1.5 |

권장 max_tokens: 일반 32,768 / 수학·코딩 난제 81,920.

### Tool Calling

- 내장 Function Calling 지원 (Qwen3.6 공식 강화 포인트)
- vLLM: `tool_call_parser: qwen3_coder` (모델 카드의 "With Tool Support" 예시 기준)
- MCP 서버 통합 지원

### 멀티모달

| 모달리티 | 35B-A3B |
|----------|:-------:|
| 텍스트 | O |
| 이미지 | O |
| 비디오 | O |
| 오디오 | X |

### Multi-Token Prediction (MTP)

- 사전 학습·사후 학습에 MTP 적용
- 추론 시 vLLM Speculative Decoding으로 활용 가능 (아래 서빙 섹션 참고)

---

## 5. 서빙 / 배포

### vLLM 공식 레시피 — "Running Qwen3.6" 전문

공식 페이지에는 Qwen3.5와 Qwen3.6을 **같은 페이지**(`docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen3.5.html`)에서 함께 다루며, Qwen3.6 전용 명령은 단 두 개다 — 이 이상은 공식 레시피에 없다.

**기본 서빙**:
```bash
vllm serve Qwen/Qwen3.6-35B-A3B \
  --tensor-parallel-size 8 \
  --max-model-len 262144 \
  --reasoning-parser qwen3
```

**MTP Speculative Decoding**:
```bash
vllm serve Qwen/Qwen3.6-35B-A3B \
  --tensor-parallel-size 8 \
  --max-model-len 262144 \
  --reasoning-parser qwen3 \
  --speculative-config '{"method": "mtp", "num_speculative_tokens": 2}'
```

> vLLM recipes GitHub 원문 기준 Qwen3.6 섹션의 전체 명령은 위 두 개가 전부. `mm_encoder_tp_mode`, `mm_processor_cache_type`, `enable-expert-parallel` 등의 플래그는 Qwen3.6 섹션 자체에는 **명시되지 않음**. (Qwen3.5 섹션의 `Qwen3.5-397B-A17B-FP8` 예시에 등장하는 이들 플래그는 아키텍처가 동일하므로 35B-A3B에도 적용 가능하지만, 이는 공식적 "Qwen3.6 전용" 권장이 아니라 Qwen3.5 레시피의 동일 아키텍처 전이 해석이라는 점을 구분해야 함.)

### 모델 카드에서 추가 권장된 명령 (공식)

HF 모델 카드에는 레시피보다 풍부한 예시가 있다 — 아래는 모두 `Qwen/Qwen3.6-35B-A3B-FP8` 카드 원문.

**Tool 사용 지원**:
```bash
vllm serve Qwen/Qwen3.6-35B-A3B-FP8 \
  --port 8000 \
  --tensor-parallel-size 8 \
  --max-model-len 262144 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder
```

**MTP (모델 카드 쪽, recipes와 method 문자열 차이에 주의)**:
```bash
vllm serve Qwen/Qwen3.6-35B-A3B-FP8 \
  --tensor-parallel-size 8 \
  --max-model-len 262144 \
  --reasoning-parser qwen3 \
  --speculative-config '{"method":"qwen3_next_mtp","num_speculative_tokens":2}'
```

> MTP method 표기 차이: vLLM recipes는 `"method": "mtp"`, 모델 카드는 `"method": "qwen3_next_mtp"`. 두 문자열 모두 동일 MTP 경로를 참조하지만 vLLM 버전에 따라 허용 값이 다를 수 있음. **운영 투입 전 실제 vLLM 0.19.0에서 시도 후 채택 권장.**

**텍스트 전용 (Vision encoder skip)**:
```bash
vllm serve Qwen/Qwen3.6-35B-A3B-FP8 \
  --tensor-parallel-size 8 \
  --max-model-len 262144 \
  --reasoning-parser qwen3 \
  --language-model-only
```

**YaRN으로 1M 컨텍스트 확장**:
```bash
VLLM_ALLOW_LONG_MAX_MODEL_LEN=1 vllm serve Qwen/Qwen3.6-35B-A3B-FP8 \
  --hf-overrides '{"text_config": {"rope_parameters": {"mrope_interleaved": true, "mrope_section": [11, 11, 10], "rope_type": "yarn", "rope_theta": 10000000, "partial_rotary_factor": 0.25, "factor": 4.0, "original_max_position_embeddings": 262144}}}' \
  --max-model-len 1010000
```

### FP8 사전 양자화 체크포인트

| 모델 | FP8 ID | 방식 |
|------|--------|------|
| 35B-A3B | `Qwen/Qwen3.6-35B-A3B-FP8` | Fine-grained FP8 (E4M3), block size 128. "원본 대비 거의 동일(nearly identical)" 성능 (모델 카드) |

### GPU 메모리

FP8 가중치 ~35 GB. chatbot-poc 현행 구성은 **L40S 46GB × 2장, TP=2**. 공식 레시피의 권장 TP=8은 H100/H200 등 대형 장비 프로파일이며, 35B-A3B는 가중치 크기상 TP=2로도 서빙 가능.

| 구성 | 가중치 | KV 캐시 가용 | 권장 `max_model_len` (실측 기준) |
|------|-------|-------------|-------------------------------|
| L40S 46GB × 1 (TP=1) | ~35 GB | 부족 | 비권장 |
| **L40S 46GB × 2 (TP=2)** | ~35 GB / 2 rank | 넉넉 | 현재 `instances/qwen.yaml` 기준 262,144 |

> Mamba-hybrid(`mamba_cache_mode='align'`)가 prefix caching과 함께 자동 활성되면 attention block_size가 ~1056~1568로 확장되어 일반 모델 대비 KV 캐시 계산이 다름. 용량 추정 시 vLLM 기동 로그의 실제 `num_gpu_blocks`를 확인할 것 (아래 7장 이슈 #37121 참조).

### 라이선스

**Apache 2.0** — Qwen3.5와 동일. 상업 사용 제한 없음. HF 토큰 불필요.

---

## 6. 한국어 성능

- **공식 한국어 단독 벤치마크 수치 없음** (모델 카드, 블로그 모두 미수록)
- 모델 카드의 다국어 섹션은 코드/에이전트 계열 위주 (SWE-bench Multilingual 67.2 등)이며, 일반 자연어 다국어(MMMLU, MMLU-ProX 등) 수치는 Qwen3.6 카드에 **미게재**
- 커뮤니티 한국어 벤치마크(LogicKor, KMMLU, Ko-LLM Leaderboard) 결과 현재 미확인 — 출시 후 4일 경과 시점(2026-04-20)이라 추후 갱신 필요
- 아키텍처·어휘(248,320 padded)·학습 레시피가 Qwen3.5와 공유이므로, 한국어 기초 능력은 Qwen3.5-35B-A3B 대비 **코딩/에이전트 강화에 비례한 상승**이 있을 것으로 기대되나 **직접 검증 필요**

---

## 7. 알려진 이슈 / 운영 참고

### 공식 / 커뮤니티 이슈

| 이슈 | 요약 | 대상 하드웨어 | L40S 영향 |
|------|------|--------------|-----------|
| [vllm #40124](https://github.com/vllm-project/vllm/issues/40124) | TurboQuant KV + Hybrid MoE 조합이 Ampere(SM 80-86)에서 실패. 13개 패치로 FP8 커널·kernel selection·online BF16→FP8 캐스팅 등 개선 제안 | **Ampere (A100/A5000 등)** | L40S는 **Ada Lovelace (SM 89)**로, 이슈 본문은 L40S 명시 언급 없음. FP8 W8A8 네이티브 지원 아키텍처라 해당 이슈의 주요 증상(FP8 커널 SM ≥ 89 가정) 영향 밖 |
| [vllm #37121](https://github.com/vllm-project/vllm/issues/37121) | **Hybrid Mamba/Attention 모델의 KV 캐시 메모리 ~7배 과잉추정** — vLLM KV cache profiler가 전 레이어를 동일 취급, GDN 레이어(O(1) state) 수가 Full Attention(O(n)) 레이어와 다름을 미반영 | Qwen3.5 계열 전체 (아키텍처 동일한 Qwen3.6 포함) | KV 용량 자동 추정이 보수적으로 나올 수 있음. 실측 `num_gpu_blocks` 기반 튜닝 필요 |
| [vllm #37602](https://github.com/vllm-project/vllm/issues/37602) | Qwen3.5-122B-A10B-FP8이 동시 이미지 요청 10+에서 EngineCore 크래시. FlashInfer `BatchPrefillWithPagedKVCache` 커널 레벨 assertion 의심. Resolution status: **미해결** | H200 × 4 TP=4 | 아키텍처가 동일한 Qwen3.6-35B-A3B에서도 동시 이미지 요청 시 동일 패턴 재현 가능성. chatbot-poc의 `max_num_seqs: 5` 상한은 이 이슈에 대한 직접적 방어선 |
| [vllm #38643](https://github.com/vllm-project/vllm/issues/38643) | `Qwen3_5ForConditionalGeneration` FLA linear attention 텐서 포맷 불일치로 gibberish 출력 | Qwen3.5 계열 (Qwen3.6 동일 클래스 경로) | vLLM 0.19.0에서 수정 여부 확인 필요 |

### 현재 chatbot-poc 운영 중 확인된 이슈

`/workspace/chatbot-poc/scripts/vllm/bugfix/2026-04-18_vllm_multimodal_encoder_cache.md`에 전말 기록됨. 요약:

| 이슈 | 핵심 원인 | 본 모델과의 관계 |
|------|----------|-----------------|
| `AssertionError: Encoder cache miss` (동시 이미지 요청 중) | vLLM 기본 `async_scheduling=True`가 scheduler 장부와 worker encoder cache 상태 사이 1-step 시차를 만들어 eviction race 유발 | Qwen3.6-35B-A3B-FP8 운영 당시 직접 관측(현재는 27B-FP8, 동일 Mamba-hybrid 계열이라 동일 방어선 적용). `async_scheduling: false` + `max_num_seqs` 상한으로 방어 |
| `AssertionError: Chunked MM input is required` | Mamba-hybrid + prefix caching이 `mamba_cache_mode='align'` 자동 활성 → attention block_size 확장 → `validate_block_size()`가 `disable_chunked_mm_input=True`를 거부 | **Qwen3.6 고유 제약**. 일반 VL 모델용 방어 플래그인 `disable_chunked_mm_input`을 본 모델에 적용 금지 |
| YAML `async_scheduling: false` 무시 | vLLM YAML 파서가 bool `false`를 drop → auto-enable 로직이 `True`로 덮음 | Launcher에서 `--no-async-scheduling` CLI 플래그 직접 주입으로 해결 |

### 현재 `instances/qwen.yaml` 적용 중인 Qwen3.6 전용 권장치 (검증됨)

| 항목 | 값 | 근거 |
|------|-----|------|
| `tensor_parallel_size` | 2 | L40S × 2 기본 운영 프로필 |
| `max_model_len` | 262,144 | 네이티브 컨텍스트 |
| `mm_encoder_tp_mode` | `data` | 아키텍처 호환(`supports_encoder_tp_data=True` MRO 상속). Qwen3.5 레시피 권장 전이 |
| `mm_processor_cache_type` | `shm` | IPC 중복 제거, 멀티모달 동시 요청 최적화 |
| `reasoning_parser` | `qwen3` | 공식 레시피 |
| `tool_call_parser` | `qwen3_xml` | (참고: 모델 카드는 `qwen3_coder` 권장. 현 설정은 범용 XML. 운영 검증 후 재고 가능) |
| `async_scheduling` | `false` | encoder cache race 방어 |
| `max_num_seqs` | 5 | encoder cache 용량 ÷ 이미지 토큰 기준 산정 |
| `max_num_batched_tokens` | `163840` | 이미지 1장 ≈ 16384 encoder tokens → 약 10장 분량 캐시 수용. `scheduler.py:235`에서 encoder_cache_size에 복제됨 |
| `enable_prefix_caching` | `true` | 시스템 프롬프트 재사용 |
| `language_model_only` | `false` | 이미지 기능 유지 (의도된 설정) |

---

## Sources

- [Qwen/Qwen3.6-35B-A3B-FP8 — HuggingFace 모델 카드](https://huggingface.co/Qwen/Qwen3.6-35B-A3B-FP8)
- [Qwen/Qwen3.6-35B-A3B — HuggingFace 모델 카드](https://huggingface.co/Qwen/Qwen3.6-35B-A3B)
- [Qwen3.5 & Qwen3.6 vLLM Recipes (공식 문서)](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen3.5.html)
- [vllm-project/recipes — Qwen3.5.md (GitHub 원문)](https://github.com/vllm-project/recipes/blob/main/Qwen/Qwen3.5.md)
- [Qwen3.6-35B-A3B 공식 블로그](https://qwen.ai/blog?id=qwen3.6-35b-a3b) *(렌더링 동적이라 본문 직접 수집 불가 — HF 모델 카드의 인용문으로 대체)*
- [GitHub vllm-project/vllm Issue #40124 — TurboQuant + Hybrid MoE on Ampere](https://github.com/vllm-project/vllm/issues/40124)
- [GitHub vllm-project/vllm Issue #37121 — Hybrid Mamba/Attention KV cache overestimation](https://github.com/vllm-project/vllm/issues/37121)
- [GitHub vllm-project/vllm Issue #37602 — Qwen3.5-122B-A10B-FP8 concurrent image crash](https://github.com/vllm-project/vllm/issues/37602)
- [GitHub vllm-project/vllm Issue #38643 — Qwen3.5 FLA linear attention format mismatch](https://github.com/vllm-project/vllm/issues/38643)
- [chatbot-poc 운영 이슈 기록 — 2026-04-18 encoder cache race](../../../../llm-serving/vllm/bugfix/2026-04-18_vllm_multimodal_encoder_cache.md)
