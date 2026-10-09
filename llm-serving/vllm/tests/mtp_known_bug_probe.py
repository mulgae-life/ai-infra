#!/usr/bin/env python3
"""알려진 MTP(추측 디코딩) 결함 재현 탐침 — vLLM 버전업 때 상류에 보고된 결함이 우리 설정에서 나오는지 본다.

추측 디코딩은 설계상 본 모델의 출력 분포를 바꾸지 않는다. 그래서 품질 결함은 문법·파서 경계나 캐시 공유 같은
구현 결함에서 나온다. 이 탐침은 그런 결함 중 운영 Gemma 설정과 겹치는 두 가지를 축소 조건으로 보낸다.
상류 보고와 모델 양자화·입력 양식·길이·GPU가 다르므로, 미검출은 "이 축소 조건에서 안 나옴"까지만 뜻한다.

모드
  grammar  추론 켬 + 추측 디코딩에서 추론 끝 경계 뒤의 출력 (상류 #38106·#43691, 수정 #44297)
           종류 넷을 각 --n건 보낸다. 샘플링은 #43691 재현 요청과 같다(temperature 1.0·top_p 0.95·top_k 20·
           presence_penalty 1.5). 종류별로 따로 집계·판정한다.
           schema, schema-stream  response_format json_schema strict. 새·옛 vLLM 모두 구조화 출력 문법이 걸리는
                                  경로라 문법 경계 검사로 쓴다. 문법이 걸리면 스키마를 벗어날 수 없으므로
                                  JSON 깨짐·스키마 위반·비정상 종료·스트림 미완료·5xx는 증상이다.
           required, required-stream  tool_choice="required". 0.31의 gemma4 파서는 이 경로에서 문법을 걸지 않고
                                  모델 고유 호출 구문을 파싱한다(Gemma4EngineToolParser.adjust_request). 옛 nightly는
                                  도구 스키마로 JSON 문법을 건다. 그래서 이 종류는 버전마다 경로가 다르며
                                  "도구 호출 계약" 검사로만 쓴다: 호출 없음·이름·인자 JSON·id·type·finish·호출 표식
                                  누출·스트림 미완료·5xx는 증상, 인자 스키마 불일치(열거값 밖 등)는 품질로 따로 센다.
           길이 초과(finish length)는 평가에서 빼되, 스트림이면 [DONE] 여부는 따로 본다.
  mix      긴 요청과 짧은 요청을 섞는다 (상류 #46088: Gemma4 + MTP + KV auto에서 짧은 요청이 첫 토큰부터 깨지고
           다른 요청의 도구 스키마가 섞여 나옴. KV fp8에서는 없었다고 보고. 독립 재현 확인 없음)
           짧은 요청을 혼자 보낸 greedy 답 3회를 기준으로 삼는다. 기준은 정상 종료·도구 호출 없음·표식 없음·
           정답 4여야 하고, 아니면 "단독 조건 품질 이상"(ref_anomaly)으로 무효 처리하고 따로 보고한다.
           긴 요청은 회차마다 앞머리 태그를 바꿔 접두 캐시를 피한다. 태그는 --seed와 회차 번호로 정해지고 반복 수는
           --long-k로 고정할 수 있어, 같은 seed·k면 MTP 켬·끔·판본이 같은 입력을 쓴다. 짧은 요청 절반은 긴 요청보다
           먼저, 나머지는 0.4초 뒤에 보낸다. 요청마다 시작·끝 시각을 남겨 긴 요청과 시간이 겹친 짧은 요청 수를 센다
           (같은 스케줄링 단계에 함께 있었는지는 입증하지 못한다). 서버의 max_num_batched_tokens가 긴 요청보다
           작아야 긴 prefill이 여러 조각으로 나뉜다.
           강한 표식(특수 구분자·대체 문자·도구 스키마 JSON 조각·연속 반복, 도구 호출, 빈 답)은 증상 후보,
           약한 표식(parameters·properties·tool_·thought 같은 낱말, 길이 초과 종료)만 있으면 "검토"로 따로 센다.
           표식 없이 기준과만 다르면 "차이"(예: four, 44)다. 증상 후보는 사람이 원문을 보고 확정한다.

MTP 동작 확인 (--mtp)
  본 측정 구간 직전·직후에 /metrics를 읽는다. 둘 다 vllm: 지표가 있는 정상 응답이어야 하고, 값이 유한·비음수이며
  초안·수락 누적값이 줄지 않아야 한다. on은 초안 토큰이 늘어야, off는 초안 지표가 없거나 늘지 않아야 유효하다.
  proc_start는 지표를 내는 프로세스의 process_start_time이 양쪽에 있고 같을 때만 "same", 아니면 "unknown"이다.
  이 값은 EngineCore의 수명 식별자가 아니라 잠정값이며, same이든 unknown이든 기동 로그 구간 검사로 재시작·엔진 오류가
  없음을 확인해야 최종 유효로 확정한다.

판정 (종료 코드, 마지막 줄 "RESULT valid=… symptoms=… quality=… review=… ref_anomaly=… ref_review=… proc_start=… code=…")
  0  유효 + 증상 0          1  유효 + 증상 있음 (원문은 --out JSON에 남는다)
  2  무효 — 요청 실패(연결·4xx), 종류별 길이 초과 20% 초과, 종류별 추론 노출 절반 미만, 기준 답 이상·불안정,
     시간 겹침 절반 미만, MTP 지표 조건 불충족, 탐침 예외. 무효여도 증상 수는 RESULT 줄과 JSON에 그대로 남긴다
  143 TERM으로 중단 — 그때까지 받은 결과를 --out에 쓰고 끝낸다
  응답 원문: 스트리밍은 공유 클라이언트(ab_regression_probe._post_stream)가 조각을 합친 합성 응답이고 조각 자체는
  남지 않는다. HTTP 오류 본문은 300자에서 잘린다.

사용 (표준 라이브러리만 사용)
    python tests/mtp_known_bug_probe.py grammar --base-url http://127.0.0.1:7090 --n 40 --mtp on --out g.json
    python tests/mtp_known_bug_probe.py mix --base-url http://127.0.0.1:7090 --long-tokens 3000 --rounds 20 --mtp on --out m.json
    python tests/mtp_known_bug_probe.py self-test     # 서버 없이 판정 함수 반례 시험
"""
import argparse
import json
import math
import os
import re
import signal
import sys
import threading
import time
import traceback
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ab_regression_probe import Client, _schema_errors  # noqa: E402  (같은 폴더의 A/B 탐침과 요청·스키마 검사를 공유)

T0 = time.monotonic()
SINK_LOCK = threading.Lock()
JUDGE_ERRORS = (KeyError, IndexError, TypeError, AttributeError, ValueError)


def _now() -> float:
    return round(time.monotonic() - T0, 3)


def _record(kind: str, req: dict, call) -> dict:
    """요청 하나를 보내고 시각·요청·응답 원문을 남긴다. 예외는 무효 기록으로 바꾸고 추적 문자열을 보존한다."""
    rec = {"kind": kind, "request": req, "t_start": _now()}
    try:
        st, body = call()
        rec.update(status=st, response=body if isinstance(body, dict) else str(body)[:2000])
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError, json.JSONDecodeError, KeyError, IndexError) as e:
        rec.update(status=0, response=None, error=f"{type(e).__name__}: {e}"[:500], tb=traceback.format_exc()[-1500:])
    rec["t_end"] = _now()
    return rec


def _msg_fields(body: dict) -> tuple[dict, str | None]:
    ch = body["choices"][0]
    return ch["message"], ch.get("finish_reason")


def _reasoning(m: dict) -> str:
    return m.get("reasoning") or m.get("reasoning_content") or ""


# ── grammar 모드 ──────────────────────────────────────────────────────
TICKET_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": ["배송", "결제", "환불", "계정", "기타"]},
        "urgency": {"type": "string", "enum": ["낮음", "보통", "높음"]},
        "reason": {"type": "string"},
    },
    "required": ["category", "urgency", "reason"],
    "additionalProperties": False,
}
TOOL_NAME = "classify_ticket"
TOOLS_G = [{"type": "function", "function": {
    "name": TOOL_NAME, "description": "고객 문의를 분류해 기록한다.", "parameters": TICKET_SCHEMA}}]
TICKETS = [
    "주문한 지 열흘이 지났는데 배송 조회가 아직 '상품 준비 중'입니다. 다음 주 월요일 행사에 써야 해서 급합니다.",
    "카드로 결제했는데 같은 금액이 두 번 빠져나갔습니다. 하나는 취소해 주세요.",
    "받은 신발 사이즈가 주문과 달라 반품했는데 2주째 환불이 안 들어왔습니다.",
    "비밀번호를 바꾼 뒤로 로그인이 안 되고, 인증 메일도 오지 않습니다.",
    "포장 상자가 찌그러져 왔지만 내용물은 멀쩡합니다. 참고로 알려 드립니다.",
    "쿠폰을 적용했는데 결제 금액에 할인이 반영되지 않았습니다. 이미 결제는 끝났어요.",
]
G_PROMPT = "다음 고객 문의를 읽고, 분류 기준을 충분히 따져 본 뒤 {how}\n문의: {t}"
G_HOW = {"schema": "지정한 JSON 형식으로만 답하세요.", "required": f"{TOOL_NAME} 도구로 기록하세요."}
G_KINDS = ("schema", "schema-stream", "required", "required-stream")
# 본문에 남으면 안 되는 Gemma 도구 호출 표식(파서가 떼어 내야 하는 것)
CALL_MARKUP = ["<|tool_call>", "<tool_call|>", "<|tool_response>", f"call:{TOOL_NAME}"]


def _ticket_errors(text) -> tuple[list[str], dict | None]:
    try:
        d = json.loads(text)
    except (json.JSONDecodeError, TypeError) as e:
        return [f"JSON 파싱 실패({e}) {str(text)[:80]!r}"], None
    if not isinstance(d, dict):
        return [f"최상위 {type(d).__name__}"], None
    errs = _schema_errors(d, TICKET_SCHEMA)
    errs += [f"$.{k} 열거값 밖 {d[k]!r}" for k, sub in TICKET_SCHEMA["properties"].items()
             if "enum" in sub and k in d and d[k] not in sub["enum"]]
    return errs, d


def judge_grammar(kind: str, st: int, body) -> dict:
    """verdict = ok | quality | symptom | truncated | invalid. kind는 G_KINDS 중 하나"""
    stream = kind.endswith("-stream")
    if not isinstance(body, dict):
        if st >= 500:
            return {"verdict": "symptom", "detail": f"HTTP {st} {str(body)[:160]}"}
        # 4xx는 본문에 grammar·fsm 낱말이 있어도 요청 문제일 수 있어 무효로 두고 원문만 남긴다
        return {"verdict": "invalid", "detail": f"HTTP {st} {str(body)[:160]}"}
    m, finish = _msg_fields(body)
    base = {"finish": finish, "reasoning_len": len(_reasoning(m))}
    if finish == "length":
        if stream and not body.get("stream_done"):   # 길이 초과여도 스트림 전송 완료는 따로 본다
            return {**base, "verdict": "symptom", "detail": "길이 초과 + [DONE] 없음"}
        return {**base, "verdict": "truncated", "detail": "길이 초과(max_tokens)"}
    content = m.get("content") or ""
    problems, quality = [], []
    if kind.startswith("schema"):
        errs, _ = _ticket_errors(content)
        problems += errs
        if finish != "stop":
            problems.append(f"finish {finish}")
    else:
        calls = m.get("tool_calls") or []
        if not calls:
            problems.append(f"도구 호출 없음 · 본문 {content[:80]!r}")
        for i, c in enumerate(calls):
            if not isinstance(c, dict):
                problems.append(f"호출{i} 객체 아님 {str(c)[:60]!r}")
                continue
            fn = c.get("function") or {}
            if fn.get("name") != TOOL_NAME:
                problems.append(f"호출{i} 이름 {fn.get('name')!r}")
            if not (isinstance(c.get("id"), str) and c["id"]):
                problems.append(f"호출{i} id 없음")
            if c.get("type") != "function":
                problems.append(f"호출{i} type {c.get('type')!r}")
            errs, d = _ticket_errors(fn.get("arguments"))
            if d is None:
                problems += [f"호출{i} {e}" for e in errs]   # 인자가 JSON 객체가 아님 = 호출 계약 위반
            else:
                quality += [f"호출{i} {e}" for e in errs]    # JSON 객체이나 스키마와 다름 = 0.31에선 문법이 없어 품질로 센다
        if calls and finish != "tool_calls":
            problems.append(f"finish {finish}")
        leak = [k for k in CALL_MARKUP if k in content]
        if leak:
            problems.append(f"본문 호출 표식 누출 {leak}")
    if stream and not body.get("stream_done"):
        problems.append("[DONE] 없음")
    if problems:
        return {**base, "verdict": "symptom", "detail": "; ".join(problems + quality)[:300]}
    if quality:
        return {**base, "verdict": "quality", "detail": "; ".join(quality)[:300]}
    return {**base, "verdict": "ok", "detail": ""}


def run_grammar(cli: Client, n: int, workers: int, max_tokens: int, sink: list) -> None:
    """결과를 받는 대로 sink에 넣는다(중간 예외·중단에도 받은 결과가 남게)"""
    jobs = [(kind, TICKETS[i % len(TICKETS)]) for kind in G_KINDS for i in range(n)]

    def one(job):
        kind, t = job
        extra = dict(max_tokens=max_tokens, temperature=1.0, top_p=0.95, top_k=20, presence_penalty=1.5,
                     chat_template_kwargs={"enable_thinking": True})
        stream = kind.endswith("-stream")
        msgs = [{"role": "user", "content": G_PROMPT.format(how=G_HOW[kind.split("-")[0]], t=t)}]
        if kind.startswith("schema"):
            extra["response_format"] = {"type": "json_schema", "json_schema": {"name": "ticket", "schema": TICKET_SCHEMA, "strict": True}}
        else:
            extra.update(tools=TOOLS_G, tool_choice="required")
        rec = _record(kind, {"messages": msgs, "stream": stream, **extra},
                      lambda: cli.chat(msgs, stream=stream, timeout=600, **extra))
        if rec["status"] == 0:
            rec.update(verdict="invalid", detail=f"요청 예외 {rec['error']}"[:300])
        else:
            try:
                rec.update(judge_grammar(kind, rec["status"], rec["response"]))
            except JUDGE_ERRORS as e:   # 응답 모양이 예상과 다름 — 원문을 남기고 무효
                rec.update(verdict="invalid", detail=f"응답 모양 이상 {type(e).__name__}: {e}"[:300])
        with SINK_LOCK:
            sink.append(rec)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(one, j) for j in jobs]
    errs = [f.exception() for f in futs if f.exception()]
    if errs:
        raise errs[0]


def summarize_grammar(res: list[dict]) -> dict:
    """종류별 집계와 유효성. 반환: {valid, symptoms, quality, review, why, lines}"""
    lines, why = [], []
    for kind in G_KINDS:
        xs = [x for x in res if x["kind"] == kind]
        if not xs:
            why.append(f"{kind} 결과 없음")
            continue
        c = {v: sum(1 for x in xs if x["verdict"] == v) for v in ("ok", "quality", "symptom", "truncated", "invalid")}
        answered = [x for x in xs if x["verdict"] in ("ok", "quality", "symptom")]
        exposed = sum(1 for x in answered if x.get("reasoning_len", 0) > 0)
        lines.append(f"[{kind}] {len(xs)}건 · 정상 {c['ok']} · 품질 {c['quality']} · 증상 {c['symptom']} · 길이 초과 {c['truncated']}"
                     f" · 무효 {c['invalid']} · 추론 노출 {exposed}/{len(answered)}")
        for x in xs:
            if x["verdict"] in ("symptom", "invalid", "quality"):
                lines.append(f"    {x['verdict']}: {x.get('detail', '')}"[:320])
        if c["invalid"]:
            why.append(f"{kind} 요청 무효 {c['invalid']}건")
        if c["truncated"] > len(xs) * 0.2:
            why.append(f"{kind} 길이 초과 {c['truncated']}/{len(xs)}(20% 초과)")
        # 추론 끝 경계를 지나야 결함 조건이 성립한다. 답한 응답의 절반 이상에 추론이 있어야 그 종류를 유효로 친다
        if exposed < len(answered) * 0.5 or not answered:
            why.append(f"{kind} 추론 노출 {exposed}/{len(answered)}(절반 미만)")
    sym = sum(1 for x in res if x["verdict"] == "symptom")
    qual = sum(1 for x in res if x["verdict"] == "quality")
    return {"valid": not why, "symptoms": sym, "quality": qual, "review": 0, "why": why, "lines": lines}


# ── mix 모드 ──────────────────────────────────────────────────────────
TOOLS_M = [{"type": "function", "function": {
    "name": f"tool_{i}", "description": f"Example tool {i}.",
    "parameters": {"type": "object", "properties": {"arg": {"type": "string"}}, "required": ["arg"]}}} for i in range(12)]
SHORT = [{"role": "user", "content": "What is 2+2? Reply with just the number."}]
STRONG_MARKS = [
    ("특수 구분자", re.compile(r'<\|"\|>|<\|[A-Za-z_]*>?|<[A-Za-z_]+\|>|<pad>')),
    ("대체 문자", re.compile("�")),
    ("도구 스키마 조각", re.compile(r'"(?:properties|parameters|required)"\s*:|\{\s*"type"\s*:\s*"object"')),
    ("연속 반복", re.compile(r"(?:thought){2,}|(\S{3,}?)\1{3,}")),
]
WEAK_WORDS = ["parameters", "properties", "tool_", "thought"]
ANSWER_RE = re.compile(r"^\s*4\s*\.?\s*$")


def build_long(k: int, tag: str = "") -> list[dict]:
    """세 턴짜리 긴 대화. k는 메시지마다 문장 반복 수(크기 조절 단위가 수십 토큰이 되게).
    tag는 맨 앞에 넣어 회차마다 접두 캐시에 걸리지 않게 한다(실제 대화처럼 매번 새로 prefill)."""
    msgs = [{"role": "system", "content": (f"[session {tag}] " if tag else "") + "You are a coding assistant."}]
    for i in range(3):
        msgs.append({"role": "user", "content": f"Step {i}: " + "consider the following code and context. " * k})
        msgs.append({"role": "assistant", "content": f"Step {i} done: " + "I reviewed and updated the implementation. " * k})
    msgs.append({"role": "user", "content": "Summarize what changed in one sentence."})
    return msgs


def short_marks(st: int, body) -> tuple[str | None, list[str], list[str], str]:
    """짧은 응답의 표식. 반환 (본문 또는 None, 강한 표식, 약한 표식, 무효 사유)"""
    if not isinstance(body, dict):
        if st >= 500:
            return None, [f"HTTP {st}"], [], ""
        return None, [], [], f"HTTP {st} {str(body)[:120]}"
    m, finish = _msg_fields(body)
    text, reason, calls = m.get("content") or "", _reasoning(m), m.get("tool_calls") or []
    both = text + "\n" + reason
    strong = [name for name, pat in STRONG_MARKS if pat.search(both)]
    if calls:
        strong.append(f"도구 호출 {len(calls)}건(누출 후보)")
    if not text.strip() and not calls:
        strong.append("빈 답")
    weak = [w for w in WEAK_WORDS if w in both]
    if finish == "length":
        weak.append("finish length")
    elif finish != "stop":
        strong.append(f"finish {finish}")
    return text, strong, weak, ""


def judge_short(ref: str, st: int, body) -> dict:
    """verdict = ok | diff | review | symptom | invalid. 강한 표식 검사를 기준 일치보다 먼저 한다"""
    text, strong, weak, inval = short_marks(st, body)
    if inval:
        return {"verdict": "invalid", "detail": inval}
    if strong:
        return {"verdict": "symptom", "text": (text or "")[:200], "detail": f"강한 표식 {strong} 약한 표식 {weak}"}
    if weak:
        return {"verdict": "review", "text": text[:200], "detail": f"약한 표식 {weak} — 원문 검토"}
    if text == ref:
        return {"verdict": "ok", "text": text}
    return {"verdict": "diff", "text": text[:200], "detail": "기준과 다르나 표식 없음"}


def check_refs(refs: list[tuple[int, object]]) -> tuple[str | None, str]:
    """단독 기준 답 3회 검사. 반환 (기준 본문 또는 None, 사유).
    사유가 '단독 조건 품질 이상'(강한 표식·정답 아님)이면 별도 보고·대조 대상, '기준 답 검토 필요'(약한 표식만)이면 원문 검토 대상"""
    texts = []
    for st, body in refs:
        text, strong, weak, inval = short_marks(st, body)
        if inval:
            return None, f"기준 요청 실패 {inval}"
        if strong or not ANSWER_RE.match(text or ""):
            return None, f"단독 조건 품질 이상: {text!r} 강한 {strong} 약한 {weak}"
        if weak:
            return None, f"기준 답 검토 필요(약한 표식만, 품질 결함으로 확정하지 않음): {text!r} 약한 {weak}"
        texts.append(text)
    if len(set(texts)) != 1:
        return None, f"기준 답 불안정 {texts!r}"
    return texts[0], ""


def run_mix(cli: Client, long_tokens: int, rounds: int, shorts: int, between, sink: list, meta: dict,
            seed: str, long_k: int | None) -> list[str]:
    """between(): 본 측정 구간 직전에 부르는 함수(MTP 지표 시작값 읽기). 결과는 sink, 준비 자료는 meta에 바로 쓴다"""
    notes = []
    meta.update(seed=seed, tools_m=TOOLS_M)
    if long_k:
        # 앞선 실행에서 정한 반복 수를 그대로 쓴다(켬·끔·판본이 같은 입력). 크기는 기록만 하고 범위는 따지지 않는다
        st, body = cli.chat(build_long(long_k, "size"), tools=TOOLS_M, tool_choice="auto", max_tokens=1, temperature=0, timeout=600)
        if st != 200:
            notes.append(f"긴 대화 크기 측정 실패 HTTP {st} {str(body)[:120]}")
            return notes
        got = body["usage"]["prompt_tokens"]
        meta.update(long_prompt_tokens=got, long_k=long_k, long_k_fixed=True)
        if not 0.85 * long_tokens <= got <= 1.0 * long_tokens:
            notes.append(f"고정 입력(k={long_k}) {got}토큰이 목표 {long_tokens}의 0.85~1.0배 밖 — 길이 조건 불충족")
            return notes
        meta["long_k_ok"] = True
        fit = long_k
    else:
        # 긴 대화 크기 맞추기: max_tokens 1 요청의 prompt_tokens로 반복 수 k를 비례 조정(최대 6번 측정)
        k, fit = 30, None   # 작게 시작해 키운다(짧은 max_model_len 설정에서 첫 측정이 길이 초과로 거절되지 않게)
        for _ in range(6):
            st, body = cli.chat(build_long(k, "size"), tools=TOOLS_M, tool_choice="auto", max_tokens=1, temperature=0, timeout=600)
            if st != 200:
                notes.append(f"긴 대화 크기 측정 실패 HTTP {st} {str(body)[:120]}")
                return notes
            got = body["usage"]["prompt_tokens"]
            meta.update(long_prompt_tokens=got, long_k=k, long_k_fixed=False)   # 마지막으로 잰 값과 그때의 k
            if 0.85 * long_tokens <= got <= 1.0 * long_tokens:
                fit = k
                meta["long_k_ok"] = True
                break
            k = max(1, int(k * long_tokens * 0.92 / got))
        if fit is None:
            notes.append(f"긴 대화 크기 {meta['long_prompt_tokens']}토큰(k={meta['long_k']})이 목표 {long_tokens}의 0.85~1.0배 밖")
            return notes
    refs, meta["ref_raw"] = [], []
    for _ in range(3):
        st, b = cli.chat(SHORT, tools=TOOLS_M, tool_choice="auto", max_tokens=24, temperature=0, timeout=120)
        refs.append((st, b))
        meta["ref_raw"].append({"status": st, "response": b if isinstance(b, dict) else str(b)[:500]})
    ref, why = check_refs(refs)
    meta["ref"] = ref
    if ref is None:
        notes.append(why)
        meta["ref_anomaly"] = why.startswith("단독 조건 품질 이상")
        meta["ref_review"] = why.startswith("기준 답 검토 필요")
        return notes

    def send(kind, r, delay, msgs):
        time.sleep(delay)
        req = {"messages": msgs, "tools": "meta.tools_m", "tool_choice": "auto", "max_tokens": 24, "temperature": 0}
        rec = _record(kind, req, lambda: cli.chat(msgs, tools=TOOLS_M, tool_choice="auto", max_tokens=24, temperature=0, timeout=600))
        rec["round"] = r
        if rec["status"] == 0:
            rec.update(verdict="invalid", detail=f"요청 예외 {rec['error']}"[:300])
        elif kind == "long":
            body = rec["response"]
            if isinstance(body, dict):
                rec.update(verdict="ok", prompt_tokens=(body.get("usage") or {}).get("prompt_tokens"))
            else:
                rec.update(verdict="symptom" if rec["status"] >= 500 else "invalid", detail=f"HTTP {rec['status']} {str(body)[:160]}")
        else:
            try:
                rec.update(judge_short(ref, rec["status"], rec["response"]))
            except JUDGE_ERRORS as e:
                rec.update(verdict="invalid", detail=f"응답 모양 이상 {type(e).__name__}: {e}"[:300])
        with SINK_LOCK:
            sink.append(rec)

    between()
    # 짧은 요청 절반은 긴 요청보다 먼저, 나머지는 0.4초 뒤에 보낸다. 긴 요청의 prefill 조각과 짧은 요청의
    # 디코딩·초안 검증이 같은 배치에 섞이는 두 순서(짧은 쪽이 먼저 돌던 중 / 긴 쪽이 먼저 돌던 중)를 노린다
    for r in range(rounds):
        long_msgs = build_long(fit, f"r{r}-{seed}")
        with ThreadPoolExecutor(max_workers=1 + shorts) as ex:
            futs = [ex.submit(send, "short", r, 0.0, SHORT) for _ in range(shorts // 2)]
            futs.append(ex.submit(send, "long", r, 0.05, long_msgs))
            futs += [ex.submit(send, "short", r, 0.4, SHORT) for _ in range(shorts - shorts // 2)]
        notes += [f"r{r} 요청 스레드 예외 {type(f.exception()).__name__}: {f.exception()}"[:200] for f in futs if f.exception()]
    return notes


def overlap_count(res: list[dict]) -> tuple[int, int]:
    """긴 요청과 시간이 겹친 짧은 요청 수 / 짧은 요청 수 (같은 회차끼리)"""
    hit = tot = 0
    for r in {x["round"] for x in res}:
        longs = [x for x in res if x["round"] == r and x["kind"] == "long"]
        for s in (x for x in res if x["round"] == r and x["kind"] == "short"):
            tot += 1
            if any(min(s["t_end"], lg["t_end"]) > max(s["t_start"], lg["t_start"]) for lg in longs):
                hit += 1
    return hit, tot


def summarize_mix(meta: dict, res: list[dict], notes: list[str], rounds: int, shorts: int) -> dict:
    lines = [f"긴 대화 약 {meta.get('long_prompt_tokens')}토큰(k={meta.get('long_k')}{' 고정' if meta.get('long_k_fixed') else ''},"
             f" seed {meta.get('seed')}) · 기준 답 {meta.get('ref')!r}"]
    sc = {v: sum(1 for x in res if x["kind"] == "short" and x["verdict"] == v) for v in ("ok", "diff", "review", "symptom", "invalid")}
    lc = {v: sum(1 for x in res if x["kind"] == "long" and x["verdict"] == v) for v in ("ok", "symptom", "invalid")}
    hit, tot = overlap_count(res)
    lp = [x.get("prompt_tokens") for x in res if x["kind"] == "long" and x.get("prompt_tokens")]
    lines.append(f"[short] {rounds}회 × {shorts}건 · 기준 일치 {sc['ok']} · 차이 {sc['diff']} · 검토 {sc['review']} · 증상 {sc['symptom']}"
                 f" · 무효 {sc['invalid']} · 긴 요청과 시간 겹침 {hit}/{tot}")
    lines.append(f"[long] {rounds}건 · 정상 {lc['ok']} · 증상 {lc['symptom']} · 무효 {lc['invalid']}"
                 f" · 실측 입력 {min(lp) if lp else '-'}~{max(lp) if lp else '-'}토큰")
    for x in sorted(res, key=lambda x: (x["round"], x["kind"], x["t_start"])):
        if x["verdict"] in ("diff", "review", "symptom", "invalid"):
            lines.append(f"    r{x['round']} {x['kind']} {x['verdict']}: {x.get('detail', '')} · {x.get('text', '')!r}"[:300])
    why = list(notes)
    if sc["invalid"] + lc["invalid"]:
        why.append(f"요청 무효 {sc['invalid'] + lc['invalid']}건")
    if res and len(res) != rounds * (1 + shorts):
        why.append(f"응답 수 {len(res)}≠{rounds * (1 + shorts)}")
    if not res and not notes:
        why.append("측정 없음")
    if tot and hit < tot * 0.5:
        why.append(f"혼합 조건 미확인: 시간 겹침 {hit}/{tot}(절반 미만)")
    return {"valid": not why, "symptoms": sc["symptom"] + lc["symptom"], "quality": sc["diff"], "review": sc["review"],
            "why": why, "lines": lines, "overlap": [hit, tot], "ref_anomaly": bool(meta.get("ref_anomaly")), "ref_review": bool(meta.get("ref_review"))}


# ── 공통: MTP 동작 확인 ───────────────────────────────────────────────
K_DRAFT = "vllm:spec_decode_num_draft_tokens_total"
K_ACC = "vllm:spec_decode_num_accepted_tokens_total"
K_START = "process_start_time_seconds"


def parse_metrics(text: str) -> dict:
    out = {"_vllm_lines": 0}
    for raw in text.splitlines():
        if raw.startswith("#"):
            continue
        if raw.startswith("vllm:"):
            out["_vllm_lines"] += 1
        for k in (K_DRAFT, K_ACC, K_START):
            if raw.startswith(k + "{") or raw.startswith(k + " "):
                v = float(raw.rsplit(" ", 1)[1])
                out[k] = out.get(k, 0.0) + v if k != K_START else v
    return out


def scrape(base: str) -> dict:
    """{'ok': bool, 'values': {...}, 'error': str}. vllm: 지표 줄이 하나도 없으면 정상 응답으로 치지 않는다"""
    try:
        with urllib.request.urlopen(f"{base.rstrip('/')}/metrics", timeout=15) as resp:
            vals = parse_metrics(resp.read().decode())
    except (urllib.error.URLError, OSError, ValueError, IndexError) as e:
        return {"ok": False, "values": {}, "error": f"{type(e).__name__}: {e}"[:200]}
    if not vals.pop("_vllm_lines"):
        return {"ok": False, "values": vals, "error": "vllm: 지표 줄 없음"}
    return {"ok": True, "values": vals, "error": ""}


def mtp_window(before: dict, after: dict, expect: str) -> dict:
    """expect = on | off | any. 반환 {valid, why, draft, accepted, proc_start}"""
    r = {"valid": True, "why": "", "draft": None, "accepted": None, "proc_start": "unknown"}
    if expect == "any":
        if before["ok"] and after["ok"] and K_DRAFT in before["values"] and K_DRAFT in after["values"]:
            r["draft"] = after["values"][K_DRAFT] - before["values"][K_DRAFT]
        return r

    def bad(msg):
        return {**r, "valid": False, "why": msg}
    if not (before["ok"] and after["ok"]):
        return bad(f"지표 수집 실패 시작:{before['error'] or '정상'} 끝:{after['error'] or '정상'}")
    b, a = before["values"], after["values"]
    for side in (b, a):
        for k, v in side.items():
            if not math.isfinite(v) or v < 0:
                return bad(f"지표 값 이상 {k}={v}")
    if K_START in b and K_START in a:
        if b[K_START] != a[K_START]:
            return bad("측정 중 엔진 재시작(process_start_time 변화)")
        r["proc_start"] = "same"
    for key, name in ((K_DRAFT, "초안"), (K_ACC, "수락")):
        if (key in b) != (key in a):
            return bad(f"{name} 지표가 한쪽에만 있음(시작 {key in b}, 끝 {key in a})")
        if key in b:
            d = a[key] - b[key]
            if d < 0:
                return bad(f"{name} 누적값 감소 {d:g}(재시작 의심)")
            r["draft" if key == K_DRAFT else "accepted"] = d
    if r["accepted"] is not None and r["draft"] is not None and r["accepted"] > r["draft"]:
        return bad(f"수락 증가 {r['accepted']:g} > 초안 증가 {r['draft']:g}")
    if expect == "on" and not (r["draft"] or 0) > 0:
        return bad(f"MTP 켬인데 본 측정 구간 초안 토큰 증가 {r['draft']}")
    if expect == "off" and (r["draft"] or 0) > 0:
        return bad(f"MTP 끔인데 초안 토큰 증가 {r['draft']:g}")
    return r


# ── 반례 시험 (서버 없이) ─────────────────────────────────────────────
def self_test() -> int:
    ok_args = json.dumps({"category": "배송", "urgency": "높음", "reason": "지연"}, ensure_ascii=False)

    def body(msg, finish="tool_calls", done=True):
        return {"choices": [{"message": msg, "finish_reason": finish}], "stream_done": done}

    def call(a, name=TOOL_NAME, cid="x", typ="function"):
        return {"id": cid, "type": typ, "function": {"name": name, "arguments": a}}

    def tm(*calls, content=None):
        return {"tool_calls": list(calls), "content": content, "reasoning": "생각"}

    def sm(content):
        return {"content": content, "reasoning": "생각"}

    J = judge_grammar
    cases = [
        ("schema 정상", J("schema", 200, body(sm(ok_args), "stop")), "ok"),
        ("schema 코드펜스", J("schema", 200, body(sm("```json\n" + ok_args + "\n```"), "stop")), "symptom"),
        ("schema 이중 중괄호", J("schema", 200, body(sm("{" + ok_args), "stop")), "symptom"),
        ("schema 열거값 밖", J("schema", 200, body(sm(ok_args.replace("배송", "택배")), "stop")), "symptom"),
        ("schema 필수 누락", J("schema", 200, body(sm('{"category":"배송","urgency":"높음"}'), "stop")), "symptom"),
        ("schema 추가 필드", J("schema", 200, body(sm(ok_args[:-1] + ', "x": 1}'), "stop")), "symptom"),
        ("schema finish abort", J("schema", 200, body(sm(ok_args), "abort")), "symptom"),
        ("schema 길이 초과", J("schema", 200, body(sm('{"cat'), "length")), "truncated"),
        ("schema-stream 길이 초과·DONE 있음", J("schema-stream", 200, body(sm('{"cat'), "length")), "truncated"),
        ("schema-stream 길이 초과·DONE 없음", J("schema-stream", 200, body(sm('{"cat'), "length", done=False)), "symptom"),
        ("schema-stream DONE 없음", J("schema-stream", 200, body(sm(ok_args), "stop", done=False)), "symptom"),
        ("schema 500", J("schema", 500, "Failed to advance FSM"), "symptom"),
        ("schema 400 grammar 낱말", J("schema", 400, "grammar rejected tokens"), "invalid"),
        ("required 정상", J("required", 200, body(tm(call(ok_args)))), "ok"),
        ("required 두 호출 정상", J("required", 200, body(tm(call(ok_args), call(ok_args, cid="y")))), "ok"),
        ("required 호출 없음", J("required", 200, body({"content": "그냥 답", "reasoning": "r"}, "stop")), "symptom"),
        ("required 인자 JSON 깨짐", J("required", 200, body(tm(call('{"category": "배송",')))), "symptom"),
        ("required 둘째 호출 깨짐", J("required", 200, body(tm(call(ok_args), call("{oops", cid="y")))), "symptom"),
        ("required 호출이 객체 아님", J("required", 200, body(tm(call(ok_args), "oops"))), "symptom"),
        ("required 이름 다름", J("required", 200, body(tm(call(ok_args, name="other")))), "symptom"),
        ("required id 없음", J("required", 200, body(tm(call(ok_args, cid="")))), "symptom"),
        ("required type 다름", J("required", 200, body(tm(call(ok_args, typ="tool")))), "symptom"),
        ("required finish stop", J("required", 200, body(tm(call(ok_args)), "stop")), "symptom"),
        ("required 표식 누출", J("required", 200, body(tm(call(ok_args), content="<|tool_call>call:classify_ticket{"))), "symptom"),
        ("required 열거값 밖 = 품질", J("required", 200, body(tm(call(ok_args.replace("배송", "택배"))))), "quality"),
        ("required 필수 누락 = 품질", J("required", 200, body(tm(call('{"category":"배송","urgency":"높음"}')))), "quality"),
        ("required-stream DONE 없음", J("required-stream", 200, body(tm(call(ok_args)), done=False)), "symptom"),
        ("required 500", J("required", 500, "EngineCore died"), "symptom"),
        ("required 400", J("required", 400, "bad request"), "invalid"),
    ]
    sb = lambda t, calls=None, finish="stop", reason="": {"choices": [{"message": {"content": t, "tool_calls": calls, "reasoning": reason}, "finish_reason": finish}]}
    cases += [
        ("짧은 답 일치", judge_short("4", 200, sb("4")), "ok"),
        ("짧은 답 기준과 같아도 연속 반복", judge_short("thoughtthought4", 200, sb("thoughtthought4")), "symptom"),
        ("짧은 답 추론에 특수 구분자", judge_short("4", 200, sb("4", reason='<|"|>x')), "symptom"),
        ("짧은 답 도구 스키마 JSON 조각", judge_short("4", 200, sb('{"type": "object", "properties": {')), "symptom"),
        ("짧은 답 대체 문자", judge_short("4", 200, sb("4�")), "symptom"),
        ("짧은 답 토막 반복", judge_short("4", 200, sb("abcabcabcabcabc")), "symptom"),
        ("짧은 답 빈 답", judge_short("4", 200, sb("")), "symptom"),
        ("짧은 답 도구 호출", judge_short("4", 200, sb("", [{"function": {"name": "tool_3"}}])), "symptom"),
        ("짧은 답 정상 문장의 낱말 = 검토", judge_short("4", 200, sb("4", reason="No tool_0 is needed; its parameters are irrelevant.")), "review"),
        ("짧은 답 떨어진 thought 두 번 = 검토", judge_short("4", 200, sb("4", reason="I thought about it. A second thought.")), "review"),
        ("짧은 답 길이 초과 종료 = 검토", judge_short("4", 200, sb("4 and so on", finish="length")), "review"),
        ("짧은 답 abort 종료 = 증상", judge_short("4", 200, sb("4", finish="abort")), "symptom"),
        ("짧은 답 종료 사유 없음 = 증상", judge_short("4", 200, sb("4", finish=None)), "symptom"),
        ("짧은 답 four = 차이", judge_short("4", 200, sb("four")), "diff"),
        ("짧은 답 44 = 차이", judge_short("4", 200, sb("44")), "diff"),
        ("짧은 답 500", judge_short("4", 500, "err"), "symptom"),
        ("짧은 답 400", judge_short("4", 400, "bad"), "invalid"),
    ]
    bad = [(n, r["verdict"], w) for n, r, w in cases if r["verdict"] != w]
    good_ref = (200, sb("4"))
    ref_cases = [
        ("기준 정상", check_refs([good_ref] * 3)[0], "4"),
        ("기준 깨짐", check_refs([(200, sb("thoughtthought"))] * 3)[1].startswith("단독 조건 품질 이상"), True),
        ("기준 four", check_refs([(200, sb("four"))] * 3)[1].startswith("단독 조건 품질 이상"), True),
        ("기준 약한 표식만 = 검토 필요", check_refs([(200, sb("4", reason="No tool_0 is needed"))] * 3)[1].startswith("기준 답 검토 필요"), True),
        ("기준 강한+약한 = 품질 이상", check_refs([(200, sb("4", reason='tool_ <|"|>'))] * 3)[1].startswith("단독 조건 품질 이상"), True),
        ("기준 abort = 품질 이상", check_refs([(200, sb("4", finish="abort"))] * 3)[1].startswith("단독 조건 품질 이상"), True),
        ("기준 불안정", check_refs([good_ref, good_ref, (200, sb("4."))])[1].startswith("기준 답 불안정"), True),
        ("기준 요청 실패", check_refs([good_ref, (400, "x"), good_ref])[1].startswith("기준 요청 실패"), True),
    ]
    g = lambda kind, v, rl=5: {"kind": kind, "verdict": v, "reasoning_len": rl, "detail": "x"}
    full_ok = [g(k, "ok") for k in G_KINDS for _ in range(4)]
    S = summarize_grammar
    sum_cases = [
        ("전부 정상", (S(full_ok)["valid"], S(full_ok)["symptoms"]), (True, 0)),
        ("증상 1", (S(full_ok + [g("schema", "symptom")])["valid"], S(full_ok + [g("schema", "symptom")])["symptoms"]), (True, 1)),
        ("무효+증상은 무효이나 증상 수 보존", (S(full_ok + [g("schema", "invalid"), g("schema", "symptom")])["valid"],
                                       S(full_ok + [g("schema", "invalid"), g("schema", "symptom")])["symptoms"]), (False, 1)),
        ("한 종류만 추론 없음", S([g(k, "ok", 0 if k == "schema" else 5) for k in G_KINDS for _ in range(4)])["valid"], False),
        ("한 종류만 길이 초과 과다", S(full_ok + [g("required", "truncated")] * 2)["valid"], False),
        ("한 종류 결과 없음", S([x for x in full_ok if x["kind"] != "required"])["valid"], False),
        ("품질은 증상이 아님", (S(full_ok + [g("required", "quality")])["valid"], S(full_ok + [g("required", "quality")])["symptoms"],
                          S(full_ok + [g("required", "quality")])["quality"]), (True, 0, 1)),
    ]
    mk = lambda kind, r, v, t0, t1: {"kind": kind, "round": r, "verdict": v, "t_start": t0, "t_end": t1, "detail": "x"}
    one_round = [mk("long", 0, "ok", 0.05, 2.0)] + [mk("short", 0, "ok", 0.0, 0.5)] * 2 + [mk("short", 0, "ok", 0.4, 0.9)] * 2
    M = summarize_mix
    mix_cases = [
        ("mix 정상", (M({"ref": "4"}, one_round, [], 1, 4)["valid"], M({"ref": "4"}, one_round, [], 1, 4)["symptoms"]), (True, 0)),
        ("mix 증상", M({"ref": "4"}, one_round[:1] + [mk("short", 0, "symptom", 0.0, 0.5)] * 4, [], 1, 4)["symptoms"], 4),
        ("mix 검토는 증상 아님", (M({"ref": "4"}, one_round[:1] + [mk("short", 0, "review", 0.0, 0.5)] * 4, [], 1, 4)["symptoms"],
                             M({"ref": "4"}, one_round[:1] + [mk("short", 0, "review", 0.0, 0.5)] * 4, [], 1, 4)["review"]), (0, 4)),
        ("mix 차이만", (M({"ref": "4"}, one_round[:1] + [mk("short", 0, "diff", 0.0, 0.5)] * 4, [], 1, 4)["valid"],
                      M({"ref": "4"}, one_round[:1] + [mk("short", 0, "diff", 0.0, 0.5)] * 4, [], 1, 4)["symptoms"]), (True, 0)),
        ("mix 응답 누락", M({"ref": "4"}, one_round[:2], [], 1, 4)["valid"], False),
        ("mix 기준 이상", (M({"ref_anomaly": True}, [], ["단독 조건 품질 이상"], 1, 4)["valid"],
                       M({"ref_anomaly": True}, [], ["단독 조건 품질 이상"], 1, 4)["ref_anomaly"]), (False, True)),
        ("mix 겹침 부족", M({"ref": "4"}, [mk("long", 0, "ok", 5.0, 6.0)] + [mk("short", 0, "ok", 0.0, 0.5)] * 4, [], 1, 4)["valid"], False),
    ]
    up = lambda **v: {"ok": True, "values": v, "error": ""}
    down = {"ok": False, "values": {}, "error": "URLError"}
    D = {K_DRAFT: 5.0}
    D9 = {K_DRAFT: 9.0}
    W = lambda b, a, e: mtp_window(b, a, e)["valid"]
    mtp_cases = [
        ("on 정상", W(up(**D), up(**D9), "on"), True),
        ("on 시작 지표 실패", W(down, up(**D9), "on"), False),
        ("on 시작 지표 없음+끝 9", W(up(), up(**D9), "on"), False),
        ("on 증가 없음", W(up(**D), up(**D), "on"), False),
        ("on 감소", W(up(**D9), up(**D), "on"), False),
        ("on 수락 감소", W(up(**{K_DRAFT: 5.0, K_ACC: 4.0}), up(**{K_DRAFT: 9.0, K_ACC: 1.0}), "on"), False),
        ("on 수락 > 초안", W(up(**{K_DRAFT: 5.0, K_ACC: 0.0}), up(**{K_DRAFT: 6.0, K_ACC: 3.0}), "on"), False),
        ("on 수락 한쪽만", W(up(**{K_DRAFT: 5.0}), up(**{K_DRAFT: 9.0, K_ACC: 1.0}), "on"), False),
        ("on 비유한 값", W(up(**D), up(**{K_DRAFT: float("nan")}), "on"), False),
        ("on 재시작", W(up(**D, process_start_time_seconds=1.0), up(**D9, process_start_time_seconds=2.0), "on"), False),
        ("시작 시각 같음 표시", mtp_window(up(**D, process_start_time_seconds=1.0), up(**D9, process_start_time_seconds=1.0), "on")["proc_start"], "same"),
        ("시작 시각 미확인 표시", mtp_window(up(**D), up(**D9), "on")["proc_start"], "unknown"),
        ("off 지표 없음", W(up(), up(), "off"), True),
        ("off 증가 0", W(up(**D), up(**D), "off"), True),
        ("off 증가", W(up(**D), up(**D9), "off"), False),
        ("off 수집 실패", W(up(), down, "off"), False),
        ("any 수집 실패도 유효", W(down, down, "any"), True),
    ]
    parse_case = parse_metrics('# HELP x\nvllm:spec_decode_num_draft_tokens_total{engine="0",model_name="g"} 12.0\n'
                               'vllm:spec_decode_num_draft_tokens_total{engine="1",model_name="g"} 3.0\nprocess_start_time_seconds 1.7e9\n')
    other = [("지표 파싱", parse_case, {"_vllm_lines": 2, K_DRAFT: 15.0, K_START: 1.7e9}),
             ("빈 지표 본문", parse_metrics("")["_vllm_lines"], 0)]
    for n, got, w in ref_cases + sum_cases + mix_cases + mtp_cases + other:
        if got != w:
            bad.append((n, got, w))
    for n, got, w in bad:
        print(f"❌ {n}: {got} (기대 {w})")
    total = len(cases) + len(ref_cases) + len(sum_cases) + len(mix_cases) + len(mtp_cases) + len(other)
    print(f"결과: 반례 {total}건 중 실패 {len(bad)}")
    return 1 if bad else 0


STATE: dict = {}
OUT: list = []   # --out 경로(신호 처리기에서 쓴다)


def _dump(suffix: str, lock_timeout: float | None) -> None:
    """STATE를 <out>.<suffix>에 쓰고 os.replace로 바꿔 넣는다(쓰다 끊겨도 이전 파일이 남는다).
    결과 목록 잠금은 일꾼 스레드만 짧게 잡는다. lock_timeout이 None이면 기다리고, 숫자면 그만큼만 기다린 뒤 잠금 없이 복사한다."""
    if not OUT:
        return
    got = SINK_LOCK.acquire() if lock_timeout is None else SINK_LOCK.acquire(timeout=lock_timeout)
    try:
        snap = json.dumps(STATE, ensure_ascii=False, indent=1, default=str)
    finally:
        if got:
            SINK_LOCK.release()
    tmp = f"{OUT[0]}.{suffix}"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(snap)
    os.replace(tmp, OUT[0])


def save_state() -> None:
    _dump("tmp", None)


def on_term(signum, frame):
    """TERM: 더 오는 TERM은 무시하고, 그때까지 받은 결과를 쓴 뒤 바로 끝낸다(요청 스레드를 기다리지 않음).
    주 스레드가 save_state 도중이어도 처리기는 다른 임시 파일을 쓰고, 결과 목록 잠금은 최대 5초만 기다린다."""
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    STATE.update(exit=143, terminated=f"신호 {signum}", valid=False)
    try:
        _dump("term.tmp", 5.0)
    finally:
        print(f"RESULT valid=0 symptoms=? quality=? review=? ref_anomaly=? ref_review=? proc_start=unknown code=143 · 신호 {signum}로 중단", flush=True)
        os._exit(143)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["grammar", "mix", "self-test"])
    ap.add_argument("--base-url", default="http://127.0.0.1:7090")
    ap.add_argument("--out")
    ap.add_argument("--n", type=int, default=40, help="grammar: 종류별 요청 수")
    ap.add_argument("--workers", type=int, default=4, help="grammar: 동시 요청 수")
    ap.add_argument("--max-tokens", type=int, default=3072, help="grammar: 추론+출력 토큰 상한")
    ap.add_argument("--long-tokens", type=int, default=3000, help="mix: 긴 대화 목표 토큰")
    ap.add_argument("--long-k", type=int, default=0, help="mix: 긴 대화 반복 수 고정(0이면 크기 맞추기)")
    ap.add_argument("--seed", default="mtpbug", help="mix: 회차 태그 씨앗(같으면 같은 긴 입력)")
    ap.add_argument("--rounds", type=int, default=20, help="mix: 섞기 회차")
    ap.add_argument("--shorts", type=int, default=4, help="mix: 회차당 짧은 요청 수")
    ap.add_argument("--mtp", choices=["on", "off", "any"], default="any", help="본 측정 구간의 MTP 동작 조건")
    a = ap.parse_args()
    if a.mode == "self-test":
        return self_test()
    STATE.update(mode=a.mode, args=vars(a), results=[], meta={}, metrics={},
                 response_note="스트리밍 응답은 공유 클라이언트가 조각을 합친 합성 응답(조각 미보존), HTTP 오류 본문은 300자에서 잘림")
    if a.out:
        OUT.append(a.out)
    signal.signal(signal.SIGTERM, on_term)
    code = 2
    try:
        code = run(a, STATE)
    except Exception:   # 최상위 경계: 탐침 자체의 예기치 못한 예외는 증상(1)이 아니라 시험 무효(2)로 끝낸다
        STATE["fatal"] = traceback.format_exc()[-3000:]
        print(STATE["fatal"])
        print(f"RESULT valid=0 symptoms=? quality=? review=? ref_anomaly=? ref_review=? proc_start=unknown code=2 · 탐침 예외(받은 결과 {len(STATE['results'])}건은 JSON에 있음)")
        code = 2
    finally:
        STATE["exit"] = code
        save_state()   # 예외가 나도 그때까지 모은 원문을 남긴다
    return code


def run(a: argparse.Namespace, state: dict) -> int:
    cli = Client(a.base_url)
    state.update(model=cli.model, version=cli.version())
    print(f"서버 {a.base_url} · 모델 {cli.model} · vLLM {state['version']} · 모드 {a.mode} · MTP 조건 {a.mtp}", flush=True)
    if a.mode == "grammar":
        state["metrics"]["before"] = scrape(a.base_url)
        run_grammar(cli, a.n, a.workers, a.max_tokens, state["results"])
        state["metrics"]["after"] = scrape(a.base_url)
        s = summarize_grammar(state["results"])
    else:
        def between():
            state["metrics"]["before"] = scrape(a.base_url)
        notes = run_mix(cli, a.long_tokens, a.rounds, a.shorts, between, state["results"], state["meta"], a.seed, a.long_k or None)
        state["metrics"]["after"] = scrape(a.base_url)
        state["notes"] = notes
        s = summarize_mix(state["meta"], state["results"], notes, a.rounds, a.shorts)
    if "before" in state["metrics"]:
        w = mtp_window(state["metrics"]["before"], state["metrics"]["after"], a.mtp)
    else:   # mix가 본 측정 전에 끝남(크기·기준 실패) — 이미 무효 사유가 있다
        w = {"valid": a.mtp == "any", "why": "본 측정 전에 끝남", "draft": None, "accepted": None, "proc_start": "unknown"}
    state["metrics"]["window"] = w
    why = s["why"] + ([w["why"]] if not w["valid"] else [])
    valid = not why
    code = 2 if not valid else (1 if s["symptoms"] else 0)
    d, acc = w.get("draft"), w.get("accepted")
    print(f"MTP 본 측정 구간 초안 토큰 {d if d is not None else '지표 없음'} · 수락 {acc if acc is not None else '-'}"
          + (f" · 수락률 {acc / d:.3f}" if d and acc is not None else "") + f" · 지표 프로세스 시작 시각 {w['proc_start']}(잠정, 로그 검사로 확정)")
    for ln in s["lines"]:
        print(ln)
    if why:
        print("판정 무효: " + ", ".join(why))
    ra, rr = int(bool(s.get("ref_anomaly"))), int(bool(s.get("ref_review")))
    state.update(valid=valid, symptoms=s["symptoms"], quality=s["quality"], review=s["review"], ref_anomaly=bool(ra), ref_review=bool(rr),
                 why=why, summary=s["lines"])
    print(f"결과: {'무효' if not valid else ('증상 검출' if s['symptoms'] else '미검출')} · 증상 {s['symptoms']} · 품질·차이 {s['quality']}"
          f" · 검토 {s['review']}" + (" · 단독 조건 품질 이상" if ra else ""))
    if a.mode == "mix" and state["meta"].get("long_k_ok"):
        print(f"LONG_K {state['meta']['long_k']}")
    print(f"RESULT valid={int(valid)} symptoms={s['symptoms']} quality={s['quality']} review={s['review']} ref_anomaly={ra} ref_review={rr} proc_start={w['proc_start']} code={code}")
    return code


if __name__ == "__main__":
    sys.exit(main())
