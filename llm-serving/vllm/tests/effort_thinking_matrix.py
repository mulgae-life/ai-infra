#!/usr/bin/env python3
"""reasoning_effort × enable_thinking 조합 시험 (게이트웨이 경유 / 백엔드 직접 공용).

vLLM 0.31부터 요청 최상위 `reasoning_effort`가 있으면 `enable_thinking`을 자동으로 켠다
(entrypoints/openai/chat_completion/protocol.py). 게이트웨이는 effort를 템플릿 인자로 옮겨 이 매핑을 피하고
"thinking 스위치는 enable_thinking, effort는 강약"이라는 계약을 유지한다. 이 스크립트는 그 계약이
옛(0.20 nightly)·새(0.31) 백엔드에서 똑같이 지켜지는지 조합별로 확인한다.

판정은 `reasoning` 필드 유무만으로 하지 않는다. 출력 토큰 수(usage.completion_tokens)와 응답 구조를 같이 적는다.
스트리밍·비스트리밍을 둘 다 돈다.

사용 (표준 라이브러리만 사용):
    # 게이트웨이 경유 (기대값 = 지금 동작)
    python tests/effort_thinking_matrix.py --base-url http://127.0.0.1:6090 --family qwen
    # 백엔드 직접 (0.31의 새 의미를 기록하는 용도, 판정 아님)
    python tests/effort_thinking_matrix.py --base-url http://127.0.0.1:7090 --family gemma --direct
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

PROMPT = "자동차보험 대인배상I과 대인배상II의 보장 범위 차이를 두 문장으로 설명해줘."

# (사례 이름, 최상위 reasoning_effort, chat_template_kwargs, 게이트웨이 경유 기대 {thinking 켜짐?, X-Effort-Applied})
# 기대값은 계획서 part2 P3 "effort × thinking" 항목. 백엔드 직접은 기대값을 판정에 쓰지 않는다.
CASES = {
    "qwen": [
        ("thinking 생략, effort 없음",        None,     {},                          (False, None)),
        ("thinking 생략, effort high",        "high",   {},                          (False, "xhigh")),
        ("thinking false, effort high",       "high",   {"enable_thinking": False},  (False, "xhigh")),
        ("thinking true, effort 없음",        None,     {"enable_thinking": True},   (True, None)),
        ("thinking true, effort high",        "high",   {"enable_thinking": True},   (True, "xhigh")),
        ("thinking true, effort low",         "low",    {"enable_thinking": True},   (True, "low")),
        ("thinking true, effort medium",      "medium", {"enable_thinking": True},   (True, "medium")),
        ("thinking true, effort none",        "none",   {"enable_thinking": True},   (False, "none")),
        ("thinking 생략, kwargs effort high", None,     {"reasoning_effort": "high"}, (False, "xhigh")),
    ],
    "gemma": [
        ("thinking 생략, effort 없음",        None,     {},                          (False, None)),
        ("thinking 생략, effort high",        "high",   {},                          (False, "dropped")),
        ("thinking true, effort 없음",        None,     {"enable_thinking": True},   (True, None)),
        ("thinking true, effort high",        "high",   {"enable_thinking": True},   (True, "dropped")),
        ("thinking true, effort none",        "none",   {"enable_thinking": True},   (False, "none")),
    ],
}


def _request(url: str, body: dict, timeout: float = 180) -> tuple[int, dict, bytes]:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def _body(effort: str | None, kwargs: dict, stream: bool, family: str) -> dict:
    body = {"model": "gemma-4", "messages": [{"role": "user", "content": PROMPT}], "max_tokens": 700, "temperature": 0}
    if effort is not None:
        body["reasoning_effort"] = effort
    if kwargs:
        body["chat_template_kwargs"] = dict(kwargs)
    if family == "gemma":
        # Gemma 4는 비스트리밍 reasoning 분리에 특수 토큰 유지가 필요하다(test_vllm_server.py t_5_2와 같은 조건)
        body["skip_special_tokens"] = False
    if stream:
        body["stream"] = True
        body["stream_options"] = {"include_usage": True}
    return body


def _parse_nonstream(raw: bytes) -> tuple[bool, int, int, str]:
    data = json.loads(raw)
    msg = data["choices"][0]["message"]
    reasoning = msg.get("reasoning") or msg.get("reasoning_content") or ""
    content = msg.get("content") or ""
    usage = data.get("usage") or {}
    return bool(reasoning), len(str(reasoning)), usage.get("completion_tokens", -1), content[:60].replace("\n", " ")


def _parse_stream(raw: bytes) -> tuple[bool, int, int, str]:
    reasoning_len = 0
    content = ""
    completion = -1
    for line in raw.decode(errors="replace").splitlines():
        if not line.startswith("data: ") or line.strip() == "data: [DONE]":
            continue
        chunk = json.loads(line[6:])
        if chunk.get("usage"):
            completion = chunk["usage"].get("completion_tokens", -1)
        for ch in chunk.get("choices", []):
            delta = ch.get("delta") or {}
            r = delta.get("reasoning") or delta.get("reasoning_content")
            if r:
                reasoning_len += len(str(r))
            if delta.get("content"):
                content += delta["content"]
    return reasoning_len > 0, reasoning_len, completion, content[:60].replace("\n", " ")


def main() -> int:
    p = argparse.ArgumentParser(description="reasoning_effort × enable_thinking 조합 시험")
    p.add_argument("--base-url", default="http://127.0.0.1:6090")
    p.add_argument("--family", choices=sorted(CASES), required=True)
    p.add_argument("--direct", action="store_true", help="백엔드 직접 호출: 기대값 판정 없이 기록만")
    args = p.parse_args()
    url = f"{args.base_url.rstrip('/')}/v1/chat/completions"

    print(f"대상 {url} · 계열 {args.family} · {'직접(기록만)' if args.direct else '게이트웨이 경유(판정)'}")
    print(f"{'사례':<32} {'모드':<5} {'HTTP':>4} {'사고':>4} {'사고글자':>7} {'출력토큰':>7} {'X-Effort-Applied':<17} 판정  응답 앞부분")
    failures = 0
    for name, effort, kwargs, (exp_thinking, exp_header) in CASES[args.family]:
        for stream in (False, True):
            status, headers, raw = _request(url, _body(effort, kwargs, stream, args.family))
            header = {k.lower(): v for k, v in headers.items()}.get("x-effort-applied")
            if status != 200:
                err = raw.decode(errors="replace")[:70].replace("\n", " ")
                verdict = "기록" if args.direct else "❌"
                failures += 0 if args.direct else 1
                print(f"{name:<32} {'strm' if stream else 'sync':<5} {status:>4} {'-':>4} {'-':>7} {'-':>7} {str(header):<17} {verdict}  {err}")
                continue
            has_r, r_len, comp, preview = (_parse_stream if stream else _parse_nonstream)(raw)
            if args.direct:
                verdict = "기록"
            else:
                ok = (has_r == exp_thinking) and (header == exp_header)
                failures += 0 if ok else 1
                verdict = "✅" if ok else f"❌(기대 사고={exp_thinking}, 헤더={exp_header})"
            print(f"{name:<32} {'strm' if stream else 'sync':<5} {status:>4} {('예' if has_r else '아니오'):>4} {r_len:>7} {comp:>7} {str(header):<17} {verdict}  {preview}")
    if args.direct:
        print("결과: 기록 완료 (직접 호출은 판정하지 않음)")
        return 0
    print(f"결과: {'✅ 전부 기대값과 일치' if failures == 0 else f'❌ {failures}건 불일치'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
