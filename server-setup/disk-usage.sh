#!/usr/bin/env bash
# 호스트 디스크 사용량 조회 (조회 전용 — 아무것도 지우지 않는다)
# 사용법: sudo bash disk-usage.sh
#
# 루트 EBS 하나에 /volume(models·data·사용자별 경로)과 /var/lib/docker가 함께 있으므로
# 둘을 같이 본다. 결과는 화면과 /tmp/disk-usage-<시각>.txt에 함께 남고,
# 끝나면 요약을 출력한 뒤 S3_DEST로 자동 업로드한다.
# du가 900GB 안팎을 훑으므로 몇 분 걸린다.

set -u

VOLUME_PATH="${VOLUME_PATH:-/volume}"
S3_DEST="${S3_DEST:-s3://hgi-ai-res/hjjo/tmp/}"
REPORT="/tmp/disk-usage-$(date +%Y%m%d-%H%M).txt"
BIG_USER_GB=100   # 요약에서 "큰 사용자"로 표시할 기준

if [ "$(id -u)" -ne 0 ]; then
    echo "sudo로 실행해야 합니다: sudo bash $0" >&2
    exit 1
fi

section() { printf '\n===== %s =====\n' "$1"; }

{
    section "디스크 전체"
    df -hT / "$VOLUME_PATH" 2>/dev/null

    section "루트 1단계 (/)"
    ROOT_DU=$(du -xh --max-depth=1 / 2>/dev/null | sort -rh | head -15)
    echo "$ROOT_DU"

    section "$VOLUME_PATH 1단계"
    VOL_DU=$(du -xh --max-depth=1 "$VOLUME_PATH" 2>/dev/null | sort -rh)
    echo "$VOL_DU"

    for d in workspace homes root-homes; do
        section "사용자별: $VOLUME_PATH/$d"
        du -xsh "$VOLUME_PATH/$d"/* 2>/dev/null | sort -rh
    done

    section "사용자별 합계 (workspace + homes + root-homes, GB)"
    USER_TOTALS=$(du -xsk "$VOLUME_PATH"/workspace/* "$VOLUME_PATH"/homes/* "$VOLUME_PATH"/root-homes/* 2>/dev/null \
        | awk '{n=split($2,p,"/"); u=p[n]; s[u]+=$1} END{for(u in s) printf "%.1f\t%s\n", s[u]/1048576, u}' | sort -rn)
    echo "$USER_TOTALS"

    section "사용자 홈 캐시 (.cache, .triton)"
    du -xsh "$VOLUME_PATH"/homes/*/.cache "$VOLUME_PATH"/homes/*/.triton \
        "$VOLUME_PATH"/root-homes/*/.cache "$VOLUME_PATH"/root-homes/*/.triton 2>/dev/null | sort -rh | head -20

    section "$VOLUME_PATH/models 3단계 상위 20"
    du -xh --max-depth=3 "$VOLUME_PATH/models" 2>/dev/null | sort -rh | head -20

    section "$VOLUME_PATH/data 2단계 상위 20"
    du -xh --max-depth=2 "$VOLUME_PATH/data" 2>/dev/null | sort -rh | head -20

    DOCKER_DF=""
    if command -v docker >/dev/null 2>&1; then
        section "Docker 요약 (이미지·컨테이너·볼륨·빌드 캐시)"
        docker system df
        DOCKER_DF=$(docker system df --format '{{.Type}}|{{.Size}}|{{.Reclaimable}}')
        section "Docker 컨테이너별 쓰기 계층 크기"
        docker ps -as --format '{{.Size}}\t{{.Names}}\t{{.Image}}'
        section "Docker 이미지 목록"
        docker images --format '{{.Size}}\t{{.Repository}}:{{.Tag}}\t{{.CreatedSince}}' | sort -rh | head -20
        section "Docker 컨테이너 로그 상위 10"
        du -sh /var/lib/docker/containers/*/*-json.log 2>/dev/null | sort -rh | head -10
    fi

    section "지워졌지만 프로세스가 잡고 있는 1GB 이상 파일"
    if command -v lsof >/dev/null 2>&1; then
        lsof -nP +L1 2>/dev/null | awk 'NR==1 || $7>1e9'
    else
        echo "lsof 없음 — 건너뜀"
    fi

    # ---- 요약: 위에서 모은 값만 다시 정리한다 (du를 다시 돌리지 않음) ----
    section "요약"
    read -r D_SIZE D_USED D_AVAIL D_PCENT <<< "$(df -h --output=size,used,avail,pcent / | tail -1)"
    echo "디스크: ${D_SIZE} 중 ${D_USED} 사용 (${D_PCENT}), 여유 ${D_AVAIL}"
    if [ "${D_PCENT%\%}" -ge 85 ]; then
        echo "  ⚠ 사용률 85% 이상 — 정리 또는 EBS 확장 검토"
    fi

    echo
    echo "[사용자별 합계 GB]"
    echo "$USER_TOTALS" | awk -v big="$BIG_USER_GB" \
        '$1>0 {printf "  %7.1f  %s%s\n", $1, $2, ($1>=big ? "  ⚠ " big "GB 이상" : ""); t+=$1}
         END {printf "  %7.1f  (사용자 소계)\n", t}'

    echo
    echo "[공통·시스템]"
    printf '  models  %s\n' "$(echo "$VOL_DU" | awk -v p="$VOLUME_PATH/models" '$2==p{print $1}')"
    printf '  data    %s\n' "$(echo "$VOL_DU" | awk -v p="$VOLUME_PATH/data" '$2==p{print $1}')"
    printf '  /var    %s (Docker 포함)\n' "$(echo "$ROOT_DU" | awk '$2=="/var"{print $1}')"

    if [ -n "$DOCKER_DF" ]; then
        echo
        echo "[Docker]"
        echo "$DOCKER_DF" | awk -F'|' '{printf "  %-15s %-9s 회수 가능 %s\n", $1, $2, $3}'
    fi
} 2>&1 | tee "$REPORT"

echo
echo "결과 파일: $REPORT"

# 자격 증명은 sudo 이전 사용자의 것을 쓴다 (root에는 AWS 설정이 없을 수 있음)
if [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != "root" ]; then
    UPLOAD=(sudo -u "$SUDO_USER" -H aws s3 cp "$REPORT" "$S3_DEST")
else
    UPLOAD=(aws s3 cp "$REPORT" "$S3_DEST")
fi
if "${UPLOAD[@]}"; then
    echo "S3 업로드 완료: ${S3_DEST}$(basename "$REPORT")"
else
    echo "S3 업로드 실패 — 직접 실행: aws s3 cp $REPORT $S3_DEST" >&2
    exit 1
fi
