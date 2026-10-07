#!/usr/bin/env bash
# 큰 판단 벤치를 무작위 표본(시드 13)으로 줄여 실험 엔진에서 돌린다. 스위트마다 따로 실행한다(--input 덮어쓰기는 스위트 하나에만 적용된다).
set -u
cd /workspace/tmp/jev-lab/repos/simple-jev
for s in security-code metatool-awareness legal-unfair-tos legal-contractnli phishing-verdict legal-casehold codecomplex-test codemmlu-full; do
  python3 eval/run.py --endpoint http://127.0.0.1:8179/v1/classifier --model qwen3.8-27b-fp8-vllm \
    --suite eval/suites/english/$s.json --input /workspace/tmp/jev-lab/data/suite-samples/$s.jsonl \
    --workers 32 --delay 0 --timeout 900 --retries 2 --output /workspace/tmp/jev-lab/runs/decision-sample/$s > /workspace/tmp/jev-lab/logs/decision-sample-$s.log 2>&1
  echo "$s exit $?"
done
echo DONE
