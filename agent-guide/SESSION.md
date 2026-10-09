---
name: session
description: ai-infra 레포 현재 상태. 세션 시작 시 다음 작업과 최근 변경 파악용.
last-updated: 2026-10-10 (게이트웨이 추론 규칙, vLLM 0.31 P5 문서·휠 정리, 부하 시험 답변 점검)
---

# 세션 상태

> 세션 시작 시 현재 상태를 빠르게 파악하기 위한 문서. 갱신은 세션 종료 시. 이력은 색인이라 상세는 `git log`와 커밋 diff에 있다. 압축 전 전문은 `git show cef33a0:agent-guide/SESSION.md`.

---

## 작업 관리

| 항목 | 내용 |
|------|------|
| **이슈 트래커** | 별도 도구 없음 (git history + 본 SESSION.md "다음 작업" 표) |
| **원격 레포** | `https://github.com/mulgae-life/ai-infra.git` (`origin/main`) |
| **배포 채널** | `aws/start.sh push`·`llm-serving/start.sh push` (S3 전체 교체) → 대상 서버에서 `./start.sh pull` |

---

## 다음 작업

| 우선순위 | 작업 | 상태 |
|---------|------|------|
| P1 | **vLLM 0.31 버전업**: 계획서 `agent-guide/plans/work-plan_261008_vllm-upgrade/`(P0~P1 ✅, P2~P3 🟡). 시험장 pip 0.31 A/B·MTP 끔 2시간 부하 통과(판정표 `llm-serving/vllm/tests/results/vllm-0.31-ab.md`). env 원본(`.env.prd`·`.env.dev`)과 인스턴스 설정 6개는 0.31 기준으로 맞췄다. 연구계 :5015 Qwen도 0.31 가상환경으로 서빙(10-09). 서버 절차는 `aws/SETUP_GUIDE.md` §4-3. 다음은 대표님이 개발 서버에서 §4-3대로 빌드·기동(첫 빌드 출력이 이미지 기준) → 결과 공유 → P4 운영 반영. P5 문서·휠 정리는 10-10 앞당겨 마침. 잔존: 연쇄 4판 자동 판정 두 경로, 재사용 전 실패 주입 모의 | P3 이미지 확인 대기 |
| P1 | **온프레미스 H200 셋업 (`on-prem/`)**: 골격 `f9c1012`. 잔존 ① 설치팀 회신(HGX/PCIe, `VOLUME_DEVICE`, RAM) ② 실서버 `setup-host.sh` 첫 실행 ③ RHEL Docker가 `apparmor=unconfined`를 무시하는지 ④ §5-3 pip 오프라인 실측 ⑤ `start.sh check`가 들여쓰인 drafter 경로를 검사하지 못함(수정 여부 대표님 결정) | 골격 ✅, 실서버 대기 |
| P1 | **운영계 반영 (`gemma-4` 별칭·정체성 프롬프트 + 31B 전환)**: 31B 본체(10-09 MTP 끔 결정으로 `-assistant` drafter는 지금 불필요)를 S3로 먼저 반입 → `push` → 운영계 `pull` → 인스턴스·게이트웨이 **둘 다** 재기동(별칭·fingerprint는 인스턴스 재기동이 있어야 반영). 기동 로그 `Maximum concurrency`와 preempt 경고로 `max_num_seqs: 20`을 판정. 옛 `vllm/slm_research/`는 이 `pull --delete`가 지운다 | 연구계 ✅, 운영계 대기 |
| P1 | **:5015 게이트웨이 프로파일 (26B 기준)**: gemma-26b fp8_per_tensor·TP2·gmu 0.9·max_len 65536, overload 20/40. 잔존: 장문 트래픽 latency·429 비율 측정. :5015 뒤에는 `gateway_port: 5015`인 인스턴스가 붙는다(10-07 현재 qwen) | 장문 검증 잔존 |
| P1 | **MTP 벤치**: Gemma·Qwen 인스턴스 모두 MTP 끔(Qwen 10-08, Gemma 10-09 — 연구계 Gemma 포함). 다시 켜는 조건은 #46088 수정 확인. 31B·Qwen 27B·26B-A4B 실기동 확인(Qwen은 08-18부터 :5015 경로, 10-07 기동 확인). 잔존: acceptance/TPOT 사내 벤치(`agent-guide/docs/slm_research/topics/mtp.md` §5) | 벤치 잔존 |
| P1 | **모델 간 속도 매트릭스**: `./start.sh speed [name\|all]`. 26B-A4B 6행 확보. 잔존: 31B·Qwen 풀 매트릭스로 3모델 비교 | 부분 완료 |
| P1 | `llm-serving/sglang/` 디렉토리 골격 (운영 가이드 + 런처 + 설정 + 테스트) | Todo |
| P1 | **STT 한국어 실측**: Whisper-large-v3 1순위(+한국어 fine-tune 트랙) 채택. `test_stt.py`(WER/RTF/정성)로 실측 확정 | 의사결정 ✅, 실측 대기 |
| P2 | **Jev 방식 후속**: 결과 `agent-guide/docs/slm_research/topics/jev-probe.md`(정확도는 같은 수준, 처리량이 초당 6~9건에서 막힘). ① TP1 A/B(서빙 설정 변경이라 대표님 결정) ② 업무 문항 600개를 Jev API로 풀기(외부 전송이라 대표님 확인) | 실측 ✅, 후속 결정 대기 |
| P2 | **보험 임베딩 파인튜닝**: 실행 계획서 `agent-guide/plans/work-plan_261008_insurance-embedding/`(P0~P6, 결정 5건은 master "결정 요청" 표), 실행 공간 `ai-research/insurance-embedding/`. 다음은 계획서 확정 → P0 결정 요청서. 라이브러리 최신화 때 학습 환경은 서빙과 분리(vLLM 0.31.0이 torch 2.13.0 고정) | 계획 초안 ✅, 대표님 검토 대기 |
| P2 | **26B-A4B MTP 튜닝**: acceptance 32~47%(31B 70~85%). 동시성 4+ 실측 후 낮으면 `num_speculative_tokens 4→2` 또는 MTP off A/B. 10-09 MTP를 껐으므로 다시 켤 때 한다 | 보류 |
| P2 | **PII NER 고도화 (보류, PII 미사용 중)**: 재사용 전 필수 🚨 512 토큰 초과 청킹(현재 500 → fail-open 무검사/fail-closed 차단) · 마이크로 배칭 · replica 스케일아웃 | 보류 |
| P2 | **PII 가드 운영 적용 (보류)**: 운영계 :5501 실기동 · 실데이터 recall 게이트 · 스트리밍 progressive buffer · 이미지 OCR PII · `PII_AUDIT_SALT` 확인. 설계 `agent-guide/plans/pii-dlp-gateway.md` | 보류 |
| P2 | **비PII qwen 대칭 보강**: qwen은 PII 경유(6502)만 존재. 필요 시 인스턴스(gw 5502) + `gateways/5502.yaml` 추가. **대표님 답변 대기** | Todo |
| P2 | **`prd-gemma` vLLM host 정리**: `host: 0.0.0.0`이라 :7070 외부 노출. 방화벽 7070 차단 확인 또는 127.0.0.1 통일 | Todo |
| P2 | **STT 동시 N 세션 전환**: voxtral gmu 0.35→0.40~0.50, max_num_seqs 1→2~4 + 게이트웨이 overload 동기 상향. 동시 stream 목표 결정 후 | Todo |
| P2 | **운영계 STT 의존성 반영**: `aws/requirements.txt`의 `soundfile/soxr/librosa` 재배포 + Voxtral 17GB S3 경유 `/models/STT/` 동기화 | Todo |
| P2 | **RTX PRO 6000 이전 후 fused MoE 튜닝**: `benchmark_moe.py`로 config json 생성 → site-packages 배치. 트리거: 운영 환경 셋업 완료 | Todo |
| P2 | **wrapper/logging.sh 가이드 보강**: STT/VLLM OPS 가이드에 본체/wrapper 구조 + `logging.sh` S3 카운트 sync 섹션 | Todo |
| P3 | `agent-guide/` MCP 도구 섹션 채우기 | Todo |

---

## 최근 세션

| 날짜 | 한 일 |
|------|------|
| **10-10** | 인스턴스 0.31 정렬·연구계 0.31 전환 `a7cf66c` · 게이트웨이 추론 규칙 변경 `0eee4cb`(대표님 결정): 기본 꺼짐, effort를 주면 켜짐, `enable_thinking` 직접 지정이 우선, `none`은 끔. 게이트웨이가 `enable_thinking`을 명시해 버전과 무관. Qwen(:5015)·Gemma 31B(시험장)에서 조합 시험 통과. `start.sh test`에 게이트웨이 계약 카테고리를 추가하고 사고 꺼짐 판정이 `reasoning` 필드도 보게 함(옛 판정은 켜진 사고를 놓침). 버전업 때 "effort는 강도만"으로 막아 둔 것은 하위 호환을 위한 내 판단이었고 대표님이 뒤집음 · P5 정리를 운영 반영 전에 앞당김: 운영 가이드 알려진 이슈 표를 상류 상태·우리 시험으로 다시 쓰고(MTP 이슈 4건 추가), STT 문서에 0.31 미시험과 연구계 가상환경의 STT 의존성 부재를 적음, nightly 휠을 `.archive/2026-10-10_vllm-nightly-wheel/`로 이동 · 부하 시험 도구가 답 없이 끝난 HTTP 200을 성공으로 세던 것을 고침: 종료 사유와 답변 글자 수를 보고 상한 도달은 경고, 상한 아닌 빈 답은 실패로 판정. 원인은 사고 켬 질문의 "약 250자" 지시라 모델이 글자를 세다 상한에 걸린 것이었고(처음 짚은 temperature 0 반복은 틀림), 질문을 계산·일정표 문제로 바꿔 Qwen·Gemma 31B 각 40건 모두 정상 종료 |
| **10-09** | vLLM 0.31 P2·P3 — `aws/` 정식 이미지 전환(nightly 휠 제거, 베이스 조합 제약)과 게이트웨이 effort를 템플릿 인자로 `bbaae21` · A/B 시험 도구 5종·판정표 `f40fdfc` · 운영 Gemma MTP 끔(결정 ⑨) `89d4899` · 이미지 확인 스크립트로 계획서 ④·⑥ 결함 3건 수정 · SSH 세션 한글 로케일 `44722eb`. 서버에서 빌드·`user.sh up`만으로 0.31이 뜨도록 env 4개(이미지 다이제스트, `EXTRA_REQUIREMENTS` 비움)·빌드 버전 확인·진입점 제약·`aws/SETUP_GUIDE.md` 버전업 절차(지금 §4-3) `2ba83cb` · `aws/SETUP_GUIDE.md` 구조 개편(상황별 바로가기, 포트 할당 설명과 버전업 확인 명령 2건 정정) `ce56d2c` · 인스턴스 설정 0.31 정렬: Gemma 4개 `fp8_per_tensor`(시험장 31B 기동·기능 31/31), 연구계 Gemma MTP 끔, `prd-pii-qwen` → Qwen3.8(결정 ⑥), `_SCHEMA.txt` 0.31 줄 번호. 연구계 Gemma `fp8` 유지 계획은 서버 :5015가 0.31로 띄우므로 뒤집음. 연구계 컨테이너도 0.31 전환: 가상환경 `~/venvs/vllm-0.31`(시험장과 206개 버전 일치) + 런처 `SERVING_VLLM_BIN`, :5015 Qwen 재기동. `~/.local` nightly는 임베딩 :8020용으로 유지. 10-07에 띄운 :5015 게이트웨이가 effort 수정 전 코드라 effort만 보내도 추론이 켜져(4/18 불일치) 게이트웨이도 재기동, 재시험 18/18 일치. 협업·도구 원본 `.archive/2026-10-09_vllm-upgrade-p3/`. 공백 반복을 "모델 습관"이라 한 것은 원인 미분리라 "공통 출력 이상"으로 정정 |
| **10-08** | vLLM 0.31 계획서 `db11b7e` · Qwen MTP 끔 `1d097b7` · 정체성 문구 기본값 비공개 `de23caf` · 시험장 0.31 예행 설치(P1) · `ai-research/` 연구·실험 레이어 신설 + 보험 임베딩 골격 `00085cf` · 보험 임베딩 실행 계획서 초안 v2 `efa102c`. 코덱스와 4라운드 합의, 협업 원본은 `.archive/2026-10-08_insurance-ft-plan-collab/`. 하드 네거티브 채굴을 E1 앞에 두려던 안은 설계 7.1절과 어긋나 E2 준비로 옮김 |
| **10-07** | 레포명 `docker` → `ai-infra`(GitHub, 로컬 경로, 레포 안 표기. Docker 도구명과 `my-docker-server/`는 유지) `c009f48` · 점검 중 찾은 기존 안내 오류 2건 정정 `cef33a0` · 연구계 qwen·:5015를 새 경로에서 재기동. GUIDE의 "서빙은 net/PID 네임스페이스 밖"은 틀려서 정정(이 컨테이너 안에서 돈다). 로컬 PC도 `/workspace/ai-infra`로 옮기고 `ssh-guard.service` 재복사 + `daemon-reload` 완료(설치본 = 레포본) · `agent-guide/docs/embedding_research/` 신설 + 대표님 임베딩 조사 문서를 원문과 대조해 4건 정정 `9352b21` · 보험 임베딩 파인튜닝 조사 `ccb18ed`. 코덱스와 4라운드 교차 검증, 원본 HTML·PDF와 협업 메모는 `.archive/2026-10-07_insurance-ft-collab/` |
| **10-06** | Jev 조사 + `slm_research/`를 `models/`·`topics/`·`sources/`로 개편 `5557317` · `slm_research/`를 `agent-guide/docs/`로 옮겨 배포 범위 밖에 두고 `start.sh` 제외 규칙 삭제 `11d7420` · Jev 방식 실측(Qwen3.8 FP8 대 Jev) `6f9550b` |
| **09-15** | 운영 배포분 주석 어조 정리 + `slm_research/` S3 제외 `298b04c`. 보안 검토 범위는 GitHub 공개 여부가 아니라 운영 서버로 가는 것(대표님 확정) · 정체성 프롬프트는 유지 · `on-prem/`은 `aws/`보다 뒤처지지 않음 |
| **09-14** | 데탑 컨테이너 재생성 전 수동 설치 도구를 Dockerfile에 고정 `c3a6976` · SSH 호스트 키 영속화 `d436e87` · `my-docker-server/README` → `SETUP_GUIDE.md` `6ffb11d`. 잔존: 휴대폰을 Tailscale로 옮기면 공유기 5000/5010 포워딩을 닫을 수 있음, 컨테이너 `btmp`는 수동 truncate |
| **09-11** | 데탑 SSH 간헐 거절(공인 포트 브루트포스가 `MaxStartups` 점유) 대응 — sshd 강화 + `DOCKER-USER` rate-limit `ssh-guard` `b3fa543`. 첫 임계값 15/60s는 봇이 바로 아래에 머물러 무효라 20/600s로 바꿈 |
| **09-04** | `prd-gemma` 26B-A4B → 31B 덴스 + gemma 4종 gmu 0.9·max_len 65536 정합 `474b890`(`prd-pii-gemma`의 옛 gmu 0.8 근거는 못 찾음) · `aws s3 sync`가 크기·시각만 비교해 갱신분을 건너뛰던 것을 `pull --exact-timestamps`로 해결 `37782ce` |
| **08-28** | `on-prem/` 신설 — RHEL 10 H200 호스트 셋업 + 폐쇄망 준비 점검 `f9c1012` |

## 이전 세션 (압축)

| 기간 | 요약 |
|------|------|
| 08-18~20 | Qwen3.8-27B-FP8 교체 `5a8fd1b` · 멀티모달 프리필 OOM 대응 `d2a3af8`·`b068ab9` · 한국어 비교·Qwen3.8 조사 `6e5848d`·`a01b97b` · API 모델명 `gemma-4` 고정 + 호환 계층 `9c7597a` · 정체성 프롬프트 주입 + fingerprint 고정 `00a48c7`. system 메시지를 맨 앞에 새로 끼우면 Qwen 템플릿이 400을 내서 기존 system에 병합하는 방식으로 바꿈 |
| 08-10 | `start.sh` QA 명령 3종 + S3 배포 진입점을 `start.sh`로 통일 + `aws/.env` 환경별 원본 분리 `5c77f3d`·`0db5427`·`0d2d82e`. `push --dryrun`이 삭제(`aws s3 rm`)는 실제로 실행할 뻔해 `--dryrun`을 삭제에도 전달 |
| 07-21~22 | 전 서빙 절단 복구 + Gemma 26B-A4B 전환 + `download` 명령 + `${model}-assistant` 치환 + NER 스레드풀 `c78b259`~`5fe1d5d` · 가이드 문서 정합, STT 포트 정정, 연구계 IP 변경 `f55374d`·`a22b71f` |
| 06-05~09 | PII/DLP 토폴로지 적용(프록시가 :5015 인수) `295ce8c` · PII 우회 차단·스트리밍 fail-closed `b1e33a6`·`1270baa`·`eaeecb6` · 한국어 PII 모델 재조사(현 구성 유지) `3c23160` · yaml 주석 슬림화 + `_SCHEMA.txt` 분리 `de734ce` |
| 05-12~27 | MTP 도입 · STT 의사결정(Whisper-large-v3 1순위), wrapper화, 단일 게이트웨이 5017 · Gemma 31B 실기동(TP2) + `tests/`·`speed_test.py` · `user.sh --extra-ports` · `start.sh logs` |
| 04-29~05-04 | 레포 3-디렉토리 재편 + agent-guide 초기화 · 게이트웨이 자동 디스커버리, `start.sh` 견고성, code-server 제거 · `AdmissionController`(429) + STT Voxtral 페어 |
