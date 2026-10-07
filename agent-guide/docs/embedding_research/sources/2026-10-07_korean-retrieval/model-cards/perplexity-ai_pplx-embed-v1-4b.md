---
license: mit
pipeline_tag: feature-extraction
tags:
- feature-extraction
- sentence-similarity
- mteb
- sentence-transformers
language:
- multilingual
---


<p align="center">
  <img src="assets/logo.svg" alt="Perplexity Logo" width="400">
</p>

<p align="center">pplx-embed-v1: Diffusion-Pretrained Dense and Contextual Embeddings</p>

`pplx-embed-v1` and `pplx-embed-context-v1` are state-of-the-art text embedding models optimized for real-world, web-scale retrieval tasks.

- Use **`pplx-embed-v1`** for independent text embedding (queries, documents, semantic search)
- Use **`pplx-embed-context-v1`** for document chunks in RAG systems where surrounding context matters

> [!IMPORTANT]
> `pplx-embed-v1` and `pplx-embed-context-v1` natively produce *unnormalized* int8-quantized embeddings. Ensure that you compare them via *cosine similarity*.


![diag.png](assets/diag.png)

## Models

| Model | Dimensions | Context | MRL | Quantization | Instruction | Pooling |
|:-----:|:----------:|:-------:|:---:|:------------:|:-----------:|:-------:|
| `pplx-embed-v1-0.6B` | 1024 | 32K | Yes | INT8/BINARY | No | Mean |
| `pplx-embed-v1-4B` | 2560 | 32K | Yes | INT8/BINARY | No | Mean |
| `pplx-embed-context-v1-0.6B` | 1024 | 32K | Yes | INT8/BINARY | No | Mean |
| `pplx-embed-context-v1-4B` | 2560 | 32K | Yes | INT8/BINARY | No | Mean |

<sub>All models are built on diffusion continued pre-trained Qwen3 at Perplexity AI.</sub>

<sub>Many modern embedding models rely on instruction tuning, where users prepend an instruction string to the text being embedded. This can yield a 2%-3% lift on benchmarks, but it also introduces prompt-selection overhead and can make indexing pipelines brittle (small instruction changes can shift embedding space). We deliberately **avoid** this requirement: you can embed the text you want to index directly, without having to choose or maintain an instruction prefix.</sub>

## Usage

<details>
<summary>Via API</summary>

```bash
curl -X POST https://api.perplexity.ai/v1/embeddings \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": [
      "Scientists explore the universe driven by curiosity.",
      "Children learn through curious exploration.",
      "Historical discoveries began with curious questions.",
      "Animals use curiosity to adapt and survive.",
      "Philosophy examines the nature of curiosity."
    ],
    "model": "pplx-embed-v1-4b"
  }'
```

</details>


<details>
<summary>Using SentenceTransformers</summary>

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "perplexity-ai/pplx-embed-v1-4B",
    trust_remote_code=True
)

texts = [
    "Scientists explore the universe driven by curiosity.",
    "Children learn through curious exploration.",
    "Historical discoveries began with curious questions.",
    "Animals use curiosity to adapt and survive.",
    "Philosophy examines the nature of curiosity.",
]

embeddings = model.encode(texts) # Shape: (5, 2560), quantized to int8
embeddings = model.encode(texts, quantization="binary") # Shape: (5, 2560), quantized to binary
```

</details>

<details>
<summary> Using ONNX models </summary>

```python

import onnxruntime as ort
from transformers import AutoTokenizer
import numpy as np

tokenizer = AutoTokenizer.from_pretrained("perplexity-ai/pplx-embed-v1-4b", trust_remote_code=True)
session = ort.InferenceSession("onnx/model.onnx")


texts = [
    "Scientists explore the universe driven by curiosity.",
    "Children learn through curious exploration.",
    "Historical discoveries began with curious questions.",
    "Animals use curiosity to adapt and survive.",
    "Philosophy examines the nature of curiosity.",
]

tokenized = tokenizer(
    texts,
    padding=True,
    truncation=True,
    return_tensors="np"
)

onnx_inputs = {
    "input_ids": tokenized["input_ids"].astype(np.int64),
    "attention_mask": tokenized["attention_mask"].astype(np.int64),
}

# Run inference
onnx_embeddings = session.run([out.name for out in session.get_outputs()], onnx_inputs)

# ONNX produces both int8 and binary precision embeddings:
int8_embeddings = onnx_embeddings[2]
binary_embeddings = onnx_embeddings[3]
packed_embeddings = np.packbits(binary_embeddings != -1, axis=-1)
```

</details>

<details>
<summary>Using Text Embeddings Inference (TEI)</summary>

> [!NOTE]
> Text Embeddings Inference v1.9.2+ is required.

> [!IMPORTANT]
> Currently, only int8-quantized embeddings are available via TEI. Remember to use cosine similarity with unnormalized int8 embeddings.

- CPU w/ Candle:

```bash
docker run -p 8080:80 ghcr.io/huggingface/text-embeddings-inference:cpu-1.9 --model-id perplexity-ai/pplx-embed-v1-4B --dtype float32
```

- CPU w/ ORT (ONNX Runtime):

```bash
docker run -p 8080:80 ghcr.io/huggingface/text-embeddings-inference:cpu-1.9 --model-id onnx-community/pplx-embed-v1-4B --dtype float32
```

- GPU w/ CUDA:

```bash
docker run --gpus all --shm-size 1g -p 8080:80 ghcr.io/huggingface/text-embeddings-inference:cuda-1.9 --model-id perplexity-ai/pplx-embed-v1-4B --dtype float32
```

> If you hit OOM during warmup, lower --max-batch-tokens and --max-client-batch-size. Set --max-batch-tokens to max_sequence_length × batch_size (e.g., 2048 tokens × 8 sequences = 16384).

> Alternatively, when running in CUDA you can use the architecture / compute capability specific
> container instead of the `cuda-1.9`, as that includes the binaries for Turing, Ampere, Hopper and
> Blackwell, so using a dedicated container will be lighter e.g., `ampere-1.9`.

And then you can send requests to it via cURL to `/embed`:

```bash
curl http://0.0.0.0:8080/embed \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      "Scientists explore the universe driven by curiosity.",
      "Children learn through curious exploration.",
      "Historical discoveries began with curious questions.",
      "Animals use curiosity to adapt and survive.",
      "Philosophy examines the nature of curiosity."
    ],
    "normalize": false
  }'
```

</details>

## Technical Details

For comprehensive technical details and evaluation results, see our paper on arXiv: https://arxiv.org/abs/2602.11151.

