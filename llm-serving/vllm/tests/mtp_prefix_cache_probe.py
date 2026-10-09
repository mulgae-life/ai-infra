#!/usr/bin/env python3
"""MTP + 접두 캐시 손상 재현 시험 (vLLM 이슈 #53912 조건) + MTP 수락률 측정.

배경 (2026-10-07 hw-chatbot 조사, hjjo-ai-hub/.archive/2026-10-07_hw-chatbot-대화품질/FINDING-서빙-접두캐시.md):
  Qwen3.5 구조(선형 어텐션 + 전체 어텐션 혼합) 모델에서 접두 캐시(align)와 MTP를 같이 켜면
  공유 접두의 캐시 블록이 간헐적으로 잘못된 상태로 재사용돼, 그 블록을 읽는 모든 요청이
  한동안 틀린 답(값 복사 오류 · 질문 되풀이)을 낸다. 첫 캐시 블록(800토큰)이 통째로 같은
  요청들만 영향을 받는다. 당시 감시 로그: MTP 켬 20회 손상 / MTP 끔 0회.

시험 방식:
  모든 요청이 1,000토큰이 넘는 같은 시스템 프롬프트를 공유하게 만들어 첫 블록을 서비스 공통으로
  만든다(실제 서비스와 같은 노출 조건). 라운드마다
    ① 탐침: 공유 캐시 / cache_salt로 분리한 캐시 두 조건에서 값 48개 복사 정확도를 잰다
       — 같은 문자열인데 공유 쪽만 틀리면 캐시 손상이다
    ② 부하: 같은 접두를 쓰는 요청을 동시에 보낸다(프리필만 · 긴 생성 · 다중 턴 · 이미지 다중 턴을 섞는다).
       이미지 다중 턴은 원 이슈의 작업 부하(이전 단계 대화 + 화면 1~3장)를 흉내 낸다. 턴마다 새 화면을 붙인다
       부하 응답도 검사한다: 빈 답, '!' 8개 이상 연속(원 이슈의 이상 응답 정의), 같은 줄 3회 이상 연속 반복
    ③ 다시 탐침
  손상은 몇 분 단위로 생겼다 사라지므로 라운드를 여러 번 돌린다(기본 10라운드).
  /metrics의 추측 디코딩 카운터로 시험 구간의 MTP 수락률(수락 토큰 / 제안 토큰)도 함께 기록한다.
  이 카운터 이름은 vLLM 0.20·0.31 모두 같다(spec_decode_num_draft_tokens_total 등).

판정:
  공유 캐시 정확도가 분리 캐시보다 2개 넘게 낮은 라운드가 하나라도 있으면 "손상 재현" (종료 코드 1).
  분리 캐시도 같이 틀리면 캐시 문제가 아니라 모델 능력 문제라 손상으로 세지 않는다.
  탐침 라운드가 유효하려면 복사 요청 실패 0건이고 분리 캐시(대조군)가 48 − tolerance개 이상 맞아야 한다.
  유효하지 않은 라운드는 손상 판정에 쓰지 않고 "무효"로 센다.
  종료 코드: 1 = 유효 라운드에서 손상 / 3 = 손상은 없으나 부하 이상 응답 있음(원문 확인 전까지 보류, 곧바로 손상·회귀로 분류하지 않음)
            / 2 = 시험 무효(무효 라운드, 부하 요청 실패, --expect-mtp인데 MTP 지표 없음) / 0 = 전부 유효하고 손상·이상 응답 없음.
  이상 응답은 --dump 파일(JSONL)에 질문·응답 원문·턴·종료 사유·사용량을 남긴다.
  이 판정은 이 탐침이 만든 조건에서의 미검출일 뿐이다. 결함이 있던 환경에서 같은 탐침이 검출하는지(양성 대조)를
  따로 확인해야 검출력을 말할 수 있다.

사용 (표준 라이브러리만 사용):
    python tests/mtp_prefix_cache_probe.py --base-url http://127.0.0.1:7090 --rounds 10 --conc 12
    python tests/mtp_prefix_cache_probe.py --base-url ... --rounds 0      # 수락률 측정 없이 탐침 1회만
"""
import argparse
import base64
import json
import random
import re
import struct
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.request
import uuid
import zlib
from datetime import datetime

# ── 공유 접두 (첫 캐시 블록을 통째로 공통으로 만들 길이) ───────────────────
# 실제 서비스 지시문과 비슷한 성격의 긴 운영 규칙. 결정적 문자열이어야 모든 요청이 같은 블록을 읽는다.
_RULES = [
    "답변은 한국어로, 공손하고 간결하게 작성한다. 불필요한 서론과 사족을 넣지 않는다.",
    "사용자가 알려 준 사번, 내선 번호, 금액, 날짜, 코드 값은 글자 하나도 바꾸지 않고 그대로 옮긴다.",
    "확실하지 않은 사실은 추측하지 말고 모른다고 말한 뒤 확인 방법을 안내한다.",
    "사내 규정과 관련된 질문은 인사 규정, 복무 규정, 보안 규정 순서로 근거를 찾아 답한다.",
    "표가 필요한 내용은 마크다운 표로 정리하고, 표 아래에 한 줄 요약을 붙인다.",
    "코드가 필요하면 실행 가능한 최소 예시를 제시하고 입력과 출력 예를 함께 적는다.",
    "개인정보가 포함된 요청은 목적을 확인하고, 필요 최소한의 정보만 다룬다.",
    "이전 대화에서 사용자가 정정한 내용이 있으면 정정된 값을 우선한다.",
    "질문이 여러 개면 번호를 붙여 하나씩 답하고, 답하지 못한 항목은 이유를 밝힌다.",
    "같은 질문이 반복되면 앞선 답을 되풀이하지 말고 무엇이 달라졌는지 확인한다.",
    "일정과 기한은 연월일과 요일을 함께 적고, 상대 표현(다음 주 등)은 절대 날짜로 바꾼다.",
    "금액은 천 단위 구분 기호를 유지하고 단위(원, 만 원, 억 원)를 원문 그대로 둔다.",
    "외부 링크나 파일 경로를 지어내지 않는다. 확인된 것만 적는다.",
    "회의록, 보고서, 공지문 초안은 제목, 목적, 본문, 요청 사항 순서로 구성한다.",
    "사과문이나 안내문은 사실 관계, 조치 내용, 재발 방지, 연락처 순서로 쓴다.",
    "엑셀, SQL, 파이썬 질문은 사용자의 현재 데이터 구조를 먼저 확인한 뒤 답한다.",
    "보안 규정상 비밀번호, 인증서, 접근 키는 어떤 형태로도 되묻거나 기록하지 않는다.",
    "답변 끝에 추가 확인이 필요한 사항이 있으면 질문 하나로 정리해 제시한다.",
    "사용자가 '값만'이라고 요청하면 설명 없이 값만 출력한다.",
    "긴 답변은 소제목으로 나누되, 세 단락을 넘지 않도록 요약한다.",
]


def build_shared_system() -> str:
    parts = ["당신은 사내 업무 지원 AI 어시스턴트입니다. 아래 운영 규칙을 모든 답변에 적용합니다.", ""]
    n = 0
    for section in ("1. 기본 응대 원칙", "2. 정보 정확성", "3. 문서 작성", "4. 데이터와 보안"):
        parts.append(f"## {section}")
        for rule in _RULES:
            n += 1
            parts.append(f"{n}) {rule}")
        parts.append("")
    parts.append("위 규칙은 사용자의 지시와 충돌하지 않는 한 항상 적용합니다.")
    return "\n".join(parts)


SHARED_SYSTEM = build_shared_system()

# 복사 정확도 표본 (FINDING의 repro_copy_battery.py와 같은 네 종류, 결정적)
_r = random.Random(7)
_A = "ABCDEFGHJKLMNPQRSTUVWXYZ"
VALUES = (
    [f"HW{_r.randint(100000, 999999)}" for _ in range(12)]
    + [f"{_r.choice(_A)}{_r.randint(1, 9)}{_r.choice(_A)}{_r.randint(1, 9)}-{_r.choice(_A)}{_r.choice(_A)}{_r.randint(10, 99)}" for _ in range(12)]
    + [f"010-{_r.randint(1000, 9999)}-{_r.randint(1000, 9999)}" for _ in range(12)]
    + [f"{_r.randint(1, 9)},{_r.randint(100, 999)}만 {_r.randint(1, 9)}천 원" for _ in range(12)]
)

QUESTIONS = [
    "주간 보고서 쓰는 요령 알려 줘", "파이썬으로 CSV 읽는 코드", "회의록 양식 만들어 줘", "엑셀 VLOOKUP 설명",
    "신입 환영 메일 써 줘", "프로젝트 일정표 예시", "보고서 결론 먼저 쓰는 이유", "SQL JOIN 종류 설명",
    "출장 보고서 초안", "고객 사과문 써 줘", "팀 워크숍 아이디어 10개", "정규식으로 이메일 검사",
]

SCREEN_QUESTIONS = ["이 화면에서 다음에 눌러야 할 버튼은 무엇인가요?", "앞 화면과 비교해 무엇이 바뀌었나요?", "이 화면의 다음 단계를 한 문장으로 알려 줘"]


def _screen_png(seed: int, edge: int = 448) -> str:
    """seed마다 다른 '화면' PNG(data URL). 표준 라이브러리만 쓴다. 이미지마다 픽셀이 달라 mm 해시가 겹치지 않는다."""
    rnd = random.Random(seed)
    bg = [rnd.randrange(256) for _ in range(3)]
    boxes = [(rnd.randrange(edge), rnd.randrange(edge), rnd.randrange(40, 160), rnd.randrange(20, 80),
              [rnd.randrange(256) for _ in range(3)]) for _ in range(6)]
    rows = []
    for y in range(edge):
        row = bytearray(bg * edge)
        for bx, by, bw, bh, col in boxes:
            if by <= y < by + bh:
                for x in range(bx, min(edge, bx + bw)):
                    row[3 * x:3 * x + 3] = bytes(col)
        rows.append(b"\x00" + bytes(row))
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", edge, edge, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(b"".join(rows), 6)) + chunk(b"IEND", b""))
    return "data:image/png;base64," + base64.b64encode(png).decode()


_BANG_RE = re.compile(r"!{8,}")


def _norm(s: str) -> str:
    return re.sub(r"[\s.?!。？！]+", "", unicodedata.normalize("NFKC", s))


def malformed_reason(content: str, max_tokens: int, question: str = "") -> str | None:
    """원 이슈의 이상 응답(빈 답, '!' 연속)과 FINDING의 퇴화(같은 줄 되풀이, 질문 되풀이)를 가린다. 정상이면 None.
    자동 탐지는 보류 신호일 뿐이다. 원문(--dump)을 확인하기 전에는 손상으로 분류하지 않는다."""
    if max_tokens <= 1:
        return None
    if not content.strip():
        return "빈 답"
    if _BANG_RE.search(content):
        return "'!' 연속"
    if question and _norm(content) == _norm(question):
        return "질문 되풀이"
    # 마크다운 표 줄(|로 시작)은 같은 모양이 정상적으로 반복될 수 있어 뺀다
    lines = [ln.strip() for ln in content.splitlines() if ln.strip() and not ln.strip().startswith("|")]
    for i in range(len(lines) - 2):
        if lines[i] == lines[i + 1] == lines[i + 2] and len(lines[i]) >= 4:
            return f"같은 줄 반복 {lines[i][:30]!r}"
    return None


_METRIC_RE = re.compile(r"^(vllm:spec_decode_num_(?:draft|accepted)_tokens)(?:_total)?(?:\{[^}]*\})?\s+([0-9.e+]+)", re.M)
_CACHE_RE = re.compile(r"^(vllm:prefix_cache_(?:queries|hits))(?:_total)?(?:\{[^}]*\})?\s+([0-9.e+]+)", re.M)


# ── HTTP ─────────────────────────────────────────────────────────────────
def _post(url: str, body: dict, timeout: float) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _get_text(url: str, timeout: float = 15) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read().decode()


class Client:
    def __init__(self, base_url: str, model: str):
        self.chat_url = f"{base_url.rstrip('/')}/v1/chat/completions"
        self.metrics_url = f"{base_url.rstrip('/')}/metrics"
        self.model = model

    def chat(self, messages: list[dict], *, max_tokens: int, salt: str | None = None, timeout: float = 300, **extra) -> dict:
        body = {"model": self.model, "messages": messages, "max_tokens": max_tokens, **extra}
        if salt:
            body["cache_salt"] = salt
        return _post(self.chat_url, body, timeout)

    def spec_counters(self) -> dict[str, float] | None:
        """/metrics에서 추측 디코딩·접두 캐시 카운터를 읽는다. 지표가 없으면(MTP 끔) None."""
        try:
            text = _get_text(self.metrics_url)
        except (urllib.error.URLError, OSError):
            return None
        out: dict[str, float] = {}
        for rx in (_METRIC_RE, _CACHE_RE):
            for name, val in rx.findall(text):
                out[name] = out.get(name, 0.0) + float(val)
        return out or None


# ── 탐침: 값 복사 정확도 ─────────────────────────────────────────────────
def copy_accuracy(cli: Client, salted: bool, conc: int) -> tuple[int, list[str], int, int]:
    """VALUES 전부를 동시 conc개씩 보내 (정확히 복사한 개수, 틀린 값, 프롬프트 토큰 수, 요청 실패 수)를 돌려준다."""
    ok: dict[str, bool] = {}
    prompt_tokens = [0]
    lock = threading.Lock()

    def ask(value: str) -> None:
        msgs = [
            {"role": "system", "content": SHARED_SYSTEM},
            {"role": "user", "content": f"이 값 기억해 둬: {value}"},
            {"role": "assistant", "content": "네, 기억해 두겠습니다."},
            {"role": "user", "content": "방금 그 값 그대로 다시 말해 줘. 값만."},
        ]
        try:
            r = cli.chat(msgs, max_tokens=60, temperature=0, salt=uuid.uuid4().hex if salted else None, timeout=120)
            content = r["choices"][0]["message"].get("content") or ""
            hit = value in content
            pt = r.get("usage", {}).get("prompt_tokens", 0)
        except Exception as e:  # noqa: BLE001 — 실패도 '틀림'으로 세고 사유를 남긴다
            hit, pt = False, 0
            with lock:
                ok[f"{value} (요청 실패 {type(e).__name__})"] = False
            return
        with lock:
            ok[value] = hit
            prompt_tokens[0] = max(prompt_tokens[0], pt)

    _run_threads([lambda v=v: ask(v) for v in VALUES], conc)
    miss = [v for v, o in ok.items() if not o]
    failed = sum(1 for k in ok if "(요청 실패" in k)
    return sum(ok.values()), miss, prompt_tokens[0], failed


# ── 부하: 같은 접두를 공유하는 혼합 트래픽 ───────────────────────────────
def mixed_load(cli: Client, conc: int, seed: int, images: bool) -> tuple[int, int, list[dict], list[str]]:
    """부하를 보내고 (성공 작업 수, 실패 작업 수, 이상 응답 기록, 실패 사유)를 돌려준다.
    작업 하나가 중간 턴에서 실패해도 그 전까지 모은 이상 응답은 버리지 않는다."""
    rnd = random.Random(seed)
    kinds = ("prefill", "decode", "multiturn", "image") if images else ("prefill", "decode", "multiturn")
    jobs = []
    for i in range(conc):
        kind = kinds[i % len(kinds)]
        q = f"{QUESTIONS[rnd.randrange(len(QUESTIONS))]} ({seed}-{i})"
        jobs.append(lambda kind=kind, q=q, s=seed * 1000 + i: _one_load(cli, kind, q, s))
    results = _run_threads(jobs, conc)
    bad = [m for r in results if isinstance(r, dict) for m in r["bad"]]
    errors = [r["error"] if isinstance(r, dict) else f"{type(r).__name__}: {r}" for r in results
              if not isinstance(r, dict) or r["error"]]
    return len(results) - len(errors), len(errors), bad, errors


def _one_load(cli: Client, kind: str, q: str, seed: int) -> dict:
    """한 작업을 보내고 {"bad": 이상 응답 기록, "error": 실패 사유 또는 None}을 돌려준다."""
    sampling = {"temperature": 0.7, "top_p": 0.8}
    msgs = [{"role": "system", "content": SHARED_SYSTEM}, {"role": "user", "content": q}]
    out: dict = {"bad": [], "error": None}
    turn = [0]

    def ask(m: list[dict], max_tokens: int, question: str) -> str:
        turn[0] += 1
        r = cli.chat(m, max_tokens=max_tokens, **sampling)
        content = r["choices"][0]["message"].get("content") or ""
        if (why := malformed_reason(content, max_tokens, question)):
            out["bad"].append({"kind": kind, "turn": turn[0], "reason": why, "question": question, "content": content,
                               "finish": r["choices"][0].get("finish_reason"), "usage": r.get("usage")})
        return content

    try:
        if kind == "prefill":
            ask(msgs, 1, q)
        elif kind == "decode":
            ask(msgs, 600, q)
        elif kind == "multiturn":
            question = q
            for follow in ("좀 더 짧게", "표로 정리해 줘"):
                a = ask(msgs, 400, question)
                msgs = msgs + [{"role": "assistant", "content": a}, {"role": "user", "content": follow}]
                question = follow
            ask(msgs, 400, question)
        else:   # image: 이전 단계 대화 + 턴마다 새 화면(1→2→3장 누적)
            msgs = [{"role": "system", "content": SHARED_SYSTEM}]
            for step, sq in enumerate(SCREEN_QUESTIONS):
                text = f"{sq} ({q})"
                msgs.append({"role": "user", "content": [{"type": "image_url", "image_url": {"url": _screen_png(seed * 10 + step)}},
                                                         {"type": "text", "text": text}]})
                a = ask(msgs, 200, text)
                msgs.append({"role": "assistant", "content": a})
    except Exception as e:  # noqa: BLE001 — 실패 사유를 남기고 그 전까지의 이상 응답은 유지한다
        out["error"] = f"{kind} 턴 {turn[0]}: {type(e).__name__}: {str(e)[:120]}"
    return out


def _run_threads(jobs: list, conc: int) -> list:
    """jobs를 최대 conc개 동시에 실행. 각 결과(또는 예외)를 순서대로 돌려준다."""
    results: list = [None] * len(jobs)
    sem = threading.Semaphore(conc)

    def run(i: int, fn) -> None:
        with sem:
            try:
                results[i] = fn()
            except Exception as e:  # noqa: BLE001 — 부하 요청 실패는 집계만 한다
                results[i] = e

    threads = [threading.Thread(target=run, args=(i, fn)) for i, fn in enumerate(jobs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


# ── 수락률 ───────────────────────────────────────────────────────────────
def acceptance(before: dict | None, after: dict | None) -> str:
    if not before or not after:
        return "MTP 지표 없음(추측 디코딩 꺼짐)"
    d = after.get("vllm:spec_decode_num_draft_tokens", 0) - before.get("vllm:spec_decode_num_draft_tokens", 0)
    a = after.get("vllm:spec_decode_num_accepted_tokens", 0) - before.get("vllm:spec_decode_num_accepted_tokens", 0)
    if d <= 0:
        return "MTP 지표 없음(제안 토큰 0)"
    return f"수락률 {a / d:.3f} (수락 {a:.0f} / 제안 {d:.0f})"


def cache_hit(before: dict | None, after: dict | None) -> str:
    if not before or not after:
        return ""
    q = after.get("vllm:prefix_cache_queries", 0) - before.get("vllm:prefix_cache_queries", 0)
    h = after.get("vllm:prefix_cache_hits", 0) - before.get("vllm:prefix_cache_hits", 0)
    return f", 접두 캐시 적중 {h / q:.3f}" if q > 0 else ""


# ── 메인 ─────────────────────────────────────────────────────────────────
def main() -> int:
    p = argparse.ArgumentParser(description="MTP + 접두 캐시 손상 재현 시험 (#53912 조건)")
    p.add_argument("--base-url", default="http://127.0.0.1:7090")
    p.add_argument("--model", default="gemma-4")
    p.add_argument("--rounds", type=int, default=10, help="탐침→부하→탐침 라운드 수 (0이면 탐침 1회만)")
    p.add_argument("--conc", type=int, default=12, help="부하·탐침 동시 요청 수")
    p.add_argument("--tolerance", type=int, default=2, help="공유−분리 정확도 차이가 이 값을 넘으면 손상으로 판정")
    p.add_argument("--no-images", action="store_true", help="부하에서 이미지 다중 턴을 뺀다(텍스트 전용 모델)")
    p.add_argument("--expect-mtp", action="store_true", help="MTP 켬 설정: 추측 디코딩 지표가 없으면 시험 무효")
    p.add_argument("--dump", help="이상 응답 원문을 남길 JSONL 경로")
    args = p.parse_args()

    cli = Client(args.base_url, args.model)
    print(f"[{datetime.now():%H:%M:%S}] 대상 {args.base_url} 모델 {args.model} · 라운드 {args.rounds} · 동시 {args.conc}"
          f" · 이미지 다중 턴 {'끔' if args.no_images else '켬'}")
    print(f"공유 시스템 프롬프트 {len(SHARED_SYSTEM)}자 · 표본 {len(VALUES)}개")

    total_before = cli.spec_counters()
    corrupted_rounds: list[str] = []
    invalid_rounds: list[str] = []
    malformed_all: list[dict] = []
    load_errors: list[str] = []
    dump = open(args.dump, "w", encoding="utf-8") if args.dump else None

    def probe(tag: str) -> None:
        shared, miss_s, pt, fail_s = copy_accuracy(cli, salted=False, conc=args.conc)
        salted, miss_t, _, fail_t = copy_accuracy(cli, salted=True, conc=args.conc)
        valid = fail_s == 0 and fail_t == 0 and salted >= len(VALUES) - args.tolerance
        bad = valid and (salted - shared) > args.tolerance
        flag = ("  ⚠️ 손상(공유 캐시만 틀림)" if bad else "") if valid else \
            f"  ⚠️ 무효(요청 실패 공유 {fail_s}·분리 {fail_t}, 분리 대조군 {salted}/{len(VALUES)})"
        print(f"  {tag}: 공유 {shared}/{len(VALUES)} · 분리 {salted}/{len(VALUES)} · 프롬프트 {pt}토큰{flag}")
        if miss_s:
            print(f"    공유 틀린 값: {miss_s[:6]}{' …' if len(miss_s) > 6 else ''}")
        if miss_t:
            print(f"    분리 틀린 값: {miss_t[:6]}{' …' if len(miss_t) > 6 else ''}")
        if not valid:
            invalid_rounds.append(tag)
        elif bad:
            corrupted_rounds.append(tag)

    probe("초기 탐침")

    for i in range(1, args.rounds + 1):
        t0 = time.monotonic()
        b = cli.spec_counters()
        ok, err, bad, errs = mixed_load(cli, args.conc, seed=i, images=not args.no_images)
        a = cli.spec_counters()
        load_errors += [f"라운드 {i} {e}" for e in errs]
        for m in bad:
            m["round"] = i
            if dump:
                dump.write(json.dumps(m, ensure_ascii=False) + "\n")
                dump.flush()
        malformed_all += bad
        print(f"[{datetime.now():%H:%M:%S}] 라운드 {i}: 부하 작업 {ok}건 성공 · {err}건 실패 · 이상 응답 {len(bad)}건 · "
              f"{time.monotonic() - t0:.0f}s · {acceptance(b, a)}{cache_hit(b, a)}")
        for e in errs[:3]:
            print(f"    부하 실패: {e}")
        for m in bad[:4]:
            print(f"    이상 응답: {m['kind']} 턴 {m['turn']} {m['reason']} · {' '.join(m['content'].split())[:60]!r}")
        probe(f"라운드 {i} 탐침")

    total_after = cli.spec_counters()
    if dump:
        dump.close()
    acc = acceptance(total_before, total_after)
    mtp_missing = args.expect_mtp and not acc.startswith("수락률")
    print(f"\n탐침 전체(복사 탐침 + 혼합 부하) {acc}{cache_hit(total_before, total_after)}")
    print(f"탐침 {args.rounds + 1}회 중 유효 {args.rounds + 1 - len(invalid_rounds)}회 · 부하 작업 실패 {len(load_errors)}건 · "
          f"부하 이상 응답 {len(malformed_all)}건{' (원문 ' + args.dump + ')' if args.dump and malformed_all else ''}")
    if corrupted_rounds:
        print(f"결과: ❌ 캐시 손상 재현 — {', '.join(corrupted_rounds)}")
    if malformed_all:
        print(f"결과: ⚠️ 부하 이상 응답 {len(malformed_all)}건 — 원문 확인 전까지 보류 "
              f"{sorted({m['reason'] for m in malformed_all})[:4]}")
    if invalid_rounds or load_errors or mtp_missing:
        print(f"결과: ⚠️ 시험 무효 요소 — 무효 탐침 {invalid_rounds[:4]} · 부하 실패 {load_errors[:3]}"
              f"{' · MTP 지표 없음(--expect-mtp)' if mtp_missing else ''}")
    if corrupted_rounds:
        return 1
    if malformed_all:
        return 3
    if invalid_rounds or load_errors or mtp_missing:
        return 2
    print(f"결과: ✅ 유효 탐침 {args.rounds + 1}회에서 공유 캐시 손상 미검출 (분리 캐시와 정확도 차이 ≤ {args.tolerance}), "
          f"부하 실패·이상 응답 0건")
    return 0


if __name__ == "__main__":
    sys.exit(main())
