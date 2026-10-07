# Google Gemma 4 모델 패밀리 종합 조사

> 초안 조사일: 2026-04-03 | 출시일: 2026-04-02
> 업데이트일: 2026-04-20 (vLLM 0.19.1 기준 보강, 7장 참조)
> Gemma 4는 Gemini 3과 동일한 연구/기술 기반으로 구축된 Google의 최신 오픈 모델 패밀리

---

## 1. 모델 라인업

| 모델 | 아키텍처 | 총 파라미터 | 활성 파라미터 | 레이어 | 컨텍스트 | 멀티모달 |
|------|----------|-----------|-------------|--------|---------|---------|
| **Gemma 4 E2B** | Dense + PLE | 5.1B | 2.3B (effective) | 35 | 128K | 텍스트, 이미지, 오디오 |
| **Gemma 4 E4B** | Dense + PLE | 8B | 4.5B (effective) | 42 | 128K | 텍스트, 이미지, 오디오 |
| **Gemma 4 26B-A4B** | MoE | 25.2B | 3.8B | 30 | 256K | 텍스트, 이미지 |
| **Gemma 4 31B** | Dense | 30.7B | 30.7B | 60 | 256K | 텍스트, 이미지 |

- **E2B / E4B**: "Effective 2B / 4B" — Per-Layer Embeddings(PLE) 기술로 모바일/엣지 최적화
- **26B-A4B**: Mixture-of-Experts — 128개 전문가 중 8개 활성 + 1개 공유 전문가
- **31B**: 전통적 Dense 아키텍처, 플래그십 모델

### HuggingFace 모델 ID

| 모델 | Base | Instruction-Tuned |
|------|------|-------------------|
| E2B | `google/gemma-4-E2B` | `google/gemma-4-E2B-it` |
| E4B | `google/gemma-4-E4B` | `google/gemma-4-E4B-it` |
| 26B-A4B | `google/gemma-4-26B-A4B` | `google/gemma-4-26B-A4B-it` |
| 31B | `google/gemma-4-31B` | `google/gemma-4-31B-it` |

양자화: `nvidia/Gemma-4-31B-IT-NVFP4`, `unsloth/gemma-4-31B-it-GGUF` 등

---

## 2. 벤치마크 성능

> IT 모델, Thinking 모드 활성화 기준. 출처: Google 공식 모델 카드

### 추론(Reasoning) 및 지식

| 벤치마크 | 31B | 26B-A4B | E4B | E2B | Gemma 3 27B |
|----------|:---:|:-------:|:---:|:---:|:-----------:|
| **MMLU Pro** | 85.2 | 82.6 | 69.4 | 60.0 | 67.6 |
| **GPQA Diamond** | 84.3 | 82.3 | 58.6 | 43.4 | 42.4 |
| **AIME 2026** (no tools) | 89.2 | 88.3 | 42.5 | 37.5 | 20.8 |
| **BigBench Extra Hard** | 74.4 | 64.8 | 33.1 | 21.9 | 19.3 |
| **MMMLU** (다국어) | 88.4 | 86.3 | 76.6 | 67.4 | 70.7 |
| **Tau2-Bench** (에이전트) | 76.9 | 68.2 | 42.2 | 24.5 | 16.2 |

### 코딩

| 벤치마크 | 31B | 26B-A4B | E4B | E2B | Gemma 3 27B |
|----------|:---:|:-------:|:---:|:---:|:-----------:|
| **LiveCodeBench v6** | 80.0 | 77.1 | 52.0 | 44.0 | 29.1 |
| **Codeforces ELO** | 2150 | 1718 | 940 | 633 | 110 |

### 비전(Vision) / 멀티모달

| 벤치마크 | 31B | 26B-A4B | E4B | E2B | Gemma 3 27B |
|----------|:---:|:-------:|:---:|:---:|:-----------:|
| **MMMU Pro** | 76.9 | 73.8 | 52.6 | 44.2 | 49.7 |
| **MATH-Vision** | 85.6 | 82.4 | 59.5 | 52.4 | 46.0 |

### Gemma 3 → 4 핵심 향상

| 항목 | Gemma 3 27B | Gemma 4 31B | 향상폭 |
|------|:-----------:|:-----------:|:------:|
| MMLU Pro | 67.6 | 85.2 | **+17.6p** |
| GPQA Diamond | 42.4 | 84.3 | **+41.9p** |
| AIME (수학) | 20.8 | 89.2 | **+68.4p** |
| LiveCodeBench v6 | 29.1 | 80.0 | **+50.9p** |
| Codeforces ELO | 110 | 2150 | **+2040** |

핵심 동인: **Configurable Thinking 모드** 도입 + 아키텍처 개선

---

## 3. 아키텍처 특징

### Hybrid Attention (슬라이딩 윈도우 + 글로벌)

- 로컬 **슬라이딩 윈도우 어텐션**과 **글로벌 풀 어텐션**을 교대 배치
- 슬라이딩 윈도우 크기: E2B/E4B 512, 26B-A4B/31B **1024**
- 마지막 레이어는 항상 글로벌 어텐션

### Proportional RoPE (p-RoPE)

- 슬라이딩 레이어: 표준 RoPE
- 글로벌 레이어: p-RoPE + 통합 Key/Value (롱 컨텍스트 메모리 최적화)

### Per-Layer Embeddings (PLE) — E2B/E4B 전용

- 각 레이어마다 토큰별 전용 벡터 주입
- 모바일 프로세서 최적화 파라미터 효율 기법

### 기타 사양

| 항목 | 값 |
|------|-----|
| 어휘 크기 | 262,144 (262K) |
| 컨텍스트 (소형) | 128K |
| 컨텍스트 (중형) | 256K |
| MoE (26B-A4B) | 128 total / 8 active / 1 shared |

---

## 4. 주요 기능

### Thinking / Reasoning 모드

- `enable_thinking: true` 또는 시스템 프롬프트에 `<|think|>` 토큰으로 활성화
- 출력 형식: `<|channel>thought\n[내부 추론]\n<channel|>[최종 답변]`
- vLLM: `reasoning_parser: gemma4`로 `reasoning_content` 필드 자동 분리

### Tool Calling

- 네이티브 함수 호출 지원
- 출력 형식: `<|tool_call>call:func{param:<|"|>value<|"|>}<tool_call|>`
- vLLM: `tool_call_parser: gemma4`

### 멀티모달 지원

| 모달리티 | E2B | E4B | 26B-A4B | 31B |
|----------|:---:|:---:|:-------:|:---:|
| 텍스트 | O | O | O | O |
| 이미지 | O | O | O | O |
| 비디오 | O | O | O | O |
| 오디오 | O | O | X | X |

- 이미지: 가변 해상도/종횡비, 토큰 예산 70~1120
- 비디오: 최대 60초 (1fps 프레임 시퀀스)
- 오디오: 최대 30초 (E2B/E4B 전용)

### 기타

- 다국어: **140개+ 언어** 네이티브 학습
- System prompt 네이티브 지원
- 구조화 출력(JSON) 지원

---

## 5. 서빙 / 배포

### vLLM 지원

- **Day-1 지원**, vLLM 0.19.0+
- transformers >= 5.5.0 필요

```bash
# 31B FP8 온라인 양자화
vllm serve google/gemma-4-31B-it \
  --quantization fp8 \
  --max-model-len 12288 \
  --gpu-memory-utilization 0.95

# NVFP4
vllm serve nvidia/Gemma-4-31B-IT-NVFP4 \
  --quantization modelopt
```

### 양자화 옵션

| 방식 | 설명 | 성능 손실 |
|------|------|----------|
| **FP8 (온라인)** | vLLM `quantization: fp8`로 동적 양자화 | 미미 |
| **NVFP4** | NVIDIA 4-bit, `quantization: modelopt` | GPQA -0.25%, MMLU Pro -0.31% |
| **GGUF** | llama.cpp용 (Q4_K_M 등) | 양자화 수준에 따라 다름 |

### GPU 메모리 (31B)

| 정밀도 | 가중치 | 비고 |
|--------|--------|------|
| BF16 | ~62 GB | 단일 GPU 불가 |
| FP8 (온라인) | ~29 GB | L40S 46GB 1장 가능 (vLLM 0.19.0 레이어별 변환) |
| NVFP4 | ~15 GB | Blackwell/Hopper 최적화 |

### 라이선스

**Apache 2.0** — 상업적/비상업적 완전 자유. HF 토큰 불필요.

---

## 6. 한국어 성능

- **공식 한국어 벤치마크 수치 없음** (출시 직후)
- MMMLU(다국어 MMLU): 31B 88.4% (다국어 평균, 한국어 개별 미공개)
- 140개+ 언어 네이티브 학습에 한국어 포함
- 커뮤니티 한국어 벤치마크(KoBEST, KLUE, LogicKor) 결과 추후 확인 필요
- **2026-04-20 업데이트**: 출시 후 약 2.5주 경과 시점에도 공식 Google/DeepMind 모델 카드 및 HuggingFace `google/gemma-4-*` 모델 카드에서 한국어 개별 벤치마크 수치 미공개 상태. Open Ko-LLM Leaderboard 등 커뮤니티 리더보드에도 공식 제출 미확인 (추후 검증 필요)

---

## 7. 2026-04 업데이트 (출시 후 ~2.5주)

### 7.1 vLLM 0.19.1 패치 릴리즈 (2026-04-18)

vLLM 0.19.0 Day-1 지원 이후 약 2주 만에 Gemma 4 안정화 패치 릴리즈가 배포됐습니다. 0.19.1은 transformers v5.5.4 의존성 업그레이드와 Gemma 4 관련 버그픽스가 주요 내용입니다.

**핵심 버그픽스**

| PR | 내용 |
|----|------|
| [#38992](https://github.com/vllm-project/vllm/pull/38992) | 스트리밍 tool call 시 partial delimiter(`<`, `|`, `>`)가 JSON에 섞여 invalid JSON 생성되던 문제 수정 |
| [#38909](https://github.com/vllm-project/vllm/pull/38909) | 스트리밍 tool call 중 HTML 태그 프리픽스 중복(`<<html`, `<<meta`) 생성 문제 수정 |
| [#39114](https://github.com/vllm-project/vllm/pull/39114) | 스트리밍 중 boolean/number 값이 split될 때 tool call 손상 수정 |
| [#38844](https://github.com/vllm-project/vllm/pull/38844) | `Gemma4ForCausalLM` LoRA 어댑터 로드 지원 |
| [#39027](https://github.com/vllm-project/vllm/pull/39027) | reasoning parser의 `adjust_request` 보정 |
| [#39045](https://github.com/vllm-project/vllm/pull/39045) | Gemma 4 MoE 양자화(quantized MoE) 지원 |
| [#39450](https://github.com/vllm-project/vllm/pull/39450) | Gemma 4 Eagle3 (speculative decoding) 지원 |
| [#39679](https://github.com/vllm-project/vllm/pull/39679) | tool parser가 bare `null`을 문자열 `"null"`로 변환하던 문제 수정 |
| [#39842](https://github.com/vllm-project/vllm/pull/39842) | BF16(PT) 모델의 토큰 반복 현상을 동적 BOS 주입으로 완화 |

> chatbot-poc 운영 시 0.19.0 사용 중이면 0.19.1로 업그레이드 권장. Tool calling + 스트리밍 조합에서 다수의 JSON 깨짐 이슈가 해결됐습니다.

### 7.2 미해결 이슈 (Open, 2026-04-20 기준)

| Issue | 영향 |
|-------|------|
| [#38887](https://github.com/vllm-project/vllm/issues/38887) | Gemma 4 E4B의 이종 head_dim(sliding 256 / global 512)으로 FlashAttention 불가 → TRITON_ATTN 강제 폴백 → RTX 4090 기준 약 9 tok/s (Llama 3.2 3B 대비 10배 이상 저하). 관련 PR [#38891](https://github.com/vllm-project/vllm/pull/38891)이 sliding-window 레이어만 FlashAttention 선택 사용하도록 완화하지만 2026-04-20 기준 미병합 |
| [#39043](https://github.com/vllm-project/vllm/issues/39043) | tool calling 시 thinking 활성화: reasoning 태그가 chat으로 leak / thinking 비활성화: tool call이 chat으로 leak |
| [#39392](https://github.com/vllm-project/vllm/issues/39392) | `--tool-call-parser gemma4` 동시 요청 처리 시 일부 응답이 `<pad>` 토큰으로 채워짐 (`Gemma4ToolParser`의 thread-safety 부족 추정). 워크어라운드: 전역 락으로 요청 직렬화 |
| [#38999](https://github.com/vllm-project/vllm/issues/38999) | 26B-A4B MoE에 `--data-parallel-size > 1` 설정 시 `cuda_communicator` 내 AssertionError. 워크어라운드: 인스턴스 분리 + 외부 로드밸런서 |
| [#39000](https://github.com/vllm-project/vllm/issues/39000) | 26B-A4B MoE의 MXFP4 런타임 양자화가 2D/3D tensor shape 불일치로 가중치 로드 중 크래시. 워크어라운드: `--quantization fp8` 대체 |
| [#38918](https://github.com/vllm-project/vllm/issues/38918) | Turing GPU(SM 7.5, 예: RTX 2080 Ti)에서 head_dim=512가 SM당 shared memory 64KB 한계 초과 → 모든 attention backend 실패 (FLASH_ATTN은 SM 8.0+ 필요, TRITON_ATTN은 공유 메모리 초과). 현재 우회 불가 |
| [#39216](https://github.com/vllm-project/vllm/issues/39216) | PyPI의 vLLM 0.19.0이 `transformers<5` 핀 → Gemma 4는 `transformers>=5.5.0` 요구 → 표준 설치 경로로는 불가. 0.19.1에서 transformers v5.5.4로 해소됨 |
| [#39468](https://github.com/vllm-project/vllm/issues/39468) | 0.19.0 tool call 응답에 `<|"|>` stray 토큰이 섞여 나오는 포맷 문제. 관련 PR [#39484](https://github.com/vllm-project/vllm/pull/39484) 진행 중 |

> 운영 권고: 0.19.0 + tool calling + 스트리밍 조합은 위 이슈들로 불안정. 0.19.1 업그레이드가 1차 조치이며, E4B의 TRITON_ATTN 성능 저하는 0.19.1에서도 미해결.

### 7.3 vLLM 공식 Recipes 플래그 (권장 서빙 구성)

vLLM 공식 [Gemma 4 Recipes](https://docs.vllm.ai/projects/recipes/en/latest/Google/Gemma4.html)에 정리된 권장 플래그:

| 플래그 | 용도 |
|--------|------|
| `--reasoning-parser gemma4` | Thinking/Reasoning 모드 출력에서 `reasoning_content` 자동 분리 |
| `--tool-call-parser gemma4` | Tool call 형식 파싱 |
| `--enable-auto-tool-choice` | 모델 출력에서 tool call 자동 감지 |
| `--chat-template examples/tool_chat_template_gemma4.jinja` | reasoning/tool 전용 템플릿 |
| `--mm-processor-kwargs '{"max_soft_tokens": N}'` | 비전 토큰 예산 (기본 280, 범위 70~1120) |
| `--limit-mm-per-prompt image=N,audio=M` | 프롬프트당 멀티모달 입력 상한 |

**텍스트 전용 워크로드 최적화** (RedHatAI NVFP4 모델 카드 권장):
- `--limit-mm-per-prompt image=0`: 이미지 처리 비활성화로 KV 캐시 확보
- `--gpu-memory-utilization 0.90`: KV 캐시 최대화

### 7.4 비전 처리 세부사항 (transformers 공식 문서)

Gemma 4 비전은 고정 토큰 예산 방식으로 가변 해상도를 지원합니다.

| Soft tokens | Patches (pooling 전) | 대응 픽셀 면적 |
|:-----------:|:--------------------:|:--------------:|
| 70 | 630 | ~161K |
| 140 | 1,260 | ~323K |
| **280 (기본)** | **2,520** | **~645K** |
| 560 | 5,040 | ~1.3M |
| 1,120 | 10,080 | ~2.6M |

- 이미지 H/W는 **48의 배수** (patch size 16 × pooling kernel 3)
- ImageNet mean/std 정규화 미적용 — 모델 내부 patch embedding이 `[-1, 1]` 스케일링 담당

### 7.5 멀티모달 관련 vLLM 플래그 (Gemma 4 적용성)

vLLM 0.19.0 소스 직접 검증(`gemma4_mm.py`, `gemma4.py`, `vllm/config/model.py`, `vllm/multimodal/registry.py`) 기반 Gemma 4 실제 적용성:

| 플래그 | 설명 | Gemma 4 실제 동작 |
|--------|------|------------------|
| `--mm-encoder-tp-mode data` | 배치 입력을 TP rank로 분산(가중치 복제). vision encoder 통신 오버헤드 제거 | ❌ **Gemma 4 미지원.** `gemma4_mm.py`에 `supports_encoder_tp_data=True` 플래그가 없어 기본값 `False` (`interfaces.py:112`). `vllm/config/model.py:617-625`에서 설정 시 **경고 로그 후 자동으로 "weights"로 폴백**. 에러 없음. 현재 DP 지원 모델은 Qwen2-VL/Qwen2.5-VL/Qwen3-VL/GLM4.1V/InternVL/MiniCPM-V/Mllama4/Kimi-VL/Kimi-K2.5/Hunyuan-Vision/Dots-OCR/Step3-VL/OpenCUA/Isaac/Eagle2.5-VL (전 16종) |
| `--mm-processor-cache-type {lru,shm}` | 기본 LRU 캐시 vs shared memory. SHM은 캐시 hit 시 prefill 처리량 69.9%↑, TTFT 40.5%↓ (일반 멀티모달 기준) | ✅ **모델 독립 글로벌 파라미터.** `vllm/multimodal/registry.py:276-328`에서 모델 분기 없이 처리 → Gemma 4에서도 동일 효과. 다중 프로세스 서빙 시 유리 |
| `--mm-processor-cache-gb N` | 프로세서 캐시 크기 (기본 4GiB) | ✅ 모델 독립. 이미지 반복 요청이 많은 챗봇 워크로드에 유효 |
| `--mm-processor-kwargs '{"max_soft_tokens": N}'` | Gemma 4 전용 비전 토큰 예산 | ✅ **Gemma 4 전용.** `Gemma4MultiModalProcessor._call_hf_processor`(gemma4_mm.py:474-485)가 {70,140,280,560,1120} validator를 수행하며 범위 외는 `sys.exit(1)`. 다른 모델에 전달 시 `get_allowed_kwarg_only_overrides`(func_utils.py:132-161)가 WARNING + 드롭 |
| `--limit-mm-per-prompt image=N` | 프롬프트당 멀티모달 입력 상한 | ✅ 모델 독립 공용 파라미터. 전 VL 모델 동일 동작 |

> 주의: 캐시 효과 수치(69.9%↑, 40.5%↓)는 일반 멀티모달 기준 vLLM 공식 문서 값이며, Gemma 4 특화 벤치는 2026-04-20 기준 공개 수치 미확인. 운영 적용 시 자체 측정 권장.

### 7.6 양자화 체크포인트 업데이트

**공식 출시된 체크포인트**

| 리포 | 방식 | 용량 | 정확도 (vs BF16) | 출시 |
|------|------|------|------------------|------|
| `nvidia/Gemma-4-31B-IT-NVFP4` | W4A4 NVFP4 (Model Optimizer v0.42.0) | ~15GB | MMLU Pro -0.31%, GPQA -0.25%, LiveCodeBench -0.27% | 2026-04-02 |
| `RedHatAI/gemma-4-31B-it-NVFP4` | W4A4 NVFP4 (LLM Compressor) | ~20B params | MMLU Pro 98.9% recovery, GSM8k-Platinum 100.1%, IFEval 99.3% | 2026-04-04 |
| `bg-digitalservices/Gemma-4-26B-A4B-it-NVFP4` | W4A4 NVFP4 (MoE) — **커뮤니티** | ~16.5GB (BF16 ~49GB 대비 2.97x 압축) | 평균 97.6% recovery, GSM8K 95.9%, IFEval 99.1% | 2026-04 |

> `bg-digitalservices`는 비공식 커뮤니티 양자화이며, `_QuantGemma4TextExperts` 플러그인으로 3D expert tensor를 개별 `nn.Linear`로 분해 후 양자화. vLLM 적용 시 `gemma4_patched.py` 별도 패치 필요.

**GGUF 체크포인트**

- `unsloth/gemma-4-E4B-it-GGUF`, `unsloth/gemma-4-26B-A4B-it-GGUF`: llama.cpp 경로
- `ggml-org/gemma-4` collection: 공식 HuggingFace 안내에서 소개되는 GGUF

**파인튜닝 지원**

- Unsloth: 전 변형(E2B/E4B/26B-A4B/31B) 비전+텍스트+오디오+RL 지원 (공식 블로그 명시)
- TRL + Vertex AI SFT 레시피 공식 제공 (vision/audio tower freeze 예시 포함)

### 7.7 LMArena 순위 (2026-04 초 기준)

- Gemma 4 **31B**: 오픈 모델 중 LMArena 텍스트 ELO ~1452 (공식 Google 자료 기준 "open 모델 #3" 주장). BenchLM 기준 전체 #34/109 (provisional) ELO 1450
- Gemma 4 **26B-A4B**: 오픈 모델 중 LMArena 텍스트 ELO ~1441 (활성 4B로 31B급에 근접)
- 세부 카테고리(BenchLM, 31B 기준): Coding 1497 / Math 1468 / Hard Prompts 1473 / Instruction Following 1452

> OpenCompass, LiveBench 등 별도 외부 리더보드에 대한 공식 수치는 2026-04-20 기준 원문 확인 실패. 원문 확인 필요.

### 7.8 chatbot-poc 운영 영향 요약 (L40S 46GB + vLLM 0.19.0)

| 항목 | 영향 | 권고 |
|------|------|------|
| vLLM 버전 | 0.19.0 tool calling + 스트리밍 불안정 (JSON 깨짐, HTML 중복, null→"null" 등) | **0.19.1로 업그레이드 권장** (Transformers v5.5.4 동반 업그레이드 필요) |
| 31B 서빙 | FP8 온라인 양자화로 L40S 1장 서빙 가능 (~29GB) | 기존 구성 유지 가능. tool calling 안정화 위해 0.19.1 필요 |
| 31B NVFP4 | ~15GB로 여유 큼. 다만 NVFP4는 Blackwell/Hopper 최적화 — L40S(Ada Lovelace)에서의 실측 성능 원문 확인 필요 | 실사용 전 자체 벤치 권장 |
| 26B-A4B | 공식 단일 GPU 가이드 기준 80GB 추천 (MoE weight 전체 상주). L40S 46GB 1장 배치 시 FP8/NVFP4 필요. 커뮤니티 NVFP4 체크포인트는 별도 패치 필요 | 26B-A4B보다 31B FP8이 운영 안정성↑ |
| E4B | RTX 4090 기준 9 tok/s 성능 문제 보고. L40S도 동일 backend 폴백 가능성. 원문 확인 필요 | 챗봇 용도로는 E4B 대신 31B 또는 Gemma 3 유지 검토 |
| Tool calling | 0.19.1에서 상당수 수정, 동시성 pad 토큰 이슈(#39392)는 미해결 | 고동시성 환경에서는 요청 직렬화 또는 대안 고려 |

---

## Sources

### 초안 조사 (2026-04-03)

- [Google 공식 블로그 — Gemma 4 발표](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/)
- [Google AI 모델 카드](https://ai.google.dev/gemma/docs/core/model_card_4)
- [HuggingFace — google/gemma-4-31B](https://huggingface.co/google/gemma-4-31B)
- [NVIDIA Gemma-4-31B-IT-NVFP4](https://huggingface.co/nvidia/Gemma-4-31B-IT-NVFP4)
- [vLLM Blog — Gemma 4 Day-0](https://vllm.ai/blog/gemma4)
- [Gemma 4 vs Qwen 3.5 비교 (ai.rs)](https://ai.rs/ai-developer/gemma-4-vs-qwen-3-5-vs-llama-4-compared)

### 2026-04-20 업데이트 보강

**vLLM 릴리즈/문서/PR**

- [vLLM v0.19.0 Release](https://github.com/vllm-project/vllm/releases/tag/v0.19.0)
- [vLLM v0.19.1 Release](https://github.com/vllm-project/vllm/releases/tag/v0.19.1)
- [vLLM Recipes — Gemma 4](https://docs.vllm.ai/projects/recipes/en/latest/Google/Gemma4.html)
- [vLLM Multimodal Config API](https://docs.vllm.ai/en/latest/api/vllm/config/multimodal/)
- [vLLM Shared Memory IPC Caching Blog](https://blog.vllm.ai/2025/11/13/shm-ipc-cache.html)
- [vLLM PR #38826 — Gemma 4 architecture support](https://github.com/vllm-project/vllm/pull/38826)
- [vLLM PR #38847 — Gemma 4 tool parser bugfix](https://github.com/vllm-project/vllm/pull/38847)
- [vLLM PR #38891 — Gemma 4 FlashAttention sliding-window 레이어 복원 (미병합)](https://github.com/vllm-project/vllm/pull/38891)
- [vLLM PR #38909 — Streaming HTML duplication fix](https://github.com/vllm-project/vllm/pull/38909)
- [vLLM PR #38992 — Streaming JSON delimiter fix](https://github.com/vllm-project/vllm/pull/38992)
- [vLLM PR #39114 — Streaming boolean/number split fix](https://github.com/vllm-project/vllm/pull/39114)

**vLLM Open Issues (2026-04-20 기준)**

- [Issue #38887 — E4B TRITON_ATTN fallback](https://github.com/vllm-project/vllm/issues/38887)
- [Issue #38918 — Turing GPU(SM 7.5) 미지원](https://github.com/vllm-project/vllm/issues/38918)
- [Issue #38999 — 26B-A4B MoE DP>1 crash](https://github.com/vllm-project/vllm/issues/38999)
- [Issue #39000 — 26B-A4B MXFP4 크래시](https://github.com/vllm-project/vllm/issues/39000)
- [Issue #39043 — tool calling + claude code leak](https://github.com/vllm-project/vllm/issues/39043)
- [Issue #39072 — PI coding agent path 검증 실패](https://github.com/vllm-project/vllm/issues/39072)
- [Issue #39133 — 31B INT4 KV cache 축소](https://github.com/vllm-project/vllm/issues/39133)
- [Issue #39216 — transformers 버전 핀 충돌](https://github.com/vllm-project/vllm/issues/39216)
- [Issue #39392 — 동시 요청 시 `<pad>` 토큰](https://github.com/vllm-project/vllm/issues/39392)
- [Issue #39468 — tool call 포맷 오류](https://github.com/vllm-project/vllm/issues/39468)
- [HF Discussion — google/gemma-4-31B-it 문자 중복](https://huggingface.co/google/gemma-4-31B-it/discussions/15)

**양자화 / 모델 카드**

- [RedHatAI/gemma-4-31B-it-NVFP4](https://huggingface.co/RedHatAI/gemma-4-31B-it-NVFP4)
- [bg-digitalservices/Gemma-4-26B-A4B-it-NVFP4 (커뮤니티)](https://huggingface.co/bg-digitalservices/Gemma-4-26B-A4B-it-NVFP4)
- [NVIDIA Developer Blog — Gemma 4 Edge/On-Device](https://developer.nvidia.com/blog/bringing-ai-closer-to-the-edge-and-on-device-with-gemma-4/)

**공식 문서**

- [HuggingFace Blog — Welcome Gemma 4](https://huggingface.co/blog/gemma4)
- [Transformers 공식 문서 — Gemma4](https://huggingface.co/docs/transformers/model_doc/gemma4)
- [Google DeepMind — Gemma 4](https://deepmind.google/models/gemma/gemma-4/)

**리더보드**

- [BenchLM — Gemma 4 31B](https://benchlm.ai/models/gemma-4-31b)
