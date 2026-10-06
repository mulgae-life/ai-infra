# Alibaba Qwen3.8-27B 조사

> 조사일: 2026-08-19 (모델카드·로컬 체크포인트 재확인 2026-08-20) | 출시: 2026-08-14
> Qwen3.5 아키텍처를 그대로 물려받고 포스트 트레이닝만 갱신한 Dense 27B 비전-언어 모델.
> 연구계 인스턴스(`instances/qwen.yaml`)가 Qwen3.6-27B-FP8에서 이 모델로 교체됐다.
>
> 한국어 능력은 [korean-ability.md](../topics/korean-ability.md), Gemma 4와의 운영 비교는 [gemma4-vs-qwen.md](../topics/gemma4-vs-qwen.md) 참조.

---

## 📌 TL;DR

1. **아키텍처는 Qwen3.5-27B·3.6-27B와 완전히 같다.** 로컬 `config.json`을 대조하면 차이가 `transformers_version` 한 줄뿐이라 서빙 프로필을 바꿀 필요가 없다.
2. **지능 축에서 세대 도약이 크다.** 같은 카드 안에서 3.6-27B 대비 GPQA +1.4, LiveCodeBench +6.4, HLE +6.8, QwenSWEBench +29.7이다.
3. **thinking을 켠 상태가 기준이다.** 현행 `qwen.yaml`은 `enable_thinking: false`라 위 수치가 그대로 재현되지 않는다.

---

## 1. 위치와 라인업

| 항목 | 값 |
|------|-----|
| 출시일 | 2026-08-14 |
| HuggingFace ID | `Qwen/Qwen3.8-27B` · `Qwen/Qwen3.8-27B-FP8` |
| 라이선스 | Apache 2.0 |
| 체크포인트 용량 (FP8) | 29GB |
| 아키텍처 클래스 | `Qwen3_5ForConditionalGeneration` |
| 입력 | 텍스트 + 이미지 + 비디오 |

### 27B 계열 3세대 대조

로컬에 받아둔 세 체크포인트를 직접 열어 확인했다.

| 항목 | Qwen3.5-27B-FP8 | Qwen3.6-27B-FP8 | **Qwen3.8-27B-FP8** |
|------|:---:|:---:|:---:|
| 레이어 | 64 | 64 | 64 |
| Hidden | 5,120 | 5,120 | 5,120 |
| 전문가(MoE) | 없음 (Dense) | 없음 (Dense) | 없음 (Dense) |
| 어휘 | 248,320 | 248,320 | 248,320 |
| 네이티브 컨텍스트 | 262,144 | 262,144 | 262,144 |
| 체크포인트 | 29GB | 29GB | 29GB |

**`config.json`의 실제 차이는 `transformers_version`(4.57.1 → 5.8.0.dev0) 한 항목뿐이다.** 3.6-27B에서 3.8-27B로 옮길 때 GPU 메모리 배분, 텐서 병렬, 컨텍스트 설정을 다시 잡을 이유가 없다.

바뀐 것은 채팅 템플릿이다. `chat_template.jinja`가 153줄에서 169줄로 늘었고 `reasoning_effort` 처리 구간이 새로 들어왔다(4장).

> ⚠️ Qwen3.6에는 MoE 계열인 35B-A3B도 있었고 `gemma4-vs-qwen.md`의 벤치 표는 그쪽 기준이다. 27B 계열은 Dense라 활성 파라미터가 27B 전부이며, 디코드 비용 특성이 35B-A3B(활성 3B)와 전혀 다르다.

---

## 2. 벤치마크 — 공식 모델카드

카드가 비교 대상으로 올린 모델은 Qwen3.6-27B(직전 세대), Qwen3.7-Plus(상위 모델), Muse Glimmer-30B, Opus4.6 Max다.

### 2.1 텍스트

| 항목 | 벤치마크 | **Qwen3.8-27B** | Qwen3.6-27B | Qwen3.7-Plus | Opus4.6 Max |
|------|------|:---:|:---:|:---:|:---:|
| 과학 추론 | GPQA Diamond | **89.2** | 87.8 | 90.3 | 91.3 |
| 다분야 추론 | HLE | **30.8** | 24.0 | 34.7 | 40.0 |
| 지시이행 | IFBench | **79.5** | 69.1 | 79.1 | 62.5 |
| 경쟁 코딩 | LiveCodeBench v6 | **90.3** | 83.9 | 89.6 | 88.8 |
| 터미널 에이전트 | Terminal Bench 2.1 | **73.0** | 63.4 | 64.0 | 78.2 |
| 에이전트 코딩 | SWE-bench Pro | **61.7** | 53.5 | 57.6 | 53.4 |
| 에이전트 코딩 | DeepSWE 1.1 | **42.2** | 13.3 | 14.2 | — |
| 레포 단위 생성 | NL2Repo-Bench | **42.3** | 36.2 | 41.1 | 47.6 |
| 소프트웨어 공학 | QwenSWEBench (자체) | **79.0** | 49.3 | 59.2 | 63.8 |
| 장기 업무 | CoWorkBench (자체) | **70.7** | 61.0 | 65.1 | 68.2 |
| 직무 과제 | JobBench | **33.4** | 21.8 | 27.6 | — |
| 프런티어 에이전트 | Agents' Last Exam (Pass@1 / Score) | **20.4 / 42.9** | 10.6 / 27.3 | 13.2 / 33.6 | — |

직전 세대 대비 상승폭이 가장 큰 항목은 DeepSWE 1.1(+28.9)과 자체 벤치인 QwenSWEBench(+29.7)다. 둘 다 에이전트 코딩 계열이라 이번 세대가 어디를 겨냥했는지 드러난다.

### 2.2 비전·멀티모달

| 항목 | 벤치마크 | **Qwen3.8-27B** | Qwen3.6-27B | Qwen3.7-Plus | Opus4.6 Max |
|------|------|:---:|:---:|:---:|:---:|
| 컴퓨터 조작 | OSWorld-Verified | **84.3** | 63.9 | 73.3 | 72.7 |
| 브라우저 조작 | WebArena-Verified | **64.8** | 48.8 | 55.3 | — |
| 모바일 조작 | AndroidWorld | **81.9** | 70.3 | 81.0 | 62.0 |
| 앱 재현 | RecreationBench (자체) | **47.1** | 29.8 | 30.2 | — |
| 멀티모달 SWE | SWE-MM | **38.6** | 25.7 | 30.0 | 27.1 |
| 시각 웹 개발 | Vision2Web | **62.9** | 45.0 | 42.1 | — |
| 시각 수학 | MathVision | **90.0** | 85.1 | 90.3 | 65.5 |
| 일반 시각 추론 | BabyVision | **65.7** | 28.9 | 64.7 | 12.6 |
| 차트 분석 | CharXiv (RQ) | **83.7** | 78.4 | 85.8 | 66.0 |
| 문서 인식 | OmniDocBench 1.5 | **91.1** | 89.4 | 91.4 | 86.6 |
| 실세계 인지 | RealWorldQA | **85.9** | 84.1 | 86.9 | 73.9 |
| 체화 지능 | ERQA | **65.5** | 62.5 | 69.8 | 40.8 |

> MathVision·BabyVision·CharXiv는 코드 인터프리터를 붙인 수치가 따로 있다. Qwen3.8-27B 기준으로 각각 94.6 / 85.6 / 90.2까지 오른다. 위 표는 코드 인터프리터 없는 값이다.

### 2.3 Gemma 4와 겹치는 항목

두 카드가 같은 이름으로 싣는 벤치마크는 세 개뿐이다.

| 벤치마크 | **Qwen3.8-27B** | Gemma 4 31B | Gemma 4 26B-A4B |
|------|:---:|:---:|:---:|
| GPQA Diamond | **89.2** | 84.3 | 82.3 |
| LiveCodeBench v6 | **90.3** | 80.0 | 77.1 |
| HLE | **30.8** | 19.5 (검색 사용 26.5) | 8.7 (검색 사용 17.2) |

Gemma 4만 싣는 항목은 MMLU-Pro(31B 85.2), AIME 2026(89.2), Tau2(76.9), Codeforces ELO(2150), MMMLU(88.4)이고, Qwen3.8만 싣는 항목은 SWE-bench Pro·Terminal Bench·IFBench 계열이다. 서로 비는 칸이 많아 종합 우열은 이 세 항목 밖으로 확장할 수 없다.

> ⚠️ **측정 조건이 같지 않다.** Qwen 쪽 코딩·에이전트 수치는 Claude Code 하네스에 256K 컨텍스트, `temperature=1.0`, `top_p=0.95` 기준이고 HLE는 GPT-4o가 채점했다. Gemma 4 카드는 자체 조건으로 잰 값이다. 소수점 단위 비교는 의미가 없고, 두 자릿수 격차만 신호로 본다.

> ⚠️ **한국어는 방향이 반대다.** 디노티시아 한국어 리더보드에서 Gemma 4 31B 0.9000, Qwen3.5-27B 0.8775이고 NOLLI 거시평균도 31B 48.3, Qwen3.5-27B 44.4다(Qwen3.8은 두 벤치 모두 미등재). 근거와 한계는 [korean-ability.md](../topics/korean-ability.md)에 정리했다.

---

## 3. 아키텍처

Qwen3.5 하이브리드 구조를 그대로 쓴다. Gated DeltaNet 세 층마다 Gated Attention 한 층을 끼우는 3:1 배치이며, 이 묶음을 16회 반복해 64층을 만든다.

```
16 × ( 3 × (Gated DeltaNet → FFN) → 1 × (Gated Attention → FFN) )
```

| 구성 | 값 |
|------|-----|
| 파라미터 | 27B (Dense) |
| 레이어 | 64 |
| Hidden | 5,120 |
| FFN 중간 차원 | 17,408 |
| Gated DeltaNet 헤드 | V 48개 / QK 16개, 헤드 차원 128 |
| Gated Attention 헤드 | Q 24개 / KV 4개(GQA), 헤드 차원 256, RoPE 차원 64 |
| 토큰 임베딩 · LM 출력 | 248,320 (padded) |
| MTP | 다단계 학습됨 (`mtp_num_hidden_layers` 존재) |
| 컨텍스트 | 262,144 네이티브, YaRN으로 1,000,000까지 확장 |

비전 인코더는 깊이 27, hidden 1,152, 패치 16, 출력 차원 5,120이다.

Gated DeltaNet 층은 상태 크기가 입력 길이와 무관해 KV 캐시 요구가 Full Attention보다 낮다. 이 특성은 3.5부터 이어진 것이라 [qwen3.6.md](qwen3.6.md)의 KV 관련 서술이 그대로 적용된다.

---

## 4. Thinking 제어

이번 세대에서 운영에 직접 영향을 주는 변경은 여기 몰려 있다.

| 항목 | 기본값 | 설명 |
|------|:---:|------|
| `enable_thinking` | **true** | 요청 단위로 끌 수 있다 |
| `reasoning_effort` | **xhigh** | 사고 깊이. `xhigh` / `medium` / `low` 세 값만 허용 |
| `preserve_thinking` | **true** | 이전 메시지의 사고 블록을 대화 내내 유지 |

**허용값을 벗어나면 HTTP 400이다.** 채팅 템플릿이 `raise_exception`을 던지기 때문이며, OpenAI 규격에서는 정상인 `high`도 여기서는 400이 된다. 운영 가이드 [VLLM_OPS_GUIDE.md §12.5](../../../VLLM_OPS_GUIDE.md)에 호출 예시와 함께 정리돼 있다.

`preserve_thinking`은 에이전트 시나리오에서 판단 일관성을 지키고 KV 캐시 재사용률을 올리는 목적이다. 최신 사용자 메시지의 사고만 남기려면 `false`로 끈다.

### 권장 샘플링 파라미터 (모델카드)

| 모드 | temperature | top_p | top_k | presence_penalty |
|------|:---:|:---:|:---:|:---:|
| Thinking | 1.0 | 0.95 | 20 | 0.0 |
| Instruct (thinking OFF) | 0.7 | 0.80 | 20 | 1.5 |

카드는 출력 길이도 따로 권한다. 사고 내용 262,144 토큰, 최종 응답 131,072 토큰이며 이는 1M 컨텍스트를 전제로 한 값이다. 65,536으로 운영하는 현재 설정과는 전제가 다르다.

---

## 5. 서빙

### 현행 `instances/qwen.yaml` 적용치

| 항목 | 값 | 근거 |
|------|-----|------|
| `model` | `Qwen/Qwen3.8-27B-FP8` | 사전 양자화 체크포인트라 `quantization` 지정 불필요 |
| `tensor_parallel_size` | 2 | GPU 2장 기본 프로필 |
| `gpu_memory_utilization` | 0.9 | 가중치 29GB + 활성화 + KV가 이 비율 안에 들어간다 |
| `max_model_len` | 65,536 | 네이티브 262,144의 일부만 사용 |
| `max_num_seqs` | 20 | 동시 시퀀스 상한 |
| `max_num_batched_tokens` | 32,768 | 멀티모달은 encoder cache로 복제됨 |
| `enable_thinking` | false | 챗봇 지연 감소 목적 |
| `reasoning_effort` | medium | thinking을 켠 호출에만 실효 |
| `speculative_config.method` | mtp | Qwen은 명시 필수 |
| `num_speculative_tokens` | 2 | 2 초과는 수용률 저하 가능 |
| `mm_encoder_tp_mode` | data | Qwen 공식 레시피 |
| `mm_processor_cache_type` | shm | 멀티모달 IPC 절감 |
| `async_scheduling` | false | 멀티모달 encoder cache eviction 경합 방어 |
| `tool_call_parser` | qwen3_xml | — |
| `reasoning_parser` | qwen3 | — |
| `PYTORCH_CUDA_ALLOC_CONF` | expandable_segments:True | 프리필·디코드 크기 편차로 생기는 단편화 방지 |

### 긴 컨텍스트 (YaRN)

262,144를 넘겨야 하면 YaRN을 켠다. vLLM은 `--hf-overrides`로 `rope_parameters`를 덮어쓰고 `VLLM_ALLOW_LONG_MAX_MODEL_LEN=1`을 함께 준다. 로컬 체크포인트의 현재 `rope_type`은 `default`라 YaRN은 꺼져 있다.

> ⚠️ 공개 프레임워크는 모두 정적 YaRN을 구현한다. 스케일 계수가 입력 길이와 무관하게 고정되므로 **짧은 텍스트 품질이 떨어질 수 있다.** 카드도 긴 컨텍스트가 실제로 필요할 때만 켜고, 상용 길이에 맞춰 `factor`를 조정하라고 명시한다(52만 토큰이 상용이면 4.0이 아니라 2.0).

### 긴 영상

`video_preprocessor_config.json`의 `size`는 텍스트·이미지 효율을 위해 보수적으로 잡혀 있다. 시간 단위 영상을 다루려면 `longest_edge`를 469,762,048(영상 토큰 약 224K 상당)로 올려야 프레임 샘플링이 촘촘해진다.

---

## 6. 한국어

공식 한국어 벤치마크는 없다. 모델카드에 다국어 항목 자체가 한 줄도 없다.

연구계 인스턴스(FP8, thinking OFF)로 직접 재본 결과는 이렇다.

| 축 | 결과 |
|------|------|
| 약관 RAG (근거인용·단서구분·환각저항·복합추론) | ✅ 4/4 |
| 13,329자 문서 내 단일 조항 검색 | ✅ 금액·면책기간·조항번호 정확 |
| 문서 어시스턴트 (요약·톤변환·JSON추출·이중제약) | ✅ |
| 격식체 업무 한국어 | ✅ 3표본 무오류 |
| 한자·가나 혼입 | ✅ 3,462자 중 0개 |
| 맞춤법 교정 | ⚠️ 7/10 |
| 어문 규범 판정 | ❌ 프롬프트 민감 |
| 역할극 호칭·등급 | ❌ 3표본 재현 실패 |
| 한글 숫자 → 자릿수 변환 | ❌ 10회 중 0회 |

3.6에서 문제였던 한자·중국어 혼입은 눈에 띄게 줄었다. 무너지는 곳은 어휘 선택과 호칭이며, 격식체 문어체는 오류가 없었다. 근거 원문과 프로브 스크립트는 [korean-ability.md](../topics/korean-ability.md)와 [`sources/2026-08-19_korean/`](../sources/2026-08-19_korean/README.md)에 있다.

---

## 7. 운영 참고

### 이전 세대 이슈의 승계

아키텍처 클래스가 `Qwen3_5ForConditionalGeneration`으로 3.5·3.6과 동일하다. [qwen3.6.md §7](qwen3.6.md)에 정리한 하이브리드 계열 이슈들 — KV 캐시 과대추정, 동시 이미지 요청 크래시, 멀티모달 encoder cache 경합 — 은 구조적으로 같은 경로를 타므로 방어 설정을 그대로 유지한다. **다만 3.8 고유의 vLLM 이슈는 이번 조사에서 확인하지 않았다.**

### thinking을 끄고 쓰는 문제

Qwen3.8은 추론을 전제로 설계됐고 기본값이 thinking ON이다. 커뮤니티 증언은 양쪽으로 갈린다. 끄면 성능이 크게 떨어진다는 쪽은 "띵킹을 끄면 개 ㅈ병신이 됨. 추론 기능을 전제로 깔고 들어간 모델"이라고 했고, 반대쪽은 기본값 `xhigh`로 켜면 과잉추론이 심하다며 SVG 하나에 추론 토큰 22,276개를 쓰고 21분이 걸린 사례를 들었다. 원문과 출처는 [korean-ability.md §5.2](../topics/korean-ability.md)에 있다.

현행 설정은 thinking OFF이므로 2장의 벤치 수치가 그대로 재현되지 않는다. 다만 6장의 약관 RAG·문서 처리 실측은 thinking OFF에서 전부 통과했다. 과제 유형에 따라 영향이 갈리므로, 실제 워크로드로 ON/OFF를 비교해 정하는 편이 확실하다.

### 멀티턴 에이전트에서의 사고 길이

카드가 직접 경고한다. 사고를 줄이면 턴당 응답은 빨라지지만 분석이 부족해 실패와 재시도가 늘어 전체 지연과 토큰 소비가 오히려 커질 수 있다. 단발 챗과 멀티턴 에이전트에서 `reasoning_effort`의 최적값이 다를 수 있다는 뜻이다.

---

## Sources

- [Qwen/Qwen3.8-27B — HuggingFace 모델카드](https://huggingface.co/Qwen/Qwen3.8-27B) (로컬 사본: [`sources/2026-08-19_korean/model-cards/hf_Qwen_Qwen3.8-27B.md`](../sources/2026-08-19_korean/model-cards/hf_Qwen_Qwen3.8-27B.md))
- [google/gemma-4-31b-it — HuggingFace 모델카드](https://huggingface.co/google/gemma-4-31b-it) (로컬 사본: [`sources/2026-08-19_korean/model-cards/hf_google_gemma-4-31b-it.md`](../sources/2026-08-19_korean/model-cards/hf_google_gemma-4-31b-it.md))
- 로컬 체크포인트 `/models/LLM/Qwen/Qwen3.8-27B-FP8` — `config.json`, `chat_template.jinja` 직접 대조
- [vLLM Qwen3.8 Recipe](https://recipes.vllm.ai/Qwen/Qwen3.8-27B)
- [korean-ability.md](../topics/korean-ability.md) — 한국어 능력 비교와 근거 원본
- [qwen3.6.md](qwen3.6.md) · [qwen3.5.md](qwen3.5.md) — 이전 세대 조사
