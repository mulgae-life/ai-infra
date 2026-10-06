---
name: session
description: docker 레포 현재 상태. 세션 시작 시 다음 작업과 최근 변경 파악용.
last-updated: 2026-09-15 (llm-serving 배포 범위 주석 정리 + `slm_research/` S3 제외 — 운영 서버로 가는 코드·문서 기준)
---

# 세션 상태

> 세션 시작 시 현재 상태를 빠르게 파악하기 위한 문서. 갱신은 세션 종료 시. 과거 세션 상세가 필요하면 `git log`와 해당 커밋 diff를 참조.

---

## 작업 관리

| 항목 | 내용 |
|------|------|
| **이슈 트래커** | 별도 도구 없음 (git history + 본 SESSION.md "다음 작업" 표) |
| **원격 레포** | `git@github.com:mulgae-life/docker.git` (`origin/main`) |
| **배포 채널** | `aws/start.sh push`·`llm-serving/start.sh push` (S3 전체 교체) → 대상 서버에서 `./start.sh pull` |

---

## 다음 작업

| 우선순위 | 작업 | 상태 |
|---------|------|------|
| P1 | **온프레미스 H200 서버 셋업 (`on-prem/`)**: 8/28 골격 신설 — `setup-host.sh`(RHEL 10, 드라이버 580.178.04 LTSB 고정 + versionlock, Docker CE, Fabric Manager는 `/dev/nvidia-nvswitch*`로 판단, 베이스 이미지 사전 pull), `start.sh check`(폐쇄망 준비 점검), `.env.prd`(H200 8장 기준, git 미추적). 컨테이너 계층은 `aws/` 공유. 잔존: ① 설치팀 회신 대기 — HGX/PCIe 구성, 데이터 NVMe 경로(`VOLUME_DEVICE`), RAM ② 실서버에서 `setup-host.sh` 최초 실행 검증(문법·`check` 로직만 연구계에서 확인, RHEL 실기동 미검증) ③ `docker-compose.yml`의 `apparmor=unconfined`가 RHEL Docker에서 무시되는지 확인 ④ 5-3 pip 오프라인 절차 실측 ⑤ `start.sh check`의 `_yaml_top_value`가 최상위 키만 읽어 들여쓰인 `speculative_config.model`(drafter `${model}-assistant`)을 검사하지 못한다 — 폐쇄망에서 drafter 누락을 기동 전에 못 잡는다(9/15 확인, 수정 여부 대표님 결정 대기). | 골격 ✅, 실서버 검증 대기 |
| P1 | **`gemma-4` 별칭 + 정체성 프롬프트 운영계 반영**: 8/20 연구계 적용·검증 완료. 잔존 — `./start.sh push` 후 운영계에서 인스턴스·게이트웨이 **둘 다** 재기동. 게이트웨이 재기동만으로 걸리는 것은 호환 계층과 정체성 주입(코드 기본값 on)이고, 별칭과 `fingerprint_mode: custom`은 **인스턴스 재기동이 있어야** 반영된다. 클라이언트 `.env`(`CHAT_MODEL` 등)는 `VLLM_OPS_GUIDE.md` §9.4 참고. 같은 `push`로 S3의 `slm_research/` 182개 객체가 지워지지만 운영 서버에 이미 내려간 사본은 제외 경로라 `pull --delete`가 안 지운다 — `pull` 후 `vllm/slm_research/`를 한 번 직접 정리할 것. | 연구계 ✅, 운영계 대기 |
| P1 | **운영계 31B 전환 반영**: 9/4 `prd-gemma`를 26B-A4B → 31B 덴스로 교체(yaml만). 잔존 — ① 운영계 `/models/LLM/google/`에 `gemma-4-31B-it` **본체와 `-assistant` drafter 둘 다** 확보(폐쇄망이라 S3 경유, `${model}-assistant` 치환이라 yaml 수정은 불필요) ② `./start.sh push` → 운영계 `pull` → 인스턴스·게이트웨이 재기동(바로 위 별칭 반영과 같은 재기동에 묶인다) ③ 기동 로그의 `GPU KV cache size`·`Maximum concurrency` 확인 — 31B는 토큰당 KV가 26B의 4배라 `max_num_seqs: 20`이 실효하는지는 이 값으로만 판정된다 ④ 부하 시 `PreemptionMode.RECOMPUTE` 경고가 뜨면 `max_num_seqs`와 게이트웨이 `max_inflight_requests`를 함께 하향. | yaml ✅, 운영계 대기 |
| P1 | **:5015 운영 프로파일 (26B 기준)**: 2026-07-21부터 :5015 = 비PII 직접 게이트웨이 + gemma-26b(fp8·TP2·gmu 0.9·max_len 65536 — `5a8fd1b`에서 32768→65536, overload 20/40). 잔존: 장문 트래픽 기준 latency·429 비율 측정. | 갱신(모델 교체), 장문 검증 잔존 |
| P1 | **MTP 실기동 검증 (31B/26B/Qwen)**: 31B·Qwen 27B(5/13) + 26B-A4B(7/21, QA 통과) 실기동 확인. 잔존: ① Qwen 5016 재기동·가용성 ② acceptance/TPOT 사내 벤치(`slm_research/topics/mtp.md` §5 참고). | 부분 완료, 벤치 잔존 |
| P1 | **모델 간 속도 매트릭스**: `./start.sh speed [name\|all]` (8/10 진입점 신설 — 무인자면 기동된 게이트웨이를 순회하며 같은 파일에 누적). 26B-A4B 6행 확보(c=1 TPS 168.5 / c=10 TPS 81 — 31B quick 64.8 대비 단발 약 2.6배). 잔존: 31B·Qwen 풀 매트릭스로 3모델 비교 완성. | 부분 완료(26B 측정) |
| P1 | `llm-serving/sglang/` 디렉토리 골격 (운영 가이드 + 런처 + 설정 + 테스트) | Todo |
| P1 | **STT 한국어 정성 비교 (PoC 잔여)**: 시나리오 E(정확도+offline) 채택 완료 — 1순위 Whisper-large-v3(+한국어 fine-tune 트랙). `test_stt.py`(WER/RTF/정성) 작성으로 실측 확정. | 의사결정 ✅, 실측 대기 |
| P2 | **26B-A4B MTP 튜닝**: acceptance 32~47%(31B 70~85% 대비 낮음 — MoE 저동시성 특성). 동시성 4+ 실측 후 낮으면 `num_speculative_tokens 4→2` 또는 MTP off A/B. | 신규 (2026-07-21) |
| P2 | **PII NER 후속 고도화 (대표님 지시로 보류)**: 현재 연구·운영 모두 PII 미사용(비PII vllm만 운영). 재사용 전 필수 — ① **🚨 512 토큰 초과 청킹**(현재 긴 텍스트 500 에러 → fail-open 무검사 통과/fail-closed 차단. overlap 청킹 + 회귀 테스트) ② 마이크로 배칭 ③ replica 스케일아웃(`configs/ner.yaml` backends 복제, LB 기지원). 동시성 1차(스레드풀+세마포어)는 7/21 완료. | 신규 (후속 대기) |
| P2 | **PII 가드 운영 적용 후속 (보류)**: 잔존 — 운영계 :5501 실기동(설정 준비 완료) · 보험 실데이터 recall 게이트 실측(`recall_gate.py` 하버스 준비, 라벨 JSONL 대기) · 스트리밍 progressive buffer(별도 합의) · 이미지 OCR PII · 배포 시 `PII_AUDIT_SALT` 확인. 설계: `agent-guide/plans/pii-dlp-gateway.md`. | 보류(PII 미사용 중) |
| P2 | **비PII qwen 대칭 보강**: qwen은 PII 경유(6502)만 존재. 필요 시 인스턴스(gw 5502) + `gateways/5502.yaml`(0.0.0.0) 추가로 gemma와 대칭. **대표님 답변 대기.** | Todo |
| P2 | **`prd-gemma`(비PII) vLLM host 정리**: `host: 0.0.0.0`이라 vLLM :7070 외부 노출(`prd-pii-gemma`는 127.0.0.1). 방화벽 7070 차단 확인 또는 127.0.0.1 통일. | Todo |
| P2 | **STT 동시 N 세션 전환**: voxtral gmu 0.35→0.40~0.50, max_num_seqs 1→2~4 + 게이트웨이 overload 동기 상향. 동시 stream 목표 결정 후. | Todo |
| P2 | **운영계 STT 의존성 반영**: `aws/requirements.txt`의 `soundfile/soxr/librosa` 재배포 + Voxtral 17GB S3 경유 `/models/STT/` 동기화(폐쇄망 대비). | Todo |
| P2 | **RTX PRO 6000 Blackwell 이전 후 fused MoE 튜닝**: `benchmark_moe.py`로 config json 생성 → site-packages 배치. 트리거: 운영 환경 셋업 완료. | Todo |
| P2 | **wrapper/logging.sh 가이드 보강**: STT/VLLM OPS 가이드에 본체/wrapper 구조 + `logging.sh` S3 카운트 sync 섹션. | Todo |
| P3 | `agent-guide/` MCP 도구 섹션 채우기 | Todo |

---

## 기타 이슈

- ~~5015 라이브 overload 값과 로컬 yaml 불일치~~ → 7/13 전 서빙 다운 + 재기동으로 해소(현재 라이브 = yaml 기준). Qwen :7080 이전 건도 같은 이유로 자연 해소.

---

## 최근 세션

### 2026-09-15 (on-prem 대조 + llm-serving 배포 범위 주석 정리 + `slm_research/` S3 제외)

#### 세션 목표
- `aws/` EC2 구성을 온프레미스에 그대로 쓸 수 있는지, `on-prem/`이 `aws/`보다 뒤처졌는지 대조
- 운영 서버로 배포되는 소스·설정·문서의 주석 중 보안 담당자가 의심할 만한 어조를 정리
- 운영 서버에 갈 이유가 없는 연구 자료가 배포 범위에 섞여 있는지 확인

#### 변경 파일

| 파일 | 변경 유형 | 요약 |
|------|----------|------|
| `llm-serving/start.sh` | 설정 | `SYNC_EXCLUDES`에 `*/slm_research/*` 추가 |
| `llm-serving/DEPLOY_GUIDE.md` | 문서 | 제외 목록 설명에 `slm_research/` 사유 반영 |
| `llm-serving/VLLM_OPS_GUIDE.md` | 문서 | §10.4·§10.5·§11 측정 안내의 주석 어조 재작성 |
| `llm-serving/vllm/instances/*.yaml` (6) | 설정 | `served_model_name`·`fingerprint_*` 주석 재작성 |
| `llm-serving/vllm/gateways/*.yaml` (6) | 설정 | `mask_model_path`·`inject_identity_prompt` 주석 재작성 |
| `llm-serving/vllm/{instances,gateways}/_SCHEMA.txt` | 문서 | 같은 키 설명 재작성 |
| `llm-serving/vllm/vllm_gateway.py` | 코드 | 모듈 독스트링 토폴로지 실측 정정(5015→7080 연구계 / 5501→7070 운영계), compat 주석·기동 로그 문구 재작성 |
| `llm-serving/vllm/start.sh` | 코드 | 없는 게이트웨이 `5016` 예시를 `5501`로, 사라진 줄번호 참조 제거 |
| `llm-serving/vllm/tests/*.py`, `tests/results/speed_results.md` | 코드·문서 | 옛 포트·경로·테스트 번호 정정, "실모델" 표기를 "체크포인트"로 통일 |

#### 결정 사항
- **보안 검토 범위는 운영 서버로 가는 것**(`llm-serving/start.sh push` → S3 → 운영계 `pull`)이라고 대표님이 확정. GitHub 공개 여부를 기준으로 삼던 초기 판단은 폐기했다. `/workspace/docker`의 연구계 전용 자료는 대상이 아니다.
- **정체성 프롬프트(`_DEFAULT_IDENTITY_PROMPT`)는 손대지 않는다.** 서빙 모델의 정상적인 시스템 프롬프트 지침이라는 대표님 지적을 받아들였다.
- **주석 재작성 원칙**: "누구에게 안 보이게 한다"가 아니라 "무엇을 어떤 값으로 고정하고, 그래서 클라이언트가 무엇을 안 바꿔도 되는가"로 쓴다. 기능과 동작 설명은 그대로 두고 어조만 바꿨으므로 동작 변경은 없다.
- **`slm_research/`는 배포 제외.** S3에 182개 객체(10,075,140바이트)가 실제로 올라가 있어 운영계가 `pull`하면 그대로 내려간다. 모델 조사 문서와 커뮤니티 수집 원본이라 서빙에 쓰이지 않는다.

#### `on-prem/` 대조 결과
`on-prem/`은 `aws/`보다 뒤처지지 않았다. 컨테이너 계층(`docker-compose.yml`·`Dockerfile.llm`·`entrypoint-llm.sh`·`user.sh`·`wheels/`)은 공유하고, 갈라지는 것은 호스트 셋업(`setup-ec2.sh` ↔ `setup-host.sh`)과 코드 전달 방식(S3 `start.sh` ↔ `git pull` + `check`)뿐이다. `.env` 키도 정합하다. 유일한 구멍은 `on-prem/start.sh check`의 `_yaml_top_value`가 최상위 키만 읽어 들여쓰인 `speculative_config.model`(drafter `${model}-assistant`)을 검사하지 못하는 것인데, 제안만 하고 손대지 않았다.

#### 현재 상태
완료. 검증은 `bash -n`(배포·서비스 진입점 2종), `py_compile`(게이트웨이 + 테스트 3종), YAML 파싱(인스턴스·게이트웨이 12종) 전부 통과. 주석 안의 포트·경로·테스트 번호는 실제 yaml과 테스트 함수로 대조했다. `push --dryrun`에서 `slm_research/` 업로드 대상 0건, 삭제 단계 182건(기존 S3 객체)을 확인했고 S3에는 손대지 않았다.

> ⚠️ **운영 서버 수동 정리 필요**: 다음 `push`로 S3의 `slm_research/` 182개 객체는 지워지지만, 제외 경로는 `pull --delete`에서도 보호되므로 운영 서버에 이미 내려간 `vllm/slm_research/`는 남는다. `pull` 후 한 번 직접 지워야 한다.

### 2026-09-14 (my-docker-server 데탑 컨테이너 재생성 + 수동 설치 도구 이미지 고정)

- **배경**: 9/11 잔존 ①(compose 프로젝트 전환)과 sshd 강화 설정 실적용을 위해 데탑 재부팅 후 cfd·dev-fullstack을 재생성. 재생성은 writable layer를 버리므로, 컨테이너 안에서 손으로 깔아 쓰던 도구를 먼저 Dockerfile에 옮겨야 했다.
- **조사 방법**: `docker diff` + `apt-mark showmanual`(베이스 이미지와 대조) + bash history로 후설치 목록 추출. `/etc` 변경·`/usr/local/bin`·시스템 pip·crontab은 없음 확인. TinyTeX(`~/.TinyTeX`)와 Antigravity CLI는 홈(바인드 마운트)에 있어 보존.
- **변경**:
  - `Dockerfile.gpu`: 추가 도구 블록 — `ffmpeg imagemagick librsvg2-bin pandoc latexdiff poppler-utils qpdf fonts-nanum fonts-noto-cjk nvtop zip unzip` + `npm install -g @google/gemini-cli`. 한글 폰트는 pandoc·ImageMagick 출력 깨짐 방지로 dev와 맞춤.
  - `Dockerfile.dev`: `libreoffice-writer libreoffice-impress poppler-utils libxfixes3 zip`.
  - `README.md` 포함 스택 표에 반영.
  - `my-docker-server/README.md` → **`SETUP_GUIDE.md`** 로 개명(aws/on-prem 과 같은 이름 규칙)하고 "한눈에 보기 → 사전 준비 → 설치 → 접속 → 보존/소실 → 운영 → 스택 → 브루트포스 → 문제 해결 → 커스터마이징" 순으로 재구성, 개조식으로 정리. 공개 레포라 SSH config 예시의 개인 주소는 자리표시자로. 루트 README·PROJECT.md 링크 갱신. `/work-verify` 점검으로 ImageMagick PDF 차단 서술(사실 아님 — 이 이미지는 policy에 PDF 규칙 없고 gs 포함) 정정, nvidia 문제 해결에 `nvidia-ctk runtime configure` 단계 추가, 조사 띄어쓰기를 레포 관행(`` `lsblk`로 ``)에 맞춤.
  - **SSH 호스트 키 영속화**(재생성 직후 발견한 문제의 재발 방지): 재빌드로 sshd 호스트 키가 새로 생겨 모든 클라이언트가 `known_hosts` 불일치로 접속 거부(`Connection reset ... [preauth]` 반복). compose 에 `/opt/docker-homes/<서비스>/ssh-hostkeys:/etc/ssh/hostkeys` 바인드 추가, `entrypoint.sh` 가 보관 키가 있으면 `/etc/ssh/` 로 복원하고 없으면(최초) 이미지 키를 보관. README 영속화 표에 행 추가.
- **결과**: `docker compose -p docker down` → `my-docker-server/`에서 `up -d --build`(전체 재빌드, cfd-gpu 19.1GB / dev-fullstack 7.69GB). 프로젝트 라벨 `my-docker-server`, sshd `-D -e`·`sshd -T`로 MaxStartups 30:50:100·AllowUsers hjjo 실적용 확인, uid 1000 매핑·홈·TinyTeX 정상. Node 22 → 24.21 LTS로 상승. openclaw(별도 프로젝트·네트워크)는 무영향.
- **교훈**: ① nvm 전역 npm 패키지는 `/usr/local/nvm`(이미지 계층)에 들어가므로 재생성 때 사라진다 — CLI 도구는 Dockerfile에 고정. ② 이 서버는 RTC가 KST 로컬 시간인데 시스템 TZ가 UTC라 부팅 직후 9시간 앞서 있다가 NTP로 되돌아간다 → `docker ps`에 "Up Less than a second"로 보이는 표시 문제(동작 무관). ③ 점검 에이전트의 일반론("우분투 ImageMagick은 PDF 차단")도 실제 컨테이너에서 확인 후 문서화 — 이번 이미지에서는 사실이 아니었다.
- **잔존**: ① 휴대폰(KT 공인 IP)을 Tailscale로 옮기면 공유기 5000/5010 포워딩을 닫을 수 있음. ② 컨테이너에 logrotate가 없어 `btmp`는 수동 truncate.

### 2026-09-11 (my-docker-server SSH 브루트포스 대응 + 개인 데탑 서버 체크아웃 정합)

- **배경**: 개인 데탑 서버(hjjo-desktop, cfd·dev-fullstack 운영 중)에서 VSCode Remote-SSH 접속이 간헐적으로 첫 시도에 거절되는 증상. 이 서버의 체크아웃은 4/29 재편 이전(루트 Dockerfile 구조)에 멈춰 있었다.
- **원인**: 공유기가 공인 5000/5010을 컨테이너 sshd로 포워딩하고 있어 약 36개 IP의 분산 브루트포스(신규 연결 분당 ~227회, IP당 9~14회)가 sshd `MaxStartups 10` 좌석을 5~14개로 상시 점유 → 10 초과분은 확률적으로 거절. Tailscale 경유든 공인 경유든 같은 sshd를 쓰므로 경로와 무관하게 영향. 컨테이너 `/var/log/btmp`가 13.5GB까지 자란 상태.
- **변경**:
  - `my-docker-server/sshd-hardening.conf` 신설 + 두 Dockerfile에 `COPY` → `sshd_config.d/50-hardening.conf`(MaxStartups 30:50:100, LoginGraceTime 30, MaxAuthTries 3, PerSourceMaxStartups 3) + `RUN echo "AllowUsers ${USERNAME}"`. CMD에 `-e` 추가(컨테이너에 syslog가 없어 sshd 로그가 버려지던 것을 `docker logs`로).
  - `my-docker-server/ssh-guard.sh` + `ssh-guard.service` 신설: 호스트 `DOCKER-USER` 체인에 5000/5010 규칙 — Tailscale(100.64.0.0/10)·LAN(192.168.75.0/24) RETURN, 그 외 `xt_recent` 600초 20회 초과 DROP. 멱등(`iptables -C` 후 삽입), `After=docker.service` oneshot으로 재부팅 후 자동 복구.
  - `README.md`에 "SSH 브루트포스 대응" 절, `PROJECT.md` 트리 갱신.
- **결정**:
  - **컨테이너·sshd 무중단 원칙**: cfd에서 CFD 실험(수 시간 잔여)이 돌고 있고 sshd가 PID 1이라 reload(SIGHUP)조차 재exec 실패 시 컨테이너 종료 위험 → sshd 설정은 파일만 고쳐 두고(`sshd -t` 검증) 다음 재시작 때 적용, 즉시 효과는 호스트 방화벽만으로 확보. 결과: 봇 좌석 점유 5~14 → 0, 신규 봇 연결 227/분 → 4/분.
  - **rate-limit 임계값 20/600s**: 첫 시도 15/60s는 무효였다 — 봇이 `PerSourceMaxStartups 3`에 스로틀되어 IP당 9~14/분으로 바로 아래에 머문다. 8/600s로 효과 확인 후 사용자 여유를 위해 20으로 상향(사용자는 Tailscale·LAN 경로라 어차피 RETURN).
  - **이 서버 UID는 1000 유지**: 재편 후 기본값 2000은 클라우드 계정 기준. 데탑은 호스트 계정·기존 컨테이너·`/workspace` 소유권이 모두 1000이라 `.env`에 `UID=1000`/`GID=1000` 명시(git 외).
- **정합 작업**: 이 서버에서 변경분 커밋 → `git pull --rebase`(rename 추적으로 Dockerfile 수정이 `my-docker-server/`로 이동) → 신규 3파일 `git mv` → `.env`를 `my-docker-server/`로 이동 → service `ExecStart` 경로 갱신.
- **교훈**: ① Docker 공개 포트는 호스트 `INPUT`이 아니라 `DOCKER-USER`(FORWARD)를 지나고 DNAT 이후라 `--ctorigdstport`로 원래 포트를 매칭해야 한다. ② Tailscale 경유 포워딩 트래픽은 SNAT되어 컨테이너 안에서 `172.18.0.1`로 보인다(100.x 아님). ③ `last`는 pty 세션만 기록해 VSCode(notty) 세션은 안 보인다. ④ 컨테이너 root는 CAP_SYS_PTRACE가 없어 sshd `/proc/PID/fd`를 못 읽는다.
- **잔존**: ① 데탑 컨테이너 compose 프로젝트 전환 → 9/14 완료. ② 휴대폰 터미널(KT 공인 IP)을 Tailscale로 옮기면 공유기 5000/5010 포워딩을 닫을 수 있음. ③ 컨테이너에 logrotate가 없어 `btmp`는 수동 truncate(9/11 비움).

### 2026-09-04 (운영계 gemma 31B 덴스 전환 + 파라미터 정합 + S3 `pull` 정합성)

- **목표**: `prd-gemma`의 백엔드를 26B-A4B(MoE)에서 31B 덴스로 교체하고, 같은 모델을 쓰는 나머지 gemma 인스턴스의 메모리·컨텍스트 값을 하나로 맞춘다.
- **변경**: `instances/prd-gemma.yaml`(model 26B-A4B → 31B) · `instances/gemma.yaml`(gmu 0.95 → 0.9, max_model_len 32768 → 65536) · `instances/prd-pii-gemma.yaml`(gmu 0.8 → 0.9, max_model_len 32768 → 65536) · `SESSION.md`
- **결정**:
  - **정합 기준은 `prd-gemma`, 근거는 `qwen.yaml`** — 같은 연구계 L40S TP2에서 8/18 OOM 대응으로 조정된 그 파일이 `gmu 0.9` + `max_model_len 65536`이다. 두 값 모두 이미 실증된 조합이라 여기에 맞췄다.
  - **`gemma.yaml`의 0.95는 8/18 OOM 대응 누락분**이었다. 같은 GPU 구성에서 Qwen3.8(`intermediate_size` 17,408)이 0.93으로 죽었는데, `intermediate_size`가 21,504로 더 큰 31B가 더 높은 0.95를 쓰고 있었다. 정합 이전에 안전 문제라 함께 내렸다.
  - **`host: 127.0.0.1`은 정합 대상에서 제외** — `prd-pii-gemma`는 PII 프록시 뒤라 vLLM 직행 우회를 막는 값이다. 0.0.0.0으로 맞추면 PII 검사를 건너뛰는 경로가 열린다.
  - **`max_num_seqs`·`num_speculative_tokens`는 손대지 않았다** — 네 파일이 이미 같고(20 / 4), 값을 바꾸는 것은 정합이 아니라 튜닝이다. 판단은 실측 뒤로 미뤘다.
- **분석**: 31B 덴스는 26B-A4B 대비 full-attention 레이어가 5 → 10개, KV head가 8 → 16개라 **토큰당 KV가 정확히 4배**(40 KiB → 160 KiB)다. `intermediate_size`는 2,112 → 21,504로 10배라 활성화 피크도 커진다. 다만 vLLM은 KV가 모자라도 기동에 실패하지 않고 preempt로 미루므로, 모델명만 바꿔 띄우면 증상이 보이지 않는다. 판정은 추정이 아니라 기동 로그의 `Maximum concurrency`와 부하 중 `PreemptionMode.RECOMPUTE` 경고로 한다.
- **부수**: "다음 작업"의 :5015 프로파일 행이 `max_len 32768`로 남아 있던 것을 65536으로 정정(`5a8fd1b`에서 바뀐 뒤 미반영).
- **상태**: yaml 완료, 운영계 반영 대기. 검증은 `yaml.safe_load` 파싱과 파일 간 diff로 확인 — `prd-gemma`↔`prd-pii-gemma`는 `gateway_port`·`host` 두 줄, `prd-gemma`↔`gemma`는 `gateway_port`·`gpus`/`tensor_parallel_size`만 남았고 전부 존재 이유가 있는 차이다. 연구계·운영계 모두 실기동은 하지 않았다.
- **미확인**: `prd-pii-gemma`의 기존 `gmu 0.8`은 근거를 코드·문서에서 찾지 못해 0.9로 맞췄다. 운영계에서 GPU 0을 다른 프로세스와 나눠 쓰려던 의도였다면 되돌려야 한다.
- **후속(같은 날) — `pull` 정합성**: 대표님이 배포 때마다 `rm -rf /workspace/llm-serving` 후 다시 받아오던 이유가 "갱신된 파일인데 안 내려오는 경우"였다. 원인은 `aws s3 sync`가 **체크섬을 보지 않고 크기와 수정시각만 비교**하는 것이다. 기본 규칙이 "크기가 같고 받는 쪽이 더 새로우면 스킵"인데, sync로 받은 파일의 mtime은 S3 객체의 시각이 아니라 다운로드한 시각으로 찍혀 받는 쪽이 늘 더 새로워진다. 여기에 받은 쪽에서 파일을 한 번 건드렸거나 시계가 어긋나면 갱신분이 조용히 넘어간다.
  - **조치**: 두 `start.sh`의 `cmd_pull`에 `--exact-timestamps` 추가(다운로드 방향 전용 옵션이라 `cmd_push`는 그대로). 판정이 "타임스탬프가 정확히 일치할 때만 스킵"으로 바뀌어 `pull` 한 번이 `rm -rf` 후 재다운로드와 같은 정합을 준다. `rm -rf`와 달리 제외 목록(`.env`·`audit.salt`)은 살아남는 것이 오히려 낫다.
  - **실측**: 같은 조건 `--dryrun` 비교에서 기존 18건 → 변경 후 270건. 252개 파일이 "이미 최신"으로 스킵되고 있었다. 옵션 수용 여부는 오타 옵션(`--exact-timestampsXX` → `Unknown options`)과 대조해 aws-cli 1.44.81에서 확인.
  - **부수**: `pii/.pytest_cache/`·`.ruff_cache/`가 S3를 오가고 있어(15개 객체) `SYNC_EXCLUDES`에 추가 → 전송 대상 270 → 255건. 두 캐시는 도구가 디렉토리 안에 자기 `.gitignore`를 심어 git에서는 저절로 빠지지만 `aws s3 sync`는 그것을 모른다. S3의 기존 객체는 다음 `push`가 프리픽스를 비우면서 정리된다.
  - **문서**: `DEPLOY_GUIDE.md`·`SETUP_GUIDE.md` §9-1에 "pull 전에 디렉토리를 지울 필요가 없다"와 그 근거 반영.

### 2026-08-20 (모델명 `gemma-4` 고정 + 게이트웨이 호환 계층)

- **목표**: API 노출 모델명을 `gemma-4`로 고정해 뒤에서 Gemma·Qwen·GLM을 자유롭게 교체. 모델별로 다른 요청 파라미터는 게이트웨이가 흡수.
- **변경**: `vllm_gateway.py`(호환 계층 신설 + 웜업 비활성 시 `model_root` 미수집 버그픽스) · `instances/*.yaml` 6개(`served_model_name: [gemma-4]`) · `gateways/*.yaml` 6개(`compat`) · `_SCHEMA.txt` 2개 · `VLLM_API_GUIDE.md`(단일 모델 기준 개편, Thinking 절 축약) · `VLLM_OPS_GUIDE.md`(§10.4 신설, 샘플링표 수용) · `speed_results.md`(라벨 주의)
- **결정**:
  - `served_model_name`만으론 `/v1/models`의 `root`에 실경로가 남아 게이트웨이가 마스킹. 별칭은 백엔드가 보고한 `id`를 쓰므로 코드에 하드코딩 없음
  - `reasoning_effort`는 제거가 아니라 번역(`high→xhigh`, 미지원 계열은 제거). 위험한 쪽은 미지원 모델이 아니라 **지원 모델** — Qwen3.8은 모르는 값에 400을 낸다
  - 번역 흔적은 `X-Effort-Applied` 헤더와 로그에 남긴다. 조용히 바꾸면 추적 불가
- **발견**: Gemma Thinking의 `skip_special_tokens: false`는 vLLM 0.20.2가 서버에서 자동 처리(`gemma4_reasoning_parser.py:60-65`) — 문서에서 삭제. 모델 무관 Thinking 규약을 막던 유일한 항목
- **후속(같은 날)**: `traffic_test_vllm.py`에 `--label` 추가(`speed_test.py`와 같은 의미 — 요청엔 안 실리고 리포트 `config.label`·진행 화면에만 남는다. 미지정 시 경고 1줄). 이어 문서 정합성 점검에서 낡은 사실 5건을 잡음 — API 가이드가 §3.3에서 백엔드를 "Gemma 4"로 단정(모델명 고정 전제와 충돌), `reasoning_content`를 OpenAI 스펙으로 잘못 표기(실제로는 vLLM 폐기 예정 구필드), OPS 헤더의 `qwen.yaml`·`prd-gemma.yaml` 모델명·게이트웨이 포트가 `5a8fd1b` 이후 미갱신(`:6016`은 매칭 인스턴스 없음), §11.1 "(현재)" 마커가 두 세대 전
- **후속2**: `speed_test.py`에도 라벨 미지정 경고를 넣어 traffic과 대칭. OPS §11.1 비교표에 Qwen3.8-27B-FP8 열과 권장 샘플링 2행 추가 — 로컬 체크포인트의 `config.json`(linear 48/full 16, 262K, FP8 e4m3)·`chat_template.jinja`(Thinking 기본 ON, `<think>`)·모델 카드(Thinking presence_penalty 0, Instruct 1.5)에서 직접 확인
- **후속3**: 모델명을 다 가려도 **"너는 어떤 모델이야"에는 백엔드 실모델을 그대로 답한다**는 것을 실측(Qwen이 통이 연구소 소속임을 스스로 밝힘). 정체성은 사후 학습으로 가중치에 박혀 서빙 설정으로 못 바꾸므로, 게이트웨이가 `/v1/chat/completions`마다 정체성 시스템 프롬프트를 주입하도록 `compat.inject_identity_prompt`(기본 on) 신설. **새 system 메시지를 index 0에 끼우는 방식은 불가** — Qwen3.8 템플릿이 선두 아닌 system에 `raise_exception`으로 400을 낸다. 클라이언트 system 메시지가 있으면 그 안으로 병합하고, 정체성 문구가 앞·클라이언트 지시가 뒤라 클라이언트 페르소나는 살아남는다
- **상태**: 완료. 연구계 재기동 후 실환경 14항목 + 단위 33건 통과(effort 8값 전부 200, 백엔드 직결은 여전히 400). 문서 수정 후 QA 스위트 31/31 재통과. 정체성 주입도 실기동 6케이스(한/영 정체성·우회 시도·클라 system 유지·일반 품질·effort 합성) + 단위 7케이스 통과 후 QA 31/31 재확인. 잔존은 "다음 작업" P1 참조
- **후속4**: `system_fingerprint`도 닫음. 전 인스턴스 yaml에 `fingerprint_mode: custom` + `fingerprint_value: gemma-4`. 원래 용도는 `seed`와 짝지어 "결정성이 깨졌을 때 서버 탓인지 판별"인데, **연속 배칭에서는 그 계약이 성립하지 않음을 실측** — 같은 `seed=777`이 한산할 땐 3회 동일, 동시 요청 9건과 섞으면 매번 다름. 지킬 계약이 없는 반면 해시에 모델 정체성이 들어가 교체 시점은 드러나므로 고정값이 이득. `none`이 아니라 `custom`인 이유는 클라이언트가 이 값을 로그·캐시 키로 쓸 때 `null`로 깨질 수 있어서. 근거는 `VLLM_OPS_GUIDE.md` §10.5
- **미결(설계 판단)**: `X-Effort-Applied`(계열별 값이라 Qwen/그 외가 갈림)·`logprobs`(토크나이저 지문)는 계열 추정 단서로 남겨둠. 끄면 각각 사고 길이 추적과 정상 용도를 함께 죽이는 맞교환이라 디버깅 쪽을 택함

### 2026-08-19~20 (한국어 능력 비교 + Qwen3.8 조사)

- **목표**: 메인 챗 후보 3종(Gemma 4 26B-A4B/31B, Qwen3.8-27B) 한국어 능력 비교 + 연구계 현행 모델의 추론·코딩 근거 확보
- **변경**: `slm_research/korean.md`·`qwen38.md` 신설 · `comparison.md` 갱신(기존 표는 Qwen3.6-35B-A3B 기준이라 낡음) · `data/2026-08-19_korean/` 원본 보존
- **상태**: 완료 (`6e5848d`, `a01b97b`). 27B 3세대(3.5/3.6/3.8) `config.json` 실차이는 `transformers_version` 한 줄뿐 → 서빙 프로필 재조정 불필요

### 2026-08-10 (start.sh QA 명령 3종 신설 + S3 배포 진입점을 start.sh로 통일)

#### 세션 목표
`tests/`에 스크립트는 있는데 `start.sh`에서 부를 길이 없어 손으로 `python tests/...`를 치던 것을 명령으로 승격. 이어서 `sync.sh`를 `start.sh`로 바꾸고 backend-doc-assistant의 push/pull 방식을 반영.

#### 변경 파일
| 파일 | 변경 유형 | 요약 |
|------|----------|------|
| `llm-serving/vllm/start.sh` | 기능 추가 | `test`·`speed`·`traffic` 3종. 공통 실행기 `run_suite`(스크립트·라벨·all허용·게이트웨이전용 4파라미터)로 대상 라우팅 일원화 |
| `llm-serving/stt/start.sh` | 설정 | `TEST_SCRIPT`=STT 스위트, `SPEED_SCRIPT`·`TRAFFIC_SCRIPT`=빈 값(미지원 표시) |
| `llm-serving/vllm/tests/test_vllm_server.py` | 버그픽스 | yaml fallback이 `tests/gateways/`를 봐서 항상 실패 → `dirname` 한 단계 상향 |
| `llm-serving/sync.sh` → `start.sh` | rename+기능 | push=프리픽스 비운 뒤 전체 업로드(버킷 루트 가드), pull=`--delete`. chmod 대상에 루트 start.sh 추가 |
| `aws/sync.sh` → `start.sh` | rename+기능 | 동일 적용 |
| `VLLM_OPS_GUIDE.md` | 문서 | 명령 목록 + §14.1·§14.3·§14.3.1 진입점 |
| `STT_OPS_GUIDE.md` | 문서 | 명령 목록 + §11 QA 체크리스트 |
| `DEPLOY_GUIDE.md`·`SETUP_GUIDE.md` | 문서 | `sync.sh` 참조 10곳 교체, 전체 교체 push 경고, 이름 충돌 주의 |
| `GUIDE.md` | 문서 | "자주 쓰는 명령"의 raw `aws s3 sync` 2행을 `./start.sh push`·`pull`로 교체, 서빙 코드 배포 행 신설 |
| `aws/.env.dev`·`.env.prd` | 신설 | 환경별 원본. `.env.prd`는 기존 `.env` 복사, `.env.dev`는 옛 dev 템플릿에 비밀번호·HF 토큰만 채움. 구 `.env.*.example` 2개는 `.archive/2026-08-10_env-example/`로 이동 |
| `aws/start.sh` | 기능 | `SYNC_EXCLUDES`에 `.env` 추가(런타임 로드본 보호), pull에서 `.env` 부재 시 `cp` 안내 |
| `vllm/start.sh` (help) | 수정 | `cmd_help`가 `SPEED_SCRIPT`·`TRAFFIC_SCRIPT` 유무를 보고 해당 줄을 빼도록 변경 — STT 도움말이 미지원 명령을 광고하고 있었다 |
| `VLLM_API_GUIDE.md`·`STT_API_GUIDE.md`·`VLLM_OPS_GUIDE.md` | 문서(대표님 변경) | 연구계 외부 IP `43.203.176.149` → `43.203.142.247` 43곳. 같은 커밋에 동반 |
| `SETUP_GUIDE.md`·`DEPLOY_GUIDE.md` | 문서 | EC2 최초 셋업의 `chmod` 대상에 `start.sh`가 빠져 raw sync 직후 `./start.sh pull`이 실행권한 없이 막히던 것을 `chmod +x *.sh`로 교체(코드 다운로드 직후로 위치 이동). DEPLOY_GUIDE 트러블슈팅에도 루트 `start.sh` 추가 |
| `GUIDE.md` | 문서 | 정합 원칙이 가리키던 `.env.example`이 `aws/`에서는 사라져, 디렉토리별 실제 파일명으로 명시 |

#### 결정 사항
- **speed·traffic은 `test` 하위 옵션이 아니라 별도 명령** — `speed`는 합격/불합격 판정이 없어 `test`의 실행/실패 요약에 얹히지 않고, `traffic`은 부하라 성격이 다르다. 기존 "동사 하나 = 명령 하나" 구조와도 맞음.
- **`traffic`은 무인자·`all` 거부 + 게이트웨이 전용** — 무인자 순회를 허용하면 운영 게이트웨이까지 동시 20 부하를 받는다. 인스턴스는 `/server-status`가 없어(vllm_gateway.py 전용) 부하 결과와 무관하게 항상 실패 판정이 나므로 대상 단계에서 차단. 실측: 게이트웨이 :5015 → 200 / 인스턴스 :7071 → 404.
- **단일 대상은 미기동이어도 SKIP하지 않음** — 이름을 찍은 것은 "떠 있어야 한다"는 기대. 무인자 `all`만 SKIP(게이트웨이 6대 중 일부만 띄우는 것이 정상 운영이라, 안 띄운 대상의 실패로 진짜 실패가 묻힌다).
- **대상은 첫 자리에서만 인식** — `--category`가 `nargs="*"`라 비대시 인자를 훑으면 `test --category infra`의 `infra`를 대상으로 오인한다(`cmd_logs`의 `--lines`는 값이 하나뿐이라 그 방식이 통했음).
- **push 전체 교체 채택** — 두 스크립트의 제외 목록이 전부 런타임 산출물·시크릿이라 삭제 단계에서 함께 지워지는 편이 정리가 된다. `wheels/`(246MB)는 제외 대상이 아니라 aws는 push마다 재업로드됨.
- **`.env`는 동기화 제외, 환경별 원본만 S3로** (backend-doc-assistant 방식) — 전에는 `.env`가 동기화에 포함돼 pull 한 번에 대상 서버의 `MODE`·`USERNAME`·GPU 배정이 다른 환경 값으로 덮어써졌다. 이제 `.env.dev`/`.env.prd`만 오가고 각 서버가 `cp .env.prd .env`로 한 번 골라두면 이후 pull에 영향받지 않는다. 두 원본은 토큰·비밀번호를 담아 `.gitignore`에 넣고 S3로만 전달. AWS CLI에서 `--exclude '.env'`는 정확매칭이라 `.env.dev`/`.env.prd`는 걸리지 않는다(`--dryrun` 실측 확인).

#### 함정 4건 (신규 발견)
- **`push --dryrun`이 실제 삭제를 유발할 뻔** — doc-assistant의 `cmd_push`는 인자를 안 받지만 이 두 스크립트는 `"$@"` 패스스루가 있고 문서도 `--dryrun`을 권장한다. 그대로 옮기면 sync만 미리보기가 되고 `aws s3 rm`은 진짜로 실행된다. `--dryrun`만 골라 rm에도 전달(`--delete` 등 sync 전용 옵션은 rm이 모르므로 제외).
- **검사 순서로 없는 기능 유도** — 인스턴스 차단을 `cmd_traffic`에 두니 STT에서 "게이트웨이를 쓰세요"가 미지원 안내보다 먼저 떴다. `run_suite`로 옮겨 미지원 검사 뒤에 배치.
- **문서 예시가 실행 불가** — STT에 `./start.sh test 7171`이라 적었으나 7171은 whisper_v3의 포트일 뿐 yaml 파일명이 아니라 라우팅 실패. `whisper_v3`/`5018`로 정정. 이후 문서의 모든 명령 예시를 실제로 실행해 대조.
- **S3는 실행권한을 보존하지 않는다** — 배포 진입점을 `start.sh`로 바꿨는데 `SETUP_GUIDE`의 최초 셋업 `chmod`는 `setup-ec2.sh user.sh`만 대상이라, raw sync로 받은 EC2에서 `./start.sh pull`이 첫 호출부터 막힌다. S3에서 실제로 받아 `-rw-rw-r--`(644)임을 확인. `chmod +x *.sh`로 교체(pull이 하는 것과 같은 범위). `DEPLOY_GUIDE`는 66행에서 `start.sh`를 챙겼는데 트러블슈팅 행에서는 빠져 있어 같이 보완 — 한쪽만 고치면 이런 비대칭이 남는다.

#### 현재 상태
완료. 검증은 실행 기반 — 인스턴스 직접 호출이 자동 회피 포트 :7071을 집어 QA 통과, `speed` 전체 순회 정상, `traffic`이 게이트웨이에서 `통과: True`. S3는 건드리지 않았고 push/pull은 가짜 `aws`로 인자 전달만 확인(반영은 대표님이 직접 실행 시).

> 부수: 검증 중 `aws/start.sh pull`의 `chmod +x *.sh`가 `entrypoint-llm.sh`를 644→755로 바꿔 `git checkout`으로 복원. `Dockerfile.llm`이 COPY 후 `RUN chmod +x`를 하므로 동작 영향은 없음.

### 2026-07-22 (가이드 문서 정합 일괄 갱신 + STT 포트 정정 + 문체 점검)

- **목표**: 7/21 변경(26B 전환·비PII/PII 2-모드·download·ner.yaml)이 미반영된 가이드 문서 전수 정합. 방향은 대표님 확정 — ① API 가이드 모델 표기 26B 전면 교체 ② PII 서술은 2-모드 구조로 재서술.
- **변경**: `VLLM_API_GUIDE.md`(모델명 약 30곳 26B-A4B 교체 — generation_config 샘플링 동일 확인, PII 박스·§3.6~3.7·에러표를 "PII 모드 한정"으로 조건부화) · `VLLM_OPS_GUIDE.md`(헤더·§6.1 구성도·§7.5/7.8/7.9·§9 파일트리·§10.1·§14를 2-모드로 재서술, `prd-pii-*` 파일명 정합, §7.4 LB 예시 소속 불일치 정정) · `DEPLOY_GUIDE.md`(진입점 맵·§3 기동 모드별 분리, download 절차 반영) · `llm-serving/README.md`·`pii/README.md`(PII "선택 모드(현재 미운용)" 강등, `ner.yaml` 등재, NER 512 토큰 한계 알려진 이슈 명기) · `slm_research/mtp.md` §5.4 본 환경 실측 추가(acceptance 31B 70~85% vs 26B 32~47%, c=1 TPS 약 2.4배).
- **상태**: 완료. 검증 — API 가이드 31B 잔존 2곳(의도된 안내문), `prd-qwen` 옛 명칭 잔존 0, "모든 LLM PII 경유" 옛 전제 문구 0.
- **(후속) STT 포트 정정 — P1 "STT 문서 정정" 해소**: 실물 yaml 기준(voxtral=gw **5018** realtime 분리 / qwen3_asr·whisper_v3=gw **5017** model 라우팅, whisper GPU **2**)으로 `STT_OPS_GUIDE`(§6 구성도·§9.1 gmu 0.4/max_len 16384·§9.3 overload 20/40/180·§11 QA 포트) · `STT_API_GUIDE`(:5018 분리, 상시 기동 안내) · `stt/README`(구성 표·GPU 충돌: whisper↔voxtral) · `PROJECT`·`llm-serving/README`·`DEPLOY`·`OPS`·루트 README·`MODEL_STUDY` 현재 상태부 일괄 정정.
- **(후속) 문체 점검**: aws·llm-serving·agent-guide 전 문서 상투어/번역체/압축체 패턴 일괄 검색 — 실질 지적 3건(수동태 직역 1, 수다 사족 1, "(소중함)" 라벨 1) 수정. 조사·계획 기록물(slm_research 상세, pii_model_research, plans/)은 이력 보존 위해 문체 미수정.
- **(후속) 연구계 IP 변경 반영**: 연구계 외부 IP `3.38.195.121` → `43.203.176.149`. `VLLM_API_GUIDE`(21곳)·`VLLM_OPS_GUIDE`(10곳)·`STT_API_GUIDE`(12곳) 총 43곳 일괄 치환, 구 IP 잔존 0. 운영계(:5501 등) 실주소는 문서에 하드코딩 없음(운영자 확인 방침 유지)이라 대상 아님.

### 2026-07-21 (재기동 복구 + Gemma 26B-A4B 전환 + download 명령 신설 + PII NER 개선)

> 6주 공백 후 세션. 7/13 10:57 전 서빙 동시 절단(전원 단절형, 7/20 호스트 재부팅) 확인 → 26B-A4B 전환 라이브까지.

**핵심 변경** (커밋 `c78b259`·`32c1e8a`·`1e3f40c`·`93c31a7` + 미커밋 PII 배치):
- **HF 모델 갱신 대응**: gemma-4 31B/26B 커밋 이력 확인 — 가중치 무변경, `chat_template.jinja`(툴콜·reasoning fix)와 `tokenizer_config.json`만 갱신 → 증분 동기화로 해결(108GB 재다운로드 불필요). 갱신 전 파일 `/models/LLM/google/.archive/2026-07-21_pre-update/` 보존.
- **`./start.sh download [name|all]` 신설**: launcher `--download-only`에 sync 모드 — 로컬이 있어도 HF 최신과 증분 동기화. **`up`은 네트워크 미접근 유지**(폐쇄망 절차: 개방→download→차단→up). STT wrapper 자동 상속.
- **`${model}-assistant` 치환**: drafter가 본체 model을 자동 추종(launcher 문자열 치환). gemma 4종 yaml spec 블록 완전 동일화 — cp 후 본체/drafter 짝 어긋남 구조적 차단. Qwen(native MTP)은 미영향.
- **`gemma-26b.yaml` 신설 + 라이브**: 26B-A4B(MoE 128/8) + MTP drafter 0.4B(`num_speculative_tokens 4` 공식 고정, method 키 금지). fp8·TP2·gmu 0.9·port 7071. `_SCHEMA.txt`에 MoE 함정 4건(저동시성 이득 제한·4-bit 양자화 금지·MXFP4 #39000·DP>1 #38999) 이관.
- **연구계 PII on/off = "모드=모델" 매핑(대표님 확정)**: 비PII 직접 `up gemma-26b`+`up 5015`(26B, gateways/5015.yaml 0.0.0.0) ↔ PII 경유 `up gemma`+`up 6015`+`pii up 5015`(31B). :5015와 GPU0·1 각각 택일.
- **PII NER 개선(미커밋)**: ① `configs/ner.yaml` 신설 — gpu/models_dir/max_concurrency/backends yaml 승격(env `PII_GPU` 우선) ② `ner_server.py` 추론 스레드풀 분리 + 세마포어 — 부하 중에도 `/health` 1ms 응답(기존: 추론 블로킹 → unhealthy 오판 → fail-closed 전체 차단 연쇄 가능).

**발견 이슈**: 🚨 NER 512 토큰 초과 청킹 부재(P1급, 기존 버그 — 긴 텍스트 500 에러). PII 미사용 중이라 후속 보류(위 다음 작업 표 참조).

**검증**: 26B 게이트웨이 :5015 ready 1/1 + `test_vllm_server.py` 9 카테고리 통과(새 chat template + gemma4 파서 궁합 포함) + speed 6행. download/치환/NER 동시성 각각 라이브 검증.

**운영 반영 주의**: `${model}-assistant` 표기 yaml은 신형 `vllm_server_launcher.py`와 **반드시 동반 배포**(구형 런처는 문자 그대로 해석해 실패).

**문서 정합(아침)**: 미기록 커밋 2건 반영 — `d242cc4`(GUIDE 작업 환경 토폴로지 신설), `c18bcbf`(start.sh 무인자 도움말). 6/09 "미커밋" 표기는 실제로는 커밋 완료였음(`de734ce`·`86a4839`).

**현재 상태**: 연구계 gemma-26b(GPU0·1) ← :5015 직접 라이브. PII·STT·qwen 미기동. 미커밋: PII 배치 4파일 + speed_results 5행 + agent-guide 3종.

---

## 과거 세션 (초압축 — 상세는 git log)

| 날짜 | 요약 |
|------|------|
| 2026-06-09 | 전 서빙 yaml 주석 슬림화(인스턴스 433→65줄 등) + 공용 `_SCHEMA.txt` 5종 분리(운영 노하우 이관). PII on/off 토글 구조(운영 5501 비PII/6501 PII 분리)·토폴로지 Q&A(enforcement=포트 인수 이유·LB 위치·bypass 정합). 커밋 `de734ce` |
| 2026-06-05 ③ | NER "연구/운영 공유" 주석 오류 10곳 정정(`3c23160`). 한국어 PII 모델 재조사 — SLM 전환 비권장(인코더 NER F1 96 vs 79), townboy 실측 최고(P 90.5/R 95)로 현 구성 유지, 라이선스 해소(`NOTICE.md`, KPF-BERT MIT + KDPII CC-BY). 리포트 `pii/pii_model_research.md` |
| 2026-06-05 ② | PII 후속 배치: ORG 과탐 헤더 토글·bypass 토큰·우회 차단(점 구분자·account→card Luhn 승격·function_call/input_text 검사)·스트리밍 재작성(fail-closed 503, n>1 보존)·`recall_gate.py` 하버스. 코덱스 리뷰 4회 선별 수용. 테스트 60건, 합성 eval P 100/R 96.6. 커밋 `b1e33a6`·`1270baa`·`eaeecb6` |
| 2026-06-05 ① | PII/DLP 운영 토폴로지 적용: 프록시가 외부 :5015 인수, 게이트웨이 6015 내부 이동(파일명=포트 rename). NER 풀(8911 vmaca/8901 townboy, GPU3) + salt 자동주입. 버그픽스 2건(brn 우선순위 누락·지역번호 regex). 연구계 :5015 enforcement 라이브. 커밋 `295ce8c` |
| 2026-05-27 | `vllm/start.sh logs [name]` 서브커맨드(tail -F 단일 진입점, 기본 all·-n 50). STT wrapper 자동 반영 |
| 2026-05-15 | `aws/user.sh --extra-ports` 콤마 구분 다중 range 지원(라벨 원본 보존으로 rebuild 복원) |
| 2026-05-13 ② | STT 단일 게이트웨이 전환(3 모델 `gateway_port: 5017` 활성, model 필드 라우팅) + `STT_API_GUIDE.md` 사용자 톤 재작성. OPS/README 옛 표기 정정은 P1 잔존 |
| 2026-05-13 ① | Gemma 31B 실기동 성공 — 단일카드 6회 fail 후 TP=2·max_len 32768·gmu 0.95 확정. `tests/` 디렉토리 신설 + `speed_test.py`(8컬럼 누적). 교훈: vLLM 메모리 에러는 startup free check ↔ KV 부족 단계 분리 진단(gmu/max_len 처방 다름) |
| 2026-05-12 ② | STT 한국어 의사결정 — 시나리오 E(정확도+offline): Whisper-large-v3 1순위(+fine-tune 트랙), Voxtral은 실시간 격리. 옵션 A 리팩토링: stt `start.sh`/`logging.sh`를 vllm 본체 thin wrapper화(-617줄). STT yaml 3종 통일 |
| 2026-05-12 ① | MTP 도입 — Gemma 31B external drafter(`-assistant` 0.5B) + Qwen 27B native(`method: mtp`). launcher `_resolve_model_path` drafter 자동 다운로드 |
| 2026-05-04 ② | STT Voxtral 페어 구조(instances/ + gateways/5017) — 게이트웨이 본체에 `audio/transcriptions`·`realtime`(WS) 라우트 추가, STT 가이드 2종 신설. 라이브 검증 통과 |
| 2026-05-04 ① | 게이트웨이 `AdmissionController`(inflight/queue 제한 + 429 Retry-After) + `traffic_test_vllm.py` smoke/overload. 라이브 과부하 24동시 통과 |
| 2026-04-30 ③ | start.sh 운영 견고성(cmdline 정체성 검증·종료 폴링) + launcher fcntl port-alloc 직렬화·atomic runtime write |
| 2026-04-30 ② | code-server/vsix 전면 제거(폐쇄망 정책) · `aws/README→SETUP_GUIDE` 분리 · start.sh `[name]` instances/gateways 자동 라우팅 · test 디버그 가독성(Tee+요청/응답 첨부) |
| 2026-04-30 ① | 게이트웨이 자동 디스커버리(Phase 2: `gateway_port` 매칭 + 포트 자동 회피 + runtime json, backends 수동 명시는 escape hatch) + yaml 통일. 교훈: mv 아카이빙·운영 주석 다이어트 금지 |
| 2026-04-29 ①~③ | 레포 3-디렉토리 재편(`my-docker-server`/`aws`/`llm-serving`) + agent-guide 3종 초기화 · STT 인프라 초안 + `DEPLOY_GUIDE.md` · aws P2 보강 + 내부망 운영 정책(`project_internal_network`) |
