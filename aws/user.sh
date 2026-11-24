#!/bin/bash
set -euo pipefail

# ============================================
# 다중 사용자 컨테이너 관리
#
# 사용법:
#   ./user.sh up <name> [--root] [--password <pw>] [--gpus <gpus>]
#                       [--service-port <p>] [--extra-ports <range>]
#   ./user.sh down <name>
#   ./user.sh rebuild [name]       ← 이미지 변경 후 컨테이너 재생성
#   ./user.sh list
#
# --root: 컨테이너 내부 OS 계정을 root로 사용 (운영계 root 컨테이너를 여러 개 동시 운용)
#         - 홈 볼륨: /volume/root-homes/<name>:/root (컨테이너별 독립)
#         - SSH 접속 불가 (PermitRootLogin no) → docker exec 로 접근
#         - 다중 운용: --service-port 로 컨테이너마다 호스트 포트 분리
#           (미지정 시 .env LLM_EXTRA_PORTS 폴백)
#
# --extra-ports <spec>: 일반 모드(--root 아님)에서 기본 자동 할당 range(예: 5041-5049) 외에
#         추가 호스트 range를 그대로 컨테이너 동일 포트로 노출.
#         단일 range: 5100-5149 / 다중 range: 5020-5029,5100-5200 (콤마 구분)
#         (재생성 시 라벨로 자동 보존)
#
# 포트 할당 (자동):
#   docker-compose 메인: 5000(SSH), 5001-5009
#   user.sh 첫 컨테이너: 5010(SSH), 5011-5019
#   user.sh 두 번째:     5020(SSH), 5021-5029
#   ...
#   user.sh 최대:        5490(SSH), 5491-5499
# ============================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT_BASE=5010
PORT_STEP=10
PORT_MAX=5500

# .env 로드 (VOLUME_PATH, HF_TOKEN, LLM_IMAGE_NAME 등)
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

# docker-compose.yml 의 LLM_IMAGE_NAME 과 반드시 동일 값이어야 함 (설정 채널 일원화)
IMAGE_NAME="${LLM_IMAGE_NAME:-llm-dev}"
VOLUME_PATH="${VOLUME_PATH:-/volume}"
# 모델·데이터 공유 경로. 온프레미스처럼 별도 파일시스템이면 .env에서 지정한다
MODELS_PATH="${MODELS_PATH:-${VOLUME_PATH}/models}"
DATA_PATH="${DATA_PATH:-${VOLUME_PATH}/data}"
HF_TOKEN="${HF_TOKEN:-}"
EXTRA_REQUIREMENTS="${EXTRA_REQUIREMENTS:-}"
SHM_SIZE="${SHM_SIZE:-16g}"
LLM_MEMORY="${LLM_MEMORY:-48g}"
CONTAINER_UID="${CONTAINER_UID:-2000}"
CONTAINER_GID="${CONTAINER_GID:-2000}"
MODE="${MODE:-dev}"

# 공유 디렉토리(/models, /data) 소유권용 글로벌 UID/GID — 시작 시점에 .env 값으로 한번만 캡처.
# rebuild가 cmd_up을 호출할 때 root 컨테이너의 컨테이너별 CONTAINER_UID=0을 인라인 환경변수로
# 주입(L437)하므로, cmd_up 안에서 보이는 CONTAINER_UID는 컨테이너 home용임.
# 공유 디렉토리는 모든 컨테이너가 함께 쓰므로 글로벌 .env 값으로 chown해야 root 컨테이너 rebuild가
# 일반 사용자(2000)의 쓰기 권한을 깨지 않음.
SHARED_UID="${CONTAINER_UID}"
SHARED_GID="${CONTAINER_GID}"

usage() {
    echo "사용법:"
    echo "  $0 up <name> [--root] [--password <pw>] [--gpus <gpus>]"
    echo "  $0 down <name>"
    echo "  $0 rebuild [name]   # 이미지 변경 후 재생성 (전체 또는 특정 컨테이너)"
    echo "  $0 list"
    echo ""
    echo "  --root: 내부 OS 계정을 root로 사용 (홈=/volume/root-homes/<name>, SSH 접속 불가)"
    echo "  --service-port <p>: --root 전용 외부 노출 서비스 포트 (단일 또는 range, 기본 .env LLM_EXTRA_PORTS)"
    echo "  --extra-ports <s>:  일반 모드 추가 노출 range — 기본 range에 더해 -p로 추가"
    echo "                       단일: 5100-5149 / 다중(콤마): 5020-5029,5100-5200"
    exit 1
}

# username 검증 (영문자 시작, 영문/숫자/밑줄/하이픈, 최대 32자)
# root는 운영계 전용 → docker compose 로 별도 관리
validate_username() {
    local name="$1"
    if [ "$name" = "root" ]; then
        echo "❌ root는 user.sh 관리 대상이 아닙니다."
        echo "   - 운영계 생성: .env에 USERNAME=root 후 'docker compose up -d'"
        echo "   - 기존 root 컨테이너 제거: 'docker stop <name> && docker rm <name>'"
        exit 1
    fi
    if ! [[ "$name" =~ ^[a-zA-Z][a-zA-Z0-9_-]{0,31}$ ]]; then
        echo "❌ username은 영문자로 시작, 영문/숫자/밑줄/하이픈만 허용 (최대 32자)"
        exit 1
    fi
}

# GPU 값 검증 (none, all 또는 숫자/콤마 조합)
validate_gpus() {
    local gpus="$1"
    if [ "$gpus" = "all" ] || [ "$gpus" = "none" ]; then return 0; fi
    if ! [[ "$gpus" =~ ^[0-9]+(,[0-9]+)*$ ]]; then
        echo "❌ --gpus는 'none', 'all' 또는 GPU 번호(예: 0,1,2)만 허용"
        exit 1
    fi
}

# 포트 스펙 검증 (단일 정수 또는 range — 5031, 5001-5009)
validate_port_spec() {
    local p="$1"
    if ! [[ "$p" =~ ^[0-9]+(-[0-9]+)?$ ]]; then
        echo "❌ 포트는 정수 또는 range(예: 5031, 5001-5009)만 허용 — '$p' 거부"
        exit 1
    fi
}

# 사용 중인 포트 베이스 목록 조회 (중지된 컨테이너 포함)
get_used_bases() {
    docker ps -a --filter "label=managed-by=user.sh" --format '{{.Names}}' 2>/dev/null | while read -r name; do
        local ssh_port
        ssh_port=$(docker inspect \
            --format='{{range $p, $conf := .HostConfig.PortBindings}}{{if eq $p "5555/tcp"}}{{(index $conf 0).HostPort}}{{end}}{{end}}' \
            "$name" 2>/dev/null || true)
        if [ -n "$ssh_port" ]; then
            echo "$ssh_port"
        fi
    done
}

# 다음 사용 가능한 포트 베이스 찾기
next_port_base() {
    local used_bases
    used_bases=$(get_used_bases | sort -n)

    local base=$PORT_BASE
    while [ $base -lt $PORT_MAX ]; do
        if ! echo "$used_bases" | grep -q "^${base}$"; then
            echo "$base"
            return
        fi
        base=$((base + PORT_STEP))
    done

    echo ""
}

# 컨테이너가 이미 존재하는지 확인
container_exists() {
    docker ps -a --filter "name=^${1}$" --format '{{.Names}}' 2>/dev/null | grep -q .
}

cmd_up() {
    local username=""
    local password="changeme"
    local gpus="all"
    local forced_port=""
    local forced_service_port=""
    local forced_extra_ports=""
    local as_root=false

    # 인자 파싱
    while [ $# -gt 0 ]; do
        case "$1" in
            --password)
                [ $# -ge 2 ] || { echo "❌ --password에 값이 필요합니다."; usage; }
                password="$2"; shift 2 ;;
            --gpus)
                [ $# -ge 2 ] || { echo "❌ --gpus에 값이 필요합니다."; usage; }
                gpus="$2"; shift 2 ;;
            --ssh-port)
                # rebuild 내부용: 기존 포트 보존
                [ $# -ge 2 ] || { echo "❌ --ssh-port에 값이 필요합니다."; exit 1; }
                forced_port="$2"; shift 2 ;;
            --service-port)
                # --root 다중 운용용: 호스트 서비스 포트(단일/range) 명시
                [ $# -ge 2 ] || { echo "❌ --service-port에 값이 필요합니다."; usage; }
                forced_service_port="$2"; shift 2 ;;
            --extra-ports)
                # 일반 모드 추가 노출 range — 기본 자동 range에 더해 -p로 한 줄 더 추가
                [ $# -ge 2 ] || { echo "❌ --extra-ports에 값이 필요합니다."; usage; }
                forced_extra_ports="$2"; shift 2 ;;
            --root)
                as_root=true; shift ;;
            -*) echo "알 수 없는 옵션: $1"; usage ;;
            *) username="$1"; shift ;;
        esac
    done

    if [ -z "$username" ]; then
        echo "❌ username을 지정해주세요."
        usage
    fi

    validate_username "$username"
    validate_gpus "$gpus"
    [ -n "$forced_service_port" ] && validate_port_spec "$forced_service_port"
    # --extra-ports 는 콤마 구분 다중 range 허용 (예: 5020-5029,5100-5200)
    # 각 토큰을 validate_port_spec으로 개별 검증
    if [ -n "$forced_extra_ports" ]; then
        IFS=',' read -ra _extra_tokens <<< "$forced_extra_ports"
        for _tok in "${_extra_tokens[@]}"; do
            validate_port_spec "$_tok"
        done
    fi

    # --service-port 는 --root 다중 운용 전용
    # — 일반 모드(자동 포트 할당)에서 사용하면 silent 무시되어 오해 소지 → fail-fast로 차단
    if ! $as_root && [ -n "$forced_service_port" ]; then
        echo "❌ --service-port 는 --root 모드 전용입니다."
        usage
    fi

    # --extra-ports 는 일반 모드 전용 (--root는 --service-port 사용)
    if $as_root && [ -n "$forced_extra_ports" ]; then
        echo "❌ --extra-ports 는 일반 모드 전용입니다. --root에서는 --service-port 를 사용하세요."
        usage
    fi

    if [ "$password" = "changeme" ]; then
        echo "⚠️ 기본 비밀번호(changeme)를 사용합니다. --password로 변경을 권장합니다."
    fi

    # 이미 존재하는 컨테이너 확인
    if container_exists "$username"; then
        local state
        state=$(docker inspect -f '{{.State.Status}}' "${username}" 2>/dev/null || true)
        if [ "$state" = "running" ]; then
            echo "✅ ${username} 이미 실행 중"
            docker port "${username}"
            return
        else
            echo "🔄 중지된 컨테이너 재시작: ${username}"
            echo "   ⚠️ 기존 설정으로 재시작됩니다. 옵션 변경이 필요하면:"
            echo "      $0 down ${username} && $0 up ${username} [옵션]"
            docker start "${username}"
            echo "✅ 재시작 완료"
            docker port "${username}"
            return
        fi
    fi

    # 이미지 확인
    if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
        echo "⚠️ 이미지 '$IMAGE_NAME'이 없습니다. 먼저 빌드하세요:"
        echo "   cd $SCRIPT_DIR && docker compose build"
        exit 1
    fi

    # 포트 할당
    # --root: .env 가 기본값, --service-port 인자가 있으면 우선 적용
    #         → 다중 root 컨테이너 동시 운용 시 인자로 컨테이너별 호스트 포트 분리
    #         → 컨테이너끼리 호스트 포트가 겹치면 docker run 단계에서 fail-fast
    # 일반  : base 자동 할당 (5010, 5020, ...) 또는 --ssh-port 로 강제
    local ssh_port extra_start extra_end extra_ports_spec
    if $as_root; then
        ssh_port="${LLM_SSH_PORT:-5000}"
        extra_start=""
        extra_end=""
        extra_ports_spec="${forced_service_port:-${LLM_EXTRA_PORTS:-5001-5009}}"
    else
        local base
        if [ -n "$forced_port" ]; then
            base=$forced_port
        else
            base=$(next_port_base)
            if [ -z "$base" ]; then
                echo "❌ 포트 범위 초과 (최대 ${PORT_MAX}). 더 이상 사용자를 생성할 수 없습니다."
                exit 1
            fi
        fi
        ssh_port=$base
        extra_start=$((base + 1))
        extra_end=$((base + PORT_STEP - 1))
        extra_ports_spec=""
    fi

    # 홈 볼륨 분기: --root는 /volume/root-homes/<name>:/root, 일반은 /volume/homes/<name>:/home/<name>
    # compose 메인(운영계)이 쓰는 /volume/root 와 구분되도록 root-homes 네임스페이스 별도 사용
    local home_host home_container home_uid home_gid container_username
    if $as_root; then
        home_host="${VOLUME_PATH}/root-homes/${username}"
        home_container="/root"
        home_uid=0
        home_gid=0
        container_username="root"
    else
        home_host="${VOLUME_PATH}/homes/${username}"
        home_container="/home/${username}"
        home_uid="${CONTAINER_UID}"
        home_gid="${CONTAINER_GID}"
        container_username="${username}"
    fi

    # 디렉토리 생성 + 소유권 설정 (sudo로 실행되므로 root 소유 방지)
    mkdir -p "${VOLUME_PATH}/workspace/${username}"
    mkdir -p "$home_host"
    mkdir -p "$MODELS_PATH"
    mkdir -p "$DATA_PATH"
    chown "${home_uid}:${home_gid}" "${VOLUME_PATH}/workspace/${username}"
    chown "${home_uid}:${home_gid}" "$home_host"
    # models/data 는 공유 디렉토리 → 글로벌 SHARED_UID/GID 소유 유지 (스크립트 시작 시점 .env 값).
    # rebuild가 root 컨테이너의 CONTAINER_UID=0을 cmd_up에 주입해도 공유 디렉토리 chown은 영향받지 않음
    # — root 컨테이너는 권한이 0이라 어차피 모든 디렉토리에 쓸 수 있고, 일반 사용자(2000) 쓰기 권한이 보존됨.
    chown "${SHARED_UID}:${SHARED_GID}" "$MODELS_PATH"
    chown "${SHARED_UID}:${SHARED_GID}" "$DATA_PATH"

    # GPU 옵션 (--gpus로 직접 제어, NVIDIA_VISIBLE_DEVICES 환경변수 미사용)
    # Docker --gpus 파서는 CSV 방식: 쉼표가 필드 구분자.
    # 복수 GPU는 리터럴 따옴표로 감싸야 하나의 device 값으로 인식됨.
    # 예: --gpus '"device=2,3"' → CSV 파서가 "device=2,3"을 단일 필드로 처리
    local -a gpu_opts=()
    if [ "$gpus" = "none" ]; then
        gpu_opts=(--runtime=runc)
    elif [ "$gpus" = "all" ]; then
        gpu_opts=(--gpus all)
    else
        gpu_opts=(--gpus "\"device=${gpus}\"")
    fi

    echo "🚀 컨테이너 생성: ${username}"
    if $as_root; then
        # 포트 출처 표기: CLI 인자가 있으면 'CLI', 없으면 '.env <키>' 폴백
        local svc_src="${forced_service_port:+CLI}${forced_service_port:-.env LLM_EXTRA_PORTS}"
        echo "   모드:         root (SSH 접속 불가 — docker exec 로 접근)"
        echo "   서비스 포트:  ${extra_ports_spec} (${svc_src})"
    else
        echo "   SSH:          ssh -p ${ssh_port} ${username}@<host>"
        echo "   포트 범위:    ${extra_start}-${extra_end} (1:1 매핑)"
        [ -n "$forced_extra_ports" ] && echo "   추가 포트:    ${forced_extra_ports} (1:1 매핑, --extra-ports)"
    fi
    echo "   GPU:          ${gpus}"

    # 포트 바인딩
    # — 일반: SSH(5555) + 서비스 range
    # — --root: SSH 미바인딩 (Dockerfile sshd가 PermitRootLogin no라 접속 불가, 포트만 점유) +
    #           서비스 포트만 노출 (셸 접근은 docker exec)
    local -a port_opts=()
    if $as_root; then
        port_opts+=(-p "${extra_ports_spec}:${extra_ports_spec}")
    else
        port_opts+=(-p "${ssh_port}:5555")
        port_opts+=(-p "${extra_start}-${extra_end}:${extra_start}-${extra_end}")
        # 일반 모드 추가 range — 기본 자동 range 외에 사용자가 명시한 추가 호스트 포트 노출
        # 콤마 구분 다중 range 지원 (예: 5020-5029,5100-5200) — 토큰별로 -p 한 줄씩 추가
        if [ -n "$forced_extra_ports" ]; then
            IFS=',' read -ra _ep_tokens <<< "$forced_extra_ports"
            for _tok in "${_ep_tokens[@]}"; do
                port_opts+=(-p "${_tok}:${_tok}")
            done
        fi
    fi

    docker run -d \
        --name "${username}" \
        --hostname "${username}" \
        --label "managed-by=user.sh" \
        --label "as-root=${as_root}" \
        --label "service-port=${extra_ports_spec}" \
        --label "extra-ports=${forced_extra_ports}" \
        --restart unless-stopped \
        --security-opt apparmor=unconfined \
        --security-opt seccomp=unconfined \
        --shm-size "$SHM_SIZE" \
        --memory "$LLM_MEMORY" \
        "${port_opts[@]}" \
        -v "${VOLUME_PATH}/workspace/${username}:/workspace" \
        -v "${MODELS_PATH}:/models" \
        -v "${DATA_PATH}:/data" \
        -v "${home_host}:${home_container}" \
        -e "USERNAME=${container_username}" \
        -e "PASSWORD=${password}" \
        -e "CONTAINER_UID=${home_uid}" \
        -e "CONTAINER_GID=${home_gid}" \
        -e "HF_TOKEN=${HF_TOKEN}" \
        -e "EXTRA_REQUIREMENTS=${EXTRA_REQUIREMENTS}" \
        -e "ASSIGNED_GPUS=${gpus}" \
        -e "MODE=${MODE}" \
        "${gpu_opts[@]}" \
        "$IMAGE_NAME"

    echo "✅ 완료"
}

cmd_down() {
    local username="${1:-}"
    if [ -z "$username" ]; then
        echo "❌ username을 지정해주세요."
        usage
    fi

    validate_username "$username"

    if ! container_exists "$username"; then
        echo "❌ 컨테이너 '${username}'이 없습니다."
        exit 1
    fi

    if ! docker inspect --format='{{index .Config.Labels "managed-by"}}' "$username" 2>/dev/null | grep -q "user.sh"; then
        echo "❌ '${username}'은 user.sh로 관리되는 컨테이너가 아닙니다."
        exit 1
    fi

    echo "🗑️ 컨테이너 중지 및 제거: ${username}"
    docker stop "${username}" 2>/dev/null || true
    docker rm "${username}" 2>/dev/null || true
    echo "✅ 완료 (데이터는 ${VOLUME_PATH}에 보존됨)"
}

cmd_list() {
    echo "=== LLM 사용자 컨테이너 (user.sh 관리) ==="
    local output
    # as-root 컬럼으로 root 모드 컨테이너 구분 표시
    output=$(docker ps -a \
        --filter "label=managed-by=user.sh" \
        --format 'table {{.Names}}\t{{.Status}}\t{{.Label "as-root"}}\t{{.Ports}}' 2>/dev/null)
    if [ -n "$output" ]; then
        echo "$output"
    else
        echo "(없음)"
    fi
}

cmd_rebuild() {
    local target="${1:-}"
    local containers

    # jq 필수 (환경변수 추출용)
    if ! command -v jq &>/dev/null; then
        echo "❌ rebuild에는 jq가 필요합니다. 설치: sudo yum install -y jq"
        exit 1
    fi

    if [ -n "$target" ]; then
        validate_username "$target"
        if ! container_exists "$target"; then
            echo "❌ 컨테이너 '${target}'이 없습니다."
            exit 1
        fi
        if ! docker inspect --format='{{index .Config.Labels "managed-by"}}' "$target" 2>/dev/null | grep -q "user.sh"; then
            echo "❌ '${target}'은 user.sh로 관리되는 컨테이너가 아닙니다."
            exit 1
        fi
        containers="${target}"
    else
        containers=$(docker ps -a \
            --filter "label=managed-by=user.sh" \
            --format '{{.Names}}' 2>/dev/null)
        if [ -z "$containers" ]; then
            echo "재생성할 컨테이너가 없습니다."
            return
        fi
    fi

    # 이미지 확인
    if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
        echo "⚠️ 이미지 '$IMAGE_NAME'이 없습니다. 먼저 빌드하세요:"
        echo "   cd $SCRIPT_DIR && docker compose build"
        exit 1
    fi

    # here-string으로 현재 쉘에서 실행 (서브쉘 회피)
    while read -r cname; do
        [ -z "$cname" ] && continue
        local uname="$cname"

        # 기존 컨테이너에서 설정 추출
        local env_json
        env_json=$(docker inspect --format='{{json .Config.Env}}' "$cname" 2>/dev/null)

        local old_password old_gpus old_uid old_gid old_ssh_port old_as_root old_service_port old_extra_ports
        old_password=$(echo "$env_json" | jq -r '.[] | select(startswith("PASSWORD=")) | sub("^PASSWORD=";"")')
        old_gpus=$(echo "$env_json" | jq -r '.[] | select(startswith("ASSIGNED_GPUS=")) | sub("^ASSIGNED_GPUS=";"")')
        # 이전 버전 호환 (NVIDIA_VISIBLE_DEVICES → ASSIGNED_GPUS 마이그레이션)
        if [ -z "$old_gpus" ]; then
            old_gpus=$(echo "$env_json" | jq -r '.[] | select(startswith("NVIDIA_VISIBLE_DEVICES=")) | sub("^NVIDIA_VISIBLE_DEVICES=";"")')
        fi
        old_uid=$(echo "$env_json" | jq -r '.[] | select(startswith("CONTAINER_UID=")) | sub("^CONTAINER_UID=";"")')
        old_gid=$(echo "$env_json" | jq -r '.[] | select(startswith("CONTAINER_GID=")) | sub("^CONTAINER_GID=";"")')
        old_mode=$(echo "$env_json" | jq -r '.[] | select(startswith("MODE=")) | sub("^MODE=";"")')

        # 기존 SSH 포트 보존
        old_ssh_port=$(docker inspect \
            --format='{{range $p, $conf := .HostConfig.PortBindings}}{{if eq $p "5555/tcp"}}{{(index $conf 0).HostPort}}{{end}}{{end}}' \
            "$cname" 2>/dev/null || true)

        # --root 모드 + 포트 인자 복원 (라벨 없는 구버전 컨테이너는 false/빈값으로 간주)
        old_as_root=$(docker inspect --format='{{index .Config.Labels "as-root"}}' "$cname" 2>/dev/null || true)
        old_service_port=$(docker inspect --format='{{index .Config.Labels "service-port"}}' "$cname" 2>/dev/null || true)
        old_extra_ports=$(docker inspect --format='{{index .Config.Labels "extra-ports"}}' "$cname" 2>/dev/null || true)

        old_password="${old_password:-changeme}"
        old_gpus="${old_gpus:-all}"
        old_uid="${old_uid:-2000}"
        old_gid="${old_gid:-2000}"
        old_mode="${old_mode:-${MODE:-dev}}"
        old_ssh_port="${old_ssh_port:-}"
        old_as_root="${old_as_root:-false}"

        echo "🔄 재생성: ${cname} (MODE: ${old_mode}, GPU: ${old_gpus}, SSH: ${old_ssh_port:-auto}, root: ${old_as_root})"

        # 기존 컨테이너 제거
        docker stop "$cname" 2>/dev/null || true
        docker rm "$cname" 2>/dev/null || true

        # 동일 설정으로 재생성
        # 일반  : 기존 SSH 포트 보존 (--ssh-port 전달)
        # --root: .env 포트 재참조 (포트 변경하려면 .env 수정 후 rebuild)
        local -a port_opts=() root_opts=()
        if [ "$old_as_root" = "true" ]; then
            root_opts=(--root)
            # 라벨에 저장된 포트 그대로 복원 — .env가 바뀌어도 기존 컨테이너 포트는 유지
            [ -n "$old_service_port" ] && root_opts+=(--service-port "$old_service_port")
        else
            [ -n "$old_ssh_port" ] && port_opts=(--ssh-port "$old_ssh_port")
            # 일반 모드 추가 range 라벨 복원 (라벨 없는 구버전 컨테이너는 빈값 → 미전달)
            [ -n "$old_extra_ports" ] && port_opts+=(--extra-ports "$old_extra_ports")
        fi

        MODE="$old_mode" CONTAINER_UID="$old_uid" CONTAINER_GID="$old_gid" \
            cmd_up "$uname" "${root_opts[@]}" --password "$old_password" --gpus "$old_gpus" "${port_opts[@]}"
    done <<< "$containers"

    echo "✅ rebuild 완료"
}

# ============================================
# 메인
# ============================================
[ $# -lt 1 ] && usage

CMD="$1"
shift

case "$CMD" in
    up)      cmd_up "$@" ;;
    down)    cmd_down "${1:-}" ;;
    rebuild) cmd_rebuild "${1:-}" ;;
    list)    cmd_list ;;
    *)       usage ;;
esac
