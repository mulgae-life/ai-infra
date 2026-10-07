# 임베딩 모델 조사 정리

> **기준:** OpenAI `text-embedding-3-large`  
> **범위:** EmbeddingGemma 2 → 공개 텍스트 모델 → 한국어 성능·후기 → Qwen3 한국어 파인튜닝  
> **조사 기준일:** 2026-10-07, 한국시간  
> **작성 방식:** 공개 원문 조사·비교. 모델 추론·벤치마크를 직접 재실행하지 않음.  
> **원문 대조:** 2026-10-07. S01–S14·S17·S18·S28–S30의 수치·라이선스를 원문 사본과 대조. S15·S16·S19–S27은 미대조(S16은 접속 차단).  
> **원본 자료:** [sources/2026-10-07_korean-retrieval/](../sources/2026-10-07_korean-retrieval/README.md)

## 1. 핵심 결론

- **한국어 검색에서도 `3-large`보다 높은 점수를 보고한 공개 모델이 여러 개 존재.**
  - 직접 비교 근거: Qwen3-Embedding-8B, KURE-v1, BGE-M3, Snowflake 한국어 튜닝판 등.
  - 단, 분야·질의·평가셋에 따라 순위가 바뀜. 모든 한국어 업무에서 우위라는 뜻은 아님. [S05–S09]
- **EmbeddingGemma 2의 다국어 텍스트 종합 점수는 Qwen3 계열보다 낮음.**
  - 공개 보고값: Gemma 2 **61.36**, Qwen3-0.6B **64.33**, Qwen3-8B **70.58**.
  - `3-large` **58.93**보다는 높음. 한국어 단독 점수와 구분 필요. [S02, S04]
- **EmbeddingGemma 2의 핵심 차별점은 소형·온디바이스·멀티모달 통합.**
  - 텍스트·이미지·음성·영상을 같은 벡터 공간에서 검색.
  - 텍스트만 사용하면 270M, 전체 멀티모달 구성은 740M.
  - 전작 대비 일반 텍스트 성능 변화는 작고, 코드 검색 개선은 큼. [S01, S02]
- **Gemma 2의 한국어 대 `3-large` 직접 비교는 이번 조사에서 미확인.**
  - 한국어 리더보드에 등장하는 `embeddinggemma-300m`은 1세대.
  - 1세대 성적을 2세대 성적으로 인용하면 안 됨. [S10]
- **한국어 소형 모델 후보는 KURE-v1·Snowflake-ko·PIXIE-Rune-v1.5가 우선 검토 대상.**
  - Qwen3-0.6B보다 높게 나온 한국어 평가도 확인됨. [S05, S07, S10]
  - PIXIE-Rune은 평가 3곳에서 KURE-v1과 같거나 앞섬. 제작사 평가가 아닌 KURE 저장소·OnAnd0n 표에서도 같은 순서(OnAnd0n은 v1.0 기준). [S05, S10, S11]
- **Qwen3-Embedding 기반 한국어 추가 학습 모델도 존재.**
  - 가장 명확한 원본 대비 개선 사례: **Sionic Comsat-embed-ko-8b-preview**.
  - Qwen3-8B 대비 한국어 검색 9개 과제 평균 **78.25 → 79.30**.
  - 공개 가중치는 **비상업용 CC-BY-NC-4.0**. [S12]
- **실제 도입은 목적별로 구분.**
  - 한국어 텍스트 RAG: Qwen3-8B, KURE-v1, Snowflake-ko부터 비교.
  - 로컬 멀티모달 검색: EmbeddingGemma 2 검토.
  - 다중 벡터 검색 구조까지 변경 가능: KURE-v2, colbert-ko-en-v2 검토.
  - 위 목록은 조사에 따른 후보 제안이며, 자체 데이터에서 확정된 순위는 아님.

## 2. 이름·평가를 먼저 구분

### 2.1 모델 이름 혼동 방지

| 이름 | 의미 | 구분할 사항 |
|---|---|---|
| `google/embeddinggemma-2` | 이번에 질문한 EmbeddingGemma 2 | 텍스트·이미지·음성·영상 지원 |
| `google/embeddinggemma-300m` | 1세대 EmbeddingGemma | 기존 한국어 리더보드의 Gemma는 이 모델 |
| `BAAI/bge-multilingual-gemma2` | Gemma 2 계열 기반의 별도 BGE 임베딩 모델 | Google EmbeddingGemma 2와 다른 모델 |
| `Qwen/Qwen3-Embedding-*` | 이번 텍스트 비교의 Qwen 모델군 | Qwen의 별도 VL 임베딩 모델군과 구분 |
| Snowflake 원본 / `dragonkue/...-ko` | 다국어 원본 / 한국어 튜닝판 | 같은 모델로 표기하지 않음 |
| `KURE-v1` / `KURE-v2` | 단일 벡터 / 토큰별 다중 벡터 검색 모델 | 모델 규모만 비교해 운영 비용을 판단하지 않음 |

근거: 모델 카드·평가 원문. [S02–S04, S06, S07, S11, S16]

### 2.2 점수 읽는 법

- **nDCG@10:** 관련 문서를 상위 10개 결과에서 얼마나 잘 정렬했는지 평가.
- **Recall@5·10:** 관련 문서를 상위 5개·10개에 얼마나 회수했는지 평가.
- **MTEB Mean(Task):** 여러 과제 점수의 평균. 검색 외 분류·군집화·유사도 등이 포함될 수 있음.
- **Mean(TaskType):** 과제 유형별 평균을 집계한 값. Mean(Task)와 다름.
- 이 문서의 nDCG·Recall 표는 대부분 **0–1 값을 100배**해 표시.
- `+1.05점`은 점수 차이. `+1.05%`라는 의미가 아님.
- **같은 평가표 안에서 비교하는 것이 기본.**
  - 데이터셋·언어·split·후보 문서 집합·프롬프트·지표가 다르면 절대점수를 직접 비교하지 않음.
  - 다국어 종합 61점과 한국어 검색 76점을 빼서 모델 간 격차를 만들지 않음.

## 3. EmbeddingGemma 2의 벤치마크 위치

### 3.1 다국어 텍스트 종합

**MTEB Multilingual v2 / Mean(Task), 공개 보고값 비교**

| 모델 | 점수 | Gemma 2 대비 |
|---|---:|---:|
| Qwen3-Embedding-8B | 70.58 | +9.22 |
| Qwen3-Embedding-4B | 69.45 | +8.09 |
| Qwen3-Embedding-0.6B | 64.33 | +2.97 |
| **EmbeddingGemma 2** | **61.36** | **기준** |
| EmbeddingGemma 1 | 61.15 | −0.21 |
| BGE-M3 | 59.56 | −1.80 |
| **text-embedding-3-large** | **58.93** | **−2.43** |

- Google·Qwen의 공개 평가표를 취합한 위치 비교. [S02–S04]
- **동일 시점·동일 실행 환경에서 모든 모델을 재평가한 결과는 아님.**
- Qwen 카드의 비교 모델 수치는 2025-05-24 MTEB 리더보드에서 가져왔다고 명시.
- 위 표의 위치를 현재 전체 리더보드의 절대 등수로 표현하지 않음.
- 한국어만의 우열은 이 표로 판단 불가.

### 3.2 전작 대비 무엇이 달라졌나

| 평가 | Gemma 1 | Gemma 2 | 변화 |
|---|---:|---:|---:|
| MTEB 다국어 v2, Mean(Task) | 61.15 | 61.36 | +0.21 |
| MTEB 영어 v2, Mean(Task) | 69.67 | 68.46 | −1.21 |
| MTEB 코드 v1, Mean(Task) | 68.76 | 78.68 | +9.92 |

- 일반 텍스트 지표가 모두 개선된 것은 아님.
- 다국어 수준을 대체로 유지하면서 코드 검색과 멀티모달 입력으로 기능을 확대.
- 코드 성적은 전작 대비 개선을 뜻함. 이 표만으로 Qwen 코드 검색보다 우수하다고 단정하지 않음. [S01–S03]

### 3.3 뒤늦게 출시한 이유로 이해할 수 있는 차별점

공식 발표가 강조하는 제품 방향이며, Google 내부의 출시 의사결정을 확인한 것은 아님.

| 차별점 | 사양·기능 | 활용 예 |
|---|---|---|
| 통합 임베딩 공간 | 텍스트·이미지·음성·영상 → 공통 768차원 벡터 | 글로 녹음이나 영상의 관련 내용을 검색 |
| 선택적 인코더 | 텍스트 270M / 이미지 포함 440M / 음성 포함 570M / 전체 740M | 앱에 필요한 입력만 활성화 |
| 짧은 벡터 지원 | 768·512·256·128차원 | 벡터 저장량·검색 비용 조정 |
| 문맥 확장 | 8,192토큰 | 1세대의 2K보다 긴 입력 처리 |
| 온디바이스 배포 | 모바일·브라우저·로컬 실행 경로 제공 | 오프라인 개인 미디어·파일 검색 |
| 라이선스 | Apache-2.0 | 1세대 Gemma 라이선스와 달라짐 |

근거: 공식 출시 글·모델 카드. [S01–S03]

- 768→256차원일 때 다국어 점수: **61.36→60.41**. 저장 효율과 품질의 절충 가능. [S02]
- 차원 축소 비율은 벡터 데이터 기준. DB 전체 저장량이 같은 비율로 줄어든다는 뜻은 아님.
- 파라미터 수가 작아도 실제 처리량·지연은 장비, 라이브러리, 입력 길이, 배치에 따라 달라짐.
- 차원 축소·로컬 실행·Apache 라이선스 자체가 Gemma만의 독점적 기능은 아님.
- **멀티모달 전체 740M과 Qwen 텍스트 0.6B의 텍스트 점수만 비교하면 기능 범위를 놓침.**
- **멀티모달에서도 Gemma가 모든 Qwen 모델보다 우수하다는 근거는 확보하지 않음.** 별도 VL 모델끼리의 동등 조건 비교가 필요.

## 4. 한국어에서 3-large를 앞선 직접 비교

### 4.1 BM-K / TelePIX: 한국어 검색 6개 과제

- 과제: Ko-StrategyQA, AutoRAG, MIRACL, PublicHealthQA, Belebele, MultiLongDocRetrieval.
- 아래 지표: **dense 임베딩의 nDCG@10 ×100**.
- 원문의 `Avg. NDCG`는 @1·3·5·10 평균이므로 아래 열과 다름. [S05]

| 모델 | nDCG@10 | 3-large 대비 |
|---|---:|---:|
| **text-embedding-3-large** | **68.53** | **기준** |
| PIXIE-Spell-Preview-1.7B | 78.82 | +10.29 |
| Qwen3-Embedding-8B | 78.39 | +9.86 |
| llama-embed-nemotron-8b | 78.13 | +9.60 |
| PIXIE-Rune-v1.5 | 76.51 | +7.98 |
| KURE-v1 | 76.42 | +7.89 |
| BGE-m3-ko | 75.14 | +6.61 |
| BGE-M3 | 74.83 | +6.30 |
| Snowflake arctic embed l v2.0 — 원본 | 73.90 | +5.37 |
| Qwen3-Embedding-0.6B | 72.15 | +3.62 |
| jina-embeddings-v3 | 70.88 | +2.35 |

- 해석: Qwen8B뿐 아니라 작은 KURE·BGE 계열도 3-large보다 높음.
- 한국어에서는 KURE·BGE가 Qwen0.6B보다 높게 나옴.
- 한계: 제작사 관련 평가. API 설정·평가 시점 등 모든 행의 조건을 완전히 감사한 것은 아님.
- PIXIE·Nemotron 등을 모두 상용 이용 가능한 모델로 분류한 표는 아님. 개별 라이선스 검토는 별도.

### 4.2 다른 직접 비교의 교차 확인

| 출처 | 평가 범위·지표 | 3-large | 공개 모델 |
|---|---|---:|---|
| KURE-v1 모델 카드 | 8개 과제, nDCG@10 | 61.67 | **KURE 69.47**, BGE-M3 68.72 |
| Snowflake-ko 모델 카드 | 7개 과제, nDCG@10 | 66.22 | **Snowflake-ko 74.04**, BGE-m3-ko 73.00, KURE 72.77 |
| Kor-IR | Ko-StrategyQA, nDCG@10 | 73.74 | **e5-large-instruct 80.68**, e5-large 80.35, BGE-M3 79.40 |
| AutoRAG 예제 벤치마크 | Recall@5 | 84.21 | **BGE-M3 92.98**, KoE5 90.35 |

출처: [S06–S09]. 모두 원문 점수에 100을 곱한 값.

- KURE-v1의 8개 과제 표와 최신 KURE 저장소의 9개 과제 표는 다름.
- Snowflake-ko의 7개 과제 평균은 MLDR을 제외.
- Kor-IR은 단일 과제 평가이므로 한국어 전체로 확대 해석하지 않음.
- Kor-IR 표는 2024-07-03 갱신 이후 멈춤. 1·2위(Upstage, Cohere)는 API 모델이라 공개 모델 열에서 제외.
- AutoRAG는 Recall만 인용. 원문의 mRR·nDCG 집계는 추가 구현 검토가 필요.
- 여러 평가에 같은 데이터셋이 반복 사용됨. **출처 수를 독립 재현 실험 수로 간주하지 않음.**

### 4.3 반대 사례: 공공보건에서는 한국어 소형 모델이 3-large에 밀림

**Snowflake-ko 모델 카드의 과제별 nDCG@10 ×100** [S07]

| 과제 | 3-large | BGE-M3 | KURE-v1 | Snowflake-ko |
|---|---:|---:|---:|---:|
| AutoRAG | 76.47 | 83.01 | 87.08 | **90.93** |
| PublicHealthQA | **85.62** | 80.41 | 81.93 | 83.37 |

- 3-large가 공공보건 최고점은 아님. 같은 표에서 e5-mistral-7b-instruct 88.73, bge-multilingual-gemma2 87.10, SFR-Embedding-2_R 86.05, gte-Qwen2-7B-instruct 85.84가 3-large 85.62보다 높음.
- 평균 우위는 후보 선정 근거.
- 특정 의료·보험·금융 문서에서 교체 효과를 보장하는 근거는 아님.
- 다국어 종합표에서는 BGE-M3가 Gemma 2보다 낮아도, 그 사실만으로 한국어 검색 순위를 결정할 수 없음.

## 5. 최신 한국어 후보: 3-large가 없는 평가

### 5.1 KURE-v2와 한국어 9개 검색 과제

**현재 KURE 저장소의 nDCG@10 ×100, 1위–13위** [S11]

| 모델 | 점수 | 검색 표현 |
|---|---:|---|
| **KURE-v2** | **81.60** | 토큰별 다중 벡터 |
| colbert-ko-en-v2 | 80.63 | 토큰별 다중 벡터 |
| Comsat-embed-ko-8b-preview | 79.27 | 단일 벡터 |
| mLateOn | 79.06 | 토큰별 다중 벡터 |
| Qwen3-Embedding-8B | 78.26 | 단일 벡터 |
| Qwen3-Embedding-4B | 77.37 | 단일 벡터 |
| harrier-oss-v1-27b | 76.67 | 단일 벡터 |
| Snowflake-ko | 76.53 | 단일 벡터 |
| F2LLM-v2-8B | 76.38 | 단일 벡터 |
| PIXIE-Rune-v1.5 | 76.18 | 단일 벡터 |
| KURE-v1 | 76.16 | 단일 벡터 |
| BGE-m3-ko | 75.47 | 단일 벡터 |
| BGE-M3 | 75.09 | 단일 벡터 |

- 원문 표에서 BGE-M3 아래 5개 행은 생략.
- KURE-v2: 2026-08-29 공개, 154M, Apache-2.0. MIT는 KURE GitHub 저장소 코드의 라이선스이며 모델카드는 Apache-2.0. [S11]
- 2위 colbert-ko-en-v2도 149M 다중 벡터 모델(Apache-2.0). 다중 벡터 방식을 검토하면 KURE-v2와 함께 비교. [S30]
- PIXIE-Rune-v1.5와 KURE-v1은 사실상 동률(76.18 / 76.16).
- 토큰별 128차원 벡터와 MaxSim 점수 사용.
- 기존 단일 벡터 검색 시스템에서 모델명만 바꾸는 교체는 불가.
- dense 행은 공식 MTEB 결과 저장소에서 취합했다고 명시.
- 이 표에는 3-large가 없음. 다른 표의 3-large 점수를 가져와 격차를 계산하지 않음.
- Comsat 제작자 표와 일부 값이 다름. MLDR 집계·평가 구성 차이를 유지하고 표를 섞지 않음.

### 5.2 OnAnd0n 한국어 리더보드 V2

- 7개 과제의 **NDCG@5·10 평균**.
- 일부 데이터셋·후보군을 수정한 자체 평가.
- 3-large 및 Qwen8B는 이 표에 없음. [S10]

| 모델 | 점수 |
|---|---:|
| pplx-embed-v1-4b | 82.79 |
| Snowflake-ko | 82.14 |
| PIXIE-Rune-v1.0 | 81.57 |
| Qwen3-Embedding-4B | 81.37 |
| KURE-v1 | 80.76 |
| jina-embeddings-v5-text-small | 80.29 |
| BGE-M3 | 79.30 |
| **embeddinggemma-300m — 1세대** | **78.19** |
| Qwen3-Embedding-0.6B | 75.88 |

- pplx-embed-v1-4b: 추가 검토할 유망 후보.
- Snowflake-ko: 소형 한국어 검색 후보로 관심을 가질 근거.
- 이 점수를 앞선 6·8·9개 과제 평균과 직접 비교하지 않음.
- **EmbeddingGemma 2의 한국어 위치는 이 표로 알 수 없음.**

## 6. 한국어 실사용 후기와 근거 수준

| 출처·시점 | 비교·관찰 | 핵심 결과 | 한계 |
|---|---|---|---|
| 코어닷투데이, 2026-10-01 | 제목·요약 589개, 질의 85개 | nDCG@10: Qwen8B **0.889**, Qwen4B **0.854**, BGE **0.833** | 3-large 없음. 짧은 콘텐츠·일부 합성 질의 |
| Judy 보험약관 RAG, 2025-02-02 | 3-large·3-small·e5-small·카카오뱅크 모델 | 공개 예시에서 작성자는 **3-large를 가장 좋게 평가** | 한 가지 공개 질문 중심. BGE·KURE·Qwen 미포함 |
| Familia 회계·세무 경험, 2024-10-15 | KoSimCSE 등과 3-large | **KoSimCSE가 더 좋았다고 보고** | 해당 주장에 대한 표준 지표·평가 규모 미공개 |
| 아카라이브 문서 유사도, 2024-08-06 | OpenAI Large·BGE Gemma2·BGE-M3, 625개 문서 | 평균 순위: Gemma2 **1.81**, OpenAI **1.87**, BGE-M3 **2.32** | 정확한 OpenAI ID 미확인. 질의 검색과 다른 과제 |

출처: [S13–S16]. 후기의 보고값이며 이번 조사에서 재현하지 않음.

- **코어닷투데이:** 키워드 질의를 뺀 67개에서도 Qwen8B > 4B > BGE 순서.
- **속도 비교:** 다른 LLM과 자원을 공유한 측정이 있어 모델 간 효율의 확정 근거로 사용하지 않음. [S13]
- **아카라이브:** 1위 비율은 OpenAI **43.68%**, BGE Gemma2 **39.68%**로 평균 순위와 결론이 다름.
- LLM 심사 시 후보 제시 순서가 고정되어 있고, 모델 공통 유사도 임계값을 적용해 편향 가능성이 있음. [S16]
- 후기에서 확인되는 핵심: 도메인·질의·평가법에 따라 승자가 달라짐.
- 최신 한국어 공개 모델과 3-large를 같은 서비스 데이터에서 대규모 비교한 독립 후기는 이번 조사에서 제한적으로 확인됨.

## 7. Qwen3-Embedding 기반 한국어 파인튜닝

### 7.1 확인한 공개 모델

| 모델 | 기반 | 추가 학습 | 원본 대비 개선 근거 |
|---|---|---|---|
| **Sionic Comsat-embed-ko-8b-preview** | Qwen3-Embedding-8B | 제작자 설명상 한국어 100만 건 이상 | **동일 한국어 9개 과제에서 원본과 직접 비교** |
| hyunseop/qwen3-embedding | Qwen3-Embedding-4B | 한국어 합성 페르소나 쌍, 대조학습 | AutoRAG·MIRACL 결과는 있으나 원본 개선 근거 부족 |
| Day1Kim/Qwen3-Embedding-0.6B-Korean | Qwen3-Embedding-0.6B | 41,881개 학습 쌍, 공개 예시는 건설·지반 기준 중심 | 자체 평가만 있고 원본 비교표 없음 |

출처: [S12, S17, S18].

- hyunseop·Day1Kim 모델카드에는 라이선스 표기가 없음. 이용 전 제작자 확인 필요. [S17, S18]

### 7.2 Comsat: 확인된 개선 폭

**제작자 모델 카드 / 한국어 9개 검색 과제 / nDCG@10 ×100** [S12]

| 과제 | Qwen3-Embedding-8B | Comsat | 변화 |
|---|---:|---:|---:|
| **평균** | **78.25** | **79.30** | **+1.05** |
| MIRACL | 67.83 | 69.64 | +1.81 |
| MrTidy | 61.87 | 62.53 | +0.66 |
| MLDR | 50.36 | 51.83 | +1.47 |
| AutoRAG | 82.76 | 85.18 | +2.42 |
| Ko-StrategyQA | 83.63 | 83.94 | +0.31 |
| PublicHealthQA | 87.21 | 88.71 | +1.50 |
| Belebele | 98.28 | 98.53 | +0.25 |
| SQuADKorV1 | 90.63 | 91.68 | +1.05 |
| LawIRKo | 81.71 | 81.64 | −0.07 |

- 9개 중 8개 과제 상승. 이미 강한 원본을 한국어 검색에 추가 적응시킨 사례.
- 4,096차원, 문맥 8,192토큰. 질의에는 지정 프롬프트 적용.
- 제작자 보고값. 학습 데이터 구성·평가 중복까지 독립 감사하지 않음.
- **공개 가중치: CC-BY-NC-4.0, 비상업용.** 상용 서비스에는 별도 허락 여부 확인 필요.
- 이 표에는 3-large가 없음. 원본 Qwen 대비 개선과 3-large 직접 비교를 구분.

### 7.3 4B·0.6B 튜닝판의 해석

**hyunseop / 4B** [S17]

- `nvidia/Nemotron-Personas-Korea`를 질의–문서 쌍으로 활용했다고 설명.
- AutoRAG: 720개 문서·114개 질의, Hit@10 **0.9298**.
- MIRACL 한국어: 약 149만 문서·213개 질의, nDCG@10 **0.49227**.
- 원본 Qwen4B와 동일 조건의 전후 비교가 없어 개선 여부를 확정하기 어려움.
- 카드의 다른 리더보드 인용을 해당 튜닝 모델의 실측 평균으로 간주하지 않음.

**Day1Kim / 0.6B** [S18]

- 41,881개 학습 샘플, 출력 1,024차원.
- 자체 검색 평가: nDCG@10 **0.6912**, Recall@10 **0.8370**.
- 공개 예시는 건설·지반 문서지만 전체 학습 데이터의 분야 분포까지 확인된 것은 아님.
- 원본 기준점과 일반 한국어 다분야 평가가 없어 범용 성능 상승은 미확인.

**추가로 확인한 유형**

- `alphaedge-ai/Qwen3-Embedding-kor-*`: 한국어 어휘 중심의 vocabulary trimming을 설명하는 경량화 계열. 한국어 검색 성능이 원본보다 향상된 모델로 분류하지 않음. [S19]
- Korean Embedding Lab: Qwen·Comsat 추가 학습 실험을 공개. 확인한 스냅샷에서는 200K 학습 모델이 Comsat 목표 점수에 미달하고 후속 평가는 미완료. 완성된 우승 모델로 추천하지 않음. [S20]

## 8. 목적별 후보 선정

| 목적·조건 | 우선 비교 후보 | 판단 근거·주의점 |
|---|---|---|
| 3-large 대체 여부 검증 | **3-large + KURE-v1 + Snowflake-ko + Qwen3-8B** | 같은 실제 질의로 직접 비교할 최소 후보군 제안 |
| 작은 모델의 한국어 문서 검색 | KURE-v1, Snowflake-ko, PIXIE-Rune-v1.5 | 3-large와의 한국어 직접 비교 근거 존재. PIXIE-Rune은 평가 3곳에서 KURE-v1과 같거나 앞섬 |
| 4B 규모에서 품질·자원 절충 | Qwen3-4B, pplx-embed-v1-4b | 한국어 모델 간 비교 유망. 별도 자체 검증 필요 |
| Qwen 한국어 추가 학습의 개선 사례 확인 | Comsat | 원본 대비 개선표 공개. 비상업 라이선스 |
| 모바일·노트북의 통합 미디어 검색 | EmbeddingGemma 2 | 소형 멀티모달·선택적 인코더 |
| 검색 구조까지 변경할 수 있음 | KURE-v2, colbert-ko-en-v2 | 다중 벡터 방식의 품질·인덱스·검색 비용 함께 평가 |
| 공개 모델의 기본 기준점 | BGE-M3 | 여러 한국어 직접 비교에서 일관된 후보 가치 |

- 위 선택은 공개 근거에 따른 **시험 우선순위**.
- 최신 전체 모델을 빠짐없이 평가한 확정 순위가 아님.
- 라이선스 확인(모델카드 기준): KURE-v1은 MIT, KURE-v2는 Apache-2.0, Snowflake-ko는 Apache-2.0, PIXIE-Rune-v1.5는 Apache-2.0, colbert-ko-en-v2는 Apache-2.0, Qwen3-Embedding은 Apache-2.0, pplx-embed-v1-4b는 MIT, Gemma 2는 Apache-2.0, Comsat preview는 CC-BY-NC-4.0. [S02, S04, S06, S07, S11, S12, S28–S30]
- 공개 가중치와 학습 데이터·코드까지 모두 공개된 모델은 구분해야 함.

### 자체 평가 권장안

1. 실제 한국어 질의 **200–500개**와 사람이 확인한 정답 문서 준비.
2. 원문·청크·검색 후보군·k는 통일하고, 모델별 공식 질의·문서 형식 적용.
3. 임베딩 단독 **Recall@10·nDCG@10**을 먼저 비교.
4. 전문용어·약어·숫자·부정·예외조건·한영 혼합·장문으로 나누어 오류 확인.
5. 동일 리랭커·생성 모델을 붙여 최종 RAG 답변 품질 비교.
6. GPU 메모리·색인 시간·질의 지연·저장량까지 포함해 도입 판단.

- 위 절차는 제안이며 이번 조사에서 실행하지 않음.
- Snowflake-ko는 질의 프롬프트가 필요하며, 카드상 미세조정 최대 길이는 1,300토큰. 지원 문맥 길이만으로 장문 성능을 가정하지 않음. [S07]
- 모델 교체 시 문서 임베딩도 새 모델로 다시 생성. 서로 다른 모델의 벡터를 같은 의미 공간으로 취급하지 않음.

## 9. 조사하면서 바로잡은 해석

| 처음 생길 수 있는 인상 | 최종 정리 |
|---|---|
| 뒤늦게 나온 Gemma 2가 Qwen보다 낮으니 의미가 없다 | 텍스트 종합 성적 외에 소형 멀티모달·온디바이스 기능을 함께 평가해야 함 |
| Gemma 2는 멀티모달에서 Qwen보다 우수하다 | 비교한 Qwen은 텍스트 모델. 별도 멀티모달 모델들과의 우열은 이번 조사로 미확정 |
| 한국어 리더보드에 Gemma 점수가 있으니 2세대 평가다 | 해당 항목은 1세대 `embeddinggemma-300m` |
| Qwen 다국어 점수가 높으니 한국어 소형 모델도 Qwen이 우선이다 | 한국어 평가에서는 KURE·BGE·Snowflake-ko가 Qwen0.6B를 앞선 사례 존재 |
| KURE-v2가 작으니 기존 벡터 DB에서 쉽게 교체할 수 있다 | 다중 벡터 인덱싱·검색이 필요하며 운영 구조가 달라짐 |
| KURE 저장소가 MIT이니 KURE-v2 가중치도 MIT다 | 모델카드는 Apache-2.0. MIT는 저장소 코드의 라이선스 |
| 공공보건 과제에서는 3-large가 최고다 | 한국어 튜닝 소형 모델보다 높을 뿐, 같은 표에 3-large보다 높은 모델이 4개 있음 |
| Comsat은 Qwen과 관계없는 한국어 모델이다 | Qwen3-Embedding-8B 기반 한국어 추가 학습 모델 |
| 한국어 파인튜닝 모델이라는 이름이면 원본보다 좋다 | 원본과 같은 조건의 비교 결과가 있어야 개선을 주장할 수 있음 |
| 서로 다른 후기 10개면 독립 검증 10회다 | 같은 원 평가표의 재인용을 제외해야 함 |

## 10. 조사 범위·제외한 근거

- 초기 한국어 조사: 12개 폭넓은 쿼리에서 중복을 제외한 URL **103개**를 선별.
- 이후 Gemma 2 공식 문서와 Qwen 한국어 튜닝 모델을 추가 확인.
- **103개 모두를 정독하거나 독립 실험으로 인정했다는 뜻은 아님.**
- 우선 채택: 공식 모델 카드, 제작자 평가, 공개 평가 코드, 작성자의 원 실험 후기.
- 모델 재실행, 학습 데이터 전수 점검, 통계적 유의성 검증은 수행하지 않음.

| 자료 유형·예시 | 처리 |
|---|---|
| PyTorchKR의 OnAnd0n 리더보드 소개 | 원 평가의 재인용. 별도 독립 실험으로 세지 않음 |
| Snowflake-ko 아카라이브 발표 글 | 제작자 모델 카드와 같은 평가 계열 |
| 2023년 한국어 Retriever 비교 | OpenAI 기준이 ada-002이므로 3-large 직접 비교에서 제외 |
| GPTers 임베딩 함수 질문 | 실제 대상이 3-small인 사례. 3-large 실패 사례로 인용하지 않음 |
| 미완성 온디바이스 비교표 | 일부 모델 점수가 TBD이거나 3-large가 없어 확정 순위 근거로 사용하지 않음 |
| 입시 챗봇 연구 저장소 | 비교 계획은 있지만 확인한 README 결과 절이 비어 있음 |
| 한국어 분류·STS와 영어 QA가 섞인 논문 | 한국어 검색에서 3-large를 이겼다는 근거로 확대하지 않음 |

검토 링크: [S21–S27].

## 11. 출처 목록

### 공식 모델·벤치마크

- **[S01]** [Google — EmbeddingGemma 2 출시 발표](https://blog.google/innovation-and-ai/technology/developers-tools/embeddinggemma-2/) — 2026-10-06.
- **[S02]** [Google — EmbeddingGemma 2 모델 카드](https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2) · [Hugging Face](https://huggingface.co/google/embeddinggemma-2).
- **[S03]** [Google — EmbeddingGemma 1 모델 카드](https://ai.google.dev/gemma/docs/embeddinggemma/model_card) · [Hugging Face](https://huggingface.co/google/embeddinggemma-300m) — Hugging Face 판은 접근 승인 필요.
- **[S04]** [Qwen — Qwen3-Embedding 공식 모델 카드·비교표](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B).
- **[S05]** [BM-K / TelePIX — Korean-MTEB-Retrieval-Evaluators](https://github.com/BM-K/Korean-MTEB-Retrieval-Evaluators).
- **[S06]** [KURE-v1 모델 카드 — 8개 과제 평가](https://huggingface.co/nlpai-lab/KURE-v1).
- **[S07]** [dragonkue — Snowflake 한국어 튜닝 모델 카드](https://huggingface.co/dragonkue/snowflake-arctic-embed-l-v2.0-ko).
- **[S08]** [Atipico1 — Kor-IR](https://github.com/Atipico1/Kor-IR).
- **[S09]** [Marker — AutoRAG 한국어 임베딩 벤치마크](https://github.com/Marker-Inc-Korea/AutoRAG-example-korean-embedding-benchmark).
- **[S10]** [OnAnd0n — 한국어 임베딩 리더보드 V2](https://github.com/OnAnd0n/ko-embedding-leaderboard).
- **[S11]** [KURE 현재 저장소 — 9개 과제 평가](https://github.com/nlpai-lab/KURE) · [KURE-v2 모델 카드](https://huggingface.co/nlpai-lab/KURE-v2).
- **[S12]** [Sionic AI — Comsat-embed-ko-8b-preview](https://huggingface.co/sionic-ai/comsat-embed-ko-8b-preview).

### 원문 대조 때 추가 확인한 모델 카드

- **[S28]** [TelePIX — PIXIE-Rune-v1.5 모델 카드](https://huggingface.co/telepix/PIXIE-Rune-v1.5).
- **[S29]** [Perplexity — pplx-embed-v1-4b 모델 카드](https://huggingface.co/perplexity-ai/pplx-embed-v1-4b).
- **[S30]** [yjoonjang — colbert-ko-en-v2 모델 카드](https://huggingface.co/yjoonjang/colbert-ko-en-v2).

### 실제 실험·후기

- **[S13]** [코어닷투데이 — 한국어 문서로 Qwen·BGE 등을 직접 비교](https://core.today/blog/korean-embedding-models-ollama-benchmark-2026).
- **[S14]** [Judy — 보험약관 RAG 임베딩 비교](https://velog.io/@judy_choi/RAG-시리즈-임베딩-모델별-RAG-성능-비교).
- **[S15]** [Familia — 회계·세무 경험 및 SimCSE·LoRA 튜닝](https://familia-89.tistory.com/101).
- **[S16]** [아카라이브 — OpenAI Large vs BGE Gemma2 vs BGE-M3](https://arca.live/b/alpaca/113094399) · [관련 데이터 설명](https://arca.live/b/alpaca/113036259?p=1).

### Qwen 한국어 튜닝·관련 실험

- **[S17]** [hyunseop — Qwen3-Embedding-4B 한국어 튜닝](https://huggingface.co/hyunseop/qwen3-embedding).
- **[S18]** [Day1Kim — Qwen3-Embedding-0.6B-Korean](https://huggingface.co/Day1Kim/Qwen3-Embedding-0.6B-Korean).
- **[S19]** [alphaedge-ai — Qwen3-Embedding-kor-32768](https://huggingface.co/alphaedge-ai/Qwen3-Embedding-kor-32768) — 어휘 축소 모델.
- **[S20]** [LLM-OS-Models — Korean Embedding Lab](https://github.com/LLM-OS-Models/Embedding) — 추가 학습·평가 실험 기록.

### 재인용·적용 범위 제한·제외 자료

- **[S21]** [PyTorchKR — 한국어 임베딩 리더보드 소개](https://discuss.pytorch.kr/t/ko-embedding-leaderboard/11416).
- **[S22]** [아카라이브 — Snowflake-ko 발표](https://arca.live/b/alpaca/130702141).
- **[S23]** [ssisOneTeam — 2023 한국어 Retriever 벤치마크](https://github.com/ssisOneTeam/Korean-Embedding-Model-Performance-Benchmark-for-Retriever).
- **[S24]** [GPTers — 임베딩 함수 질문](https://www.gpters.org/question/post/please-recommend-embedding-function-Tgo3a980BRA884U).
- **[S25]** [Peterica — 온디바이스 한국어 임베딩 비교](https://github.com/peterica/peterica-edge-rag/blob/main/ondevice-rag/02-cases/embedding/embedding-benchmark-ko.md).
- **[S26]** [KMOU-NLP-Lab — 입시 챗봇 연구 저장소](https://github.com/KMOU-NLP-Lab/DeuChatbot).
- **[S27]** [정보과학회 — 임베딩 모델 평가 연구](https://jok.kiise.or.kr/pub-reader/1818).

---

**문서 사용 시:** 각 표의 평가 범위와 원문을 함께 유지할 것. 동적으로 갱신되는 리더보드·모델 카드의 수치는 조사일 이후 달라질 수 있음.
