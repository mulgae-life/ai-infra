# vLLM SLM API 가이드 — 개발계·운영계

## 1. 접속 정보

| 항목 | 값 |
|------|-----|
| 개발계 Base URL | `http://10.150.122.69:5501/v1` |
| 운영계 Base URL | `http://10.150.128.19:5501/v1` |
| 모델명 (`model` 필드) | `gemma-4` |
| API 키 | 불필요 |
| 지원 기능 | 스트리밍, Thinking, 이미지 입력, Tool Calling |

- 예시는 개발계 주소 기준입니다. 운영계는 주소만 바꿉니다.
- OpenAI Chat Completions 호환 — OpenAI SDK, LangChain `ChatOpenAI`, `curl`에 `base_url`만 지정합니다.

| 메서드 | 경로 | 용도 |
|--------|------|------|
| POST | `/v1/chat/completions` | 추론 (텍스트·이미지·툴 호출) |
| GET | `/v1/models` | 모델 목록과 컨텍스트 한도 |
| GET | `/health` | 헬스체크 (`200 OK`) |

---

## 2. 첫 호출

### 2.1 curl

```bash
curl http://10.150.122.69:5501/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4",
    "messages": [
      {"role": "system", "content": "간결하게 답변해."},
      {"role": "user",   "content": "대한민국의 수도는?"}
    ],
    "max_tokens": 100
  }'
```

응답:

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "model": "gemma-4",
  "choices": [{
    "index": 0,
    "message": {"role": "assistant", "content": "서울입니다."},
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 25, "completion_tokens": 5, "total_tokens": 30}
}
```

### 2.2 Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://10.150.122.69:5501/v1",
    api_key="not-needed",   # 인증은 없지만 SDK가 빈 값을 거부하므로 아무 값이나 넣는다
)

resp = client.chat.completions.create(
    model="gemma-4",
    messages=[
        {"role": "system", "content": "간결하게 답변해."},
        {"role": "user",   "content": "파이썬이란?"},
    ],
    max_tokens=200,
)
print(resp.choices[0].message.content)
```

### 2.3 LangChain

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="http://10.150.122.69:5501/v1",
    model="gemma-4",
    api_key="not-needed",
    max_tokens=200,
)

print(llm.invoke("대한민국의 수도는?").content)
```

### 2.4 Node.js (OpenAI SDK)

```javascript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "http://10.150.122.69:5501/v1",
  apiKey: "not-needed",
});

const resp = await client.chat.completions.create({
  model: "gemma-4",
  messages: [{ role: "user", content: "안녕" }],
  max_tokens: 100,
});

console.log(resp.choices[0].message.content);
```

### 2.5 컨텍스트 한도 확인

```bash
curl http://10.150.122.69:5501/v1/models
```

```json
{"object": "list", "data": [{
  "id": "gemma-4",
  "max_model_len": 65536,
  "object": "model", "owned_by": "vllm"
}]}
```

- `max_model_len`: 프롬프트 + 출력 합산 토큰 한도
- 초과 시 400

---

## 3. 기능별 사용법

### 3.1 스트리밍

- `"stream": true` → 생성되는 토큰을 SSE로 바로 받음

```bash
curl http://10.150.122.69:5501/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4",
    "messages": [{"role": "user", "content": "긴 시 한 편 써줘"}],
    "max_tokens": 500,
    "stream": true,
    "stream_options": {"include_usage": true}
  }'
```

```
data: {"choices":[{"delta":{"role":"assistant","content":""},"index":0}]}
data: {"choices":[{"delta":{"content":"봄"},"index":0}]}
data: {"choices":[{"delta":{"content":"날의"},"index":0}]}
...
data: {"choices":[],"usage":{"prompt_tokens":14,"completion_tokens":120,"total_tokens":134}}
data: [DONE]
```

- `choices[].delta.content`: 새로 생성된 텍스트
- `data: [DONE]`: 스트림 종료
- `stream_options.include_usage: true` → 마지막 청크에 `usage`

```python
stream = client.chat.completions.create(
    model="gemma-4",
    messages=[{"role": "user", "content": "긴 시 한 편"}],
    max_tokens=500,
    stream=True,
)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### 3.2 Thinking (사고 과정 분리)

- 기본값: 꺼짐
- 켜기: `"chat_template_kwargs": {"enable_thinking": true}`
- 사고 과정: 응답의 `reasoning` 필드 (꺼져 있으면 `null`)

```bash
curl http://10.150.122.69:5501/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4",
    "messages": [{"role": "user", "content": "한 자리 소수를 모두 나열해줘. 이유도 설명해."}],
    "max_tokens": 1000,
    "chat_template_kwargs": {"enable_thinking": true}
  }'
```

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "한 자리 소수는 2, 3, 5, 7입니다.",
      "reasoning": "1은 소수가 아니고... 4=2×2, 6=2×3, 8=2³, 9=3²이므로 합성수..."
    },
    "finish_reason": "stop"
  }]
}
```

Python SDK는 `extra_body`로 전달:

```python
resp = client.chat.completions.create(
    model="gemma-4",
    messages=[{"role": "user", "content": "12를 소인수분해해줘"}],
    max_tokens=1500,
    extra_body={"chat_template_kwargs": {"enable_thinking": True}},
)
print(resp.choices[0].message.reasoning)   # 사고 과정
print(resp.choices[0].message.content)     # 최종 답변
```

- 출력이 2~4배로 늘어남 → `max_tokens` 1,000 이상
- 멀티턴 히스토리에는 `content`만 넣고 `reasoning`은 제외
- `reasoning_effort`(사고 길이)는 현재 모델이 지원하지 않음 — 보내면 값은 무시되고 Thinking만 켜짐

### 3.3 이미지 입력

- `content`를 배열로 보내고 이미지와 텍스트를 함께 넣음
- 요청당 이미지 최대 5장 (초과 시 400)

| 형식 | 용도 |
|------|------|
| `image_url` (data URL, base64) | 로컬 파일, 스크린샷 — **권장** |
| `image_url` (URL) | 서버가 직접 내려받을 수 있는 URL만 가능 (서버가 외부망에 못 나가면 실패) |

**URL 입력**:

```bash
curl http://10.150.122.69:5501/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "image_url", "image_url": {"url": "https://example.com/cat.jpg"}},
        {"type": "text",      "text": "이 이미지에 무엇이 보이나요?"}
      ]
    }],
    "max_tokens": 500
  }'
```

**로컬 파일 (Python)**:

```python
import base64

with open("./document.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

resp = client.chat.completions.create(
    model="gemma-4",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
            {"type": "text", "text": "이 문서의 핵심 내용을 3줄로 요약해줘."},
        ],
    }],
    max_tokens=800,
)
print(resp.choices[0].message.content)
```

- 원본 해상도로 전송 (작은 이미지는 글자 인식 저하)
- 문서·차트는 PNG 등 무손실 형식 권장

### 3.4 Tool Calling

1. `tools`에 함수 정의 → 모델이 필요하면 `tool_calls`로 응답
2. 클라이언트가 함수 실행
3. 결과를 `role: "tool"` 메시지로 다시 전송 → 최종 답변

**1단계 — 툴 정의와 질문**:

```bash
curl http://10.150.122.69:5501/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4",
    "messages": [{"role": "user", "content": "서울 날씨 알려줘"}],
    "tools": [{
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "지정한 도시의 현재 날씨를 조회합니다.",
        "parameters": {
          "type": "object",
          "properties": {"city": {"type": "string", "description": "도시 이름"}},
          "required": ["city"]
        }
      }
    }],
    "max_tokens": 300
  }'
```

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "chatcmpl-tool-abc",
        "type": "function",
        "function": {"name": "get_weather", "arguments": "{\"city\": \"서울\"}"}
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

**2단계 — 실행 결과 전달**:

```bash
curl http://10.150.122.69:5501/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4",
    "messages": [
      {"role": "user", "content": "서울 날씨 알려줘"},
      {"role": "assistant", "content": null,
       "tool_calls": [{"id": "call_1", "type": "function",
                       "function": {"name": "get_weather", "arguments": "{\"city\": \"서울\"}"}}]},
      {"role": "tool", "tool_call_id": "call_1",
       "content": "{\"temperature\": 22, \"condition\": \"맑음\", \"humidity\": 45}"}
    ],
    "max_tokens": 300
  }'
```

```json
{"choices": [{"message": {"role": "assistant", "content": "현재 서울은 22°C, 맑음이며 습도는 45%입니다."},
              "finish_reason": "stop"}]}
```

**LangChain**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """지정한 도시의 현재 날씨를 조회합니다."""
    return f"{city}: 22°C, 맑음"

llm = ChatOpenAI(base_url="http://10.150.122.69:5501/v1", model="gemma-4", api_key="not-needed")
resp = llm.bind_tools([get_weather]).invoke("서울 날씨 알려줘")
print(resp.tool_calls)
```

### 3.5 멀티턴 대화

- 서버는 대화 상태를 저장하지 않음 → 이전 대화를 `messages`에 누적해 전송

```python
messages = [
    {"role": "system", "content": "간결한 한국어 비서."},
    {"role": "user",   "content": "내 이름은 홍길동이야."},
]
resp1 = client.chat.completions.create(model="gemma-4", messages=messages, max_tokens=100)
messages.append({"role": "assistant", "content": resp1.choices[0].message.content})

messages.append({"role": "user", "content": "내 이름이 뭐였지?"})
resp2 = client.chat.completions.create(model="gemma-4", messages=messages, max_tokens=100)
print(resp2.choices[0].message.content)
```

| role | 설명 |
|------|------|
| `system` | 역할·톤 지시 (맨 앞에 1개) |
| `user` | 사용자 입력 |
| `assistant` | 모델의 이전 응답 |
| `tool` | 툴 실행 결과 |

- 같은 `system` 프롬프트로 반복 호출하면 첫 토큰이 빨라짐 (프리픽스 캐싱, 자동 적용)

---

## 4. 레퍼런스

### 4.1 요청 파라미터

| 파라미터 | 필수 | 설명 |
|----------|:----:|------|
| `model` | O | `gemma-4` |
| `messages` | O | 대화 메시지 배열 |
| `max_tokens` | — | 최대 생성 토큰 수 |
| `stream` | — | `true`면 스트리밍 |
| `stream_options` | — | `{"include_usage": true}`면 마지막 청크에 usage |
| `tools` | — | Tool Calling 함수 정의 |
| `chat_template_kwargs` | — | `{"enable_thinking": true}`로 Thinking 켜기 |
| `temperature` | — | 0이면 결정적 출력. 생략하면 서버 기본값 |
| `top_p` / `top_k` | — | 생략하면 서버 기본값 |
| `seed` | — | 재현용 (`temperature: 0`과 함께) |
| `stop` | — | 생성 중단 문자열 |
| `presence_penalty` | — | 같은 표현이 반복되면 1.0~1.5 |

- 샘플링 파라미터(`temperature`·`top_p`·`top_k`)는 생략 권장 — 서버가 모델 기본값 적용

### 4.2 응답 형식

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1738200000,
  "model": "gemma-4",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "...",
      "reasoning": "...",
      "tool_calls": [...]
    },
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 25, "completion_tokens": 120, "total_tokens": 145}
}
```

| `finish_reason` | 의미 |
|-----------------|------|
| `stop` | 정상 종료 |
| `length` | `max_tokens`에 도달해 잘림 |
| `tool_calls` | 툴 호출 요청 |

### 4.3 에러 코드

| HTTP | 의미 | 조치 |
|------|------|------|
| 400 | 잘못된 요청 | 요청 본문 형식, 파라미터 값, 이미지 개수(5장), 컨텍스트 한도 확인 |
| 404 | 없는 모델·경로 | `model`이 `gemma-4`인지, 경로 확인 |
| 429 | 서버 혼잡 | `Retry-After` 헤더의 초만큼 기다렸다가 재시도 |
| 504 | 응답 시간 초과 (300초) | 긴 생성은 `stream: true`로 받거나 `max_tokens`를 줄임 |
| 500 | 서버 오류 | 잠시 후 재시도, 계속되면 운영자 문의 |

에러 응답 예:

```json
{"error": {"message": "temperature must be non-negative, got -1.0.", "type": "BadRequestError", "param": "temperature", "code": 400}}
```
