#!/usr/bin/env bash
# 한국어 공개 벤치(jev-korean-benchmark)를 채팅 경로로 돌려 정확도·지연을 잰다.
# 지연 측정이 서로 간섭하지 않게 순서대로 실행한다.
set -u
LAB=/workspace/tmp/jev-lab
D=$LAB/repos/simple-jev/eval/data
O=$LAB/runs/chat
P="python3 $LAB/lab/chat_probe.py --format simplejev --warmup"
mkdir -p "$O"

# 1) 확률 읽기, 게이트웨이(:5015), 동시성 1 — 세 조건
for c in ko-ko ko-en en-en; do
  $P --input $D/korean-public-$c.jsonl --mode prob --output $O/kpub-$c-prob-5015-c1.jsonl
done
# 2) 같은 요청을 vLLM 직접(:7080)으로 — 게이트웨이 비용과 안내문 영향 분리
$P --input $D/korean-public-ko-ko.jsonl --mode prob --endpoint http://127.0.0.1:7080 --output $O/kpub-ko-ko-prob-7080-c1.jsonl
# 3) 답 생성(사고 끔), 동시성 1
$P --input $D/korean-public-ko-ko.jsonl --mode gen --output $O/kpub-ko-ko-gen-5015-c1.jsonl
# 4) 확률 읽기 동시성 변화
for c in 4 8 16 20 32; do
  $P --input $D/korean-public-ko-ko.jsonl --mode prob --concurrency $c --output $O/kpub-ko-ko-prob-5015-c$c.jsonl
done
# 5) 사고 켬: 단건 지연(앞 30문항, 동시성 1)과 전체 정확도(동시성 16)
$P --input $D/korean-public-ko-ko.jsonl --mode think --limit 30 --output $O/kpub-ko-ko-think-5015-c1.jsonl
$P --input $D/korean-public-ko-ko.jsonl --mode think --concurrency 16 --output $O/kpub-ko-ko-think-5015-c16.jsonl
echo DONE
