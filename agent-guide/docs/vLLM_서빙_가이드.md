# vLLM으로 LLM 서빙하기

## 📑 목차

1. [한눈에 보기](#1-한눈에-보기)
2. [권장 구성](#2-권장-구성)
3. [준비와 설치](#3-준비와-설치)
4. [모델 준비](#4-모델-준비)
5. [서버 띄우기](#5-서버-띄우기)
6. [API 호출](#6-api-호출)
7. [핵심 옵션](#7-핵심-옵션)
8. [운영](#8-운영)
9. [트러블슈팅](#9-트러블슈팅)
10. [체크리스트](#10-체크리스트)

---

## 1. 한눈에 보기

### vLLM이 하는 일

- 오픈 모델(Hugging Face 가중치)을 GPU에 올려 **OpenAI 호환 HTTP API**로 제공하는 추론 서버.
- 클라이언트는 OpenAI SDK에서 `base_url`만 바꿔 그대로 사용.
- 강점은 GPU 하나로 많은 동시 요청을 처리한다는 점. 아래 두 기술이 핵심.
  - **연속 배칭**: 요청이 끝나는 대로 빈자리에 다음 요청을 끼워 넣어 GPU를 쉬지 않게 함.
  - **KV 캐시 관리**: 대화 맥락(KV 캐시)을 작은 블록 단위로 관리해 메모리 낭비를 줄임.

### 진행 순서

| 단계 | 할 일 | 절 |
|------|-------|----|
| ① 준비 | GPU 드라이버 확인, vLLM 설치 (가상환경 또는 Docker) | §3 |
| ② 모델 받기 | Hugging Face에서 가중치를 로컬 디렉토리로 내려받기 | §4 |
| ③ 띄우기 | 설정 파일(YAML)로 `vllm serve` 실행 | §5 |
| ④ 확인·호출 | `/health` 200 확인 → `/v1/chat/completions` 호출 | §5.4, §6 |
| ⑤ 운영 | 앞단 게이트웨이, 감시, 튜닝, 장애 대응 | §8 |

### 꼭 알아야 할 용어

| 용어 | 뜻 |
|------|----|
| 가중치 | 모델 파일 자체. GPU 메모리를 고정으로 차지 |
| KV 캐시 | 요청별 대화 맥락을 담는 GPU 메모리. 많을수록 긴 대화·많은 동시 요청 가능 |
| 컨텍스트 길이 | 한 요청의 입력 + 출력 토큰 합의 상한 (`max-model-len`) |
| TP (텐서 병렬) | 모델 하나를 여러 GPU에 쪼개 올리기 |
| DP (데이터 병렬) | 같은 모델을 GPU마다 한 벌씩 올려 처리량 늘리기 |
| 양자화 | 가중치를 낮은 정밀도(FP8, 4bit)로 줄여 메모리 절약 |
| TTFT / TPS | 첫 토큰까지 걸린 시간 / 초당 생성 토큰 수 |

---

## 2. 권장 구성

처음에는 vLLM 하나만 띄워도 됨. 서비스로 열 때는 아래 구성을 권장.

```
            Client (App / OpenAI SDK)
                      │  http://<server>:<port>/v1
                      ▼
            ┌─────────────────────────┐
            │         Gateway         │   ← 외부에 여는 유일한 포트
            │  LB · health · warmup   │
            │  limit(429) · timeout   │
            └─────────────────────────┘
                 │               │        ← 여기부터 내부 전용
                 ▼               ▼
            ┌──────────┐    ┌──────────┐
            │ vLLM #1  │    │ vLLM #2  │  ← 인스턴스 1개 = 설정 파일 1개
            │ GPU 0,1  │    │ GPU 2,3  │
            │ TP=2     │    │ TP=2     │
            └──────────┘    └──────────┘
                 └─ same model ──┘           (복제해서 처리량 확장)
```

**구성 원칙**

- 🔑 **인스턴스 1개 = 설정 파일 1개**: 모델·GPU·포트·튜닝값을 YAML로 관리. 변경 이력이 남고, 복제할 때는 파일만 복사하면 됨.
- 🔑 **외부에는 게이트웨이 포트 하나만**: vLLM 포트는 내부 전용. vLLM에는 기본 인증이 없음.
- 🔑 **API 모델명 고정**: `served-model-name`을 서비스용 이름(예: `my-llm`)으로 고정하면, 백엔드 모델을 바꿔도 클라이언트 설정은 그대로.
- 🔑 **오프라인 기동**: 모델은 미리 받아 두고, 서빙할 때는 네트워크에 접속하지 않게 함. 폐쇄망에서도 똑같이 뜸.

**게이트웨이가 맡는 일** (상세는 §8.1)

- 여러 인스턴스로 요청 분산, 죽은 인스턴스 자동 제외
- 기동 직후 예열(웜업)로 첫 요청 지연 제거
- 동시 요청 상한 초과 시 대기열, 대기열도 차면 429로 거절
- 구현은 nginx 같은 리버스 프록시로 시작. 헬스체크·웜업까지 필요하면 경량 프록시를 직접 작성.

---

## 3. 준비와 설치

### 3.1 서버 체크리스트

| 항목 | 확인 방법 | 비고 |
|------|----------|------|
| NVIDIA 드라이버 | `nvidia-smi` | vLLM 0.31.0은 CUDA 13.0 기반이라 드라이버 580 이상 필요 |
| Python 3.10~3.14 | `python3 --version` | 3.12 권장 |
| Docker + NVIDIA Container Toolkit | `docker run --rm --gpus all ubuntu nvidia-smi` | Docker로 띄울 때만 |
| Fabric Manager | `systemctl status nvidia-fabricmanager` | NVSwitch로 묶인 8-GPU 서버(HGX)만. 없으면 CUDA가 초기화되지 않아 GPU를 못 씀 |
| 디스크 | `df -h` | 모델 크기의 2배 이상 여유 (교체 시 신·구 모델 공존) |

- 호스트에 CUDA 툴킷은 따로 설치할 필요 없음. vLLM 패키지와 Docker 이미지에 CUDA 런타임이 들어 있어, 호스트에는 그 CUDA 버전을 지원하는 드라이버만 있으면 됨.

### 3.2 설치 — 둘 중 하나

**A. 가상환경 (실험·개발용)**

```bash
# uv가 없으면: curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.12 ~/venvs/vllm
source ~/venvs/vllm/bin/activate
uv pip install vllm==0.31.0        # 버전은 항상 고정
vllm --version
```

**B. Docker (운영 권장)**

```bash
docker pull vllm/vllm-openai:v0.31.0   # 태그로 버전 고정
```

| | 가상환경 | Docker |
|---|---|---|
| 장점 | 설치 빠름, 코드 수정·디버깅 쉬움 | 환경 고정, 재현성, 재시작 정책 |
| 단점 | 다른 패키지와 충돌 가능 | 이미지 크기, 마운트 설정 필요 |
| 추천 | 처음 익힐 때, 실험 | 서비스 운영 |

---

## 4. 모델 준비

### 4.1 모델 크기 고르기

GPU 메모리에 **가중치 + KV 캐시**가 함께 들어가야 함.

**가중치 크기 ≈ 파라미터 수 × 정밀도별 바이트**

| 파라미터 수 | BF16 (2바이트) | FP8 (1바이트) | 4bit (0.5바이트) |
|-------------|----------------|---------------|------------------|
| 8B | 약 16 GB | 약 8 GB | 약 4 GB |
| 27~32B | 54~64 GB | 27~32 GB | 14~16 GB |
| 70B | 약 140 GB | 약 70 GB | 약 35 GB |

**GPU 메모리 참고**: L40S 48 GB · H100 80 GB · H200 141 GB

- 💡 **경험칙**: 가중치가 (GPU 메모리 합 × 0.9)의 **절반 이하**면 KV 캐시가 넉넉해 동시 요청과 긴 컨텍스트를 감당함. 넘으면 TP로 GPU를 늘리거나 양자화 모델 사용.
- 💡 **MoE 모델**(예: `26B-A4B`): 메모리는 전체 파라미터(26B)만큼 필요하고, 생성 속도는 활성 파라미터(4B) 모델에 가까움.
- 💡 **양자화 모델**: 이름에 `-FP8`, `-AWQ`, `-GPTQ`가 붙은 체크포인트는 vLLM이 자동 인식. FP8은 L40S·H100·H200 같은 Ada·Hopper 세대 이상에서 제 속도가 나옴.

### 4.2 내려받기

```bash
export MODEL_ROOT=/data/models

hf download Qwen/Qwen3-8B --local-dir $MODEL_ROOT/Qwen/Qwen3-8B

# 접근 승인이 필요한 모델(Llama 등)
HF_TOKEN=hf_xxx hf download <repo_id> --local-dir $MODEL_ROOT/<repo_id>
```

- 📁 디렉토리는 **`$MODEL_ROOT/<조직>/<모델명>`**, 즉 Hugging Face repo ID 그대로. 어떤 모델이 어디 있는지 바로 보임.
- ✅ 받은 뒤 확인: `config.json`, `tokenizer*.json`, `*.safetensors`가 모두 있어야 함.
- 🔒 **폐쇄망**: 인터넷이 되는 곳에서 받은 뒤 디렉토리째 옮김.

### 4.3 오프라인 서빙

```bash
export HF_HUB_OFFLINE=1
```

- 이 변수를 켜고 **로컬 경로**로 띄우면 vLLM이 기동 중에 Hugging Face에 접속하지 않음.
- 네트워크 상태와 무관하게 늘 같은 파일로 뜸. 모델 갱신은 내려받기 단계에서만.

---

## 5. 서버 띄우기

### 5.1 가장 단순한 실행 (동작 확인용)

```bash
CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1 \
vllm serve $MODEL_ROOT/Qwen/Qwen3-8B \
  --served-model-name my-llm \
  --port 8000
```

### 5.2 설정 파일로 실행 (권장)

```yaml
# configs/main.yaml — vLLM 인스턴스 1개 = 파일 1개
# 키 이름은 CLI 옵션과 똑같이 하이픈(-)으로

model: /data/models/Qwen/Qwen3-8B     # 로컬 경로 (YAML은 환경변수를 못 쓰므로 실제 경로로)
served-model-name: my-llm             # API 모델명 (백엔드를 바꿔도 고정)
host: 127.0.0.1                       # 게이트웨이 뒤면 내부 바인딩, 단독 공개면 0.0.0.0
port: 8000

# GPU / 메모리
tensor-parallel-size: 1               # 사용할 GPU 수
gpu-memory-utilization: 0.90          # §7.1

# 처리량 / 길이
max-model-len: 32768                  # 입력+출력 상한. 서비스에 필요한 만큼만
max-num-seqs: 32                      # 동시 처리 요청 수
max-num-batched-tokens: 8192          # 한 스텝에 처리할 토큰 수

# 캐시
enable-prefix-caching: true           # 공통 시스템 프롬프트 재사용 → 첫 토큰이 빨라짐
# kv-cache-dtype: fp8                 # KV 용량 2배. 품질 확인 후 사용

# 모델별 기능 (모델 카드에서 파서 이름 확인)
# reasoning-parser: qwen3             # 사고 과정을 본문과 분리
# enable-auto-tool-choice: true       # 도구 호출(function calling)
# tool-call-parser: hermes
# default-chat-template-kwargs: {enable_thinking: false}   # 사고 모드 기본값
```

```bash
CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
vllm serve --config configs/main.yaml
```

- 우선순위는 **CLI 인자 > 설정 파일 > 기본값**. 잠깐 바꿔 볼 값은 CLI로 덧붙이면 됨.
- ⚠️ **키는 하이픈으로.** 밑줄(`enable_prefix_caching: false`)로 쓰면 `false` 값이 오류 없이 무시됨.
- 옵션 설명은 `vllm serve --help=<옵션명>`(예: `--help=max-model-len`)으로 확인. 옵션 이름과 기본값은 버전마다 바뀜.
- 💡 `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`는 GPU 메모리 단편화로 생기는 OOM을 막음. 속도 영향이 없어 항상 켜 둠.

**Docker로 같은 설정 실행**

```bash
docker run -d --name vllm-main \
  --gpus '"device=0"' --ipc=host \
  --restart unless-stopped \
  -p 127.0.0.1:8000:8000 \
  -v $MODEL_ROOT:/data/models:ro \
  -v $PWD/configs:/configs:ro \
  -e HF_HUB_OFFLINE=1 \
  -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  vllm/vllm-openai:v0.31.0 \
  --config /configs/main.yaml --host 0.0.0.0
```

- `--ipc=host`: 여러 GPU 프로세스가 공유 메모리로 통신. 빠지면 TP에서 멈추거나 죽음.
- `--host 0.0.0.0`: 컨테이너 안에서는 전체 바인딩이 필요. 외부 노출은 `-p 127.0.0.1:...`로 막음.

### 5.3 GPU 배치 — TP와 DP

```
   TP=2 (split one model)          DP=2 (one copy per GPU)
   ┌─────────┬─────────┐           ┌─────────┐  ┌─────────┐
   │  GPU 0  │  GPU 1  │           │  GPU 0  │  │  GPU 1  │
   │ model ½ │ model ½ │           │  model  │  │  model  │
   └─────────┴─────────┘           └─────────┘  └─────────┘
      = 1 instance                  = 2 instances (+ gateway)
```

| | TP (텐서 병렬) | DP (데이터 병렬) |
|---|---|---|
| 언제 | 모델이 GPU 1장에 안 들어감, 긴 컨텍스트 필요 | 모델이 1장에 들어가고 동시 사용자가 많음 |
| 효과 | 큰 모델 실행, KV 캐시 증가 | 처리량이 인스턴스 수에 비례해 증가 |
| 설정 | `tensor-parallel-size: N` + `CUDA_VISIBLE_DEVICES`에 N장 | 설정 파일 복제 → GPU·포트만 바꿔 인스턴스 추가 → 게이트웨이로 분산 |
| 주의 | N은 보통 1·2·4·8 (모델의 어텐션 헤드 수로 나눠떨어져야 함). NVLink로 연결된 GPU끼리 묶어야 빠름 | 인스턴스마다 가중치를 따로 올림 |

- vLLM 자체 DP 옵션(`--data-parallel-size`)도 있지만, 인스턴스를 나눠 두면 하나가 죽어도 나머지가 서비스를 이어 감.

### 5.4 기동 과정과 확인

```
 start ─▶ load weights ─▶ profile memory ─▶ allocate KV cache ─▶ capture CUDA graphs ─▶ ready
           (1~10 min, depends on model size)        │
                                                    └─ log: "GPU KV cache size: N tokens"
```

- ⏳ 기동에 수 분 걸림. 준비 완료는 로그 문구가 아니라 **`/health`가 200을 주는지**로 판단.

```bash
until curl -sf http://localhost:8000/health >/dev/null; do sleep 5; done; echo READY
curl -s http://localhost:8000/v1/models        # served-model-name이 보이면 정상
```

**기동 로그에서 꼭 볼 두 줄**

| 로그 | 의미 |
|------|------|
| `GPU KV cache size: N tokens` | KV 캐시에 담을 수 있는 총 토큰 수 |
| `Maximum concurrency for L tokens per request: X.XXx` | 최대 길이(L) 요청을 동시에 X건 처리 가능 |

- 운영 중에는 주기적으로 `Running: N reqs, Waiting: M reqs` 줄이 찍힘. `Waiting`이 계속 쌓이면 용량 부족 (§8.3).

---

## 6. API 호출

### 6.1 주요 엔드포인트

| 경로 | 용도 |
|------|------|
| `POST /v1/chat/completions` | 대화형 생성 (가장 많이 씀) |
| `POST /v1/completions` | 프롬프트 이어 쓰기 |
| `POST /v1/responses` | OpenAI Responses API 호환 |
| `POST /v1/embeddings` | 임베딩 모델을 띄웠을 때 |
| `GET /v1/models` | 서빙 중인 모델명 확인 |
| `GET /health` | 준비 여부 (200 = 정상) |
| `GET /metrics` | Prometheus 지표 |

### 6.2 curl

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "my-llm",
    "messages": [{"role": "user", "content": "안녕하세요"}],
    "max_tokens": 256
  }'
```

### 6.3 Python (OpenAI SDK)

```python
# pip install openai
from openai import OpenAI

# --api-key를 안 썼으면 api_key는 아무 문자열이나
client = OpenAI(base_url="http://<server>:8000/v1", api_key="EMPTY")
messages = [{"role": "user", "content": "vLLM이 뭔지 한 문단으로 설명해 주세요"}]

# 일반 호출
resp = client.chat.completions.create(
    model="my-llm",                     # served-model-name과 같아야 함
    messages=messages,
    max_tokens=512,
)
print(resp.choices[0].message.content)

# 스트리밍
stream = client.chat.completions.create(model="my-llm", messages=messages, stream=True)
for chunk in stream:
    if chunk.choices:
        print(chunk.choices[0].delta.content or "", end="", flush=True)
```

### 6.4 사고(thinking) 모델

- `reasoning-parser`를 켜면 사고 과정은 `message.reasoning`, 최종 답은 `message.content`로 나뉘어 옴.
- 사고 모드는 요청마다 켜고 끌 수 있음 (지원 모델만, 키 이름은 모델 카드 확인).

```python
resp = client.chat.completions.create(
    model="my-llm",
    messages=messages,
    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
)
```

---

## 7. 핵심 옵션

### 7.1 GPU 메모리 구조 — `gpu-memory-utilization`

```
 GPU memory 100%
 ├───────────── gpu-memory-utilization (e.g. 0.90) ─────────────┤─ rest ─┤
 ┌─────────┬────────────┬────────────┬──────────────────────────┬────────┐
 │ weights │ activation │ CUDA graph │ KV cache (all the rest)  │ buffer │
 └─────────┴────────────┴────────────┴──────────────────────────┴────────┘
   fixed     per-batch     fixed        grows with util            CUDA ctx
```

- vLLM은 이 비율 **안에** 가중치·활성화·KV를 모두 넣고, 남는 자리는 전부 KV 캐시로 사용.
- ⚠️ 값을 올리면 **KV만 늘고 활성화 여유는 줄어듦.** 큰 배치나 이미지 입력이 몰릴 때 OOM으로 죽음.
- 기본값은 0.92. **0.90에서 시작**하고, OOM이 나면 낮춤. 같은 GPU에 다른 프로세스가 있으면 그만큼 뺌.

### 7.2 요청 처리 흐름 — `max-num-seqs`

```
 requests ─▶ [ Waiting queue (FCFS) ] ─▶ [ Running ≤ max-num-seqs ] ─▶ response
                almost no GPU memory          uses KV cache
```

- 상한을 넘는 요청은 거절되지 않고 대기열에서 순서를 기다림.
- KV 캐시가 모자라도 vLLM은 죽지 않고 일부 요청을 잠시 미룸. 대신 응답이 느려짐.

### 7.3 옵션 표

| 옵션 | 뜻 | 정하는 기준 |
|------|----|------------|
| `tensor-parallel-size` | 모델을 나눠 올릴 GPU 수 | §4.1 경험칙으로 결정 |
| `gpu-memory-utilization` | vLLM이 쓸 GPU 메모리 비율 | 0.90 시작, OOM이면 낮춤 |
| `max-model-len` | 요청당 입력+출력 토큰 상한 | 서비스에 필요한 만큼. 크게 잡으면 동시성이 줄어듦 |
| `max-num-seqs` | 동시 처리 요청 수 | 기동 로그의 최대 동시성과 실제 부하를 보고 조정 |
| `max-num-batched-tokens` | 한 스텝 처리 토큰 수 | 크면 긴 입력 처리가 빠르지만 활성화 메모리 증가 |
| `served-model-name` | API에서 쓰는 모델명 | 서비스용 이름으로 고정 |
| `enable-prefix-caching` | 같은 앞부분(시스템 프롬프트) KV 재사용 | 켬 (생성 모델 기본값) |
| `kv-cache-dtype` | KV 캐시 정밀도 | `auto`. 용량이 모자라면 `fp8` (품질 확인 후) |
| `quantization` | 즉석 양자화 | 양자화 체크포인트면 생략(자동). BF16 모델을 줄일 때 `fp8` |
| `reasoning-parser` | 사고 과정 분리 | 사고 모델이면 모델 카드의 이름으로 |
| `enable-auto-tool-choice` + `tool-call-parser` | 도구 호출 파싱 | 도구 호출을 쓰면 모델 카드의 이름으로 |
| `default-chat-template-kwargs` | 채팅 템플릿 기본 인자 | 사고 모드 기본 끔 등 |
| `api-key` | API 키 인증 | 게이트웨이 없이 노출할 때 |
| `host` / `port` | 바인딩 주소 / 포트 | 게이트웨이 뒤면 `127.0.0.1` |

### 7.4 처음 값 정하는 순서

```
 model size ─▶ choose TP ─▶ util 0.90 ─▶ set max-model-len ─▶ start
                                                               │
 load test ◀── adjust max-num-seqs ◀── read "KV cache size" log ┘
```

1. 모델 크기로 GPU 수(TP) 결정
2. `gpu-memory-utilization: 0.90`, `max-model-len`은 서비스 필요량으로 잡고 기동
3. 기동 로그에서 KV 토큰 수와 최대 동시성 확인
4. 그 범위 안에서 `max-num-seqs`를 정하고 실제 부하로 시험 (§8.4)

---

## 8. 운영

### 8.1 게이트웨이 (앞단 프록시)

| 기능 | 동작 | 시작값 예시 |
|------|------|------------|
| 부하 분산 | 정상 인스턴스에 요청을 나눔 | 라운드로빈 |
| 헬스체크 | 각 vLLM의 `/health`를 주기적으로 확인, 연속 실패 시 제외, 회복 시 복귀 | 10초 간격, 3회 연속 실패 시 제외 |
| 기동 대기 | 모델 로딩이 끝날 때까지 기다린 뒤 투입 | 최대 15분 |
| 웜업 | 투입 전 더미 요청으로 예열. 공통 시스템 프롬프트를 한 번 보내 프리픽스 캐시를 채움 | 기동·회복 때마다 |
| 과부하 차단 | 처리 중 요청이 상한을 넘으면 대기열, 대기열도 차면 429 + `Retry-After` | 처리 중 ≤ `max-num-seqs`, 대기열 = 그 2배 |
| 타임아웃 | 긴 응답을 감안해 넉넉하게 | 300초 |

- 클라이언트 타임아웃은 게이트웨이 대기 시간보다 길게 설정. 짧으면 대기 중인 요청이 클라이언트에서 먼저 끊김.

### 8.2 보안

- 🔒 vLLM에는 기본 인증이 없음. vLLM 포트는 `127.0.0.1` 바인딩이나 방화벽으로 **내부 전용**으로 둠.
- 🔒 외부에는 게이트웨이 포트 하나만 공개. 인증이 필요하면 게이트웨이에 걸거나 vLLM `--api-key` 사용.

### 8.3 모니터링

| 무엇을 | 어디서 | 이상 신호 |
|--------|--------|----------|
| 실행·대기 요청 수 | 로그 `Running` / `Waiting`, `/metrics` | `Waiting`이 계속 쌓임 → 인스턴스 추가 또는 `max-num-seqs` 조정 |
| KV 캐시 사용률 | 로그, `/metrics` | 늘 100% 근처 → 컨텍스트·동시성 재조정 |
| 첫 토큰 시간·생성 속도 | `/metrics` | 평소보다 급증 → 부하 또는 긴 입력 몰림 |
| GPU 메모리·사용률 | `nvidia-smi` | 서버를 내렸는데 메모리가 안 빔 → §9 잔여 프로세스 |

- `/metrics`는 Prometheus 형식이라 Prometheus로 수집해 Grafana로 보면 됨.

### 8.4 배포 전 시험

새 모델이나 새 버전은 아래 네 관문을 통과한 뒤 교체. 속도는 참고 지표.

| 관문 | 확인 내용 |
|------|----------|
| 기동 | 오프라인으로 뜨는가, 기동 시간 |
| 기능 | 일반 응답, 스트리밍, 도구 호출, 사고 분리, (해당 시) 이미지 입력 |
| 품질 | 실제 서비스 질문 셋으로 답변 비교 |
| 안정성 | 목표 동시성으로 1~2시간 부하, 오류·크래시 0건 |

### 8.5 프로세스 관리

- ♻️ systemd 또는 Docker `--restart unless-stopped`로 죽으면 다시 뜨게 함.
- ♻️ **`/health` 기반 감시**도 둠. 엔진이 죽어도 API 프로세스가 한동안 살아 있어, 프로세스 생존 감시만으로는 못 잡는 경우가 있음. 예: `/health`가 90초 이상 실패하면 재시작.
- 📝 로그는 재시작 때 덮어쓰지 말고 보존. 첫 크래시 원인이 로그에만 남음.
- 🛑 정지는 `Ctrl+C` 또는 `SIGTERM`으로. 정지 뒤 `nvidia-smi`로 GPU 메모리가 비었는지 확인.

### 8.6 모델 교체와 업그레이드

- `served-model-name`을 고정해 두면 설정 파일의 `model`만 바꾸고 재시작하면 됨. 클라이언트는 손댈 필요 없음.
- vLLM·모델 버전은 **고정**. 올릴 때는 별도 인스턴스에서 §8.4 시험을 거친 뒤 교체.
- ⚠️ 추측 디코딩(speculative decoding, MTP 등) 같은 속도 기능은 모델·버전 조합에 따라 답이 섞이거나 틀리는 버그가 보고된 사례가 있음. **검증된 뒤에만** 사용.

---

## 9. 트러블슈팅

| 증상 | 원인 | 조치 |
|------|------|------|
| 기동 중 `No available memory for the cache blocks` | 가중치만으로 메모리가 꽉 참 | TP로 GPU 늘리기, 양자화 모델 사용, 같은 GPU의 다른 프로세스 확인 |
| 기동 중 `... KV cache is needed, which is larger than the available KV cache memory` | `max-model-len` 한 건을 담을 KV 공간도 없음 | 오류 문구의 `estimated maximum model length` 이하로 `max-model-len` 줄이기, 또는 `kv-cache-dtype: fp8`, TP 증가 |
| 운영 중 `CUDA out of memory`로 크래시 | 큰 배치·이미지 입력의 활성화 메모리 부족, 메모리 단편화 | `gpu-memory-utilization` 낮추기(예: 0.90→0.85), `max-num-batched-tokens` 줄이기, `expandable_segments:True` 확인 |
| 재시작하자마자 OOM | 이전 프로세스가 GPU를 쥐고 남아 있음 | `nvidia-smi`로 PID 확인 → `kill` → 안 죽으면 `kill -9` |
| 404 `model ... does not exist` | 요청의 `model` ≠ `served-model-name` | `/v1/models`로 이름 확인 |
| 응답에 사고 과정이 섞여 나옴 | `reasoning-parser` 미설정 | 모델 카드의 파서 이름으로 설정 |
| 도구 호출이 일반 텍스트로 옴 | 도구 호출 옵션 미설정 | `enable-auto-tool-choice` + `tool-call-parser` 설정 |
| 기동이 네트워크에서 멈춤 | Hugging Face 접속 시도 (폐쇄망) | `HF_HUB_OFFLINE=1` + 로컬 경로로 실행 |
| 첫 요청만 유독 느림 | 예열 전 | 게이트웨이 웜업 또는 기동 후 더미 요청 1회 |
| 점점 느려지고 대기가 쌓임 | 용량 부족 | `Waiting` 확인 → 인스턴스 추가(DP) 또는 `max-model-len`·`max-num-seqs` 재조정 |
| 이미지 요청이 몰릴 때 크래시 | 멀티모달 처리 경합 | 동시 이미지 수에 맞춰 `max-num-seqs` 제한, 재현되면 `--no-async-scheduling` |
| Docker에서 TP 시작 시 멈춤·크래시 | 공유 메모리 부족 | `--ipc=host` 추가 |
| 8-GPU 서버(HGX)에서 CUDA 초기화 실패 | Fabric Manager 미기동 | `nvidia-fabricmanager` 설치·기동 (드라이버와 같은 버전) |

---

## 10. 체크리스트

**띄우기 전**

- [ ] `nvidia-smi`에 GPU가 모두 보임
- [ ] vLLM 버전 고정 (`vllm==X.Y.Z` 또는 이미지 태그)
- [ ] 모델을 `$MODEL_ROOT/<조직>/<모델명>`에 받았고 파일이 다 있음
- [ ] 가중치 크기와 GPU 메모리로 TP 결정
- [ ] 설정 파일 1개 = 인스턴스 1개, 키는 하이픈

**띄운 뒤**

- [ ] `/health` 200, `/v1/models`에 서비스용 이름이 보임
- [ ] 기동 로그의 KV 토큰 수·최대 동시성 확인
- [ ] 일반·스트리밍 호출 정상 (쓰는 경우 도구 호출·사고 분리도)

**서비스 전**

- [ ] vLLM 포트는 내부 전용, 외부는 게이트웨이 하나
- [ ] 헬스체크·웜업·과부하 차단·타임아웃 설정
- [ ] 목표 동시성으로 부하 시험 통과
- [ ] 자동 재시작, `/health` 감시, 로그 보존 설정

---

## 참고

- 공식 문서: https://docs.vllm.ai
- 서버 옵션 전체: https://docs.vllm.ai/en/latest/configuration/serve_args.html
- 메모리 절약 방법: https://docs.vllm.ai/en/latest/configuration/conserving_memory/
- 지원 모델 목록: https://docs.vllm.ai/en/latest/models/supported_models.html
- 옵션 확인: `vllm serve --help=max-model-len` (옵션 하나), `vllm serve --help=CacheConfig` (분류별)
