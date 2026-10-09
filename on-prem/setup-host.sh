#!/bin/bash
set -euo pipefail

# ============================================
# 온프레미스 GPU 서버 초기 세팅 스크립트
# 대상: RHEL 10 + NVIDIA H200 (HGX 8-GPU 또는 PCIe)
#
# aws/setup-ec2.sh(Amazon Linux 2023)를 RHEL 10 기준으로 옮긴 것이다. 두 스크립트의
# Phase 구조·디렉토리 정책·안전 가드는 같고, 다음만 다르다:
#   - 저장소: NVIDIA rhel10 repo(모듈 스트림 없음) + Docker CE 공식 repo (AL2023 dnf docker 아님)
#   - 드라이버 버전 고정: .env NVIDIA_DRIVER_VERSION + dnf versionlock
#     (RHEL 10 repo는 브랜치 스트림이 없어 `dnf update`가 최신 브랜치(610 등)로 올려버린다)
#   - EBS/cloud-init/ssm-user 없음. 데이터 디스크는 VOLUME_DEVICE로 동일하게 처리
#   - 폐쇄망 대비: 셋업 시점에 베이스 이미지를 미리 pull (세팅 후 네트워크가 끊길 수 있다)
#   - RHEL 고유: 구독 확인, firewalld 포트 개방, SELinux 라벨
#
# 사용법:
#   chmod +x setup-host.sh
#   sudo ./setup-host.sh
#
# Phase 1: 시스템 + Docker + NVIDIA 드라이버 → 자동 reboot
# Phase 2: Container Toolkit + Fabric Manager + 이미지 pull → 완료
# ============================================

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
PHASE_FILE="/var/tmp/onprem-setup-phase"
LOG_FILE="/var/log/onprem-setup.log"

# .env는 ../aws/.env 하나만 쓴다. docker-compose.yml과 user.sh가 그 경로를 읽으므로
# 여기서 별도 .env를 두면 USERNAME·VOLUME_PATH·포트가 두 벌로 갈라진다.
ENV_FILE="${SCRIPT_DIR}/../aws/.env"

# 기본 설정 (.env 파일 또는 환경변수로 오버라이드 가능)
USERNAME="${USERNAME:-}"
PASSWORD="${PASSWORD:-}"
VOLUME_PATH="${VOLUME_PATH:-/volume}"
SSH_PORT="${SSH_PORT:-5555}"
CONTAINER_UID="${CONTAINER_UID:-2000}"
CONTAINER_GID="${CONTAINER_GID:-2000}"
MODE="${MODE:-prd}"

# 데이터 디스크 디바이스 경로 (lsblk로 확인 후 설정, 비우면 루트 디스크에 디렉토리만)
VOLUME_DEVICE="${VOLUME_DEVICE:-}"         # 예: /dev/nvme1n1
CUDA_TEST_IMAGE="${CUDA_TEST_IMAGE:-nvidia/cuda:12.8.1-base-ubuntu24.04}"
VLLM_IMAGE="${VLLM_IMAGE:-}"

# NVIDIA 버전 고정값. 브랜치 선택 근거는 SETUP_GUIDE.md §1 참조.
NVIDIA_DRIVER_VERSION="${NVIDIA_DRIVER_VERSION:-580.178.04}"
NVIDIA_CONTAINER_TOOLKIT_VERSION="${NVIDIA_CONTAINER_TOOLKIT_VERSION:-1.20.0-1}"

# 컨테이너 포트 정책 (aws/user.sh: compose 5000-5009, user.sh 5010-5499). firewalld 개방 범위.
CONTAINER_PORT_RANGE="${CONTAINER_PORT_RANGE:-5000-5499}"

NVIDIA_REPO_URL="https://developer.download.nvidia.com/compute/cuda/repos/rhel10/x86_64/cuda-rhel10.repo"
DOCKER_REPO_URL="https://download.docker.com/linux/rhel/docker-ce.repo"
EPEL_RPM_URL="https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm"
NCT_REPO_URL="https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo"

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
        error_exit "root 권한이 필요합니다. sudo ./setup-host.sh 으로 실행하세요."
    fi
}

# RHEL 확인. 다른 배포판이면 저장소 URL·패키지명이 전부 어긋나므로 시작 전에 막는다.
check_os() {
    local id ver
    id=$(. /etc/os-release && echo "${ID:-}")
    ver=$(. /etc/os-release && echo "${VERSION_ID:-}")
    if [ "$id" != "rhel" ]; then
        error_exit "RHEL 전용 스크립트입니다 (감지: ${id:-?} ${ver:-?}). Rocky/Alma는 NVIDIA repo 경로가 같아 동작할 수 있으나 검증하지 않았습니다."
    fi
    if [ "${ver%%.*}" != "10" ]; then
        error_exit "RHEL 10 전용입니다 (감지: ${ver}). RHEL 9는 nvidia-driver 모듈 스트림 방식이라 드라이버 설치 절차가 다릅니다."
    fi
    log "  OS: RHEL ${ver}"
}

# RHEL 구독이 없으면 BaseOS/AppStream이 비어 kernel-devel·gcc 설치부터 실패한다.
# 하드웨어 설치팀 인계 항목이라 여기서는 확인만 하고 등록은 하지 않는다.
check_subscription() {
    if ! dnf repolist --enabled 2>/dev/null | grep -qiE "baseos"; then
        error_exit "RHEL BaseOS 저장소가 활성화되지 않았습니다. 구독 등록 필요: subscription-manager register --auto-attach"
    fi
    log "  RHEL 구독 저장소 확인 (BaseOS 활성)"
}

# 데이터 디스크를 포맷 + 마운트 + fstab 등록 (디바이스 미지정 시 mount_point 디렉토리만 생성)
mount_data_volume() {
    local device="$1"
    local mount_point="$2"

    # VOLUME_DEVICE 미설정 → 루트 디스크에 디렉토리만 생성
    # — 온프레미스는 보통 모델용 NVMe를 따로 붙이므로 설치팀에 디바이스 경로를 받아 .env에 적는 것이 기본.
    #   비워두면 OS 디스크에 모델(수십~수백 GB)이 쌓여 루트가 차는 사고가 난다.
    if [ -z "$device" ]; then
        log "  ℹ️  VOLUME_DEVICE 미설정 → 루트 디스크에 ${mount_point} 디렉토리만 생성 (mkfs/mount/fstab 건너뜀)"
        log "  ⚠️  모델 저장소가 OS 디스크에 놓입니다. 별도 NVMe가 있으면 lsblk로 확인해 .env VOLUME_DEVICE에 지정하세요."
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
lsblk로 확인 후 데이터 디스크(예: /dev/nvme1n1)만 지정하세요."
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
        # — 예: 기존 데이터 디스크가 /dev/nvme1n1p1 형태인데 .env에 /dev/nvme1n1을 지정 →
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
디스크 전체 포맷은 자식 파티션의 데이터를 파괴합니다. 파티션 경로를 직접 지정하거나(예: /dev/${first_part}) 빈 디스크를 사용하세요."
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

# 작업 사본 배치: 컨테이너가 /workspace로 마운트하는 ${VOLUME_PATH}/workspace/root 아래에
# 이 레포를 둔다. 그래야 컨테이너 안에서 /workspace/ai-infra/llm-serving 경로가 연구계와 같아진다.
# — 이 스크립트가 이미 그 안에서 실행 중이면(최초부터 거기 clone) 아무것도 하지 않는다.
# — 밖(예: ~/ai-infra 부트스트랩 사본)에서 실행 중이면 같은 origin으로 clone하고 .env를 옮긴다.
#   데이터 디스크를 /volume에 마운트한 뒤에 clone해야 하므로 mount_data_volume 이후에 호출한다.
place_working_copy() {
    local repo_root target
    repo_root=$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)
    if [ -z "$repo_root" ]; then
        log "  ⚠️ 이 스크립트가 git 저장소 안에 없습니다. 작업 사본 배치 건너뜀 — SETUP_GUIDE.md §3-2 (4)의 작업 사본(clone + .env 복사)을 수동으로 배치하세요."
        return
    fi
    target="${VOLUME_PATH}/workspace/root/ai-infra"

    if [ "$repo_root" = "$(realpath "$target" 2>/dev/null || true)" ]; then
        log "  작업 사본이 이미 ${target}에 있음 (현재 실행 위치). 건너뜀."
        return
    fi
    if [ -d "$target/.git" ]; then
        log "  ${target}에 기존 작업 사본 존재. 건너뜀 (갱신은 그 안에서 on-prem/start.sh pull)."
        return
    fi

    local origin
    origin=$(git -C "$repo_root" remote get-url origin 2>/dev/null || true)
    if [ -z "$origin" ]; then
        log "  ⚠️ origin 원격이 없어 clone 불가. ${target}에 수동으로 배치하세요."
        return
    fi
    mkdir -p "$(dirname "$target")"
    log "  ${origin} → ${target} clone 중..."
    git clone --quiet "$origin" "$target"
    # 부트스트랩 사본의 .env를 작업 사본으로 옮긴다 (.env는 git 추적 밖이라 clone에 안 실려온다).
    if [ -f "$ENV_FILE" ]; then
        cp "$ENV_FILE" "$target/aws/.env"
        log "  .env → ${target}/aws/.env 복사"
    fi
    chmod +x "$target"/aws/*.sh "$target"/on-prem/*.sh 2>/dev/null || true
    log "  작업 사본 배치 완료. 이후 명령은 ${target}/aws 에서 실행"
    log "  vLLM은 베이스 이미지(v0.31.0) 정식 빌드를 쓴다 — 따로 전달할 휠 없음 (SETUP_GUIDE.md §3-2 (5))"
}

# ============================================
# Phase 1: 시스템 + Docker + NVIDIA 드라이버
# ============================================
phase1() {
    log "========== Phase 1 시작 =========="

    log "[0/10] 환경 확인"
    check_os
    check_subscription

    # --- 사용자 생성 ---
    if [ -n "$USERNAME" ]; then
        log "[1/10] 사용자 생성: $USERNAME"
        if [ "$USERNAME" = "root" ]; then
            # USERNAME=root (운영계): 호스트 root는 이미 존재(UID=0)하고 변경 불가.
            # .env CONTAINER_UID는 컨테이너 내부의 공유 UID 정책으로만 사용되므로
            # 호스트 root와 일치 검증을 하면 prd 기본값(CONTAINER_UID=2000)에서 즉시 실패.
            # → 호스트 사용자 생성/검증 단계는 통째로 스킵.
            log "  USERNAME=root (운영계). 호스트 root는 이미 존재. 사용자 생성/검증 건너뜀."
        elif id "$USERNAME" &>/dev/null; then
            # 기존 사용자가 있으면 .env CONTAINER_UID/GID와 일치하는지 검증
            # — 호스트 사용자 UID와 컨테이너 UID가 다르면 데이터 디렉토리 chown은 호스트 UID로 되는데
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
        log "[1/10] USERNAME 미설정. 사용자 생성 건너뜀."
    fi

    # --- SSH 설정 + fail2ban + firewalld ---
    log "[2/10] SSH 설정 + fail2ban + firewalld (포트: ${SSH_PORT})"
    sed -i "s/^#\?Port .*/Port ${SSH_PORT}/" /etc/ssh/sshd_config
    grep -q "^Port ${SSH_PORT}" /etc/ssh/sshd_config || echo "Port ${SSH_PORT}" >> /etc/ssh/sshd_config
    sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
    grep -q "^PasswordAuthentication yes" /etc/ssh/sshd_config || echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config
    sed -i 's/^#\?KbdInteractiveAuthentication.*/KbdInteractiveAuthentication yes/' /etc/ssh/sshd_config
    sed -i 's/^#\?MaxAuthTries.*/MaxAuthTries 5/' /etc/ssh/sshd_config
    grep -q "^MaxAuthTries" /etc/ssh/sshd_config || echo "MaxAuthTries 5" >> /etc/ssh/sshd_config

    # SELinux: sshd는 22 외 포트에 바인딩하려면 ssh_port_t 라벨이 필요하다. 빠뜨리면
    # sshd 재시작이 "Permission denied"로 죽고 원격 접속이 끊긴다 (콘솔 없으면 복구 불가).
    if command -v getenforce &>/dev/null && [ "$(getenforce)" != "Disabled" ]; then
        dnf install -y policycoreutils-python-utils
        semanage port -a -t ssh_port_t -p tcp "$SSH_PORT" 2>/dev/null \
            || semanage port -m -t ssh_port_t -p tcp "$SSH_PORT" 2>/dev/null || true
        log "  SELinux ssh_port_t에 ${SSH_PORT} 등록"
    fi

    # firewalld: RHEL 기본 활성. 개방하지 않으면 SSH_PORT와 컨테이너 포트가 외부에서 안 보인다.
    # Docker 자체는 firewalld의 docker zone에 스스로 등록하지만, 호스트 SSH 포트는 수동이다.
    if systemctl is-active --quiet firewalld; then
        firewall-cmd --permanent --add-port="${SSH_PORT}/tcp" >/dev/null
        firewall-cmd --permanent --add-port="${CONTAINER_PORT_RANGE}/tcp" >/dev/null
        firewall-cmd --reload >/dev/null
        log "  firewalld 개방: ${SSH_PORT}/tcp, ${CONTAINER_PORT_RANGE}/tcp"
    else
        log "  firewalld 비활성. 포트 개방 건너뜀."
    fi
    systemctl restart sshd

    # fail2ban은 EPEL 패키지라 저장소를 먼저 등록한다 (dkms도 EPEL이라 어차피 필요).
    if ! rpm -q epel-release &>/dev/null; then
        dnf install -y "$EPEL_RPM_URL"
    fi
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
        log "  ⚠️ fail2ban 설치 실패. dnf install -y fail2ban 으로 수동 설치하세요 (EPEL 필요)."
    fi
    log "  SSH 포트 ${SSH_PORT}, 비밀번호 인증 활성화 완료"

    # --- 데이터 디스크 마운트 (또는 /volume 디렉토리 생성) ---
    log "[3/10] 데이터 디스크 마운트 (또는 ${VOLUME_PATH} 디렉토리 생성)"
    if [ -n "$VOLUME_DEVICE" ]; then
        log "  사용 가능한 블록 디바이스:"
        lsblk -o NAME,SIZE,TYPE,MOUNTPOINT | tee -a "$LOG_FILE"
    fi
    mount_data_volume "$VOLUME_DEVICE" "$VOLUME_PATH"

    # --- 작업/데이터 디렉토리 설정 ---
    log "[4/10] 작업/데이터 디렉토리 설정"
    # /volume 자체는 root:root + 0775로 통일
    # - 컨테이너는 /volume을 직접 마운트하지 않음 (/workspace, /data, /models, /home로만 접근)
    # - setup-host.sh, user.sh는 sudo 전제 → root 소유여도 mkdir 가능
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

    # SELinux: 컨테이너 bind mount 대상은 container_file_t 라벨을 준다. Docker 데몬 기본값은
    # selinux-enabled=false라 지금 구성에서는 없어도 동작하지만, 누가 데몬 옵션을 켜는 순간
    # /volume 전체가 Permission denied가 되므로 미리 라벨링해 둔다 (멱등).
    if command -v semanage &>/dev/null && [ "$(getenforce 2>/dev/null || echo Disabled)" != "Disabled" ]; then
        semanage fcontext -a -t container_file_t "${VOLUME_PATH}(/.*)?" 2>/dev/null \
            || semanage fcontext -m -t container_file_t "${VOLUME_PATH}(/.*)?" 2>/dev/null || true
        restorecon -R "$VOLUME_PATH"
        log "  SELinux: ${VOLUME_PATH} container_file_t 라벨 적용"
    fi

    # --- 시스템 업데이트 + 커널 패키지 ---
    log "[5/10] 시스템 업데이트 + 커널 패키지 설치"
    dnf update -y --exclude='kernel*'
    dnf install -y \
        dnf-plugins-core python3-dnf-plugin-versionlock \
        curl wget git jq htop tmux pciutils \
        gcc dkms python3-pip --allowerasing

    # nvitop (호스트에서 GPU 실시간 모니터링 — htop의 GPU 버전, Phase 2 완료 후 동작)
    # — RHEL 10도 PEP 668(외부 관리 환경) 정책으로 시스템 Python에 직접 pip install이 차단됨.
    #   호스트 운영자용 단일 CLI라 시스템 site-packages 충돌 위험이 낮으므로 --break-system-packages로 우회.
    if command -v nvitop &>/dev/null; then
        log "  nvitop 이미 설치됨. 건너뜀."
    elif pip3 install --break-system-packages nvitop 2>/dev/null \
        || pip3 install nvitop 2>/dev/null; then
        log "  nvitop 설치 완료 (호스트에서 nvitop 실행 → GPU 실시간 모니터링)"
    else
        log "  ⚠️ nvitop 설치 실패. 수동 설치: pip3 install --break-system-packages nvitop"
    fi

    # 커널 헤더: NVIDIA 공식 가이드(RHEL 10)의 kernel-devel-matched — 실행 중 커널과 정확히 같은
    # 버전을 고른다. dkms가 이걸로 nvidia 모듈을 빌드하므로 버전이 어긋나면 드라이버가 안 뜬다.
    dnf install -y kernel-devel-matched kernel-headers
    log "  커널: $(uname -r), kernel-devel-matched 설치"

    # --- 작업 사본 배치 ---
    log "[6/10] 작업 사본 배치 (${VOLUME_PATH}/workspace/root/ai-infra)"
    place_working_copy

    # --- Docker 설치 (Docker CE 공식 저장소) ---
    log "[7/10] Docker 설치"
    if command -v docker &>/dev/null && docker --version 2>/dev/null | grep -q "Docker"; then
        log "  Docker 이미 설치됨: $(docker --version). 건너뜀."
    else
        # RHEL 기본 컨테이너 스택은 podman이다. docker-ce·containerd.io와 패키지 충돌(runc 등)이
        # 나므로 Docker 공식 설치 문서대로 먼저 걷어낸다. 설치돼 있을 때만 제거한다.
        local conflict_pkgs=() p
        for p in podman buildah runc docker docker-client docker-common docker-engine; do
            rpm -q "$p" &>/dev/null && conflict_pkgs+=("$p")
        done
        if [ ${#conflict_pkgs[@]} -gt 0 ]; then
            log "  충돌 패키지 제거: ${conflict_pkgs[*]}"
            dnf remove -y "${conflict_pkgs[@]}"
        fi
        dnf config-manager --add-repo "$DOCKER_REPO_URL"
        # compose·buildx가 플러그인 패키지로 함께 온다 — AL2023처럼 curl로 따로 받을 필요가 없다.
        dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        systemctl enable --now docker
        log "  Docker 설치 완료: $(docker --version)"
    fi
    # 사용자를 docker 그룹에 추가
    if [ -n "$USERNAME" ] && [ "$USERNAME" != "root" ] && id "$USERNAME" &>/dev/null; then
        usermod -aG docker "$USERNAME" 2>/dev/null || true
    fi
    log "  Compose: $(docker compose version --short 2>/dev/null || echo '?') / Buildx: $(docker buildx version 2>/dev/null | grep -oE 'v[0-9.]+' | head -1 || echo '?')"

    # --- Claude Code (dev 전용 호스트 도구) ---
    log "[8/10] Claude Code 설치"
    if [ "$MODE" != "dev" ]; then
        log "  MODE=${MODE}: 운영 모드 → Claude Code 호스트 설치 건너뜀."
    elif [ -n "$USERNAME" ] && [ "$USERNAME" != "root" ]; then
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
        log "  USERNAME 미설정 또는 root. 건너뜀."
    fi

    # --- NVIDIA 저장소 ---
    log "[9/10] NVIDIA 저장소 등록"
    dnf config-manager --add-repo "$NVIDIA_REPO_URL" 2>/dev/null || true
    dnf clean expire-cache

    # --- NVIDIA 드라이버 ---
    log "[10/10] NVIDIA 드라이버 설치 (nvidia-open ${NVIDIA_DRIVER_VERSION})"
    if nvidia-smi &>/dev/null; then
        local cur
        cur=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | tr -d ' ')
        if [ "$cur" != "$NVIDIA_DRIVER_VERSION" ]; then
            # 다른 버전이 이미 떠 있으면 교체하지 않는다. 드라이버 교체는 커널 모듈 언로드가 얽혀
            # 자동화하면 원격 세션이 끊길 수 있고, 어느 쪽을 남길지는 운영 판단이다.
            log "  ⚠️ 설치된 드라이버 ${cur} ≠ .env NVIDIA_DRIVER_VERSION ${NVIDIA_DRIVER_VERSION}"
            log "     교체하려면 수동: dnf remove -y 'nvidia-*' 'kmod-nvidia-*' && reboot 후 재실행"
        else
            log "  NVIDIA 드라이버 ${cur} 이미 설치됨."
        fi
        lock_nvidia_versions
        echo "2" > "$PHASE_FILE"
        log "========== Phase 1 완료 (reboot 불필요) =========="
        phase2
        return
    fi

    # RHEL 10 repo는 모듈 스트림이 없다. nvidia-open 메타패키지에 버전을 붙여 설치하면
    # 의존성(nvidia-driver-cuda, kmod-nvidia-open-dkms 등)이 같은 버전으로 따라온다.
    dnf install -y "nvidia-open-${NVIDIA_DRIVER_VERSION}"
    lock_nvidia_versions

    # persistenced: 없으면 GPU가 유휴 때 드라이버를 내려놓아 첫 요청마다 초기화 지연이 붙는다.
    systemctl enable nvidia-persistenced 2>/dev/null \
        && log "  nvidia-persistenced 활성화 (부팅 시 자동)" \
        || log "  ⚠️ nvidia-persistenced 유닛 없음. Phase 2 후 systemctl enable --now nvidia-persistenced 확인"

    # Phase 2 자동 실행을 위한 systemd 서비스 등록
    echo "2" > "$PHASE_FILE"
    register_phase2_service

    log "========== Phase 1 완료. 10초 후 reboot =========="
    log "  reboot 후 Phase 2가 자동 실행됩니다."
    log "  진행 상황: tail -f $LOG_FILE"
    sleep 10
    reboot
}

# NVIDIA 패키지 버전 잠금. RHEL 10 저장소는 브랜치를 스트림으로 가르지 않아서 `dnf update`가
# 580(LTSB, 2028-06까지)을 610(NFB, 지원 종료)으로 올려버린다. 잠그지 않으면 LTS를 고른 의미가 없다.
# 멱등: 이미 잠긴 항목은 dnf가 무시한다.
lock_nvidia_versions() {
    dnf versionlock add 'nvidia-*' 'kmod-nvidia-*' 'libnvidia-*' 'libnvsdm*' >/dev/null 2>&1 || true
    log "  dnf versionlock: nvidia-* 잠금 ($(dnf versionlock list 2>/dev/null | grep -c nvidia || echo 0)건)"
}

# ============================================
# Phase 2: Container Toolkit + Fabric Manager + 이미지 pull
# ============================================
phase2() {
    # Phase 2 종료 시 (성공/실패 무관) systemd 서비스 + phase 파일 정리 (리부트 루프 방지).
    # EXIT trap 사용 이유: ERR trap은 if-조건 실패/||-체인/exit N 일부 케이스에서 미발동 가능 →
    # 정리가 누락되면 phase 파일이 남아 재부팅 시 phase2 재실행 루프 위험. EXIT은 정상 종료/exit/
    # signal 모두 커버. 정상 종료 시는 명시 정리 후 trap을 해제해 완료 메시지 순서를 유지.
    trap 'cleanup_phase2_service; rm -f "$PHASE_FILE"' EXIT

    log "========== Phase 2 시작 =========="

    # --- NVIDIA 드라이버 확인 ---
    log "[1/5] NVIDIA 드라이버 확인"
    if nvidia-smi &>/dev/null; then
        nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader | while read -r line; do
            log "  GPU: $line"
        done
    else
        error_exit "NVIDIA 드라이버가 로드되지 않았습니다. dmesg | grep -i nvidia 확인 필요 (dkms 빌드 실패면 kernel-devel-matched 버전 확인)"
    fi
    systemctl enable --now nvidia-persistenced 2>/dev/null || true

    # --- NVIDIA Container Toolkit ---
    log "[2/5] NVIDIA Container Toolkit 설치 (${NVIDIA_CONTAINER_TOOLKIT_VERSION})"
    if ! command -v nvidia-ctk &>/dev/null; then
        curl -fsSL "$NCT_REPO_URL" | tee /etc/yum.repos.d/nvidia-container-toolkit.repo >/dev/null
        dnf clean expire-cache
        # 공식 가이드의 버전 고정 형식. 4개를 같은 버전으로 맞춰야 의존성 해소가 된다.
        dnf install -y \
            "nvidia-container-toolkit-${NVIDIA_CONTAINER_TOOLKIT_VERSION}" \
            "nvidia-container-toolkit-base-${NVIDIA_CONTAINER_TOOLKIT_VERSION}" \
            "libnvidia-container-tools-${NVIDIA_CONTAINER_TOOLKIT_VERSION}" \
            "libnvidia-container1-${NVIDIA_CONTAINER_TOOLKIT_VERSION}"
        dnf versionlock add 'nvidia-container-toolkit*' 'libnvidia-container*' >/dev/null 2>&1 || true
        log "  Container Toolkit 설치 완료"
    else
        log "  Container Toolkit 이미 설치됨: $(nvidia-ctk --version 2>/dev/null | head -1)"
    fi
    # runtime configure는 멱등 명령이라 매번 실행
    # — 이미 설치돼 있어도 docker daemon에 nvidia runtime 등록이 빠진 케이스 보장
    nvidia-ctk runtime configure --runtime=docker
    systemctl restart docker

    # --- Fabric Manager (NVSwitch 자동 감지) ---
    log "[3/5] Fabric Manager 확인"
    # GPU 이름(H200)만 보면 PCIe 카드 구성까지 잡힌다. NVSwitch가 실제로 있을 때만 드라이버가
    # /dev/nvidia-nvswitch*를 만드니 그걸 본다 (Phase 2는 드라이버 로드 후라 판단 가능).
    local nvswitch_count
    nvswitch_count=$(ls /dev/nvidia-nvswitch* 2>/dev/null | wc -l)
    if [ "$nvswitch_count" -gt 0 ]; then
        log "  NVSwitch ${nvswitch_count}개 감지 (HGX 보드) → Fabric Manager 설치"
        local driver_version
        driver_version=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | tr -d ' ')
        # FM은 드라이버와 소수점까지 같은 버전이어야 기동한다. 설치된 드라이버 버전을 그대로 쓴다.
        # RHEL 10 공식 가이드의 패키지 조합 (libnvidia-nscq, libnvsdm, nvidia-imex 동반).
        if dnf install -y "nvidia-fabricmanager-${driver_version}" libnvidia-nscq libnvsdm nvidia-imex; then
            dnf versionlock add 'nvidia-fabricmanager*' >/dev/null 2>&1 || true
            systemctl enable nvidia-fabricmanager
            systemctl start nvidia-fabricmanager
            log "  Fabric Manager 설치 + 시작 완료 (driver=${driver_version})"
        else
            log "  ⚠️ Fabric Manager 자동 설치 실패. 수동 설치 필요:"
            log "     dnf install -y nvidia-fabricmanager-${driver_version} libnvidia-nscq libnvsdm nvidia-imex"
            log "     ⚠️ FM 없이는 GPU 간 NVLink 통신이 안 되어 tensor_parallel 기동이 실패합니다."
        fi
    else
        if nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | grep -qiE "H100|H200|A100|B100|B200"; then
            log "  NVSwitch 디바이스 없음 → PCIe 구성으로 판단. Fabric Manager 불필요."
            log "     (HGX 보드인데 이 메시지가 나오면 lspci -d 10de: | grep -i bridge 로 확인)"
        else
            log "  NVSwitch GPU 미감지. Fabric Manager 불필요."
        fi
    fi

    # --- 폐쇄망 대비: 베이스 이미지 미리 pull ---
    # 세팅 후 네트워크가 끊길 수 있다. docker compose build가 FROM에서 당기는 vLLM 이미지와
    # GPU 테스트 이미지는 지금 받아 둔다. 모델 가중치와 pip 휠은 컨테이너 안에서 받으므로
    # on-prem/start.sh check 가 점검한다 (SETUP_GUIDE.md §5).
    log "[4/5] 베이스 이미지 pull (폐쇄망 대비)"
    if [ -n "$VLLM_IMAGE" ]; then
        if docker image inspect "$VLLM_IMAGE" &>/dev/null; then
            log "  ${VLLM_IMAGE} 이미 있음."
        else
            docker pull "$VLLM_IMAGE" && log "  ${VLLM_IMAGE} pull 완료" \
                || log "  ⚠️ ${VLLM_IMAGE} pull 실패 — 네트워크 개방 상태에서 docker pull 재시도"
        fi
    else
        log "  ⚠️ VLLM_IMAGE 미설정 — aws/.env 확인. 미리 받지 못하면 폐쇄망에서 build가 실패한다."
    fi
    docker image inspect "$CUDA_TEST_IMAGE" &>/dev/null || docker pull "$CUDA_TEST_IMAGE" \
        || log "  ⚠️ ${CUDA_TEST_IMAGE} pull 실패"

    # --- Docker GPU 테스트 ---
    # GPU Docker 환경 구축이 본 스크립트의 목적이므로 실패 시 fail-fast
    # (성공 메시지로 넘어가면 사용자가 정상 종료로 오해 → 실제로는 컨테이너에서 GPU 못 봄)
    log "[5/5] Docker GPU 연동 테스트"
    if docker run --rm --gpus all "$CUDA_TEST_IMAGE" nvidia-smi &>/dev/null; then
        log "  ✅ Docker GPU 연동 정상"
    else
        error_exit "Docker GPU 테스트 실패. nvidia-container-toolkit 또는 docker 데몬 설정 확인 필요. (재시도: systemctl restart docker && docker run --rm --gpus all ${CUDA_TEST_IMAGE} nvidia-smi)"
    fi

    # Phase 2 완료 — 명시 정리 후 EXIT trap 해제 (실패 시는 trap이 자동 정리)
    cleanup_phase2_service
    rm -f "$PHASE_FILE"
    trap - EXIT

    local work_dir="${VOLUME_PATH}/workspace/root/ai-infra/aws"
    [ -d "$work_dir" ] || work_dir="${SCRIPT_DIR}/../aws"

    log ""
    log "============================================"
    log "  ✅ 온프레미스 GPU 서버 세팅 완료"
    log "============================================"
    log ""
    log "  OS            : $(. /etc/os-release && echo "$PRETTY_NAME")"
    log "  NVIDIA Driver : $(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)"
    log "  Docker        : $(docker --version)"
    log "  Compose       : $(docker compose version --short 2>/dev/null || echo 'N/A')"
    log "  Fabric Mgr    : $(systemctl is-active nvidia-fabricmanager 2>/dev/null || echo '해당 없음')"
    log "  GPU           :"
    nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader | while read -r line; do
        log "    $line"
    done
    log ""
    log "  다음 단계:"
    log "    cd $(realpath "$work_dir")"
    log "    docker compose build && docker compose up -d"
    log "    네트워크 끊기 전: ../on-prem/start.sh check"
    log ""
    log "  로그: $LOG_FILE"
    log "============================================"
}

# ============================================
# systemd 서비스: reboot 후 phase2 자동 실행
# ============================================
register_phase2_service() {
    cat > /etc/systemd/system/onprem-setup-phase2.service <<UNIT
[Unit]
Description=On-prem GPU Setup Phase 2
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
    systemctl enable onprem-setup-phase2.service
    log "  Phase 2 자동 실행 서비스 등록 완료"
}

cleanup_phase2_service() {
    if [ -f /etc/systemd/system/onprem-setup-phase2.service ]; then
        systemctl disable onprem-setup-phase2.service 2>/dev/null || true
        rm -f /etc/systemd/system/onprem-setup-phase2.service
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
    if [ -f "$ENV_FILE" ]; then
        log ".env 파일 로드: $ENV_FILE"
        # Windows 줄 끝(CRLF) 제거
        sed -i 's/\r$//' "$ENV_FILE"
        set -a
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set +a
    else
        log "⚠️ ${ENV_FILE} 없음 — 기본값으로 진행. 먼저 cp on-prem/.env.prd aws/.env 를 권장"
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
