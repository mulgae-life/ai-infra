#!/usr/bin/env bash
# server-setup/ 코드 동기화 + 폐쇄망 준비 점검
# 사용법: ./start.sh {push|pull|check} [추가 aws s3 sync 옵션...]
#
# .env의 PLATFORM으로 서버 종류를 가른다 (비우면 aws — 기존 AWS 서버 .env에는 이 키가 없다)
#   - aws   : push(개발 머신 → S3) / pull(S3 → EC2 호스트)
#   - onprem: pull은 git pull. 세팅 시점에만 네트워크가 열리므로 끊기 전에 check로 점검한다
#
# 재빌드/재기동은 이 스크립트 책임이 아니다 (SRP):
#   - 이미지 재빌드: docker compose build  (SETUP_GUIDE.md §4-1)
#   - 인스턴스 재생성: ./user.sh rebuild <name>
# 여기선 코드 동기화만 하고, 완료 후 다음 단계 명령을 안내한다.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
cd "$SCRIPT_DIR"

# .env 전체를 source하지 않고 PLATFORM만 읽는다 (push·pull은 다른 값이 필요 없다)
PLATFORM=$(grep -E '^PLATFORM=' "$ENV_FILE" 2>/dev/null | tail -1 | cut -d= -f2 | tr -d '"'"'"' \r')
PLATFORM="${PLATFORM:-aws}"
case "$PLATFORM" in
    aws|onprem) ;;
    *) echo ".env PLATFORM은 aws 또는 onprem이어야 합니다 (현재: ${PLATFORM})"; exit 1 ;;
esac

# =====================================================================
# S3 배포 설정 (SETUP_GUIDE.md §1-3 참조)
# 경로는 env로 오버라이드 가능 — 하드코딩 대신 안전한 기본값 + 설정 분리.
# =====================================================================
# 폴더 이름은 server-setup/이지만 S3 경로와 EC2의 ~/aws 는 예전 이름 그대로 둔다 (가동 중인 서버 영향 없음)
S3_URI="${AWS_INFRA_S3_URI:-s3://hgi-ai-res/hjjo/aws/}"

# push(로컬→S3) / pull(S3→로컬) 공통 제외 목록.
# ※ wheels/ 는 vLLM 0.31.0 전환으로 Dockerfile.llm이 더는 쓰지 않는다(nightly 휠 덮어쓰기 제거).
#    2026-10-10 레포 루트 .archive/로 옮겼다. 되돌리기는 휠이 아니라 pre-0.31 태그 이미지로 한다.
# ※ .env(각 서버의 런타임 로드본)는 제외한다 — 환경별 .env.dev/.env.prd만 S3에 보관하고
#    각 서버가 배포 후 알맞은 것을 .env로 복사한다. 제외하지 않으면 pull 한 번에
#    그 서버의 .env가 다른 환경 값으로 덮어써진다(MODE·USERNAME·GPU 배정까지 뒤바뀜).
#    .env.dev/.env.prd는 '.env' 정확매칭에 걸리지 않아 그대로 동기화된다.
#    두 파일은 토큰·비밀번호를 담고 있어 git에는 올리지 않는다(내부망 전용 정책, S3로만 전달).
# ※ .env.onprem은 온프레미스 전용이라 S3에 올리지 않는다(scp로 전달).
SYNC_EXCLUDES=(
    --exclude '.git/*'
    --exclude '**/__pycache__/*'
    --exclude '*.pyc'
    --exclude '.archive/*'
    --exclude '.claude/*'
    --exclude '*.log'
    --exclude '.env'
    --exclude '.env.onprem'
)

require_aws() {
    if ! command -v aws > /dev/null 2>&1; then
        echo "[$1] aws CLI를 찾을 수 없습니다. AWS CLI 설치 또는 IAM Role/aws configure 설정이 필요합니다."
        exit 1
    fi
}

# 로컬 → S3 전체 교체 업로드 (개발 머신에서 코드 변경 반영)
# 증분 sync만으로는 로컬에서 지우거나 이름을 바꾼 파일이 S3에 남아 pull 때 되살아난다.
# 프리픽스를 비운 뒤 올려 로컬과 정확히 일치시킨다.
# 제외 목록(.git/·__pycache__/·.archive/·*.log)은 애초에 S3에 있어서는 안 되는 것들이라
# 삭제 단계에서 함께 지워져도 잃을 것이 없다.
# ※ 큰 파일을 이 폴더 아래에 두면 제외 대상이 아니라 push마다 다시 올라간다.
#    변경분만 올리고 싶으면 --dryrun으로 규모를 먼저 확인할 것.
cmd_push() {
    require_aws push

    # 버킷 루트 오설정 시 rm --recursive가 버킷 전체를 지우는 것을 차단
    if [[ ! "$S3_URI" =~ ^s3://[^/]+/.+ ]]; then
        echo "[push] S3_URI가 버킷 루트이거나 형식 오류: $S3_URI — 중단"
        exit 1
    fi

    # --dryrun은 삭제 단계에도 붙인다. sync에만 넘기면 "미리보기"로 부른 호출이
    # S3를 실제로 비워버린다. --delete 같은 sync 전용 옵션은 rm이 모르므로 걸러낸다.
    local rm_opts=() a
    for a in "$@"; do
        [ "$a" = "--dryrun" ] && rm_opts+=(--dryrun)
    done

    echo "[push] S3 기존 객체 전체 삭제: $S3_URI"
    if ! aws s3 rm "$S3_URI" --recursive "${rm_opts[@]}"; then
        echo "[push] S3 삭제 실패 — 경로/권한(IAM Role) 확인 후 재시도"
        exit 1
    fi

    echo "[push] 로컬 → S3 업로드: $SCRIPT_DIR → $S3_URI"
    if ! aws s3 sync "$SCRIPT_DIR" "$S3_URI" "${SYNC_EXCLUDES[@]}" "$@"; then
        echo "[push] S3 업로드 실패 — 프리픽스가 비워진 상태이니 반드시 push를 재실행할 것"
        exit 1
    fi
    echo "[push] 업로드 완료 (.env.dev·.env.prd 포함, .env 런타임본은 제외)"
    echo "[push] 운영계 적용: ./start.sh pull 후 docker compose build && ./user.sh rebuild <name>"
}

# S3 → 로컬 다운로드 (EC2 호스트에서 코드 받기)
# --delete: S3에서 사라진 파일을 로컬에서도 지워 push(전체 교체)와 정확히 일치시킨다.
# 제외 목록(.git/·.archive/·*.log 등)은 --delete에서도 삭제되지 않고 보호된다.
# --exact-timestamps: 크기가 같은 파일은 타임스탬프가 정확히 일치할 때만 건너뛴다.
#   기본 규칙은 "크기가 같고 로컬이 더 새로우면 스킵"인데, sync로 받은 파일의 mtime은 S3
#   객체의 시각이 아니라 다운로드한 시각으로 찍혀 로컬이 늘 더 새로워진다. 여기에 받은 쪽에서
#   파일을 한 번 건드렸거나 두 서버 시계가 어긋나면 갱신된 파일이 조용히 스킵된다. sync는
#   체크섬을 보지 않으므로 크기까지 같은 수정(.env.prd의 포트 번호 한 자리 변경 등)에서 특히
#   잘 걸린다. 이 옵션이 그 판정을 막아 rm -rf 후 재다운로드와 같은 정합을 준다.
cmd_pull() {
    if [ "$PLATFORM" = "onprem" ]; then
        cmd_pull_git "$@"
        return
    fi
    if git -C "$SCRIPT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        echo "[pull] git 작업 사본에서는 S3 pull을 하지 않습니다 (--delete가 로컬 변경을 지운다): $SCRIPT_DIR"
        echo "       온프레미스면 .env에 PLATFORM=onprem 을 넣으세요"
        exit 1
    fi
    require_aws pull

    echo "[pull] S3 → 로컬 동기화(잔재 삭제 포함): $S3_URI → $SCRIPT_DIR"
    if ! aws s3 sync "$S3_URI" "$SCRIPT_DIR" --delete --exact-timestamps "${SYNC_EXCLUDES[@]}" "$@"; then
        echo "[pull] S3 다운로드 실패 — 경로/권한(IAM Role) 확인 후 재시도"
        exit 1
    fi
    chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null || true
    echo "[pull] 다운로드 완료 (.env 런타임본은 제외 — 기존 설정 유지됨)"
    # 최초 배포 서버에는 .env가 없다. 여기서 안내하지 않으면 docker compose가
    # 빈 변수로 뜨면서 원인이 드러나지 않는 실패를 낸다.
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        echo "[pull] .env가 없습니다. 최초 1회 환경에 맞는 설정을 복사하세요:"
        echo "         cp .env.dev .env   (개발계)   또는   cp .env.prd .env   (운영계)"
    fi
    echo "[pull] 다음 단계: docker compose build && ./user.sh rebuild <name>"
}

# git pull (네트워크 개방 시에만 동작). S3와 달리 .env는 git 밖이라 안 따라온다.
cmd_pull_git() {
    if ! git -C "$SCRIPT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        echo "[pull] git 저장소가 아닙니다: $SCRIPT_DIR"
        exit 1
    fi
    echo "[pull] git pull: $(git -C "$SCRIPT_DIR" remote get-url origin 2>/dev/null || echo '?')"
    if ! git -C "$SCRIPT_DIR" pull --ff-only; then
        echo "[pull] 실패 — 네트워크가 닫혀 있으면 개발 머신에서 rsync/scp로 밀어 넣어야 합니다 (SETUP_GUIDE_ONPREM.md §7-1)"
        exit 1
    fi
    chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null || true
    echo "[pull] 완료 (.env는 git 밖 — 바뀌었으면 별도 scp)"
    echo "[pull] 다음 단계: docker compose build && ./user.sh rebuild <name>"
}

# 폐쇄망 준비 점검. 네트워크를 끊기 전에 실행해 "나중에 받으면 되지"가 없는지 확인한다.
# 항목마다 PASS/FAIL/WARN을 찍고, FAIL이 하나라도 있으면 종료 코드 1.
_fail=0
ok()   { echo "  ✅ $1"; }
warn() { echo "  ⚠️  $1"; }
fail() { echo "  ❌ $1"; _fail=1; }

cmd_check() {
    if [ -f "$ENV_FILE" ]; then
        set -a
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set +a
    fi
    local VOLUME_PATH="${VOLUME_PATH:-/volume}"
    local DATA_PATH="${DATA_PATH:-${VOLUME_PATH}/data}"
    local VLLM_IMAGE="${VLLM_IMAGE:-}"
    local LLM_IMAGE_NAME="${LLM_IMAGE_NAME:-llm-prd}"
    local EXTRA_REQUIREMENTS="${EXTRA_REQUIREMENTS:-}"
    local NVIDIA_DRIVER_VERSION="${NVIDIA_DRIVER_VERSION:-580.196.07}"
    echo "[check] 폐쇄망 준비 점검 (.env: ${ENV_FILE}, PLATFORM=${PLATFORM})"
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
        fail "VLLM_IMAGE 미설정 (.env)"
    fi
    docker image inspect "$LLM_IMAGE_NAME" &>/dev/null \
        && ok "빌드 이미지 ${LLM_IMAGE_NAME}" \
        || fail "빌드 이미지 ${LLM_IMAGE_NAME} 없음 → docker compose build"
    if [ -n "${CUDA_TEST_IMAGE:-}" ]; then
        docker image inspect "$CUDA_TEST_IMAGE" &>/dev/null \
            && ok "GPU 테스트 ${CUDA_TEST_IMAGE}" \
            || warn "GPU 테스트 이미지 ${CUDA_TEST_IMAGE} 없음 (선택)"
    fi
    echo

    echo "빌드 재료 (git 미추적 — scp로 가져와야 함)"
    # vLLM 0.31.0 전환으로 nightly 휠은 빌드 재료가 아니다 — 베이스 이미지의 정식 빌드를 쓴다
    [ -f "$ENV_FILE" ] && ok ".env" || fail ".env 없음 → cp .env.onprem .env"
    echo

    echo "런타임 pip (entrypoint가 매 기동마다 EXTRA_REQUIREMENTS 를 pip install)"
    if [ -n "$EXTRA_REQUIREMENTS" ]; then
        local wheels_dir="${DATA_PATH}/pip-wheels"
        local pipconf="${VOLUME_PATH}/root/.config/pip/pip.conf"
        if [ -d "$wheels_dir" ] && [ -n "$(ls -A "$wheels_dir" 2>/dev/null)" ]; then
            ok "오프라인 휠 ${wheels_dir} ($(ls "$wheels_dir" | wc -l)개)"
        else
            fail "EXTRA_REQUIREMENTS=${EXTRA_REQUIREMENTS} 인데 ${wheels_dir} 비어 있음 → 폐쇄망에서 컨테이너 기동 실패 (SETUP_GUIDE_ONPREM.md §5-3)"
        fi
        if [ -f "$pipconf" ] && grep -q "no-index" "$pipconf"; then
            ok "pip.conf 오프라인 설정 (${pipconf})"
        else
            fail "${pipconf} 없음 또는 no-index 미설정 → pip이 PyPI로 나가다 실패 (SETUP_GUIDE_ONPREM.md §5-3)"
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
    push)   shift; cmd_push "$@" ;;
    pull)   shift; cmd_pull "$@" ;;
    check)  shift; cmd_check "$@" ;;
    *)
        echo "사용법: $0 {push|pull|check} [추가 aws s3 sync 옵션...]   (현재 PLATFORM=${PLATFORM})"
        echo ""
        echo "  push   로컬 → S3 전체 교체 업로드 (기존 S3 객체 삭제 후 업로드, 개발 머신)"
        echo "  pull   aws: S3 → 로컬 받기 (S3에 없는 로컬 파일 삭제, EC2 호스트)"
        echo "         onprem: git pull (네트워크 개방 시). .env는 별도 scp"
        echo "  check  폐쇄망 준비 점검 — 드라이버 잠금·이미지·pip 오프라인 설정 (온프레미스)"
        echo ""
        echo "추가 옵션 예시:"
        echo "  ./start.sh push --dryrun       업로드 미리보기 (삭제 단계도 미리보기로 동작)"
        exit 1
        ;;
esac
