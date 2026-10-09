#!/usr/bin/env bash
# aws/ 인프라 코드 S3 동기화 (로컬 ↔ S3)
# 사용법: ./start.sh {push|pull} [추가 aws s3 sync 옵션...]
#
# 재빌드/재기동은 이 스크립트 책임이 아니다 (SRP):
#   - 이미지 재빌드: docker compose build  (SETUP_GUIDE.md §4-1)
#   - 인스턴스 재생성: ./user.sh rebuild <name>
# 여기선 코드 동기화만 하고, 완료 후 다음 단계 명령을 안내한다.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# =====================================================================
# S3 배포 설정 (SETUP_GUIDE.md §1-3 참조)
# 경로는 env로 오버라이드 가능 — 하드코딩 대신 안전한 기본값 + 설정 분리.
# =====================================================================
S3_URI="${AWS_INFRA_S3_URI:-s3://hgi-ai-res/hjjo/aws/}"

# push(로컬→S3) / pull(S3→로컬) 공통 제외 목록.
# ※ wheels/ 는 vLLM 0.31.0 전환으로 Dockerfile.llm이 더는 쓰지 않는다(nightly 휠 덮어쓰기 제거).
#    폴더는 운영 반영 확인 뒤 .archive/로 옮긴다 — 그 전까지는 있으면 push에 함께 올라간다.
# ※ .env(각 서버의 런타임 로드본)는 제외한다 — 환경별 .env.dev/.env.prd만 S3에 보관하고
#    각 서버가 배포 후 알맞은 것을 .env로 복사한다. 제외하지 않으면 pull 한 번에
#    그 서버의 .env가 다른 환경 값으로 덮어써진다(MODE·USERNAME·GPU 배정까지 뒤바뀜).
#    .env.dev/.env.prd는 '.env' 정확매칭에 걸리지 않아 그대로 동기화된다.
#    두 파일은 토큰·비밀번호를 담고 있어 git에는 올리지 않는다(내부망 전용 정책, S3로만 전달).
SYNC_EXCLUDES=(
    --exclude '.git/*'
    --exclude '**/__pycache__/*'
    --exclude '*.pyc'
    --exclude '.archive/*'
    --exclude '.claude/*'
    --exclude '*.log'
    --exclude '.env'
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
# ※ wheels/(246MB)가 남아 있으면 제외 대상이 아니라 push마다 다시 올라간다(위 주석 참고).
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

case "${1:-}" in
    push)   shift; cmd_push "$@" ;;
    pull)   shift; cmd_pull "$@" ;;
    *)
        echo "사용법: $0 {push|pull} [추가 aws s3 sync 옵션...]"
        echo ""
        echo "  push   로컬 → S3 전체 교체 업로드 (기존 S3 객체 삭제 후 업로드, 개발 머신)"
        echo "  pull   S3 → 로컬 받기 (S3에 없는 로컬 파일 삭제, EC2 호스트)"
        echo ""
        echo "추가 옵션 예시:"
        echo "  ./start.sh push --dryrun       업로드 미리보기 (삭제 단계도 미리보기로 동작)"
        exit 1
        ;;
esac
