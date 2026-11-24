# 🎙️ STT 서빙 (vLLM 기반, 페어 구조)

`llm-serving/vllm/` 의 `instances/` + `gateways/` 패턴을 STT에 그대로 적용.
**Voxtral-Mini-4B-Realtime-2602** 를 게이트웨이 `:5018` 로 외부 노출하고(비교 PoC 2종은 `:5017`),
`vllm_gateway.py` 본체가 `/v1/audio/transcriptions` (HTTP) + `/v1/realtime` (WebSocket) 라우트를 제공한다.

> 사용자(API 호출)용: [`../STT_API_GUIDE.md`](../STT_API_GUIDE.md)
> 운영자(서버 기동·튜닝)용: [`../STT_OPS_GUIDE.md`](../STT_OPS_GUIDE.md)
> 후보 모델 비교 / 시나리오: [`MODEL_STUDY.md`](MODEL_STUDY.md)

---

## 📦 구성

| 인스턴스 | 모델 | GPU | 내부 포트 | 외부 게이트웨이 | 상태 |
|---------|------|:---:|:----:|:----:|:----:|
| `voxtral` | `mistralai/Voxtral-Mini-4B-Realtime-2602` | 2 | 7172 | **5018** | ✅ 운영 |
| `qwen3_asr` | `Qwen/Qwen3-ASR-1.7B` | 0 | 7170 | 5017 | 🧪 비교 PoC |
| `whisper_v3` | `openai/whisper-large-v3` | 2 | 7171 | 5017 | 🧪 비교 PoC |

`qwen3_asr` / `whisper_v3` 는 비교 PoC 게이트웨이 `:5017` 소속(`model` 필드로 백엔드 라우팅)이고, 내부 포트(7170/7171) 직접 호출은 디버그용입니다. voxtral은 실시간(realtime) 트래픽 분리를 위해 전용 게이트웨이 `:5018`을 씁니다.

```
llm-serving/stt/
├── README.md                # 본 문서
├── MODEL_STUDY.md           # 후보 모델 비교 / 시나리오
├── start.sh                 # vllm/start.sh 패턴 풀 도입 (instances/+gateways/ 페어 자동 순회)
├── instances/
│   ├── voxtral.yaml         # gateway_port: 5018 → :5018 페어, 내부 :7172
│   ├── qwen3_asr.yaml       # 비교용 (gateway_port: 5017, 내부 :7170)
│   └── whisper_v3.yaml      # 비교용 (gateway_port: 5017, 내부 :7171)
├── gateways/
│   ├── 5017.yaml            # 비교 PoC 게이트웨이 (discover_from: ../instances)
│   └── 5018.yaml            # 메인 게이트웨이 (voxtral 전용, warmup 비활성화, timeout 600s)
└── logs/                    # 인스턴스/게이트웨이 stdout/stderr (자동 생성)
```

> `start.sh` / `logging.sh` / `vllm_server_launcher.py` / `vllm_gateway.py` 는 모두 `../vllm/` 의 본체를 재사용한다 (코드 단일 출처). `stt/start.sh` 와 `stt/logging.sh` 는 STT 디렉토리·라벨만 env로 export한 뒤 본체를 `exec` 호출하는 thin wrapper다.

---

## 🚀 사용법

```bash
cd llm-serving/stt

./start.sh up                       # 인자 없음 → 전체 적용 confirm 프롬프트 [y/N]
./start.sh up all                   # 전체 인스턴스 + 게이트웨이 기동 (확인 없이)
./start.sh up voxtral               # voxtral 단독 (게이트웨이 미터치)
./start.sh up 5018                  # 5018 게이트웨이 단독 (인스턴스 미터치)
./start.sh status                   # UP/DOWN/STARTING/STALE 표시
./start.sh down                     # 인자 없음 → 전체 중지 confirm 프롬프트 [y/N]
./start.sh down all                 # 모든 인스턴스 + 게이트웨이 중지 (확인 없이)
./start.sh down voxtral             # voxtral 단독 중지
./start.sh down 5018                # 5018 게이트웨이 단독 중지
./start.sh restart                  # 인자 없음 → 전체 재시작 confirm 프롬프트 [y/N]
./start.sh restart <name>           # 단일 대상 재시작
```

> ⚠️ 무인자 호출은 [y/N] 기본 No로 묻는다 (다른 모델/게이트웨이를 실수로 stop시키는 사고 방지). 비대화 환경(파이프/cron)에서는 `'all'` 또는 이름 명시 필수.

상태 확인:

```bash
curl http://localhost:5018/health             # 메인 게이트웨이 health (비교 PoC는 :5017)
curl http://localhost:5018/v1/models          # 모델 목록
curl http://localhost:7172/health             # 내부 인스턴스 직접 (디버그용)
```

---

## 🔬 첫 호출 (smoke test)

```bash
# 1초 사인파 생성
python3 -c "
import numpy as np, soundfile as sf
sr=16000; t=np.linspace(0,1,sr,endpoint=False)
sf.write('/tmp/sine_1s.wav', (0.1*np.sin(2*np.pi*440*t)).astype('float32'), sr)
"

# Transcription HTTP
curl http://localhost:5018/v1/audio/transcriptions \
  -F "file=@/tmp/sine_1s.wav" \
  -F "model=Voxtral-Mini-4B-Realtime-2602" \
  -F "language=ko" \
  -F "temperature=0"
# {"text":"","usage":{"type":"duration","seconds":1}}

# Realtime WebSocket — session.created 수신 확인
python3 - <<'PY'
import asyncio, json, websockets
async def main():
    async with websockets.connect("ws://localhost:5018/v1/realtime?model=Voxtral-Mini-4B-Realtime-2602") as ws:
        print(json.loads(await ws.recv())["type"])
asyncio.run(main())
PY
# session.created
```

호출 예제·SDK 통합·파라미터 표는 [`../STT_API_GUIDE.md`](../STT_API_GUIDE.md) 참조.

---

## ⚠️ 운영 주의

### 의존성 (Voxtral 필수)

```bash
pip install --user soundfile soxr librosa
```

미설치 시 vLLM 기동 직후 `EngineCore failed to start` + `ImportError: soundfile` 로 fail. 운영계 컨테이너 재배포 시 동일 실패 방지를 위해 `server-setup/requirements.txt` 추가 권장.

### GPU 점유 충돌 (LLM 인스턴스와 동시 운영)

- **voxtral** 은 GPU 2 단독 → LLM 인스턴스(GPU 0·1)와 충돌 없음.
- **qwen3_asr**(GPU 0)는 LLM과, **whisper_v3**(GPU 2)는 voxtral과 GPU가 겹침 → 비교 PoC 시 충돌 대상 먼저 stop:

```bash
cd ../vllm && ./start.sh down <인스턴스명>   # qwen3_asr 띄울 때: 운영 중 LLM (예: gemma-26b)
cd ../stt  && ./start.sh down voxtral        # whisper_v3 띄울 때: voxtral
cd ../stt  && ./start.sh up qwen3_asr        # 또는 whisper_v3
```

### 모델 다운로드

- 첫 실행 시 launcher가 `/models/STT/<HF_ID>/` 로 자동 다운로드.
- Voxtral / Qwen3-ASR / Whisper-large-v3 모두 Apache 2.0 또는 MIT 라이선스 → HF_TOKEN 불필요.
- Voxtral 합계 ~17GB (consolidated.safetensors 8.5GB + model.safetensors 8.5GB).
- 폐쇄망에선 외부망 PC → S3 → `/models/STT/` 사전 동기화. 절차는 [`../STT_OPS_GUIDE.md`](../STT_OPS_GUIDE.md) §8.2.

### 첫 기동 시간 (재기동, 다운로드 제외)

- weight 로딩 ~3초, KV 프로파일링 ~15초, CUDA graph capture ~1초, 게이트웨이 health probe ~10초.
- `./start.sh status`에서 `[UP]`이면 추론 가능.

---

## 🔍 트러블슈팅

상세 표는 [`../STT_OPS_GUIDE.md`](../STT_OPS_GUIDE.md) §10. 자주 보는 항목:

| 증상 | 1차 조치 |
|------|----------|
| `ImportError: soundfile` 로 EngineCore 실패 | `pip install --user soundfile soxr librosa` |
| `[STARTING]` 만 1분 이상 지속 | `tail -f logs/vllm_voxtral.log` 로 cudagraph capture 단계 확인 |
| 게이트웨이 ready 0/1 | 백엔드 voxtral 의 `/health` 가 200인지 확인. 미응답이면 `[STALE]` 정리 후 재기동 |
| GPU OOM | `instances/voxtral.yaml` 의 `gpu_memory_utilization` 하향 (0.30~0.40) |
| 게이트웨이 → 백엔드 라우팅 안 됨 | 게이트웨이 포트와 인스턴스의 `gateway_port` 일치 확인 (voxtral=5018, PoC 2종=5017) |

---

## 📋 다음 단계 (PoC)

- [ ] **한국어 테스트 셋 준비** (Zeroth-Korean / FLEURS Korean / KsponSpeech 일부)
- [ ] **`test_stt.py` 작성** — WER / RTF / latency / 정성 평가 (고유명사·숫자·전문용어)
- [ ] **세 모델 한국어 비교 결과 정리** (`MODEL_STUDY.md` 부록)
- [ ] **동시 N 세션 운영 전환** — `gpu_memory_utilization`/`max_num_seqs`/`max_inflight_requests` 함께 상향
