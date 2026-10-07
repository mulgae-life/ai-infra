---
license: mit
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
dataset_info:
  features:
  - name: DATASET
    dtype: string
  - name: QUESTION
    dtype: string
  - name: ANSWER
    dtype: string
  splits:
  - name: train
    num_bytes: 180899
    num_examples: 719
  download_size: 43802
  dataset_size: 180899
task_categories:
- question-answering
language:
- ko
tags:
- insurance
- medical
pretty_name: Seoul University Insurnace mathcing QA Dataset
size_categories:
- n<1K
---