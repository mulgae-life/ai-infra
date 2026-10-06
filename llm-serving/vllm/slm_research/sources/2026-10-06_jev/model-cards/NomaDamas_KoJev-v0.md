---
license: apache-2.0
language:
  - ko
base_model: skt/A.X-Encoder-base
tags:
  - encoder
  - korean
  - typed-decisions
  - system-one
library_name: transformers
---

# KoJev-v0

Korean typed-decision encoder. A **state** plus `choice` / `score` / `noul` questions in, calibrated probabilities out, one forward pass. Not a chat model.

Independent of TypeSafe Jev. Wire shape follows `POST /v1/systemone`.

## License

**Apache-2.0.** Backbone is a fine-tune of [`skt/A.X-Encoder-base`](https://huggingface.co/skt/A.X-Encoder-base) (Apache-2.0, SKT AI Model Lab). See `NOTICE`.

## What's in the box

| file | what |
|---|---|
| `model.safetensors` + `config.json` | A.X Encoder backbone after SFT |
| `head.safetensors` | span-pooling grouped-softmax head |
| `kojev_config.json` | pooling, temperature, markers |
| `tokenizer.json` | A.X tokenizer plus `[STATE]` `[Q]` `[OPT]` |

Load with the [KoJev](https://github.com/NomaDamas/kojev) package (`load_checkpoint`), not `AutoModelForSequenceClassification`.

```python
from pathlib import Path
from huggingface_hub import snapshot_download
from kojev.encoder import load_checkpoint
from kojev.schema import Example, Question, QuestionType

root = Path(snapshot_download("NomaDamas/KoJev-v0"))
model, collator, _ = load_checkpoint(root)
example = Example(
    state="오늘 날씨가 맑다.",
    questions=[
        Question(
            type=QuestionType.NOUL,
            instructions="긍정적인 내용이다.",
            options=["아니오", "예"],
            gold=1,
            meta={},
        )
    ],
    source="demo",
    split="dev",
)
print(model.decide(example, collator))
```

## Training (short)

- Backbone `skt/A.X-Encoder-base`, full finetune (backbone lr 2e-5, head lr 1e-3).
- Gold mix: 12 Korean HF sources, ~104k train states / ~311k questions. KoBEST held out.
- SFT 1 epoch × 3 seeds, then one continue-train epoch from seed 2. RLCD attempted, NO-GO; this file is SFT-only.
- Product run: `sft-full-seed2-ep2`, `diverged=false`.

## Honest numbers

In-domain gold-val overall **0.764** (majority 0.645). OOD rule-gold **0.416** (majority 0.482). KoBEST zero-shot is near chance. This is a fitted Korean gold encoder, not a general Korean Jev.

| split | acc |
|---|---:|
| gold-val | 0.764 |
| ood | 0.416 |
| kobest-boolq | 0.490 |
| kobest-copa | 0.475 |
| kobest-wic | 0.501 |
| kobest-hellaswag | 0.318 |
| kobest-sentineg | 0.505 |

Same 80-example slices vs OpenRouter `typesafe/jev-1.13`: Jev wins every KoBEST task by a wide margin; KoJev only competes on gold-val.

## Citation

```
@misc{kojev-v0,
  title={KoJev-v0},
  author={NomaDamas},
  year={2026},
  howpublished={\\url{https://huggingface.co/NomaDamas/KoJev-v0}},
}
```

Also cite [A.X Encoder-base](https://huggingface.co/skt/A.X-Encoder-base).
