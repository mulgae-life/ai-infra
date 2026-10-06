# Alibaba Qwen 3.5 모델 패밀리 종합 조사

> 초회 조사일: 2026-04-03 | 최신 보강: 2026-04-20 | 출시: 2026-02-16 ~ 2026-03-30 (순차 공개)
> Qwen 3.5는 하이브리드 어텐션(Gated DeltaNet + Gated Attention)을 도입한 Qwen의 최신 세대

---

## 1. 모델 라인업

### 릴리즈 타임라인

| 날짜 | 릴리즈 |
|------|--------|
| 2026-02-16 | Qwen3.5-397B-A17B (플래그십 MoE) |
| 2026-02-24 | Qwen3.5-122B-A10B, 35B-A3B, 27B |
| 2026-03-02 | Qwen3.5-9B, 4B, 2B, 0.8B (Small 시리즈) |
| 2026-03-30 | Qwen3.5-Omni / Omni-Plus (전방위 멀티모달) |

### 전체 모델 목록

| 모델 | 총 파라미터 | 활성 파라미터 | 아키텍처 | 레이어 | Hidden |
|------|-----------|-------------|---------|--------|--------|
| **Qwen3.5-0.8B** | 0.8B | 0.8B | Hybrid Dense | 24 | 1,024 |
| **Qwen3.5-2B** | 2B | 2B | Hybrid Dense | 24 | 2,048 |
| **Qwen3.5-4B** | 4B | 4B | Hybrid Dense | 32 | 2,560 |
| **Qwen3.5-9B** | 9B | 9B | Hybrid Dense | 32 | 4,096 |
| **Qwen3.5-27B** | 27B | 27B | Hybrid Dense | 64 | 5,120 |
| **Qwen3.5-35B-A3B** | 35B | **3B** | Hybrid MoE | 40 | 2,048 |
| **Qwen3.5-122B-A10B** | 122B | **10B** | Hybrid MoE | 48 | 3,072 |
| **Qwen3.5-397B-A17B** | 397B | **17B** | Hybrid MoE | 60 | 4,096 |

### HuggingFace 모델 ID

| 모델 | IT | FP8 |
|------|-----|-----|
| 0.8B | `Qwen/Qwen3.5-0.8B` | — |
| 2B | `Qwen/Qwen3.5-2B` | — |
| 4B | `Qwen/Qwen3.5-4B` | — |
| 9B | `Qwen/Qwen3.5-9B` | — |
| 27B | `Qwen/Qwen3.5-27B` | `Qwen/Qwen3.5-27B-FP8` |
| 35B-A3B | `Qwen/Qwen3.5-35B-A3B` | `Qwen/Qwen3.5-35B-A3B-FP8` |
| 122B-A10B | `Qwen/Qwen3.5-122B-A10B` | `Qwen/Qwen3.5-122B-A10B-FP8` |
| 397B-A17B | `Qwen/Qwen3.5-397B-A17B` | `Qwen/Qwen3.5-397B-A17B-FP8` |

Omni: `Qwen/Qwen3.5-Omni`, `Qwen/Qwen3.5-Omni-Plus` *(⚠️ 2026-04-20 기준 HF 컬렉션 미등록 — §7.4 참고)*

### Qwen3 vs Qwen3.5 핵심 차이

| 항목 | Qwen3 | Qwen3.5 |
|------|-------|---------|
| **아키텍처** | 표준 Transformer (Softmax Attention) | **하이브리드** (Gated DeltaNet 75% + Gated Attention 25%) |
| **멀티모달** | 별도 모델 (Qwen3 + Qwen3-VL) | **네이티브 멀티모달** (Early Fusion) |
| **언어 지원** | 119개 | **201개** 언어/방언 |
| **어휘 크기** | ~150K | **248,320** |
| **컨텍스트** | 최대 128K | **262K (네이티브), 1M+ (YaRN)** |
| **디코딩 속도** | 기준 | 256K에서 **19배**, 일반 **8.6배** 빠름 |
| **에이전트** | Terminal Bench 2: 22.5 | **52.5** (2.3배) |
| **효율** | 235B-A22B (22B 활성) | 35B-A3B (3B 활성)가 Qwen3-235B-A22B 능가 |

---

## 2. 벤치마크 성능

> Thinking 모드 활성화 기준. 출처: 각 모델 HuggingFace 카드

### Medium/Large 모델

| 벤치마크 | 27B | 35B-A3B | 122B-A10B | 397B-A17B | GPT-5-mini | Claude 4.5 |
|----------|:---:|:-------:|:---------:|:---------:|:----------:|:----------:|
| **MMLU-Pro** | 86.1 | 85.3 | 86.7 | **87.8** | 83.7 | 89.5 |
| **GPQA Diamond** | 85.5 | 84.2 | 86.6 | **88.4** | 82.8 | 87.0 |
| **LiveCodeBench v6** | 80.7 | 74.6 | 78.9 | **83.6** | 80.5 | 84.8 |
| **SWE-bench Verified** | 72.4 | 69.2 | 72.0 | **76.4** | 72.0 | — |
| **CodeForces ELO** | 1899 | 2028 | 2100 | 2100 | **2160** | — |
| **IFEval** | **95.0** | 91.9 | 93.4 | 92.6 | 93.9 | 90.9 |
| **HMMT Feb 25** | 92.0 | 89.0 | 91.4 | **94.8** | 89.2 | 92.9 |
| **HLE w/ CoT** | 24.3 | 22.4 | 25.3 | **28.7** | 19.4 | 30.8 |

### Small 모델

| 벤치마크 | 0.8B | 4B | 9B | GPT-OSS-120B | Qwen3-30B |
|----------|:----:|:--:|:--:|:------------:|:---------:|
| **MMLU-Pro** | 42.3 | 79.1 | **82.5** | 80.8 | 80.9 |
| **GPQA Diamond** | 11.9 | 76.2 | **81.7** | 80.1 | 73.4 |
| **LiveCodeBench v6** | — | 55.8 | 65.6 | **82.7** | 66.0 |
| **IFEval** | 44.0 | 89.8 | **91.5** | 88.9 | 88.9 |

> 주목: Qwen3.5-9B가 GPT-OSS-120B를 MMLU-Pro, GPQA Diamond에서 능가

### 에이전트/Tool 벤치마크

| 벤치마크 | 9B | 27B | 397B-A17B |
|----------|:--:|:---:|:---------:|
| **BFCL-V4** (Function Calling) | 66.1 | 68.5 | **72.9** |
| **TAU2-Bench** | 79.1 | 79.0 | **86.7** |
| **MCP-Mark** | — | — | **46.1** |
| **BrowseComp** | — | 61.0 | **69.0** |
| **Terminal Bench 2** | — | 41.6 | **52.5** |

---

## 3. 아키텍처 특징

### 하이브리드 어텐션 (3:1 구조)

Qwen3.5의 핵심 혁신 — **3:1 하이브리드 레이어**:

```
N x (3 x (Gated DeltaNet → FFN/MoE) → 1 x (Gated Attention → FFN/MoE))
```

- **75% 레이어**: Gated DeltaNet (Linear Attention) — 시퀀스 길이에 대해 **선형 스케일링**
- **25% 레이어**: Gated Attention (Softmax Attention) — 전통적 어텐션으로 정확도 보완

Gated DeltaNet은 토큰별 어텐션 매트릭스 없이 Running State를 순차 업데이트.
256K 컨텍스트에서 디코딩 **19배 빠름** (vs 표준 Transformer).

### GQA (Grouped Query Attention)

모든 모델의 Gated Attention 레이어에서 GQA 사용:

| 모델 | GA Q/KV 헤드 | DeltaNet V/QK 헤드 |
|------|:----------:|:-----------------:|
| 0.8B~2B | 8/**2** | 16/16 |
| 4B~9B | 16/**4** | 32/16 |
| 27B | 24/**4** | 48/16 |
| MoE 전체 | 16~32/**2** | 32~64/16 |

### 기타 사양

| 항목 | 값 |
|------|-----|
| 어휘 크기 | 248,320 |
| 컨텍스트 (네이티브) | 262,144 (전 모델) |
| 컨텍스트 (확장, YaRN) | 1,010,000+ |
| MoE (397B) | 512 total / 10 active / 1 shared |

---

## 4. 주요 기능

### Thinking / Reasoning 모드

- 4B 이상: Thinking 기본 활성화 (0.8B/2B는 Non-thinking 기본)
- 출력 형식: `<think>\n...(reasoning)...\n</think>\n\n(final answer)`
- 비활성화: `enable_thinking=False`
- 모드별 권장 샘플링:
  - Thinking (일반): temperature=1.0, top_p=0.95, top_k=20, presence_penalty=1.5
  - Thinking (코딩): temperature=0.6, top_p=0.95, top_k=20
  - Non-thinking: temperature=0.7, top_p=0.8, top_k=20
- vLLM: `reasoning_parser: qwen3`

### Tool Calling

- 내장 Function Calling 지원
- vLLM: `tool_call_parser: qwen3_coder` 또는 `qwen3_xml`
- BFCL-V4: 66.1 (9B) ~ 72.9 (397B)

### MCP (Model Context Protocol)

- MCP 통합 지원
- MCP-Mark 벤치마크: 46.1 (397B)
- Qwen-Agent 프레임워크 연동

### 멀티모달 (네이티브)

- Early Fusion으로 텍스트/이미지/비디오 단일 모델 처리
- Vision Encoder 내장 (텍스트 전용: `--language-model-only`)
- Qwen3.5-Omni: 오디오 입출력, 113개 언어 음성 인식

### Multi-Token Prediction (MTP)

- 학습 시 다단계 토큰 예측
- 추론 시 Speculative Decoding으로 활용

### 기타

- 다국어: **201개 언어/방언** (한국어 포함)
- 구조화 출력(JSON) 지원
- System prompt 지원

---

## 5. 서빙 / 배포

### vLLM 지원

전면 지원. [공식 레시피](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen3.5.html) 존재.
공식 검증: **8x H200 GPUs** 및 **8x MI300X/MI355X GPUs** (L40S 미검증).

```bash
# 기본 서빙
vllm serve Qwen/Qwen3.5-27B --reasoning-parser qwen3

# Tool Calling
vllm serve Qwen/Qwen3.5-27B --reasoning-parser qwen3 \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder

# MTP Speculative Decoding
vllm serve Qwen/Qwen3.5-27B --reasoning-parser qwen3 \
  --speculative-config '{"method":"qwen3_next_mtp","num_speculative_tokens":2}'

# 텍스트 전용 (Vision Encoder 제외)
vllm serve Qwen/Qwen3.5-27B --language-model-only
```

#### 공식 권장 구성 (2026-04 기준 업데이트, H200 8장 기준)

> 출처: vLLM Recipes Qwen3.5 공식 페이지. L40S×2 구성은 별도 벤치마크 필요.

**Throughput-Focused (텍스트 전용)**
```bash
vllm serve Qwen/Qwen3.5-397B-A17B-FP8 \
  -dp 8 \
  --enable-expert-parallel \
  --language-model-only \
  --reasoning-parser qwen3 \
  --enable-prefix-caching
```

**Throughput-Focused (멀티모달)** — 신규 플래그 2종
```bash
vllm serve Qwen/Qwen3.5-397B-A17B-FP8 \
  -dp 8 \
  --enable-expert-parallel \
  --mm-encoder-tp-mode data \
  --mm-processor-cache-type shm \
  --reasoning-parser qwen3 \
  --enable-prefix-caching
```

- `--mm-encoder-tp-mode data`: Vision Encoder를 **Data-Parallel** 방식으로 배치. Throughput 향상. 추가 메모리 소비 → `--gpu-memory-utilization` 조정 필요
- `--mm-processor-cache-type shm`: 전처리된 멀티모달 입력을 **공유 메모리(shm)**에 캐시. DP worker 간 전송 효율 개선

**Latency-Focused (MTP-1)**
```bash
vllm serve Qwen/Qwen3.5-397B-A17B-FP8 \
  --tensor-parallel-size 8 \
  --speculative-config '{"method": "mtp", "num_speculative_tokens": 1}' \
  --reasoning-parser qwen3
```
- MTP-1은 고부하(high concurrency) 환경에서는 KV 캐시를 소비하여 throughput 하락
- `num_speculative_tokens`는 1~5 조정 가능. 높을수록 latency 개선, 수용률(acceptance rate) 저하 가능
- AMD GPU용 MTP-1은 **개발 중** (4월 기준)

#### 알려진 플래그/에러 주의사항

- **Prefix Caching (Mamba "align" 모드)**: 공식 문서상 **실험적(experimental)** 표기 유지 중 (4월 기준). 이슈 발견 시 리포트 권장
- **Disable Reasoning**: `--reasoning-parser qwen3 --default-chat-template-kwargs '{"enable_thinking": false}'`로 CLI에서 비활성화 가능
- **`causal_conv1d_update` assertion 에러**: `assert num_cache_lines >= batch` 에러 발생 시 `--max-cudagraph-capture-size`를 512 미만으로 줄일 것 (기본 512). 원인은 Mamba 캐시 크기보다 cudagraph capture 크기가 커서. 참고: [vLLM PR #34571](https://github.com/vllm-project/vllm/pull/34571)
- **Ultra-Long Context (1M+)**: `VLLM_ALLOW_LONG_MAX_MODEL_LEN=1` + `--hf-overrides`로 YaRN 스케일링 활성화 필요. `longest_edge: 469762048`로 224K 시각 컨텍스트까지 확장 가능

### FP8 사전 양자화 체크포인트

공식 FP8 (E4M3, block 128) 체크포인트 제공:

| 모델 | FP8 ID | BF16 VRAM | FP8 VRAM |
|------|--------|-----------|----------|
| 27B | `Qwen/Qwen3.5-27B-FP8` | ~54 GB | **~27 GB** |
| 35B-A3B | `Qwen/Qwen3.5-35B-A3B-FP8` | ~70 GB | ~35 GB |
| 122B-A10B | `Qwen/Qwen3.5-122B-A10B-FP8` | ~244 GB | ~122 GB |
| 397B-A17B | `Qwen/Qwen3.5-397B-A17B-FP8` | ~794 GB | ~397 GB |

> Small 모델(0.8B~9B)은 공식 FP8 미제공 (커뮤니티 GGUF/AWQ 존재)

### GPU 메모리 (L40S 46GB 기준)

| 모델 | 정밀도 | 가중치 | L40S 1장 | 비고 |
|------|--------|--------|:-------:|------|
| 9B | BF16 | ~18 GB | O | KV 캐시 여유 충분 |
| 27B | FP8 | ~27 GB | **O** | 사전 양자화 체크포인트, KV 캐시 ~17 GB |
| 27B | BF16 | ~54 GB | X | 2장 필요 |
| 35B-A3B | FP8 | ~35 GB | O | 활성 3B만 연산, 전체는 메모리에 적재 |

> ⚠️ **2026-04 실사용 보고 주의사항**
> - 커뮤니티 관측: 27B-FP8 런타임 실제 ~31-32 GB (활성 오버헤드 15-20% 포함), KV 캐시 여유는 `--gpu-memory-utilization` 설정에 따라 달라짐 (출처: community blog, 공식 수치 아님)
> - **GPTQ-Int4가 FP8보다 메모리 더 큼** 현상 보고 (vLLM [#37080](https://github.com/vllm-project/vllm/issues/37080), 2026-03-14, Open): L40S에서 Int4 OOM, FP8 성공. `moe_wna16` 양자화 파라미터 이슈로 추정
> - **Hybrid KV 캐시 과대추정 버그** ([#37121](https://github.com/vllm-project/vllm/issues/37121), 2026-03-15, Open): vLLM 프로파일러가 GatedDeltaNet O(1) state를 Attention O(n)처럼 계산. 측정 사례: 프로파일 61,776 토큰 / 7.57 GiB 예약 vs 실제 8,447 토큰 / ~1 GiB 사용 (13.7% 활용률). **L40S처럼 메모리 여유가 적은 환경에서 실 운영 시 예상보다 많은 KV 캐시 배정으로 반대로 초과 확보됨에 주의**

### 라이선스

**Apache 2.0** — 전 모델 공통. 사용 제한 없음.

---

## 6. 한국어 성능

- **공식 한국어 개별 벤치마크 수치 없음**
- 201개 언어 지원에 한국어 포함
- 다국어 벤치마크 (한국어 포함 평균):

| 벤치마크 | 9B | 27B | 397B | 설명 |
|----------|:--:|:---:|:----:|------|
| **MMMLU** | 81.2 | 85.9 | 88.5 | 다국어 MMLU |
| **MMLU-ProX** (29개 언어) | 76.3 | 82.2 | 84.7 | 29개 언어 평균 |
| **NOVA-63** (63개 언어) | 55.9 | 58.1 | 59.1 | 63개 언어 지식 |
| **WMT24++** (55개 언어) | 72.6 | 77.6 | 78.9 | 번역 품질 |

- 어휘 248,320으로 CJK 인코딩 효율 개선
- 중국어 강세 (C-Eval: 90.5) → 유사 CJK 계열 한국어에도 양호 기대

---

---

## 7. 2026-04 업데이트 (보강)

> 기간: 2026-04-03 ~ 2026-04-20. 공식 레시피·GitHub Issues·커뮤니티 실측 기준 추가 확인 사항.

### 7.1 vLLM 버전 이슈 및 릴리즈 현황

| 버전 | 날짜 | Qwen3.5 관련 주요 변경 |
|------|------|----------------------|
| **v0.19.0** | 2026-04-03 | Qwen3.5 GDN 양자화 모델 지원 (#37448), H200 Triton MoE 튜닝 9.9% E2E 개선 (#37340), FP8 weight loading 수정 (#37348), DeepGEMM E8M0 FP8 정확도 수정 (#38083), Triton autotuning (#37338) |
| **v0.19.1** | 2026-04-18 | **Qwen3.5 직접 수정 없음** (주로 Gemma4 버그 수정, Kimi K25 media placeholder) |

> 운영 중인 0.19.0 유지 가능. Qwen3.5 전용 핫픽스는 0.19.1에 포함되지 않음.

### 7.2 알려진 버그/이슈 (Open 상태 위주)

| 이슈 | 번호 | 날짜 | 상태 | 영향 |
|------|------|------|------|------|
| **GatedDeltaNet Marlin MIN_THREAD_N=64 실패** | [#35924](https://github.com/vllm-project/vllm/issues/35924) | 2026-03-03 | Open | 27B는 TP>=1에서, 397B는 TP>=2에서 `in_proj_ba` 분할이 64 미만 → 커널 실패. 제안 수정: `MergedColumnParallelLinear` → `ReplicatedLinear` 2개 |
| **_warmup_prefill_kernels 메모리 누수 ~3.4 GiB** | [#36973](https://github.com/vllm-project/vllm/issues/36973) | 2026-03-13 | Open | `qwen3_next.py`의 워밍업이 Triton 커널 바이너리를 CUDA 컨텍스트에 유지. KV 캐시 66% 감소 사례 (RTX 5090 기준 134K → 44K 토큰). 워크어라운드: pre-fix nightly + pre-warmed Triton cache |
| **Pipeline Parallelism 미지원** | [#36643](https://github.com/vllm-project/vllm/issues/36643) | 2026-03-10 | Open | `SupportsPP` 미구현. `NotImplementedError`. **TP 사용 필수** |
| **Hybrid Mamba KV 캐시 7배 과대추정** | [#37121](https://github.com/vllm-project/vllm/issues/37121) | 2026-03-15 | Open | 4B/9B/32B/MoE 전 계열 영향. 실제 13.7% 활용에 그침 |
| **4B Qwen3_5ForCausalLM 미등록** | [#36275](https://github.com/vllm-project/vllm/issues/36275) | 2026-03-06 | Open | 텍스트 전용 체크포인트 weight 접두사 `model.layers.*` vs vLLM 기대값 `language_model.model.layers.*` 불일치 |
| **FA3 backend 8.5x 성능 회귀 (Hopper)** | [#39323](https://github.com/vllm-project/vllm/issues/39323) | 2026-04-08 | Open (nightly에서는 수정됨) | 35B-A3B-FP8, H100/H200. 0.19.0에서 문제. **FLASHINFER 백엔드 사용 권장**. throughput 336.07s → 39.37s 개선 확인 |
| **122B-A10B-FP8 동시 이미지 요청 크래시** | [#37602](https://github.com/vllm-project/vllm/issues/37602) | 2026-03-19 | Open | EngineCore exit code 0. 텍스트 전용은 안정. FlashInfer batch prefill + GDN 추정 |
| **thinking_token_budget → content 오염** | [#39697](https://github.com/vllm-project/vllm/issues/39697) | 2026-04-13 | Open | `reasoning_end_str`이 응답 content에 누출. 27B-GPTQ-Int4 재현. vLLM 0.19.0 |
| **9B-AWQ ROCm JSON schema 무한 `!` 생성** | [#39348](https://github.com/vllm-project/vllm/issues/39348) | 2026-04-08 | Open | vLLM 0.19.0 + ROCm에서 JSON 제약 출력 중 무한 반복 |
| **27B-FP8 첫 요청 TTFT ~43s** | [#39163](https://github.com/vllm-project/vllm/issues/39163) | 2026-04-07 | **Closed (PR #39169)** | 워크어라운드: 기동 직후 더미 워밍업 요청 1회 (43s 소요, 이후 정상화) |
| **Qwen3.5-27B DeltaNet dtype mismatch (torch.compile)** | [#35238](https://github.com/vllm-project/vllm/issues/35238) | 2026-02-24 | **Closed (PR #35256)** | `--enforce-eager` 시 ~23 tps vs compile ~53 tps. 이미 수정됨 |
| **122B NVFP4 MTP 0% 수용률** | [#36331](https://github.com/vllm-project/vllm/issues/36331) | 2026-03-07 | Closed | 122B NVFP4는 0% acceptance. 35B-FP8은 정상 동작. CUTLASS/FlashInfer autotune 실패 추정 |
| **MTP 활성화 시 prefix cache hit 감소 (92% → 71%)** | [#38182](https://github.com/vllm-project/vllm/issues/38182) | 2026-03-26 | Open | 35B-A3B 기준. MTP+prefix caching 조합 성능 trade-off |

### 7.3 MTP (Speculative Decoding) 실측 성능

> 2026-04-03 기존 문서는 "MTP 언급만" 상태였음. 아래는 이후 확보된 **실측 벤치마크**.

**Google Cloud + B200 실측 (Qwen3.5-27B, vLLM):**
- MTP-1 활성화 시 각 decode step당 ~1.9 토큰 생성 (acceptance rate **~90%**)
- 단일 노드 최대 throughput: **96,023 tokens/s**
- 12 노드 × 96 B200 GPU: **1,103,941 tokens/s** (96.5% 스케일링 효율)
- TPOT 중앙값: **~46 ms**
- TTFT: 5,580~8,065 ms (노드 수에 따라 변동)
- 핵심 플래그: `--data-parallel-size=8`, `--kv-cache-dtype=fp8_e4m3`, `--gpu-memory-utilization=0.92`, `--max-model-len=2560`
- MTP가 없으면 B200이 너무 한가함 (27B 모델이 작아서): GPU 활용률 4.4% FLOPS / 10.9% 메모리 대역폭

**주의:** MTP 수용률은 **모델/양자화 조합에 따라 편차가 큼**:
- ✅ 35B-FP8: 정상 작동 확인
- ❌ 122B-NVFP4: 0% 수용 (이슈 #36331, closed)
- ⚠️ MTP-1 + prefix caching 동시 사용 시 cache hit rate 저하 (이슈 #38182, open)

### 7.4 Qwen3.5-Omni 정정

> 기존 문서는 "Omni/Omni-Plus" HuggingFace ID를 기재했으나, **4월 시점 검증 결과 오픈웨이트 미공개 확인**.

- **2026-04-20 기준 Qwen3.5 HuggingFace 컬렉션에 Omni 변종 없음** ([컬렉션](https://huggingface.co/collections/Qwen/qwen35) 직접 확인)
- 2026-03-30 발표된 Qwen3.5-Omni / Plus / Flash / Light는 **DashScope API 전용**으로 접근 (open-weight 상태 공식 미확정)
- 다만 전작 Qwen3-Omni는 Apache 2.0 오픈웨이트로 공개된 바 있음
- **Qwen3.5-Omni 자체는 아직 vLLM 직접 서빙 대상 아님.** 오픈웨이트 공개 후 vLLM 0.17.0+ 요구 예상 (오디오 캐시 핸들링 수정 포함)
- 발표된 스펙:
  - 256K 컨텍스트 (10시간 오디오 / 400초 720p 비디오 지원)
  - 음성 인식 113개 언어 / 음성 생성 36개 언어 (전작 대비 확장)
  - 벤치마크 공식 수치는 "MMAU / RUL-MuchoMusic"가 Gemini 3.1 Pro 대비 우위라고 언급되나, 정확 숫자는 보도/블로그 인용이 엇갈려 원문 확인 필요 (공식 Qwen 블로그 원문 확보 실패)

### 7.5 Hybrid Attention (Gated DeltaNet) vLLM 구현 상태

- **기본 동작**: vLLM 0.19.0에서 전면 지원. GDN은 `MergedColumnParallelLinear` 기반
- **알려진 한계** (2026-04 시점):
  1. Pipeline Parallelism 미지원 → TP만 가능
  2. Marlin 커널 MIN_THREAD_N 제약으로 **27B 모델은 사실상 TP=1 고정** (TP≥1부터 실패 케이스 보고)
  3. GDN 프로파일러의 O(1) state를 O(n)으로 잘못 추정하는 KV 계산 버그 (Open)
  4. 워밍업 시 ~3.4 GiB 누수 (작은 GPU에서 KV 캐시 심각히 축소)
  5. Prefix caching (Mamba "align" 모드)은 공식 **실험적** 표기 유지
  6. `max-num-batched-tokens`는 커뮤니티 보고 기준 **2096** 이상 권장 (GDN/Mamba 캐시 정렬 제약)
- **로드맵**: `blog.vllm.ai`의 Qwen3-Next 글에 "자동 prefix caching + P/D disaggregation 추가 예정", GatedDeltaNet 커널 최적화 지속 예고

### 7.6 L40S 46GB × 2 (TP=2) 운영 가이드 (보강)

> 현재 운영 장비 기준. 공식 레시피는 H200/MI300X만 검증.

| 권장 모델 | 상태 | 비고 |
|-----------|:----:|------|
| **9B (BF16)** | ✅ 안전 | 단일 장비 가능, 2장이면 여유 충분 |
| **27B-FP8** | ⚠️ 주의 | TP=2 사용 시 [#35924](https://github.com/vllm-project/vllm/issues/35924) 이슈 재현 가능성 있음 (27B는 TP≥1부터 보고). 현재 운영은 Qwen3.6-27B-FP8(Mamba-hybrid)이며, 본 #35924는 Qwen3.5-27B(Transformer) 보고 건이라 아키텍처가 달라 직접 영향 가능성은 낮음(실기동 확인 권장) |
| **35B-A3B-FP8** | ⚠️ 주의 | 실제 ~35 GB 가중치 + KV 캐시 → 2장 분산 시 MoE + Expert Parallel 필요. `--max-model-len` 축소 권장 |
| **122B-A10B-FP8 이상** | ❌ | L40S×2로는 불가 |

**적용 가능한 신규 플래그 (TP=2 환경):**
- `--mm-processor-cache-type shm`: 멀티모달 시 유효 (이미지 기능 유지 시)
- `--mm-encoder-tp-mode data`: TP=2 환경에서는 이득 제한적 (DP=1 환경이 주 대상)
- `--speculative-config '{"method":"mtp","num_speculative_tokens":1}'`: latency 개선. FLASHINFER 백엔드 병용 권장 (FA3 회귀 이슈 회피)

### 7.7 한국어 벤치마크 (추가 확인)

> 공식 한국어 단독 벤치마크 여전히 **미공개**. 다국어 벤치마크만 존재.

35B-A3B-FP8 모델 카드 기준 (한국어 포함 다국어 평균, 27B 수치와 상이 — 모델 카드별 재확인):

| 벤치마크 | 35B-A3B-FP8 | 설명 |
|----------|:-----------:|------|
| **MMMLU** | 85.2 | 다국어 MMLU |
| **MMLU-ProX** (29개 언어) | 81.0 | 29개 언어 평균 |
| **NOVA-63** (63개 언어) | 57.1 | 63개 언어 지식 |
| **WMT24++** (55개 언어) | 76.3 | XCOMET-XXL 번역 |
| **MAXIFE** | 86.6 | 영어 + 23개 다국어 |

- KMMLU / LogicKor / HAERAE-Bench / KoBEST 등 **한국어 전용 벤치마크에 대한 공식 Qwen3.5 수치는 2026-04-20 기준 여전히 미공개**
- 커뮤니티 단독 평가도 체계적 리더보드 보고 미확인 (원문 확인 필요)

---

## Sources

### 기존
- [Qwen3.5 공식 블로그](https://qwen.ai/blog?id=qwen3.5)
- [Qwen3.5-397B-A17B HuggingFace](https://huggingface.co/Qwen/Qwen3.5-397B-A17B)
- [Qwen3.5-27B HuggingFace](https://huggingface.co/Qwen/Qwen3.5-27B)
- [Qwen3.5-27B-FP8 HuggingFace](https://huggingface.co/Qwen/Qwen3.5-27B-FP8)
- [Qwen3.5 vLLM Recipes](https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen3.5.html)
- [Qwen3.5 아키텍처 분석 (HuggingFace Blog)](https://huggingface.co/blog/mlabonne/qwen35)
- [Gemma 4 vs Qwen 3.5 비교 (ai.rs)](https://ai.rs/ai-developer/gemma-4-vs-qwen-3-5-vs-llama-4-compared)

### 2026-04 보강 추가
- [vLLM Recipes Qwen3.5 최신본 (raw)](https://raw.githubusercontent.com/vllm-project/recipes/main/Qwen/Qwen3.5.md)
- [Qwen3.5 HuggingFace Collection](https://huggingface.co/collections/Qwen/qwen35)
- [Qwen3.5-35B-A3B-FP8 HuggingFace](https://huggingface.co/Qwen/Qwen3.5-35B-A3B-FP8)
- [vLLM Releases (v0.19.0, v0.19.1)](https://github.com/vllm-project/vllm/releases)
- [Issue #35924 — GatedDeltaNet Marlin MIN_THREAD_N=64 at TP>=4](https://github.com/vllm-project/vllm/issues/35924)
- [Issue #35238 — Qwen3.5-27B DeltaNet dtype mismatch (Closed)](https://github.com/vllm-project/vllm/issues/35238)
- [Issue #36275 — 4B Qwen3_5ForCausalLM incompatibility](https://github.com/vllm-project/vllm/issues/36275)
- [Issue #36331 — Qwen 3.5 122B NVFP4 MTP 0% acceptance rate (Closed)](https://github.com/vllm-project/vllm/issues/36331)
- [Issue #36643 — Pipeline parallelism not supported](https://github.com/vllm-project/vllm/issues/36643)
- [Issue #36973 — _warmup_prefill_kernels 3.4 GiB leak](https://github.com/vllm-project/vllm/issues/36973)
- [Issue #37080 — Int4 memory higher than FP8 (L40S)](https://github.com/vllm-project/vllm/issues/37080)
- [Issue #37121 — KV cache ~7x overestimation (Hybrid Mamba)](https://github.com/vllm-project/vllm/issues/37121)
- [Issue #37602 — 122B-A10B-FP8 concurrent image request crash](https://github.com/vllm-project/vllm/issues/37602)
- [Issue #38182 — MTP reduces prefix cache hit rate](https://github.com/vllm-project/vllm/issues/38182)
- [Issue #39163 — 27B-FP8 first request slow startup (Closed, PR #39169)](https://github.com/vllm-project/vllm/issues/39163)
- [Issue #39323 — 35B-A3B-FP8 8.5x FA3 regression on Hopper](https://github.com/vllm-project/vllm/issues/39323)
- [Issue #39348 — 9B-AWQ ROCm JSON schema infinite `!` loop](https://github.com/vllm-project/vllm/issues/39348)
- [Issue #39697 — thinking_token_budget leak into content](https://github.com/vllm-project/vllm/issues/39697)
- [Google Cloud: 1M Tokens/s Qwen 3.5-27B on B200 with vLLM](https://medium.com/google-cloud/1-million-tokens-per-second-qwen-3-5-27b-on-gke-with-b200-gpus-161da5c1b592)
- [WaveSpeedAI: What Is Qwen3.5-Omni (Capabilities)](https://wavespeed.ai/blog/posts/what-is-qwen3-5-omni/)
- [vLLM PR #34571 — causal_conv1d_update assertion fix reference](https://github.com/vllm-project/vllm/pull/34571)
