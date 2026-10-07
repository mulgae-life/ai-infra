# Evaluation results — project

Model: qwen3.8-27b-fp8-vllm

| Project | Configuration | Score | Metric | Questions | Failed | Project coverage |
| --- | --- | --- | --- | --- | --- | --- |
| Jevtest | jevtest-support-subset | 1.000000 | accuracy | 6 | 0 | complete |
| SemIf | authored | 0.978175 | mean_family_balanced_accuracy | 144 | 0 | complete |
| SemIf | perturbations | 1.000000 | mean_family_balanced_accuracy | 108 | 0 | complete |
| wondertwins/jev-benchmark | clean | 0.973333 | exact_set_accuracy | 75 | 0 | complete |
| wondertwins/jev-benchmark | stt | 0.906667 | exact_set_accuracy | 75 | 0 | complete |
| wondertwins/jev-benchmark | stt-misheard | 0.853333 | exact_set_accuracy | 75 | 0 | complete |

Scores are recomputed from examples. Different metrics/configurations are not averaged.
Complete means all declared suites are represented; failures and missing predictions remain in the metrics.
