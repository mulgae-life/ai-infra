# vLLM SLM API 가이드 — 연구계 (사용자용)

> **대상**: 연구계 서버를 호출하는 API 사용자 (개발자, 챗봇/RAG 통합)
> **모델명**: `gemma-4` — 요청의 `model` 필드에 항상 이 값을 씁니다. 뒤에서 어떤 모델이 돌든 이 이름은 바뀌지 않습니다.
> **Base URL**: `http://43.203.142.247:5015/v1` (외부, 연구계). 개발계·운영계 호출은 [`VLLM_API_GUIDE_dev_prd.md`](VLLM_API_GUIDE_dev_prd.md)를 보세요.
> **API 호환**: OpenAI Chat Completions 100% — 기존 OpenAI SDK · LangChain `ChatOpenAI` · `curl` 그대로
> **인증**: 불필요 (`Authorization` 헤더 생략 가능)

자체 호스팅한 vLLM SLM(Small Language Model)을 **OpenAI API · Claude API 쓰듯** 호출하기 위한 가이드입니다.

처음 호출하는 분은 §1~§3만 보면 됩니다. 운영(서버 기동·튜닝·트러블슈팅·테스트)은 [`VLLM_OPS_GUIDE.md`](VLLM_OPS_GUIDE.md) 참고.

---

## 📑 목차

1. [한눈에 보기](#1-한눈에-보기)
2. [첫 호출](#2-첫-호출)
3. [핵심 기능](#3-핵심-기능)
   - 3.1 스트리밍 (SSE)
   - 3.2 Thinking 모드 (사고 과정 분리)
   - 3.3 이미지 멀티모달 (Vision)
   - 3.4 Tool Calling (함수 호출)
   - 3.5 멀티턴 대화
4. [파라미터·응답·에러 레퍼런스](#4-파라미터응답에러-레퍼런스)

---

## 1. 한눈에 보기

| 항목 | 값 |
|------|-----|
| Base URL | `http://43.203.142.247:5015/v1` (연구계) |
| 모델명 (`model` 필드) | **`gemma-4`** — 고정 |
| API 키 | 불필요 |
| 멀티모달 (이미지) | ✅ |
| Tool Calling | ✅ |
| 스트리밍 (SSE) | ✅ |
| Thinking | 기본 OFF. `enable_thinking`으로 요청 단위 제어 ([§3.2](#32-thinking-모드-사고-과정-분리)) |
| 컨텍스트 길이 | `GET /v1/models`의 `max_model_len` 참조 ([§2.5](#25-모델-목록-확인)) |

> 📌 **모델명은 `gemma-4` 하나뿐입니다.** 서버 뒤에서는 상황에 따라 다른 모델이 돌 수 있지만,
> API가 노출하는 이름은 바뀌지 않습니다. `model` 필드에 다른 값을 넣으면 404가 납니다.
>
> 모델이 바뀌어도 클라이언트 코드를 고칠 일이 없도록 게이트웨이가 요청을 맞춰줍니다. 아래 두 가지만
> 지키면 됩니다.
>
> - **사고 과정은 `reasoning` 필드로 읽습니다.** 모델마다 다른 사고 토큰 형식은 서버가 처리합니다.
> - **컨텍스트 한도는 코드에 박지 말고 `/v1/models`에서 읽습니다.** 운영 튜닝값에 따라 달라집니다.

**API 호환성**: vLLM은 OpenAI Chat Completions API와 **100% 호환**. `OpenAI` SDK · `langchain_openai.ChatOpenAI` · `fetch` · `curl` 어떤 클라이언트도 `base_url`만 바꾸면 그대로 동작합니다.

**엔드포인트 요약**:

| 메서드 | 경로 | 용도 |
|--------|------|------|
| POST | `/v1/chat/completions` | **메인 추론 API** (텍스트·이미지·툴 호출 모두) |
| GET | `/v1/models` | 로드된 모델 목록 |
| GET | `/health` | 서버 헬스체크 |

> 🔒 **PII/DLP 가드 (운영 모드에 따라 적용)** — LLM 진입점(`:5015`)은 두 모드 중 하나로 운영됩니다. **① 비PII 모드(현재 기본)**: 게이트웨이가 직접 응답하며 아래 검사가 적용되지 않습니다. **② PII 모드**: 프록시가 같은 포트를 인수해 요청(in)과 응답(out)의 텍스트를 모두 검사합니다. 어느 모드든 **호출 주소·방식은 동일**하며, 현재 모드는 운영자에게 확인하세요. PII 모드에서는 아래가 적용됩니다:
> - **차단 (HTTP 422)**: 주민등록번호·신용카드번호가 포함되면 추론 전에 거부됩니다 (`type: pii_blocked`). 이런 정보는 보내지 마세요.
> - **자동 마스킹**: 이름·전화·주소·조직·계좌·사업자등록번호·이메일은 `[이름]`·`[전화번호]` 등으로 치환되어 모델에 전달되고, **응답에서도** 동일하게 마스킹됩니다.
> - **조직명 마스킹 끄기 (서비스 선택)**: 문서 생성처럼 부서명·회사명을 보존해야 하는 서비스는 요청 헤더 `X-PII-Ignore-Types: org` 로 **조직(ORG) 마스킹만** 끌 수 있습니다. 핵심 PII(주민·카드·이름·전화·주소 등)는 헤더와 무관하게 **항상 마스킹**됩니다 (서버 화이트리스트로 끌 수 있는 타입을 통제). 상세는 [§3.6](#36-pii-마스킹-토글-헤더).
> - **PII 없이 SLM 직행**: 요청 헤더 `X-PII-Mode: bypass` 로 **PII 검사를 통째 건너뛰고** 모델에 원문을 보낼 수 있습니다 (`:5015` 프록시 설정 기본 활성, 헤더 없으면 강제 검사). 상세는 [§3.7](#37-pii-우회-bypass-헤더).
> - **스트리밍**: 응답 PII 검사를 위해 `stream:true`라도 완결 후 한 번에 전달됩니다(토큰 점진 출력만 일시 비활성). `usage`·`finish_reason`·`reasoning` 분리 등 응답 구조는 보존됩니다 — [§3.1](#31-스트리밍-sse).
> - **이미지 입력**: 멀티모달 요청의 **텍스트 파트는 검사·마스킹**됩니다. 단, **이미지 바이트 자체**는 검사 대상이 아닙니다(설계상 한계 — [§3.3](#33-이미지-멀티모달-vision)).
> - **도구 호출**: `tool_calls`의 함수 인자(JSON) 안 PII도 요청·응답 양방향으로 마스킹됩니다.
> - **장애 시**: PII 엔진 일시 장애면 보안상 요청을 차단합니다 (HTTP 503 `pii_unavailable`, fail-closed). fail-open 설정이라도 주민·카드 같은 구조화 PII는 항상 마스킹됩니다.

---

## 2. 첫 호출

> 호출 전 살아있는지 확인: `curl http://43.203.142.247:5015/health` → `200 OK`.

### 2.1 curl

```bash
curl http://43.203.142.247:5015/v1/chat/completions \
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
    base_url="http://43.203.142.247:5015/v1",
    api_key="not-needed",   # vLLM 기본 인증 없음. 빈 문자열은 SDK가 거부하므로 더미값.
)

resp = client.chat.completions.create(
    model="gemma-4",
    messages=[
        {"role": "system", "content": "간결하게 답변해."},
        {"role": "user",   "content": "파이썬이란?"},
    ],
    max_tokens=200,
    temperature=0.7,
)
print(resp.choices[0].message.content)
```

### 2.3 LangChain

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="http://43.203.142.247:5015/v1",
    model="gemma-4",
    api_key="not-needed",
    temperature=0.7,
    max_tokens=200,
)

print(llm.invoke("대한민국의 수도는?").content)
```

### 2.4 Node.js (OpenAI SDK)

```javascript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "http://43.203.142.247:5015/v1",
  apiKey: "not-needed",
});

const resp = await client.chat.completions.create({
  model: "gemma-4",
  messages: [{ role: "user", content: "안녕" }],
  max_tokens: 100,
});

console.log(resp.choices[0].message.content);
```

### 2.5 모델 목록 확인

```bash
curl http://43.203.142.247:5015/v1/models
```

```json
{"object": "list", "data": [{
  "id": "gemma-4",
  "max_model_len": 65536,
  "object": "model", "owned_by": "vllm"
}]}
```

`max_model_len`이 **프롬프트와 출력을 합친 현재 컨텍스트 한도**입니다. 운영 튜닝에 따라 달라지므로
코드에 숫자를 박지 말고 여기서 읽으세요. 초과하면 400이 납니다.

---

## 3. 핵심 기능

### 3.1 스트리밍 (SSE)

`stream: true`를 주면 토큰이 생성되는 즉시 Server-Sent Events로 흘러나옵니다.

> 🔒 **PII 모드 한정 제약**: 비PII 모드(현재 기본)에서는 토큰이 생성 즉시 점진적으로 흘러나옵니다. **PII 모드**의 `:5015`는 응답 PII 마스킹을 보장하기 위해 스트리밍을 **완결 후 1회 방출**합니다. 즉 `stream:true`를 줘도 토큰이 점진적으로 오지 않고, 마스킹이 끝난 전체 응답이 도착합니다. 단, **응답 구조는 보존**됩니다 — `id`/`created`/`model`, `usage`(`include_usage` 시), `finish_reason`, `reasoning`↔`content` 분리, `tool_calls` 인자가 그대로 유지되어 OpenAI 클라이언트 파싱이 정상 동작합니다. 토큰 점진 출력은 **현재 미지원**입니다(PII 경계 누출 위험으로 별도 설계 후 도입 예정). PII가 불필요한 호출이면 [§3.7](#37-pii-우회-bypass-헤더) 우회로 원문 스트리밍을 받을 수 있습니다.

**curl**:

```bash
curl http://43.203.142.247:5015/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4",
    "messages": [{"role": "user", "content": "긴 시 한 편 써줘"}],
    "max_tokens": 500,
    "stream": true,
    "stream_options": {"include_usage": true}
  }'
```

응답 (SSE):

```
data: {"choices":[{"delta":{"role":"assistant","content":""},"index":0}]}
data: {"choices":[{"delta":{"content":"봄"},"index":0}]}
data: {"choices":[{"delta":{"content":"날의"},"index":0}]}
...
data: {"choices":[],"usage":{"prompt_tokens":14,"completion_tokens":120,"total_tokens":134}}
data: [DONE]
```

- 각 청크는 `data: ` 접두사 + JSON
- `choices[].delta.content`에 새로 생성된 토큰 텍스트
- `data: [DONE]`이 스트림 종료 신호
- `stream_options.include_usage: true`를 넣으면 마지막 청크에 `usage`가 따라옴

**Python 스트리밍**:

```python
stream = client.chat.completions.create(
    model="gemma-4",
    messages=[{"role": "user", "content": "긴 시 한 편"}],
    max_tokens=500,
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

---

### 3.2 Thinking 모드 (사고 과정 분리)

모델이 답변 전에 **"생각"하는 과정**을 `reasoning` 필드로 분리해서 받습니다. 추론·수학·복잡한 분석처럼 사고 과정 자체가 쓸모 있는 작업에 씁니다.

**기본값은 OFF입니다** (챗봇 응답 지연을 줄이기 위해). 요청 단위로 켭니다.

**켜는 법** — 이 한 줄이 전부입니다.

```json
{"chat_template_kwargs": {"enable_thinking": true}}
```

**읽는 법** — 응답 메시지의 `reasoning` 필드를 봅니다. Thinking을 끈 응답에서는 `null`입니다.

```bash
curl http://43.203.142.247:5015/v1/chat/completions \
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

**Python** (OpenAI SDK는 vLLM 전용 옵션을 `extra_body`로 전달합니다):

```python
resp = client.chat.completions.create(
    model="gemma-4",
    messages=[{"role": "user", "content": "12를 소인수분해해줘"}],
    max_tokens=1500,
    extra_body={"chat_template_kwargs": {"enable_thinking": True}},
)
print("🤔 사고 과정:", resp.choices[0].message.reasoning)   # 꺼져 있으면 None
print("💬 최종 답변:", resp.choices[0].message.content)
```

> 📌 **모델이 바뀌어도 이 코드는 그대로입니다.** 사고 과정을 감싸는 토큰은 모델마다 다르지만
> (`<think>…</think>`, `<|channel>…<channel|>` 등), 서버가 그 차이를 처리해서 항상 `reasoning`
> 필드로 넘겨줍니다. 클라이언트가 토큰 형식을 알아야 할 일은 없습니다.
>
> 필드명은 `reasoning`입니다. 예전 vLLM과 DeepSeek 계열 서버는 `reasoning_content`를 썼고
> 지금도 입력 쪽에 남아 있지만 폐기 예정입니다. 다른 서버와 코드를 공유한다면
> `msg.get("reasoning") or msg.get("reasoning_content")` 패턴으로 받으세요.

**주의 사항**:

- Thinking을 켜면 응답 토큰이 보통 2~4배로 늘어납니다. `max_tokens`를 1,000 이상으로 잡으세요.
- 멀티턴 히스토리에 **사고 과정을 다시 넣지 마세요**. `messages`에는 최종 `content`만 넣습니다. 사고 과정은 그 턴에서만 씁니다.

#### 사고 길이 조절 (`reasoning_effort`)

Thinking을 켠 상태에서 **얼마나 오래 생각할지**를 조절합니다. `enable_thinking`이 스위치라면 이쪽은 강약입니다.

| 값 | 동작 | 언제 |
|----|------|------|
| `low` | 짧게 생각하고 결론으로 | 지연이 중요할 때 |
| `medium` | 기본 수준 | 대부분의 호출 |
| `high` | 가정 검증·대안 검토까지 길게 | 어려운 추론·분석. 생성량이 배로 늘어 그만큼 오래 걸림 |
| (생략) | 서버 기본값 | 특별한 이유가 없으면 |

```bash
curl http://43.203.142.247:5015/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4",
    "messages": [{"role": "user", "content": "이 설계의 병목을 찾아줘"}],
    "max_tokens": 8000,
    "reasoning_effort": "high",
    "chat_template_kwargs": {"enable_thinking": true}
  }'
```

> 📌 **아무 값이나 보내도 에러가 나지 않습니다.** 모델마다 받아들이는 값이 다르지만, 게이트웨이가
> 현재 모델이 아는 값으로 번역하고, 지원하지 않는 모델이면 조용히 무시합니다.
>
> 실제로 적용된 값은 응답 헤더 **`X-Effort-Applied`** 에 실립니다. `high`를 보냈는데 헤더에
> `xhigh`가 오면 번역된 것이고, `dropped`면 현재 모델이 이 옵션을 지원하지 않아 무시된 것입니다.
> 사고 길이가 기대와 다르면 이 헤더부터 확인하세요.

> ⚠️ **`high` + 큰 `max_tokens`는 비스트리밍에서 504가 납니다.** 게이트웨이 업스트림 타임아웃이
> 300초인데, 비스트리밍은 생성이 다 끝나야 첫 바이트가 오기 때문입니다. `max_tokens: 32000` +
> 최대 강도로 재보니 요청당 4~8분이 걸려 `upstream_timeout`으로 끊겼습니다.
> 스트리밍(`"stream": true`)은 청크가 올 때마다 타이머가 갱신되어 이 제한에 걸리지 않습니다.
> 비스트리밍으로 길게 사고시켜야 하면 `max_tokens`를 낮추세요.

---

### 3.3 이미지 멀티모달 (Vision)

이미지와 텍스트를 함께 보내면 이미지를 읽고 답합니다. 문서 글자 인식, 차트 해석, 화면 캡처 질의에 씁니다.

> 🔒 **PII 가드 (PII 모드 한정)**: 멀티모달 요청의 **텍스트 파트(`{"type":"text"}`)는 정상적으로 in/out 검사·마스킹**됩니다. 단, **이미지 바이트 자체**(픽셀 내 글자 등)는 검사 대상이 아닙니다. 개인정보가 담긴 문서 **이미지**를 보낼 때는 이미지 안의 PII가 가려지지 않는다는 점에 유의하세요.

**입력 형식 2가지**:

| 형식 | 사용 시 |
|------|--------|
| `image_url` | 공개 URL (외부 접근 가능 이미지) |
| `data URL (base64)` | 로컬 파일, 스크린샷 등 |

> 한 요청당 첨부 가능 이미지 수는 운영 튜닝값(`limit_mm_per_prompt.image`)에 따라 달라집니다. 초과 시 HTTP 400이 반환되니 작게 시작해 늘려보세요. 정확한 현재 한도는 운영자에게 확인하세요.

**curl — URL 입력**:

```bash
curl http://43.203.142.247:5015/v1/chat/completions \
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

**curl — Base64 입력**:

```bash
# Linux (GNU coreutils)
B64=$(base64 -w0 ./screenshot.png)
# macOS (BSD base64 — `-w0` 미지원, 기본이 한 줄 출력)
# B64=$(base64 -i ./screenshot.png | tr -d '\n')

curl http://43.203.142.247:5015/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"gemma-4\",
    \"messages\": [{
      \"role\": \"user\",
      \"content\": [
        {\"type\": \"image_url\", \"image_url\": {\"url\": \"data:image/png;base64,${B64}\"}},
        {\"type\": \"text\",      \"text\": \"이 화면의 텍스트를 모두 추출해줘.\"}
      ]
    }],
    \"max_tokens\": 1500
  }"
```

**Python — 로컬 파일을 base64로**:

```python
import base64
from openai import OpenAI

client = OpenAI(base_url="http://43.203.142.247:5015/v1", api_key="not-needed")

with open("./document.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

resp = client.chat.completions.create(
    model="gemma-4",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image_url",
             "image_url": {"url": f"data:image/png;base64,{b64}"}},
            {"type": "text",
             "text": "이 문서의 핵심 내용을 3줄로 요약해줘."},
        ],
    }],
    max_tokens=800,
)
print(resp.choices[0].message.content)
```

**Python — 이미지 + Thinking 동시**:

```python
resp = client.chat.completions.create(
    model="gemma-4",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image_url",
             "image_url": {"url": f"data:image/png;base64,{b64}"}},
            {"type": "text", "text": "이 차트가 보여주는 트렌드는?"},
        ],
    }],
    max_tokens=2000,
    extra_body={"chat_template_kwargs": {"enable_thinking": True}},
)
print("사고:", resp.choices[0].message.reasoning)
print("답변:", resp.choices[0].message.content)
```

**해상도/사용 팁**:

- 이미지가 너무 작으면 (예: 50×50 아이콘) 모델이 "잘 안 보인다"고 답할 수 있음 → 원본 해상도를 유지해서 보내세요.
- 동일 요청에 너무 많은 이미지를 묶으면 HTTP 400 (운영 한도 초과). 안전하게 한두 장씩 끊어 보내거나 운영자에게 한도 확인.
- 디테일이 중요한 문서/차트는 PNG 같은 무손실 포맷 권장 (JPEG는 글자 가장자리 흐림).

---

### 3.4 Tool Calling (함수 호출)

모델이 외부 함수를 **호출하기로 결정**하면 OpenAI 호환 JSON으로 자동 파싱되어 옵니다. `tools` 정의 → 모델이 `tool_calls` 응답 → 클라이언트가 실제 함수 실행 → 결과를 `role: "tool"` 메시지로 다시 전달 → 최종 답변.

**1단계 — 툴 정의 + 사용자 질문**:

```bash
curl http://43.203.142.247:5015/v1/chat/completions \
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
          "properties": {
            "city": {"type": "string", "description": "도시 이름"}
          },
          "required": ["city"]
        }
      }
    }],
    "max_tokens": 300
  }'
```

응답 — 모델이 함수 호출을 결정:

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "chatcmpl-tool-abc",
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"city\": \"서울\"}"
        }
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

**2단계 — 함수 실행 결과를 다시 전달**:

```bash
curl http://43.203.142.247:5015/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4",
    "messages": [
      {"role": "user", "content": "서울 날씨 알려줘"},
      {
        "role": "assistant",
        "content": null,
        "tool_calls": [{
          "id": "call_1",
          "type": "function",
          "function": {"name": "get_weather", "arguments": "{\"city\": \"서울\"}"}
        }]
      },
      {
        "role": "tool",
        "tool_call_id": "call_1",
        "content": "{\"temperature\": 22, \"condition\": \"맑음\", \"humidity\": 45}"
      }
    ],
    "max_tokens": 300
  }'
```

최종 응답:

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "현재 서울은 22°C, 맑음이며 습도는 45%입니다."
    },
    "finish_reason": "stop"
  }]
}
```

**LangChain `bind_tools`**:

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """지정한 도시의 현재 날씨를 조회합니다."""
    return f"{city}: 22°C, 맑음"

llm = ChatOpenAI(
    base_url="http://43.203.142.247:5015/v1",
    model="gemma-4",
    api_key="not-needed",
)
llm_with_tools = llm.bind_tools([get_weather])
resp = llm_with_tools.invoke("서울 날씨 알려줘")
print(resp.tool_calls)
# → [{'name': 'get_weather', 'args': {'city': '서울'}, 'id': 'chatcmpl-tool-...'}]
```

> 툴이 필요 없다고 모델이 판단하면 `tool_calls` 없이 `content`로 바로 답변합니다.

---

### 3.5 멀티턴 대화

이전 응답을 그대로 `messages`에 누적해 보내면 됩니다. 별도 세션 ID 관리 불필요 (stateless).

```python
messages = [
    {"role": "system", "content": "간결한 한국어 비서."},
    {"role": "user",   "content": "내 이름은 홍길동이야."},
]

resp1 = client.chat.completions.create(
    model="gemma-4", messages=messages, max_tokens=100,
)
messages.append({"role": "assistant", "content": resp1.choices[0].message.content})

messages.append({"role": "user", "content": "내 이름이 뭐였지?"})
resp2 = client.chat.completions.create(
    model="gemma-4", messages=messages, max_tokens=100,
)
print(resp2.choices[0].message.content)   # → "홍길동님이라고 하셨습니다."
```

**역할 (`role`) 규칙**:

| role | 설명 |
|------|------|
| `system` | 모델의 역할·톤 지시 (선택, 1개 권장, 맨 앞) |
| `user` | 사용자 입력 |
| `assistant` | 모델의 이전 응답 (멀티턴 누적) |
| `tool` | 툴 실행 결과 (Tool Calling 시) |

**프리픽스 캐싱**: 동일 `system` 프롬프트로 반복 호출하면 vLLM이 KV 캐시를 재사용해 TTFT(첫 토큰 대기시간)를 크게 줄여줍니다 — 챗봇 시나리오에 자동 적용. 별도 옵션 불필요.

---

### 3.6 PII 마스킹 토글 (헤더)

> 📌 **PII 모드 전용** — 비PII 모드(현재 기본)에서는 검사 자체가 없어 이 헤더가 의미 없습니다. §3.6~§3.7은 PII 모드 환경에서만 해당합니다.

PII 모드의 `:5015`는 이름·전화·주소·**조직(ORG)** 등 비식별 PII를 자동 마스킹합니다. 하지만 **문서 생성**처럼 작성부서명·회사명을 보존해야 하는 서비스는 조직명이 `[조직]`으로 가려지면 문서 헤더가 손상됩니다. 이를 위해 **요청 단위로 ORG 마스킹만 끄는** 헤더를 제공합니다.

| 헤더 | 값 | 효과 |
|------|----|----|
| `X-PII-Ignore-Types` | `org` | 해당 요청의 in/out에서 **조직명 마스킹만** 비활성화 |

> 🔒 **안전장치**: 끌 수 있는 타입은 서버 화이트리스트(`ignorable_types`, 기본 `["org"]`)로 통제됩니다. **핵심 PII(주민·카드·이름·전화·주소·이메일·계좌 등)는 이 헤더로 끌 수 없습니다** — 무슨 값을 보내도 항상 마스킹됩니다. 차단 대상(주민·카드)도 마찬가지로 항상 422 차단됩니다. ORG를 끄더라도 감사로그에는 검출 사실이 `skip`으로 기록됩니다.

**curl — 조직명 보존**:

```bash
curl http://43.203.142.247:5015/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-PII-Ignore-Types: org" \
  -d '{
    "model": "gemma-4",
    "messages": [{"role": "user",
      "content": "작성부서 디지털AI센터, 담당자 홍길동 010-1234-5678 기준으로 보고서 헤더를 만들어줘."}]
  }'
# → 모델에 전달되는 텍스트: "작성부서 디지털AI센터, 담당자 [이름] [전화번호] 기준으로 …"
#   (조직명 '디지털AI센터'는 보존, 이름·전화는 그대로 마스킹)
```

**Python (OpenAI SDK) — 기본 헤더로 주입**:

```python
from openai import OpenAI

# 문서 생성 서비스: 클라이언트 단에서 한 번만 설정하면 모든 호출에 적용
client = OpenAI(base_url="http://43.203.142.247:5015/v1", api_key="not-needed",
                default_headers={"X-PII-Ignore-Types": "org"})
```

---

### 3.7 PII 우회 (bypass 헤더)

PII가 전혀 필요 없는 호출(예: 비식별 사내 문서 가공, PII가 없음이 보장된 배치 작업)에서는 검사 자체를 건너뛰고 SLM에 원문을 그대로 보낼 수 있습니다. **§3.6의 `X-PII-Ignore-Types`가 "특정 타입만 마스킹 스킵"인 것과 달리, 이건 in/out 검사를 통째 생략**합니다.

| 헤더 | 값 | 효과 |
|------|----|----|
| `X-PII-Mode` | `bypass` | 해당 요청의 PII 검사(in/out) 전체 생략, 원문 직행 |
| `X-PII-Mode` | `enforce` 또는 생략 | 기본 — PII 검사 적용 |

> ⚠️ **현재 기본 활성화**: 이 우회는 프록시 설정 `allow_bypass`로 게이팅됩니다. **현재 `:5015`는 기본값이 `true`라 헤더만으로 우회**됩니다(토큰 미설정). 강제 검사로 묶으려면 해당 프록시 설정에서 `allow_bypass: false`로 끄면 됩니다(끄면 헤더를 보내도 무시되고 검사가 강제됨). 모든 우회 요청은 감사로그에 `action=bypass`로 기록됩니다.
>
> 🔑 **토큰 2차 가드(선택)**: 운영자가 `bypass_token`(env `PII_BYPASS_TOKEN`)을 설정한 환경에서는 추가로 헤더 `X-PII-Bypass-Token: <토큰>`이 일치해야 우회됩니다. 외부 포트가 열린 환경에서 "헤더 하나로 우회"를 막는 용도이며, 토큰이 틀리면 검사가 강제됩니다.

```bash
# 현재 :5015는 기본 활성(allow_bypass=true) — 헤더만으로 우회됨
curl http://43.203.142.247:5015/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-PII-Mode: bypass" \
  -d '{"model": "gemma-4",
       "messages": [{"role": "user", "content": "비식별 공지문 초안을 다듬어줘 ..."}]}'
```

> 💡 **언제 무엇을 쓰나**: 조직명만 살리고 싶다 → `X-PII-Ignore-Types: org`(§3.6). PII 가드 자체가 불필요하다 → `X-PII-Mode: bypass`(본 절). 둘 다 헤더 단위라 요청마다 선택 가능합니다.

---

## 4. 파라미터·응답·에러 레퍼런스

### 4.1 자주 쓰는 요청 파라미터

| 파라미터 | 필수 | 기본값 | 설명 |
|----------|:----:|--------|------|
| `model` | O | — | `gemma-4` (고정) |
| `messages` | O | — | 대화 메시지 배열 |
| `max_tokens` | — | 모델 한계 | 최대 생성 토큰 수. Thinking ON이면 1,000+ 권장 |
| `temperature` | — | 서버 기본 | 0=결정적. 생략하면 모델 기본값이 적용됩니다 |
| `top_p` | — | 서버 기본 | 누적 확률 상위 토큰만 후보로 |
| `top_k` | — | 서버 기본 | 후보 토큰 수 |
| `seed` | — | — | 재현 가능한 출력 (`temperature=0`과 함께) |
| `stop` | — | — | 생성 중단 토큰(들) |
| `stream` | — | false | true면 SSE 스트리밍 |
| `stream_options` | — | — | `{"include_usage": true}`면 스트리밍 마지막 청크에 usage 포함 |
| `tools` | — | — | Tool Calling 함수 정의 |
| `chat_template_kwargs` | — | — | 템플릿 인자. `{"enable_thinking": true}` ([§3.2](#32-thinking-모드-사고-과정-분리)) |
| `reasoning_effort` | — | 서버 기본 | 사고 길이. `low`/`medium`/`high`. 어떤 값을 보내도 에러가 나지 않습니다 ([§3.2](#32-thinking-모드-사고-과정-분리)) |
| `presence_penalty` | — | 0 | 같은 표현 반복이 보이면 1.0~1.5 |
| `extra_body` (Python SDK) | — | — | OpenAI 표준에 없는 vLLM 옵션을 실어 보낼 때 |

> 샘플링 파라미터는 **생략을 권합니다.** 서버가 현재 모델에 맞는 기본값을 적용하므로, 값을 박아두면
> 모델이 바뀌었을 때 오히려 품질이 떨어질 수 있습니다. 결정적 출력이 필요할 때만 `temperature: 0` +
> `seed`를 명시하세요.

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
      "content": "...",                  // 텍스트 답변
      "reasoning": "...",                // (Thinking ON 시) 사고 과정
      "tool_calls": [...]                // (함수 호출 시)
    },
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 25, "completion_tokens": 120, "total_tokens": 145}
}
```

`finish_reason`:

| 값 | 의미 |
|----|------|
| `stop` | 자연 종료 (EOS 토큰 생성) |
| `length` | `max_tokens` 도달로 잘림 — `max_tokens`를 늘리세요 |
| `tool_calls` | 툴 호출 요청 |

### 4.3 에러 코드

| HTTP | 의미 | 흔한 원인 |
|------|------|----------|
| **400** | Bad Request | 요청 바디 형식 오류, 파라미터 값 범위 위반 (예: `temperature: -1`), 멀티모달 한도 초과 |
| **404** | Not Found | 잘못된 모델명 또는 엔드포인트 경로 |
| **422** | **PII 차단** (PII 모드) | 주민/카드번호 포함으로 차단 (`type: pii_blocked`) |
| **429** | 서버 혼잡 | 대기열이 가득 참 — `Retry-After` 헤더의 초만큼 기다렸다가 재시도 |
| **504** | 응답 시간 초과 | 비스트리밍 응답이 300초를 넘음 — `stream: true`로 받거나 `max_tokens`를 줄임 ([§3.2](#32-thinking-모드-사고-과정-분리)) |
| **503** | PII 검사 불가 (PII 모드) | PII 엔진(NER) 일시 장애 시 fail-closed로 요청 차단 (`type: pii_unavailable`) — 잠시 후 재시도 |
| **500** | Internal Error | 서버 측 문제 — 잠시 후 재시도, 지속 시 운영자 문의 |

> 🔒 **PII 차단 응답 형식** (HTTP 422):
> ```json
> {"error": {"message": "입력에 개인정보(주민등록번호·카드번호 등)가 포함되어 차단되었습니다.",
>            "type": "pii_blocked", "request_id": "..."}}
> ```
> `request_id`는 감사로그 추적용입니다(원문 PII는 저장되지 않음).

일반 에러 응답 형식:

```json
{
  "error": {
    "message": "temperature must be non-negative, got -1.0.",
    "type": "BadRequestError",
    "param": "temperature",
    "code": 400
  }
}
```

### 4.4 샘플링 파라미터

모델의 `generation_config.json`이 서버에서 자동 적용되므로 **보통 아무것도 명시하지 않는 게 낫습니다.**
모델별 권장값은 모델을 교체할 때마다 달라지므로 운영자용 문서인
[`VLLM_OPS_GUIDE.md`](VLLM_OPS_GUIDE.md)에서 관리합니다.

명시가 필요한 경우는 둘뿐입니다.

- **결정적 출력**: `temperature: 0` + `seed` 고정
- **같은 표현 반복**: `presence_penalty` 1.0~1.5. 한국어 응답에 다른 언어가 섞일 때도 효과가 있습니다

---

## 다음 단계

- 서버 운영(기동/중지·모델 교체·튜닝·트러블슈팅): [`VLLM_OPS_GUIDE.md`](VLLM_OPS_GUIDE.md)
- 배포 절차(로컬 → S3 → EC2): [`DEPLOY_GUIDE.md`](DEPLOY_GUIDE.md)
