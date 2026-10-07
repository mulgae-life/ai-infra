---
dataset_info:
- config_name: default
  features:
  - name: question
    dtype: string
  - name: passage_text
    dtype: string
  splits:
  - name: train
    num_bytes: 20981103490.3464
    num_examples: 4467542
  - name: eval
    num_bytes: 46963416.32679984
    num_examples: 10000
  - name: test
    num_bytes: 46963416.32679984
    num_examples: 10000
  download_size: 11876547676
  dataset_size: 21075030323.000004
- config_name: question-answer
  features:
  - name: question
    dtype: string
  - name: answer
    dtype: string
  splits:
  - name: train
    num_bytes: 2677334616.396122
    num_examples: 4467542
  - name: eval
    num_bytes: 5992858.3019390125
    num_examples: 10000
  - name: test
    num_bytes: 5992858.3019390125
    num_examples: 10000
  download_size: 1566020441
  dataset_size: 2689320333.0
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
  - split: eval
    path: data/eval-*
  - split: test
    path: data/test-*
- config_name: question-answer
  data_files:
  - split: train
    path: question-answer/train-*
  - split: eval
    path: question-answer/eval-*
  - split: test
    path: question-answer/test-*
task_categories:
- text-retrieval
- question-answering
language:
- en
tags:
- medical
- retrieval
size_categories:
- 1M<n<10M
---

# MIRIAD 4.4M, split

[MIRIAD](https://huggingface.co/datasets/miriad/miriad-4.4M) reformatted for training retrieval
models: train, eval and test splits, and two subsets depending on what you want the model to
retrieve.

| subset | columns | use it to retrieve |
|---|---|---|
| `default` | `question`, `passage_text` | the source passage a question was generated from (averaging 941 tokens) |
| `question-answer` | `question`, `answer` | the generated answer to a question (much shorter) |

| split | rows |
|---|---|
| `train` | 4,467,542 |
| `eval` | 10,000 |
| `test` | 10,000 |

> [!TIP]
> This is the **training** data. To **evaluate** retrieval models on this domain, use
> [tomaarsen/miriad-benchmark-200k](https://huggingface.co/datasets/tomaarsen/miriad-benchmark-200k),
> a 1,000-query, 200,000-passage benchmark built deterministically from the splits here.

## Usage

```python
from datasets import load_dataset

# Question to source passage
train = load_dataset("tomaarsen/miriad-4.4M-split", split="train")

# Question to generated answer
qa = load_dataset("tomaarsen/miriad-4.4M-split", "question-answer", split="train")
```

The `default` subset is a plain (anchor, positive) pair format, so it works directly with
`MultipleNegativesRankingLoss` and its cached and multi-vector variants in
[Sentence Transformers](https://sbert.net/). It was used to train
[multi-vector-encoder/mLateOn-medical](https://huggingface.co/multi-vector-encoder/mLateOn-medical),
walked through in
[Training and Finetuning Multi-Vector Embedding Models](https://huggingface.co/blog/train-multi-vector-encoder).

Because the questions are generated from their source passages, lexical overlap between a question
and its gold passage is higher than in most retrieval data. Expect strong BM25 baselines, and
expect scores here to be higher than on datasets with organic queries.

## Citation

This dataset is a reformatting of MIRIAD. Please cite the original work:

```bibtex
@misc{zheng2025miriadaugmentingllmsmillions,
      title={MIRIAD: Augmenting LLMs with millions of medical query-response pairs},
      author={Qinyue Zheng and Salman Abdullah and Sam Rawal and Cyril Zakka and Sophie Ostmeier and Maximilian Purk and Eduardo Reis and Eric J. Topol and Jure Leskovec and Michael Moor},
      year={2025},
      eprint={2506.06091},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2506.06091},
}
```
