---
license: apache-2.0
base_model: Qwen/Qwen3.5-4B
base_model_relation: adapter
library_name: peft
pipeline_tag: text-classification
language:
  - ko
  - en
tags:
  - lora
  - decision-model
  - calibration
  - system-one
  - intent-classification
model-index:
  - name: CoCo-Decision-4B-Ko
    results:
      - task:
          type: text-classification
          name: Decision (System One)
        dataset:
          name: JevBench public
          type: jevbench
          split: public
        metrics:
          - type: accuracy
            value: 0.870
            name: Accuracy
          - type: ece
            value: 0.070
            name: ECE (15 bins)
      - task:
          type: text-classification
          name: Intent and scenario classification
        dataset:
          name: MASSIVE ko-KR (600-answer test sample)
          type: AmazonScience/massive
          config: ko-KR
          split: test
        metrics:
          - type: accuracy
            value: 0.915
            name: Accuracy
          - type: ece
            value: 0.023
            name: ECE (15 bins)
      - task:
          type: text-classification
          name: Intent and scenario classification
        dataset:
          name: MASSIVE en-US (600-answer test sample)
          type: AmazonScience/massive
          config: en-US
          split: test
        metrics:
          - type: accuracy
            value: 0.933
            name: Accuracy
          - type: ece
            value: 0.030
            name: ECE (15 bins)
---

# CoCo-Decision-4B-Ko

**Version 1.0.0** (2026-09-29) · Git tag `v1.0.0` in this repository

CoCo-Decision-4B-Ko is a 4B-parameter bilingual (Korean / English) decision model. Given a situation and a typed question, it returns a probability distribution instead of free text:

| Question type | Output |
|---|---|
| `noul` | probability that a yes/no statement holds |
| `choice` | probability for each of the listed options |
| `score` | probability for each point on an ordinal scale |

It is a LoRA adapter on [Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) (revision `851bf6e8`). Probabilities are read from the option-label token logits of a single forward pass, so one decision costs one prefill and no generation.

> Not affiliated with or endorsed by TypeSafe AI. "System One" and "Jev" are names used by TypeSafe AI; this model independently implements a compatible decision interface.

## Intended use

- Front-line routing and gating in agent systems: intent routing, "is this answerable from the document", "does this response meet the request", escalation decisions
- Places where a threshold on a probability is more useful than a generated answer (for example, act automatically above 0.9, ask a human below it)

Out of scope: open-ended generation, factual question answering without a supplied context, and high-stakes decisions (medical, legal, credit, employment) without human review.

## How to use

### Quick start (transformers + PEFT)

Requirements: `torch`, `transformers>=5.17`, `peft>=0.21`, and `bitsandbytes` for 4-bit loading.

```python
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

BASE, REVISION = "Qwen/Qwen3.5-4B", "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a"

tokenizer = AutoTokenizer.from_pretrained(BASE, revision=REVISION)
model = AutoModelForCausalLM.from_pretrained(
    BASE, revision=REVISION, device_map="auto", dtype=torch.bfloat16,
    # 8 GB GPU: 4-bit base. Remove quantization_config for bf16 on a GPU with >= 12 GB.
    quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                           bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True),
)
model = PeftModel.from_pretrained(model, "corners-ai/CoCo-Decision-4B-Ko", revision="v1.0.0").eval()


def decide(state: str, question: str, options: dict[str, str]) -> dict[str, float]:
    """Return a probability for each option key."""
    letters = [chr(ord("A") + i) for i in range(len(options))]
    lines = ["State:", state, "", f"Question: {question}", "Options:"]
    lines += [f"{letter}. {key}: {text}" for letter, (key, text) in zip(letters, options.items())]
    lines.append("Answer with the letter only.")
    prompt = tokenizer.apply_chat_template(
        [{"role": "user", "content": "\n".join(lines)}], tokenize=False, add_generation_prompt=True
    ) + "Answer:"
    ids = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(model.device)
    with torch.no_grad():
        logits = model(**ids).logits[0, -1]
    label_ids = [tokenizer.encode(" " + letter, add_special_tokens=False)[0] for letter in letters]
    probs = torch.softmax(logits[label_ids].float(), dim=-1).tolist()
    return dict(zip(options, probs))


print(decide(
    "Customer: I was charged twice for my order last week.",
    "Which team should handle this ticket?",
    {"billing": "payment, refund or invoice problems",
     "shipping": "delivery status or delays",
     "account": "login or profile problems"},
))
# {'billing': 0.986, 'shipping': 0.008, 'account': 0.006}  (4-bit, RTX 4060)

print(decide(
    "Refunds are available within 14 days of delivery. The order was delivered 20 days ago.",
    "Is the customer eligible for a refund?",
    {"yes": "The statement is true.", "no": "The statement is false."},
))
# {'yes': 0.064, 'no': 0.936}
```

### Prompt format

The adapter was trained on exactly this input; deviations lower accuracy and calibration.

- User turn: `State:` + the situation, a blank line, `Question:` + the question, `Options:`, one line per option as `<letter>. <key>: <description>`, then `Answer with the letter only.`
- Apply the model's chat template with `add_generation_prompt=True` and append `Answer:`.
- Read the next-token logits of the letters **with a leading space** (`" A"`, `" B"`, ...) and softmax over those letters only.
- Yes/no questions are two options: `yes: The statement is true.` and `no: The statement is false.` (or your own descriptions of the true and false case).
- Ordinal scores are options `0`, `1`, `2`, ... with one description per level.
- A structured situation can be passed as JSON text in `State:`.

Hardware: 12 GB of GPU memory in bf16 at a 4,096-token context, or 8 GB with the 4-bit base shown above (JevBench public accuracy 0.857 in 4-bit vs 0.870 in bf16).

### Serving and evaluation (optional)

The model was built and evaluated with [oh-my-jev (omj)](https://github.com/iamupd/oh-my-jev), an open-source toolkit that serves it behind a TypeSafe-compatible `/v1/systemone` endpoint and runs the benchmarks below.

```bash
git clone https://github.com/iamupd/oh-my-jev && cd oh-my-jev
uv sync --extra semif
uv run omj bench --model corners-ai/CoCo-Decision-4B-Ko --suite jevbench-public --view   # benchmark, report in the browser
uv run omj ui --target corners-ai/CoCo-Decision-4B-Ko --target Qwen/Qwen3.5-4B             # side-by-side playground vs the base model
```

## Training

- Method: LoRA (r=16, alpha=32) on the attention and linear-attention projections, one epoch, context length 4,096 tokens
- Objective: cross-entropy restricted to the option-label tokens, plus a Brier-score term for calibration and a KL term to the base model on selected tasks to limit forgetting
- Data: a mixture of publicly available Korean and English datasets (intent classification, reading comprehension, natural-language inference, sentiment, reasoning and response-quality judgement) converted into the three question types; synthetic decisions whose labels are computed by code (rule engines, date and arithmetic calculations); and synthetic decisions labelled by an LLM teacher, kept only when repeated labelling agreed. No outputs from any commercial decision API were used.

### Benchmark contamination statement

- No JevBench items (public or sealed) were used for training.
- Part of the synthetic data was designed after studying the task types in the JevBench public set (long policy documents, multi-step reasoning, date arithmetic). All synthetic text was written independently and checked to share no 8-gram with the public items. Scores on the JevBench public set may therefore overstate performance on unseen items of the same types.
- Model versions were selected on separate contamination-filtered holdout suites, not on JevBench.

## Evaluation

Measured with `omj bench` in bf16 (2026-09). Jev 1.13 figures were measured through its public API on the same items. Brackets are 95% Wilson intervals for accuracy.

| Suite | N | CoCo-Decision-4B-Ko accuracy | CoCo-Decision-4B-Ko ECE | Jev 1.13 accuracy | Jev 1.13 ECE |
|---|---|---|---|---|---|
| JevBench public | 231 | **0.870** [0.821, 0.907] | 0.070 | 0.853 | **0.040** |
| MASSIVE ko-KR (test sample) | 600 | **0.915** [0.890, 0.935] | 0.023 | 0.831 | 0.076 |
| MASSIVE en-US (test sample) | 600 | **0.933** [0.910, 0.951] | 0.030 | 0.856 | 0.075 |

- JevBench public: hard-tier accuracy 0.748; coverage at 5% risk 0.745 (Jev 1.13: 0.836).
- The JevBench accuracy difference to Jev 1.13 is within the 95% interval; it is not a statistically established lead.
- ECE: expected calibration error (15 bins; lower is better).

## Limitations

- Calibration is weaker than Jev 1.13 on JevBench (ECE 0.070 vs 0.040); recalibrate (`omj bench --fit-temperature`) on your own data before relying on fixed thresholds.
- Long policy documents and date/number calculations remain the weakest JevBench task types (public set: 0.63 and 0.40 accuracy), and the model is overconfident on the latter.
- Korean and English only. Other languages are untested.

## Versions

| Version | Date | Notes |
|---|---|---|
| 1.0.0 | 2026-09-29 | First release. LoRA adapter on Qwen/Qwen3.5-4B @ `851bf6e8` |

Load a fixed version with `hf download corners-ai/CoCo-Decision-4B-Ko --revision v1.0.0`.

## License

The adapter is released under Apache-2.0. The base model is subject to its own license ([Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B)).

## Citation

```bibtex
@misc{cocodecision4bko2026,
  title  = {CoCo-Decision-4B-Ko: a calibrated bilingual decision model},
  version = {1.0.0},
  author = {{Corners AI}},
  year   = {2026},
  url    = {https://huggingface.co/corners-ai/CoCo-Decision-4B-Ko}
}
```
