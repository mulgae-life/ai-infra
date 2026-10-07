#!/usr/bin/env bash
# :5015 대기열 3번째: 업무 문항 실험이 끝나면 입력 길이별 지연, 질문 묶음 지연을 잰다.
set -u
LAB=/workspace/tmp/jev-lab
until grep -q DONE $LAB/logs/kobiz-chat.log 2>/dev/null; do sleep 15; done
mkdir -p $LAB/runs/speed
python3 $LAB/lab/length_sweep.py --output $LAB/runs/speed/length-5015.json
python3 $LAB/lab/bundle_probe.py --mode chat --endpoint http://127.0.0.1:5015 --model gemma-4 --output $LAB/runs/speed/bundle-5015.json
echo DONE
