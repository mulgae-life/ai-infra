#!/usr/bin/env bash
# 행 수를 선언한 두 벤치(MetaTool, CodeMMLU)를 표본용 매니페스트로 다시 돌린다. 첫 표본 묶음이 끝난 뒤 시작한다.
set -u
LAB=/workspace/tmp/jev-lab
until grep -q DONE $LAB/logs/decision-sample.log 2>/dev/null; do sleep 15; done
cd $LAB/repos/simple-jev
for s in metatool-awareness codemmlu-full; do
  python3 eval/run.py --endpoint http://127.0.0.1:8179/v1/classifier --model qwen3.8-27b-fp8-vllm \
    --suite $LAB/data/suite-samples/manifests/$s.json \
    --workers 32 --delay 0 --timeout 900 --retries 2 --output $LAB/runs/decision-sample/$s > $LAB/logs/decision-sample2-$s.log 2>&1
  echo "$s exit $?"
done
echo DONE2
