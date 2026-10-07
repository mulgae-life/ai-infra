# Jev 조사 원본 자료 (2026-10-06)

[`jev.md`](../../topics/jev.md)의 근거 자료다. 문서에 인용한 수치와 문장은 전부 여기 있는 원본에서 나왔다. 모델카드·문서·순위표는 계속 갱신되므로 인용 시점을 고정하려고 남긴다.

조사 대상은 TypeSafe AI의 Jev(`jev-1.13.0`)와 허깅페이스에 공개된 Jev 계열 재현 모델, 그중 한국어 모델이다.

## 디렉터리

| 경로 | 내용 |
|------|------|
| `official/` | TypeSafe 공식 문서·블로그·약관·평가 사이트 사본 |
| `model-cards/` | HuggingFace 모델카드 로컬 사본 |
| `benchmarks/` | 커뮤니티 순위표 Jev Decision Index 0.2.1 원본 데이터 |
| `repos/` | 재현 프로젝트 GitHub README 사본 |
| `community/` | 커뮤니티 분석 글 원문 (텍스트 추출본) |
| `probes/` | 연구계 Qwen3.8-27B-FP8에 직접 보낸 확률 읽기 요청과 출력 |

## official/

| 파일 | 설명 |
|------|------|
| `llms.txt` | 공식 문서 전체 목차. 쿡북 설명에 "질문 13개를 한 요청에 묶으면 10.0배 빠르다"는 수치가 있다 |
| `models.md` | 모델 ID, 가격, 속도 제한, 컨텍스트, 언어 지원, 맞춤 학습 불가 방침 |
| `model-jaggedness_jev-1.13.md` | 공식이 밝힌 약점 9가지 (2026-10-02 검토판) |
| `concepts_system-one.md`, `primitives.md`, `api.md` | System One 개념, 질문 유형, HTTP API |
| `introduction_machine-learning-primer.md` | RLCD 설명. 구조나 손실 함수는 나오지 않는다 |
| `introduction_coding-agents.md`, `legal.md` | 코딩 에이전트용 안내, 법률 문서 목록 |
| `blog_introducing-system-one-models-and-jev.txt` | 9/15 출시 글. "new model architecture, parallel sampler", 193.6배 주장의 출처 |
| `legal_mca.txt` | 고객 약관(MCA, 2026-09-23판). 제한 조항 (b) 증류 금지, (c) 역공학 금지 |
| `evals.typesafe.ai.html.gz` | 공식 워크플로 평가 사이트 원본. 모델별 정확도·비용·시간이 `이름 · workflow · 정확도% · $비용 · 시간 s` 형태로 들어 있다 |
| `github_WorkflowEvals_README.md` | 위 평가의 재현 코드 설명 |
| `github_org_repos.txt` | TypeSafe GitHub 조직의 저장소 목록과 라이선스 (2026-10-06 조회). 공개 범위가 SDK·예제·평가 코드·연동 도구와 포크뿐이라는 근거 |

## model-cards/

| 파일 | 설명 |
|------|------|
| `autotrust_JEV-27B.md` | Qwen3.8-27B 원본 + LoRA 판단 블록. Jev 출력 증류, vLLM 서빙법, B200 속도, 학습 데이터 출처가 가장 자세하다 |
| `autotrust_JEV-27B-VL.md`, `autotrust_JEV-9B.md` | 같은 제작사의 비전판과 9B판 |
| `autotrust_JEV-Gemma4-26B-A4B.md` | gemma-4-26B-A4B-it 기반판 |
| `convaiinnovations_laya*.md` | Laya 영어·다국어·업무 특화판 (인코더 방식) |
| `frontier-infra_jebadiah-27b.md`, `akhilaaa3_Jev-Omni.md`, `AlexWortega_openjev.md`, `wayfind_metask-jev-4b-policy-mix.md`, `iapp_OpenThai-SystemOne.md` | 기타 재현 모델 |
| `ThakiCloud_kd-4b-ko-v0.md` | 한국어. Jev API·Qwen3.8-27B·Laya를 같은 한국어 문항으로 비교한 표가 있다 |
| `corners-ai_CoCo-Decision-4B-Ko.md`, `2nugu_laya-ko.md`, `NomaDamas_KoJev-v0.md`, `mmetamong_ko-decision-roberta-large-klue.md` | 한국어 |

## benchmarks/

| 파일 | 설명 |
|------|------|
| `decision-index-0.2.1_index.json.gz` | 2026-09-28 생성. `jev`와 `models[]`(70개)에 점수(`scores.balanced_skill`), 지연(`latency.median`·`p95`, ms), 측정 경로(`latency_path`), 바탕 모델(`meta.base_model`)이 들어 있다 |
| `decision-index-0.2.1_methodology.json.gz` | 채점·지연 측정 방법. `latency.reproductions.summary`에 측정 조건이 있다 |
| `space_README.md` | 순위표 Space 설명 |

## repos/

| 파일 | 설명 |
|------|------|
| `Mapika_decider_README.md` | 학습 없이 원본 Gemma-4-31B-it로 2위를 한 읽기 방식, vLLM 서빙법. "Jev에서 증류한 것 없음" 명시 |
| `featherless-ai_simple-jev_README.md` | 아무 공개 모델이나 다음 토큰 확률을 읽어 판단 엔드포인트로 만드는 서버 |
| `jaredpalmer_kev_README.md` | Kev. TypeSafe SDK가 그대로 붙는 호환 서버, L40S 속도 수치 |

## community/

| 파일 | 설명 |
|------|------|
| `archerhume_jevs-architecture-unmasked.txt` | 9/17 블랙박스 역추적 글. API 실험으로 구조를 추정하고 관찰과 추정을 구분해 적었다 |
| `systemonemodels_jev-architecture.txt` | 독립 사이트의 정리 글. 공식 공개 범위와 커뮤니티 가설 세 가지 |

## probes/

[`jev.md`](../../topics/jev.md) 7.1절의 근거다. 2026-10-06 연구계에서 실행했다.

| 파일 | 설명 |
|------|------|
| `logprob_chat_easy.py`, `.out.txt` | 쉬운 문항 하나를 게이트웨이 채팅 경로(:5015)로 보내 상위 5개 점수를 받는다. B·C가 상위 5개 밖으로 밀린 사례 |
| `logprob_ambiguous.py`, `.out.txt` | 애매한 문항 하나를 vLLM 전용 경로(:7080 `/generative_scoring`)로 선택지 순서를 돌려 3회 보내고, 같은 문항을 채팅 경로로도 보내 비교한다 |
