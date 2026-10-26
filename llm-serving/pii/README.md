# 🔒 PII/DLP 가드

사내 폐쇄망 LLM 서빙 앞단에서 개인정보를 검사하는 보안 레이어. 외부 단일 포트를 프록시가 인수해 요청(in)·응답(out) 텍스트를 검사한 뒤 게이트웨이로 포워딩한다. 방화벽이 외부엔 프록시 포트만 열어 **검사 우회 경로를 차단**하는 전제 위에서 enforcement가 성립한다.

> 📌 **운용 모드**: PII 가드는 **선택 모드**다(2026-07 전환). 현재 연구·운영 모두 **비PII 모드**(게이트웨이가 외부 포트에 직접, PII 스택 미기동)로 운용 중이며, 이 문서의 토폴로지·기동 절차는 **PII 모드 적용 시** 기준이다. 모드 비교는 [`../VLLM_OPS_GUIDE.md`](../VLLM_OPS_GUIDE.md) §6.1.

> 빠른 호출(사용자)은 [`../VLLM_API_GUIDE_research.md`](../VLLM_API_GUIDE_research.md) §3.6~§3.7(PII 박스), 기동·정책 상세(운영자)는 [`../VLLM_OPS_GUIDE.md`](../VLLM_OPS_GUIDE.md) §7.9.

## 토폴로지

```
클라이언트
   │  외부 진입점 (방화벽이 여는 유일한 포트)
   ▼
PII 프록시(proxy.py)        in/out 검사 · 마스킹 · 차단(422) · 감사로그
   │  내부 게이트웨이 (127.0.0.1)
   ▼
게이트웨이(../vllm)         LB · 모델 라우팅 · /v1/models
   │  내부 vLLM
   ▼
vLLM                       추론
```

**진입점 (PII 적용 LLM):**

| 모델 | 외부 진입점(연구/운영) | 내부 게이트웨이 | vLLM |
|------|----------------------|----------------|------|
| gemma | `:5015` / `:5501` | `:6015` / `:6501` | `:7070` |

**연구계·운영계는 격리된 별도 서버**다. 각 서버가 자기 localhost의 NER(GPU3, `:8911`/`:8901`)+프록시만 띄운다 — 같은 서버에 프록시를 더 띄워도 이 NER 풀을 공유한다(NER은 한 번만 기동). 연구↔운영 NER은 물리 분리(공유 아님). yaml의 `127.0.0.1`은 "각 서버 자체 localhost"를 뜻한다.

## 검출 2-track

| track | 구현 | 대상 | 방식 |
|-------|------|------|------|
| **구조화** | `detectors/structured.py` | 주민(rrn)·카드(card)·전화(phone)·계좌(account)·사업자(brn)·이메일(email) | regex + 체크섬 (결정적, 모델 대체 불가) |
| **비정형** | `detectors/ner_client.py` + `ner_server.py` | 이름(name)·주소(address)·조직(org) | NER (GPU3, `vmaca123` + `townboy` LB union) |

NER 모델은 token-classification이라 vLLM 비대상 → transformers로 GPU3에 별도 서빙(`ner_server.py`). GPU 번호·모델 경로·백엔드 목록·동시 처리 상한은 [`configs/ner.yaml`](configs/ner.yaml)에서 설정한다(키 상세는 [`configs/_SCHEMA.txt`](configs/_SCHEMA.txt), 일회성 오버라이드는 `PII_GPU=2 ./start.sh up`). 모델 가중치는 `/models/PII/`(저장소 미포함). 모델 출처·라이선스는 [`NOTICE.md`](NOTICE.md), 조사·실측 평가는 [`pii_model_research.md`](pii_model_research.md).

> ⚠️ **알려진 한계 (2026-07-21 발견)**: NER 백엔드는 BERT 위치 임베딩 512 토큰 상한을 넘는 긴 입력에서 추론이 실패한다(청킹 미구현 → RuntimeError → 500). PII 모드를 재적용하기 전에 overlap 청킹 구현이 필요하다(백로그 P1).

## 정책 (기본값)

| 항목 | 설정 키 | 기본값 | 동작 |
|------|--------|--------|------|
| 차단 타입 | `block_types` | `[rrn, card]` | 검출 시 **422 차단**(고유식별정보) |
| 그 외 타입 | — | — | **마스킹**(`[이름]`, `[전화]` 등)으로 통과 |
| ORG 마스킹 토글 | `ignorable_types` | `[org]` | 헤더 `X-PII-Ignore-Types`로 서비스가 끌 수 있음(문서 메타) |
| 이미지 | `image_policy` | `allow` | allow(텍스트만 검사) / block(이미지 포함 요청 422) |
| 스트리밍 out | `stream_mode` | `post` | 완결 후 1회 검사·재방출(구조 보존). off=패스스루 |
| NER 부분 장애 | `ner_require_all_backends` | `false` | true=fail-closed(컴플라이언스) / false=살아있는 모델 union |
| 우회 | `allow_bypass` | `true` | 헤더 `X-PII-Mode: bypass`로 검사 생략(감사로그 `action=bypass`). `bypass_token`/`PII_BYPASS_TOKEN`으로 2차 가드 |

설정은 `configs/proxy.yaml`(5015)·`proxy.5501.yaml`(5501). 감사로그는 HMAC 지문만 남기고 **평문 미저장**(salt=`configs/audit.salt`, 권한 600 자동생성, S3 동기화 제외).

## 기동

PII는 **안쪽부터** 올린다(프록시가 외부 입구를 인수하므로 게이트웨이·vLLM이 먼저 떠 있어야 함).

```bash
# ── 운영계 서버 (:5501) ──
cd /workspace/llm-serving/vllm
./start.sh up prd-pii-gemma  # gemma vLLM (GPU0)  →  ./start.sh up 6501  (게이트웨이)
cd ../pii
bash start.sh up 5501        # 프록시 (외부 :5501 인수, NER 동반 기동)

# ── 연구계 서버 (:5015) ──
#   up gemma → up 6015 → bash start.sh up        (인자 없으면 5015)

bash start.sh status         # NER + 프록시 health
bash start.sh down 5501      # 특정 프록시만 중지 (NER은 로딩 비용이 커 유지)
bash start.sh down all       # 프록시 전부 + NER 중지
```

> 🔒 외부엔 **프록시(:5015/:5501)만** 열고 게이트웨이(:6015/:6501)·vLLM(:7070/:7080)·NER(:8911/:8901)은 외부 차단해야 우회 불가. 인스턴스 yaml이 `host: 0.0.0.0`이면 특히 주의.

## 정확성 평가

```bash
cd pii && python tests/eval_pii.py      # 한국어 합성 케이스셋, 타입별 precision/recall + 과탐
```

## 파일 구성

| 파일 | 역할 |
|------|------|
| `proxy.py` | 외부 포트 인수 프록시 (in/out 검사 → 게이트웨이 포워딩, 스트리밍 post) |
| `ner_server.py` | 비정형 PII NER 서버 (GPU3, transformers token-classification. 추론은 스레드풀 + 세마포어로 동시 처리 — 상한은 `ner.yaml`의 `max_concurrency`) |
| `config.py` | 프록시 설정 스키마 (pydantic, 오타 시 기동 단계 fail-fast) |
| `hooks.py` | 타입 우선순위/한글 라벨 병합 |
| `audit.py` | HMAC 감사로그 (평문 미저장) |
| `detectors/structured.py` | 구조화 PII regex + 체크섬 |
| `detectors/ner_client.py` | NER LB union 클라이언트 |
| `detectors/normalize.py` | 전각→반각(NFKC) 정규화 (전각 숫자 등 우회 차단) |
| `configs/` | NER 풀 `ner.yaml`(gpu/models_dir/backends/max_concurrency) · 포트별 프록시 설정 `proxy.yaml`(5015)·`proxy.5501.yaml`(5501) · `proxy.e2e.yaml`(테스트) · 키 상세 `_SCHEMA.txt` |
| `NOTICE.md` | NER 모델 라이선스 고지 |
| `pii_model_research.md` | 한국어 PII 모델 조사·실측 평가 |
