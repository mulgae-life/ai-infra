# Part 1: 준비와 시험장 — P0-P1

> master: [master.md](master.md)
> 선행 Part: - | 후속 Part: [part2](part2-image-ab.md)
> 담당 Phase: P0-P1 | 변경 파일: 레포 0개 (시험장 레포 사본, 레포 밖 기록) | 상태: 초안 v3.2

## 목표
- 결정 요청을 올리고, A/B 기준선과 운영 되돌리기 묶음을 기록한다.
- GPU 없이 할 수 있는 준비를 시험장 `llm-hgiai`에서 끝낸다. 코드를 옮기고 0.31을 예행 설치해 의존성 충돌을 찾고, 설정 9개가 새 버전 인자 파서에서 의도한 값으로 해석되는지 확인한다.

## 전제 조건
- [ ] 이 계획서 확정
- [ ] 결정 ② 목표 버전 (없으면 0.31.0)

## 작업 목록

### P0 준비
- [ ] 결정 요청 전달 (master "결정 요청" 표). 결정 ⑥은 P4 전까지만 받으면 된다
- [ ] :5015 담당 세션에 Qwen3.8 MTP·effort 의미 확인 (대표님 경유)
- [ ] 기준선 기록 (연구계 hjjo, 옛 환경)
  - `~/.local` 패키지 목록(`pip freeze --user`), `vllm --version`
  - 인스턴스별 최근 기동 로그의 핵심 줄: Model Runner, 어텐션 백엔드, KV 블록 수·최대 동시성, MTP 방식
  - `tests/results/speed_results.md`는 참고만 하고, 판정에는 같은 시간대에 다시 잰 값을 쓴다
- [ ] 되돌리기 묶음 정의 (대표님께 받을 값 포함)
  - 운영 컨테이너가 **실제로 쓰는 이미지 ID**(`docker inspect`의 Image 값). 이름표(`llm-prd`)만으로는 어느 이미지인지 보장되지 않는다. 되돌릴 때 셸 변수가 아니라 이 기록 파일로 대조한다(part3)
  - 운영 env의 `VLLM_IMAGE`·`LLM_IMAGE_NAME`·`EXTRA_REQUIREMENTS` 현재 값과, `user.sh rebuild`가 옛 컨테이너가 아니라 `.env`에서 다시 읽는 런타임 값(`SHM_SIZE`·`LLM_MEMORY`·`VOLUME_PATH`, `aws/user.sh:47-51`)
  - 운영에 배포된 `llm-serving/`·`aws/`의 커밋과, 커밋 밖 변경이 있는지 여부
  - 모델 파일 해시: 대상 모델의 `config.json`, 토크나이저 파일, 채팅 템플릿. 모델은 이번 변경 대상이 아니지만 다른 세션의 변경과 구분하려고 남긴다
  - 되돌리기는 이미지만으로 끝나지 않는다. `/workspace`·`/home`은 호스트 볼륨이라 재생성해도 남으므로 설정·게이트웨이 코드·사용자 패키지 복구도 묶음에 넣는다
- [ ] 시험장 현황 기록: `pip freeze`(시스템), `pip list --user`, `/etc/ld.so.conf.d/`, Python 경로
- [ ] 디스크 예산: 시험장과 연구계가 같은 nvme를 쓴다(10-08 남은 106GB). 새 이미지 레이어, 예행 설치, 패키지 캐시, 시험 로그를 이 하나의 여유에서 나눠 쓴다고 보고 예산을 적는다

### P1 시험장 준비 (`llm-hgiai`, GPU 불필요)
- [ ] 코드 이관: `/workspace/ai-infra`에 GitHub에서 clone한다. `/workspace`는 호스트 볼륨이라 컨테이너를 다시 만들어도 남는다. 시험장에는 rsync가 없어 git으로 맞춘다
- [ ] 접속 방식: 시험장 `~/.ssh/authorized_keys`에 연구계 공개키를 등록해 비밀번호 입력 없이 접속한다
- [ ] 0.31 예행 설치 (시스템 위치, sudo). 목적은 의존성 충돌 찾기다. 지금 시험장은 CUDA 12.9 툴킷과 0.19 패키지가 남은 환경이라 GPU 실행 판정과 최종 조합 판정에는 쓰지 않는다
  - 순서는 운영 이미지와 같다: vLLM 0.31.0 → 핵심 패키지 제약 생성 → `aws/requirements.txt`를 그 제약으로 설치 → `pip check`
  - requirements는 P2에서 넣을 음성 묶음(av, `mistral_common[audio]`)을 더한 사본으로 설치한다. 여기서 해석된 음성 패키지 버전이 P2 `==` 고정의 **후보**다. 정본은 P2 이미지에서 확인하고 P3까지 통과한 조합이다(part2)
  - 제약은 `pip freeze` 문자열이 아니라 설치된 배포 메타데이터의 이름·버전으로 만든다. `pip freeze`는 직접 설치된 패키지를 `이름 @ 경로`로 내므로 `==` 필터는 vLLM을 빠뜨릴 수 있다
  - 충돌이 나면 제약을 풀지 말고 어떤 패키지가 무엇을 바꾸려 했는지 기록한다. 이 기록이 P2 Dockerfile의 근거다
  - FlashInfer 부속 패키지는 진단으로만 기록한다. PyPI의 vLLM 휠은 `flashinfer-cubin`을 의존성에서 뺀다(`setup.py:1342`, 공식 이미지는 `requirements/cuda.txt:18`로 설치). 그래서 예행에서는 cubin이 없거나 0.19 환경의 것이 남아 있을 수 있다. 버전과 출처를 적되 판정에 쓰지 않는다
  - 실제로 깔린 버전 기록: 생성기 `--final` 목록 전부. 없는 항목은 "없음"으로 적는다(예행은 실패로 끝나도 기록을 남긴다)
- [ ] 실행 경로 확인: `python`, `python3`, `pip`, `vllm`이 가리키는 파일과 버전. 사용자 site(`~/.local`)에 시스템과 같은 이름의 패키지가 있는지 본다(10-08 시험장: nvidia-ml-py, gpustat, nvitop)
- [ ] 설정 해석 확인 (엔진 기동 없음)
  - 인스턴스 9개(vllm 6, stt 3)를 런처가 만드는 임시 config 형태로 바꿔 0.31 인자 파서로 해석한다
  - 모르는 키·잘못된 값이 없는지에 더해, 핵심 값의 **최종 해석값**을 기록한다: `async_scheduling`(False여야 함), `quantization`, `speculative_config`, `reasoning_parser`, `tool_call_parser`, `default_chat_template_kwargs`
  - 런처의 `--no-async-scheduling` 주입이 있을 때와 없을 때를 모두 본다. 0.31도 밑줄 키 `async_scheduling: false`를 버리는지 실제 진입점으로 확인하는 단계다
- [ ] 경고 수집: `quantization: fp8` 사용 중단 경고 등 새 버전이 내는 경고 목록
- [ ] 음성 의존성: soundfile·soxr·av·torchcodec·`mistral_common.audio`를 import해 본다. torchcodec은 시스템 FFmpeg이 없으면 import 단계에서 실패하므로 그 결과도 적는다(`multimodal/media/audio.py:39-44`). 모델 기동은 P3에서만 한다
- [ ] STT 정답 표본 준비: `Bingsu/zeroth-korean`(CC BY 4.0) test 분할에서 20개와 정답 전사를 시험장 레포 밖(`~/vllm-upgrade/stt-ref/`)에 받는다. 데이터셋 리비전과 고른 20개의 ID를 기록한다. 기존 `zeroth_ko_sample` 1건만으로는 오류율을 비교할 수 없다
- [ ] 시험 설정 묶음 준비 (`instances/` 밖, 양쪽 동일)
  - 인스턴스 사본: GPU 2 고정·TP1(10-08 대표님이 GPU 2를 비움), Qwen3.8은 MTP 끔·켬 두 벌. 생성 스크립트·결과는 `~/vllm-upgrade/make_bundle.py`, `bundle/`
  - 변형마다 폴더를 따로 둔다(예: `qwen-mtp-off/`, `qwen-mtp-on/`). 게이트웨이 탐색은 실행 여부와 관계없이 폴더 안의 YAML을 모두 읽고, 같은 게이트웨이 포트에 실제 포트가 겹치면 설정 로딩에서 `ValueError`로 멈춘다(`vllm_gateway.py:214-241`). 한 시험에서 탐색 폴더에는 그 시험에서 쓸 변형 하나만 둔다
  - 게이트웨이 사본: `discover_from`이 그 시험의 변형 폴더를 가리키게 한다. 런처가 쓰는 `.runtime` 포트 파일도 그 폴더 기준이다. 시험마다 게이트웨이 기동 로그의 "매칭 N개" 줄로 의도한 백엔드 하나만 잡혔는지 확인한다
  - 시험장 clone에는 다른 세션의 미커밋 변경(Qwen MTP 끔, 5015 정체성 문구)이 없으므로 이 사본에 명시적으로 넣는다

## 변경 예시

**시험장 코드 이관**
```bash
git clone https://github.com/mulgae-life/ai-infra.git /workspace/ai-infra
```

**핵심 패키지 제약 생성기 (배포 메타데이터 기준)** — 이 파일을 P2에서 `aws/gen-core-constraints.py`로 커밋해 예행·이미지 빌드·운영 대조가 같이 쓴다. 파일은 하나이고 모드가 둘이다
- 기본 모드: `requirements.txt` 설치 **전**에 베이스의 핵심 조합을 `-c` 제약으로 낸다. 필수 항목이 없으면 실패한다
- `--final` 모드: 설치가 끝난 **최종 서빙 조합**을 확인·기록한다. FlashInfer 부속과 음성 경로까지 모두 필수다. 이미지 기록과 운영 대조는 이 출력으로 한다
```python
#!/usr/bin/env python3
"""vLLM 핵심 조합: 설치 전 제약 생성(기본) / 최종 서빙 조합 확인(--final)."""
import argparse
import importlib.metadata as md
import sys

CORE = ["vllm", "torch", "torchaudio", "torchvision", "triton", "transformers", "tokenizers",
        "flashinfer-python", "xgrammar", "fastapi", "starlette", "pydantic", "numpy",
        "mistral_common"]   # 베이스 버전 유지. requirements의 [audio]는 의존성만 채우고 버전은 못 바꾼다
# 베이스에 있으면 고정, 없으면 건너뜀. PyPI 휠은 cubin을 의존성에서 빼고(setup.py:1342) jit-cache도 넣지 않는다
CORE_IF_PRESENT = ["flashinfer-cubin", "flashinfer-jit-cache"]
# 최종 이미지에서만 필수: FlashInfer 부속, 음성 입력 경로(디코딩·리샘플), 유지하는 librosa
FINAL_EXTRA = ["flashinfer-cubin", "flashinfer-jit-cache", "torchcodec",
               "av", "scipy", "soundfile", "soxr", "librosa"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final", action="store_true", help="최종 서빙 조합 확인 모드")
    final = parser.parse_args().final
    required = CORE + (FINAL_EXTRA if final else [])
    optional = [] if final else CORE_IF_PRESENT
    missing = []
    for name in dict.fromkeys(required + optional):
        try:
            print(f"{name}=={md.version(name)}")      # +cu130 같은 로컬 버전 표시는 그대로 둔다
        except md.PackageNotFoundError:
            if name in required:
                missing.append(name)
    if missing:
        sys.exit(f"필수 패키지 누락: {', '.join(missing)}")


if __name__ == "__main__":
    main()
```
```bash
# P1에는 아직 레포에 없으므로 레포 밖 사본(~/vllm-upgrade/gen-core-constraints.py)으로 돌린다
G=~/vllm-upgrade/gen-core-constraints.py
python3 "$G" > ~/vllm-upgrade/vllm-core-constraints.txt
# 예행의 최종 조합은 누락이 있어도 멈추지 않고 출력과 종료 코드를 함께 남긴다
python3 "$G" --final > ~/vllm-upgrade/rehearsal-final.txt 2>&1; echo "exit=$?" >> ~/vllm-upgrade/rehearsal-final.txt
pip freeze > ~/vllm-upgrade/rehearsal-full-freeze.txt   # 재현 기록용. 제약으로 쓰지 않는다
```

**설정 해석 확인 (개념)**
```python
# 런처의 설정 변환으로 임시 config를 만든 뒤, vLLM 인자 파서로 해석만 한다
parser = make_arg_parser(FlexibleArgumentParser())
args = parser.parse_args(["serve", model, "--config", runtime_config, *launcher_extra_flags])
engine_args = AsyncEngineArgs.from_cli_args(args)
record(engine_args.async_scheduling, engine_args.quantization, engine_args.speculative_config)
```

## 실행 기록 (2026-10-08)
기록 위치: 연구계 `~/vllm-upgrade/baseline/`, 시험장 `~/vllm-upgrade/`
- **기준선 (연구계 nightly)**: vLLM 0.20.2rc1.dev251, torch 2.11.0+cu130, transformers 5.8.0, FlashInfer 0.6.11(cubin 0.6.11, jit-cache 0.6.11+cu129), mistral_common 1.11.2. av·torchcodec 없음, soundfile 0.13.1·soxr 1.1.0·librosa 0.11.0·scipy 1.17.1
- **코드 이관**: 시험장 `/workspace/ai-infra`에 clone(`de23caf`). 접속은 비밀번호 방식을 유지했고 공개키 등록은 하지 않았다
- **예행 설치**: vLLM 0.31.0 → 제약 생성 → requirements(+av, `mistral_common[audio]`) 설치 모두 종료 코드 0. `pip check`는 시험장 기존 시스템 패키지 1건(pygobject → pycairo)만 걸림. `--final` 누락 없음
  - 0.31.0 휠이 `torch==2.13.0`과 함께 `torchaudio==2.11.0`을 직접 고정한다(torchaudio 2.11.0은 torch 요구 없음). P2 이미지에서 공식 이미지 값과 대조
  - librosa가 하한(`>=0.11.0`) 때문에 1.0.0(메이저 변경)으로 해석됐다 → P2에서 연구계 값 0.11.0으로 고정(audioread 3.1.0이 함께 들어옴, 가상 설치로 해석 확인)
  - 음성 후보: av 19.0.1, soundfile 0.14.0, soxr 1.1.0, scipy 1.17.1, torchcodec 0.17.0, mistral_common 1.12.0
  - FlashInfer 부속은 0.19 환경의 cubin 0.6.6·jit-cache 0.6.6+cu129가 남았다(진단 기록만, 예상대로)
- **음성 import**: soundfile·soxr·av·torchcodec·`mistral_common.audio`·librosa·scipy 모두 성공. 시험장에는 `/usr/bin/ffmpeg`가 있다
- **설정 해석 9/9**: 옛 nightly·0.31 모두 해석 통과. 런처 주입(`--no-async-scheduling`)이 있으면 최종 `async_scheduling`=False, 없으면 None — 0.31도 밑줄 키 `false`를 버리므로 런처 우회는 계속 필요. 엔진 설정 단계(TP1 강제)는 LLM 5개 통과, `prd-pii-qwen`(체크포인트 없음)과 STT 3종(모델 없음)은 모델 경로 단계에서 멈춤
- **확인된 공백**: `/models/STT`가 비어 있다(08-26 이후, HF 캐시도 빈 항목). Qwen3.6-27B-FP8도 없다
  - 19:30 추가 발견: Gemma 4 26B-A4B 체크포인트(`/models/LLM/google/gemma-4-26B-A4B-it`)와 드래프트(`-assistant`)도 없었다(P1 점검 누락). 런처가 자동 다운로드를 시작해 그대로 받았다(49GB, 두 샤드 헤더 크기 일치 확인, `/models` 여유 260GB). `/models`는 연구계·시험장이 같은 호스트 볼륨을 공유하므로 양쪽에서 보인다
- **시험 묶음**: 4개 변형(gemma31b, gemma26b, qwen-mtp-off, qwen-mtp-on), GPU 2·TP1·내부 포트 6090/7090. 연구계·시험장 양쪽 md5 일치
  - 18:20 수정: `gemma31b` 변형에 L40S 한 장용 재정의(`max_model_len 8192`, `max_num_batched_tokens 8192`, `gpu_memory_utilization 0.92`). 65536으로는 가중치 32.33 GiB + 프로파일 피크 뒤 KV가 0.94 GiB만 남아 기동 실패(30.79 GiB 필요, `smoke-old-gemma31b.try3-kv-insufficient-65k.log`)
  - 18:28 추가: 8192·KV auto도 KV 4.53 GiB(6.89 GiB 필요)로 실패(`...try4-kv-insufficient-8k.log`, 가중치 외 피크 약 4 GiB) → `kv_cache_dtype fp8_e4m3` 추가. 재생성 뒤 양쪽 yaml md5 일치. 운영 조건과의 차이는 판정표에 기록
  - 19:50 추가: `gemma26b` 변형은 0.9에서 KV 7.24 GiB(65536에 7.7 GiB 필요)로 실패(`smoke-old-gemma26b.try2-kv-insufficient-0.9.log`) → `gpu_memory_utilization 0.92`만 재정의. 양쪽 md5 일치
- **GPU 2 외부 선점 (17:57~18:08, 3회)**: 가중치 fp8 변환 중 메모리를 잠깐 놓는 순간 다른 컨테이너의 프로세스가 23GB(46GB의 절반, `gpu_memory_utilization 0.5`에 해당)를 가져가 OOM. 연구계·시험장 안에는 해당 프로세스 없음(`/proc/*/fd`의 `/dev/nvidia*` 전수 확인, MPS는 GPU 3 전용). 대표님이 호스트에서 자동 재시작 서비스를 정리(18:1x). 이후 재발 없음
- **베이스 다이제스트 (Docker Hub, 10-08 조회)**: `vllm/vllm-openai:v0.31.0@sha256:c1c9f6fd5c109ba7f0546a59f5b2f15fb87f64c77782e90a27b648b42a8e67c3` (amd64 압축 9.0GB)

## 검증
- 예행 환경에서 `vllm --version`이 0.31.0, 제약 생성이 누락 없이 끝나고 `pip check` 통과 (실패하면 충돌 기록이 남아 있음)
- 설정 해석 9/9 통과, `async_scheduling` 최종값이 False (런처 주입 포함 경로)
- `python`, `python3`, `pip`, `vllm`이 같은 Python 3.12 환경을 가리키고, 사용자 site와 겹치는 패키지 목록이 기록됨
- 연구계 :5015 서빙이 영향을 받지 않음 (`./start.sh status`)

## 완료 기준
- [x] 결정 ②에 답변을 받음 (10-08 착수 지시: 정식 릴리스 0.31.0)
- [x] 기준선·되돌리기 묶음·예행 설치 기록·시험 설정 묶음 저장 (`~/vllm-upgrade/`)
- [x] 위 검증 통과 (실행 기록 참조)
- [x] master Phase 맵에서 part1 상태 갱신 (10-09)
