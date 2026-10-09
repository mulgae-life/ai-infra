# AWS EC2 GPU 서버 (vLLM + 다중 사용자)

Amazon Linux 2023 + NVIDIA GPU EC2에 vLLM 기반 LLM 환경을 1회 셋업으로 띄우는 Docker 인프라 템플릿.

**제공 기능**
- vLLM 베이스 컨테이너 + SSH
- 다중 사용자 컨테이너 자동 관리 (`user.sh`, 포트/홈 자동 할당)
- 폐쇄망 대응 (SSM Session Manager 셸 접근)
- 한 인스턴스 = 한 모드 (`MODE=dev` 또는 `MODE=prd`)

---

## 1. 사전 준비

| 항목 | 내용 |
|------|------|
| EC2 인스턴스 | NVIDIA GPU 탑재 (g6e/p4/p5 등) |
| OS | Amazon Linux 2023 |
| 추가 EBS | (선택) 데이터/모델 영속화용. 연결 시 `lsblk`로 디바이스 경로 확인(예: `/dev/nvme1n1`). 미연결 시 루트 디스크에 `/volume` 디렉토리만 생성 ⚠️ 인스턴스 종료 시 손실 |
| 권한 | `sudo` 가능한 OS 계정 |
| AWS CLI | EC2 호스트에서 S3 접근 가능 (IAM Role 또는 `aws configure`) |
| (선택) | HuggingFace 토큰 (게이트 모델 사용 시) |

> 💡 **운영 환경**: 본 인프라는 **내부망 전용**입니다. `.env`의 `HF_TOKEN`/`PASSWORD` 등 시크릿은 내부 정책으로 보호되므로 S3/EBS 동기화 시에도 별도 마스킹하지 않습니다.

---

## 2. 모드 선택: dev vs prd

| 항목 | `MODE=dev` | `MODE=prd` |
|------|:----------:|:----------:|
| 용도 | 개발/실험 | 챗봇/서빙 |
| Claude Code 자동 설치 | ✅ | ❌ |
| nvm + Node + codex 빌드 | ✅ | ❌ |
| 이미지 슬림화 | ❌ | ✅ |
| 기본 `USERNAME` | `user` | `root` |
| 기본 `LLM_EXTRA_PORTS` | `5001-5009` (range) | `5031` (단일) |
| 기본 `LLM_IMAGE_NAME` | `llm-dev` | `llm-prd` |

> 인스턴스 단위로 모드를 결정합니다. 한 인스턴스에 두 모드를 공존시키지 않습니다.

---

## 3. 빠른 시작

### 3-1. 로컬 → S3 (코드 변경 시)
```bash
cd /workspace/ai-infra/aws && ./start.sh push
```

> ⚠️ `push`는 **전체 교체**입니다. S3 프리픽스를 비운 뒤 올려 로컬과 정확히 일치시킵니다. 로컬에서 지운 파일이 S3에 남아 `pull` 때 되살아나는 것을 막기 위해서입니다. 업로드 중 실패하면 프리픽스가 빈 상태로 남으니 반드시 다시 실행하세요. `wheels/`(246MB)는 vLLM 0.31.0 전환 뒤 빌드에 쓰지 않지만, 운영 반영 확인 뒤 `.archive/`로 옮기기 전까지 남아 있으면 제외 대상이 아니라 push마다 다시 올라가므로, 규모를 먼저 보려면 `./start.sh push --dryrun`을 쓰세요(삭제 단계까지 미리보기로 동작).

> 🔑 `.env`는 각 서버의 런타임 로드본이라 동기화에서 빠집니다. S3로 오가는 것은 환경별 원본인 `.env.dev`·`.env.prd`뿐입니다. 그래서 서버마다 한 번 `cp`로 골라두면 이후 `pull`을 몇 번 하든 그 서버의 `.env`는 그대로 남습니다. 값을 바꿔 배포하려면 `.env`가 아니라 `.env.dev`/`.env.prd`를 고친 뒤 `push`하고, 대상 서버에서 다시 `cp` 하세요. 두 파일은 토큰과 비밀번호를 담고 있어 git에는 올라가지 않습니다(S3로만 전달).

### 3-2. EC2 인스턴스 최초 셋업
```bash
# (1) 코드 다운로드 — 최초 1회는 start.sh가 아직 없어 raw 명령 (이후 갱신은 ./start.sh pull)
mkdir -p ~/aws && aws s3 sync s3://hgi-ai-res/hjjo/aws/ ~/aws/
cd ~/aws
chmod +x *.sh                  # S3는 실행권한을 보존하지 않아 받은 .sh가 전부 644다. 이후 pull은 start.sh가 자동 처리

# (2) 환경 모드 선택 → .env 생성
cp .env.dev .env               # 개발 EC2
# 또는
cp .env.prd .env               # 운영 EC2

vim .env                       # VOLUME_DEVICE 등 서버 고유값 확인 (USERNAME·PASSWORD·HF_TOKEN은 채워져 있음)

# (3) 호스트 셋업 (Phase 1 → 자동 reboot → Phase 2 자동 실행)
sudo ./setup-ec2.sh
tail -f /var/log/ec2-setup.log    # 진행 확인 (다른 터미널)

# (4) 컨테이너 빌드 + 기동
docker compose build
docker compose up -d
docker compose logs -f llm        # 로그 확인
```

---

## 4. `.env` 주요 키

> 전체 키와 기본값은 `.env.dev` / `.env.prd` 참조. 아래는 자주 만지는 키.

**사용자 / 시스템**

| 키 | 설명 | 필수 |
|----|------|:----:|
| `MODE` | `dev` \| `prd` (모드 분기 트리거) | ✅ |
| `USERNAME` | OS 계정명 (prd는 `root`) | ✅ |
| `PASSWORD` | SSH 패스워드 | ✅ |
| `CONTAINER_UID` / `GID` | 컨테이너 내부 사용자 UID/GID (기본 `2000`). 기존 EC2 사용자가 다른 UID면 그 값으로 맞춰야 함 | — |
| `SSH_PORT` | EC2 호스트 SSH 포트 (기본 `5555`, 22 미사용). fail2ban 동일 포트 적용 | — |
| `HF_TOKEN` | HuggingFace 토큰 | 게이트 모델 시 |

**스토리지**

| 키 | 설명 | 필수 |
|----|------|:----:|
| `VOLUME_DEVICE` | EBS 디바이스 경로 (`lsblk` 확인, 추가 EBS만). **비우면 루트 디스크에 `/volume` 생성** (운영계 + S3 재동기화 정책 시) ⚠️ 인스턴스 종료 시 손실 | — |
| `VOLUME_PATH` | EBS 마운트 경로 (기본 `/volume`) | — |
| `EXTRA_REQUIREMENTS` | 컨테이너가 뜰 때마다 추가로 pip 설치할 파일 경로. **비워 둔다**(서빙 의존성은 이미지 빌드 때 `requirements.txt`로 들어간다). 값을 주면 빌드 때의 핵심 패키지 제약(`/opt/vllm-core-constraints.txt`)을 걸어 설치하므로 vLLM·torch·transformers 버전을 바꾸는 패키지는 설치가 실패하고 컨테이너가 멈춘다 | — |

**이미지**

| 키 | 설명 | 필수 |
|----|------|:----:|
| `VLLM_IMAGE` | vLLM 베이스 이미지. 태그와 다이제스트를 함께 적는다(현재 `vllm/vllm-openai:v0.31.0@sha256:c1c9f6fd…`). 버전을 바꾸면 `Dockerfile.llm`의 `ARG VLLM_VERSION`도 같이 바꾼다 — 둘이 다르면 빌드 첫 단계에서 멈춘다 | ✅ |
| `LLM_IMAGE_NAME` | 빌드 결과 이미지 태그 (기본 dev=`llm-dev`, prd=`llm-prd`). **`docker-compose.yml`과 `user.sh`가 공유** — 한 .env에서만 관리 | — |
| `CUDA_TEST_IMAGE` | Phase 2 GPU 연동 테스트용 이미지 (기본 `nvidia/cuda:12.8.1-base-ubuntu24.04`) | — |

**포트 / 리소스**

| 키 | 설명 | 필수 |
|----|------|:----:|
| `LLM_SSH_PORT` | 메인 컨테이너 호스트 SSH 포트 (기본 `5000`, 충돌 시 변경) | — |
| `LLM_EXTRA_PORTS` | 서비스용 포트 (단일 `5031` 또는 range `5001-5009`) | — |
| `LLM_GPUS` | `all` 또는 `0,1` 등 (기본 `all`, compose `NVIDIA_VISIBLE_DEVICES`로 직접 노출 제어) | — |
| `LLM_MEMORY` | 컨테이너 메모리 한도 (기본 `48g`) | — |
| `SHM_SIZE` | 공유 메모리 (멀티GPU 통신용, 기본 `16g`) | — |

---

## 5. `setup-ec2.sh`가 하는 일

### Phase 1 (재부팅 전) — 9단계

| 단계 | 내용 |
|:----:|------|
| 1 | OS 사용자 생성 + sudo 권한 (`USERNAME=root`이면 스킵). 기존 사용자 UID/GID가 `.env`와 다르면 fail-fast |
| 2 | SSH 포트 변경(`SSH_PORT`, 기본 5555) + 비밀번호 인증 활성화 + `fail2ban` |
| 3 | EBS 포맷(xfs) + 마운트 + fstab 등록. 디바이스 미지정/UUID 미생성 시 폴백 동작 |
| 4 | `/volume/{workspace,data,models,homes,root-homes}` 생성. `/volume` 자체는 `root:root` `0775`, `data`/`models`는 `CONTAINER_UID:GID` |
| 5 | 시스템 업데이트 + 커널 헤더(`kernel-devel`/`kernel-modules-extra`) + `gcc`/`dkms`/`python3-pip` + **`nvitop` 자동 설치** (호스트 GPU 모니터링, PEP 668 우회) |
| 6 | Docker 엔진 설치 + 사용자(`ec2-user`/`ssm-user`/`USERNAME`)를 `docker` 그룹 추가 |
| 7 | Docker Compose V2 + Buildx (>= 0.17.0 검사, 미만이면 v0.21.2 자동 재설치) |
| 8 | Claude Code 호스트 설치 (**dev 모드만**) |
| 9 | NVIDIA 오픈 드라이버(`nvidia-open`) — 설치 후 자동 `reboot` |

### Phase 2 (재부팅 후 자동, systemd) — 4단계

| 단계 | 내용 |
|:----:|------|
| 1 | NVIDIA 드라이버 로드 확인 (`nvidia-smi`) |
| 2 | NVIDIA Container Toolkit 설치 + `nvidia-ctk runtime configure` (멱등) |
| 3 | Fabric Manager — NVSwitch GPU(H100/H200/A100/B100/B200) 자동 감지 시 설치 |
| 4 | `docker run --gpus all $CUDA_TEST_IMAGE nvidia-smi` 연동 테스트 (실패 시 fail-fast) |

> Phase 2는 `systemd` 서비스(`ec2-setup-phase2.service`)로 자동 실행. 성공/실패 무관 EXIT trap이 서비스+phase 파일을 정리하여 리부트 루프 방지.

> 진행 확인: `tail -f /var/log/ec2-setup.log` / `systemctl status ec2-setup-phase2.service`

---

## 6. 다중 사용자 컨테이너 (`user.sh`)

`user.sh`로 사용자별 독립 컨테이너를 생성합니다. 포트는 자동 할당 (10포트씩).

```bash
# 일반 개발 사용자 (SSH, 동명 OS 계정 자동 생성)
sudo ~/aws/user.sh up jin    --password 1234 --gpus 2,3
sudo ~/aws/user.sh up song   --password 1234 --gpus 0,1
sudo ~/aws/user.sh up cho    --password 1234 --gpus 0

# 일반 사용자에게 기본 range(예: 5041-5049) 외에 추가 포트 range가 더 필요할 때
# (재생성 시 라벨로 자동 보존됨 — 변경하려면 down 후 다시 up)
sudo ~/aws/user.sh up demo --password 1234 --gpus 0 --extra-ports 5100-5149
# 다중 range는 콤마로 구분 (docker-proxy 프로세스 부담 고려해 꼭 필요한 만큼만)
sudo ~/aws/user.sh up demo2 --password 1234 --gpus 0 --extra-ports 5020-5029,5100-5149

# 운영 root 컨테이너 (SSH 불가, docker exec 접근)
sudo ~/aws/user.sh up prd-job --root --password aiteam12 --gpus all

# 다중 root 컨테이너 (서비스별 분리 — 한 EC2에서 동시 운영)
sudo ~/aws/user.sh up job --root --password 1234 --service-port 5031 --gpus 0
sudo ~/aws/user.sh up gemma --root --password 1234 --service-port 5015 --gpus 2,3
sudo ~/aws/user.sh up mail --root --password 1234 --service-port 5032 --gpus none
# ⚠️ --password 생략 시 기본값 'changeme'로 운영 컨테이너가 생성됨

sudo ~/aws/user.sh list                  # 컨테이너 목록
sudo ~/aws/user.sh down jin              # 중지 + 제거 (데이터는 /volume 보존)
sudo ~/aws/user.sh rebuild               # 이미지 변경 후 전체 재생성
sudo ~/aws/user.sh rebuild jin           # 특정 사용자만
```

### 포트 자동 할당 규칙

| 컨테이너 | SSH 포트 | 추가 포트 |
|----------|:--------:|:---------:|
| 메인 (`docker compose`) | 5000 | 5001-5009 |
| `user.sh` 첫 사용자 | 5010 | 5011-5019 |
| `user.sh` 두 번째 | 5020 | 5021-5029 |
| ... | ... | ... |
| `user.sh` 49번째 | 5490 | 5491-5499 |

---

## 7. 접속

### 7-1. SSH
```bash
ssh -p <PORT> <user>@<host>     # PORT = LLM_SSH_PORT 또는 user.sh 할당 포트
```

`~/.ssh/config` 예시 (메인 컨테이너 미사용 시 — 첫 `user.sh` 사용자가 5010):
```
Host AWS-jin
    HostName <host>
    Port 5010
    User jin
```

메인 컨테이너(`docker compose up`)도 함께 운영 중이면 메인이 `LLM_SSH_PORT`(기본 5000)를 점유하므로 첫 사용자는 5020부터 시작 — `ssh-config-sample` 참조.

### 7-2. 운영 root 컨테이너 (SSH 불가)

`USERNAME=root` 메인 컨테이너 / `user.sh --root` 컨테이너는 SSH가 막혀 있어 호스트에서 `docker exec`로 접근:

```bash
sudo docker exec -it <container_name> bash
```

폐쇄망에서 EC2 호스트 자체 접근은 SSM Session Manager (`aws ssm start-session --target i-<INSTANCE_ID>`).

---

## 8. 운영 환경 (prd) 별도 안내

```bash
cp .env.prd .env               # MODE=prd, USERNAME=root 기본
vim .env                       # EXTRA_REQUIREMENTS 등 서버별로 다른 값만 확인
sudo ./setup-ec2.sh
docker compose up -d
```

- **이미지 슬림화**: nvm/Node/codex 빌드 안 됨, Claude Code 미설치
- **`USERNAME=root`**: OS 사용자 생성 스킵, `/root` 홈 사용
- **`/root` 영속화**: 호스트 `/volume/root`에 마운트 (bash history 보존)
- **SSH 접속 불가** → `docker exec` 또는 SSM Session Manager로 셸 접근 (§7-2)
- **다중 운영계 슬롯**: `user.sh --root`는 `--service-port` 인자로 컨테이너별 호스트 서비스 포트를 분리할 수 있어 한 EC2에서 다수 동시 운용 가능. 인자 미지정 시 `.env LLM_EXTRA_PORTS` 폴백이라 compose `llm-root`와 같은 포트가 되어 충돌하므로, **다중 운용 시 인자 명시 필수**. 홈은 `/volume/root-homes/<name>`에 컨테이너별 독립 보존, `rebuild` 시 라벨에 저장된 포트가 그대로 복원됨.

---

## 9. 유지보수

### 9-1. 코드 변경 반영
```bash
# (1) 로컬 → S3 (전체 교체)
cd /workspace/ai-infra/aws && ./start.sh push

# (2) EC2 → 다운로드 + 재빌드 (pull이 --delete로 잔재 정리 + *.sh 실행권한 자동 부여)
#     .env는 동기화 제외라 이 서버 설정 그대로 유지됨. 환경 원본을 고쳤다면 cp .env.prd .env 로 다시 반영
cd ~/aws && ./start.sh pull
docker compose build --no-cache && docker compose up -d
sudo ~/aws/user.sh rebuild              # 사용자 컨테이너 일괄 갱신
```

> 🔁 `pull` 전에 `~/aws`를 지울 필요가 없습니다. `aws s3 sync`는 체크섬을 보지 않고 크기와 수정시각만 비교하는데, 기본 규칙이 "크기가 같고 받는 쪽이 더 새로우면 스킵"이라 갱신된 파일이 조용히 넘어가는 일이 있었습니다. 받은 파일의 mtime이 S3 객체의 시각이 아니라 다운로드한 시각으로 찍혀 로컬이 늘 더 새롭기 때문입니다.
>
> `start.sh`가 `--exact-timestamps`로 그 판정을 막으므로 `pull` 한 번이면 S3와 같은 상태가 됩니다. 디렉토리를 통째로 지우고 받는 방식과 달리 제외 목록(`.env` 등)은 그대로 남습니다.

### 9-2. `.env`만 수정한 경우 (이미지 재빌드 불필요)
```bash
docker compose up -d --force-recreate
sudo ~/aws/user.sh rebuild              # 이미지 갱신 + 기존 옵션 보존 재생성
```

> ⚠️ `user.sh rebuild`는 기존 컨테이너의 `PASSWORD`/`GPU`/`MODE` 등을 그대로 복원합니다. **비밀번호·GPU 할당·모드 변경**은 `down` → `up` 사이클이 필요합니다:
> ```bash
> sudo ~/aws/user.sh down jin
> sudo ~/aws/user.sh up jin --password new_pw --gpus 0,1
> ```

### 9-3. vLLM 버전업 반영 (0.31.0, 이미 셋업된 서버)

호스트 셋업(`setup-ec2.sh`)은 다시 하지 않는다. 운영 이미지가 이미 CUDA 13(torch cu130)이라 드라이버 조건이 같다. 바뀌는 것은 이미지(`aws/`), env 두 줄, 서빙 코드(`llm-serving/`) 세 가지다.

```bash
# ── (1) 로컬(연구계) → S3: env 원본과 서빙 코드를 함께 올린다
cd /workspace/ai-infra/aws && ./start.sh push
cd /workspace/ai-infra/llm-serving && ./start.sh push

# ── (2) 대상 서버 호스트: 받기 + env 확인
cd ~/aws && ./start.sh pull
cp .env.prd .env               # 개발계는 .env.dev. 서버 고유값(VOLUME_DEVICE 등)을 고쳐 둔 서버는 아래 두 줄만 옮긴다
grep -E '^(VLLM_IMAGE|EXTRA_REQUIREMENTS)=' .env
#   VLLM_IMAGE=vllm/vllm-openai:v0.31.0@sha256:c1c9f6fd5c109ba7f0546a59f5b2f15fb87f64c77782e90a27b648b42a8e67c3
#   EXTRA_REQUIREMENTS=          ← 비어 있어야 한다

# ── (3) 이미지 빌드 — 되돌리기용으로 지금 서빙 컨테이너가 실제로 쓰는 이미지 ID에 태그를 먼저 남긴다
IMG=$(grep '^LLM_IMAGE_NAME=' .env | cut -d= -f2)      # 운영 llm-prd, 개발 llm-dev
docker tag "$(docker inspect -f '{{.Image}}' <지금 서빙 컨테이너>)" "$IMG:pre-0.31"   # 새 서버면 생략
docker compose build             # 베이스 9GB를 받는다. 첫 단계에서 vLLM 버전을 확인하고, 끝에 --final 조합을 출력한다
docker run --rm --entrypoint cat "$IMG" /opt/image-core-final.txt   # 핵심 조합. 이미지 확인 때 만든 aws/image-freeze-0.31.0.txt와 다르면 여기서 멈춘다
#   → vllm==0.31.0 / torch==2.13.0+cu130 / transformers==5.17.0 …

# ── (4) 서빙 컨테이너를 새 이미지로
sudo ./user.sh up llm-serving --root --password <pw> --service-port 5501 --gpus 0   # 새로 만들 때
sudo ./user.sh rebuild <이름>                                                       # 이미 있는 user.sh 컨테이너(포트·GPU 보존)
docker compose up -d --force-recreate                                               # compose 메인 컨테이너(llm-root)를 쓰는 서버

# ── (5) 컨테이너 안: 서빙 코드 받기 → 기동 → 확인
sudo docker exec -it llm-serving bash
aws s3 sync s3://hgi-ai-res/hjjo/llm-serving/ /workspace/llm-serving/   # 처음 한 번. 이후는 cd /workspace/llm-serving && ./start.sh pull
chmod +x /workspace/llm-serving/start.sh /workspace/llm-serving/*/start.sh
cd /workspace/llm-serving/vllm
./start.sh up prd-gemma && ./start.sh up 5501   # PII 모드면 llm-serving/DEPLOY_GUIDE.md §3.2
./start.sh logs prd-gemma -n 400 | grep -E 'speculative_config|Model Runner|Selected'   # speculative_config=None (운영 Gemma MTP 끔)
./start.sh test prd-gemma
```

- 이미 운영 중인 서버는 계획서 `agent-guide/plans/work-plan_261008_vllm-upgrade/part3-rollout-cleanup.md` P4 순서를 따른다: 새 게이트웨이를 옛 vLLM 위에서 먼저 재기동해 확인하고, 게이트웨이를 거치지 않는 직접 호출 클라이언트가 없는지 본 뒤, 조합을 대조하고 컨테이너를 바꾼다.
- 코드와 이미지의 순서는 바뀌어도 된다. 게이트웨이 effort 처리와 MTP 끔 설정은 옛 이미지(0.20.2 nightly)에서도 같은 동작이다. 다만 새 이미지에 옛 코드를 붙이면 effort만 보낸 요청에서 thinking이 켜지므로, (5)의 `pull`을 건너뛰지 않는다.
- `quantization: fp8`은 0.31에서 "deprecated, `fp8_per_tensor`를 쓰라"는 경고만 내고 같은 경로로 동작한다. 키 변경은 운영 반영을 확인한 뒤에 한다. 옛 nightly에서 `fp8_per_tensor`는 `fp8`과 다른 구현이라, 먼저 바꾸면 되돌릴 때 경로가 달라진다.
- **되돌리기**: `docker tag "$IMG:pre-0.31" "$IMG"` → (4)와 같은 명령으로 컨테이너를 다시 만든다. 서빙 코드는 두 버전에서 동작하므로 그대로 둔다. 다음 빌드를 옛 버전으로 하려면 `.env`의 `VLLM_IMAGE`와 `Dockerfile.llm`의 `VLLM_VERSION`도 함께 되돌린다.

---

## 10. 디렉토리 구조 (`/volume`)

```
/volume/                 # root:root  0775   ← setup-ec2.sh가 생성, USERNAME 의존 X
├── workspace/<user>     # <user>:<user>     컨테이너 /workspace
├── homes/<user>         # <user>:<user>     컨테이너 /home/<user>
├── root-homes/<name>    # 0:0               user.sh --root 컨테이너별 /root (독립)
├── root                 # 0:0               메인 운영계 /root (USERNAME=root) ※ docker가 첫 기동 시 자동 생성
├── models               # CONTAINER_UID:GID 모델 저장소 (모든 컨테이너 공유)
└── data                 # CONTAINER_UID:GID 데이터 (모든 컨테이너 공유)
```

> - `/volume` 자체는 `root:root` 0775로 통일 — `USERNAME=root`/일반 모드 전환 시에도 일관성 유지.
> - `data`/`models`는 공유 디렉토리라 `CONTAINER_UID` 소유. root 컨테이너는 권한 0이라 모두 쓰기 가능, 일반 사용자(2000)도 쓰기 가능.
> - 컨테이너를 `down`/`rm`해도 `/volume`은 보존됩니다.

---

## 11. 트러블슈팅

| 증상 | 원인 / 해결 |
|------|-------------|
| `setup-ec2.sh: 디바이스 또는 자식 파티션이 ... 마운트됨` 에러 | 루트/시스템 디스크 또는 자식 파티션이 이미 사용 중. `lsblk`로 `/`나 `/boot/efi`가 안 붙은 추가 EBS만 지정 (디스크 전체 `/dev/nvme0n1` 입력 시에도 자식 `p1`이 `/`에 붙어 있으면 차단됨). 추가 EBS가 없는 운영계라면 `VOLUME_DEVICE`를 비워두면 됨 |
| `setup-ec2.sh: 기존 파티션이 존재합니다` 에러 | 기존 데이터 EBS가 파티션 형태(예: `/dev/nvme1n1p1`)로 데이터를 보유 중인데 `.env`에 디스크 전체 경로(`/dev/nvme1n1`)를 지정하여 발생. 자식 데이터 파괴 방지 가드 → 파티션 경로(`/dev/nvme1n1p1`)를 직접 입력하거나 새 EBS 사용 |
| `⚠️ <device>의 UUID를 읽을 수 없습니다. fstab 등록 건너뜀.` 로그 | `blkid -o value -s UUID`가 빈 값 → fstab 미등록 → **재부팅 시 `/volume` 마운트 안 됨**. `blkid <device>` 수동 확인, UUID가 보이면 `/etc/fstab`에 직접 추가 (`UUID=<uuid> /volume xfs defaults,nofail 0 2`) |
| `setup-ec2.sh: 사용자 UID/GID 불일치` 에러 | 호스트의 기존 사용자 UID/GID가 `.env CONTAINER_UID`/`GID`와 다름 (이전에 다른 UID로 만들어진 케이스). **데이터 보존 권장**: `.env`의 값을 에러 메시지에 표시된 기존 UID/GID로 맞춘 후 재실행 → `/volume` 데이터 그대로 유지 |
| `docker compose build` 시 `buildx` 버전 호환 에러 | AL2023 dnf docker 패키지가 구버전 buildx(< 0.17.0)를 함께 설치 → Compose v2.27+ 요구사항 미달. `setup-ec2.sh` 재실행 시 자동 감지하여 v0.21.2로 재설치. 수동: `curl -fsSL https://github.com/docker/buildx/releases/download/v0.21.2/buildx-v0.21.2.linux-amd64 -o /usr/libexec/docker/cli-plugins/docker-buildx && chmod +x $_` |
| `setup-ec2.sh: Docker GPU 테스트 실패` 에러 | `systemctl restart docker` 후 `docker run --rm --gpus all $CUDA_TEST_IMAGE nvidia-smi` 수동 재실행. 정상이면 `sudo ./setup-ec2.sh --phase2` 재시도 |
| `nvidia-smi` 실패 | Phase 2 미완료. `tail -f /var/log/ec2-setup.log` 확인 후 `sudo systemctl status ec2-setup-phase2.service` |
| `user.sh up` 시 포트 범위 초과 | 사용자 컨테이너가 49개 도달. 미사용 사용자 `down`으로 정리 |
| Claude Code 설치 실패 (폐쇄망) | dev 모드에서만 시도, 실패해도 컨테이너는 정상 기동. 수동 설치: `curl -fsSL https://claude.ai/install.sh \| bash` |
| Fabric Manager 자동 설치 실패 | NVSwitch GPU(H100/H200 등)에서 발생 가능. 로그의 안내대로 수동 설치: `dnf module install -y nvidia-driver:<branch>-open/fm` |
| 빌드 첫 단계에서 `베이스 이미지의 vLLM X != 0.31.0` | `.env`의 `VLLM_IMAGE`가 옛 값이다. `.env.prd`(개발계는 `.env.dev`)를 다시 `cp`하거나 두 줄(`VLLM_IMAGE`·`EXTRA_REQUIREMENTS`)을 §9-3대로 고친다 |
| 빌드 중 pip `ResolutionImpossible` / `Cannot install` | `requirements.txt`의 패키지가 베이스의 핵심 조합(vLLM·torch·transformers·FlashInfer 등, `gen-core-constraints.py`)을 바꾸려 한다. 그 패키지의 버전을 베이스와 맞는 값으로 고친다. 핵심 조합은 베이스 이미지가 정하므로 requirements에서 바꾸지 않는다 |
| 컨테이너가 기동 직후 멈추고 로그에 `==> 추가 패키지 설치` 뒤 pip 오류 | `EXTRA_REQUIREMENTS`에 값이 남아 있고, 그 파일이 핵심 조합을 바꾸려 한다(진입점이 같은 제약을 건다). `.env`에서 비우고 `user.sh rebuild <이름>` |
| 호스트 GPU 모니터링 (`nvitop`) 동작 안 함 | Phase 1에서 PEP 668 우회로 자동 설치되지만 실패 가능. 수동: `pip3 install --break-system-packages nvitop`. 실행: 호스트 셸에서 `nvitop` |
