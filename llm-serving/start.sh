#!/usr/bin/env bash
# llm-serving/ 서빙 코드 S3 동기화 (로컬 ↔ S3)
# 사용법: ./start.sh {push|pull} [추가 aws s3 sync 옵션...]
#
# 이 파일은 llm-serving 루트의 '코드 배포' 진입점이고, 하위 vllm/·stt/·pii/의 start.sh는
# '서비스 제어' 진입점이다. 이름은 같지만 역할이 다르니 혼동 주의:
#   배포:      llm-serving/start.sh push|pull
#   서비스:    llm-serving/{vllm,stt,pii}/start.sh up|down|status|...
#              QA 명령은 클러스터마다 다르다 — vllm은 test·speed·traffic,
#              stt는 test만, pii는 up|down|status만 받는다.
#
# 모델 기동/재시작은 이 스크립트 책임이 아니다 (SRP):
#   - vLLM: cd vllm && ./start.sh restart <name>
#   - STT : cd stt  && ./start.sh restart <name>
# 여기선 코드 동기화만 하고, 완료 후 다음 단계 명령을 안내한다.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# =====================================================================
# S3 배포 설정 (DEPLOY_GUIDE.md §1 참조)
# 경로는 env로 오버라이드 가능 — 하드코딩 대신 안전한 기본값 + 설정 분리.
# =====================================================================
S3_URI="${LLM_SERVING_S3_URI:-s3://hgi-ai-res/hjjo/llm-serving/}"

# push(로컬→S3) / pull(S3→로컬) 공통 제외 목록.
# logs/, __pycache__/, .pytest_cache/, .ruff_cache/, 런처 임시 config(.vllm_serve_*),
# 포트 회피 상태(.runtime/), samples/ 는 런타임 산출물이라 제외 (.gitignore와 동일 기준).
# 두 캐시는 도구가 디렉토리 안에 자기 .gitignore를 심어 git에서는 저절로 빠지지만,
# aws s3 sync는 .gitignore를 모르므로 여기 명시하지 않으면 S3를 오간다.
SYNC_EXCLUDES=(
    --exclude '*/logs/*'
    --exclude '*/__pycache__/*'
    --exclude '*.pyc'
    --exclude '*/.pytest_cache/*'
    --exclude '*/.ruff_cache/*'
    --exclude '*/.vllm_serve_*'
    --exclude '*/.runtime/*'
    --exclude '*/samples/*'
    --exclude '*/.archive/*'
    --exclude '*/audit.salt'      # PII 감사로그 HMAC 시크릿 — 환경별 분리, S3 업로드 금지
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
# 제외 목록(logs/·.runtime/·audit.salt 등)은 전부 런타임 산출물·환경별 시크릿이라
# 애초에 S3에 있어서는 안 되는 것들이다. 삭제 단계에서 함께 지워지는 편이 오히려 정리가 된다.
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
    echo "[push] 업로드 완료"
    echo "[push] 운영계 적용: ./start.sh pull 후 cd {vllm,stt} && ./start.sh restart <name>"
}

# S3 → 로컬 다운로드 (운영계 컨테이너에서 코드 받기)
# --delete: S3에서 사라진 파일을 로컬에서도 지워 push(전체 교체)와 정확히 일치시킨다.
# 제외 목록(logs/·.runtime/·audit.salt 등)은 --delete에서도 삭제되지 않고 보호된다.
# --exact-timestamps: 크기가 같은 파일은 타임스탬프가 정확히 일치할 때만 건너뛴다.
#   기본 규칙은 "크기가 같고 로컬이 더 새로우면 스킵"인데, sync로 받은 파일의 mtime은 S3
#   객체의 시각이 아니라 다운로드한 시각으로 찍혀 로컬이 늘 더 새로워진다. 여기에 받은 쪽에서
#   파일을 한 번 건드렸거나 두 서버 시계가 어긋나면 갱신된 파일이 조용히 스킵된다. sync는
#   체크섬을 보지 않으므로 크기까지 같은 수정(yaml의 0.95 → 0.90 같은 자릿수 동일 치환)에서
#   특히 잘 걸린다. 이 옵션이 그 판정을 막아 rm -rf 후 재다운로드와 같은 정합을 준다.
cmd_pull() {
    require_aws pull

    echo "[pull] S3 → 로컬 동기화(잔재 삭제 포함): $S3_URI → $SCRIPT_DIR"
    if ! aws s3 sync "$S3_URI" "$SCRIPT_DIR" --delete --exact-timestamps "${SYNC_EXCLUDES[@]}" "$@"; then
        echo "[pull] S3 다운로드 실패 — 경로/권한(IAM Role) 확인 후 재시도"
        exit 1
    fi
    # 루트(배포)와 하위 클러스터(서비스 제어) 양쪽의 start.sh에 실행 권한을 준다.
    chmod +x "$SCRIPT_DIR"/start.sh "$SCRIPT_DIR"/*/start.sh 2>/dev/null || true
    echo "[pull] 다운로드 완료"
    echo "[pull] 다음 단계: cd {vllm,stt} && ./start.sh restart <name>"
}

case "${1:-}" in
    push)   shift; cmd_push "$@" ;;
    pull)   shift; cmd_pull "$@" ;;
    *)
        echo "사용법: $0 {push|pull} [추가 aws s3 sync 옵션...]"
        echo ""
        echo "  push   로컬 → S3 전체 교체 업로드 (기존 S3 객체 삭제 후 업로드, 개발 머신)"
        echo "  pull   S3 → 로컬 받기 (S3에 없는 로컬 파일 삭제, 운영계 컨테이너)"
        echo ""
        echo "추가 옵션 예시:"
        echo "  ./start.sh push --dryrun       업로드 미리보기 (삭제 단계도 미리보기로 동작)"
        echo ""
        echo "※ 서비스 기동/중지는 이 스크립트가 아니라 하위 클러스터에서:"
        echo "     cd vllm && ./start.sh up|down|status|test"
        exit 1
        ;;
esac
