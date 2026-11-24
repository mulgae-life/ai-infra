#!/bin/bash
set -euo pipefail

# ============================================
# 런타임 초기화
# - USERNAME=root: 운영계 모드 (사용자 생성 스킵, root 홈 /root 사용)
# - USERNAME=<일반>: 개발 모드 (사용자 생성 + 홈 셋업)
# ============================================
USERNAME="${USERNAME:-user}"
PASSWORD="${PASSWORD:-changeme}"
CONTAINER_UID="${CONTAINER_UID:-2000}"
CONTAINER_GID="${CONTAINER_GID:-2000}"
MODE="${MODE:-dev}"

# 홈 디렉토리 기본 설정
setup_user_home() {
    local home_dir="$1"
    su - "$USERNAME" -c "git config --global --add safe.directory /workspace && git config --global core.quotePath false" || true
    # .tmux.conf는 부재 시에만 생성 — 컨테이너 재진입(빈 홈 복원 케이스 등) 시 사용자 커스텀 설정 보존
    [ -f "$home_dir/.tmux.conf" ] || echo "set -g mouse on" > "$home_dir/.tmux.conf"
    # CUDA + pip 사용자 패키지 PATH (중복 추가 방지)
    if ! grep -q '/usr/local/cuda/bin' "$home_dir/.bashrc" 2>/dev/null; then
        echo 'export PATH="/usr/local/cuda/bin:$HOME/.local/bin:$PATH"' >> "$home_dir/.bashrc"
        echo 'export LD_LIBRARY_PATH="/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"' >> "$home_dir/.bashrc"
    fi
    # nvm 설정 (sudo 없이 npm 사용) — dev 모드에서만
    if [ "$MODE" = "dev" ] && ! grep -q 'NVM_DIR' "$home_dir/.bashrc" 2>/dev/null; then
        echo 'export NVM_DIR=/usr/local/nvm' >> "$home_dir/.bashrc"
        echo '[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"' >> "$home_dir/.bashrc"
    fi
    chown -R "${USERNAME}:${USERNAME}" "$home_dir"
}

# ============================================
# 런타임 requirements 설치 (vLLM 의존성 보강용)
# 기본은 비워 둔다 — 서빙 의존성은 이미지 빌드 때 requirements.txt로 들어간다.
# 값을 주면 컨테이너가 뜰 때마다 설치하므로, 빌드 때 만든 핵심 패키지 제약(vLLM·torch·transformers·
# FlashInfer 등 ==)을 같이 건다. 추가 패키지가 그 조합을 바꾸려 하면 설치가 실패하고 컨테이너가 멈춘다
# (조용히 버전이 바뀌는 것보다 낫다). 제약 파일이 없는 옛 이미지는 예전처럼 제약 없이 설치한다.
# ============================================
CORE_CONSTRAINTS=/opt/vllm-core-constraints.txt
if [ -n "${EXTRA_REQUIREMENTS:-}" ]; then
    if [ -f "${EXTRA_REQUIREMENTS}" ]; then
        echo "==> 추가 패키지 설치: $EXTRA_REQUIREMENTS"
        constraint_args=()
        [ -f "$CORE_CONSTRAINTS" ] && constraint_args=(-c "$CORE_CONSTRAINTS")
        python3 -m pip install --no-cache-dir --break-system-packages -q -r "$EXTRA_REQUIREMENTS" "${constraint_args[@]}"
    else
        echo "⚠️ EXTRA_REQUIREMENTS=${EXTRA_REQUIREMENTS} 파일이 존재하지 않습니다." >&2
    fi
fi

# ============================================
# 일반 사용자 생성 (root는 이미 있으므로 스킵)
# ============================================
if [ "$USERNAME" != "root" ]; then
    if ! id "$USERNAME" &>/dev/null; then
        existing_user=$(getent passwd "$CONTAINER_UID" | cut -d: -f1 || true)
        [ -n "$existing_user" ] && userdel -r "$existing_user" 2>/dev/null || true
        existing_group=$(getent group "$CONTAINER_GID" | cut -d: -f1 || true)
        [ -n "$existing_group" ] && groupdel "$existing_group" 2>/dev/null || true

        groupadd -g "$CONTAINER_GID" "$USERNAME" 2>/dev/null || true
        useradd -m -s /bin/bash -u "$CONTAINER_UID" -g "$CONTAINER_GID" "$USERNAME"
        echo "${USERNAME}:${PASSWORD}" | chpasswd
        usermod -aG sudo "$USERNAME"

        setup_user_home "/home/${USERNAME}"
    fi

    # 홈 디렉토리 초기화 (bind mount 시 빈 디렉토리/UID 불일치 모두 처리)
    # - 빈 홈: /etc/skel 복원 (bind mount 첫 기동)
    # - UID 불일치: 호스트에서 다른 UID로 만들어진 홈 디렉토리 보정
    # - 두 케이스 모두 setup_user_home 호출 → bashrc/tmux/git 설정 일관성 보장
    #   (setup_user_home은 idempotent: grep -q / [ -f ] 가드로 중복 추가 방지)
    HOME_DIR="/home/$USERNAME"
    if [ -d "$HOME_DIR" ]; then
        if [ -z "$(ls -A "$HOME_DIR" 2>/dev/null)" ]; then
            cp -a /etc/skel/. "$HOME_DIR/" 2>/dev/null || true
        fi
        if [ "$(stat -c %u "$HOME_DIR")" != "$CONTAINER_UID" ]; then
            chown -R "${USERNAME}:${USERNAME}" "$HOME_DIR"
        fi
        setup_user_home "$HOME_DIR"
    fi

    if [ "$MODE" = "dev" ] && [ -d /usr/local/nvm ]; then
        chown -R "${USERNAME}:${USERNAME}" /usr/local/nvm
    fi
fi

# ============================================
# Docker 환경변수 (SSH 셸 공통)
# ============================================
{
    echo 'export PATH="/usr/local/cuda/bin:$HOME/.local/bin:$PATH"'
    echo 'export LD_LIBRARY_PATH="/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"'
    if [ "$MODE" = "dev" ]; then
        echo 'export NVM_DIR=/usr/local/nvm'
        echo '[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"'
    fi
    [ -n "${HF_TOKEN:-}" ] && echo "export HF_TOKEN=\"$HF_TOKEN\""
    [ -n "${ASSIGNED_GPUS:-}" ] && echo "export NVIDIA_VISIBLE_DEVICES=\"$ASSIGNED_GPUS\""
    true
} > /etc/profile.d/docker-env.sh

# 비로그인 bash 셸에서도 env 적용 (docker exec 등)
if ! grep -q 'docker-env.sh' /etc/bash.bashrc 2>/dev/null; then
    echo '[ -f /etc/profile.d/docker-env.sh ] && . /etc/profile.d/docker-env.sh' >> /etc/bash.bashrc
fi

# ============================================
# 사용자 홈 디렉토리 동적 탐지
# (root: /root, 일반: /home/<user>)
# ============================================
USER_HOME=$(getent passwd "$USERNAME" | cut -d: -f6)
if [ -z "$USER_HOME" ] || [ ! -d "$USER_HOME" ]; then
    echo "❌ 사용자 '${USERNAME}' 홈 디렉토리를 찾을 수 없습니다." >&2
    exit 1
fi

# ============================================
# Claude Code 설치 (폐쇄망이면 실패해도 진행)
# ============================================
if [ "$MODE" = "dev" ] && [ ! -f "${USER_HOME}/.local/bin/claude" ]; then
    echo "==> Claude Code 설치 시도: ${USERNAME} (home: ${USER_HOME})"
    # timeout 필수: 폐쇄망 방화벽이 TCP SYN을 drop하면 기본 curl은 수 분간 재전송 대기 → 컨테이너 기동이 hang 걸린 것처럼 보임
    # pipefail 필수: curl 실패를 bash(빈 입력으로 0 종료)가 가려서 실패 로그가 안 찍히는 문제 방지
    su - "$USERNAME" -c "set -o pipefail; curl -fsSL --connect-timeout 5 --max-time 30 https://claude.ai/install.sh | bash" \
        || echo "⚠️ Claude Code 설치 실패 (폐쇄망이거나 네트워크 문제) — 무시하고 진행" >&2
fi

# ============================================
# SSH 기동 준비 (sshd 실행 직전 필수 조건 정리)
# - /run/sshd: privilege separation 디렉토리. "must be owned by root" 체크 실패 시 sshd 즉시 종료
#   (Docker 에서 /run 이 tmpfs 로 초기화되어 이미지 빌드 시 만든 디렉토리가 사라지는 케이스 대응)
# - /etc/ssh/ssh_host_*_key: 퍼미션 600 필수 ("UNPROTECTED PRIVATE KEY FILE" 방지)
# - 두 체크 중 하나라도 실패하면 sshd 가 즉시 exit → restart 루프
# ============================================
mkdir -p /run/sshd
chown root:root /run/sshd
chmod 0755 /run/sshd

ssh-keygen -A 2>/dev/null || true
chmod 600 /etc/ssh/ssh_host_*_key 2>/dev/null || true
chmod 644 /etc/ssh/ssh_host_*_key.pub 2>/dev/null || true

exec "$@"
