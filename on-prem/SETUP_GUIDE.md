# 온프레미스 H200 서버 (RHEL 10 + vLLM)

사내 H200 서버에 vLLM 기반 LLM 환경을 띄우는 호스트 셋업 가이드. [`../aws/`](../aws/)의 EC2 구성을 온프레미스로 옮긴 것으로, **호스트 계층(드라이버·Docker·디스크·방화벽)만 여기서 다루고 컨테이너 계층(`docker compose`, `user.sh`, `Dockerfile.llm`)은 `../aws/`를 그대로 실행합니다.** 컨테이너 계층은 호스트 OS와 무관하고 두 벌로 나누면 고칠 때마다 어긋나기 때문입니다.

AWS와 다른 점은 셋뿐입니다.

| 항목 | AWS (`aws/`) | 온프레미스 (`on-prem/`) |
|------|------|------|
| 호스트 OS | Amazon Linux 2023 | RHEL 10 |
| 코드 전달 | S3 sync (`start.sh push/pull`) | git clone/pull + `.env`는 scp |
| 네트워크 | 상시 | **세팅 시점만 개방, 이후 끊길 수 있음** → 끊기 전 `start.sh check` |

---

## 1. 설치팀에 전달하는 사양

| 항목 | 버전 | 근거 |
|------|------|------|
| **OS** | RHEL 10 (최신 마이너) | 기본 Python 3.12(BaseOS `python3`, RHEL 10 수명 내내 고정) — 컨테이너 안과 동일. 구독 등록까지 요청 |
| **NVIDIA Driver** | **580.178.04** (open kernel module) | R580은 LTSB로 **2028-06**까지 지원. R610은 번호가 크지만 NFB라 2026-08 종료, R595는 PB로 2027-03 종료 |
| **CUDA Toolkit** | 13.0 (호스트 설치 선택) | 컨테이너 안 PyTorch가 `cu130` 빌드. 호스트에 깔 거면 같은 버전으로 |
| **Python** | 3.12 | RHEL 10 기본 |
| **Docker Engine** | 29.x (2026-08 최신 안정) | Docker CE 공식 저장소. **RHEL 기본 Podman 아님** — 명시 필수 |
| **NVIDIA Container Toolkit** | 1.20.0 | 2026-08-13 릴리스 |
| **Fabric Manager** | 580.178.04 (드라이버와 동일) | **HGX 보드(NVSwitch)일 때만.** PCIe 카드 구성이면 불필요 |

설치팀은 **드라이버까지만** 맡기고 Docker·Toolkit·Fabric Manager는 `setup-host.sh`가 설치해도 됩니다. 어느 쪽이든 스크립트는 이미 설치된 항목을 감지해 건너뜁니다. 단, 드라이버 버전이 `.env`의 고정값과 다르면 교체하지 않고 경고만 냅니다(§7).

추가로 확인할 하드웨어 항목입니다.

| 항목 | 요청 값 | 이유 |
|------|------|------|
| GPU 구성 | HGX(8장 한 판) / PCIe(개별 카드) 중 어느 것인지 | Fabric Manager 필요 여부가 갈림 |
| 모델용 디스크 | NVMe 2TB 이상, OS 디스크와 **별도** | 27B FP8 하나가 30GB급, 여러 모델 보관. `lsblk` 경로를 받아 `.env VOLUME_DEVICE`에 기입 |
| 시스템 RAM | GPU 총 VRAM(8×141GB)의 1.5배 이상 → 1TB 권장 | 모델 로드 시 가중치가 CPU RAM을 한 번 거침 |
| 네트워크 | 세팅 기간 동안 GitHub·PyPI·HuggingFace·NVIDIA/Docker 저장소 개방 | 이미지·모델·휠을 이때 다 받는다 |

> 출처: [NVIDIA 지원 드라이버·CUDA 표](https://docs.nvidia.com/datacenter/tesla/drivers/supported-drivers-and-cuda-toolkit-versions.html), [드라이버 580.178.04 릴리스 노트](https://docs.nvidia.com/datacenter/tesla/tesla-release-notes-580-178-04/index.html), [RHEL Docker 설치](https://docs.docker.com/engine/install/rhel/), [Container Toolkit 설치](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). 패키지 존재는 NVIDIA rhel10 저장소 목록에서 `nvidia-open-580.178.04-1.el10`·`nvidia-fabricmanager-580.178.04-1.el10`으로 확인(2026-08-28).

---

## 2. 사전 준비

| 항목 | 내용 |
|------|------|
| 서버 | RHEL 10, NVIDIA 드라이버 580.178.04 설치(또는 미설치 — 스크립트가 설치), 구독 등록 완료(`dnf repolist`에 BaseOS) |
| 권한 | `sudo` 가능한 OS 계정 |
| 네트워크 | 세팅 중 개방 (§1) |
| 개발 머신에서 가져갈 것 | `on-prem/.env.prd` (git 미추적) |

> 💡 본 인프라는 **내부망 전용**입니다. `.env`의 `HF_TOKEN`/`PASSWORD`는 내부 정책으로 보호되므로 별도 마스킹하지 않습니다.

---

## 3. 빠른 시작

### 3-1. 개발 머신에서 준비

```bash
# on-prem/.env.prd 의 서버 고유값 확인 (VOLUME_DEVICE는 설치팀에 받은 경로)
vim /workspace/ai-infra/on-prem/.env.prd
```

### 3-2. 서버 최초 셋업

```bash
# (1) 부트스트랩 clone — 셋업 스크립트를 꺼내기 위한 임시 사본
git clone https://github.com/mulgae-life/ai-infra.git ~/ai-infra
cd ~/ai-infra

# (2) 개발 머신에서 .env 전달 → aws/.env 로 (setup-host.sh·compose·user.sh 가 모두 이 경로를 읽는다)
#     개발 머신에서: scp /workspace/ai-infra/on-prem/.env.prd <server>:~/ai-infra/aws/.env
vim aws/.env                         # VOLUME_DEVICE, SSH_PORT 등 서버 고유값 최종 확인

# (3) 호스트 셋업 (Phase 1 → 자동 reboot → Phase 2 자동 실행)
chmod +x on-prem/setup-host.sh
sudo ./on-prem/setup-host.sh
tail -f /var/log/onprem-setup.log    # 진행 확인 (다른 터미널)

# (4) 완료 후 작업 사본으로 이동 — Phase 1이 /volume/workspace/root/ai-infra 에 clone하고 .env를 옮겨 둔다.
#     컨테이너 안에서 /workspace/ai-infra 로 보이는 위치라 연구계와 경로가 같다. ~/ai-infra 는 이제 안 쓴다.
cd /volume/workspace/root/ai-infra/aws

# (5) 컨테이너 빌드 + 기동 (vLLM은 베이스 이미지 v0.31.0 정식 빌드를 쓴다 — 따로 전달할 휠 없음)
docker compose build
docker compose up -d
docker compose logs -f llm
```

### 3-3. 네트워크 끊기 전 (반드시)

```bash
# 모델 가중치 — 컨테이너 안에서
sudo docker exec -it llm-root bash
cd /workspace/ai-infra/llm-serving/vllm && ./start.sh download all
exit

# 런타임 pip 휠 — §5-3
# 점검 — 전부 ✅ 여야 끊어도 된다
/volume/workspace/root/ai-infra/on-prem/start.sh check
```

---

## 4. `.env` 주요 키

`aws/.env.prd`와 같은 키에 아래가 추가됐습니다. 나머지는 [`../aws/SETUP_GUIDE.md` §4](../aws/SETUP_GUIDE.md#4-env-주요-키) 참조.

| 키 | 설명 | 기본 |
|----|------|------|
| `NVIDIA_DRIVER_VERSION` | 설치·고정할 드라이버. 설치 후 `dnf versionlock` | `580.178.04` |
| `NVIDIA_CONTAINER_TOOLKIT_VERSION` | Toolkit 4개 패키지 공통 버전 (`-1`은 rpm 릴리스 번호) | `1.20.0-1` |
| `CONTAINER_PORT_RANGE` | firewalld로 여는 컨테이너 포트 범위 | `5000-5499` |
| `VOLUME_DEVICE` | 모델용 NVMe (`lsblk` 확인). **온프레미스는 채우는 게 기본** — 비우면 OS 디스크에 모델이 쌓인다 | (빈값) |
| `LLM_MEMORY` / `SHM_SIZE` | H200 8장 기준 `512g` / `64g`. 호스트 RAM 확정 후 조정 | — |

---

## 5. `setup-host.sh`가 하는 일

### Phase 1 (재부팅 전) — 10단계

| 단계 | 내용 | AWS와 차이 |
|:----:|------|------|
| 0 | RHEL 10 확인 + 구독 저장소(BaseOS) 확인 | 신규 |
| 1 | OS 사용자 생성 + sudo (`USERNAME=root`면 스킵). UID/GID 불일치 fail-fast | 동일 |
| 2 | SSH 포트 변경 + 비밀번호 인증 + **SELinux `ssh_port_t` 등록** + **firewalld 개방** + fail2ban(EPEL) | SELinux·firewalld 신규 |
| 3 | 데이터 디스크 xfs 포맷 + 마운트 + fstab (루트 디스크 오지정 가드 동일) | EBS→NVMe, 로직 동일 |
| 4 | `/volume/{workspace,data,models,homes,root-homes}` + 소유권 + **SELinux `container_file_t` 라벨** | 라벨 신규 |
| 5 | 시스템 업데이트(커널 제외) + git/gcc/dkms + `kernel-devel-matched` + versionlock 플러그인 + nvitop | 커널 패키지명 |
| 6 | **작업 사본 배치**: `/volume/workspace/root/ai-infra`에 clone + `.env` 복사 (git 설치 뒤라 최소 설치 RHEL에서도 동작) | 신규 (S3 없음) |
| 7 | **Docker CE 공식 저장소** (podman·runc 충돌 패키지 제거 후) — compose·buildx 플러그인 동봉 | AL2023 dnf docker 아님 |
| 8 | Claude Code (dev 모드만) | 동일 |
| 9 | NVIDIA rhel10 저장소 등록 | repo 경로 |
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

RHEL 9까지는 `nvidia-driver:580-open` 같은 **모듈 스트림**으로 브랜치를 고정했습니다. RHEL 10 저장소는 스트림이 없고 580·595·610이 한 저장소에 나란히 있어, `dnf update`가 가장 높은 610으로 올려버립니다. 610은 이번 달 지원이 끝나는 NFB입니다. 그래서 설치 직후 `dnf versionlock add 'nvidia-*' 'kmod-nvidia-*'`를 걸고, `start.sh check`가 잠금 여부를 확인합니다.

의도적으로 올릴 때는 `dnf versionlock delete 'nvidia-*'` 후 `.env NVIDIA_DRIVER_VERSION`을 바꾸고 재설치합니다.

### 5-2. Fabric Manager 판단 기준

`aws/setup-ec2.sh`는 GPU 이름(H100/H200…)으로 판단했는데, 온프레미스는 **H200 NVL(PCIe 카드)** 구성도 있어 이름만으로는 NVSwitch 유무를 모릅니다. 드라이버가 NVSwitch를 잡으면 `/dev/nvidia-nvswitch0…`이 생기므로 그걸 봅니다. HGX 보드인데 감지가 안 되면 `lspci -d 10de: | grep -i bridge`로 확인하고 §7대로 수동 설치합니다.

### 5-3. 런타임 pip 오프라인 처리

> vLLM 0.31.0 전환부터 `.env.prd`의 `EXTRA_REQUIREMENTS`는 비어 있습니다. 서빙 의존성은 이미지 빌드 때 들어가므로 이 절은 값을 따로 넣은 경우에만 필요합니다. 값을 넣으면 진입점이 빌드 때의 핵심 패키지 제약을 걸어 설치합니다.

`aws/entrypoint-llm.sh`는 **컨테이너가 뜰 때마다** `EXTRA_REQUIREMENTS`(값이 있을 때)를 `pip install`합니다. 폐쇄망에서는 PyPI에 못 나가 `set -e`로 컨테이너가 죽습니다. 컨테이너 스크립트를 고치지 않고 해결하는 방법은 pip 설정을 root 홈에 두는 것입니다 — 운영 컨테이너의 `/root`는 호스트 `/volume/root`에 영속되므로 한 번 만들면 재생성돼도 남습니다.

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

`start.sh check`가 `/volume/data/pip-wheels`와 `/volume/root/.config/pip/pip.conf`를 함께 봅니다. `user.sh --root <name>` 컨테이너는 홈이 `/volume/root-homes/<name>`이라 `pip.conf`를 그쪽에도 복사해야 합니다.

---

## 6. 유지보수

### 6-1. 코드 변경 반영

```bash
# 네트워크 개방 시
cd /volume/workspace/root/ai-infra && on-prem/start.sh pull
cd aws && docker compose build --no-cache && docker compose up -d
sudo ./user.sh rebuild

# 네트워크 폐쇄 시 — 개발 머신에서 밀어 넣기 (.git 제외, .env 보존)
rsync -av --delete --exclude .git --exclude .env --exclude .archive --exclude logs \
      /workspace/ai-infra/ <server>:/volume/workspace/root/ai-infra/
```

`.env`는 git 밖이라 `pull`로 안 따라옵니다. 바뀌었으면 scp로 따로 옮깁니다.

### 6-2. `.env`만 수정한 경우

[`../aws/SETUP_GUIDE.md` §9-2](../aws/SETUP_GUIDE.md#9-2-env만-수정한-경우-이미지-재빌드-불필요)와 같습니다. `NVIDIA_*`·`VOLUME_DEVICE`·`SSH_PORT`는 호스트 값이라 `setup-host.sh`를 다시 돌려야 반영됩니다(멱등).

### 6-3. 다중 사용자·접속·디렉토리 구조

컨테이너 계층은 AWS와 동일합니다 — [`../aws/SETUP_GUIDE.md`](../aws/SETUP_GUIDE.md) §6(`user.sh`), §7(접속), §10(`/volume` 구조). SSM 대신 호스트 SSH(`SSH_PORT`)로 들어갑니다.

---

## 7. 트러블슈팅

| 증상 | 원인 / 해결 |
|------|-------------|
| `RHEL BaseOS 저장소가 활성화되지 않았습니다` | 구독 미등록. `subscription-manager register --auto-attach` 후 재실행 |
| `설치된 드라이버 X ≠ .env NVIDIA_DRIVER_VERSION` 경고 | 설치팀이 다른 버전을 깔아 둔 경우. 스크립트는 교체하지 않는다(원격 세션 단절 위험). 교체: `dnf versionlock delete 'nvidia-*'; dnf remove -y 'nvidia-*' 'kmod-nvidia-*'; reboot` 후 재실행 |
| Phase 2 `NVIDIA 드라이버가 로드되지 않았습니다` | dkms 빌드 실패가 대부분. `dkms status`, `uname -r`과 `rpm -q kernel-devel` 버전 일치 확인. 커널이 올라갔으면 `dnf install kernel-devel-matched && dkms autoinstall` |
| SSH 재시작 후 접속 불가 | SELinux가 `SSH_PORT` 바인딩 거부. 콘솔에서 `semanage port -a -t ssh_port_t -p tcp <포트>` (스크립트가 하지만 `policycoreutils-python-utils` 설치 실패 시 누락) |
| 외부에서 컨테이너 포트 안 보임 | firewalld. `firewall-cmd --list-ports`에 `5000-5499/tcp` 있는지, 없으면 `--permanent --add-port` |
| `docker compose build`가 `vllm/vllm-openai` pull에서 멈춤 | 폐쇄망인데 Phase 2 pull이 안 된 경우. 네트워크 개방 후 `docker pull <VLLM_IMAGE>` |
| 컨테이너가 기동 직후 죽고 로그에 `pip install` 에러 | 폐쇄망에서 `EXTRA_REQUIREMENTS` 설치 실패. §5-3 |
| `tensor_parallel_size: 8` 기동 시 NCCL 에러 | HGX인데 Fabric Manager 미기동. `systemctl status nvidia-fabricmanager`, `ls /dev/nvidia-nvswitch*`. 수동: `dnf install -y nvidia-fabricmanager-<드라이버버전> libnvidia-nscq libnvsdm nvidia-imex && systemctl enable --now nvidia-fabricmanager` |
| `nvidia-smi`는 되는데 `docker run --gpus all` 실패 | `nvidia-ctk runtime configure --runtime=docker && systemctl restart docker` 후 `sudo ./setup-host.sh --phase2` |
| `dnf update` 후 `nvidia-smi` 버전이 바뀜 | versionlock 누락. `dnf versionlock list \| grep nvidia`가 비어 있으면 `setup-host.sh` 재실행(잠금만 다시 건다) |
| `docker-compose.yml`의 `apparmor=unconfined` 경고 | RHEL은 AppArmor가 없다. Docker가 해당 옵션을 무시하는지는 **실기동에서 확인 필요** — 에러가 나면 compose에서 그 줄을 빼야 한다 |
