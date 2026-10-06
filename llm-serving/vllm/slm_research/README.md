# SLM 리서치

서빙 모델을 고르고 운영 설정을 정할 때 근거로 쓴 조사 문서다. 연구계 전용이라 S3 배포에서 제외한다(`llm-serving/start.sh`의 `*/slm_research/*`).

## 구조

| 경로 | 내용 |
|------|------|
| `models/` | 모델 패밀리 하나를 다루는 조사. 스펙, 벤치마크, 아키텍처, vLLM 서빙 |
| `topics/` | 여러 모델에 걸친 주제 조사. 모델 간 비교, 한국어, 서빙 기법, 신규 모델 계열 |
| `sources/` | 문서가 인용한 원본 자료. `<조사일>_<주제>/` 단위로 묶고, 각 폴더의 README가 어느 문서의 근거인지 밝힌다 |

## 문서

### models/

| 문서 | 조사일 | 내용 |
|------|--------|------|
| [qwen3.8.md](models/qwen3.8.md) | 2026-08-19 | Qwen3.8-27B. **현행 연구계 모델** |
| [qwen3.6.md](models/qwen3.6.md) | 2026-04-20 | Qwen3.6 패밀리, 하이브리드 계열 알려진 이슈 |
| [qwen3.5.md](models/qwen3.5.md) | 2026-04-03 | Qwen3.5 전 라인업 (3.6·3.8의 아키텍처 원형) |
| [gemma4.md](models/gemma4.md) | 2026-04-03 | Gemma 4 전 라인업, Thinking 모드, 운영 플래그 |

### topics/

| 문서 | 조사일 | 내용 | 원본 자료 |
|------|--------|------|-----------|
| [gemma4-vs-qwen.md](topics/gemma4-vs-qwen.md) | 2026-04-20 | Gemma 4와 Qwen의 운영 관점 비교. 본문 표는 Qwen3.6 기준이고 2.6절에 Qwen3.8 갱신분이 있다 | — |
| [korean-ability.md](topics/korean-ability.md) | 2026-08-19 | Gemma 4 26B·31B와 Qwen3.8 27B의 한국어 능력 | [2026-08-19_korean](sources/2026-08-19_korean/README.md) |
| [mtp.md](topics/mtp.md) | 2026-05-12 | Multi-Token Prediction의 모델별 도입 형태와 vLLM 서빙 차이 | — |
| [jev.md](topics/jev.md) | 2026-10-06 | TypeSafe Jev 판단 전용 모델과 공개 재현 모델 | [2026-10-06_jev](sources/2026-10-06_jev/README.md) |

## 새 조사를 넣을 때

- 모델 하나를 다루면 `models/<패밀리><버전>.md`, 여러 모델이나 기법을 다루면 `topics/<주제>.md`에 둔다.
- 원본 자료를 남기면 `sources/<YYYY-MM-DD>_<주제>/`를 만들고 README에 근거 대상 문서와 하위 폴더 설명을 적는다. 하위 폴더 이름은 기존 것을 재사용한다: `official/`(제작사 공식 자료), `model-cards/`, `benchmarks/`, `papers/`, `community/`, `repos/`, `probes/`(직접 돌린 실측), `collect/`(수집 스크립트).
- 이 표에 한 줄을 추가한다.
