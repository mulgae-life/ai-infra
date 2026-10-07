#!/usr/bin/env bash
# 실험 엔진 대기열 3번째: 표본 판단 벤치(두 묶음)가 끝나면 업무 문항(정확도·지연), 질문 묶음 지연, 한국어 벤치 단건 지연을 잰다.
set -u
LAB=/workspace/tmp/jev-lab
until grep -q DONE2 $LAB/logs/decision-sample2.log 2>/dev/null; do sleep 15; done
mkdir -p $LAB/runs/kobiz $LAB/runs/speed
python3 $LAB/lab/systemone_probe.py --input $LAB/data/ko-biz/all.jsonl --concurrency 16 --warmup --output $LAB/runs/kobiz/systemone-lab.jsonl
python3 $LAB/lab/systemone_probe.py --input $LAB/data/ko-biz/all.jsonl --concurrency 1 --warmup --output $LAB/runs/kobiz/systemone-lab-c1.jsonl
python3 $LAB/lab/bundle_probe.py --mode systemone --endpoint http://127.0.0.1:8179 --model qwen3.8-27b-fp8-vllm --output $LAB/runs/speed/bundle-lab.json
cd $LAB/repos/simple-jev && python3 eval/run.py --endpoint http://127.0.0.1:8179/v1/classifier --model qwen3.8-27b-fp8-vllm \
  --suite eval/suites/non-english/korean-public-ko-ko.json --workers 1 --delay 0 --timeout 300 --output $LAB/runs/korean-public-c1 > $LAB/logs/korean-public-c1.log 2>&1
echo DONE
