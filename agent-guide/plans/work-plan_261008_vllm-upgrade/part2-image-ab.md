# Part 2: 이미지 반영과 A/B 시험 — P2-P3

> master: [master.md](master.md)
> 선행 Part: [part1](part1-prep-staging.md) | 후속 Part: [part3](part3-rollout-cleanup.md)
> 담당 Phase: P2-P3 | 변경 파일: 레포 수정 5, 신규 3, 조건부 1 + git 밖 env 4 | 상태: 초안 v3.2

## 목표
- P1 예행 기록을 근거로 `aws/`를 고치고, 대표님이 빌드한 새 이미지로 시험장을 다시 만든다. 이 이미지의 베이스·패키지 조합을 기록해 운영 빌드와 대조할 기준으로 삼는다.
- 새 이미지 시험장과 연구계 옛 환경을 같은 GPU에서 차례로 띄워 기능·회귀·성능을 비교하고 판정표를 만든다.

## 전제 조건
- [ ] part1 완료: 예행 설치 기록, 설정 해석 9/9, 시험 설정 묶음
- [ ] 결정 ⑤ effort 의미 (P3 전)
- [ ] P3 시작 시 대표님이 GPU 0·1을 비워 줌

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
- [ ] 대표님 요청 사항 (연구계 호스트)
  - 시험장 이미지 이름을 `user.sh` 컨테이너와 겹치지 않게 한다. 공통 `.env`의 `LLM_IMAGE_NAME`은 `user.sh`도 읽으므로(`aws/user.sh:38-46`) 바꾸지 말고, 시험장 전용 env 파일이나 그 compose 명령에만 값을 준다
  - 지금 시험장 컨테이너의 이미지 ID에 되돌리기 태그를 붙인 뒤 빌드 → `llm-hgiai` 재생성. `/workspace`, `/home/hgiai`는 호스트 볼륨이라 레포 사본과 기록이 남는다
- [ ] 이미지 확인 (재생성된 시험장)
  - `python`, `python3`, `python3 -m pip`, `vllm`의 실경로·버전, `pip check`
  - 로딩 위치: `vllm`, `torch`가 시스템 site-packages에서 올라오는지. 사용자 site와 겹치는 패키지 목록
  - 실행 중 추가 설치: `EXTRA_REQUIREMENTS`가 비어 있는지. 쓰면 같은 제약을 건다
  - 재생성 뒤 `hgiai` 사용자·홈 소유권·sudo. 0.31 이미지에는 UID 2000 `vllm` 사용자가 있고 Ubuntu 24.04에는 UID 1000 `ubuntu`가 있지만, `entrypoint-llm.sh:50-57`이 같은 UID의 기존 사용자를 지우고 새로 만든다
  - 핵심 패키지 대조표: 이미지 값과 P1 예행 기록을 나란히 적고 다른 항목은 이유를 적는다
  - 설정 해석 9/9 재실행, `async_scheduling` 최종값 False
  - 생성기 `--final` 통과(FlashInfer cubin·jit-cache의 존재·버전·CUDA 표시 포함), 음성 모듈 import(soundfile, soxr, av, torchcodec, `mistral_common.audio`), 게이트웨이 의존성 import
- [ ] 이미지 기록: 베이스 다이제스트, 빌드 인자(`MODE` 등), 생성기 `--final` 출력, 전체 `pip freeze`를 `aws/image-freeze-0.31.0.txt`에 남긴다. 운영 빌드 결과를 이 파일과 대조한다(part3)
- [ ] 시험장에서 되돌리기 절차 예행: 새 이미지 → 태그해 둔 이전 시험장 이미지 → 새 이미지로 재생성해 절차와 소요 시간을 확인한다. 시험장은 compose 컨테이너라 compose 경로로 한다. 이미지는 `LLM_IMAGE_NAME=<보존 태그>`로 고르고 `--no-build --pull never`를 붙인다. 이 예행은 compose 절차의 확인이며, 운영 `user.sh` 절차를 실행 검증한 것으로 기록하지 않는다. 운영에서 실연하자는 뜻도 아니다

### 게이트웨이 effort 처리 (결정 ⑤가 "지금 의미 유지"일 때만)
- [ ] `llm-serving/vllm/vllm_gateway.py`: 번역한 effort를 최상위 `reasoning_effort`가 아니라 `chat_template_kwargs.reasoning_effort`로 넘긴다. 최상위 필드는 지금처럼 지운다
  - 0.31의 자동 thinking 매핑은 최상위 값이 있을 때만 일어난다(`chat_completion/protocol.py:584-586`). 템플릿 인자로 넘기면 매핑을 피하고, thinking 기본값은 서버가 자기 설정으로 정한다. 기본값을 게이트웨이에 복제할 필요가 없다
  - 옛 nightly도 같은 병합 규칙이다: 최상위가 None이면 템플릿 인자의 값을 남긴다(`renderers/params.py`의 `merge_kwargs`). 두 버전에서 동작이 같다
  - 최상위 effort를 따로 쓰는 곳은 Harmony 렌더러(gpt-oss)뿐이다(`renderers/online_renderer.py:522`). 지금 번역표에 있는 계열(qwen3.8)과 무관하다
  - `none → enable_thinking=false`, 미지원 계열의 effort 제거, `X-Effort-Applied` 헤더는 그대로 둔다
- [ ] 의미 보존 범위는 **게이트웨이 경유**다. 백엔드 직접 호출은 0.31의 새 의미를 따른다. `VLLM_OPS_GUIDE.md`에 적는다(part3)

### P3 A/B 시험 (GPU 0·1, 대표님이 비워 준 시간)
- [ ] 배치: 모델마다 옛 환경(연구계 hjjo `~/.local`) 기동 → 시험 → 내림 → 새 이미지(시험장) 기동 → 같은 시험 → 내림. part1의 시험 설정 묶음과 같은 시험 인자만 쓴다
- [ ] 순서: Gemma 4 31B → 26B-A4B → Qwen3.8(MTP 끔, 이어서 새 쪽만 MTP 켬) → STT 3종. 위험이 큰 Gemma 31B를 먼저 본다
- [ ] 기동 로그 대조: Model Runner, 어텐션 백엔드, 양자화 방식과 경고, MTP 방식, KV 블록 수·최대 동시성, CUDA graph 캡처 시간, 기동 소요. 새 이미지는 V2여야 하며, V1으로 돌아가면 통과로 치지 않고 원인을 기록한다. 옛 환경은 기준선이므로 V1이어도 그대로 기록한다
- [ ] 기능: `tests/test_vllm_server.py --base-url http://localhost:<백엔드 포트>` (직접 호출). `./start.sh test`는 실행 중인 게이트웨이를 모두 돌므로 쓰지 않는다. STT는 `test_stt_server.py`
- [ ] 게이트웨이 경유: part1의 게이트웨이 사본으로 띄운다(정식 `gateways/`·`instances/`를 쓰지 않는다). 정체성 문구 주입, developer 역할 병합, `/v1/audio/*`, `/v1/realtime` 중계를 본다
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
- [ ] STT: 정답 표본 20개의 CER, 30초 넘는 음성 1건(Whisper), Voxtral `/v1/realtime` 연결·종료. 긴 음성과 리샘플링 확인은 CER 표본과 따로 판정한다
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
| STT CER | CER = (치환+삭제+삽입) 합 / 정답 글자 수 합. 정규화(문장부호 제거, 띄어쓰기 제거)를 고정하고 CER_새 − CER_옛 ≤ 0.01. 오류 글자 수와 분모를 함께 적는다. 표본 20개는 회귀 점검용이며 품질 전체를 증명하지 않는다 |
| STT 입력 호환 (44.1kHz WAV·MP3) | 새 쪽 12건 모두 성공 조건 충족. 옛 쪽 결과는 위 판정 규칙으로 분류한다. 모든 형식·대체 경로를 덮는 시험이 아니다 |
| 장시간 부하 | 엔진 오류·자동 재기동 0건, 요청을 비운 뒤 메모리 증가가 이어지지 않음. 429만 쌓인 회차는 부하 시험으로 치지 않는다 |
| 안정성 입력 | 4xx 거절, 엔진 생존 |

문턱 값(5%, 1%p)은 이 계획이 제안한 값이다. vLLM이 보장한 수치가 아니다.

## 검증
- 이미지 확인 항목 전부 통과, 대조표와 `aws/image-freeze-0.31.0.txt` 작성
- 시험장 되돌리기 예행 기록 (절차, 소요 시간)
- 판정표의 모든 행에 옛·새 값과 판정이 있음
- 각 시험 시간이 끝나면 :5015가 옛 환경으로 복구돼 `./start.sh status`와 대상 지정 시험이 정상

## 완료 기준
- [ ] 새 이미지 시험장 확인 완료, `aws/` 변경 커밋 (운영 반영 전)
- [ ] 판정표 완성, 코덱스 검수 (판정 해석)
- [ ] 대표님 판정: 운영 반영 승인
- [ ] master Phase 맵에서 part2 상태 갱신
