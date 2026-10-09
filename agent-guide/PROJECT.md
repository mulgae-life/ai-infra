---
name: project
description: ai-infra 레포 핵심 요약. 서버·운영 구성 자산 모음으로 디렉토리 분리 원칙과 기술 스택 파악용.
last-updated: 2026-10-08 (ai-research 레이어 신설)
---

# 프로젝트 개요

> 서버 설치·운영·배포·서빙 인프라 구성을 한 레포에서 관리하는 **운영 자산 모음**. 로컬 dev / AWS 인프라 / LLM 서빙을 디렉토리로 분리해 영역별로 독립 갱신합니다.

---

## TL;DR

| 항목 | 내용 |
|------|------|
| **프로젝트** | ai-infra (서버 세팅 & 운영 구성 모음). 2026-10-07에 `docker`에서 이름을 바꿨다 |
| **목적** | 인프라(어디에 띄우는가) ↔ 서빙(무엇을 어떻게 띄우는가)을 한 레포에서 관리하면서 디렉토리로 책임 분리 |
| **기술 스택** | Docker, Ubuntu 24.04, NVIDIA CUDA 12.6, AWS EC2 GPU, vLLM, Python 3.12 / Node.js LTS |
| **운영 자산** | `my-docker-server/` (로컬 dev/GPU) + `aws/` (EC2 GPU 인프라) + `on-prem/` (사내 H200 호스트 셋업) + `llm-serving/vllm/` (서빙) |
| **작업 관리** | 별도 도구 없음 → `git log` + `SESSION.md` "다음 작업" |

---

## 디렉토리 분리 원칙

| 레이어 | 책임 | 위치 | 안 다루는 것 |
|--------|------|------|------------|
| **개발 환경** | 로컬 PC·사내 서버에 띄우는 컨테이너 (개발자 PC) | `my-docker-server/` | EC2 호스트 셋업, 모델 서빙 |
| **인프라** | 호스트 셋업, 드라이버, 다중 사용자, 포트/볼륨 정책 | `aws/` (EC2, 컨테이너 계층 포함) / `on-prem/` (사내 RHEL 10 H200 — 호스트 계층만, `.env`·compose·`user.sh`는 `aws/` 공유) | 모델 추론 로직, 게이트웨이 라우팅 |
| **서빙** | LLM 모델 서빙 프레임워크 설정·게이트웨이·운영 가이드 | `llm-serving/` | 어디에 띄울지 (인프라), 컨테이너 OS 설정 |
| **연구** | 모델 학습·실험을 돌리는 코드·설정·데이터·실행 결과. 데이터·실행 결과·가중치는 git 제외 | `ai-research/` | 서빙 설정 (`llm-serving/`), 조사·설계 문서 (`agent-guide/docs/*_research/`) |

> 신규 파일을 만들 때는 위 책임 표를 보고 디렉토리를 결정하세요. 예: vLLM의 새로운 멀티모달 설정은 `llm-serving/vllm/`, EC2 자동 스케일 정책은 `aws/`, 새로운 로컬 GPU 워크플로우는 `my-docker-server/`, 새 학습 실험은 `ai-research/<프로젝트>/`.

---

## 프로젝트 구조

```
ai-infra/
├── README.md                         # 메타 진입점 (디렉토리 안내)
├── agent-guide/                      # AI 에이전트 가이드 (GUIDE/PROJECT/SESSION)
│   ├── docs/slm_research/            # 모델 조사 (models/·topics/·sources/, 목록은 README) — 연구계 전용, S3 배포 범위 밖
│   └── docs/embedding_research/      # 임베딩 모델 조사 (slm_research와 같은 구조) — 연구계 전용, S3 배포 범위 밖
│
├── ai-research/                      # 연구·실험 실행 공간 — S3 배포 범위 밖. 프로젝트 목록과 git 추적 구분은 README
│   ├── .gitignore                    # 프로젝트 바로 아래 data/·runs/·models/ 제외
│   └── insurance-embedding/          # 보험 임베딩 파인튜닝 (설계: docs/embedding_research/topics/insurance-finetuning.md)
│
├── my-docker-server/                 # 로컬 dev/GPU Docker 환경
│   ├── Dockerfile.dev                # Ubuntu 24.04 + Node/Python/Playwright/CC
│   ├── Dockerfile.gpu                # CUDA 12.6 + CuPy/Numba
│   ├── docker-compose.yml            # cfd + dev-fullstack 서비스
│   ├── entrypoint.sh                 # 홈 디렉토리 초기화 + chown + SSH 호스트 키 보관/복원
│   ├── .env.example                  # USERNAME/PASSWORD/UID=2000/GID=2000
│   ├── sshd-hardening.conf           # 컨테이너 sshd 브루트포스 대응 (이미지에 COPY)
│   ├── ssh-guard.sh / .service       # 호스트 DOCKER-USER 방화벽 (Tailscale·LAN 통과, 그 외 rate-limit)
│   └── SETUP_GUIDE.md                # 설치·접속·운영·문제 해결 가이드 (aws/on-prem 과 같은 이름 규칙)
│
├── aws/                              # AWS EC2 GPU 인프라
│   ├── start.sh                      # S3 코드 배포 (push=전체 교체 / pull=--delete 받기)
│   ├── setup-ec2.sh                  # Phase 1 → reboot → Phase 2 자동
│   ├── user.sh                       # 다중 사용자 컨테이너 (포트 자동 할당)
│   ├── docker-compose.yml            # vLLM 베이스 컨테이너
│   ├── Dockerfile.llm                # vLLM 베이스 + SSH (dev/prd)
│   ├── entrypoint-llm.sh
│   ├── requirements.txt              # 컨테이너 내 pip (transformers는 --no-deps)
│   ├── .env.dev / .env.prd           # 환경별 원본 (S3만, git 제외) — 배포 후 cp .env.dev .env
│   ├── .env                          # 각 서버 런타임 로드본 (S3 동기화 제외, git 제외)
│   ├── ssh-config-sample
│   └── README.md
│
└── llm-serving/                      # LLM/STT 서빙 프레임워크 모음
    ├── start.sh                      # S3 코드 배포 (push/pull) — 하위 start.sh(서비스 제어)와 역할 다름
    ├── README.md                     # 프레임워크 인덱스
    ├── DEPLOY_GUIDE.md               # 서빙 인프라 배포 가이드 (LLM+STT 공용)
    ├── VLLM_API_GUIDE.md             # vLLM 사용자용 API 가이드 (호출 예시·파라미터)
    ├── VLLM_OPS_GUIDE.md             # vLLM 운영자용 가이드 (기동·튜닝·트러블슈팅)
    ├── STT_API_GUIDE.md              # STT 사용자용 API 가이드 (transcription·realtime·통합)
    ├── STT_OPS_GUIDE.md              # STT 운영자용 가이드 (시스템 구조·메모리 핏·의존성)
    ├── vllm/                         # LLM 운영 중 (격리 페어 + 자동 디스커버리)
    │   ├── start.sh                  # 서비스 제어 (up/down/status/logs) + download 모델 동기화 + test/speed/traffic QA
    │   ├── vllm_server_launcher.py   # 단일 vLLM 기동 + 포트 자동 회피 + 모델 증분 동기화(--download-only) + ${model} 치환
    │   ├── vllm_gateway.py           # OpenAI 호환 게이트웨이 (chat + audio + realtime)
    │   ├── instances/                # 인스턴스 yaml (키당 제목 한줄 슬림, 상세는 _SCHEMA.txt)
    │   │   ├── _SCHEMA.txt            #   인스턴스 키 레퍼런스 + 모델별 노하우(MTP·soft_tokens·GPU표)
    │   │   ├── gemma.yaml            #   ├ 연구 gemma 31B   gw 6015 → 외부 :5015 (PII 경유)
    │   │   ├── gemma-26b.yaml        #   ├ 연구 gemma 26B-A4B gw 5015 → :5015 직접 (비PII, 31B와 GPU0·1 택일)
    │   │   ├── prd-gemma.yaml        #   ├ 운영 gemma  gw 5501 → :5501 직접 (PII 미경유)
    │   │   ├── prd-pii-gemma.yaml    #   ├ 운영 gemma  gw 6501 → :5501 (PII 경유)
    │   │   ├── qwen.yaml             #   ├ 연구 qwen   gw 6016 → :5016 (PII 경유)
    │   │   └── prd-pii-qwen.yaml     #   └ 운영 qwen   gw 6502 → :5502 (PII 경유)
    │   ├── gateways/                 # 게이트웨이 yaml (host/port만 차이, 상세는 _SCHEMA.txt)
    │   │   ├── _SCHEMA.txt            #   게이트웨이 키 레퍼런스
    │   │   ├── 5015.yaml             #   외부 직접 (0.0.0.0, 비PII 연구 gemma-26b)
    │   │   ├── 5501.yaml             #   외부 직접 (0.0.0.0, 비PII 운영 gemma)
    │   │   └── 6015/6016/6501/6502.yaml  # 내부 전용 (외부 입구는 pii/ 프록시)
    │   ├── tests/                   # 테스트 코드/픽스처/결과 디렉토리
    │   │   ├── test_vllm_server.py  # 서버 헬스/추론 9 카테고리 QA
    │   │   ├── traffic_test_vllm.py # 보수적 트래픽/과부하 테스트
    │   │   ├── speed_test.py        # 모델 간 속도 매트릭스 누적 (진입점 ./start.sh speed)
    │   │   ├── ab_regression_probe.py   # vLLM 버전 A/B 회귀·품질 탐침 (--compare로 두 결과 대조)
    │   │   ├── effort_thinking_matrix.py # reasoning_effort × enable_thinking 계약 확인
    │   │   ├── gateway_compat_probe.py  # 게이트웨이 호환 계층(정체성 문구·developer 역할·root 가림)
    │   │   ├── mtp_known_bug_probe.py   # 상류 MTP 결함(문법·요청 혼합) 재현 탐침
    │   │   ├── mtp_prefix_cache_probe.py # MTP + 접두 캐시 손상 재현 + 수락률
    │   │   ├── image.png            # 멀티모달 fixture
    │   │   └── results/             # speed_results.md, vllm-0.31-ab.md(버전업 판정표) 등 누적 리포트
    │   └── bugfix/                   # 운영 중 발견 이슈 기록
    ├── pii/                          # PII/DLP 가드 운영 중 (외부 포트 인수 → 게이트웨이 포워딩, enforcement)
    │   ├── start.sh                  # NER(GPU3)+프록시 기동 (up/down/status [5015|5016|5501|5502|all])
    │   ├── proxy.py                  # in/out PII 검사 프록시 (외부 5015/5016/5501/5502 인수)
    │   ├── ner_server.py             # 한국어 NER 서버 (transformers, GPU)
    │   ├── hooks.py/config.py/audit.py  # 통합 검사·설정·감사로그(평문 미저장 HMAC)
    │   ├── detectors/                # structured(regex+체크섬) + ner_client(LB) + normalize(NFKC)
    │   ├── configs/                  # ner.yaml(NER 풀: gpu/동시성/백엔드) + proxy.{yaml(5015)/5501/5016/5502/e2e}.yaml + _SCHEMA.txt + audit.salt(시크릿, git·S3 제외)
    │   └── tests/                    # 단위 + e2e + eval_pii(합성 정확성) + recall_gate(실데이터 recall 게이트, data/ 라벨 JSONL)
    └── stt/                          # STT 운영 중 (vllm 페어 패턴 동일, launcher/gateway 본체 재사용)
        ├── README.md
        ├── MODEL_STUDY.md            # 후보 모델 비교 / 시나리오
        ├── start.sh                  # vllm/start.sh 패턴 풀 도입 (../vllm 코드 재사용)
        ├── instances/                # + _SCHEMA.txt (키 레퍼런스 + 모델별 표)
        │   ├── voxtral.yaml          # gw 5018 (realtime 분리, GPU 2, 내부 :7172)
        │   ├── qwen3_asr.yaml        # gw 5017 (GPU 0, 내부 :7170)
        │   └── whisper_v3.yaml       # gw 5017 (GPU 2, 내부 :7171)
        └── gateways/                 # 5017.yaml + 5018.yaml + _SCHEMA.txt (warmup off, audio timeout 600s)
```

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| **컨테이너** | Docker, Docker Compose v2, Buildx |
| **베이스 OS** | Ubuntu 24.04, NVIDIA CUDA 12.6.3-devel-ubuntu24.04 |
| **GPU 호스트** | NVIDIA Open Driver, NVIDIA Container Toolkit, Fabric Manager (H100/H200/A100/B100/B200) |
| **클라우드** | AWS EC2 (g6e/p4/p5), EBS, IAM/S3, SSM Session Manager |
| **온프레미스** | RHEL 10, H200, 드라이버 580 LTSB 고정(`dnf versionlock`), Docker CE 저장소, 폐쇄망 대비 사전 pull |
| **서빙** | vLLM (chat + audio + realtime), FastAPI 게이트웨이 (OpenAI 호환 + 대기열 기반 과부하 차단 + 모델 교체 호환 계층). LLM(:5015/:5016 — API 노출명은 백엔드 모델과 무관하게 `gemma-4` 고정) + STT(Voxtral :5018, 비교 PoC :5017). 향후 SGLang 추가 예정 |
| **런타임** | Python 3.12, Node.js LTS (nvm) |
| **개발 도구** | Claude Code, OpenAI Codex, GitHub CLI, tmux, fzf, ripgrep |
| **풀스택 SDK** | Next.js, FastAPI, LangChain, ChromaDB, Supabase CLI, Playwright |
| **GPU Python** | NumPy, Numba, CuPy, Matplotlib, nvitop |
| **보안 / 접근** | OpenSSH, fail2ban |
| **로케일** | ko_KR.UTF-8, Asia/Seoul |

---

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `my-docker-server/docker-compose.yml` | `cfd`(GPU) + `dev`(풀스택) 서비스 정의, 호스트 홈 영속화 |
| `aws/start.sh` | S3 코드 배포 (`push` 전체 교체 / `pull` `--delete` 받기). 구 `sync.sh` |
| `llm-serving/start.sh` | S3 코드 배포 (`push`/`pull`). 구 `sync.sh` — 하위 `vllm/`·`stt/`·`pii/`의 `start.sh`는 서비스 제어라 역할이 다름 |
| `aws/setup-ec2.sh` | Amazon Linux 2023 호스트 1회 셋업 (사용자/SSH/EBS/Docker/NVIDIA, Phase 1↔2 자동 전환) |
| `aws/user.sh` | 사용자별 독립 컨테이너 + 포트 자동 할당(`up`/`down`/`list`/`rebuild`) |
| `aws/Dockerfile.llm` | vLLM 베이스(v0.31.0 정식 이미지) + SSH. dev/prd 모드 분기. 베이스의 핵심 패키지 조합을 제약으로 고정해 requirements를 설치 |
| `aws/gen-core-constraints.py` | 베이스 이미지의 vLLM·torch·transformers·FlashInfer 등을 `==` 제약으로 출력(기본) / 최종 서빙 조합 확인(`--final`, 누락 시 빌드 실패) |
| `aws/docker-compose.yml` | 메인 컨테이너 정의 (`.env`로 GPU/메모리/포트 제어) |
| `llm-serving/vllm/vllm_server_launcher.py` | 다중 vLLM 서버 기동 (GPU 분할, yaml-relative runtime json) — LLM/STT 공용. `--download-only`로 모델+drafter 증분 동기화(서빙 경로는 네트워크 미접근), `speculative_config.model`의 `${model}` 치환 |
| `llm-serving/vllm/vllm_gateway.py` | OpenAI 호환 게이트웨이 (chat/completions + audio/transcriptions + realtime WebSocket) — LLM/STT 공용. 모델 교체 호환 계층 포함(`reasoning_effort` 번역, `/v1/models`의 `root` 마스킹 — `compat` 설정) |
| `llm-serving/vllm/tests/test_vllm_server.py` | 서버 헬스/추론 9 카테고리 QA — 진입점 `./start.sh test [name\|all\|URL]` |
| `llm-serving/vllm/tests/traffic_test_vllm.py` | 운영 서버 보호를 우선한 smoke/overload 트래픽 테스트 — 진입점 `./start.sh traffic <포트>` (게이트웨이 전용, 대상 명시 필수) |
| `llm-serving/vllm/tests/speed_test.py` | 게이트웨이 단위 속도 매트릭스 측정 (모델명 자동 추출, results/speed_results.md 누적 append) — 진입점 `./start.sh speed [name\|all\|URL]` |
| `llm-serving/vllm/tests/ab_regression_probe.py` | vLLM 버전업 회귀·품질 탐침(값 복사·도구 인자·JSON 스키마·이미지 반복·긴 입력). 옛·새 결과 파일을 `--compare`로 대조, 실패 시 종료 1 |
| `llm-serving/vllm/tests/effort_thinking_matrix.py`·`gateway_compat_probe.py` | 게이트웨이 계약 확인 — effort × thinking 조합, 정체성 문구·developer 역할·`/v1/models` root 가림 |
| `llm-serving/vllm/tests/mtp_known_bug_probe.py`·`mtp_prefix_cache_probe.py` | MTP 결함 재현 탐침 — 상류 문법·요청 혼합 결함(#38106·#46088), 접두 캐시 손상(#53912)과 수락률. 버전업 때 MTP 재활성 판단 근거 |
| `llm-serving/pii/proxy.py` | PII 가드 프록시 — 외부 5015/5501 인수, in(주민·카드 차단/이름·주소·전화 마스킹)·out 검사 후 게이트웨이 포워딩 |
| `llm-serving/pii/start.sh` | NER+프록시 기동, 다중 포트 (`up/down/status [5015\|5501\|all]`), salt 자동주입. NER 풀 정의는 `configs/ner.yaml`(gpu/max_concurrency/backends, env `PII_GPU` 우선) |
| `llm-serving/pii/tests/eval_pii.py` | PII 정확성 평가 (한국어 합성 케이스셋, 타입별 precision/recall + 과탐) |
| `llm-serving/pii/tests/recall_gate.py` | 실데이터 recall 게이트 하버스 (라벨 JSONL span-겹침 매칭, person/address/org ≥0.95 미달 시 exit 1, 데이터 없으면 스킵) |
| `llm-serving/VLLM_API_GUIDE.md` | vLLM 사용자용 API 가이드 (§1~§4: 호출·기능·파라미터·에러) |
| `llm-serving/VLLM_OPS_GUIDE.md` | vLLM 운영자용 가이드 (§6~§15: 기동·튜닝·트러블슈팅·QA) |
| `llm-serving/STT_API_GUIDE.md` | STT 사용자용 API 가이드 (§1~§5: transcription·realtime·통합) |
| `llm-serving/STT_OPS_GUIDE.md` | STT 운영자용 가이드 (§6~§12: 시스템 구조·메모리 핏·의존성·트러블슈팅·QA) |
| `llm-serving/stt/start.sh` | STT 클러스터 기동 (vllm/start.sh 패턴 풀 도입, ../vllm 코드 재사용) |
| `llm-serving/stt/instances/voxtral.yaml` | Voxtral 인스턴스 (gateway_port 5018, GPU 2, 내부 :7172) |
| `llm-serving/stt/gateways/` | STT 게이트웨이 — `5018.yaml`(voxtral 메인) + `5017.yaml`(비교 PoC). 공통: warmup 비활성화, audio timeout 600s |

---

## 빠른 시작

```bash
# 1) 로컬 dev/GPU 환경
cd my-docker-server
cp .env.example .env       # USERNAME/PASSWORD 수정 (UID/GID 기본 2000)
docker compose up -d --build       # GPU 미보유 시: docker compose up -d --build dev
ssh <USERNAME>@localhost -p 5010   # dev
ssh <USERNAME>@localhost -p 5000   # cfd

# 2) AWS EC2 GPU 인프라 (Amazon Linux 2023)
cd aws
cp .env.dev .env           # 또는 .env.prd (S3에서 받은 환경별 원본)
vim .env                   # VOLUME_DEVICE 등 서버 고유값 확인
sudo ./setup-ec2.sh        # Phase 1 → 자동 reboot → Phase 2
docker compose up -d --build
sudo ./user.sh up jin --password 1234 --gpus 0,1   # 추가 사용자

# 3) vLLM 서빙 (LLM)
cd llm-serving/vllm
./start.sh download gemma-26b  # 모델+drafter 최신 동기화 (증분, 네트워크 개방 시점에)
./start.sh up gemma-26b && ./start.sh up 5015   # 비PII 직접 모드 (:5015 = 26B)
./start.sh status          # 인스턴스/게이트웨이 상태 확인
python tests/test_vllm_server.py # 추론/스트리밍/툴콜 QA
python tests/speed_test.py --base-url http://localhost:5015  # 모델 간 속도 매트릭스 누적

# 4) STT 서빙 (Voxtral, vllm 페어 패턴 동일)
cd ../stt
./start.sh up              # instances/voxtral.yaml ↔ gateways/5018.yaml 페어 자동
./start.sh status          # voxtral(:7172) + Gateway 5018 (ready 1/1)
curl http://localhost:5018/health   # 게이트웨이 health
```

> 자세한 절차/트러블슈팅은 각 디렉토리의 README 또는 `llm-serving/{VLLM,STT}_{OPS,API}_GUIDE.md` 참조.

---

## 상세 참조

| 문서 | 내용 |
|------|------|
| [SESSION.md](SESSION.md) | 현재 상태, 다음 작업, 최근 세션 로그 |
| [GUIDE.md](GUIDE.md) | 작업 원칙, 용어, 체크리스트 |
| [../README.md](../README.md) | 레포 메타 안내 (디렉토리 진입점) |
| [../my-docker-server/SETUP_GUIDE.md](../my-docker-server/SETUP_GUIDE.md) | 로컬 dev/GPU 환경 설치·접속·운영·문제 해결 |
| [../aws/SETUP_GUIDE.md](../aws/SETUP_GUIDE.md) | EC2 셋업·다중 사용자·dev/prd 모드 |
| [../llm-serving/README.md](../llm-serving/README.md) | 서빙 프레임워크 인덱스 |
| [../llm-serving/VLLM_API_GUIDE.md](../llm-serving/VLLM_API_GUIDE.md) | vLLM 사용자용 API 가이드 |
| [../llm-serving/VLLM_OPS_GUIDE.md](../llm-serving/VLLM_OPS_GUIDE.md) | vLLM 운영자용 가이드 |
| [../llm-serving/STT_API_GUIDE.md](../llm-serving/STT_API_GUIDE.md) | STT 사용자용 API 가이드 (transcription·realtime) |
| [../llm-serving/STT_OPS_GUIDE.md](../llm-serving/STT_OPS_GUIDE.md) | STT 운영자용 가이드 |
| [../llm-serving/stt/README.md](../llm-serving/stt/README.md) | STT 디렉토리 안내 |
