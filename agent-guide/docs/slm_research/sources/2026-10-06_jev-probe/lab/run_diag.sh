#!/usr/bin/env bash
# 채팅 경로 대기열: :7080 앞단 병목 진단, 그다음 :5015 질문 묶음(문서 캐시 선적재) 지연.
set -u
LAB=/workspace/tmp/jev-lab
mkdir -p $LAB/runs/speed
python3 $LAB/lab/diag_frontend.py $LAB/runs/speed/diag-frontend-7080.json
python3 $LAB/lab/bundle_probe.py --mode chat --warm-first --endpoint http://127.0.0.1:5015 --model gemma-4 --output $LAB/runs/speed/bundle-5015-warmfirst.json
echo DONE
