#!/usr/bin/env python3
"""vLLM STT 서버 QA 테스트 (smoke).

STT 서버 배포 후 기능 검증을 위한 최소 테스트 스위트.
test_vllm_server.py와 동일 구조이며, multipart audio transcription 호출용으로 단순화.
외부 의존성 없이 Python 표준 라이브러리만 사용.

테스트 단계:
  1. 인프라: /health, /v1/models, 잘못된 엔드포인트 응답 확인.
  2. Transcriptions: 기본 호출, language 명시(reference 언어 자동 hint), response_format=text, 잘못된 모델명 확인.
  3. 경계값: file 필드 누락, 잘못된 multipart 본문 확인.

사용법 (stt/ 디렉토리에서 실행):
    # 기본 (localhost:5017 = voxtral 게이트웨이)
    python tests/test_stt_server.py

    # whisper_v3 단독 (:7171 직접 노출, 비교 PoC)
    python tests/test_stt_server.py --base-url http://localhost:7171

    # qwen3_asr 단독 (:7170 직접 노출, 비교 PoC)
    python tests/test_stt_server.py --base-url http://localhost:7170

    # 특정 카테고리만 실행
    python tests/test_stt_server.py --category infra transcription

    # 카테고리 목록 확인
    python tests/test_stt_server.py --list

음성 샘플 (default):
  tests/zeroth_ko_sample.flac — HuggingFace `Bingsu/zeroth-korean` (Apache 2.0) test split 첫 샘플.
  16kHz mono FLAC native 인코딩. 정답 텍스트: tests/zeroth_ko_sample.txt.

※ 16kHz mono 사용 이유 — vLLM이 음성을 ASR 모델 expected SR(Whisper=16kHz)로 강제 resample하는데
   resample 경로(`vllm.multimodal.audio.resample_audio_pyav`)가 PyAV에 의존한다. PyAV가 호스트/
   컨테이너에 없으면 native_sr ≠ 16kHz인 음성은 `Invalid or unsupported audio file.` 400으로 거부됨.
   0.20.2에서 확인했고, 0.31.0도 soundfile로 읽은 음성은 같은 함수로 리샘플한다(media/audio.py:246, 소스 대조만
   했고 STT 실행 시험은 안 함). 서버 이미지에는 av가 들어 있다(aws/requirements.txt).
   16kHz mono native 자산은 resample을 트리거하지 않으므로 PyAV 의존성 없이 안전. 임의 음성 사용 시
   동일 조건(16kHz mono)으로 사전 변환 후 `--audio`로 전달 권장.

정답 텍스트 매칭:
  audio_path 옆에 같은 basename + `.txt` 파일이 있으면 reference로 자동 로드.
  reference에 한국어 음절(가-힣)이 있으면 응답과 음절 overlap ≥ 50%를 PASS 기준으로 사용.
  음절 미존재(타 언어)이거나 reference 부재 시 응답 비어있지 않음만 확인 (smoke 본질 유지).
"""
import argparse
import http.client  # noqa: F401  (urllib 내부 사용 — 명시적 import 보존)
import json
import os
import re
import sys
import textwrap
import time
import traceback
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass, field

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
    audio_path: str
    reference: str | None  # 정답 텍스트 (있으면 한국어 음절 overlap 기반 매칭)
    colors: dict
    results: list = field(default_factory=list)
    verbose: bool = False


# ── HTTP 헬퍼 ────────────────────────────────────────────

# 마지막 요청/응답 메타. _run_test가 fail 시 자동으로 detail에 부착.
_LAST_REQUEST: dict | None = None
_LAST_RESPONSE: dict | None = None


def _record_request(method: str, url: str, body_summary) -> None:
    global _LAST_REQUEST
    _LAST_REQUEST = {"method": method, "url": url, "body": body_summary}


def _record_response(status, body) -> None:
    global _LAST_RESPONSE
    _LAST_RESPONSE = {"status": status, "body": body}


def _reset_request_log() -> None:
    global _LAST_REQUEST, _LAST_RESPONSE
    _LAST_REQUEST = None
    _LAST_RESPONSE = None


def _request(
    url: str,
    *,
    method: str = "GET",
    body: dict | None = None,
    timeout: float = 30,
) -> tuple[int, dict | str]:
    """JSON 요청 헬퍼 (multipart 아닌 일반 GET/POST)."""
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


_AUDIO_CONTENT_TYPE = {
    ".flac": "audio/flac",
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".ogg": "audio/ogg",
}


def _build_multipart(
    fields: dict,
    *,
    file_path: str | None = None,
    file_field: str = "file",
) -> tuple[bytes, str]:
    """RFC 7578 multipart/form-data 본문 구성. (body_bytes, content_type) 반환.

    fields의 값이 None이면 해당 필드 생략. file_path=None이면 파일 part 미포함.
    """
    boundary = f"----stt-test-{uuid.uuid4().hex}"
    crlf = b"\r\n"
    parts: list[bytes] = []

    for name, value in fields.items():
        if value is None:
            continue
        parts.append(f"--{boundary}".encode())
        parts.append(f'Content-Disposition: form-data; name="{name}"'.encode())
        parts.append(b"")
        parts.append(str(value).encode())

    if file_path is not None:
        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_name)[1].lower()
        ct = _AUDIO_CONTENT_TYPE.get(ext, "application/octet-stream")
        parts.append(f"--{boundary}".encode())
        parts.append(
            f'Content-Disposition: form-data; name="{file_field}"; filename="{file_name}"'.encode()
        )
        parts.append(f"Content-Type: {ct}".encode())
        parts.append(b"")
        with open(file_path, "rb") as f:
            parts.append(f.read())

    parts.append(f"--{boundary}--".encode())
    parts.append(b"")
    return crlf.join(parts), f"multipart/form-data; boundary={boundary}"


def _transcribe(
    ctx: TestContext,
    *,
    audio_path: str | None,
    model: str | None = None,
    language: str | None = None,
    temperature: float = 0,
    response_format: str | None = None,
    extra_fields: dict | None = None,
    timeout: float = 120,
) -> tuple[int, dict | str]:
    """`POST /v1/audio/transcriptions` multipart 호출. (status, parsed_body) 반환.

    audio_path=None 이면 파일 part 없이 호출(필수 필드 누락 검증용).
    """
    url = f"{ctx.base_url}/v1/audio/transcriptions"
    fields: dict = {
        "model": model if model is not None else ctx.model,
        "language": language,
        "temperature": temperature,
        "response_format": response_format,
    }
    if extra_fields:
        fields.update(extra_fields)
    body, content_type = _build_multipart(fields, file_path=audio_path)

    summary = {"fields": {k: v for k, v in fields.items() if v is not None}}
    if audio_path:
        summary["file"] = {"path": audio_path, "size": len(body)}
    _record_request("POST", url, summary)

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": content_type, "Content-Length": str(len(body))},
        method="POST",
    )
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


# ── 테스트 실행 프레임워크 ────────────────────────────────


def _format_body(body, *, max_len: int = 800) -> str:
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


# ── 2. Transcriptions ────────────────────────────────────

_HANGUL_RE = re.compile(r"[가-힣]")


def _check_response(text: str, reference: str | None) -> tuple[bool, str]:
    """smoke 검증 — reference에 한국어 음절 있으면 overlap ≥ 50%, 없으면 응답 존재만 확인.

    정밀 정확도 측정(WER/CER)은 별도 정성 비교 트랙. 본 smoke는 "서빙 잘 됐는지" 확인 용도.
    """
    text = text.strip()
    if not text:
        return False, "빈 응답"
    if reference:
        ref_syl = set(_HANGUL_RE.findall(reference))
        if ref_syl:
            hyp_syl = set(_HANGUL_RE.findall(text))
            overlap = len(hyp_syl & ref_syl) / len(ref_syl)
            ok = overlap >= 0.5
            detail = (
                f"한국어 음절 overlap: {overlap:.1%} ({len(hyp_syl & ref_syl)}/{len(ref_syl)})\n"
                f"  hyp: {text[:200]}\n"
                f"  ref: {reference[:200]}"
            )
            return ok, detail
    # reference 없거나 한국어 음절 없는 경우(영어 등) — 응답 존재만 확인.
    return True, f"응답: {text[:200]}"


def test_transcription(ctx: TestContext):
    c = ctx.colors
    print(f"\n{_c(c, 'bold', '2. Transcriptions (POST /v1/audio/transcriptions)')}")

    # reference에 한국어 음절이 있으면 한국어 모드, 아니면 영어 모드. language 인자 자동 선택.
    lang_hint = "ko" if ctx.reference and _HANGUL_RE.search(ctx.reference) else "en"

    def t_2_1():
        """기본 transcription — 정답 텍스트와 한국어 음절 overlap 검증"""
        status, body = _transcribe(ctx, audio_path=ctx.audio_path)
        if status != 200:
            return False, f"HTTP {status}: {body}"
        text = body.get("text", "") if isinstance(body, dict) else str(body)
        return _check_response(text, ctx.reference)

    def t_2_2():
        """language 명시 (자동 감지 비용 절약)"""
        status, body = _transcribe(ctx, audio_path=ctx.audio_path, language=lang_hint)
        if status != 200:
            return False, f"HTTP {status}: {body}"
        text = body.get("text", "") if isinstance(body, dict) else str(body)
        return _check_response(text, ctx.reference)

    def t_2_3():
        """response_format=text — 평문 응답"""
        status, body = _transcribe(ctx, audio_path=ctx.audio_path, response_format="text")
        if status != 200:
            return False, f"HTTP {status}: {body}"
        # text 포맷은 문자열이거나 {"text": "..."} 둘 다 허용 (모델/버전별 차이).
        if isinstance(body, dict):
            text = body.get("text", "")
        else:
            text = str(body)
        ok = bool(text.strip())
        return ok, f"형식: {type(body).__name__}, 응답: {text[:200]}"

    def t_2_4():
        """존재하지 않는 모델명"""
        status, _ = _transcribe(ctx, audio_path=ctx.audio_path, model="nonexistent-model")
        return status >= 400, f"HTTP {status}"

    _run_test(ctx, "2.1", "Transcription", f"기본 transcription ({lang_hint})", t_2_1)
    _run_test(ctx, "2.2", "Transcription", f"language={lang_hint} 명시", t_2_2)
    _run_test(ctx, "2.3", "Transcription", "response_format=text 평문 응답", t_2_3)
    _run_test(ctx, "2.4", "Transcription", "존재하지 않는 모델명", t_2_4)


# ── 3. 경계값 ──────────────────────────────────────────

def test_edge_cases(ctx: TestContext):
    c = ctx.colors
    print(f"\n{_c(c, 'bold', '3. 경계값')}")

    def t_3_1():
        """file 필드 누락 — 400+ 에러"""
        status, _ = _transcribe(ctx, audio_path=None)
        return status >= 400, f"HTTP {status}"

    def t_3_2():
        """잘못된 multipart 본문"""
        url = f"{ctx.base_url}/v1/audio/transcriptions"
        req = urllib.request.Request(
            url,
            data=b"not a valid multipart body",
            headers={"Content-Type": "multipart/form-data; boundary=garbage"},
            method="POST",
        )
        _record_request("POST", url, "<garbage multipart>")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                _record_response(resp.status, "<unexpected 2xx>")
                return False, f"에러 예상했으나 HTTP {resp.status}"
        except urllib.error.HTTPError as e:
            _record_response(e.code, "<expected error>")
            return e.code in (400, 422), f"HTTP {e.code}"

    _run_test(ctx, "3.1", "경계값", "file 필드 누락", t_3_1)
    _run_test(ctx, "3.2", "경계값", "잘못된 multipart 본문", t_3_2)


# ═══════════════════════════════════════════════════════════
# 카테고리 레지스트리
# ═══════════════════════════════════════════════════════════

CATEGORIES = {
    "infra": ("서버 기동 / 인프라", test_infra),
    "transcription": ("Transcriptions", test_transcription),
    "edge": ("경계값", test_edge_cases),
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

    categories: dict = {}
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

    failures = [r for r in results if not r.passed]
    if failures:
        print(f"\n {_c(c, 'red', '실패 목록:')}")
        for r in failures:
            print(f"  [{r.id}] {r.name}")
            if r.detail:
                for line in r.detail.split("\n"):
                    print(f"       {_c(c, 'dim', line)}")

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
        description="vLLM STT 서버 QA 테스트 (smoke)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            카테고리:
              infra          서버 기동 / 인프라
              transcription  Transcriptions (POST /v1/audio/transcriptions)
              edge           경계값 (필드 누락, 잘못된 multipart)

            예시 (stt/ 디렉토리에서 실행):
              python tests/test_stt_server.py                                       # voxtral 게이트웨이(:5017), 한국어 default
              python tests/test_stt_server.py --base-url http://localhost:7171      # whisper_v3 단독
              python tests/test_stt_server.py --base-url http://localhost:7170      # qwen3_asr 단독
              python tests/test_stt_server.py --audio /path/to/my.wav --reference /path/to/my.txt
              python tests/test_stt_server.py --category infra
        """),
    )
    p.add_argument("--base-url", default="http://localhost:5017", help="STT 서버 URL (기본: http://localhost:5017)")
    p.add_argument(
        "--model", default=None,
        help="모델명 (미지정 시 base-url의 /v1/models API에서 첫 모델 자동 추출)",
    )
    p.add_argument(
        "--audio", default=None,
        help="음성 파일 경로 (미지정 시 tests/zeroth_ko_sample.flac — 한국어 default, 16kHz mono native)",
    )
    p.add_argument(
        "--reference", default=None,
        help="정답 텍스트 파일 경로 (미지정 시 audio basename + '.txt' 자동 탐색). 미존재 시 응답 존재만 확인.",
    )
    p.add_argument("--category", nargs="*", choices=list(CATEGORIES.keys()), help="실행할 카테고리 (미지정 시 전체)")
    p.add_argument("--list", action="store_true", help="카테고리 목록 출력")
    p.add_argument("--no-color", action="store_true", help="컬러 출력 비활성화")
    p.add_argument("--verbose", "-v", action="store_true", help="성공 테스트도 상세 출력")
    return p.parse_args()


def _resolve_model_from_api(base_url: str, timeout: float = 5.0) -> str:
    """OpenAI 호환 /v1/models 엔드포인트로 모델명을 조회한다.
    STT 인스턴스/게이트웨이 모두 응답하므로 게이트웨이 미경유 직접 노출에서도 동작."""
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


def _open_log_file() -> tuple[str, "object"]:
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"test_stt_{time.strftime('%Y%m%d_%H%M%S')}.log")
    log_file = open(log_path, "w", encoding="utf-8", buffering=1)
    return log_path, log_file


def main():
    args = parse_args()
    colors = NO_COLORS if args.no_color else COLORS

    if args.list:
        print("카테고리 목록:")
        for key, (desc, _) in CATEGORIES.items():
            print(f"  {key:<15} {desc}")
        return

    log_path, log_file = _open_log_file()
    orig_stdout, orig_stderr = sys.stdout, sys.stderr
    sys.stdout = _Tee(orig_stdout, log_file)
    sys.stderr = _Tee(orig_stderr, log_file)

    try:
        # 모델명 자동 추출 — /v1/models API 우선. 실패 시 명확한 에러로 종료.
        try:
            model = args.model or _resolve_model_from_api(args.base_url)
        except Exception as e:
            print(
                f"\n{_c(colors, 'red', '모델명 자동 추출 실패')}: {args.base_url} ({type(e).__name__}: {e})\n"
                "  --model로 직접 지정하거나 서버가 살아있는지 확인하세요."
            )
            sys.exit(1)

        # 음성 파일 경로 — 미지정 시 tests/zeroth_ko_sample.flac (한국어 default, 16kHz mono).
        if args.audio is not None:
            audio_path = args.audio
        else:
            audio_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zeroth_ko_sample.flac")
        if not os.path.isfile(audio_path):
            print(f"\n{_c(colors, 'red', '음성 파일 없음')}: {audio_path}")
            print("  tests/zeroth_ko_sample.flac이 없으면 --audio로 경로를 지정하세요.")
            sys.exit(1)

        # 정답 텍스트 — 미지정 시 audio basename + '.txt'. 미존재 시 None (한국어 매칭 건너뜀).
        if args.reference is not None:
            ref_path = args.reference
        else:
            ref_path = os.path.splitext(audio_path)[0] + ".txt"
        reference: str | None = None
        if os.path.isfile(ref_path):
            with open(ref_path, encoding="utf-8") as rf:
                reference = rf.read().strip()

        ctx = TestContext(
            base_url=args.base_url.rstrip("/"),
            model=model,
            audio_path=audio_path,
            reference=reference,
            colors=colors,
            verbose=args.verbose,
        )

        print(f"\n{_c(colors, 'bold', 'vLLM STT 서버 QA 테스트 (smoke)')}")
        print(f"  서버: {ctx.base_url}")
        print(f"  모델: {ctx.model}")
        print(f"  음성: {ctx.audio_path}")
        if reference:
            print(f"  정답: {ref_path}")
            print(f"        {reference[:120]}{'...' if len(reference) > 120 else ''}")
        else:
            print(f"  정답: <없음 — 응답 존재만 확인>")
        print(f"  로그: {log_path}")

        # 서버 연결 확인
        try:
            _request(f"{ctx.base_url}/health", timeout=5)
        except Exception as e:
            print(f"\n{_c(colors, 'red', '서버 연결 실패')}: {ctx.base_url}/health ({type(e).__name__}: {e})")
            print("STT 서버가 실행 중인지 확인하세요. (./start.sh status)")
            sys.exit(1)

        selected = args.category or list(CATEGORIES.keys())
        for key in selected:
            _, test_fn = CATEGORIES[key]
            test_fn(ctx)

        print_summary(ctx)
        print(f"  로그 파일: {log_path}")

        failures = sum(1 for r in ctx.results if not r.passed)
        sys.exit(1 if failures else 0)
    finally:
        sys.stdout, sys.stderr = orig_stdout, orig_stderr
        log_file.close()


if __name__ == "__main__":
    main()
