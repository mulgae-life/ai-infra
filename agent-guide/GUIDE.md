---
name: guide
description: AI 에이전트 작업 원칙과 세션 시작 체크리스트. 세션 시작 시 가장 먼저 읽기.
last-updated: 2026-06-10
---

# 에이전트 가이드

> AI 에이전트가 세션을 시작할 때 읽는 문서입니다. 이 레포는 코드 앱이 아니라 **서버·운영 구성 자산 모음**이라는 점을 항상 의식하세요.

---

## 작업 환경 토폴로지

> 이 작업 공간(`/workspace/docker`)은 **연구계 GPU 서버의 사용자 컨테이너(`hjjo`) 내부**입니다. **운영계는 물리적으로 다른 서버**(별도 EC2)입니다.

| 구분 | 내용 |
|------|------|
| **연구계 (현 위치)** | L40S × 4 호스트의 `hjjo` 컨테이너. 서빙 프로세스(vLLM/게이트웨이/PII)는 이 컨테이너의 net/PID 네임스페이스 밖이라 `ss`/`ps`로 직접 안 보임 — 라이브 점검은 호스트 IP 경유 |
| **운영계 (별도 서버)** | 여기서 직접 조작 불가. 코드 반영 경로: `./start.sh push` (S3) → 운영계에서 `./start.sh pull` — **운영자가 직접 수행** |

- **운영계 실기동/재기동을 이 환경에서 시도 금지** — 여기서 띄우면 연구계에 잘못 뜹니다. 설정·코드·절차 준비까지만 하고, 실행 단계는 절차로 전달하세요.

---

## 작업 원칙

- 모든 커뮤니케이션은 **한국어**로
- **최소 변경**: 꼭 필요한 범위만 수정. 인접 파일 리포맷/리네이밍 금지
- **근본 원인 해결** 우선, 우회 패치 지양 (특히 셋업 스크립트의 안전성/가드)
- **3-디렉토리 분리 원칙 유지**: `my-docker-server` ↔ `aws` ↔ `llm-serving` 책임이 섞이지 않도록 신규 파일을 적절한 디렉토리에 둡니다 (자세한 분리 기준은 `PROJECT.md` "디렉토리 분리 원칙" 참조)
- **정합 우선**: 환경 파일(`my-docker-server/.env.example`, `aws/.env.dev`·`.env.prd`) ↔ Dockerfile ARG ↔ compose 기본값은 항상 같은 값으로 맞춥니다 (UID/GID, 포트 등)
- **민감 정보 절대 금지**: HF_TOKEN, PASSWORD, AWS 자격증명 등은 코드/README에 직접 쓰지 않고 `.env` 또는 IAM Role
- 커밋 메시지: `feat/fix/docs/refactor/chore/aws/repo` 등 prefix + 한국어 본문

---

## 용어 정리

| 용어 | 설명 |
|------|------|
| **dev / prd 모드** | `aws/` 인스턴스 단위 모드. dev=개발(Claude Code/Codex 자동 설치), prd=운영(슬림화, USERNAME=root) |
| **cfd** | `my-docker-server/`의 GPU 연산 컨테이너 서비스명 (CUDA 12.6 + CuPy/Numba) |
| **dev-fullstack** | `my-docker-server/`의 풀스택 개발 컨테이너 이름 (서비스명은 `dev`) |
| **VOLUME_DEVICE** | `aws/.env`에서 지정하는 추가 EBS 디바이스 경로 (예: `/dev/nvme1n1`) |
| **Phase 1 / Phase 2** | `aws/setup-ec2.sh`의 재부팅 전(드라이버/EBS/Docker) ↔ 재부팅 후(NVIDIA Container Toolkit/Fabric Manager/GPU 검증) 단계 |
| **user.sh** | `aws/`의 다중 사용자 컨테이너 관리 스크립트 (포트 5010~5499 자동 할당) |
| **vLLM Gateway** | `llm-serving/vllm/vllm_gateway.py`. OpenAI 호환 + 모델 라우팅 (다중 vLLM 서버 라우팅) |
| **SLM** | Small Language Model. `agent-guide/docs/slm_research/`에 비교 자료 (Gemma, Qwen) |
| **SSM Session Manager** | AWS Systems Manager로 폐쇄망 EC2 호스트 셸 접근 |
| **MCP** | Model Context Protocol. AI가 외부 도구와 통신하는 방식 |
| **P0/P1/P2** | 우선순위. P0(긴급) > P1(중요) > P2(보통) |

---

## 세션 시작 체크리스트

1. **프로젝트 파악**: `PROJECT.md` 읽기 (디렉토리 책임, 운영 자산, 기술 스택)
2. **현재 상태 파악**: `SESSION.md` 읽기 (다음 작업, 최근 세션)
3. **작업 확인**: 별도 작업 관리 도구 없음 → `git log --oneline -10`과 `SESSION.md` "다음 작업" 표 확인
4. **작업 제안**: 1-3개 제안. 파일 3개 이상 수정 예상되면 `planner` 위임 또는 계획서 먼저

---

## MCP 도구

[TODO: MCP 연동 시 도구 목록 추가]

> 현재는 미연동. 향후 AWS API/SSM, GitHub Issues 등을 MCP로 붙이면 여기 기록.

---

## 자주 쓰는 명령

| 목적 | 명령 |
|------|------|
| 로컬 dev 컨테이너 기동 | `cd my-docker-server && docker compose up -d --build dev` |
| 로컬 GPU 컨테이너 기동 | `cd my-docker-server && docker compose up -d --build` |
| AWS 코드 배포 (S3) | `cd aws && ./start.sh push` — 전체 교체(프리픽스를 비우고 재업로드) |
| EC2에서 코드 동기화 | `cd ~/aws && ./start.sh pull` |
| 서빙 코드 배포 (S3) | `cd llm-serving && ./start.sh push` / 운영계에서 `./start.sh pull` |
| EC2 호스트 셋업 | `cd ~/aws && sudo ./setup-ec2.sh` |
| vLLM 서버 기동 | `cd llm-serving/vllm && ./start.sh up <인스턴스명>` — 무인자는 도움말, `up all`은 전체 |
| 모델 최신 동기화 (증분) | `cd llm-serving/vllm && ./start.sh download <인스턴스명>` — 폐쇄망은 네트워크 개방 시점에 |

---

## 문서 역할

| 문서 | 갱신 시점 |
|------|----------|
| `SESSION.md` | 세션 종료 시 (오늘 한 일, 결정, 다음 작업 갱신) |
| `PROJECT.md` | 디렉토리 분리/아키텍처/기술 스택 변경 시에만 |
| `GUIDE.md` | 작업 원칙·용어·체크리스트 변경 시에만 |

---

## 시작 예시

> "현재 상태 요약하고, 오늘 작업 제안해줘"

> "SESSION.md 읽고 이어서 진행하자"

> "llm-serving에 sglang 디렉토리 골격 잡아줘"
