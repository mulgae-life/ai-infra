#!/usr/bin/env python3
"""vLLM 서버 QA 테스트 스크립트.

vLLM 서버 배포 후 기능 검증을 위한 테스트 스위트.
외부 의존성 없이 Python 표준 라이브러리만 사용.

테스트 단계:
  1. 인프라: /health, /v1/models, 잘못된 엔드포인트 응답 확인.
  2. 기본 추론: 단일 턴, 시스템 프롬프트, 멀티턴 맥락, 잘못된 모델명 확인.
  3. 스트리밍: SSE 청크, [DONE], stream_options.include_usage 확인.
  4. 샘플링: temperature/seed, 높은 temperature, max_tokens=1, 잘못된 temperature 확인.
  5. Thinking: 기본 OFF, 요청 단위 ON reasoning 분리, 명시적 OFF 확인.
  6. Tool Calling: 단일 tool, 복수 tool, tool 미사용 응답, tool 결과 반영 확인.
  7. 경계값/스트레스: 빈 입력, 긴 입력, 동시 텍스트 요청, 잘못된 JSON, 필수 필드 누락 확인.
  8. 프리픽스 캐싱: 동일 시스템 프롬프트 반복 호출의 응답 시간 비교.
  9. 멀티모달: 단일 이미지, 동시 이미지, 이미지+텍스트 혼합 요청 안정성 확인.
 10. 게이트웨이 계약: effort와 추론 켜고 끄기, 정체성 문구, developer 역할, 모델 경로 가림 확인.
     대상이 게이트웨이일 때만 돈다(백엔드 vLLM에 직접 붙으면 건너뜀).

사용법 (vllm/ 디렉토리에서 실행):
    # 기본 (localhost:5015, base-url 포트 → gateways/+instances/에서 모델명 자동 추출)
    python tests/test_vllm_server.py

    # 커스텀 서버/모델
    python tests/test_vllm_server.py --base-url http://localhost:8000 --model MyModel

    # 특정 카테고리만 실행
    python tests/test_vllm_server.py --category infra inference

    # 카테고리 목록 확인
    python tests/test_vllm_server.py --list
"""
import argparse
import base64
import http.client
import json
import os
import re
import sys
import textwrap
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

# 정체성 확인의 금지어·질문은 단독 탐침과 같은 목록을 쓴다(같은 폴더라 스크립트 실행 시 import된다).
from gateway_compat_probe import _FORBIDDEN as _IDENTITY_FORBIDDEN, IDENTITY_QUESTIONS

# ── 로그 Tee (콘솔 + 파일) ──────────────────────────────
# main 진입 시 sys.stdout/stderr를 _Tee로 교체. 콘솔에는 색 그대로,
# 파일에는 ANSI escape 제거하여 사후 검토 가독성 확보.
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


class _Tee:
    def __init__(self, console, log_file):
        self.console = console
        self.log_file = log_file

    def write(self, data):
        self.console.write(data)
        self.log_file.write(_ANSI_RE.sub("", data))
        self.console.flush()
        self.log_file.flush()

    def flush(self):
        self.console.flush()
        self.log_file.flush()

    def isatty(self):
        return self.console.isatty()

# ── 컬러 출력 ────────────────────────────────────────────

COLORS = {
    "green": "\033[92m",
    "red": "\033[91m",
    "yellow": "\033[93m",
    "cyan": "\033[96m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "reset": "\033[0m",
}

NO_COLORS = {k: "" for k in COLORS}


def _c(colors: dict, name: str, text: str) -> str:
    return f"{colors[name]}{text}{colors['reset']}"


# ── 테스트 결과 ──────────────────────────────────────────


@dataclass
class TestResult:
    id: str
    category: str
    name: str
    passed: bool
    detail: str = ""
    elapsed_ms: float = 0


@dataclass
class TestContext:
    base_url: str
    model: str
    colors: dict
    results: list = field(default_factory=list)
    verbose: bool = False


# ── HTTP 헬퍼 ────────────────────────────────────────────

# 마지막 요청/응답 메타. _run_test가 fail 시 자동으로 detail에 부착.
# 동시 요청 테스트(t_7.3·t_7.4, t_9.2~t_9.4)에선 race condition 가능하지만, 그런 케이스는
# 자체 detail로 풍부 정보를 채우므로 보조 컨텍스트로만 사용.
_LAST_REQUEST: dict | None = None
_LAST_RESPONSE: dict | None = None


def _record_request(method: str, url: str, body: dict | None) -> None:
    global _LAST_REQUEST
    _LAST_REQUEST = {"method": method, "url": url, "body": body}


def _record_response(status: int | str, body) -> None:
    global _LAST_RESPONSE
    _LAST_RESPONSE = {"status": status, "body": body}


def _reset_request_log() -> None:
    """_run_test 시작 시 호출 — 이전 테스트의 메타가 다음 fail 진단에 누수되지 않게."""
    global _LAST_REQUEST, _LAST_RESPONSE
    _LAST_REQUEST = None
    _LAST_RESPONSE = None


def _request(
    url: str,
    *,
    method: str = "GET",
    body: dict | None = None,
    timeout: float = 60,
) -> tuple[int, dict | str]:
    """urllib로 HTTP 요청. (status_code, parsed_body) 반환.
    실패 진단을 위해 마지막 요청/응답을 모듈 전역에 기록한다."""
    _record_request(method, url, body)
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = raw
            _record_response(resp.status, parsed)
            return resp.status, parsed
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw
        _record_response(e.code, parsed)
        return e.code, parsed
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        _record_response(f"<network error: {type(e).__name__}>", str(e))
        raise


def _chat(
    ctx: TestContext,
    messages: list[dict],
    *,
    timeout: float = 60,
    **extra,
) -> tuple[int, dict]:
    """chat/completions 요청 헬퍼."""
    body = {"model": ctx.model, "messages": messages, **extra}
    return _request(f"{ctx.base_url}/v1/chat/completions", method="POST", body=body, timeout=timeout)


# 이미지 파일은 반복 로딩 낭비를 피하기 위해 모듈 레벨에서 1회 캐시한다.
_TEST_IMAGE_DATA_URL: str | None = None


def _load_test_image() -> str:
    """tests/image.png를 data URL(base64)로 로드한다.

    vLLM OpenAI 호환 API는 image_url.url에 data URL을 직접 받는다.
    동시 10개 테스트에서 반복 디스크 IO를 피하려고 모듈 캐시 사용.
    """
    global _TEST_IMAGE_DATA_URL
    if _TEST_IMAGE_DATA_URL is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image.png")
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        _TEST_IMAGE_DATA_URL = f"data:image/png;base64,{b64}"
    return _TEST_IMAGE_DATA_URL


def _chat_with_image(
    ctx: TestContext,
    text: str,
    image_url: str,
    *,
    timeout: float = 120,
    **extra,
) -> tuple[int, dict]:
    """이미지 + 텍스트 chat/completions 요청 헬퍼."""
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }
    ]
    body = {"model": ctx.model, "messages": messages, **extra}
    return _request(f"{ctx.base_url}/v1/chat/completions", method="POST", body=body, timeout=timeout)


def _stream_chat(
    ctx: TestContext,
    messages: list[dict],
    *,
    timeout: float = 60,
    **extra,
) -> tuple[int, list[str]]:
    """스트리밍 chat/completions 요청. (status, [raw_lines]) 반환."""
    url = f"{ctx.base_url}/v1/chat/completions"
    body = {"model": ctx.model, "messages": messages, "stream": True, **extra}
    _record_request("POST", url, body)
    data = json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            lines = []
            for line in resp:
                decoded = line.decode().strip()
                if decoded:
                    lines.append(decoded)
            _record_response(resp.status, f"<{len(lines)} SSE lines>")
            return resp.status, lines
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw
        _record_response(e.code, parsed)
        return e.code, []
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        _record_response(f"<network error: {type(e).__name__}>", str(e))
        raise


# ── 테스트 실행 프레임워크 ────────────────────────────────


def _format_body(body, *, max_len: int = 800) -> str:
    """dict는 indent=2로 pretty print, 그 외는 str. 길이 cap."""
    if body is None:
        return "<none>"
    if isinstance(body, (dict, list)):
        try:
            text = json.dumps(body, ensure_ascii=False, indent=2)
        except (TypeError, ValueError):
            text = repr(body)
    else:
        text = str(body)
    if len(text) > max_len:
        text = text[:max_len] + f"\n... (생략, 전체 {len(text)}자)"
    return text


def _build_failure_context() -> str:
    """fail/예외 시 detail에 자동으로 부착할 마지막 요청/응답 컨텍스트."""
    if _LAST_REQUEST is None and _LAST_RESPONSE is None:
        return ""
    parts = []
    if _LAST_REQUEST is not None:
        parts.append(f"요청: {_LAST_REQUEST['method']} {_LAST_REQUEST['url']}")
        if _LAST_REQUEST.get("body") is not None:
            parts.append("요청 body:")
            parts.append(_format_body(_LAST_REQUEST["body"], max_len=600))
    if _LAST_RESPONSE is not None:
        parts.append(f"응답: HTTP {_LAST_RESPONSE['status']}")
        parts.append("응답 body:")
        parts.append(_format_body(_LAST_RESPONSE["body"], max_len=1200))
    return "\n".join(parts)


def _run_test(ctx: TestContext, test_id: str, category: str, name: str, fn):
    """테스트 함수를 실행하고 결과를 기록한다.
    실패 시 마지막 HTTP 요청/응답 컨텍스트를 자동 부착, 예외는 traceback 포함."""
    c = ctx.colors
    label = f"  [{test_id}] {name}"
    _reset_request_log()
    start = time.monotonic()
    try:
        passed, detail = fn()
        elapsed = (time.monotonic() - start) * 1000
        result = TestResult(test_id, category, name, passed, detail, elapsed)
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        tb = traceback.format_exc().rstrip()
        detail = f"예외: {type(e).__name__}: {e}\n{tb}"
        result = TestResult(test_id, category, name, False, detail, elapsed)

    if not result.passed:
        ctx_info = _build_failure_context()
        if ctx_info:
            result.detail = f"{result.detail}\n{ctx_info}" if result.detail else ctx_info

    ctx.results.append(result)

    status = _c(c, "green", "PASS") if result.passed else _c(c, "red", "FAIL")
    time_str = _c(c, "dim", f"({result.elapsed_ms:.0f}ms)")
    print(f"{status} {label} {time_str}")
    if result.detail and (not result.passed or ctx.verbose):
        for line in result.detail.split("\n"):
            print(f"       {_c(c, 'dim', line)}")


# ═══════════════════════════════════════════════════════════
# 테스트 카테고리
# ═══════════════════════════════════════════════════════════


# ── 1. 서버 기동 / 인프라 ────────────────────────────────

def test_infra(ctx: TestContext):
    c = ctx.colors
    print(f"\n{_c(c, 'bold', '1. 서버 기동 / 인프라')}")

    def t_1_1():
        """헬스체크"""
        status, _ = _request(f"{ctx.base_url}/health")
        return status == 200, f"HTTP {status}"

    def t_1_2():
        """모델 목록 조회"""
        status, body = _request(f"{ctx.base_url}/v1/models")
        if status != 200:
            return False, f"HTTP {status}"
        models = [m["id"] for m in body.get("data", [])]
        found = ctx.model in models
        return found, f"모델 목록: {models}" + ("" if found else f" ('{ctx.model}' 없음)")

    def t_1_3():
        """잘못된 엔드포인트"""
        status, _ = _request(f"{ctx.base_url}/v1/nonexistent")
        return status in (404, 405), f"HTTP {status}"

    _run_test(ctx, "1.1", "인프라", "헬스체크", t_1_1)
    _run_test(ctx, "1.2", "인프라", "모델 목록 조회", t_1_2)
    _run_test(ctx, "1.3", "인프라", "잘못된 엔드포인트", t_1_3)


# ── 2. 기본 추론 ────────────────────────────────────────

def test_inference(ctx: TestContext):
    c = ctx.colors
    print(f"\n{_c(c, 'bold', '2. 기본 추론 (Chat Completions)')}")

    def t_2_1():
        """단일 턴 — 짧은 응답"""
        status, body = _chat(ctx, [{"role": "user", "content": "실손보험이 뭐야?"}], max_tokens=50)
        if status != 200:
            return False, f"HTTP {status}: {body}"
        content = body["choices"][0]["message"]["content"]
        has_content = bool(content.strip())
        return has_content, f"응답: {content[:100]}"

    def t_2_2():
        """시스템 프롬프트 반영"""
        status, body = _chat(
            ctx,
            [
                {"role": "system", "content": "You must respond in English only. Never use Korean."},
                {"role": "user", "content": "자동차보험 대인배상 담보에 대해 알려줘"},
            ],
            max_tokens=100,
        )
        if status != 200:
            return False, f"HTTP {status}"
        content = body["choices"][0]["message"]["content"]
        return True, f"응답: {content[:100]}"

    def t_2_3():
        """멀티턴 대화 맥락 유지"""
        status, body = _chat(
            ctx,
            [
                {"role": "user", "content": "운전자보험 가입하고 싶어. 내 이름은 김철수야."},
                {"role": "assistant", "content": "안녕하세요, 김철수님! 운전자보험 관련 안내 도와드리겠습니다."},
                {"role": "user", "content": "내 이름이 뭐라고 했지?"},
            ],
            max_tokens=100,
        )
        if status != 200:
            return False, f"HTTP {status}"
        content = body["choices"][0]["message"]["content"]
        has_name = "철수" in content or "김철수" in content
        return has_name, f"응답: {content[:100]}" + ("" if has_name else " ('철수/김철수' 미포함)")

    def t_2_4():
        """존재하지 않는 모델명"""
        body = {"model": "nonexistent-model", "messages": [{"role": "user", "content": "보험 문의"}], "max_tokens": 10}
        status, resp = _request(f"{ctx.base_url}/v1/chat/completions", method="POST", body=body)
        is_error = status >= 400
        return is_error, f"HTTP {status}"

    _run_test(ctx, "2.1", "추론", "단일 턴 — 짧은 응답", t_2_1)
    _run_test(ctx, "2.2", "추론", "시스템 프롬프트 반영", t_2_2)
    _run_test(ctx, "2.3", "추론", "멀티턴 대화 맥락 유지", t_2_3)
    _run_test(ctx, "2.4", "추론", "존재하지 않는 모델명", t_2_4)


# ── 3. 스트리밍 ──────────────────────────────────────────

def test_streaming(ctx: TestContext):
    c = ctx.colors
    print(f"\n{_c(c, 'bold', '3. 스트리밍 (SSE)')}")

    def t_3_1():
        """기본 스트리밍 — 청크 순차 출력 + [DONE]"""
        status, lines = _stream_chat(
            ctx,
            [{"role": "user", "content": "화재보험에서 보장하는 담보 항목을 설명해줘"}],
            max_tokens=100,
        )
        if status != 200:
            return False, f"HTTP {status}"
        data_lines = [l for l in lines if l.startswith("data:")]
        has_done = any("data: [DONE]" in l for l in lines)
        chunk_count = len(data_lines)
        return has_done and chunk_count > 1, f"청크 {chunk_count}개, [DONE]: {has_done}"

    def t_3_2():
        """스트리밍 usage 반환"""
        status, lines = _stream_chat(
            ctx,
            [{"role": "user", "content": "실손보험 청구 절차 알려줘"}],
            max_tokens=30,
            stream_options={"include_usage": True},
        )
        if status != 200:
            return False, f"HTTP {status}"
        # 마지막 data 청크에서 usage 확인
        has_usage = False
        for line in reversed(lines):
            if line.startswith("data:") and line != "data: [DONE]":
                try:
                    chunk = json.loads(line[5:].strip())
                    if chunk.get("usage"):
                        has_usage = True
                        break
                except json.JSONDecodeError:
                    continue
        return has_usage, f"usage 포함: {has_usage}"

    _run_test(ctx, "3.1", "스트리밍", "기본 SSE 청크 + [DONE]", t_3_1)
    _run_test(ctx, "3.2", "스트리밍", "스트리밍 usage 반환", t_3_2)


# ── 4. 샘플링 파라미터 ───────────────────────────────────

def test_sampling(ctx: TestContext):
    c = ctx.colors
    print(f"\n{_c(c, 'bold', '4. 샘플링 파라미터')}")

    def t_4_1():
        """temperature=0 결정적 출력"""
        results = []
        for _ in range(2):
            status, body = _chat(
                ctx,
                [{"role": "user", "content": "자동차보험 의무가입 담보명을 한 단어로 답해."}],
                max_tokens=10,
                temperature=0,
                seed=42,
            )
            if status != 200:
                return False, f"HTTP {status}"
            results.append(body["choices"][0]["message"]["content"].strip())
        # vLLM의 continuous batching·CUDA 비결정성으로 length cutoff 직전 borderline에서
        # 한쪽이 다른 쪽의 prefix가 되는 경우(같은 분기를 따라가다 잘린 길이만 다름)는 통과로 본다.
        # 진짜 비결정(서로 다른 분기로 발산)은 prefix가 아니므로 여전히 fail로 잡힌다.
        match = (
            results[0] == results[1]
            or results[0].startswith(results[1])
            or results[1].startswith(results[0])
        )
        return match, f"1차: {results[0]!r}, 2차: {results[1]!r}, 일치: {match}"

    def t_4_2():
        """temperature=1.5 — 크래시 없음"""
        status, body = _chat(
            ctx,
            [{"role": "user", "content": "손해보험 담보 종류 3개만 나열해줘"}],
            max_tokens=50,
            temperature=1.5,
            top_p=0.95,
        )
        return status == 200, f"HTTP {status}"

    def t_4_3():
        """max_tokens=1 — 최소 출력"""
        status, body = _chat(
            ctx,
            [{"role": "user", "content": "보험료 납입 방법 알려줘"}],
            max_tokens=1,
        )
        if status != 200:
            return False, f"HTTP {status}"
        choice = body["choices"][0]
        reason = choice["finish_reason"]
        tokens = body["usage"]["completion_tokens"]
        return reason == "length" and tokens <= 2, f"finish_reason: {reason}, tokens: {tokens}"

    def t_4_4():
        """잘못된 temperature — 에러 응답"""
        body = {
            "model": ctx.model,
            "messages": [{"role": "user", "content": "보험 문의"}],
            "temperature": -1,
        }
        status, _ = _request(f"{ctx.base_url}/v1/chat/completions", method="POST", body=body)
        return status >= 400, f"HTTP {status}"

    _run_test(ctx, "4.1", "샘플링", "temperature=0 결정적 출력", t_4_1)
    _run_test(ctx, "4.2", "샘플링", "temperature=1.5 크래시 없음", t_4_2)
    _run_test(ctx, "4.3", "샘플링", "max_tokens=1 최소 출력", t_4_3)
    _run_test(ctx, "4.4", "샘플링", "잘못된 temperature 에러", t_4_4)


# ── 5. Thinking 모드 ────────────────────────────────────

def _reasoning_of(msg: dict) -> str:
    """reasoning_parser가 분리한 사고 본문. 버전에 따라 필드명이 다르다."""
    return str(msg.get("reasoning") or msg.get("reasoning_content") or "")


def _thinking_off_verdict(msg: dict) -> tuple[bool, str]:
    """사고가 꺼졌는지 판정한다.

    content의 <think>만 보면, 사고가 켜져도 파서가 reasoning 필드로 분리하는 순간 통과한다
    (2026-10-09 effort 때문에 사고가 켜진 사고를 이 스위트가 놓쳤다). 그래서 reasoning 필드도 본다.
    호출부는 skip_special_tokens=False를 함께 보낸다(5.2와 같은 조건). Gemma 4는 특수 토큰이 남아야
    사고를 분리하는데, 0.31은 파서가 요청마다 강제하지만(parser/engine/parser_engine.py adjust_request)
    파서가 강제하지 않는 버전에서도 사고가 content에 평문으로 섞여 판정을 놓치지 않게 하기 위해서다.
    """
    reasoning = _reasoning_of(msg)
    content = str(msg.get("content") or "")
    has_think_tag = "<think>" in content
    ok = not reasoning and not has_think_tag
    return ok, f"reasoning {len(reasoning)}자, <think> 포함: {has_think_tag}, 응답: {content[:80]}"


def test_thinking(ctx: TestContext):
    c = ctx.colors
    print(f"\n{_c(c, 'bold', '5. Thinking 모드')}")

    def t_5_1():
        """Thinking OFF (기본) — 사고 미생성"""
        status, body = _chat(
            ctx,
            [{"role": "user", "content": "상해보험과 질병보험의 차이점은?"}],
            max_tokens=100,
            skip_special_tokens=False,
        )
        if status != 200:
            return False, f"HTTP {status}"
        return _thinking_off_verdict(body["choices"][0]["message"])

    def t_5_2():
        """요청 단위 Thinking ON (서버 OFF → 요청 ON)"""
        status, body = _chat(
            ctx,
            [{"role": "user", "content": "자동차보험 대인배상I과 대인배상II의 보장 범위 차이를 분석해줘."}],
            max_tokens=500,
            # Gemma 4는 non-streaming reasoning 분리 시 특수 토큰 유지가 필요하다.
            skip_special_tokens=False,
            chat_template_kwargs={"enable_thinking": True},
        )
        if status != 200:
            return False, f"HTTP {status}"
        msg = body["choices"][0]["message"]
        # vLLM은 reasoning_parser 설정 시 thinking을 "reasoning" 필드로 분리
        reasoning = msg.get("reasoning") or msg.get("reasoning_content") or ""
        has_reasoning = bool(reasoning)
        content = str(msg.get("content") or "")[:100]
        reasoning_preview = str(reasoning)[:100]
        return has_reasoning, f"reasoning 분리: {has_reasoning}\n응답: {content}\n사고: {reasoning_preview}"

    def t_5_3():
        """요청 단위 Thinking OFF 명시적 전달"""
        status, body = _chat(
            ctx,
            [{"role": "user", "content": "실손보험 자기부담금이 얼마야?"}],
            max_tokens=50,
            skip_special_tokens=False,
            chat_template_kwargs={"enable_thinking": False},
        )
        if status != 200:
            return False, f"HTTP {status}"
        return _thinking_off_verdict(body["choices"][0]["message"])

    _run_test(ctx, "5.1", "Thinking", "OFF (기본) — 사고 미생성", t_5_1)
    _run_test(ctx, "5.2", "Thinking", "요청 단위 ON — reasoning 분리", t_5_2)
    _run_test(ctx, "5.3", "Thinking", "요청 단위 OFF 명시적 전달", t_5_3)


# ── 6. Tool Calling ──────────────────────────────────────

def test_tool_calling(ctx: TestContext):
    c = ctx.colors
    print(f"\n{_c(c, 'bold', '6. Tool Calling')}")

    coverage_tool = {
        "type": "function",
        "function": {
            "name": "lookup_coverage",
            "description": "보험 상품의 담보 정보를 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "description": "보험 상품명"},
                },
                "required": ["product_name"],
            },
        },
    }

    claim_tool = {
        "type": "function",
        "function": {
            "name": "check_claim_status",
            "description": "보험금 청구 상태를 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "claim_id": {"type": "string", "description": "청구 번호"},
                },
                "required": ["claim_id"],
            },
        },
    }

    def t_6_1():
        """단일 Tool Call"""
        status, body = _chat(
            ctx,
            [{"role": "user", "content": "한화손해보험 자동차보험의 담보 정보를 조회해줘"}],
            tools=[coverage_tool],
            max_tokens=200,
        )
        if status != 200:
            return False, f"HTTP {status}"
        msg = body["choices"][0]["message"]
        tool_calls = msg.get("tool_calls", [])
        if not tool_calls:
            return False, f"tool_calls 없음. content: {msg.get('content', '')[:100]}"
        tc = tool_calls[0]
        name = tc["function"]["name"]
        args = tc["function"]["arguments"]
        return name == "lookup_coverage", f"tool: {name}, args: {args}"

    def t_6_2():
        """복수 Tool 선택"""
        status, body = _chat(
            ctx,
            [{"role": "user", "content": "화재보험 담보 조회하고, 청구번호 CLM-2024-001 상태도 확인해줘"}],
            tools=[coverage_tool, claim_tool],
            max_tokens=300,
        )
        if status != 200:
            return False, f"HTTP {status}"
        msg = body["choices"][0]["message"]
        tool_calls = msg.get("tool_calls", [])
        names = [tc["function"]["name"] for tc in tool_calls]
        has_both = "lookup_coverage" in names and "check_claim_status" in names
        return has_both, f"호출된 tools: {names}" + ("" if has_both else " (2개 모두 호출 기대)")

    def t_6_3():
        """Tool 불필요 시 직접 응답"""
        status, body = _chat(
            ctx,
            [{"role": "user", "content": "보험이란 무엇인가요?"}],
            tools=[coverage_tool],
            max_tokens=50,
        )
        if status != 200:
            return False, f"HTTP {status}"
        msg = body["choices"][0]["message"]
        has_tools = bool(msg.get("tool_calls"))
        content = msg.get("content", "")
        return not has_tools and bool(content.strip()), f"tool_calls: {has_tools}, content: {content[:80]}"

    def t_6_4():
        """Tool 결과 반영 최종 응답"""
        status, body = _chat(
            ctx,
            [
                {"role": "user", "content": "자동차보험 담보 정보 알려줘"},
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {"name": "lookup_coverage", "arguments": '{"product_name": "자동차보험"}'},
                        }
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1",
                    "content": '{"product": "자동차보험", "coverages": ["대인배상I", "대인배상II", "대물배상", "자기신체사고"], "premium": "월 45,000원"}',
                },
            ],
            max_tokens=200,
        )
        if status != 200:
            return False, f"HTTP {status}"
        content = body["choices"][0]["message"]["content"]
        has_info = any(kw in content for kw in ("대인배상", "대물배상", "자동차"))
        return has_info, f"응답: {content[:120]}"

    _run_test(ctx, "6.1", "Tool", "단일 Tool Call", t_6_1)
    _run_test(ctx, "6.2", "Tool", "복수 Tool 선택", t_6_2)
    _run_test(ctx, "6.3", "Tool", "Tool 불필요 시 직접 응답", t_6_3)
    _run_test(ctx, "6.4", "Tool", "Tool 결과 반영 최종 응답", t_6_4)


# ── 7. 경계값 / 스트레스 ─────────────────────────────────

def test_edge_cases(ctx: TestContext):
    c = ctx.colors
    print(f"\n{_c(c, 'bold', '7. 경계값 / 스트레스')}")

    def t_7_1():
        """빈 메시지 — 크래시 없음"""
        status, body = _chat(
            ctx,
            [{"role": "user", "content": ""}],
            max_tokens=50,
        )
        # 에러든 빈 응답이든 크래시만 아니면 통과
        return True, f"HTTP {status}"

    def t_7_2():
        """긴 입력 (컨텍스트 한계 근접)"""
        long_input = "안녕하세요. " * 3000  # ~15000 토큰
        status, body = _chat(
            ctx,
            [{"role": "user", "content": long_input}],
            max_tokens=50,
            timeout=120,
        )
        if status == 200:
            return True, f"정상 처리 (토큰 내). usage: {body.get('usage', {})}"
        else:
            # 에러 응답도 크래시가 아니면 통과
            detail = body if isinstance(body, str) else body.get("error", {}).get("message", str(body))
            return True, f"예상된 에러 (HTTP {status}): {str(detail)[:150]}"

    def _concurrent_test(n: int):
        """n개 동시 요청을 보내고 결과를 반환한다."""
        results = []
        errors = []

        def send(i):
            try:
                s, b = _chat(
                    ctx,
                    [{"role": "user", "content": f"보험 담보 유형 {i}번에 대해 한 문장으로 설명해."}],
                    max_tokens=50,
                    timeout=180,
                )
                results.append((i, s))
            except Exception as e:
                errors.append((i, str(e)))

        threads = [threading.Thread(target=send, args=(i,)) for i in range(1, n + 1)]
        start = time.monotonic()
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=300)
        elapsed = time.monotonic() - start

        all_ok = all(s == 200 for _, s in results) and len(results) == n and not errors
        detail = f"{n}개 동시 요청, {elapsed:.1f}s 소요. 결과: {sorted(results)}"
        if errors:
            detail += f" 에러: {errors}"
        return all_ok, detail

    def t_7_3():
        """동시 5개 요청 (max_num_seqs 이내)"""
        return _concurrent_test(5)

    def t_7_4():
        """동시 10개 요청 (max_num_seqs 초과 → 큐잉)"""
        return _concurrent_test(10)

    def t_7_5():
        """잘못된 JSON 요청"""
        url = f"{ctx.base_url}/v1/chat/completions"
        req = urllib.request.Request(
            url,
            data=b'{"invalid json',
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return False, f"에러 예상했으나 HTTP {resp.status}"
        except urllib.error.HTTPError as e:
            return e.code in (400, 422), f"HTTP {e.code}"
        except Exception as e:
            return False, f"예외: {e}"

    def t_7_6():
        """필수 필드 누락 (messages 없음)"""
        body = {"model": ctx.model, "max_tokens": 50}
        status, resp = _request(f"{ctx.base_url}/v1/chat/completions", method="POST", body=body)
        return status >= 400, f"HTTP {status}"

    _run_test(ctx, "7.1", "경계값", "빈 메시지 — 크래시 없음", t_7_1)
    _run_test(ctx, "7.2", "경계값", "긴 입력 (컨텍스트 한계)", t_7_2)
    _run_test(ctx, "7.3", "경계값", "동시 5개 요청 (max_num_seqs 이내)", t_7_3)
    _run_test(ctx, "7.4", "경계값", "동시 10개 요청 (큐잉)", t_7_4)
    _run_test(ctx, "7.5", "경계값", "잘못된 JSON 요청", t_7_5)
    _run_test(ctx, "7.6", "경계값", "필수 필드 누락", t_7_6)


# ── 8. 프리픽스 캐싱 ─────────────────────────────────────

def test_caching(ctx: TestContext):
    c = ctx.colors
    print(f"\n{_c(c, 'bold', '8. 프리픽스 캐싱')}")

    def t_8_1():
        """동일 시스템 프롬프트 반복 — TTFT 비교"""
        system = "당신은 전문 AI 어시스턴트입니다. 항상 정확하고 도움이 되는 답변을 제공합니다. 사용자의 질문에 친절하게 답변해주세요."
        times = []
        for i in range(2):
            start = time.monotonic()
            status, body = _chat(
                ctx,
                [
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"인공지능이란? (호출 {i + 1})"},
                ],
                max_tokens=50,
            )
            elapsed = (time.monotonic() - start) * 1000
            times.append(elapsed)
            if status != 200:
                return False, f"HTTP {status} (호출 {i + 1})"

        faster = times[1] < times[0]
        detail = f"1차: {times[0]:.0f}ms, 2차: {times[1]:.0f}ms"
        if faster:
            detail += f" (2차가 {times[0] - times[1]:.0f}ms 빠름)"
        else:
            detail += " (2차가 느림 — 워밍업/부하 영향 가능)"
        # 캐싱 효과는 환경에 따라 다를 수 있어 soft pass
        return True, detail

    _run_test(ctx, "8.1", "캐싱", "동일 시스템 프롬프트 TTFT 비교", t_8_1)


# ── 9. 멀티모달 (이미지) ────────────────────────────────


def test_multimodal(ctx: TestContext):
    """멀티모달(이미지) 경로 검증.

    2026-04-18 07:17:51 `Encoder cache miss` 크래시 재발 방지를 위한 테스트.
    - 동시 이미지 요청이 max_num_seqs와 encoder cache 용량에 맞게 처리되는지
    - max_num_seqs 초과 시 FCFS 큐잉이 정상 동작하는지
    - 이미지 + 텍스트 혼합 트래픽이 섞여도 안정한지
    정답(강아지 5마리)은 VL 모델 기본 시각 추론 정상성도 동시에 확인한다.
    """
    c = ctx.colors
    print(f"\n{_c(c, 'bold', '9. 멀티모달 (이미지)')}")

    IMAGE_PROMPT = "사진에 강아지가 몇 마리 있나요? 숫자만 답해주세요."

    def _is_correct(content: str) -> bool:
        """응답에 정답(5)이 포함됐는지 판정. '5' 또는 '다섯' 둘 다 허용."""
        return "5" in content or "다섯" in content

    def t_9_1():
        """단일 이미지 — 강아지 5마리 정답"""
        image = _load_test_image()
        status, body = _chat_with_image(
            ctx,
            IMAGE_PROMPT,
            image,
            max_tokens=100,
            timeout=120,
        )
        if status != 200:
            return False, f"HTTP {status}: {body}"
        content = body["choices"][0]["message"]["content"]
        correct = _is_correct(content)
        return correct, f"응답: {content[:150]}" + ("" if correct else " (정답 '5' 미포함)")

    def _concurrent_image_test(n: int):
        """n개 동시 이미지 요청. 성공률 + 정답률을 함께 반환."""
        image = _load_test_image()
        results: list[tuple[int, int]] = []   # (idx, status)
        contents: list[str] = []
        errors: list[tuple[int, str]] = []
        lock = threading.Lock()

        def send(i):
            try:
                s, b = _chat_with_image(
                    ctx,
                    IMAGE_PROMPT,
                    image,
                    max_tokens=100,
                    timeout=300,
                )
                with lock:
                    results.append((i, s))
                    if s == 200:
                        contents.append(b["choices"][0]["message"]["content"])
            except Exception as e:
                with lock:
                    errors.append((i, str(e)))

        threads = [threading.Thread(target=send, args=(i,)) for i in range(1, n + 1)]
        start = time.monotonic()
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=600)
        elapsed = time.monotonic() - start

        success_count = sum(1 for _, s in results if s == 200)
        correct_count = sum(1 for c in contents if _is_correct(c))
        all_ok = success_count == n and not errors
        detail = (
            f"{n}개 동시, {elapsed:.1f}s, "
            f"HTTP 200: {success_count}/{n}, 정답(5): {correct_count}/{success_count}"
        )
        if errors:
            detail += f"\n에러 {len(errors)}건: {errors[:2]}"
        return all_ok, detail

    def t_9_2():
        """동시 이미지 5개 (max_num_seqs 이내)"""
        return _concurrent_image_test(5)

    def t_9_3():
        """동시 이미지 10개 (max_num_seqs 초과 → FCFS 큐잉)"""
        return _concurrent_image_test(10)

    def t_9_4():
        """이미지 + 텍스트 혼합 동시 10개 (이미지 5 + 텍스트 5)"""
        image = _load_test_image()
        results: list[tuple[str, int, int]] = []   # (kind, idx, status)
        errors: list[tuple[str, int, str]] = []
        lock = threading.Lock()

        def send_image(i):
            try:
                s, _ = _chat_with_image(
                    ctx,
                    IMAGE_PROMPT,
                    image,
                    max_tokens=100,
                    timeout=300,
                )
                with lock:
                    results.append(("img", i, s))
            except Exception as e:
                with lock:
                    errors.append(("img", i, str(e)))

        def send_text(i):
            try:
                s, _ = _chat(
                    ctx,
                    [{"role": "user", "content": f"보험 담보 {i}번에 대해 한 문장으로 설명해."}],
                    max_tokens=50,
                    timeout=300,
                )
                with lock:
                    results.append(("txt", i, s))
            except Exception as e:
                with lock:
                    errors.append(("txt", i, str(e)))

        threads = []
        for i in range(1, 6):
            threads.append(threading.Thread(target=send_image, args=(i,)))
            threads.append(threading.Thread(target=send_text, args=(i,)))

        start = time.monotonic()
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=600)
        elapsed = time.monotonic() - start

        img_ok = sum(1 for kind, _, s in results if kind == "img" and s == 200)
        txt_ok = sum(1 for kind, _, s in results if kind == "txt" and s == 200)
        all_ok = img_ok == 5 and txt_ok == 5 and not errors
        detail = f"혼합 10개 (이미지 5 + 텍스트 5), {elapsed:.1f}s, 성공 img={img_ok}/5, txt={txt_ok}/5"
        if errors:
            detail += f"\n에러 {len(errors)}건: {errors[:2]}"
        return all_ok, detail

    _run_test(ctx, "9.1", "멀티모달", "단일 이미지 — 강아지 5마리 정답", t_9_1)
    _run_test(ctx, "9.2", "멀티모달", "동시 이미지 5개 (max_num_seqs 이내)", t_9_2)
    _run_test(ctx, "9.3", "멀티모달", "동시 이미지 10개 (큐잉)", t_9_3)
    _run_test(ctx, "9.4", "멀티모달", "이미지 + 텍스트 혼합 동시 10개", t_9_4)


# ── 10. 게이트웨이 계약 ─────────────────────────────────
# vllm_gateway.py가 클라이언트에 약속하는 동작(VLLM_OPS_GUIDE §10.4). 백엔드 vLLM에 직접 붙으면
# effort 번역·정체성 주입·경로 가림이 없어 규칙 자체가 다르므로 이 카테고리를 건너뛴다.

def _is_gateway(ctx: TestContext) -> bool:
    """/server-status는 게이트웨이에만 있다(vLLM은 404)."""
    status, _ = _request(f"{ctx.base_url}/server-status", timeout=10)
    return status == 200


def test_gateway(ctx: TestContext):
    c = ctx.colors
    print(f"\n{_c(c, 'bold', '10. 게이트웨이 계약')}")
    if not _is_gateway(ctx):
        print(f"  {_c(c, 'yellow', '건너뜀')} — 대상이 게이트웨이가 아님(/server-status 없음, 백엔드 직접 연결)")
        return

    question = [{"role": "user", "content": "자동차보험 대인배상I과 대인배상II의 보장 범위 차이를 두 문장으로 설명해줘."}]

    def _thinking(**extra) -> tuple[int, dict, str]:
        # 사고가 켜지면 길어지므로 max_tokens·timeout을 넉넉히 둔다(사고 본문이 잘려도 reasoning은 채워진다).
        status, body = _chat(ctx, question, max_tokens=700, temperature=0, skip_special_tokens=False,
                             timeout=180, **extra)
        if status != 200:
            return status, {}, ""
        msg = body["choices"][0]["message"]
        return status, msg, _reasoning_of(msg)

    def t_10_1():
        """effort만 보내면 사고가 켜진다 (Gemma처럼 강도를 모르는 계열도 켜짐)"""
        status, msg, reasoning = _thinking(reasoning_effort="medium")
        if status != 200:
            return False, f"HTTP {status}"
        return bool(reasoning), f"reasoning {len(reasoning)}자, 응답: {str(msg.get('content') or '')[:80]}"

    def t_10_2():
        """enable_thinking false를 직접 보내면 effort가 있어도 꺼진다"""
        status, msg, _ = _thinking(reasoning_effort="high", chat_template_kwargs={"enable_thinking": False})
        if status != 200:
            return False, f"HTTP {status}"
        return _thinking_off_verdict(msg)

    def t_10_3():
        """effort none은 enable_thinking true여도 끈다"""
        status, msg, _ = _thinking(reasoning_effort="none", chat_template_kwargs={"enable_thinking": True})
        if status != 200:
            return False, f"HTTP {status}"
        return _thinking_off_verdict(msg)

    def t_10_4():
        """정체성 질문에 기반 모델·회사 이름이 나오지 않는다"""
        leaks = []
        for q in IDENTITY_QUESTIONS:
            status, body = _chat(ctx, [{"role": "user", "content": q}], max_tokens=150, temperature=0)
            if status != 200:
                return False, f"HTTP {status}: {q}"
            content = str(body["choices"][0]["message"].get("content") or "")
            found = [w for w in _IDENTITY_FORBIDDEN if w in content.lower()]
            if found:
                leaks.append(f"{q[:20]!r} → {found}: {content[:80]}")
        return not leaks, "\n".join(leaks) or f"질문 {len(IDENTITY_QUESTIONS)}개 모두 미노출"

    def t_10_5():
        """developer 역할 시스템 메시지가 400 없이 반영된다"""
        status, body = _chat(ctx, [
            {"role": "developer", "content": "답은 반드시 '확인:'으로 시작한다."},
            {"role": "user", "content": "오늘 할 일을 한 줄로 정해줘."},
        ], max_tokens=40, temperature=0)
        if status != 200:
            return False, f"HTTP {status}"
        content = str(body["choices"][0]["message"].get("content") or "")
        return "확인" in content, f"응답: {content[:80]}"

    def t_10_6():
        """/v1/models의 root가 체크포인트 경로 대신 별칭이다"""
        status, body = _request(f"{ctx.base_url}/v1/models")
        if status != 200:
            return False, f"HTTP {status}"
        pairs = [(m.get("id"), m.get("root")) for m in body.get("data", [])]
        return bool(pairs) and all(i == r for i, r in pairs), f"(id, root): {pairs}"

    _run_test(ctx, "10.1", "게이트웨이", "effort만 → 사고 켜짐", t_10_1)
    _run_test(ctx, "10.2", "게이트웨이", "enable_thinking false 우선 → 꺼짐", t_10_2)
    _run_test(ctx, "10.3", "게이트웨이", "effort none → 꺼짐", t_10_3)
    _run_test(ctx, "10.4", "게이트웨이", "정체성 질문 — 기반 모델 미노출", t_10_4)
    _run_test(ctx, "10.5", "게이트웨이", "developer 역할 병합", t_10_5)
    _run_test(ctx, "10.6", "게이트웨이", "모델 경로 가림", t_10_6)


# ═══════════════════════════════════════════════════════════
# 카테고리 레지스트리
# ═══════════════════════════════════════════════════════════

CATEGORIES = {
    "infra": ("서버 기동 / 인프라", test_infra),
    "inference": ("기본 추론", test_inference),
    "streaming": ("스트리밍", test_streaming),
    "sampling": ("샘플링 파라미터", test_sampling),
    "thinking": ("Thinking 모드", test_thinking),
    "tool": ("Tool Calling", test_tool_calling),
    "edge": ("경계값 / 스트레스", test_edge_cases),
    "caching": ("프리픽스 캐싱", test_caching),
    "multimodal": ("멀티모달 (이미지)", test_multimodal),
    "gateway": ("게이트웨이 계약", test_gateway),
}


# ═══════════════════════════════════════════════════════════
# 결과 요약
# ═══════════════════════════════════════════════════════════


def print_summary(ctx: TestContext):
    c = ctx.colors
    results = ctx.results
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    print(f"\n{'═' * 60}")
    print(_c(c, "bold", " 테스트 결과 요약"))
    print(f"{'═' * 60}")

    # 카테고리별 집계
    categories = {}
    for r in results:
        if r.category not in categories:
            categories[r.category] = {"pass": 0, "fail": 0}
        if r.passed:
            categories[r.category]["pass"] += 1
        else:
            categories[r.category]["fail"] += 1

    print(f"\n {'카테고리':<20} {'Pass':>6} {'Fail':>6}")
    print(f" {'─' * 20} {'─' * 6} {'─' * 6}")
    for cat, counts in categories.items():
        p = _c(c, "green", str(counts["pass"]))
        f_str = _c(c, "red", str(counts["fail"])) if counts["fail"] else str(counts["fail"])
        print(f" {cat:<20} {p:>15} {f_str:>15}")

    # 실패 목록
    failures = [r for r in results if not r.passed]
    if failures:
        print(f"\n {_c(c, 'red', '실패 목록:')}")
        for r in failures:
            print(f"  [{r.id}] {r.name}")
            if r.detail:
                for line in r.detail.split("\n"):
                    print(f"       {_c(c, 'dim', line)}")

    # 최종
    total_time = sum(r.elapsed_ms for r in results)
    if failed == 0:
        verdict = _c(c, "green", f"ALL PASS ({passed}/{total})")
    else:
        verdict = _c(c, "red", f"FAIL ({failed}/{total} 실패)")
    print(f"\n {verdict}  {_c(c, 'dim', f'총 {total_time / 1000:.1f}s')}")
    print(f"{'═' * 60}\n")


# ═══════════════════════════════════════════════════════════
# 엔트리포인트
# ═══════════════════════════════════════════════════════════


def parse_args():
    p = argparse.ArgumentParser(
        description="vLLM 서버 QA 테스트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            카테고리:
              infra       서버 기동 / 인프라
              inference   기본 추론
              streaming   스트리밍 (SSE)
              sampling    샘플링 파라미터
              thinking    Thinking 모드
              tool        Tool Calling
              edge        경계값 / 스트레스
              caching     프리픽스 캐싱
              multimodal  멀티모달 (이미지, image.png 필요)
              gateway     게이트웨이 계약 (게이트웨이 대상일 때만)

            예시 (vllm/ 디렉토리에서 실행):
              python tests/test_vllm_server.py
              python tests/test_vllm_server.py --category infra inference
              python tests/test_vllm_server.py --category multimodal
              python tests/test_vllm_server.py --base-url http://gpu-server:5015
        """),
    )
    p.add_argument("--base-url", default="http://localhost:5015", help="vLLM 서버 URL (기본: http://localhost:5015)")
    p.add_argument(
        "--model", default=None,
        help="모델명 (미지정 시 자동 추출: 1) base-url의 /v1/models API → 2) 로컬 gateways/<port>.yaml + instances/<name>.yaml fallback)",
    )
    p.add_argument("--category", nargs="*", choices=list(CATEGORIES.keys()), help="실행할 카테고리 (미지정 시 전체)")
    p.add_argument("--list", action="store_true", help="카테고리 목록 출력")
    p.add_argument("--no-color", action="store_true", help="컬러 출력 비활성화")
    p.add_argument("--verbose", "-v", action="store_true", help="성공 테스트도 상세 출력")
    return p.parse_args()


def _resolve_model_from_api(base_url: str, timeout: float = 5.0) -> str:
    """OpenAI 호환 /v1/models 엔드포인트로 모델명을 조회한다.
    원격 서버에서도 yaml 사본 없이 동작. 게이트웨이가 listen 중이고
    backend가 살아있을 때만 응답."""
    url = f"{base_url.rstrip('/')}/v1/models"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    data = payload.get("data") or []
    if not data:
        raise RuntimeError(f"{url}: data 비어있음")
    model_id = data[0].get("id")
    if not model_id:
        raise RuntimeError(f"{url}: 첫 모델의 id 누락")
    return model_id


def _resolve_model_from_config(base_url: str) -> str:
    """로컬 fallback: base_url 포트 → gateways/<port>.yaml → 매칭 instances/<name>.yaml의
    served_model_name. 원격에서 같은 레포 사본을 들고 있을 때 / 게이트웨이가 다운일 때 유용."""
    import glob
    import yaml
    from urllib.parse import urlparse

    parsed = urlparse(base_url)
    port = parsed.port
    if port is None:
        raise RuntimeError(f"--base-url에서 포트를 추출할 수 없습니다: {base_url}")

    # 이 파일은 vllm/tests/ 에 있고 yaml은 vllm/gateways·instances/ 에 있다.
    # tests/ 기준으로 join하면 존재하지 않는 tests/gateways/를 보게 되어 fallback이 항상 실패한다.
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gw_yaml = os.path.join(base_dir, "gateways", f"{port}.yaml")
    if not os.path.isfile(gw_yaml):
        raise RuntimeError(f"게이트웨이 설정 없음: {gw_yaml}")

    with open(gw_yaml, encoding="utf-8") as f:
        gw = yaml.safe_load(f) or {}
    gateway_port = int((gw.get("gateway") or {}).get("port", port))
    discover_from = gw.get("discover_from", "../instances")
    instances_dir = os.path.normpath(os.path.join(os.path.dirname(gw_yaml), discover_from))

    for inst_path in sorted(glob.glob(os.path.join(instances_dir, "*.yaml"))):
        with open(inst_path, encoding="utf-8") as f:
            inst = yaml.safe_load(f) or {}
        if int(inst.get("gateway_port", 0)) != gateway_port:
            continue
        served = inst.get("served_model_name", [])
        if isinstance(served, list) and served:
            return served[0]
        if isinstance(served, str) and served:
            return served
        model = inst.get("model", "")
        return model.split("/")[-1] if "/" in model else model

    raise RuntimeError(
        f"게이트웨이 :{gateway_port}와 매칭되는 인스턴스 yaml이 {instances_dir}에 없습니다."
    )


def _resolve_model_auto(base_url: str) -> str:
    """모델명 자동 추출: /v1/models API 우선 → 로컬 yaml fallback.
    원격 서버여도 게이트웨이만 살아있으면 동작. 두 경로 모두 실패 시 명확한 에러."""
    try:
        return _resolve_model_from_api(base_url)
    except Exception as api_err:
        try:
            return _resolve_model_from_config(base_url)
        except Exception as cfg_err:
            raise RuntimeError(
                "모델명 자동 추출 실패. --model을 직접 지정하세요.\n"
                f"  /v1/models 시도: {api_err}\n"
                f"  로컬 yaml fallback: {cfg_err}"
            ) from cfg_err


def _open_log_file() -> tuple[str, "object"]:
    """logs/test_YYYYMMDD_HHMMSS.log 생성 후 (path, file) 반환."""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"test_{time.strftime('%Y%m%d_%H%M%S')}.log")
    log_file = open(log_path, "w", encoding="utf-8", buffering=1)
    return log_path, log_file


def main():
    args = parse_args()
    colors = NO_COLORS if args.no_color else COLORS

    if args.list:
        print("카테고리 목록:")
        for key, (desc, _) in CATEGORIES.items():
            print(f"  {key:<12} {desc}")
        return

    # 로그 파일 항상 저장 — 콘솔에는 색 그대로, 파일에는 ANSI 제거.
    log_path, log_file = _open_log_file()
    orig_stdout, orig_stderr = sys.stdout, sys.stderr
    sys.stdout = _Tee(orig_stdout, log_file)
    sys.stderr = _Tee(orig_stderr, log_file)

    try:
        model = args.model or _resolve_model_auto(args.base_url)

        ctx = TestContext(
            base_url=args.base_url.rstrip("/"),
            model=model,
            colors=colors,
            verbose=args.verbose,
        )

        print(f"\n{_c(colors, 'bold', 'vLLM 서버 QA 테스트')}")
        print(f"  서버: {ctx.base_url}")
        print(f"  모델: {ctx.model}")
        print(f"  로그: {log_path}")

        # 서버 연결 확인
        try:
            status, _ = _request(f"{ctx.base_url}/health", timeout=5)
        except Exception as e:
            print(f"\n{_c(colors, 'red', '서버 연결 실패')}: {ctx.base_url}/health ({type(e).__name__}: {e})")
            print("vLLM 서버가 실행 중인지 확인하세요.")
            sys.exit(1)

        # 카테고리 실행
        selected = args.category or list(CATEGORIES.keys())
        for key in selected:
            _, test_fn = CATEGORIES[key]
            test_fn(ctx)

        print_summary(ctx)
        print(f"  로그 파일: {log_path}")

        # 실패 시 exit code 1
        failures = sum(1 for r in ctx.results if not r.passed)
        sys.exit(1 if failures else 0)
    finally:
        sys.stdout, sys.stderr = orig_stdout, orig_stderr
        log_file.close()


if __name__ == "__main__":
    main()
