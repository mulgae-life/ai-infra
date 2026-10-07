---
license: gemma
base_model: google/embeddinggemma-300m
library_name: sentence-transformers
pipeline_tag: sentence-similarity
tags:
- sentence-transformers
- retrieval
- matryoshka
- insurance
---

# neuralchainai/embeddinggemma-300m-insuranceqa

A fully fine-tuned (not LoRA) **EmbeddingGemma** retriever for insurance question
answering. Base model: `google/embeddinggemma-300m`. Fine-tuned on
[`deccan-ai/insuranceQA-v2`](https://huggingface.co/datasets/deccan-ai/insuranceQA-v2) with
`MultipleNegativesRankingLoss` + `MatryoshkaLoss`.

## Before / after (test split, dim 768)

Retrieval is scored against a fixed **global unique-answer bank** (all splits deduped).

| Metric | Base | Fine-tuned | Δ |
|---|---|---|---|
| recall@1 | 0.2753 | 0.3181 | +0.0428 |
| recall@5 | 0.5031 | 0.5978 | +0.0946 |
| recall@10 | 0.6082 | 0.7108 | +0.1026 |
| recall@100 | 0.8774 | 0.9550 | +0.0776 |
| mrr@10 | 0.4747 | 0.5487 | +0.0740 |
| ndcg@10 | 0.4709 | 0.5532 | +0.0824 |

## Usage

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("neuralchainai/embeddinggemma-300m-insuranceqa")
q = model.encode_query(["How much does term life insurance cost?"])
d = model.encode_document(["Term life premiums depend on age, health, and coverage."])
```

## Prompts (asymmetric)

- query: `task: search result | query: `
- document: `title: none | text: `

## Matryoshka dimensions

[768, 512, 256, 128]

## Limitations

Evaluated against a fixed global answer bank; a test question's gold answer often also
appears among training answers (InsuranceQA reuses answers), so the headline numbers
reflect a shared train/prod bank. See the repo's unseen-answer subset for a
generalization-only view.

## License

Derivative of Google's EmbeddingGemma, distributed under the
[Gemma Terms of Use](https://ai.google.dev/gemma/terms). Use is subject to those terms.
