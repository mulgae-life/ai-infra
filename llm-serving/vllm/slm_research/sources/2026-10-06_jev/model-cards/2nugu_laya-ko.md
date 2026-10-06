---
license: apache-2.0
base_model: convaiinnovations/laya
language:
- ko
- en
- ja
library_name: transformers
pipeline_tag: text-classification
tags:
- laya
- decision-model
- system-one
- calibrated-decisions
- korean
- klue
- classification
- routing
- onnx
metrics:
- accuracy
model-index:
- name: laya-ko
  results:
  - task:
      type: text-classification
      name: Topic classification (KLUE-YNAT)
    dataset:
      name: KLUE YNAT (validation)
      type: klue
      config: ynat
      split: validation
    metrics:
    - type: accuracy
      value: 0.834
      name: Accuracy
    - type: ece
      value: 0.077
      name: Expected calibration error
  - task:
      type: text-classification
      name: Relation extraction (KLUE-RE)
    dataset:
      name: KLUE RE (validation)
      type: klue
      config: re
      split: validation
    metrics:
    - type: accuracy
      value: 0.705
      name: Accuracy
  - task:
      type: text-classification
      name: Natural language inference (KLUE-NLI)
    dataset:
      name: KLUE NLI (validation)
      type: klue
      config: nli
      split: validation
    metrics:
    - type: accuracy
      value: 0.815
      name: Accuracy
  - task:
      type: text-classification
      name: Semantic textual similarity, binned to 6 ordinal levels (KLUE-STS)
    dataset:
      name: KLUE STS (validation)
      type: klue
      config: sts
      split: validation
    metrics:
    - type: accuracy
      value: 0.509
      name: Accuracy
---

# laya-ko

Korean fine-tune of [Laya](https://huggingface.co/convaiinnovations/laya). Same
architecture, same 322 M parameters, same single forward pass — it just answers Korean
typed decisions far better.

**Code, benchmarks and the Rust/ONNX client:** https://github.com/\<your-github\>/laya-ko

> 라야(Laya)가 한국어를 잘 못하길래 튜닝해 보았습니다. 한국어 이용자분들 파이팅!

## This is not a generative model

Laya is a bidirectional encoder (mmBERT-base) with a decision head. Each option in a
question gets a `[MASK]` marker; the head scores those markers and softmaxes **over that
question's options only**. No tokens are generated. You hand it text plus a typed
question and get back a calibrated probability distribution over options you defined at
call time.

| type | you give | you get |
|---|---|---|
| `choice` | named options, optionally described | best option + per-option probabilities |
| `score` | ordered levels, low to high | mean level + distribution over levels |
| `noul` | a yes/no statement | probability that it holds |

Good for classification, routing, intent detection, moderation gates, relevance judging
and grading, at ~30 ms on a CPU. Not for summarizing, translating or chatting.

## Usage

```bash
pip install laya
```

```python
import laya

agent = laya.load("2nugu/laya-ko")

state = "한국은행, 기준금리 0.25%p 인하 결정"
questions = {
    "topic": {
        "type": "choice",
        "instructions": "다음 뉴스 제목의 주제 분야를 고르세요.",
        "criteria": {
            "IT과학": "정보기술·과학 기사", "경제": "경제·금융·산업 기사",
            "사회": "사회·사건사고 기사", "생활문화": "생활·문화·연예 기사",
            "세계": "국제·해외 기사", "스포츠": "스포츠 기사", "정치": "정치·외교 기사",
        },
    },
    "urgent": {
        "type": "noul",
        "instructions": "이 뉴스는 즉시 대응이 필요한 사안인가?",
    },
    "importance": {
        "type": "score",
        "instructions": "이 뉴스의 중요도를 판정하세요.",
        "criteria": ["매우 낮음", "낮음", "보통", "높음", "매우 높음"],
    },
}

result = agent.predict(state, questions)
result["answers"]["topic"]["choice"]           # "경제"
result["answers"]["topic"]["probabilities"]    # {"경제": 1.0, "사회": 0.0, ...}
result["answers"]["urgent"]["noul"]            # 0.009
result["answers"]["importance"]["score"]       # 0.64  (mean level, 0–4)
```

All three questions run in one forward pass. They share the `state` and cannot see each
other. Label sets are supplied at call time, so you can change them without retraining.

These are the actual outputs. Note what they show: `topic` is a label set the model was
trained on and it is decisive; `urgent` and `importance` are scales invented on the spot
that it has never seen, and it handles the boolean far better than the ordinal. That is
the general pattern — `choice` and `noul` transfer to new label sets much more readily
than `score` does.

### ONNX

`onnx/` holds a single-graph export for non-Python deployment: `model.onnx` +
`model.onnx.data` (fp32) + `tokenizer.json` + `laya_runtime.json` (temperatures, special
token ids, token budgets) + `golden.json` (13 verification cases).

```python
import onnxruntime as ort
sess = ort.InferenceSession("onnx/model.onnx")
logits = sess.run(None, {"input_ids": ids, "attention_mask": att,
                         "marker_pos": pos, "marker_mask": mask, "qtype": qt})[0]
```

All axes are dynamic; one batch may mix question types and option counts. 28–48 ms per
item on CPU at batch 16. A non-Python client must reimplement sequence construction —
see the repo's `docs/ONNX.md` and the Rust reference in `rust/` (published uncompiled —
see the repo README). Do not use naive int8 dynamic quantization: it costs up to 9
accuracy points for ~20 % throughput.

## Results

Accuracy, and ECE (expected calibration error — lower is better):

| benchmark | n | chance | before | **after** | Δ | ECE before → after |
|---|---|---|---|---|---|---|
| KLUE-RE (relation, 30-way) | 1000 | 0.033 | 0.136 | **0.705** | **+56.9 pp** | 0.184 → 0.065 |
| KLUE-YNAT (topic, 7-way) | 1000 | 0.143 | 0.414 | **0.834** | **+42.0 pp** | 0.315 → 0.077 |
| KLUE-STS (ordinal, 6 levels) | 519 | 0.167 | 0.210 | **0.509** | **+29.9 pp** | 0.120 → 0.188 |
| AI-Hub culture MC | 900 | 0.367 | 0.373 | **0.628** | **+25.4 pp** | 0.250 → 0.084 |
| KLUE-NLI (3-way) | 1000 | 0.333 | 0.761 | **0.815** | +5.4 pp | 0.144 → 0.113 |
| KMMLU (knowledge MC) | 900 | 0.250 | 0.244 | 0.298 | +5.3 pp | 0.203 → 0.253 |
| *typed-decisions (EN)* | 2000 | 0.318 | 0.350 | **0.725** | +37.5 pp | 0.319 → 0.243 |
| *JCommonsenseQA (JA)* | 500 | 0.200 | 0.526 | **0.566** | +4.0 pp | 0.025 → 0.084 |
| *Kev decision-v2 (EN)* | 1440 | 0.300 | 0.585 | 0.572 | −1.4 pp | 0.267 → 0.307 |
| *MMLU (EN)* | 560 | 0.250 | 0.295 | 0.266 | −2.9 pp | 0.140 → 0.297 |

*Italic rows are retention checks, never trained on.* Japanese improved; the only real
English cost is 1.4 points on Kev decision-v2. English typed-decisions rose because 19 %
of each training epoch was English replay from that distribution.

Two things worth reading carefully:

- **The base model was not bad at Korean.** It already solved KLUE-NLI at 0.761. What was
  missing was ordinal judgement (STS 0.210 against a 0.167 floor), high-cardinality
  classification (RE 0.136) and calibration (YNAT ECE 0.315 — confidently wrong).
- **KMMLU and MMLU are the wrong tool for this model** and are listed only so they are not
  mistaken for a Korean signal. All three upstream Laya checkpoints score 0.24–0.32 on
  MMLU regardless of language: a 322 M encoder has no facts to recall.

## Training

| | |
|---|---|
| base | `convaiinnovations/laya`, `multilingual` subfolder |
| objective | upstream RLCD — policy gradient on a strictly proper scoring rule + soft cross-entropy |
| data | 108,665 typed decisions: 102,665 Korean + 6,000 English replay (oversampled ×4 to ≈ 19 %/epoch) |
| schedule | 4 epochs, effective batch 64, OneCycle; encoder LR 1e-5, head LR 1e-4 |
| hardware | one RTX PRO 6000, 19 minutes |

Korean data: **KLUE** (CC BY-SA 4.0 — YNAT/NLI/STS/RE `train` splits) plus several
**AI-Hub** corpora with usable metadata labels. English replay:
`LocalLLaMA/typed-decisions` (Apache-2.0). The training set is not redistributed; the
repo's `scripts/traindata.py` rebuilds the public portions.

KLUE evaluation uses the `validation` split against `train`-split training, so those rows
are clean. The AI-Hub culture row excludes its eval items by exact text match but draws
from the same corpus, so its +25.4 pp is in-domain transfer, not zero-shot.

## Limitations

- **Not generative.** No text out.
- **No world knowledge.** KMMLU 0.298 against a 0.250 floor.
- **Calibration is Korean-tuned.** Temperatures were fitted on a mixture that is ~81 %
  Korean, which is why English ECE is worse than English accuracy suggests. The repo ships
  `scripts/recalibrate.py` to refit on your own labelled data — one forward pass, no
  weight changes.
- **Korean-first, and verified in three languages only.** The base covers 100+; the other
  97 were not measured and may have regressed.
- **Budget limits.** Instructions + all options must fit in 256 tokens (48 per option);
  `state` takes the rest up to 1024 and is truncated from the right.
- **`score` is the weakest of the three types.** If an ordinal question can be re-expressed
  as a `choice`, it will usually be more accurate.

## Attribution

Built on **Laya** by Convai Innovations (Apache-2.0) —
[weights](https://huggingface.co/convaiinnovations/laya) ·
[source](https://github.com/NandhaKishorM/laya). Encoder
[mmBERT-base](https://huggingface.co/jhu-clsp/mmBERT-base) (Apache-2.0). Training recipe follows Laya's own fine-tuning notebook. See `NOTICE` for
the full list including every evaluation dataset and its license.

Licensed Apache-2.0, matching upstream.
