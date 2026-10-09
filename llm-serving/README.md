# 🚀 LLM Serving

LLM 서빙 프레임워크 운영 구성 모음. 서버 인프라(EC2/Docker)와 분리된, **서빙 레이어 전용** 디렉토리.

> 인프라(EC2 + Docker)는 [`../aws/`](../aws/), 컨테이너 환경은 [`../my-docker-server/`](../my-docker-server/) 참조.
> 코드/모델 이관(로컬 → S3 → EC2 → 컨테이너) 절차는 [`DEPLOY_GUIDE.md`](DEPLOY_GUIDE.md) 참조.

## 📦 구성

| 프레임워크 | 상태 | 용도 |
|-----------|:----:|------|
| [`vllm/`](vllm/) | ✅ 운영 | vLLM 서버 + 멀티 GPU 게이트웨이 (한 인스턴스에서 다중 모델 라우팅, OpenAI 호환) |
| [`pii/`](pii/) | 🟡 선택 모드 (현재 미운용) | **PII/DLP 가드** — LLM 앞단 개인정보 검사. PII 모드 적용 시 외부 단일 포트(`:5015`/`:5501`)를 프록시가 인수해 in(주민·카드 차단/이름·주소·전화 마스킹)·out(응답 마스킹) 검사 후 게이트웨이로 포워딩. 구조화(regex+체크섬)+비정형(NER GPU3). 현재는 비PII 모드(게이트웨이 직접)로 운용 |
| `sglang/` | 🔜 예정 | SGLang 기반 서빙 |
| [`stt/`](stt/) | ✅ 운영 | vLLM 기반 STT — Voxtral-Mini-4B-Realtime을 게이트웨이 :5018로 노출 (OpenAI Audio + Realtime API). Qwen3-ASR / Whisper-large-v3는 :5017 게이트웨이 소속 한국어 비교 PoC |

## 🎯 vLLM (현재 운영 중)

설정은 **인스턴스 단위 yaml**(`instances/`)과 **게이트웨이 단위 yaml**(`gateways/`)로 분리. 게이트웨이는 `discover_from` + 인스턴스 yaml의 `gateway_port` 메타 키로 backends를 자동 매칭한다 (수동 명시 불필요).

| 파일 / 디렉토리 | 역할 |
|------|------|
| [`VLLM_API_GUIDE.md`](VLLM_API_GUIDE.md) | **사용자용** API 가이드 (호출 예시 · 파라미터 · `.env` 통합) |
| [`VLLM_OPS_GUIDE.md`](VLLM_OPS_GUIDE.md) | **운영자용** 가이드 (서버 기동 · 모델 교체 · 트러블슈팅 · QA) |
| [`vllm/start.sh`](vllm/start.sh) | 빠른 기동 스크립트 (`up [name\|all]` / `down [name\|all]` / `restart [name\|all]` / `status` / `download [name\|all]` 모델 증분 동기화. `up`·`down` 무인자는 [y/N] 전체 적용 confirm, `./start.sh` 단독 실행은 사용법 출력) |
| [`vllm/vllm_server_launcher.py`](vllm/vllm_server_launcher.py) | vLLM 서버 런처 (인스턴스 yaml `-c` 인자 수신) |
| [`vllm/vllm_gateway.py`](vllm/vllm_gateway.py) | OpenAI 호환 게이트웨이 (자동 디스커버리 LB + 대기열 기반 과부하 차단) |
| [`vllm/instances/`](vllm/instances/) | **인스턴스 단위 yaml** (`<name>.yaml` 1개 = vLLM 프로세스 1대). `gateway_port` 메타 + 모델/포트/GPU. 키 제목 한 줄로 슬림, 키 상세·운영 노하우는 [`instances/_SCHEMA.txt`](vllm/instances/_SCHEMA.txt) |
| [`vllm/gateways/`](vllm/gateways/) | **게이트웨이 단위 yaml** (`<port>.yaml` 1개 = 게이트웨이 1대). `discover_from`으로 인스턴스 자동 매칭. 키 상세는 [`gateways/_SCHEMA.txt`](vllm/gateways/_SCHEMA.txt) |
| [`vllm/tests/`](vllm/tests/) | 테스트 코드 디렉토리 (기능/트래픽/속도 + `results/` 누적 리포트) |
| [`vllm/tests/test_vllm_server.py`](vllm/tests/test_vllm_server.py) | 서버 헬스/추론 기능 테스트 (9개 카테고리 QA) |
| [`vllm/tests/traffic_test_vllm.py`](vllm/tests/traffic_test_vllm.py) | 동시 부하 시험 — 429 방어 응답 집계와 답변 점검(생성 상한 도달·답변 없음) |
| [`vllm/tests/speed_test.py`](vllm/tests/speed_test.py) | 모델 간 속도 비교 (TTFT · TPS 매트릭스 누적, 입력 ~2k자 고정 × max_tokens [512,2048] × 동시성 [1,5,10]) |
| [`../agent-guide/docs/slm_research/`](../agent-guide/docs/slm_research/README.md) | 모델 조사 문서 (Gemma, Qwen, Jev). 목록은 README. 연구계 전용이라 배포 폴더 밖에 둔다 |
| [`vllm/bugfix/`](vllm/bugfix/) | 운영 중 발견된 이슈 기록 |

운영 인스턴스/게이트웨이 추가는 yaml 한 파일 복사 → 값만 수정 → `./start.sh up <name>` (인스턴스) 또는 게이트웨이 재기동(자동 디스커버리). 자세한 사용법은 [`VLLM_OPS_GUIDE.md`](VLLM_OPS_GUIDE.md) 참조. 단순 호출만 필요한 사용자는 [`VLLM_API_GUIDE.md`](VLLM_API_GUIDE.md)부터 보세요.

## 🔒 PII/DLP 가드 (선택 모드 — 현재 미운용)

LLM 앞단에서 개인정보를 검사하는 보안 레이어. **PII 모드** 적용 시 외부 단일 포트를 프록시가 인수해 in(주민·카드 차단 / 이름·주소·전화 마스킹)·out(응답 마스킹) 검사 후 내부 게이트웨이로 포워딩한다 — gemma(연구 `:5015`→`:6015` / 운영 `:5501`→`:6501`), qwen(연구 `:5016`→`:6016` / 운영 `:5502`→`:6502`). **현재는 연구·운영 모두 비PII 모드**(게이트웨이가 외부 포트에 직접, PII 스택 미기동)로 운용하며, 포트당 모드는 택일이다. **연구계/운영계는 격리된 별도 서버**이며, PII 모드 시 각 서버가 자기 NER(GPU3, `:8911`/`:8901`)+프록시만 띄운다(공유 아님).

| 파일 / 디렉토리 | 역할 |
|------|------|
| [`pii/README.md`](pii/README.md) | PII 가드 개요 · 토폴로지 · 기동 · 정책 |
| [`pii/proxy.py`](pii/proxy.py) | 외부 포트 인수 프록시 (in/out 검사 → 게이트웨이 포워딩, 스트리밍 post 검사) |
| [`pii/ner_server.py`](pii/ner_server.py) | 비정형 PII NER 서버 (token-classification, GPU3, transformers 서빙) |
| [`pii/detectors/`](pii/detectors/) | `structured.py`(구조화 regex+체크섬) · `ner_client.py`(NER LB union) · `normalize.py` |
| [`pii/configs/`](pii/configs/) | NER 풀 설정 `ner.yaml`(gpu/모델경로/backends/max_concurrency) · gemma `proxy.yaml`(5015)·`proxy.5501.yaml`(5501) · qwen `proxy.5016.yaml`·`proxy.5502.yaml` · `proxy.e2e.yaml`(테스트) · 키 상세 [`_SCHEMA.txt`](pii/configs/_SCHEMA.txt) |
| [`pii/start.sh`](pii/start.sh) | NER + 프록시 기동 (`up [5015\|5016\|5501\|5502\|all]` / `down` / `status`) |
| [`pii/tests/`](pii/tests/) | E2E + 한국어 합성 케이스셋 회귀 평가(`eval_pii.py`) |
| [`pii/NOTICE.md`](pii/NOTICE.md) | NER 모델 서드파티 출처·라이선스 고지 |
| [`pii/pii_model_research.md`](pii/pii_model_research.md) | 한국어 PII 모델 조사·3종 실측 평가 리포트 |

검출은 **2-track**: 구조화(regex+체크섬, 결정적·모델 대체 불가) + 비정형(NER GPU3, 이름/주소/조직). 기동·정책·트러블슈팅 상세는 [`VLLM_OPS_GUIDE.md`](VLLM_OPS_GUIDE.md) §7.9.

## 🎙️ STT (Voxtral)

vLLM의 `instances/` + `gateways/` 페어 패턴을 STT에도 동일하게 적용. `vllm/vllm_gateway.py`가 chat/completions 외에도 `/v1/audio/transcriptions`, `/v1/realtime` 라우트를 제공하므로 STT 게이트웨이는 **별도 코드 없이 같은 본체를 재사용**합니다.

| 파일 / 디렉토리 | 역할 |
|------|------|
| [`STT_API_GUIDE.md`](STT_API_GUIDE.md) | **사용자용** API 가이드 (transcription · realtime · 파라미터 · 통합 예제) |
| [`STT_OPS_GUIDE.md`](STT_OPS_GUIDE.md) | **운영자용** 가이드 (시스템 구조 · 메모리 핏 · 의존성 · 트러블슈팅 · QA) |
| [`stt/start.sh`](stt/start.sh) | STT 클러스터 기동 (vllm/start.sh와 동일 패턴, launcher/gateway는 ../vllm/ 재사용) |
| [`stt/instances/voxtral.yaml`](stt/instances/voxtral.yaml) | Voxtral 인스턴스 (gateway_port 5018, 내부 :7172, GPU 2) |
| [`stt/gateways/`](stt/gateways/) | STT 게이트웨이 — `5018.yaml`(voxtral 메인) + `5017.yaml`(비교 PoC). 공통: warmup 비활성화, audio timeout 600s |
| [`stt/MODEL_STUDY.md`](stt/MODEL_STUDY.md) | 후보 모델 비교 / 시나리오 |

빠른 호출은 [`STT_API_GUIDE.md`](STT_API_GUIDE.md)부터, 서버 운영은 [`STT_OPS_GUIDE.md`](STT_OPS_GUIDE.md) 참고.

## ➕ 새 프레임워크 추가 시

`llm-serving/<framework>/` 디렉토리를 만들고:
- 운영 가이드(`<FRAMEWORK>_OPS_GUIDE.md`)
- 기동 스크립트
- 설정 파일
- 테스트 스크립트

위 vLLM 구조를 참고해 일관된 형태로 추가합니다.
