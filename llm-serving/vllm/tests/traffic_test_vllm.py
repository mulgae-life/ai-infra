#!/usr/bin/env python3
"""vLLM 게이트웨이 하드 트래픽 테스트.

기능 검증용 test_vllm_server.py와 달리 운영 지표를 확인한다.
기본값은 동시 20명과 장문 출력 부하를 기준으로 설정한다.

테스트 단계:
  1. 모델 확인: --model 미지정 시 /v1/models에서 첫 모델명을 자동 추출.
       API 모델명은 served_model_name(gemma-4)으로 고정돼 있으므로, 어떤
       체크포인트를 잰 기록인지 남기려면 --label로 체크포인트명을 찍어야 한다.
  2. 사전 스냅샷: /health, /server-status, /v1/models 상태 저장.
  3. 조건 확정: 요청 수, 동시성, 생성 토큰 수, 타임아웃을 CLI 인자로 확정.
  4. 진행 화면: 기본으로 로컬 URL에서 요청별 생성 상태 표시.
  5. 요청 방식: 진행 화면은 stream, --no-ui 지정 시 --stream 여부에 따름.
  6. 트래픽 실행: 요청 큐를 만들고 --concurrency 워커가 순차 처리.
  7. 보호 장치: 허용되지 않은 에러율 또는 연속 실패 기준 초과 시 조기 중단.
  8. 사후 점검: 테스트 후 /health와 /server-status 생존 여부를 통과 조건에 반영.
  9. 지표 집계: 200 성공, 429 방어 응답, 상태코드, RPS, TPS, latency, TTFT 집계.
     답변 점검: HTTP 200 중 생성 상한 도달(finish_reason=length)은 경고, 상한이 아닌데
     답변이 0자면 실패로 판정한다.
 10. 결과 저장: logs/traffic_*.json 리포트 저장, 통과 기준 미달 시 exit 1.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import math
import os
import queue
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable


# 사고 켬 질문에는 글자 수를 지정하지 않는다. "약 250자"를 주면 Qwen3.8이 사고 과정에서
# 한 글자씩 세며 다듬느라 3천~4천 토큰을 쓰고, 생성 상한(4096)에 걸려 답 없이 끝났다
# (2026-10-10 :5015 실측, 지난 리포트에서도 사고 켬 요청의 일부가 같은 증상).
# 대신 계산과 시각 배분이 필요한 계획 문제를 준다. 사고가 실제로 일을 하면서도 끝이 있어
# Qwen3.8 기준 사고 600~750 토큰, 전체 생성 1.3천~1.8천 토큰에서 멈춘다(같은 날 3회 동시 실측).
# "한 문장씩" 같은 가벼운 질문은 사고가 140 토큰 안팎이라 부하 시험으로서 너무 가벼웠다.
# 사고 끔 질문은 글자를 세지 않으므로 출력 부하를 만들려고 분량 지정을 유지한다.
PROMPTS = [
    {
        "content": "4인 가족의 한 달 전기요금을 줄이는 계획을 세워주세요. 에어컨, 냉장고, 세탁기, TV, 조명의 소비전력과 하루 사용 시간을 가정해 월 사용량(kWh)을 계산하고, 절약 방법 다섯 가지와 각각의 월 예상 절감량을 표로 정리해주세요. 최종 답변만 작성해주세요.",
        "enable_thinking": True,
    },
    {
        "content": "초등학생 두 명과 비 오는 토요일을 집에서 보낼 일정을 짜주세요. 오전 9시부터 오후 6시까지 점심과 간식 시간, 30분 낮잠을 넣고, 활동마다 시작·끝 시각, 준비물, 주의할 점을 표로 정리해주세요. 최종 답변만 작성해주세요.",
        "enable_thinking": True,
    },
    {
        "content": "처음 자취를 시작하는 사람이 한 달 생활비를 관리하는 방법을 약 750자 분량으로 설명해주세요. 월세, 식비, 공과금, 비상금, 소비 습관을 포함해주세요.",
        "enable_thinking": False,
    },
    {
        "content": "부모님과 함께 1박 2일 국내 여행을 계획할 때 숙소, 이동, 식사, 일정, 예산을 어떻게 잡으면 좋은지 약 1000자 분량으로 설명해주세요.",
        "enable_thinking": False,
    },
]

DEFAULT_TRAFFIC_CONFIG = {
    "requests": 40,
    "concurrency": 20,
    "max_tokens": 4096,
    "timeout": 900,
    "ramp_up_seconds": 0.0,
    "sleep_seconds": 0.0,
    "max_error_rate": 0.05,
    "max_consecutive_errors": 3,
    "min_requests_before_break": 10,
    "require_200": True,
    "require_429": False,
    "image_ratio": 0.5,
    "image_edge": 4096,
}

# 멀티모달 부하용 이미지 풀. --image-ratio > 0일 때만 채워진다.
_IMAGE_POOL: list[str] = []
_IMAGE_RATIO = 0.0

MAX_DASHBOARD_TEXT_CHARS = 20000


@dataclass
class RequestResult:
    index: int
    ok: bool
    status: int | str
    latency_ms: float
    ttft_ms: float | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    error: str
    # HTTP 200이어도 답이 없을 수 있다. 사고가 생성 상한을 다 쓰면 finish_reason이 length이고
    # 답변(content)은 0자다. 상태코드만 보면 이런 응답이 성공으로 섞인다.
    finish_reason: str | None = None
    answer_chars: int = 0  # 공백을 뺀 답변 글자 수. 줄바꿈만 온 응답도 답이 없는 것으로 본다
    reasoning_tokens: int | None = None


def _answer_outcome(result: RequestResult) -> str | None:
    """HTTP 200 응답의 답변 상태. 정상이면 None, 실패 응답은 판단하지 않는다."""
    if not result.ok:
        return None
    if result.finish_reason == "length":
        return "truncated_empty" if result.answer_chars == 0 else "truncated"
    if result.answer_chars == 0:
        return "empty"
    return None


def _visible_chars(text: str) -> int:
    return sum(1 for ch in text if not ch.isspace())


def _reasoning_tokens(usage: dict[str, Any]) -> int | None:
    details = usage.get("completion_tokens_details") or {}
    value = details.get("reasoning_tokens") if isinstance(details, dict) else None
    return value if isinstance(value, int) else None


class DashboardState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._started_at = time.time()
        self._completed_at: float | None = None
        self._status = "준비 중"
        self._config: dict[str, Any] = {}
        self._model: str | None = None
        self._label: str | None = None
        self._requests: dict[int, dict[str, Any]] = {}
        self._summary: dict[str, Any] = {}
        self._postcheck: dict[str, Any] = {}
        self._pass_criteria: dict[str, Any] = {}
        self._report_path = ""
        self._error = ""

    def configure(
        self,
        args: argparse.Namespace,
        model: str | None = None,
        label: str | None = None,
    ) -> None:
        with self._lock:
            self._config = {
                "base_url": args.base_url,
                "requests": args.requests,
                "concurrency": args.concurrency,
                "max_tokens": args.max_tokens,
                "timeout": args.timeout,
                "stream": args.stream,
            }
            self._model = model
            self._label = label
            self._status = "테스트 준비 중"

    def set_status(self, status: str) -> None:
        with self._lock:
            self._status = status

    def set_error(self, error: str) -> None:
        with self._lock:
            self._status = "오류"
            self._error = error
            self._completed_at = time.time()

    def start_request(self, index: int, prompt_config: dict[str, Any],
                      has_image: bool) -> None:
        with self._lock:
            self._requests[index] = {
                "index": index + 1,
                "prompt": str(prompt_config["content"]),
                "enable_thinking": bool(prompt_config["enable_thinking"]),
                "has_image": has_image,
                "status": "진행 중",
                "started_at": time.time(),
                "finished_at": None,
                "answer": "",
                "thinking": "",
                "result": None,
            }

    def append_text(self, index: int, kind: str, text: str) -> None:
        if not text:
            return
        field = "thinking" if kind == "thinking" else "answer"
        with self._lock:
            item = self._requests.get(index)
            if not item:
                return
            item[field] = f"{item.get(field, '')}{text}"[-MAX_DASHBOARD_TEXT_CHARS:]

    def finish_request(self, result: RequestResult) -> None:
        with self._lock:
            item = self._requests.setdefault(
                result.index,
                {
                    "index": result.index + 1,
                    "prompt": "",
                    "enable_thinking": False,
                    "has_image": False,
                    "started_at": None,
                    "answer": "",
                    "thinking": "",
                },
            )
            outcome = _answer_outcome(result)
            if outcome in ("truncated", "truncated_empty"):
                status = "상한 도달"
            elif outcome == "empty":
                status = "답변 없음"
            elif result.ok:
                status = "완료"
            elif _is_overload_rejection(result):
                status = "429 방어"
            else:
                status = "실패"
            item["status"] = status
            item["finished_at"] = time.time()
            item["latency_ms"] = result.latency_ms
            item["result"] = asdict(result)

    def complete(
        self,
        *,
        summary: dict[str, Any],
        postcheck: dict[str, Any],
        pass_criteria: dict[str, Any],
        report_path: str,
    ) -> None:
        with self._lock:
            self._summary = summary
            self._postcheck = postcheck
            self._pass_criteria = pass_criteria
            self._report_path = report_path
            self._completed_at = time.time()
            if not pass_criteria["passed"]:
                self._status = "실패"
            elif pass_criteria.get("warnings"):
                self._status = "완료 (경고 있음)"
            else:
                self._status = "완료"

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "started_at": self._started_at,
                "completed_at": self._completed_at,
                "status": self._status,
                "config": dict(self._config),
                "model": self._model,
                "label": self._label,
                "requests": [dict(item) for _, item in sorted(self._requests.items())],
                "summary": dict(self._summary),
                "postcheck": dict(self._postcheck),
                "pass_criteria": dict(self._pass_criteria),
                "report_path": self._report_path,
                "error": self._error,
            }


_DASHBOARD_HTML = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>vLLM 트래픽 진행 화면</title>
  <style>
    :root {
      --orange: #F37321;
      --orange-dark: #C75E14;
      --navy: #1A2B4A;
      --navy-soft: #273A5B;
      --bg: #F7F9FC;
      --surface: #FFFFFF;
      --surface-2: #EEF2F7;
      --line: #D8E0EA;
      --text: #14213D;
      --muted: #64748B;
      --success: #16A34A;
      --warning: #B45309;
      --danger: #DC2626;
      --info: #3B82F6;
      --shadow: 0 14px 36px rgba(26, 43, 74, 0.14);
      --request-card-height: 560px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "HanwhaGothic", "IBM Plex Sans", "AtoZ", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .topbar {
      background: var(--navy);
      color: white;
      border-bottom: 4px solid var(--orange);
    }
    .topbar-inner {
      width: min(1440px, 100%);
      margin: 0 auto;
      padding: 22px 28px;
      display: flex;
      justify-content: space-between;
      gap: 20px;
      align-items: center;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }
    .mark {
      width: 52px;
      height: 36px;
      border-radius: 12px;
      background: var(--orange);
      display: grid;
      place-items: center;
      font-size: 12px;
      font-weight: 800;
      color: white;
      box-shadow: 0 10px 24px rgba(243, 115, 33, 0.26);
    }
    h1 {
      margin: 0;
      font-family: "Hanwha", "HanwhaGothic", system-ui, sans-serif;
      font-size: 24px;
      line-height: 1.15;
      letter-spacing: 0;
    }
    .target {
      margin-top: 6px;
      color: #DDE6F2;
      font-size: 13px;
      word-break: break-all;
    }
    .status {
      min-width: 108px;
      border: 1px solid rgba(255, 255, 255, 0.22);
      border-radius: 12px;
      padding: 10px 14px;
      background: rgba(255, 255, 255, 0.08);
      color: white;
      font-weight: 700;
      text-align: center;
      white-space: nowrap;
    }
    main {
      width: min(1440px, 100%);
      margin: 0 auto;
      padding: 24px 28px 32px;
    }
    .metrics {
      display: grid;
      grid-template-columns: repeat(6, minmax(130px, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }
    .metric, .panel, .request {
      border: 1px solid var(--line);
      background: var(--surface);
      box-shadow: var(--shadow);
    }
    .metric {
      border-radius: 16px;
      padding: 15px 16px;
      min-height: 84px;
    }
    .metric span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 8px;
    }
    .metric strong {
      display: block;
      color: var(--navy);
      font-size: 25px;
      line-height: 1.1;
      overflow-wrap: anywhere;
    }
    .layout {
      display: grid;
      grid-template-columns: minmax(260px, 360px) minmax(0, 1fr);
      gap: 16px;
      align-items: start;
    }
    .panel {
      border-radius: 16px;
      padding: 16px;
      position: sticky;
      top: 16px;
    }
    .panel h2 {
      margin: 0 0 14px;
      font-family: "Hanwha", "HanwhaGothic", system-ui, sans-serif;
      font-size: 16px;
      letter-spacing: 0;
    }
    .kv {
      display: grid;
      grid-template-columns: 108px minmax(0, 1fr);
      gap: 10px 12px;
      color: var(--muted);
      font-size: 13px;
    }
    .kv b {
      color: var(--text);
      font-weight: 700;
      overflow-wrap: anywhere;
    }
    .progress {
      height: 12px;
      overflow: hidden;
      border-radius: 999px;
      background: var(--surface-2);
      border: 1px solid var(--line);
      margin-top: 16px;
    }
    .progress div {
      height: 100%;
      width: 0%;
      background: var(--orange);
      transition: width 250ms ease;
    }
    .requests {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      grid-auto-rows: var(--request-card-height);
      gap: 12px;
    }
    .request {
      border-radius: 16px;
      overflow: hidden;
      min-width: 0;
      height: var(--request-card-height);
      min-height: 0;
      display: flex;
      flex-direction: column;
    }
    .request-head {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      padding: 12px 14px;
      background: #FBFCFE;
      border-bottom: 1px solid var(--line);
      flex: 0 0 auto;
    }
    .request-title {
      display: flex;
      gap: 8px;
      align-items: center;
      min-width: 0;
      font-weight: 800;
      color: var(--navy);
    }
    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 3px 8px;
      border-radius: 8px;
      border: 1px solid var(--line);
      color: var(--muted);
      background: white;
      font-size: 12px;
      white-space: nowrap;
    }
    .badge.done { color: var(--success); border-color: rgba(22, 163, 74, 0.36); }
    .badge.fail { color: var(--danger); border-color: rgba(220, 38, 38, 0.36); }
    .badge.wait { color: var(--warning); border-color: rgba(180, 83, 9, 0.36); }
    .badge.img { color: var(--navy); border-color: rgba(26, 43, 74, 0.36); }
    .prompt {
      margin: 0;
      padding: 12px 14px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.55;
      border-bottom: 1px solid var(--line);
      flex: 0 0 88px;
      overflow: auto;
    }
    pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: "IBM Plex Sans", "HanwhaGothic", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      line-height: 1.55;
      font-size: 13px;
    }
    .thinking {
      border-bottom: 1px solid var(--line);
      background: rgba(59, 130, 246, 0.06);
      flex: 0 0 132px;
      min-height: 0;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    .thinking-title {
      padding: 10px 14px;
      color: var(--info);
      font-size: 13px;
      font-weight: 800;
      flex: 0 0 auto;
    }
    .thinking pre {
      padding: 0 14px 12px;
      color: #284A7A;
      flex: 1 1 auto;
      min-height: 0;
      height: 0;
      overflow: auto;
      overscroll-behavior: contain;
    }
    .answer {
      flex: 1 1 auto;
      min-height: 0;
      overflow: auto;
      overscroll-behavior: contain;
      padding: 14px;
      color: var(--text);
      background: white;
    }
    .empty {
      color: var(--muted);
    }
    @media (max-width: 1100px) {
      .metrics { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .layout { grid-template-columns: 1fr; }
      .panel { position: static; }
    }
    @media (max-width: 760px) {
      :root { --request-card-height: 620px; }
      .topbar-inner, main { padding-left: 18px; padding-right: 18px; }
      .topbar-inner { align-items: flex-start; flex-direction: column; }
      .metrics, .requests { grid-template-columns: 1fr; }
      .status { white-space: normal; }
    }
  </style>
</head>
<body>
  <header class="topbar">
    <div class="topbar-inner">
      <div class="brand">
        <div class="mark">vLLM</div>
        <div>
          <h1>vLLM 트래픽 진행 화면</h1>
          <div class="target" id="target">대상 서버 확인 중</div>
        </div>
      </div>
      <div class="status" id="status">준비 중</div>
    </div>
  </header>
  <main>
    <section class="metrics" id="metrics"></section>
    <section class="layout">
      <aside class="panel">
        <h2>실행 설정</h2>
        <div class="kv" id="config"></div>
        <div class="progress"><div id="bar"></div></div>
      </aside>
      <section class="requests" id="requests"></section>
    </section>
  </main>
  <script>
    const metricsEl = document.getElementById('metrics');
    const requestsEl = document.getElementById('requests');
    const configEl = document.getElementById('config');
    const statusEl = document.getElementById('status');
    const targetEl = document.getElementById('target');
    const barEl = document.getElementById('bar');

    function esc(value) {
      return String(value ?? '').replace(/[&<>"']/g, (ch) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
      }[ch]));
    }

    function fixed(value, digits = 2) {
      return Number.isFinite(value) ? value.toFixed(digits) : '-';
    }

    function requestSeconds(request) {
      return Number.isFinite(request.latency_ms) ? request.latency_ms / 1000 : null;
    }

    function requestTps(request) {
      const seconds = Number.isFinite(request.latency_ms) && Number.isFinite(request.result?.ttft_ms)
        ? (request.latency_ms - request.result.ttft_ms) / 1000
        : null;
      const tokens = request.result?.completion_tokens;
      if (!seconds || !Number.isFinite(tokens)) return null;
      return tokens / seconds;
    }

    function metric(label, value) {
      return `<div class="metric"><span>${esc(label)}</span><strong>${esc(value)}</strong></div>`;
    }

    function badgeClass(status) {
      if (status === '완료') return 'done';
      if (status === '실패') return 'fail';
      if (status === '답변 없음') return 'fail';
      if (status === '429 방어' || status === '상한 도달') return 'wait';
      return '';
    }

    // 답변 칸이 빈 이유. 끝난 요청에 "응답 대기 중"을 띄우면 아직 기다리는 것으로 오해한다.
    function emptyAnswerText(request) {
      const result = request.result;
      if (!result) return request.thinking ? '사고 중 — 답변은 사고가 끝난 뒤 나옵니다' : '응답 대기 중';
      if (!result.ok) return `응답 실패: ${result.error || result.status}`;
      if (result.finish_reason === 'length') return '답변 없음 — 생성 상한(max_tokens)에 도달해 사고 중에 끊겼습니다';
      return '답변 없음 — 모델이 답변 없이 끝냈습니다';
    }

    function renderRequest(request) {
      const status = request.status || '대기';
      const thinking = request.thinking
        ? `<div class="thinking"><div class="thinking-title">생각 과정</div><pre data-scroll-key="thinking-${esc(request.index)}">${esc(request.thinking)}</pre></div>`
        : '';
      const answer = request.answer
        ? esc(request.answer)
        : `<span class="empty">${esc(emptyAnswerText(request))}</span>`;
      const seconds = requestSeconds(request);
      const tps = requestTps(request);
      return `
        <article class="request">
          <div class="request-head">
            <div class="request-title">
              <span>#${esc(request.index)}</span>
              <span class="badge">${request.enable_thinking ? '생각 켬' : '생각 끔'}</span>
              ${request.has_image ? '<span class="badge img">🖼 이미지</span>' : ''}
            </div>
            <div>
              <span class="badge ${badgeClass(status)}">${esc(status)}</span>
              ${seconds ? `<span class="badge">${esc(fixed(seconds, 1))}s</span>` : ''}
              ${tps ? `<span class="badge">${esc(fixed(tps, 1))} tok/s</span>` : ''}
            </div>
          </div>
          <p class="prompt">${esc(request.prompt)}</p>
          ${thinking}
          <pre class="answer" data-scroll-key="answer-${esc(request.index)}">${answer}</pre>
        </article>
      `;
    }

    function collectScrollState() {
      const state = new Map();
      document.querySelectorAll('[data-scroll-key]').forEach((el) => {
        const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
        state.set(el.dataset.scrollKey, {
          top: el.scrollTop,
          stickToBottom: distanceFromBottom <= 24,
        });
      });
      return state;
    }

    function syncGeneratedTextScroll(previousScroll) {
      const scroll = () => {
        document.querySelectorAll('[data-scroll-key]').forEach((el) => {
          const previous = previousScroll.get(el.dataset.scrollKey);
          if (!previous || previous.stickToBottom) {
            el.scrollTop = el.scrollHeight;
            return;
          }
          el.scrollTop = Math.min(previous.top, el.scrollHeight);
        });
      };
      requestAnimationFrame(() => {
        scroll();
        requestAnimationFrame(scroll);
      });
    }

    function render(state) {
      const scrollState = collectScrollState();
      const config = state.config || {};
      const summary = state.summary || {};
      const requests = state.requests || [];
      const finished = summary.sent ?? requests.filter((item) => item.result).length;
      const total = config.requests || requests.length || 0;
      const ok = summary.ok ?? requests.filter((item) => item.result?.ok).length;
      const rejected = summary.overload_rejected ?? requests.filter((item) => item.status === '429 방어').length;
      const failed = summary.failed ?? requests.filter((item) => item.status === '실패').length;
      const truncated = summary.length_truncated ?? requests.filter((item) => item.status === '상한 도달').length;
      const noAnswer = summary.empty_answer ?? requests.filter((item) => item.result?.ok && !item.result?.answer_chars).length;
      const progress = total > 0 ? Math.min(100, Math.round((finished / total) * 100)) : 0;

      statusEl.textContent = state.status || '준비 중';
      const modelText = state.model || '모델 확인 중';
      const labelText = state.label && state.label !== state.model ? ` (${state.label})` : '';
      targetEl.textContent = `${config.base_url || '-'} · ${modelText}${labelText}`;
      barEl.style.width = `${progress}%`;

      metricsEl.innerHTML = [
        metric('진행률', `${finished}/${total}`),
        metric('성공', ok),
        metric('429 방어', rejected),
        metric('실패', failed),
        metric('상한 도달', truncated),
        metric('답변 없음', noAnswer),
        metric('RPS', fixed(summary.requests_per_second)),
        metric('서버 TPS', fixed(summary.completion_tokens_per_second)),
        metric('실제 TPS p50', fixed(summary.decode_tokens_per_second?.p50)),
      ].join('');

      configEl.innerHTML = [
        ['요청 수', config.requests],
        ['동시성', config.concurrency],
        ['최대 토큰', config.max_tokens],
        ['타임아웃', `${config.timeout ?? '-'}초`],
        ['스트리밍', config.stream ? '사용' : '미사용'],
        ['리포트', state.report_path || '-'],
      ].map(([key, value]) => `<span>${esc(key)}</span><b>${esc(value)}</b>`).join('');

      if (state.error) {
        requestsEl.innerHTML = `<article class="request"><pre class="answer" data-scroll-key="error">${esc(state.error)}</pre></article>`;
        syncGeneratedTextScroll(scrollState);
        return;
      }
      requestsEl.innerHTML = requests.length
        ? requests.map(renderRequest).join('')
        : '<article class="request"><pre class="answer empty" data-scroll-key="empty">요청 준비 중</pre></article>';
      syncGeneratedTextScroll(scrollState);
    }

    async function refresh() {
      try {
        const res = await fetch('/state', { cache: 'no-store' });
        render(await res.json());
      } catch (error) {
        statusEl.textContent = '연결 대기';
      }
    }

    refresh();
    setInterval(refresh, 500);
  </script>
</body>
</html>
"""


def _make_dashboard_handler(state: DashboardState) -> type[BaseHTTPRequestHandler]:
    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            path = self.path.split("?", 1)[0]
            if path == "/":
                self._send_bytes(_DASHBOARD_HTML.encode("utf-8"), "text/html; charset=utf-8")
                return
            if path == "/state":
                payload = json.dumps(state.snapshot(), ensure_ascii=False).encode("utf-8")
                self._send_bytes(payload, "application/json; charset=utf-8")
                return
            self.send_error(404)

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _send_bytes(self, body: bytes, content_type: str) -> None:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

    return DashboardHandler


def _start_dashboard_server(
    host: str,
    port: int,
    state: DashboardState,
) -> tuple[ThreadingHTTPServer, str]:
    server = ThreadingHTTPServer((host, port), _make_dashboard_handler(state))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    bound_host, bound_port = server.server_address[:2]
    display_host = "127.0.0.1" if bound_host in ("0.0.0.0", "::") else bound_host
    return server, f"http://{display_host}:{bound_port}"


def _wait_for_dashboard_shutdown(server: ThreadingHTTPServer, url: str) -> None:
    print("")
    print(f"진행 화면 유지 중: {url}")
    print("종료하려면 Ctrl+C를 누르세요.")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("")
        print("진행 화면 종료")
    finally:
        server.shutdown()
        server.server_close()


def _percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    pos = (len(ordered) - 1) * pct
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


def _format_float(value: Any) -> str:
    if value is None:
        return "-"
    return f"{float(value):.2f}"


def _format_ms_as_seconds(value: Any) -> str:
    if value is None:
        return "-"
    return f"{float(value) / 1000:.2f}s"


def _request_json(
    url: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    timeout: float = 30,
) -> tuple[int, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw
        return e.code, parsed


def _snapshot(base_url: str, timeout: float) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for path in ("/health", "/server-status", "/v1/models"):
        try:
            status, body = _request_json(f"{base_url}{path}", timeout=timeout)
            data[path] = {"status": status, "body": body}
        except Exception as e:
            data[path] = {"status": "error", "body": f"{type(e).__name__}: {e}"}
    return data


def _resolve_model(base_url: str, model: str | None, timeout: float) -> str:
    if model:
        return model
    status, body = _request_json(f"{base_url}/v1/models", timeout=timeout)
    if status != 200:
        raise RuntimeError(f"/v1/models HTTP {status}: {body}")
    models = body.get("data") or []
    if not models or not models[0].get("id"):
        raise RuntimeError(f"/v1/models 응답에서 모델명을 찾지 못함: {body}")
    return models[0]["id"]


def _prompt_for_index(index: int) -> dict[str, Any]:
    return PROMPTS[index % len(PROMPTS)]


def _build_image_pool(size: int, edge: int) -> list[str]:
    """서로 다른 이미지 size개를 data URL로 만든다.

    같은 이미지를 재사용하면 encoder/prefix 캐시에 히트해 프리필이 사라지므로
    멀티모달 부하가 재현되지 않는다. 픽셀을 바꿔 mm_hash를 서로 다르게 만든다.
    edge는 한 변 픽셀 수 — Qwen3-VL 계열은 실효 패치가 32x32라 4096이면 이미지
    1장이 약 16,400 tok로 이미지 프로세서 상한(16,777,216 px)에 해당한다.
    """
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit("이미지 부하에는 Pillow가 필요합니다 "
                         "(pip install pillow, 또는 --image-ratio 0으로 텍스트만 테스트)")

    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image.png")
    if not os.path.exists(base_path):
        raise SystemExit(f"이미지 원본이 없습니다: {base_path}")

    pool: list[str] = []
    for i in range(size):
        img = Image.open(base_path).convert("RGB").resize((edge, edge), Image.BICUBIC)
        px = img.load()
        for k in range((i + 1) * 64):
            x, y = k % img.width, (k // img.width) % img.height
            r, g, b = px[x, y]
            px[x, y] = ((r + 37 * (i + 1)) % 256, (g + 11 * (i + 1)) % 256, (b + 7 * k) % 256)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=92)   # PNG는 수십 MB — 전송량 때문에 JPEG
        pool.append("data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode())
    return pool


def _wants_image(index: int) -> bool:
    """이 요청에 이미지를 실을지. --image-ratio 비율만큼 요청 순서에 고르게 섞는다."""
    if not _IMAGE_POOL or _IMAGE_RATIO <= 0:
        return False
    # 누적 개수가 한 장 넘어가는 지점에서만 참 — 0.5면 한 건 걸러 한 건이 된다.
    # 앞쪽 N개를 먼저 채우는 방식은 요청 수가 적으면 전부 이미지가 되어 비율이 무시된다.
    return math.floor((index + 1) * _IMAGE_RATIO) > math.floor(index * _IMAGE_RATIO)


def _coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(value)


def _extract_message_text(payload: Any) -> tuple[str, str]:
    if not isinstance(payload, dict):
        return "", ""
    choices = payload.get("choices") or []
    if not choices:
        return "", ""
    message = choices[0].get("message") or {}
    answer = _coerce_text(message.get("content"))
    thinking = _coerce_text(message.get("reasoning_content") or message.get("reasoning"))
    return answer, thinking


def _chat_once(
    *,
    base_url: str,
    model: str,
    index: int,
    stream: bool,
    max_tokens: int,
    timeout: float,
    token_callback: Callable[[int, str, str], None] | None = None,
) -> RequestResult:
    prompt_config = _prompt_for_index(index)
    prompt = str(prompt_config["content"])
    enable_thinking = bool(prompt_config["enable_thinking"])
    content: Any = prompt
    if _wants_image(index):
        content = [
            {"type": "image_url",
             "image_url": {"url": _IMAGE_POOL[index % len(_IMAGE_POOL)]}},
            {"type": "text", "text": prompt},
        ]
    body = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": max_tokens,
        "temperature": 0,
        "chat_template_kwargs": {"enable_thinking": enable_thinking},
    }
    if enable_thinking:
        body["skip_special_tokens"] = False
    if stream:
        body["stream"] = True
        body["stream_options"] = {"include_usage": True}

    start = time.monotonic()
    if stream:
        return _stream_once(base_url, body, index, timeout, start, token_callback)
    return _non_stream_once(base_url, body, index, timeout, start, token_callback)


def _is_overload_rejection(result: RequestResult) -> bool:
    return result.status == 429


def _is_allowed_result(result: RequestResult) -> bool:
    return result.ok or _is_overload_rejection(result)


def _non_stream_once(
    base_url: str,
    body: dict[str, Any],
    index: int,
    timeout: float,
    start: float,
    token_callback: Callable[[int, str, str], None] | None,
) -> RequestResult:
    try:
        status, payload = _request_json(
            f"{base_url}/v1/chat/completions",
            method="POST",
            body=body,
            timeout=timeout,
        )
        latency_ms = (time.monotonic() - start) * 1000
        usage = payload.get("usage", {}) if isinstance(payload, dict) else {}
        ok = status == 200
        error = "" if ok else _short_error(payload)
        answer, thinking = _extract_message_text(payload)
        choices = payload.get("choices") if isinstance(payload, dict) else None
        finish_reason = choices[0].get("finish_reason") if choices else None
        if ok and token_callback:
            token_callback(index, "thinking", thinking)
            token_callback(index, "answer", answer)
        return RequestResult(
            index=index,
            ok=ok,
            status=status,
            latency_ms=latency_ms,
            ttft_ms=None,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            error=error,
            finish_reason=str(finish_reason) if finish_reason else None,
            answer_chars=_visible_chars(answer),
            reasoning_tokens=_reasoning_tokens(usage),
        )
    except Exception as e:
        return _exception_result(index, start, e)


def _stream_once(
    base_url: str,
    body: dict[str, Any],
    index: int,
    timeout: float,
    start: float,
    token_callback: Callable[[int, str, str], None] | None,
) -> RequestResult:
    headers = {"Accept": "text/event-stream", "Content-Type": "application/json"}
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=data,
        headers=headers,
        method="POST",
    )
    usage: dict[str, Any] = {}
    first_token_at: float | None = None
    finish_reason: str | None = None
    answer_chars = 0
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                item = line[5:].strip()
                if item == "[DONE]":
                    break
                try:
                    chunk = json.loads(item)
                except json.JSONDecodeError:
                    continue
                if chunk.get("usage"):
                    usage = chunk["usage"]
                choices = chunk.get("choices") or []
                if choices:
                    if choices[0].get("finish_reason"):
                        finish_reason = str(choices[0]["finish_reason"])
                    delta = choices[0].get("delta") or {}
                    answer_text = _coerce_text(delta.get("content"))
                    thinking_text = _coerce_text(
                        delta.get("reasoning_content") or delta.get("reasoning")
                    )
                    answer_chars += _visible_chars(answer_text)
                    if first_token_at is None and (answer_text or thinking_text):
                        first_token_at = time.monotonic()
                    if token_callback:
                        token_callback(index, "thinking", thinking_text)
                        token_callback(index, "answer", answer_text)
            latency_ms = (time.monotonic() - start) * 1000
            ttft_ms = None if first_token_at is None else (first_token_at - start) * 1000
            return RequestResult(
                index=index,
                ok=resp.status == 200,
                status=resp.status,
                latency_ms=latency_ms,
                ttft_ms=ttft_ms,
                prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"),
                total_tokens=usage.get("total_tokens"),
                error="",
                finish_reason=finish_reason,
                answer_chars=answer_chars,
                reasoning_tokens=_reasoning_tokens(usage),
            )
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        return RequestResult(
            index=index,
            ok=False,
            status=e.code,
            latency_ms=(time.monotonic() - start) * 1000,
            ttft_ms=None,
            prompt_tokens=None,
            completion_tokens=None,
            total_tokens=None,
            error=_short_error(raw),
        )
    except Exception as e:
        return _exception_result(index, start, e)


def _exception_result(index: int, start: float, exc: Exception) -> RequestResult:
    return RequestResult(
        index=index,
        ok=False,
        status=f"{type(exc).__name__}",
        latency_ms=(time.monotonic() - start) * 1000,
        ttft_ms=None,
        prompt_tokens=None,
        completion_tokens=None,
        total_tokens=None,
        error=str(exc),
    )


def _short_error(payload: Any, max_len: int = 500) -> str:
    if isinstance(payload, (dict, list)):
        text = json.dumps(payload, ensure_ascii=False)
    else:
        text = str(payload)
    return text[:max_len]


def _run_traffic(
    args: argparse.Namespace,
    model: str,
    dashboard: DashboardState | None = None,
) -> tuple[list[RequestResult], bool]:
    work: queue.Queue[int] = queue.Queue()
    for i in range(args.requests):
        work.put(i)

    results: list[RequestResult] = []
    lock = threading.Lock()
    stop_event = threading.Event()
    tripped = False

    def should_trip() -> bool:
        if len(results) < args.min_requests_before_break:
            return False
        failures = [r for r in results if not _is_allowed_result(r)]
        if len(failures) >= args.max_consecutive_errors:
            tail = results[-args.max_consecutive_errors :]
            if len(tail) == args.max_consecutive_errors and all(
                not _is_allowed_result(r) for r in tail
            ):
                return True
        return len(failures) / len(results) > args.max_error_rate

    def worker() -> None:
        nonlocal tripped
        while not stop_event.is_set():
            try:
                idx = work.get_nowait()
            except queue.Empty:
                return
            if dashboard:
                dashboard.start_request(idx, _prompt_for_index(idx), _wants_image(idx))
            result = _chat_once(
                base_url=args.base_url,
                model=model,
                index=idx,
                stream=args.stream,
                max_tokens=args.max_tokens,
                timeout=args.timeout,
                token_callback=dashboard.append_text if dashboard else None,
            )
            if dashboard:
                dashboard.finish_request(result)
            with lock:
                results.append(result)
                if should_trip():
                    tripped = True
                    stop_event.set()
            work.task_done()
            if args.sleep_seconds > 0:
                time.sleep(args.sleep_seconds)

    threads = []
    delay = args.ramp_up_seconds / max(args.concurrency - 1, 1)
    for _ in range(args.concurrency):
        t = threading.Thread(target=worker, daemon=True)
        threads.append(t)
        t.start()
        if delay > 0:
            time.sleep(delay)
    for t in threads:
        t.join()
    return sorted(results, key=lambda r: r.index), tripped


def _summarize(results: list[RequestResult], elapsed_s: float) -> dict[str, Any]:
    ok_results = [r for r in results if r.ok]
    rejected_results = [r for r in results if _is_overload_rejection(r)]
    failed_results = [r for r in results if not _is_allowed_result(r)]
    latencies = [r.latency_ms for r in ok_results]
    ttfts = [r.ttft_ms for r in ok_results if r.ttft_ms is not None]
    completion_tokens = [r.completion_tokens or 0 for r in ok_results]
    total_completion_tokens = sum(completion_tokens)
    decode_tokens_per_second = [
        r.completion_tokens / ((r.latency_ms - r.ttft_ms) / 1000)
        for r in ok_results
        if r.completion_tokens
        and r.ttft_ms is not None
        and r.latency_ms > r.ttft_ms
    ]
    status_counts: dict[str, int] = {}
    for r in results:
        key = str(r.status)
        status_counts[key] = status_counts.get(key, 0) + 1
    finish_reason_counts: dict[str, int] = {}
    for r in ok_results:
        key = str(r.finish_reason)
        finish_reason_counts[key] = finish_reason_counts.get(key, 0) + 1
    outcomes = [_answer_outcome(r) for r in ok_results]

    return {
        "sent": len(results),
        "ok": len(ok_results),
        "overload_rejected": len(rejected_results),
        "allowed": len(results) - len(failed_results),
        "failed": len(failed_results),
        "error_rate": 0 if not results else len(failed_results) / len(results),
        "status_counts": status_counts,
        "finish_reason_counts": finish_reason_counts,
        # HTTP 200 중 생성 상한에 걸린 건수와, 답변이 0자인 건수(상한 도달 포함)
        "length_truncated": sum(o in ("truncated", "truncated_empty") for o in outcomes),
        "empty_answer": sum(o in ("truncated_empty", "empty") for o in outcomes),
        "empty_answer_not_truncated": outcomes.count("empty"),
        "elapsed_seconds": elapsed_s,
        "requests_per_second": 0 if elapsed_s <= 0 else len(results) / elapsed_s,
        "completion_tokens_per_second": 0 if elapsed_s <= 0 else total_completion_tokens / elapsed_s,
        "decode_tokens_per_second": {
            "avg": (
                sum(decode_tokens_per_second) / len(decode_tokens_per_second)
                if decode_tokens_per_second
                else None
            ),
            "p50": statistics.median(decode_tokens_per_second)
            if decode_tokens_per_second
            else None,
            "p95": _percentile(decode_tokens_per_second, 0.95),
            "min": min(decode_tokens_per_second) if decode_tokens_per_second else None,
            "max": max(decode_tokens_per_second) if decode_tokens_per_second else None,
        },
        "latency_ms": {
            "min": min(latencies) if latencies else None,
            "p50": statistics.median(latencies) if latencies else None,
            "p95": _percentile(latencies, 0.95),
            "p99": _percentile(latencies, 0.99),
            "max": max(latencies) if latencies else None,
        },
        "ttft_ms": {
            "p50": statistics.median(ttfts) if ttfts else None,
            "p95": _percentile(ttfts, 0.95),
            "max": max(ttfts) if ttfts else None,
        },
    }


def _postcheck(snapshot: dict[str, Any]) -> dict[str, Any]:
    health_status = snapshot.get("/health", {}).get("status")
    server_status = snapshot.get("/server-status", {}).get("status")
    failures = []
    if health_status != 200:
        failures.append(f"/health HTTP {health_status}")
    if server_status != 200:
        failures.append(f"/server-status HTTP {server_status}")
    return {
        "ok": not failures,
        "health_status": health_status,
        "server_status": server_status,
        "failures": failures,
    }


def _evaluate_pass(
    args: argparse.Namespace,
    summary: dict[str, Any],
    tripped: bool,
    postcheck: dict[str, Any],
) -> dict[str, Any]:
    failures = []
    if tripped:
        failures.append("회로차단 발생")
    if summary["failed"] > 0:
        failures.append(f"허용되지 않은 실패 {summary['failed']}건")
    if args.require_200 and summary["ok"] == 0:
        failures.append("HTTP 200 성공 응답 없음")
    if args.require_429 and summary["overload_rejected"] == 0:
        failures.append("HTTP 429 과부하 차단 응답 없음")
    if not postcheck["ok"]:
        failures.extend(postcheck["failures"])
    # 상한에 걸리지 않았는데 답이 없으면 서버·파서 쪽 이상이라 실패로 본다.
    if summary["empty_answer_not_truncated"] > 0:
        failures.append(f"답변 없이 끝난 HTTP 200 {summary['empty_answer_not_truncated']}건")
    # 상한 도달은 요청 설정(max_tokens)과 질문 길이의 문제라 서버 안정성 판정에서는 경고로 둔다.
    # 숨기지 않도록 리포트·출력·진행 화면에 건수를 남긴다.
    warnings = []
    if summary["length_truncated"] > 0:
        warnings.append(
            f"생성 상한(max_tokens={args.max_tokens}) 도달 {summary['length_truncated']}건, "
            f"그중 답변 없음 {summary['empty_answer'] - summary['empty_answer_not_truncated']}건"
        )
    return {
        "passed": not failures,
        "require_200": args.require_200,
        "require_429": args.require_429,
        "failures": failures,
        "warnings": warnings,
    }


def _write_report(args: argparse.Namespace, report: dict[str, Any]) -> str:
    os.makedirs(args.output_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(args.output_dir, f"traffic_{stamp}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="vLLM 게이트웨이 하드 트래픽 테스트")
    p.add_argument("--base-url", default="http://localhost:5015", help="게이트웨이 URL")
    p.add_argument("--model", default=None, help="요청에 실을 모델명. 미지정 시 /v1/models에서 자동 추출")
    p.add_argument("--label", default=None,
                   help="리포트에 남길 백엔드 체크포인트 표시명 (예: Qwen3.8-27B-FP8). "
                        "요청에는 쓰이지 않는다. 미지정 시 --model/자동 추출값과 동일")
    p.add_argument("--mode", choices=("smoke", "overload"), default=None, help=argparse.SUPPRESS)
    p.add_argument("--requests", type=int, default=None, help="총 요청 수")
    p.add_argument("--concurrency", type=int, default=None, help="동시 요청 수")
    p.add_argument("--max-tokens", type=int, default=None, help="요청당 최대 생성 토큰")
    p.add_argument("--timeout", type=float, default=None, help="요청 타임아웃 초")
    p.add_argument("--stream", action="store_true", help="SSE 스트리밍으로 테스트")
    p.add_argument("--image-ratio", type=float, default=None,
                   help="이미지를 포함할 요청 비율 0~1 (기본 0.5 = 절반, 0이면 텍스트만). "
                        "요청마다 다른 이미지를 실어 encoder/prefix 캐시를 우회한다")
    p.add_argument("--image-edge", type=int, default=None,
                   help="이미지 한 변 픽셀 (기본 4096 ≈ 16,400 tok/장)")
    p.add_argument("--ramp-up-seconds", type=float, default=None, help="워커 시작 분산 시간")
    p.add_argument("--sleep-seconds", type=float, default=None, help="워커별 요청 사이 휴식")
    p.add_argument("--max-error-rate", type=float, default=None, help="초과 시 조기 중단")
    p.add_argument("--max-consecutive-errors", type=int, default=None, help="연속 실패 조기 중단 기준")
    p.add_argument("--min-requests-before-break", type=int, default=None, help="회로차단 판단 최소 요청 수")
    p.add_argument(
        "--require-200",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="HTTP 200 응답을 통과 조건으로 요구",
    )
    p.add_argument(
        "--require-429",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="HTTP 429 과부하 차단 응답을 통과 조건으로 요구",
    )
    p.add_argument("--output-dir", default="logs", help="결과 JSON 저장 디렉토리")
    p.add_argument(
        "--ui",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="로컬 진행 화면 URL을 띄우고 요청별 생성 내용을 표시",
    )
    p.add_argument("--ui-host", default="127.0.0.1", help="진행 화면 바인딩 주소")
    p.add_argument("--ui-port", type=int, default=0, help="진행 화면 포트. 0은 자동 할당")
    args = p.parse_args()
    args.base_url = args.base_url.rstrip("/")
    for key, value in DEFAULT_TRAFFIC_CONFIG.items():
        if getattr(args, key) is None:
            setattr(args, key, value)
    args.effective_defaults = {key: getattr(args, key) for key in DEFAULT_TRAFFIC_CONFIG}
    if args.requests < 1:
        raise SystemExit("--requests는 1 이상이어야 합니다")
    if args.concurrency < 1:
        raise SystemExit("--concurrency는 1 이상이어야 합니다")
    if args.concurrency > args.requests:
        args.concurrency = args.requests
    if args.ui_port < 0:
        raise SystemExit("--ui-port는 0 이상이어야 합니다")
    if not 0.0 <= args.image_ratio <= 1.0:
        raise SystemExit("--image-ratio는 0~1 사이여야 합니다")
    if args.image_edge < 64:
        raise SystemExit("--image-edge는 64 이상이어야 합니다")
    return args


def main() -> None:
    global _IMAGE_POOL, _IMAGE_RATIO

    args = parse_args()
    if args.ui and not args.stream:
        args.stream = True

    if args.image_ratio > 0:
        # 동시에 도는 요청끼리 이미지가 겹치지 않도록 풀 크기를 동시성에 맞춘다.
        _IMAGE_RATIO = args.image_ratio
        print(f"이미지 풀 생성 중 ({args.concurrency}장, {args.image_edge}px)...")
        _IMAGE_POOL = _build_image_pool(args.concurrency, args.image_edge)

    dashboard = DashboardState() if args.ui else None
    dashboard_server: ThreadingHTTPServer | None = None
    dashboard_url = ""
    if dashboard:
        dashboard.configure(args)
        dashboard_server, dashboard_url = _start_dashboard_server(
            args.ui_host,
            args.ui_port,
            dashboard,
        )
        print(f"진행 화면: {dashboard_url}")

    try:
        model = _resolve_model(args.base_url, args.model, args.timeout)
    except Exception as e:
        if dashboard and dashboard_server:
            dashboard.set_error(f"{type(e).__name__}: {e}")
            _wait_for_dashboard_shutdown(dashboard_server, dashboard_url)
            sys.exit(1)
        raise
    # API 모델명은 인스턴스 yaml의 served_model_name으로 고정돼 있어, 리포트의
    # model만으로는 어떤 체크포인트를 잰 기록인지 알 수 없다. --label이 그 공백을 메운다.
    label = args.label or model
    if dashboard:
        dashboard.configure(args, model, label)

    print("vLLM 트래픽 테스트")
    print(f"  서버: {args.base_url}")
    print(f"  모델: {model}")
    if args.label:
        print(f"  체크포인트: {label}")
    else:
        print("  체크포인트: (--label 미지정 — 리포트에 백엔드 체크포인트가 남지 않습니다)")
    print(f"  요청: {args.requests}, 동시성: {args.concurrency}, stream={args.stream}")
    if args.image_ratio > 0:
        print(f"  이미지: 비율 {args.image_ratio:.0%}, {args.image_edge}px, 풀 {len(_IMAGE_POOL)}장")

    before = _snapshot(args.base_url, args.timeout)
    if dashboard:
        dashboard.set_status("트래픽 실행 중")
    start = time.monotonic()
    results, tripped = _run_traffic(args, model, dashboard)
    elapsed_s = time.monotonic() - start
    if dashboard:
        dashboard.set_status("결과 집계 중")
    after = _snapshot(args.base_url, args.timeout)
    summary = _summarize(results, elapsed_s)
    postcheck = _postcheck(after)
    pass_criteria = _evaluate_pass(args, summary, tripped, postcheck)

    report = {
        "config": {
            "base_url": args.base_url,
            "model": model,
            "label": label,
            "requests": args.requests,
            "concurrency": args.concurrency,
            "max_tokens": args.max_tokens,
            "timeout": args.timeout,
            "stream": args.stream,
            "max_error_rate": args.max_error_rate,
            "max_consecutive_errors": args.max_consecutive_errors,
            "require_200": args.require_200,
            "require_429": args.require_429,
            "image_ratio": args.image_ratio,
            "image_edge": args.image_edge,
            "ui": args.ui,
            # 질문이 바뀌면 지난 리포트와 지연·TPS를 바로 비교할 수 없다. 어떤 질문으로 잰 것인지 남긴다
            "prompts": PROMPTS,
        },
        "effective_defaults": args.effective_defaults,
        "circuit_breaker_tripped": tripped,
        "pass_criteria": pass_criteria,
        "postcheck": postcheck,
        "summary": summary,
        "snapshots": {"before": before, "after": after},
        "results": [asdict(r) for r in results],
    }
    report_path = _write_report(args, report)
    if dashboard:
        dashboard.complete(
            summary=summary,
            postcheck=postcheck,
            pass_criteria=pass_criteria,
            report_path=report_path,
        )

    print("")
    print("결과")
    print(f"  성공/전체: {summary['ok']}/{summary['sent']}")
    print(f"  429 방어 응답: {summary['overload_rejected']}")
    print(f"  허용/전체: {summary['allowed']}/{summary['sent']}")
    print(f"  에러율: {summary['error_rate']:.2%}")
    print(f"  상태코드: {summary['status_counts']}")
    print(
        f"  답변 점검: 상한 도달 {summary['length_truncated']}건, "
        f"답변 없음 {summary['empty_answer']}건 (상한 아닌데 답변 없음 {summary['empty_answer_not_truncated']}건), "
        f"종료 사유 {summary['finish_reason_counts']}"
    )
    print(f"  RPS: {_format_float(summary['requests_per_second'])}")
    print(f"  server TPS: {_format_float(summary['completion_tokens_per_second'])}")
    print(
        "  실제 생성 TPS avg/p50/p95: "
        f"{_format_float(summary['decode_tokens_per_second']['avg'])} / "
        f"{_format_float(summary['decode_tokens_per_second']['p50'])} / "
        f"{_format_float(summary['decode_tokens_per_second']['p95'])}"
    )
    print(
        "  latency p50/p95/p99: "
        f"{_format_ms_as_seconds(summary['latency_ms']['p50'])} / "
        f"{_format_ms_as_seconds(summary['latency_ms']['p95'])} / "
        f"{_format_ms_as_seconds(summary['latency_ms']['p99'])}"
    )
    if args.stream:
        print(
            "  TTFT p50/p95: "
            f"{_format_ms_as_seconds(summary['ttft_ms']['p50'])} / "
            f"{_format_ms_as_seconds(summary['ttft_ms']['p95'])}"
        )
    print(f"  회로차단: {tripped}")
    print(
        "  사후 생존 확인: "
        f"{postcheck['ok']} "
        f"(/health={postcheck['health_status']}, /server-status={postcheck['server_status']})"
    )
    print(f"  통과: {pass_criteria['passed']}")
    if pass_criteria["failures"]:
        print(f"  실패 사유: {pass_criteria['failures']}")
    for warning in pass_criteria["warnings"]:
        print(f"  ⚠️ 경고: {warning}")
    print(f"  리포트: {report_path}")

    if dashboard_server:
        _wait_for_dashboard_shutdown(dashboard_server, dashboard_url)

    if not pass_criteria["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
