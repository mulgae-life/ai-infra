# AWS EC2 GPU 서버 셋업 (vLLM + 다중 사용자)

Amazon Linux 2023 + NVIDIA GPU EC2에 vLLM 서빙 이미지를 빌드하고 컨테이너를 띄우는 절차입니다.

- 서버 하나는 한 가지 모드로만 씁니다. 개발(`MODE=dev`) 또는 운영(`MODE=prd`)입니다.
- 사용자·서비스마다 컨테이너를 따로 만듭니다(`user.sh`).
- 모델 서빙 코드(`llm-serving/`)의 배포와 기동은 [`../llm-serving/DEPLOY_GUIDE.md`](../llm-serving/DEPLOY_GUIDE.md)에서 다룹니다.

## 한눈에 보기

```
로컬 (/workspace/ai-infra/aws) ──push──▶ S3 ──pull──▶ EC2 호스트 (~/aws)
                                                       ├─ docker compose build → 이미지 llm-dev / llm-prd
                                                       ├─ docker compose up    → 메인 컨테이너 llm-<USERNAME>
                                                       └─ user.sh up           → 사용자·서비스 컨테이너
```

| 하려는 일 | 볼 곳 |
|---|---|
| 새 EC2를 처음 셋업 | [2. 처음 셋업](#2-처음-셋업-새-ec2) |
| 사용자·서비스 컨테이너 만들기 | [3. 컨테이너 관리](#3-컨테이너-관리-usersh) |
| 코드 변경 반영 | [4-1. 코드 변경](#4-1-코드-변경) |
| `.env`만 변경 | [4-2. `.env`만 변경](#4-2-env만-변경) |
| vLLM 0.31.0으로 버전업 | [4-3. vLLM 0.31.0 버전업](#4-3-vllm-0310-버전업-이미-셋업된-서버) |
| 오류 대응 | [6. 문제 해결](#6-문제-해결) |

---

## 1. 준비

### 1-1. 필요한 것

| 항목 | 내용 |
|---|---|
| EC2 | NVIDIA GPU 인스턴스 (g6e, p4, p5 등) |
| OS | Amazon Linux 2023 |
| 권한 | `sudo`가 되는 OS 계정 |
| AWS CLI | 호스트에서 S3 접근 (IAM Role 또는 `aws configure`) |
| 추가 EBS (선택) | 모델·데이터 보관용. 없으면 루트 디스크에 `/volume`을 만들고, 인스턴스를 종료하면 함께 사라짐 |
| HuggingFace 토큰 (선택) | 접근 승인이 필요한 모델을 받을 때 |

### 1-2. 모드: dev / prd

| 항목 | `dev` (개발·실험) | `prd` (서빙) |
|---|:---:|:---:|
| 이미지 이름 `LLM_IMAGE_NAME` | `llm-dev` | `llm-prd` |
| 컨테이너 계정 `USERNAME` | `user` | `root` |
| 메인 컨테이너 서비스 포트 `LLM_EXTRA_PORTS` | `5001-5009` | `5031` |
| Claude Code, Node, codex | 설치 | 설치 안 함 |

운영(prd) 모드는 아래가 다릅니다.

- 컨테이너 계정이 `root`라 SSH로 들어갈 수 없습니다. 호스트에서 `docker exec`로 들어갑니다([3-3](#3-3-접속)).
- 호스트에 OS 사용자를 만들지 않습니다.
- 메인 컨테이너의 `/root`는 호스트 `/volume/root`에 남습니다.

### 1-3. 코드와 `.env` 전달

**push / pull**

- 로컬에서 `./start.sh push`, 서버에서 `./start.sh pull`을 씁니다. S3 경로는 `s3://hgi-ai-res/hjjo/aws/`입니다.
- `push`는 S3 경로를 비운 뒤 다시 올립니다. 업로드 중에 실패하면 S3가 빈 채로 남으니 바로 다시 실행합니다.
- 올릴 내용을 미리 보려면 `./start.sh push --dryrun`을 씁니다. 삭제 단계도 미리보기로만 실행됩니다.
- `pull`은 서버를 S3와 같게 맞춥니다. S3에 없는 파일은 지우고 `*.sh`에 실행 권한을 다시 줍니다. 받기 전에 `~/aws`를 지울 필요는 없습니다.

**`.env`**

- `.env`는 주고받지 않고 서버마다 따로 둡니다. S3로 오가는 것은 원본인 `.env.dev`, `.env.prd`입니다.
- 서버에서는 원본을 복사해 씁니다: `cp .env.prd .env`(개발 서버는 `.env.dev`).
- 값을 바꿀 때는 로컬 원본을 고쳐 `push`하고, 서버에서 다시 `cp`합니다.
- 원본에는 토큰과 비밀번호가 들어 있어 git에 올리지 않습니다. 내부망 전용이라 S3에는 그대로 둡니다.

---

## 2. 처음 셋업 (새 EC2)

```bash
# 1) 코드 받기 — 처음에는 start.sh가 없어 aws 명령으로 직접 받는다
mkdir -p ~/aws && aws s3 sync s3://hgi-ai-res/hjjo/aws/ ~/aws/
cd ~/aws && chmod +x *.sh          # S3는 실행 권한을 보존하지 않는다

# 2) .env 만들기
cp .env.prd .env                   # 운영 서버. 개발 서버는 cp .env.dev .env
vim .env                           # 이 서버에만 쓰는 값(VOLUME_DEVICE 등) 확인

# 3) 호스트 셋업 — 1단계가 끝나면 자동 재부팅, 2단계는 재부팅 뒤 자동 실행
sudo ./setup-ec2.sh
tail -f /var/log/ec2-setup.log     # 다른 터미널에서 진행 확인

# 4) 이미지 빌드, 메인 컨테이너 기동
docker compose build
docker compose up -d
docker compose logs -f llm
```

- 계정, 비밀번호, 토큰은 원본 `.env`에 이미 들어 있습니다.
- 추가 EBS를 붙였다면 `lsblk`로 디바이스 경로(예: `/dev/nvme1n1`)를 확인해 `VOLUME_DEVICE`에 넣습니다.
- 셋업 단계별 내용은 [5-2](#5-2-setup-ec2sh-단계), 오류는 [6-1](#6-1-호스트-셋업)을 봅니다.

---

## 3. 컨테이너 관리 (`user.sh`)

- 모든 컨테이너가 같은 이미지(`LLM_IMAGE_NAME`)를 씁니다.
- 컨테이너를 지워도 `/volume`의 데이터는 남습니다([5-3](#5-3-volume-구조)).

### 3-1. 명령

**일반 사용자** (SSH 접속, 포트 자동 할당)

```bash
sudo ~/aws/user.sh up jin   --password 1234 --gpus 2,3
sudo ~/aws/user.sh up cho   --password 1234 --gpus 0

# 기본 포트 외에 포트 구간이 더 필요할 때 (여러 구간은 콤마로)
sudo ~/aws/user.sh up demo  --password 1234 --gpus 0 --extra-ports 5100-5149
sudo ~/aws/user.sh up demo2 --password 1234 --gpus 0 --extra-ports 5020-5029,5100-5149
```

**서비스용 root 컨테이너** (SSH 없음, `docker exec`로 접근)

```bash
sudo ~/aws/user.sh up llm-serving --root --password <pw> --service-port 5501 --gpus 0
sudo ~/aws/user.sh up gemma       --root --password <pw> --service-port 5015 --gpus 2,3
sudo ~/aws/user.sh up mail        --root --password <pw> --service-port 5032 --gpus none
```

**관리**

```bash
sudo ~/aws/user.sh list              # 목록
sudo ~/aws/user.sh down jin          # 중지 후 제거 (데이터는 남음)
sudo ~/aws/user.sh rebuild jin       # 지금 이미지로 다시 만들기 (설정 유지)
sudo ~/aws/user.sh rebuild           # user.sh 컨테이너 전부 다시 만들기
```

**주의**

- `--password`를 빼면 비밀번호가 `changeme`가 됩니다.
- root 컨테이너를 여러 개 띄울 때는 `--service-port`를 컨테이너마다 다르게 줍니다. 빼면 `.env`의 `LLM_EXTRA_PORTS`를 써서 메인 컨테이너와 포트가 겹칩니다.
- `--extra-ports`는 일반 사용자 전용, `--service-port`는 root 컨테이너 전용입니다.
- 포트 구간은 필요한 만큼만 엽니다. 포트마다 호스트에 docker-proxy 프로세스가 생깁니다.
- `rebuild`는 비밀번호, GPU, 모드, 포트를 그대로 가져갑니다. 이 값을 바꾸려면 `down` 후 `up`을 다시 합니다.

### 3-2. 포트 할당

| 컨테이너 | SSH 포트 | 서비스 포트 |
|---|:---:|:---:|
| 메인 (`docker compose`) | `LLM_SSH_PORT` (5000) | `LLM_EXTRA_PORTS` |
| `user.sh` 일반 사용자 | 5010, 5020, … 5490 | SSH 다음 9개 (예: 5011-5019) |
| `user.sh --root` | 없음 | `--service-port` 값 |

- 일반 사용자는 비어 있는 번호 중 가장 작은 것을 받습니다. 최대 49명입니다.
- 메인 컨테이너와 root 컨테이너는 이 번호를 차지하지 않습니다.

### 3-3. 접속

| 대상 | 방법 |
|---|---|
| 일반 사용자 컨테이너 | `ssh -p <SSH 포트> <이름>@<호스트>`. `~/.ssh/config` 예시는 `ssh-config-sample` |
| root 컨테이너, 운영 메인 컨테이너 | 호스트에서 `sudo docker exec -it <컨테이너 이름> bash` |
| 호스트 (폐쇄망) | `aws ssm start-session --target i-<INSTANCE_ID>` |

- 컨테이너 이름은 `user.sh`로 만든 것은 지정한 이름, 메인은 `llm-<USERNAME>`(운영은 `llm-root`)입니다.

---

## 4. 업데이트

### 4-1. 코드 변경

```bash
# 로컬
cd /workspace/ai-infra/aws && ./start.sh push

# 서버
cd ~/aws && ./start.sh pull
docker compose build --no-cache
docker compose up -d                 # 메인 컨테이너
sudo ~/aws/user.sh rebuild           # user.sh 컨테이너 전부. 하나만이면 이름을 붙인다
```

- `pull`은 `.env`를 바꾸지 않습니다. 원본을 고쳤다면 `cp .env.prd .env`를 다시 합니다.

### 4-2. `.env`만 변경

이미지는 다시 빌드하지 않습니다.

```bash
docker compose up -d --force-recreate   # 메인 컨테이너
sudo ~/aws/user.sh rebuild              # user.sh 컨테이너 전부. 하나만이면 이름을 붙인다
```

- `rebuild`는 비밀번호, GPU, 모드, 포트를 유지합니다. 이 값을 바꾸려면 다시 만듭니다.

```bash
sudo ~/aws/user.sh down jin
sudo ~/aws/user.sh up jin --password new_pw --gpus 0,1
```

### 4-3. vLLM 0.31.0 버전업 (이미 셋업된 서버)

**바뀌는 것**

- 이미지: 베이스가 `vllm/vllm-openai:v0.31.0`이 됩니다.
- `.env` 두 줄: `VLLM_IMAGE`(0.31.0 다이제스트), `EXTRA_REQUIREMENTS`(비움).
- 서빙 코드: `llm-serving/`.
- 추론 규칙: 게이트웨이를 거친 요청에 `reasoning_effort`가 있으면 추론이 켜집니다(`enable_thinking`을 직접 보낸 요청은 그 값을 따름). 지금까지는 effort만으로 켜지지 않았습니다. 상세는 [`VLLM_OPS_GUIDE.md` §10.4](../llm-serving/VLLM_OPS_GUIDE.md#104-모델-교체-호환-계층-compat).
- 호스트 셋업(`setup-ec2.sh`)은 다시 하지 않습니다. 지금 운영 이미지도 CUDA 13 기반이라 드라이버 조건이 같습니다.

**1) 로컬 → S3**

```bash
cd /workspace/ai-infra/aws && ./start.sh push
cd /workspace/ai-infra/llm-serving && ./start.sh push
```

**2) 운영 중인 서버만: 게이트웨이를 먼저 확인**

```bash
# 서빙 컨테이너 안 — 아직 옛 vLLM이 떠 있는 상태
cd /workspace/llm-serving && ./start.sh pull
cd vllm && ./start.sh restart 5501 && ./start.sh test 5501
```

- 새 게이트웨이가 옛 vLLM에서 시험을 통과해야 다음으로 갑니다.
- 게이트웨이를 거치지 않고 vLLM 포트(:7070)에 직접 붙는 클라이언트가 있는지 확인합니다. 있으면 멈추고 검토합니다. 0.31은 `reasoning_effort`만 보낸 요청에서 사고 과정(thinking)을 켜는 방식이 다릅니다.

**3) 서버 호스트: 코드 받기, `.env` 확인**

```bash
cd ~/aws && ./start.sh pull
cp .env.prd .env                     # 개발 서버는 .env.dev
grep -E '^(VLLM_IMAGE|EXTRA_REQUIREMENTS)=' .env
#   VLLM_IMAGE=vllm/vllm-openai:v0.31.0@sha256:c1c9f6fd5c109ba7f0546a59f5b2f15fb87f64c77782e90a27b648b42a8e67c3
#   EXTRA_REQUIREMENTS=              ← 비어 있어야 한다
```

- 이 서버의 `.env`를 따로 고쳐 둔 값(`VOLUME_DEVICE` 등)이 있으면 `cp` 대신 위 두 줄만 고칩니다.

**4) 이미지 빌드**

```bash
IMG=$(grep '^LLM_IMAGE_NAME=' .env | cut -d= -f2)      # 운영 llm-prd, 개발 llm-dev

# 되돌리기용 태그: 지금 서빙 컨테이너가 쓰는 이미지에 남긴다 (새 서버면 생략)
docker tag "$(docker inspect -f '{{.Image}}' <서빙 컨테이너>)" "$IMG:pre-0.31"

docker compose build
docker run --rm --entrypoint cat "$IMG" /opt/image-core-final.txt | tee ~/image-core-0.31.0.txt
```

- 빌드는 베이스 이미지(약 9GB)를 먼저 받습니다.
- 빌드 첫 단계에서 베이스의 vLLM 버전을 확인합니다. `.env`가 옛 값이면 여기서 멈춥니다([6-2](#6-2-이미지-빌드)).
- 마지막 명령은 핵심 패키지 버전을 출력합니다. 첫 줄이 `vllm==0.31.0`이어야 합니다.
- 처음 빌드한 서버(개발 서버)의 출력이 기준입니다. 운영 서버의 출력이 이와 다르면 멈춥니다.
- 빌드가 끝나면 이후 `user.sh`로 만드는 컨테이너는 모두 새 이미지를 씁니다. 확인을 마칠 때까지 다른 컨테이너를 다시 만들지 않습니다.

**5) 서빙 컨테이너를 새 이미지로**

```bash
sudo ./user.sh rebuild <서빙 컨테이너>     # 이미 있는 user.sh 컨테이너. 이름을 꼭 붙인다
sudo ./user.sh up llm-serving --root --password <pw> --service-port 5501 --gpus 0   # 새로 만들 때
docker compose up -d --force-recreate     # 메인 컨테이너(llm-root)로 서빙하는 서버
```

- `rebuild`에 이름을 빼면 `user.sh` 컨테이너가 전부 다시 만들어집니다.

**6) 컨테이너 안: 코드 받기, 기동, 확인**

```bash
sudo docker exec -it <서빙 컨테이너> bash

# 서빙 코드 받기
cd /workspace/llm-serving && ./start.sh pull
#   새 컨테이너라 폴더가 없으면 처음 한 번만:
#   aws s3 sync s3://hgi-ai-res/hjjo/llm-serving/ /workspace/llm-serving/
#   chmod +x /workspace/llm-serving/start.sh /workspace/llm-serving/*/start.sh

# 기동
cd /workspace/llm-serving/vllm
./start.sh up prd-gemma && ./start.sh up 5501
./start.sh status                    # prd-gemma가 [UP]이 될 때까지 기다린다 (1~5분)

# 확인
grep -o 'speculative_config=[A-Za-z]*' logs/vllm_prd-gemma.log | tail -1   # speculative_config=None
./start.sh test 5501
```

- 코드 받기를 건너뛰지 않습니다. 새 이미지에 옛 서빙 코드를 쓰면 `reasoning_effort`만 보낸 요청에서 사고 과정이 켜집니다.
- `speculative_config=None`은 MTP(다중 토큰 예측)가 꺼져 있다는 뜻입니다. Gemma·Qwen 인스턴스는 모두 MTP를 끕니다.
- 로그에 `fp8 ... deprecated, use fp8_per_tensor` 경고가 나오면 옛 서빙 코드입니다. 지금 설정은 `fp8_per_tensor`라 이 경고가 나오지 않습니다. 코드 받기부터 다시 합니다.
- PII 모드로 운영하는 서버는 기동 명령이 다릅니다: [`DEPLOY_GUIDE.md` §3.2](../llm-serving/DEPLOY_GUIDE.md#32-gemma-기동-비pii-기본--pii-모드).

**되돌리기**

```bash
cd ~/aws && IMG=$(grep '^LLM_IMAGE_NAME=' .env | cut -d= -f2)
docker tag "$IMG:pre-0.31" "$IMG"
sudo ./user.sh rebuild <서빙 컨테이너>     # 또는 5)에서 쓴 방법으로 다시 만든다
```

- 서빙 코드는 옛 vLLM에서도 동작하므로 그대로 둡니다.
- 옛 이미지(0.20.2 + nightly 휠)는 지금 `Dockerfile.llm`으로 다시 빌드할 수 없습니다. `pre-0.31` 태그 이미지를 지우지 않습니다.

---

## 5. 참고

### 5-1. `.env` 주요 키

전체 키와 기본값은 `.env.dev`, `.env.prd`에 있습니다. (필수) 표시가 없는 키는 기본값을 써도 됩니다.

| 구분 | 키 | 설명 |
|---|---|---|
| 계정 | `MODE` | `dev` 또는 `prd` (필수) |
| | `USERNAME` | 컨테이너 OS 계정. 운영은 `root` (필수) |
| | `PASSWORD` | SSH 비밀번호 (필수) |
| | `CONTAINER_UID` / `GID` | 컨테이너 사용자 UID/GID (기본 2000). 호스트의 같은 사용자가 다른 UID면 그 값으로 맞춤 |
| | `SSH_PORT` | 호스트 SSH 포트 (기본 5555, 22 안 씀). fail2ban도 이 포트에 적용 |
| | `HF_TOKEN` | HuggingFace 토큰. 접근 승인이 필요한 모델에 필수 |
| 저장소 | `VOLUME_DEVICE` | 추가 EBS 디바이스 경로. 비우면 루트 디스크에 `/volume`을 만듦 (인스턴스 종료 시 사라짐) |
| | `VOLUME_PATH` | 마운트 경로 (기본 `/volume`) |
| 이미지 | `VLLM_IMAGE` | 베이스 이미지. 태그와 다이제스트를 함께 적음 (지금 `vllm/vllm-openai:v0.31.0@sha256:c1c9f6fd…`). 바꾸면 `Dockerfile.llm`의 `ARG VLLM_VERSION`도 같이 바꿈. 둘이 다르면 빌드 첫 단계에서 멈춤 (필수) |
| | `LLM_IMAGE_NAME` | 빌드한 이미지 이름 (`llm-dev`, `llm-prd`). compose와 `user.sh`가 함께 씀 |
| | `EXTRA_REQUIREMENTS` | 비워 둠. 컨테이너가 뜰 때마다 pip로 더 설치할 파일 경로. 서빙 패키지는 이미지 빌드 때 들어감. 값을 주면 vLLM·torch·transformers 버전을 바꾸는 패키지는 설치에 실패하고 컨테이너가 멈춤 |
| | `CUDA_TEST_IMAGE` | 셋업 2단계의 GPU 연동 확인용 이미지 |
| 메인 컨테이너 | `LLM_SSH_PORT` | SSH 포트 (기본 5000) |
| | `LLM_EXTRA_PORTS` | 서비스 포트. 단일(`5031`) 또는 구간(`5001-5009`) |
| | `LLM_GPUS` | 쓸 GPU. `all` 또는 `0,1` |
| | `LLM_MEMORY` | 메모리 한도 (`.env.dev` 48g, `.env.prd` 128g) |
| | `SHM_SIZE` | 공유 메모리. GPU 여러 장 사이 통신용 (기본 16g) |

### 5-2. `setup-ec2.sh` 단계

**1단계 (재부팅 전)**

| # | 내용 |
|:-:|---|
| 1 | OS 사용자 생성, sudo 권한. `USERNAME=root`면 건너뜀. 기존 사용자의 UID/GID가 `.env`와 다르면 중단 |
| 2 | SSH 포트 변경(`SSH_PORT`), 비밀번호 로그인 허용, fail2ban |
| 3 | EBS 포맷(xfs), 마운트, fstab 등록. `VOLUME_DEVICE`가 비어 있으면 폴더만 만듦 |
| 4 | `/volume` 아래 폴더 생성 ([5-3](#5-3-volume-구조)) |
| 5 | 시스템 업데이트, 커널 헤더, gcc·dkms·pip, 호스트 GPU 모니터링용 `nvitop` |
| 6 | Docker 설치. `ec2-user`, `ssm-user`, `USERNAME`을 docker 그룹에 추가 |
| 7 | Docker Compose V2, Buildx (0.17.0 미만이면 0.21.2로 다시 설치) |
| 8 | Claude Code 설치 (dev만) |
| 9 | NVIDIA 오픈 드라이버(`nvidia-open`) 설치 후 자동 재부팅 |

**2단계 (재부팅 뒤 systemd가 자동 실행)**

| # | 내용 |
|:-:|---|
| 1 | 드라이버 확인 (`nvidia-smi`) |
| 2 | NVIDIA Container Toolkit 설치, Docker 런타임 설정 |
| 3 | Fabric Manager 설치. NVSwitch GPU(H100, H200, A100, B100, B200)일 때만 |
| 4 | `docker run --gpus all $CUDA_TEST_IMAGE nvidia-smi`로 GPU 연동 확인. 실패하면 중단 |

- 진행 확인: `tail -f /var/log/ec2-setup.log`, `systemctl status ec2-setup-phase2.service`
- 2단계는 성공과 실패에 관계없이 한 번만 실행됩니다. 재부팅이 반복되지 않습니다.

### 5-3. `/volume` 구조

```
/volume/                 # root:root 0775 (setup-ec2.sh가 생성)
├── workspace/<name>     # 컨테이너의 /workspace
├── homes/<user>         # 일반 사용자 컨테이너의 /home/<user>
├── root-homes/<name>    # user.sh --root 컨테이너의 /root (컨테이너마다 따로)
├── root                 # 운영 메인 컨테이너의 /root (첫 기동 때 생성)
├── models               # 모델 (모든 컨테이너가 같이 씀)
└── data                 # 데이터 (모든 컨테이너가 같이 씀)
```

- `models`, `data`는 `CONTAINER_UID` 소유입니다. root 컨테이너와 일반 사용자(UID 2000) 모두 쓸 수 있습니다.
- 컨테이너를 `down`해도 `/volume`은 남습니다.

---

## 6. 문제 해결

### 6-1. 호스트 셋업

| 증상 | 원인 | 해결 |
|---|---|---|
| `디바이스 또는 자식 파티션이 ... 마운트됨` | 루트·시스템 디스크나 그 파티션을 지정함 | `lsblk`로 `/`, `/boot/efi`가 붙지 않은 추가 EBS만 지정. 추가 EBS가 없으면 `VOLUME_DEVICE`를 비움 |
| `기존 파티션이 존재합니다` | 데이터가 파티션(`/dev/nvme1n1p1`)에 있는데 디스크 전체(`/dev/nvme1n1`)를 지정함. 데이터 보호를 위해 멈춤 | 파티션 경로를 직접 지정하거나 새 EBS를 씀 |
| `UUID를 읽을 수 없습니다. fstab 등록 건너뜀` | fstab에 등록되지 않아 재부팅하면 `/volume`이 마운트되지 않음 | `blkid <device>`로 UUID를 확인하고 `/etc/fstab`에 `UUID=<uuid> /volume xfs defaults,nofail 0 2` 추가 |
| `사용자 UID/GID 불일치` | 호스트의 기존 사용자가 `.env`와 다른 UID/GID로 만들어져 있음 | `.env`의 `CONTAINER_UID`/`GID`를 오류에 나온 값으로 맞추고 다시 실행. `/volume` 데이터는 그대로 |
| `Docker GPU 테스트 실패` | 2단계 4번(GPU 연동 확인) 실패 | `systemctl restart docker` 후 `docker run --rm --gpus all $CUDA_TEST_IMAGE nvidia-smi`. 정상이면 `sudo ./setup-ec2.sh --phase2` |
| `nvidia-smi` 실패 | 2단계가 끝나지 않음 | `tail -f /var/log/ec2-setup.log`, `sudo systemctl status ec2-setup-phase2.service` |
| Fabric Manager 설치 실패 | NVSwitch GPU에서 자동 설치가 안 됨 | 로그 안내대로 `dnf module install -y nvidia-driver:<branch>-open/fm` |
| `nvitop` 실행 안 됨 | 1단계 자동 설치 실패 | `pip3 install --break-system-packages nvitop` |
| Claude Code 설치 실패 | 폐쇄망 (dev 모드만 시도, 컨테이너는 정상 기동) | `curl -fsSL https://claude.ai/install.sh \| bash` |

### 6-2. 이미지 빌드

| 증상 | 원인 | 해결 |
|---|---|---|
| `buildx` 버전 오류 | AL2023 기본 buildx가 0.17.0 미만 | `setup-ec2.sh`를 다시 실행하면 0.21.2로 바꿈. 직접: `curl -fsSL https://github.com/docker/buildx/releases/download/v0.21.2/buildx-v0.21.2.linux-amd64 -o /usr/libexec/docker/cli-plugins/docker-buildx && chmod +x $_` |
| `베이스 이미지의 vLLM X != 0.31.0` | `.env`의 `VLLM_IMAGE`가 옛 값 | `cp .env.prd .env`(개발 서버는 `.env.dev`)를 다시 하거나 `VLLM_IMAGE`, `EXTRA_REQUIREMENTS` 두 줄을 [4-3](#4-3-vllm-0310-버전업-이미-셋업된-서버) 값으로 고침 |
| pip `ResolutionImpossible` / `Cannot install` | `requirements.txt`의 패키지가 베이스의 핵심 패키지(vLLM, torch, transformers, FlashInfer 등) 버전을 바꾸려 함. 목록은 `gen-core-constraints.py` | 그 패키지를 베이스와 맞는 버전으로 고침. 핵심 패키지 버전은 베이스 이미지가 정하므로 requirements에서 바꾸지 않음 |

### 6-3. 컨테이너

| 증상 | 원인 | 해결 |
|---|---|---|
| 기동 직후 멈추고 로그에 `==> 추가 패키지 설치` 뒤 pip 오류 | `EXTRA_REQUIREMENTS`의 패키지가 핵심 패키지 버전을 바꾸려 함 | `.env`에서 `EXTRA_REQUIREMENTS`를 비우고 `user.sh rebuild <이름>` |
| `user.sh up` 때 포트 범위 초과 | 일반 사용자 컨테이너가 49개 | 쓰지 않는 컨테이너를 `down` |
