#!/usr/bin/env bash
# on-prem/ 코드 갱신 + 폐쇄망 준비 점검
# 사용법: ./start.sh {pull|check}
#
# aws/start.sh(S3 push/pull)의 온프레미스 판이다. 온프레미스는 세팅 시점에만 네트워크가
# 열리고 이후 끊길 수 있어, 코드 동기화는 git으로 하고 그 대신 "끊기 전에 다 받았는가"를
# 점검하는 check가 붙었다.
#
# 재빌드/재기동은 이 스크립트 책임이 아니다 (SRP):
#   - 이미지 재빌드: cd ../aws && docker compose build  (aws/SETUP_GUIDE.md §4-1)
#   - 인스턴스 재생성: ../aws/user.sh rebuild <name>
# 컨테이너 계층은 전부 ../aws/ 에서 실행한다 — 여기는 호스트 계층만 다룬다.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AWS_DIR="$(cd "$SCRIPT_DIR/../aws" && pwd)"
ENV_FILE="$AWS_DIR/.env"
cd "$SCRIPT_DIR"

if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
fi
VOLUME_PATH="${VOLUME_PATH:-/volume}"
VLLM_IMAGE="${VLLM_IMAGE:-}"
LLM_IMAGE_NAME="${LLM_IMAGE_NAME:-llm-prd}"
EXTRA_REQUIREMENTS="${EXTRA_REQUIREMENTS:-}"
NVIDIA_DRIVER_VERSION="${NVIDIA_DRIVER_VERSION:-580.178.04}"

# git pull (네트워크 개방 시에만 동작). S3와 달리 .env는 git 밖이라 안 따라온다.
cmd_pull() {
    if ! git -C "$SCRIPT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        echo "[pull] git 저장소가 아닙니다: $SCRIPT_DIR"
        exit 1
    fi
    echo "[pull] git pull: $(git -C "$SCRIPT_DIR" remote get-url origin 2>/dev/null || echo '?')"
    if ! git -C "$SCRIPT_DIR" pull --ff-only; then
        echo "[pull] 실패 — 네트워크가 닫혀 있으면 개발 머신에서 rsync/scp로 밀어 넣어야 합니다 (SETUP_GUIDE.md §6)"
        exit 1
    fi
    chmod +x "$SCRIPT_DIR"/*.sh "$AWS_DIR"/*.sh 2>/dev/null || true
    echo "[pull] 완료 (.env는 git 밖 — 바뀌었으면 별도 scp)"
    echo "[pull] 다음 단계: cd $AWS_DIR && docker compose build && ../aws/user.sh rebuild <name>"
}

# 최상위 yaml 키의 값 하나를 꺼낸다 (인라인 주석·따옴표 제거). 인자: 키, 파일.
_yaml_top_value() {
    awk -F'#' -v key="$1" '
        $0 ~ "^"key":" { v=$1; sub("^"key":[ \t]*", "", v); gsub(/[ \t]+$/, "", v); gsub(/["'"'"']/, "", v); print v; exit }
    ' "$2"
}

# 폐쇄망 준비 점검. 네트워크를 끊기 전에 실행해 "나중에 받으면 되지"가 없는지 확인한다.
# 항목마다 PASS/FAIL/WARN을 찍고, FAIL이 하나라도 있으면 종료 코드 1.
_fail=0
ok()   { echo "  ✅ $1"; }
warn() { echo "  ⚠️  $1"; }
fail() { echo "  ❌ $1"; _fail=1; }

cmd_check() {
    echo "[check] 폐쇄망 준비 점검 (.env: ${ENV_FILE})"
    echo

    echo "호스트"
    if nvidia-smi &>/dev/null; then
        local drv
        drv=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | tr -d ' ')
        if [ "$drv" = "$NVIDIA_DRIVER_VERSION" ]; then
            ok "NVIDIA 드라이버 ${drv} (.env 고정값과 일치)"
        else
            warn "NVIDIA 드라이버 ${drv} ≠ .env NVIDIA_DRIVER_VERSION ${NVIDIA_DRIVER_VERSION}"
        fi
    else
        fail "nvidia-smi 실패 — 드라이버 미로드"
    fi
    if command -v dnf &>/dev/null; then
        local locked
        locked=$(dnf versionlock list 2>/dev/null | grep -c nvidia || true)
        if [ "${locked:-0}" -gt 0 ]; then
            ok "dnf versionlock nvidia-* ${locked}건 (dnf update로 브랜치가 바뀌지 않음)"
        else
            warn "dnf versionlock에 nvidia 항목 없음 — dnf update 시 드라이버가 610 등으로 올라갈 수 있음 (setup-host.sh 재실행)"
        fi
    fi
    if ls /dev/nvidia-nvswitch* &>/dev/null; then
        if systemctl is-active --quiet nvidia-fabricmanager; then
            ok "Fabric Manager 동작 중 (NVSwitch 감지)"
        else
            fail "NVSwitch가 있는데 nvidia-fabricmanager 비활성 — tensor_parallel 기동 실패 원인"
        fi
    else
        ok "NVSwitch 없음 → Fabric Manager 해당 없음"
    fi
    if command -v docker &>/dev/null; then
        ok "Docker $(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1) / Compose $(docker compose version --short 2>/dev/null || echo '?')"
    else
        fail "docker 없음"
    fi
    echo

    echo "Docker 이미지 (build·기동이 네트워크 없이 되려면 로컬에 있어야 함)"
    if [ -n "$VLLM_IMAGE" ]; then
        docker image inspect "$VLLM_IMAGE" &>/dev/null \
            && ok "베이스 ${VLLM_IMAGE}" \
            || fail "베이스 ${VLLM_IMAGE} 없음 → docker pull ${VLLM_IMAGE}"
    else
        fail "VLLM_IMAGE 미설정 (aws/.env)"
    fi
    docker image inspect "$LLM_IMAGE_NAME" &>/dev/null \
        && ok "빌드 이미지 ${LLM_IMAGE_NAME}" \
        || fail "빌드 이미지 ${LLM_IMAGE_NAME} 없음 → cd ${AWS_DIR} && docker compose build"
    if [ -n "${CUDA_TEST_IMAGE:-}" ]; then
        docker image inspect "$CUDA_TEST_IMAGE" &>/dev/null \
            && ok "GPU 테스트 ${CUDA_TEST_IMAGE}" \
            || warn "GPU 테스트 이미지 ${CUDA_TEST_IMAGE} 없음 (선택)"
    fi
    echo

    echo "빌드 재료 (git 미추적 — scp로 가져와야 함)"
    # vLLM 0.31.0 전환으로 nightly 휠(aws/wheels/)은 빌드 재료가 아니다 — 베이스 이미지의 정식 빌드를 쓴다
    [ -f "$ENV_FILE" ] && ok "aws/.env" || fail "aws/.env 없음 → cp on-prem/.env.prd aws/.env"
    echo

    echo "모델 가중치 (${VOLUME_PATH}/models — llm-serving 인스턴스 yaml 기준)"
    local inst_dir="$SCRIPT_DIR/../llm-serving/vllm/instances"
    local found=0 f model ddir host_dir
    for f in "$inst_dir"/*.yaml; do
        [ -f "$f" ] || continue
        # yaml 파서 없이 awk — 키가 최상위 한 줄(model: X / download_dir: Y)이라는 파일 규약에 기댄다.
        # sed의 '.*'는 로케일이 C면 한글 주석 바이트에서 멈춰 주석이 남는다. '#'로 자르는 awk가 안전.
        model=$(_yaml_top_value model "$f")
        ddir=$(_yaml_top_value download_dir "$f")
        [ -n "$model" ] && [ -n "$ddir" ] || continue
        found=1
        # 컨테이너 /models/LLM → 호스트 ${VOLUME_PATH}/models/LLM (compose bind mount 경로 규약)
        host_dir="${VOLUME_PATH}/${ddir#/}/${model}"
        if [ -d "$host_dir" ] && [ -n "$(ls -A "$host_dir" 2>/dev/null)" ]; then
            ok "$(basename "$f" .yaml): ${model} ($(du -sh "$host_dir" 2>/dev/null | cut -f1))"
        else
            fail "$(basename "$f" .yaml): ${model} 없음 → 컨테이너에서 ./start.sh download $(basename "$f" .yaml)"
        fi
    done
    [ "$found" = 1 ] || warn "instances/*.yaml 에서 model/download_dir 를 읽지 못함"
    echo

    echo "런타임 pip (entrypoint가 매 기동마다 EXTRA_REQUIREMENTS 를 pip install)"
    if [ -n "$EXTRA_REQUIREMENTS" ]; then
        local wheels_dir="${VOLUME_PATH}/data/pip-wheels"
        local pipconf="${VOLUME_PATH}/root/.config/pip/pip.conf"
        if [ -d "$wheels_dir" ] && [ -n "$(ls -A "$wheels_dir" 2>/dev/null)" ]; then
            ok "오프라인 휠 ${wheels_dir} ($(ls "$wheels_dir" | wc -l)개)"
        else
            fail "EXTRA_REQUIREMENTS=${EXTRA_REQUIREMENTS} 인데 ${wheels_dir} 비어 있음 → 폐쇄망에서 컨테이너 기동 실패 (SETUP_GUIDE.md §5-3)"
        fi
        if [ -f "$pipconf" ] && grep -q "no-index" "$pipconf"; then
            ok "pip.conf 오프라인 설정 (${pipconf})"
        else
            fail "${pipconf} 없음 또는 no-index 미설정 → pip이 PyPI로 나가다 실패 (SETUP_GUIDE.md §5-3)"
        fi
    else
        ok "EXTRA_REQUIREMENTS 비어 있음 → 런타임 pip 없음"
    fi
    echo

    if [ "$_fail" = 0 ]; then
        echo "[check] ✅ 통과 — 네트워크를 끊어도 build/up 이 됩니다"
    else
        echo "[check] ❌ FAIL 항목이 있습니다. 네트워크가 열려 있는 동안 해결하세요"
        exit 1
    fi
}

case "${1:-}" in
    pull)   shift; cmd_pull "$@" ;;
    check)  shift; cmd_check "$@" ;;
    *)
        echo "사용법: $0 {pull|check}"
        echo ""
        echo "  pull   git pull (네트워크 개방 시). .env는 별도 scp"
        echo "  check  폐쇄망 준비 점검 — 이미지·휠·모델·pip 오프라인 설정이 로컬에 있는지"
        exit 1
        ;;
esac
