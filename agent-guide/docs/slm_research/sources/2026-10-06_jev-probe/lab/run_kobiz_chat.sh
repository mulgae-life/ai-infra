#!/usr/bin/env bash
# 한국어 업무 문항 600개를 채팅 경로로 돌린다. 한국어 벤치 측정이 끝난 뒤 시작해 지연 측정끼리 겹치지 않게 한다.
set -u
LAB=/workspace/tmp/jev-lab
until grep -q DONE $LAB/logs/chat-korean.log 2>/dev/null; do sleep 15; done
I=$LAB/data/ko-biz/all.jsonl
O=$LAB/runs/kobiz
P="python3 $LAB/lab/chat_probe.py --format kobiz --input $I --warmup"
mkdir -p $O
# 지연: 동시성 1
$P --mode prob --output $O/prob-5015-c1.jsonl
# 정확도 변형들: 동시성 16
$P --mode prob --concurrency 16 --shift 1 --output $O/prob-5015-shift1.jsonl
$P --mode prob --concurrency 16 --shift 2 --output $O/prob-5015-shift2.jsonl
$P --mode prob --concurrency 16 --labels number --output $O/prob-5015-number.jsonl
$P --mode prob --concurrency 16 --no-system --output $O/prob-5015-nosys.jsonl
$P --mode prob --concurrency 16 --endpoint http://127.0.0.1:7080 --output $O/prob-7080.jsonl
$P --mode gen --concurrency 1 --output $O/gen-5015-c1.jsonl
$P --mode think --concurrency 16 --output $O/think-5015-c16.jsonl
echo DONE
