# 🏗️ ai-infra — 서버 세팅 & 운영 구성 모음

서버 설치·운영·배포·서빙과 관련된 모든 구성을 한 곳에 모은 레포입니다. 2026-10-07에 이름을 `docker`에서 `ai-infra`로 바꿨습니다. 옛 이름으로 받은 사본은 GitHub가 새 주소로 연결해 주지만, `git remote set-url origin https://github.com/mulgae-life/ai-infra.git`으로 바꿔 두기를 권합니다.

## 📂 디렉토리 구조

| 경로 | 역할 |
|------|------|
| [`my-docker-server/`](my-docker-server/) | 로컬 PC·사내 서버용 dev/GPU Docker 환경 (`Dockerfile.dev`, `Dockerfile.gpu`, `docker-compose.yml`) |
| [`aws/`](aws/) | AWS EC2 GPU 인스턴스 셋업 + 다중 사용자 컨테이너 운영 인프라 (vLLM 베이스, SSH) |
| [`on-prem/`](on-prem/) | 온프레미스 H200 서버(RHEL 10) 호스트 셋업 + 폐쇄망 준비 점검. 컨테이너 계층은 `aws/`를 그대로 실행 |
| [`llm-serving/`](llm-serving/) | LLM/STT 서빙 프레임워크 운영 구성 (vLLM 기반 LLM :5015/:5016 + STT Voxtral :5018, 향후 SGLang 추가 예정) |
| [`ai-research/`](ai-research/) | 모델 학습·실험 실행 공간 (보험 임베딩 파인튜닝). 데이터·실행 결과·가중치는 git 제외 |

각 디렉토리는 자체 README/가이드를 포함합니다. 아래 진입점에서 시작하세요.

## 🚀 목적별 진입점

| 하고 싶은 것 | 시작 위치 |
|--------------|----------|
| 로컬 PC에 풀스택 dev/GPU 컨테이너 띄우기 | [`my-docker-server/SETUP_GUIDE.md`](my-docker-server/SETUP_GUIDE.md) |
| AWS GPU 인스턴스에 vLLM 베이스 + 다중 사용자 운영 환경 셋업 | [`aws/SETUP_GUIDE.md`](aws/SETUP_GUIDE.md) |
| 온프레미스 H200 서버(RHEL 10) 호스트 셋업 + 네트워크 끊기 전 점검 | [`on-prem/SETUP_GUIDE.md`](on-prem/SETUP_GUIDE.md) |
| vLLM API 호출 (사용자) | [`llm-serving/VLLM_API_GUIDE.md`](llm-serving/VLLM_API_GUIDE.md) |
| vLLM 서버 + 멀티 GPU 게이트웨이 띄우기 (운영자) | [`llm-serving/VLLM_OPS_GUIDE.md`](llm-serving/VLLM_OPS_GUIDE.md) |
| STT API 호출 (사용자) | [`llm-serving/STT_API_GUIDE.md`](llm-serving/STT_API_GUIDE.md) |
| STT 서버 + 게이트웨이 띄우기 (운영자) | [`llm-serving/STT_OPS_GUIDE.md`](llm-serving/STT_OPS_GUIDE.md) |
| 새 LLM/STT 서빙 프레임워크(SGLang 등) 추가 | [`llm-serving/README.md`](llm-serving/README.md) |
| 보험 임베딩 파인튜닝 실험 | [`ai-research/insurance-embedding/README.md`](ai-research/insurance-embedding/README.md) |

## 🧭 디렉토리 분리 원칙

| 레이어 | 책임 | 위치 |
|--------|------|------|
| **개발 환경** | 로컬·사내 개발자 PC에 띄우는 컨테이너 | `my-docker-server/` |
| **인프라** | 호스트 셋업, 드라이버, 다중 사용자, 포트/볼륨 정책 | `aws/` (EC2), `on-prem/` (사내 H200 — 호스트 계층만, 컨테이너 계층은 `aws/` 공유) |
| **서빙** | LLM/STT 모델 서빙 프레임워크 설정·게이트웨이·운영 가이드 | `llm-serving/` |
| **연구** | 모델 학습·실험의 코드·설정·데이터·실행 결과 | `ai-research/` |

> 인프라(어디에 띄우는가) ↔ 서빙(무엇을 어떻게 띄우는가)을 분리해 각 영역을 독립적으로 갱신할 수 있도록 구성합니다.
