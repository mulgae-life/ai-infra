---
license: cc-by-nc-4.0
base_model: Qwen/Qwen3-Embedding-8B
base_model_relation: finetune
language:
- ko
- en
library_name: sentence-transformers
pipeline_tag: sentence-similarity
tags:
- sentence-transformers
- feature-extraction
- sentence-similarity
- mteb
- korean
- retrieval
---

<p align="center">
  <img src="assets/sionic_ai.png" alt="Sionic AI" width="480"/>
</p>

# comsat-embed-ko-8b-preview

**comsat-embed-ko-8b-preview** is a decoder-based embedding model developed by **Sionic AI**, optimized for Korean semantic retrieval tasks. Trained on **over 1M Korean examples**, it encodes queries and documents into vectors so that the most relevant documents can be found by similarity. The model is designed to provide high-quality text representations for real-world information retrieval scenarios, including document search, question answering, knowledge base retrieval, and enterprise semantic search. By leveraging Korean retrieval-oriented training data, comsat-embed-ko-8b-preview delivers robust performance across Korean search environments where accurate semantic matching is essential.

## Highlights

- **Korean-specialized** — trained on 1M+ Korean examples and tuned for Korean search; achieves **state-of-the-art average NDCG@10 (0.7930)** on the 9-subset MTEB Korean retrieval benchmark among the compared models.
- **Long context** — handles inputs up to 8,192 tokens, well suited to long-document retrieval.
- **Instruction-aware queries** — queries are encoded with a task-instruction prompt to improve retrieval quality; documents need no prefix.
- **High-dimensional embeddings** — 4096-dimensional, last-token pooled and L2-normalized, compared with cosine similarity.

## Usage

First install the Sentence Transformers library

```bash
pip install -U sentence-transformers
```

### Sentence Transformers Usage

> ⚠️ Queries **must** be encoded with the query prompt; documents are encoded **without** any prefix. (Skipping the query prompt slightly degrades retrieval quality.)

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sionic-ai/comsat-embed-ko-8b-preview")

queries  = ["한국의 수도는 어디인가?"]
passages = ["대한민국의 수도는 서울특별시이다."]

# Option 1) pass the query prompt explicitly (query only; documents get no prefix)
q_emb = model.encode(queries,  prompt_name="query", normalize_embeddings=True)
d_emb = model.encode(passages,                      normalize_embeddings=True)

# Option 2) sentence-transformers 5.x helper API (equivalent result)
# q_emb = model.encode_query(queries)
# d_emb = model.encode_document(passages)

scores = q_emb @ d_emb.T   # cosine similarity
print(scores)
```

### Transformers Usage

```python
# Requires transformers>=4.51.0

import torch
import torch.nn.functional as F

from torch import Tensor
from transformers import AutoTokenizer, AutoModel


def last_token_pool(last_hidden_states: Tensor,
                 attention_mask: Tensor) -> Tensor:
    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]


def get_detailed_instruct(task_description: str, query: str) -> str:
    return f'Instruct: {task_description}\nQuery:{query}'

# Each query must come with a one-sentence instruction that describes the task
task = 'Given a web search query, retrieve relevant passages that answer the query'

queries = [
    get_detailed_instruct(task, '한국의 수도는 어디인가?'),
    get_detailed_instruct(task, '광합성은 어떻게 일어나는가?')
]
# No need to add instruction for retrieval documents
documents = [
    "대한민국의 수도는 서울특별시이다.",
    "광합성은 식물이 빛 에너지를 이용해 이산화탄소와 물로 포도당을 합성하는 과정이다."
]
input_texts = queries + documents

tokenizer = AutoTokenizer.from_pretrained('sionic-ai/comsat-embed-ko-8b-preview', padding_side='left')
model = AutoModel.from_pretrained('sionic-ai/comsat-embed-ko-8b-preview')

# We recommend enabling flash_attention_2 for better acceleration and memory saving.
# model = AutoModel.from_pretrained('sionic-ai/comsat-embed-ko-8b-preview', attn_implementation="flash_attention_2", torch_dtype=torch.bfloat16).cuda()

max_length = 8192

# Tokenize the input texts
batch_dict = tokenizer(
    input_texts,
    padding=True,
    truncation=True,
    max_length=max_length,
    return_tensors="pt",
)
batch_dict.to(model.device)
outputs = model(**batch_dict)
embeddings = last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])

# normalize embeddings
embeddings = F.normalize(embeddings, p=2, dim=1)
scores = (embeddings[:2] @ embeddings[2:].T)
print(scores.tolist())
```

### Korean Retrieval Benchmark
- [LawIRKo](https://huggingface.co/datasets/on-and-on/lawgov_ir-ko): A **Korean legal-domain retrieval dataset** for finding statutes and precedents relevant to legal queries.
- [SQuADKorV1Retrieval](https://huggingface.co/datasets/yjoonjang/squad_kor_v1): A **Korean Wikipedia passage retrieval dataset** based on Korean SQuAD v1.
- [AutoRAGRetrieval](https://huggingface.co/datasets/yjoonjang/markers_bm): A **Korean document retrieval dataset** constructed by parsing PDFs from five domains: **finance, public, medical, legal, and commerce**.
- [Ko-StrategyQA](https://huggingface.co/datasets/taeminlee/Ko-StrategyQA): A Korean **ODQA multi-hop retrieval dataset**, translated from StrategyQA.
- [PublicHealthQA](https://huggingface.co/datasets/xhluca/publichealth-qa): A **retrieval dataset** focused on **medical and public health domains** in Korean.
- [BelebeleRetrieval](https://huggingface.co/datasets/mteb/belebele): A **Korean document retrieval dataset** based on FLORES-200.
- [MultiLongDocRetrieval](https://huggingface.co/datasets/mteb/MultiLongDocRetrieval): A **long-document retrieval dataset** covering various domains in Korean.
- [MIRACLRetrieval](https://huggingface.co/datasets/mteb/MIRACLRetrieval): A **Korean document retrieval dataset** based on Wikipedia.
- [MrTidyRetrieval](https://huggingface.co/datasets/mteb/mrtidy): A **Wikipedia-based Korean document retrieval dataset**.

## Performance (MTEB Korean Retrieval, NDCG@10)

All scores are NDCG@10 on the **full corpus**, measured with the standard MTEB evaluation pipeline. For multilingual tasks the Korean subset is used (MLDR=ko, MIRACL/MrTidy=ko, Belebele=kor-kor).

| Model | Avg | MIRACL | MrTidy | MLDR | AutoRAG | Ko-StrategyQA | PublicHealthQA | Belebele | SQuADKorV1 | LawIRKo |
|---|---|---|---|---|---|---|---|---|---|---|
| **comsat-embed-ko-8b-preview** | **0.7930** | 0.6964 | 0.6253 | 0.5183 | 0.8518 | 0.8394 | 0.8871 | 0.9853 | 0.9168 | 0.8164 |
| Qwen/Qwen3-Embedding-8B | 0.7825 | 0.6783 | 0.6187 | 0.5036 | 0.8276 | 0.8363 | 0.8721 | 0.9828 | 0.9063 | 0.8171 |
| Qwen/Qwen3-Embedding-4B | 0.7718 | 0.6803 | 0.6076 | 0.4895 | 0.8431 | 0.8270 | 0.8693 | 0.9479 | 0.9044 | 0.7769 |
| upstage/solar-embedding-1-large | 0.7674 | 0.6703 | 0.5766 | 0.3850 | 0.8833 | 0.8366 | 0.8787 | 0.9684 | 0.9521 | 0.7557 |
| microsoft/harrier-oss-v1-27b | 0.7669 | 0.6653 | 0.5306 | 0.4073 | 0.8176 | 0.8361 | 0.8971 | 0.9538 | 0.9204 | 0.8737 |
| dragonkue/snowflake-arctic-embed-l-v2.0-ko | 0.7636 | 0.6685 | 0.5712 | 0.4150 | 0.9093 | 0.8050 | 0.8337 | 0.9518 | 0.9447 | 0.7735 |
| codefuse-ai/F2LLM-v2-8B | 0.7621 | 0.6311 | 0.6162 | 0.3950 | 0.7678 | 0.8371 | 0.9332 | 0.9509 | 0.8874 | 0.8405 |
| nlpai-lab/KURE-v1 | 0.7603 | 0.6816 | 0.5909 | 0.4521 | 0.8708 | 0.7999 | 0.8193 | 0.9502 | 0.9357 | 0.7426 |
| telepix/PIXIE-Rune-v1.5 | 0.7602 | 0.6393 | 0.5492 | 0.4340 | 0.8927 | 0.8064 | 0.8426 | 0.9617 | 0.9457 | 0.7705 |
| nvidia/llama-nemotron-embed-vl-1b-v2 | 0.7579 | 0.6975 | 0.5998 | 0.3704 | 0.8773 | 0.8084 | 0.8223 | 0.9584 | 0.9360 | 0.7513 |
| dragonkue/BGE-m3-ko | 0.7534 | 0.6833 | 0.6099 | 0.3784 | 0.8738 | 0.7959 | 0.8155 | 0.9503 | 0.9414 | 0.7322 |
| BAAI/bge-m3 | 0.7508 | 0.7015 | 0.6471 | 0.4273 | 0.8301 | 0.7941 | 0.8041 | 0.9316 | 0.9038 | 0.7174 |
| intfloat/multilingual-e5-large | 0.7333 | 0.6649 | 0.6421 | 0.2708 | 0.8134 | 0.8035 | 0.8253 | 0.9450 | 0.9056 | 0.7293 |
| nlpai-lab/KoE5 | 0.7329 | 0.6235 | 0.5841 | 0.2942 | 0.8434 | 0.8001 | 0.8351 | 0.9425 | 0.8980 | 0.7756 |

> Avg is the mean over the 9 subsets (higher is better).
> Reproduction: evaluated with the MTEB retrieval pipeline (NDCG@10, full corpus); the query prompt is applied to queries only (documents get no prefix).

## License

- Model weights: **cc-by-nc-4.0** (non-commercial use).
