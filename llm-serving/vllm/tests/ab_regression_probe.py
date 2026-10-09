#!/usr/bin/env python3
"""vLLM 버전 A/B 회귀·품질 탐침 — 계획서 part2 P3의 "회귀 집중"·"품질" 항목.

같은 GPU·같은 설정으로 옛·새 vLLM에 각각 돌려 결과 파일을 남기고, --compare로 두 파일을 대조한다.
기능 시험(test_vllm_server.py 31종)이 덮지 않는 것만 모았다.

판정 항목 (정답을 기계적으로 가릴 수 있는 것만, 하나라도 실패하면 종료 코드 1):
  copy    숫자·코드 값 복사 5건 — 원문 그대로 응답에 들어 있는지
  tool    숫자·괄호가 든 도구 인자 — thinking 끔/켬 × 비스트리밍/스트리밍 4건.
          tool_choice auto로 보내 서버의 도구 호출 파서 경로를 탄다(이름 지정 호출은 구조화 출력이라 파서를 안 탄다).
          인자 값 외에 호출 1건·id·type function·finish_reason tool_calls·본문에 호출 표식 누출 없음·스트림 [DONE]을 본다.
          thinking 켬에서 사고 없이 바로 호출해도 실패로 치지 않는다
  tool-followup  비스트리밍 호출의 id로 도구 결과를 돌려준 뒤 최종 답변이 나오는지(thinking 끔/켬 2건)
  schema  JSON 스키마 응답(response_format json_schema strict) — 비스트리밍/스트리밍 × (스키마 준수, 기대값) 4건.
          스키마 준수는 타입·필수·추가 필드 금지·배열 원소·최소 개수·패턴과 finish_reason stop·스트림 [DONE]을 검사한다
  image   같은 이미지 반복 — 순차 3건 + 동시 3건, 정답 5(test_vllm_server.py 9.1과 같은 사진). 응답의 숫자가 5 하나뿐이거나
          숫자 없이 '다섯'이면 정답('15'는 오답)
  long    긴 입력 — 앞쪽에 넣은 확인 코드를 찾고, 실제 입력 토큰이 목표의 0.9~1.05배인지 본다.
          --long-tokens 0이면 '건너뜀'으로 기록한다(컨텍스트가 짧은 설정). 건너뜀은 실패로 세지 않는다
  greedy  greedy 요청 20건이 모두 응답했는지(요청 실패·예외는 여기서 세고 빈 답변·대조에서 뺀다)
  empty   응답한 greedy 중 빈 답변이 없는지
기록 항목 (판정 아님):
  greedy  고정 프롬프트 20개를 temperature 0으로 생성한 출력. --compare가 옛·새 일치율과 유사도를 낸다

사용 (표준 라이브러리만 사용):
    python tests/ab_regression_probe.py --base-url http://127.0.0.1:7090 --out new.json --long-tokens 60000
    python tests/ab_regression_probe.py --compare old.json new.json
"""
import argparse
import base64
import difflib
import json
import os
import re
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime

GREEDY_PROMPTS = [
    "대한민국의 수도와 그 도시의 대표적인 궁궐 두 곳을 한 문장으로 알려 주세요.",
    "다음 문장을 영어로 번역하세요: 회의는 다음 주 화요일 오후 3시로 연기되었습니다.",
    "다음 영어 문장을 자연스러운 한국어로 옮기세요: The quarterly report must be submitted by Friday.",
    "17 곱하기 23은 얼마인지 계산 과정을 한 줄로 보여 주세요.",
    "2026년 3월 1일이 무슨 요일인지 근거와 함께 짧게 답하세요.",
    "파이썬으로 리스트에서 중복을 제거하되 순서를 유지하는 함수를 작성하세요.",
    "SQL로 orders 테이블에서 고객별 주문 금액 합계 상위 5명을 구하는 쿼리를 작성하세요.",
    "다음 글을 두 문장으로 요약하세요: 발효 식품은 미생물의 작용으로 맛과 영양이 바뀐 식품이다. 김치, 된장, 간장이 대표적이며 지역과 기후에 따라 담그는 방식이 다르다. 최근에는 장 건강과 관련한 연구가 늘고 있다.",
    "엑셀에서 A열의 값이 100 이상인 행의 B열 합계를 구하는 수식을 알려 주세요.",
    "출장 보고서의 기본 구성 항목을 순서대로 5개 나열하세요.",
    "고객 문의에 대한 사과 안내문의 첫 문단을 3문장으로 작성하세요. 배송이 이틀 지연된 상황입니다.",
    "피보나치 수열의 처음 10개 항을 쉼표로 구분해 쓰세요.",
    "다음 단어들을 가나다순으로 정렬하세요: 사과, 바나나, 가지, 다래, 마늘, 나물",
    "HTTP 상태 코드 400, 401, 403, 404, 429의 의미를 각각 한 줄로 설명하세요.",
    "다음 JSON에서 total 값을 계산해 숫자만 답하세요: {\"items\": [{\"price\": 1200, \"qty\": 3}, {\"price\": 450, \"qty\": 4}]}",
    "정규 표현식으로 한국 휴대전화 번호(010-1234-5678 형식)를 검사하는 패턴을 쓰고 한 줄로 설명하세요.",
    "다음 날짜를 ISO 8601 형식으로 바꾸세요: 2026년 10월 9일 오전 9시 30분 (한국 시간)",
    "연차 휴가 신청 메일을 3줄로 작성하세요. 10월 20일부터 22일까지 3일입니다.",
    "1부터 100까지 자연수 중 3의 배수이면서 5의 배수인 수의 개수를 구하세요.",
    "다음 목록을 마크다운 표로 바꾸세요: 서울 9.4백만, 부산 3.3백만, 인천 3.0백만",
]

COPY_CASES = [   # (라벨, 값) — 값만 대조한다(모델이 라벨을 빼고 값만 적어도 정답)
    ("사번", "A-20391-K"),
    ("내선 번호", "0042-7781"),
    ("금액", "1,250,000원"),
    ("코드", "QX7-PL0-09Z"),
    ("좌표", "(37.5665, 126.9780)"),
]

TOOL_LABEL = "분기(Q3) 매출[억원]"
TOOL_VALUES = [12.5, -3, 1000000, 0.0042]
TOOL_EXPR = "(12.5 + 3) * [4, 5] / {2}"
TOOLS = [{
    "type": "function",
    "function": {
        "name": "record_values",
        "description": "라벨, 숫자 값 목록, 계산식을 그대로 기록한다.",
        "parameters": {
            "type": "object",
            "properties": {
                "label": {"type": "string", "description": "라벨 원문"},
                "values": {"type": "array", "items": {"type": "number"}, "description": "숫자 값 목록"},
                "expression": {"type": "string", "description": "계산식 원문"},
            },
            "required": ["label", "values", "expression"],
        },
    },
}]
TOOL_PROMPT = (
    "record_values 도구를 호출해 아래 내용을 원문 그대로 기록해 주세요.\n"
    f"라벨: {TOOL_LABEL}\n값: 12.5, -3, 1000000, 0.0042\n식: {TOOL_EXPR}"
)

SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "tags": {"type": "array", "items": {"type": "string"}, "minItems": 2},
        "address": {
            "type": "object",
            "properties": {"city": {"type": "string"}, "zip": {"type": "string", "pattern": "^[0-9]{5}$"}},
            "required": ["city", "zip"],
            "additionalProperties": False,
        },
    },
    "required": ["name", "age", "tags", "address"],
    "additionalProperties": False,
}
SCHEMA_PROMPT = "다음 인물 정보를 JSON으로 정리하세요: 이름 홍길동, 나이 37세, 관심사 등산과 사진, 주소 서울 종로구(우편번호 03154)."

IMAGE_PROMPT = "사진에 강아지가 몇 마리 있나요? 숫자만 답해주세요."
LONG_CODE = "QX-4729-LM"
LONG_UNIT = ("지역별 기후 자료에 따르면 연평균 기온과 강수량은 해마다 조금씩 달라지며, 농작물의 파종 시기와 "
             "수확량도 그에 따라 바뀐다. 발효 식품을 담그는 시기 역시 기온의 영향을 크게 받는다. ")


# ── HTTP ─────────────────────────────────────────────────────────────
def _post(url: str, body: dict, timeout: float) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:300]


def _post_stream(url: str, body: dict, timeout: float) -> tuple[int, dict | str]:
    """SSE 응답을 비스트리밍 응답과 같은 모양(message, finish_reason, usage)으로 합친다."""
    req = urllib.request.Request(url, data=json.dumps({**body, "stream": True, "stream_options": {"include_usage": True}}).encode(),
                                 headers={"Content-Type": "application/json"})
    content, reasoning, calls, finish, usage, done = [], [], {}, None, None, False
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            for raw in resp:
                line = raw.decode().strip()
                if line == "data: [DONE]":
                    done = True
                    continue
                if not line.startswith("data:"):
                    continue
                chunk = json.loads(line[5:])
                usage = chunk.get("usage") or usage
                for ch in chunk.get("choices", []):
                    d = ch.get("delta", {})
                    content.append(d.get("content") or "")
                    reasoning.append(d.get("reasoning") or d.get("reasoning_content") or "")
                    for tc in d.get("tool_calls") or []:
                        slot = calls.setdefault(tc.get("index", 0), {"id": "", "type": "", "name": "", "arguments": ""})
                        slot["id"] = slot["id"] or tc.get("id") or ""
                        slot["type"] = slot["type"] or tc.get("type") or ""
                        fn = tc.get("function") or {}
                        slot["name"] += fn.get("name") or ""
                        slot["arguments"] += fn.get("arguments") or ""
                    finish = ch.get("finish_reason") or finish
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:300]
    msg = {"content": "".join(content), "reasoning": "".join(reasoning),
           "tool_calls": [{"id": c["id"], "type": c["type"], "function": {"name": c["name"], "arguments": c["arguments"]}}
                          for c in (calls[i] for i in sorted(calls))]}
    return 200, {"choices": [{"message": msg, "finish_reason": finish}], "usage": usage, "stream_done": done}


class Client:
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")
        with urllib.request.urlopen(f"{self.base}/v1/models", timeout=15) as resp:
            self.model = json.loads(resp.read())["data"][0]["id"]

    def chat(self, messages: list[dict], *, stream: bool = False, timeout: float = 300, **extra) -> tuple[int, dict | str]:
        body = {"model": self.model, "messages": messages, **extra}
        fn = _post_stream if stream else _post
        return fn(f"{self.base}/v1/chat/completions", body, timeout)

    def version(self) -> str:
        try:
            with urllib.request.urlopen(f"{self.base}/version", timeout=15) as resp:
                return json.loads(resp.read()).get("version", "")
        except (urllib.error.URLError, ValueError):
            return "조회 실패"


def _msg(body: dict) -> dict:
    return body["choices"][0]["message"]


def _reasoning_len(m: dict) -> int:
    return len(m.get("reasoning") or m.get("reasoning_content") or "")


# ── 판정 항목 ─────────────────────────────────────────────────────────
def check_copy(cli: Client) -> list[dict]:
    out = []
    for label, value in COPY_CASES:
        st, body = cli.chat([{"role": "user", "content": f"다음 값을 설명 없이 원문 그대로 한 번만 적으세요: {label} {value}"}],
                            max_tokens=64, temperature=0)
        content = _msg(body)["content"] if st == 200 else ""
        ok = st == 200 and value in content
        out.append({"item": "copy", "case": label, "ok": ok, "detail": f"HTTP {st} · {str(content or body)[:80]!r}"})
    return out


TOOL_MARKUP = ("<tool_call", "tool_call>", "<|tool_call", "call:record_values", "<function=")   # 파서가 못 걷어 낸 호출 표식


def _judge_tool(st: int, body, stream: bool) -> tuple[bool, str]:
    if st != 200:
        return False, f"HTTP {st} {str(body)[:120]}"
    m = _msg(body)
    calls = m.get("tool_calls") or []
    if not calls:
        return False, f"도구 호출 없음 · 본문 {str(m.get('content'))[:80]!r}"
    call = calls[0]
    fn = call["function"]
    try:
        args = json.loads(fn["arguments"])
    except (json.JSONDecodeError, TypeError) as e:
        return False, f"인자 JSON 파싱 실패({e}) · {str(fn.get('arguments'))[:100]!r}"
    if not isinstance(args, dict):
        return False, f"인자가 객체가 아님 · {str(fn.get('arguments'))[:100]!r}"
    vals = args.get("values")
    vals_ok = (isinstance(vals, list) and len(vals) == len(TOOL_VALUES)
               and all(isinstance(v, (int, float)) and not isinstance(v, bool) and abs(v - w) < 1e-9
                       for v, w in zip(vals, TOOL_VALUES)))
    expr_ok = str(args.get("expression", "")).replace(" ", "") == TOOL_EXPR.replace(" ", "")
    finish = body["choices"][0].get("finish_reason")
    leak = [k for k in TOOL_MARKUP if k in (m.get("content") or "")]
    problems = [name for name, bad in (
        ("호출 수≠1", len(calls) != 1),
        ("이름", fn["name"] != "record_values"),
        ("라벨", args.get("label") != TOOL_LABEL),
        ("값", not vals_ok),
        ("식", not expr_ok),
        ("id 없음", not (isinstance(call.get("id"), str) and call["id"])),
        ("type≠function", call.get("type") != "function"),
        (f"finish {finish}", finish != "tool_calls"),
        (f"본문 표식 누출 {leak}", bool(leak)),
        ("[DONE] 없음", stream and not body.get("stream_done")),
    ) if bad]
    detail = (f"{'문제 ' + ', '.join(problems) + ' · ' if problems else ''}이름 {fn['name']} · "
              f"인자 {json.dumps(args, ensure_ascii=False)[:150]} · finish {finish} · 사고 {_reasoning_len(m)}자")
    return not problems, detail


def _tool_followup(cli: Client, thinking: bool, first: dict) -> dict:
    """비스트리밍 호출을 이어 받아 도구 결과를 돌려주고, 도구를 다시 부르지 않는 최종 답변이 나오는지 본다."""
    case = f"thinking {'켬' if thinking else '끔'}"
    call = _msg(first)["tool_calls"][0]
    msgs = [{"role": "user", "content": TOOL_PROMPT},
            {"role": "assistant", "content": None,
             "tool_calls": [{"id": call["id"], "type": "function",
                             "function": {"name": call["function"]["name"], "arguments": call["function"]["arguments"]}}]},
            {"role": "tool", "tool_call_id": call["id"], "content": json.dumps({"saved": len(TOOL_VALUES)})}]
    st, body = cli.chat(msgs, tools=TOOLS, tool_choice="auto", max_tokens=4096 if thinking else 512, temperature=0,
                        chat_template_kwargs={"enable_thinking": thinking})
    if st != 200:
        return {"item": "tool-followup", "case": case, "ok": False, "detail": f"HTTP {st} {str(body)[:120]}"}
    m = _msg(body)
    finish = body["choices"][0].get("finish_reason")
    content = (m.get("content") or "").strip()
    ok = finish == "stop" and bool(content) and not m.get("tool_calls")
    return {"item": "tool-followup", "case": case, "ok": ok,
            "detail": f"finish {finish} · 호출 {len(m.get('tool_calls') or [])}건 · {' '.join(content.split())[:80]!r}"}


def check_tool(cli: Client) -> list[dict]:
    out = []
    for thinking in (False, True):
        for stream in (False, True):
            st, body = cli.chat([{"role": "user", "content": TOOL_PROMPT}], stream=stream, tools=TOOLS, tool_choice="auto",
                                max_tokens=4096 if thinking else 512, temperature=0,
                                chat_template_kwargs={"enable_thinking": thinking})
            ok, detail = _judge_tool(st, body, stream)
            out.append({"item": "tool", "case": f"thinking {'켬' if thinking else '끔'} · {'스트리밍' if stream else '비스트리밍'}",
                        "ok": ok, "detail": detail})
            if not stream:
                if ok:
                    out.append(_tool_followup(cli, thinking, body))
                else:
                    out.append({"item": "tool-followup", "case": f"thinking {'켬' if thinking else '끔'}", "ok": False,
                                "detail": "첫 호출 실패로 진행 못 함"})
    return out


_JSON_TYPES = {"object": dict, "array": list, "string": str, "number": (int, float), "integer": int, "boolean": bool}


def _schema_errors(v, s: dict, path: str = "$") -> list[str]:
    """SCHEMA가 쓰는 키워드(type·properties·required·additionalProperties·items·minItems·pattern)만 검사한다."""
    t = s.get("type")
    if t and (not isinstance(v, _JSON_TYPES[t]) or (isinstance(v, bool) and t != "boolean")):
        return [f"{path} 타입 {type(v).__name__}≠{t}"]
    errs = []
    if t == "object":
        props = s.get("properties", {})
        errs += [f"{path}.{k} 누락" for k in s.get("required", []) if k not in v]
        if s.get("additionalProperties") is False:
            errs += [f"{path}.{k} 추가 필드" for k in v if k not in props]
        for k, sub in props.items():
            if k in v:
                errs += _schema_errors(v[k], sub, f"{path}.{k}")
    elif t == "array":
        if len(v) < s.get("minItems", 0):
            errs.append(f"{path} 원소 {len(v)}개<{s['minItems']}")
        for i, x in enumerate(v):
            errs += _schema_errors(x, s.get("items", {}), f"{path}[{i}]")
    elif t == "string" and "pattern" in s and not re.search(s["pattern"], v):
        errs.append(f"{path} 패턴 불일치 {v!r}")
    return errs


def check_schema(cli: Client) -> list[dict]:
    out = []
    rf = {"type": "json_schema", "json_schema": {"name": "person", "schema": SCHEMA, "strict": True}}
    for stream in (False, True):
        mode = "스트리밍" if stream else "비스트리밍"
        st, body = cli.chat([{"role": "user", "content": SCHEMA_PROMPT}], stream=stream, response_format=rf,
                            max_tokens=512, temperature=0)
        if st != 200:
            out += [{"item": "schema", "case": f"{mode} · {k}", "ok": False, "detail": f"HTTP {st} {str(body)[:120]}"}
                    for k in ("스키마 준수", "기대값")]
            continue
        content = _msg(body)["content"] or ""
        finish = body["choices"][0].get("finish_reason")
        try:
            d = json.loads(content)
        except json.JSONDecodeError as e:
            out += [{"item": "schema", "case": f"{mode} · {k}", "ok": False,
                     "detail": f"JSON 파싱 실패({e}) · finish {finish} · {content[:120]!r}"} for k in ("스키마 준수", "기대값")]
            continue
        errs = _schema_errors(d, SCHEMA)
        # 내용이 맞아도 비정상 종료(길이 초과·중단)거나 스트림이 [DONE] 없이 끝나면 실패로 둔다
        if finish != "stop":
            errs.append(f"finish {finish}")
        if stream and not body.get("stream_done"):
            errs.append("[DONE] 없음")
        out.append({"item": "schema", "case": f"{mode} · 스키마 준수", "ok": not errs,
                    "detail": "; ".join(errs)[:160] if errs else " ".join(content.split())[:160]})
        if not isinstance(d, dict):   # 최상위가 객체가 아니면 기대값을 볼 수 없다(예외로 결과를 잃지 않게)
            out.append({"item": "schema", "case": f"{mode} · 기대값", "ok": False, "detail": f"최상위 {type(d).__name__}"})
            continue
        # 기대값은 스키마를 지킨 경우에만 의미가 있다(타입이 틀리면 값 비교도 실패로 둔다)
        val_ok = (not errs and d["name"] == "홍길동" and d["age"] == 37
                  and any("등산" in x for x in d["tags"]) and any("사진" in x for x in d["tags"])
                  and "서울" in d["address"]["city"] and d["address"]["zip"] == "03154")
        out.append({"item": "schema", "case": f"{mode} · 기대값", "ok": val_ok,
                    "detail": f"name {d.get('name')!r} · age {d.get('age')!r} · tags {d.get('tags')!r} · address {d.get('address')!r}"[:160]})
    return out


def check_image(cli: Client) -> list[dict]:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image.png")
    with open(path, "rb") as f:
        url = "data:image/png;base64," + base64.b64encode(f.read()).decode()
    msgs = [{"role": "user", "content": [{"type": "text", "text": IMAGE_PROMPT}, {"type": "image_url", "image_url": {"url": url}}]}]

    def one() -> tuple[bool, str]:
        st, body = cli.chat(msgs, max_tokens=100, temperature=0, timeout=120)
        content = (_msg(body)["content"] or "") if st == 200 else str(body)
        nums = re.findall(r"\d+", content)
        ok = st == 200 and (nums == ["5"] or (not nums and "다섯" in content))
        return ok, f"HTTP {st} · {content[:40]!r}"

    out = [{"item": "image", "case": f"순차 {i + 1}", "ok": ok, "detail": d} for i, (ok, d) in enumerate(one() for _ in range(3))]
    res: list[tuple[bool, str]] = [(False, "미실행")] * 3

    def run(i: int) -> None:
        res[i] = one()
    ths = [threading.Thread(target=run, args=(i,)) for i in range(3)]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    out += [{"item": "image", "case": f"동시 {i + 1}", "ok": ok, "detail": d} for i, (ok, d) in enumerate(res)]
    return out


def check_long(cli: Client, target_tokens: int) -> list[dict]:
    # 단위 문단의 토큰 수를 서버 토크나이저로 재고(usage.prompt_tokens), 목표 길이에 맞춰 문단 수를 정한다
    def build(n: int) -> str:
        units = [f"[{i}] {LONG_UNIT}" for i in range(n)]
        units.insert(max(1, n // 50), f"참고: 이번 점검의 확인 코드는 {LONG_CODE} 입니다.")
        return "\n".join(units) + "\n\n위 자료에서 확인 코드를 찾아 코드만 그대로 적으세요."

    st, body = cli.chat([{"role": "user", "content": build(100)}], max_tokens=1, temperature=0)
    if st != 200:
        return [{"item": "long", "case": "보정", "ok": False, "detail": f"HTTP {st} {str(body)[:120]}"}]
    per_unit = body["usage"]["prompt_tokens"] / 100
    n = int((target_tokens - 200) / per_unit)
    t0 = time.time()
    st, body = cli.chat([{"role": "user", "content": build(n)}], max_tokens=32, temperature=0, timeout=900)
    if st != 200:
        return [{"item": "long", "case": f"목표 {target_tokens}토큰", "ok": False, "detail": f"HTTP {st} {str(body)[:160]}"}]
    content = _msg(body)["content"] or ""
    got = body["usage"]["prompt_tokens"]
    in_range = 0.9 * target_tokens <= got <= 1.05 * target_tokens
    ok = LONG_CODE in content and in_range
    return [{"item": "long", "case": f"목표 {target_tokens}토큰", "ok": ok,
             "detail": f"{'' if in_range else '입력 길이가 목표의 0.9~1.05배 밖 · '}입력 {got}토큰 · "
                       f"{time.time() - t0:.1f}초 · {content[:40]!r}"}]


def run_greedy(cli: Client) -> list[dict]:
    """요청마다 결과를 남긴다. 요청 실패·예상 밖 응답은 "error"에 적고 계속한다(빈 답변 판정과 섞지 않는다)."""
    out = []
    for i, p in enumerate(GREEDY_PROMPTS, 1):
        try:
            st, body = cli.chat([{"role": "user", "content": p}], max_tokens=256, temperature=0)
            if st != 200:
                raise RuntimeError(f"HTTP {st}")
            out.append({"id": i, "content": _msg(body)["content"] or "", "finish": body["choices"][0]["finish_reason"],
                        "tokens": body["usage"]["completion_tokens"]})
        except Exception as e:  # noqa: BLE001
            out.append({"id": i, "content": "", "finish": None, "tokens": 0, "error": f"{type(e).__name__}: {str(e)[:120]}"})
    return out


# ── 대조 ─────────────────────────────────────────────────────────────
def compare(old_path: str, new_path: str) -> int:
    with open(old_path, encoding="utf-8") as f:
        old = json.load(f)
    with open(new_path, encoding="utf-8") as f:
        new = json.load(f)
    print(f"옛 {old['meta']['version']} ({old['meta']['time']}) ↔ 새 {new['meta']['version']} ({new['meta']['time']})")
    og, ng = {g["id"]: g for g in old["greedy"]}, {g["id"]: g for g in new["greedy"]}
    errs = sorted(i for i in og.keys() | ng.keys() if og.get(i, {}).get("error") or ng.get(i, {}).get("error"))
    if errs:
        print(f"greedy 요청 실패로 대조에서 뺀 번호: {errs}")
    og = {i: g for i, g in og.items() if i not in errs}
    ng = {i: g for i, g in ng.items() if i not in errs}
    ratios = []
    for i in sorted(og.keys() & ng.keys()):
        r = difflib.SequenceMatcher(None, og[i]["content"], ng[i]["content"]).ratio()
        ratios.append((r, i))
    same = sum(1 for r, _ in ratios if r == 1.0)
    if ratios:
        print(f"greedy {len(ratios)}건: 완전 일치 {same}건 · 유사도 중앙값 {statistics.median(r for r, _ in ratios):.3f} · 최저 {min(ratios)[0]:.3f}")
    else:
        # 유효 쌍 0개: 품질 대조는 할 수 없지만 판정 항목 표는 계속 출력한다(코덱스 4라운드 Q5)
        print("greedy 대조 불가: 양쪽 모두 응답한 번호가 없음")
    for r, i in sorted(ratios)[:5]:
        if r < 1.0:
            print(f"  #{i} 유사도 {r:.3f} · 옛 {og[i]['tokens']}토큰 {og[i]['finish']} / 새 {ng[i]['tokens']}토큰 {ng[i]['finish']}")
            print(f"     옛: {og[i]['content'][:90]!r}\n     새: {ng[i]['content'][:90]!r}")
    print("판정 항목 (옛 → 새):")
    oc = {(c["item"], c["case"]): c["ok"] for c in old["checks"]}
    for c in new["checks"]:
        before = oc.get((c["item"], c["case"]), "없음")
        mark = "회귀" if before is True and c["ok"] is False else ("해소" if before is False and c["ok"] is True else "")
        print(f"  {c['item']:13} {c['case']:24} {_mark(before)} → {_mark(c['ok'])} {mark}")
    return 0


def _mark(ok) -> str:
    return {True: "✅", False: "❌", None: "⏭️"}.get(ok, "—")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", default="http://127.0.0.1:7090", help="vLLM 백엔드 URL (직접 호출)")
    ap.add_argument("--out", help="결과 JSON 경로")
    ap.add_argument("--long-tokens", type=int, default=0, help="긴 입력 목표 토큰 수. 0이면 건너뜀(max_model_len보다 작게)")
    ap.add_argument("--compare", nargs=2, metavar=("OLD", "NEW"), help="두 결과 파일 대조")
    a = ap.parse_args()
    if a.compare:
        return compare(*a.compare)
    if not a.out:
        ap.error("--out이 필요합니다")
    cli = Client(a.base_url)
    meta = {"base_url": a.base_url, "model": cli.model, "version": cli.version(), "time": datetime.now().isoformat(timespec="seconds")}
    print(f"[{meta['time']}] {meta['base_url']} · 모델 {meta['model']} · vLLM {meta['version']}")
    greedy = run_greedy(cli)
    checks: list[dict] = []
    groups = [("copy", check_copy), ("tool", check_tool), ("schema", check_schema), ("image", check_image)]
    if a.long_tokens > 0:
        groups.append(("long", lambda c: check_long(c, a.long_tokens)))
    else:
        checks.append({"item": "long", "case": "건너뜀", "ok": None, "detail": "--long-tokens 0 (max_model_len이 짧은 설정)"})
    for name, fn in groups:
        # 탐침 자체의 예외(예상 못 한 응답 모양)는 서버 결함과 구분해 기록하고 나머지 항목을 계속한다
        try:
            checks += fn(cli)
        except Exception as e:  # noqa: BLE001
            checks.append({"item": name, "case": "탐침 오류", "ok": False, "probe_error": True,
                           "detail": f"{type(e).__name__}: {str(e)[:140]}"})
    gerr = [g["id"] for g in greedy if g.get("error")]
    checks.append({"item": "greedy", "case": f"요청 {len(greedy)}건", "ok": not gerr,
                   "detail": f"요청 실패 {gerr} {greedy[gerr[0] - 1]['error']}" if gerr else "모두 응답"})
    empty = [g["id"] for g in greedy if not g.get("error") and not g["content"].strip()]
    # case 이름은 3판과 같게 둬 --compare가 판본을 넘어 짝을 맞추게 한다
    checks.append({"item": "empty", "case": "greedy 20건", "ok": not empty,
                   "detail": f"응답 {len(greedy) - len(gerr)}건 중 빈 답변 {empty or '없음'}"})
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "greedy": greedy, "checks": checks}, f, ensure_ascii=False, indent=1)
    for c in checks:
        print(f"{_mark(c['ok'])} {c['item']:13} {c['case']:24} {c['detail']}")
    fails = sum(1 for c in checks if c["ok"] is False)
    skips = sum(1 for c in checks if c["ok"] is None)
    perr = sum(1 for c in checks if c.get("probe_error"))
    print(f"결과: {'✅ 전부 통과' if not fails else f'❌ {fails}건 실패'} ({len(checks)}건, 건너뜀 {skips}"
          f"{f', 탐침 오류 {perr}' if perr else ''}) · 저장 {a.out}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
