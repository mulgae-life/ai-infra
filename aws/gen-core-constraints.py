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
