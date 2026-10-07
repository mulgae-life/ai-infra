---
language: en
license: apache-2.0
tags:
- legal
- embeddings
- retrieval
- sentence-transformers
- contract-analysis
- information-retrieval
base_model: BAAI/bge-base-en-v1.5
datasets:
- custom
metrics:
- recall
- precision
model-index:
- name: legal-embeddings-bge-base
  results:
  - task:
      type: text-retrieval
      name: Legal Document Retrieval (LODO Cross-Validation)
    dataset:
      name: LegalBench-RAG mini (held-out datasets)
      type: custom
    metrics:
    - type: recall_at_64
      value: 0.955
      name: Recall@64 (avg, held-out)
    - type: recall_at_16
      value: 0.798
      name: Recall@16 (avg, held-out)
---

# legal-embeddings-bge-base

A `BAAI/bge-base-en-v1.5` model fine-tuned on legal (query, passage) pairs from the [LegalBench-RAG](https://github.com/zeroentropy-ai/legalbenchrag) benchmark. Built for [LegalKit](https://github.com/legalkit/legalkit), an open-source legal AI platform.

## ⚠️ Honest Assessment

**This model does not meaningfully outperform the base BGE model on held-out legal data.** We are publishing it for reproducibility and transparency, not as a recommended improvement over the base model.

Our initial evaluation showed strong results (99% R@64), but this was evaluated on the same data distribution the model was trained on. A proper **leave-one-dataset-out (LODO) cross-validation** — training on 3 of 4 benchmark datasets and evaluating on the held-out 4th — tells a different story:

### LODO Cross-Validation Results (the fair comparison)

| Held-out Dataset | Fine-tuned R@64 | Base BGE R@64 | Δ |
|---|---|---|---|
| CUAD | 96.5% | 95.7% | +0.7pp |
| MAUD | 80.7% | 82.6% | **-1.9pp** |
| ContractNLI | 101.8% | 101.8% | +0.0pp |
| PrivacyQA | 103.2% | 103.2% | +0.0pp |
| **Average** | **95.5%** | **95.8%** | **-0.3pp** |

The fine-tuned model is within noise of the base model — and slightly *worse* on MAUD (M&A agreements). The high recall numbers (95%+) for both models are driven by our large paragraph-aware chunk size (~1500 chars), not embedding quality.

### What happened

The training data (9,409 pairs) was extracted directly from LegalBench-RAG ground-truth annotations. When we evaluated on LegalBench-RAG, we were testing in-distribution — the model had seen queries and documents from the same benchmark. The base `BAAI/bge-base-en-v1.5` model is already excellent on legal text, and our fine-tuning added dataset-specific patterns rather than generalizable legal domain knowledge.

### Recommendation

**For most use cases, use the base `BAAI/bge-base-en-v1.5` directly.** It performs equivalently on held-out legal datasets without the complexity of a custom model. Invest in retrieval architecture (hybrid semantic + BM25, cross-reference expansion, reranking) rather than embedding fine-tuning — that's where the real gains are.

## Previous Claims (Retracted)

Our earlier model card stated this model "beats text-embedding-3-large." That comparison was based on in-distribution evaluation and is not supported by held-out results. We retract that claim. We have not conducted a fair head-to-head comparison with text-embedding-3-large using held-out data.

## Model Description

A bi-encoder sentence embedding model that produces 768-dimensional dense embeddings. Fine-tuned with `MultipleNegativesRankingLoss` on legal (query, positive_passage, hard_negative) triples.

## Usage

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("epequeno/legal-embeddings-bge-base")

query = "What is the indemnification cap under this agreement?"
passage = "The aggregate liability of Seller under Section 8.1 shall not exceed Five Million Dollars ($5,000,000)."

query_emb = model.encode(query)
passage_emb = model.encode(passage)

score = np.dot(query_emb, passage_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(passage_emb))
print(f"Similarity: {score:.3f}")
```

## Training Details

| Parameter | Value |
|---|---|
| Base model | `BAAI/bge-base-en-v1.5` |
| Training examples | 9,409 (query, positive, hard_negative) triples |
| Validation examples | 1,045 |
| Loss | MultipleNegativesRankingLoss |
| Epochs | 3 |
| Batch size | 32 |
| Learning rate | 2e-5 |
| Max sequence length | 256 tokens |
| GPU | NVIDIA A10G |
| Training time | ~13 minutes |

### Training Data

Positive pairs extracted from [LegalBench-RAG](https://github.com/zeroentropy-ai/legalbenchrag) ground-truth span annotations across 4 datasets:

| Source | Pairs | Domain |
|---|---|---|
| CUAD | 6,189 | Commercial contracts (41 clause types) |
| MAUD | 2,456 | M&A merger agreements |
| ContractNLI | 1,360 | Non-disclosure agreements |
| PrivacyQA | 449 | Privacy policies |

Hard negatives were mined from the same documents (nearby non-overlapping spans).

## Limitations

- **Does not improve over the base model on held-out legal data** (see LODO results above)
- Optimized for US commercial contracts and privacy policies
- Max sequence length is 256 tokens
- Best used in hybrid retrieval (semantic + BM25), not semantic-only

## Related Resources

- [LegalKit](https://github.com/legalkit/legalkit) — open-source legal AI platform
- [legal-entailment-deberta-v3-large](https://huggingface.co/epequeno/legal-entailment-deberta-v3-large) — companion citation verification model
- [BAAI/bge-base-en-v1.5](https://huggingface.co/BAAI/bge-base-en-v1.5) — base model (recommended)
- [LegalBench-RAG](https://github.com/zeroentropy-ai/legalbenchrag) — training data source

## Citation

```bibtex
@software{legalkit2026,
  author = {Pequeno, Steven},
  title = {LegalKit: Open-Source Legal AI Platform},
  year = {2026},
  url = {https://github.com/legalkit/legalkit}
}
```
