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
  - 인스턴스 사본: GPU 0·1 고정(STT 3종 포함, 원래 STT는 GPU 2), Qwen3.8은 MTP 끔·켬 두 벌
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

## 검증
- 예행 환경에서 `vllm --version`이 0.31.0, 제약 생성이 누락 없이 끝나고 `pip check` 통과 (실패하면 충돌 기록이 남아 있음)
- 설정 해석 9/9 통과, `async_scheduling` 최종값이 False (런처 주입 포함 경로)
- `python`, `python3`, `pip`, `vllm`이 같은 Python 3.12 환경을 가리키고, 사용자 site와 겹치는 패키지 목록이 기록됨
- 연구계 :5015 서빙이 영향을 받지 않음 (`./start.sh status`)

## 완료 기준
- [ ] 결정 ②에 답변을 받음
- [ ] 기준선·되돌리기 묶음·예행 설치 기록·시험 설정 묶음 저장 (`~/vllm-upgrade/`)
- [ ] 위 검증 통과
- [ ] master Phase 맵에서 part1 상태 갱신
