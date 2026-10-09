# STT 운영 가이드 (운영자용)

> **대상**: STT 서버 운영자 (서버 기동·튜닝·트러블슈팅 담당)
> **메인 모델**: `mistralai/Voxtral-Mini-4B-Realtime-2602` (BF16, 4B params)
> **게이트웨이**: `:5018` → voxtral `:7172`(GPU 2, 메인) · `:5017` → 비교 PoC qwen3_asr `:7170`(GPU 0) / whisper_v3 `:7171`(GPU 2)
>
> 사용자(API 호출)용 가이드: [`STT_API_GUIDE.md`](STT_API_GUIDE.md)

> **vLLM 버전 (2026-10-10)**: 서버 이미지와 연구계 런처는 0.31.0입니다. **STT는 0.31.0에서 시험하지 않았습니다** — 버전업 때 STT를 쓰지 않아 시험 범위에서 뺐고, 이 문서의 실측은 0.20.2(nightly) 기준입니다. 다시 쓰기 전에 [§11](#11-qa-체크리스트) QA를 먼저 돌립니다. 0.31에서 바뀐 음성 경로는 [§8.3](#83-의존성-필수)에 적었습니다.

vLLM 기반 STT 게이트웨이의 **시스템 구조 / 기동·중지 / 모델 관리 / 설정 / 트러블슈팅**을 다룹니다. § 번호는 사용자 가이드(`STT_API_GUIDE.md` §1~§5)와의 cross-reference 안정성을 위해 6부터 시작합니다.

---

## 📑 목차

6. [시스템 구조](#6-시스템-구조)
7. [기동·중지·재시작](#7-기동중지재시작)
8. [모델 다운로드·관리](#8-모델-다운로드관리)
9. [인스턴스·게이트웨이 설정](#9-인스턴스게이트웨이-설정)
10. [트러블슈팅](#10-트러블슈팅)
11. [QA 체크리스트](#11-qa-체크리스트)
12. [호출 로그 동기화 (logging.sh)](#12-호출-로그-동기화-loggingsh)
13. [참고 자료](#13-참고-자료)

---

## 6. 시스템 구조

### 6.1 격리 페어 + 자동 디스커버리

vLLM 클러스터(LLM)와 동일한 패턴을 STT에도 도입했습니다. 모든 STT 인스턴스/게이트웨이는 `llm-serving/stt/` 하위에서 자기 완결적으로 동작합니다.

```
클라이언트
  │
  ▼
Gateway :5018            stt/gateways/5018.yaml  (메인 — voxtral realtime 분리)
  │  (transcription / realtime / chat 라우팅)
  │  HealthChecker · Admission · LB
  ▼
vLLM voxtral :7172       stt/instances/voxtral.yaml (GPU 2)

Gateway :5017            stt/gateways/5017.yaml  (비교 PoC — model 필드로 라우팅)
  ├─ vLLM qwen3_asr  :7170   stt/instances/qwen3_asr.yaml  (GPU 0)
  └─ vLLM whisper_v3 :7171   stt/instances/whisper_v3.yaml (GPU 2)
```

자동 디스커버리: 각 게이트웨이 yaml의 `discover_from: ../instances` → 그 디렉토리의 `*.yaml` 중 `gateway_port == 자기 포트`인 인스턴스만 backends에 등록.

### 6.2 LLM과의 책임 분리

| 레이어 | 디렉토리 | 책임 |
|--------|---------|------|
| LLM 서빙 | `llm-serving/vllm/` | Gemma/Qwen 등 chat 모델 (게이트웨이 :5015 / :5016) |
| STT 서빙 | `llm-serving/stt/` | Voxtral 등 음성 모델 (게이트웨이 :5018 메인 / :5017 비교 PoC) |
| 공용 코드 | `llm-serving/vllm/{start.sh, logging.sh, vllm_server_launcher.py, vllm_gateway.py}` | STT는 `start.sh` / `logging.sh`도 vllm 본체를 호출하는 thin wrapper (옵션 A, 2026-05-12). launcher/gateway는 같은 파이썬 모듈 재사용. |

> 게이트웨이 코드는 `vllm/vllm_gateway.py` 단일 출처. STT 게이트웨이는 chat/completions 외에도 `/v1/audio/transcriptions`, `/v1/realtime` 라우트를 자동 제공합니다.

### 6.3 Runtime json 격리

launcher가 `instances/.runtime/<name>.json`에 실제 listen 포트를 기록. 게이트웨이는 이 파일을 우선 참조해 backend port를 결정합니다.

```
stt/instances/.runtime/voxtral.json   ← STT 인스턴스 runtime
vllm/instances/.runtime/gemma.json    ← LLM 인스턴스 runtime
```

각 디렉토리에 격리되므로 STT/LLM이 같은 launcher 코드를 재사용해도 runtime 파일이 섞이지 않습니다 (`vllm_server_launcher.py:main`이 yaml dirname 기준으로 RUNTIME_DIR 동적 결정).

### 6.4 디렉토리 구조

```
llm-serving/stt/
├── README.md
├── MODEL_STUDY.md             # 후보 모델 비교 / 시나리오 분석
├── start.sh                   # thin wrapper → ../vllm/start.sh (env-driven 본체 호출, 옵션 A)
├── logging.sh                 # thin wrapper → ../vllm/logging.sh (S3 호출 카운트 5분 sync)
├── instances/
│   ├── voxtral.yaml           # gateway_port: 5018, 내부 :7172 (메인 운영)
│   ├── whisper_v3.yaml        # 비교 PoC, gateway_port: 5017, 내부 :7171
│   └── qwen3_asr.yaml         # 비교 PoC, gateway_port: 5017, 내부 :7170
├── gateways/
│   ├── 5017.yaml              # 비교 PoC 게이트웨이 (discover_from: ../instances)
│   └── 5018.yaml              # 메인 게이트웨이 (voxtral 전용 — realtime 분리)
└── logs/                      # 인스턴스/게이트웨이 stdout/stderr (자동 생성)
```

---

## 7. 기동·중지·재시작

> `stt/start.sh`는 `../vllm/start.sh`를 호출하는 thin wrapper(옵션 A, 2026-05-12). 운영 로직(up/down/status/restart, `[name]` 라우팅, confirm 프롬프트, fcntl 직렬화, atomic runtime write, cmdline PID 매칭)은 vllm 본체 단일 출처. 호출 사용법은 vllm/와 동일하며 라벨만 `═══ STT 클러스터 상태 ═══`로 표시. 다만 `speed`·`traffic`은 STT용 테스트 스크립트가 없어 wrapper가 빈 값으로 막고 "미지원"으로 거부한다(`test`는 `tests/test_stt_server.py`로 연결).

### 7.1 명령 요약

```bash
cd llm-serving/stt

./start.sh up                       # 인자 없음 → 전체 적용 confirm 프롬프트 [y/N]
./start.sh up all                   # 전체 인스턴스 + 모든 게이트웨이 기동 (확인 없이)
./start.sh up voxtral               # instances/voxtral.yaml 단독 기동 (게이트웨이 미터치)
./start.sh up 5017                  # gateways/5017.yaml 단독 기동 (인스턴스 미터치)
./start.sh down                     # 인자 없음 → 전체 중지 confirm 프롬프트 [y/N]
./start.sh down all                 # 모든 인스턴스 + 게이트웨이 중지 (확인 없이)
./start.sh down voxtral             # 인스턴스 단독 중지
./start.sh down 5017                # 게이트웨이 단독 중지
./start.sh status                   # 상태 확인
./start.sh restart                  # 인자 없음 → 전체 재시작 confirm 프롬프트 [y/N]
./start.sh restart <name>           # 단일 대상 재시작 (내부적으로 down→up)
./start.sh logs                     # 전체 인스턴스+게이트웨이 로그 tail -F (기본 -n 50)
./start.sh logs voxtral             # 인스턴스 단독 tail -F (logs/vllm_voxtral.log)
./start.sh logs 5017                # 게이트웨이 단독 tail -F (logs/gateway_5017.log)
./start.sh logs --lines 200         # 초기 라인 수 오버라이드 (-n N alias 가능)
./start.sh download voxtral         # 모델 다운로드/최신 동기화 (서빙 미터치, §8 참조)
./start.sh test                     # 기동된 게이트웨이 전부 QA 테스트 (미기동은 SKIP, §11 참조)
./start.sh test 5018                # 게이트웨이 단독
./start.sh test whisper_v3          # 인스턴스 단독 (게이트웨이 미경유 직접 호출)
```

`<name>`이 `instances/<name>.yaml`이면 인스턴스, `gateways/<name>.yaml`이면 게이트웨이로 자동 라우팅. `all` 명시는 확인 없이 전체 적용. 같은 이름이 양쪽에 있으면 즉시 에러.

> ⚠️ **안전 정책**: 무인자 호출은 [y/N] 기본 No로 묻는다 (다른 모델/게이트웨이를 실수로 stop시키는 사고 방지). 자동화 스크립트/cron 등 비대화 환경에서는 prompt 띄울 곳이 없으므로 무인자 호출이 거부되며 `'all'` 또는 이름을 명시해야 한다.

### 7.2 상태 의미

```
[UP]      vLLM voxtral (GPU 2, :7172, → gw :5018, PID ...)
[STARTING] ... (PID 살아있음 / health 응답 없음 — 모델 로딩 중)
[STALE]   ... (runtime PID launcher 아님/죽음 — './start.sh down <name>'으로 정리)
[DOWN]    ...

[UP]      Gateway 5018 (:5018, ready 1/1)
[STARTING] Gateway 5018 (:5018, ready 0/1 — 백엔드 대기/웜업 중)
```

### 7.3 첫 기동 소요 시간

| 단계 | 소요 |
|------|------|
| 모델 다운로드 (최초 1회) | ~35초 (17GB, network 의존) |
| weight 로딩 | ~3초 (8.38 GiB BF16) |
| KV cache 프로파일링 | ~15초 |
| CUDA graph capture (PIECEWISE) | ~1초 |
| 게이트웨이 health probe | ~10초 (백엔드 ready 잡힌 직후) |
| **합계 (재기동)** | **~30초** (다운로드 제외) |

---

## 8. 모델 다운로드·관리

### 8.1 자동 다운로드

`instances/<name>.yaml`의 `model: <HF ID>` + `download_dir: /models/STT` 조합으로 launcher가 첫 기동 시 `snapshot_download`로 다운로드. Voxtral은 Apache 2.0 → HF_TOKEN 불필요.

이미 받은 모델을 HF 최신 리비전과 맞추려면 `./start.sh download <name>` (변경 파일만 증분 다운로드, 서빙 미터치 — vllm 본체의 `download` 명령이 wrapper로 그대로 동작). `up`은 로컬 모델이 있으면 네트워크를 보지 않는다.

```yaml
model: mistralai/Voxtral-Mini-4B-Realtime-2602
download_dir: /models/STT
# → /models/STT/mistralai/Voxtral-Mini-4B-Realtime-2602/ 에 저장
```

### 8.2 폐쇄망 운영

EC2 외부망 차단 환경에서는 외부망 PC에서 사전 다운로드 → S3 → `/models/STT/` 로 동기화:

```bash
# 외부망 PC
huggingface-cli download mistralai/Voxtral-Mini-4B-Realtime-2602 \
  --local-dir ./Voxtral-Mini-4B-Realtime-2602
aws s3 sync ./Voxtral-Mini-4B-Realtime-2602 \
  s3://hgi-ai-res/models/STT/mistralai/Voxtral-Mini-4B-Realtime-2602/

# 운영계 EC2
sudo aws s3 sync s3://hgi-ai-res/models/STT/ /models/STT/
```

### 8.3 의존성 (필수)

Voxtral은 **`soundfile`, `soxr`, `librosa`** 가 vLLM serving 시 필수 (없으면 `EngineCore failed to start`).

- **서버 이미지**: `aws/requirements.txt`에 vLLM 0.31의 audio 의존성(`av`, `scipy`, `soundfile`, `soxr`, `mistral_common[audio]`)과 `librosa`가 `==`로 고정돼 들어 있습니다. 따로 설치하지 않습니다.
- **연구계 컨테이너**: 런처가 `SERVING_VLLM_BIN`의 0.31 가상환경(`/home/hjjo/venvs/vllm-0.31`)으로 STT도 띄웁니다. 이 가상환경에는 위 패키지가 없고 `~/.local`도 보지 않으므로(`include-system-site-packages = false`), STT를 쓰기 전에 이미지와 같은 버전으로 넣습니다.

```bash
uv pip install --python /home/hjjo/venvs/vllm-0.31/bin/python \
  av==19.0.1 soundfile==0.14.0 soxr==1.1.0 librosa==0.11.0 scipy==1.17.1
```

**0.31의 음성 읽기 경로** (`vllm/multimodal/media/audio.py`): 기본(`auto`)은 soundfile → torchcodec → PyAV 순서로 시도합니다. soundfile로 읽은 음성이 모델 샘플레이트(Whisper·Voxtral 16kHz)와 다르면 PyAV로 리샘플하므로, `av`가 없으면 16kHz가 아닌 입력이 실패합니다. 16kHz mono로 보내면 리샘플을 타지 않습니다.

---

## 9. 인스턴스·게이트웨이 설정

### 9.1 메모리 핏 (instances/*.yaml — 3종 통일)

3종 인스턴스는 동일 키 구조(2026-05-12 yaml 통일)이며 모델별 값만 차이:

| 인스턴스 | 노출 경로 | gpu_memory_utilization | max_num_seqs | max_model_len | 예약(L40S 46GB) | 비고 |
|---|---|---|---|---|---|---|
| **voxtral** | gw `:5018` → `:7172` (GPU 2) | 0.4 | 1 | 16384 | 18.4 GiB | 메인 운영 (실시간 + transcription) |
| **qwen3_asr** | gw `:5017` → `:7170` (GPU 0) | 0.50 | 8 | 8192 | ~23 GiB | 비교 PoC |
| **whisper_v3** | gw `:5017` → `:7171` (GPU 2) | 0.20 | 5 | 모델 config 자동(448) | ~9 GiB | 비교 PoC, 시나리오 E 1순위 |

L40S 46GB × util별 동작 (voxtral 실측):

| util | 예약 | weight | KV 가용 | KV token | 권장 max_num_seqs |
|------|------|--------|---------|---------|---------|
| 0.35 | 16.1 GiB | 8.38 | 4.24 GiB | 2,160 | 1 (단일 세션 PoC) |
| 0.40 (현재) | 18.4 GiB | 8.38 | ~6.5 GiB | ~3,300 | 2~3 |
| 0.50 | 23.0 GiB | 8.38 | 10.9 GiB | 5,568 | 4 (max_concurrency 2.71x) |

> vLLM은 continuous batching이라 `max_num_seqs`는 동시 in-flight 상한일 뿐, 실제 동시 N 세션 처리는 KV cache 슬롯이 제한합니다. 부족하면 일부 시퀀스가 swap out(preemption) → 사실상 일부 순차화. 그래서 `gpu_memory_utilization`과 `max_num_seqs`는 **목표 동시 stream 수에 맞춰 함께** 조정합니다.

### 9.2 vLLM 컴파일 모드 (모델카드 권장)

```yaml
env:
  VLLM_DISABLE_COMPILE_CACHE: "1"   # launcher가 subprocess.env에 머지
compilation_config:
  cudagraph_mode: PIECEWISE         # 모델카드 권장
```

> `_LAUNCHER_KEYS`에 `env`가 포함되므로 vllm serve로 전달되지 않고 launcher가 환경변수로만 export.

### 9.3 게이트웨이 과부하 차단 (gateways/5017.yaml·5018.yaml 공통)

```yaml
overload:
  enabled: true
  max_inflight_requests: 20   # 즉시 백엔드로 넘길 최대 요청
  max_queue_size: 40
  queue_timeout_seconds: 180
  retry_after_seconds: 10
```

429 + `Retry-After` 헤더로 클라이언트 재시도 유도. 실제 동시 처리는 인스턴스 `max_num_seqs`(voxtral 현재 1)와 KV 슬롯이 제한하므로, 동시 N 세션으로 확장 시 인스턴스 쪽(util·max_num_seqs)과 함께 검토.

### 9.4 STT 전용 게이트웨이 차이점 (vs LLM 게이트웨이)

| 키 | LLM(:5015) | STT(:5017/:5018) | 사유 |
|----|------------|------------|------|
| `warmup.enabled` | true | **false** | STT는 chat dummy 추론으로 웜업 불가 → /health 프로브만 |
| `prefix_cache_warmup.enabled` | true | **false** | STT는 시스템 프롬프트 캐싱 패턴과 무관 |
| `http_client.timeout_seconds` | 300 | **600** | audio 길이에 비례 (chat보다 길게) |

---

## 10. 트러블슈팅

| 증상 | 원인 / 해결 |
|------|-------------|
| `EngineCore failed to start` + `ImportError: soundfile` | Voxtral 의존성 미설치. 연구계는 0.31 가상환경에 설치([§8.3](#83-의존성-필수)), 서버 이미지는 `aws/requirements.txt`로 들어감 |
| `vllm: error: unrecognized arguments: --task transcription` | vLLM 0.20.x에서 `--task` CLI 인자가 제거되고 model config 기반 자동 감지로 통합됨. launcher `_LAUNCHER_KEYS`(`vllm_server_launcher.py:74`)가 yaml의 `task` 키를 필터하여 vllm serve에 전달하지 않도록 보장(`task` 포함 런처 전용 키 8개). yaml의 `task` 키는 PoC 비교 운영 메타로만 보존. 자동 감지가 부정확한 모델이 나오면 launcher에 `--runner` 매핑 분기 추가. |
| 게이트웨이 `/health`가 503 + `ready: 0/1` | 백엔드 voxtral가 미기동 또는 로딩 중. `./start.sh status` → `[STARTING]`이면 1~2분 대기 |
| 게이트웨이 로그 `realtime 백엔드 연결 실패` | voxtral.yaml의 `gateway_port`(5018)와 게이트웨이 포트 일치 확인. 디스커버리 결과는 게이트웨이 기동 로그(`logs/gateway_<port>.log`)에 표시 |
| `[STALE]` 표시 | launcher가 SIGKILL/crash로 죽음. `./start.sh down voxtral`로 runtime 파일 정리 |
| GPU OOM | `gpu_memory_utilization` 낮춤(0.30~0.35). 또는 LLM 인스턴스가 같은 GPU 점유 중인지 `nvidia-smi`로 확인 |
| Transcription HTTP 504 | 600s 초과. 오디오를 더 짧게 분할하거나 해당 게이트웨이 yaml의 `http_client.timeout_seconds`를 상향 |
| WebSocket close 4429 | 과부하 차단. `max_inflight_requests`/`max_queue_size` 또는 클라이언트 동시성 조정 |
| WebSocket close 4500 | 게이트웨이 → 백엔드 WS 연결 실패. 백엔드 vllm 로그(`logs/vllm_voxtral.log`) 확인 |
| 코드 수정 반영 안 됨 | `__pycache__` 캐시. `find /workspace -name __pycache__ -exec rm -rf {} +` 후 재기동 |

---

## 11. QA 체크리스트

게이트웨이 + 인스턴스 정상 기동 후, 자동 검증은 `./start.sh test`로 돌립니다. `tests/test_stt_server.py`의 세 카테고리(`infra`·`transcription`·`edge`)를 실행하며, 하나라도 실패하면 종료 코드 1을 냅니다.

```bash
./start.sh test                 # 기동된 게이트웨이 전부 (5017·5018)
./start.sh test 5018            # voxtral 게이트웨이만
./start.sh test whisper_v3      # 인스턴스 직접 (게이트웨이 미경유)
./start.sh test --category infra
```

아래는 개별 항목을 손으로 확인할 때의 절차입니다.

```bash
# 1) 게이트웨이 health (voxtral 메인 = 5018)
curl -s -w "\n[%{http_code}]\n" http://localhost:5018/health
# {"status":"ok","ready":1,"total":1}  [200]

# 2) 모델 등록 확인
curl -s http://localhost:5018/v1/models | python3 -m json.tool

# 3) Smoke transcription (1초 사인파)
python3 -c "
import numpy as np, soundfile as sf
sr=16000; t=np.linspace(0,1,sr,endpoint=False)
sf.write('/tmp/sine_1s.wav', (0.1*np.sin(2*np.pi*440*t)).astype('float32'), sr)
"
curl -s -w "\n[%{http_code} (%{time_total}s)]\n" \
  http://localhost:5018/v1/audio/transcriptions \
  -F "file=@/tmp/sine_1s.wav" \
  -F "model=Voxtral-Mini-4B-Realtime-2602" \
  -F "language=ko" \
  -F "temperature=0"
# {"text":"","usage":{"type":"duration","seconds":1}}  [200]

# 4) Realtime WebSocket 핸드셰이크
python3 - <<'PY'
import asyncio, json, websockets
async def main():
    async with websockets.connect("ws://localhost:5018/v1/realtime?model=Voxtral-Mini-4B-Realtime-2602") as ws:
        msg = await ws.recv()
        print("session.created OK:", json.loads(msg)["type"])
asyncio.run(main())
PY
# session.created OK: session.created

# 5) Smoke transcription — 비교 PoC 게이트웨이(:5017, model 필드로 백엔드 라우팅)
curl -s -w "\n[%{http_code} (%{time_total}s)]\n" \
  http://localhost:5017/v1/audio/transcriptions \
  -F "file=@/tmp/sine_1s.wav" \
  -F "model=whisper-large-v3" \
  -F "language=ko" \
  -F "temperature=0"
# {"text":"","usage":{"type":"duration","seconds":1}}  [200]  (디버그용 직접 호출은 :7171)
```

위 1~4번이 모두 통과하면 5018 게이트웨이 + voxtral 백엔드는 운영 가능 상태입니다. 비교 PoC(`whisper_v3` / `qwen3_asr`)는 5번 절차로 확인.

---

## 12. 호출 로그 동기화 (logging.sh)

`stt/logging.sh`는 `../vllm/logging.sh`를 호출하는 thin wrapper(옵션 A). vLLM 호출 로그를 5분 간격으로 S3에 sync하여 인스턴스별 호출 카운트 통계를 생성합니다. **read-only**(stat / tail -c / awk)로 로그를 읽을 뿐, vLLM 프로세스·포트·파일에 일절 손대지 않으므로 서비스 영향 없음.

### 12.1 환경 분리 (STT vs LLM)

| 클러스터 | S3 prefix | 기본 인스턴스 |
|---|---|---|
| LLM (vllm/) | `s3://hgi-ai-res/logs/vllm/` | `prd-gemma` |
| STT (stt/) | `s3://hgi-ai-res/logs/stt/` | `voxtral` |

STT wrapper(`stt/logging.sh`)가 `WORK_DIR=$HERE`, `INST_DEFAULT=voxtral`, `S3_PREFIX=logs/stt`를 export하여 본체 호출. wrapper 30줄, 본체 로직은 단일 출처.

### 12.2 시작·중지·확인

```bash
cd llm-serving/stt

./logging.sh                    # 기본 voxtral 시작
./logging.sh whisper_v3         # 인스턴스 명시 시작
./logging.sh stop               # 중지

tail -f logs/logging.out        # sync 로그 watch (5분마다 "uploaded N date(s)")
cat logs/.logging.pid           # 데몬 PID
```

### 12.3 매칭·일자 라우팅 동작

- **필터**: `POST /v1/` 라인만 추출. `/v1/audio/transcriptions`(POST)는 매칭, `/v1/realtime`(WebSocket upgrade)은 미매칭 — **본 통계는 transcription 호출만 포함**.
- **일자 자동 분배**: vLLM 로그 안의 `INFO MM-DD ...` 라인(throughput 10초 주기 등)에서 일자를 추출하여 호출 라인을 해당 일자 파일로 라우팅. 자정 경계의 5분 chunk도 양일에 정확히 분배되며, 며칠치 백로그가 쌓여 있어도 첫 sync에서 일자별로 자동 분할.
- **truncate 감지**: 로그 파일 크기가 줄면 offset을 0으로 리셋(vLLM 재기동 대응).

### 12.4 호출 카운트 확인 (S3)

```bash
# 오늘자 voxtral transcription 호출 수
aws s3 cp s3://hgi-ai-res/logs/stt/voxtral/$(date +%F).log - | wc -l

# 특정 일자 whisper_v3 호출 수
aws s3 cp s3://hgi-ai-res/logs/stt/whisper_v3/2026-05-13.log - | wc -l

# 인스턴스별 일자 파일 목록
aws s3 ls s3://hgi-ai-res/logs/stt/voxtral/
```

### 12.5 운영 트러블슈팅

| 증상 | 원인 / 해결 |
|------|-------------|
| `already running (PID ...)` | 이미 데몬 실행 중. 의도적이면 무시, 재시작 필요 시 `./logging.sh stop` 후 재실행 |
| `skip — logs/vllm_<inst>.log 없음` | 인스턴스 미기동 또는 다른 인스턴스명 지정. `./start.sh status`로 확인 |
| S3 업로드 0건이 5분 이상 지속 | (1) `POST /v1/` 라인 미발생(트래픽 없음) — 정상 (2) AWS credential 만료 — `aws s3 ls` 점검 |
| 자정 경계 호출이 다음날로 합쳐짐 | vLLM 로그에 `INFO MM-DD` 일자 표기 라인이 없는 경우(이례적). 통상 throughput 라인이 10초마다 찍히므로 발생 빈도 매우 낮음 |

---

## 13. 참고 자료

- 사용자 호출 가이드: [`STT_API_GUIDE.md`](STT_API_GUIDE.md) §1~§5
- 배포 절차(로컬 → S3 → 운영계): [`DEPLOY_GUIDE.md`](DEPLOY_GUIDE.md)
- 후보 모델 비교 / 시나리오: [`stt/MODEL_STUDY.md`](stt/MODEL_STUDY.md)
- LLM 운영 가이드(같은 페어 패턴): [`VLLM_OPS_GUIDE.md`](VLLM_OPS_GUIDE.md)
- Voxtral 모델카드: <https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602>
- OpenAI Audio API: <https://platform.openai.com/docs/api-reference/audio>
- OpenAI Realtime API: <https://platform.openai.com/docs/api-reference/realtime>
