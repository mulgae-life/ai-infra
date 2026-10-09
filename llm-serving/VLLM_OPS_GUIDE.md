# vLLM SLM 운영 가이드 (운영자용)

> **대상**: 서버 운영자 (기동/중지, 설정 튜닝, 모델 교체, 트러블슈팅, QA)
> **API 호출 사용법**: [`VLLM_API_GUIDE.md`](VLLM_API_GUIDE.md) 참고.

> **서비스 구성 — 2-모드 운용**: 각 진입 포트는 **① 비PII 모드**(게이트웨이가 곧 외부 입구 — **현재 기본**)와 **② PII 모드**(프록시가 같은 포트를 인수, 게이트웨이는 내부로) 중 하나로 운영합니다. 외부 호출 주소는 모드와 무관하게 불변(gemma 연구 `:5015`/운영 `:5501`, qwen 연구 `:5016`/운영 `:5502`).
>   - **연구계 비PII (현재 프로파일)**: `:5015`(`gateways/5015.yaml`) ← `gemma-26b.yaml` (Gemma 4 26B-A4B fp8_per_tensor, GPU 0·1 TP2, vLLM `:7071`, MTP 끔) **또는** `qwen.yaml` (Qwen3.8 27B FP8, GPU 0·1 TP2, vLLM `:7080`). 두 인스턴스 모두 `gateway_port: 5015`라 기동한 쪽이 백엔드가 됩니다 — GPU가 겹쳐 동시 기동은 불가. **현재는 `qwen.yaml`**.
>   - **연구계 컨테이너의 vLLM (10-09~)**: 0.31.0 가상환경 `/home/hjjo/venvs/vllm-0.31`(시험장 검증 조합과 버전이 모두 같음). `~/.bashrc`의 `SERVING_VLLM_BIN`을 런처가 읽어 이 환경의 `vllm`으로 띄운다(없으면 PATH의 `vllm`, 서버 이미지는 지정하지 않음). `~/.local`의 옛 nightly는 임베딩 서버(:8020)가 계속 쓴다. 옛 버전으로 되돌리기: `env -u SERVING_VLLM_BIN ./start.sh restart qwen`
>   - 연구계 PII: `:5015`(프록시) → gw `:6015` ← `gemma.yaml` (Gemma 4 31B, vLLM `:7070`). `:5016`/gw `:6016`은 `qwen.yaml`이 5015로 옮겨간 뒤 매칭 인스턴스가 없어 비어 있습니다.
>   - **운영계 비PII (현재 운용)**: `:5501`(`gateways/5501.yaml`) ← `prd-gemma.yaml` (Gemma 4 31B, GPU 0, vLLM `:7070`, MTP 끔)
>   - 운영계 PII: `:5501`(프록시) → gw `:6501` ← `prd-pii-gemma.yaml` · `:5502`(프록시) → gw `:6502` ← `prd-pii-qwen.yaml` (Qwen3.8 27B FP8, GPU 0, vLLM `:7080`)
>   - 📌 **아래 기동·테스트 명령 예시는 연구계 비PII(`:5015`/`gemma-26b.yaml`) 기준**입니다. 운영계는 `:5501` / `prd-gemma` 등으로 치환하세요.
> **인프라**: AWS L40S 46GB × 4장.
> **vLLM 버전**: 0.31.0 (운영 이미지 `aws/Dockerfile.llm`, 연구계 :5015 가상환경). 2026-10 이전은 0.20.2 + nightly(dev251)였고, 버전업 시험 기록은 [`vllm/tests/results/vllm-0.31-ab.md`](vllm/tests/results/vllm-0.31-ab.md)에 있습니다. 본문에 "0.19.0 기준"으로 남은 설명은 그때 소스로 확인한 것입니다.

> 🆕 **2026-04-30 구조 변경**: 단일 `vllm_config.yaml` + `vllm_gateway_config.yaml` → **인스턴스 단위 `instances/<name>.yaml`** + **게이트웨이 단위 `gateways/<port>.yaml`**. 게이트웨이는 인스턴스 yaml의 `gateway_port` 메타 키로 backends를 자동 매칭(`discover_from`). 구식 yaml은 `agent-guide/.archive/2026-04-30_vllm-config-migration/`에 보존.
>
> 🆕 **포트 자동 회피**: 인스턴스 yaml의 `port`는 **hint**. launcher가 사용 중인 포트면 +1, +2 … 비어있는 첫 포트로 자동 회피하고, 실제 포트를 `instances/.runtime/<name>.json`에 기록한다. 게이트웨이는 이 파일을 우선 참조하여 backends를 등록하므로 **복붙 LB 시나리오에서 port를 깜빡해도 자동으로 다른 포트에 띄우고 게이트웨이가 LB**된다.
>
> 🆕 **2026-06-04 PII/DLP 가드 (enforcement)**: 사내 정책으로 LLM 앞단에 PII 가드가 의무화됨. 외부에 열린 단일 포트를 **PII 프록시가 인수**하고 게이트웨이는 내부 포트로 한 칸 물러난다 — 연구계 `:5015`→게이트웨이 `:6015`, 운영계 `:5501`→게이트웨이 `:6501`. **외부 호출 주소(`:5015`/`:5501`)는 불변**. PII 프록시·NER 서버 코드는 [`pii/`](pii/), 설계는 [`agent-guide/plans/pii-dlp-gateway.md`](../agent-guide/plans/pii-dlp-gateway.md), 기동 절차는 아래 [§7.9](#79-pii-가드-포함-기동)를 참고. ⚠️ 게이트웨이 yaml 파일명·`gateway.port`가 6015/6501로 바뀌었으므로 `./start.sh up 6015`처럼 **새 포트로 호출**한다.
>
> 🆕 **2026-07-21 2-모드 운용 전환**: PII 가드는 **선택 모드**가 됨 — 현재 연구·운영 모두 **비PII 모드**(게이트웨이가 외부 포트에 직접, PII 스택 미기동)로 운용하고, PII 모드는 필요 시 프록시+NER을 올려 전환한다. 연구계 비PII 프로파일은 `gemma-26b.yaml`(26B-A4B) ↔ `gateways/5015.yaml` 페어, 운영계는 `prd-gemma.yaml` ↔ `gateways/5501.yaml`. 모델 증분 동기화는 `./start.sh download`([§8.2](#82-다운로드최신-동기화--startsh-download)).

---

## 📑 목차

6. [시스템 구조](#6-시스템-구조)
7. [서버 기동·중지](#7-서버-기동중지)
8. [모델 준비 (다운로드)](#8-모델-준비-다운로드)
9. [설정 파일](#9-설정-파일)
10. [API 운영 레퍼런스](#10-api-운영-레퍼런스)
11. [모델 관리](#11-모델-관리)
12. [Qwen3.6/3.8 고급 기능](#12-qwen3638-고급-기능)
13. [트러블슈팅 & 운영 주의](#13-트러블슈팅--운영-주의)
14. [QA 테스트](#14-qa-테스트)
15. [참고 자료](#15-참고-자료)

> 📝 § 번호는 사용자 가이드(`VLLM_API_GUIDE.md` §1~§4)와 겹치지 않도록 6부터 시작합니다.

---

## 6. 시스템 구조

### 6.1 전체 구성도

**모드 ① 비PII (현재 기본)** — 게이트웨이가 곧 외부 입구:

```
chatbot-poc (.env)
  PROVIDER=huggingface
  HF_BASE_URL=http://...:5015/v1   ※ 운영계는 :5501
                │
                ▼
┌──────────────────────────────┐
│ Gateway :5015 (0.0.0.0)      │  gateways/5015.yaml  ※ 운영계 5501.yaml
│   discover_from: ../instances│  • LB  • 헬스체크  • 웜업
└──────────────────────────────┘
                │
                ▼
┌──────────────────────────────┐
│ vLLM :7071 (GPU 0·1, TP2)    │  instances/gemma-26b.yaml
│   gateway_port: 5015 ────────┘  ※ 운영계 prd-gemma.yaml (:7070, GPU 0)
│   model: google/gemma-4-26B… │
└──────────────────────────────┘
```

**모드 ② PII** — 프록시가 같은 외부 포트를 인수하고 게이트웨이는 내부로 물러난다 (운영계 prd-pii 페어 기준):

```
┌──────────────────────────────┐    ┌──────────────────────────────┐
│ PII :5501 → Gateway :6501    │    │ PII :5502 → Gateway :6502    │
│ gateways/6501.yaml (내부전용) │    │ gateways/6502.yaml (내부전용) │
│   discover_from: ../instances│    │   discover_from: ../instances│
│   • LB  • 헬스체크  • 웜업   │    │   • LB  • 헬스체크  • 웜업   │
└──────────────────────────────┘    └──────────────────────────────┘
                │                                │
                ▼                                ▼
┌──────────────────────────────┐    ┌──────────────────────────────┐
│ vLLM :7070 (GPU 0)           │    │ vLLM :7080 (GPU 0)           │
│ instances/prd-pii-gemma.yaml │    │ instances/prd-pii-qwen.yaml  │
│   gateway_port: 6501 ────────┘    │   gateway_port: 6502 ────────┘
│   model: gemma-4-31B-it      │    │   model: Qwen3.8-27B-FP8     │
└──────────────────────────────┘    └──────────────────────────────┘
```
> ⚠️ PII 모드에서는 gemma·qwen 모두 외부 입구가 **PII 프록시**, 게이트웨이는 **내부 전용**이다(아래 🔒 박스). 연구계는 gemma `:5015`→`:6015` / qwen `:5016`→`:6016`, 운영계는 gemma `:5501`→`:6501` / qwen `:5502`→`:6502`. 같은 외부 포트에 두 모드를 동시에 쓸 수 없으므로 **모드는 포트당 택일**이다(예: 연구계 `:5015`는 비PII면 게이트웨이, PII면 프록시).

- 각 게이트웨이 yaml은 자기 포트만 알고, `discover_from`(`../instances`)에서 `gateway_port == 자기 포트`인 인스턴스 yaml을 자동 매칭해 backends로 등록한다.
- **LB 시나리오**: 같은 `gateway_port`를 갖는 인스턴스 yaml을 추가하면 같은 게이트웨이 아래 vLLM 여러 대가 LB된다(단, vLLM `port`가 겹치면 게이트웨이 기동 시 ValueError로 거부).
- **격리**: 다른 `gateway_port`를 가진 인스턴스끼리는 서로 영향 없음.
- **외부 노출**: **비PII 모드(현재 기본)**는 게이트웨이 포트(연구 :5015 / 운영 :5501)가 외부에 열린다(vLLM 포트는 내부 전용). **PII 모드**에서는 프록시(gemma :5015/:5501, qwen :5016/:5502)만 열고 게이트웨이(:6015/:6016/:6501/:6502)·vLLM 포트는 내부 전용이어야 enforcement가 성립한다.

> 🔒 **PII 가드 적용 토폴로지** (위 모드 ② 구성도의 `:5501` prd-pii-gemma 페어 기준):
> ```
> AI서비스 → :5501 (PII 프록시, 외부 유일 입구)
>              │  in 검사(주민/카드 차단·이름/주소/전화 마스킹)
>              ▼
>           :6501 (게이트웨이, 127.0.0.1)  ── LB·웜업·헬스체크
>              ▼
>           :7070 (vLLM prd-pii-gemma, GPU 0)
>              ▲
>      + NER 서버 2종 (GPU3, :8911 vmaca123 / :8901 townboy) ← 프록시가 비정형 PII 검사 시 호출
>              │  out 검사(응답 마스킹) 후 클라이언트로 반환
> ```
> 방화벽이 외부 단일 포트(:5501)만 열어, PII 프록시를 거치지 않고는 게이트웨이/vLLM에 도달할 수 없다(enforcement). 연구계(:5015/:5016)·운영계(:5501/:5502)는 격리된 별도 서버이며, 각 서버가 자기 localhost(:8911/:8901)에 NER을 띄워 자기 프록시만 호출한다(연구↔운영 NER 물리 분리).

### 6.2 구성요소 역할

| 구성요소 | 역할 | 파일 |
|---------|------|------|
| **vLLM 서버** | 실제 모델 추론 수행 (GPU 점유) | `vllm_server_launcher.py` |
| **Gateway** | 클라이언트 요청 분배 + 헬스체크 + 웜업 + 자동 디스커버리 | `vllm_gateway.py` |
| **start.sh** | `instances/*.yaml` + `gateways/*.yaml` 일괄/단일 기동·중지 | `start.sh` |
| **인스턴스 yaml** | vLLM 1대 = 1 yaml. 모델/포트/GPU + `gateway_port` 메타 | `instances/<name>.yaml` |
| **게이트웨이 yaml** | 게이트웨이 1대 = 1 yaml. `discover_from`으로 백엔드 자동 매칭 | `gateways/<port>.yaml` |

### 6.3 왜 게이트웨이가 있나요?

- **단일 엔드포인트**: 클라이언트는 외부 진입점(`:5015` gemma / `:5016` qwen)만 알면 됩니다. 내부에서 게이트웨이·vLLM 인스턴스가 몇 개든 상관없습니다.
- **헬스체크**: 죽은 인스턴스는 라우팅 풀에서 자동 제외.
- **CUDA 웜업**: 첫 요청 지연(cold start)을 제거.
- **프리픽스 캐시 웜업**: 시스템 프롬프트를 미리 KV 캐시에 적재 → TTFT(첫 토큰 대기시간) 감소.
- **자동 디스커버리**: 인스턴스 추가 시 yaml 한 파일만 두면 게이트웨이 재기동 시 자동 등록.

> 게이트웨이 없이도 vLLM에 직접 붙을 수 있습니다. 그때는 `HF_BASE_URL=http://...:7070/v1` 처럼 vLLM 포트를 가리키면 됩니다. (부하분산·웜업 혜택은 사라집니다.)

### 6.4 Qwen PII 적용

Qwen도 gemma와 **동일하게 PII 프록시 구성이 준비**되어 있습니다(2026-06-08). PII 모드에서는 연구계 `:5016`, 운영계 `:5502`가 외부 입구이고, 게이트웨이는 내부(`:6016`/`:6502`)로 물러납니다.

> 📌 2026-07-21부터 PII는 **선택 모드**입니다(현재 비PII 운용). 아래 표는 **PII 모드 기준** 서술이며, qwen은 비PII 게이트웨이(`gateways/5016.yaml`)가 아직 없어 **PII 모드 구성만 존재**합니다 — 비PII로 qwen을 열려면 게이트웨이 yaml 신설이 필요합니다(백로그).

| 항목 (PII 모드) | gemma (:5015/:5501) | Qwen (:5016/:5502) |
|------|--------------------|--------------------|
| 외부 입구 | PII 프록시 | PII 프록시 |
| 게이트웨이 | 내부 :6015/:6501 | 내부 :6016/:6502 |
| PII 검사 | ✅ in/out | ✅ in/out |
| NER 풀 | GPU3 :8911/:8901 | 같은 서버 풀 공유 |

구성: `gateways/6016.yaml`·`6502.yaml`(내부 전용) + `instances/prd-pii-qwen.yaml`(gateway_port 6502) + `pii/configs/proxy.5016.yaml`·`proxy.5502.yaml`. 같은 서버의 gemma·qwen 프록시는 NER 풀(8911/8901)을 공유하므로 NER은 한 번만 기동된다. 기동은 [§7.9](#79-pii-가드-포함-기동) 또는 gemma와 동일 패턴(안쪽부터: vLLM → 게이트웨이 → 프록시).

> ⚠️ 연구계 쪽 `qwen.yaml`은 2026-08-18(`5a8fd1b`)에 `gateway_port`가 6016에서 5015로 옮겨갔다. 그래서 **`:6016`에는 매칭되는 인스턴스가 없다** — 연구계 PII로 qwen을 다시 열려면 인스턴스 yaml을 하나 더 만들어야 한다.

> STT(:5017/:5018)는 음성 전용이라 텍스트 PII 정책 대상이 아니며 모드 구분 없이 항상 게이트웨이가 외부 입구다.

---

## 7. 서버 기동·중지

### 7.1 권장 방법 — start.sh

가장 쉽고 안전한 방법입니다. `start.sh`가 `instances/*.yaml`과 `gateways/*.yaml`을 자동 순회합니다.

```bash
cd /workspace/llm-serving/vllm

./start.sh up                # 인자 없음 → 전체 적용 confirm 프롬프트 [y/N]
./start.sh up all            # 전체 인스턴스 + 게이트웨이 기동 (확인 없이)
./start.sh up <name>         # 단독 기동 (자동 라우팅 — 아래 표 참조)
./start.sh down              # 인자 없음 → 전체 중지 confirm 프롬프트 [y/N]
./start.sh down all          # 모든 인스턴스 + 게이트웨이 중지 (확인 없이)
./start.sh down <name>       # 단독 중지
./start.sh status            # 상태 확인
./start.sh restart           # 인자 없음 → 전체 재시작 confirm 프롬프트 [y/N]
./start.sh restart <name>    # 단일 대상 재시작 (내부적으로 down→up)
./start.sh logs              # 전체 인스턴스+게이트웨이 로그 tail -F (기본 -n 50)
./start.sh logs <name>       # 단일 대상 tail -F (인스턴스/게이트웨이 자동 라우팅)
./start.sh logs --lines 200  # 초기 라인 수 오버라이드 (-n N alias 가능)
./start.sh download <name>   # 모델 다운로드/최신 동기화 (서빙 미터치, §8 참조)
./start.sh test              # 기동된 게이트웨이 전부 기능 QA (미기동은 SKIP, §14 참조)
./start.sh test <name>       # 단일 대상 (인스턴스는 게이트웨이 미경유 직접 호출)
./start.sh speed <name>      # 속도 측정 — TTFT/TPS 매트릭스 (§14.3.1)
./start.sh traffic <포트>    # 하드 부하 — 게이트웨이만, 대상 명시 필수 (§14.3)
```

> ⚠️ **안전 정책**: 무인자 호출은 [y/N] 기본 No로 묻는다 (다른 모델/게이트웨이를 실수로 stop시키는 사고 방지). 자동화 스크립트/cron 등 비대화 환경에서는 prompt 띄울 곳이 없으므로 무인자 호출이 거부되며 `'all'` 또는 이름을 명시해야 한다.

**`<name>` 자동 라우팅 규칙**

| `<name>` 형태 | 매칭 yaml | 동작 |
|--------------|-----------|------|
| 모델명 (예: `gemma`, `qwen`) | `instances/<name>.yaml` | 인스턴스만 처리, 게이트웨이 미터치 |
| 포트 숫자 (예: `5015`, `5016`) | `gateways/<name>.yaml` | 게이트웨이만 처리, 인스턴스 미터치 |
| `all` (명시) | 전체 | 인스턴스 + 게이트웨이 모두 (확인 없이) |
| 생략 (무인자) | 전체 | [y/N] 프롬프트 후 전체 — non-tty 환경은 거부 |
| 매칭 없음 | — | 즉시 에러 + 인스턴스/게이트웨이 후보 목록 출력 |

> 인스턴스 yaml은 모델명, 게이트웨이 yaml은 포트 숫자로 명명되어 충돌 가능성이 없습니다. 만일 충돌하면(`instances/X.yaml`과 `gateways/X.yaml` 동명) 에러로 멈춥니다.

### 7.2 GPU 배치 규칙

각 인스턴스 yaml의 `gpus` + `tensor_parallel_size` 조합으로 인스턴스 1대의 GPU 점유가 결정됩니다. 멀티 인스턴스/LB는 yaml을 추가하는 방식으로 확장합니다.

| `gpus` | `tensor_parallel_size` | 결과 |
|--------|------------------------|------|
| `[0]` | 1 | GPU 0 단독 |
| **`[0, 1]`** | **2** | GPU 0,1 텐서 병렬 (TP=2, 큰 모델용) |
| `[0, 1, 2, 3]` | 4 | GPU 0,1,2,3 텐서 병렬 (TP=4) |

DP(Data Parallel) 시나리오는 인스턴스 yaml을 복사해서 `gpus`만 다르게 한 새 yaml을 추가하는 방식으로 구성합니다 (같은 `gateway_port` 아래 LB).

> **TP vs DP**
> - **TP (Tensor Parallel)**: 한 모델을 여러 GPU에 쪼개 얹음. 큰 모델을 돌릴 수 있지만 GPU 간 통신 비용 있음.
> - **DP (Data Parallel)**: GPU마다 똑같은 모델을 올림. 동시 처리량이 늘지만 GPU당 메모리가 충분해야 함. 본 구조에선 인스턴스 yaml을 복사하여 같은 `gateway_port`로 묶음.

### 7.3 기동 순서 (start.sh 내부)

1. `instances/*.yaml`(또는 단일 인스턴스 yaml) 파싱 → 인스턴스 단위로 launcher 호출
2. launcher가 yaml의 메타 키(`gateway_port`, `gpus`, `download_dir`)를 vllm serve 인자에서 제외하고 vLLM 기동
3. `gateways/*.yaml`(또는 단일 게이트웨이 yaml) 파싱 → 게이트웨이 기동
4. 게이트웨이가 `discover_from`으로 인스턴스 yaml 스캔 → `gateway_port == 자기포트` 매칭 → backends 등록
5. 같은 `gateway_port` 그룹 내 vLLM `port` 중복 검증 → 중복 시 ValueError로 즉시 중단
6. 게이트웨이가 각 백엔드 `/health` 폴링 → CUDA 웜업 → 프리픽스 캐시 웜업
7. 최소 1대 ready 시 게이트웨이 포트에서 요청 수신

### 7.4 인스턴스 동적 추가/제거

**복붙 LB 시나리오 (강력 추천 흐름)**:
```bash
# 1. 기존 인스턴스 yaml을 복사 (port를 깜빡 안 바꿔도 OK)
cp instances/gemma-26b.yaml instances/gemma-26b_replica.yaml
# (필요한 키만 수정: gpus 등. port는 그대로 둬도 launcher가 자동 회피.
#  gateway_port가 같아야 같은 게이트웨이 아래 LB로 묶인다)

# 2. 새 인스턴스 기동 (launcher가 yaml의 port를 hint로, 사용 중이면 +1)
./start.sh up gemma-26b_replica

# 3. 게이트웨이 재기동 → instances/.runtime/*.json 발견 → 자동 LB 등록
#    (게이트웨이 yaml 이름이 5015이면 down/up도 5015 명시)
./start.sh down 5015
./start.sh up 5015
```

**메커니즘**:
- launcher가 yaml의 `port` 값으로 socket binding 시도 → 사용 중이면 `+1`, `+2` ... 비어있는 첫 포트 사용
- 실제 사용 포트를 `instances/.runtime/<name>.json`에 기록 (PID, model 등 함께)
- 게이트웨이가 `discover_from` 시점에 이 파일을 우선 참조 → 자동 LB
- launcher 종료 시 runtime 파일 삭제 (SIGKILL 등 비정상 종료는 다음 launcher 시작 시 PID 살아있음 검사로 stale 정리)

**기타**:
- **HealthChecker 자동 감지**: 이미 backends에 등록된 인스턴스의 다운/복구는 게이트웨이 재기동 없이 자동 처리.
- **수동 오버라이드**: 게이트웨이 yaml에 `backends:` 리스트를 명시하면 `discover_from`보다 우선 (escape hatch / 디버깅용).
- **runtime 파일 직접 확인**: `cat instances/.runtime/<name>.json` 으로 실제 사용 중 포트와 PID 확인.

### 7.5 개별 기동 (start.sh 없이)

```bash
cd /workspace/llm-serving/vllm

# 1. vLLM 인스턴스 기동 (yaml `-c` + GPU 인자) — 연구계 비PII 예시; 운영은 prd-gemma로 치환
python vllm_server_launcher.py -c instances/gemma-26b.yaml -g 0,1

# 2. 게이트웨이 기동 (비PII 모드는 게이트웨이가 곧 외부 입구)
python vllm_gateway.py -c gateways/5015.yaml

# 백그라운드 실행
mkdir -p logs
nohup python vllm_gateway.py -c gateways/5015.yaml > logs/gateway_5015.log 2>&1 &
```

> 🔒 **PII 모드**에서는 게이트웨이가 내부 포트(6015/6016)로 물러나고 외부 입구(:5015/:5016)는 **PII 프록시까지 기동**해야 열립니다 — [§7.9](#79-pii-가드-포함-기동) 참고.

### 7.6 더 로우레벨한 방법 — vllm serve 네이티브

vLLM v0.18.0+는 YAML config를 네이티브로 지원합니다. 단, **인스턴스 yaml의 메타 키(`gateway_port`, `gpus`, `download_dir`)는 vllm serve가 인식하지 못하므로** 보통은 launcher 사용을 권장합니다(launcher가 자동 필터). 굳이 네이티브로 가야 하면 메타 키를 수동 제거한 임시 yaml을 만들어야 합니다.

```bash
cd /workspace/llm-serving/vllm

# 모델 로컬 경로를 positional 인자로 직접 넘김
CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  vllm serve /models/LLM/google/gemma-4-31B-it --config /tmp/gemma_vllm_only.yaml
# (gemma_vllm_only.yaml은 instances/gemma.yaml에서 메타 키 제거 버전)
```

### 7.7 3가지 기동 방법 비교

| | `vllm serve` 네이티브 | Python 런처 | **`start.sh` (권장)** |
|---|---|---|---|
| 모델 경로 | 전체 경로 직접 지정 | HF ID → 로컬 경로 자동 | yaml에서 자동 |
| 모델 자동 다운로드 | ❌ 사전 다운로드 필요 | ✅ 자동 또는 `--download-only` | ✅ 자동 |
| CUDA 설정 | `CUDA_VISIBLE_DEVICES=0` 직접 | `-g 0` 또는 환경변수 | yaml `gpus` 키 → start.sh가 launcher에 전달 |
| HF 오프라인 플래그 | 환경변수 직접 | 자동 적용 | 자동 적용 |
| 메타 키 필터링 | 수동 제거 필요 | `_LAUNCHER_KEYS` 자동 필터 | launcher 경유로 자동 |
| 다중 인스턴스 / LB | 수동 | 수동 | yaml 추가 + 재기동 자동 |
| 게이트웨이 | 별도 기동 필요 | 별도 기동 필요 | 함께 기동 |
| 중지 방법 | `kill` | `kill` | `./start.sh down <name>` |

### 7.8 보안 주의

게이트웨이 자체에는 **인증 기능이 없습니다**. 공개망에 직접 노출하지 말고 AWS Security Group, 방화벽, nginx 등으로 접근을 제한하세요.

> 🔒 **PII enforcement 방화벽 체크리스트 (PII 모드 시 필수)**: PII 가드는 "외부엔 PII 프록시만 열려 있다"는 전제 위에서만 우회 불가능합니다. PII 모드로 운용하는 서버는 다음을 보안그룹/방화벽에 **고정**하세요. (비PII 모드는 게이트웨이 포트만 열고 vLLM 포트를 내부 전용으로 두면 됩니다.)
> - ✅ 외부 오픈: **PII 프록시만** — gemma `:5015`(연구)/`:5501`(운영), qwen `:5016`(연구)/`:5502`(운영).
> - ❌ 외부 차단: **게이트웨이 `:6015`/`:6016`/`:6501`/`:6502`**, **vLLM `:7070`/`:7080`**, **NER `:8911`/`:8901`**. 하나라도 외부에서 닿으면 PII 검사를 건너뛰는 직행 경로가 생깁니다(인스턴스 yaml `host: 0.0.0.0`이면 특히 주의 — 가능하면 게이트웨이/vLLM 동일 호스트에서 `127.0.0.1` 바인딩 권장).
> - ✅ **STT `:5017`/`:5018`은 PII 비경유**(음성 전용, 모드 무관).
> - 📋 **bypass 헤더 주의**: 현재 5015·5501은 기본 활성(`allow_bypass: true`, 토큰 미설정)이라 **헤더 `X-PII-Mode: bypass` 하나로 검사가 우회**됩니다. PII 강제가 필요한 배포는 해당 프록시에서 `allow_bypass: false`로 끄거나 `PII_BYPASS_TOKEN`을 설정하세요. 우회 요청은 감사로그 `action=bypass`로 기록되니 비율을 주기적으로 모니터링하세요.

vLLM에 `--api-key`를 설정한 경우:

- **클라이언트 → 게이트웨이**: `Authorization` 헤더를 백엔드에 패스스루.
- **게이트웨이 내부 요청**: 웜업·모델 감지 등 내부 요청은 `backend_api_key` 설정값을 사용.

```yaml
# gateways/<port>.yaml
backend_api_key: "your-secret-key"   # vLLM --api-key 값과 일치
```

### 7.9 PII 가드 포함 기동

> 📌 이 절은 **모드 ② PII** 전용이다. 현재 기본인 **비PII 모드**는 PII 스택 없이 두 단계로 끝난다:
> ```bash
> ./start.sh up gemma-26b      # ① vLLM 인스턴스 (운영계: prd-gemma)
> ./start.sh up 5015           # ② 게이트웨이 = 외부 입구 (운영계: 5501)
> ```

PII 적용 게이트웨이는 **3계층(PII 프록시 → 게이트웨이 → vLLM)**을 안쪽부터 기동한다. 연구계/운영계는 격리된 별도 서버이며, 각 서버가 자기 NER 서버(GPU3, :8911/:8901)를 띄운다(아래 두 블록은 각각 다른 서버에서 실행).

```bash
# ── 연구계 (외부 :5015) ──
cd /workspace/llm-serving/vllm
./start.sh up gemma          # ① vLLM 인스턴스 (GPU 0,1)
./start.sh up 6015           # ② 게이트웨이 (내부 127.0.0.1:6015)
cd ../pii
bash start.sh up             # ③ NER 2종(GPU3) + PII 프록시 (외부 :5015 인수)  ※ 기본=5015

# ── 운영계 (외부 :5501) — GPU 여유 확보 후 ──
cd /workspace/llm-serving/vllm
./start.sh up prd-gemma      # GPU 0
./start.sh up 6501           # 게이트웨이 (내부 127.0.0.1:6501)
cd ../pii
bash start.sh up 5501        # 운영 서버 NER(GPU3, 이미 떠있으면 skip) + 5501 프록시

# ── 상태 / 중지 ──
cd ../pii && bash start.sh status        # NER + 프록시(5015/5501)
bash start.sh down 5015                  # 특정 프록시만 (NER 유지)
bash start.sh down all                   # 프록시 전부 + NER
```

> - **PII 감사로그 salt**: `pii/start.sh`가 `configs/audit.salt`(없으면 자동 생성, 권한 600)에서 읽어 `PII_AUDIT_SALT`로 주입한다. salt는 환경별 시크릿이라 git/S3 동기화에서 제외된다(`.gitignore`, 루트 `start.sh`).
> - **검사 정책**: 주민·카드 = 차단(422), 이름·주소·전화·조직·계좌·사업자·이메일 = 마스킹. 설정은 `pii/configs/proxy.yaml`(5015)·`proxy.5501.yaml`(5501).
> - **정확성 회귀 평가**: `cd pii && python tests/eval_pii.py` (한국어 합성 케이스셋, 타입별 precision/recall + 과탐).

---

## 8. 모델 준비 (다운로드)

### 8.1 자동 다운로드 (기본)

처음 기동할 때 로컬에 모델이 없으면 `vllm_server_launcher.py`가 `huggingface_hub.snapshot_download` API로 자동 다운로드합니다. 별도 명령이 필요 없습니다. **로컬에 모델이 이미 있으면 `up`은 네트워크를 전혀 보지 않습니다** (폐쇄망 보장) — 최신 동기화는 §8.2의 `download` 명령으로만 일어납니다.

> Qwen3.6 / Gemma 4 모두 Apache 2.0(또는 Gemma 라이선스)이라 **HF 토큰이 필요 없습니다**. Llama처럼 gated 모델은 `HF_TOKEN=hf_xxx`를 환경변수로 넘기세요.

### 8.2 다운로드/최신 동기화 — `./start.sh download`

```bash
cd /workspace/llm-serving/vllm

./start.sh download <name>   # 인스턴스 1개 (본체 + drafter 함께)
./start.sh download all      # 전체 인스턴스
```

- 로컬에 모델이 **없으면** 전체 다운로드, **있으면** HF 최신 리비전과 **증분 동기화** — 변경 파일만 받습니다(가중치 무변경 시 chat_template 등 소형 파일만, 수 초).
- `speculative_config`의 drafter(`${model}-assistant` 치환 포함)도 같은 호출에서 함께 처리됩니다.
- 서빙 프로세스는 건드리지 않습니다. 실행 중인 서버에 반영하려면 `./start.sh restart <name>`.

**폐쇄망 운영 절차**: 네트워크 일시 개방 → `./start.sh download <name>` → 네트워크 차단 → `./start.sh up <name>`. `up`은 네트워크 미접근이므로 차단 후에도 정상 기동합니다. 네트워크 개방이 불가한 환경은 외부망 PC에서 받아 S3 경유로 모델 디렉토리를 이관합니다.

<details>
<summary>launcher 직접 호출 (start.sh 없이)</summary>

```bash
# 1) 인스턴스 yaml의 model / download_dir 사용 (download 명령과 동일 경로)
python vllm_server_launcher.py -c instances/gemma.yaml --download-only

# 2) Gated 모델
HF_TOKEN=hf_xxx python vllm_server_launcher.py -c instances/<name>.yaml --download-only

# 3) 모델 override (yaml의 model을 무시하고 다른 모델 받기)
python vllm_server_launcher.py -c instances/qwen.yaml --download-only -m Qwen/Qwen3.6-27B-FP8   # yaml은 3.8
```

> `--download-only`는 내부적으로 `download_model()`을 호출하므로 **실제 서빙과 동일한 경로 규칙**을 씁니다. `./start.sh download`는 이 호출의 wrapper입니다.

</details>

### 8.3 운영 규칙

- 네트워크가 되는 환경(또는 일시 개방 시점)에서 `./start.sh download`로 먼저 받는다.
- 실제 서빙은 항상 `HF_HUB_OFFLINE=1` + `TRANSFORMERS_OFFLINE=1` (런처·start.sh는 자동 적용).
- 다운로드 경로는 반드시 `{download_dir}/{HF repo_id}` 레이아웃을 지킬 것. 예:
  - config: `model: Qwen/Qwen3.6-27B-FP8`, `download_dir: /models/LLM`
  - 실제 경로: `/models/LLM/Qwen/Qwen3.6-27B-FP8`
- 모델(특히 chat template) 갱신 후에는 `tests/test_vllm_server.py`로 툴콜·reasoning 카테고리 회귀 확인.

### 8.4 다운로드 확인

```bash
MODEL_DIR="/models/LLM/Qwen/Qwen3.6-27B-FP8"

test -f "$MODEL_DIR/config.json"              # 모델 config
test -f "$MODEL_DIR/tokenizer_config.json"    # 토크나이저
find "$MODEL_DIR" -maxdepth 1 \( -name '*.safetensors' -o -name '*.bin' \)  # 가중치 파일
```

### 8.5 Python 런처 전용 옵션

| 옵션 | 설명 |
|------|------|
| `-g, --gpu` | `CUDA_VISIBLE_DEVICES` (예: `-g 0`, `-g 0,1`) |
| `-m, --model` | HF 모델 ID 또는 경로 (config override) |
| `-c, --config` | 인스턴스 yaml 경로 (예: `instances/gemma.yaml`) |
| `--online` | 서빙 시 HF Hub 접근 허용 (기본: 오프라인) |
| `--download-only` | 다운로드만 수행, 서버는 실행 안 함 |

런처는 yaml의 메타 키(`gateway_port`, `gpus`, `download_dir`)를 `_LAUNCHER_KEYS`로 자동 필터하여 vllm serve에 전달하지 않습니다.

그 외 인자는 모두 `vllm serve`에 그대로 전달됩니다.

---

## 9. 설정 파일

설정은 **인스턴스 단위**(`instances/<name>.yaml`)와 **게이트웨이 단위**(`gateways/<port>.yaml`)로 분리됩니다.

```
llm-serving/vllm/   (비PII/PII 페어가 파일명으로 구분된다 — prd-* = 운영, 무접두 = 연구)
├── instances/
│   ├── gemma-26b.yaml      (gateway_port: 5015, port: 7071, gpus: [0,1])  # 연구 비PII (현재 기본)
│   ├── gemma.yaml          (gateway_port: 6015, port: 7070)               # 연구 PII (외부는 프록시 :5015)
│   ├── qwen.yaml           (gateway_port: 5015, port: 7080, gpus: [0,1])  # 연구 비PII (gemma-26b와 택일)
│   ├── prd-gemma.yaml      (gateway_port: 5501, port: 7070, gpus: [0])    # 운영 비PII (현재 운용)
│   ├── prd-pii-gemma.yaml  (gateway_port: 6501, port: 7070, gpus: [0])    # 운영 PII (외부는 프록시 :5501)
│   └── prd-pii-qwen.yaml   (gateway_port: 6502, port: 7080, gpus: [0])    # 운영 PII (외부는 프록시 :5502)
└── gateways/
    ├── 5015.yaml           (외부 직접 노출 0.0.0.0 — 연구 비PII)
    ├── 5501.yaml           (외부 직접 노출 0.0.0.0 — 운영 비PII)
    ├── 6015.yaml · 6016.yaml   (내부전용 127.0.0.1 — 연구 PII)
    └── 6501.yaml · 6502.yaml   (내부전용 127.0.0.1 — 운영 PII)
```

### 9.1 설정 우선순위

```
CLI 인자  >  instances/<name>.yaml  >  vLLM 기본값
```

게이트웨이의 backends 결정 우선순위:

```
1) gateways/<port>.yaml의 backends 명시 (수동 오버라이드 — escape hatch)
2) gateways/<port>.yaml의 discover_from + 인스턴스 yaml의 gateway_port 매칭 (자동)
   둘 다 미설정 시 ValueError로 fail-fast.
```

### 9.2 인스턴스 yaml (`instances/<name>.yaml`) 주요 설정

두 인스턴스 yaml(`gemma.yaml`, `qwen.yaml`)은 **주석/섹션 구조 100% 동일**, 모델/리소스 값만 다릅니다(복붙 확장 가능).

| 키 | 분류 | 설명 |
|----|------|------|
| **`gateway_port`** | 메타 | **이 인스턴스가 소속될 게이트웨이 포트.** vllm serve에는 전달되지 않고(`_LAUNCHER_KEYS` 필터), 게이트웨이의 `discover_from`이 이 키로 매칭. |
| `model` | 모델 | HF 모델 ID. 런처가 `download_dir`과 조합해 로컬 경로 자동 해석 |
| `download_dir` | 모델 | `/models/LLM` — 모델 로컬 저장 루트 |
| `quantization` | 모델 | `fp8` (사전 양자화 체크포인트는 자동 감지되지만 명시해도 무해) |
| `dtype` | 모델 | `auto` (모델 config.json 따름) |
| **서버** | | |
| `host` | 서버 | `0.0.0.0` (외부 접근 허용 시) |
| `port` | 서버 | vLLM 포트(내부). 게이트웨이가 backends로 등록. **같은 `gateway_port`로 묶인 인스턴스끼리 중복 시 ValueError**. |
| `uvicorn_log_level` | 서버 | `info` |
| **GPU/메모리** | | |
| `gpus` | GPU | 인스턴스 1대가 점유할 GPU 번호 목록. `_LAUNCHER_KEYS`로 vllm serve에서 제외 (런처가 `CUDA_VISIBLE_DEVICES`로 변환) |
| `tensor_parallel_size` | GPU | TP 크기 |
| `gpu_memory_utilization` | GPU | 0.85 (멀티모달 비중 큼) ~ 0.92 (모델 가중치 큼). (1-util) 외부 영역은 vision encoder transient 활성화 메모리에 사용 |
| **추론** | | |
| `max_model_len` | 추론 | 컨텍스트 길이. 두 인스턴스 모두 65536 (안정 기동 우선) |
| `max_num_seqs` | 추론 | 동시 처리 시퀀스 상한. 멀티모달 encoder cache 용량과 맞춤 |
| `max_num_batched_tokens` | 추론 | 배치당 최대 토큰. ⚠️ `encoder_cache_size`로도 복제됨 (scheduler.py:235). 이미지 1장 ≈ 16,384 tokens |
| `seed` | 추론 | `42` |
| **Thinking** | | |
| `default_chat_template_kwargs` | 모델 | `{enable_thinking: false}` (챗봇 응답 지연 줄이기) |
| └ `reasoning_effort` | 모델 | **Qwen3.8 전용.** 사고 길이 기본값 `medium`. 템플릿 기본 `xhigh`는 사고 지시문을 최대로 주입해 생성량이 늘어 챗봇엔 과다 → 명시 고정. 허용값 `xhigh`/`medium`/`low` 외에는 HTTP 400 [12.5](#125-reasoning_effort-사고-길이-제어-qwen38) |
| `reasoning_parser` | 모델 | `gemma4` / `qwen3` 등 모델별 |
| **멀티모달** | | |
| `mm_encoder_tp_mode` | 멀티모달 | `data` — 비전 인코더 DP 처리 |
| `mm_processor_cache_type` | 멀티모달 | `shm` — 프로세스 간 shm FIFO 공유 |
| `mm_processor_kwargs` | 멀티모달 | 모델별: Gemma 4 `{ max_soft_tokens: 1120 }` / Qwen3-VL `{}` |
| `limit_mm_per_prompt` | 멀티모달 | `{ image: 2 }` |
| `language_model_only` | 멀티모달 | `false` (이미지 입력 허용) |
| **안정성** | | |
| `async_scheduling` | 안정성 | `false` (scheduler ↔ worker race 방지) |
| ~~`disable_chunked_mm_input`~~ | 안정성 | *(Mamba-hybrid 모델 — 예: Qwen3.6 — 에서 절대 설정 금지)* [13.3](#133-disable_chunked_mm_input이-qwen36에-금지인-이유) |
| **캐시** | | |
| `enable_prefix_caching` | 캐시 | `true` |
| `kv_cache_dtype` | 캐시 | `auto`. FP8 KV는 `fp8_e4m3`로 변경 시 용량 2배 |
| **Tool Calling** | | |
| `enable_auto_tool_choice` | tool | `true` |
| `tool_call_parser` | tool | 모델별: `gemma4` / `qwen3_xml` 등 |

자세한 설명(라인 참조, 크래시 사후 분석, GPU 메모리 매트릭스 등)은 `instances/<name>.yaml` 내 한국어 주석에 있습니다.

### 9.3 게이트웨이 yaml (`gateways/<port>.yaml`) 주요 설정

게이트웨이 yaml(비PII 직접 노출분 `5015.yaml`·`5501.yaml`과 STT `5017.yaml`·`5018.yaml`은 외부 `0.0.0.0`, PII 내부분 `6015.yaml`·`6016.yaml`·`6501.yaml`·`6502.yaml`은 내부 전용 `127.0.0.1`)도 주석/구조 100% 동일, 포트·바인딩 host만 다릅니다.

| 키 | 분류 | 설명 |
|----|------|------|
| `gateway.host` | 서버 | `0.0.0.0` |
| `gateway.port` | 서버 | 게이트웨이 포트. 비PII분(5015/5501)·STT(5017/5018)는 외부, PII분(6015/6016/6501/6502)은 내부 전용. `discover_from`의 매칭 키. |
| `gateway.log_level` | 서버 | `info` |
| **`discover_from`** | 디스커버리 | 인스턴스 yaml 디렉토리(상대 경로). `../instances` |
| `backends` | 디스커버리 | (선택) 수동 명시 시 `discover_from`보다 우선 — escape hatch |
| `backend_api_key` | 인증 | vLLM `--api-key` 설정 시 내부 요청에 사용 |
| `health_check.interval_seconds` | 헬스체크 | `10` |
| `health_check.unhealthy_threshold` | 헬스체크 | `3` (연속 N회 실패 → unhealthy) |
| `health_check.healthy_threshold` | 헬스체크 | `1` (연속 N회 성공 → healthy → 웜업 재실행) |
| `warmup.enabled` | 웜업 | `true` (CUDA 웜업) |
| `warmup.boot_poll.timeout_seconds` | 웜업 | `900` (모델 로딩 포함 상한) |
| `warmup.inference.prompt` | 웜업 | 더미 추론 프롬프트 |
| `prefix_cache_warmup.enabled` | 캐시 웜업 | `true` |
| `prefix_cache_warmup.system_prompt` | 캐시 웜업 | 웜업 시 KV에 적재할 시스템 프롬프트 (보험 챗봇용) |
| `http_client.timeout_seconds` | HTTP | `300` (추론 요청 전체 타임아웃) |

### 9.4 .env 설정 (chatbot-poc 측)

```env
PROVIDER=huggingface
# 페어 게이트웨이 중 선택:
HF_BASE_URL=http://43.203.142.247:5015/v1     # Gemma 페어
# HF_BASE_URL=http://43.203.142.247:5016/v1   # Qwen 페어
CHAT_MODEL=gemma-4                          # 모델을 교체해도 이 값은 그대로
RERANKER_MODEL=gemma-4
```

> **`CHAT_MODEL`은 반드시 `served_model_name`과 일치**해야 vLLM이 요청을 받습니다. 전 인스턴스가 `gemma-4`로 고정돼 있으므로 어느 백엔드로 붙든 이 값이면 됩니다 ([§10.4](#104-모델-교체-호환-계층-compat)).

### 9.5 📝 참고: YAML `bool false` 전달 제약 (런처 내부)

> 런처가 자동 처리하므로 운영 시 직접 신경 쓸 일은 없음 — 내부 동작 참고용.

vLLM의 YAML 파서는 `key: true`를 `--key` 플래그로 바꿉니다. 0.31.0부터는 `key: false`도 `--no-<key>`로 바꾸지만, 키 이름을 하이픈으로 바꾸기 전에 등록된 옵션을 조회합니다(`vllm/utils/argparse_utils.py:615`). 그래서 `async_scheduling`처럼 밑줄이 든 키는 `--no-async_scheduling`으로 조회돼 여전히 버려집니다. 기본값이 `None`인 필드는 CLI로 전달되지 않으면 auto-enable 로직에 의해 `True`로 뒤집힙니다. 옛 nightly는 `false`를 아예 무시했습니다.

런처는 `async_scheduling: false`를 감지하면 `--no-async-scheduling` CLI 플래그를 직접 주입하여 이 제약을 우회합니다. 덕분에 YAML에 `false`로 써도 실제로 `false`가 적용됩니다.

---

## 10. API 운영 레퍼런스

> 사용자(클라이언트) 호출 가이드는 [`VLLM_API_GUIDE.md`](VLLM_API_GUIDE.md)를 참고하세요. 본 섹션은 운영자에게만 의미 있는 **게이트웨이 디버그 엔드포인트**, **모델 검증용 복붙 예시**, **모델 교체 호환 계층**을 다룹니다.

### 10.1 게이트웨이 전용 엔드포인트

vLLM 표준 OpenAI API 외에 게이트웨이가 추가로 노출하는 운영용 엔드포인트입니다.

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | 게이트웨이 자체 + 백엔드 ready 카운터 (`{ready, total}`) |
| GET | `/server-status` | 백엔드 서버 상세 상태 대시보드 |

> 🔒 **PII 모드 접근 포트 주의**: 비PII 모드(현재 기본)에서는 `:5015`/`:5501`이 곧 게이트웨이라 `/server-status`를 그대로 조회할 수 있습니다. **PII 모드**에서는 이 엔드포인트들이 내부 게이트웨이(`:6015` 등)에 있습니다 — PII 프록시는 `/health`와 `/v1/*`만 노출하므로 `:5015/server-status`는 404이고, 운영 호스트에서 `127.0.0.1:6015`로 조회하세요. (Qwen도 동일 — `127.0.0.1:6016`.)

```bash
# 비PII 모드(현재 기본): 외부 포트가 곧 게이트웨이
curl http://localhost:5015/server-status
# PII 모드: 게이트웨이는 내부 전용 → 운영 호스트에서 로컬 조회
curl http://127.0.0.1:6015/server-status
curl http://127.0.0.1:6016/server-status
```

```json
{
  "gateway": {"uptime_seconds": 3600.0},
  "backends": [{
    "url": "http://127.0.0.1:7070",
    "is_healthy": true,
    "is_ready": true,
    "active_connections": 2,
    "consecutive_failures": 0
  }],
  "overload": {
    "enabled": true,
    "max_inflight_requests": 20,
    "max_queue_size": 20,
    "queue_timeout_seconds": 60.0,
    "retry_after_seconds": 5,
    "inflight_requests": 0,
    "queued_requests": 0,
    "accepted_total": 0,
    "rejected_total": 0,
    "queue_timeout_total": 0
  },
  "ready_count": 1,
  "total_count": 1
}
```

`is_healthy`(헬스체크 OK) ≠ `is_ready`(웜업 완료) — 둘 다 true여야 라우팅 풀에 포함됩니다. `consecutive_failures`가 누적되면 게이트웨이가 해당 백엔드를 풀에서 제외합니다.
`overload.max_inflight_requests`는 vLLM에 즉시 넘길 요청 수이고, `overload.max_queue_size`는 초과 요청을 게이트웨이에 대기시킬 수입니다. 대기열 포화 또는 `queue_timeout_seconds` 초과 시 게이트웨이는 429와 `Retry-After`를 반환합니다.

### 10.2 Qwen3.6 Thinking 모델 검증용 복붙 예시

> Qwen 인스턴스(`:5016`) 단독 검증/디버그 시 사용. 사용자 일반 호출 가이드는 [`VLLM_API_GUIDE.md` §3.2](VLLM_API_GUIDE.md#32-thinking-모드-사고-과정-분리) 참고.

**Qwen3.6 공식 권장 샘플링 파라미터** (모델 카드 기준):

| 모드 | temperature | top_p | top_k | min_p | presence_penalty |
|------|:-----------:|:-----:|:-----:|:-----:|:----------------:|
| Thinking · 일반 | 1.0 | 0.95 | 20 | 0.0 | **1.5** |
| Thinking · 정밀 코딩 | 0.6 | 0.95 | 20 | 0.0 | 0.0 |
| Instruct · 일반 | 0.7 | 0.8 | 20 | 0.0 | **1.5** |
| Instruct · reasoning | 1.0 | 1.0 | 40 | 0.0 | **2.0** |

> `top_p`/`top_k`는 `generation_config.json`이 자동 적용되므로 명시 생략 가능. `presence_penalty`는 vLLM 기본 0이라 장문 Thinking에서 반복 붕괴 방지용으로 명시 권장. 한국어 응답에서 언어 혼합이 보이면 1.0~1.2로 낮추세요.

**권장 방식 — JSON 파일 + `-d @`**:

```bash
cat > /tmp/qwen_req.json <<'EOF'
{
  "model": "gemma-4",
  "messages": [
    {"role": "system", "content": "자세하게 답변해줘."},
    {"role": "user", "content": "미국인과 한국인의 차이점 비교 설명해줘"}
  ],
  "max_tokens": 10000,
  "temperature": 1.0,
  "presence_penalty": 1.0,
  "chat_template_kwargs": {"enable_thinking": true}
}
EOF

curl http://43.203.142.247:5016/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d @/tmp/qwen_req.json
```

**한 줄 명령**:

```bash
curl -sS http://43.203.142.247:5016/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"gemma-4","messages":[{"role":"system","content":"자세하게 답변해줘."},{"role":"user","content":"미국인과 한국인의 차이점 비교 설명해줘"}],"max_tokens":10000,"temperature":1.0,"presence_penalty":1.0,"chat_template_kwargs":{"enable_thinking":true}}'
```

**Thinking OFF — 빠른 응답**:

```bash
cat > /tmp/qwen_req_nothink.json <<'EOF'
{
  "model": "gemma-4",
  "messages": [
    {"role": "user", "content": "미국인과 한국인의 차이점 간단히 설명"}
  ],
  "max_tokens": 2000,
  "temperature": 0.7,
  "top_p": 0.8,
  "presence_penalty": 1.5,
  "chat_template_kwargs": {"enable_thinking": false}
}
EOF

curl http://43.203.142.247:5016/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d @/tmp/qwen_req_nothink.json
```

**응답 파싱 (jq)**:

```bash
# 사고 과정 + 최종 답변 모두
curl -sS http://43.203.142.247:5016/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d @/tmp/qwen_req.json | jq '.choices[0].message | {reasoning, content}'

# 최종 답변만
curl -sS http://43.203.142.247:5016/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d @/tmp/qwen_req.json | jq -r '.choices[0].message.content'
```

**자주 하는 실수**:

- `\` 줄바꿈 뒤에 **공백이 붙으면** 이어쓰기가 깨져서 첫 줄만 GET으로 가 `{"detail":"Method Not Allowed"}`가 돌아옵니다. **파일 방식(`-d @`)을 권장**합니다.
- `chat_template_kwargs`는 **top-level 필드**입니다. `extra_body` 래핑 불필요 (단, OpenAI Python SDK는 `extra_body`로 감싸야 전달됨).
- Thinking 토큰이 쉽게 2~4K를 먹으므로 복잡한 질의엔 `max_tokens`를 10,000 이상 잡으세요.

### 10.3 vLLM 인스턴스 직접 호출 (게이트웨이 우회)

게이트웨이 디버깅 시 vLLM 인스턴스에 직접 붙어 게이트웨이 계층(LB·웜업·헬스체크) 영향을 배제할 수 있습니다.

```bash
# Gemma 인스턴스 직접 (내부 포트 :7070)
curl http://127.0.0.1:7070/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemma-4","messages":[{"role":"user","content":"ping"}],"max_tokens":20}'

# Qwen 인스턴스 직접 (내부 포트 :7080)
curl http://127.0.0.1:7080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemma-4","messages":[{"role":"user","content":"ping"}],"max_tokens":20}'
```

> 백엔드도 `served_model_name`이 `gemma-4`라 `model` 필드는 어느 인스턴스든 같습니다. 실제로 어떤 모델인지는 `/v1/models`의 `root`로 확인합니다([§10.4](#104-모델-교체-호환-계층-compat)).
> 게이트웨이를 우회하므로 effort 번역이 적용되지 않습니다 — Qwen3.8 백엔드에 `reasoning_effort: high`를 보내면 400입니다.

> ⚠️ vLLM 포트는 **외부 비개방**이라 운영계 호스트 안에서만 접근됩니다. 외부에서 접근하려면 게이트웨이를 거쳐야 합니다.
>
> 🆕 launcher 자동 포트 회피로 실제 포트가 hint와 다를 수 있습니다. 정확한 포트는 `instances/.runtime/<name>.json` 또는 `./start.sh status`로 확인.

---

### 10.4 모델 교체 호환 계층 (compat)

클라이언트가 보는 모델명을 `gemma-4` 하나로 고정한 채 뒤에서 모델을 갈아끼우기 위한 계층입니다. 모델을 바꿔도 챗봇·RAG 클라이언트가 코드를 고치지 않게 하는 것이 목적입니다.

세 부분으로 되어 있습니다.

**① 모델명 고정** — 인스턴스 yaml의 `served_model_name: [gemma-4]`가 담당합니다. 전 인스턴스가 이 값으로 통일돼 있습니다. 다만 이것만으로는 `/v1/models` 응답의 `root`에 실제 체크포인트 경로가 그대로 남으므로, 게이트웨이의 `compat.mask_model_path`가 `root`를 `id`와 같은 값으로 덮습니다.

```bash
# 게이트웨이 경유 — 클라이언트가 보는 값
curl -s http://127.0.0.1:5015/v1/models | jq '.data[0] | {id, root, max_model_len}'
# { "id": "gemma-4", "root": "gemma-4", "max_model_len": 65536 }

# 백엔드 직결 — 운영자가 실제 체크포인트를 확인하는 경로
curl -s http://127.0.0.1:7080/v1/models | jq '.data[0].root'
# "/models/LLM/Qwen/Qwen3.8-27B-FP8"
```

어떤 체크포인트가 떠 있는지는 백엔드 직결 조회, `./start.sh status`, `instances/.runtime/<name>.json` 셋 중 아무거나로 확인합니다. 게이트웨이 로그에도 기동 시 `[127.0.0.1:7080] 모델 경로: ...`로 남습니다.

**② `reasoning_effort` 번역** — 모델마다 받아들이는 값이 다른 유일한 파라미터입니다. 게이트웨이가 백엔드 계열에 맞춰 값을 바꾸거나 제거해서, 클라이언트가 무엇을 보내든 400·422가 나지 않게 합니다.

| 클라이언트가 보낸 값 | Qwen3.8 백엔드 | 그 외 백엔드 |
|---|---|---|
| `minimal`, `low` | `low` | 제거 |
| `medium` | `medium` | 제거 |
| `high`, `xhigh`, `max` | `xhigh` | 제거 |
| `none` | 제거 + `enable_thinking: false` | 제거 |
| 스펙 밖 문자열 | 제거 | 제거 |

적용 결과는 응답 헤더 `X-Effort-Applied`와 게이트웨이 로그에 남습니다. 값이 `dropped`면 현재 백엔드가 이 옵션을 지원하지 않아 무시된 것입니다.

**추론 켜고 끄기 (2026-10-10~)** — 기본은 추론 꺼짐이고, effort를 주면 추론이 켜집니다(OpenAI와 vLLM 0.31의 규칙과 같음).

| 요청 | 추론 |
|---|---|
| 아무것도 안 보냄 | 꺼짐 (인스턴스 기본값) |
| effort만 보냄 (`minimal`~`max`) | **켜짐**, Qwen3.8은 그 강도로. 강도를 지원하지 않는 계열(Gemma)은 켜지기만 함 |
| `chat_template_kwargs.enable_thinking`을 직접 보냄 | 보낸 값을 따름 (effort보다 우선) |
| effort `none` | 꺼짐 (`enable_thinking: true`를 보내도 끔) |
| 스펙 밖 문자열 | 기본값 그대로 (꺼짐) |

게이트웨이가 `enable_thinking`을 명시해 넘기므로 옛 nightly와 0.31에서 같게 동작합니다. 백엔드에 직접 붙으면 이 규칙이 아니라 vLLM 규칙을 따릅니다(0.31은 최상위 effort로만 자동으로 켬).

```bash
# 번역 동작 확인 — 백엔드 직결은 400, 게이트웨이 경유는 200
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:7080/v1/chat/completions \
  -H "Content-Type: application/json" -d '{"model":"gemma-4","messages":[{"role":"user","content":"1+1?"}],
  "max_tokens":20,"reasoning_effort":"high","chat_template_kwargs":{"enable_thinking":true}}'   # 400

curl -s -D - -o /dev/null http://127.0.0.1:5015/v1/chat/completions \
  -H "Content-Type: application/json" -d '{"model":"gemma-4","messages":[{"role":"user","content":"1+1?"}],
  "max_tokens":20,"reasoning_effort":"high","chat_template_kwargs":{"enable_thinking":true}} ' \
  | grep -i 'x-effort-applied'   # x-effort-applied: xhigh
```

**새 모델이 effort를 지원할 때** — 게이트웨이 yaml의 `compat.effort_profiles`에 항목을 추가합니다. 키는 `/v1/models`의 `root` 경로에 대한 부분 문자열(대소문자 무시)입니다.

```yaml
compat:
  effort_profiles:
    qwen3.8: {minimal: low, low: low, medium: medium, high: xhigh, xhigh: xhigh, max: xhigh}
    glm-5:   {minimal: low, low: low, medium: medium, high: high,  xhigh: high,  max: high}
```

비워두면 코드 기본값(`vllm_gateway.py`의 `_DEFAULT_EFFORT_PROFILES` — 현재 `qwen3.8`만 등록)을 씁니다. 등록되지 않은 계열은 effort 미지원으로 보고 필드를 제거합니다.

> ⚠️ **번역은 요청을 조용히 바꿉니다.** `high`를 보낸 클라이언트는 실제로 `xhigh`로 돌았다는 걸 모릅니다. 사고 길이가 기대와 다르다는 문의가 오면 `X-Effort-Applied` 헤더와 게이트웨이 로그의 `reasoning_effort 번역:` 줄을 먼저 확인하세요.
>
> 백엔드 계열 판정은 웜업 때 받아둔 `root`로 합니다. 그 조회가 실패해 `model_root`가 비면 안전을 택해 effort를 항상 제거합니다 — effort가 무시되는 증상이 계속되면 게이트웨이 기동 로그의 `모델 경로:` 줄이 찍혔는지 보세요.

**③ 정체성 프롬프트 주입** — ①이 응답 메타데이터의 모델 식별자를 `gemma-4`로 통일해도, **모델에게 직접 물어보면 학습 때 이름을 답합니다.** 모델의 자기소개는 사후 학습(post-training) 단계에서 가중치에 박히는 것이라 서빙 설정으로는 바꿀 수 없습니다.

```bash
# compat.inject_identity_prompt: false 였을 때 (2026-08-20 실측)
curl -s http://127.0.0.1:5015/v1/chat/completions -H "Content-Type: application/json" \
  -d '{"model":"gemma-4","messages":[{"role":"user","content":"너는 어떤 모델이야?"}],"max_tokens":200}' \
  | jq -r '.choices[0].message.content'
# 저는 알리바바 그룹의 통이 연구소(Tongyi Lab)에서 독자적으로 개발한 ... 큐웬(Qwen)입니다.
```

그래서 게이트웨이가 `/v1/chat/completions` 요청마다 정체성 문구를 `messages` 맨 앞에 얹습니다. 문구는 `vllm_gateway.py`의 `_DEFAULT_IDENTITY_PROMPT`에 있고, 게이트웨이 yaml의 `compat.identity_prompt`로 덮어쓸 수 있습니다.

병합 규칙은 이렇습니다.

| 클라이언트 요청 | 게이트웨이가 보내는 것 |
|---|---|
| system 메시지 없음 | 정체성 문구를 `system` 메시지로 맨 앞에 삽입 |
| `messages[0]`이 system | **그 메시지 안으로 병합** — 정체성 문구가 앞, 클라이언트 지시가 뒤 |
| `messages[0]`이 developer | 위와 같이 병합하되 **role을 `system`으로 눕힘** — Qwen3.8 템플릿은 `developer`를 몰라 `raise_exception('Unexpected message role.')`으로 400을 낸다(실측). 눕히면 Gemma·Qwen 양쪽에서 통한다 |
| system 내용이 멀티모달 배열 | 텍스트 파트 하나를 배열 맨 앞에 삽입 |
| `messages`가 없거나 빈 배열 | 손대지 않음 (백엔드가 낼 400을 그대로 보여주려고) |

> ⚠️ **새 system 메시지를 끼워 넣는 방식은 못 씁니다.** Qwen3.8 챗 템플릿은 선두가 아닌 system 메시지를 만나면 `raise_exception('System message must be at the beginning.')`으로 **400**을 냅니다. Gemma 템플릿은 예외는 안 던지지만 `messages[0]`만 시스템 턴으로 취급하고 나머지는 일반 턴으로 흘립니다. 병합이 유일하게 두 계열 모두에서 동작하는 방식입니다.

정체성 문구가 앞, 클라이언트 지시가 뒤인 순서에는 이유가 있습니다. 뒤에 오는 지시가 우선하므로 클라이언트가 자기 봇 이름을 붙이는 설정은 그대로 살아납니다. 맞추려는 것은 모델 자기소개와 API 모델명의 일치이지 클라이언트의 페르소나 설정이 아닙니다. 실제로 `"너는 '하나봇'이다"`를 보낸 클라이언트는 `"저는 '하나봇'입니다. ... Google에서 개발한 Gemma 4 기반으로 동작합니다"`를 받습니다.

> 📌 **모델명 말고도 백엔드마다 달라지는 응답 필드가 있습니다.** 하나는 고정했고 둘은 그대로 뒀습니다.
>
> - **`system_fingerprint` — 고정.** 기본값(`full`)이면 `vllm-<버전>-tp2-<해시8>`이 실리는데, 이 해시에 모델·양자화·어텐션 백엔드가 들어가서 **백엔드를 교체할 때마다 값이 바뀝니다.** 클라이언트가 이 값을 로그·캐시 키로 쓰고 있으면 교체마다 흔들리므로, 전 인스턴스 yaml에 `fingerprint_mode: custom` + `fingerprint_value: gemma-4`를 넣어 고정값으로 바꿨습니다. 자세한 배경은 아래 [§10.5](#105-system_fingerprint를-고정값으로-두는-이유).
> - **`X-Effort-Applied` — 그대로.** ②의 번역표가 계열별이라 `high`를 보내면 Qwen은 `xhigh`, 그 외는 `dropped`가 돌아옵니다. 백엔드에 따라 값이 달라지지만, 이 헤더가 사고 길이 문의를 추적하는 유일한 수단이라 진단 쪽을 택했습니다.
> - **`logprobs` — 그대로.** 토큰 분절이 백엔드 토크나이저를 따라갑니다. 통일하려면 `logprobs` 자체를 차단해야 하는데 정상 용도를 함께 죽입니다.
>
> 주입 대상은 `/v1/chat/completions` 뿐입니다. `/v1/audio/*`와 `/v1/realtime`은 본문을 그대로 흘려보냅니다 — 지금 뜬 인스턴스는 전부 텍스트·비전 LLM이라 이 경로로 대화가 오가지 않지만, 음성 모델을 올리면 그때 주입 범위를 다시 봐야 합니다.

**끄는 법** — 게이트웨이 yaml에서 `compat.translate_reasoning_effort: false`, `compat.mask_model_path: false`, `compat.inject_identity_prompt: false`. 번역을 끄면 클라이언트 값이 백엔드로 그대로 가서 Qwen3.8에 `high`를 보내면 400이 납니다. 주입을 끄면 위 실측처럼 모델이 학습 때 이름으로 자기소개합니다.

### 10.5 `system_fingerprint`를 고정값으로 두는 이유

`system_fingerprint`는 vLLM이 만든 필드가 아니라 **OpenAI API 표준**입니다. `seed`와 한 쌍으로 쓰라고 만든 것입니다.

```
seed:
  "...repeated requests with the same seed and parameters should return the same
   result. Determinism is not guaranteed, and you should refer to the
   system_fingerprint response parameter to monitor changes in the backend."

system_fingerprint:
  "This fingerprint represents the backend configuration that the model runs with.
   Can be used in conjunction with the seed request parameter to understand when
   backend changes have been made that might impact determinism."
```

의도는 이런 상황입니다. 어제까지 `seed=42`로 재현되던 결과가 오늘 달라졌을 때, 지문 값이 같으면 클라이언트 탓이고 다르면 서버 탓입니다. **결정성이 깨졌을 때 책임 소재를 가르는 표식**입니다.

**우리 환경에서는 이 계약이 성립하지 않습니다.** 직접 재봤습니다(2026-08-20, `:5015` / Qwen3.8-27B-FP8 / `temperature=1.0`).

| 조건 | `seed=777` 반복 결과 |
|---|---|
| 서버가 한산할 때 3회 | 세 번 모두 동일 |
| 동시 요청 9건과 섞어서 3회 | 매번 다름. 한산할 때 값과도 다름 |

연속 배칭에서는 **어떤 요청들과 같은 배치에 묶이느냐**에 따라 부동소수점 누적 순서가 달라집니다. 트래픽이 있는 순간 `seed`는 이미 못 믿으므로, 지문이 지켜줄 계약 자체가 없습니다.

반면 잃는 것은 분명합니다. 해시에 모델과 설정이 들어가므로 **백엔드를 교체하면 값이 바뀝니다.** 클라이언트가 이 값을 로그·캐시 키로 쓰고 있으면 교체마다 흔들리니, 모델명을 `gemma-4`로 고정한 것과 같은 이유로 이 값도 고정하는 편이 낫습니다.

그래서 전 인스턴스 yaml에 이렇게 넣었습니다.

```yaml
fingerprint_mode: custom
fingerprint_value: gemma-4
```

**`none`이 아니라 `custom`을 쓰는 이유** — `none`은 필드를 `null`로 만듭니다. 클라이언트가 이 값을 로그 키나 캐시 키로 쓰고 있으면 `null` 처리를 안 해뒀을 수 있습니다. 고정 문자열이면 필드는 그대로 살아 있고 값만 안 변하므로, 호환은 유지한 채 값만 안정시킵니다. 값을 API 모델명과 같은 `gemma-4`로 둬서 표기도 일관됩니다.

> 📌 **모드는 넷입니다** (`entrypoints/openai/fingerprint.py`). `full`(기본, 버전+병렬도+해시8) / `hash`(병렬도만 제거 — 해시는 그대로라 교체하면 값이 바뀜) / `custom`(고정 문자열) / `none`(필드 생략). **`hash`는 우리 목적에 안 맞습니다.**
>
> 운영자가 실제 백엔드를 확인하는 경로는 그대로입니다. `./start.sh status`, 백엔드 직결 `/v1/models`, `instances/.runtime/<name>.json`, 게이트웨이 기동 로그의 `모델 경로:` 줄 — 넷 다 지문보다 정확합니다.
>
> 이 설정은 **인스턴스 재기동이 필요합니다**(게이트웨이가 아니라 `vllm serve` 인자). 런처는 `_LAUNCHER_KEYS` 밖의 yaml 키를 그대로 넘기므로 별도 배선은 없습니다. 반영되면 기동 로그 `non-default args:` 줄에 `'fingerprint_mode': 'custom'`이 찍힙니다.

---

## 11. 모델 관리

### 11.1 지원 모델 비교

| | **Qwen3.8-27B-FP8 (연구계)** | Qwen3.6-27B-FP8 | Qwen3.5-27B-FP8 | Gemma 4 26B-A4B-it | **Gemma 4 31B-it (운영계)** |
|---|---|---|---|---|---|
| **HF 모델 ID** | `Qwen/Qwen3.8-27B-FP8` | `Qwen/Qwen3.6-27B-FP8` | `Qwen/Qwen3.5-27B-FP8` | `google/gemma-4-26B-A4B-it` | `google/gemma-4-31B-it` |
| **파라미터** | 27B (Dense, Mamba-hybrid) | 27B (Dense, Mamba-hybrid) | 27B (Dense) | 26B active / ~45B total (MoE) | 30.7B (Dense) |
| **아키텍처** | linear 48 + full 16 레이어 (Mamba-hybrid, 3.6과 동일 구성) | Gated DeltaNet 75% + Gated Attention 25% (Mamba-hybrid) | Transformer | MoE | Transformer |
| **기본 dtype** | FP8 (사전 양자화, e4m3) | FP8 (사전 양자화) | FP8 (사전 양자화) | BF16 | BF16 |
| **양자화 필요?** | 불필요 | 불필요 | 불필요 | `quantization: fp8_per_tensor` (온라인) | `quantization: fp8_per_tensor` (온라인) |
| **가중치 크기** | 29 GB | ~29 GB | ~27 GB | ~25 GB | ~29 GB |
| **라이선스** | Apache 2.0 | Apache 2.0 | Apache 2.0 | Gemma | Apache 2.0 |
| **HF 토큰** | 불필요 | 불필요 | 불필요 | 불필요 | 불필요 |
| **컨텍스트 (네이티브/YaRN)** | 262K / 1.05M | 262K / 1.01M | 131K | 128K | 256K |
| **멀티모달** | 텍스트 + 이미지 + 비디오 | 텍스트 + 이미지 + 비디오 | 텍스트 전용 | 텍스트 + 이미지 | 텍스트 + 이미지 |
| **Thinking 기본값** | ON (서버 OFF 덮음) | ON (서버 OFF 덮음) | ON | OFF | OFF |
| **Thinking 형식** | `<think>...</think>` | `<think>...</think>` | `<think>...</think>` | `<\|channel>thought...<channel\|>` | `<\|channel>thought...<channel\|>` |
| **tool_call_parser** | `qwen3_xml` | `qwen3_xml` (카드 권장: `qwen3_coder`) | `qwen3_xml` | `gemma4` | `gemma4` |
| **reasoning_parser** | `qwen3` | `qwen3` | `qwen3` | `gemma4` | `gemma4` |
| **샘플링 (Thinking)** | temp=1.0, top_k=20, top_p=0.95, presence_penalty=0 | temp=1.0, top_k=20, top_p=0.95, presence_penalty=1.5 | temp=0.6, top_k=20, top_p=0.95 | temp=1.0, top_k=64, top_p=0.95 | temp=1.0, top_k=64, top_p=0.95 |
| **MTP Speculative Decoding** | ✅ (지금 끔) | ✅ | ✅ | ✅ drafter 별도 (지금 끔) | ✅ drafter 별도 (지금 끔) |
| **vLLM 최소 버전** | 0.20.2 (0.31.0 실기동 확인) | 0.19.0 | 0.18.0 | 0.19.0 (0.31.0 실기동 확인) | 0.19.0 (0.31.0 실기동 확인) |
| **transformers 최소 버전** | 5.8.0 (config.json 기재) | ≥4.56.0 | ≥4.56.0 | ≥5.5.0 | ≥5.5.0 |

> Qwen3.8 열은 로컬 체크포인트(`/models/LLM/Qwen/Qwen3.8-27B-FP8`)의 `config.json`·`chat_template.jinja`·모델 카드에서 직접 확인한 값입니다. 벤치마크와 세대 비교는 [`slm_research/models/qwen3.8.md`](../agent-guide/docs/slm_research/models/qwen3.8.md), Qwen3.5 vs 3.6와 Gemma 4 vs Qwen3.6 비교는 [`slm_research/topics/gemma4-vs-qwen.md`](../agent-guide/docs/slm_research/topics/gemma4-vs-qwen.md) 참고.

**모델별 권장 샘플링** (모델 카드·`generation_config.json` 기준):

| 모델 | 모드 | temperature | top_p | top_k | presence_penalty |
|------|------|:-----------:|:-----:|:-----:|:----------------:|
| Gemma 4 (26B-A4B·31B) | 일반 | 1.0 | 0.95 | 64 | 0 |
| **Qwen3.8-27B** | Thinking | 1.0 | 0.95 | 20 | **0** |
| **Qwen3.8-27B** | Instruct(비Thinking) | 0.7 | 0.80 | 20 | **1.5** |
| Qwen3.6-27B | Thinking·일반 | 1.0 | 0.95 | 20 | **1.5** |
| Qwen3.6-27B | Thinking·코딩 | 0.6 | 0.95 | 20 | 0 |
| Qwen3.6-27B | Instruct·일반 | 0.7 | 0.8 | 20 | **1.5** |

> 모델의 `generation_config.json`이 자동 적용되므로 클라이언트가 명시하지 않는 것이 기본입니다. 사용자 가이드에서 샘플링 권장값을 뺀 이유도 같습니다 — 모델을 교체하면 권장값이 달라지는데 클라이언트가 옛 값을 박아두면 품질이 떨어집니다. 값 조정이 필요하면 인스턴스 yaml에서 서버 기본값으로 넣으세요.

### 11.2 모델 교체 퀵 가이드

기존 인스턴스를 다른 모델로 교체하려면 해당 `instances/<name>.yaml`의 모델 관련 키만 바꾸면 됩니다(포트·GPU는 모델 무관). **새 모델을 추가**하는 경우엔 `instances/<new>.yaml`을 복사하여 만들고 게이트웨이를 재기동하면 자동 디스커버리됩니다.

> 🔒 **`served_model_name: [gemma-4]`은 건드리지 않습니다.** 사용자에게 노출되는 이름을 고정해 두고 뒤에서만 모델을 바꾸는 것이 현재 정책입니다. 이 값을 바꾸면 챗봇·RAG 클라이언트가 전부 404를 받습니다. 배경과 동작은 [§10.4](#104-모델-교체-호환-계층-compat) 참고.

```yaml
# ── Qwen3.6-27B-FP8 (현재, Mamba-hybrid Dense) ──
model: Qwen/Qwen3.6-27B-FP8
# quantization 생략 (사전 양자화 체크포인트, 자동 감지)
tool_call_parser: qwen3_xml              # 모델 카드 권장은 qwen3_coder
reasoning_parser: qwen3
# Mamba-hybrid 운영 필수
async_scheduling: false
mm_encoder_tp_mode: data
mm_processor_cache_type: shm

# ── Qwen3.5 27B FP8로 교체 시 ──
# model: Qwen/Qwen3.5-27B-FP8
# tool_call_parser: qwen3_xml
# reasoning_parser: qwen3

# ── Gemma 4 26B-A4B (MoE, BF16→FP8 온라인 양자화) ──
# model: google/gemma-4-26B-A4B-it
# quantization: fp8
# tool_call_parser: gemma4
# reasoning_parser: gemma4
# # 비전 토큰 예산(기본 280 → 560 권장, 문서/차트 QA 최소선). 상세는 §11.4 참고.
# mm_processor_kwargs:
#   max_soft_tokens: 560
# limit_mm_per_prompt:
#   image: 4
#   audio: 0
#   video: 0

# ── Gemma 4 31B (Dense) ──
# model: google/gemma-4-31B-it
# quantization: fp8
# tool_call_parser: gemma4
# reasoning_parser: gemma4
# # 비전 토큰 예산(기본 280 → 560 권장, 문서/차트 QA 최소선). 상세는 §11.4 참고.
# mm_processor_kwargs:
#   max_soft_tokens: 560
# limit_mm_per_prompt:
#   image: 4
#   audio: 0
#   video: 0
```

> 교체 후 `.env`는 손댈 필요가 없습니다. `CHAT_MODEL`은 `served_model_name`(=`gemma-4`)과 짝이고, 그 값은 모델을 바꿔도 그대로이기 때문입니다.
>
> **Qwen3.6 → Gemma 4 교체 시 멀티모달 플래그 정정** (vLLM 0.19.0 소스 검증):
> - `mm_encoder_tp_mode: data` — Gemma 4는 `supports_encoder_tp_data=False`(`gemma4_mm.py`에 플래그 없음)라 `vllm/config/model.py:617-625`에서 **"weights"로 자동 폴백 + 경고**. 설정 자체는 무해하나 효과 없음 → Gemma 4에서는 제거 권장.
> - `mm_processor_cache_type: shm` — **모델 독립 글로벌 파라미터**(`vllm/multimodal/registry.py:276-328`). Gemma 4에서도 동일하게 IPC 중복 제거 효과 → 그대로 **유지 권장**.
> - `async_scheduling: false` — Qwen3.6 Mamba-hybrid + `mamba_cache_mode=align` 조합의 encoder cache race 방어선이 구체적 사유. Gemma 4에서는 `align` 모드가 없으므로 기본값(`true`)으로 되돌려 TPS 5~15% 회수 가능. 단, 다중 이미지 동시성이 높으면 안전하게 `false` 유지도 가능.

### 11.3 GPU 메모리 참고

`gpu_memory_utilization` 기준. 현재 0.9 (Mamba-hybrid KV 추정 오차 대비 보수).

**L40S 46GB × 1장**:

| 모델 | 가중치 | KV Cache 가용 | 권장 `max_model_len` |
|------|--------|--------------|---------------------|
| Qwen3.6-27B-FP8 | ~29 GB | 부족 | **비권장** (TP=2 사용) |
| Gemma 4 31B FP8 (온라인) | ~29 GB | ~14.7 GB | 12288 |
| Qwen3.5-27B FP8 | ~27 GB | ~16.7 GB | 12288~16384 |
| 14B BF16 | ~28 GB | ~15.7 GB | 12288~32768 |
| 8B BF16 | ~16 GB | ~27.7 GB | 32768~65536 |

**L40S 46GB × 2장 (`tensor_parallel_size: 2`) — 현재 운영**:

| 모델 | 가중치 (rank당) | KV Cache 가용 | 권장 `max_model_len` |
|------|-----------------|---------------|----------------------|
| **Qwen3.6-27B-FP8 (현재)** | ~14.5 GB | 넉넉 (Mamba-hybrid로 Full-Attn 대비 절감) | 262144 (실기동 확인) |
| Qwen3.5-27B FP8 | ~13.5 GB | ~60.4 GB | 65536~131072 |
| Gemma 4 31B FP8 (온라인) | ~14.5 GB | ~58.4 GB | 65536~131072 |

> ⚠️ vLLM KV cache profiler가 Mamba-hybrid 구조에서 ~7배 과잉추정(vllm-project/vllm [#37121](https://github.com/vllm-project/vllm/issues/37121))되는 이슈가 있습니다. 기동 로그의 실제 `num_gpu_blocks`를 확인해 튜닝하세요.

### 11.4 Gemma 4 비전 토큰 예산 튜닝

Gemma 4 비전 인코더는 이미지당 **soft token 고정 예산** 방식으로 가변 해상도를 처리합니다. 기본값 280은 챗봇 썸네일급(≈ 645K 픽셀)에 맞춰져 있어 문서·차트·스크린샷 QA 같은 고해상도 이미지에서는 디테일 손실이 발생합니다. 공식 허용값과 대응 픽셀 면적은 다음과 같습니다 (transformers `Gemma4ImageProcessor` 공식).

| `max_soft_tokens` | Patches (pooling 전) | 대응 픽셀 면적 | 대응 해상도 | 용도 |
|:-:|:-:|:-:|:-:|:--|
| 70 | 630 | ~161K | ~400×400 | 썸네일, 아이콘 |
| 140 | 1,260 | ~323K | ~570×570 | 중저해상도 |
| **280 (기본)** | **2,520** | **~645K** | **~800×800** | 일반 사진 |
| 560 | 5,040 | ~1.3M | ~1152×1152 | **문서·차트 QA 최소 권장** |
| 1120 | 10,080 | ~2.6M | ~1620×1620 | OCR·세밀 디테일 |

> ⚠️ `gemma4_mm.py:474-485`에 validator가 하드코딩되어 있어 **이 5개 값을 벗어난 정수는 `sys.exit(1)`로 기동 자체가 실패**합니다. 중간값(예: 400)은 불가.

#### 설정 방법 3가지

**(a) YAML — `instances/<name>.yaml` (인스턴스 전체 기본값)**
```yaml
mm_processor_kwargs:
  max_soft_tokens: 560
limit_mm_per_prompt:
  image: 4
  audio: 0
  video: 0
```

**(b) CLI — `vllm serve` 네이티브**
```bash
vllm serve google/gemma-4-31B-it \
  --mm-processor-kwargs '{"max_soft_tokens": 560}' \
  --limit-mm-per-prompt image=4
```

**(c) 요청 단위 override — 특정 요청만 예산 변경**
```json
{
  "model": "gemma-4",
  "messages": [
    {"role": "user", "content": [
      {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
      {"type": "text", "text": "Extract all text in this document."}
    ]}
  ],
  "mm_processor_kwargs": {"max_soft_tokens": 1120}
}
```
→ 썸네일 요청은 140, 문서 이미지는 1120처럼 워크로드별 동적 조절.

#### 워크로드별 권장값

| 워크로드 | `max_soft_tokens` | 근거 |
|----------|:-:|------|
| 챗봇 일반 사진(프로필, 로고 등) | 280 (기본) | ~800×800까지 정보 보존 충분 |
| 문서·차트·슬라이드 QA | **560** (운영 시작점) | A4 상단 1/3 ~ 전체 읽기 가능. 프로젝트 권장 디폴트 |
| OCR·세밀 표·소형 글씨 | 1120 | 이미지당 비용 4× 감수 |
| 썸네일 전용 | 70~140 | KV/prefill 비용 절약 |

#### 트레이드오프 (운영 영향)

| 항목 | 280 (기본) | 560 | 1120 |
|------|:-:|:-:|:-:|
| 이미지당 KV 캐시 점유 | 1× | 2× | 4× |
| vision prefill TTFT | 기준 | ~1.7–2× | ~3–4× |
| 문서·차트 정확도 | 표준 | +α | 최대 |
| `max_num_batched_tokens` 여유 | 넉넉 | 고려 필요 | **재튜닝 필수** |

560으로 올릴 때 `max_num_batched_tokens`는 `이미지당 토큰 × 동시 이미지 수 + 텍스트 여유` 기준으로 재산정하세요. 현재 98304 설정에서 `max_num_seqs: 5` × 이미지 1장이면 여유롭지만, 560 × 4장 요청이 들어오면 encoder cache 압박.

#### 다른 모델과의 키 충돌 — vLLM 0.19.0 실측

- `mm_processor_kwargs.max_soft_tokens`는 **Gemma 4 `Gemma4MultiModalProcessor`에서만 해석**됩니다. Qwen3-VL/InternVL 등 다른 VL 모델에서는 `vllm/multimodal/processing/context.py:260`의 `get_allowed_kwarg_only_overrides`가 HF processor signature를 inspect하여 **WARNING 로그 후 자동 드롭**합니다. 기동 실패나 런타임 에러는 나지 않습니다.
- Qwen3-VL 계열(Qwen3.5/3.6 MoE 포함)의 비전 파라미터는 `min_pixels` / `max_pixels` / `fps` / `num_frames` 체계(`qwen3_vl.py:733-740`)이며 Gemma 4와 호환되지 않습니다.

> 프로젝트에서는 인스턴스 yaml이 모델별로 분리되어 있어 — `instances/gemma.yaml`은 `mm_processor_kwargs: { max_soft_tokens: 1120 }`로 활성화, `instances/qwen.yaml`은 빈 dict `{}` — 모델 전환 시 주석 처리/해제 불필요합니다. 두 파일은 동일 키 구조 + 값만 다른 형태로 통일되어 있어 새 모델 추가 시 복붙 후 값만 수정하면 됩니다.

---

## 12. Qwen3.6/3.8 고급 기능

### 12.1 MTP Speculative Decoding

Qwen3.6-27B-FP8은 Multi-Token Prediction으로 사전·사후 학습됐습니다. vLLM Speculative Decoding으로 **2토큰 예측**을 활성화하면 처리량이 향상됩니다 (동일 Mamba-hybrid 계열 35B-A3B B200 실측 ~96K tokens/s·수락률 90% 참고 — 27B 자체 수치는 실기동 측정 필요).

```bash
vllm serve Qwen/Qwen3.6-27B-FP8 \
  --tensor-parallel-size 2 \
  --max-model-len 262144 \
  --reasoning-parser qwen3 \
  --speculative-config '{"method": "mtp", "num_speculative_tokens": 2}'
```

> ⚠️ **MTP method 표기 차이**: vLLM recipes는 `"method": "mtp"`, HF 모델 카드는 `"method": "qwen3_next_mtp"`. vLLM 0.31.0은 `qwen3_next_mtp`를 받으면 사용 중단 경고를 내고 `mtp`로 바꿉니다(`vllm/config/speculative.py:1135-1139`). 그래서 `mtp`로 적습니다.
>
> ⚠️ **지금 Qwen·Gemma 인스턴스는 모두 MTP를 끕니다.** Qwen은 접두 캐시와 MTP를 함께 쓰면 같은 접두의 요청이 틀린 답을 내는 문제(#53912), Gemma는 요청 혼합 오염(#46088)이 해결되지 않았습니다. 다시 켜는 조건은 `instances/qwen.yaml`·`prd-gemma.yaml`의 주석에 있습니다.

### 12.2 preserve_thinking (에이전트 반복 루프 최적화)

Qwen3.6 고유 신규 옵션. 멀티턴 대화에서 **이전 턴 reasoning**을 자동으로 히스토리에 유지해, 복잡한 에이전트 루프의 토큰 재사용 효율을 높입니다.

```json
{
  "model": "gemma-4",
  "messages": [ ... ],
  "chat_template_kwargs": {
    "enable_thinking": true,
    "preserve_thinking": true
  }
}
```

> - Qwen3.5, Gemma 4는 이 옵션 **미지원**. 교체 시 필드를 제거해야 합니다.
> - `/think`·`/nothink` 소프트 스위치는 **공식 미지원** (Qwen3 계열과의 분기점).

### 12.3 컨텍스트 1M 확장 (YaRN)

Qwen3.6는 YaRN으로 `max_model_len`을 1,010,000까지 확장할 수 있습니다. 다만 KV cache 부담이 폭증해 **현재 L40S×2 프로필에서는 비권장**합니다.

```bash
# 참고용 — 실제 운영에서는 262144 유지
VLLM_ALLOW_LONG_MAX_MODEL_LEN=1 vllm serve Qwen/Qwen3.6-27B-FP8 \
  --hf-overrides '{"text_config": {"rope_parameters": {"mrope_interleaved": true, "mrope_section": [11, 11, 10], "rope_type": "yarn", "rope_theta": 10000000, "partial_rotary_factor": 0.25, "factor": 4.0, "original_max_position_embeddings": 262144}}}' \
  --max-model-len 1010000
```

### 12.4 Thinking 모드 제어 (서버 vs 요청)

| 레벨 | 설정 방법 | 용도 |
|------|----------|------|
| **서버 기본값** | `instances/<name>.yaml`의 `default_chat_template_kwargs.enable_thinking` | 모든 요청의 기본 동작 |
| **요청 단위** | request body의 `chat_template_kwargs.enable_thinking` | 해당 요청만 온·오프 |

```yaml
# 서버 기본: 비활성화 (챗봇용)
default_chat_template_kwargs:
  enable_thinking: false

# 서버 기본: 활성화 (reasoning 분리가 항상 필요할 때)
default_chat_template_kwargs:
  enable_thinking: true
```

모델별 thinking 토큰 형식 차이:

| 모델 | reasoning_parser | 토큰 형식 |
|------|-----------------|-----------|
| Qwen 3 / 3.5 / 3.6 / 3.8 | `qwen3` | `<think>사고과정</think>최종답변` |
| Gemma 4 | `gemma4` | `<\|channel>thought...<channel\|>최종답변` |
| DeepSeek R1 | `deepseek_r1` | `<think>사고과정</think>최종답변` |

### 12.5 reasoning_effort (사고 길이 제어, Qwen3.8)

Qwen3.8에서 새로 생긴 채팅 템플릿 변수입니다. thinking을 켠 호출에서 **모델이 얼마나 오래 생각할지**를 지시문으로 조절합니다. 게이트웨이 경유에서는 effort를 주면 추론도 함께 켜집니다(§10.4의 "추론 켜고 끄기" 표).

| 값 | 템플릿이 주입하는 지시문 | 용도 |
|----|------------------------|------|
| `xhigh` | "가정을 검증하고 대안을 검토하며 정확성·일관성을 우선하라" | 템플릿 기본값. 어려운 추론·검증 워크로드 |
| `medium` | **없음**(중립) | 운영 기본값 — 균형 |
| `low` | "생각을 짧고 집중되게 유지하고 곧바로 결론으로 가라" | 지연 최소화 |

> ⚠️ **허용값은 이 3개뿐입니다.** 그 외 값은 채팅 템플릿이 `raise_exception`을 던져 **HTTP 400**이 됩니다(`chat_template.jinja:47-49`). vLLM의 최상위 `reasoning_effort` 필드 자체는 `none`/`minimal`/`low`/`medium`/`high`/`xhigh`/`max` 7개를 통과시키기 때문에, OpenAI 스펙상 멀쩡해 보이는 **`high`가 Qwen3.8에서는 그대로 400**입니다.
>
> ```
> {"error":{"message":"Unexpected reasoning effort high. Supported types are
>  xhigh (default), medium, and low.","type":"BadRequestError","code":400}}
> ```
>
> 📌 **이 400은 백엔드 직결에서만 봅니다.** 게이트웨이를 거치면 호환 계층이 `high`를 `xhigh`로 번역하므로 사용자에게는 노출되지 않습니다([§10.4](#104-모델-교체-호환-계층-compat)). 이 절은 번역이 무엇을 막아주고 있는지, 그리고 번역을 껐을 때 무슨 일이 생기는지를 기록해 둔 것입니다.

**왜 서버 기본값을 medium으로 고정했나**: 템플릿 기본값이 `xhigh`라 아무것도 지정하지 않으면 사고 지시문이 항상 최대로 붙습니다. 같은 질문(알고리즘 설계)을 thinking ON으로 던져보니 총 생성 토큰이 `medium` 1,673 → `xhigh` 4,092로 2.4배였습니다. 챗봇 트래픽 대부분은 그만큼 사고할 필요가 없으므로 `instances/qwen.yaml`에서 `medium`으로 눌러두고, 필요한 호출만 `xhigh`로 올립니다.

> 위 수치는 값마다 1회씩 잰 참고치입니다. 응답 지연은 같은 실측에서 effort 순서를 따르지 않았는데, 동시 트래픽에 따라 생성 속도가 요청마다 달라지기 때문입니다. 지연을 판단 근거로 쓰려면 부하가 없는 시간대에 반복 측정해야 합니다.

서버 기본값을 `xhigh`로 올릴 생각이라면 PII 게이트웨이(5015)의 업스트림 타임아웃 300초를 함께 봐야 합니다(`pii/config.py:90`). 비스트리밍 요청은 생성이 300초를 넘는 순간 504로 끊깁니다(스트리밍은 청크마다 타이머가 갱신돼 영향 없음). 상세는 API 가이드 §3.2.

**우선순위** — 아래로 갈수록 강합니다(아래 것이 위를 덮어씀):

| 위치 | 적용 범위 |
|------|----------|
| 인스턴스 yaml `default_chat_template_kwargs.reasoning_effort` | 서버 전체 기본값 |
| 요청 body `chat_template_kwargs.reasoning_effort` | 해당 요청만 변경 |
| 요청 body **최상위** `reasoning_effort` | 가장 강함 — 위 둘을 덮어씀 |

vLLM은 `merge_kwargs(서버 기본값, merge_kwargs(요청 kwargs, 최상위 필드))` 순으로 병합합니다(`renderers/params.py:28`, `entrypoints/openai/chat_completion/serving.py:194`). 최상위 필드를 주지 않으면 `None`이라 병합에서 제외되고 하위 값이 그대로 살아납니다.

```bash
# 이 요청만 깊게 생각시키기 (게이트웨이 경유 — high가 xhigh로 번역되고 추론도 켜진다)
curl -sS http://127.0.0.1:5015/v1/chat/completions -H "Content-Type: application/json" -d '{
  "model": "gemma-4",
  "messages": [{"role":"user","content":"이 설계의 병목을 찾아줘"}],
  "max_tokens": 8000,
  "reasoning_effort": "high"
}'
```

**모델별 지원**:

- **Qwen3.8** — 지원. 위 3값만.
- **Qwen3.5 / 3.6, Gemma 4** — 템플릿에 이 변수가 없어 값을 줘도 **무시**됩니다(에러는 아님). 게이트웨이는 이 계열에서 필드를 아예 제거하므로 결과는 같습니다.
- **thinking OFF일 때** — 템플릿이 effort 분기 자체를 타지 않아, 잘못된 값을 줘도 400 없이 통과합니다(실측). 즉 400은 thinking을 켠 요청에서만 납니다.

---

## 13. 트러블슈팅 & 운영 주의

### 13.1 멀티모달 Encoder Cache — 가장 주의할 포인트

vLLM V1의 **encoder cache**는 멀티모달 모델의 비전 인코더 출력(embedding)을 보관합니다. 이미지 1장이 패치 분할 후 만드는 encoder output 토큰 수를 단위로 동작합니다.

**설계 제약** (vLLM 0.19.0에서 확인, 0.31.0 소스도 같음):

- `encoder_cache_size`는 **사용자가 직접 설정할 수 없음** (0.31.0 `config/scheduler.py:154`, `init=False`).
- 내부적으로 `max_num_batched_tokens` 값이 그대로 복사됨 (0.31.0 `config/scheduler.py:304-305`).
- `max_num_seqs`와는 **연동되지 않음** — 동시 요청 상한을 올려도 encoder cache는 안 커짐.

**용량 산정식**:

```
encoder cache 수용 이미지 수 ≈ max_num_batched_tokens ÷ (이미지 1장 encoder 토큰)
```

Qwen3.6-VL 계열 기준 이미지 1장 ≈ 16,384 encoder 토큰. 현재 `max_num_batched_tokens: 163840` → 약 10장 수용.

### 13.2 `Encoder cache miss for <hash>` 크래시 대응

**증상**: 정상 동작하다가 worker가 assertion으로 죽고 APIServer도 shutdown.

```
AssertionError: Encoder cache miss for <hash>.
  at gpu_model_runner.py:2961 _gather_mm_embeddings
```

**근본 원인**: encoder cache 용량 < 동시 멀티모달 요청 수 + `async_scheduling` pipeline race. scheduler 장부와 worker 실제 cache 상태가 1-step 어긋날 때 발생.

**과거 사례 (2026-04-18 07:17:51 GPU0_1)**:
- 동시 5개 이미지 요청 + encoder cache budget 2장 분량 + async scheduling 활성.
- 14시간 가동 후 경합 타이밍이 맞아 assertion. 평소 Running 1~2개일 땐 표면화되지 않음.

**해결 설정 (동시 N장 기준)**:

| 설정 | 값 | 이유 |
|------|----|------|
| `async_scheduling` | **false** | scheduler-worker pipeline race 제거 (TPS 5~15% 감소 감수) |
| `max_num_batched_tokens` | **N × 16384 × 여유 20%** | encoder cache 동반 확장. N=5 → 98304. 현재 163840으로 10장 여유 |
| `max_num_seqs` | **N** | 동시 요청 상한을 encoder cache 수용량과 매칭 |

현재 `instances/qwen.yaml`(Qwen 챗봇 운영 가정)에 3가지가 모두 반영돼 있습니다. 트래픽이 더 늘면 `max_num_batched_tokens`와 `max_num_seqs`를 비례 증가하세요.

### 13.3 `disable_chunked_mm_input`이 Qwen3.6에 금지인 이유

> ⚠️ **`disable_chunked_mm_input: true`를 Qwen3.6에서 절대 설정하지 마세요.**

Qwen3.6-27B-FP8은 Mamba-hybrid 구조라서, `enable_prefix_caching: true`가 켜지면 vLLM이 `mamba_cache_mode='align'`을 자동 적용합니다.

- align 모드는 attention block_size를 1056 같은 큰 값으로 확장합니다.
- 따라서 MM 입력을 block_size 배수로 쪼갤 유연성이 반드시 필요합니다.
- `vllm/config/vllm.py:1730`의 `validate_block_size()`가 `disable_chunked_mm_input=True`를 **AssertionError로 거부**합니다.

일반 VL 모델 가이드에서 이 옵션을 권장하는 글이 많지만, Mamba-hybrid에서는 반대로 동작합니다. 이 모델의 encoder cache 방어선은 `async_scheduling: false` + `max_num_seqs` 상한 + `max_num_batched_tokens` 조합으로 충분하도록 설계되어 있습니다.

### 13.4 동시 요청이 `max_num_seqs`를 초과하면?

vLLM scheduler가 FCFS(First-Come-First-Served)로 자동 큐잉합니다:

- 앞 N개: 즉시 Running.
- 나머지: Waiting 큐 (KV/encoder cache 할당 없음, 메모리 거의 안 먹음).
- Running 완료 시마다 Waiting에서 1개씩 promote.
- Gateway HTTP 타임아웃(300s)이 실질 대기 상한.

로그 확인:

```
Engine 000: ... Running: 5 reqs, Waiting: 3 reqs, ...
```

### 13.5 좀비 Worker 프로세스 주의

engine crash 시 APIServer는 shutdown되지만 **Worker 프로세스가 좀비로 남아 GPU 메모리를 계속 점유**하는 경우가 있습니다. `start.sh`의 `/health` 폴링은 이걸 감지 못해 `[SKIP] 실행 중 아님`으로 오판합니다.

재기동 시 OOM(`CUDA error: out of memory`)이 나면:

```bash
# GPU 점유 프로세스 확인
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader

# vllm 관련 프로세스 확인
ps aux | grep -E "vllm|Worker_TP" | grep -v grep

# 정상 종료 시도
kill <좀비 PID들>

# 안 죽으면 강제 종료
kill -9 <좀비 PID들>
```

### 13.6 알려진 vLLM 이슈 (운영 영향도)

> 상류 상태는 2026-10-10 GitHub 기준이고, "우리 시험"은 L40S에서 0.31.0으로 잰 결과입니다([판정표](vllm/tests/results/vllm-0.31-ab.md)). 이슈가 닫혀도 우리 조건에서 해결이 확인되기 전에는 방어선을 풀지 않습니다.

| 이슈 | 요약 | 상류 상태 (0.31.0) | 현재 방어선 |
|------|------|------|------------|
| [vllm #46088](https://github.com/vllm-project/vllm/issues/46088) | Gemma 4 + MTP + KV `auto`에서 긴 요청과 짧은 요청을 같이 돌리면 짧은 요청에 다른 요청 내용이 섞임 | 수정 없이 닫힘(not_planned) | **Gemma 인스턴스 4개 모두 MTP 끔**. 우리 축소 재현은 옛·새 모두 0건이라 검출력이 없어 안전 근거로 쓰지 않음. 버전업으로 해결이 확인되면 다시 켬 |
| [vllm #53912](https://github.com/vllm-project/vllm/issues/53912) | Qwen3.5 계열(GDN) + 접두 캐시 + MTP에서 캐시된 상태가 오염돼 숫자 복사 오류·질문 되풀이 | 열림. 수정 PR #57128 병합 전 | **Qwen 인스턴스 MTP 끔**. 수정이 릴리스에 들어가면 우리 환경에서 재확인 뒤 켬 |
| [vllm #38106](https://github.com/vllm-project/vllm/issues/38106) | 추론 켬 + 추측 디코딩 + 문법 제약(`tool_choice="required"`, JSON 스키마)에서 문법 상태가 깨져 도구 호출 실패 | 이슈는 열림. 같은 원인 수정 #44297·#44993이 0.31.0에 포함 | 옛 nightly + MTP는 우리 시험에서 108/320 실패, 0.31은 0건. 지금은 MTP를 꺼서 해당 없음. MTP를 다시 켤 때 `tests/mtp_known_bug_probe.py`로 재확인 |
| [vllm #42261](https://github.com/vllm-project/vllm/issues/42261) | H200 + Gemma 31B MTP 8토큰에서 몇 시간마다 device-side assert 크래시 | 해결 확인 없이 닫힘(not_planned) | MTP 끔이라 해당 없음. 온프레미스 H200에서 MTP를 켤 때 관찰 항목 |
| [vllm #37121](https://github.com/vllm-project/vllm/issues/37121) | Hybrid Mamba/Attention(Qwen3.5 계열) KV cache ~7배 과잉추정 | 열림 | 기동 로그의 `num_gpu_blocks` 재확인 후 튜닝 |
| [vllm #37602](https://github.com/vllm-project/vllm/issues/37602) | Qwen3.5 계열 동시 이미지 10+에서 EngineCore 크래시 | 닫힘(07-23, completed) | `max_num_seqs: 20`. 0.31 Qwen3.8 2시간 부하에서 동시 이미지 10건 정답 10/10, 엔진 오류 0 |
| [vllm #38643](https://github.com/vllm-project/vllm/issues/38643) | Qwen3.5 FLA linear attention 포맷 불일치 gibberish | 열림. 다른 사용자들은 최신 main에서 재현하지 못했고, 원인으로 지목된 경고는 #38255에서 오탐으로 제거됨 | 방어선 없음. 0.31 Qwen3.8 FP8은 기능·회귀 시험에서 증상 없음 |
| [vllm #40124](https://github.com/vllm-project/vllm/issues/40124) | TurboQuant KV + Hybrid MoE가 Ampere(SM 80-86)에서 실패 | 열림 | **L40S(Ada Lovelace, SM 89) 무영향** — GPU 교체 시에만 주의 |
| 자체 Bug 2026-04-18 | `Encoder cache miss` assertion | — | `async_scheduling: false` + `max_num_seqs` 상한. 0.31도 YAML의 `false`가 버려져 런처가 `--no-async-scheduling`을 붙임([§9.5](#95--참고-yaml-bool-false-전달-제약-런처-내부)). 상세는 [vllm/bugfix/2026-04-18_vllm_multimodal_encoder_cache.md](vllm/bugfix/2026-04-18_vllm_multimodal_encoder_cache.md) |

### 13.7 운영 환경 튜닝 백로그

#### Gemma 4 26B-A4B (E=128, N=352, fp8_w8a8) fused MoE config 부재

기동 로그에 다음 WARNING이 출력된다.

```
WARNING fused_moe.py:1090
Using default MoE config. Performance might be sub-optimal!
Config file not found at .../configs/E=128,N=352,device_name=NVIDIA_<GPU>,dtype=fp8_w8a8.json
```

**상태**: vLLM 0.31.0 동봉 335개 사전 튜닝 JSON 중 TP2(`N=352`) + fp8_w8a8 매칭은 여전히 H100_80GB_HBM3 한 종 뿐이고, L40S용은 없어 default fallback으로 동작한다. TP1(`N=704`)은 `NVIDIA_RTX_PRO_6000_Blackwell_Workstation_Edition` 파일이 있다. 운영 GPU의 `device_name`이 이 이름과 같으면 TP1 26B-A4B는 튜닝 없이 맞는 파일을 쓴다. 기동 로그에 `Using configuration from ... for MoE layer`가 나오면 매칭된 것이다. 지금 운영 인스턴스는 31B 덴스라 MoE가 없다.

**영향**: 정확도/안정성에는 영향 없음. MoE GEMM throughput 잠재 손실 (조합에 따라 10~30%).

**대응 (운영 이전 후)**:

```bash
# 1) vLLM 소스 클론 (튜닝 스크립트는 pip 패키지에 미포함)
git clone https://github.com/vllm-project/vllm.git /tmp/vllm
cd /tmp/vllm

# 2) 운영 GPU(RTX PRO 6000)에서 튜닝 실행 (vLLM 잠시 내려야 함)
python benchmarks/kernels/benchmark_moe.py \
  --model google/gemma-4-26B-A4B-it \
  --tp-size <운영 TP 크기> \
  --dtype fp8_w8a8 \
  --tune

# 3) 산출물을 볼륨의 폴더에 두고 인스턴스 yaml의 env로 지정
#    VLLM_TUNED_CONFIG_FOLDER가 동봉 configs/보다 먼저 조회된다(0.31.0 fused_moe.py:1135).
#    이미지 안 site-packages에 복사하면 컨테이너를 다시 만들 때 사라진다.
mkdir -p /models/moe-configs
cp E=128,N=<산출 N>,device_name=<GPU 이름>,dtype=fp8_w8a8.json /models/moe-configs/
#    instances/<name>.yaml:
#    env:
#      VLLM_TUNED_CONFIG_FOLDER: "/models/moe-configs"

# 4) vLLM 재기동 → WARNING 대신 "Using configuration from /models/moe-configs/..." 로그
```

**선택 사항**: 산출 JSON을 vLLM 본가 `vllm/model_executor/layers/fused_moe/configs/`에 PR. RTX PRO 6000 Blackwell 변종은 이미 코어팀이 다른 모델용으로 동봉 시작한 GPU라 머지 가능성 높음.

**트리거**: 운영 환경 셋업 완료 후. 개발 환경 L40S에서는 의미 없음 (운영 환경 아님).

---

## 14. QA 테스트

서버 배포 후 기능 검증을 자동화하는 스크립트. Python 표준 라이브러리만 사용합니다.

### 14.1 기본 사용법

`./start.sh test`가 진입점입니다. `[name]`을 실제 포트로 바꿔 `tests/test_vllm_server.py`를 호출하므로, launcher가 포트를 자동 회피했더라도 포트를 직접 찾을 필요가 없습니다.

```bash
cd /workspace/llm-serving/vllm

./start.sh test                      # 기동된 게이트웨이 전부 (미기동은 SKIP)
./start.sh test 5015                 # 게이트웨이 1대
./start.sh test gemma-26b            # 인스턴스 직접 (게이트웨이 미경유, runtime의 실제 포트)
./start.sh test http://gpu-server:5015   # 원격 서버
./start.sh test 5015 --category infra inference tool   # 대상 뒤 인자는 테스트 스크립트로 그대로 전달
./start.sh test --list               # 카테고리 목록
```

전체 카테고리를 다 돌리면 멀티모달·캐싱 항목 때문에 대상 1대당 수 분이 걸립니다. 배포 직후 빠르게 확인할 때는 `--category infra inference`로 좁히세요. 하나라도 실패하면 종료 코드 1이라 cron·CI에서 그대로 판정에 쓸 수 있습니다.

마지막 `gateway` 카테고리는 게이트웨이가 클라이언트에 약속한 동작(§10.4)을 봅니다. effort와 추론 켜고 끄기, 정체성 문구, developer 역할, 모델 경로 가림입니다. 대상이 게이트웨이일 때만 돌고, 인스턴스에 직접 붙으면 "건너뜀"으로 표시됩니다. 사고가 꺼졌는지는 응답의 `<think>`만이 아니라 `reasoning` 필드까지 봅니다. 파서가 사고를 분리하면 `<think>`가 content에 남지 않기 때문입니다.

아래는 테스트 스크립트를 직접 호출하는 방법입니다. 포트를 직접 지정하거나 `-v` 같은 옵션을 쓸 때 참고하세요.

```bash
# 전체 테스트 (모델명 자동 추출 — 아래 우선순위)
python tests/test_vllm_server.py

# 원격 서버 — 로컬 yaml 사본 없어도 동작 (게이트웨이가 listen 중이면)
python tests/test_vllm_server.py --base-url http://gpu-server:5015

# 모델명 명시
python tests/test_vllm_server.py --base-url http://gpu-server:5015 --model MyModel

# 특정 카테고리만
python tests/test_vllm_server.py --category infra inference tool

# 카테고리 목록
python tests/test_vllm_server.py --list

# 상세 출력
python tests/test_vllm_server.py -v
```

**모델명 자동 추출 우선순위**

| 순위 | 경로 | 사용 조건 |
|------|------|----------|
| 1 | `--model <name>` 인자 | 사용자 직접 지정 (최우선) |
| 2 | `{base_url}/v1/models` API 첫 결과 (timeout 5s) | 게이트웨이가 listen + backend ready |
| 3 | 로컬 `gateways/<port>.yaml` → `instances/<name>.yaml`의 `served_model_name` | 같은 레포 사본 보유 시 fallback |
| 실패 | 두 사유 합쳐 RuntimeError | 위 모두 실패 시 — `--model`을 직접 지정 |

> 원격 서버 테스트 시 로컬에 yaml 사본이 없어도 2번 경로(`/v1/models`)가 응답하면 정상 동작합니다.

**실패 진단 — 자동 부착 정보**

테스트가 fail이거나 예외가 나면 다음 정보가 자동으로 detail에 부착됩니다 (별도 옵션 없이):

- **마지막 HTTP 요청** — `method` · `URL` · 요청 body (pretty JSON)
- **마지막 HTTP 응답** — `status` · 응답 body (vLLM의 에러 메시지 등 그대로)
- **예외 발생 시** — `type` · 메시지 · 전체 traceback (파일·라인까지)

각 테스트 직후 콘솔에 한 번, 끝에 `print_summary` "실패 목록"에서 다시 한 번 출력됩니다. JSON 응답은 `indent=2`로 가독성 있게 표시됩니다.

**자동 로그 파일 — 항상 저장**

매 실행마다 콘솔 출력 전체가 다음 경로에 자동 저장됩니다 (ANSI 색 제거된 plain text):

```
llm-serving/vllm/tests/logs/test_YYYYMMDD_HHMMSS.log
```

main 시작 시 path가 안내되고 종료 시 다시 출력됩니다. 사후 분석 예시:

```bash
# 최근 로그 확인 (vllm/ 디렉토리에서 실행)
ls -lt tests/logs/test_*.log | head -3
# 실패만 추출
grep -B1 -A20 "FAIL " tests/logs/test_20260430_144909.log
```

> 백그라운드/CI 실행, 긴 출력 스크롤 등으로 콘솔 확인이 어려울 때 이 파일이 단일 진실 소스입니다.

### 14.2 테스트 카테고리

| 카테고리 | 키 | 테스트 수 | 검증 내용 |
|---------|-----|----------|----------|
| 서버 기동 | `infra` | 3 | 헬스체크, 모델 목록, 잘못된 엔드포인트 |
| 기본 추론 | `inference` | 4 | 단일턴, 시스템 프롬프트, 멀티턴, 잘못된 모델명 |
| 스트리밍 | `streaming` | 2 | SSE 청크, usage 반환 |
| 샘플링 | `sampling` | 4 | temperature 범위, max_tokens 경계, 잘못된 값 |
| Thinking | `thinking` | 3 | 기본 OFF, 요청 단위 ON/OFF |
| Tool Calling | `tool` | 4 | 단일/복수 호출, 불필요 시 스킵, 결과 반영 |
| 경계값 | `edge` | 6 | 빈 메시지, 긴 입력, 동시 5/10개, 잘못된 JSON |
| 캐싱 | `caching` | 1 | 프리픽스 캐싱 TTFT 비교 |
| 멀티모달 | `multimodal` | 4 | 단일 이미지, 동시 5/10개, 이미지+텍스트 혼합 (Encoder cache 안정성) |

### 14.3 트래픽 테스트

`traffic_test_vllm.py`는 게이트웨이에 동시 요청을 걸어 서버가 버티는지 보는 부하 시험입니다. 기본값은 요청 40건, 동시 20, 요청당 생성 상한 4,096토큰, 절반은 4096px 이미지 포함이고, 질문 4개(사고 켬 2·끔 2)를 돌려 씁니다. 429 과부하 방어 응답은 실패가 아니라 정상 방어로 집계합니다. 예전 문서의 `--mode smoke/overload`는 지금 받기만 하고 쓰지 않습니다. 강도는 `--requests`, `--concurrency`, `--max-tokens`, `--image-ratio`로 정합니다.

**답변 점검 (2026-10-10~)**: HTTP 200이어도 답이 없을 수 있어 응답마다 종료 사유(`finish_reason`)와 답변 글자 수를 봅니다.

| 경우 | 진행 화면 | 판정 |
|------|-----------|------|
| 생성 상한에 걸림(`finish_reason: length`) | "상한 도달", 답변이 없으면 "답변 없음 — 생성 상한에 도달해 사고 중에 끊겼습니다" | 경고. 건수가 출력·리포트에 남고 통과는 유지 |
| 상한이 아닌데 답변이 0자 | "답변 없음" | 실패. 사고만 하고 답을 안 낸 것이라 파서나 서버 쪽 이상 |

예전 질문은 사고 켬 질문에 "약 250자"처럼 글자 수를 지정했습니다. Qwen3.8은 이 지시를 지키려고 사고 과정에서 한 글자씩 세느라 3천~4천 토큰을 썼고, 일부가 상한에 걸려 답 없이 끝났는데도 성공으로 집계됐습니다. 지금은 사고 켬 질문으로 전기요금 계산표와 하루 일정표를 만들게 합니다. 사고가 계산과 시각 배분에 쓰이므로 끝이 있고, Qwen3.8 기준 전체 생성이 1.3천~1.8천 토큰에서 멈춥니다. 질문이 바뀌면 지연·TPS를 예전 리포트와 바로 비교할 수 없으므로 리포트의 `config.prompts`에 어떤 질문으로 쟀는지 남깁니다.

진입점은 `./start.sh traffic`입니다. 부하가 큰 명령이라 두 가지를 강제합니다. 대상을 반드시 찍어야 하고(무인자·`all` 거부), 게이트웨이만 받습니다. 인스턴스를 직접 겨냥하면 통과 조건에 들어가는 `/server-status`가 게이트웨이 전용이라 404가 떠서 부하 결과와 무관하게 항상 실패 판정이 납니다.

```bash
./start.sh traffic 5015                       # 게이트웨이 대상, 기본 설정
./start.sh traffic 5015 --requests 80 --concurrency 80 --require-429   # 뒤 인자는 traffic_test_vllm.py로 그대로 전달. 과부하 방어(429) 확인
./start.sh traffic http://호스트:5015 --requests 20 --concurrency 20
```

> ⚠️ **기록으로 남길 측정에는 `--label`을 붙이세요.** 리포트의 `config.model`은 API 모델명이라 어느 백엔드를 재도 `gemma-4`입니다([§10.4](#104-모델-교체-호환-계층-compat)). `--label`은 요청에 실리지 않고 리포트의 `config.label`과 진행 화면 헤더에만 남는 표시용 값이라, 나중에 어느 체크포인트의 부하 특성이었는지 되짚을 수 있습니다. 생략하면 실행 첫 화면에 경고 한 줄이 뜨고 `config.label`에는 API 모델명이 그대로 들어갑니다.
>
> ```bash
> ./start.sh traffic 5015 --label "Qwen3.8-27B-FP8"
> ```

아래는 스크립트를 직접 호출하는 방법입니다.

```bash
cd llm-serving/vllm

# 저강도 생존/성공률 확인 (텍스트만, 짧게)
python tests/traffic_test_vllm.py --base-url http://43.203.142.247:5015 --requests 10 --concurrency 5 --image-ratio 0

# 대기열/429 방어 확인 — 동시성이 게이트웨이 한도(처리 20 + 대기열 40 = 60)를 넘어야 429가 난다
python tests/traffic_test_vllm.py --base-url http://43.203.142.247:5015 --requests 80 --concurrency 80 --require-429

# 동시 사용자 20명 기준 짧은 응답 테스트 (상한에 일부러 걸리므로 "상한 도달" 경고가 정상)
python tests/traffic_test_vllm.py --base-url http://43.203.142.247:5015 --requests 20 --concurrency 20 --max-tokens 32
```

운영 전에는 `max_tokens >= 512` 또는 실제 서비스 평균 프롬프트/출력 길이로 한 번 더 확인합니다. 테스트 후 `/health`가 200이어야 통과입니다(`/server-status` 조회 포트는 모드에 따라 다름 — [§10.1](#101-게이트웨이-전용-엔드포인트)). PII 모드에서는 위 `--base-url :5015`가 프록시를 경유하므로 마스킹 오버헤드가 포함된 실경로 성능입니다(순수 게이트웨이 성능은 내부 `:6015`로 측정). 비PII 모드는 `:5015`가 곧 게이트웨이라 그대로 순수 성능입니다.

### 14.3.1 속도 비교 테스트 (모델 간 매트릭스 누적)

`tests/speed_test.py`는 게이트웨이 단위 속도 측정 도구입니다. 모델명은 `{base_url}/v1/models`에서 자동 추출하며, 결과는 `tests/results/speed_results.md`에 Markdown 테이블 행으로 누적 append 됩니다. 여러 모델 비교는 게이트웨이별로 두 번 호출하면 같은 파일에 이어 쌓입니다.

> ⚠️ **모델 비교 측정에는 `--label`이 필수입니다.** 자동 추출되는 이름은 이제 어느 백엔드든 `gemma-4`라서([§10.4](#104-모델-교체-호환-계층-compat)), 라벨 없이 재면 결과 표의 `model` 열이 전부 `gemma-4`가 되어 무엇을 잰 기록인지 구분할 수 없습니다. 생략하면 실행 첫 화면에 경고 한 줄이 뜹니다.
>
> ```bash
> ./start.sh speed 5015 --label "Qwen3.8-27B-FP8"
> ```

진입점은 `./start.sh speed`입니다. 합격·불합격 판정이 없는 측정 도구라, 실패로 잡히는 것은 연결 자체가 안 될 때뿐입니다. 인스턴스 직접 지정도 됩니다.

```bash
./start.sh speed 5015              # 게이트웨이 대상, 6조합 측정
./start.sh speed gemma-26b         # 인스턴스 직접 (게이트웨이 오버헤드 제외한 순수 속도)
./start.sh speed 5015 --quick      # 1조합만 (연결 확인용)
./start.sh speed                   # 기동된 게이트웨이 전부 — 같은 파일에 이어서 누적
```

무인자로 돌리면 기동된 게이트웨이를 순회하며 한 파일에 쌓으므로, 모델 간 비교표를 한 번에 만들 수 있습니다.

아래는 스크립트를 직접 호출하는 방법입니다.

```bash
cd llm-serving/vllm

# 게이트웨이별 측정 — 동시성[1,5,10] × max_tokens[512,2048] = 6 row / 호출
# (입력은 ~2000자 한국어 RAG 컨텍스트 고정 — speed_test.py의 PROMPT_KO_CONTEXT)
python tests/speed_test.py --base-url http://localhost:5015     # Gemma 게이트웨이
python tests/speed_test.py --base-url http://localhost:5016     # Qwen 진입점(PII 프록시) (같은 파일에 누적)

# 모델명 직접 지정 (자동 추출 건너뜀)
python tests/speed_test.py --base-url http://localhost:5015 --model gemma-4 --label "Gemma-32k"

# 빠른 구문/연결 확인 (동시성 1, max_tokens 512만)
python tests/speed_test.py --base-url http://localhost:5015 --quick

# 결과 경로 변경
python tests/speed_test.py --base-url http://localhost:5015 --results-path tests/results/2026-05_speed.md
```

**결과 테이블 컬럼** (`tests/results/speed_results.md`)
- `TTFT_ms`: 첫 토큰까지 지연 (ms, prefill 성능)
- `TPS`: 요청당 출력 토큰 생성 속도 (output tok/s, decode 성능 = 텍스트 출력 속도)
- `ok/N`: 성공 요청 / 전체 요청 (실패 섞이면 TPS가 왜곡되니 확인용)

> 콘솔에는 추가 진단치(`429`, `err`, `svrTPS` = 전체 elapsed 기준 시스템 처리량)도 같이 출력되지만, 결과 파일에는 핵심 3종만 누적해 모델 간 가독성을 유지합니다.

### 14.4 테스트 항목 상세

#### 서버 기동 / 인프라 (`infra`)

| ID | 테스트 | 판정 기준 |
|----|-------|----------|
| 1.1 | 헬스체크 | HTTP 200 |
| 1.2 | 모델 목록 조회 | `served_model_name` 포함 |
| 1.3 | 잘못된 엔드포인트 | HTTP 404/405 |

#### 기본 추론 (`inference`)

| ID | 테스트 | 판정 기준 |
|----|-------|----------|
| 2.1 | 단일 턴 짧은 응답 | HTTP 200 + content 비어있지 않음 |
| 2.2 | 시스템 프롬프트 반영 | 영어 응답 지시 준수 확인 |
| 2.3 | 멀티턴 맥락 유지 | 응답에 언급한 이름 포함 |
| 2.4 | 존재하지 않는 모델명 | HTTP 4xx |

#### 스트리밍 (`streaming`)

| ID | 테스트 | 판정 기준 |
|----|-------|----------|
| 3.1 | 기본 SSE 청크 | 청크 2개 이상 + `data: [DONE]` |
| 3.2 | 스트리밍 usage | 마지막 청크에 usage 포함 |

#### 샘플링 (`sampling`)

| ID | 테스트 | 판정 기준 |
|----|-------|----------|
| 4.1 | temperature=0 결정적 출력 | 동일 프롬프트 2회가 동일 응답 |
| 4.2 | temperature=1.5 크래시 없음 | HTTP 200 |
| 4.3 | max_tokens=1 | `finish_reason: length` + ≤2 토큰 |
| 4.4 | 잘못된 temperature | HTTP 400 |

#### Thinking (`thinking`)

| ID | 테스트 | 판정 기준 |
|----|-------|----------|
| 5.1 | OFF 기본 | content에 `<think>` 미포함 |
| 5.2 | 요청 단위 ON | `reasoning` (또는 `reasoning_content`) 필드 존재 |
| 5.3 | 요청 단위 OFF 명시적 전달 | content에 `<think>` 미포함 |

> **`skip_special_tokens`는 클라이언트가 신경 쓸 필요가 없습니다.** Gemma 4의 `<|channel>...<channel|>`는 스페셜 토큰이라 기본 설정으로는 제거되어 reasoning 분리가 깨지는데, vLLM의 Gemma 4 파서가 요청마다 `skip_special_tokens=False`로 처리합니다(0.31.0 `vllm/parser/gemma4.py`의 `Gemma4Parser`. 옛 nightly는 `vllm/reasoning/gemma4_reasoning_parser.py`의 `adjust_request()`). Qwen의 `<think>...</think>`는 일반 토큰이라 애초에 무관합니다.
> 예전 가이드가 요구하던 요청 본문의 `skip_special_tokens: false`는 이제 불필요합니다.

#### Tool Calling (`tool`)

| ID | 테스트 | 판정 기준 |
|----|-------|----------|
| 6.1 | 단일 Tool Call | `tool_calls[0].function.name == "lookup_coverage"` |
| 6.2 | 복수 Tool 선택 | 2개 Tool 모두 호출 |
| 6.3 | Tool 불필요 시 직접 응답 | `tool_calls` 없이 content |
| 6.4 | Tool 결과 반영 | 최종 응답에 Tool 결과 핵심 정보 포함 |

#### 경계값 (`edge`)

| ID | 테스트 | 판정 기준 |
|----|-------|----------|
| 7.1 | 빈 메시지 | HTTP 200 (크래시 없음) |
| 7.2 | 긴 입력 (~6000 토큰) | 정상 처리 + usage |
| 7.3 | 동시 5개 (max_num_seqs 이내) | 5개 모두 HTTP 200 |
| 7.4 | 동시 10개 (큐잉) | 10개 모두 HTTP 200, 크래시 없음 |
| 7.5 | 잘못된 JSON | HTTP 400/422 |
| 7.6 | 필수 필드 누락 | HTTP 400/422 |

#### 캐싱 (`caching`)

| ID | 테스트 | 판정 기준 |
|----|-------|----------|
| 8.1 | 프리픽스 캐싱 TTFT | 2차 요청이 1차보다 빠름 |

#### 멀티모달 (`multimodal`)

| ID | 테스트 | 판정 기준 |
|----|-------|----------|
| 9.1 | 단일 이미지 — 강아지 5마리 정답 | HTTP 200 + 응답에 "5"/"다섯" 포함 |
| 9.2 | 동시 이미지 5개 (max_num_seqs 이내) | 5개 모두 HTTP 200 |
| 9.3 | 동시 이미지 10개 (큐잉) | 10개 모두 HTTP 200, 크래시 없음 |
| 9.4 | 이미지 + 텍스트 혼합 동시 10개 | img 5/5 + txt 5/5 |

> 9.x는 2026-04-18 `Encoder cache miss` 크래시 재발 방지를 위한 회귀 테스트입니다.

---

## 15. 참고 자료

### 15.1 프로젝트 파일 구성

```
llm-serving/
├── VLLM_API_GUIDE.md            ← 사용자용 API 가이드 (§1~§4)
├── VLLM_OPS_GUIDE.md            ← 이 문서 (운영자용, §6~§15)
├── DEPLOY_GUIDE.md              ← 배포 절차 (로컬 → S3 → EC2)
├── README.md                    ← llm-serving 인덱스 (vllm/sglang/stt)
├── vllm/                        ← vLLM 본체
│   ├── start.sh                 (launcher ↔ gateway 통합 진입점, name 자동 라우팅)
│   ├── vllm_server_launcher.py  (yaml 단위 vLLM 서브프로세스 + 포트 자동 회피 + runtime json)
│   ├── vllm_gateway.py          (LB + Admission Controller + 헬스체크 + 웜업)
│   ├── tests/                   ← 테스트 코드 디렉토리
│   │   ├── test_vllm_server.py  (10 카테고리 QA)
│   │   ├── traffic_test_vllm.py (동시 부하 시험)
│   │   ├── speed_test.py        (모델 간 속도 매트릭스 누적)
│   │   └── results/             (speed_results.md 등 누적 리포트)
│   ├── instances/               ← 인스턴스 단위 yaml (vLLM 1대 = 1 yaml)
│   │   ├── gemma-26b.yaml       (연구 비PII, gateway_port: 5015, port hint: 7071, gpus: [0,1])
│   │   ├── gemma.yaml           (연구 PII, gateway_port: 6015 — 외부는 프록시 :5015)
│   │   ├── qwen.yaml            (연구 PII, gateway_port: 6016 — 외부는 프록시 :5016)
│   │   ├── prd-gemma.yaml       (운영 비PII, gateway_port: 5501, port hint: 7070, gpus: [0])
│   │   ├── prd-pii-gemma.yaml   (운영 PII, gateway_port: 6501 — 외부는 프록시 :5501)
│   │   ├── prd-pii-qwen.yaml    (운영 PII, gateway_port: 6502 — 외부는 프록시 :5502)
│   │   └── .runtime/            ← launcher가 기록하는 실제 사용 포트/PID (gitignore 대상)
│   │       └── <name>.json      (port, pid, model, started_at)
│   ├── gateways/                ← 게이트웨이 단위 yaml
│   │   ├── 5015.yaml · 5501.yaml    (비PII — 외부 직접 노출 0.0.0.0)
│   │   └── 6015 · 6016 · 6501 · 6502.yaml  (PII — 내부전용 127.0.0.1, 외부는 프록시)
│   ├── bugfix/                  ← 인시던트 기록 (원인 → 수정 → 재발 방지)
│   └── logs/                    ← 런타임 로그 (gitignore 대상)
├── stt/                         ← STT PoC (Qwen3-ASR + Whisper-large-v3)
└── sglang/                      ← (예정) SGLang 운영 디렉토리
```

> 구식 단일 yaml(`vllm_config.yaml`, `vllm_gateway_config.yaml`)은 2026-04-30 새 구조 도입 시 `agent-guide/.archive/2026-04-30_vllm-config-migration/`로 이관됨.

### 15.2 관련 문서

**워크스페이스 문서**

- [`VLLM_API_GUIDE.md`](VLLM_API_GUIDE.md) — 사용자용 API 가이드 (호출 예시 · 파라미터 · `.env` 통합)
- [`DEPLOY_GUIDE.md`](DEPLOY_GUIDE.md) — 배포 절차 (로컬 → S3 → EC2 동기화)
- [`README.md`](README.md) — llm-serving 디렉토리 인덱스
- [`stt/README.md`](stt/README.md) — STT PoC 가이드
- [`../agent-guide/PROJECT.md`](../agent-guide/PROJECT.md) — 워크스페이스 전체 구조
- [`../agent-guide/SESSION.md`](../agent-guide/SESSION.md) — 세션 로그 (구조 변경 이력 포함)

**모델 리서치 / 인시던트**

- [`slm_research/README.md`](../agent-guide/docs/slm_research/README.md) — 리서치 문서 전체 목록 (연구계 전용, `agent-guide/docs/`)
- [`slm_research/models/qwen3.6.md`](../agent-guide/docs/slm_research/models/qwen3.6.md) — Qwen3.6 모델 상세 스펙·벤치마크·운영 메모
- [`slm_research/models/qwen3.5.md`](../agent-guide/docs/slm_research/models/qwen3.5.md) — Qwen3.5 조사
- [`slm_research/models/gemma4.md`](../agent-guide/docs/slm_research/models/gemma4.md) — Gemma 4 조사
- [`slm_research/topics/gemma4-vs-qwen.md`](../agent-guide/docs/slm_research/topics/gemma4-vs-qwen.md) — Gemma 4 vs Qwen 3.6 비교
- [`vllm/bugfix/2026-04-18_vllm_multimodal_encoder_cache.md`](vllm/bugfix/2026-04-18_vllm_multimodal_encoder_cache.md) — encoder cache race 해결 기록

### 15.3 외부 링크

- [vLLM 공식 문서](https://docs.vllm.ai/)
- [vLLM GitHub Issues](https://github.com/vllm-project/vllm/issues)
- [Gemma 4 26B-A4B (Google) HuggingFace](https://huggingface.co/google/gemma-4-26B-A4B-it)
- [Gemma 4 31B (Google) HuggingFace](https://huggingface.co/google/gemma-4-31B-it)
- [Qwen3.6 HuggingFace 모델 카드](https://huggingface.co/Qwen/Qwen3.6-27B-FP8)
- [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat) (vLLM이 호환하는 API 명세)
