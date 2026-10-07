| 벤치 | 설정 | 행 | Qwen3.8 FP8 | Jev 1.13 | 차이 | 비고 |
|---|---|---|---|---|---|---|
| Jevtest | jevtest-support-subset | 6 | 1.0000 | 1.0000 | +0.0000 |  |
| wondertwins/jev-benchmark | clean | 75 | 0.9733 | 0.9200 | +0.0533 | exact_set_accuracy |
| wondertwins/jev-benchmark | stt | 75 | 0.9067 | 0.8667 | +0.0400 | exact_set_accuracy |
| wondertwins/jev-benchmark | stt-misheard | 75 | 0.8533 | 0.8533 | +0.0000 | exact_set_accuracy |
| SemIf | authored | 144 | 0.9782 | 0.9713 | +0.0068 | mean_family_balanced_accuracy |
| SemIf | perturbations | 108 | 1.0000 | 1.0000 | +0.0000 | mean_family_balanced_accuracy |
| JevBench | easy | 48 | 1.0000 | 1.0000 | +0.0000 |  |
| JevBench | hard | 111 | 0.8288 | 0.7207 | +0.1081 |  |
| JevBench | original | 72 | 1.0000 | 0.9861 | +0.0139 |  |
| SemIf | typesafe | 102 | 0.8962 | 0.8915 | +0.0047 | equal_case_modal_agreement |
| SemIf | wanli | 256 | 0.7635 | 0.7710 | -0.0075 | mean_family_balanced_accuracy |
| CodeComplex | codecomplex-test | 300 | 0.7000 | 0.7082 | -0.0082 |  행 수 다름(Jev 980) |
| CodeMMLU | valid-choice release | 500 | 0.6500 | 0.7049 | -0.0549 |  행 수 다름(Jev 19875) |
| LexGLUE | casehold | 300 | 0.7700 | 0.7744 | -0.0044 |  행 수 다름(Jev 3600) |
| ContractNLI | contractnli | 300 | 0.7767 | 0.7786 | -0.0019 |  행 수 다름(Jev 2091) |
| LexGLUE | unfair-tos | 300 | 0.4079 | 0.3553 | +0.0526 | f1 행 수 다름(Jev 1607) |
| MetaTool | tool awareness | 300 | 0.8267 | 0.7894 | +0.0372 |  행 수 다름(Jev 1040) |
| Jev Phishing Bench | phishing-verdict | 300 | 0.8200 | 0.6285 | +0.1915 |  행 수 다름(Jev 2000) |
| Jev Sec Bench | code | 400 | 0.8294 | 0.7935 | +0.0358 | auroc_successful_only |

벤치 19개 단순 평균: Qwen3.8 0.8411 / Jev 0.8165 / 차이 +0.0246
