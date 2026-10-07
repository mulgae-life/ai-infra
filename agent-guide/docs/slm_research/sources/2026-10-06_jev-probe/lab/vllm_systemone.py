"""simple-jev 프롬프트 컴파일러 + vLLM AsyncLLM 백엔드로 SystemOne 호환 서버를 띄운다.

simple-jev hf-server의 DecisionService·PromptCompiler·응답 조립은 그대로 쓰고,
모델 forward(HFBackend)만 vLLM으로 바꾼다. 라벨 점수는 SamplingParams.logprob_token_ids로
지정 토큰의 로그 확률만 받는다. 로그 확률은 로짓에서 상수(logsumexp)를 뺀 값이라
라벨끼리 softmax한 결과는 로짓으로 계산한 것과 같다.

엔드포인트: POST /v1/classifier, POST /v1/systemone (simple-jev와 동일)
"""
import argparse
import asyncio
import logging
import os
import sys
import time
import uuid

SIMPLE_JEV = os.environ.get("SIMPLE_JEV_DIR", "/workspace/tmp/jev-lab/repos/simple-jev")
sys.path.insert(0, SIMPLE_JEV)
sys.path.insert(0, os.path.join(SIMPLE_JEV, "hf-server"))

import torch  # noqa: E402
import uvicorn  # noqa: E402
from transformers import AutoConfig, AutoTokenizer  # noqa: E402

from hf_prompt_policies import resolve_prompt_policy  # noqa: E402
from hf_server import BackendResult, DecisionService, PromptCompiler, create_app  # noqa: E402

from vllm import SamplingParams  # noqa: E402
from vllm.engine.arg_utils import AsyncEngineArgs  # noqa: E402
from vllm.inputs import TokensPrompt  # noqa: E402
from vllm.sampling_params import MAX_LOGPROB_TOKEN_IDS  # noqa: E402
from vllm.v1.engine.async_llm import AsyncLLM  # noqa: E402

log = logging.getLogger("vllm_systemone")


class VLLMBackend:
    """HFBackend와 같은 계약: score(compiled) -> BackendResult(라벨 점수 텐서, 지표)."""

    def __init__(self, engine: AsyncLLM):
        self.engine = engine

    async def _label_logprobs(self, token_ids: list[int], label_ids: list[int]) -> list[float]:
        params = SamplingParams(
            max_tokens=1,
            temperature=0.0,
            logprob_token_ids=list(label_ids),
            detokenize=False,
        )
        final = None
        async for out in self.engine.generate(
            TokensPrompt(prompt_token_ids=token_ids), params, uuid.uuid4().hex
        ):
            final = out
        if final is None or not final.outputs or not final.outputs[0].logprobs:
            raise RuntimeError("vLLM이 로그 확률을 돌려주지 않았다")
        table = final.outputs[0].logprobs[0]
        missing = [t for t in label_ids if t not in table]
        if missing:
            raise RuntimeError(f"라벨 토큰 로그 확률 누락: {missing[:5]}")
        return [table[t].logprob for t in label_ids]

    async def _branch(self, branch) -> list[float]:
        ids = branch.output_ids
        # logprob_token_ids는 요청당 128개가 상한이다. 넘으면 나눠 보내고 합친다.
        # 같은 프롬프트라 접두사 캐시를 그대로 재사용한다.
        chunks = [ids[i : i + MAX_LOGPROB_TOKEN_IDS] for i in range(0, len(ids), MAX_LOGPROB_TOKEN_IDS)]
        parts = await asyncio.gather(*(self._label_logprobs(branch.token_ids, c) for c in chunks))
        return [v for part in parts for v in part]

    async def score(self, compiled):
        start = time.perf_counter()
        branches = compiled.branches
        if any(b.model_inputs is not None for b in branches):
            raise ValueError("이 백엔드는 텍스트 전용이다")
        values = await asyncio.gather(*(self._branch(b) for b in branches))
        logits = {
            b.branch_id: torch.tensor(v, dtype=torch.float32) for b, v in zip(branches, values)
        }
        return BackendResult(
            logits,
            {
                "backend": "vllm-asyncllm",
                "engine_requests": sum(
                    -(-len(b.output_ids) // MAX_LOGPROB_TOKEN_IDS) for b in branches
                ),
                "branch_prompt_tokens": sum(len(b.token_ids) for b in branches),
                "branch_output_tokens": 0,
                "scored_positions": len(branches),
                "backend_seconds": time.perf_counter() - start,
            },
        )


async def serve(args):
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    config = AutoConfig.from_pretrained(args.model)
    policy, selection = resolve_prompt_policy(config, args.prompt_policy)
    log.warning("prompt policy: %s (%s)", policy, selection)
    compiler = PromptCompiler(
        tokenizer,
        max_tokens=args.max_model_len,
        prompt_policy=policy,
        max_choice_options=255,
    )
    compiler.validate_choice_capacity()

    engine_args = AsyncEngineArgs(
        model=args.model,
        served_model_name=[args.served_model_name],
        max_model_len=args.max_model_len,
        gpu_memory_utilization=args.gpu_memory_utilization,
        enable_prefix_caching=True,
        max_num_seqs=args.max_num_seqs,
        max_num_batched_tokens=args.max_num_batched_tokens,
        max_logprobs=256,
        language_model_only=True,
        seed=42,
    )
    engine = AsyncLLM.from_engine_args(engine_args)
    service = DecisionService(
        args.served_model_name,
        compiler,
        VLLMBackend(engine),
        metadata={"backend": "vllm-asyncllm", "prompt_policy": policy, "model_path": args.model},
        concurrency=args.concurrency,
        queue_size=args.queue_size,
        max_request_branches=256,
        max_choice_options=255,
        advanced_metrics=True,
    )
    app = create_app(service)
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=args.port, log_level="warning"))
    try:
        await server.serve()
    finally:
        engine.shutdown()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="/models/LLM/Qwen/Qwen3.8-27B-FP8")
    ap.add_argument("--served-model-name", default="qwen3.8-27b-fp8-vllm")
    ap.add_argument("--prompt-policy", default=None)
    ap.add_argument("--port", type=int, default=8179)
    ap.add_argument("--max-model-len", type=int, default=32768)
    ap.add_argument("--gpu-memory-utilization", type=float, default=0.88)
    ap.add_argument("--max-num-seqs", type=int, default=128)
    ap.add_argument("--max-num-batched-tokens", type=int, default=16384)
    ap.add_argument("--concurrency", type=int, default=64)
    ap.add_argument("--queue-size", type=int, default=512)
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve(args))


if __name__ == "__main__":
    main()
