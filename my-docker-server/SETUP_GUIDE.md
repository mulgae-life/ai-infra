# 로컬 dev / GPU 컨테이너 (my-docker-server)

PC·사내 서버 한 대에 개발용·GPU용 컨테이너를 띄우고 SSH(VSCode Remote-SSH 포함)로 접속하는 구성.

**제공 기능**
- 풀스택 개발 컨테이너 `dev-fullstack` (Ubuntu 24.04)
- GPU 연산 컨테이너 `cfd` (CUDA 12.6)
- 코드·홈·SSH 호스트 키 호스트 보존 → 재빌드해도 유지
- Claude Code / Codex / Gemini CLI 내장
- SSH 브루트포스 대응 (컨테이너 sshd 설정 + 호스트 방화벽)

**관련 문서**
- AWS EC2 운영 인프라 → [`../aws/SETUP_GUIDE.md`](../aws/SETUP_GUIDE.md)
- LLM 서빙 → [`../llm-serving/`](../llm-serving/)

---

## 0. 한눈에 보기

### 컨테이너

| 컨테이너 | compose 서비스 | 용도 | SSH | 서비스 포트 | 메모리 | 이미지 |
|---|---|---|---|---|---|---|
| `dev-fullstack` | `dev` | 풀스택 개발 | **5010** | 5011-5019 | 24g | `Dockerfile.dev` |
| `cfd` | `cfd` | GPU 연산 + 문서/미디어 | **5000** | 5001-5009 | 24g | `Dockerfile.gpu` |

**이름 구분**
- `docker compose ...` → 서비스 이름 (`dev`, `cfd`)
- `docker exec` / `docker logs` → 컨테이너 이름 (`dev-fullstack`, `cfd`)
- 호스트 보존 경로 `/opt/docker-homes/<서비스>/` → 서비스 이름

### 파일

| 파일 | 역할 |
|---|---|
| `docker-compose.yml` | 서비스 정의 (포트·볼륨·메모리·GPU) |
| `Dockerfile.dev` / `Dockerfile.gpu` | 이미지 내용. 도구 추가 시 수정 |
| `entrypoint.sh` | 기동 시 홈 초기화 + SSH 호스트 키 보관/복원 |
| `.env` | 계정명·비밀번호·UID/GID (`.env.example` 복사, **git 제외**) |
| `sshd-hardening.conf` | 컨테이너 sshd 브루트포스 대응 (이미지에 포함) |
| `ssh-guard.sh` / `.service` | 호스트 방화벽 규칙 + 재부팅 후 자동 적용 |

---

## 1. 사전 준비

| 항목 | 내용 |
|---|---|
| OS | Linux (Ubuntu 검증) |
| Docker | Docker Engine + Compose v2 |
| GPU (cfd만) | NVIDIA 드라이버 + [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). 없으면 dev만 |
| 권한 | `sudo` 가능 계정. `docker` 그룹이면 docker 명령은 sudo 불필요 |
| 디스크 | 이미지 약 27GB (cfd 19 + dev 8). 여유 40GB 권장 |

```bash
# Docker 미설치 시
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # 재로그인 후 적용
```

---

## 2. 처음 설치

```bash
# 1) 레포 받기
git clone https://github.com/mulgae-life/ai-infra.git
cd ai-infra/my-docker-server

# 2) 계정 설정
cp .env.example .env
id -u; id -g                            # 호스트 UID/GID 확인
nano .env                               # 아래 표 참고

# 3) 빌드 + 기동 (최초는 CUDA·Playwright 계층까지 받아 오래 걸림)
docker compose up -d --build dev        # dev만
docker compose up -d --build            # 전체

# 4) 확인
docker compose ps
ssh <USERNAME>@localhost -p 5010        # dev-fullstack
ssh <USERNAME>@localhost -p 5000        # cfd
```

### `.env` 항목

| 키 | 의미 | 설정 기준 |
|---|---|---|
| `USERNAME` | 컨테이너 계정 = SSH 로그인 이름 | 호스트 계정과 동일 권장 |
| `PASSWORD` | SSH·sudo 비밀번호 | 공인 IP 노출 시 길게 |
| `UID` / `GID` | 계정 숫자 ID | **호스트와 반드시 일치** (`id -u`/`id -g`) |

- UID/GID 불일치 → `/workspace` 파일 권한 어긋남
- 기본값 2000 = 클라우드 서버 기준. 개인 PC는 보통 1000

---

## 3. 접속하기

### SSH config 예시 (접속 PC의 `~/.ssh/config`)

```
# 집 LAN
Host desktop-cfd
    HostName <호스트 LAN IP>              # 호스트에서 ip -4 addr
    User <USERNAME>
    Port 5000

# Tailscale (권장)
Host desktop-ts-cfd
    HostName <머신이름>.<tailnet>.ts.net   # 또는 100.x.y.z (tailscale ip -4)
    User <USERNAME>
    Port 5000

# 공인 IP (공유기 포트포워딩 시)
Host desktop-pub-cfd
    HostName <공인 IP 또는 DDNS>
    User <USERNAME>
    Port 5000
```

- dev-fullstack → 같은 형식, `Port 5010`
- VSCode → Remote-SSH에서 `Host` 이름 선택
- `HostName` 값 = PC `known_hosts`에 기록되는 주소 = 8절 `<호스트>`

### 경로별 특성

| 경로 | 장점 | 주의 |
|---|---|---|
| 집 LAN | 가장 빠름 | 집 안에서만 |
| Tailscale | 어디서든, 방화벽 무조건 통과, 봇 노출 없음 | 양쪽 기기에 설치 필요 |
| 공인 IP | 앱 설치 없이 접속 | 봇 상시 공격 → 7절 필수 |

### 첫 접속 시 지문 확인

- "지문(fingerprint)을 믿겠느냐" 확인이 1회 표시됨
- 서버에서 지문 조회 후 비교·수락
  ```bash
  docker exec cfd ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
  ```
- 호스트 키 보존으로 재빌드해도 지문 불변 (4절)

---

## 4. 재빌드 시 남는 것 / 사라지는 것

`docker compose down` → `up --build`로 재빌드할 때 기준.

### ✅ 남는 것 (호스트에 보존)

| 컨테이너 경로 | 호스트 위치 | 내용 |
|---|---|---|
| `/workspace` | `/workspace` | 코드·프로젝트 |
| `/home/<USERNAME>` | `/opt/docker-homes/<서비스>/<USERNAME>` | 홈 전체 |
| `/etc/ssh/hostkeys` | `/opt/docker-homes/<서비스>/ssh-hostkeys` | SSH 호스트 키 |

**홈에 포함되는 것**
- Claude Code·Codex 로그인과 대화 기록
- SSH 키, git 설정, `.bashrc`, `.tmux.conf`
- npm/pip 캐시
- 홈에 설치한 도구: `pip install --user`, `~/.local/bin`, TinyTeX(`tlmgr`)

**홈 초기값**
- 첫 기동 시 홈이 비어 있으면 → Dockerfile 초기 설정 복사
- 이후 → 기존 홈 우선 (Dockerfile의 `.bashrc` 변경은 반영 안 됨)

### ❌ 사라지는 것 (이미지 계층)

- 컨테이너 안에서 `sudo apt install` 한 패키지
- `npm install -g` 전역 패키지 (`/usr/local/nvm` 아래)
- `/etc`, `/usr/local/bin`에 직접 넣은 파일

→ 계속 쓸 도구는 **Dockerfile `# 추가 도구` 블록에 추가 후 재빌드** (5절)

---

## 5. 일상 운영

모든 명령은 `ai-infra/my-docker-server/`에서 실행.

| 목적 | 명령 |
|---|---|
| 상태 확인 | `docker compose ps` |
| sshd 로그 (접속 실패 원인) | `docker logs cfd --tail 50` |
| 재시작 (설치물 유지) | `docker compose restart cfd` |
| Dockerfile 수정 반영 | `docker compose up -d --build` |
| 컨테이너 삭제 (홈·코드 유지) | `docker compose down` |
| 컨테이너 셸 진입 | `docker exec -it cfd bash` |

**재부팅 동작**
- 컨테이너 자동 재기동 (`restart: unless-stopped`)
- 안에서 돌던 프로세스는 종료 → 긴 작업은 `tmux` 안에서

### 도구 추가 절차

1. `Dockerfile.gpu` / `Dockerfile.dev`의 `# 추가 도구` 블록에 추가
   - apt 패키지 → `apt install -y` 줄
   - npm 전역 → `npm install -g` 줄
2. `docker compose up -d --build` → 앞 단계는 캐시, 추가분만 설치
3. `docker exec cfd which <도구>`로 확인

### 홈 초기화 (Dockerfile 기본 설정으로 되돌릴 때)

```bash
docker compose down
sudo mv /opt/docker-homes/dev/<USERNAME> /opt/docker-homes/dev/<USERNAME>.bak   # 백업
docker compose up -d
```

---

## 6. 이미지 구성

### dev-fullstack

| 영역 | 구성 |
|---|---|
| 런타임 | Node.js LTS (nvm), Python 3.12 |
| 패키지 매니저 | pnpm, yarn, pip |
| 프레임워크 | Next.js, FastAPI, LangChain |
| DB/검색 | PostgreSQL client, Supabase CLI, ChromaDB |
| 크롤링/테스트 | Playwright + Chromium, BeautifulSoup |
| 문서 변환 | LibreOffice (Writer/Impress), poppler-utils |
| 도구 | Git, GitHub CLI, Claude Code, Codex, tmux, fzf, ripgrep, zip/unzip |
| 로케일 | ko_KR.UTF-8, 서울 타임존, 나눔·Noto CJK 폰트 |

### cfd

| 영역 | 구성 |
|---|---|
| 런타임 | Node.js LTS (nvm), Python 3.12, CUDA 12.6 |
| 라이브러리 | NumPy, Numba, CuPy, Matplotlib |
| 문서/미디어 | pandoc, latexdiff, poppler-utils, qpdf, ImageMagick, librsvg, ffmpeg |
| GPU 모니터링 | nvitop, nvtop |
| 도구 | Git, Claude Code, Codex, Gemini CLI, tmux, cmake, zip/unzip |
| 로케일 | ko_KR.UTF-8, 서울 타임존, 나눔·Noto CJK 폰트 |

**참고**
- pandoc PDF 출력 → TeX 필요. 이미지에 없음, 홈에 TinyTeX 설치 시 재빌드 후에도 유지
- PDF → 이미지 → poppler `pdftoppm` 권장 (ImageMagick `convert`도 가능, 내부적으로 ghostscript 사용)

---

## 7. SSH 브루트포스 대응

**문제**
- 공유기에서 SSH 포트를 외부로 열면 봇이 하루 수만 회 시도
- 봇이 sshd 미인증 좌석(`MaxStartups`) 점유 → **정상 접속이 간헐적으로 거절**

**대응** → 2계층

### 1) 컨테이너 sshd 설정 — 이미지에 포함, 작업 불필요

- `sshd-hardening.conf` → 빌드 시 `/etc/ssh/sshd_config.d/50-hardening.conf`
- sshd `-e` 옵션 → 로그가 `docker logs <컨테이너>`로 출력

| 항목 | 값 | 효과 |
|---|---|---|
| `MaxStartups` | 30:50:100 | 미인증 좌석 10 → 30 |
| `LoginGraceTime` | 30 | 좌석 점유 120초 → 30초 |
| `MaxAuthTries` | 3 | 연결당 비밀번호 시도 제한 |
| `PerSourceMaxStartups` | 3 | IP 당 동시 미인증 연결 제한 |
| `AllowUsers` | `.env` USERNAME | 다른 계정명 즉시 거부 |

### 2) 호스트 방화벽 — 1회 설치, 재부팅 후 자동 적용

**규칙** (`DOCKER-USER` 체인 — Docker 공개 포트는 `INPUT`을 거치지 않음)
- Tailscale `100.64.0.0/10` → 무조건 통과
- 집 LAN `192.168.75.0/24` → 무조건 통과
- 그 외 → IP 당 10분에 새 연결 20회 초과 시 차단
- 컨테이너 재시작 불필요

```bash
# 사전 확인: 스크립트의 LAN 대역·PORTS가 내 환경과 맞는지
chmod +x ssh-guard.sh
sudo ./ssh-guard.sh                                  # 즉시 적용 (반복 실행 안전)
sudo cp ssh-guard.service /etc/systemd/system/       # ExecStart 경로 확인
sudo systemctl daemon-reload && sudo systemctl enable --now ssh-guard.service
sudo iptables -L DOCKER-USER -v -n                   # 차단 카운터 확인
```

**운영 팁**
- 임계값 변경 → 스크립트 `--hitcount` 수정 → 기존 규칙 삭제 → 재실행
- 원천 차단 → 모든 기기를 Tailscale로 전환 + 공유기 포트포워딩 닫기

---

## 8. 문제 해결

### 🔑 "REMOTE HOST IDENTIFICATION HAS CHANGED" / VSCode 연결 직후 계속 끊김

- **확인**: `docker logs cfd`에 `Connection reset by 172.18.0.1 [preauth]` 반복
- **원인**: SSH 호스트 키 변경을 클라이언트가 거부
  - 호스트 키 보존 도입 전 빌드, 또는 `ssh-hostkeys/` 삭제·서버 이전
- **해결**: **접속 PC마다 1회**, 옛 지문 삭제 → 재접속 → 새 지문 수락
  ```bash
  ssh-keygen -R "[<호스트>]:5000"    # cfd
  ssh-keygen -R "[<호스트>]:5010"    # dev-fullstack
  ```
  - `<호스트>` = SSH config `HostName` 값. LAN·Tailscale·공인 IP 등 쓰는 주소 전부
  - 원본은 `known_hosts.old`로 자동 백업
  - 처음 접속하는 PC는 해당 없음

### 📶 접속이 됐다 안 됐다 함 (특히 공인 IP 경로)

- **확인**: `docker logs cfd`에 낯선 IP의 `Invalid user` 다수
- **원인**: 봇이 sshd 좌석 점유
- **해결**: 7절 호스트 방화벽 설치

### 📁 컨테이너 안에서 `/workspace` 파일 수정 불가

- **원인**: `.env` UID/GID ≠ 호스트 계정
- **해결**: `.env` 수정 → `docker compose up -d --build`

### 🎮 cfd에서 `nvidia-smi` 실패

- **원인**: nvidia-container-toolkit 미설치 또는 드라이버 문제
- **해결**: 호스트 `nvidia-smi` 확인 → toolkit 설치 → `sudo nvidia-ctk runtime configure --runtime=docker` → `sudo systemctl restart docker`

### 🏷️ `up` 시 "container name already in use"

- **원인**: 다른 compose 프로젝트(다른 디렉토리)에서 띄운 동명 컨테이너 존재
- **해결**:
  ```bash
  docker ps --format '{{.Names}} {{.Label "com.docker.compose.project"}}'   # 옛 프로젝트명 확인
  docker compose -p <옛 프로젝트> -f docker-compose.yml down
  docker compose up -d
  ```

### 📜 `docker logs <컨테이너>`에 sshd 로그가 안 나옴

- **원인**: `-e` 옵션 없는 옛 이미지
- **해결**: `docker compose up -d --build`

### 💾 컨테이너 `/var/log/btmp`가 수 GB

- **원인**: 봇 로그인 실패 기록 누적 (logrotate 없음)
- **해결**: 7절 방화벽 적용 → `docker exec cfd truncate -s 0 /var/log/btmp`

---

## 9. 커스터마이징

| 변경 대상 | 수정 위치 | 비고 |
|---|---|---|
| 메모리 제한 | `docker-compose.yml` → `deploy.resources.limits.memory` | 아래 표 참고 |
| 사용 GPU 수 | `docker-compose.yml` → cfd `devices.count` | `all` → `1` 등 |
| GPU 없는 환경 | `docker compose up -d dev`로 dev만 기동 | 인자 없는 `up`을 쓰려면 cfd의 `deploy` 블록 삭제 |
| CUDA 버전 | `Dockerfile.gpu` 1행 `FROM` | [태그 목록](https://hub.docker.com/r/nvidia/cuda/tags) |
| Node.js 버전 | 두 Dockerfile의 `nvm install --lts` | 예: `nvm install 22 && nvm alias default 22` |
| Python 패키지 | 각 Dockerfile `pip install --no-cache-dir` 블록 | |
| apt / npm 전역 | 각 Dockerfile `# 추가 도구` 블록 | 5절 절차 |
| 포트 범위 | `docker-compose.yml` `ports` + Dockerfile `EXPOSE` | **함께** 수정. 공인 IP 사용 시 공유기·`ssh-guard.sh` `PORTS`도 |
| 작업 디렉토리 | `docker-compose.yml` `/workspace:/workspace` 앞쪽 | 호스트 경로 |

**메모리 권장값**

| 호스트 RAM | 컨테이너당 |
|---|---|
| 16GB | 12g |
| 32GB | 24g (현재) |
| 64GB | 48g |

**Node.js 임시 변경** (컨테이너 안에서만 유효, 재빌드하면 사라짐)
```bash
nvm install 22 && nvm alias default 22   # use만 하면 현재 셸에만 적용
```
