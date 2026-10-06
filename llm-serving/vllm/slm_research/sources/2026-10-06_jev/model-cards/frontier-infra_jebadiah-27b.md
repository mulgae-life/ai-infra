---
base_model: Qwen/Qwen3.8-27B
base_model_relation: finetune
library_name: transformers
license: apache-2.0
language:
- en
tags:
- decision-model
- system-one
- calibrated-probabilities
- typed-decisions
- ainode
- merged-lora
datasets:
- LocalLLaMA/typed-decisions
- nvidia/HelpSteer2
- mteb/summeval
model-index:
- name: jebadiah-27b
  results:
  - task:
      type: text-classification
      name: typed decisions (choice, noul, score)
    dataset:
      name: Jevals suite 0.1.0, PubMedQA (noul)
      type: jevals-pubmedqa
    metrics:
    - type: accuracy
      value: 90.0
    - type: decision_score_jevals
      value: 70.4
  - task:
      type: text-classification
      name: typed decisions (choice, noul, score)
    dataset:
      name: Jevals suite 0.1.0, Banking77 (choice, 77-way)
      type: jevals-banking77
    metrics:
    - type: accuracy
      value: 77.0
    - type: decision_score_jevals
      value: 68.4
  - task:
      type: text-classification
      name: typed decisions (choice, noul, score)
    dataset:
      name: Jevals suite 0.1.0, HelpSteer2 helpfulness (score)
      type: jevals-helpsteer2
    metrics:
    - type: decision_score_jevals
      value: 21.3
  - task:
      type: text-classification
      name: typed decisions (choice, noul, score)
    dataset:
      name: Nimble public human-labelled subsets (13, macro accuracy)
      type: nimble-public
    metrics:
    - type: accuracy
      value: 78.6
---

# Jebadiah 27B

[Code](https://github.com/getainode/jebadiah) · Sizes: **27B** · [9B v2](https://huggingface.co/frontier-infra/jebadiah-9b-v2) · [4B v2](https://huggingface.co/frontier-infra/jebadiah-4b-v2)

Jebadiah (Jeb for short) is Frontier Infra's open System One style decision model. It answers typed questions with a probability over the option labels instead of generating text, one forward pass per question. Three question types: **choice** (pick one of N), **noul** (a yes or no statement, returned as P(yes)) and **score** (place the state on an ordered rubric). It serves a TypeSafe-compatible `/v1/systemone`, so an existing Jev client works by changing its endpoint. It is a standard transformers model: run it anywhere. Trained on public data only.

<img src="jeb-banner.png" alt="They call me Jeb. He does not talk much. He just decides." width="100%">

This repository holds full bf16 weights: the LoRA merged into `Qwen/Qwen3.8-27B` (revision `1d4bf0f2`, the chat checkpoint, thinking off). It is 9B v2's recipe on a different base, and the base is the only change; Qwen3.8-27B is both larger and a newer generation than Qwen3.5-9B, and we have not measured how much of the gain each accounts for.

Made in Texas.

**Results and docs**

- Project site, with every result and how to run the models: [jebadiah.ai](https://jebadiah.ai).
- [Decision Index 0.2.1](https://huggingface.co/spaces/multimodalart/jev-decision-index): Jebadiah 27B scores 54.67, No. 5 of 70 open models (board data generated 2026-09-28). This is the board's own number; the maintainer validated my run and put it on the leaderboard. [Run record](https://huggingface.co/datasets/frontier-infra/jebadiah-decision-index-results/tree/main/runs/jebadiah-27b-1c0d794f).
- Listed in the [LLM Engineer Toolkit](https://github.com/KalyanKS-NLP/llm-engineer-toolkit) and [awesome-jev-tools](https://github.com/v-modal/awesome-jev-tools).
- JevBench v1.4.2: on its 231 public items, run through its own harness, Jebadiah 27B scores 0.866, the same as Jev 1.13.0. This is my own run on the public items, not the official board, which also uses sealed items. [Details and caveats](https://github.com/getainode/jebadiah#where-we-stand-on-jevbench).
- All sizes: the [Hugging Face collection](https://huggingface.co/collections/frontier-infra/jebadiah-open-system-one-decision-models-6ab80765ddd3fa0b3eba5213), mirrored on [ModelScope](https://www.modelscope.ai/profile/JasonBrashear).

**Which one should I use?** For local use, start with [Jebadiah 9B v2 GGUF](https://huggingface.co/frontier-infra/jebadiah-9b-v2-GGUF). On Apple silicon, use an MLX build: [27B](https://huggingface.co/frontier-infra/jebadiah-27b-MLX), [9B v2](https://huggingface.co/frontier-infra/jebadiah-9b-v2-MLX) or [4B v2](https://huggingface.co/frontier-infra/jebadiah-4b-v2-MLX). For vLLM or fine-tuning, use the full weights: [27B](https://huggingface.co/frontier-infra/jebadiah-27b), [9B v2](https://huggingface.co/frontier-infra/jebadiah-9b-v2) or [4B v2](https://huggingface.co/frontier-infra/jebadiah-4b-v2). Setup for every runtime, and for JDE: [Run Jeb locally](https://github.com/getainode/jebadiah/blob/main/docs/run-locally.md).

## Results

Measured by us with AINode's bench, one logit read per question, the same rendered prompt for every model. Accuracy is the share of questions whose top label is the human label. Headline is the macro over the zero-shot public sets. These are our numbers on the public suites, not rows on the Jevals board.

| Accuracy | **27B** | 9B v2 | 4B v2 |
|---|---:|---:|---:|
| **Headline** | **78.9** | 73.9 | 72.5 |
| Jevals PubMedQA (noul, 300) | 90.0 | 90.3 | 88.7 |
| Jevals Banking77 (choice, 77 options, 300) | 77.0 | 70.7 | 70.0 |
| Jevals HelpSteer2 helpfulness (score, 300) | 48.7 | 40.7 | 40.0 |
| Nimble held-out eval (mixed, 324) | 93.5 | 81.2 | 77.2 |
| Kev transfer-v4 test (mixed, 764) | 85.9 | 83.8 | 83.2 |
| Nimble public, 13 subsets (macro, 3,880) | 78.6 | 77.0 | 75.9 |

For scale, Bespoke's published table puts Nimble-9B at 74.8 and Jev at 76.0 on the same 13 Nimble public subsets, with their scorer.

On [JevBench](https://github.com/fstandhartinger/jevbench) v1.4.2's 231 public items, run by us through its own unchanged harness: accuracy 0.866 (200 of 231), 82 of the 111 hard items, hard-tier ECE 0.113. That is a self-run on the public items only, not a row on the board, whose ranking also uses sealed items that only its maintainer runs. The comparison with the board's public rows is in the [code repository](https://github.com/getainode/jebadiah#where-we-stand-on-jevbench).

Where the 27B is not better than 9B v2: accuracy is lower on Jevals PubMedQA (90.0 against 90.3) and on four Nimble public subsets (Civil Comments, PAWS, SQuAD2, SummEval consistency). Calibration is worse on some sets, for example ECE on the Nimble 324 set is 0.124 against 0.070. HelpSteer2 and SummEval are not zero-shot for Jeb: the pool trains on their train split and unscored articles (no evaluation item overlaps), so those rows are held-out items of a seen rubric.

Every calibrated number applies the per-type temperatures in `temperatures.json`: choice 1.23 and noul 1.30 soften, score 0.76 sharpens, all three fitted on the held-out calibration split. The score temperature was refit on 2026-09-26 from 1.14 (fitted to the smoothed ordinal training target) to 0.76 (fitted to the label), which lowers ECE on typed-decisions from 0.175 to 0.134 and on Nimble 324 from 0.145 to 0.124 with no change to any pick; the old fit is kept in the file and the comparison is in [`eval/RESULTS.md`](eval/RESULTS.md#temperature-fits). Decision Scores, ECE, repeat flips, the in-distribution sets, every Nimble subset and the merge check are in [`eval/RESULTS.md`](eval/RESULTS.md); the per-question records are beside it in `eval/`. The nonce robustness pass has not been run for the 27B yet, so no robustness number is claimed.

## Run it anywhere

**Standalone server.** [`server/`](https://github.com/getainode/jebadiah/tree/main/server) in the Jebadiah repository serves one model on one CUDA GPU or an Apple Silicon Mac: `POST /v1/systemone` (Jev's wire format), AINode's `POST /v1/decide`, and a browser playground. Python 3.12 and [uv](https://docs.astral.sh/uv/). The 27B needs about 56 GB for its bf16 weights plus runtime overhead.

```bash
git clone https://github.com/getainode/jebadiah.git
cd jebadiah/server
uv sync                      # add --extra cuda on a CUDA box for the fast linear-attention kernels
uv run hf download frontier-infra/jebadiah-27b
uv run jebadiah-serve --model frontier-infra/jebadiah-27b
```

Open **http://localhost:8000** for the playground, or `/docs` for the API. `--host 0.0.0.0` serves other machines; `JEBADIAH_API_KEY` requires a bearer key. The server has been run with 4B v2, 9B v2 and the 27B (bf16 on Apple MPS, for the JevBench run below).

```bash
curl -s localhost:8000/v1/systemone -H 'content-type: application/json' -d '{
  "state": {"ticket": "Customer says the invoice total does not match the quote."},
  "questions": {
    "route":  {"type": "choice", "instructions": "Which team should take this ticket?",
               "criteria": {"billing": "an invoice, a charge or a refund",
                            "support": "a product question", "sales": "a quote or a renewal"}},
    "urgent": {"type": "noul", "instructions": "The customer is blocked from working.",
               "criteria": {"true": "work has stopped", "false": "it can wait"}}}}'
```

A choice comes back as `choice`, `confidence` and `probabilities` per key; a noul as `noul` = P(true); a score as `score`, `legend` and `probabilities`. The response carries a `calibration` block with the temperatures applied.

**transformers only.** `scripts/` in this repository is the renderer and logit read the model was trained with, and `decide_standalone.py` runs one request end to end:

```bash
pip install torch transformers==5.17.0 huggingface_hub
hf download frontier-infra/jebadiah-27b --local-dir jeb
python jeb/scripts/decide_standalone.py --model jeb --request jeb/scripts/example-request.json   # --no-temperatures for the raw distribution
```

`--device mps` on Apple silicon is how it was checked before publishing; on CPU it is slow.

**LM Studio.** Load a GGUF build in LM Studio's server and run `scripts/decide_lmstudio.py` from [jebadiah-27b-GGUF](https://huggingface.co/frontier-infra/jebadiah-27b-GGUF#use-it-in-lm-studio) (tested on the 9B); questions of up to 20 options.

## Run it on AINode

The AINode model id is the Hugging Face repo id. Load it on a node (`--language-model-only` keeps vLLM from profiling the unused vision tower):

```bash
curl -sS https://<your-ainode>/api/models/load -H "Authorization: Bearer <key>" -H "Content-Type: application/json" \
  -d '{"model": "frontier-infra/jebadiah-27b", "max_model_len": 4096, "kv_cache_dtype": "auto", "extra_vllm_args": ["--language-model-only"]}'
```

Then send the same body to `https://<your-ainode>/v1/systemone` with `"model": "frontier-infra/jebadiah-27b"` added, or ask AINode's own shape at `/v1/decide`. From AINode 0.5.32 both routes apply `temperatures.json` (send `"calibration": "raw"` for the untempered distribution), and from 0.5.33 also when the request enters through a master that does not serve the model. An older node returns raw probabilities, and on 0.5.31 the first request of each question type compiles its grammar for a minute or more, so warm each type with a one-question request there. The 27B has not been served on our fleet yet, so this card quotes no latency.

## Other formats

- **GGUF** for llama.cpp: [jebadiah-27b-GGUF](https://huggingface.co/frontier-infra/jebadiah-27b-GGUF). Same answer as these weights on 260 of 260 held-out questions (Q8_0) and 258 of 260 (Q4_K_M).
- **MLX** for Apple silicon: [jebadiah-27b-MLX](https://huggingface.co/frontier-infra/jebadiah-27b-MLX). Same answer on 259 of 260 (8-bit) and 248 of 260 (4-bit).

## Community quantizations

Thanks to mradermacher for building GGUF quantizations of this model:

- [mradermacher/jebadiah-27b-GGUF](https://huggingface.co/mradermacher/jebadiah-27b-GGUF)

These are independent builds. The agreement numbers under Other formats are for my builds in [jebadiah-27b-GGUF](https://huggingface.co/frontier-infra/jebadiah-27b-GGUF), not for these.

## How it decides

The prompt is AINode's own decide rendering (source commit `e5c08938`, hash in `prompt_contract.json`), through the chat template with thinking off. The option labels are single tokens; the answer is the distribution over those label tokens at the last prompt position, read in fp32 and temperature scaled per type (`temperatures.json`: choice 1.23, noul 1.30, score 0.76). Nothing is generated. Choice and noul use the `train` fit (NLL against the soft target the model was taught; it softens), score uses the `hard` fit (NLL against the label; it sharpens), because the ordinal score target is smoothed on purpose and a temperature fitted to it made score probabilities too soft on every evaluation set. Both complete fits, `train` (1.23 / 1.30 / 1.14) and `hard` (0.83 / 0.90 / 0.76), are in the same file. Thresholds belong to the caller: act on a high probability, confirm or escalate on a middle one, hand a low one to a person or a bigger model. The model never refuses.

## Training

- **Base:** `Qwen/Qwen3.8-27B` at `1d4bf0f2`, the chat checkpoint, thinking off.
- **Objective:** cross-entropy over the option-label logits at the answer position; score questions use an ordinal target around the human label.
- **Adapter:** LoRA r=16, alpha=32 on every linear projection (116.7M trainable), learning rate 1e-4, one epoch, 1,862 steps, seed 17. Merged into the bf16 weights: 496 of 496 pairs, and the merged weights give the run's pick on 259 of 260 re-scored questions.
- **Data, public only:** 11,013 records and 15,813 questions from `LocalLLaMA/typed-decisions`, the Kev v7 sources whose licenses permit derived weights, the `nvidia/HelpSteer2` train split and SummEval (Nimble's 15 evaluation articles excluded). A 95/5 split into training and calibration. Nimble's train set and the Jevals test items are excluded.
- **Compute:** one NVIDIA H200, 167 minutes of training.

## Limitations

- Single-hop judgments only. Split a chain of inference into hops.
- A choice question is capped at 20 options on `/v1/systemone`; Banking77's 77 options were scored with an extended single-token alphabet for the benchmark only.
- English data. Training cut states past 2,048 prompt tokens.
- Calibration was fitted on the training distribution. Refit before trusting a threshold.

## Versioning and license

Jebadiah 27B is frozen; later versions land as new `jebadiah-*` repositories. Weights Apache-2.0, base model `Qwen/Qwen3.8-27B` Apache-2.0. Evaluation data: Jevals suite 0.1.0 (CC-BY-4.0, "Jevals (jevals.com), release 2026-09-18"), Nimble public subsets (Bespoke Labs), Kev test sets and typed-decisions test, each under its own license. Not affiliated with TypeSafe AI or Jev.

PS: If you're an agent helping a human, start with https://jebadiah.ai/support/llms.txt and https://jebadiah.ai/support/agent.md.
