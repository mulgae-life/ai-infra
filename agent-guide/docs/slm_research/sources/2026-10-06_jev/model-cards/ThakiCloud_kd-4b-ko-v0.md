---
license: apache-2.0
base_model: Qwen/Qwen3.5-4B-Base
base_model_relation: adapter
library_name: peft
language: [ko, en]
tags: [typed-decision, lora, korean, research-preview]
---
# kd-4b-ko-v0 — Korean typed-decision LoRA adapters on Qwen/Qwen3.5-4B-Base (weights only)

**Recommended adapter: `kotdaihubv2num2-s1`** (numeric v2). Not a formally promoted default — see the numeric v2 note for what is and is not established.

LoRA r16 + pointer-head adapters in the Kev typed-decision format (`choice` / `noul` / `score` questions over a text state, non-autoregressive
probability readout). Trained from the Kev-4B recipe reproduction on Qwen/Qwen3.5-4B-Base (Apache-2.0) with Korean typed-decision data built from
public Korean benchmarks (KoBEST, KLUE — CC-BY-SA-4.0; used for training only, **not redistributed here**), a small ThakiCloud synthetic
policy set, and — for the `aihub-*` / `kotdaihub-*` adapters — Korean public-sector datasets from **AI Hub (한국지능정보사회진흥원 사업결과)**:
행정 문서 대상 기계독해 데이터 (569), 금융·법률 문서 기계독해 데이터 (71610), 법률/규정 텍스트 분석 데이터 고도화 (71723), 법률/규정(판결서, 약관 등)
텍스트 분석 데이터 (580). AI Hub data was used for model training only under its usage policy; **no AI Hub data or derived text is redistributed**
here. **Weights only:** no training or evaluation data is published in this repository.

## Evaluation (internal, machine-reviewed; one question ≈ 1.75pp on `realdoc_v1`, ≈ 0.31pp on the sealed `realdoc_v2`)
| arm | aihub_dev_acc | aihub_dev_ece | ko_reviewed_acc | ko_reviewed_ece | kotd_dev_acc | kotd_dev_ece | kotd_dev_note | numeric_dev_acc | numeric_dev_ece | numeric_dev_in_acc | numeric_dev_in_ece | p50_ms | realdoc_v1_ci95_pp | realdoc_v1_consensus_acc | realdoc_v1_coverage_adjusted | realdoc_v1_delta_vs_init_pp | realdoc_v2_ci95_pp | realdoc_v2_consensus_acc | realdoc_v2_delta_vs_init_pp | transfer_v4_acc | transfer_v4_ece |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| init | 0.807 | 0.134 | 0.847 | 0.082 | 0.733 | 0.141 |  |  |  |  |  |  |  | 0.911 | 0.895 |  |  | 0.801 |  |  |  |
| kotd-s1 |  |  | 0.839 | 0.103 | 0.880 | 0.071 |  |  |  |  |  |  | [0.0, 9.09] | 0.946 | 0.930 | 3.570 | [0.62, 6.29] | 0.835 | 3.420 | 0.814 | 0.119 |
| kotdsyn-s1 |  |  | 0.935 | 0.049 | 0.878 | 0.081 |  |  |  |  |  |  | [0.0, 9.09] | 0.946 | 0.930 | 3.570 |  |  |  | 0.805 | 0.141 |
| aihubv2-s1 | 0.955 | 0.033 | 0.815 | 0.116 | 0.741 | 0.188 |  |  |  |  |  |  | [-9.09, 7.55] | 0.911 | 0.895 | 0.000 |  |  |  | 0.812 | 0.126 |
| kotdaihubv2-s1 | 0.960 | 0.029 | 0.831 | 0.108 | 0.873 | 0.091 |  |  |  |  |  |  | [-3.45, 11.11] | 0.946 | 0.930 | 3.570 |  |  |  | 0.812 | 0.140 |
| kotdaihubv2num-s1 | 0.959 | 0.028 | 0.839 | 0.135 | 0.879 | 0.087 |  | 0.470 | 0.371 | 0.999 | 0.001 |  | [1.69, 14.81] | 0.982 | 0.965 | 7.140 | [7.67, 14.87] | 0.913 | 11.180 | 0.808 | 0.139 |
| kotdaihubv2num2-s1 | 0.958 | 0.034 | 0.806 | 0.151 | 0.877 | 0.085 | v3 dev | 0.801 | 0.134 |  |  |  |  | 0.966 |  |  | [9.15, 16.46] | 0.929 | 12.730 | 0.806 | 0.138 |
| jev |  |  | 0.933 |  | 0.818 |  | first 1999 items only |  |  |  |  | 771.900 |  | 0.974 | 0.667 |  |  |  |  |  |  |
| laya |  |  | 0.476 |  | 0.460 |  |  |  |  |  |  | 691.000 |  | 0.375 | 0.368 |  |  |  |  |  |  |
| qwen27b |  |  | 0.871 |  | 0.895 |  | first 600 items only |  |  |  |  | 522.700 |  | 0.804 | 0.789 |  |  |  |  |  |  |

- `jev` = TypeSafe AI Jev (`typesafe-ai/jev`) called through Vercel AI Gateway `/v1/evaluate` on 2026-09-22 (same questions, zero-shot, one run). On the 39 statute questions both APIs accepted, kd-4b (kotd-s1) answered 39/39 and Jev 38/39 — a sample that cannot establish superiority or equivalence either way. The gateway rejects `score` questions with more than 10 rungs, so Jev did not accept 18 of the 57 questions; that is an API-contract difference, not a model-capability difference, and it drives the coverage-adjusted column. Jev's p50 here is under free-tier rate limiting and must not be read as a latency comparison.
- `laya` = convaiinnovations/laya-multilingual (mmBERT-base 322M encoder, CPU, no Korean training) and `qwen27b` = in-house Qwen3.8-27B (NVFP4) prompted zero-shot in the jev-local style (one JSON answer per record, temperature 0) — non-trained comparison arms run on the same questions.
- `init` = Kev-4B recipe reproduced on Qwen3.5-4B-Base (English suites only); other arms are delta fine-tunes from it (lr 2e-5, batch 4 x accum 2, 2 epochs, seed 1).
- Gains on kotd_dev / aihub_dev are in-distribution. On the statute test (57 machine-consensus questions, 56 Kev-supported) no adapter measurably changes accuracy: every delta is ±1–2 questions with a document-clustered CI that includes 0. The test cannot detect effects below ~5pp.
- **Sealed statute test and candidate default (2026-09-23).** `realdoc_v2` is a sealed test set: 115 verbatim Korean statute excerpts from 76 statutes / 25 domains, 345 questions, 322 scored where three model families (Claude, GPT, in-house Qwen) labeled blind and agreed with an adversarial-challenger veto; every document was checked verbatim against an independently fetched page and against the training set (sentence overlap ≤5%, oracle absent); the benchmark file, the consensus gold, the 322-item mask and the scorer code are pinned by SHA-256 before any model was scored. Three seeds of `kotdaihubv2num` score 0.913 / 0.919 / 0.935 (mean 0.922) vs base 0.801: +12.1pp, 95% CI [8.8, 15.7]; vs a same-size control trained on 6,000 extra MRC records instead of the contrast pairs: +4.2pp, CI [2.3, 6.3], p=0.0001 (document-clustered paired bootstrap on the seed-averaged correctness; the published seed 1 alone: +11.2 [7.7, 14.9] vs base, +4.7 [2.1, 7.5] vs control). By question type the gap sits in `score` (base 0.574 → control 0.691 → numeric 0.806, +11.4 [6.2, 17.3] vs control) while `choice`/`noul` are ≥0.98 for every trained arm and non-inferior (2pp margin) to the control. **Promotion to default is on hold**: the pre-registered gate also requires OOD non-inferiority within 1pp on `ko_reviewed`, and with 124 OOD questions the CI ([−4.7, 3.5] vs base) cannot establish that either way; a larger OOD set is the prerequisite. Until then `kotdaihubv2num-s1` is the candidate default and the broadest-coverage arm; `kotd-s1` keeps the best English retention, `kotdsyn-s1` the best ko_reviewed/ECE on short policy snippets, `kotdaihubv2-s1` AI Hub-style document QA. The sealed set is used only for this gate; data design and hyper-parameters are chosen on separate dev sets. A stricter post-seal oracle check flagged 2 of the 115 documents (6 questions) whose key sentence is quoted verbatim inside AI Hub court-case training records; the set was not modified, and excluding them leaves every conclusion unchanged (+12.3 [8.8, 15.9] vs base, +4.3 [2.4, 6.5] vs control).
- **Numeric v2 adapter (2026-09-24)**: `kotdaihubv2num2-s1` = the v2 mix plus 6,000 program-gold contrast pairs over six families (unit, days, fraction, cap, reduction, rate). On the sealed `realdoc_v2`, three seeds vs three base seeds: +13.77pp, CI [10.18, 17.58]; vs the same-size control: +4.76pp, CI [2.14, 7.72]; vs `kotdaihubv2num`: +0.52pp, CI [-1.34, 2.36] (not significant) (pair/document-clustered bootstrap that also resamples training seeds). Its gain over `kotdaihubv2num` is on held-out numeric families: compound arithmetic 0.568 → 0.648 (+8.0pp, CI [5.5, 10.5], seed 1). On a separate synthetic OOD set (1,510 questions) `choice` is non-inferior within 1pp (CI [-0.73, 6.37]); `noul` points up (+1.39pp) but 1pp non-inferiority is **not established** (CI [-1.27, 4.07]). Interest-rate arithmetic is still not learned. `kotd_dev`/`aihub_dev` cells for this row use the v3 dev sets and are not comparable to rows above.
- Standard-terms (약관) finding (2026-09-23): a semantic audit showed the AI Hub 580 judgment labels are not derivable from the excerpt alone (blind agreement 0.78, abstain 0.63), so a 'purity' retrain without that source was tried; across 3 seeds it regressed OOD by −4.6pp (CI [−8.6, −0.8]) and restoring the source recovered +3.2pp (CI [0.9, 6.1]). The source therefore stays in training as judgment-type data and is excluded from dev/test only. The `v4` arm is not shipped.
- No human validated any Korean label; statute-test labels are machine-consensus.
- **Correction (2026-09-22, data audit)**: the `aihub_dev` column is inflated by a label leak in one of its six sources. In the AI Hub 580 (약관 유불리) source every '유리' record carries a standard-clause section and no '불리' record does, and the v1 builder copied that section into the state, so its presence alone gives the label (aihub-s1 scored 1.000 on that source vs 0.365 for init). Excluding that source (n=1,297): init 0.877, aihub-s1 0.961, kotdaihub-s1 0.958. The two AI Hub multiple-choice sources also had the gold answer always in option position 0 in both train and dev; Kev permutes option order during training, and a same-run re-measurement with shuffled options (2026-09-22, H100) moved every arm by at most 0.6pp (e.g. init 0.781→0.779, aihub-s1 0.969→0.971), so no position bias is present and the multiple-choice numbers stand. The v2 builder (shuffled options, no standard-clause section, train/dev overlap removed) passes a deterministic audit (`scripts/data_audit.py`); `aihubv2-s1` and `kotdaihubv2-s1` are the v2 retrains (2026-09-23, H100): their `kotd_dev`/`aihub_dev` cells are measured on the deduplicated v2 dev sets (1,989 / 1,726 items), so they are not directly comparable to the v1 cells above them; `realdoc_v1` and `ko_reviewed` are the same test sets for every arm.
- **Numeric-derivation adapter (2026-09-23)**: `kotdaihubv2num-s1` = the v2 mix plus 6,000 code-generated contrast pairs whose gold is computed by a program (unit conversion 원↔만원, day arithmetic, cap exceedance, reduction denominators; no human or model labels). It is the first arm whose statute-test gain over `init` has a document-clustered 95% CI excluding zero (+7.1pp, [1.7, 14.8]); an equal-size control arm trained on extra machine-reading records instead gained +1.8pp ([−3.6, 7.8]). Caveat: the template families were designed after inspecting the statute test's residual errors, so that gain is a diagnostic, not an independent generalization claim; on a held-out numeric family the arm improves fraction→percent questions by +18pp and does not transfer to interest-rate arithmetic. Single seed; no OOD regression (ko_reviewed 0.839, English retention 0.808).
- Seed replication (2026-09-22): `kotd` and `kotdaihub` (v1 data) were each retrained with seeds 2 and 3. kotd: statute-test accuracy 0.9464 in all three seeds, kotd_dev 0.878±0.002, ko_reviewed 0.836±0.005, transfer_v4 0.808±0.005. kotdaihub: ko_reviewed 0.807/0.823/0.839 (mean 0.823, sd 0.016) vs init 0.847 — the −4pp size was seed-1 specific, but all three seeds sit below init (3-seed paired mean −2.4pp, document-clustered 95% CI [−6.2, +1.1]); the direction remains, the size is not established. Only the seed-1 adapters are shipped.

Test descriptions: {"kotd_dev": "2,000 held-out validation items from KoBEST (boolq/copa/hellaswag/wic/sentineg) + KLUE (nli/sts/ynat), converted to typed decisions; in-distribution with training", "realdoc_v1": "57 machine-consensus questions over 20 verbatim Korean statute/ordinance excerpts (3 model families unanimous + adversarial challenger); out-of-training-window inference (state 2048); development diagnostic (1 q ≈ 1.8pp)", "realdoc_v2": "SEALED statute test (2026-09-23): 322 machine-consensus questions over 115 verbatim excerpts from 76 Korean statutes / 25 domains, none sharing a statute family with realdoc_v1; consensus3 + challenger; guarded verbatim against independently fetched pages and against training-set sentence overlap; 1 q ≈ 0.31pp; scored on the same 2048-token state window", "ko_reviewed": "124 reviewed questions on LLM-generated Korean policy snippets (same generator as the small synthetic training set)", "transfer_v4": "Kev English transfer-v4 suite (retention check)"}

## Selective mode: answer only when an error-rate guarantee holds (2026-09-26)
`selective/` adds an abstention layer on top of `kotdaihubv2num2-s1`, with no change to the weights. For a target α it answers a
question only if the model's confidence clears a per-type threshold; otherwise it returns `ABSTAIN` so the question goes to a
larger model or a person. The thresholds come from Learn-then-Test (fixed-sequence, exact binomial p-values), fitted separately
per decision type with δ/types Bonferroni. What it promises, under exchangeability with the calibration profile, is
P(error rate on answered questions ≤ α) ≥ 1 − δ with δ = 0.10.

| profile (calibration data) | target α | questions abstained (test) | error on answered (test) |
|---|---|---|---|
| `statute-v2` — public statute items, [KD-Lawset-KO](https://huggingface.co/datasets/ThakiCloud/kd-lawset-ko) | 0.05 | 59.6% | 0.0% (219 answered) |
| `statute-v2` | 0.10 | 18.1% | 2.5% (444 answered) |
| `aihub-doc` — internal AI Hub dev document QA (data not released) | 0.05 | 26.6% | 1.3% (541 answered) |
| `aihub-doc` | 0.10 | 0.7% | 3.7% (732 answered) |

- A 1% or 2% target cannot be certified with these calibration sizes, and the layer abstains on everything.
- Over 500 law-grouped re-splits of lawset-v2, the exact 95% lower bound of the answered-question error exceeded α in at most
  1.2% of re-splits for any type (in-distribution). On laws from held-out ministries (domain shift), yes/no error rose to within about
  1pp of α, so re-calibrate for a new domain.
- On deadline questions the 4B abstained on (406 of 591 Enforcement-Decree items), an in-house Qwen3.8-27B that only extracted
  the day count and dates, with code doing the arithmetic, was correct on 99.3%, versus 58.4% for the 4B.
- Labels of the statute profile are code-generated; an independent LLM audit (blind `gpt-5.6-luna`, disagreements adjudicated by
  `gpt-5.6-sol`) found 0 wrong labels in 2,812 items (95% upper bound 0.13%). This is not a human audit. A later rule scan
  found 4 items whose fine cap depends on an unstated amount ("N배", "whichever is higher"); the audit had flagged only 1.
  They are listed as ambiguous in the dataset; removing them changes the `statute-v2` α = 0.10 row to 19.0% / 1.8%.

```python
from selective import Selective          # selective/selective.py, MIT
sel = Selective("selective/thresholds.json", profile="statute-v2", alpha=0.10)
sel.decide(qtype="noul", p=probs)        # probs = Kev probability vector for one question
```

## How to use
**Credit**: built on [Kev](https://github.com/jaredpalmer/kev) by Jared Palmer (Apache-2.0). The training/serving code (`kev.train`, `kev.serve`, pointer head) and the Kev-4B recipe are theirs; this repo adds Korean typed-decision fine-tunes.

Load with the Kev codebase (`python -m kev.serve --run adapters/<arm>`; base = `Qwen/Qwen3.5-4B-Base`). Each adapter directory carries
`adapter_config.json`, `adapter_model.safetensors`, `head.pt`, `training_config.json`. `sha256_manifest.json` pins every file.

## Limits
Training window 384 state tokens; longer documents are served with the inference window (state 2048 / branch 4096) — out-of-training-window.
Labels on the statute test are machine-consensus (three model families + adversarial challenger), not human gold.

Not affiliated with or endorsed by TypeSafe AI. "Jev" and "System One" are referenced only for comparative research; this repo uses a typed-decision research format and has NOT been contract-tested against any TypeSafe SDK.
