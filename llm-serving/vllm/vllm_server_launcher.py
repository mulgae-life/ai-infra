#!/usr/bin/env python3
"""vLLM 서버 런처

vllm serve 위에 환경변수 관리 + 모델 자동 다운로드를 추가한 래퍼.
start.sh에서 호출되며, 직접 실행도 가능.

설정 모델:
    -c instances/<name>.yaml 형태로 인스턴스 단위 yaml을 받는다.
    yaml 안의 메타 키(gateway_port, gpus 등)는 _LAUNCHER_KEYS로 필터링되어
    vllm serve에는 전달되지 않는다.

사용법:
    # start.sh를 통한 실행 (권장)
    ./start.sh up all                   # 전체 인스턴스 + 게이트웨이 기동 (확인 없이)
    ./start.sh up                       # [y/N] 전체 적용 confirm 프롬프트
    ./start.sh up gemma                 # 단일 인스턴스 (instances/gemma.yaml)
    ./start.sh download gemma           # 모델 다운로드/최신 동기화 (--download-only wrapper)

    # 직접 실행
    python vllm_server_launcher.py -c instances/gemma.yaml
    python vllm_server_launcher.py -c instances/qwen.yaml

    # 모델 다운로드/최신 동기화만 (로컬이 있으면 변경 파일만 증분 다운로드)
    python vllm_server_launcher.py -c instances/qwen.yaml --download-only

    # Gated 모델
    HF_TOKEN=hf_xxx python vllm_server_launcher.py -c instances/<name>.yaml
"""
import argparse
import fcntl
import glob
import json
import logging
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("vllm-launcher")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# INSTANCES_DIR / RUNTIME_DIR / PORT_ALLOC_LOCK은 yaml 경로의 dirname 기준으로 main()에서
# 동적 결정한다 (런처는 vllm/instances/, stt/instances/ 등 여러 디렉토리를 서비스하므로).
# 여기서는 임시 fallback 값만 두고, main()이 yaml 경로에 맞춰 덮어쓴다.
INSTANCES_DIR = os.path.join(BASE_DIR, "instances")
RUNTIME_DIR = os.path.join(INSTANCES_DIR, ".runtime")
# port 할당 + runtime 기록을 동시 기동 launcher 간에 직렬화하기 위한 advisory lock 파일.
# 프로세스 종료 시 OS가 자동으로 lock 해제하므로 stale lock 위험 없음.
PORT_ALLOC_LOCK = os.path.join(RUNTIME_DIR, ".port_alloc.lock")

# vllm serve --config에 전달하지 않는 런처 전용 키 + 게이트웨이 매칭용 메타 키.
# gateway_port: gateways/<port>.yaml의 discover_from이 인스턴스 yaml에서 읽는 메타.
#   vllm serve는 이 키를 알지 못하므로 임시 config에서 제거해야 한다.
# port: 자동 회피 로직이 결정한 실제 포트를 --port CLI로 따로 넘기므로 yaml에서는 제거.
# env: dict 형태 환경변수. subprocess.Popen의 env에 머지하고 vllm serve에는 전달하지 않는다.
#   예) Voxtral 권장 VLLM_DISABLE_COMPILE_CACHE=1 처럼 모델별 env 의존성이 있을 때 사용.
# task: vLLM 0.20.x에서 --task CLI 인자가 제거되고 model config 기반 자동 감지로 통합됨.
#   STT yaml(whisper_v3 / qwen3_asr / voxtral)의 task 키는 PoC 비교 메타로만 보존하고
#   vllm serve에는 전달하지 않는다. 자동 감지가 부정확한 모델이 나오면 그때 vLLM 새 인자
#   (--runner 등)로 매핑하는 launcher 분기를 추가한다.
_LAUNCHER_KEYS = {"gpus", "download_dir", "gateway_port", "port", "env", "task",
                  "auto_restart_max", "watchdog_unhealthy_seconds"}

# 자동 재기동 backoff. 연속 실패마다 순서대로 적용하고 끝에 도달하면 마지막 값을 유지.
_RESTART_BACKOFFS = [10, 30, 60]
# 이 시간 이상 가동한 뒤 죽었으면 새로운 장애로 보고 연속 실패 카운터를 초기화한다
# (간헐적 장애가 누적 집계되어 재기동이 영구 차단되는 것을 막는다).
_RESTART_STABLE_SECONDS = 300

# health 무응답 감시. EngineCore가 죽어도 API 서버가 워커를 기다리며 수 분간 잔존해
# proc.wait()가 반환되지 않는 경우가 있어, 워치독 없이는 자동 재기동이 발동하지 못한다.
_WATCHDOG_INTERVAL_SECONDS = 10
_WATCHDOG_UNHEALTHY_SECONDS = 90


def parse_args():
    p = argparse.ArgumentParser(
        description="vLLM 서버 런처",
        epilog="위 옵션 외 모든 인자는 vllm serve에 그대로 전달됩니다.",
    )
    p.add_argument(
        "-c", "--config",
        required=True,
        help="인스턴스 설정 파일 경로 (예: instances/gemma.yaml)",
    )
    p.add_argument("-g", "--gpu", type=str, help="CUDA_VISIBLE_DEVICES (예: 0 또는 0,1)")
    p.add_argument("-m", "--model", type=str, help="HF 모델 ID (config override)")
    p.add_argument("--online", action="store_true", help="HF 온라인 모드 허용")
    p.add_argument("--download-only", action="store_true", help="모델 다운로드/최신 동기화만 수행 (서버 미기동)")
    args, extra = p.parse_known_args()
    return args, extra


def download_model(model_id: str, local_dir: str) -> None:
    """HuggingFace 모델을 snapshot_download API로 다운로드."""
    os.environ.pop("HF_HUB_OFFLINE", None)
    os.environ.pop("TRANSFORMERS_OFFLINE", None)
    token = os.environ.get("HF_TOKEN") or None

    logger.info("모델 다운로드 시작: %s → %s", model_id, local_dir)
    try:
        from huggingface_hub import snapshot_download

        snapshot_download(repo_id=model_id, local_dir=local_dir, token=token)
    except Exception as e:
        logger.error(
            "모델 다운로드 실패: %s\n"
            "Gated 모델이면 HF_TOKEN 환경변수를 설정하세요:\n"
            "  export HF_TOKEN=hf_xxx",
            e,
        )
        sys.exit(1)
    logger.info("모델 다운로드 완료: %s", local_dir)


def _resolve_model_path(
    model_id: str, download_dir: str, *, kind: str = "모델", sync: bool = False
) -> str:
    """HF ID를 download_dir 하위 로컬 절대경로로 해석한다 (없으면 자동 다운로드).

    - 빈 값/None: 그대로 반환
    - 절대경로: 디렉토리 존재 검증만 수행 (없으면 sys.exit)
    - HF ID + download_dir 있음: {download_dir}/{model_id} 경로 사용, 없으면 받음
    - HF ID + download_dir 없음: 변환 없이 그대로 반환 (vLLM이 HF Hub에서 해석)
    kind는 로그/에러 라벨 ("모델", "drafter" 등).

    sync=True(--download-only 경로)면 로컬 디렉토리가 있어도 snapshot_download를
    실행해 HF 최신 리비전과 증분 동기화한다 (변경 파일만 다운로드 — 가중치 무변경 시
    chat_template 등 소형 파일만 받음). 서빙 경로(up)는 sync=False로 기존 파일을
    그대로 쓰므로 네트워크를 보지 않는다 (폐쇄망 운영 보장).
    """
    if not model_id:
        return model_id
    if os.path.isabs(model_id):
        if not os.path.isdir(model_id):
            logger.error(
                "%s 경로가 존재하지 않습니다: %s\n"
                "config에서 HF 모델 ID 형식(예: google/gemma-4-31B-it)을 사용하세요.",
                kind, model_id,
            )
            sys.exit(1)
        return model_id
    if not download_dir:
        return model_id
    local_path = os.path.join(download_dir, model_id)
    if os.path.isdir(local_path):
        if sync:
            logger.info("로컬 %s 최신 동기화 (증분): %s", kind, local_path)
            download_model(model_id, local_path)
        else:
            logger.info("%s 경로 해석: %s → %s", kind, model_id, local_path)
    else:
        logger.info("로컬 %s 없음, 자동 다운로드: %s", kind, local_path)
        download_model(model_id, local_path)
    return local_path


def _write_vllm_config(config: dict) -> str:
    """런처 전용 키를 제거한 vllm serve용 임시 config 파일을 생성한다."""
    vllm_only = {k: v for k, v in config.items() if k not in _LAUNCHER_KEYS}
    fd, path = tempfile.mkstemp(suffix=".yaml", prefix=".vllm_serve_", dir=BASE_DIR)
    with os.fdopen(fd, "w") as f:
        yaml.dump(vllm_only, f, default_flow_style=False, allow_unicode=True)
    return path


def _cleanup_stale_configs(min_age_seconds: int = 60) -> None:
    """이전 실행에서 남은 임시 config 파일을 정리한다.

    SIGKILL/crash로 finally가 실행되지 않은 경우를 대비한 보험.
    min_age_seconds 이상 오래된 파일만 삭제하여 동시 기동 중인 다른 런처의
    임시 파일을 지우지 않도록 방어한다.
    """
    pattern = os.path.join(BASE_DIR, ".vllm_serve_*.yaml")
    now = time.time()
    for path in glob.glob(pattern):
        try:
            if now - os.path.getmtime(path) >= min_age_seconds:
                os.unlink(path)
        except OSError:
            pass


def _is_port_free(port: int, host: str = "0.0.0.0") -> bool:
    """포트가 비어있는지 socket binding test로 확인.

    SO_REUSEADDR을 켜고 잠깐 binding을 시도한다. 실제 binding은 vllm serve가
    수행하므로 검사와 vLLM 기동 사이에 다른 프로세스가 잡을 수 있는 race
    window가 있지만, 운영 환경(단일 사용자)에서는 실용적으로 무시 가능.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((host, port))
    except OSError:
        return False
    finally:
        s.close()
    return True


def _find_free_port(start: int, max_tries: int = 100, exclude=None) -> int:
    """yaml의 port를 시작점으로 비어있는 첫 포트를 찾는다.

    동작:
        - start 포트가 비어있고 exclude에 없으면 그대로 사용 (의도된 포트 보존).
        - 사용 중이거나 exclude에 있으면 +1, +2 ... max_tries까지 회피 탐색.
        - 모두 사용 중이면 RuntimeError로 fail-fast.

    의도: 인스턴스 yaml을 복붙해 같은 port가 남아있는 경우에도 자동 회피하여
    같은 게이트웨이 아래 LB 인스턴스를 올릴 수 있게 한다. 게이트웨이는
    runtime 파일에서 실제 포트를 읽으므로 backends 등록은 자동.

    exclude는 동시 기동 race 방어용 — 다른 active launcher가 막 결정해 runtime에
    기록한 port가 socket에선 아직 free로 보이는 윈도우에서도 회피하도록.
    """
    exclude = exclude or set()
    for offset in range(max_tries):
        port = start + offset
        if port in exclude:
            continue
        if _is_port_free(port):
            if offset > 0:
                logger.info(
                    "port %d 사용 중 → +%d 회피하여 %d 사용", start, offset, port,
                )
            return port
    raise RuntimeError(
        f"비어있는 port를 찾지 못함: {start} ~ {start + max_tries - 1} 모두 사용 중",
    )


def _ports_taken_by_active_runtimes() -> set:
    """현재 살아있는 다른 launcher가 점유 중인 port를 runtime json에서 수집.

    동일 yaml port hint를 가진 launcher가 동시 기동될 때 socket bind 검사만으로는
    같은 port를 둘 다 free로 보는 race가 발생한다. runtime json은 launcher가
    port 결정 직후 기록하므로, lock 안에서 함께 검사하면 충돌 회피 가능.
    """
    taken: set = set()
    if not os.path.isdir(RUNTIME_DIR):
        return taken
    for path in glob.glob(os.path.join(RUNTIME_DIR, "*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        pid = data.get("pid")
        port = data.get("port")
        if port is None or pid is None:
            continue
        if not _is_pid_alive(int(pid)):
            continue
        try:
            taken.add(int(port))
        except (TypeError, ValueError):
            continue
    return taken


def _allocate_port_and_register(*, instance_name: str, yaml_port: int, model: str):
    """fcntl.flock으로 port 결정 + runtime 기록을 직렬화한다.

    동일 yaml port hint를 가진 launcher가 동시 기동될 때, socket bind 검사만으로는
    한쪽이 close()와 다른 쪽 bind() 사이에 같은 port를 free로 보는 race가 발생한다.
    이를 막기 위해 PORT_ALLOC_LOCK을 EX-lock으로 잡고, 그 안에서
    (1) 다른 active launcher의 점유 port 수집 (2) free port 결정 (3) runtime json 기록.

    프로세스가 죽으면 OS가 lock 자동 해제하므로 stale lock 위험 없음.
    반환: (actual_port, runtime_path)
    """
    os.makedirs(RUNTIME_DIR, exist_ok=True)
    with open(PORT_ALLOC_LOCK, "w") as lf:
        fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
        try:
            taken = _ports_taken_by_active_runtimes()
            actual_port = _find_free_port(yaml_port, exclude=taken)
            runtime_path = _write_runtime_file(
                name=instance_name,
                port=actual_port,
                yaml_port_hint=yaml_port,
                model=model,
            )
            return actual_port, runtime_path
        finally:
            fcntl.flock(lf.fileno(), fcntl.LOCK_UN)


def _instance_name_from_config(config_path: str) -> str:
    """yaml 파일 경로에서 인스턴스 이름 추출 (예: instances/gemma.yaml → 'gemma')."""
    return os.path.splitext(os.path.basename(config_path))[0]


def _runtime_path(name: str) -> str:
    """인스턴스 이름에 대응하는 runtime json 경로."""
    return os.path.join(RUNTIME_DIR, f"{name}.json")


def _write_runtime_file(name: str, port: int, yaml_port_hint: int, model: str) -> str:
    """launcher가 실제 사용 중인 port를 runtime 파일에 기록한다.

    형식:
        {"port": <actual>, "yaml_port_hint": <yaml에 적힌 시작 포트>,
         "pid": <launcher PID>, "model": <모델명>, "started_at": <epoch>}

    게이트웨이의 _discover_backends가 이 파일을 우선 참조하여 backends에
    실제 포트를 등록한다. 파일이 없으면 yaml의 port로 fallback.

    원자성: tmp 파일에 dump 후 os.replace로 atomic rename. 직접 open("w")으로
    쓰면 truncate된 0바이트 상태가 잠시 노출되어, start.sh가 파일 존재만 보고
    진행하거나 게이트웨이가 partial json을 읽고 yaml port hint로 잘못 fallback하는
    race가 발생한다 (launcher가 +1 자동 회피한 경우 영구 unhealthy로 굳음).
    """
    os.makedirs(RUNTIME_DIR, exist_ok=True)
    path = _runtime_path(name)
    data = {
        "port": port,
        "yaml_port_hint": yaml_port_hint,
        "pid": os.getpid(),
        "model": model,
        "started_at": time.time(),
    }
    # 동일 디렉토리에 tmp 작성 — os.replace가 동일 파일시스템 내에서만 atomic.
    fd, tmp_path = tempfile.mkstemp(suffix=".json.tmp", prefix=f"{name}.", dir=RUNTIME_DIR)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    logger.info("runtime 기록: %s (port=%d, pid=%d)", path, port, os.getpid())
    return path


def _remove_runtime_file(name: str) -> None:
    """launcher 종료 시 자기 runtime 파일을 정리한다."""
    path = _runtime_path(name)
    try:
        os.unlink(path)
        logger.info("runtime 정리: %s", path)
    except OSError:
        pass


def _is_pid_alive(pid: int) -> bool:
    """PID가 살아있는지 signal 0으로 검사 (실제 신호는 안 보냄)."""
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    return True


def _cleanup_stale_runtime_files() -> None:
    """이전 실행에서 SIGKILL/crash로 남은 runtime 파일을 정리한다.

    PID가 살아있지 않은 항목만 삭제하여 동시 실행 중인 다른 인스턴스의
    runtime 파일은 보존한다. atomic write 도중 SIGKILL되어 남은 .json.tmp
    잔재도 함께 정리.
    """
    if not os.path.isdir(RUNTIME_DIR):
        return
    for path in glob.glob(os.path.join(RUNTIME_DIR, "*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            pid = data.get("pid")
            if pid is None or not _is_pid_alive(pid):
                os.unlink(path)
                logger.info("stale runtime 정리: %s (pid=%s 죽음)", path, pid)
        except (OSError, json.JSONDecodeError):
            try:
                os.unlink(path)
            except OSError:
                pass
    # atomic write 실패 잔재 (.json.tmp) 정리 — 살아있는 launcher가 진행 중인
    # 일시적 tmp일 수도 있으므로 1분 이상 묵은 것만 삭제.
    now = time.time()
    for tmp_path in glob.glob(os.path.join(RUNTIME_DIR, "*.json.tmp")):
        try:
            if now - os.path.getmtime(tmp_path) >= 60:
                os.unlink(tmp_path)
                logger.info("stale runtime tmp 정리: %s", tmp_path)
        except OSError:
            pass


def _gpu_compute_pids(gpus_csv):
    """nvidia-smi로 지정 GPU를 점유 중인 프로세스 PID 목록을 얻는다.

    gpus_csv는 yaml의 gpus(물리 인덱스)로, nvidia-smi -i와 같은 체계라 그대로 넘긴다.
    """
    try:
        out = subprocess.run(
            ["nvidia-smi", "-i", gpus_csv,
             "--query-compute-apps=pid", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as e:
        logger.warning("nvidia-smi 조회 실패 (고아 워커 검사 생략): %s", e)
        return []
    if out.returncode != 0:
        logger.warning("nvidia-smi 조회 실패 rc=%s (고아 워커 검사 생략): %s",
                       out.returncode, out.stderr.strip())
        return []
    pids = []
    for line in out.stdout.splitlines():
        line = line.strip()
        if line.isdigit():
            pids.append(int(line))
    return pids


def _find_stale_workers(gpus_csv):
    """지정 GPU에서 회수해야 할 vLLM 워커 PID 목록.

    엔진이 죽어도 VLLM::Worker_TP*는 CUDA 컨텍스트를 쥔 채 남아 GPU 메모리를 반환하지 않고,
    그대로 재기동하면 메모리 부족으로 실패한다.

    판정은 프로세스 그룹으로 한다 (launcher / vllm serve / 워커가 PGID를 공유).
      · 내 그룹             → 내가 띄운 워커. 회수.
      · 남의 그룹·리더 사망 → 이전 실행이 남긴 고아. 회수.
      · 남의 그룹·리더 생존 → 다른 인스턴스의 정상 워커. 건드리지 않는다.

    주의: vllm serve가 살아있는 동안 호출하면 정상 워커를 죽인다. 기동 전이나 proc 종료를
    확인한 뒤에만 호출할 것.
    """
    stale = []
    my_pgid = os.getpgid(0)
    for pid in _gpu_compute_pids(gpus_csv):
        try:
            with open(f"/proc/{pid}/comm", encoding="utf-8") as f:
                comm = f.read().strip()
        except OSError:
            continue                       # 이미 사라졌거나 조회 권한 없음
        if not comm.startswith("VLLM::Worker"):
            continue                       # vLLM 워커가 아니면 대상 아님
        try:
            pgid = os.getpgid(pid)
        except OSError:
            continue
        if pgid == my_pgid:
            stale.append(pid)              # 내가 띄운 워커 → 회수 대상
            continue
        try:
            os.kill(pgid, 0)
        except ProcessLookupError:
            stale.append(pid)              # 그룹 리더 사망 → 이전 실행의 고아
        except OSError:
            continue                       # 권한 등으로 판정 불가 → 건드리지 않음
    return stale


def _cleanup_stale_workers(gpus_csv, context):
    """남은 워커를 SIGTERM → (무응답 시) SIGKILL로 정리한다.

    OOM 등으로 죽은 워커는 CUDA 커널 안에서 멈춰 SIGTERM에 반응하지 않는 경우가 많아
    SIGKILL 단계가 반드시 필요하다.
    """
    orphans = _find_stale_workers(gpus_csv)
    if not orphans:
        return
    logger.warning("[%s] 잔여 vLLM 워커 %d개 발견 (GPU %s): %s — 정리",
                   context, len(orphans), gpus_csv, orphans)
    for pid in orphans:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
    deadline = time.time() + 10
    while time.time() < deadline:
        if not any(_pid_alive(pid) for pid in orphans):
            logger.info("[%s] 잔여 워커 정리 완료 (SIGTERM)", context)
            return
        time.sleep(0.5)
    for pid in orphans:
        if _pid_alive(pid):
            logger.warning("[%s] PID %s SIGTERM 무응답 10s → SIGKILL", context, pid)
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
    deadline = time.time() + 10
    while time.time() < deadline:
        if not any(_pid_alive(pid) for pid in orphans):
            break
        time.sleep(0.5)
    remaining = [pid for pid in orphans if _pid_alive(pid)]
    if remaining:
        logger.error("[%s] 잔여 워커 정리 실패 — 수동 확인 필요: %s", context, remaining)
    else:
        logger.info("[%s] 잔여 워커 정리 완료", context)


def _pid_alive(pid):
    """PID 생존 확인. 좀비(exit 후 미회수)는 죽은 것으로 본다."""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as f:
            state = f.read().rsplit(")", 1)[1].split()[0]
        return state != "Z"
    except (OSError, IndexError):
        return False


def _health_ok(port, timeout=3):
    """vLLM /health가 200을 주는지 확인."""
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/health", timeout=timeout
        ) as resp:
            return resp.status == 200
    except Exception:
        return False


def _watchdog(proc, port, stop_event, unhealthy_seconds):
    """health 무응답이 이어지면 vllm serve를 강제 종료해 재기동 경로로 넘긴다.

    감시는 **한 번이라도 healthy가 된 뒤부터** 시작한다. 모델 로딩에 수 분이 걸리는데
    그 구간을 장애로 오판하면 기동 자체가 불가능해지기 때문이다.
    """
    became_healthy = False
    unhealthy_for = 0
    while not stop_event.wait(_WATCHDOG_INTERVAL_SECONDS):
        if proc.poll() is not None:
            return                          # 이미 종료됨 — 재기동 로직이 처리
        if _health_ok(port):
            if not became_healthy:
                logger.info("워치독: health 확인 — 이후 무응답 %d초면 강제 종료",
                            unhealthy_seconds)
            became_healthy = True
            unhealthy_for = 0
            continue
        if not became_healthy:
            continue                        # 기동(모델 로딩) 중 — 감시 대상 아님
        unhealthy_for += _WATCHDOG_INTERVAL_SECONDS
        logger.warning("워치독: health 무응답 %d초 / 한계 %d초",
                       unhealthy_for, unhealthy_seconds)
        if unhealthy_for >= unhealthy_seconds:
            logger.error("워치독: health 무응답 %d초 — vllm serve(PID %s) 강제 종료",
                         unhealthy_for, proc.pid)
            try:
                proc.kill()
            except OSError:
                pass
            return


def _raise_keyboard_interrupt(signum, frame):
    """SIGTERM을 KeyboardInterrupt로 승격하여 main의 finally cleanup이 실행되게 한다."""
    raise KeyboardInterrupt()


def main():
    args, passthrough = parse_args()

    # start.sh의 stop/restart는 kill(SIGTERM)을 사용하므로 핸들러 등록 필요.
    signal.signal(signal.SIGTERM, _raise_keyboard_interrupt)

    # 이전 실행에서 SIGKILL/crash로 남은 임시 config 정리. (BASE_DIR = launcher 자기 위치)
    # _cleanup_stale_runtime_files()는 RUNTIME_DIR을 yaml 기준으로 갱신한 뒤 호출 (아래).
    _cleanup_stale_configs()

    # ── 설정 로드 ──
    config_path = os.path.abspath(args.config)
    if not os.path.exists(config_path):
        logger.error("설정 파일 없음: %s", config_path)
        sys.exit(1)
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    instance_name = _instance_name_from_config(config_path)

    # yaml의 dirname 기준으로 INSTANCES/RUNTIME 결정 — 여러 인스턴스 디렉토리(vllm/instances/,
    # stt/instances/ 등)를 같은 launcher 코드가 서비스하면서도 runtime json을 yaml 옆에
    # 격리시킨다. 게이트웨이의 _resolve_actual_port도 yaml dirname 기준으로 .runtime을 찾으므로
    # 이 정의가 일치해야 함.
    global INSTANCES_DIR, RUNTIME_DIR, PORT_ALLOC_LOCK
    INSTANCES_DIR = os.path.dirname(config_path)
    RUNTIME_DIR = os.path.join(INSTANCES_DIR, ".runtime")
    PORT_ALLOC_LOCK = os.path.join(RUNTIME_DIR, ".port_alloc.lock")

    # RUNTIME_DIR이 yaml 기준으로 확정된 후 stale runtime 정리.
    _cleanup_stale_runtime_files()

    # ── 환경변수 ──
    env = os.environ.copy()
    if args.gpu is not None:
        env["CUDA_VISIBLE_DEVICES"] = args.gpu
        logger.info("CUDA_VISIBLE_DEVICES=%s", args.gpu)
    if not args.online:
        env["HF_HUB_OFFLINE"] = "1"
        env["TRANSFORMERS_OFFLINE"] = "1"
        logger.info("HF 오프라인 모드")

    # yaml의 env dict를 subprocess 환경에 머지 (모델별 권장 env 반영, 예: Voxtral의
    # VLLM_DISABLE_COMPILE_CACHE=1). 셸이 아닌 python에서 직접 처리하여 start.sh
    # 변경 없이 모든 인스턴스 yaml에서 동일한 메타 키로 사용 가능.
    yaml_env = config.get("env") or {}
    if not isinstance(yaml_env, dict):
        logger.error("yaml의 env는 dict 여야 합니다 (현재: %r): %s", type(yaml_env).__name__, config_path)
        sys.exit(1)
    for k, v in yaml_env.items():
        env[str(k)] = str(v)
        logger.info("env(yaml): %s=%s", k, v)

    # ── 모델 경로 해석 ──
    # --download-only일 때만 sync=True: 로컬이 있어도 HF 최신과 증분 동기화.
    # 서빙 경로(up)는 sync=False — 로컬 파일만 사용, 네트워크 미접근 (폐쇄망 보장).
    raw_model = args.model or config.get("model", "")  # 치환용 원본 ID (경로 해석 전)
    download_dir = config.get("download_dir", "")
    model = _resolve_model_path(raw_model, download_dir, kind="모델", sync=args.download_only)

    # ── speculative_config.model 경로 해석 (drafter 자동 다운로드) ──
    # external drafter 기반 MTP(예: Gemma 4 *-it-assistant) 사용 시, dict 안의
    # model 키도 메인 모델과 동일하게 download_dir 하위로 해석한다.
    # 절대경로로 변환되어 vLLM에 전달되므로 자식 프로세스의 HF_HUB_OFFLINE=1과
    # 무관하게 로컬에서 로드된다.
    # native MTP(method 키만 있는 Qwen 3.6 등)는 model 키가 없어 이 블록을 건너뛴다.
    # ${model} 치환: drafter ID를 본체 모델명에서 유도 (예: "${model}-assistant").
    # 본체 model만 바꾸면 drafter가 자동 추종 — cp 후 짝 어긋남(31B 본체 + 26B drafter 등) 차단.
    # 유도 규칙은 yaml에 명시적으로 보이게 하고, 런처는 문자열 치환만 담당 (벤더 규칙 비내장).
    spec_cfg = config.get("speculative_config")
    if isinstance(spec_cfg, dict) and spec_cfg.get("model"):
        spec_cfg["model"] = _resolve_model_path(
            spec_cfg["model"].replace("${model}", raw_model),
            download_dir, kind="drafter", sync=args.download_only
        )

    if args.download_only:
        logger.info("다운로드 완료. 서버를 실행하지 않습니다.")
        sys.exit(0)

    # ── 포트 자동 회피 + runtime 기록 (직렬화) ──
    # yaml의 port는 hint. 사용 중이면 +1 회피하여 비어있는 첫 포트 사용.
    # 결정된 실제 포트는 runtime 파일에 기록 → 게이트웨이가 우선 참조.
    # 동시 기동 시 같은 port를 둘 다 free로 보는 race를 막기 위해 fcntl.flock으로
    # port 할당과 runtime 기록을 launcher 간 직렬화한다.
    yaml_port = config.get("port")
    if yaml_port is None:
        logger.error("yaml에 port 키가 없습니다 (port hint 필요): %s", config_path)
        sys.exit(1)
    actual_port, runtime_path = _allocate_port_and_register(
        instance_name=instance_name,
        yaml_port=yaml_port,
        model=config.get("model", ""),
    )

    # ── vllm serve 명령 구성 ──
    os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
    runtime_config = _write_vllm_config(config)  # _LAUNCHER_KEYS(port 포함) 제거됨

    # SERVING_VLLM_BIN: 한 컨테이너에 vLLM이 둘 이상 있을 때 쓸 실행 파일(예: 연구계 컨테이너의 0.31 가상환경).
    # 지정하지 않으면 PATH의 vllm을 쓴다(서버 이미지는 vLLM이 하나라 지정하지 않는다).
    # VLLM_ 접두어를 쓰지 않는다: vLLM이 모르는 VLLM_* 환경변수마다 경고를 낸다.
    vllm_bin = os.environ.get("SERVING_VLLM_BIN", "vllm")
    if not shutil.which(vllm_bin):
        logger.error("vLLM 실행 파일을 찾을 수 없습니다: %s (SERVING_VLLM_BIN 확인)", vllm_bin)
        sys.exit(1)
    logger.info("vLLM 실행 파일: %s", shutil.which(vllm_bin))
    cmd = [vllm_bin, "serve"]
    if model:
        cmd.append(model)
    cmd.extend(["--config", runtime_config])

    # 실제 포트는 yaml에서 제거되었으므로 CLI로 명시 전달 (자동 회피 결과 반영).
    cmd.extend(["--port", str(actual_port)])

    # served_model_name 자동 추출 (config에 미설정 시)
    original_id = args.model or config.get("model", "")
    if "served_model_name" not in config and "/" in original_id:
        derived_name = original_id.split("/")[-1]
        cmd.extend(["--served-model-name", derived_name])
        logger.info("served_model_name 자동 추출: %s", derived_name)

    # vLLM YAML 파서(argparse_utils.py:501-504)는 bool true만 --key로 변환하고
    # bool false는 그냥 버린다. async_scheduling은 기본값이 None이고,
    # None으로 들어가면 vllm/config/vllm.py:755-788의 자동 활성화 로직이
    # True로 덮어쓴다(멀티모달 encoder cache race 유발).
    # → YAML에서 false로 명시한 의도를 관철시키려면 --no-async-scheduling
    #   플래그를 직접 추가해야 한다(argparse BooleanOptionalAction 덕분에 유효).
    # 2026-10-08 vLLM 0.31.0 확인: false를 --no-<키>로 바꾸는 코드가 생겼지만 키 이름을
    # 하이픈으로 바꾸기 전에 조회해 밑줄 키(async_scheduling)는 여전히 버린다
    # (utils/argparse_utils.py:615). 0.20 nightly·0.31 모두 이 블록이 있어야 최종값이 False다
    # (시험장 설정 해석 실측: 주입 시 False, 미주입 시 None). 그래서 블록을 유지한다.
    if config.get("async_scheduling") is False:
        cmd.append("--no-async-scheduling")
        logger.info("async_scheduling: false → --no-async-scheduling 플래그 추가")

    cmd.extend(passthrough)
    logger.info("실행: %s", " ".join(cmd))

    # ── 프로세스 실행 (비정상 종료 시 자동 재기동) ──
    # 엔진이 OOM 등으로 죽으면 vllm serve는 종료되지만 VLLM::Worker_TP*가 GPU 메모리를
    # 쥔 채 남는다. 잔재를 정리하지 않고 재기동하면 메모리 부족으로 기동 자체가 실패한다.
    # 기동 전에도 한 번 정리한다 — 이전 실행이 SIGKILL로 끊겨 finally를 못 탄 경우 대비.
    restart_max = int(config.get("auto_restart_max", 3))
    watchdog_seconds = int(config.get("watchdog_unhealthy_seconds",
                                      _WATCHDOG_UNHEALTHY_SECONDS))
    if args.gpu:
        _cleanup_stale_workers(args.gpu, "기동 전")

    proc = None
    attempt = 0
    stop_watchdog = threading.Event()
    try:
        while True:
            started = time.time()
            proc = subprocess.Popen(cmd, env=env)
            stop_watchdog = threading.Event()
            if watchdog_seconds > 0:
                threading.Thread(
                    target=_watchdog,
                    args=(proc, actual_port, stop_watchdog, watchdog_seconds),
                    daemon=True,
                ).start()
            proc.wait()
            stop_watchdog.set()
            uptime = time.time() - started

            if proc.returncode == 0:
                break
            if restart_max <= 0:
                logger.error("vLLM 비정상 종료 rc=%s — 자동 재기동 비활성화됨 "
                             "(auto_restart_max=0)", proc.returncode)
                break
            if uptime >= _RESTART_STABLE_SECONDS:
                attempt = 0
            if attempt >= restart_max:
                logger.error("vLLM 비정상 종료 rc=%s — 연속 %d회 실패로 자동 재기동 중단. "
                             "로그에서 원인 확인 후 수동 기동 필요", proc.returncode, attempt)
                break

            if args.gpu:
                _cleanup_stale_workers(args.gpu, "재기동 전")
            delay = _RESTART_BACKOFFS[min(attempt, len(_RESTART_BACKOFFS) - 1)]
            attempt += 1
            logger.warning("vLLM 비정상 종료 rc=%s (가동 %.0fs) — %d초 후 자동 재기동 (%d/%d)",
                           proc.returncode, uptime, delay, attempt, restart_max)
            time.sleep(delay)
    except KeyboardInterrupt:
        logger.info("서버 종료 중...")
        stop_watchdog.set()          # 정상 종료 경로에서 워치독이 개입하지 않도록
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("정상 종료 실패, 강제 종료")
                proc.kill()
    except FileNotFoundError:
        logger.error(
            "'vllm' 명령어를 찾을 수 없습니다. "
            "pip install vllm 으로 설치했는지 확인하세요."
        )
        sys.exit(1)
    finally:
        try:
            os.unlink(runtime_config)
        except OSError:
            pass
        # runtime 파일은 종료 시 정리 (게이트웨이가 더는 이 인스턴스를 보지 않게)
        _remove_runtime_file(instance_name)
        # vllm serve가 내려가도 워커가 GPU를 쥔 채 남을 수 있다. `./start.sh down`이
        # "완료"를 찍고도 GPU가 안 비는 원인이므로 종료 경로에서 반드시 확인한다.
        if args.gpu:
            _cleanup_stale_workers(args.gpu, "종료 시")
    sys.exit(proc.returncode if proc else 1)


if __name__ == "__main__":
    main()
