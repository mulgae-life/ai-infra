# 임베딩 모델 리서치

검색·RAG에 쓸 임베딩 모델을 고를 때 근거로 쓰는 조사 문서다. 연구계 전용 문서라 S3 배포 대상(`llm-serving/`) 밖인 `agent-guide/docs/`에 둔다. 생성 모델 조사는 [slm_research](../slm_research/README.md)에 있고, 디렉토리 구조와 규칙은 그쪽과 같다.

## 구조

| 경로 | 내용 |
|------|------|
| `models/` | 모델 패밀리 하나를 다루는 조사. 스펙, 벤치마크, 아키텍처, 서빙. 첫 문서가 생길 때 만든다 |
| `topics/` | 여러 모델에 걸친 주제 조사. 모델 간 비교, 한국어 검색, 단일·다중 벡터 방식, 한국어 추가 학습 |
| `sources/` | 문서가 인용한 원본 자료. `<조사일>_<주제>/` 단위로 묶고, 각 폴더의 README가 어느 문서의 근거인지 밝힌다 |

## 문서

### topics/

| 문서 | 조사일 | 내용 | 원본 자료 |
|------|--------|------|-----------|
| [korean-retrieval.md](topics/korean-retrieval.md) | 2026-10-07 | OpenAI `text-embedding-3-large`를 기준으로 본 공개 임베딩 모델. EmbeddingGemma 2의 위치, 한국어 검색 직접 비교, Qwen3-Embedding 한국어 추가 학습, 목적별 후보 | [2026-10-07_korean-retrieval](sources/2026-10-07_korean-retrieval/README.md) |

## 새 조사를 넣을 때

- 모델 하나를 다루면 `models/<패밀리><버전>.md`, 여러 모델이나 기법을 다루면 `topics/<주제>.md`에 둔다.
- 원본 자료를 남기면 `sources/<YYYY-MM-DD>_<주제>/`를 만들고 README에 근거 대상 문서와 하위 폴더 설명을 적는다. 하위 폴더 이름은 `slm_research`와 같은 것을 쓴다: `official/`(제작사 공식 자료), `model-cards/`, `benchmarks/`, `papers/`, `community/`, `repos/`, `probes/`(직접 돌린 실측), `collect/`(수집 스크립트).
- 이 표에 한 줄을 추가한다.
