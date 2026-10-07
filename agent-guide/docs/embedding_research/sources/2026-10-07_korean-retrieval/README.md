# 한국어 검색 임베딩 조사 원본 자료 (2026-10-07)

[`korean-retrieval.md`](../../topics/korean-retrieval.md)의 근거 자료다. 문서의 수치와 라이선스는 2026-10-07에 여기 있는 사본과 한 줄씩 대조했다. 모델카드와 리더보드는 계속 갱신되므로 인용 시점을 고정하려고 남긴다.

조사 대상은 OpenAI `text-embedding-3-large`와 비교되는 공개 임베딩 모델, 그중 한국어 검색 성능과 EmbeddingGemma 2다.

## 디렉터리

| 경로 | 내용 |
|------|------|
| `official/` | Google 공식 발표 글과 문서 (텍스트 추출본) |
| `model-cards/` | HuggingFace 모델카드 로컬 사본 |
| `benchmarks/` | 한국어 검색 리더보드·평가 저장소의 README 사본 |
| `community/` | 실사용 후기 글 원문 (텍스트 추출본) |

## official/

| 파일 | 문서 출처 | 설명 |
|------|-----------|------|
| `blog_embeddinggemma-2.txt` | S01 | 2026-10-06 출시 글. 740M, Apache 2.0, 코드 검색 68.76 → 78.68(+9.92) |
| `ai-google-dev_embeddinggemma-1_model-card.txt` | S03 | 1세대 모델카드. 문맥 2K, MTEB 다국어 61.15, 영어 69.67, 코드 68.76. HuggingFace 판은 접근 승인이 필요해 Google 문서 판을 받았다 |

## model-cards/

| 파일 | 문서 출처 | 설명 |
|------|-----------|------|
| `google_embeddinggemma-2.md` | S02 | 2세대 사양(270M~740M, 8,192토큰, 768차원)과 차원별 점수표 |
| `Qwen_Qwen3-Embedding-0.6B.md` | S04 | Qwen3-Embedding 비교표. 비교 모델 수치는 2025-05-24 MTEB 리더보드 기준이라고 적혀 있다 |
| `nlpai-lab_KURE-v1.md` | S06 | 8개 과제 Top-k별 평균표. "Top-k 10" 절의 열 이름이 `NDCG_top1`로 잘못 적혀 있으나 값은 @10이다 |
| `dragonkue_snowflake-arctic-embed-l-v2.0-ko.md` | S07 | 7개 과제 표(MLDR 제외), 학습 최대 길이 1,300토큰, 질의 프롬프트 |
| `nlpai-lab_KURE-v2.md` | S11 | 154M 다중 벡터 모델. 라이선스는 Apache-2.0 |
| `sionic-ai_comsat-embed-ko-8b-preview.md` | S12 | Qwen3-Embedding-8B 대비 9개 과제 표, CC-BY-NC-4.0 |
| `hyunseop_qwen3-embedding.md` | S17 | Qwen3-Embedding-4B 한국어 튜닝판. 라이선스 표기 없음 |
| `Day1Kim_Qwen3-Embedding-0.6B-Korean.md` | S18 | Qwen3-Embedding-0.6B 한국어 튜닝판. 라이선스 표기 없음. 위젯 예시 문장이 많아 용량이 크다 |
| `telepix_PIXIE-Rune-v1.5.md` | S28 | 라이선스 확인용 (Apache-2.0) |
| `perplexity-ai_pplx-embed-v1-4b.md` | S29 | 라이선스 확인용 (MIT) |
| `yjoonjang_colbert-ko-en-v2.md` | S30 | 라이선스 확인용 (Apache-2.0) |

## benchmarks/

| 파일 | 문서 출처 | 설명 |
|------|-----------|------|
| `BM-K_Korean-MTEB-Retrieval-Evaluators_README.md` | S05 | 한국어 6개 과제 dense·sparse 표. TelePIX(PIXIE 제작사)의 평가다 |
| `nlpai-lab_KURE_README.md` | S11 | MTEB(kor, v2) 9개 과제 순위표 18행과 KURE-v2 배포 비용 측정. 저장소 코드 라이선스는 MIT |
| `OnAnd0n_ko-embedding-leaderboard_README.md` | S10 | 리더보드 V2. 7개 과제, NDCG@5·10 평균 |
| `Atipico1_Kor-IR_README.md` | S08 | Ko-StrategyQA 단일 과제. 2024-07-03 이후 갱신 없음 |
| `Marker-Inc-Korea_AutoRAG-example-korean-embedding-benchmark_README.md` | S09 | Top-k별 표. 문서가 인용한 Recall@5는 "Top-k 5" 절에 있다 |

## community/

| 파일 | 문서 출처 | 설명 |
|------|-----------|------|
| `core-today_korean-embedding-models-ollama-benchmark-2026.txt` | S13 | 2026-10-01. 문서 589건, 질의 85개(사람 22, LLM 45, 키워드 18) |
| `velog_judy-choi_rag-embedding-comparison.txt` | S14 | 2025-02-02. 보험약관 RAG, 단일 질문 "보험금의 지급사유" |

## 받지 못한 자료

- S16 아카라이브 글은 접속이 403으로 막혀 사본이 없다. 문서의 해당 수치는 원문 대조를 하지 못했다.
- S15, S19, S20과 제외 자료 S21–S27은 이번에 받지 않았다.
