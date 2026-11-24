#!/bin/bash
set -euo pipefail

# ============================================
# EC2 GPU 서버 초기 세팅 스크립트
# 대상: Amazon Linux 2023 + NVIDIA GPU (L40S, H200 등)
#
# 사용법:
#   chmod +x setup-ec2.sh
#   sudo ./setup-ec2.sh
#
# Phase 1: 시스템 + Docker + NVIDIA 드라이버 → 자동 reboot
# Phase 2: Container Toolkit + Compose + Fabric Manager → 완료
# ============================================

SCRIPT_PATH=$(realpath "$0")
PHASE_FILE="/var/tmp/ec2-setup-phase"
LOG_FILE="/var/log/ec2-setup.log"

# 기본 설정 (.env 파일 또는 환경변수로 오버라이드 가능)
USERNAME="${USERNAME:-}"
PASSWORD="${PASSWORD:-}"
VOLUME_PATH="${VOLUME_PATH:-/volume}"
SSH_PORT="${SSH_PORT:-5555}"
CONTAINER_UID="${CONTAINER_UID:-2000}"
CONTAINER_GID="${CONTAINER_GID:-2000}"
MODE="${MODE:-dev}"

# EBS 볼륨 디바이스 경로 (lsblk로 확인 후 설정)
VOLUME_DEVICE="${VOLUME_DEVICE:-}"         # 예: /dev/nvme1n1
CUDA_TEST_IMAGE="${CUDA_TEST_IMAGE:-nvidia/cuda:12.8.1-base-ubuntu24.04}"

# ============================================
# 유틸리티 함수
# ============================================
log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg" | tee -a "$LOG_FILE"
}

error_exit() {
    log "❌ 에러: $1"
    exit 1
}

check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        error_exit "root 권한이 필요합니다. sudo ./setup-ec2.sh 으로 실행하세요."
    fi
}

# EBS 볼륨을 포맷 + 마운트 + fstab 등록 (디바이스 미지정 시 mount_point 디렉토리만 생성)
mount_ebs_volume() {
    local device="$1"
    local mount_point="$2"

    # VOLUME_DEVICE 미설정 → 루트 디스크에 디렉토리만 생성 (운영계 폴백)
    # — 추가 EBS 없이 루트 디스크만으로 동작하는 케이스. /volume이 일반 디렉토리가 됨.
    # — 운영계 전제: 모델/데이터는 S3에서 재동기화하므로 인스턴스 종료 시 손실 허용.
    # — 영속 데이터가 필요한 환경(개발 EC2 등)에서는 .env에 추가 EBS 디바이스 명시 권장.
    if [ -z "$device" ]; then
        log "  ℹ️  VOLUME_DEVICE 미설정 → 루트 디스크에 ${mount_point} 디렉토리만 생성 (mkfs/mount/fstab 건너뜀)"
        log "  ⚠️  인스턴스 종료(terminate) 시 ${mount_point} 데이터도 함께 삭제됩니다. 영속 데이터는 S3 백업 필수."
        mkdir -p "$mount_point"
        return
    fi

    if [ ! -b "$device" ]; then
        error_exit "${device} 블록 디바이스가 존재하지 않습니다. lsblk 확인 후 .env 수정 필요."
    fi

    # device 자체 + 자식 파티션의 모든 마운트포인트 검사 (mount_point 외에 하나라도 있으면 거부)
    # — findmnt -S 만으로는 "디스크 전체 경로(/dev/nvme0n1)" 입력을 못 잡음:
    #   디바이스 자체에 마운트가 없고 자식(/dev/nvme0n1p1)이 / 에 붙어 있으면 검사 통과 → mkfs로 시스템 파괴
    # — lsblk -no MOUNTPOINTS는 디바이스 + 자식 파티션의 마운트포인트를 줄별로 출력 (디스크 전체 케이스도 포착)
    local existing_mounts
    existing_mounts=$(lsblk -no MOUNTPOINTS "$device" 2>/dev/null | grep -v '^$' | grep -v "^${mount_point}$" || true)
    if [ -n "$existing_mounts" ]; then
        error_exit "${device} 또는 자식 파티션이 다음 위치에 이미 마운트되어 있습니다 (루트/시스템 디스크 가능성):
$(echo "$existing_mounts" | sed 's/^/    /')
lsblk로 확인 후 추가 EBS 디바이스(예: /dev/nvme1n1)만 지정하세요."
    fi

    mkdir -p "$mount_point"

    # 이미 mount_point에 마운트되어 있으면 건너뜀 (재실행 시)
    if mountpoint -q "$mount_point" 2>/dev/null; then
        log "  ${mount_point}: 이미 마운트됨. 건너뜀."
        return
    fi

    # 파일시스템 확인 → 없으면 xfs로 포맷
    local fs_type
    fs_type=$(blkid -o value -s TYPE "$device" 2>/dev/null || true)
    if [ -z "$fs_type" ]; then
        # mkfs 직전 가드: 디스크 자체에는 fs가 없어도 자식 파티션이 데이터를 보유 중일 수 있음.
        # — 예: 기존 데이터 EBS가 /dev/nvme1n1p1 형태인데 .env에 /dev/nvme1n1을 지정 →
        #   blkid TYPE는 비어있고(디스크 본체에 fs 없음) 자식이 미마운트면 위 마운트 검사도 통과 →
        #   mkfs로 디스크 전체 포맷 시 nvme1n1p1의 데이터 전부 파괴.
        # — device가 disk(전체)일 때만 자식 파티션 검사. 파티션 경로(/dev/nvme1n1p1)를 직접 지정한
        #   경우 lsblk가 자기 자신을 part로 출력하여 오탐 → 미포맷 파티션 신규 사용 케이스가 막힘.
        local device_type
        device_type=$(lsblk -ndo TYPE "$device" 2>/dev/null || true)
        if [ "$device_type" = "disk" ]; then
            local child_parts
            child_parts=$(lsblk -nro NAME,TYPE "$device" 2>/dev/null | awk '$2 == "part" {print $1}')
            if [ -n "$child_parts" ]; then
                local first_part
                first_part=$(echo "$child_parts" | head -1)
                error_exit "${device}에 기존 파티션이 존재합니다:
$(echo "$child_parts" | sed 's/^/    /')
디스크 전체 포맷은 자식 파티션의 데이터를 파괴합니다. 파티션 경로를 직접 지정하거나(예: /dev/${first_part}) 새 EBS를 사용하세요."
            fi
        fi
        log "  ${device} → xfs 포맷 중..."
        mkfs -t xfs -f "$device"
    else
        log "  ${device}: 기존 파일시스템 ${fs_type} 감지. 포맷 건너뜀."
    fi

    # 마운트
    mount "$device" "$mount_point"
    log "  ${device} → ${mount_point} 마운트 완료"

    # fstab 등록 (중복 방지)
    local uuid
    uuid=$(blkid -o value -s UUID "$device" 2>/dev/null || true)
    if [ -z "$uuid" ]; then
        log "  ⚠️ ${device}의 UUID를 읽을 수 없습니다. fstab 등록 건너뜀."
        return
    fi
    if ! grep -q "UUID=${uuid}" /etc/fstab; then
        cp /etc/fstab /etc/fstab.bak
        local fstab_type
        fstab_type=$(blkid -o value -s TYPE "$device" 2>/dev/null || echo "xfs")
        echo "UUID=${uuid} ${mount_point} ${fstab_type} defaults,nofail 0 2" >> /etc/fstab
        log "  fstab 등록 완료 (UUID=${uuid})"
    else
        log "  fstab에 이미 등록됨. 건너뜀."
    fi
}

# ============================================
# Phase 1: 시스템 + Docker + NVIDIA 드라이버
# ============================================
phase1() {
    log "========== Phase 1 시작 =========="

    # --- 사용자 생성 ---
    if [ -n "$USERNAME" ]; then
        log "[1/9] 사용자 생성: $USERNAME"
        if [ "$USERNAME" = "root" ]; then
            # USERNAME=root (운영계): 호스트 root는 이미 존재(UID=0)하고 변경 불가.
            # .env CONTAINER_UID는 컨테이너 내부의 공유 UID 정책으로만 사용되므로
            # 호스트 root와 일치 검증을 하면 prd 기본값(CONTAINER_UID=2000)에서 즉시 실패.
            # → 호스트 사용자 생성/검증 단계는 통째로 스킵.
            log "  USERNAME=root (운영계). 호스트 root는 이미 존재. 사용자 생성/검증 건너뜀."
        elif id "$USERNAME" &>/dev/null; then
            # 기존 사용자가 있으면 .env CONTAINER_UID/GID와 일치하는지 검증
            # — 호스트 사용자 UID와 컨테이너 UID가 다르면 EBS 디렉토리 chown은 호스트 UID로 되는데
            #   컨테이너는 CONTAINER_UID로 동작 → /workspace, /home 쓰기 실패
            local existing_uid existing_gid
            existing_uid=$(id -u "$USERNAME")
            existing_gid=$(id -g "$USERNAME")
            if [ "$existing_uid" != "$CONTAINER_UID" ]; then
                error_exit "사용자 ${USERNAME}의 UID(${existing_uid})가 .env CONTAINER_UID(${CONTAINER_UID})와 다릅니다. .env 값을 ${existing_uid}로 맞추거나 사용자를 재생성하세요."
            fi
            if [ "$existing_gid" != "$CONTAINER_GID" ]; then
                error_exit "사용자 ${USERNAME}의 GID(${existing_gid})가 .env CONTAINER_GID(${CONTAINER_GID})와 다릅니다. .env 값을 ${existing_gid}로 맞추거나 사용자를 재생성하세요."
            fi
            log "  사용자 $USERNAME 이미 존재 (UID=${existing_uid}, GID=${existing_gid}). 건너뜀."
        else
            # UID/GID 충돌 시 fail-fast
            # (자동 변경은 /tmp /var/log 등 다른 위치의 기존 사용자 파일 소유권 어긋남 위험 → 명시적 중단)
            local existing_uid_user existing_gid_group
            existing_uid_user=$(getent passwd "$CONTAINER_UID" | cut -d: -f1 || true)
            if [ -n "$existing_uid_user" ] && [ "$existing_uid_user" != "$USERNAME" ]; then
                error_exit "UID ${CONTAINER_UID}이(가) ${existing_uid_user}에 의해 점유됨. .env의 CONTAINER_UID를 다른 값(예: 2000)으로 변경하세요."
            fi
            existing_gid_group=$(getent group "$CONTAINER_GID" | cut -d: -f1 || true)
            if [ -n "$existing_gid_group" ] && [ "$existing_gid_group" != "$USERNAME" ]; then
                error_exit "GID ${CONTAINER_GID}이(가) ${existing_gid_group}에 의해 점유됨. .env의 CONTAINER_GID를 다른 값(예: 2000)으로 변경하세요."
            fi
            groupadd -g "$CONTAINER_GID" "$USERNAME" 2>/dev/null || true
            useradd -m -s /bin/bash -u "$CONTAINER_UID" -g "$CONTAINER_GID" "$USERNAME"
            if [ -n "$PASSWORD" ]; then
                echo "${USERNAME}:${PASSWORD}" | chpasswd
            fi
            # sudoers.d 방식 (안전)
            echo "${USERNAME} ALL=(ALL:ALL) ALL" > "/etc/sudoers.d/${USERNAME}"
            chmod 0440 "/etc/sudoers.d/${USERNAME}"
            log "  사용자 생성 완료 + sudo 권한 부여"
        fi
    else
        log "[1/9] USERNAME 미설정. 사용자 생성 건너뜀."
    fi

    # --- SSH 설정 + fail2ban ---
    log "[2/9] SSH 설정 + fail2ban (포트: ${SSH_PORT})"
    sed -i "s/^#\?Port .*/Port ${SSH_PORT}/" /etc/ssh/sshd_config
    grep -q "^Port ${SSH_PORT}" /etc/ssh/sshd_config || echo "Port ${SSH_PORT}" >> /etc/ssh/sshd_config
    sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
    grep -q "^PasswordAuthentication yes" /etc/ssh/sshd_config || echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config
    sed -i 's/^#\?KbdInteractiveAuthentication.*/KbdInteractiveAuthentication yes/' /etc/ssh/sshd_config
    sed -i 's/^#\?MaxAuthTries.*/MaxAuthTries 5/' /etc/ssh/sshd_config
    grep -q "^MaxAuthTries" /etc/ssh/sshd_config || echo "MaxAuthTries 5" >> /etc/ssh/sshd_config
    # cloud-init이 SSH 설정을 덮어쓰지 않도록 드롭인 파일 정리
    rm -f /etc/ssh/sshd_config.d/50-cloud-init.conf 2>/dev/null || true
    systemctl restart sshd

    # fail2ban 설치 + SSH jail 설정
    if dnf install -y fail2ban 2>/dev/null; then
        cat > /etc/fail2ban/jail.local <<JAIL
[sshd]
enabled = true
port = ${SSH_PORT}
maxretry = 5
bantime = 3600
findtime = 600
JAIL
        systemctl enable fail2ban
        systemctl start fail2ban
        log "  fail2ban 활성화 완료"
    else
        log "  ⚠️ fail2ban 설치 실패. AL2023.6 이상에서 dnf install -y fail2ban 으로 수동 설치하세요."
    fi
    log "  SSH 포트 ${SSH_PORT}, 비밀번호 인증 활성화 완료"

    # --- EBS 볼륨 마운트 (또는 /volume 디렉토리 생성) ---
    log "[3/9] EBS 볼륨 마운트 (또는 ${VOLUME_PATH} 디렉토리 생성)"
    if [ -n "$VOLUME_DEVICE" ]; then
        log "  사용 가능한 블록 디바이스:"
        lsblk -o NAME,SIZE,TYPE,MOUNTPOINT | tee -a "$LOG_FILE"
    fi
    mount_ebs_volume "$VOLUME_DEVICE" "$VOLUME_PATH"

    # --- 작업/데이터 디렉토리 설정 ---
    log "[4/9] 작업/데이터 디렉토리 설정"
    # /volume 자체는 root:root + 0775로 통일
    # - 컨테이너는 /volume을 직접 마운트하지 않음 (/workspace, /data, /models, /home로만 접근)
    # - setup-ec2.sh, user.sh는 sudo 전제 → root 소유여도 mkdir 가능
    # - USERNAME 값에 의존하지 않으므로 운영(root) ↔ 개발(user) 모드 전환 시 일관성 유지
    chown root:root "$VOLUME_PATH"
    chmod 0775 "$VOLUME_PATH"

    # 표준 하위 디렉토리 일괄 생성
    # - root-homes는 user.sh --root 컨테이너용. 첫 호출 시 mkdir 멱등이지만 미리 만들어 일관성 ↑
    mkdir -p \
        "${VOLUME_PATH}/workspace" \
        "${VOLUME_PATH}/data" \
        "${VOLUME_PATH}/models" \
        "${VOLUME_PATH}/homes" \
        "${VOLUME_PATH}/root-homes"

    # /models, /data는 모든 컨테이너 공유 → CONTAINER_UID 소유로 통일
    # (일반 사용자 컨테이너는 CONTAINER_UID로 동작, root 컨테이너는 권한 0이라 어차피 모두 쓰기 가능)
    chown "$CONTAINER_UID":"$CONTAINER_GID" "${VOLUME_PATH}/data" "${VOLUME_PATH}/models"

    # 사용자별 디렉토리는 호스트 사용자 소유로 (컨테이너 UID와 동일하면 권한 일치)
    # - USERNAME=root: /volume/root는 compose 마운트가 첫 기동 시 자동 생성 → 별도 작업 불필요
    # - 일반 사용자: workspace/<user>, homes/<user> 미리 생성 + chown
    if [ -n "$USERNAME" ] && [ "$USERNAME" != "root" ]; then
        mkdir -p "${VOLUME_PATH}/workspace/${USERNAME}" "${VOLUME_PATH}/homes/${USERNAME}"
        chown -R "$USERNAME":"$USERNAME" \
            "${VOLUME_PATH}/workspace/${USERNAME}" \
            "${VOLUME_PATH}/homes/${USERNAME}"
        log "  ${VOLUME_PATH}/{workspace,homes}/${USERNAME} + {data,models} 생성/소유권 설정 완료"
    elif [ "$USERNAME" = "root" ]; then
        log "  ${VOLUME_PATH}/{data,models,root-homes} 생성/소유권 설정 완료 (root 모드)"
    else
        log "  ${VOLUME_PATH}/{data,models,root-homes} 생성/소유권 설정 완료 (USERNAME 미설정)"
    fi

    # --- 시스템 업데이트 + 커널 패키지 ---
    log "[5/9] 시스템 업데이트 + 커널 패키지 설치"
    dnf update -y --exclude='kernel*'
    dnf install -y \
        dnf-plugins-core curl wget git jq htop tmux \
        gcc dkms python3-pip --allowerasing

    # nvitop (호스트에서 GPU 실시간 모니터링 — htop의 GPU 버전, Phase 2 완료 후 동작)
    # — AL2023은 PEP 668(외부 관리 환경) 정책으로 시스템 Python에 직접 pip install이 차단됨.
    #   호스트 운영자용 단일 CLI라 시스템 site-packages 충돌 위험이 낮으므로 --break-system-packages로 우회.
    # — pip3가 아주 구버전이라 해당 플래그를 모르면 plain pip3 install로 폴백 (현재 dnf python3-pip는 충분히 신버전).
    if command -v nvitop &>/dev/null; then
        log "  nvitop 이미 설치됨. 건너뜀."
    elif pip3 install --break-system-packages nvitop 2>/dev/null \
        || pip3 install nvitop 2>/dev/null; then
        log "  nvitop 설치 완료 (호스트에서 nvitop 실행 → GPU 실시간 모니터링)"
    else
        log "  ⚠️ nvitop 설치 실패. 수동 설치: pip3 install --break-system-packages nvitop"
    fi

    # AL2023 커널 패키지명 자동 감지 (6.1: kernel-devel, 6.12+: kernel6.12-devel)
    local kver kpkg
    kver=$(uname -r)
    case "$kver" in
        6.1.*) kpkg="kernel" ;;
        *)     kpkg="kernel$(echo "$kver" | cut -d. -f1,2)" ;;
    esac
    log "  커널 패키지 접두사: ${kpkg} (커널: ${kver})"
    dnf install -y "${kpkg}-devel-${kver}" "${kpkg}-headers-${kver}" --allowerasing
    dnf install -y "${kpkg}-modules-extra-${kver}" 2>/dev/null || true
    dnf install -y "${kpkg}-modules-extra-common-${kver}" 2>/dev/null || true

    # --- Docker 설치 ---
    log "[6/9] Docker 설치"
    if command -v docker &>/dev/null; then
        log "  Docker 이미 설치됨. 건너뜀."
    else
        dnf install -y docker
        systemctl start docker
        systemctl enable docker
    fi
    # 기본 사용자들을 docker 그룹에 추가
    for u in ec2-user ssm-user ${USERNAME:-}; do
        if id "$u" &>/dev/null; then
            usermod -aG docker "$u" 2>/dev/null || true
        fi
    done
    log "  Docker 설치 완료"

    # --- Docker Compose V2 + Buildx 플러그인 ---
    log "[7/9] Docker Compose V2 + Buildx 설치"
    mkdir -p /usr/libexec/docker/cli-plugins
    if docker compose version &>/dev/null; then
        log "  Docker Compose 이미 설치됨. 건너뜀."
    else
        curl -fsSL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" \
            -o /usr/libexec/docker/cli-plugins/docker-compose
        chmod +x /usr/libexec/docker/cli-plugins/docker-compose
        log "  Docker Compose $(docker compose version --short) 설치 완료"
    fi
    # Buildx는 단순 존재 여부가 아니라 최소 버전(>= 0.17.0)까지 검사한다.
    # 사유: AL2023의 dnf docker 패키지는 구버전 buildx(< 0.17.0)를 함께 설치하는데,
    # 최신 docker compose v2.27+ 는 buildx 0.17.0+ 를 요구하므로 빌드가 실패한다.
    local buildx_required="0.17.0"
    local buildx_target="0.21.2"
    local buildx_install="true"
    if docker buildx version &>/dev/null; then
        local buildx_current
        buildx_current=$(docker buildx version 2>/dev/null | grep -oE 'v?[0-9]+\.[0-9]+\.[0-9]+' | head -1 | tr -d 'v')
        if [ -n "$buildx_current" ] \
            && [ "$(printf '%s\n%s\n' "$buildx_current" "$buildx_required" | sort -V | head -1)" = "$buildx_required" ]; then
            log "  Docker Buildx v${buildx_current} (>= ${buildx_required}) 이미 설치됨. 건너뜀."
            buildx_install="false"
        else
            log "  Docker Buildx v${buildx_current:-?} 감지 — Compose가 요구하는 ${buildx_required} 미만. v${buildx_target}로 재설치."
        fi
    fi
    if [ "$buildx_install" = "true" ]; then
        local buildx_arch="amd64"
        [ "$(uname -m)" = "aarch64" ] && buildx_arch="arm64"
        curl -fsSL "https://github.com/docker/buildx/releases/download/v${buildx_target}/buildx-v${buildx_target}.linux-${buildx_arch}" \
            -o /usr/libexec/docker/cli-plugins/docker-buildx
        chmod +x /usr/libexec/docker/cli-plugins/docker-buildx
        log "  Docker Buildx $(docker buildx version 2>/dev/null | head -1 || echo 'installed') 설치 완료"
    fi

    # --- Claude Code (dev 전용 호스트 도구) ---
    log "[8/9] Claude Code 설치"
    if [ "$MODE" != "dev" ]; then
        log "  MODE=${MODE}: 운영 모드 → Claude Code 호스트 설치 건너뜀."
    elif [ -n "$USERNAME" ]; then
        if [ -f "/home/${USERNAME}/.local/bin/claude" ]; then
            log "  Claude Code 이미 설치됨. 건너뜀."
        else
            if su - "$USERNAME" -c "curl -fsSL https://claude.ai/install.sh | bash" 2>/dev/null; then
                log "  Claude Code 설치 완료"
            else
                log "  ⚠️ Claude Code 설치 실패. 수동 설치: curl -fsSL https://claude.ai/install.sh | bash"
            fi
        fi
    else
        log "  USERNAME 미설정. 건너뜀."
    fi

    # --- NVIDIA 드라이버 ---
    log "[9/9] NVIDIA 드라이버 설치"
    if nvidia-smi &>/dev/null; then
        log "  NVIDIA 드라이버 이미 설치됨. 건너뜀."
        echo "2" > "$PHASE_FILE"
        log "========== Phase 1 완료 (reboot 불필요) =========="
        phase2
        return
    fi

    # NVIDIA repo 추가 + 드라이버 설치
    dnf config-manager --add-repo \
        https://developer.download.nvidia.com/compute/cuda/repos/amzn2023/x86_64/cuda-amzn2023.repo 2>/dev/null || true
    dnf clean expire-cache
    # CUDA repo의 모듈 스트림 활성화 후 오픈소스 드라이버 설치
    dnf module enable -y nvidia-driver:open-dkms 2>/dev/null || true
    dnf install -y nvidia-open

    # Phase 2 자동 실행을 위한 systemd 서비스 등록
    echo "2" > "$PHASE_FILE"
    register_phase2_service

    log "========== Phase 1 완료. 10초 후 reboot =========="
    log "  reboot 후 Phase 2가 자동 실행됩니다."
    log "  진행 상황: tail -f $LOG_FILE"
    sleep 10
    reboot
}

# ============================================
# Phase 2: Container Toolkit + Fabric Manager
# ============================================
phase2() {
    # Phase 2 종료 시 (성공/실패 무관) systemd 서비스 + phase 파일 정리 (리부트 루프 방지).
    # EXIT trap 사용 이유: ERR trap은 if-조건 실패/||-체인/exit N 일부 케이스에서 미발동 가능 →
    # 정리가 누락되면 phase 파일이 남아 재부팅 시 phase2 재실행 루프 위험. EXIT은 정상 종료/exit/
    # signal 모두 커버. 정상 종료 시는 명시 정리 후 trap을 해제해 완료 메시지 순서를 유지.
    trap 'cleanup_phase2_service; rm -f "$PHASE_FILE"' EXIT

    log "========== Phase 2 시작 =========="

    # --- NVIDIA 드라이버 확인 ---
    log "[1/4] NVIDIA 드라이버 확인"
    if nvidia-smi &>/dev/null; then
        nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader | while read -r line; do
            log "  GPU: $line"
        done
    else
        error_exit "NVIDIA 드라이버가 로드되지 않았습니다. dmesg | grep -i nvidia 확인 필요"
    fi

    # --- NVIDIA Container Toolkit ---
    log "[2/4] NVIDIA Container Toolkit 설치"
    if ! command -v nvidia-ctk &>/dev/null; then
        curl -fsSL https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | \
            tee /etc/yum.repos.d/nvidia-container-toolkit.repo
        dnf clean expire-cache
        dnf install -y nvidia-container-toolkit
        log "  Container Toolkit 설치 완료"
    else
        log "  Container Toolkit 이미 설치됨."
    fi
    # runtime configure는 멱등 명령이라 매번 실행
    # — 이미 설치돼 있어도 docker daemon에 nvidia runtime 등록이 빠진 케이스 보장
    nvidia-ctk runtime configure --runtime=docker
    systemctl restart docker

    # --- Fabric Manager (NVSwitch GPU 자동 감지) ---
    log "[3/4] Fabric Manager 확인"
    local needs_fm=false
    if nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | grep -qiE "H100|H200|A100|B100|B200"; then
        needs_fm=true
    fi

    if [ "$needs_fm" = true ]; then
        log "  NVSwitch GPU 감지 → Fabric Manager 설치"
        local driver_version
        driver_version=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | tr -d ' ')

        # CUDA repo 추가 (Fabric Manager 패키지용 — Phase 1과 동일한 amzn2023 repo 사용)
        dnf config-manager --add-repo \
            https://developer.download.nvidia.com/compute/cuda/repos/amzn2023/x86_64/cuda-amzn2023.repo 2>/dev/null || true
        dnf clean expire-cache

        # AL2023는 모듈 프로파일(/fm) 방식이 공식 가이드
        # 현재 드라이버 브랜치에 맞는 open 스트림을 우선 시도 → 실패 시 open-dkms 폴백
        local driver_branch
        driver_branch="${driver_version%%.*}-open"
        if dnf module install -y "nvidia-driver:${driver_branch}/fm" --allowerasing 2>/dev/null \
            || dnf module install -y "nvidia-driver:open-dkms/fm" --allowerasing 2>/dev/null; then
            systemctl enable nvidia-fabricmanager
            systemctl start nvidia-fabricmanager
            log "  Fabric Manager 설치 + 시작 완료 (driver=${driver_version})"
        else
            log "  ⚠️ Fabric Manager 자동 설치 실패. 수동 설치 필요:"
            log "     dnf module install -y nvidia-driver:${driver_branch}/fm --allowerasing"
        fi
    else
        log "  NVSwitch GPU 미감지 (L40S 등). Fabric Manager 불필요."
    fi

    # --- Docker GPU 테스트 ---
    # GPU Docker 환경 구축이 본 스크립트의 목적이므로 실패 시 fail-fast
    # (성공 메시지로 넘어가면 사용자가 정상 종료로 오해 → 실제로는 컨테이너에서 GPU 못 봄)
    log "[4/4] Docker GPU 연동 테스트"
    if docker run --rm --gpus all "$CUDA_TEST_IMAGE" nvidia-smi &>/dev/null; then
        log "  ✅ Docker GPU 연동 정상"
    else
        error_exit "Docker GPU 테스트 실패. nvidia-container-toolkit 또는 docker 데몬 설정 확인 필요. (재시도: systemctl restart docker && docker run --rm --gpus all ${CUDA_TEST_IMAGE} nvidia-smi)"
    fi

    # Phase 2 완료 — 명시 정리 후 EXIT trap 해제 (실패 시는 trap이 자동 정리)
    cleanup_phase2_service
    rm -f "$PHASE_FILE"
    trap - EXIT

    log ""
    log "============================================"
    log "  ✅ EC2 GPU 서버 세팅 완료"
    log "============================================"
    log ""
    log "  NVIDIA Driver : $(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)"
    log "  Docker        : $(docker --version)"
    log "  Compose       : $(docker compose version --short 2>/dev/null || echo 'N/A')"
    log "  GPU           :"
    nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader | while read -r line; do
        log "    $line"
    done
    log ""
    log "  다음 단계:"
    log "    cd $(dirname "$SCRIPT_PATH")"
    log "    docker compose build && docker compose up -d"
    log ""
    log "  로그: $LOG_FILE"
    log "============================================"
}

# ============================================
# systemd 서비스: reboot 후 phase2 자동 실행
# ============================================
register_phase2_service() {
    cat > /etc/systemd/system/ec2-setup-phase2.service <<UNIT
[Unit]
Description=EC2 GPU Setup Phase 2
After=network-online.target docker.service
Wants=network-online.target docker.service

[Service]
Type=oneshot
ExecStart=/bin/bash "${SCRIPT_PATH}" --phase2
RemainAfterExit=no
StandardOutput=journal+console

[Install]
WantedBy=multi-user.target
UNIT
    systemctl daemon-reload
    systemctl enable ec2-setup-phase2.service
    log "  Phase 2 자동 실행 서비스 등록 완료"
}

cleanup_phase2_service() {
    if [ -f /etc/systemd/system/ec2-setup-phase2.service ]; then
        systemctl disable ec2-setup-phase2.service 2>/dev/null || true
        rm -f /etc/systemd/system/ec2-setup-phase2.service
        systemctl daemon-reload
        log "  Phase 2 서비스 정리 완료"
    fi
}

# ============================================
# 메인 실행
# ============================================
main() {
    check_root

    # .env 파일이 있으면 항상 로드 (phase2 자동 실행 시에도 적용)
    if [ -f "$(dirname "$SCRIPT_PATH")/.env" ]; then
        log ".env 파일 로드"
        # Windows 줄 끝(CRLF) 제거
        sed -i 's/\r$//' "$(dirname "$SCRIPT_PATH")/.env"
        set -a
        source "$(dirname "$SCRIPT_PATH")/.env"
        set +a
    fi
    # 온프레미스용 .env(.env.onprem)를 잘못 복사한 경우를 막는다
    if [ "${PLATFORM:-aws}" != "aws" ]; then
        error_exit ".env PLATFORM=${PLATFORM} — EC2는 cp .env.dev .env 또는 cp .env.prd .env 후 실행"
    fi

    case "${1:-}" in
        --phase2)
            phase2
            ;;
        --phase1)
            phase1
            ;;
        *)
            # 자동 판별: phase 파일이 있으면 phase2, 없으면 phase1
            if [ -f "$PHASE_FILE" ] && [ "$(cat "$PHASE_FILE")" = "2" ]; then
                phase2
            else
                phase1
            fi
            ;;
    esac
}

main "$@"
