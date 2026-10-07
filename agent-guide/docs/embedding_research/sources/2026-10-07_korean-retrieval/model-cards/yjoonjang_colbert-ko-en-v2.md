---
tags:
- ColBERT
- PyLate
- late-interaction
- multi-vector
- sentence-transformers
- sentence-similarity
- feature-extraction
language:
- ko
- en
base_model: skt/A.X-Encoder-base
pipeline_tag: sentence-similarity
library_name: PyLate
license: apache-2.0
---

# colbert-ko-en-v2

**colbert-ko-en-v2** is a Korean-English bilingual late-interaction (ColBERT) retriever built on
[skt/A.X-Encoder-base](https://huggingface.co/skt/A.X-Encoder-base). It encodes every token into a
128-dimensional vector and scores query–document pairs with MaxSim, keeping the term-level matching
signal that a single pooled vector discards.

At **149M parameters** it reaches an average nDCG@10 of **0.7984** across the nine MTEB(kor, v2)
retrieval tasks — the strongest late-interaction model on that suite, and in the same range as
single-vector models many times its size.

## Key Characteristics

- **Late interaction**: one 128-d vector per token, scored with MaxSim. No pooling.
- **Long documents**: up to 8,192 tokens, on ModernBERT's RoPE attention.
- **Compact**: 149M parameters.
- **No instruction prefixes**: queries and documents need no task instruction. Query expansion to
  64 tokens is handled by the model.

## Usage

```bash
pip install -U pylate
```

### Indexing documents

```python
from pylate import indexes, models, retrieve

model = models.ColBERT(model_name_or_path="yjoonjang/colbert-ko-en-v2")

index = indexes.PLAID(
    index_folder="pylate-index",
    index_name="index",
    override=True,
)

documents_ids = ["1", "2", "3"]
documents = [
    "세종대왕은 1443년에 훈민정음을 창제하고 1446년에 이를 반포하였다.",
    "김치는 배추나 무를 소금에 절인 뒤 고춧가루와 젓갈을 넣어 발효시킨 음식이다.",
    "한라산은 해발 1,947m로 남한에서 가장 높은 산이며 제주도 중앙에 자리한다.",
]

documents_embeddings = model.encode(
    documents,
    batch_size=32,
    is_query=False,
    show_progress_bar=True,
)

index.add_documents(
    documents_ids=documents_ids,
    documents_embeddings=documents_embeddings,
)
```

To reuse an existing index, instantiate it without `override`:

```python
index = indexes.PLAID(index_folder="pylate-index", index_name="index")
```

### Retrieving top-k documents

```python
retriever = retrieve.ColBERT(index=index)

queries_embeddings = model.encode(
    ["훈민정음은 언제 만들어졌나요?"],
    batch_size=32,
    is_query=True,
    show_progress_bar=True,
)

scores = retriever.retrieve(
    queries_embeddings=queries_embeddings,
    k=10,
)
```

### Reranking

To rerank a first-stage candidate list without building an index:

```python
from pylate import models, rank

model = models.ColBERT(model_name_or_path="yjoonjang/colbert-ko-en-v2")

queries = [
    "전기차 폐배터리는 어떻게 재활용하나요?",
    "겨울에 한라산을 오를 때 필요한 장비는?",
]
documents = [
    [
        "폐배터리에서 리튬과 코발트를 회수하는 습식 제련 공정이 상용화되고 있다.",
        "급속 충전기는 30분 내외로 배터리를 80%까지 충전할 수 있다.",
    ],
    [
        "겨울 한라산 산행에는 아이젠과 방한 장갑이 필수이며 입산 시간이 제한된다.",
        "제주 올레길은 해안을 따라 이어지는 27개 코스로 구성되어 있다.",
        "적설기에는 등산화에 스패츠를 착용해 눈이 들어가는 것을 막는 것이 좋다.",
    ],
]
documents_ids = [[1, 2], [1, 3, 2]]

queries_embeddings = model.encode(queries, is_query=True)
documents_embeddings = model.encode(documents, is_query=False)

reranked_documents = rank.rerank(
    documents_ids=documents_ids,
    queries_embeddings=queries_embeddings,
    documents_embeddings=documents_embeddings,
)
```

## Evaluation

nDCG@10 on the nine **MTEB(kor, v2)** retrieval tasks.

| Model | Params | Avg | AutoRAG | PubHealth | StrategyQA | LawIR | SQuAD | Belebele (ko-ko) | MrTidy | MLDR | MIRACL |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Late-Interaction Models** | | | | | | | | | | |
| **[yjoonjang/colbert-ko-en-v2](https://huggingface.co/yjoonjang/colbert-ko-en-v2)** | 149M | **0.8063** | 0.9686 | 0.8222 | 0.7940 | 0.7181 | 0.9846 | 0.9687 | 0.5783 | 0.6992 | 0.7230 |
| lightonai/mLateOn | 307M | 0.7906 | 0.9392 | 0.8061 | 0.7905 | 0.6431 | 0.9803 | 0.9608 | 0.5817 | 0.7005 | 0.7135 |
| perplexity-ai/pplx-embed-v1-late-0.6b | 596M | 0.7381 | 0.8557 | 0.8089 | 0.7973 | 0.7285 | 0.9696 | 0.9548 | 0.5400 | 0.2816 | 0.7064 |
| dragonkue/colbert-ko-0.1b | 149M | 0.6776 | 0.9700 | 0.7482 | 0.7364 | 0.4475 | 0.9794 | 0.9644 | 0.3966 | 0.2872 | 0.5685 |
| yjoonjang/colbert-ko-v1 | 149M | 0.6282 | 0.9557 | 0.6783 | 0.6560 | 0.4823 | 0.9594 | 0.9154 | 0.3279 | 0.2214 | 0.4575 |
| **Single-Vector Models** | | | | | | | | | | |
| sionic-ai/comsat-embed-ko-8b-preview | 7.6B | 0.7927 | 0.8518 | 0.8871 | 0.8394 | 0.8164 | 0.9168 | 0.9853 | 0.6253 | 0.5157 | 0.6964 |
| Qwen/Qwen3-Embedding-8B | 7.6B | 0.7826 | 0.8276 | 0.8721 | 0.8363 | 0.8171 | 0.9063 | 0.9824 | 0.6187 | 0.5046 | 0.6783 |
| Qwen/Qwen3-Embedding-4B | 4.0B | 0.7737 | 0.8431 | 0.8693 | 0.8270 | 0.7769 | 0.9044 | 0.9522 | 0.6076 | 0.5022 | 0.6803 |
| microsoft/harrier-oss-v1-27b | 27.0B | 0.7667 | 0.8176 | 0.8971 | 0.8361 | 0.8737 | 0.9204 | 0.9546 | 0.5306 | 0.4046 | 0.6653 |
| codefuse-ai/F2LLM-v2-8B | 7.6B | 0.7638 | 0.7678 | 0.9380 | 0.8371 | 0.8405 | 0.8874 | 0.9513 | 0.6162 | 0.4047 | 0.6313 |
| dragonkue/snowflake-arctic-embed-l-v2.0-ko | 568M | 0.7653 | 0.9093 | 0.8337 | 0.8050 | 0.7735 | 0.9447 | 0.9518 | 0.5712 | 0.4304 | 0.6685 |
| telepix/PIXIE-Rune-v1.5 | 568M | 0.7618 | 0.8927 | 0.8426 | 0.8064 | 0.7705 | 0.9457 | 0.9617 | 0.5492 | 0.4482 | 0.6393 |
| nlpai-lab/KURE-v1 | 568M | 0.7616 | 0.8708 | 0.8193 | 0.7999 | 0.7426 | 0.9357 | 0.9502 | 0.5909 | 0.4637 | 0.6816 |
| dragonkue/BGE-m3-ko | 568M | 0.7547 | 0.8738 | 0.8155 | 0.7959 | 0.7322 | 0.9414 | 0.9503 | 0.6099 | 0.3899 | 0.6833 |
| nlpai-lab/KoE5 | 560M | 0.7337 | 0.8434 | 0.8351 | 0.8001 | 0.7756 | 0.8980 | 0.9425 | 0.5841 | 0.3015 | 0.6235 |

Late-interaction rows were measured with `mteb` 2.18.16 and PLAID retrieval; single-vector rows are
taken from the official [MTEB results repository](https://github.com/embeddings-benchmark/results), except for Belebele using only Korean query, Korean corpus subset. 
The original version also includes cross-lingual subsets (Korean query - English corpus, English query - Korean corpus).

## Model Details

- **Model type**: ColBERT / PyLate
- **Base model**: [skt/A.X-Encoder-base](https://huggingface.co/skt/A.X-Encoder-base) — ModernBERT, 22 layers, 768 hidden
- **Parameters**: 149M
- **Output dimensionality**: 128 per token
- **Similarity function**: MaxSim
- **Document length**: 8,192 tokens
- **Query length**: 64 tokens (MASK expansion)
- **Languages**: Korean, English

```
ColBERT(
  (0): Transformer({'max_seq_length': 8191, 'do_lower_case': False, 'architecture': 'ModernBertModel'})
  (1): Dense({'in_features': 768, 'out_features': 128, 'bias': False, 'activation_function': 'torch.nn.modules.linear.Identity', 'use_residual': False})
)
```

## Citation

```bibtex
@misc{colbert-ko-en-v2,
  title  = {colbert-ko-en-v2: a Korean-English bilingual late-interaction retriever},
  author = {Jang, Yongjoon},
  year   = {2026},
  url    = {https://huggingface.co/yjoonjang/colbert-ko-en-v2},
}
```

```bibtex
@inproceedings{santhanam-etal-2022-colbertv2,
  title     = {ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction},
  author    = {Santhanam, Keshav and Khattab, Omar and Saad-Falcon, Jon and Potts, Christopher and Zaharia, Matei},
  booktitle = {Proceedings of the 2022 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies},
  year      = {2022},
  pages     = {3715--3734},
}
```

```bibtex
@misc{PyLate,
  title  = {PyLate: Flexible Training and Retrieval for Late Interaction Models},
  author = {Chaffin, Antoine and Sourty, Raphaël},
  year   = {2024},
  url    = {https://github.com/lightonai/pylate},
}
```
