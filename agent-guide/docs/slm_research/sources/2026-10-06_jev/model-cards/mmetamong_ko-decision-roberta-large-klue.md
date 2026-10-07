---
language:
- ko
- en
license: cc-by-sa-4.0
base_model: klue/roberta-large
library_name: transformers
datasets:
- klue/klue
- skt/kobest_v1
- LocalLLaMA/typed-decisions
pipeline_tag: text-classification
inference: false
tags:
- korean
- decision-model
- system-one
- typed-decisions
- choice
- noul
- score
- classification
- nli
- klue
- kobest
- relation-extraction
- roberta
- calibration
---

# ko-decision-roberta-large-klue

A Korean **typed-decision model** (Choice / Noul / Score) fine-tuned from `klue/roberta-large` (337M parameters, bidirectional encoder). Given a state, an instruction and a list of options, it returns a probability for every option. It does not generate text.

## Versions

Two checkpoints of one model line, both CC BY-SA 4.0. They differ in training data.

| | [`ko-decision-roberta-large-klue`](https://huggingface.co/mmetamong/ko-decision-roberta-large-klue) | [`ko-decision-roberta-large`](https://huggingface.co/mmetamong/ko-decision-roberta-large) |
|---|---|---|
| Training data | KLUE, KoBEST (BoolQ, COPA), typed-decisions | + KoBEST-HellaSwag and 7 open-license Kev sources |
| KLUE-NLI accuracy | 90.69% | 90.49% |
| KLUE-YNAT accuracy | **88.30%** | 87.10% |
| KLUE-STS MAE (lower is better) | 0.450 | **0.431** |
| KLUE-RE accuracy | 82.2% | 82.5% |
| KoBEST-HellaSwag accuracy | 39.0% | **81.2%** |
| Kev transfer suites, unseen formats | 44.2% | 44.1% |
| Picks `A` on letter-labelled KMMLU | 81% | 40% |

- **`ko-decision-roberta-large`** (recommended): adds Korean four-way multiple choice and is less distracted by letter labels, at a cost of 1.2 points of YNAT (significant against `-klue`).
- **`ko-decision-roberta-large-klue`**: the narrowest training data and the best YNAT. Choose it if you only need the KLUE-style tasks.

This card describes **`ko-decision-roberta-large-klue`**.

## 한국어 요약

- **무엇인가:** 글을 쓰지 않고, 주어진 선택지마다 확률을 매기는 한국어 판단 모델입니다. 고르기(Choice), 예/아니오(Noul), 점수 매기기(Score) 세 가지 질문을 받습니다.
- **잘하는 것:** 학습한 KLUE 네 과제(자연어 추론, 뉴스 주제 분류, 문장 유사도, 관계 추출)에서 `2nugu/laya-ko`보다 높습니다. 같은 2,080문항에서 NLI 90.7% 대 81.0%, YNAT 88.3% 대 82.0%, STS 오차 0.450 대 0.553이고, 관계 추출 1,000문항에서 82.2% 대 70.8%입니다. 바탕이 된 Laya 다국어 모델(같은 문항에서 NLI 73.67%, YNAT 39.60%)보다는 훨씬 높습니다.
- **못하는 것:** 학습하지 않은 형식의 질문은 `laya-ko`보다 뚜렷하게 약합니다(영어 Kev decision-v2 34.2% 대 57.2%, 일본어 상식 23.0% 대 58.4%). 지식 문제(KMMLU, MMLU)는 찍는 수준입니다.
- **주의:** 원래 확률은 실제보다 확신이 과합니다. 확신도가 필요하면 `calibration.json`의 과제별 온도로 나눠 쓰세요. 코드 판단 데이터는 학습에도 평가에도 쓰지 않았습니다.
- **사용법:** 아래 Usage의 코드를 그대로 실행하면 됩니다.

## Results against `2nugu/laya-ko` and Laya multilingual

Fixed 2,080-row KLUE slice (NLI 999 rows / 333 premise groups, YNAT 1,000, STS 81), raw probabilities at temperature 1. `laya-ko` and Laya multilingual (`convaiinnovations/laya`, `multilingual` subfolder) were evaluated on 2026-10-04 with the same harness and their shipped temperatures. Intervals are paired cluster bootstrap, 10,000 replicates.

| Metric | Laya multilingual | laya-ko | this model | Δ vs laya-ko, 95% interval | Δ vs Laya, 95% interval |
|---|---:|---:|---:|---|---|
| KLUE-NLI accuracy | 73.67% | 80.98% | **90.69%** | +9.71 pp [+7.21, +12.11] | +17.02 pp [+14.31, +19.62] |
| KLUE-YNAT accuracy | 39.60% | 82.00% | **88.30%** | +6.30 pp [+4.00, +8.70] | +48.70 pp [+45.30, +52.10] |
| KLUE-STS MAE (lower is better) | 1.1285 | 0.5527 | **0.4504** | −0.102 [−0.196, −0.009] | −0.678 [−0.890, −0.475] |

All six intervals exclude zero. `laya-ko` is Laya multilingual fine-tuned on Korean; Laya multilingual is the general upstream model it started from.

This slice is public KLUE validation data that earlier work in this project had looked at; it is not a blind external test. The sample IDs behind the numbers on the laya-ko model card are unpublished, so these figures are not comparable with that card. laya-ko is 322M parameters and was trained on a different mix (KLUE, AI-Hub, English replay).

## On the benchmarks the laya-ko card reports

Same benchmarks, evaluated with one harness. The author's sample IDs and STS binning are unpublished, so these are not the same rows; the harness nevertheless lands close to the card for the two Laya models (card values in parentheses). AI-Hub culture MC is not public and was not run.

### Trained tasks

| Benchmark | Laya multilingual | laya-ko | this model |
|---|---:|---:|---:|
| KLUE-RE, 1,000 rows, 30-way accuracy | 16.4% (13.6%) | 70.8% (70.5%) | **82.2%** |
| KLUE-YNAT, 1,000 rows, accuracy | 39.6% (41.4%) | 82.2% (83.4%) | **88.3%** |
| KLUE-NLI, 999 rows, accuracy | 73.7% (76.1%) | 81.0% (81.5%) | **90.7%** |
| KLUE-STS, 519 rows, 6-level accuracy | 20.6% (21.0%) | 50.7% (50.9%) | **56.3%** |
| typed-decisions EN, 2,000 rows, accuracy | 35.0% (35.0%) | 71.2% (72.5%) | 71.6% |

KLUE rows are from the validation split; training used the train split. English is on par with laya-ko, not better.

### Tasks this model was not trained on

| Benchmark | Chance | Laya multilingual | laya-ko | this model |
|---|---:|---:|---:|---:|
| Kev decision-v2 (EN), 1,440 questions | 30.0% | 58.8% (58.5%) | **57.1%** (57.2%) | 34.2% |
| JCommonsenseQA (JA), 500 rows | 20.0% | 52.8% (52.6%) | **58.4%** (56.6%) | 23.0% |
| KMMLU, 900 rows | 25.0% | 24.4% (24.4%) | 24.3% (29.8%) | 14.6% |
| MMLU, 560 rows | 25.0% | 27.9% (29.5%) | 27.9% (26.6%) | 22.3% |

**This model does not transfer to question formats it was not trained on, and laya-ko does.** Laya started as an English decision model before Korean was added; this model started from a plain Korean encoder and learned six task families.

- **Letter bias.** When options carry letter labels (`A: …`, `B: …`) this model picks `A` most of the time, because each option is scored without seeing the others. That is why KMMLU and MMLU are *below* chance. With the letters removed and only the option text given, it is at chance: KMMLU 23.3%, MMLU 24.8%, JCommonsenseQA 25.6%. Do not put letter or number labels in front of options.
- **Yes bias.** On Kev's unseen yes/no questions it answers "yes" far more often than the gold labels do.
- KMMLU and MMLU test recall of facts, which none of these encoders has; the laya-ko card says the same. The KMMLU and MMLU prompt layout is ours (no published fixture), which may explain the gap to the card's laya-ko KMMLU figure.

## Other evaluations

| Evaluation | Rows | Result |
|---|---:|---|
| Project test: KLUE-NLI / KLUE-YNAT accuracy | 600 / 700 | 91.8% / 86.6% |
| Project test: KLUE-STS MAE | 200 | 0.406 |
| Project test: KoBEST-BoolQ / KoBEST-COPA accuracy | 200 / 200 | 89.5% / 86.5% |
| Common slice: STS Pearson / Spearman | 81 | 0.925 / 0.926 |
| Out of domain: KoBEST-WiC accuracy | 150 | 60.0% |
| English typed-decisions test: choice / noul accuracy | 600 / 600 | 72.0% / 80.7% |
| English typed-decisions test: score MAE | 800 | 0.292 |

## Probability quality — read before using confidences

Raw probabilities are **overconfident**. Per-task temperatures fitted on a held-out calibration split (599 rows) are 2.45–4.4. The table shows their effect on the project test split:

| Task | Temperature | NLL (T=1 → fitted) | ECE10 (T=1 → fitted) |
|---|---:|---|---|
| KLUE-NLI | 3.30 | 0.587 → 0.260 | 0.074 → 0.025 |
| KLUE-YNAT | 2.45 | 0.719 → 0.437 | 0.098 → 0.028 |
| KLUE-STS | 3.20 | 1.349 → 1.001 | — |
| KoBEST-BoolQ | 4.40 | 0.597 → 0.250 | 0.105 → 0.059 |
| KoBEST-COPA | 2.60 | 0.442 → 0.303 | 0.090 → 0.039 |

Divide the scores by the task temperature in `calibration.json` before the softmax when you need calibrated confidence. No temperature was fitted for KLUE-RE (no calibration rows). The temperatures were fitted on KLUE/KoBEST only and are not expected to transfer to other domains. Temperature does not change which option ranks first.

## Usage

```bash
pip install "transformers>=4.57" torch huggingface_hub
```

### 1. Load the model

Run this once. The examples below reuse `decide` and `temperatures`.

```python
import json
import torch
from huggingface_hub import hf_hub_download
from transformers import AutoModelForSequenceClassification, AutoTokenizer

repo = "mmetamong/ko-decision-roberta-large-klue"
device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(repo)
model = AutoModelForSequenceClassification.from_pretrained(repo).to(device).eval()
temperatures = json.load(open(hf_hub_download(repo, "calibration.json")))["temperatures"]


@torch.inference_mode()
def decide(state, instruction, options, temperature=1.0):
    """Return one probability per option. Each option is one (instruction + option, state) text pair."""
    batch = tokenizer([f"{instruction} {o}" for o in options], [state] * len(options),
                      truncation="only_second", max_length=512, padding=True, return_tensors="pt").to(device)
    scores = model(**batch).logits[:, 0].float()
    return torch.softmax(scores / temperature, dim=0).tolist()


def show(name, probs):
    print(name, [round(p, 3) for p in probs])
```

| Type | Question | Options | How to read the output |
|---|---|---|---|
| Choice | Which one? | Any list of candidates | Highest probability is the answer |
| Noul | Yes or no? | `[false, true]` order | Last probability is P(true) |
| Score | How much? | Ordered levels | Expected level is the score |

### 2. Choice — natural language inference

```python
nli_options = ["entailment: 가설이 전제로부터 반드시 참이다 (함의)",
               "neutral: 가설이 전제로부터 참인지 거짓인지 알 수 없다 (중립)",
               "contradiction: 가설이 전제와 모순된다 (모순)"]
nli = dict(state="전제: 하지만 불편함 없이 이용할 수 있습니다.\n가설: 이용할 때 불편함이 있습니다.",
           instruction="전제에 대해 가설이 갖는 논리적 관계를 판정하세요.",
           options=nli_options)
probs = decide(**nli)
show("nli raw       ", probs)
print("  ->", nli_options[probs.index(max(probs))])
```

```text
nli raw        [0.0, 0.0, 1.0]
  -> contradiction: 가설이 전제와 모순된다 (모순)
```

### 3. Choice — topic classification

```python
topics = ["IT과학", "경제", "사회", "생활문화", "세계", "스포츠", "정치"]
probs = decide(state="삼성전자, 차세대 반도체 공정 양산 시작",
               instruction="뉴스 제목의 주제를 7개 후보 중에서 고르라.",
               options=topics)
show("topic         ", probs)
print("  ->", topics[probs.index(max(probs))])
```

```text
topic          [0.283, 0.717, 0.0, 0.0, 0.0, 0.0, 0.0]
  -> 경제
```

The probability is split between IT과학 (0.283) and 경제 (0.717): a headline about a chip maker fits both labels.

### 4. Noul — yes/no question

```python
probs = decide(state="문맥: 한라산은 제주도에 있는 산으로, 높이는 1,947m이며 대한민국에서 가장 높다.\n"
                     "판단할 내용: 한라산은 대한민국에서 가장 높은 산이다.",
               instruction="문맥을 근거로 판단할 내용이 참인가? 예 또는 아니오로 판단하라.",
               options=["거짓: 질문의 답은 아니오이다.", "참: 질문의 답은 예이다."])
print(f"boolq           P(true) = {probs[1]:.3f}")
```

```text
boolq           P(true) = 1.000
```

### 5. Score — sentence similarity (0–5)

```python
probs = decide(state="문장 1: 숙소 위치가 지하철역에서 가까워서 좋았어요.\n문장 2: 숙소가 역 근처라 편리했습니다.",
               instruction="두 문장의 의미 유사도를 0~5 척도로 판단하라. 핵심 내용은 사실·정보·요청·명령·감정이며, "
                           "부차적 내용은 뉘앙스·공손함 등이다. 각 점수의 설명을 적용하라.",
               options=["0: 의미와 주제가 모두 다르다.",
                        "1: 주제만 같고 핵심 내용과 부차적 내용은 다르다.",
                        "2: 핵심 내용은 다르고 일부 부차적 내용만 비슷하다.",
                        "3: 핵심 내용은 비슷하지만 부차적 내용에 무시할 수 없는 차이가 있다.",
                        "4: 의미가 거의 같고 일부 부차적 내용만 다르다.",
                        "5: 핵심 내용과 부차적 내용의 의미가 모두 같다."])
show("sts           ", probs)
print(f"  -> similarity = {sum(level * p for level, p in enumerate(probs)):.2f} / 5")
```

```text
sts            [0.0, 0.0, 0.0, 0.212, 0.787, 0.0]
  -> similarity = 3.79 / 5
```

### 6. Calibrated confidence

Pass the task temperature from `calibration.json`. The ranking stays the same; only the confidence changes.

```python
show("nli calibrated", decide(**nli, temperature=temperatures["klue_nli"]))
```

```text
nli calibrated [0.02, 0.02, 0.96]
```

Outputs above are from this checkpoint on Apple MPS.

### 7. With `pipeline`

The standard `text-classification` pipeline also works. Pass text pairs and `function_to_apply="none"` to get the raw scores, then take the softmax over one question's options yourself.

```python
from transformers import pipeline

scorer = pipeline("text-classification", model=repo, function_to_apply="none")
pairs = [{"text": f"{nli['instruction']} {o}", "text_pair": nli["state"]} for o in nli_options]
scores = torch.tensor([r["score"] for r in scorer(pairs)])
show("pipeline      ", torch.softmax(scores, dim=0).tolist())
```

```text
pipeline       [0.0, 0.0, 1.0]
```

### Notes

- **Format.** A standard `RobertaForSequenceClassification` with one output (`num_labels=1`), loaded with `AutoModelForSequenceClassification`; no custom code. Each (instruction + option, state) pair gets one score, and a softmax over one question's options gives the distribution. A score on its own, without the other options of the same question, has no fixed meaning.
- **Head.** The model was trained with a single linear layer on the first token. RoBERTa's classification head adds a dense layer and a tanh, so that layer is stored as 0.001 × identity, which makes the head compute the trained linear layer: over the 2,080 common-slice rows the largest probability difference to the training-format checkpoint is below 1e-6 (`eval/export_check.json`).
- **Tokenizer.** Configured not to emit `token_type_ids` (RoBERTa has a single token type). Inputs beyond 512 tokens are truncated on the state side.
- **Hub widget.** Disabled, because it sends single texts, not pairs.
- **Check.** Output from this repository on Apple MPS (float32) picks the same top option as the training-GPU evaluation (BF16) on all 2,080 common-slice rows; the largest probability difference is 0.041 (`eval/verify_local.json`).
- The `eval/*.json` records name project scripts (`scripts/…`) in their `harness` fields; those scripts are not part of this repository.

## Training

Two stages. Stage 2 continues from the stage-1 weights and adds KLUE-RE while replaying all stage-1 data, so the earlier tasks are not forgotten.

### Data

| Source | Rows | Share (stage 2) | Stage | License |
|---|---:|---:|---|---|
| KLUE-YNAT | 45,678 | 35.9% | 1, 2 | CC BY-SA 4.0 |
| KLUE-RE | 32,170 | 25.3% | 2 | CC BY-SA 4.0 |
| KLUE-NLI | 24,993 | 19.7% | 1, 2 | CC BY-SA 4.0 |
| KLUE-STS | 11,656 | 9.2% | 1, 2 | CC BY-SA 4.0 |
| `LocalLLaMA/typed-decisions` (English) | 6,000 | 4.7% | 1, 2 | Apache-2.0 |
| KoBEST-BoolQ | 3,659 | 2.9% | 1, 2 | CC BY-SA 4.0 |
| KoBEST-COPA | 3,006 | 2.4% | 1, 2 | CC BY-SA 4.0 |
| **Total** | **127,162** | 100% | | |

Korean rows come from the official train splits with the evaluation groups excluded. NLI, YNAT and STS rows use three option phrasings (original, Korean description, English description) in equal shares. KLUE-RE uses the 30 label names as options; 300 further train rows were held out for monitoring.

### Setup

| Item | Stage 1 | Stage 2 |
|---|---|---|
| Starts from | `klue/roberta-large` | Stage-1 checkpoint (encoder and head) |
| Data | 94,992 rows (no KLUE-RE) | 127,162 rows |
| Epochs / steps | 4 / 11,876 | 2 / 7,948 |
| Wall time | 72 minutes | 78 minutes |
| Checkpoint selection | Lowest dev error over NLI, YNAT, STS; step 11,872 | Lowest dev error over NLI, YNAT, STS, RE; step 5,961 |

Common to both stages:

| Item | Value |
|---|---|
| Objective | Soft-target cross-entropy over a row's options; no auxiliary loss |
| Optimiser | AdamW, weight decay 0.01, gradient clip 1.0 |
| Learning rate | Encoder 1e-5, head 1e-4 |
| Schedule | 10% linear warm-up, then linear decay |
| Batch | 32 rows per step (length-sorted micro-batches of at most 64 options, gradients accumulated) |
| Seed | 43 |
| Precision / hardware | BF16 autocast, one RTX PRO 6000 |

The dev error is the mean of `1 − accuracy` per classification task and `MAE / 5` for STS.

### What stage 2 changed

Against the stage-1 checkpoint on the common slice (paired, 95% interval): NLI +0.10 pp [-1.30, +1.50], YNAT +0.00 pp [-1.20, +1.20], STS MAE +0.019 [-0.011, +0.049]: no detectable change. KLUE-RE went from 13.4% to 82.2%.

A single-stage run on the same 127,162 rows from `klue/roberta-large` reached 76.2% on KLUE-RE but 88.1% on NLI, significantly below stage 1, and was not released. Stage-1 records are kept under `eval/stage1_*`.

## Limitations

- **Narrow.** Strong on the six trained task families, weak elsewhere: Kev decision-v2 34.2% and JCommonsenseQA 23.0% against laya-ko's 57.2% and 58.4%. KoBEST-WiC is 60.0%.
- **Letter and yes biases** on unseen formats (see above). Give options as plain text without `A:`/`1.` labels.
- Korean-centred vocabulary: English words and code are split into very small pieces (`def` → `de`, `##f`). English results cover four business workflows only; **no code-judgement data was used in training or evaluation**.
- One forward pass per option: a 7-option question costs seven passes and a 30-way KLUE-RE question costs thirty.
- The comparison slice is public and has been inspected during this project; STS has only 81 rows there.
- YNAT and KLUE-RE are 61% of the training rows; task balance was not tuned.
- Stage 2 was run once (one seed). Stage 1 was run with two seeds; the other reached 88.6% NLI on the common slice, so about two points of NLI are within seed-to-seed variation.
- No safety, bias or toxicity evaluation.
- Raw confidences are overconfident (see above).

## License and attribution

Released under **CC BY-SA 4.0**.

- Base model: `klue/roberta-large`. The KLUE repository states "This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License"; neither that repository nor the base model's Hugging Face card states a separate license for the pretrained weights. This release follows the repository's CC BY-SA 4.0 statement.
- Training data: KLUE and KoBEST are CC BY-SA 4.0 (see `DATA_NOTICE.md`, `DATA_LICENSE_CC-BY-SA-4.0.txt`); `LocalLLaMA/typed-decisions` is Apache-2.0.

Citations:

- KLUE: Park et al., 2021, https://arxiv.org/abs/2105.09680
- KoBEST: Kim et al., 2022, https://arxiv.org/abs/2204.04541
