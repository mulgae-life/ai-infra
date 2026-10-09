# PII/DLP 게이트웨이 도입 플랜

> 작성일: 2026-06-04 | 대상: `llm-serving/` vLLM 서빙 (한화손해보험 보험 AI, 폐쇄망)
> 목표: 사내 정책상 LLM 서빙 앞단에 DLP/PII 가드를 **우회 불가능하게** 의무화. 요청(in)·응답(out) 양방향 검사.
> 근거: 코드 직접 정독 + PII 오픈소스 리서치 워크플로우(에이전트 14, 출처 본문 확인) 종합.

---

## 아키텍처 흐름 (시각)

### 전체 토폴로지 (네트워크 · 포트 · 컨테이너)

```
            🌐 AI 서비스들 (챗봇/RAG)  — 호출 주소·인증 변경 0
                     │  http://<ip>:5015/v1/chat/completions
                     ▼
        🔒 방화벽 (5015 한 포트만 인바운드 오픈)   ← 운영은 5501
                     │
 ┌───────────────────┼──────────────  gemma 컨테이너  ───────────────────┐
 │                   ▼                                                     │
 │   ┌─────────────────────────────────────────┐                         │
 │   │  🛡️ PII 프록시   (0.0.0.0:5015)           │  ← 외부 유일 입구        │
 │   │      ① 요청(in) 검사   ③ 응답(out) 검사   │                         │
 │   │   ┌─ 구조화 PII: regex+체크섬 (CPU, 인라인)│  주민·사업자·카드·계좌  │
 │   │   └─ 비정형 PII: NER LB 풀 호출 ──────────┐│  이름·주소·조직         │
 │   └───────────────────────────────│──────────┘│                         │
 │                  │ (검사 통과 body)│           │                         │
 │                  ▼                 ▼           │                         │
 │   ┌──────────────────────┐   ┌─────────────────────── GPU3 (42GB) ──┐  │
 │   │ 🚪 게이트웨이          │   │  🤖 NER 서버 풀 (least-conn + health) │  │
 │   │  127.0.0.1:6015       │   │   ├ townboy  :8901                    │  │
 │   │  (내부로 한 칸 이동)   │   │   ├ townboy  :8902   ← multi-replica  │  │
 │   │  LB·admission·웜업     │   │   └ vmaca123 :8911                    │  │
 │   │  (기존 코드 그대로)    │   └───────────────────────────────────────┘  │
 │   └──────────┬───────────┘                                              │
 │              ▼                                                           │
 │   🧠 vLLM gemma  (127.0.0.1:7070, GPU0·1 TP2)  ← 기존 그대로            │
 └─────────────────────────────────────────────────────────────────────────┘

핵심: 외부에 열린 5015 = PII 프록시뿐. 게이트웨이·vLLM은 컨테이너 내부 + 방화벽 비공개
      → AI 서비스가 PII 검사를 건너뛸 경로가 없음 (enforcement 성립)
```

### 요청 1건 처리 (in → 추론 → out)

```
 ① 요청 검사 (in)
 AI서비스 ─▶ 프록시:5015
    │  messages[].content 추출
    ├─▶ 구조화 regex+체크섬 ─┐  주민/사업자/카드/계좌
    └─▶ NER 풀(GPU3) ────────┤  이름/주소/조직     (병렬 → span 병합)
                             ▼
         고유식별정보(주민·카드) → 🚫 차단(422, 게이트웨이 미전송)
         이름·주소 등            → 🎭 마스킹 후 통과
                             ▼ (정제된 body)
 ② 추론
    프록시 ─▶ 게이트웨이:6015 ─▶ vLLM gemma ─▶ 응답 생성
 ③ 응답 검사 (out)
    vLLM ─▶ 게이트웨이 ─▶ 프록시
    │  content + reasoning + tool_calls 추출 → (in과 동일 엔진 풀)
    │  검출 시 🎭 마스킹
    │  [스트리밍이면 SSE 프레임 누적 버퍼링 후 검사 → 경계까지만 flush]
                             ▼
                         AI 서비스 (정제된 응답)
```

### 흐름 원칙 4가지

| | 원칙 |
|--|------|
| **단일 입구** | 방화벽이 여는 5015 = PII 프록시. 우회 경로 없음 (enforcement) |
| **2-엔진 병렬** | 구조화=regex+체크섬(결정적·CPU) / 비정형=NER(GPU3 LB 풀). 한 모델로 다 안 함 |
| **양방향** | 같은 엔진 풀을 in(프롬프트)·out(응답)이 공유 |
| **fail-closed** | NER 풀 장애 시 차단(누출 방지). 단 구조화 regex는 풀과 무관하게 계속 동작 → graceful degrade |

---

## 0. 확정 사실 (정독으로 검증 — 추측 아님)

| 사실 | 출처 (라인) |
|------|------|
| 게이트웨이는 yaml `host:0.0.0.0` + `port:5015`로 uvicorn 바인딩 | `vllm_gateway.py` L1178-1183, `gateways/5015.yaml` L27-29 |
| `port`는 "방화벽/보안그룹 오픈 대상", `host:0.0.0.0`은 "외부 접속 허용" (의도된 설계) | `gateways/5015.yaml` L24-25 주석 |
| AI 서비스는 **인증 없이** `http://<ip>:5015/v1/chat/completions` 호출 | `VLLM_API_GUIDE.md` L7, L65 |
| 메인 모델 = `gemma-4-31B-it` (멀티모달) | `VLLM_API_GUIDE.md` L35 |
| chat forward: raw body → admission(L844) → LB(L861) → 백엔드 | `vllm_gateway.py` L830-880 |
| **out 비스트림 검사점** = `resp.json()` 직후 | L891-892 |
| **out 스트림 검사점** = `resp.aiter_bytes()` 순수 바이트 패스스루 (버퍼링 없음) | L938-941 |
| 인증 패스스루만 함 (게이트웨이 자체 인증 없음) | L872-875 |
| `backend_api_key`는 전 게이트웨이에서 주석 처리(미설정) | `gateways/{5015,5501}.yaml` L78-80 |
| 런처 `_LAUNCHER_KEYS`에 `host` 없음 → instances yaml `host`가 vLLM 바인딩 | `vllm_server_launcher.py` L70, L144-150 |
| 연구계 gemma = `user.sh --root --service-port 5015`, 운영계 = 5501 | `aws/SETUP_GUIDE.md` §3-1 |
| thinking 응답은 `reasoning` 키로 분리(out 검사 대상) | `VLLM_API_GUIDE.md` L216, L591 |

**운영 토폴로지 (대표님 확인)**: 방화벽이 호스트 **5015(연구)/5501(운영)만** 인바운드 오픈. vLLM 백엔드 포트는 컨테이너 내부 + 방화벽 비공개라 외부 직타 불가. → **방화벽이 이미 1차 enforcement**.

---

## 1. enforcement 모델 (핵심 설계)

외부에 열린 단일 포트(5015/5501)에 **PII 프록시를 앉히고, 게이트웨이를 컨테이너 내부 포트로 한 칸 물린다.**

```
[방화벽: 5015만 오픈]
  → PII 프록시 (0.0.0.0:5015, 외부 유일 입구)   ← AI 서비스는 변경 0
        in 검사 → forward → out 검사
        → 게이트웨이 (127.0.0.1:6015, 내부 이동)  ← gateways/5015.yaml port만 변경
              → vLLM 백엔드 (127.0.0.1:7070)       ← 기존 그대로 (방화벽 비공개)
        ↕ korean-pii 사이드카 (127.0.0.1:8900)
```

- **AI 서비스 호출 변경 0** (여전히 `:5015`), **방화벽 규칙 변경 0**
- enforcement 성립: 외부에 닿는 `:5015` = 프록시뿐. 게이트웨이/vLLM은 컨테이너 내부 + 방화벽 비공개 → 우회 경로 없음
- 게이트웨이 코드 **무수정** (port yaml 1줄 변경 제외). PII 정책은 프록시·사이드카에 격리 → 결합도 최소
- **운영(5501)도 동일 패턴** — 프록시가 5501 인수, 게이트웨이 내부 이동

> ⚠️ 검증 에이전트의 "backend_api_key/게이트웨이 토큰 필수화(AND)"는 **퍼블릭 클라우드 위협모델 기준**. 폐쇄망 + 방화벽 단일 포트 + 내부 신뢰 경계에서는 **선택적 심층방어로 격하**. 같은 컨테이너 내 프로세스의 게이트웨이 내부포트 직접 접근만 잔여 리스크이며, 필요 시 backend `--api-key`를 보강으로 추가(프록시가 키를 흡수, AI 서비스는 무인증 유지).

---

## 2. PII 엔진 스택 (HF 13종 모델카드 본문 정독 + 라이선스 배제 기능우선 — 대표님 지시)

> HF 13종 본문 검증 결과: **전부 한국 구조화 PII(주민/사업자/카드)를 전용 라벨로 못 잡거나 `account_number` 하나로 뭉침** → 2-엔진 구조 확정.
> 라이선스는 사내 폐쇄망 정책상 기능 우선(운영 투입 시점에 법무 검토). HfApi 직접 질의로 13종 후보 확보, WebFetch로 모델카드 본문 정독.

| 역할 | 채택 | 근거 |
|------|------|------|
| 구조화 PII | regex + 체크섬 (Presidio 보강) | 주민·사업자·카드·계좌. 결정적 = 모델 대체 불가. 13종 중 한국 구조화 PII 전용 라벨 보유 모델 전무 |
| 비정형 NER 1순위 | `townboy/kpfbert-kdpii` (110M) | 한국 PII **33종 최광범위**(이름·주소·조직·생년월일+정형까지), F1 0.92, stable transformers GPU 즉시 |
| 비정형 NER 비교 | `vmaca123/korean-pii-ner-v3` (335M) | 이름·주소·조직 3축 전용 + **통짜주소(ADDRESS_FULL)** → 설계 원칙 정확 부합, 주소 조각 문제 없음 |
| 경량 베이스라인 | `amoeba04/koelectra-privacy` (14M) | 초경량 stable, 빠른 PoC 기준선 |

**하락/탈락**: `FrameByFrame/privacy-korean`(조직 미탐 + 이름 recall 0.69 + MoE 서빙부담), `openai/privacy-filter`·`fastino/gliner2`·`OpenMed` 계열(한국어 미학습/저성능 Macro F1 0.42), `Leo97 modu-ner`(정형 PII 라벨 전무).

**공통 필수 게이트**: 보고 F1(0.92~0.9998)은 자체 합성·과적합 의심 → **보험 실데이터 200~500건 홀드아웃에서 이름·주소·조직 entity-level recall ≥0.95** 통과해야 운영. false negative(누출)를 오탐보다 우선하는 지표(recall@high-precision).

**구조화 PII 검증 규칙**:
- 주민등록번호: 가중치 `[2,3,4,5,6,7,8,9,2,3,4,5]` Mod-11. **단 2020.10 이후 발급분은 뒷 6자리 임의화로 체크섬 무효** → 13자리 형식 정규식 우선, 체크섬은 오탐 저감 보조
- 사업자등록번호: 가중치 `[1,3,7,1,3,7,1,3,5]` + 9번째×5/10 보정, Mod-10
- 카드: Luhn (Presidio 내장)
- 계좌/전화/여권: 표준 체크섬 부재 → 정규식 + 이름 근접 조합탐지로 오탐 저감

---

## 2.5 NER GPU 서빙 + LB

- **GPU3 실측 42.2GB 여유**(`nvidia-smi` 확인, L40S 46GB×4 / gemma=GPU0·1 TP2). NER(≤1.4GB)에 과충분 → **multi-replica** 적재.
- token-classification은 **vLLM 비대상**(생성형 전용) → `transformers AutoModelForTokenClassification(device='cuda', bf16)` 또는 ONNX Runtime/Triton 서빙.
- **LB**: 게이트웨이 `LoadBalancer`(least-conn, `vllm_gateway.py` L295) + `HealthChecker` 코드를 NER 백엔드용으로 **이식**. 단 기존 게이트웨이는 chat/audio 전용이라 그대로 못 붙임 → **NER 전용 서버+LB 별도 구축**(코드 패턴만 재사용).
- 프록시가 **구조화 regex(인라인 CPU) + NER LB 풀(GPU3)을 병렬 호출 후 span 병합**. in/out 동일 NER 풀 공유.
- **다층 방어(union)**: 단일 NER recall 한계 보완 — 이름(성씨 사전+호칭/관계어 ~씨/~님/피보험자), 조직(법인 접미사 ㈜·생명·화재·손해보험 사전), 주소(행정구역 읍·면·동·로·길 사전+우편번호 정규식)를 NER과 OR 결합.

---

## 3. in/out 흐름 (프록시 내부 — 게이트웨이 무수정)

**in (요청)**: 프록시 핸들러에서 raw body `json.loads`(실패 400) → `messages[].content` 추출 → 2단 검사 → block(422)/mask(Presidio Anonymizer)/tokenize → 게이트웨이 forward. **게이트웨이 admission보다 앞단**이라 차단 시 슬롯·추론·과금 0 소모.

**out 비스트림**: 게이트웨이 JSONResponse 수신 → `choices[].message.content` + **`reasoning`(thinking) + `tool_calls.arguments`** 검사 → mask/block.

**out 스트림(난이도 최고)**: 게이트웨이 SSE를 프록시가 재수신 → `\n\n` 프레임 파싱 → `delta.content`/`reasoning` str 누적 버퍼 → 경계 안전구간까지 flush.

**2단 검사 (지연 완화)**: 구조화 PII(주민/사업자/카드)는 프록시 **인라인 regex+체크섬**으로 즉시 판정(사이드카 왕복 0). 비정형(이름 등)만 korean-pii 사이드카 위임. **스트리밍 핫패스에서는 사이드카 미호출** (인라인 regex만) — NER은 in·비스트림·완결후 audit에만.

---

## 4. 검증에서 나온 필수 보완 (4렌즈 적대적)

**⏱️ 스트리밍 성능** (severity High):
- `hold_chars` 보류 윈도우가 체감 TTFT 가산 (Gemma 88ms→300ms+). **고정 32 ❌ → "엔티티 최대길이(카드 19)+여유 ≈ 27자"로 최소화** + prefix-incremental 매칭(부분일치 시에만 보류)
- `delta.content`만 스캔 시 **`reasoning`/`tool_calls` PII 100% 누락** → 전 텍스트 채널 스캔
- UTF-8 멀티바이트 청크 분할 → `codecs.getincrementaldecoder('utf-8')` (글자깨짐 방지)
- `stream_mode=post`(완결후 1회)는 스트리밍 死 → 고민감 검출 시점부터 그 응답만 동적 전환

**🇰🇷 한국어 recall** (severity High):
- **korean-pii가 주소(`주소`) entity를 탐지 못 함** → 행안부 도로명주소 DB(폐쇄망 반입) 기반 전용 recognizer 추가 + 행정구역 사전 + 접미사(로/길/동/타워) 휴리스틱
- 전각숫자(`１２３`)·공백 구분자·비표준 구분자 우회 → `normalize()`(NFKC + 구분자 제거) 레이어 **검사 전 필수**
- 부분마스킹 잔존(`끝 4자리 3456`) 준식별자 → mask+audit 카테고리 추가
- NER F1 0.84는 정제 코퍼스 기준, 채팅체 OOD에선 더 낮음 → 이름 단독도 역할키워드(수신인/예금주/대표자) 동반 시 mask 승격

**🔧 운영** (severity High):
- `fail-closed` + 단일 사이드카 = SPOF → 구조화는 regex로 graceful degrade(사이드카 무관), NER만 사이드카. circuit-breaker로 flap 격리. 사이드카 auto-restart
- 기동 순서: 사이드카 ready 후 프록시 트래픽 수용(`/health` 폴링). cold-start 동안 503+Retry-After
- 감사로그: 평문 미저장. HMAC-SHA256(value, env `PII_AUDIT_SALT`) 앞 8-12자 + 부분마스킹만. forward body·raw body 로깅 절대 금지

---

## 5. 구현 로드맵

| Phase | 내용 | 비고 |
|-------|------|------|
| 0 | **포트 인수 준비**: `gateways/5015.yaml` port 5015→6015(내부), host 127.0.0.1. `ss -ltnp`로 바인딩 검증 | enforcement 기반 |
| 1 | GPU3에 `townboy`+`vmaca123` NER 서버(transformers cuda bf16) 기동 + LB 골격(게이트웨이 LoadBalancer 이식) + **보험 실데이터 recall 평가**(이름·주소·조직 ≥0.95) + 추론 지연 실측 | 모델 결정 게이트 |
| 2 | `pii/` 패키지: client.py / hooks.py / config.py / audit.py + 2단 검사 + 구조화 정규식 단위테스트(2020.10 체크섬 무효 케이스 포함) | God 모듈 회피 |
| 3 | `pii_proxy.py` in_flow (0.0.0.0:5015) → 게이트웨이 forward. 무효입력·block·mask 통합테스트 먼저 | 목표기반 |
| 4 | out 비스트림: content+reasoning+tool_calls 검사. fail-closed 테스트 | |
| 5 | **out SSE 재중계**: 프레임 누적+normalize+incremental decode+경계 flush. 청크경계 분할 PII 테스트 | 난이도 최고 |
| 6 | 설정·기동 통합: `pii/<port>.yaml`, start.sh 라우팅 확장. 운영 5501 동일 적용 | |
| 7 | 전 채널: audio(L972) 응답, realtime WS(L1055) | |
| 8 | 운영 강화: 헬스/알림, fail-closed E2E, TTFT 측정(in/out on·off 4조합), audit 평문 grep 검증, recall 게이트 | work-verify |

---

## 5.5 구현·검증 현황 (PoC 완료, 2026-06-04)

**구현** (`llm-serving/pii/`, 11파일):
`detectors/{normalize,structured,ner_client}.py` · `hooks.py` · `config.py` · `audit.py` · `ner_server.py` · `proxy.py` · `configs/{proxy,proxy.e2e}.yaml` · `start.sh` · `tests/×4`

**테스트**: 단위·통합·HTTP E2E **29/29 통과**. 실서버 Full E2E(GPU3 NER 2종 + 게이트웨이 + gemma 추론)로 검증:
- 주민/카드 입력 → **422 차단**(게이트웨이 미전송, 추론·과금 0)
- 이름(vmaca)·전화(regex) → 마스킹 후 실추론 → `반가워요, [이름]님([전화번호])!`
- out 응답 마스킹 동작 + 감사로그 평문 미저장(fingerprint)
- **과마스킹 발견·완화**: "서울"(지명)·"대한민국"(국가)이 주소로 마스킹 → `LC_PLACE`/`LCP_COUNTRY` 제외 + **주소 구체성 필터**(도로명/번지/동/숫자) → "서울입니다" 정상, 구체주소("…테헤란로 152")는 마스킹 유지

**남은 작업 (배포 전)**:
- env `PII_AUDIT_SALT` 설정 (현재 `NOSALT`)
- 게이트웨이 `5015→6015` 이동 + 프록시 `5015` 인수 (운영 적용, gateways yaml 1줄 + 프록시 기동)
- **보험 실데이터 recall 게이트**(이름·주소·조직 ≥0.95) — 운영 투입 조건
- 스트리밍 `buffer` 모드(현 `post`=완결 후 1회) — TTFT 최적화
- NER 서버 GPU3 상주 기동을 `start.sh`/운영 절차에 통합 (lsof 미동작 → PID 기반 종료 유의)

---

## 6. PoC로 확정해야 할 미검증 항목 (정직 고지)

- KoELECTRA CPU 추론 지연 **ms 미측정** → fail-closed timeout 전제. Phase 1에서 부하 하 실측 후 timeout 설정
- `korean-pii` 조합탐지 거리 임계값 README 미공개 → 코드 확인 필요
- knowledgator GLiNER 한국어 성능 모델카드 미기재 → 채택 보류(자체 PoC 전)
- **recall 게이트**(운영 투입 조건): 적대적 한국어 PII 셋에서 주민/카드 1.0, 주소/이름 ≥0.9, 변형셋 ≥0.95 미달 시 배포 보류

---

## 7. 확정된 결정 / 남은 항목

**확정 (대표님)**:
- 토폴로지: PII 프록시·NER 서버를 **gemma 컨테이너 내부**(5015 단일 매핑 활용)
- 액션: in 고유식별정보=**차단**, 이름 등=마스킹 / out=**마스킹**
- backend `--api-key`: 후순위 (방화벽 단일 포트가 1차 enforcement)
- 순서: **연구계(5015) PoC → 운영계(5501)**
- NER 모델: **`townboy/kpfbert-kdpii`(1순위) + `vmaca123/korean-pii-ner-v3`(비교)**, GPU3 서빙
- 라이선스: **기능 우선**(운영 투입 시점 법무 검토)

**남은 항목 (PoC 중 결정)**:
- townboy 단독 vs vmaca 단독 vs 둘 union — 보험 실데이터 recall로 확정
- NER 서빙: `transformers` cuda vs ONNX/Triton (지연 실측 후)
- replica 수 / NER용 admission(동시성) 파라미터 튜닝
