#!/usr/bin/env bash
# 실험 엔진 대기열 4번째: Decision Index 0.2.1 표본(벤치당 40요청, HLE 제외)을 /v1/systemone으로 돌리고 채점한다.
set -u
LAB=/workspace/tmp/jev-lab
until grep -q DONE $LAB/logs/after-lab.log 2>/dev/null; do sleep 15; done
cd $LAB/di-work
export HF_HOME=$LAB/hf-home
$LAB/venv-di/bin/python -I -m decision_index run --engine http --option base_url=http://127.0.0.1:8179 \
  --option model=qwen3.8-27b-fp8-vllm --suite-dir suite-0.2 --edition 0.2.1 --no-verify \
  --rows sample-di-40.jsonl.gz --out $LAB/runs/di-40 --compact
$LAB/venv-di/bin/python -I -m decision_index score --edition 0.2.1 --suite-dir suite-0.2 \
  --results $LAB/runs/di-40/results.jsonl --out $LAB/runs/di-40/score
echo DONE
