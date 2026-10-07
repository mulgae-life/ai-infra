# 🚀 llm-serving 배포 가이드

`llm-serving/` 코드를 **로컬 → S3 → 운영계 컨테이너**로 옮기고, 모델 서버를 **안쪽(vLLM)부터 바깥(진입점)** 순으로 띄우는 절차.

> 인프라 셋업(EC2/Docker/컨테이너 기동)은 [`../aws/SETUP_GUIDE.md`](../aws/SETUP_GUIDE.md). 본 문서는 그 위에서 **서빙 코드/모델만** 다룹니다.

---

## 한눈에

**① 배포 파이프라인** — 코드는 S3를 경유해 운영계 컨테이너로, 모델은 컨테이너에서 자동 다운로드.

```
[로컬]                            [S3]                          [운영계 컨테이너]
/workspace/ai-infra/llm-serving  →  s3://hgi-ai-res/hjjo/  →  /workspace/llm-serving/
   (start.sh push)                    llm-serving/              (start.sh pull → 클러스터별 start.sh up)

                                                              /models/  ← 첫 기동 시 자동 다운로드
                                                                          (갱신은 ./start.sh download — 폐쇄망은 네트워크 개방 시점에)
```

**② 서비스 진입점 맵** — 배포 후 클라이언트가 들어가는 **외부 포트**와 그 뒤 내부 흐름. 외부엔 진입점만 열고 내부 포트는 방화벽으로 차단한다.

```
── 비PII 모드 (현재 기본) — 게이트웨이가 곧 외부 입구 ──
 :5015  gemma 연구   →  게이트웨이 → vLLM :7071  (gemma-26b, GPU 0,1)
 :5501  gemma 운영   →  게이트웨이 → vLLM :7070  (prd-gemma, GPU 0)   · 운영=별도 서버
 :5018  voxtral STT  →  게이트웨이 → vLLM :7172  (GPU 2)              · 모드 무관 항상 이 구조
 :5017  STT 비교 PoC →  게이트웨이 → qwen3_asr :7170 / whisper_v3 :7171 (model 필드 라우팅)

── PII 모드 (선택 — 프록시가 같은 외부 포트를 인수) ──
 :5015  gemma 연구   →  PII 프록시 → 게이트웨이 :6015 → vLLM :7070  (gemma, GPU 0,1)
 :5016  qwen  연구   →  PII 프록시 → 게이트웨이 :6016 → vLLM :7080  (GPU 0,1)
 :5501  gemma 운영   →  PII 프록시 → 게이트웨이 :6501 → vLLM :7070  (prd-pii-gemma, GPU 0)
 :5502  qwen  운영   →  PII 프록시 → 게이트웨이 :6502 → vLLM :7080  (prd-pii-qwen, GPU 0)
 :8911 / :8901  NER (vmaca123 / townboy, GPU 3)  ←  PII 프록시가 호출
```

> 외부 호출 주소는 모드와 무관하게 불변이고, **포트당 모드는 택일**이다. PII 모드에서는 **게이트웨이가 내부 포트로 한 칸 물러나고 외부 입구를 PII 프록시가 인수**하므로 기동 순서가 달라진다([§3](#3-기동)). qwen은 비PII 게이트웨이가 아직 없어 PII 모드 구성만 있다. 깊은 토폴로지는 [`VLLM_OPS_GUIDE.md`](VLLM_OPS_GUIDE.md) §6.

---

## 1. 로컬 → S3 (코드 업로드)

```bash
cd /workspace/ai-infra/llm-serving && ./start.sh push
```

> `logs/`, `__pycache__/`, 런처 임시 config(`.vllm_serve_*`·`.runtime/`), `samples/`, `audit.salt`는 런타임 산출물/시크릿이라 `start.sh`가 자동 제외. 모델 조사 문서는 연구계 전용이라 2026-10-06에 `agent-guide/docs/slm_research/`로 옮겨 배포 대상(`llm-serving/`) 밖에 있다 — 운영 서버에는 서빙에 필요한 코드·설정·테스트만 간다. 이동 전 운영 서버에 내려간 `vllm/slm_research/`가 있으면 다음 `pull`이 `--delete`로 지운다.

> ⚠️ `push`는 **전체 교체**입니다. S3 프리픽스를 비운 뒤 올려 로컬과 정확히 일치시킵니다. 증분만 올리면 로컬에서 지우거나 이름을 바꾼 파일이 S3에 남아 `pull` 때 되살아나기 때문입니다. 업로드 단계에서 중단되면 프리픽스가 빈 상태로 남으므로 반드시 `push`를 다시 실행하세요. 규모를 먼저 보려면 `./start.sh push --dryrun`을 쓰면 삭제 단계까지 미리보기로 동작합니다.

> 루트의 `start.sh`는 **코드 배포**(push·pull) 전용이고, `vllm/`·`stt/`·`pii/` 아래의 `start.sh`는 **서비스 제어**입니다. 이름이 같으니 실행 위치를 확인하세요. 제어 명령은 클러스터마다 다릅니다. `vllm/`은 up·down·status·logs·download·test·speed·traffic 전부, `stt/`는 speed·traffic을 뺀 나머지, `pii/`는 up·down·status만 받습니다.

---

## 2. 운영계 컨테이너 → S3 다운로드

운영계 EC2 호스트에서 컨테이너 진입 후 작업:

```bash
docker exec -it gemma bash               # 컨테이너 이름은 환경에 맞게 (예: gemma, llm-root, jin)

# 컨테이너 안에서 — 최초 1회는 start.sh가 아직 없어 raw 명령 (이후 갱신은 ./start.sh pull)
sudo aws s3 sync s3://hgi-ai-res/hjjo/llm-serving/ /workspace/llm-serving/
sudo chmod +x /workspace/llm-serving/start.sh /workspace/llm-serving/*/start.sh
```

> 컨테이너 이름 확인: `docker ps`. user.sh 로 띄운 컨테이너는 이름 그대로(`gemma` 등), 메인 compose 는 `llm-<USERNAME>`.

---

## 3. 기동

### 3.1 진입점 구조

기동하기 전에 **무엇을 어떤 순서로 띄우는지** 잡고 간다. 핵심은 **운용 모드(비PII/PII)에 따라 외부 입구와 기동 단위가 달라진다**는 것.

| 외부 진입점 | 서비스 | 모드 | 내부 경로 | 기동 단위 |
|------------|--------|:---:|-----------|-----------|
| `:5015` | LLM gemma (연구) | 비PII (현재) | 게이트웨이 → vLLM `:7071` | `gemma-26b` + `5015` |
| `:5015` | LLM gemma (연구) | PII | 프록시 → 게이트웨이 `:6015` → vLLM `:7070` | `gemma` + `6015` + `pii up` |
| `:5016` | LLM qwen (연구) | PII만 | 프록시 → 게이트웨이 `:6016` → vLLM `:7080` | `qwen` + `6016` + `pii up 5016` |
| `:5501` | LLM gemma (운영) | 비PII (현재) | 게이트웨이 → vLLM `:7070` | `prd-gemma` + `5501` |
| `:5501` | LLM gemma (운영) | PII | 프록시 → 게이트웨이 `:6501` → vLLM `:7070` | `prd-pii-gemma` + `6501` + `pii up 5501` |
| `:5502` | LLM qwen (운영) | PII만 | 프록시 → 게이트웨이 `:6502` → vLLM `:7080` | `prd-pii-qwen` + `6502` + `pii up 5502` |
| `:5018` | STT voxtral | — | 게이트웨이 → vLLM `:7172` | `voxtral` + `5018` |
| `:5017` | STT 비교 PoC | — | 게이트웨이 → `:7170`/`:7171` | `qwen3_asr`/`whisper_v3` + `5017` |

> ✅ **비PII 모드(현재 기본)**·STT는 게이트웨이가 곧 외부 입구 — 인스턴스 → 게이트웨이 두 단계로 끝난다.
> ✅ **PII 모드**는 **안쪽부터**(vLLM → 게이트웨이 → 프록시) 올린다. 프록시가 외부 입구를 인수하므로 게이트웨이·vLLM이 먼저 떠 있어야 한다.
> ⚠️ 같은 외부 포트에 두 모드를 동시에 쓸 수 없다(포트당 택일). `./start.sh up all`은 비PII·PII 인스턴스를 모두 올려 GPU가 충돌할 수 있으니 **이름 명시 기동**을 권장.

### 3.2 gemma 기동 (비PII 기본 / PII 모드)

운영계(`:5501`) 기준. 연구계(`:5015`)는 괄호 안 값으로 치환한다. (qwen은 [§3.4](#34-qwen-llm-옵션-pii-모드-구성만))

**비PII 모드 (현재 기본)** — 게이트웨이가 곧 외부 입구, 두 단계로 끝:

```bash
cd /workspace/llm-serving/vllm
./start.sh up prd-gemma      # ① vLLM (연구: gemma-26b) — 모델 미보유 시 자동 다운로드(→ /models/LLM/), UP까지 1~5분
./start.sh up 5501           # ② 게이트웨이 = 외부 입구 (연구: 5015)
./start.sh status            # UP 확인
```

**PII 모드 (안쪽부터)**:

```bash
# ① vLLM 인스턴스 — 모델 미보유 시 자동 다운로드(→ /models/LLM/), UP까지 1~5분
cd /workspace/llm-serving/vllm
./start.sh up prd-pii-gemma  # 운영 prd-pii-gemma=GPU0 (연구 gemma=GPU0,1)
./start.sh status            # UP 확인

# ② 게이트웨이 — 내부 전용(127.0.0.1). gateway_port로 위 인스턴스 자동 매칭
./start.sh up 6501           # (연구: 6015)

# ③ PII 프록시 — NER 2종(GPU3) + 프록시. 외부 :5501 입구를 인수
cd ../pii
bash start.sh up 5501        # (연구: 인자 없이 `bash start.sh up` = 5015)
bash start.sh status         # NER + 프록시 health
```

> 🔒 **방화벽 전제**: 외부엔 **PII 프록시(gemma `:5015`/`:5501`, qwen `:5016`/`:5502`)만** 열고, 게이트웨이(`:6015`/`:6016`/`:6501`/`:6502`)·vLLM(`:7070`/`:7080`)·NER(`:8911`/`:8901`)은 외부 차단해야 enforcement가 성립한다(인스턴스 yaml `host: 0.0.0.0`이면 특히 주의). 하나라도 외부에서 닿으면 검사를 건너뛰는 직행 경로가 생긴다.
> 🔑 **감사 salt**: `pii/start.sh`가 `configs/audit.salt`(없으면 권한 600으로 자동 생성)에서 읽어 `PII_AUDIT_SALT`로 주입한다. 환경별 시크릿이라 S3 동기화에서 제외된다.
> 📋 기동·정책(차단 타입·마스킹·bypass) 상세는 [`pii/README.md`](pii/README.md), [`VLLM_OPS_GUIDE.md`](VLLM_OPS_GUIDE.md) §7.9.

### 3.3 STT (Voxtral, 독립 서비스)

STT는 PII를 거치지 않고 게이트웨이가 곧 외부 입구다. vLLM 패턴 동일 — voxtral은 `instances/voxtral.yaml` ↔ `gateways/5018.yaml` 페어, 비교 PoC 2종(qwen3_asr/whisper_v3)은 `gateways/5017.yaml` 소속.

```bash
cd /workspace/llm-serving/stt
./start.sh up voxtral        # voxtral 인스턴스 (모델 미보유 시 자동 다운로드 → /models/STT/, 17GB)
./start.sh up 5018           # voxtral 게이트웨이 = 외부 입구
./start.sh status            # UP/STARTING 확인
# 비교 PoC: ./start.sh up qwen3_asr(또는 whisper_v3) → ./start.sh up 5017
```

> ⚠️ **Voxtral 의존성**: 컨테이너 재배포 시 `pip install soundfile soxr librosa` 필요. 영구 등재는 `aws/requirements.txt`. 미설치 시 vLLM 기동 직후 `EngineCore failed to start` + `ImportError: soundfile` 로 fail.
> ⚠️ **GPU 충돌**: voxtral(GPU 2)은 LLM(GPU 0·1)과 충돌 없음. 비교용 `qwen3_asr`(GPU 0)는 LLM과, `whisper_v3`(GPU 2)는 voxtral과 겹침 → 충돌 대상 먼저 stop(`./start.sh down <name>` — 이름 명시 권장). 상세는 [`stt/README.md`](stt/README.md) "운영 주의".

### 3.4 Qwen (LLM 옵션, PII 모드 구성만)

Qwen은 현재 **PII 모드 구성만** 있다(비PII 게이트웨이 미구성 — 필요 시 `gateways/5016.yaml` 신설). PII 프록시 뒤에서 안쪽부터 기동하며(연구 `:5016` / 운영 `:5502`), NER은 같은 서버의 gemma 프록시와 공유한다.

```bash
# 연구계 (외부 :5016)
cd /workspace/llm-serving/vllm
./start.sh up qwen           # ① 인스턴스(:7080, GPU 0,1)
./start.sh up 6016           # ② 게이트웨이(내부 127.0.0.1:6016)
cd ../pii
bash start.sh up 5016        # ③ PII 프록시(외부 :5016 인수)

# 운영계 (외부 :5502) — prd-pii-qwen=GPU0
#   up prd-pii-qwen → up 6502 → bash start.sh up 5502
```

---

## 4. 동작 확인 (테스트 / 로그)

```bash
cd /workspace/llm-serving/vllm

# QA 테스트 — 모델명은 /v1/models API에서 자동 추출 (--model 불필요)
# (:5015는 외부 진입점 — 비PII 모드는 게이트웨이 직접, PII 모드는 프록시 경유. 운영계는 5501)
python tests/test_vllm_server.py --base-url http://localhost:5015
python tests/test_vllm_server.py --base-url http://localhost:5015 --category infra inference   # 일부만
python tests/test_vllm_server.py --list                                                         # 카테고리 목록

# 속도 비교 테스트 (게이트웨이별로 호출 — 같은 results 파일에 모델명 자동 추출하여 누적 append)
python tests/speed_test.py --base-url http://localhost:5015                  # Gemma 진입점
python tests/speed_test.py --base-url http://localhost:5016                  # Qwen 게이트웨이 (같은 파일에 이어 쌓임)
python tests/speed_test.py --base-url http://localhost:5015 --quick          # 빠른 검증 (동시성 1, max_tokens 512)

# 로그 — 매 실행마다 tests/logs/test_YYYYMMDD_HHMMSS.log에 자동 저장 (ANSI 색 제거)
ls -lt tests/logs/test_*.log | head -3
grep -B1 -A20 "FAIL " tests/logs/test_20260430_144909.log     # 실패만 추출

# PII 정확성 회귀 평가 (한국어 합성 케이스셋, 타입별 precision/recall + 과탐)
cd ../pii && python tests/eval_pii.py
```

> 실패/예외 시 detail에 **요청 method·URL·body + 응답 status·body + (예외 시) 전체 traceback**이 자동 부착됩니다. 상세 우선순위/포맷은 [`VLLM_OPS_GUIDE.md`](VLLM_OPS_GUIDE.md) §14.1.

---

## 5. 코드 변경 반영

```bash
# (로컬) 수정 후 S3 재업로드
cd /workspace/ai-infra/llm-serving && ./start.sh push

# (운영계) 재다운로드 + 재시작
cd /workspace/llm-serving && sudo ./start.sh pull
cd vllm && ./start.sh restart <name>  # 또는 stt; 무인자는 [y/N] 전체 재시작 프롬프트, 'all'은 확인 없이 전체

# 모델(가중치·chat template) 갱신은 코드 sync와 별개 — 네트워크 개방 시점에 증분 동기화
cd /workspace/llm-serving/vllm && ./start.sh download <name>   # 이후 네트워크 차단 후 up 가능 (up은 네트워크 미접근)

# PII 코드만 고쳤다면 프록시만 재기동 (NER은 로딩 비용이 커 유지)
cd /workspace/llm-serving/pii && bash start.sh down 5501 && bash start.sh up 5501  # 연구계는 5015
```

> 로컬에서 파일을 지우거나 이름을 바꿨어도 별도 옵션이 필요 없다. `push`가 S3 프리픽스를 비우고 다시 올리고, `pull`이 `--delete --exact-timestamps`로 받으므로 로컬 → S3 → 운영계가 그대로 일치한다. 제외 목록(`logs/`·`.runtime/`·`audit.salt` 등)은 `--delete`에서도 보호되어 운영계의 로그와 시크릿은 지워지지 않는다. 규모를 먼저 보려면 `--dryrun`을 붙인다.
>
> **`pull` 전에 운영계 디렉토리를 지울 필요가 없다.** `aws s3 sync`는 체크섬을 보지 않고 크기와 수정시각만 비교하는데, 기본 규칙이 "크기가 같고 받는 쪽이 더 새로우면 스킵"이라 갱신된 파일이 조용히 넘어가는 일이 있었다. 받은 파일의 mtime이 S3 객체의 시각이 아니라 다운로드한 시각으로 찍혀 로컬이 늘 더 새롭기 때문이다. `--exact-timestamps`가 그 판정을 막는다. 디렉토리를 통째로 지우는 방식과 달리 위 제외 목록이 살아남는 것도 이점이다.

---

## 6. 트러블슈팅

| 증상 | 해결 |
|------|------|
| `aws: command not found` (운영계) | 컨테이너에 aws CLI 미설치. 호스트에서 `sudo aws s3 sync … /volume/workspace/<USERNAME>/llm-serving/` 후 컨테이너 안에서 작업 |
| `Unable to locate credentials` | EC2 IAM Role 미부여 또는 `aws configure` 미실행 |
| `Permission denied: ./start.sh` | S3가 실행권한을 보존하지 않아 raw `sync`로 받으면 644가 된다. `sudo chmod +x llm-serving/start.sh llm-serving/*/start.sh` |
| 모델 다운로드 401/403 | gated 모델 + HF_TOKEN 미설정. `~/aws/.env` 의 `HF_TOKEN` 확인 후 `docker compose up -d --force-recreate` |
| 모델 다운로드 timeout (폐쇄망) | EC2 외부망 차단. 네트워크 일시 개방 후 `./start.sh download <name>` → 재차단 → `up`(네트워크 미접근). 개방 불가 시 외부망 PC에서 사전 다운로드 → S3 → `/volume/models/` 이관. 절차는 [`VLLM_OPS_GUIDE.md`](VLLM_OPS_GUIDE.md) §8.2 참조 |
| 코드 수정이 반영 안 됨 | `__pycache__` 캐시. `find /workspace/llm-serving -name __pycache__ -exec rm -rf {} +` 후 재시작 |
| GPU OOM | `vllm/instances/<name>.yaml` 의 `gpu_memory_utilization` 낮추기, 또는 다른 인스턴스 stop (`./start.sh down <name>`) |
| PII 프록시 502/503 | 게이트웨이(:6015/:6501) 또는 vLLM이 안 떠 있음. PII는 안쪽부터 기동([§3.2](#32-gemma-기동-비pii-기본--pii-모드)). `pii/start.sh status`로 NER·프록시 health 확인 |
| 정상 요청이 422 차단 | PII 검사가 주민·카드로 오탐. 케이스셋 회귀 평가 `cd pii && python tests/eval_pii.py`로 재현·확인. 정책은 `pii/configs/proxy.5501.yaml`(운영)·`proxy.yaml`(연구) |
| PII 검사가 안 걸림(원문 통과) | ① 헤더 `X-PII-Mode: bypass` 우회(기본 활성, 감사로그 `action=bypass`) ② 외부에 게이트웨이/vLLM 포트가 직접 열려 프록시 우회. 방화벽 점검([§3.1](#31-진입점-구조) 전제) |

---

## 참고

- 인프라/컨테이너: [`../aws/SETUP_GUIDE.md`](../aws/SETUP_GUIDE.md)
- vLLM API 호출 (사용자): [`VLLM_API_GUIDE.md`](VLLM_API_GUIDE.md)
- vLLM 운영 상세 (토폴로지·모델 교체·메모리 표): [`VLLM_OPS_GUIDE.md`](VLLM_OPS_GUIDE.md)
- PII 가드 개요·기동·정책: [`pii/README.md`](pii/README.md), [`VLLM_OPS_GUIDE.md`](VLLM_OPS_GUIDE.md) §7.9
- PII 모델 라이선스 고지 / 모델 조사: [`pii/NOTICE.md`](pii/NOTICE.md), [`pii/pii_model_research.md`](pii/pii_model_research.md)
- STT API 호출 (사용자): [`STT_API_GUIDE.md`](STT_API_GUIDE.md)
- STT 운영 (시스템 구조, 메모리 핏, 트러블슈팅): [`STT_OPS_GUIDE.md`](STT_OPS_GUIDE.md)
- STT 모델 비교 / PoC: [`stt/README.md`](stt/README.md), [`stt/MODEL_STUDY.md`](stt/MODEL_STUDY.md)
