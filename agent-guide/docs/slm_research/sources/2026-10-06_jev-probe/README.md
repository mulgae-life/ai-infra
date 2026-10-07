# Jev 방식 판단 실측 원본 (2026-10-06)

[`jev-probe.md`](../../topics/jev-probe.md)의 근거 자료다. 연구계에서 Qwen3.8-27B-FP8의 선택지 확률을 읽어 Jev 1.13과 비교한 실험의 스크립트, 직접 만든 한국어 업무 문항, 요약 결과를 담는다.

공개 벤치마크 문항 원문과 문항별 원시 결과는 넣지 않았다. 라이선스(KorMedMCQA CC BY-NC, Belebele CC BY-SA 등)와 문항 공개 금지 조건(GPQA·HLE) 때문이다. 작업 디렉터리 전체(문항별 결과, 로그, 외부 저장소 클론, Decision Index 재구성본)는 `/workspace/tmp/jev-lab/`에서 레포의 `.archive/2026-10-06_jev-probe/`(git 미추적)로 옮겼다. 스크립트의 절대 경로는 옮기기 전의 `/workspace/tmp/jev-lab/` 기준이다.

## 디렉터리

| 경로 | 내용 |
|------|------|
| `data/ko-biz/` | 직접 만든 한국어 업무 판단 문항 600개(6분야 × 100)와 작성 규격 `SPEC.md`. 인물·회사·번호는 모두 가상이다 |
| `data/ko-biz/review/` | 정답을 가린 블라인드 검수 답(분야별 JSONL)과 이의 문항 목록 `flagged.json` |
| `lab/` | 실험 엔진, 측정 클라이언트, 분석 스크립트 |
| `results/` | 실행별 요약 JSON과 분석 출력(마크다운 표). 아래 표 참고 |

분석 스크립트는 6개 분야 파일을 이어 붙인 `all.jsonl`을 입력으로 쓴다. `cat route.jsonl voc.jsonl claim.jsonl comply.jsonl fraud.jsonl calc.jsonl > all.jsonl`로 만든다.

## results/

| 경로 | 내용 | 보고서 절 |
|------|------|------|
| `suites/vs-jev.md` | 영어 판단 벤치 19종과 Jev 1.13 비교표 (`compare_suites.py` 출력) | 2장 |
| `suites/<실행>/by-project.md` | simple-jev 평가 도구의 벤치별 점수. `quick-validate`는 실험 엔진 검증(446/477) | 1.2절, 2장 |
| `korean/lab-vs-jev.md` | 한국어 공개 벤치 실험 엔진 대 Jev, 과제·조건별 McNemar·Brier·보정 오차 | 3.1절 |
| `korean/chat-analysis.md`, `korean/kpub-*.summary.json` | 채팅 경로(게이트웨이, vLLM 직접)의 방식·동시성별 정확도와 지연 | 3.2절, 6.1~6.2절 |
| `kobiz/analysis.md`, `kobiz/*.summary.json` | 업무 문항 실행별 정확도, 분야·태그별, 보정, 자동 처리율, 순서 편향, 2단계 구성 | 5장 |
| `speed/length-5015.json` | 문서 길이별 지연 (캐시 없음·있음) | 6.3절 |
| `speed/bundle-*.json` | 한 문서에 질문 N개를 물을 때의 지연 | 6.3절 |
| `speed/diag-frontend-7080.json` | :7080 토큰 직접 입력 대 채팅 요청 처리량 | 6.4절 |
| `di/compare.json`, `di/sample-score.md` | Decision Index 0.2.1 표본(벤치당 약 40요청) 채점, 영역별 지수와 벤치별 점수를 Jev·simple-jev와 비교 | 4장 |
| `di/sample-di-40.summary.json` | 표본 구성(벤치별 요청 수, 원 표본의 sha256) | 4장 |

## lab/

| 파일 | 설명 |
|------|------|
| `vllm_systemone.py` | 실험 엔진. simple-jev의 프롬프트 컴파일러·응답 조립을 그대로 쓰고 모델 계산만 vLLM `AsyncLLM`(`logprob_token_ids`)으로 바꾼 SystemOne 호환 서버(`/v1/classifier`, `/v1/systemone`). GPU 3, TP1 |
| `chat_probe.py` | 채팅 경로(:5015 게이트웨이, :7080 vLLM 직접) 측정. 확률 읽기(`prob`), 사고 끔 생성(`gen`), 사고 켬 생성(`think`)과 선택지 순서·기호 형식·시스템 프롬프트 변형 |
| `systemone_probe.py` | 업무 문항을 SystemOne 형식으로 실험 엔진에 보낸다 |
| `length_sweep.py`, `bundle_probe.py` | 입력 길이별 지연, 한 문서에 질문 N개를 물을 때의 지연 |
| `diag_frontend.py` | :7080 처리량 병목이 API 서버 전처리인지 가린다 (토큰 직접 입력 대 채팅 요청) |
| `compare_korean.py`, `analyze_chat_korean.py` | 한국어 공개 벤치를 Jev 문항별 원응답과 짝지어 비교 (McNemar, Brier, ECE, 지연) |
| `compare_suites.py` | simple-jev 평가 결과를 Jev 1.13 공개 결과와 벤치마크별로 맞댄다 |
| `analyze_kobiz.py`, `check_review.py` | 업무 문항 분석(분야·난이도·태그, 보정, 자동 처리율, 순서 편향, 합치기, 2단계 구성), 블라인드 검수 대조 |
| `di_cut_v2.py`, `di_sample_cap.py` | Decision Index 0.2.1 재구성(HLE 제외) 절단과 벤치마크별 표본 상한 |
| `di_score_sample.py` | 표본 행만 담은 채점용 묶음을 만들어 공식 코드로 채점하고, Jev·simple-jev 순위표 값을 같은 공식으로 HLE 없이 다시 합산해 맞댄다 |
| `run_*.sh` | 실행 순서 기록. 지연 측정끼리 겹치지 않게 대기열로 묶었다. 2단계 구성 실측(`think-5015-c1-lt09`)은 대기열 밖에서 따로 돌렸다. 입력은 `prob-5015-c1`의 확신도가 0.9 미만인 136문항(검수 이의 4문항 제외)을 `all.jsonl`에서 뽑은 것이다 |

## 재현에 쓴 외부 저장소

| 저장소 | 리비전 | 용도 |
|--------|--------|------|
| `featherless-ai/simple-jev` | `9c11582` (2026-10-03) | 프롬프트 컴파일러, 평가 도구, Jev 1.13 공개 결과(`eval/benchmarks/jev-1.13/2026-09-20/`) |
| `mahlernim/jev-korean-benchmark` | `2c983b7` (2026-09-17) | 한국어 공개 벤치 800문항과 Jev 문항별 원응답·지연(`results/responses.jsonl`) |
| `apolinario/decision-index` | `87d4650` (2026-09-27) | Decision Index 0.2.1 문항 재구성과 채점 |
