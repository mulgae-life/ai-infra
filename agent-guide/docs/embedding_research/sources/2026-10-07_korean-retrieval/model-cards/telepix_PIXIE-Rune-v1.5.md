---
tags:
- sentence-transformers
- sentence-similarity
- dense-encoder
- dense
- feature-extraction
- retrieval
- multimodal
- multi-modal
- crossmodal
- cross-modal
- aerospace
- telepix
language:
- af
- ar
- az
- be
- bg
- bn
- ca
- ceb
- cs
- cy
- da
- de
- el
- en
- es
- et
- eu
- fa
- fi
- fr
- gl
- gu
- he
- hi
- hr
- ht
- hu
- hy
- id
- is
- it
- ja
- jv
- ka
- kk
- km
- kn
- ko
- ky
- lo
- lt
- lv
- mk
- ml
- mn
- mr
- ms
- my
- ne
- nl
- pa
- pl
- pt
- qu
- ro
- ru
- si
- sk
- sl
- so
- sq
- sr
- sv
- sw
- ta
- te
- th
- tl
- tr
- uk
- ur
- vi
- yo
- zh
pipeline_tag: feature-extraction
library_name: sentence-transformers
license: apache-2.0
---
<p align="center">
    <img src="https://cdn-uploads.huggingface.co/production/uploads/61d6f4a4d49065ee28a1ee7e/V8n2En7BlMNHoi1YXVv8Q.png" width="400"/>
<p>

# PIXIE-Rune-v1.5
**PIXIE-Rune-v1.5** is an encoder-based embedding model trained on Korean and English information retrieval dataset, 
developed by [TelePIX Co., Ltd](https://telepix.net/).
**PIXIE** stands for Tele**PIX** **I**ntelligent **E**mbedding, representing TelePIX’s high-performance embedding technology.
This model is specifically optimized for semantic retrieval tasks in Korean and English, and demonstrates strong performance in aerospace domain. Through extensive fine-tuning and domain-specific evaluation, PIXIE shows robust retrieval quality for real-world use cases such as document understanding, technical QA, and semantic search in aerospace and related high-precision fields.
It also performs competitively across a wide range of open-domain Korean and English retrieval benchmarks, making it a versatile foundation for multilingual semantic search systems.


## Model Description
- **Model Type:** Sentence Transformer
<!-- - **Base model:** [Unknown](https://huggingface.co/unknown) -->
- **Maximum Sequence Length:** 6144 tokens
- **Output Dimensionality:** 1024 dimensions
- **Similarity Function:** Cosine Similarity
- **Language:** Multilingual — optimized for high performance in Korean and English
- **Domain Specialization:** Aerospace Information Retrieval
- **License:** apache-2.0 

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'max_seq_length': 6144, 'do_lower_case': False}) with Transformer model: XLMRobertaModel 
  (1): Pooling({'word_embedding_dimension': 1024, 'pooling_mode_cls_token': True, 'pooling_mode_mean_tokens': False, 'pooling_mode_max_tokens': False, 'pooling_mode_mean_sqrt_len_tokens': False, 'pooling_mode_weightedmean_tokens': False, 'pooling_mode_lasttoken': False, 'include_prompt': True})
  (2): Normalize()
)
```

## Quality Benchmarks
**PIXIE-Rune-v1.5** is a multilingual embedding model specialized for Korean and English retrieval tasks. 
It delivers consistently strong performance across a diverse set of domain-specific and open-domain benchmarks in both languages, demonstrating its effectiveness in real-world semantic search applications.
The table below presents the retrieval performance of several embedding models evaluated on a variety of Korean and English benchmarks.
We report **Normalized Discounted Cumulative Gain (nDCG@10)** scores, which measure how well a ranked list of documents aligns with ground truth relevance. Higher values indicate better retrieval quality.  
  
All evaluations were conducted using the open-source **[Korean-MTEB-Retrieval-Evaluators](https://github.com/BM-K/Korean-MTEB-Retrieval-Evaluators)** codebase to ensure consistent dataset handling, indexing, retrieval, and nDCG@10 computation across models.

### Benchmark Overview and Dataset Descriptions
| Model Name | # params | STELLA (XL) | MTEB (ko) | RTEB (en) |
|------|:---:|:---:|:---:|:---:|
| telepix/PIXIE-Spell-v1.5-0.6B | 0.6B | 0.6731 | 0.7717 | 0.5923 |
| telepix/PIXIE-Spell-Preview-0.6B | 0.6B | 0.5364 | 0.7612 | 0.5722 |
| **telepix/PIXIE-Rune-v1.5** | **0.5B** | **0.6559** | **0.7651** | **0.5546** |
| telepix/PIXIE-Rune-v1.0 | 0.5B | 0.6345 | 0.7603 | 0.5439 |
| telepix/PIXIE-Rune-Preview | 0.5B | 0.6127 | 0.7698 | 0.4925 |
| | | | | |
| nvidia/llama-embed-nemotron-8b | 8B | 0.7181 | 0.7813 | 0.6968 |
| Qwen/Qwen3-Embedding-8B | 8B | 0.6154 | 0.7839 | 0.7372 |
| Snowflake/snowflake-arctic-embed-l-v2.0 | 0.5B | 0.5448 | 0.7390 | 0.5222 |
| BAAI/bge-m3 | 0.5B | 0.5056 | 0.7483 | 0.5104 |
| Qwen/Qwen3-Embedding-0.6B | 0.6B | 0.4707 | 0.7017 | 0.6521 |
| Octen/Octen-Embedding-0.6B | 0.6B | 0.4683 | 0.7057 | 0.7378 |
| Salesforce/SFR-Embedding-Mistral | 7B | 0.4579 | N/A | N/A |
| Alibaba-NLP/gte-multilingual-base | 0.3B | 0.4097 | 0.7084 | 0.5261 |
| intfloat/multilingual-e5-large-instruct | 0.6B | 0.2384 | 0.7050 | 0.5481 |
| jinaai/jina-embeddings-v3 | 0.5B | N/A | 0.7088 | N/A |
| openai/text-embedding-3-large | N/A | N/A | 0.6646 | 0.6174 |

To better interpret the evaluation results above, we briefly describe the characteristics and evaluation intent of each benchmark suite used in this comparison.
Each benchmark is designed to assess different aspects of retrieval capability, ranging from domain-specific technical understanding to open-domain and multilingual generalization.

#### STELLA
[STELLA](https://arxiv.org/abs/2601.03496) is an aerospace-domain Information Retrieval (IR) benchmark constructed from NASA Technical Reports Server (NTRS) documents. It is designed to evaluate both:

- **Lexical matching** ability (does the retriever benefit from exact technical terms? | TCQ)
- **Semantic matching** ability (can the retriever match concepts even when technical terms are not explicitly used? | TAQ).

STELLA provides **dual-type synthetic queries** and a **cross-lingual extension** for multilingual evaluation while keeping the corpus in English.

#### 6 Datasets of MTEB (Korean)
Descriptions of the benchmark datasets used for evaluation are as follows:
- **Ko-StrategyQA**  
  A Korean multi-hop open-domain question answering dataset designed for complex reasoning over multiple documents.
- **AutoRAGRetrieval**  
  A domain-diverse retrieval dataset covering finance, government, healthcare, legal, and e-commerce sectors.
- **MIRACLRetrieval**  
  A document retrieval benchmark built on Korean Wikipedia articles.
- **PublicHealthQA**  
  A retrieval dataset focused on medical and public health topics.
- **BelebeleRetrieval**  
  A dataset for retrieving relevant content from web and news articles in Korean.
- **MultiLongDocRetrieval**  
  A long-document retrieval benchmark based on Korean Wikipedia and mC4 corpus.

#### RTEB (English)
Retrieval Embedding Benchmark ([RTEB](https://huggingface.co/blog/rteb)), a new benchmark designed to reliably evaluate the retrieval accuracy of embedding models for real-world applications. Existing benchmarks struggle to measure true generalization, while RTEB addresses this with a hybrid strategy of open and private datasets. Its goal is simple: to create a fair, transparent, and application-focused standard for measuring how models perform on data they haven’t seen before.

  
## Direct Use (Semantic Search)

```python
from sentence_transformers import SentenceTransformer
  
# Load the model
model_name = 'telepix/PIXIE-Rune-v1.5'
model = SentenceTransformer(model_name)

# Define the queries and documents
queries = [
        "텔레픽스는 어떤 산업 분야에서 위성 데이터를 활용하나요?",
        "국방 분야에 어떤 위성 서비스가 제공되나요?",
        "텔레픽스의 기술 수준은 어느 정도인가요?",
]
documents = [
        "텔레픽스는 해양, 자원, 농업 등 다양한 분야에서 위성 데이터를 분석하여 서비스를 제공합니다.",
        "정찰 및 감시 목적의 위성 영상을 통해 국방 관련 정밀 분석 서비스를 제공합니다.",
        "TelePIX의 광학 탑재체 및 AI 분석 기술은 Global standard를 상회하는 수준으로 평가받고 있습니다.",
        "텔레픽스는 우주에서 수집한 정보를 분석하여 '우주 경제(Space Economy)'라는 새로운 가치를 창출하고 있습니다.",
        "텔레픽스는 위성 영상 획득부터 분석, 서비스 제공까지 전 주기를 아우르는 솔루션을 제공합니다.",
]

# Compute embeddings: use `prompt_name="query"` to encode queries!
query_embeddings = model.encode(queries, prompt_name="query")
document_embeddings = model.encode(documents)

# Compute cosine similarity scores
scores = model.similarity(query_embeddings, document_embeddings)

# Output the results
for query, query_scores in zip(queries, scores):
    doc_score_pairs = list(zip(documents, query_scores))
    doc_score_pairs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)
    print("Query:", query)
    for document, score in doc_score_pairs:
        print(score, document)

```

## License
The PIXIE-Rune-v1.5 model is licensed under Apache License 2.0.

## Citation
```
@misc{TelePIX-PIXIE-Rune-v1.5,
  title={PIXIE-Rune-v1.5},
  author={TelePIX AI Research Team and Bongmin Kim},
  year={2026},
  url={https://huggingface.co/telepix/PIXIE-Rune-v1.5}
}
```

## Contact

If you have any suggestions or questions about the PIXIE, please reach out to the authors at bmkim@telepix.net.