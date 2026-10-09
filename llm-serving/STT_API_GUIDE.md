# STT API 가이드 (사용자용)

> **대상**: API 사용자 (음성 → 텍스트 변환을 호출할 개발자)
> **메인 모델**: `whisper-large-v3` (OpenAI Whisper, MIT 라이선스, 산업 표준 baseline)
> **API 호환**: OpenAI Audio API 100% — 기존 OpenAI SDK · LangChain · `curl` 그대로
> **인증**: 불필요 (`Authorization` 헤더 생략 가능)

자체 호스팅한 vLLM 기반 STT 서버를 **OpenAI Audio API 쓰듯** 호출하기 위한 가이드입니다.

처음 호출하는 분은 §1~§3만 보면 됩니다. 운영(서버 기동·튜닝·트러블슈팅·테스트)은 [`STT_OPS_GUIDE.md`](STT_OPS_GUIDE.md) 참고.

---

## 📑 목차

1. [한눈에 보기](#1-한눈에-보기)
2. [첫 호출](#2-첫-호출)
3. [핵심 기능](#3-핵심-기능)
   - 3.1 Transcription (음성 → 원어 텍스트)
   - 3.2 Translation (음성 → 영어 텍스트)
   - 3.3 타임스탬프 (`verbose_json` / word·segment)
   - 3.4 Realtime 스트리밍 (Voxtral 옵션)
4. [파라미터·응답·에러 레퍼런스](#4-파라미터응답에러-레퍼런스)
5. [클라이언트 통합 (.env)](#5-클라이언트-통합-env)

---

## 1. 한눈에 보기

**Base URL**: `http://43.203.142.247:5017/v1` — whisper·Qwen3-ASR용 게이트웨이 (`model` 필드로 라우팅). **Voxtral(Realtime 포함)은 전용 게이트웨이 `:5018`** 로 호출합니다.

> 현재 상시 기동은 Voxtral(`:5018`)이고, whisper·Qwen3-ASR(`:5017`)은 비교 PoC로 필요 시에만 기동됩니다. 호출 전 해당 포트의 `/health`·`/v1/models`로 가용 여부를 확인하세요.

| 항목 | **Whisper (메인)** | Voxtral (실시간 옵션) | Qwen3-ASR (옵션) |
|------|---------------------|------------------------|-------------------|
| 모델명 (`model` 필드) | **`whisper-large-v3`** | `Voxtral-Mini-4B-Realtime-2602` | `Qwen3-ASR-1.7B` |
| API 키 | 불필요 | 불필요 | 불필요 |
| Transcription (HTTP) | ✅ | ✅ | ✅ |
| Translation (HTTP, → 영어) | ✅ (모델 카드 명시) | — | — |
| Realtime (WebSocket) | ❌ | ✅ (단독 지원) | ❌ |
| `verbose_json` + 타임스탬프 | ✅ (word/segment) | ❌ (요청 시 400) | ✅* |
| 권장 입력 | wav/mp3/flac/m4a, 16kHz mono 권장 | PCM16 16kHz mono | wav/mp3/flac/m4a |
| 권장 샘플링 | `temperature=0` | `temperature=0` (모델카드 강제) | `temperature=0` |

> `*` Qwen3-ASR은 OpenAI 호환 transcription 모델로 `verbose_json` 응답 자체는 반환되나, word·segment 타임스탬프 정밀도는 Whisper와 다를 수 있음 — 정확한 타임스탬프가 필수면 `model=whisper-large-v3` 권장.

> 컨텍스트 길이·동시 세션 한도 등은 운영 튜닝값에 따라 달라집니다. 현재 값은 `GET /v1/models` 응답 또는 운영자에게 확인.

**API 호환성**: vLLM은 OpenAI Audio API와 **100% 호환**. `OpenAI` SDK · `langchain_openai` · `fetch` · `curl` 어떤 클라이언트도 `base_url`만 바꾸면 그대로 동작합니다.

**엔드포인트 요약**:

| 메서드 | 경로 | 용도 |
|--------|------|------|
| POST | `/v1/audio/transcriptions` | **음성 → 원어 텍스트** (multipart 업로드) |
| POST | `/v1/audio/translations` | 음성 → 영어 텍스트 |
| WS   | `/v1/realtime` | 실시간 스트리밍 (`model=Voxtral-Mini-4B-Realtime-2602` 한정, `:5018`) |
| GET  | `/v1/models` | 로드된 모델 목록 |
| GET  | `/health` | 서버 헬스체크 |

---

## 2. 첫 호출

> 호출 전 살아있는지 확인: `curl http://43.203.142.247:5017/health` → `200 OK`.

### 2.1 curl

```bash
curl http://43.203.142.247:5017/v1/audio/transcriptions \
  -F "file=@sample_ko.wav" \
  -F "model=whisper-large-v3" \
  -F "language=ko" \
  -F "temperature=0"
```

응답:

```json
{
  "text": "안녕하세요, 오늘 날씨가 좋네요.",
  "usage": {"type": "duration", "seconds": 4}
}
```

### 2.2 Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://43.203.142.247:5017/v1",
    api_key="not-needed",   # vLLM 기본 인증 없음. 빈 문자열은 SDK가 거부하므로 더미값.
)

with open("sample_ko.wav", "rb") as f:
    resp = client.audio.transcriptions.create(
        file=f,
        model="whisper-large-v3",
        language="ko",
        temperature=0,
    )
print(resp.text)
```

### 2.3 LangChain

```python
from langchain_core.tools import tool
from openai import OpenAI

_stt = OpenAI(base_url="http://43.203.142.247:5017/v1", api_key="not-needed")

@tool
def transcribe_audio(path: str, language: str = "ko") -> str:
    """오디오 파일 경로를 받아 텍스트로 변환."""
    with open(path, "rb") as f:
        return _stt.audio.transcriptions.create(
            file=f, model="whisper-large-v3",
            language=language, temperature=0,
        ).text
```

### 2.4 Node.js (OpenAI SDK)

```javascript
import OpenAI from "openai";
import fs from "fs";

const client = new OpenAI({
  baseURL: "http://43.203.142.247:5017/v1",
  apiKey: "not-needed",
});

const resp = await client.audio.transcriptions.create({
  file: fs.createReadStream("sample_ko.wav"),
  model: "whisper-large-v3",
  language: "ko",
  temperature: 0,
});

console.log(resp.text);
```

### 2.5 모델 목록 확인

```bash
curl http://43.203.142.247:5017/v1/models
```

응답에 `served_model_name`(예: `whisper-large-v3`)과 `max_model_len`이 들어 있어, 클라이언트에서 모델명을 자동 감지하는 데 쓸 수 있습니다.

---

## 3. 핵심 기능

### 3.1 Transcription (음성 → 원어 텍스트)

OpenAI Audio API와 동일. multipart/form-data로 audio 파일 + form 필드 업로드.

| 필드 | 필수 | 값 | 설명 |
|------|:----:|----|------|
| `file` | O | 파일 | wav / mp3 / flac / m4a / ogg 등 (vLLM 0.31은 soundfile → torchcodec → PyAV 순서로 디코드) |
| `model` | O | `whisper-large-v3` | `/v1/models`로 확인한 정확한 ID |
| `language` | 권장 | `ko` 등 ISO-639-1 | 지정 시 언어 자동감지 비용 절약 |
| `temperature` | 권장 | `0` | 숫자/고유명사 안정성 — Whisper 모델카드 권장 |
| `response_format` | 선택 | `json`(기본) / `text` / `srt` / `vtt` / `verbose_json` | §3.3 참조 |
| `timestamp_granularities[]` | 선택 | `word` / `segment` | `verbose_json` 일 때만 의미 있음 |

**Whisper의 30초 chunk 처리**: Whisper는 구조적으로 30초 단위로 처리됩니다. 30초가 넘는 입력은 vLLM이 자동으로 chunk를 잘라 순차 디코드합니다 — 클라이언트 측 분할 불필요. 다만 1시간 이상의 매우 긴 오디오는 네트워크/timeout 안정성을 위해 사전 분할을 권장.

**입력 포맷 팁**:

- 샘플레이트는 모델 expected SR(Whisper=16kHz)와 다르면 vLLM이 자동 resample. 자동 resample 경로는 PyAV(`av` 패키지) 의존성이 있으므로, 운영 환경에 PyAV가 없으면 `Invalid or unsupported audio file.` 400이 날 수 있습니다 — 안전하게 **16kHz mono로 사전 변환**해 보내는 것을 권장.
- 스테레오는 다운믹스해 mono로 보내는 편이 정확. 채널 정보가 텍스트에 기여하지 않음.

```bash
# ffmpeg로 16kHz mono 변환 예시
ffmpeg -i input.mp3 -ar 16000 -ac 1 -c:a pcm_s16le output.wav
```

### 3.2 Translation (음성 → 영어 텍스트)

`/v1/audio/translations`로 호출하면 **원어가 무엇이든 영어로 번역된 텍스트**가 반환됩니다.

```bash
curl http://43.203.142.247:5017/v1/audio/translations \
  -F "file=@sample_ko.wav" \
  -F "model=whisper-large-v3" \
  -F "temperature=0"
# {"text": "Hello, the weather is nice today."}
```

> 영어 외 다른 언어로의 번역은 미지원 (OpenAI Audio API 표준 그대로). 다른 언어로 번역이 필요하면 transcription → 별도 번역 LLM 호출.

### 3.3 타임스탬프 (`verbose_json` / word·segment)

`response_format=verbose_json` + `timestamp_granularities[]` 조합으로 segment·word 단위 타임스탬프를 받습니다. 회의록·자막 작업에 사용.

```bash
curl http://43.203.142.247:5017/v1/audio/transcriptions \
  -F "file=@meeting_ko.wav" \
  -F "model=whisper-large-v3" \
  -F "language=ko" \
  -F "response_format=verbose_json" \
  -F "timestamp_granularities[]=segment" \
  -F "timestamp_granularities[]=word" \
  -F "temperature=0"
```

응답:

```json
{
  "task": "transcribe",
  "language": "ko",
  "duration": 12.5,
  "text": "지난해 삼 월 김 전 장관의 동료인 …",
  "segments": [
    {"id": 0, "start": 0.0, "end": 4.5, "text": "지난해 삼 월 …",
     "tokens": [...], "temperature": 0.0,
     "avg_logprob": -0.18, "compression_ratio": 1.05, "no_speech_prob": 0.01}
  ],
  "words": [
    {"word": "지난해", "start": 0.10, "end": 0.62},
    {"word": "삼",     "start": 0.62, "end": 0.84}
  ]
}
```

**자막 출력**: `response_format=srt` 또는 `vtt`를 주면 바로 자막 파일 형식 문자열로 떨어집니다 — 후가공 불필요.

> Voxtral-Realtime은 `verbose_json` 미지원. 타임스탬프가 필요하면 `model=whisper-large-v3` 또는 `model=Qwen3-ASR-1.7B`로 호출.

### 3.4 Realtime 스트리밍 (Voxtral 옵션)

실시간 마이크 입력 같이 **양방향 스트리밍이 필요한 경우**만 Voxtral 모델로 WebSocket 엔드포인트(`/v1/realtime`)에 접속합니다. OpenAI Realtime API와 동일한 프로토콜.

```python
import asyncio, json, websockets

URL = "ws://43.203.142.247:5018/v1/realtime?model=Voxtral-Mini-4B-Realtime-2602"

async def main():
    async with websockets.connect(URL) as ws:
        # 1) 서버가 session.created 송신
        msg = json.loads(await ws.recv())
        print("[server]", msg["type"])

        # 2) 입력 포맷/언어 협상
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "input_audio_format": "pcm16",
                "input_audio_transcription": {"language": "ko"},
            },
        }))

        # 3) PCM16 16kHz mono chunk를 base64로 input_audio_buffer.append 반복 송신
        # 4) response.create로 응답 트리거
        # ...

asyncio.run(main())
```

권장 입력 포맷:

| 항목 | 권장값 | 비고 |
|------|--------|------|
| 샘플레이트 | 16,000 Hz | Voxtral 학습 기본 |
| 채널 | mono (1 channel) | 스테레오는 다운믹스 |
| 인코딩 | PCM16 (little-endian) | base64로 `input_audio_buffer.append`에 첨부 |
| chunk size | 80ms × N (모델카드 권장 480ms) | 짧을수록 latency↓, 정확도↓ |

**WebSocket close code**:

| code | 의미 | 대응 |
|------|------|------|
| 4429 | 과부하 차단 | 잠시 후 재시도 (`Retry-After` 헤더 참고) |
| 4503 | 사용 가능한 백엔드 없음 | 잠시 후 재시도 |
| 4500 | 게이트웨이 → 백엔드 연결 실패 | 잠시 후 재시도 |
| 1000 | 정상 종료 | — |

> Realtime 프로토콜 상세는 OpenAI 공식 문서: <https://platform.openai.com/docs/api-reference/realtime>.

---

## 4. 파라미터·응답·에러 레퍼런스

### 4.1 자주 쓰는 요청 파라미터 (transcriptions)

| 파라미터 | 필수 | 기본값 | 설명 |
|----------|:----:|--------|------|
| `file` | O | — | multipart 업로드 파일 |
| `model` | O | — | `whisper-large-v3` / `Voxtral-Mini-4B-Realtime-2602` / `Qwen3-ASR-1.7B` |
| `language` | — | 자동감지 | ISO-639-1 (`ko`, `en`, …). 명시 시 정확도/속도 모두 유리 |
| `temperature` | — | 0 | 0이 권장. 0이 아니면 같은 입력에 다른 출력 가능 |
| `response_format` | — | `json` | `json` / `text` / `srt` / `vtt` / `verbose_json` |
| `timestamp_granularities[]` | — | `[]` | `verbose_json`에서만 의미. `word` / `segment` |

### 4.2 응답 형식

**`json` (기본)**:

```json
{
  "text": "변환된 텍스트",
  "usage": {"type": "duration", "seconds": 4}
}
```

**`verbose_json`** (Whisper / Qwen3-ASR만):

```json
{
  "task": "transcribe",
  "language": "ko",
  "duration": 4.0,
  "text": "...",
  "segments": [{
    "id": 0, "start": 0.0, "end": 1.5, "text": "...",
    "tokens": [...], "temperature": 0.0,
    "avg_logprob": -0.2, "compression_ratio": 1.1, "no_speech_prob": 0.01
  }],
  "words": [{"word": "안녕", "start": 0.1, "end": 0.45}]
}
```

### 4.3 에러 코드

| HTTP | 의미 | 흔한 원인 |
|------|------|----------|
| **400** | Bad Request | 잘못된 form 필드, 지원하지 않는 `response_format`, 디코드 실패 |
| **404** | Not Found | 잘못된 모델명 또는 엔드포인트 경로 |
| **422** | Unprocessable | 요청 바디 파싱 실패 |
| **429** | Too Many Requests | 과부하 차단 — `Retry-After` 후 재시도 |
| **500** | Internal Error | 서버 측 문제 — 잠시 후 재시도, 지속 시 운영자 문의 |
| **502** | Bad Gateway | 게이트웨이 → 백엔드 연결 실패 (게이트웨이 경유 시) |
| **503** | Service Unavailable | 백엔드 미준비 (재기동/웜업 중) |
| **504** | Gateway Timeout | 백엔드 타임아웃 — 오디오를 더 짧게 분할 |

응답 형식:

```json
{
  "error": {
    "message": "...",
    "type": "rate_limit_error | server_error | timeout | bad_gateway",
    "code": "..."
  }
}
```

---

## 5. 클라이언트 통합 (.env)

```bash
# 외부 호출 — whisper·Qwen3-ASR은 :5017 (model 필드 라우팅), Voxtral은 :5018
STT_BASE_URL=http://43.203.142.247:5017/v1
STT_MODEL=whisper-large-v3            # 필요 시 Qwen3-ASR-1.7B. Voxtral은 :5018로
STT_LANGUAGE=ko

# 동일 EC2 안에서 호출 (같은 호스트)
# STT_BASE_URL=http://localhost:5017/v1

# Realtime WS는 Voxtral 전용 게이트웨이(:5018) + ws:// 스킴
# STT_REALTIME_URL=ws://43.203.142.247:5018/v1/realtime
# STT_REALTIME_MODEL=Voxtral-Mini-4B-Realtime-2602
```

FastAPI 프록시 예시:

```python
import os
from openai import AsyncOpenAI
from fastapi import FastAPI, UploadFile

app = FastAPI()
stt = AsyncOpenAI(base_url=os.environ["STT_BASE_URL"], api_key="not-needed")

@app.post("/transcribe")
async def transcribe(file: UploadFile):
    data = await file.read()
    resp = await stt.audio.transcriptions.create(
        file=(file.filename, data, file.content_type or "audio/wav"),
        model=os.environ["STT_MODEL"],
        language=os.environ.get("STT_LANGUAGE", "ko"),
        temperature=0,
    )
    return {"text": resp.text}
```

---

## 다음 단계

- 서버 운영(기동/중지·모델 교체·튜닝·트러블슈팅): [`STT_OPS_GUIDE.md`](STT_OPS_GUIDE.md)
- 배포 절차(로컬 → S3 → EC2): [`DEPLOY_GUIDE.md`](DEPLOY_GUIDE.md)
- vLLM SLM API (Chat): [`VLLM_API_GUIDE.md`](VLLM_API_GUIDE.md)
- OpenAI Audio API 표준: <https://platform.openai.com/docs/api-reference/audio>
- OpenAI Realtime API 표준: <https://platform.openai.com/docs/api-reference/realtime>
