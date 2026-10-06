# 한국어 능력 조사 원본 자료 (2026-08-19)

[`korean-ability.md`](../../topics/korean-ability.md)의 근거 자료다. 문서에 인용한 수치·증언은 전부 여기 있는 원본에서 나왔고, 나중에 재조사 없이 다시 확인하거나 다른 모델로 갱신할 때 쓰라고 남긴다.

조사 대상은 Gemma 4 26B-A4B, Gemma 4 31B, Qwen3.8-27B 세 모델의 한국어 능력이다.

## 디렉터리

| 경로 | 내용 |
|------|------|
| `model-cards/` | HuggingFace 모델카드 로컬 사본 |
| `benchmarks/` | 서드파티 벤치마크 원본 |
| `papers/` | arXiv 논문 전문 (텍스트 추출본) |
| `community/` | 커뮤니티·블로그 글 원문 |
| `probes/` | Qwen3.8 라이브 프로브 스크립트와 실측 기록 |
| `collect/` | 수집에 쓴 스크립트 |

## model-cards/

수집 당시의 모델카드 사본이다. 카드는 갱신되므로 인용 시점을 고정하려고 남긴다.

| 파일 | 설명 |
|------|------|
| `hf_Qwen_Qwen3.8-27B.md` | Qwen3.8-27B 모델카드. 텍스트·비전 벤치마크 표, 아키텍처 구성, `reasoning_effort`·`preserve_thinking` 설명, YaRN 설정이 들어 있다 |
| `hf_google_gemma-4-31b-it.md` | Gemma 4 31B 모델카드. 벤치마크 표에 31B·26B-A4B·12B·E4B·E2B와 Gemma 3 27B가 한 표로 실려 있어 26B 수치의 출처이기도 하다 |

두 카드를 나란히 읽은 결과는 [`qwen3.8.md`](../../models/qwen3.8.md) 2.3절에 정리했다. 같은 이름으로 겹치는 벤치마크는 GPQA Diamond, LiveCodeBench v6, HLE 세 개뿐이다.

## benchmarks/

| 파일 | 설명 |
|------|------|
| `denotitia_leaderboard.html.gz` | 디노티시아 한국어 리더보드 페이지 원본. 점수는 Bokeh 플롯 JSON 안에 `"__ndarray__"` 키로 들어 있고, base64 디코딩 → gzip 해제 → `struct.unpack('<Nd')` 순으로 꺼낸다 |
| `wikidocs_ranking.csv` | 위키독스 「우리말 잘하는 LLM」 62개 모델 순위표 |
| `wikidocs_score_total.csv` | 같은 벤치의 배점 합계 |
| `wikidocs_answers_scored.csv.gz` | 문항별 모델 답변과 채점 원본 (3.1MB). Gemma 4 26B 22문항 포함 |
| `g_*.csv` | 같은 스프레드시트의 나머지 시트 |
| `kbench_results.md` | 한국어 벤치마크 생태계 조사 메모 |

디노티시아 점수 (조사 시점):

```
google/gemma-4-31b-it      0.9000
qwen/qwen3.5-27b           0.8775
google/gemma-4-26b-a4b-it  0.8655
qwen/qwen3.6-35b-a3b       0.8358
google/gemma-3-27b-it      0.8200
qwen/qwen3.8               미등재
```

## papers/

`h_<arXiv ID>.txt` 형식이다. 주요 논문은 다음과 같다.

- `h_2608.04397.txt` — NOLLI. 한국어 추론 벤치마크
- `h_2606.02404.txt` — K-BrowseComp. 한국어 웹 탐색
- 나머지는 한국어 벤치마크·국산 모델 기술보고서로, Gemma 4 베이스라인이 있는지 확인하려고 받았다 (결과는 전부 없음)

HTML 원본은 용량 때문에 넣지 않았다. arXiv ID로 다시 받으면 된다.

## community/

디시인사이드, 아카라이브, 클리앙, 레딧, 브런치, 나무위키에서 모은 글이다. 파일명 앞글자로 출처를 구분한다.

- `arca_*` 아카라이브 · `clien*` 클리앙 · `rl_*` 레딧(redlib 미러) · `g_*` `p_*` `s_*` 검색·본문 수집분
- `hf_discussions/` — HuggingFace 모델 토론 API 응답 (`/api/models/<repo>/discussions`)
- `reddit/` — 레딧 스레드 본문
- `dcinside/` — 파싱된 본문 텍스트와 원본 HTML 압축본 두 개. `raw_html.tar.gz`는 개별 글, `raw_gallery_dump.tar.gz`는 갤러리 단위 수집분이다. 본문 추출은 `collect/parse_dc.py`로 재현한다

## probes/

Qwen3.8만 게이트웨이 5015에서 실제로 돌려본 기록이다. Gemma 두 모델은 GPU를 동시에 못 올려 실측하지 않았다.

| 파일 | 용도 |
|------|------|
| `qwen38_ko_findings.md` | 실측 결과 요약 |
| `uc_rag.py` | 보험 약관 기반 답변 (검색 정확도) |
| `uc_doc.py` | 문서 어시스턴트 |
| `uc_proof.py` | 맞춤법 교정 |
| `ko_probe*.py` | 경어법·자모 분해·한자 혼입 등 한국어 품질 |
| `tok_*.py` | 한국어 토크나이저 측정 (문서 본문에는 반영하지 않음) |

## collect/

차단 사이트 접근에 쓴 스크립트다. 같은 조사를 다시 할 때 이 부분에서 시간을 가장 많이 쓴다.

- **디시인사이드**: 데스크톱 주소(`gall.dcinside.com`)는 76바이트만 돌려준다. `m.dcinside.com` 주소에 모바일 User-Agent와 Referer를 붙여야 본문이 나온다 (`dcget.sh`, `dcbulk.sh`)
- **디시 통합검색**: `https://search.dcinside.com/post/q/<URL 인코딩>`으로 받아 결과 HTML에서 글 번호를 뽑고 모바일 주소로 바꾼다 (`dcsearch.py`, `dcpost.py`)
- **아카라이브·클리앙·위키독스 일부**: `https://r.jina.ai/<URL>` 프록시를 앞에 붙인다 (`arca.sh`, `clien.sh`, `jina.sh`)
- **레딧**: 크롤러를 막으므로 redlib 미러를 `r.jina.ai`로 다시 감싼다

## 넣지 않은 것

- 논문 HTML 원본 — 텍스트 추출본으로 대체
- HuggingFace 모델 목록 조회 응답 약 600건 — 근거로 쓰지 않았다
- 이 조사와 무관한 이전 작업 파일 (부하 테스트 로그, 스크린샷 등)
