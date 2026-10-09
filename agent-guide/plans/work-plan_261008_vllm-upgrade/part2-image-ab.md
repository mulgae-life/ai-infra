# Part 2: 이미지 반영과 A/B 시험 — P2-P3

> master: [master.md](master.md)
> 선행 Part: [part1](part1-prep-staging.md) | 후속 Part: [part3](part3-rollout-cleanup.md)
> 담당 Phase: P2-P3 | 변경 파일: 레포 수정 5, 신규 3, 조건부 1 + git 밖 env 4 (10-09 실제: 수정 10, 신규 6, master 정량 요약 참조) | 상태: 초안 v3.2

## 목표
- P1 예행 기록을 근거로 `aws/`를 고친다. 이미지 빌드·확인은 A/B 뒤 맨 마지막에 한다(10-08 저녁 대표님 지시: 시험장 컨테이너는 다시 만들지 않는다). 그 이미지의 베이스·패키지 조합을 기록해 운영 빌드와 대조할 기준으로 삼는다.
- 시험장에 pip로 올린 0.31(P1 예행 설치본)과 연구계 옛 환경을 같은 GPU 2에서 차례로 띄워 기능·회귀·성능·MTP를 비교하고 판정표를 만든다. STT 3종은 시험하지 않는다.

## 전제 조건
- [ ] part1 완료: 예행 설치 기록, 설정 해석 9/9, 시험 설정 묶음
- [ ] 결정 ⑤ effort 의미 (P3 전)
- [ ] P3 시작 시 대표님이 GPU 2를 비워 줌

## 작업 목록

### P2 이미지 반영 (GPU 불필요)
- [ ] `aws/Dockerfile.llm`
  - nightly 휠 복사·설치 단계를 지운다. Gemma 4 MTP는 0.21.0부터 정식 포함이다
  - transformers를 따로 까는 줄을 지운다. 지금처럼 하한만 두고 다시 깔면 0.31의 상한(5.18 미만)을 넘는 버전이 깔릴 수 있다
  - `requirements.txt` 설치 전에 베이스의 핵심 패키지 제약을 **배포 메타데이터로** 만들고(part1의 생성기 기본 모드, 누락 시 빌드 실패), `-c`로 걸어 설치한 뒤 `pip check`. 이어서 생성기 `--final`로 최종 서빙 조합을 확인한다. FlashInfer 부속·음성 경로 패키지가 하나라도 없으면 빌드를 실패시킨다. `--final` 출력과 전체 `pip freeze`는 빌드 로그와 이미지 안 파일로 남긴다
  - `/usr/bin/python` 링크 대상을 고정 경로 대신 실제 `python3`로 잡는다. 0.31 공식 런타임 Dockerfile은 `/usr/bin/python3`(apt)를 쓰고 `/usr/local/bin/python3`를 만드는 단계가 없다(소스 `docker/Dockerfile:804-817`). 실제 배포 이미지의 경로는 P2 이미지 확인에서 본다. v0.20.2 베이스는 `/usr/local`에 빌드한 Python을 쓴다. 대상이 비었거나 가상환경을 가리키면 빌드를 실패시킨다
  - FlashInfer 주석을 베이스 기준(0.7.0.post1, 공식 이미지가 같은 버전 jit-cache를 설치)으로 정리한다
  - ldconfig 블록은 유지한다. 등록 결과는 빌드 로그로, 실제 JIT 동작은 P3 첫 추론으로 확인한다
  - apt 단계의 `libatk1.0-0`, `libatk-bridge2.0-0`은 Ubuntu 24.04에서 `t64` 이름으로 바뀌었다. 빌드 로그에서 대체 설치되는지 본다
- [ ] `aws/requirements.txt`: 베이스 표기 0.31.0, nightly 설명 삭제, Gemma 4 MTP 첫 릴리스를 0.21.0으로 정정. 오디오 의존성은 vLLM 0.31의 `audio` 추가 의존성(av, scipy, soundfile, soxr, mistral_common[audio], 소스 `setup.py:1538-1544`)과 맞추고 librosa는 유지한다
  - 근거: 전사 서버는 입력을 모델 샘플레이트로 읽는다(`speech_to_text/base/serving.py:176`). soundfile 경로는 원본 샘플레이트가 다르면 PyAV로 리샘플한다(`multimodal/media/audio.py:245`). av가 없으면 이 경로가 ImportError로 끝나고 torchcodec(0.31 휠 의존성, FFmpeg 필요)으로 넘어간다. 옛 nightly도 같은 PyAV 리샘플을 쓰는데 연구계 hjjo에는 av와 torchcodec이 모두 없어, 16kHz가 아닌 입력은 지금도 실패할 수 있다(운영 이미지의 상태는 확인하지 않았다)
  - Voxtral은 `mistral_common.audio`를 직접 쓴다(`voxtral.py:13`). `mistral_common[audio]`는 soundfile·soxr 묶음이다
  - 공식 Dockerfile은 `audio` 묶음을 따로 설치하지 않는다(`requirements/common.txt:36`은 `mistral_common[image]`). 다른 의존성으로 들어오는 것도 있으므로 최종 조합은 생성기 `--final`로 확인한다
  - librosa는 vLLM 목록에는 없지만 transformers 오디오 유틸에 쓰는 경로가 남아 있어 이번에는 그대로 둔다. 빼는 일은 이 계획 범위 밖이다
  - 버전 고정: requirements에서 직접 까는 음성 패키지(av, soundfile, soxr, librosa, 그리고 librosa가 끌어오는 scipy)를 `==`로 고정한다. 하한만 두면 빌드마다 다른 조합이 골라질 수 있어서다
    - 처음 값은 P1 예행에서 해석된 버전(후보)이다. 예행은 OS·잔존 패키지가 달라 NumPy ABI·코덱 라이브러리 영향을 배제하지 못하므로 정본으로 삼지 않는다
    - P2 빌드가 후보 그대로 설치·import·`pip check`를 통과하고 P3 시험까지 통과하면 그 이미지의 `--final`을 운영 대조 기준으로 확정한다. 후보와 일치하고 통과했다면 다시 빌드하지 않는다
    - P2·P3에서 조정이 필요하면 requirements와 이미지 기록을 함께 고치고, 조정한 이미지로 필요한 시험을 다시 한다
  - `mistral_common`은 베이스 버전을 유지한다. 생성기 기본 모드의 필수 제약에 넣어 `[audio]` 설치가 버전을 바꾸지 못하게 한다. 충돌하면 조용히 올리지 않고 원인을 기록한다
- [ ] `aws/docker-compose.yml`: 예시 주석의 이미지 태그
- [ ] `aws/SETUP_GUIDE.md`, `on-prem/SETUP_GUIDE.md`: nightly 휠 전달 단계 삭제 (Dockerfile과 같은 커밋)
- [ ] 베이스 고정: `VLLM_IMAGE`를 태그와 다이제스트로 적는다(`vllm/vllm-openai:v0.31.0@sha256:...`). 태그만 쓰면 운영 빌드 때 다른 베이스가 올 수 있다. 운영용 env 3개(`aws/.env`, `.env.prd`, `on-prem/.env.prd`)는 P4 반영 때 바꾸고, P2에서는 시험장 빌드에 쓰는 값만 정한다
- [ ] 코덱스 검수 후 커밋 (대표님 지시 시). 운영 반영은 하지 않는다
- [ ] **(맨 마지막, P3 뒤)** 대표님 요청 사항 (연구계 호스트). 시험장 컨테이너 `llm-hgiai`는 바꾸지 않고, 새 이미지는 GPU 2를 쓰는 임시 컨테이너로 확인한다
  - 시험장 이미지 이름을 `user.sh` 컨테이너와 겹치지 않게 한다. 공통 `.env`의 `LLM_IMAGE_NAME`은 `user.sh`도 읽으므로(`aws/user.sh:38-46`) 바꾸지 말고, 시험장 전용 env 파일이나 그 compose 명령에만 값을 준다
  - 지금 시험장 컨테이너의 이미지 ID에 되돌리기 태그를 붙인 뒤 빌드 → 임시 컨테이너 기동(`/workspace`와 시험장 작업 폴더 `~/vllm-upgrade`는 읽기만, 홈은 붙이지 않음, 포트는 열지 않음). 재생성은 하지 않는다
- [ ] 이미지 확인 (임시 컨테이너, 맨 마지막)
  - 실행 경로 4종(gemma31b·gemma26b·qwen-mtp-off·qwen-mtp-on, 시험 묶음 그대로)을 하나씩 기동 → `test_vllm_server.py` 전체 카테고리 통과. pip 환경 A/B 결과와 기동 로그(백엔드·KV 블록·MTP)를 대조한다(아래 ⑥)
  - **결정 ⑨(10-09, 운영 Gemma MTP 끔) 반영**: pip 환경의 gemma31b 기능 시험·장시간 부하는 MTP 켬으로 했고, 0.31 MTP 끔은 문법 탐침 320건만 봤다. 그래서 이미지 확인의 gemma31b는 MTP 끔 묶음(`gemma31b-nomtp`)으로도 기동해 기능 시험 전체, 게이트웨이 경유 확인, 장시간 부하 2시간을 한다. 이것이 운영에 올라갈 조합의 안정성 근거다
    - `gemma31b-nomtp`는 A/B 묶음 `gemma31b`에서 `speculative_config`만 주석 처리한 것이다. KV fp8·길이 8192는 L40S 48GB 제약으로 A/B 묶음과 같고, 운영값(KV auto·65536)과는 다르다. MTP 켬 부하(7,910건)와 MTP만 다르게 두어 비교한다
    - 이미지 확인 전에 pip 환경에서 같은 점검을 먼저 한다(10-09 저녁, 아래 P3 실행 기록). 이미지 확인은 그 결과와 대조하는 최종 확인이다
    - 이미지 안의 실행은 `image_check.sh`(원본 사본 `.archive/2026-10-09_vllm-upgrade-p3/image_check.sh`, 시험장 `~/vllm-upgrade/image_check.sh`로 반영, 임시 컨테이너에서는 `/mnt/vllm-upgrade/image_check.sh`)가 맡는다. 아래 명령 묶음 ④·⑥
  - `python`, `python3`, `python3 -m pip`, `vllm`의 실경로·버전, `pip check`
  - 로딩 위치: `vllm`, `torch`가 시스템 site-packages에서 올라오는지. 사용자 site와 겹치는 패키지 목록
  - 실행 중 추가 설치: `EXTRA_REQUIREMENTS`가 비어 있는지. 쓰면 같은 제약을 건다
  - 재생성 뒤 `hgiai` 사용자·홈 소유권·sudo. 0.31 이미지에는 UID 2000 `vllm` 사용자가 있고 Ubuntu 24.04에는 UID 1000 `ubuntu`가 있지만, `entrypoint-llm.sh:50-57`이 같은 UID의 기존 사용자를 지우고 새로 만든다
  - 핵심 패키지 대조표: 이미지 값과 P1 예행 기록을 나란히 적고 다른 항목은 이유를 적는다
  - 설정 해석 9/9 재실행, `async_scheduling` 최종값 False
  - 생성기 `--final` 통과(FlashInfer cubin·jit-cache의 존재·버전·CUDA 표시 포함), 음성 모듈 import(soundfile, soxr, av, torchcodec, `mistral_common.audio`), 게이트웨이 의존성 import
- [ ] 이미지 기록: 베이스 다이제스트, 빌드 인자(`MODE` 등), 생성기 `--final` 출력, 전체 `pip freeze`를 `aws/image-freeze-0.31.0.txt`에 남긴다. 운영 빌드 결과를 이 파일과 대조한다(part3)
- [ ] 되돌리기 절차 예행(임시 컨테이너로): 새 이미지 → 태그해 둔 이전 시험장 이미지 → 새 이미지 순서로 임시 컨테이너를 만들어 절차와 소요 시간을 확인한다. `llm-hgiai` 자체는 건드리지 않는다. 시험장은 compose 컨테이너라 compose 경로로 한다. 이미지는 `LLM_IMAGE_NAME=<보존 태그>`로 고르고 `--no-build --pull never`를 붙인다. 이 예행은 compose 절차의 확인이며, 운영 `user.sh` 절차를 실행 검증한 것으로 기록하지 않는다. 운영에서 실연하자는 뜻도 아니다

### 게이트웨이 effort 처리 (결정 ⑤가 "지금 의미 유지"일 때만)
- [ ] `llm-serving/vllm/vllm_gateway.py`: 번역한 effort를 최상위 `reasoning_effort`가 아니라 `chat_template_kwargs.reasoning_effort`로 넘긴다. 최상위 필드는 지금처럼 지운다
  - 0.31의 자동 thinking 매핑은 최상위 값이 있을 때만 일어난다(`chat_completion/protocol.py:584-586`). 템플릿 인자로 넘기면 매핑을 피하고, thinking 기본값은 서버가 자기 설정으로 정한다. 기본값을 게이트웨이에 복제할 필요가 없다
  - 옛 nightly도 같은 병합 규칙이다: 최상위가 None이면 템플릿 인자의 값을 남긴다(`renderers/params.py`의 `merge_kwargs`). 두 버전에서 동작이 같다
  - 최상위 effort를 따로 쓰는 곳은 Harmony 렌더러(gpt-oss)뿐이다(`renderers/online_renderer.py:522`). 지금 번역표에 있는 계열(qwen3.8)과 무관하다
  - `none → enable_thinking=false`, 미지원 계열의 effort 제거, `X-Effort-Applied` 헤더는 그대로 둔다
- [ ] 의미 보존 범위는 **게이트웨이 경유**다. 백엔드 직접 호출은 0.31의 새 의미를 따른다. `VLLM_OPS_GUIDE.md`에 적는다(part3)

### P3 A/B 시험 (GPU 2·TP1, 대표님이 비워 준 시간)
- [ ] 배치: 모델마다 옛 환경(연구계 hjjo `~/.local`) 기동 → 시험 → 내림 → 새 환경(시험장 시스템 site `/usr/local/lib/python3.12/dist-packages`의 pip 0.31, P1 예행 설치본) 기동 → 같은 시험 → 내림. part1의 시험 설정 묶음(`~/vllm-upgrade/bundle/<변형>/`, 양쪽 md5 일치)과 `~/vllm-upgrade/ab_run.sh <레이블>`만 쓴다
- [ ] 순서: Gemma 4 31B → 26B-A4B → Qwen3.8(MTP 끔, 이어서 새 쪽만 MTP 켬). 위험이 큰 Gemma 31B를 먼저 본다. STT 3종은 제외(10-08 지시)
- [ ] MTP 점검(모든 변형 공통, `tests/mtp_prefix_cache_probe.py`): 1,000토큰 넘는 공유 접두로 첫 캐시 블록을 공통으로 만들고, 값 48개 복사 정확도를 공유 캐시 / `cache_salt` 분리 캐시로 나눠 라운드마다 잰다. 라운드 사이에 같은 접두를 쓰는 혼합 부하(프리필·긴 생성·다중 턴, 동시 12)를 건다. 수락률은 `/metrics`의 `spec_decode_num_accepted_tokens_total / num_draft_tokens_total` 증가분(옛·새 지표 이름 같음). Gemma(MTP 자동)는 옛·새 모두 재고, Qwen MTP 켬은 새 쪽만 라운드 10회 이상으로 #53912 재현 여부를 본다
- [ ] 기동 로그 대조: Model Runner, 어텐션 백엔드, 양자화 방식과 경고, MTP 방식, KV 블록 수·최대 동시성, CUDA graph 캡처 시간, 기동 소요. 새 이미지는 V2여야 하며, V1으로 돌아가면 통과로 치지 않고 원인을 기록한다. 옛 환경은 기준선이므로 V1이어도 그대로 기록한다
- [ ] 기능: `tests/test_vllm_server.py --base-url http://localhost:<백엔드 포트>` (직접 호출). `./start.sh test`는 실행 중인 게이트웨이를 모두 돌므로 쓰지 않는다. STT(`test_stt_server.py`)는 이번에 시험하지 않는다(10-08 지시)
- [ ] 게이트웨이 경유: part1의 게이트웨이 사본으로 띄운다(정식 `gateways/`·`instances/`를 쓰지 않는다). 정체성 문구 주입, developer 역할 병합을 본다. `/v1/audio/*`·`/v1/realtime` 중계는 STT 제외로 이번에 보지 않는다
- [ ] 게이트웨이를 고친다면 세 조합을 본다: 옛 게이트웨이 + 옛 vLLM(기준), 새 게이트웨이 + 옛 vLLM(호환), 새 게이트웨이 + 새 vLLM(목표)
- [ ] effort × thinking (게이트웨이 경유, 기대값 = 지금 동작)
  - thinking 생략·false → effort가 무엇이든 꺼짐
  - thinking true → 켜짐. Qwen3.8은 번역된 effort(low/medium/xhigh, effort 없으면 서버 기본 medium), Gemma는 effort 제거
  - effort `none` → thinking true여도 꺼짐 (지금 게이트웨이 동작)
  - `X-Effort-Applied`: Qwen3.8은 번역값, Gemma는 `dropped`, `none`은 `none`, effort 없으면 헤더 없음
  - 판정은 `reasoning` 필드 유무만으로 하지 않는다. 출력 토큰 수와 응답 구조(생각 없이 바로 도구 호출하는 경우 포함)를 함께 본다. 스트리밍·비스트리밍 둘 다
  - 직접 호출은 새 의미를 확인하는 용도로 같은 조합을 돌려 기록한다(판정 아님). Qwen 템플릿은 thinking이 켜졌거나 지정되지 않았을 때만 effort를 검사하고 xhigh·medium·low만 받는다. 그래서 `high`·`none`이 thinking 켬과 만날 때의 400은 의도된 동작이고, 명시적 `enable_thinking=false`면 검사를 건너뛴다
- [ ] 회귀 집중 (Gemma): thinking 기본 끔 / 요청으로 켬 / 켬 + 도구 호출 (스트리밍·비스트리밍), 숫자·괄호가 든 도구 인자, 이미지 동시 5개와 같은 이미지 반복(shm 캐시), JSON 스키마 응답, 6만 토큰 근처 입력
- [ ] Qwen3.8: thinking·effort 조합, `qwen3_xml` 도구 호출. MTP 켬은 #53912 재현 조건(같은 접두를 쓰는 요청 반복, 숫자 복사 검증)으로 본다
- [ ] FP8 (Gemma): 주 비교는 옛 `fp8` ↔ 새 `fp8`이다. 새 버전 안의 `fp8` ↔ `fp8_per_tensor`는 같은 경로인지 확인하는 용도로만 1회 본다
- [ ] 품질: 고정 프롬프트 20개를 greedy로 돌려 옛·새 출력 차이율을 기록한다(판정 아님). 판정은 정답을 가릴 수 있는 항목으로 한다: 숫자 복사, 도구 인자, JSON 유효성, 빈 답변
- [ ] 성능: `speed_test`·`traffic_test`를 같은 인자로 3회씩. 지표는 처리량, TTFT p50·p95, 디코딩 속도. 회차마다 통계를 내고 그 3개 값의 중앙값을 비교한다. 지금 스크립트의 TPOT 값은 디코딩 TPS 중앙값의 역수라는 점을 판정표에 적는다
- [ ] MTP 수락률: 같은 요청 집합에서 수락 토큰 합 / 제안 토큰 합. 옛·새 모두 엔진 로그 집계로 같은 방식으로 잰다. 새 쪽은 MTP가 켜진 설정에만 `--per-request-spec-decode-metrics summary`를 붙여 요청별 값을 진단용으로 남긴다. 추측 디코딩이 없는 설정에 붙이면 설정 검증 오류다(`config/vllm.py:1662-1669`). 값은 비스트리밍이면 응답 최상위 `metrics.speculative_decoding`, 스트리밍이면 `include_usage` 마지막 청크에 실린다
- [ ] ~~STT~~ **제외(10-08 저녁 대표님 지시: 지금 쓰지 않음)**. 아래 STT 항목은 나중에 STT를 다시 쓸 때의 절차로 남긴다. 이번 판정표에는 "시험 안 함"으로 적는다
  - STT: 정답 표본 20개의 CER, 30초 넘는 음성 1건(Whisper), Voxtral `/v1/realtime` 연결·종료. 긴 음성과 리샘플링 확인은 CER 표본과 따로 판정한다
  - 리샘플 경로 (입력 호환 점검): 정답 표본(zeroth)은 16kHz다. 각 모델의 목표 샘플레이트를 기동 뒤 확인하고(Voxtral은 토크나이저 음성 설정에서 정해짐, `voxtral_realtime.py:450`), 16kHz인 모델에서만 "정답 표본은 리샘플을 타지 않는다"고 적는다
    - 같은 표본 2건을 44.1kHz WAV와 MP3로 바꾸고 변환 결과의 실제 샘플레이트·재생 가능 여부를 확인한 뒤 모델 3종에 보낸다(버전당 12건). 16kHz 원본도 대조 입력으로 같이 보낸다
    - 성공 조건: HTTP 성공, 비어 있지 않고 원 발화에 맞는 전사, 엔진 생존
    - 판정: 옛·새 성공 = 통과 / 옛은 원인이 확인된 기존 환경 결함(예: av 부재)으로 실패, 새는 성공 = 기존 결함 해소(그 사례의 버전 간 비교는 "계산 불가") / 옛 성공·새 실패 = 회귀, 통과 불가 / 둘 다 실패 = 입력·설정·환경 원인을 가르고, 새 환경 성공 조건 미달로 본다
    - 처리 경로는 확인된 것만 적는다. "Failed to load audio via soundfile" 로그는 soundfile 경로를 ImportError로 벗어났다는 뜻일 뿐이고 그 뒤 torchcodec·PyAV 중 어느 쪽이 처리했는지는 알려 주지 않는다. 형식 탐지 실패는 이 로그 없이 대체 경로로 간다(`multimodal/media/audio.py:464-479`). 확인이 안 되면 "자동 선택, 최종 처리기 미확인"으로 남긴다. 이를 위해 서빙 코드에 로깅을 더하지 않는다
    - 새 이미지에는 av가 있으므로 WAV·MP3 모두 soundfile + PyAV로 처리될 수 있다. 이 시험을 torchcodec 대체 경로의 실행 검증으로 기록하지 않는다
    - CER 표본은 따로 유지한다. 이 점검에서 옛 쪽이 실패한 사실을 CER 계산에서 표본을 빼는 근거로 쓰지 않는다
- [ ] 안정성 입력 (새 쪽): 어휘 밖 토큰 ID, 과도한 `min_tokens`가 4xx로 거절되고 엔진이 살아 있는지
- [ ] 장시간 부하 (새 쪽, LLM 모델마다 2시간)
  - 기존 `traffic_test_vllm.py`는 정해진 요청 수만 처리한다. 2시간 동안 반복 실행하고, 회차마다 성공 요청 수·오류·429·응답 시간을 모은다
  - 부하에는 새 이미지·같은 이미지 반복, thinking 켬·끔을 섞는다. 도구 호출·JSON 스키마·긴 입력은 고정 사례로 중간과 끝에 한 번씩 돌린다
  - GPU·호스트 메모리를 1분 간격으로 기록하고, 예열·캐시 적재로 생긴 초기 증가와 요청을 비운 뒤에도 이어지는 증가를 나눠 본다
  - 실사용자가 없으므로 "관찰 기간"을 이것으로 대신한다. 2시간이 장기 안정성을 보장한다고 쓰지 않는다
- [ ] 각 시험 시간이 끝나면 연구계 :5015를 옛 환경으로 되살리고 `./start.sh status`로 확인한다
- [ ] 판정표 작성: `llm-serving/vllm/tests/results/vllm-0.31-ab.md`. PII 프록시 경유 성능·지표는 검증하지 않았다고 적는다(전체 검사 모드가 SSE를 재조립하며 `metrics`를 보존하지 않음, `pii/proxy.py:325,389`)

## 변경 예시

**`aws/Dockerfile.llm` — 설치 단계**
```dockerfile
# 변경 전: requirements → nightly 휠 → transformers(하한만)
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir /tmp/wheels/vllm-*.whl \
    && pip install --no-cache-dir --no-deps "transformers>=5.8.0"

# 변경 후: 베이스(v0.31.0)의 핵심 조합을 배포 메타데이터로 제약을 만들어 고정하고 챗봇 의존성만 얹는다.
# 설치 뒤에는 최종 서빙 조합(FlashInfer 부속·음성 경로 포함)을 확인하고 기록한다
COPY gen-core-constraints.py /opt/gen-core-constraints.py   # part1 예시의 생성기. 운영 대조 때 이미지 안에서 다시 쓴다
RUN python3 /opt/gen-core-constraints.py > /tmp/vllm-core-constraints.txt \
    && pip install --no-cache-dir -r /tmp/requirements.txt -c /tmp/vllm-core-constraints.txt \
    && pip check \
    && python3 /opt/gen-core-constraints.py --final > /opt/image-core-final.txt \
    && pip freeze > /opt/image-freeze.txt
```
생성기는 `aws/gen-core-constraints.py` 한 파일로 두고 모드로 나눈다. P1 예행, 이미지 빌드, 운영 대조(part3)가 같은 파일을 쓰므로 목록이 한 곳에서 관리된다. 이미지 안 `/opt/`에 생성기와 두 기록을 남겨, 운영에서는 서비스 컨테이너를 바꾸기 전에 임시 컨테이너로 꺼내 대조한다.

**`aws/Dockerfile.llm` — Python 링크**
```dockerfile
# 변경 전
    && ln -sf /usr/local/bin/python3 /usr/bin/python \
# 변경 후: 베이스가 python3를 어디에 두든 그 파일을 가리키고, 비었으면 실패
    && PY3="$(command -v python3)" && [ -n "$PY3" ] && [ -x "$PY3" ] \
    && ln -sf "$PY3" /usr/bin/python && python --version \
```

**게이트웨이 (결정 ⑤가 "지금 의미 유지"일 때)**
```python
    elif resolved:
        # 0.31부터 최상위 reasoning_effort가 있으면 vLLM이 enable_thinking을 켠다(protocol.py:584-586).
        # 템플릿 인자로 넘기면 자동 매핑을 피하고 thinking 기본값은 서버 설정을 따른다. 옛 버전도 같은 병합 규칙이다.
        new_kwargs["reasoning_effort"] = resolved
        applied = resolved
```

**판정 기준**

| 항목 | 통과 조건 |
|------|-----------|
| 기동·기능 시험, 회귀 집중 항목, effort × thinking (게이트웨이 경유) | 전부 기대값과 일치 |
| 처리량, 디코딩 속도 | 새 / 옛 ≥ 0.95 (3회 중앙값) |
| TTFT p50·p95 | 새 / 옛 ≤ 1.05 (3회 중앙값) |
| 경계 구간 | 처리량·디코딩 속도 0.93~0.97, TTFT 1.03~1.07이면 2회 더 재고 5회 중앙값으로 판정. 회차 간 흔들림이 판정 폭보다 크거나 5회 뒤에도 구간 안이면 "판정 보류"로 남긴다 |
| MTP 수락률 | 진단 지표. 옛 대비 −5%p를 넘게 떨어지면 원인을 조사하고 성능 판정과 함께 본다 |
| MTP + 접두 캐시 손상 (#53912) | 공유 캐시 정확도가 분리 캐시보다 2개 넘게 낮은 라운드 0회. Qwen MTP 켬은 새 쪽 10라운드 이상. 1회라도 재현되면 Qwen MTP는 "끔 유지"로 판정 |
| STT CER (이번 제외) | CER = (치환+삭제+삽입) 합 / 정답 글자 수 합. 정규화(문장부호 제거, 띄어쓰기 제거)를 고정하고 CER_새 − CER_옛 ≤ 0.01. 오류 글자 수와 분모를 함께 적는다. 표본 20개는 회귀 점검용이며 품질 전체를 증명하지 않는다 |
| STT 입력 호환 (44.1kHz WAV·MP3, 이번 제외) | 새 쪽 12건 모두 성공 조건 충족. 옛 쪽 결과는 위 판정 규칙으로 분류한다. 모든 형식·대체 경로를 덮는 시험이 아니다 |
| 장시간 부하 | 엔진 오류·자동 재기동 0건, 요청을 비운 뒤 메모리 증가가 이어지지 않음. 429만 쌓인 회차는 부하 시험으로 치지 않는다 |
| 안정성 입력 | 4xx 거절, 엔진 생존 |

문턱 값(5%, 1%p)은 이 계획이 제안한 값이다. vLLM이 보장한 수치가 아니다.

## 마지막 단계 명령 묶음 (대표님 실행, 연구계 호스트)
시험장 `llm-hgiai`는 그대로 두고 임시 컨테이너로만 확인한다. `aws/.env`는 건드리지 않는다(`user.sh`가 읽는 `LLM_IMAGE_NAME`을 바꾸면 다른 컨테이너까지 영향).

```bash
# ① 레포 최신화(aws/ 변경 커밋 뒤) — 호스트의 aws 디렉토리에서
cd <aws 디렉토리> && git pull   # 또는 ./start.sh pull (S3 경로일 때)

# ② 되돌리기 태그: 지금 시험장이 쓰는 이미지 ID를 보존
docker tag "$(docker inspect -f '{{.Image}}' llm-hgiai)" llm-dev:pre-0.31-$(date +%y%m%d)

# ③ 빌드 — 이미지 이름·베이스를 명령에만 준다(.env 변경 없음). dev 모드로 빌드하면 nvm·codex까지 들어가므로 prd로 1회, dev로 1회 빌드해 둘 다 기동 확인
VLLM_IMAGE='vllm/vllm-openai:v0.31.0@sha256:c1c9f6fd5c109ba7f0546a59f5b2f15fb87f64c77782e90a27b648b42a8e67c3' \
MODE=prd LLM_IMAGE_NAME=llm-0.31-test docker compose build llm 2>&1 | tee /tmp/build-0.31-prd.log
#   빌드 로그에서 볼 것: python --version / [ldconfig] registered cudart / --final 출력(FlashInfer cubin·jit-cache, torchcodec, av …) / pip check 통과

# ④ 임시 컨테이너 기동 (GPU 2만, 시험장 볼륨 읽기 전용). 시험은 ⑥에서 컨테이너 안에서 하므로 포트를 열지 않는다
#   홈(/home/hgiai)은 붙이지 않고 시험장 작업 폴더만 /mnt/vllm-upgrade로 붙인다(10-09 저녁 고침).
#   진입점 entrypoint-llm.sh는 set -e이고 사용자 홈에 chown -R을 하므로(setup_user_home), 홈을 읽기 전용으로 붙이면 컨테이너가 기동 직후 끝난다.
#   홈은 진입점이 컨테이너 안에 새로 만든다
docker run -d --name llm-0.31-test --gpus '"device=2"' --shm-size 16g \
  -e MODE=prd -e USERNAME=hgiai -e PASSWORD=<임시> -e CONTAINER_UID=2000 -e CONTAINER_GID=2000 \
  -v /volume/models:/models:ro -v /volume/workspace/hgiai:/workspace:ro -v /volume/homes/hgiai/vllm-upgrade:/mnt/vllm-upgrade:ro \
  llm-0.31-test
docker ps --filter name=llm-0.31-test --format '{{.Status}}'; docker logs llm-0.31-test 2>&1 | tail -5   # Up이어야 한다. Exited면 진입점 로그를 본다

# ⑤ 이미지 확인 (컨테이너 안에서)
docker exec -u hgiai llm-0.31-test bash -lc '
  which python python3 vllm ps free nvidia-smi; python --version; python3 -m pip --version   # ps·free·nvidia-smi는 ⑥ 부하 메모리 기록에 쓴다
  python3 -c "import vllm,torch,transformers,flashinfer;print(vllm.__version__,torch.__version__,transformers.__version__,flashinfer.__version__,vllm.__file__)"
  python3 -m pip check; python3 /opt/gen-core-constraints.py --final; cat /opt/image-core-final.txt'
#   → /opt/image-core-final.txt를 시험장 pip 환경의 ~/vllm-upgrade/rehearsal-final.txt와 대조(차이는 이유를 적는다)
#   → 전체 목록 /opt/image-freeze.txt를 레포 aws/image-freeze-0.31.0.txt로 저장(베이스 다이제스트·빌드 인자 머리말 포함)

# ⑥ 모델별 실행 경로 기동·기능 시험 — 시험 묶음 그대로, 한 번에 하나씩. 스크립트 하나가 기동·시험·로그 추출·내림까지 한다
#   (10-09 저녁 고침) 처음 적은 방식은 읽기 전용 볼륨 때문에 동작하지 않는다: 런처·게이트웨이는 자기 폴더에 임시 설정·logs/를,
#   기능 시험은 tests/logs를, vLLM은 ~/.cache에 컴파일 캐시를 쓴다. 묶음이 host 127.0.0.1이라 호스트 포트 연결로도 닿지 않는다.
#   image_check.sh는 필요한 코드와 묶음을 /tmp 실행 폴더로 복사하고 HOME도 그 아래로 바꿔 돌린다. 시험은 컨테이너 안에서 한다
#   10-09 저녁 시험장 pip 환경에서 IMAGE_CHECK_GPU=2 IMAGE_CHECK_VU=/home/hgiai/vllm-upgrade로 예행했다(P3 실행 기록)
#   gemma31b-nomtp(운영 조합, 결정 ⑨, 게이트웨이 시험 포함)와 gemma31b가 필수다. gemma26b는 생략할 수 있다(운영 인스턴스 아님)
#   시험장 pip 설치본과 공식 이미지는 선택 패키지(DeepGEMM 등) 유무가 달라 커널 선택이 바뀔 수 있으므로 한 종으로 대신하지 않는다(10-09 코덱스 검수)
#   한 변형이라도 0이 아닌 값으로 끝나면(시험 실패 1, 런처 세션을 비우지 못함 1, 인자·복사·기동 실패 2) 그 자리에서 멈추고
#   다음 변형과 아래 장시간 부하를 시작하지 않는다(코덱스 R6-02). ok 줄부터 장시간 부하 줄까지 한 번에 붙여 넣는다
ok=1
for V in gemma31b gemma26b qwen-mtp-off qwen-mtp-on; do
  docker exec -u hgiai llm-0.31-test bash /mnt/vllm-upgrade/image_check.sh $V   # 변형마다 5~20분, 끝나면 런처를 스스로 내린다
  rc=$?; [ $rc = 0 ] || { echo "❌ $V 종료 $rc — 여기서 멈춤. 다음 변형과 장시간 부하는 시작하지 않음"; ok=0; break; }
done
# 운영 조합(결정 ⑨): 기능·회귀·게이트웨이 시험 뒤 게이트웨이 경유 장시간 부하 120분. 2시간 넘게 걸리므로 -d로 띄운다
[ $ok = 1 ] && docker exec -d -u hgiai -e IMAGE_CHECK_SOAK_MIN=120 llm-0.31-test bash /mnt/vllm-upgrade/image_check.sh gemma31b-nomtp gw
#   멈췄다면: 해당 변형의 summary.txt를 보고, 잔존이 없는지 확인한 뒤(아래 두 줄) 남은 변형부터 다시 한다
#   docker exec llm-0.31-test ps -eo pid,sid,args | grep -E 'vllm|launcher|gateway' | grep -v grep   → 아무것도 없어야 한다
#   nvidia-smi -i 2 --query-gpu=memory.used --format=csv   → 외부 점유만 남아야 한다
docker exec llm-0.31-test bash -c 'tail -3 /tmp/image-check/gemma31b-nomtp-*/out/summary.txt'   # 진행 확인. "판정 재료" 줄이 나오면 끝
docker cp llm-0.31-test:/tmp/image-check ./image-check-0.31   # 결과 회수: 변형별 summary.txt, boot_lines.txt(실행 경로 줄), 시험·부하 원문
#   boot_lines.txt를 판정표 기동 로그 표·시험장 pip 기동 로그와 대조한다: V2 Model Runner, `Selected … for …`, 어텐션 백엔드, MoE 백엔드(gemma26b), MTP, KV 토큰 수

# ⑦ 되돌리기 예행: llm-0.31-test를 내리고 pre-0.31 태그 이미지로 같은 docker run → vllm --version이 0.20.2 nightly인지 → 다시 새 이미지
docker rm -f llm-0.31-test   # (대표님 실행)
```

## 실행 기록 (2026-10-08)
기록 위치: 연구계 `~/vllm-upgrade/baseline/`(옛 기동 로그), `~/vllm-upgrade/ab/<레이블>/`(시험 출력), 시험장 같은 경로
아래에서 "스크래치"라고 적은 도구·협업 기록(`collab/…` 포함)은 10-09 밤 레포 `.archive/2026-10-09_vllm-upgrade-p3/`(git 밖)로 옮겼다. 경로는 그 폴더 기준이다
- **P2 파일 변경 (10-09 커밋)**: `aws/Dockerfile.llm`(nightly 단계 삭제, 제약 설치, Python 링크 탐색), `aws/gen-core-constraints.py`(신규), `aws/requirements.txt`(오디오 `==` 고정, librosa 0.11.0), `aws/docker-compose.yml`·`aws/start.sh`·`on-prem/SETUP_GUIDE.md` 표기, `vllm_gateway.py` effort → `chat_template_kwargs`(직접 호출 6사례 검증)
  - 10-09 커밋 전 점검에서 휠 잔여를 더 고쳤다.
    - `on-prem/start.sh check`는 `aws/wheels/vllm-*.whl`이 없으면 실패로 판정했다. 0.31 빌드에서는 거짓 실패라 이 검사를 없앴다. 같은 파일의 pull 안내 3곳도 고쳤다
    - `on-prem/setup-host.sh`의 휠 scp 안내 2곳을 고쳤다
    - `on-prem/SETUP_GUIDE.md` 비교표와 `aws/SETUP_GUIDE.md` push 안내를 고쳤다
    - 수정 뒤 `git grep -E "wheels/|\.whl|nightly" -- aws on-prem`을 다시 돌렸다. 남은 줄은 "휠 덮어쓰기를 없앴다"는 설명뿐이다(`pip-wheels` 오프라인 설정은 별개)
- **시험 도구**: `tests/mtp_prefix_cache_probe.py`(신규, #53912 재현 + 수락률), `~/vllm-upgrade/ab_run.sh`(기능 → 속도 3회 → 탐침, 양쪽 배치). 공유 접두는 Qwen 토크나이저 기준 2,148토큰(첫 두 블록 공통)
- **P3 옛 Gemma 31B 기동**: 17:57~18:08 GPU 2 외부 선점으로 3회 실패(part1 기록). 18:09 4번째 기동은 65536 컨텍스트에서 KV 0.94 GiB로 실패, 18:21 8192도 KV 4.53 GiB(필요 6.89)로 실패 → KV fp8_e4m3 추가 후 18:29 기동, 18:34 완료(KV 10,886토큰, 엔진 초기화 246초)
- **P3 옛 Gemma 31B 결과 (18:35~18:59)**: 기능 31/31, 속도 3회(1×512 TTFT 87ms·48 TPS, 10×2048 TTFT 265ms·43 TPS 중앙값), MTP 수락률 부하 중 0.59~0.61, 공유 접두 캐시 손상 0/3. 게이트웨이 경유는 옛·새 게이트웨이 모두 effort×thinking 10/10, 정체성·developer·경로 가림 통과. 값은 판정표 `tests/results/vllm-0.31-ab.md`
- **P3 새 Gemma 31B (19:00~19:30)**: 기동 완료(V2 Model Runner, TRITON_ATTN, `fp8`→Fp8PerTensorOnline + "fp8 deprecated, use fp8_per_tensor" 경고, KV 10,157토큰, 엔진 초기화 302초). 기능 31/31, 속도 전 시나리오 통과(TTFT 0.75~0.96배, 디코딩 1.08~1.09배), MTP 수락률 0.60~0.64·손상 0/3, 게이트웨이 옛·새 모두 통과, 안정성 입력 4종 400 거절·엔진 생존. **직접 호출에서 0.31의 "최상위 effort → thinking 자동 켬" 실측 확인**(계획 예측과 일치)
- **순서 조정**: 장시간 부하는 모델 3종 A/B(기능·속도·탐침·게이트웨이)를 모두 끝낸 뒤 새 쪽에서 돌린다. GPU 한 장을 순차로 쓰므로 모델마다 2시간을 끼워 넣으면 A/B 자체가 밤을 넘긴다
- **P3 옛 Gemma 26B-A4B (19:31~20:04)**: 체크포인트·드래프트가 없어 런처 자동 다운로드(49GB, 6분). 0.9에서 KV 0.46 GiB 부족 → 비율 0.92로 재정의(컨텍스트 65536 유지, KV 69,173토큰). 기능 31/31, 속도 3회(1×512 TTFT 50.7ms·127 TPS, 10×2048 102ms·88 TPS), MTP 수락률 0.53~0.59·손상 0/3, 게이트웨이 옛·새 10/10+3/3
- **P3 새 Gemma 26B-A4B (20:05~20:21)**: 기동 완료(V2 Model Runner, 150층 fp8_per_tensor_static, TRITON Fp8 MoE, KV 66,918토큰(옛 −3%), 엔진 초기화 295초). 기능 31/31, 속도 전 시나리오 통과(TTFT 0.66~0.94배, 디코딩 1.18~1.28배), MTP 수락률 0.53~0.60·손상 0/3, 게이트웨이 옛·새 10/10+3/3, 안정성 입력 4종 400·생존. 직접 호출 effort→thinking 자동 켬도 동일 확인
- **P3 옛 Qwen MTP 끔 (20:22~22:11)**: 기동 완료(V1, FLASH_ATTN + GDN Triton/FLA, 블록 FP8 사전 양자화, KV 83,012토큰, Mamba `align` 접두 캐시 실험 기능 경고). 기능 31/31, 속도 3회(1×512 TTFT 229ms·17.5 TPS), 탐침 손상 0/3(MTP 없는 대조군), 게이트웨이 옛·새 18/18+3/3. 직접 호출: 최상위 effort는 템플릿 변수로 들어가 `high`·`none`은 400, `low`는 사고 단축
- **P3 새 Qwen MTP 끔 (22:12~23:21)**: 기동 완료(V2 Model Runner, FA2 + GDN, KV 83,740토큰(옛 +0.9%), 엔진 초기화 238초). 블록 FP8 선형층 커널이 옛 Triton W8A8에서 **MarlinFP8ScaledMM(가중치만 FP8)**으로 바뀌었다(0.31 Marlin이 8.9 이상 제외 조건을 없앰, L40S 한정 관찰, 운영 GPU는 이미지 확인 때 `Selected … for Fp8LinearMethod`로 확인). 기능 31/31, 속도 전 시나리오 통과(TTFT 0.60~0.83배, 디코딩 1.17~1.33배, 커널 교체 몫 포함), 탐침 손상 0/3, 안정성 입력 4종 400·생존. 게이트웨이: 새 게이트웨이 18/18+3/3, **옛 게이트웨이+새 vLLM 14/18**(thinking 생략 + effort high가 켜짐) → 리스크 1번 실측 확인, 게이트웨이를 vLLM보다 먼저 또는 같이 반영. 직접 호출 `thinking 생략 + effort high`는 옛 200(꺼짐)에서 400으로 바뀜
- **P3 새 Qwen MTP 켬**: 23:22 첫 기동은 비율 0.9에서 KV 3.75 GiB(65536에 4.88 GiB 필요)로 실패. MTP 층 가중치 +0.76 GiB와 드래프트 CUDA 그래프 몫이다(연구계 :5015는 TP2라 해당 없음). 런처 자동 재기동(1/3)은 처음 만든 실행 설정을 그대로 다시 쓰므로 런처를 내리고, `make_bundle.py`의 `MEMORY_OVERRIDES`에 `qwen-mtp-on: 0.94`를 넣어 이 변형만 다시 만들었다(다른 묶음 md5 그대로). 23:31 재기동 완료(KV 73,902토큰 / 1.13x, 엔진 초기화 96초). 결과(23:35~00:20): 기능 31/31, **탐침 손상 0/10**(매 라운드 48/48, 부하 중 수락률 0.64~0.73), 새 게이트웨이 18/18+3/3, 안정성 입력 4종 400·생존. 속도는 같은 0.31의 MTP 끔 대비 디코딩 1.7~2.1배, TTFT 2~15배(판정 아님). TTFT 원인은 0.31이 MTP에서 접두 캐시 적중의 마지막 블록을 버리고 다시 계산하는 정확성 장치(`kv_cache_coordinator.py:110-131`)이고, Qwen 블록이 800토큰이라 835토큰 속도 프롬프트는 적중이 0이 된다
- **P3 장시간 부하 (10-09 00:20~)**: 시험장 `~/vllm-upgrade/soak_chain.sh 120 qwen-mtp-on gemma31b gemma26b qwen-mtp-off`(변형마다 런처 기동 → 새 게이트웨이 → `soak.sh` 120분 → 요청 비운 뒤 5분 메모리 → 자동 재기동·엔진 오류 집계 → 정리). 진행 로그 `~/vllm-upgrade/soak_chain.log`, 변형별 `ab/new-<변형>/soak/chain_summary.txt`. **00:36 중단**: `soak.sh`의 텍스트·thinking 회차가 `--image-ratio`를 주지 않아 트래픽 도구 기본값(이미지 50%·4096px, 장당 약 16,400토큰)으로 돌았다. Qwen MTP 켬은 KV 사용률 90~95%에서 3~4건만 실행되고 16~17건이 대기해 "텍스트 20동시" 설계와 달랐다(오류 0, 60/60). 부분 결과는 `ab/new-qwen-mtp-on/soak.aborted-img4096/`에 보존. 코덱스 검수 의견을 받아 `soak.sh`를 고친 뒤 처음부터 다시 돌린다
- **P3 A/B 2차분 (10-09 00:37~)**: 계획 P3 중 남은 항목(품질 greedy 20개, 회귀 집중: 숫자 복사·숫자/괄호 도구 인자·thinking 켬 도구 호출·JSON 스키마·같은 이미지 반복·6만 토큰 입력, `traffic_test` 3회 텍스트·이미지 1024px). 신규 `tests/ab_regression_probe.py` + `~/vllm-upgrade/ab_regress_side.sh`(양쪽 md5 일치), 연구계에서 순서 진행(새 qwen-mtp-on → 옛·새 gemma31b → gemma26b → qwen-mtp-off). 진행 로그 연구계 `~/vllm-upgrade/regress_orch.log`. 시운전(00:28, 새 qwen-mtp-on, 긴 입력 3천 토큰) 19/19 통과
  - **00:40 중단 → 00:45 재시작**: 코덱스 1라운드(`scratchpad/collab/vllm-ab-review/r1_codex.md`)가 탐침 1판의 거짓 통과를 짚었다(스키마 타입 미검사, 이미지 '15' 정답 처리, 스트림 도구 호출 id·type·종료 미검사). 코드로 확인한 뒤 2판(md5 `ade4f175`)으로 고쳐 모의 입력·실서버 시운전(23/23)을 거쳐 처음부터 다시 돌렸다. 1판 출력은 `ab/new-qwen-mtp-on/regress.aborted-v1/`
  - 재시작 순서에 더한 것: gemma31b·gemma26b 속도 4·5회차(회차 변동으로 판정이 뒤집힐 수 있는 칸, 판정표 성능 절), 새 gemma26b-pt(`quantization: fp8_per_tensor` 한 줄만 바꾼 묶음, 시험장 `bundle/gemma26b-pt`)의 탐침
  - `traffic_test`의 exit=1은 사후 확인이 게이트웨이 전용 `/server-status`를 백엔드에 조회해 404를 받은 부산물이다(60/60 성공). 지표 대조는 `scratchpad/ab_traffic_compare.py`로 한다
- **P3 MTP 양성 대조 (10-09 03:09~04:07 완료, 결과: 검출력 미확인)**: 10-07 옛 nightly MTP 켬에서 실측된 손상(`hjjo-ai-hub/.archive/2026-10-07_hw-chatbot-대화품질/FINDING-서빙-접두캐시.md`)을 근거로, 옛 nightly MTP 켬 → 새 0.31 MTP 켬 순서로 MTP 탐침 3판(md5 `3f658b62`, 이미지 다중 턴·이상 응답 검사·시험 무효 분리·원문 보존)을 15라운드·동시 12, `--expect-mtp`로 돌린다(`scratchpad/mtp_pair.sh`). 옛 쪽 검출 여부로 탐침 검출력을 정한다. 2판(`78b808b6`)은 코덱스 2라운드에서 요청 실패를 무시하는 종료 판정이 확인돼 실행하지 않았다
  - 결과: 옛 nightly(Triton 커널)와 새 0.31(Marlin 커널) 모두 유효 탐침 16/16에서 손상 0, 부하 실패·이상 응답 0이다. 수락률은 0.744와 0.741이다. 옛 쪽이 미검출이므로 사전 정책대로 "검출력 미확인"으로 적고 운영 Qwen MTP 끔을 유지한다. 같은 새 기동의 회귀 탐침 4판은 24개 전부 통과, greedy #15는 `7800`이다(판정표 #53912 절)
- **P3 장시간 부하 2판 (양성 대조 뒤 예정)**: `soak_v2.sh`·`soak_chain_v2.sh`·`soak_summary.py`(스크래치 초안, 코덱스 3라운드 지적 M1·M2 반영). 회귀 탐침은 A/B 2차분이 끝난 뒤 4판(greedy 예외 보존, 코덱스 3라운드 M3)으로 바꿔 양성 대조·장시간 부하에 쓴다. 판정표 장시간 부하 절의 1판 중단 사유와 2판 변경점 참고
  - A/B 뒤 자동 진행(스크래치 `after_orch_v2.sh`, 10-09 01:38 대기 시작). 1판은 코덱스 4라운드 Q1·Q2 지적으로 01:35에 중단했고, 그때는 A/B 종료를 기다리는 첫 단계였다. 1판의 결함은 두 가지였다. 시험장 경로가 연구계 홈으로 확장됐고, 단계가 실패해도 다음 단계로 넘어갔다. 2판의 동작은 다음과 같다
    - A/B 진행 스크립트가 정상 종료 기록을 남기고 GPU 2가 비었을 때만 다음 단계로 간다
    - 시험장 파일은 `.new`로 올린다. 묶음 전체의 해시가 맞을 때만 이전 판을 보존하고 교체한다
    - 양성 대조가 기동 실패로 끝나면 멈춘다. 결과 파일이 이미 있으면 덮어쓰지 않는다(`mtp_pair.sh` exit 1·4)
    - 장시간 부하 시작은 이번 실행 시각 뒤의 새 기록과 연쇄 프로세스로 확인한다
    - 5라운드 J2와 T0 보완: 탐침 완료는 허용 종료 코드와 결과 줄이 둘 다 있을 때만 인정한다. 원격 기준 시각의 형식이 틀리면 멈춘다. 이 보완을 넣으려고 02:01에 대기 단계에서 다시 띄웠다
  - **코덱스 설계 검수 종료 (10-09 02:14, 6라운드)**: 시험 도구와 자동 진행의 설계 쟁점은 미합의 0건, 신규 핵심 쟁점 0건으로 닫았다. 커널 기여량을 분리하지 않은 한계(C2)는 부분 합의로 남는다. 실제 결과 검수는 7라운드부터 한다. 결정 기록은 `scratchpad/collab/vllm-ab-review/decision_log.md`에 있다
  - **Qwen 블록 FP8 커널 진단 (10-09 03:1x 결정, 장시간 부하 앞에 끼움)**: qwen-mtp-off A/B에서 Qwen에만 세 가지 차이가 나왔다. 이미지 TTFT p50이 1.7배, 6만 토큰 요청 경과 시간이 1.54배 길었고, greedy #15 계산 답이 기동 세 번 모두 틀렸다. 0.31이 L40S에서 블록 FP8 선형층을 Triton W8A8 대신 Marlin(가중치만 FP8)으로 고른 것이 우선 검증할 후보다. GDN 연산 이름과 그래프 설정도 달라 다른 후보는 아직 배제하지 않았다(판정표 「품질·회귀 집중」 qwen-mtp-off 항목)
    - 스크래치 `soak_hold`로 후속 연쇄 2판이 양성 대조까지만 하고 멈추게 했다(설계된 보류 경로). 실행 중인 스크립트는 고치지 않았다
    - 이어서 `diag_qwen.sh` 4판이 자동으로 돈다(03:59 대기 시작). 1~3판은 코덱스 7~9라운드 지적을 반영하려고 모두 대기 단계에서 멈췄다(원격 동작 없음)
      - 옛·새(자동)·새 `-tri`(`linear_backend: triton` 블록) 순으로 기동한다. 각 기동에서 #15를 3회 묻고 긴 입력 16k·60k의 스트리밍 TTFT를 3회씩 잰다
      - tri는 회귀 탐침 4판, 트래픽 3회, 속도 3회까지 돌린다. 실행·전송·자료 실패는 기본 분기로 보내지 않고 멈춘다. 받은 결과는 `diag_validate.py`로 검사한다
      - 그 뒤 `soak_start.sh`(후속 연쇄 ④를 떼어 변형 목록만 인자로 받게 한 것)로 장시간 부하를 시작한다. 반환값은 그대로 전달한다
    - 장시간 부하의 MTP 끔 칸을 `-tri`로 바꿀지는 결과 전에 고정한 S규칙(`diag_rule.py`, 반례 모의 20종)으로 정한다. MTP 켬 칸은 바꾸지 않는다
    - 운영 권고는 P규칙 3판으로 판정한다(코덱스 9라운드 판정 원칙 합의, 판정표 qwen-mtp-off 항목). 성능 ⏸ 칸의 4·5회차는 `ab_extra45.sh`로만 잰다. 기존 `ab_regress_side.sh`의 speed45 모드는 회귀·트래픽 1~3회차를 다시 써서 폐기했다(코덱스 9라운드 R9-01)
    - **진단 결과(04:08~05:29)**: 긴 입력 TTFT는 자동(Marlin)이 옛 대비 1.64·1.54배(❌), tri는 0.99·0.98배(✅)다. #15는 옛·자동·tri 모두 `7800`이다. S규칙은 미충족이므로 장시간 부하는 기본 묶음으로 05:32에 시작했다
    - **P규칙 판정**: 사전 규칙 그대로면 tri는 권고하지 않는다(G2 #15 실패, 성능 ✅ 25 · ⏸ 3). #15 제외는 사후 분석으로만 따로 적었다. 조건 처리와 tri 후보 유지 여부는 대표님 결정 사항이다(판정표 진단 결과)
    - **코덱스 협업 종료(06:20경, 10라운드 상한)**: 미합의 0건이다. 장시간 부하, tri 묶음 부하, ⏸ 3칸 4·5회차, #15 원인 확인, 운영 GPU 커널 확인은 보류 목록으로 넘겼다(`scratchpad/collab/vllm-ab-review/decision_log.md` §4)
    - 05:29~05:40 장시간 부하 시작 단계에서 사고가 1건 있었다. 원격 명령 `cd X && setsid nohup … &`의 서브셸이 ssh를 붙잡아 시작 확인 단계가 멈췄다. 그 서브셸만 종료했고, 부하 연쇄는 다른 세션이라 계속 돈다. `soak_start.sh`는 `cd X || exit 1; …`로 고쳤다
- **P3 장시간 부하 진행(10-09 05:32~)**: 기본 묶음 `qwen-mtp-on gemma31b gemma26b qwen-mtp-off`, 변형마다 120분. 변형이 끝날 때마다 판정표 장시간 부하 표에 적는다
  - qwen-mtp-on(05:32~07:37)은 통과 후보다. 3,164건이 모두 성공했고, 고정 사례·회귀 24/24·동시 이미지 정답이 중간·끝 모두 통과했다. 유휴 메모리는 평탄했다
  - gemma31b(07:44~09:46)는 통과 후보다. 7,910건이 모두 성공했고, 고정 사례·회귀 23 통과(긴 입력 1 건너뜀)·동시 이미지 정답이 중간·끝 모두 통과했다. 유휴 메모리는 평탄했다
  - 09:56 연쇄가 멈췄다. gemma31b를 내린 뒤 GPU2에 2,951 MiB가 남아 다음 변형을 띄우지 않았다(설계된 중단 경로). 점유는 09:11경 시작됐고 시험장·연구계 어느 PID 공간에도 보이지 않는 외부 프로세스다. 처음에는 GPU2가 비기를 기다렸다
  - 11:2x 대표님 지시("gpu2 써")로 연쇄 3판을 반영했다. 3판은 비움 상한을 환경변수로 받고, 이번 실행은 4000 MiB로 다시 시작했다
  - 11:35 대표님 결정으로 gemma26b를 건너뛰었다(운영 인스턴스가 아님). 기동 중에 런처를 내렸고, 이때 고아로 남은 EngineCore는 PID로 종료했다
  - 11:38 qwen-mtp-off 런처를 기동했고 11:42에 백엔드가 준비됐다
  - qwen-mtp-off(11:42~13:48)는 통과 후보다. 2,599건이 모두 성공했고, 고정 사례·회귀 24/24·동시 이미지 정답이 중간·끝 모두 통과했다. 유휴 메모리는 평탄했다. 전 구간이 외부 점유와 함께였다
    - 13:53 연쇄가 런처를 내렸다. 사후 확인은 스크래치 `post_qwen_off_check.sh`로 했고, 결과는 `collab/final-verdict-review/qwen_off_post/`에 있다. 결과 회수, 재집계(종료 0), 엔진·게이트웨이 원문 독립 검사(실행 구간 오류 0, 자동 재기동 0)를 마쳤다. PID·세션 번호로 잔존 프로세스가 0인 것도 확인했다
    - 이것으로 장시간 부하 세 변형(qwen-mtp-on, gemma31b, qwen-mtp-off)이 모두 통과 후보다. gemma26b는 대표님 결정으로 생략했다
- **P3 Gemma MTP 상류 버그 재현 시험(10-09 13:53~)**: 대표님 지시("큐웬 끝나면 두 건 재현 시험 해봐")에 따라 진행한다. 탐침은 `tests/mtp_known_bug_probe.py`, 연쇄는 스크래치 `mtpbug_run.sh`(3판), 실행 ID는 1009-135350이다
  - 두 건은 다음과 같다. ① #38106: 추론 켬 + 추측 디코딩 + 문법 제약(JSON 스키마, 도구 강제)에서 추론 끝 경계가 어긋나는 결함이다. ② #46088: KV `auto` + MTP에서 긴 요청과 짧은 요청을 섞으면 짧은 요청이 깨지는 결함이다
  - 순서: 새 gemma31b(fp8 KV) → 새 gemma31b-kvauto(운영과 같은 KV auto, 길이 4096·배치 2048로 축소) → 옛 gemma31b(양성 대조) → 옛 gemma31b-kvauto(지금 운영 조합). 증상이 나오면 같은 설정에서 MTP만 끈 대조군을 돌린다
  - 설계 검수는 코덱스와 3라운드로 했다(`collab/mtpbug-review/`). 2라운드의 P0 두 건(기능 시험 자식 추적 누락, 기동 기록 공백)은 환경 변수 소유 표식과 "상태 기록 뒤 exec"로 고쳤다. 3라운드에서 새 P0는 없었고, 권장 보완 다섯 건도 반영했다
  - 이 검수 고리는 10-09 21:51 8라운드로 닫았다(결정 기록 `collab/mtpbug-review/decision_log.md`). 남은 한계 두 가지: 세션 밖 프로세스의 환경 표식은 읽을 수 있는 것만 확인한다(R3-02). 연쇄의 상태 쓰기 실패와 원격 조회 비정상 종료는 실패를 넣어 시험하지 않았다(R3-06). 이 연쇄를 다시 쓰기 전에 그 두 실패를 넣는 모의 시험을 먼저 한다
  - 실행 1009-135350 도중 백엔드 소유 확인 도우미를 교체했다(`hotfix_1009-135350.txt`, EngineCore의 환경 변수가 지워져 fd 1·2의 기동 로그 연결로 소유를 보완). 요청 생성·탐침 판정 코드는 바꾸지 않아 측정은 유효하다. 보완의 범위는 같은 세션·실행 전용 로그 조건까지이고, 세션을 벗어나 환경 표식도 지운 프로세스를 전수 추적하지는 않는다(코덱스 R4-07)
  - 판정 규칙: 같은 설정의 MTP 켬에서만 증상이 나오면 운영 Gemma MTP 끄기를 권고한다. 축소 조건에서 미검출이어도 운영 64k 조건의 안전 근거로 쓰지 않는다. #46088이 미해결로 남으면 기본 추천은 MTP 끄기이고, 이를 대표님 결정 항목으로 올린다
  - 12시 종합 판정 초안에 대한 코덱스 검수 1라운드(`scratchpad/collab/final-verdict-review/r1_codex.md`)를 받았다. P0은 없고 P1은 4건이다
    - 판정표: 시험 판정과 채택 결정을 나눴다. Gemma 성능 보류 5칸은 "통과"로 쓰지 않고 대표님 결정 ⑧로 넘겼다. Qwen #15의 품질 보류도 종합표에 되살렸다
    - 연쇄 스크립트: 2판부터 있던 경로 두 개를 찾았다. 하나는 로그를 읽지 못해도 자동 "통과 후보"가 되는 경로이고, 다른 하나는 런처 조회가 실패하면 런처가 없는 것으로 보는 경로다. 실행 중인 연쇄는 고치지 않는다. qwen-mtp-off가 마지막 변형이므로, 엔진·게이트웨이 원문 로그와 종료 뒤 프로세스를 사람이 확인해 대신한다
  - 공백 대조 연쇄(실행 1009-152740, 15:27~): 0.31·옛 nightly 각각 KV auto MTP 켬·끔 네 구성에서 종류마다 80건이다. 3단계(옛 KV auto MTP 켬, 지금 운영 조합)에서 문법 증상 108/320이 나와 17시 20분경 대표님이 운영 Gemma MTP 끔을 결정했다(master 결정 ⑨). 4단계(옛 끔)는 미리 정한 비교를 마치려고 그대로 진행한다
- **P3 MTP 끔 운영 조합 점검(10-09 18:00 대기 시작, 스크래치 `nomtp_check.sh`)**: 결정 ⑨의 조합(0.31 + Gemma 31B MTP 끔)은 문법 탐침 말고는 시험한 적이 없어서, 이미지 확인 전에 pip 환경에서 먼저 본다
  - 묶음 `gemma31b-nomtp`(A/B 묶음에서 MTP만 끔). 공백 대조 연쇄가 끝나고 GPU2가 비면 자동으로 시작한다
  - 순서: 기동(로그에서 `speculative_config=None` 확인) → 기능 시험 전체(직접) → 회귀 탐침(직접) → 게이트웨이 시험(`gw_tests.sh`, 새 게이트웨이) → 장시간 부하 120분
  - 기능·회귀·게이트웨이 중 하나라도 실패하면 런처를 내리고 멈춘다. 장시간 부하는 연쇄 4판으로 돌린다. 4판은 3판과 한 줄만 다르다: 긴 입력 건너뛰기 조건에 `gemma31b-nomtp`를 넣었다(길이 8192)
  - **결과(18:27~20:54)**: 기동 18:32(`speculative_config=None`, KV 17,385토큰), 기능 31/31, 회귀 24 통과(긴 입력 1 건너뜀), 게이트웨이 시험 통과, 2시간 부하 104회차·2,938건 실패 0(통과 후보). 수동 판정 관문도 통과했다(오류식 1줄은 기능 시험의 의도된 404, 재시작 0, 게이트웨이 오류 0, 잔존 0). 처리량은 MTP 켬 부하의 약 37%다
  - 4판에는 자동 판정의 알려진 두 경로(로그 읽기 실패를 오류 0으로 셈, 런처 조회 실패를 부재로 봄)가 그대로 있다. 그래서 자동 "통과 후보"만으로 판정하지 않고, 런처 로그 전 구간·게이트웨이 로그 원문 검사와 종료 뒤 프로세스 잔존 확인을 사람이 한다. 판정표 해당 절에 관문을 적었다(코덱스 R5-07)
- **P3 이미지 확인 스크립트 예행(10-09 20:55~, 스크래치 `image_check.sh`)**: 마지막 단계 명령 묶음 ④·⑥의 결함(읽기 전용 볼륨에 쓰는 런처·게이트웨이·시험 도구, 127.0.0.1 묶음에 닿지 않는 포트 연결, 홈을 읽기 전용으로 붙이면 진입점 `chown -R`이 실패해 컨테이너가 멈춤)을 고치려고 만든 스크립트를 시험장 pip 환경에서 미리 돌린다
  - 1차(20:55~21:24, 판 `27ffe2b7`, `gemma31b-nomtp gw`, 부하 5분): 첫 기동 5분 52초(새 HOME이라 컴파일 캐시 없음), 실행 경로 줄 9줄이 2시간 부하 기동과 같음(Cutlass FP8 선형, TRITON_ATTN, 240층, KV 17,385토큰). 기능 31/31, 회귀 24 통과·1 건너뜀, 게이트웨이 조합·호환 통과, 부하 113건 실패 0(집계 통과 후보), 게이트웨이 로그 오류 0, 기동 뒤 오류식 1줄은 의도된 404, 종료 0. 기준 시각 뒤 `/workspace`·`/home/hgiai` 아래 바뀐 파일은 기존 로그 수집 루프(`logging.sh`, 10-08 17:26부터 5분 간격)의 `logs/logging.out`과 VS Code 잠금 파일뿐이었다
  - 2차(21:25~21:40, 수정 판 `13bf8253`: 작업 폴더 변수 `IMAGE_CHECK_VU`, 런처 세션 잔존 확인, 길이 값 검사, 그래프 메모리 줄 추출, `qwen-mtp-off gw`): 인자 오류 4경우가 모두 종료 2이고 폴더를 만들지 않음을 먼저 확인했다. 기동 6분 22초, 기능 31/31, 회귀 24 통과(긴 입력 6만 토큰 포함), 게이트웨이 조합·호환 통과, 오류식은 의도된 404 1줄, 세션 잔존 0, 종료 0. KV 83,012토큰(10-09 11:41 장시간 부하 기동과 같음)
  - 판 `5bc51fc4`: 2차에서 실행 경로 패턴이 Qwen의 본 어텐션 백엔드(FLASH_ATTN·FA2)와 GDN 커널 줄을 놓쳐 추출 패턴만 넓혔다. 두 예행 기동 로그에 다시 적용해 확인했다(Gemma 10줄, Qwen 13줄)
  - 판 `812a85d8`(코덱스 6라운드 R6-01·R6-02 반영, 시험장 반영본도 같은 해시): 프로세스 목록 조회가 실패하면 잔존 0으로 보지 않고 실패한다. 기동 뒤 로그는 한 시점 사본으로 구간 줄 수까지 맞춰 보고, 검색 종료 2 이상은 실패로 센다. 유휴 표본의 RSS 조회가 실패하면 0 대신 빈 칸을 써서 집계가 보류하게 했다. 함수만 뽑아 실패를 넣는 모의 시험 13경우가 연구계·시험장 모두 기대대로였다(스크래치 `mock_r6.sh`). 명령 묶음 ⑥ 반복문은 한 변형이라도 실패하면 멈추고 장시간 부하를 시작하지 않는다(가짜 docker로 확인)
- **P3 후속 측정(10-09 07:31 대기 시작, 연구계 스크래치 `post_soak.sh` 4판)**: 코덱스 10라운드 보류 목록 중 Claude 담당 두 항목을 장시간 부하 뒤에 무인으로 잰다
  - 측정 1: ⏸ 3칸의 4·5회차. 옛 qwen-mtp-off와 새 tri에서 `ab_extra45.sh img speed`로 잰다
  - 측정 2: #15 원인 확인. 옛 두 번, tri, 자동 기동에서 회귀 탐침 전체를 기동 직후 먼저 묻는다. 이어서 `q15_cause.py`로 logprobs·이력·salt 조건을 나눠 묻는다. 캐시 지표 차이는 기록만 하고 해석하지 않는다
  - 설계 검수는 코덱스와 3라운드로 했다(`scratchpad/collab/post-soak-review/decision_log.md`). 3라운드에서 원격 단계 중단 경로의 P0 결함이 나왔다. 4판에서 고쳤고, 종료 후 확인에서 코덱스가 무인 실행에 동의했다
  - 진행 로그는 연구계 `~/vllm-upgrade/post_soak.log`, 결과는 `~/vllm-upgrade/post_soak/`다. 종료 0은 단계가 모두 유효하게 끝났다는 뜻일 뿐이며 운영 판정이 아니다
  - **10-09 09:40 중단(대표님 결정)**: 블록 FP8 커널은 설정하지 않고 vLLM 기본 선택을 쓴다. 그래서 Triton 비교용인 이 측정은 대기 단계에서 멈췄다. 원격 동작은 없었다. 판정표 "결정 기록"에 남겼다

## 검증
- 이미지 확인 항목 전부 통과, 대조표와 `aws/image-freeze-0.31.0.txt` 작성
- 시험장 되돌리기 예행 기록 (절차, 소요 시간)
- 판정표의 모든 행에 옛·새 값과 판정이 있음
- 각 시험 시간이 끝나면 :5015가 옛 환경으로 복구돼 `./start.sh status`와 대상 지정 시험이 정상

## 완료 기준
- [ ] `aws/` 변경 커밋 (운영 반영 전), 맨 마지막에 새 이미지 임시 컨테이너 확인 완료
- [ ] 판정표 완성, 코덱스 검수 (판정 해석)
- [ ] 대표님 판정: 운영 반영 승인
- [ ] master Phase 맵에서 part2 상태 갱신
