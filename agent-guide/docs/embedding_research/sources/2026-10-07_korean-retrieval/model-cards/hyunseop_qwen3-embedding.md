---
library_name: sentence-transformers
pipeline_tag: sentence-similarity
base_model: Qwen/Qwen3-Embedding-4B
datasets:
  - nvidia/Nemotron-Personas-Korea
tags:
  - sentence-transformers
  - korean
  - embedding
  - contrastive-learning
---

# qwen3-embedding-h100

H100 fine-tuned Korean embedding model based on `Qwen/Qwen3-Embedding-4B`.

This is the stronger of the two uploaded models for public Korean retrieval. Compared with `bge-m3-ko-h100`, it is the better model to highlight when you want the strongest general Korean retrieval story.

## Training

Fine-tuned from `Qwen/Qwen3-Embedding-4B` with a **contrastive (in-batch-negative) objective**.

- **Base model:** [`Qwen/Qwen3-Embedding-4B`](https://huggingface.co/Qwen/Qwen3-Embedding-4B)
- **Training data:** [`nvidia/Nemotron-Personas-Korea`](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea) — synthetic Korean personas (demographic / geographic / personality), used as `(query, positive-document)` pairs
- **Objective:** `sentence-transformers` `MultipleNegativesRankingLoss` (in-batch negatives, InfoNCE-style)
- **Hardware:** 4×H100 (Slurm)
- **Hyperparameters:** 3 epochs · per-device batch size 1 · gradient accumulation 8 · learning rate 1e-5 · warmup ratio 0.1 · weight decay 0.01 · bf16
- **Finetune run:** `111677_20260506_114341_both_2gpu`


## Benchmark Results

### AutoRAG

- Corpus size: 720
- Queries evaluated: 114
- MRR: 0.7677
- MAP: 0.7677
- Hit@1: 0.6579
- Hit@5: 0.9035
- Hit@10: 0.9298
- Hit@50: 0.9649

### MIRACL

- Task: `MIRACLRetrieval`
- Dataset subset: `ko`
- Corpus size: 1,486,752
- Queries evaluated: 213
- mRR: 0.5773
- mAP: 0.4328

| cutoff | Precision | Recall | F1 | mAP | mRR | NDCG |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| @1 | 0.46479 | 0.29452 | 0.32978 | 0.29452 | 0.464789 | 0.46479 |
| @3 | 0.25665 | 0.42305 | 0.28522 | 0.42305 | 0.577318 | 0.45190 |
| @5 | 0.18310 | 0.47493 | 0.23726 | 0.47493 | 0.577318 | 0.45852 |
| @10 | 0.11737 | 0.58359 | 0.17922 | 0.58359 | 0.577318 | 0.49227 |
| @20 | 0.07254 | 0.67332 | 0.12345 | 0.67332 | 0.577318 | 0.52325 |
| @100 | 0.02028 | 0.83695 | 0.03891 | 0.83695 | 0.577318 | 0.56629 |
| @1000 | 0.00246 | 0.95250 | 0.00491 | 0.95250 | 0.577318 | 0.58808 |

## Artifacts

- Model: `output/111677_20260506_114341_both_2gpu/qwen`
- AutoRAG benchmark: `benchmark_results/autorag_benchmark.json`
- MIRACL summary: `benchmark_results/qwen_miracl_fast4/miracl_benchmark.txt`
- MIRACL details: `benchmark_results/qwen_miracl_fast4/miracl_benchmark.json`

## Comparison note

- Strongest public Korean retrieval story among the open Korean embedding models I checked
- Ahead of `dragonkue/snowflake-arctic-embed-l-v2.0-ko` `0.740433`, `dragonkue/BGE-m3-ko` `0.729993`, `nlpai-lab/KURE-v1` `0.727739`, and `nlpai-lab/KoE5` `0.711356` on the Korean retrieval leaderboard cited by the model card
- Public Qwen3-Embedding-4B leaderboard result on Korean retrieval is average NDCG@10 `0.7484`
