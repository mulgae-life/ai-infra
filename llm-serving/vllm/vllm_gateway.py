#!/usr/bin/env python3
"""vLLM Gateway — 로드밸런싱 + 헬스체크 + 웜업 리버스 프록시.

다수의 vLLM 인스턴스 앞단에서 Least-Connection 로드밸런싱,
주기적 헬스체크, 기동/재기동 시 자동 웜업을 제공한다.

구조 (격리 페어 + 자동 디스커버리):
    클라이언트 → Gateway(:5015) → vLLM(:7080)            [연구계 페어]
    클라이언트 → Gateway(:5501) → vLLM(:7070)            [운영계 페어]
    (LB 시) Gateway(:5015) → vLLM(:7080, :7081, ...)     [동일 게이트웨이 소속]

자동 디스커버리:
    gateways/<port>.yaml 의 discover_from 디렉토리(예: ../instances)를 스캔하여
    각 인스턴스 yaml의 gateway_port == 자기 게이트웨이 포트인 것만
    backends로 등록한다. 인스턴스를 추가하려면 instances/*.yaml에 한 파일을
    추가하고 게이트웨이만 재기동하면 된다.

사용법:
    python vllm_gateway.py -c gateways/5015.yaml
    python vllm_gateway.py -c gateways/5501.yaml

    # 백그라운드 실행
    mkdir -p logs && nohup python vllm_gateway.py -c gateways/5015.yaml \
        > logs/gateway_5015.log 2>&1 &
"""

from __future__ import annotations

import argparse
import asyncio
import glob
import json
import logging
import logging.handlers
import os
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator

import httpx
import uvicorn
import websockets
import yaml
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from websockets.exceptions import ConnectionClosed as WSConnectionClosed

# ═══════════════════════════════════════════════════════
# 로깅
# ═══════════════════════════════════════════════════════

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("vllm-gateway")

# 파일 로깅: 삭제해도 자동 재생성
_file_handler = logging.handlers.WatchedFileHandler(
    os.path.join(LOG_DIR, "gateway.log"), encoding="utf-8",
)
_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logging.getLogger().addHandler(_file_handler)


# ═══════════════════════════════════════════════════════
# Pydantic 설정 모델
# ═══════════════════════════════════════════════════════


class BackendConfig(BaseModel):
    """해석된 백엔드 설정. load_config에서 포트가 자동 할당된다."""

    host: str = "127.0.0.1"
    port: int

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class GatewayServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 5015
    log_level: str = "info"


class HealthCheckConfig(BaseModel):
    interval_seconds: int = 10
    timeout_seconds: int = 3
    unhealthy_threshold: int = 3
    healthy_threshold: int = 1


class BootPollConfig(BaseModel):
    interval_seconds: int = 5
    timeout_seconds: int = 300


class InferenceWarmupConfig(BaseModel):
    prompt: str = "안녕하세요"
    max_tokens: int = 5
    timeout_seconds: int = 60


class WarmupConfig(BaseModel):
    enabled: bool = True
    boot_poll: BootPollConfig = BootPollConfig()
    inference: InferenceWarmupConfig = InferenceWarmupConfig()


class PrefixCacheWarmupConfig(BaseModel):
    enabled: bool = True
    max_tokens: int = 1
    timeout_seconds: int = 60
    system_prompt: str = ""


class HttpClientConfig(BaseModel):
    timeout_seconds: int = 300
    connect_timeout_seconds: int = 5
    max_connections: int = 100


class OverloadConfig(BaseModel):
    enabled: bool = True
    max_inflight_requests: int = 2
    max_queue_size: int = 4
    queue_timeout_seconds: float = 3.0
    retry_after_seconds: int = 5


class CompatConfig(BaseModel):
    """모델 교체 호환 계층.

    백엔드 모델을 Gemma ↔ Qwen ↔ GLM으로 갈아끼워도 클라이언트가 코드를 고치지
    않게 만든다. 클라이언트가 보는 모델명은 인스턴스 yaml의 served_model_name
    으로 고정하고, 모델마다 다른 요청 파라미터는 여기서 흡수한다.
    """

    translate_reasoning_effort: bool = True  # effort 값을 백엔드가 아는 값으로 번역
    mask_model_path: bool = True             # /v1/models의 root를 id 별칭과 같은 값으로 통일
    inject_identity_prompt: bool = True      # 기반 모델을 밝히지 않게 하는 시스템 프롬프트 주입
    # 모델 계열별 effort 매핑. 키는 /v1/models의 root(체크포인트 경로)에 대한
    # 부분 문자열(대소문자 무시), 값은 {클라이언트 값: 백엔드 값}.
    # 비워두면 _DEFAULT_EFFORT_PROFILES를 쓴다.
    effort_profiles: dict[str, dict[str, str]] = {}
    # 주입할 정체성 문구. 비워두면 _DEFAULT_IDENTITY_PROMPT를 쓴다.
    identity_prompt: str = ""


class GatewayConfig(BaseModel):
    gateway: GatewayServerConfig = GatewayServerConfig()
    discover_from: str = ""                # 인스턴스 yaml 디렉토리 (gateway_port 매칭)
    backend_api_key: str = ""              # vLLM --api-key 설정 시 내부 요청에 사용
    backends: list[BackendConfig] = []     # load_config에서 자동 생성
    health_check: HealthCheckConfig = HealthCheckConfig()
    warmup: WarmupConfig = WarmupConfig()
    prefix_cache_warmup: PrefixCacheWarmupConfig = PrefixCacheWarmupConfig()
    http_client: HttpClientConfig = HttpClientConfig()
    overload: OverloadConfig = OverloadConfig()
    compat: CompatConfig = CompatConfig()


def _resolve_actual_port(instance_dir: str, yaml_path: str, yaml_port: int) -> tuple[int, str]:
    """인스턴스의 실제 listen 포트를 결정한다.

    동작:
      - instance_dir/.runtime/<name>.json 이 존재하면 거기 기록된 port 사용 (launcher가 자동 회피한 실제 포트).
      - 없으면 yaml의 port를 fallback으로 사용 (vLLM이 아직 안 떴거나 port 자동 회피 미사용 구버전).

    반환: (actual_port, source) — source는 "runtime" 또는 "yaml"
    """
    name = os.path.splitext(os.path.basename(yaml_path))[0]
    runtime_path = os.path.join(instance_dir, ".runtime", f"{name}.json")
    if os.path.isfile(runtime_path):
        try:
            with open(runtime_path, encoding="utf-8") as f:
                data = json.load(f)
            if "port" in data:
                return int(data["port"]), "runtime"
        except (OSError, json.JSONDecodeError, ValueError) as e:
            logger.warning("runtime 파일 파싱 실패, yaml port 사용: %s (%s)", runtime_path, e)
    return int(yaml_port), "yaml"


def _discover_backends(config_path: str, raw: dict) -> list[dict]:
    """discover_from 디렉토리를 스캔해 gateway_port가 일치하는 인스턴스를 backends로 변환.

    동작:
      1. discover_from(상대 경로 → 절대 경로)의 *.yaml을 모두 읽는다.
      2. 각 yaml의 gateway_port가 자기 게이트웨이 포트와 일치하는 것만 채택.
      3. 실제 vLLM port는 instances/.runtime/<name>.json 우선 (launcher 자동 회피 결과),
         없으면 yaml의 port hint로 fallback.
      4. {host, port}로 변환하여 backends 리스트로 반환.
      5. 같은 게이트웨이로 묶인 인스턴스 간 실제 port 중복은 즉시 ValueError.

    그 외 yaml(gateway_port 미설정 / 다른 게이트웨이 소속)은 조용히 스킵.
    """
    gateway_port = raw.get("gateway", {}).get("port")
    if gateway_port is None:
        raise ValueError("discover_from 사용 시 gateway.port 명시 필수")

    config_dir = os.path.dirname(os.path.abspath(config_path))
    instance_dir = os.path.normpath(os.path.join(config_dir, raw["discover_from"]))
    if not os.path.isdir(instance_dir):
        raise FileNotFoundError(f"discover_from 디렉토리 없음: {instance_dir}")

    matched: list[tuple[str, dict]] = []
    for yaml_path in sorted(glob.glob(os.path.join(instance_dir, "*.yaml"))):
        try:
            with open(yaml_path, encoding="utf-8") as f:
                inst = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            logger.warning("yaml 파싱 실패, 스킵: %s (%s)", yaml_path, e)
            continue

        if inst.get("gateway_port") != gateway_port:
            continue
        if "port" not in inst:
            logger.warning("port 키 없음, 스킵: %s", yaml_path)
            continue
        matched.append((yaml_path, inst))

    # 실제 port 해석 (runtime 파일 우선, yaml fallback) + 중복 검증
    seen_ports: dict[int, str] = {}
    backends: list[dict] = []
    sources: list[str] = []
    for yaml_path, inst in matched:
        actual_port, source = _resolve_actual_port(instance_dir, yaml_path, inst["port"])
        if actual_port in seen_ports:
            raise ValueError(
                f"같은 gateway_port({gateway_port})로 묶인 인스턴스끼리 "
                f"실제 vLLM port {actual_port}가 중복됩니다: "
                f"{seen_ports[actual_port]} vs {yaml_path}"
            )
        seen_ports[actual_port] = yaml_path
        backends.append({"host": inst.get("host_for_gateway", "127.0.0.1"), "port": actual_port})
        sources.append(f"{os.path.basename(yaml_path)}→{actual_port}({source})")

    logger.info(
        "discover_from %s → gateway_port=%d 매칭 %d개: %s",
        instance_dir, gateway_port, len(backends), sources,
    )
    return backends


def load_config(path: str) -> GatewayConfig:
    """게이트웨이 YAML을 읽어 GatewayConfig로 파싱한다.

    백엔드 결정 우선순위:
      1) yaml에 backends 리스트 명시 → 그대로 사용 (수동 오버라이드 / 이질 라우팅)
      2) discover_from 명시 → 해당 디렉토리에서 gateway_port 매칭 자동 등록
    둘 다 없으면 ValueError로 fail-fast.
    """
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    # 1) yaml에 backends 명시 → 그대로 사용
    if raw.get("backends"):
        logger.info(
            "backends 명시됨: %s",
            [f"{b.get('host', '127.0.0.1')}:{b['port']}" for b in raw["backends"]],
        )
        return GatewayConfig(**raw)

    # 2) discover_from 명시 → 디렉토리 스캔
    if raw.get("discover_from"):
        raw["backends"] = _discover_backends(path, raw)
        return GatewayConfig(**raw)

    raise ValueError(
        f"{path}: backends 또는 discover_from 중 하나는 명시해야 합니다. "
        "예: discover_from: '../instances'"
    )


# ═══════════════════════════════════════════════════════
# BackendServer — 백엔드 상태 추적
# ═══════════════════════════════════════════════════════


@dataclass
class BackendServer:
    """vLLM 백엔드 인스턴스 1대의 상태."""

    config: BackendConfig
    active_connections: int = 0
    is_healthy: bool = False
    is_ready: bool = False  # 웜업까지 완료된 상태
    is_warming_up: bool = False  # 웜업 진행 중 (중복 방지)
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_health_check: float = 0.0
    # /v1/models의 root(실제 체크포인트 경로). served_model_name으로 별칭을 씌워도
    # root에는 실경로가 남으므로(vLLM api_server.py의 BaseModelPath) 모델 계열 판정에 쓴다.
    # 웜업 시 채워지고, 비어 있으면 reasoning_effort를 제거하는 쪽으로 동작한다.
    model_root: str = ""

    @property
    def base_url(self) -> str:
        return self.config.base_url

    @property
    def label(self) -> str:
        return f"{self.config.host}:{self.config.port}"


# ═══════════════════════════════════════════════════════
# LoadBalancer — Least-Connection
# ═══════════════════════════════════════════════════════


class LoadBalancer:
    """Least-Connection 방식 로드밸런서.

    asyncio.Lock으로 스레드 안전성을 보장한다.
    is_ready=True인 서버만 라우팅 대상에 포함한다.
    """

    def __init__(self, servers: list[BackendServer]) -> None:
        self._servers = servers
        self._lock = asyncio.Lock()

    async def acquire(self) -> BackendServer:
        """활성 연결이 가장 적은 ready 서버를 선택한다.

        ready 서버가 없으면 503 에러를 위해 RuntimeError를 발생시킨다.
        """
        async with self._lock:
            ready = [s for s in self._servers if s.is_ready]
            if not ready:
                raise RuntimeError("사용 가능한 백엔드 서버가 없습니다")
            server = min(ready, key=lambda s: s.active_connections)
            server.active_connections += 1
            return server

    async def release(self, server: BackendServer) -> None:
        """요청 완료 후 연결 카운트를 감소시킨다."""
        async with self._lock:
            server.active_connections = max(0, server.active_connections - 1)

    @property
    def servers(self) -> list[BackendServer]:
        return self._servers

    @property
    def ready_count(self) -> int:
        return sum(1 for s in self._servers if s.is_ready)


# ═══════════════════════════════════════════════════════
# AdmissionController — 게이트웨이 과부하 차단
# ═══════════════════════════════════════════════════════


class AdmissionRejected(Exception):
    def __init__(self, reason: str, retry_after_seconds: int) -> None:
        self.reason = reason
        self.retry_after_seconds = retry_after_seconds
        super().__init__(reason)


class AdmissionController:
    """vLLM으로 넘길 동시 요청과 대기열 길이를 게이트웨이에서 제한한다."""

    def __init__(self, config: OverloadConfig) -> None:
        self._enabled = config.enabled
        self._max_inflight = max(1, config.max_inflight_requests)
        self._max_queue = max(0, config.max_queue_size)
        self._queue_timeout = max(0.0, config.queue_timeout_seconds)
        self._retry_after = max(1, config.retry_after_seconds)
        self._condition = asyncio.Condition()
        self._inflight = 0
        self._queued = 0
        self._accepted_total = 0
        self._rejected_total = 0
        self._queue_timeout_total = 0

    async def acquire(self) -> None:
        """슬롯을 확보한다. 대기열이 꽉 차거나 대기 시간이 초과되면 429 대상."""
        if not self._enabled:
            return

        async with self._condition:
            if self._inflight < self._max_inflight:
                self._inflight += 1
                self._accepted_total += 1
                return

            if self._queued >= self._max_queue:
                self._rejected_total += 1
                raise AdmissionRejected("queue_full", self._retry_after)

            self._queued += 1
            try:
                deadline = time.monotonic() + self._queue_timeout
                while self._inflight >= self._max_inflight:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        self._rejected_total += 1
                        self._queue_timeout_total += 1
                        raise AdmissionRejected("queue_timeout", self._retry_after)
                    try:
                        await asyncio.wait_for(self._condition.wait(), timeout=remaining)
                    except asyncio.TimeoutError as e:
                        self._rejected_total += 1
                        self._queue_timeout_total += 1
                        raise AdmissionRejected("queue_timeout", self._retry_after) from e

                self._inflight += 1
                self._accepted_total += 1
            finally:
                self._queued = max(0, self._queued - 1)

    async def release(self) -> None:
        """요청 종료 시 슬롯을 반환한다."""
        if not self._enabled:
            return

        async with self._condition:
            self._inflight = max(0, self._inflight - 1)
            self._condition.notify(1)

    async def snapshot(self) -> dict:
        async with self._condition:
            return {
                "enabled": self._enabled,
                "max_inflight_requests": self._max_inflight,
                "max_queue_size": self._max_queue,
                "queue_timeout_seconds": self._queue_timeout,
                "retry_after_seconds": self._retry_after,
                "inflight_requests": self._inflight,
                "queued_requests": self._queued,
                "accepted_total": self._accepted_total,
                "rejected_total": self._rejected_total,
                "queue_timeout_total": self._queue_timeout_total,
            }


# ═══════════════════════════════════════════════════════
# WarmupManager — 서버 웜업 (CUDA + 프리픽스 캐시)
# ═══════════════════════════════════════════════════════


class WarmupManager:
    """서버 기동/재기동 시 웜업을 수행한다.

    2단계 웜업:
    1. 서버 웜업 — 더미 추론으로 CUDA 커널 예열
    2. 프리픽스 캐시 웜업 — 시스템 프롬프트 KV 캐시 사전 적재

    모델명은 백엔드의 GET /v1/models에서 자동 감지한다.
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        warmup_config: WarmupConfig,
        prefix_config: PrefixCacheWarmupConfig,
        api_key: str = "",
    ) -> None:
        self._client = client
        self._warmup = warmup_config
        self._prefix = prefix_config
        self._auth_headers: dict[str, str] = (
            {"Authorization": f"Bearer {api_key}"} if api_key else {}
        )

    async def warmup_all(self, servers: list[BackendServer]) -> None:
        """현재 떠있는 서버만 웜업한다. 나머지는 HealthChecker가 감지."""
        if not self._warmup.enabled:
            logger.info("웜업 비활성화 — health 프로브만 수행")
            for s in servers:
                try:
                    resp = await self._client.get(f"{s.base_url}/health", timeout=2.0)
                    if resp.status_code == 200:
                        s.is_healthy = True
                        s.is_ready = True
                        # 웜업을 껐어도 모델 정보는 받아둔다. model_root가 비면
                        # 호환 계층이 백엔드 계열을 판정하지 못해 reasoning_effort를
                        # 무조건 제거하게 된다.
                        await self._detect_model(s)
                except httpx.HTTPError:
                    pass
                except (ValueError, KeyError) as e:
                    logger.warning("[%s] 모델 정보 조회 실패: %s", s.label, e)
            return

        # 빠른 프로브: 현재 떠있는 서버 감지
        live: list[BackendServer] = []
        for s in servers:
            try:
                resp = await self._client.get(f"{s.base_url}/health", timeout=2.0)
                if resp.status_code == 200:
                    live.append(s)
            except httpx.HTTPError:
                pass

        if not live:
            # 아무도 안 떠있으면 첫 번째 서버만 boot_poll 대기
            logger.info(
                "기동된 백엔드 없음 — 첫 번째 서버 대기 (최대 %ds)",
                self._warmup.boot_poll.timeout_seconds,
            )
            await self._warmup_single(servers[0])
        else:
            logger.info("기동된 서버 %d/%d대 감지 — 웜업 시작", len(live), len(servers))
            tasks = [self._warmup_single(s) for s in live]
            await asyncio.gather(*tasks, return_exceptions=True)
        # 미기동 서버는 HealthChecker가 자동 감지 → rewarmup

    async def warmup_single(self, server: BackendServer) -> None:
        """단일 서버 웜업 (재기동 시 HealthChecker가 호출)."""
        await self._warmup_single(server)

    async def _warmup_single(self, server: BackendServer) -> None:
        """단일 서버 웜업 시퀀스."""
        label = server.label
        server.is_warming_up = True
        try:
            # 1. /health 대기
            await self._wait_for_health(server)

            # 2. 모델명 감지
            model_name = await self._detect_model(server)
            logger.info("[%s] 모델 감지: %s", label, model_name)

            # 3. CUDA 웜업 (더미 추론)
            await self._run_inference_warmup(server, model_name)

            # 4. 프리픽스 캐시 웜업
            await self._run_prefix_cache_warmup(server, model_name)

            server.is_healthy = True
            server.is_ready = True
            logger.info("[%s] 웜업 완료 — 라우팅 풀 등록", label)

        except Exception:
            server.is_ready = False
            logger.exception("[%s] 웜업 실패", label)
        finally:
            server.is_warming_up = False

    async def _wait_for_health(self, server: BackendServer) -> None:
        """서버가 /health에 200을 반환할 때까지 폴링한다."""
        label = server.label
        poll = self._warmup.boot_poll
        deadline = time.monotonic() + poll.timeout_seconds
        logger.info("[%s] 서버 기동 대기 (최대 %ds)...", label, poll.timeout_seconds)

        while time.monotonic() < deadline:
            try:
                resp = await self._client.get(
                    f"{server.base_url}/health",
                    timeout=3.0,
                )
                if resp.status_code == 200:
                    logger.info("[%s] 서버 기동 확인", label)
                    return
            except httpx.HTTPError:
                pass
            await asyncio.sleep(poll.interval_seconds)

        raise TimeoutError(f"[{label}] 서버 기동 대기 타임아웃 ({poll.timeout_seconds}s)")

    async def _detect_model(self, server: BackendServer) -> str:
        """GET /v1/models에서 모델명을 자동 감지한다.

        모델 계열 판정용 root(실제 체크포인트 경로)도 함께 기록한다. 별칭
        (served_model_name)을 씌우면 id로는 어떤 모델인지 알 수 없기 때문이다.
        """
        resp = await self._client.get(
            f"{server.base_url}/v1/models", timeout=10.0, headers=self._auth_headers,
        )
        resp.raise_for_status()
        data = resp.json()
        models = data.get("data", [])
        if not models:
            raise ValueError(f"[{server.label}] /v1/models 응답에 모델이 없습니다")
        server.model_root = models[0].get("root") or ""
        logger.info("[%s] 모델 경로: %s", server.label, server.model_root or "(미확인)")
        return models[0]["id"]

    async def _run_inference_warmup(self, server: BackendServer, model: str) -> None:
        """더미 추론으로 CUDA 커널을 예열한다."""
        label = server.label
        cfg = self._warmup.inference
        logger.info("[%s] CUDA 웜업 시작...", label)

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": cfg.prompt}],
            "max_tokens": cfg.max_tokens,
            "temperature": 0,
        }
        start = time.monotonic()
        resp = await self._client.post(
            f"{server.base_url}/v1/chat/completions",
            json=payload,
            headers=self._auth_headers,
            timeout=cfg.timeout_seconds,
        )
        resp.raise_for_status()
        elapsed = time.monotonic() - start
        logger.info("[%s] CUDA 웜업 완료 (%.1fs)", label, elapsed)

    async def _run_prefix_cache_warmup(self, server: BackendServer, model: str) -> None:
        """시스템 프롬프트의 KV 캐시를 사전 적재한다."""
        if not self._prefix.enabled or not self._prefix.system_prompt.strip():
            return

        label = server.label
        logger.info("[%s] 프리픽스 캐시 웜업 시작...", label)

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": self._prefix.system_prompt.strip()},
                {"role": "user", "content": "준비"},
            ],
            "max_tokens": self._prefix.max_tokens,
            "temperature": 0,
        }
        start = time.monotonic()
        resp = await self._client.post(
            f"{server.base_url}/v1/chat/completions",
            json=payload,
            headers=self._auth_headers,
            timeout=self._prefix.timeout_seconds,
        )
        resp.raise_for_status()
        elapsed = time.monotonic() - start
        logger.info("[%s] 프리픽스 캐시 웜업 완료 (%.1fs)", label, elapsed)


# ═══════════════════════════════════════════════════════
# HealthChecker — 주기적 헬스체크 + 재기동 감지
# ═══════════════════════════════════════════════════════


class HealthChecker:
    """백그라운드 주기적 헬스체크.

    연속 실패/성공 threshold 기반으로 상태를 전환한다.
    unhealthy → healthy 전환 시 웜업을 재실행한다.
    """

    def __init__(
        self,
        servers: list[BackendServer],
        client: httpx.AsyncClient,
        config: HealthCheckConfig,
        warmup_manager: WarmupManager,
    ) -> None:
        self._servers = servers
        self._client = client
        self._config = config
        self._warmup = warmup_manager
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """헬스체크 백그라운드 태스크를 시작한다."""
        self._task = asyncio.create_task(self._check_loop())
        logger.info("헬스체크 시작 (간격: %ds)", self._config.interval_seconds)

    async def stop(self) -> None:
        """헬스체크 태스크를 중지한다."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            logger.info("헬스체크 중지")

    async def _check_loop(self) -> None:
        """주기적으로 전체 서버를 헬스체크한다."""
        while True:
            await asyncio.sleep(self._config.interval_seconds)
            for server in self._servers:
                await self._check_single(server)

    async def _check_single(self, server: BackendServer) -> None:
        """개별 서버 헬스체크 및 상태 전환."""
        label = server.label
        ok = False
        try:
            resp = await self._client.get(
                f"{server.base_url}/health",
                timeout=self._config.timeout_seconds,
            )
            ok = resp.status_code == 200
        except httpx.HTTPError:
            ok = False

        server.last_health_check = time.monotonic()

        if ok:
            server.consecutive_failures = 0
            server.consecutive_successes += 1

            if not server.is_healthy and not server.is_warming_up and server.consecutive_successes >= self._config.healthy_threshold:
                # unhealthy → healthy 전환: 웜업 재실행
                logger.info("[%s] 서버 복구 감지 — 웜업 재실행", label)
                # 웜업을 비동기로 실행 (헬스체크 루프를 블로킹하지 않음)
                asyncio.create_task(self._rewarmup(server))
        else:
            server.consecutive_successes = 0
            server.consecutive_failures += 1

            if server.is_healthy and server.consecutive_failures >= self._config.unhealthy_threshold:
                server.is_healthy = False
                server.is_ready = False
                logger.warning("[%s] 서버 다운 감지 (연속 %d회 실패)", label, server.consecutive_failures)

    async def _rewarmup(self, server: BackendServer) -> None:
        """재기동된 서버를 웜업하고 라우팅 풀에 복귀시킨다."""
        try:
            await self._warmup.warmup_single(server)
        except Exception:
            logger.exception("[%s] 재웜업 실패", server.label)


# ═══════════════════════════════════════════════════════
# FastAPI 앱
# ═══════════════════════════════════════════════════════

# 전역 상태 (lifespan에서 초기화)
_lb: LoadBalancer
_client: httpx.AsyncClient
_health_checker: HealthChecker
_admission: AdmissionController
_start_time: float
_compat: CompatConfig


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """앱 수명주기: 기동 시 웜업/헬스체크, 종료 시 정리."""
    global _lb, _client, _health_checker, _admission, _start_time, _compat

    # ── 설정 로드 ──
    config_path = os.environ.get("VLLM_GATEWAY_CONFIG")
    if not config_path:
        raise RuntimeError(
            "VLLM_GATEWAY_CONFIG 환경변수가 설정되지 않았습니다. "
            "`python vllm_gateway.py -c gateways/<port>.yaml`로 실행하세요."
        )
    config = load_config(config_path)
    logger.info("설정 로드: %s", config_path)

    _compat = config.compat
    logger.info(
        "호환 계층: effort 번역 %s / 모델 경로 통일 %s / 정체성 프롬프트 %s",
        "on" if _compat.translate_reasoning_effort else "off",
        "on" if _compat.mask_model_path else "off",
        "on" if _compat.inject_identity_prompt else "off",
    )

    # ── httpx 클라이언트 (앱 수명주기로 관리) ──
    _client = httpx.AsyncClient(
        timeout=httpx.Timeout(
            config.http_client.timeout_seconds,
            connect=config.http_client.connect_timeout_seconds,
        ),
        limits=httpx.Limits(
            max_connections=config.http_client.max_connections,
            max_keepalive_connections=config.http_client.max_connections,
        ),
    )

    # ── 백엔드 서버 초기화 ──
    servers = [BackendServer(config=bc) for bc in config.backends]
    _lb = LoadBalancer(servers)
    logger.info("백엔드 %d개 등록: %s", len(servers), [s.label for s in servers])

    # ── 과부하 차단 ──
    _admission = AdmissionController(config.overload)
    logger.info("과부하 차단 설정: %s", await _admission.snapshot())

    # ── 웜업 (백그라운드) ──
    # backend ready를 lifespan startup에서 await하면 첫 backend가 뜰 때까지 uvicorn이
    # listen을 시작하지 못한다(yield에 도달 못 함). backend가 안 떠있는 상태에서도
    # 게이트웨이가 health 응답·운영 명령을 받을 수 있어야 하므로 백그라운드 태스크로 분리.
    # 첫 요청이 들어왔는데 ready 서버가 없으면 LoadBalancer.acquire가 503을 발생시킨다.
    warmup_mgr = WarmupManager(
        _client, config.warmup, config.prefix_cache_warmup, config.backend_api_key,
    )
    warmup_task = asyncio.create_task(warmup_mgr.warmup_all(servers))

    def _log_warmup_result(t: asyncio.Task) -> None:
        if t.cancelled():
            return
        exc = t.exception()
        if exc is not None:
            logger.error("웜업 백그라운드 태스크 실패", exc_info=exc)
        else:
            logger.info("웜업 백그라운드 태스크 완료 — %d/%d 서버 ready",
                        _lb.ready_count, len(servers))
    warmup_task.add_done_callback(_log_warmup_result)

    # ── 헬스체크 시작 ──
    _health_checker = HealthChecker(servers, _client, config.health_check, warmup_mgr)
    await _health_checker.start()

    _start_time = time.monotonic()
    logger.info("게이트웨이 시작 — :%d (웜업/헬스체크 백그라운드 진행)", config.gateway.port)

    yield

    # ── 종료 ──
    if not warmup_task.done():
        warmup_task.cancel()
        try:
            await warmup_task
        except (asyncio.CancelledError, Exception):
            pass
    await _health_checker.stop()
    await _client.aclose()
    logger.info("게이트웨이 종료")


app = FastAPI(title="vLLM Gateway", lifespan=lifespan)


# ═══════════════════════════════════════════════════════
# 모델 교체 호환 계층
# ═══════════════════════════════════════════════════════
#
# 클라이언트가 보는 모델명은 항상 하나(served_model_name)이고, 그 뒤에서
# Gemma/Qwen/GLM을 자유롭게 교체한다. 모델마다 다른 요청 파라미터는 여기서
# 흡수해 클라이언트가 400/422를 보지 않게 한다.
#
# reasoning_effort가 유일한 비호환 파라미터다. 미지원 모델은 값을 무시하지만
# (Gemma 템플릿은 이 변수를 참조하지 않는다), 지원 모델은 자기가 아는 값이
# 아니면 템플릿에서 예외를 던진다. 즉 위험한 쪽은 지원 모델이다.
#
# 파라미터와 별개로 모델의 자기소개도 흡수 대상이다. 정체성은 사후 학습으로
# 가중치에 박혀 있어 서빙 설정으로는 못 바꾼다 — "너 누구야"에 학습 때 이름을
# 답한다(2026-08-20 실측). 기반 모델을 감추려면 시스템 프롬프트로 지시해야 한다.

# vLLM이 최상위 reasoning_effort로 허용하는 값(chat_completion/protocol.py의 Literal).
# 이 밖의 문자열은 백엔드에서 422가 되므로 게이트웨이가 먼저 걷어낸다.
_OPENAI_EFFORT_VALUES = frozenset(
    {"none", "minimal", "low", "medium", "high", "xhigh", "max"}
)

# 모델 계열별 번역표. 키는 /v1/models의 root(체크포인트 경로)에 대한 부분 문자열,
# 값은 {클라이언트가 보낸 값: 백엔드에 넣을 값}.
# Qwen3.8 채팅 템플릿은 xhigh/medium/low만 받고 그 외에는 raise_exception →
# HTTP 400 "Unexpected reasoning effort ..."를 낸다(2026-08-20 실측).
# 여기에 없는 계열은 effort를 지원하지 않는 것으로 보고 필드를 제거한다.
_DEFAULT_EFFORT_PROFILES: dict[str, dict[str, str]] = {
    "qwen3.8": {
        "minimal": "low",
        "low": "low",
        "medium": "medium",
        "high": "xhigh",
        "xhigh": "xhigh",
        "max": "xhigh",
    },
}

# X-Effort-Applied 헤더에 실을 값. 실제 적용된 effort이거나 아래 둘 중 하나다.
_EFFORT_DROPPED = "dropped"        # 백엔드가 모르는 파라미터라 제거함
_EFFORT_THINKING_OFF = "none"      # effort=none → thinking 자체를 끔


def _select_effort_profile(
    model_root: str, profiles: dict[str, dict[str, str]]
) -> dict[str, str] | None:
    """백엔드 체크포인트 경로로 effort 번역표를 고른다. 미등록 계열은 None."""
    if not model_root:
        return None
    root = model_root.lower()
    for key, mapping in profiles.items():
        if key.lower() in root:
            return mapping
    return None


def _translate_effort(
    payload: dict, server: BackendServer, compat: CompatConfig
) -> tuple[dict | None, str | None]:
    """reasoning_effort를 백엔드가 아는 값으로 번역하고, effort가 오면 추론을 켠다.

    클라이언트는 OpenAI 표준값을 그대로 보내면 되고, 백엔드가 그 값을 모르면
    조용히 제거되어 200으로 응답한다. 값이 바뀐 사실은 X-Effort-Applied 헤더와
    로그에 남긴다 — 조용히 바꾸기만 하면 디버깅이 불가능해지기 때문이다.

    Returns:
        (백엔드로 보낼 payload, 헤더에 실을 값). payload가 None이면 변경 없음이라
        호출자가 원본 body를 그대로 흘려보내면 된다.
    """
    if not compat.translate_reasoning_effort:
        return None, None

    kwargs = payload.get("chat_template_kwargs")
    kwargs = kwargs if isinstance(kwargs, dict) else {}
    # 최상위 필드가 우선한다. vLLM은 최상위 값을 chat_template_kwargs에 병합하되
    # None이면 클라이언트가 직접 넣은 값을 남기므로(renderers/params.py의
    # merge_kwargs), 두 위치를 모두 봐야 누락이 없다.
    requested = payload.get("reasoning_effort") or kwargs.get("reasoning_effort")
    if not isinstance(requested, str) or not requested:
        return None, None

    profile = _select_effort_profile(server.model_root, compat.effort_profiles
                                     or _DEFAULT_EFFORT_PROFILES)
    resolved = profile.get(requested.lower()) if profile else None

    new_payload = dict(payload)
    new_kwargs = dict(kwargs)
    new_payload.pop("reasoning_effort", None)
    new_kwargs.pop("reasoning_effort", None)

    if requested.lower() == "none":
        # OpenAI에서 none은 "추론하지 말라"는 뜻이다. effort 값으로는 어느 모델도
        # 받지 않으므로 thinking 스위치 자체를 끄는 것으로 옮긴다.
        new_kwargs["enable_thinking"] = False
        applied = _EFFORT_THINKING_OFF
    elif resolved:
        # 최상위가 아니라 템플릿 인자로 넘긴다. 추론을 켤지는 아래에서 게이트웨이가
        # enable_thinking으로 명시하고, vLLM 0.31의 최상위 effort 자동 처리
        # (chat_completion/protocol.py)에 맡기지 않는다. 옛 nightly는 그 처리가 없어
        # 맡기면 버전마다 동작이 달라진다.
        new_kwargs["reasoning_effort"] = resolved
        applied = resolved
    else:
        # 백엔드가 effort를 모르거나(프로파일 없음), 알아도 받지 않는 값이거나,
        # vLLM 스펙 밖의 문자열이다. 셋 다 제거하면 정상 응답이 된다.
        applied = _EFFORT_DROPPED

    # effort를 주면 추론을 켠다(2026-10-10 대표님 결정. OpenAI와 vLLM 0.31의 규칙과 같다).
    # 클라이언트가 enable_thinking을 직접 보냈으면 그 값을 따른다. 강도를 지원하지 않는
    # 계열(Gemma)도 추론은 켠다. 스펙 밖 문자열은 추론 요청으로 보지 않는다.
    effort_key = requested.lower()
    if (effort_key != "none" and effort_key in _OPENAI_EFFORT_VALUES
            and "enable_thinking" not in kwargs):
        new_kwargs["enable_thinking"] = True

    if new_kwargs:
        new_payload["chat_template_kwargs"] = new_kwargs
    else:
        new_payload.pop("chat_template_kwargs", None)

    if applied != requested:
        known = "" if requested.lower() in _OPENAI_EFFORT_VALUES else " (스펙 밖 값)"
        logger.info(
            "[%s] reasoning_effort 번역: %s%s → %s", server.label, requested, known, applied,
        )
    return new_payload, applied


# 모든 요청의 맨 앞에 붙는 정체성 문구. 영어로 쓴 이유는 사용자 질문이 무슨
# 언어든 같은 지시가 걸려야 하기 때문이고, 그래서 답변 언어를 사용자 쪽에
# 맞추라는 문장을 따로 넣었다.
# 마지막 문장은 이 지시의 적용 범위를 정체성 질문으로 한정한다 — 없어도 되는지
# 재보진 않았으니, 문구를 손볼 때는 정체성 질문과 일반 질문을 함께 확인할 것.
# 2026-10-08 "Gemma 4 by Google"로 답하게 하던 문구를 기반 모델 비공개로 바꿨다.
# 백엔드가 Qwen이어도 Gemma라고 답해 사실과 어긋났고, 백엔드를 갈아끼울 때마다
# 문구가 거짓이 될 수 있었다. 어떤 계열이 붙어도 참인 문구라야 게이트웨이 yaml마다
# 따로 재정의하지 않아도 된다. 이름·페르소나는 각 서비스의 시스템 프롬프트가 정한다.
_DEFAULT_IDENTITY_PROMPT = (
    "If you are asked about your identity, model name, version, developer, or "
    "architecture, do not name any model, model family, lab, or company, and do "
    "not describe the serving stack behind this API. Say only that you are the "
    "AI assistant of this service and that the underlying model is not disclosed. "
    "Answer in the language the user writes in. "
    "Apart from this rule, follow the user's instructions as usual and do not "
    "bring up your identity on your own."
)

# 시스템 메시지로 인정되는 role. OpenAI가 system을 developer로 바꾸는 중이라
# 둘 다 받는다. Gemma 템플릿은 두 값을 같이 처리하지만 Qwen3.8 템플릿은
# developer를 모른다 — raise_exception('Unexpected message role.')으로 400이다
# (2026-08-20 실측). 병합할 때 role을 system으로 눕히면 두 계열 모두에서 통한다.
_SYSTEM_ROLES = frozenset({"system", "developer"})


def _inject_identity_prompt(payload: dict, compat: CompatConfig) -> dict | None:
    """정체성 시스템 프롬프트를 messages 맨 앞에 얹는다.

    새 system 메시지를 index 0에 끼워 넣는 방식은 쓸 수 없다. Qwen3.8 템플릿은
    선두가 아닌 system 메시지를 만나면 raise_exception('System message must be
    at the beginning.')으로 400을 내고, Gemma 템플릿은 messages[0]만 시스템 턴
    으로 취급해 나머지를 일반 턴으로 흘린다. 그래서 클라이언트 system 메시지가
    있으면 그 안으로 병합하고, role은 system으로 눕힌다(developer는 Qwen3.8이
    모르는 role이라 그대로 넘기면 400이다).

    정체성 문구가 앞, 클라이언트 지시가 뒤다. 뒤에 오는 지시가 우선하므로
    클라이언트가 자기 봇 이름을 붙이는 것은 그대로 살아난다 — 막으려는 것은
    기반 모델의 노출이지 클라이언트의 페르소나 설정이 아니다.

    Returns:
        수정된 payload. 변경할 게 없으면 None (호출자가 원본 body를 그대로 흘린다).
    """
    if not compat.inject_identity_prompt:
        return None

    prompt = compat.identity_prompt or _DEFAULT_IDENTITY_PROMPT
    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        # messages가 없거나 비었으면 백엔드가 400을 낼 요청이다. 여기서 손대면
        # 에러 메시지만 엉뚱해지므로 그대로 넘긴다.
        return None

    head = messages[0]
    if isinstance(head, dict) and head.get("role") in _SYSTEM_ROLES:
        # role을 system으로 통일한다. developer를 그대로 넘기면 Qwen3.8이 400을
        # 내 클라이언트 지시와 정체성 문구가 함께 죽는다.
        merged = dict(head, role="system")
        content = head.get("content")
        if isinstance(content, str):
            merged["content"] = f"{prompt}\n\n{content}" if content.strip() else prompt
        elif isinstance(content, list):
            # 멀티모달 파트 배열. 텍스트 파트 하나를 맨 앞에 끼운다.
            merged["content"] = [{"type": "text", "text": prompt}, *content]
        else:
            merged["content"] = prompt
        new_messages = [merged, *messages[1:]]
    else:
        new_messages = [{"role": "system", "content": prompt}, *messages]

    return {**payload, "messages": new_messages}


def _mask_model_list(data: dict) -> dict:
    """모델 목록의 root를 id 별칭과 같은 값으로 통일한다.

    served_model_name으로 id에 별칭을 씌워도 root에는 체크포인트 경로가 남아
    식별자가 둘이 된다. 클라이언트가 보는 모델 식별자는 하나여야 하므로 root를
    id와 같은 값으로 덮는다. max_model_len은 클라이언트가 컨텍스트 한도를
    확인하는 용도라 남긴다.
    """
    models = data.get("data")
    if not isinstance(models, list):
        return data
    masked = []
    for card in models:
        if not isinstance(card, dict):
            masked.append(card)
            continue
        card = dict(card)
        alias = card.get("id")
        if alias and card.get("root"):
            card["root"] = alias
        if card.get("parent"):
            card["parent"] = alias
        masked.append(card)
    return {**data, "data": masked}


# ── GET /health ──────────────────────────────────────


@app.get("/health")
async def health() -> JSONResponse:
    """게이트웨이 헬스체크. ready 서버 1개 이상이면 200, 아니면 503."""
    ready = _lb.ready_count
    total = len(_lb.servers)
    status = 200 if ready > 0 else 503
    return JSONResponse(
        content={"status": "ok" if ready > 0 else "unavailable", "ready": ready, "total": total},
        status_code=status,
    )


# ── GET /v1/models ───────────────────────────────────


@app.get("/v1/models")
async def list_models(request: Request) -> JSONResponse:
    """임의의 ready 서버에서 모델 목록을 가져온다."""
    try:
        server = await _lb.acquire()
    except RuntimeError:
        return JSONResponse(content={"error": "사용 가능한 백엔드 없음"}, status_code=503)

    try:
        headers: dict[str, str] = {}
        auth = request.headers.get("authorization")
        if auth:
            headers["Authorization"] = auth
        resp = await _client.get(f"{server.base_url}/v1/models", timeout=10.0, headers=headers)
        data = resp.json()
        if _compat.mask_model_path and resp.status_code == 200:
            data = _mask_model_list(data)
        return JSONResponse(content=data, status_code=resp.status_code)
    except httpx.HTTPError as e:
        logger.error("[%s] /v1/models 프록시 실패: %s", server.label, e)
        return JSONResponse(content={"error": "백엔드 연결 실패"}, status_code=502)
    finally:
        await _lb.release(server)


# ── POST /v1/chat/completions ────────────────────────


@app.post("/v1/chat/completions", response_model=None)
async def chat_completions(request: Request) -> JSONResponse | StreamingResponse:
    """OpenAI chat/completions 프록시 (스트리밍/논스트리밍)."""
    body = await request.body()

    # stream 여부 판단
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "잘못된 JSON"}, status_code=400)

    is_stream = payload.get("stream", False)

    try:
        await _admission.acquire()
    except AdmissionRejected as e:
        logger.warning("요청 거절: %s", e.reason)
        return JSONResponse(
            content={
                "error": {
                    "message": "서버가 바쁩니다. 잠시 후 다시 시도해주세요.",
                    "type": "rate_limit_error",
                    "code": e.reason,
                }
            },
            status_code=429,
            headers={"Retry-After": str(e.retry_after_seconds)},
        )

    # 서버 선택
    try:
        server = await _lb.acquire()
    except RuntimeError:
        await _admission.release()
        return JSONResponse(
            content={"error": {"message": "사용 가능한 백엔드 서버가 없습니다", "type": "server_error"}},
            status_code=503,
        )

    url = f"{server.base_url}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    # Authorization 헤더 패스스루 (백엔드 --api-key 설정 시 필요)
    auth = request.headers.get("authorization")
    if auth:
        headers["Authorization"] = auth

    # 모델 교체 호환: 정체성 프롬프트를 얹고, 백엔드가 모르는 reasoning_effort를
    # 번역하거나 제거한다. 둘 중 하나라도 손댔을 때만 재직렬화한다 — 이미지가
    # 실린 요청은 본문이 크다.
    injected = _inject_identity_prompt(payload, _compat)
    translated, effort_applied = _translate_effort(injected or payload, server, _compat)
    mutated = translated if translated is not None else injected
    if mutated is not None:
        body = json.dumps(mutated).encode()
    extra_headers = {"X-Effort-Applied": effort_applied} if effort_applied else {}

    if is_stream:
        return await _proxy_streaming(server, url, body, headers, extra_headers)
    else:
        return await _proxy_non_streaming(server, url, body, headers, extra_headers)


async def _proxy_non_streaming(
    server: BackendServer,
    url: str,
    body: bytes,
    headers: dict[str, str],
    extra_headers: dict[str, str] | None = None,
) -> JSONResponse:
    """논스트리밍 프록시."""
    try:
        resp = await _client.post(url, content=body, headers=headers)
        return JSONResponse(
            content=resp.json(), status_code=resp.status_code, headers=extra_headers or None,
        )
    except httpx.TimeoutException:
        logger.error("[%s] 타임아웃", server.label)
        return JSONResponse(content={"error": "백엔드 타임아웃"}, status_code=504)
    except httpx.HTTPError as e:
        logger.error("[%s] 연결 실패: %s", server.label, e)
        return JSONResponse(content={"error": "백엔드 연결 실패"}, status_code=502)
    finally:
        await _lb.release(server)
        await _admission.release()


async def _proxy_streaming(
    server: BackendServer,
    url: str,
    body: bytes,
    headers: dict[str, str],
    extra_headers: dict[str, str] | None = None,
) -> StreamingResponse | JSONResponse:
    """SSE 스트리밍 프록시. 상태 코드 확인 후 바이트 단위로 패스스루한다."""
    # 스트림 연결을 열고 상태 코드를 먼저 확인한다
    try:
        req = _client.build_request("POST", url, content=body, headers=headers)
        resp = await _client.send(req, stream=True)
    except httpx.TimeoutException:
        logger.error("[%s] 스트리밍 연결 타임아웃", server.label)
        await _lb.release(server)
        await _admission.release()
        return JSONResponse(
            content={"error": "백엔드 타임아웃"}, status_code=504, headers=extra_headers or None,
        )
    except httpx.HTTPError as e:
        logger.error("[%s] 스트리밍 연결 실패: %s", server.label, e)
        await _lb.release(server)
        await _admission.release()
        return JSONResponse(
            content={"error": "백엔드 연결 실패"}, status_code=502, headers=extra_headers or None,
        )

    # 백엔드 에러 시 상태 코드를 정확히 전달.
    # 실패 응답에도 X-Effort-Applied를 실어야 한다 — 번역 결과를 확인하려는 상황은
    # 대개 요청이 실패했을 때다. 성공 경로에만 붙이면 정작 필요할 때 없다.
    if resp.status_code != 200:
        error_body = await resp.aread()
        await resp.aclose()
        await _lb.release(server)
        await _admission.release()
        try:
            return JSONResponse(
                content=json.loads(error_body), status_code=resp.status_code,
                headers=extra_headers or None,
            )
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JSONResponse(
                content={"error": "백엔드 에러"}, status_code=resp.status_code,
                headers=extra_headers or None,
            )

    # 200 — SSE 스트리밍 시작
    async def _stream() -> AsyncGenerator[bytes, None]:
        try:
            async for chunk in resp.aiter_bytes():
                yield chunk
        except httpx.TimeoutException:
            logger.error("[%s] 스트리밍 타임아웃", server.label)
        except httpx.HTTPError as e:
            logger.error("[%s] 스트리밍 실패: %s", server.label, e)
        finally:
            await resp.aclose()
            await _lb.release(server)
            await _admission.release()

    return StreamingResponse(
        _stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            **(extra_headers or {}),
        },
    )


# ── POST /v1/audio/transcriptions, /v1/audio/translations ─────────
#
# OpenAI Audio API 멀티파트 프록시.
#   - chat/completions와 같이 admission(과부하 차단) + LB(least-connection) 적용
#   - request body는 multipart/form-data (audio file + form fields)이라
#     JSON 파싱 없이 raw bytes + 클라이언트 Content-Type(=boundary 포함)을 그대로 전달
#   - 응답은 JSON ({"text": "...", "usage": {...}}) — 스트리밍 아님 (현재 vLLM 0.19 기준)
#   - 장시간 오디오를 고려한 별도 timeout 600s (chat default보다 길게)
#
# 한 함수에서 두 path를 서비스하기 위해 request.url.path를 그대로 백엔드에 전달.
# 향후 새로운 audio 엔드포인트(예: /v1/audio/speech)가 생기면 데코레이터에 추가.
_AUDIO_TIMEOUT_SECONDS = 600.0


@app.post("/v1/audio/transcriptions", response_model=None)
@app.post("/v1/audio/translations", response_model=None)
async def audio_proxy(request: Request) -> JSONResponse:
    """OpenAI Audio API 멀티파트 프록시 (transcription/translation)."""
    body = await request.body()

    try:
        await _admission.acquire()
    except AdmissionRejected as e:
        logger.warning("audio 요청 거절: %s", e.reason)
        return JSONResponse(
            content={
                "error": {
                    "message": "서버가 바쁩니다. 잠시 후 다시 시도해주세요.",
                    "type": "rate_limit_error",
                    "code": e.reason,
                }
            },
            status_code=429,
            headers={"Retry-After": str(e.retry_after_seconds)},
        )

    try:
        server = await _lb.acquire()
    except RuntimeError:
        await _admission.release()
        return JSONResponse(
            content={"error": {"message": "사용 가능한 백엔드 서버가 없습니다", "type": "server_error"}},
            status_code=503,
        )

    # 클라이언트의 path/Content-Type/Authorization을 그대로 백엔드로 전달
    url = f"{server.base_url}{request.url.path}"
    headers: dict[str, str] = {}
    ct = request.headers.get("content-type")
    if ct:
        headers["Content-Type"] = ct  # multipart boundary 보존 필수
    auth = request.headers.get("authorization")
    if auth:
        headers["Authorization"] = auth

    try:
        resp = await _client.post(url, content=body, headers=headers, timeout=_AUDIO_TIMEOUT_SECONDS)
        # 응답이 JSON이 아닐 가능성(에러)도 안전하게 처리
        try:
            content = resp.json()
        except (json.JSONDecodeError, UnicodeDecodeError):
            content = {"error": {"message": resp.text[:500], "type": "backend_error"}}
        return JSONResponse(content=content, status_code=resp.status_code)
    except httpx.TimeoutException:
        logger.error("[%s] audio 타임아웃 (%.0fs 초과)", server.label, _AUDIO_TIMEOUT_SECONDS)
        return JSONResponse(content={"error": {"message": "백엔드 타임아웃", "type": "timeout"}}, status_code=504)
    except httpx.HTTPError as e:
        logger.error("[%s] audio 연결 실패: %s", server.label, e)
        return JSONResponse(content={"error": {"message": "백엔드 연결 실패", "type": "bad_gateway"}}, status_code=502)
    finally:
        await _lb.release(server)
        await _admission.release()


# ── WebSocket /v1/realtime ───────────────────────────
#
# OpenAI Realtime API 양방향 WebSocket 프록시.
#   - 클라이언트 ↔ 게이트웨이 ↔ 백엔드 vLLM 의 양방향 frame relay
#   - admission/LB은 연결 시점에 1회 acquire하고 연결 종료 시 release
#     (단일 세션이 길게 점유 — STT realtime의 자연스러운 워크로드)
#   - WebSocket close code 매핑:
#       4429 — admission rejected (과부하)
#       4503 — no backend ready
#       4500 — proxy 내부 오류 (백엔드 연결 실패 등)
#   - timeout 미적용: 클라이언트 또는 백엔드가 능동 종료할 때까지 양방향 relay
#
# Query string(예: ?model=Voxtral-Mini-...)은 그대로 백엔드에 전달.


async def _ws_close_silently(ws: WebSocket | "websockets.WebSocketClientProtocol", **kwargs) -> None:
    """이미 닫힌 소켓에 close()를 호출해도 예외를 무시한다."""
    try:
        await ws.close(**kwargs)
    except Exception:
        pass


@app.websocket("/v1/realtime")
async def realtime_proxy(client_ws: WebSocket) -> None:
    """OpenAI Realtime WebSocket 프록시 (양방향 frame relay)."""
    await client_ws.accept()

    try:
        await _admission.acquire()
    except AdmissionRejected as e:
        logger.warning("realtime 요청 거절: %s", e.reason)
        await _ws_close_silently(client_ws, code=4429, reason=e.reason[:120])
        return

    try:
        server = await _lb.acquire()
    except RuntimeError:
        await _admission.release()
        await _ws_close_silently(client_ws, code=4503, reason="no backend ready")
        return

    # 백엔드 WS URL (Query string 패스스루)
    qs = client_ws.url.query
    backend_url = f"ws://{server.config.host}:{server.config.port}/v1/realtime"
    if qs:
        backend_url += f"?{qs}"

    logger.info("[%s] realtime 프록시 시작 → %s", server.label, backend_url)
    try:
        # max_size=None: 오디오 chunk가 큰 경우(수 MB) 대비
        async with websockets.connect(backend_url, max_size=None, open_timeout=10) as backend_ws:
            async def client_to_backend() -> None:
                try:
                    while True:
                        msg = await client_ws.receive()
                        if msg.get("type") == "websocket.disconnect":
                            return
                        if msg.get("text") is not None:
                            await backend_ws.send(msg["text"])
                        elif msg.get("bytes") is not None:
                            await backend_ws.send(msg["bytes"])
                except (WebSocketDisconnect, WSConnectionClosed):
                    return

            async def backend_to_client() -> None:
                try:
                    async for msg in backend_ws:
                        if isinstance(msg, (bytes, bytearray, memoryview)):
                            await client_ws.send_bytes(bytes(msg))
                        else:
                            await client_ws.send_text(msg)
                except WSConnectionClosed:
                    return

            # 한 쪽이 종료되면 양쪽 모두 닫는다 (짝방향 stale 방지).
            tasks = [
                asyncio.create_task(client_to_backend()),
                asyncio.create_task(backend_to_client()),
            ]
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            await _ws_close_silently(backend_ws)
            await _ws_close_silently(client_ws)

    except (websockets.exceptions.InvalidURI, OSError, asyncio.TimeoutError) as e:
        logger.error("[%s] realtime 백엔드 연결 실패: %s", server.label, e)
        await _ws_close_silently(client_ws, code=4500, reason=f"backend connect failed: {type(e).__name__}")
    except Exception as e:
        logger.exception("[%s] realtime 프록시 오류: %s", server.label, e)
        await _ws_close_silently(client_ws, code=4500, reason=f"proxy error: {type(e).__name__}")
    finally:
        await _lb.release(server)
        await _admission.release()
        logger.info("[%s] realtime 프록시 종료", server.label)


# ── GET /server-status ───────────────────────────────


@app.get("/server-status")
async def server_status() -> JSONResponse:
    """백엔드 서버 상태 대시보드."""
    uptime = time.monotonic() - _start_time
    backends = []
    for s in _lb.servers:
        backends.append({
            "url": s.base_url,
            "is_healthy": s.is_healthy,
            "is_ready": s.is_ready,
            "active_connections": s.active_connections,
            "consecutive_failures": s.consecutive_failures,
        })
    return JSONResponse(content={
        "gateway": {"uptime_seconds": round(uptime, 1)},
        "backends": backends,
        "overload": await _admission.snapshot(),
        "ready_count": _lb.ready_count,
        "total_count": len(_lb.servers),
    })


# ═══════════════════════════════════════════════════════
# 진입점
# ═══════════════════════════════════════════════════════


def main() -> None:
    parser = argparse.ArgumentParser(description="vLLM Gateway")
    parser.add_argument(
        "-c", "--config",
        required=True,
        help="게이트웨이 설정 파일 경로 (예: gateways/5015.yaml)",
    )
    args = parser.parse_args()

    config_path = os.path.abspath(args.config)
    if not os.path.exists(config_path):
        logger.error("설정 파일 없음: %s", config_path)
        raise SystemExit(1)

    os.environ["VLLM_GATEWAY_CONFIG"] = config_path
    config = load_config(config_path)

    uvicorn.run(
        app,
        host=config.gateway.host,
        port=config.gateway.port,
        log_level=config.gateway.log_level,
    )


if __name__ == "__main__":
    main()
