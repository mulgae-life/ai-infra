# 온프레미스 H200 서버 (RHEL 9 + vLLM)

사내 H200 서버에 vLLM 기반 LLM 환경을 띄우는 가이드. AWS EC2와 같은 `server-setup/` 폴더를 씁니다.

- 호스트 셋업만 서버 종류별로 다릅니다: AWS는 `setup-ec2.sh`, 온프레미스는 `setup-host.sh`
- 컨테이너 계층(`docker-compose.yml`, `user.sh`, `Dockerfile.llm` 등)과 `start.sh`는 공용입니다. 사용법은 [`SETUP_GUIDE.md`](SETUP_GUIDE.md)
- 어느 서버인지는 `.env`의 `PLATFORM`(`aws` | `onprem`)으로 구분합니다. 온프레미스 원본은 `.env.onprem`

AWS와 다른 점입니다.

| 항목 | AWS | 온프레미스 |
|------|------|------|
| 호스트 OS | Amazon Linux 2023 | RHEL 9.8 (스크립트는 RHEL 10도 지원) |
| 호스트 셋업 | `setup-ec2.sh` | `setup-host.sh` |
| `.env` 원본 | `.env.dev`, `.env.prd` (`PLATFORM=aws`) | `.env.onprem` (`PLATFORM=onprem`) |
| 코드 전달 | S3 sync (`start.sh push/pull`) | git clone/pull(`start.sh pull`) + `.env`는 scp |
| 디스크 | `/volume` 하나 | 설치팀이 만든 `/appdata`, `/data`, `/model`을 나눠 씀 (§4) |
| 네트워크 | 상시 | **세팅 시점만 개방, 이후 끊길 수 있음** → 끊기 전 `start.sh check` |
| 호스트 접속 | SSM | 호스트 SSH (`SSH_PORT`) |

---

## 1. 서버 사양 (서버 구성 요청서 기준)

요청 원본은 `서버구성요청서_AI연구서버.docx`(2026-11-06, 호스트명 `honp-rn-ai-airap01`)입니다.

| 항목 | 값 | 비고 |
|------|------|------|
| **OS** | RHEL 9.8 | 사내 고정. 구독 등록까지 요청 |
| **GPU** | H200 × 4 | HGX(NVSwitch)인지 PCIe인지에 따라 Fabric Manager 여부가 갈림 (§5-2) |
| **CPU / RAM** | 64코어 / 512GB | |
| **NVIDIA Driver** | **580.196.07** (open kernel module) | R580은 LTSB로 **2028-06**까지 지원 |
| **Docker Engine** | 29.9.3 (Docker CE) | **RHEL 기본 Podman 아님** |
| **NVIDIA Container Toolkit** | 1.20.1 | |
| **Fabric Manager** | 580.196.07 (드라이버와 동일) | **NVSwitch가 있을 때만** |
| **호스트 계정** | `hwada` (root 권한) | 컨테이너 계정(`.env USERNAME=root`)과 별개 |

| 파일시스템 | 용량 | 용도 |
|------|------|------|
| `/appdata` | 830GB | 작업공간·홈 (`VOLUME_PATH`) |
| `/data` | 3.57TB (3.84TB 디스크 전체) | 데이터 (`DATA_PATH`) |
| `/model` | `/data`와 같은 파일시스템 공유 | 모델 (`MODELS_PATH`) |
| `/var/lib/docker` | 400GB | Docker 이미지·컨테이너 |

설치팀이 드라이버·Docker·Toolkit을 먼저 깔아 두면 `setup-host.sh`는 이미 설치된 항목을 감지해 건너뜁니다. 단, 드라이버 버전이 `.env`의 고정값과 다르면 교체하지 않고 경고만 냅니다(§8).

세팅 기간에는 GitHub·PyPI·HuggingFace·NVIDIA/Docker 저장소·EPEL이 열려 있어야 합니다. 이미지·모델·휠을 이때 다 받습니다.

> 출처: [NVIDIA 지원 드라이버·CUDA 표](https://docs.nvidia.com/datacenter/tesla/drivers/supported-drivers-and-cuda-toolkit-versions.html), [RHEL Docker 설치](https://docs.docker.com/engine/install/rhel/), [Container Toolkit 설치](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). 패키지 존재는 2026-11-24 저장소 목록에서 확인: NVIDIA rhel9 `nvidia-open-580.196.07-1.el9`·`nvidia-fabricmanager-580.196.07-1.el9`(모듈 스트림 `nvidia-driver:580-open`), Toolkit `1.20.1-1`, Docker CE `29.9.3-1.el9`, EPEL 9.

---

## 2. 사전 준비

| 항목 | 내용 |
|------|------|
| 서버 | RHEL 9.8, NVIDIA 드라이버 580.196.07 설치(또는 미설치 — 스크립트가 설치), 구독 등록 완료(`dnf repolist`에 BaseOS), 파일시스템 `/appdata`·`/data`·`/model` 생성 완료 |
| 권한 | `sudo` 가능한 OS 계정 |
| 네트워크 | 세팅 중 개방 (§1) |
| 개발 머신에서 가져갈 것 | `server-setup/.env.onprem` (git 미추적) |

> 💡 본 인프라는 **내부망 전용**입니다. `.env`의 `HF_TOKEN`/`PASSWORD`는 내부 정책으로 보호되므로 별도 마스킹하지 않습니다.

---

## 3. 빠른 시작

### 3-1. 개발 머신에서 준비

```bash
# .env.onprem 의 서버 고유값 확인 (VOLUME_DEVICE는 비워 둔다 — 파일시스템은 설치팀이 만든다)
vim /workspace/ai-infra/server-setup/.env.onprem
```

### 3-2. 서버 최초 셋업

```bash
# (1) 부트스트랩 clone — 셋업 스크립트를 꺼내기 위한 임시 사본
git clone https://github.com/mulgae-life/ai-infra.git ~/ai-infra
cd ~/ai-infra/server-setup

# (2) 개발 머신에서 .env 전달 → server-setup/.env 로 (setup-host.sh·compose·user.sh 가 모두 이 파일을 읽는다)
#     개발 머신에서: scp /workspace/ai-infra/server-setup/.env.onprem <server>:~/ai-infra/server-setup/.env
vim .env                             # VOLUME_PATH·MODELS_PATH·DATA_PATH, SSH_PORT 등 서버 고유값 최종 확인

# (3) 호스트 셋업 (Phase 1 → 자동 reboot → Phase 2 자동 실행)
chmod +x setup-host.sh
sudo ./setup-host.sh
tail -f /var/log/onprem-setup.log    # 진행 확인 (다른 터미널)

# (4) 완료 후 작업 사본으로 이동 — Phase 1이 ${VOLUME_PATH}/workspace/root/ai-infra 에 clone하고 .env를 옮겨 둔다.
#     컨테이너 안에서 /workspace/ai-infra 로 보이는 위치라 연구계와 경로가 같다. ~/ai-infra 는 이제 안 쓴다.
cd /appdata/workspace/root/ai-infra/server-setup

# (5) 이미지 빌드 + 검증 + 기동 (vLLM은 베이스 이미지 v0.31.0 정식 빌드를 쓴다 — 따로 전달할 휠 없음)
docker compose build
docker run --rm -i --entrypoint sha256sum llm-prd -c - < image-freeze-0.31.0.txt   # 세 줄 모두 OK
docker compose up -d
docker compose logs -f llm
```

- 빌드 첫 단계에서 베이스 이미지의 vLLM 버전을 확인합니다. `.env`의 `VLLM_IMAGE`가 옛 값이면 여기서 멈춥니다.
- `sha256sum` 검증은 새 이미지가 시험을 통과한 이미지와 같은 패키지 조합인지 대조합니다. `FAILED`가 나오면 서빙을 올리지 않고 멈춥니다. 다른 부분은 `docker run --rm --entrypoint cat llm-prd /opt/image-core-final.txt`로 출력해 `image-freeze-0.31.0.txt` 안의 목록과 비교합니다.

### 3-3. 네트워크 끊기 전 (반드시)

- 모델 가중치: LLM 서빙 쪽 다운로드 명령으로 `/model` 아래에 모두 받아 둡니다. 폐쇄망에서는 새로 받을 수 없습니다.
- 런타임 pip 휠: `EXTRA_REQUIREMENTS`를 쓸 때만 §5-3.
- 마지막으로 점검합니다. 전부 ✅여야 끊어도 됩니다.

```bash
cd /appdata/workspace/root/ai-infra/server-setup && ./start.sh check
```

---

## 4. `.env` 주요 키

공용 키(계정·이미지·메인 컨테이너)는 [`SETUP_GUIDE.md` §5-1](SETUP_GUIDE.md#5-1-env-주요-키)과 같습니다. 온프레미스에서 따로 정하는 키입니다. 전체 값은 `.env.onprem`에 있습니다.

| 키 | 설명 | 값 |
|----|------|------|
| `PLATFORM` | 서버 종류. `start.sh pull`이 git으로 동작하고, `setup-ec2.sh`는 실행을 거부한다 | `onprem` |
| `NVIDIA_DRIVER_VERSION` | 설치·고정할 드라이버. 설치 후 `dnf versionlock`. RHEL 9는 이 값의 브랜치로 `nvidia-driver:<브랜치>-open` 스트림을 켠다 | `580.196.07` |
| `NVIDIA_CONTAINER_TOOLKIT_VERSION` | Toolkit 4개 패키지 공통 버전 (`-1`은 rpm 릴리스 번호) | `1.20.1-1` |
| `DOCKER_VERSION` | Docker CE 버전 고정. 값이 있으면 설치 후 `dnf versionlock`. 비우면 저장소 최신 | `29.9.3` |
| `CONTAINER_PORT_RANGE` | firewalld로 여는 컨테이너 포트 범위 | `5000-5499` |
| `VOLUME_DEVICE` | 값을 넣으면 그 디스크를 xfs로 **포맷**·마운트한다. 설치팀이 파일시스템을 만들어 주므로 **비워 둔다** | (빈값) |
| `VOLUME_PATH` | 작업공간·홈 경로 (`workspace/`, `homes/`, `root-homes/`, `root/`) | `/appdata` |
| `MODELS_PATH` / `DATA_PATH` | 컨테이너 `/models`·`/data`로 연결되는 호스트 경로. 비우면 `${VOLUME_PATH}/models`·`/data` | `/model` / `/data` |
| `LLM_MEMORY` / `SHM_SIZE` | H200 4장, 호스트 RAM 512GB 기준 | `384g` / `32g` |

---

## 5. `setup-host.sh`가 하는 일

### Phase 1 (재부팅 전) — 10단계

| 단계 | 내용 | AWS와 차이 |
|:----:|------|------|
| 0 | RHEL 9·10 확인 + 구독 저장소(BaseOS) 확인 | 신규 |
| 1 | OS 사용자 생성 + sudo (`USERNAME=root`면 스킵). UID/GID 불일치 fail-fast | 동일 |
| 2 | SSH 포트 변경 + 비밀번호 인증 + **SELinux `ssh_port_t` 등록** + **firewalld 개방** + fail2ban(EPEL) | SELinux·firewalld 신규 |
| 3 | `VOLUME_DEVICE`가 있을 때만 xfs 포맷 + 마운트 + fstab (루트 디스크 오지정 가드 동일). 비우면 디렉토리만 | EBS→NVMe, 로직 동일 |
| 4 | `${VOLUME_PATH}/{workspace,homes,root-homes}` + `MODELS_PATH`·`DATA_PATH` + 소유권 + **SELinux `container_file_t` 라벨**. 모델·데이터 경로가 마운트포인트가 아니면 경고 | 라벨·경로 분리 신규 |
| 5 | 시스템 업데이트(커널 제외) + git/gcc/dkms + `kernel-devel-matched` + versionlock 플러그인 + nvitop | 커널 패키지명 |
| 6 | **작업 사본 배치**: `${VOLUME_PATH}/workspace/root/ai-infra`에 clone + `server-setup/.env` 복사 (git 설치 뒤라 최소 설치 RHEL에서도 동작) | 신규 (S3 없음) |
| 7 | **Docker CE 공식 저장소** (podman·runc 충돌 패키지 제거 후) — compose·buildx 플러그인 동봉. `DOCKER_VERSION`이 있으면 그 버전 + versionlock | AL2023 dnf docker 아님 |
| 8 | Claude Code (dev 모드만) | 동일 |
| 9 | NVIDIA rhel9/rhel10 저장소 등록. **RHEL 9는 `nvidia-driver:<브랜치>-open` 모듈 스트림 활성화** | repo 경로 |
| 10 | `nvidia-open-<버전>` 설치 + **`dnf versionlock`** + `nvidia-persistenced` → 자동 reboot | 버전 고정 신규 |

### Phase 2 (재부팅 후 자동, systemd) — 5단계

| 단계 | 내용 |
|:----:|------|
| 1 | 드라이버 로드 확인 (`nvidia-smi`) |
| 2 | Container Toolkit 4개 패키지 버전 고정 설치 + `nvidia-ctk runtime configure` |
| 3 | Fabric Manager — **`/dev/nvidia-nvswitch*` 존재로 판단** (GPU 이름이 아니라 실제 NVSwitch). 드라이버와 같은 버전 설치 |
| 4 | **베이스 이미지 미리 pull** (`VLLM_IMAGE`, `CUDA_TEST_IMAGE`) — 폐쇄망 대비 |
| 5 | `docker run --gpus all nvidia-smi` 연동 테스트 (실패 시 fail-fast) |

> 진행 확인: `tail -f /var/log/onprem-setup.log` / `systemctl status onprem-setup-phase2.service`

### 5-1. 왜 드라이버를 잠그는가

- **RHEL 9**: 저장소가 브랜치를 **모듈 스트림**으로 나눕니다. 기본 스트림(`open-dkms`)은 최신 브랜치를 따라가므로, 스크립트가 `dnf module enable nvidia-driver:580-open`으로 580 브랜치를 켠 뒤 설치합니다. 스트림은 브랜치만 막고 같은 브랜치 안의 새 버전(580.x)으로는 올라가므로 버전도 잠급니다.
- **RHEL 10**: 스트림이 없고 580·595·610이 한 저장소에 나란히 있어, 잠그지 않으면 `dnf update`가 가장 높은 브랜치로 올려버립니다.
- 두 경우 모두 설치 직후 `dnf versionlock add 'nvidia-*' 'kmod-nvidia-*'`를 걸고, `start.sh check`가 잠금 여부를 확인합니다.

의도적으로 올릴 때는 `dnf versionlock delete 'nvidia-*'` 후 `.env NVIDIA_DRIVER_VERSION`을 바꾸고 재설치합니다. RHEL 9에서 브랜치를 바꾸면 `dnf module switch-to nvidia-driver:<새 브랜치>-open`도 필요합니다.

### 5-2. Fabric Manager 판단 기준

AWS용 `setup-ec2.sh`는 GPU 이름(H100/H200…)으로 판단했는데, 온프레미스는 **H200 NVL(PCIe 카드)** 구성도 있어 이름만으로는 NVSwitch 유무를 모릅니다. 드라이버가 NVSwitch를 잡으면 `/dev/nvidia-nvswitch0…`이 생기므로 그걸 봅니다. HGX 보드인데 감지가 안 되면 `lspci -d 10de: | grep -i bridge`로 확인하고 §8대로 수동 설치합니다.

### 5-3. 런타임 pip 오프라인 처리

> vLLM 0.31.0 전환부터 `.env.prd`의 `EXTRA_REQUIREMENTS`는 비어 있습니다. 서빙 의존성은 이미지 빌드 때 들어가므로 이 절은 값을 따로 넣은 경우에만 필요합니다. 값을 넣으면 진입점이 빌드 때의 핵심 패키지 제약을 걸어 설치합니다.

`entrypoint-llm.sh`는 **컨테이너가 뜰 때마다** `EXTRA_REQUIREMENTS`(값이 있을 때)를 `pip install`합니다. 폐쇄망에서는 PyPI에 못 나가 `set -e`로 컨테이너가 죽습니다. 컨테이너 스크립트를 고치지 않고 해결하는 방법은 pip 설정을 root 홈에 두는 것입니다 — 운영 컨테이너의 `/root`는 호스트 `/appdata/root`에 영속되므로 한 번 만들면 재생성돼도 남습니다.

```bash
# 네트워크가 열려 있을 때, 컨테이너 안에서
sudo docker exec -it llm-root bash
mkdir -p /data/pip-wheels
pip download -r /data/requirements.txt -d /data/pip-wheels        # 의존성 포함 전부 휠로
mkdir -p /root/.config/pip
cat > /root/.config/pip/pip.conf <<'EOF'
[global]
no-index = true
find-links = /data/pip-wheels
EOF
pip install --dry-run -r /data/requirements.txt                    # 오프라인 해소 확인
exit
```

`start.sh check`가 `${DATA_PATH}/pip-wheels`와 `${VOLUME_PATH}/root/.config/pip/pip.conf`를 함께 봅니다. `user.sh --root <name>` 컨테이너는 홈이 `${VOLUME_PATH}/root-homes/<name>`이라 `pip.conf`를 그쪽에도 복사해야 합니다.

---

## 6. 컨테이너 관리 (`user.sh`)

명령·포트 할당·접속은 [`SETUP_GUIDE.md` §3](SETUP_GUIDE.md#3-컨테이너-관리-usersh)과 같습니다. 온프레미스에서 다른 점입니다.

- 명령은 작업 사본에서 실행합니다: `cd /appdata/workspace/root/ai-infra/server-setup && sudo ./user.sh ...`
- 호스트 접속은 SSM 대신 호스트 SSH입니다: `ssh -p <SSH_PORT> <계정>@<호스트>`
- firewalld는 `CONTAINER_PORT_RANGE`(5000-5499)만 엽니다. 이 밖의 포트를 쓰면 직접 열어야 합니다.

디렉토리는 [`SETUP_GUIDE.md` §5-3](SETUP_GUIDE.md#5-3-volume-구조)의 `/volume`이 `/appdata`이고, `models`·`data`만 따로 나뉩니다.

```
/appdata/                # VOLUME_PATH
├── workspace/<name>     # 컨테이너의 /workspace (작업 사본은 workspace/root/ai-infra)
├── homes/<user>         # 일반 사용자 컨테이너의 /home/<user>
├── root-homes/<name>    # user.sh --root 컨테이너의 /root
└── root                 # 메인 컨테이너의 /root
/model                   # MODELS_PATH → 컨테이너 /models (모든 컨테이너 공유)
/data                    # DATA_PATH   → 컨테이너 /data   (모든 컨테이너 공유)
```

- `setup-host.sh`가 `/appdata`를 `root:root 0775`로 맞춥니다. 설치팀이 정한 권한과 다르면 확인합니다.

---

## 7. 유지보수

### 7-1. 코드 변경 반영

```bash
# 네트워크 개방 시
cd /appdata/workspace/root/ai-infra/server-setup && ./start.sh pull
docker compose build --no-cache && docker compose up -d     # 메인 컨테이너
sudo ./user.sh rebuild                                       # user.sh 컨테이너 전부

# 네트워크 폐쇄 시 — 개발 머신에서 밀어 넣기 (.git 제외, .env 보존)
rsync -av --delete --exclude .git --exclude .env --exclude .archive --exclude logs \
      /workspace/ai-infra/ <server>:/appdata/workspace/root/ai-infra/
```

`.env`는 git 밖이라 `pull`로 안 따라옵니다. 바뀌었으면 scp로 따로 옮깁니다.

### 7-2. `.env`만 수정한 경우

이미지는 다시 빌드하지 않습니다.

```bash
docker compose up -d --force-recreate   # 메인 컨테이너
sudo ./user.sh rebuild                  # user.sh 컨테이너 전부. 하나만이면 이름을 붙인다
```

`NVIDIA_*`·`DOCKER_VERSION`·`VOLUME_DEVICE`·`SSH_PORT`는 호스트 값이라 `setup-host.sh`를 다시 돌려야 반영됩니다(멱등).

---

## 8. 트러블슈팅

| 증상 | 원인 / 해결 |
|------|-------------|
| `RHEL BaseOS 저장소가 활성화되지 않았습니다` | 구독 미등록. `subscription-manager register --auto-attach` 후 재실행 |
| `nvidia-driver:580-open 활성화 실패` (RHEL 9) | 다른 스트림(예: 설치팀이 쓴 `open-dkms`)이 이미 켜져 있음. `dnf module list nvidia-driver`로 확인 후 `dnf module switch-to -y nvidia-driver:580-open` |
| `설치된 드라이버 X ≠ .env NVIDIA_DRIVER_VERSION` 경고 | 설치팀이 다른 버전을 깔아 둔 경우. 스크립트는 교체하지 않는다(원격 세션 단절 위험). 교체: `dnf versionlock delete 'nvidia-*'; dnf remove -y 'nvidia-*' 'kmod-nvidia-*'; reboot` 후 재실행 |
| Phase 2 `NVIDIA 드라이버가 로드되지 않았습니다` | dkms 빌드 실패가 대부분. `dkms status`, `uname -r`과 `rpm -q kernel-devel` 버전 일치 확인. 커널이 올라갔으면 `dnf install kernel-devel-matched && dkms autoinstall` |
| SSH 재시작 후 접속 불가 | SELinux가 `SSH_PORT` 바인딩 거부. 콘솔에서 `semanage port -a -t ssh_port_t -p tcp <포트>` (스크립트가 하지만 `policycoreutils-python-utils` 설치 실패 시 누락) |
| 외부에서 컨테이너 포트 안 보임 | firewalld. `firewall-cmd --list-ports`에 `5000-5499/tcp` 있는지, 없으면 `--permanent --add-port` |
| `docker compose build`가 `vllm/vllm-openai` pull에서 멈춤 | 폐쇄망인데 Phase 2 pull이 안 된 경우. 네트워크 개방 후 `docker pull <VLLM_IMAGE>` |
| 빌드 중 `베이스 이미지의 vLLM X != 0.31.0` | `.env`의 `VLLM_IMAGE`가 옛 값. `.env.prd`의 값으로 고침 |
| pip `ResolutionImpossible` / `Cannot install` | `requirements.txt`의 패키지가 베이스의 핵심 패키지(vLLM, torch, transformers 등) 버전을 바꾸려 함. 목록은 `gen-core-constraints.py`. 그 패키지를 베이스와 맞는 버전으로 고침 |
| 컨테이너가 기동 직후 죽고 로그에 `pip install` 에러 | 폐쇄망에서 `EXTRA_REQUIREMENTS` 설치 실패(§5-3), 또는 핵심 패키지 버전을 바꾸려 함. `.env`에서 비우고 `user.sh rebuild <이름>` |
| `user.sh up` 때 포트 범위 초과 | 일반 사용자 컨테이너가 49개. 쓰지 않는 컨테이너를 `down` |
| `tensor_parallel_size: 4` 기동 시 NCCL 에러 | HGX인데 Fabric Manager 미기동. `systemctl status nvidia-fabricmanager`, `ls /dev/nvidia-nvswitch*`. 수동: `dnf install -y nvidia-fabricmanager-<드라이버버전> libnvidia-nscq libnvsdm nvidia-imex && systemctl enable --now nvidia-fabricmanager` |
| `nvidia-smi`는 되는데 `docker run --gpus all` 실패 | `nvidia-ctk runtime configure --runtime=docker && systemctl restart docker` 후 `sudo ./setup-host.sh --phase2` |
| `dnf update` 후 `nvidia-smi` 버전이 바뀜 | versionlock 누락. `dnf versionlock list \| grep nvidia`가 비어 있으면 `setup-host.sh` 재실행(잠금만 다시 건다) |
| `docker-compose.yml`의 `apparmor=unconfined` 경고 | RHEL은 AppArmor가 없다. Docker가 해당 옵션을 무시하는지는 **실기동에서 확인 필요** — 에러가 나면 compose에서 그 줄을 빼야 한다 |
