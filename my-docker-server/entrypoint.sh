#!/bin/bash
for INIT_DIR in /etc/docker-home-init/*/; do
    [ -d "$INIT_DIR" ] || continue
    USERNAME=$(basename "$INIT_DIR")
    HOME_DIR="/home/$USERNAME"

    if [ -d "$HOME_DIR" ] && [ -z "$(ls -A "$HOME_DIR" 2>/dev/null)" ]; then
        # 홈 디렉토리가 비어있으면 초기 설정 파일 복사
        cp -a "$INIT_DIR/." "$HOME_DIR/"
        chown -R "$USERNAME:$USERNAME" "$HOME_DIR"
    elif [ -d "$HOME_DIR" ] && [ "$(stat -c %u "$HOME_DIR")" != "$(id -u "$USERNAME")" ]; then
        # 홈 디렉토리 소유자 UID가 현재 사용자 UID와 불일치하면 chown
        chown -R "$USERNAME:$USERNAME" "$HOME_DIR"
    fi
done

# SSH 호스트 키 영속화: 이미지를 다시 빌드하면 키가 새로 생겨 클라이언트가
# "호스트 키가 바뀌었다"며 접속을 거부한다. compose 가 /etc/ssh/hostkeys 를
# 호스트 디렉토리로 마운트해 두면, 보관된 키가 있을 때는 복원하고
# 없을 때(최초 기동)는 이미지가 만든 키를 보관한다.
HOSTKEY_DIR=/etc/ssh/hostkeys
if [ -d "$HOSTKEY_DIR" ]; then
    if ls "$HOSTKEY_DIR"/ssh_host_*_key >/dev/null 2>&1; then
        cp -a "$HOSTKEY_DIR"/ssh_host_* /etc/ssh/
    else
        cp -a /etc/ssh/ssh_host_* "$HOSTKEY_DIR"/
    fi
    chmod 600 /etc/ssh/ssh_host_*_key
    chmod 644 /etc/ssh/ssh_host_*_key.pub
fi

# /tmp 권한 복원: compose 가 /tmp 를 호스트 디렉토리로 마운트하는데, 그 디렉토리가
# 없으면 Docker 가 root 755 로 만들어 일반 계정이 /tmp 에 쓰지 못한다.
# 원래 /tmp 권한(모두 쓰기 + 남의 파일 삭제 금지)으로 맞춘다.
chmod 1777 /tmp

exec "$@"
