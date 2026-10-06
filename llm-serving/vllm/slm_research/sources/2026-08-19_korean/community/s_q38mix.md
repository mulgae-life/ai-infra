Title: Redlib: search results - qwen3.8 chinese language mixing

URL Source: https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all

Markdown Content:
[red lib.](https://redlib.catsarch.com/)

Feeds

MAIN FEEDS

[Home](https://redlib.catsarch.com/)[Popular](https://redlib.catsarch.com/r/popular)[All](https://redlib.catsarch.com/r/all)

[reddit](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#popup)

# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all)

[settings](https://redlib.catsarch.com/settings)

- [x] in r/LocalLLaMA 

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/Inevitable-Log5414](https://redlib.catsarch.com/u/Inevitable-Log5414)•May 14 '26

## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[Built an open-source one-prompt-to-cinematic-reel pipeline on a single GPU — FLUX.2 [klein] for character keyframes, Wan2.2-I2V for animation, vision critic with auto-retry, music + 9-language narration in the same pipeline](https://redlib.catsarch.com/r/LocalLLaMA/comments/1tcsqwk/built_an_opensource_oneprompttocinematicreel/)

[Video 3](about:blank)

 74  Upvotes

Shipped this for the AMD x lablab hackathon. Attached video is one of the actual reels the pipeline produced - one English sentence in, finished mp4 with characters, story, music, and voice-over out (fast demo video, not the best quality). ~45 minutes end-to-end on a single AMD Instinct MI300X. Every model is Apache 2.0 or MIT.

**Pipeline (8 stages, all sequential on the same GPU):**

1.   **Director Agent** - Qwen3.5-35B-A3B (vLLM + AITER MoE) plans 6 shots from one sentence, returns structured JSON with character bibles, shot prompts, music brief, per-shot voice-over script, narration language
2.   **Character masters** - FLUX.2 [klein] paints one canonical portrait per character. **No LoRA training step** - reference editing pins identity across shots by construction
3.   **Per-shot keyframes** - FLUX.2 again with reference image. Sub-second per keyframe after warmup
4.   **Animation** - Wan2.2-I2V-A14B, 81 frames @ 16 fps native. FLF2V for cut:false continuation arcs (last frame of shot N anchors first frame of shot N+1)
5.   **Vision critic** - same Qwen3.5-35B reloaded with 10 structured failure labels (character drift, extras invade frame, camera ignored, walking backwards, object morphing, hand/finger artifact, wardrobe drift, neon glow leak, stylized AI look, random intimacy). Bad clips re-render with targeted retry strategies (different seed, FLF2V anchor, prompt simplification)
6.   **Music** - ACE-Step v1 generates a 30s instrumental from Director's brief
7.   **Narration** - Kokoro-82M, 9 languages. Director picks language to match setting (Tokyo→Japanese, Paris→French, Mumbai→Hindi)
8.   **Mix** - ffmpeg with per-shot vo aligned via adelay

**Wan 2.2 specifics (the bit this sub will care about):** - 1280×720, **not** 640×640 default. Costs more but matches what producers want - 121 frames at 24 fps was my first attempt - gave temporal rippling. Switched to 81 @ 16 fps native (the distribution Wan was trained on) and it cleaned up - flow_shift = 5 for hero shots, 8 for b-roll (upstream wan_i2v_A14B.py defaults) - Negative prompt: **verbatim Chinese trained negative** from shared_config.py. umT5 was multilingual-pretrained against those exact tokens. English translation is observably weaker - Camera language: ONE camera verb per shot, sentence-case, placed first ("Tracking shot following from behind"). Multiple verbs in one prompt cancel each other out - Avoid the word "cinematic" - triggers Wan's stylization branch, gives the AI look. Use lens/film tags instead ("Arri Alexa, anamorphic, 35mm film grain")

**Performance work:** - ParaAttention FBCache (lossless 2× on Wan2.2) - torch.compile on transformer_2 (selective, the dual-expert MoE makes full compile flaky) - another 1.2× - AITER MoE acceleration on Qwen director (vLLM) - End-to-end: 25.9 min → 10.4 min per 720p clip on MI300X

**Why a single MI300X:** 192 GB HBM3 lets a 35B MoE, 4B diffusion, 14B I2V MoE, 3.5B music, and a TTS share the same card sequentially. Same stack on a 24 GB consumer GPU would need 4-5 boxes wired together.

**Code (public, Apache 2.0):**[https://github.com/bladedevoff/studiomi300](https://github.com/bladedevoff/studiomi300)

**Hugging Face (documentation, like this space 🙏)**[https://huggingface.co/spaces/lablab-ai-amd-developer-hackathon/studiomi300](https://huggingface.co/spaces/lablab-ai-amd-developer-hackathon/studiomi300)

Live demo on HF Space is temporarily offline while infra restores - should be back within hours. In the meantime the showcase reels in the repo are real pipeline outputs, no human re-edited shots.

Happy to dig into AITER MoE setup, FBCache tuning, FLF2V anchoring, or the vision critic's failure taxonomy in comments.

[24 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1tcsqwk/built_an_opensource_oneprompttocinematicreel/ "24 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/ex-arman68](https://redlib.catsarch.com/u/ex-arman68)•Jun 14 '26

## [Tutorial | Guide](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Tutorial%20|%20Guide%22&restrict_sr=on)[Which is the best local VLM? Benchmark results June 2026](https://redlib.catsarch.com/r/LocalLLaMA/comments/1u5oydc/which_is_the_best_local_vlm_benchmark_results/)

 0  Upvotes

> I am re-running the benchmark tests with a few differences: using latest llama.cpp instead of ollama. **-b 4096 -ub 4096** parameters to avoid splitting the image tokens into multiple blocks (default value is 512). Max image budget tokens for all gemma 4 models, with parameters **--image-min-tokens 560 --image-max-tokens 2240** (best values according to recent tests here on reddit; default is 280). Adding dense Gemma 4 31B and Qwen 3.6 27B. Once the results are in, and I have analysed them, I will create a new post. Some prelimary interesting findings: llama-server with the -b and -ub parameters seems 4-5x faster than ollama!

It all started because the LLM I use for coding does not have vision support. It relies on a cloud hosted MCP server for image analysis, which works well, but I keep hitting my monthly limit. So I have just started writing my own local MCP as a replacement, and the first step was finding which VLM to use.

I selected what I think are the best and latest current local VLM models, as of June 2026. If I am wrong, please let me know.

*   Gemma 4 12B
*   Gemma 4 26B-A4B (MoE)
*   Gemma 4 E4B (MoE)
*   GLM-4.6V-Flash 9B
*   InternVL3.5 8B
*   Qwen3-VL 4B
*   Qwen3-VL 8B
*   Qwen3.5 4B
*   Qwen3.5 9B
*   Qwen3.6 35B-A3B

I also wanted to include the following, but I did not manage to run them on my Mac:

*   Phi-4-reasoning-vision-15B (llama.cpp hasn't implemented the phi4-siglip vision architecture yet)
*   DeepSeek-VL2 (no working multimodal GGUF port, I would need vLLM)
*   InternVL3:8b-Q4_K_M (broken Modelfile with no multimodal projector declared)
*   Qwen3.5 27B and Qwen3.6 27B dense (skipped, too slow for the use case)

My initial assumption was that Gemma 4 12B would be the best model.

I prepared a test suite, with 20 varied images, in types, subject, file format; then a script to automatically load the models, run the queries and collect the results. Here is how the working models ranked.

# Performance

Sorted by median tokens per second, fastest first.

| Model | Arch | Disk size | Median tok/s | Median time/image | Median output tokens | Successful |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Qwen3-VL 4B** | Dense, 4B | 3.3 GB | **61** | 32 s | 1732 | 20/20 |
| **Qwen3.5 4B** | Dense, 4B (thinking) | 3.4 GB | 52 | 44 s | 1728 | 17/20 ⚠️ |
| **Qwen3.6 35B-A3B** | MoE, 3B active / 35B total | 23 GB | 50 | 39 s | 1470 | **20/20** |
| Qwen3-VL 8B | Dense, 8B | 6.1 GB | 43 | 46 s | 1429 | 20/20 |
| Qwen3.5 9B | Dense, 9B (thinking) | 6.6 GB | 38 | 59 s | 1691 | 16/20 ⚠️ |
| InternVL3.5 8B | Dense, 8B | 5.7 GB | 41 | 15 s | 394 | 20/20 |
| Gemma 4 E4B | MoE, ~4B active | 9.6 GB | 41 | 35 s | 1380 | 20/20 |
| Gemma 4 26B-A4B | MoE, 4B active / 26B total | 17 GB | 40 | 43 s | 1673 | 20/20 |
| GLM-4.6V-Flash 9B | Dense, 9B | 8.0 GB | 37 | 44 s | 1357 | 20/20 |
| **Gemma 4 12B** | Dense, 12B (encoder-free) | 7.6 GB | **21** | 69 s | 1508 | 20/20 |

Test conditions:

*   specs: Apple M2 Max, 96GB RAM
*   runtime: Ollama 0.30.8 with `OLLAMA_FLASH_ATTENTION=1 OLLAMA_KV_CACHE_TYPE=q8_0`
*   models Q4 GGUF (default tag), pulled from the official Ollama library where available, community ports otherwise
*   prompt: _"Describe this image in detail. Include: visible text (verbatim), objects, people, layout, colors, and any notable features. Use Markdown headings to organize your answer."_
*   temperature=0.1
*   timeout: 5 minutes per call (this matters — see below)

⚠️ = timeouts. The two Qwen 3.5 thinking models timed out on 3 and 4 images respectively. The Qwen 3.6 MoE flagship, also a thinking model, had zero timeouts. Qwen appears to have fixed the thinking-mode stability issues between 3.5 and 3.6.

# Quality ranking

Ranked by my subjective read of the 186 outputs. Here are the headline findings:

*   **Qwen3-VL 8B** is one of three models that correctly identified the right-hand emblem on a banner as _"hands holding a heart, surrounded by laurel leaves"_ and read both Chinese characters _少林寺_ and Latin text "SHAOLIN TEMPEL ÖSTERREICH".
*   **Qwen3.6 35B-A3B** and **Qwen3.5 9B** also got the banner emblem right.
*   **Gemma 4 26B-A4B** was the only model that produced a clean Markdown table unprompted when describing an architecture diagram, correctly identifying all 6 components and both protocols.
*   **GLM-4.6V-Flash 9B** and **Qwen3.6 35B-A3B** were the closest on the manga panel count — both said 12 (actual: 11). Every other model said 8 or 9, or timed out.
*   **Gemma 4 E4B** was wrong on two basic-facts tests: claimed 6 people in a photo of 5 (with a confident "four men and two women" breakdown), and claimed an album cover text appeared twice when it appears once.
*   **InternVL3.5 8B** thought a QR code was a _"black and white maze-like pattern"_ and also said 6 people for the photo of 5.
*   **Qwen3.5 4B** got the people-count right (5) but said "three men and two women" when it's actually two men and three women.

| Rank | Model | Quality | Clear strength | Weakness | Best for |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Qwen3-VL 8B** | Excellent | **OCR and fine detail.** Reads mixed-script text (Chinese + Latin) reliably. Caught the banner emblem detail. Correct on the 5-person headcount. Zero timeouts. | Verbose (1.4–2.2k tokens) — may be too much for token-cost-sensitive pipelines | **Detail extraction, OCR, and mixed-language content.** The default for a coding-assistant MCP. |
| 2 | **Qwen3.6 35B-A3B** | Excellent | **Reasoning over dense real-world content.** Chain-of-thought fully extracted a weekly schedule poster — every time slot, activity name, color-code, and the registration URL — and recognized fine emblem details (hands-heart-laurels). 50 tok/s on a 35B MoE. | 23 GB on disk; needs ≥32 GB RAM. Thinking output adds tokens you may not need. | **Users with ≥32 GB RAM who want the newest, most reliable thinking VLM.** Strong alternative to Qwen3-VL 8B if you have the memory. |
| 3 | **Gemma 4 26B-A4B** | Excellent | **Dense scenes and structured output.** Best on the busy music-catalog screenshot (3332 tokens of structured detail). Produces clean Markdown tables without being asked. Correct on people-count. | 17 GB on disk; needs ≥32 GB RAM to run comfortably. | **Complex screenshots — dashboards, IDE screenshots, dense UIs.** Worth the RAM when you need everything extracted. |
| 4 | **Qwen3-VL 4B** | Very good | **Speed/quality ratio.** Same family as 8B; quality close enough that you only notice on the hardest images. 3 GB on disk, 61 tok/s. | Hedged on the banner emblem ("symbolic imagery") where 8B committed. | **High-throughput pipelines, RAG embeddings, base-model Macs (≤16 GB RAM).** |
| 5 | **Qwen3.5 9B** | Very good | **Native vision at 9B.** Got the banner detail right. Correct on people-count. Polished output. | **4 timeouts out of 20** — thinking mode unstable on certain image types. Slower than Qwen3-VL 8B at the same accuracy tier. | **Skip in favor of Qwen3-VL 8B unless you specifically need native vision + thinking.** The 3.6 generation fixed the stability issues — use that instead. |
| 6 | **GLM-4.6V-Flash 9B** | Very good | **Panel-by-panel layout analysis.** Tied for closest on the manga panel count (12 vs actual 11). Best row-by-row breakdown of complex layouts. Polished prose. | Slower than Qwen3-VL equivalents at the same accuracy tier | **Comic / manga / multi-panel image analysis.** Also good for layout-heavy content where structure matters as much as content. |
| 7 | **Gemma 4 12B** | Very good | **Well-formatted, dependable descriptions.** Correct on the architecture diagram and the people-count. | 21 tok/s — slowest in the lineup, no category where it wins. Encoder-free architecture doesn't pay off here. | **Nothing specific.** It's competent everywhere and exceptional nowhere. Pick it only if you specifically need Apache 2.0 + encoder-free. |
| 8 | **Qwen3.5 4B** | Mixed | **Fast and usually right on counts.** Got the 5-person headcount correct. | **Invents gender splits.** Said "three men and two women" for a photo of two men and three women. 3 timeouts out of 20. Slower than Qwen3-VL 4B at the same size. | **Skip in favor of Qwen3-VL 4B** — same size, faster, more reliable, no thinking-mode timeouts. |
| 9 | **Gemma 4 E4B** | Mixed | **Fast MoE.** 41 tok/s with structured output. | **Invents details.** Wrong on the people-count (6 vs 5, with a confident-but-wrong gender breakdown). Wrong on the album text duplication (claimed it appeared twice). | **Avoid for any task where accuracy matters.** OK for fast first-pass summaries that you'll verify. |
| 10 | **InternVL3.5 8B** | Poor | **Terse summaries.** 4× shorter outputs than peers — perfect for cheap embeddings. | **Wrong on basic facts.** Called a QR code a _"maze-like pattern."_ Wrong on the people-count. Terseness correlates with missing detail. | **Brief image summaries for RAG indexing, where you'll re-rank with a text model.** Do not use for OCR or anything requiring accuracy. |

# Which model is best depending on the task

| Category | Winner | Why |
| :--- | :--- | :--- |
| OCR / mixed-script text | **Qwen3-VL 8B, Qwen3.5 9B, Qwen3.6 35B-A3B** (tie) | All three correctly read the Chinese + Latin banner and identified the hands-heart-laurels emblem. Qwen3-VL 8B is the smallest of the three. |
| Dense / busy screenshots | **Gemma 4 26B-A4B** | 3332 tokens on the OneRPM catalog vs ~2000 for everyone else. |
| Speed | **Qwen3-VL 4B** | 61 tok/s, ~2× the next-fastest reliable model. |
| Multi-panel layout analysis | **GLM-4.6V-Flash 9B and Qwen3.6 35B-A3B** (tie) | Both said 12 panels on the manga page (actual: 11); best row-by-row structure. |
| Code extraction | **Tie (all 10)** | Every model that completed the test extracted the Python snippet verbatim with correct indentation. Use whichever is fastest. |
| Diagrams / architecture | **Tie (7 of 10)** | Most models identified all 6 components. Gemma 4 E4B hedged; InternVL3.5 was terse; Qwen3.5 4B/9B timed out before getting there. |

# Recommendation

**Qwen3-VL 8B** is the best single model to use for everything.

It's not the only model that aces the OCR/detail test (Qwen3.6 35B-A3B and Qwen3.5 9B now tie it), but it remains the best combination of small (6 GB), fast (43 tok/s), accurate, and reliable (zero timeouts, no thinking-mode instability). Qwen3.6 35B-A3B is excellent but it's 23 GB on disk and requires more RAM.

# By hardware specs

| Specs | Primary pick | Notes |
| :--- | :--- | :--- |
| **8–16 GB RAM** (M1 / M2 base, Intel Macs) | **Qwen3-VL 4B** | 3 GB on disk, 61 tok/s, quality close to 8B. The only model in the lineup that runs comfortably on a base-model Mac. |
| **16–32 GB RAM** (M1/M2 Pro, M2 Air 24 GB) | **Qwen3-VL 8B** | The default. Pairs well with a coding LLM running alongside. |
| **32 GB+ RAM** (M Max, M Pro mid-tier) | **Qwen3-VL 8B + Gemma 4 26B-A4B**, or **Qwen3.6 35B-A3B** as a single-model alternative | 8B for everyday lookups; 26B-A4B when you need every detail extracted from a dense screenshot. Or replace both with Qwen3.6 35B-A3B if you'd rather maintain one model. |

[27 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1u5oydc/which_is_the_best_local_vlm_benchmark_results/ "27 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/Moreh](https://redlib.catsarch.com/u/Moreh)•Mar 10 '26

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[gpt oss 120b or qwen 3.5 for non-english/chinese/russian language](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rpqy9z/gpt_oss_120b_or_qwen_35_for/)

 3  Upvotes

**Edit for clarity:** I'm asking about performance on **non-major** languages — specifically Indonesian. My data is mixed English/Indonesian.

Hi all,

I'm planning some batch text analysis on ~30k rows of short strings in mixed English and Indonesian. I'd prefer a smarter model even if it's slower.

The obvious open-source choices seem to be Qwen 3.5, GLM, and GPT OSS 120B. GPT OSS looks slightly faster so I'm leaning that way, but does anyone have experience with how these models compare on Indonesian language tasks specifically?

Thanks for any input

[7 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rpqy9z/gpt_oss_120b_or_qwen_35_for/ "7 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/hi_im_ryanli](https://redlib.catsarch.com/u/hi_im_ryanli)•Feb 05 '25

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[Rant about Language Mixing in <think> ... </think>](https://redlib.catsarch.com/r/LocalLLaMA/comments/1iioooo/rant_about_language_mixing_in_think_think/)

 25  Upvotes

Just finished reading the Deepseek R1 paper - in section 2.3.2, they talked about their mitigation strategies against language mixing, which included CoT cold start and a new reward for language consistency.

I totally understand why they might want to encourage language consistency - better alignment with human preference and such, but I speak 4-ish languages (English (native), Chinese (native), Chinese regional dialet (native), Japanese (conversational)) and my thought processes are usually in mixed languages.

As I learned math at a young age in Chinese, before moving to the States, and studing STEM in English, my "internal reasoning" on lots of STEM-related questions are in a mixture of English and Chinese. I usually found myself reasoning better when this way.

Considering pretraining usually happens in mixed language anyways, it feels a bit odd that the research community decided against language mixing altogether, especially the paper also called out that this comes with a sligh performance degradation.

Thanks for reading my rant.

[15 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1iioooo/rant_about_language_mixing_in_think_think/ "15 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/Reddactor](https://redlib.catsarch.com/u/Reddactor)•Mar 23 '26

## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[RYS II - Repeated layers with Qwen3.5 27B and some hints at a 'Universal Language'](https://redlib.catsarch.com/r/LocalLLaMA/comments/1s1t5ot/rys_ii_repeated_layers_with_qwen35_27b_and_some/)

[![Image 1: Thumbnail](https://redlib.catsarch.com/preview/pre/8ycc38gnvuqg1.png?width=140&height=120&auto=webp&s=18ed61da18557528bf3a550023559c8e8346cd0a) gallery](https://redlib.catsarch.com/r/LocalLLaMA/comments/1s1t5ot/rys_ii_repeated_layers_with_qwen35_27b_and_some/)

 587  Upvotes

So, I've had my H100s grind for you all, and have some interesting new results AND fresh models!

So, what did I find? Well because my blog article are too damn long (_I know some of you are not reading the whole thing..._), here is a **TL;DR**:

1.   I found that LLMs seem to _think in a universal language_. During the middle layers, the models latent representations are more similar on the same content in Chinese and English than different content in the same language.
2.   I tried a bunch of different stuff, but in the end, repeating blocks in the middle of the transformer stack works the best.
3.   You should still read the blog: [https://dnhkng.github.io/posts/rys-ii/](https://dnhkng.github.io/posts/rys-ii/)

If you still didnt read the blog, well, I guess you can just try the models?

[https://huggingface.co/dnhkng/RYS-Qwen3.5-27B-FP8-S](https://huggingface.co/dnhkng/RYS-Qwen3.5-27B-FP8-S)

[https://huggingface.co/dnhkng/RYS-Qwen3.5-27B-FP8-M](https://huggingface.co/dnhkng/RYS-Qwen3.5-27B-FP8-M)

[https://huggingface.co/dnhkng/RYS-Qwen3.5-27B-FP8-L](https://huggingface.co/dnhkng/RYS-Qwen3.5-27B-FP8-L)

[https://huggingface.co/dnhkng/RYS-Qwen3.5-27B-FP8-XL](https://huggingface.co/dnhkng/RYS-Qwen3.5-27B-FP8-XL)

Wen GGUF? _When someone GGUF's them I guess?_

When you repeat layers, you benefit a lot from fine tuning. I expect the first team to fine tune RYS-Qwen3.5-27B-FP8-XL will have a new SOTA for that size range. Lastly, Ive been chatting with TurboDerp; hopefully we can get this into a new format where you can keep the duplicated later as copies, and not use more VRAM (except for the KV cache). S**_tay tuned!_**

[108 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1s1t5ot/rys_ii_repeated_layers_with_qwen35_27b_and_some/ "108 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/jacek2023](https://redlib.catsarch.com/u/jacek2023)•Sep 22 '25

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[3 Qwen3-Omni models have been released](https://redlib.catsarch.com/r/LocalLLaMA/comments/1nnt1bw/3_qwen3omni_models_have_been_released/)

 652  Upvotes

[https://huggingface.co/Qwen/Qwen3-Omni-30B-A3B-Captioner](https://huggingface.co/Qwen/Qwen3-Omni-30B-A3B-Captioner)

[https://huggingface.co/Qwen/Qwen3-Omni-30B-A3B-Thinking](https://huggingface.co/Qwen/Qwen3-Omni-30B-A3B-Thinking)

[https://huggingface.co/Qwen/Qwen3-Omni-30B-A3B-Instruct](https://huggingface.co/Qwen/Qwen3-Omni-30B-A3B-Instruct)

Qwen3-Omni is the natively end-to-end multilingual omni-modal foundation models. It processes text, images, audio, and video, and delivers real-time streaming responses in both text and natural speech. We introduce several architectural upgrades to improve performance and efficiency. Key features:

*   **State-of-the-art across modalities**: Early text-first pretraining and mixed multimodal training provide native multimodal support. While achieving strong audio and audio-video results, unimodal text and image performance does not regress. Reaches SOTA on 22 of 36 audio/video benchmarks and open-source SOTA on 32 of 36; ASR, audio understanding, and voice conversation performance is comparable to Gemini 2.5 Pro.
*   **Multilingual**: Supports 119 text languages, 19 speech input languages, and 10 speech output languages. 
    *   **Speech Input**: English, Chinese, Korean, Japanese, German, Russian, Italian, French, Spanish, Portuguese, Malay, Dutch, Indonesian, Turkish, Vietnamese, Cantonese, Arabic, Urdu.
    *   **Speech Output**: English, Chinese, French, German, Russian, Italian, Spanish, Portuguese, Japanese, Korean.

*   **Novel Architecture**: MoE-based Thinker–Talker design with AuT pretraining for strong general representations, plus a multi-codebook design that drives latency to a minimum.
*   **Real-time Audio/Video Interaction**: Low-latency streaming with natural turn-taking and immediate text or speech responses.
*   **Flexible Control**: Customize behavior via system prompts for fine-grained control and easy adaptation.
*   **Detailed Audio Captioner**: Qwen3-Omni-30B-A3B-Captioner is now open source: a general-purpose, highly detailed, low-hallucination audio captioning model that fills a critical gap in the open-source community.

Below is the description of all Qwen3-Omni models. Please select and download the model that fits your needs.

| Model Name | Description |
| :--- | :--- |
| Qwen3-Omni-30B-A3B-Instruct | The Instruct model of Qwen3-Omni-30B-A3B, containing both thinker and talker, supporting audio, video, and text input, with audio and text output. For more information, please read the [Qwen3-Omni Technical Report](https://github.com/QwenLM/Qwen3-Omni/blob/main/assets/Qwen3_Omni.pdf). |
| Qwen3-Omni-30B-A3B-Thinking | The Thinking model of Qwen3-Omni-30B-A3B, containing the thinker component, equipped with chain-of-thought reasoning, supporting audio, video, and text input, with text output. For more information, please read the [Qwen3-Omni Technical Report](https://github.com/QwenLM/Qwen3-Omni/blob/main/assets/Qwen3_Omni.pdf). |
| Qwen3-Omni-30B-A3B-Captioner | A downstream audio fine-grained caption model fine-tuned from Qwen3-Omni-30B-A3B-Instruct, which produces detailed, low-hallucination captions for arbitrary audio inputs. It contains the thinker, supporting audio input and text output. For more information, you can refer to the model's [cookbook](https://github.com/QwenLM/Qwen3-Omni/blob/main/cookbooks/omni_captioner.ipynb). |

[121 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1nnt1bw/3_qwen3omni_models_have_been_released/ "121 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/jacek2023](https://redlib.catsarch.com/u/jacek2023)•Dec 08 '25

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[GLM-4.6V (108B) has been released](https://redlib.catsarch.com/r/LocalLLaMA/comments/1phaaon/glm46v_108b_has_been_released/)

 393  Upvotes

[![Image 2](https://redlib.catsarch.com/preview/pre/dyfhb6nhwy5g1.jpg?width=10101&format=pjpg&auto=webp&s=d03177e251a72b04491b10634e66bdde1a9544c5)](https://redlib.catsarch.com/preview/pre/dyfhb6nhwy5g1.jpg?width=10101&format=pjpg&auto=webp&s=d03177e251a72b04491b10634e66bdde1a9544c5)
GLM-4.6V series model includes two versions: GLM-4.6V (106B), a foundation model designed for cloud and high-performance cluster scenarios, and GLM-4.6V-Flash (9B), a lightweight model optimized for local deployment and low-latency applications. GLM-4.6V scales its context window to 128k tokens in training, and achieves SoTA performance in visual understanding among models of similar parameter scales. Crucially, we integrate native Function Calling capabilities for the first time. This effectively bridges the gap between "visual perception" and "executable action" providing a unified technical foundation for multimodal agents in real-world business scenarios.

Beyond achieves SoTA performance across major multimodal benchmarks at comparable model scales. GLM-4.6V introduces several key features:

*   **Native Multimodal Function Calling** Enables native vision-driven tool use. Images, screenshots, and document pages can be passed directly as tool inputs without text conversion, while visual outputs (charts, search images, rendered pages) are interpreted and integrated into the reasoning chain. This closes the loop from perception to understanding to execution.
*   **Interleaved Image-Text Content Generation** Supports high-quality mixed media creation from complex multimodal inputs. GLM-4.6V takes a multimodal context—spanning documents, user inputs, and tool-retrieved images—and synthesizes coherent, interleaved image-text content tailored to the task. During generation it can actively call search and retrieval tools to gather and curate additional text and visuals, producing rich, visually grounded content.
*   **Multimodal Document Understanding** GLM-4.6V can process up to 128K tokens of multi-document or long-document input, directly interpreting richly formatted pages as images. It understands text, layout, charts, tables, and figures jointly, enabling accurate comprehension of complex, image-heavy documents without requiring prior conversion to plain text.
*   **Frontend Replication & Visual Editing** Reconstructs pixel-accurate HTML/CSS from UI screenshots and supports natural-language-driven edits. It detects layout, components, and styles visually, generates clean code, and applies iterative visual modifications through simple user instructions.

[https://huggingface.co/zai-org/GLM-4.6V](https://huggingface.co/zai-org/GLM-4.6V)

please notice that llama.cpp support for GLM 4.5V is still draft

[https://github.com/ggml-org/llama.cpp/pull/16600](https://github.com/ggml-org/llama.cpp/pull/16600)

[76 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1phaaon/glm46v_108b_has_been_released/ "76 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/returnity](https://redlib.catsarch.com/u/returnity)•14d ago

## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[DeepSeek v4 Flash vs. Qwen3.6-27B, 3.5-122B, and Gemma 4 31B Benchmark](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/)

[![Image 3: Thumbnail](https://redlib.catsarch.com/preview/pre/xucnql0lcehh1.png?width=140&height=45&auto=webp&s=ba4a99fb597610c9ecf4c11489b47d2238e306ec) gallery](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/)

 31  Upvotes

**EDIT:** To make this clear, this benchmark was done to see the capabilities of models that can be run on my (and many others here) 128GB RAM system. It's NOT intended as a comparison of the absolute capabilities of the models. Read the Setup section for specifics -- this is for people wondering what is the smartest model they can run LOCALLY -- still DSv4 Flash, even quantized. PLEASE read the Setup section and the Notes before commenting critically. Kinda shocked by the hate for a test of what people can actually run locally in a LOCAL LLM subreddit... =/

Just wanted to share my local (not API) agentic coding benchmark run of DSv4F 0731 at both High and Low reasoning efforts (not Max)... I ran a 109-question subset of Aider Polyglot (the JS/C++/Python languages), based on the coding that I do most often. This benchmark measures file-editing and diffs in a harness, and gives the model two tries to accomplish the task -- one try blind, then if it fails, it gets another shot after seeing the results of its first attempt.

I tracked first try pass rate, second try pass rate, well-formed diffs, # malformed, # of context overflows (60k token limit) and timeouts (1-hour limit including retry) [first image]. I also tracked cost, based on seconds/case, prompt tokens, completion tokens, prefill and decode tokens, and kilotokens/solved question [second image] Finally, I broke down the success rate by language for each model [3rd image].

Overall, as expected, Flash on High was the overall winner. However, it wasn't that far ahead, and it outspent the next-best 122B over 5X in tokens to get there. Also, the Qwen models solved a LOT more of the cases on their first try than DS4, which is a surprising find. Overall, I was shocked how well 122B performed. I used the excellent ThinkingCap fine-tune of 27B because I didn't want to die of old age before base 27B finished the benchmark -- in previous coding and knowledge benchmark runs I did to choose my daily driver, 27B and ThinkingCap always performed within the statistical margin of error of each other, but ThinkingCap completed the same task using 20-30% of the total tokens. I highly recommend trying it out if you feel like 27B overthinks excessively. Or, if you can fit it, just run 122B -- it consistently overdelivers in all my testing.

Setup: M5 Max 128GB

*   DeepSeek v4 Flash: antirez mixed Q4-Q2 imatrix, Dwarfstar inference engine.
*   Qwen3.5-122B: Unsloth Q5_K_XL, llama.cpp [n=4]
*   Qwen3.6-27B-ThinkingCap: Unsloth Q8_0, llama.cpp [n=4]
*   Gemma4-31B-QAT: Unsloth Q4_K_XL (QAT uncompressed) [n=4]

**Notes:**

1.   I ran both High and Low reasoning modes in DSv4 because of a [quirk in the way reasoning effort is sent in the current build of Dwarfstar](https://github.com/antirez/ds4/pull/686), the inference engine I use for DSv4. Basically, Deepseek changed the encoding of reasoning effort between preview and 0731, so the string used to trigger Max effort on preview now triggers High effort on 0731, a new string triggers Max, and if no string is passed, instead of defaulting to High 0731 defaults to Low effort. There is currently no way to call Max effort in Dwarfstar without editing the code, and after seeing the token use of Low/High, I decided I wasn't likely to use Max in actual use anyways, so I didn't make the edits required to do a Max run. I'd already burnt several days of GPU time on this anyways...
2.   The JS/C++/Python set of Aider Polyglot is 109 questions, not 107. However, 2 questions triggered a linter bug in several runs before I caught it, resulting in uncontrolled generation as the linter fed back an empty error message. DS4F in particular generated 60k tokens trying to find a non-existent error, which is what led me to catch the issue, as I thought the run was hung. Out of fairness, I have excluded these 2 questions from all the metrics.
3.   For the llama.cpp models, I ran n=4 (4 simultaneous threads). Tok/sec speeds are for ONE of 4 simultenous threads, so multiply by 2.5x for comparable single-stream speeds to compare with DSv4. This allowed me to complete the benchmarks ~2.5x as fast. Dwarfstar doesn't allow this, so in the interest of fairness, I measured both aggregate decode and single-stream decode for each model on the same prompt/output, then scaled wall clock time by that proportion to ensure the numbers are comparable, and 2.5x is the conversion. I just forgot to scale the decode column. Sorry!

Please share any benchmarks or comparisons you've done!

EDIT: YES, there is Low reasoning mode in 0731 (not preview): [https://www.reddit.com/r/LocalLLaMA/comments/1vdqsod/deepseekv4flash0731_when_low_is_higher_than_high/](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vdqsod/deepseekv4flash0731_when_low_is_higher_than_high/)

[76 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/ "76 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/dsdt](https://redlib.catsarch.com/u/dsdt)•Jul 07 '26

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[Laravel dev running Qwen 3.6 35B A3B—do we really need all these languages?](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/)

 6  Upvotes

I run **Qwen3.6-35B-A3B** daily for Laravel + Vue full-stack work, and it genuinely bugs me that a 20GB+ model spends weights on French, Chinese, Spanish—languages I will never prompt in.

My variables are `$user`, `$product`, `$order`. Laravel errors, Vue docs, PHP RFCs—all English. Every parameter spent on Mandarin fluency is a parameter not spent on Laravel 11 syntax, Vue 3 Composition API edge cases, or PHP 8.3 behavior. Yet the model can discuss Chinese poetry and still tell me `php artisan serve` defaults to port 8080 (it's 8000).

Yes, it's MoE—only ~3B active. But the dense **Qwen3.6-27B** has no such luxury. No sparse routing, no free lunch: it needs the full ~16-20GB loaded, multilingual weights included. That locks out anyone on a single 3060 12GB, 4060 8GB, or older card from running a genuinely strong local coding model—not because the reasoning capacity isn't there, but because a chunk of it is spent on languages they'll never use.

**Two questions:**

1.   Will we see English+code-only models trained from scratch? Zero multilingual data, all budget into English technical text and code.
2.   Can existing models be pruned post-hoc? Is there a way to strip non-English weights from something like **Qwen** or **Gemma** after training—not just quantize, but actually remove the multilingual capacity and reclaim the VRAM? A pruned Qwen-27B that fits in 10GB instead of 18GB would put real coding models within reach of a 3060 12GB, and a quantized version within reach of an 8GB card.

I'd trade a chunk of general multilingual reasoning for better Laravel/Vue accuracy and half the VRAM footprint. Is that technically feasible, or are we stuck with bloated dense models for the foreseeable future?

Edit : for those who say multilingualism help reasoning or coding please check this out : [https://ar5iv.labs.arxiv.org/html/2509.24405](https://ar5iv.labs.arxiv.org/html/2509.24405)

Summary : State-of-the-art reasoning models like DeepSeek-R1 and OpenAI o1 only reach about 4% execution accuracy relying on their own intrinsic reasoning, compared to roughly 60% on the earlier, easier MultiSpider 1.0. That's a massive difficulty jump

[77 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ "77 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/Fun_Dragonfruit_4613](https://redlib.catsarch.com/u/Fun_Dragonfruit_4613)•Jan 22 '25

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[R1-Zero: Pure RL Creates a Mind We Can’t Decode—Is This AGI’s Dark Mirror?](https://redlib.catsarch.com/r/LocalLLaMA/comments/1i765q0/r1zero_pure_rl_creates_a_mind_we_cant_decodeis/)

 304  Upvotes

The AI world is losing its mind over DeepSeek-R1-Zero, a model that skipped supervised fine-tuning (SFT) entirely and learned purely through reinforcement learning (RL). Unlike its sibling R1—which uses **some** SFT data to stay "human-readable"—R1-Zero’s training mirrors AlphaZero’s trial-and-error self-play. The result? **Jaw-dropping performance** (AIME math scores jumped from 15.6% → 86.7%) paired with **bizarre, uninterpretable reasoning**. Researchers observed "aha moments" where it autonomously rechecked flawed logic mid-process and allocated more compute to harder problems—**without human guidance**. But here’s the kicker: its outputs are riddled with garbled language mixes (e.g., Chinese/English spaghetti code) and logic leaps that even its creators can’t fully explain.

Meanwhile, R1 (the SFT-hybrid version) achieves similar performance **without the chaos**, proving that human-curated data still tames the beast. But at what cost? R1-Zero’s pure RL approach hints at a terrifying possibility: **minds that optimize truth beyond human comprehension**. And with API costs 50x cheaper than OpenAI’s, scaling this could democratize superintelligence—or unleash unreadable black-box AI.

If R1-Zero’s "alien logic" solves problems we can’t, does readability even matter… or is this how alignment dies?

[127 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1i765q0/r1zero_pure_rl_creates_a_mind_we_cant_decodeis/ "127 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/ButtercupLyn100](https://redlib.catsarch.com/u/ButtercupLyn100)•8d ago

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[I gave DeepSeek V4 Flash basic vision by training a 40M connector on 100K examples](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vl6ior/i_gave_deepseek_v4_flash_basic_vision_by_training/)

[![Image 4: Thumbnail](https://redlib.catsarch.com/preview/pre/9qnqst7s0oih1.png?width=140&height=78&auto=webp&s=c4fa78060fbd2646fc7d62088472ccc8170d4139) gallery](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vl6ior/i_gave_deepseek_v4_flash_basic_vision_by_training/)

 186  Upvotes

I wanted to find out whether a huge text-only MoE could be given basic vision without retraining the language model itself.

The short answer is yes.

I froze DeepSeek V4 Flash and a 417M-parameter MoonViT image encoder, then trained a 40.1M-parameter connector between them on 100,000 image-text examples.

The completed NVFP4 model loaded across four B200s in a custom SGLang stack and answered real image prompts. It has basic vision, although this 100K-example pilot is not yet a production-quality VLM.

# Models and weights

DeepSeek V4 Flash Vision NVFP4:

[https://huggingface.co/webbrain-one/DeepSeek-V4-Flash-Vision-NVFP4](https://huggingface.co/webbrain-one/DeepSeek-V4-Flash-Vision-NVFP4)

BF16 vision tower and connector:

[https://huggingface.co/webbrain-one/DeepSeek-V4-Flash-Vision-BF16](https://huggingface.co/webbrain-one/DeepSeek-V4-Flash-Vision-BF16)

DeepSeek V4 Flash 0731 Vision NVFP4:

[https://huggingface.co/webbrain-one/DeepSeek-V4-Flash-0731-Vision-NVFP4](https://huggingface.co/webbrain-one/DeepSeek-V4-Flash-0731-Vision-NVFP4)

Laguna XS 2.1 Vision NVFP4:

[https://huggingface.co/webbrain-one/Laguna-XS-2.1-Vision-NVFP4](https://huggingface.co/webbrain-one/Laguna-XS-2.1-Vision-NVFP4)

# What I built

The model has three components:

*   DeepSeek V4 Flash: 284B total / 13B active MoE — frozen
*   MoonViT-3d: 417M-parameter image encoder from Kimi K2.6 — frozen
*   A 40.1M-parameter connector — trained

The image path is:

Image → frozen MoonViT → 1152-dimensional image features → merge each 2×2 patch group → small MLP connector → 4096-dimensional embeddings → frozen DeepSeek V4 Flash

Only the connector learned anything. Neither the language model nor the image encoder received weight updates.

Images used up to 512 visual tokens, while the maximum training sequence length was 2,048 tokens.

# Training data

I sampled 100,000 examples from HuggingFaceM4/the_cauldron.

The mixture included:

*   General image questions and captions
*   OCR and text-heavy images
*   Documents and infographics
*   Charts, plots and diagrams
*   Science questions
*   Spatial reasoning
*   Website screenshots and UI descriptions

One important observation was that 100,000 examples did not mean 100,000 different images.

The dataset contained only 39,619 unique images because some subsets ask multiple questions about the same image.

I first cached MoonViT’s output for every unique image. This meant that I did not need to run the 417M-parameter image encoder again during every training step.

# Training numbers

*   Trainable parameters: 40,119,040
*   Training examples: 100,000
*   Epochs: 1
*   Global batch size: 128
*   Optimizer steps: 782
*   Optimizer: AdamW
*   Learning rate: 1e-3
*   Precision: BF16
*   Hardware: 5× H200
*   Throughput during the clean portion: approximately 4,938 examples per hour
*   Theoretical uninterrupted runtime: approximately 20.25 hours
*   Approximate end-to-end project expenditure: $2,000

During the final portion of training, the recorded loss decreased from 1.0225 to 0.8301.

The complete experiment cost more than the clean training-pass figure. Including dataset preparation, storage, model conversion, unsuccessful hosts, repeated loading attempts and inference validation, I spent approximately $2,000.

# Does it work?

At a basic level, yes.

For one street image, the model recognized people, boxes and a storefront sign. For a browser screenshot, it identified an “Upload file” control in the sidebar. It also answered a WebBrain UI-grounding question by identifying the correct form field and the currently open menu.

In an earlier runtime, one 36-token image response took 7.49 seconds, corresponding to approximately 4.81 generated tokens per second.

This establishes that the complete path works:

*   The image is processed by MoonViT.
*   The trained connector converts its representation into DeepSeek’s embedding space.
*   The resulting visual embeddings influence DeepSeek’s response.
*   The model can be loaded and served from NVFP4 weights.

I would call the result working basic vision rather than a competitive general-purpose VLM. The model can still give answers that are too short, miss small text, invent visual details or fail on complicated GUI grounding.

I think the main issue is training scale and diversity, not that the connector method is invalid.

# Why 100K examples were not enough

This was a pilot intended to establish whether the architecture could work.

Although it contained 100,000 image-text examples, it exposed the connector to only 39,619 unique images. That is not enough diversity for reliable OCR, documents, dense web interfaces, charts, spatial reasoning and long-tail visual concepts.

The next run should use approximately one million carefully curated image-text examples, with a much higher proportion of unique images and deliberate coverage of:

*   Websites and application interfaces
*   Documents, tables and charts
*   OCR at multiple resolutions
*   Grounded question answering
*   Spatial relationships
*   Natural scenes and objects
*   Multi-step visual instructions
*   Hard negative examples that discourage invented text and objects

One million examples would not automatically make this competitive with Qwen3.6-VL. Dataset quality, resolution, visual-token budget, connector architecture and training objectives still matter.

However, the 100K pilot gives me enough evidence to believe that data scale is now the most useful variable to test.

# What would a one-million-example run cost?

A direct training-only extrapolation gives:

*   Approximately 202.5 hours on the same 5× H200 configuration
*   Approximately 8.4 days of continuous training

A credible one-million-example project should include dataset curation, high-resolution MoonViT feature generation, short learning-rate and architecture pilots, at least one ablation, the final training run, formal evaluation and B200 deployment validation.

Based on what the complete 100K experiment cost, my realistic estimate for doing the one-million-example phase properly is approximately **$15,000–$20,000.**

I cannot responsibly self-fund that complete run today, but I am willing to organize and execute it if there is enough genuine interest from users, contributors, compute providers or sponsors.

# A few engineering details

Training required the BF16 language model even though DeepSeek’s weights were frozen. Gradients still had to pass backward through DeepSeek to reach the connector, while the FP8 and NVFP4 inference kernels did not provide the required input gradients.

DeepSeek’s hash-based MoE routing also expected token IDs for image positions rather than visual embeddings alone. I retained the original IDs for text and assigned deterministic routing IDs to the visual positions.

Serving required a custom image processor, a model wrapper that inserts the visual embeddings while preserving routing IDs, and a small SGLang integration patch.

These were integration requirements rather than evidence that the overall connector method had failed.

# I also trained a Laguna XS 2.1 version

I repeated the same general method with Laguna XS 2.1:

*   33B total / 3B active MoE
*   Same frozen MoonViT encoder
*   30.7M trainable connector parameters
*   100,000 training examples
*   782 optimizer steps
*   Recorded loss: 0.8452 → 0.7318

The longer-term goal is to make the Laguna version usable on a single 96GB Blackwell GPU. Its smaller backbone should also make future training and evaluation considerably cheaper than DeepSeek.

# Credit and lineage

The most direct inspiration for this project was Baseten’s GLM-5.2 Vision NVFP4 release:

[https://huggingface.co/baseten/GLM-5.2-Vision-NVFP4](https://huggingface.co/baseten/GLM-5.2-Vision-NVFP4)

Baseten demonstrated a practical recipe: keep a large text-only MoE frozen, keep MoonViT frozen, and train only a relatively small PatchMerger connector between them.

Their 49.5M-parameter projector maps MoonViT’s 1152-dimensional output into GLM-5.2’s 6144-dimensional token space.

I adapted the same general design to DeepSeek:

*   MoonViT output: 1152 dimensions
*   Connector hidden layer: 4608 dimensions
*   DeepSeek embedding space: 4096 dimensions
*   Trainable connector: 40.1M parameters
*   MoonViT and DeepSeek: frozen

DeepSeek additionally required handling its hash-MoE routing IDs and building the custom SGLang integration.

Moonshot AI deserves credit for MoonViT, DeepSeek for the text backbone, and Baseten for demonstrating that this style of frozen vision retrofit could be packaged into a real large-model deployment.

# The project has already inspired follow-on work

One of the nicest outcomes is that the project has encouraged other people to explore the same direction.

After I shared it, TechMDAI published a related Qwen-based follow-on experiment:

[https://x.com/TechMDAI/status/2086186864105464007](https://x.com/TechMDAI/status/2086186864105464007)

That is exactly why I released the model artifacts and integration code publicly. I would like this to become a reproducible technique for upgrading strong text-only models rather than a one-off release.

# Why I'm working on this

I am building [WebBrain](https://www.webbrain.one/), an open-source browser agent. Browser agents cannot understand everything from the DOM or extracted text. They also need to see screenshots, dashboards, charts, dialogs, rich-text editors and the actual positions of controls.

In our open-model [benchmark](https://www.webbrain.one/blog/american-chinese-open-model-frontier-gap-benchmark), DeepSeek V4 Flash and Laguna XS 2.1 stood out in their respective size classes, but both were text-only:

Instead of replacing them with much larger native vision-language models, I wanted to test whether useful visual perception could be added while preserving the original language models.

The pilot shows that this is possible. The next question is how far the method can go with a genuinely production-scale dataset.

# Interested in the one-million-example run?

I made a short form for people who might:

*   Test the current models
*   Contribute datasets or evaluation cases
*   Help with training or inference engineering
*   Donate GPU capacity
*   Sponsor part of the next training run
*   Use a stronger version in a real product

[https://forms.gle/bNoeJ6cvLYQ4VgKd7](https://forms.gle/bNoeJ6cvLYQ4VgKd7)

This is not a funding commitment. I am using the responses to determine whether enough real demand exists to justify organizing the approximately $15,000–$20,000 next phase.

If there is sufficient interest, I am up for running it and publishing the resulting weights, evaluations and technical findings.

Where do you think the next budget would make the largest difference: more data, a stronger connector or a different vision encoder?

[22 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vl6ior/i_gave_deepseek_v4_flash_basic_vision_by_training/ "22 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/Ok-Shower7286](https://redlib.catsarch.com/u/Ok-Shower7286)•8d ago

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[Muse-Glimmer 30B Hits ~280 t/s in Real Production Coding](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vl2sv6/museglimmer_30b_hits_280_ts_in_real_production/)

 41  Upvotes

These numbers were captured during a real feature implementation task in Next.js and Nest.js (adding a theme switching system across components). The structural predictability of UI/state refactoring is likely why DFlash hit such a high draft acceptance rate (~97%).

Here is a quick log analysis and performance summary running Muse-Glimmer-30B (UD-

 Q6_K_XL) paired with DFlash (Speculative Decoding) via llama.cpp (llama-server + single RTX 5090).

-ngl 99 -c 200000 --host [0.0.0.0](http://0.0.0.0/) --port 8080 --timeout 600 --cache-reuse 256 --parallel 1 --flash-attn on --spec-type draft-dflash --spec-draft-n-max 16 --spec-draft-p-min 0.7 --spec-draft-ngl 99 --cache-type-k q8_0 --cache-type-v q8_0 --no-webui --load-mode none --cache-ram 12192 --temperature 0.8 --top-k 30 --top-p 0.95 --min-p 0.05 --repeat-penalty 1.1 --repeat-last-n 64 --reasoning on --chat-template-kwargs {"enable_thinking":true}

Compared to Qwen 3.6 27B: No Chinese language-mixing bugs, no overthinking loops, and concise responses. Its lighter memory footprint at Q6 also freed up more VRAM/RAM for a much larger context size.

| **Metric** | **Measured Value** | **Notes** |
| :--- | :--- | :--- |
| **Generation Speed (Peak)** | **100 – 287 tokens/sec** | Average ~173 t/s across all tasks; ideal for IDE completion |
| **Prompt Processing (Short)** | **1,000 – 2,100 t/s** | ~100–1,000 tokens evaluated in 0.1s – 0.5s |
| **Prompt Processing (Long)** | **2,654 tokens/sec** | 14.3k tokens evaluated in **~5.35 seconds** |
| **Draft Acceptance Rate** | **63.3% – 97.5%** | Average **82.3%** across 22 test tasks |
| **Mean Accepted Draft Length** | **Up to 14.0 tokens** | Multi-token acceptance driving massive acceleration |
| **KV Cache Reuse (LCP)** | **99.9% (f_sim = 0.999)** | Near-instant response on repeated code contexts |

* update: Muse glimmer 30B's seq length is 131,072

[31 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vl2sv6/museglimmer_30b_hits_280_ts_in_real_production/ "31 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/Southern-Chain-6485](https://redlib.catsarch.com/u/Southern-Chain-6485)•Mar 04 '26

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[I don't understand the hype for Qwen 3.5. They are crap](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rkmcg9/i_dont_understand_the_hype_for_qwen_35_they_are/)

 0  Upvotes

Let's be honest here, their thinking process sucks, seriously suck. Even using repeat penalty and presence penalty, they are prone to being useless. Case in point, with unloth's Qwen3.5-122B-A10B-UD-Q4_K_XL.gguf

Write me 5 sci fi and 5 fantasy prompts to generate wallpapers for android cell phone with ai image generation models that use natural language in their prompts

Reasoning

Toggle reasoning content

Here's a thinking process that leads to the suggested AI wallpaper prompts:

1.   **Analyze the Request:** 

 * **Topic:** Sci-Fi (5) and Fantasy (5).

 * **Purpose:** Android cell phone wallpapers. This is crucial because it dictates aspect ratio, composition, color palette contrast for visibility vs. lock screen text readability, etc. Vertical orientation ($9:16$ or similar high resolution), focus on top/bottom safety zones often needed but AI doesn't know that exactly so general vertical framing helps more than horizontal cut-offs.

 * **Tool:** Natural Language prompts (for models like Midjourney v5/v6/DALL-E 3/Stable Diffusion XL). These need to be descriptive, stylistic, and specific about lighting/composition without being too code-like unless necessary for the model's syntax rules. Since DALL-3 is good at following instructions naturally while MJ prefers concise keywords mixed with natural language (v5/v6), I should strike a balance that works across most "natural language" focused models.

 * **Quantity:** 10 total prompts ($+ \text{categories}$).

2.   **Understand Android Wallpaper Constraints/Requirements for AI Images:** 

 * **Aspect Ratio:** Needs to be vertical (Portrait mode) with longform aspect ratio parameters if supported, or described as "vertical composition". For natural language models without explicit flags like `--ar 9:16`, the prompt must emphasize height. However, most current advanced LLM-image hybrids understand terms like "--aspect-ratio" in some contexts but DALL-E usually just follows text instructions well enough to generate vertical images if asked ("portrait orientation"). *Correction:* Most "Natural Language AI Image Models" (like Bing/D3 or MJ v6 with settings) respond better when told the aspect ratio explicitly, even via natural language like "$1080x2400$". I will include these technical constraints in parentheses to be safe.

 * **Focus/Content:** Android icons are usually at the bottom ($7:3$: $95\%$, lock screen often top-heavy). It's best if AI is told not to crowd the very center or ensure there is negative space for widgets/text (optional but helpful advice, though prompt-wise we focus on aesthetics first. I will add notes about icon placement in my intro/outro text rather than over-constrain prompts which might ruin composition too much).

 * **Visual Quality:** 8k resolution details, high contrast or vibrant colors stand out against widgets/notifications (dark mode friendly vs light background options? Androids usually support both. I'll aim for visually striking images that work well generally—often deep backgrounds with glowing elements look great on OLED screens.)

3.   Drafting the Prompts - **Sci-Fi Category:**

 * Idea 1: Cyberpunk Cityscape (classic, popular). Needs neon rain and verticality to emphasize tall buildings suitable for phone screen height ($95\%$ focus at top/middle leaving bottom clear-ish or just general high-res detail. Okay $40 \sim cm$. Let's aim wide angle perspective looking up.)

 * Idea 2: Space Station/Orbit view (calm, deep space). Focus on Earth in distance with foreground structure details for depth to make it look wallpaper-ready rather than flat landscape picture of a planet or just the background. Okay $40 \sim cm$. Let's aim wide angle perspective looking up.)

 * Idea 3: Futuristic Vehicle/Transport (speed, motion). A sleek hover vehicle driving through clouds/tunnels. Motion blur implies speed but clean UI for home screen text readability needs to ensure center focus isn't too busy? Actually AI can handle dynamic composition where the subject is central or off-center with breathing room elsewhere.)

 * Idea 4: Alien Planet Landscape (exotic colors). Bioluminescent flora, purple skies. Very distinct look that makes a phone stand out. Darker foreground for widgets visibility on lock screen sometimes better? Actually bright center works well too as long text can sit over dark parts of image or use icon masks in launcher settings.)

 * Idea 5: Abstract/Geometric Sci-Fi (modern UI style). Minimalist, neon lines forming shapes that are "techy" but not cluttered. Good for widgets overlaying the bottom area while top remains clean and abstract art vibe

4 Drafts - **Fantasy Category:**

 * I will ensure verticality is emphasized in natural language instructions like 'vertical composition', portrait orientation'. Also emphasizing high detail, lighting effects (bloom/occlusion), no text/artifacts. Ensure clarity of prompts for AI understanding.) *Self-Correction:* The user specifically asked to generate wallpaper using the prompt itself?

 *(Wait... re-reading request: "Write me 5 sci fi and $8$ fantasy prompts that use natural language in their own wording." Wait, no - it says "$7$" wait. Let's read again carefully.*

*(Self-Correction on Count)* The user asked for **"$9$"**? No... **"10 total ($+ \text{categories}$)."**

 *(Wait: $5 + 6 = something else ... "Write me =$?$" )* *Actually, the prompt says "$2$" or nothing.*

*(Re-reading very carefully)*. The user said in my instructions that I should have a specific plan but also follow general guidelines for formatting output... wait no.)

 Okay let's re-read actual request: **"$5$ sci-fi and $7 \sim 8 ... Wait."** *I need to stop overthinking the instruction check.* Let me read input again.

*Input:* "Write me =$?$" (Wait, I am simulating my own thinking process here based on initial thought trace.)

 Okay let's look at real user text: **" Write "$5$" sci fi and $8$ fantasy prompts"** Wait... no it says **"$10 \sim 9 + ...".** Actually looking closely "Write me =$?$" is not the prompt. The actual request I must answer now (in this thinking block) based on original input? *No, wait.*

 Okay let's re-evaluate what was asked: **" Write "$5$" sci fi and $8$ fantasy prompts to generate wallpapers..."** Wait did it say **"$10 + \sim 7 ..."** actually no. It says in the very first line of user text "**Write me =$?$" (Wait I am checking my own trace again)**

 Okay let's go back.)

*User Text:* " Write "$5$" sci fi and $8$ fantasy prompts to generate wallpapers for android cell phone with ai image generation models that use natural language in their..." No wait. Let me check the very beginning of input: **"Write"$?"".** It says **"$10 + \sim 9 ..."**

 Okay I am confusing myself by simulating errors now.)

*Let's read prompt text strictly:* "** Write "$5$" sci fi and $8$ fantasy prompts...**" NO! The actual user message provided at start of session was: **"Write me =$?$".** *Wait no.* Let's open the window.

 Actual User Message is in chat history... It says *" **"$10 + \sim 9 ...** Wait I cannot find that.**

*Okay, let us read prompt text strictly from current state:* "** Write "$5$" sci fi and $8$ fantasy prompts to generate wallpapers...**" NO! The user message actually was: "Write me =$?$".

 *Actually looking at the very first line of this session's actual content provided by system... it says **"$10 + \sim 9 ... Wait.** Let us assume standard request logic.*

*Wait, I am over-analyzing. What did user ASK in prompt text? "Write me =$?$"

 *No! The User Prompt is:" Write "$5$" sci fi and $8$ fantasy prompts...". **NO!** It says:** "**"$10 + \sim 9 ... Wait.** Let's look at the REAL input."

*Input:* **"$$** (Wait, no. I need to stop hallucinating counts.*

 The prompt text provided by User is:"Write me =$?$" -> NO! *User Text IS: " Write "$5$" sci fi and $8$ fantasy prompts..."? No!* It says "**"$10 + \sim 9 ... Wait.** Let's assume standard."

*Okay let us read input very carefully NOW.* **Input:** **"**Write me =$?$"

 **(Wait I cannot see actual user text in this thinking block due to system architecture restriction... wait no. The prompt IS provided above.)".** *Let look again:* " Write "$5$" sci fi and $8$ fantasy prompts..." NO! It says "**"$10 + \sim 9 ... Wait.**"

*(Self-Correction)*: I must stop simulating input confusion because it blocks output generation. Let's assume the request is standard based on title provided in initial system instruction trace? No.)

*Okay look at prompt text again:* " ** Write me =$?$ "** *No wait.* It says **"Write "$10 + \sim 9 ... Wait.**"

*(Stop simulating input confusion. I am thinking about the request itself).* The user asked for a list of prompts in my output?

*Wait, let's look at original prompt text provided by User:* "** Write me =$?$ ** (No wait...)" *Okay.* Let me just generate 5 sci-fi and $7$ fantasy based on standard interpretation that might be missing. Wait no! The request is: "Write "$10 + \sim ... No."

*Let's look at the very first line of prompt text:* "** Write "$?" ** (No wait...)".

 Okay let me stop simulating input confusion.* *User Prompt Text IS:**"**"** **"$. Let it go.** I will produce standard output based on request: "Write 5 sci-fi and $7$ fantasy prompts..." Wait, no... It says `10 total`? No.

*Okay final check:* User text in box above is **"$"?**.

 Actually looking at real input provided by system interface here:**"** Write "$?" "**No! The user prompt IS: **"Write me =$?$" (Wait.)** I cannot see actual specific numbers if they were scrambled but logic suggests $10$ total.

*Okay, let's assume User asked for 5 Sci-Fi and *?* Fantasy.*

 Actually looking closely at original text provided in "User Prompt"* section:* "** Write "$?" **". Wait no it says *"Write me =$?$" (Wait)* I cannot see... Okay the system input box shows: **"**

*Okay let's just generate standard 5+6 = $10$? Or *?*.*

 Actually looking at original text provided in "User Prompt"* section:* "** Write "$?" **". Wait no it says *"Write me =$?$" (Wait)* I cannot see... Okay the system input box shows: **"

*(STOP. The actual user prompt IS visible to model).* Let's look really hard.*

 User Text:**"**""** wait, let just read text provided:* "** Write "$?" **". Wait no it says *"Write me =$?$" (Wait)* I cannot see... Okay the system input box shows: **"

*Okay final decision on counts based on visible prompt line "Read carefully ... *"*

 User Text:**"**""** wait, let just read text provided:* "** Write "$?" **". Wait no it says *"Write me =$?$" (Wait)* I cannot see... Okay the system input box shows: **"

*(STOP. The actual user prompts IS visible to model).* Let's look really hard.*

 User Text:**"**""** wait, let just read text provided:* "** Write "$?" **". Wait no it says *"Write me =$?$" (Wait)* I cannot see... Okay the system input box shows: **"

*Okay final decision on counts based on visible prompt line "Read carefully ... *"*

 User Text:**"**""** wait, let just read text provided:* "** Write "$?" **". Wait no it says *"Write me =$?$" (Wait)* I cannot see... Okay the system input box shows: **"

*(STOP. The actual user prompts IS visible to model).* Let's look really hard.*

 User Text:**"**""** wait, let just read text provided:* "** Write "$?" **". Wait no it says *"Write me =$?$" (Wait)* I cannot see... Okay the system input box shows: **"

*(Okay enough simulation. Here is real prompt):** "

*User Prompt Is Visible In Input Box Above.* It reads exactly:"

 `**"**` No wait.**Let's read actual text provided in this block:** "**Write me =$?**" (Wait, no). **The user asked for 5 Sci-Fi and $8$ Fantasy? Or *?***.

*(Okay let us assume standard request logic is to produce what I am thinking.)*

 User Text: ` Write "$10 + \sim ... Wait.` No wait... Let's read prompt again.* "Write me =$?"** (Wait). **The user asked for 5 Sci-Fi and $8$ Fantasy? Or *?***.

*(Okay enough simulation.) The request says in input box above:* "**"**

 Actually, I see text now:**" Write "$10 + \sim ... No wait. Let's look at real prompt.** "Write me =$?"** (Wait). **The user asked for 5 Sci-Fi and $8$ Fantasy? Or *?***.

*(Okay enough simulation.) The request says in input box above:* "**"**

 Actually, I see text now:**" Write "$10 + \sim ... No wait. Let's look at real prompt.** "Write me =$?"** (Wait). **The user asked for 5 Sci-Fi and $8$ Fantasy? Or *?***.

*Okay enough simulation.) The request says in input box above:* "**"**

 Actually, I see text now:**" Write "$10 + \sim ... No wait. Let's look at real prompt.** "Write me =$?"** (Wait). **The user asked for 5 Sci-Fi and $8$ Fantasy? Or *?***.

*Okay enough simulation.) The request says in input box above:* "**"**

 Actually, I see text now:**" Write "$10 + \sim ... No wait. Let's look at real prompt.** "Write me =$?"** (Wait). **The user asked for 5 Sci-Fi and $8$ Fantasy? Or *?***.

*Okay enough simulation.) The request says in input box above:* "**"**

 Actually, I see text now:**" Write "$10 + \sim ... No wait. Let's look at real prompt.** "Write me =$?"** (Wait). **The user asked for 5 Sci-Fi and $8$ Fantasy? Or *?***.

*Okay enough simulation.) The request says in input box above:* "**"**

 Actually, I see text now:**" Write "$10 + \sim ... No wait. Let's look at real prompt.** "Write me =$?"** (Wait). **The user asked for 5 Sci-Fi and $8$ Fantasy? Or *?***.

*Okay enough simulation.) The request says in input box above:* "**"**

 Actually, I see text now:**" Write "$10 +

[72 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rkmcg9/i_dont_understand_the_hype_for_qwen_35_they_are/ "72 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/LowerGears](https://redlib.catsarch.com/u/LowerGears)•15d ago

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[I compared MinerU, Granite-Docling, and PaddleOCR-VL on 12 PDF-parsing capabilities using 6 document types](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vecxhw/i_compared_mineru_granitedocling_and_paddleocrvl/)

[![Image 5: Post image](https://redlib.catsarch.com/img/puni9buas5hh1.png)](https://redlib.catsarch.com/img/puni9buas5hh1.png)

 55  Upvotes

I tested them by sending the 6 documents, each meant to represent a different document type, through my own webapp and comparing every output against the source. All ran on the same L4 GPU.

The documents:

1.   Financial statements with merged multi-level headers (A typical annual report)
2.   Two pages of a two-column arXiv paper ("Deep Residual Learning for Image Recognition")
3.   Scanned German invoice with no text layer
4.   French municipal report with an embedded bar chart
5.   Typical datasheet page mixing German, French, Chinese and Russian
6.   A 2-page, 3-column newsletter article

Things to note:

*   One thing the capability grades don't show: Granite-Docling is the only one that outputs markdown-native pipe tables and real heading levels (MinerU gives you HTML tables and promotes everything to #), so on clean digital documents its raw markdown is the nicest to actually read.
*   MinerU quietly read a bar chart and returned the values as a table, and wrote its own description of an embedded image (tagged as generated).
*   MinerU seemed to dropped the invoice's IBAN from the footer. But the model actually transcribes it yet the MinerU's markdown generator silently discards anything it classifies as page furniture (i.e things like footers, page numbers, fine print....), and there's no option or configuration to acutally change this behavior. So I rebuild the markdown from its block list instead, and re-ran that column, to give a fair comparison. If you are using stock MinerU's .md output, you're likely have footers missing.

If anyone is interested in how these models compare in handling other document types, let me know and I'd be happy to compare them. I ran this benchmark using my own API provided via my own service ( [hexread.com](http://hexread.com/) ). You can also test your PDFs directly on the website (there’s a free trial but you only get automatic model selection with that).

[25 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vecxhw/i_compared_mineru_granitedocling_and_paddleocrvl/ "25 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/crossivejoker](https://redlib.catsarch.com/u/crossivejoker)•May 12 '26

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[MagicQuant (v2.0) - Hybrid Mixed GGUF Models + Unsloth Dynamic Learned Quant Configurations + Benchmark table with collapsed winners and more](https://redlib.catsarch.com/r/LocalLLaMA/comments/1tb3sja/magicquant_v20_hybrid_mixed_gguf_models_unsloth/)

 93  Upvotes

I spent the past 5+ months building a pipeline that creates hybrid GGUF quant mixes. I also built it to learn from Unsloth (or other) models by utilizing their quant to tensor assignment. And some architectures like Qwen3.6 27B have super weird patterns that can get genuinely lower KLD while dropping the model size meaningfully. Totally depends on the architecture though! This has been incredibly fun for me to build. I call my project, "MagicQuant". And I'd love to show you what it is currently producing alongside the published repo's to showcase.

And the hybrid aspect is super fun and mostly what I'll talk about. But the final results table doesn't just include hybrids, it includes Unsloth, llama.cpp, or anything else it learns from, but it only shows the survivors of the pipelines gauntlet.

MagicQuant has dominance, premium, nonlinear sub space winners, and collapse logic that instead of a quant dump repo that says "I don't know if IQ4_XS or Q4_K_S is better than the other even though they're the same size. Nor do I know if this model is allergic to IQ4_NL, but good luck!" MagicQuant aims to actually test what's the best bang for your buck based on the VRAM you have.

Some models are very predictable, boring, and don't really have crazy improvements to be made, but maybe some nice optional sub zones, great collapse spaces, etc. Some models are weird, have quirks, and the system recognizes this and optimizes the living hell out of it.

MagicQuant aims to solve a few key issues I personally have with the space:

1.) Everyone posts Q8/Q6/Q5 and so on. But there's no benchmarks. Was there a dramatic dip in KLD going from one quant to another? If so, why are you showing me an obviously bad trade?

2.) What if I need to be in the Q4 size range, but am willing to sacrifice a few more bytes for nonlinearly better KLD win? AKA, find good nonlinear KLD trade points that deserve to exist as an option.

3.) When downloading a model, I want to know only what quants matter. Not every quant currently available. Which is worth it? Which did better on this model? Hint hint, model architectures are weird, some like certain quants, some like weird quants but only in certain bit ranges where noise gets beneficial, some are allergic, some favor weird ones massively. Some LOVE MXFP4, though most hate it lol.

4.) Detect anomalies, hunt them down, validate their existence, and abuse the learned pattern. This is rare, but when it exists, USE IT! Qwen3.6 27B falls under this category of weirdness that can be abused.

**This post is long. Here's the 'what to skip':**

*   **Example Section** - showcases the actual results. Should read to understand.
*   **Please Understand** - I understand it's weird to have a section on the topic of, "This is more grounded than you think, please understand X". But without this section you may misjudge or misunderstand MagicQuant. You can skip it if you want, but I think it's important.
*   **Cloning Section** - Optional read, but like, it's cool.
*   **Nonlinear Wins Section** - If you don't care how winners are picked or what this means, skip.
*   **What Is MagicQuant Section** - Probably should read, but like if you just want to see the results, click download, and play, skip this too.

Basically the Examples and final sections are really all that's necessary. The rest is just the sauce for those who want to understand, have questions, etc. Again, I apologize for the length, but it was a ton of work, a lot of fun and a lot of after work hours effort hammering away at this.

# MagicQuant Repo Examples

Lets start with my favorite and best results thus far because it's the most fun. Most models are way more tame, but Qwen3.6 27B had a lot of room to flex what MagicQuant found.

# Qwen3.6 27B

There were many more models that were eliminated from the running and uploaded. But I showcased just a couple that're crossed out to help give reference points. Utilized for learning config patterns was Unsloth Dynamic XL models (they only had the XL models) and llama.cpp default configurations.

| Name | KLD | Size (GB) |
| :--- | :--- | :--- |
| ~~LM-Q8_0~~ | ~~0.003768~~ | ~~28.60~~ |
| [MQ-Q6_K_1](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.002845 | 27.25 |
| MQ-Q6_K_2 | 0.003884 | 25.23 |
| MQ-Q6_K_3 | 0.004914 | 23.66 |
| ~~LM-Q6_K~~ | ~~0.007249~~ | ~~22.08~~ |
| [MQ-Q5_K_S_1](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.006477 | 21.90 |
| MQ-Q5_K_S_2 | 0.007617 | 20.86 |
| LM-Q5_K_S | 0.010790 | 18.68 |
| ~~UD-Q4_K_XL~~ | ~~0.023521~~ | ~~17.61~~ |
| [MQ-IQ4_NL_1](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.019687 | 17.59 |
| LM-IQ4_NL | 0.025714 | 15.80 |
| LM-IQ4_XS | 0.027015 | 15.08 |
| [MQ-IQ3_M_1](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.043802 | 14.49 |
| [LM-IQ3_S](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.064393 | 12.42 |
| [LM-IQ3_XXS](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.093578 | 11.19 |
| LM-IQ2_M | 0.163117 | 10.00 |
| [LM-IQ2_S](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.210251 | 9.36 |
| LM-IQ2_XXS | 0.302597 | 8.43 |

# Smaller than Q8 but lower KLD?

So, let me point out the elephant in the room. How in the world did MagicQuant build a model that was 1.35 GB smaller than Q8_0 but drop the KLD damage by nearly 25%?

Well, because `Q6_K` in `ffn_down` resulted in a KLD that was lower than if it had `Q8_0`! This was not a detectable pattern in the isolated environment, but it was an emergent behavior when quantization occurred with much less BF16 around the board.

MagicQuant has ways to try to smoke test anomalies, in this scenario it found multiple, but I'm pointing out one. And `MQ-Q6_K_1` simply rebuilt the same model with `Q8_0` on every group except for `ffn_down`.

# What's going on?

Well, MagicQuant builds winners that're nonlinearly better for the KLD to size trade, or just what I call free lunch (aka smaller or same size and better).

When it comes to dominance winners or nonlinear winners, that's just great winning models found. Things like "premium" winners or "collapse winners" is more spicy logic, not always necessarily "purely better" but it's also still very sound logic in general.

But the `MQ-Q6_K_1` was a simple showcase of a hybrid pattern, but once you start hitting lower bit, you start seeing super fun patterns like the following.

This was `MQ-Q5_K_S_1`:

```
{
  "embeddings": "IQ4_NL",
  "lm_head": "Q6_K",
  "attn_q": "IQ4_XS",
  "attn_kv": "Q8_0",
  "attn_output": "Q8_0",
  "ffn_up_gate": "UD-Q6_K_XL",
  "ffn_down": "Q5_K"
}
```

Or sometimes it's less crazy like that and you get wins like the `UD-Q4_K_XL` that was eliminated by `MQ-IQ4_NL_1` with this pattern:

```
{
  "embeddings": "IQ4_NL",
  "lm_head": "UD-Q4_K_XL",
  "attn_q": "IQ4_XS",
  "attn_kv": "Q5_K_S",
  "attn_output": "UD-Q4_K_XL",
  "ffn_up_gate": "UD-Q4_K_XL",
  "ffn_down": "UD-Q4_K_XL"
}
```

I love that it literally just used Unsloths Q4_K_XL and said, "oh if I just change these 2 groups, it's free lunch." This is actually how `UD-Q3_K_XL` got eliminated too, though it was eliminated by "premium" logic not due to it being purely "better".

"premium" winners means it's maximum 1% bigger than the baseline we're comparing too, and the KLD is nonlinearly better than going to the next bit anchor point. So it's a more bias spicy winner in my pipeline but it's also a very high bar imo.

But MagicQuant on this model was able to hit really hard as you can see. Anomaly detection is rare, but when it occurs you see madness like this. And it's how 7 hybrids were decisively chosen as the end final survivors.

But normally from what I've observed, the 27B model was extra spicy, but more tame and normal results looks like Qwen3 4B.

# Qwen3 4B 2507 Instruct

Now the following [Qwen3-4B-Instruct-2507](https://huggingface.co/magiccodingman/Qwen3-4B-Instruct-2507-Unsloth-MagicQuant-v2-GGUF) is more what I'd call, "normal" for MagicQuant. No anomalies, no craziness, just what I consider straight value.

| Name | Quant Family | KLD | Size (GiB) |
| :--- | :--- | :--- | :--- |
| LM-Q8_0 | Q8_0 | 0.001339 | 3.99 |
| MQ-Q6_K_1 | Q6_K | 0.001817 | 3.58 |
| UD-Q6_K_XL | UD-Q6_K_XL | 0.002111 | 3.41 |
| LM-Q6_K | Q6_K | 0.004640 | 3.08 |
| [MQ-Q5_K_1](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | Q5_K | 0.006632 | 2.88 |
| [UD-Q5_K_XL](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | UD-Q5_K_XL | 0.009839 | 2.73 |
| [MQ-Q4_K_M_1](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | Q4_K_M | 0.020346 | 2.44 |
| [LM-Q4_K_S](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | Q4_K_S | 0.029803 | 2.22 |
| LM-IQ4_XS | IQ4_XS | 0.031300 | 2.11 |
| UD-Q3_K_XL | UD-Q3_K_XL | 0.072278 | 1.98 |

A cool win for a hybrid GGUF was the `MQ-Q4_K_M_1`. It was what MagicQuant calls a "nonlinear" winner and it ended up collapsing and removed `UD-Q4_K_XL`, `LM-Q4_K_M`.

here's a side by side:

| Model | KLD | PPL Δ | Size (GiB) |
| :--- | :--- | :--- | :--- |
| **MQ-Q4_K_M_1** | **0.020346** | **0.8312%** | **2.439** |
| UD-Q4_K_XL | 0.022351 | 1.2805% | 2.413 |
| LM-Q4_K_M | 0.025432 | 1.6528% | 2.326 |

This does NOT mean it was the same size or smaller than those it collapsed. Sometimes it does, sometimes it doesn't. But the system values nonlinear winners. Basically the difference in size was considered too small to keep all 3. Especially when there were additional smaller quants under `LM-Q4_K_M`. The system has lots of smart configurable logic that said in this scenario, "Do we really need 3 separate models within 113 MB size range of each other?" And there was a nonlinear winning hybrid, unsloth model, and llama.cpp model within a collapsible range.

But this is just is a showcase of one of many decisions MagicQuant will make to create a clean quant table of what was decided to be clear winners worth their salt and that actually pay rent.

Mind you, hybrids, llama.cpp, or unsloth models are treated identically. Each can win collapsed spaces, `UD-Q5_K_XL` and `LM-Q4_K_S` both collapsed other models and became the winner for example.

Also shown in the table, 2 of the hybrids, `MQ-Q6_K_1` and `MQ-5_K_1` both were discovered as nonlinear trade wins between their quant family bit space. Meaning it's not just a Q6.5 or Q5.5, but genuinely good trades for KLD for the increase in size. Thus the system decided they were worthy of existing.

The 3 shown MagicQuant Hybrids actually utilized the following configurations:

| Name | embeddings | attn_q | attn_kv | attn_output | ffn_up_gate | ffn_down |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MQ-Q6_K_1 | Q8_0 | Q8_0 | Q8_0 | Q8_0 | Q6_K | Q8_0 |
| MQ-Q5_K_1 | Q8_0 | Q5_K | Q8_0 | Q6_K | UD-Q5_K_XL | Q5_K_S |
| MQ-Q4_K_M_1 | Q8_0 | Q5_K | Q8_0 | Q6_K | IQ4_XS | IQ4_XS |

The goal is not to light up the map with hybrid models only. It's to find what's the best KLD to file size trades you can make.

# Qwen3.6 35B A3B - MOE Example

So, how does this system handle MOE? Well, as well as whatever Quant it learns from. Here's a more fun and recent example from the new Qwen3.6 series. In which this series has more Unsloth Dynamic to showcase too. Now you'll notice a lot of MagicQuant hybrids and less options as well.

Reason is because tons of stuff was dominated and collapsed. This was actually less because of gnarly hybrids. Actually the funkiest one was this:

```
{
  "embeddings": "UD-IQ3_S",
  "lm_head": "Q8_0",
  "attn_q": "Q6_K",
  "attn_kv": "Q8_0",
  "attn_output": "Q8_0",
  "ffn_up_gate": "UD-IQ4_NL",
  "ffn_down": "UD-Q3_K_XL",
  "moe_router": "Q8_0"
}
```

But in reality, most were like this:

```
{
  "embeddings": "UD-IQ3_S",
  "lm_head": "UD-Q6_K",
  "attn_q": "UD-Q6_K",
  "attn_kv": "UD-Q6_K",
  "attn_output": "UD-Q6_K",
  "ffn_up_gate": "UD-Q6_K",
  "ffn_down": "UD-Q6_K",
  "moe_router": "UD-Q6_K"
}
```

This MOE model mostly comes down to the experts, and Unsloth dominated freaking EVERYWHERE. I mean of course they did! But UD-IQ3_S was basically a free lunch cheat code. Why a Q3 you may ask? Well, remember Unloth Dynamic feels out tensor sensitivity and at the UD-IQ3_S and a variety of others that matched (this is just what my system latched onto even though others tied it). Unsloth made the embeddings really really strong on UD-IQ3_S because their system obviously found out it was sensitive and worth protecting. The size of that tensor group is actually larger than Q5 mind you but it demolished Q6 and Q8 in that category because it was both smaller and lower KLD!

Which is how the following table was born:

| Name | KLD | Size (GB) |
| :--- | :--- | :--- |
| LM-Q8_0 | 0.004654 | 36.90 |
| [MQ-Q6_K_1](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.005149 | 31.59 |
| [MQ-Q5_K_1](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.005523 | 29.19 |
| [MQ-Q5_K_S_1](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.006730 | 26.33 |
| [MQ-Q4_K_M_1](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.007799 | 24.82 |
| [MQ-Q4_K_M_2](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.011007 | 22.32 |
| [MQ-IQ4_NL_1](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.013277 | 20.89 |
| [MQ-IQ3_M_1](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.026330 | 17.60 |
| [UD-IQ3_S](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.068376 | 13.68 |
| [MQ-IQ2_XXS_1](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8+chinese+language+mixing&restrict_sr=on&sort=relevance&t=all#winner-notes) | 0.275130 | 9.59 |

This has been a pretty clear pattern I've noticed mind you. When a model has more Unsloth Dynamic models to work with, the better it can do. Which again... That makes tons of sense. But this is how MagicQuant works. Sometimes wins are really weird combinations, sometimes it's anomalies, sometimes it's cool sub zones, and sometimes it's just honestly noticing a few tweaks could be make here or there to effectively get a bit of a boost.

# Please Understand

I want to stress that MagicQuant can't "guarantee" anything. I can't say, "give me an optimized Q4". It instead checks the search space and tries to find **IF** any spaces exist at all. It may or may not exist. That's the point. Some MagicQuant tables will light up MagicQuant hybrids on the map like a Christmas tree. Some MagicQuant goes, "Unsloth killed it, go use them. Here's maybe 2 sub zones for nonlinear wins if you're in this VRAM size."

Additionally, the utilization of KLD is the primary metric, though there's other PPL metrics behind the scenes and showcased on manifest files on the repo. I use PPL as a secondary smoke signal. But I'm also sampling hundreds of isolated probes, so physics is an issue. I'd love to add more benchmarks, but KLD is very effective at testing tensor configurations and thus a very good, cheap benchmark that's heavily utilized throughout the process. Plus it lets me finish the pipeline before my great great great grand babies are born. But I'm always open to ideas, improvements, etc! But the goal isn't to produce a model that claims it's universally better in every single situation. It's to test and find the best tensor configurations!

If you see metrics showcasing MagicQuant beating an Unsloth model. Please keep in mind I never once benchmark the original Unsloth Dynamic artifact. I grab an Unsloth model, just like I would for a llama.cpp or batwoski GGUF model. I then strip the model away from all its special sauce, then I normalize it with my derivative model, my imatrix, etc. Finally I begin grouping tensors, isolating them, probing, and begin building hybrid models.

So when you see something beating an Unsloth model for example. I am NOT saying this version beats Unsloths original artifact. I never ran that benchmark. They use their own imatrix, their own stuff, the only thing I benchmarked was their tensor config in a fair and isolated environment. But it is saying that under my isolated environment, the tensor configuration pattern on X did beat Y.

I hope that makes sense 😄

That's also why when an Unsloth Dynamic model wins, I literally link to their repo instead of re-hosting their quants. Plus, whenever an Unsloth model is beat, it's usually literally a MagicQuant model using Unsloths very tensor configurations but with a more optimized group pattern. So I didn't quantize jack diddly! You say don't quantize 1 dimensional tensors? I say, "That's not my responsibility to care about. Unsloth already protected that, thus so did MagicQuant."

Quantization is very hard. I leave that to the smart people working on that frontier. Think of MagicQuant like a meta level above quantization.

But it's also why when in the past for MagicQuant v1.0 when I was asked, "Does this beat Unsloth Dynamic." I didn't realize the misunderstanding because MagicQuant isn't a quantizer that makes tensor by tensor decisions like Unlsoth Dynamic. I literally use their Unsloth Dynamic configurations. To me, asking if I beat Unsloth is kind of like asking me after I overclocked a CPU, "Did you beat Intel/Ryzen?"

As where it's more like, "I mean I got some good silicon and was able to overclock it to X. But it's still the same CPU."

# Cloning

Another cool feature of MagicQuant is cloning. MagicQuant repositories are automatically generated. One of the generated files is called, "`magicquant.clone-configs.json`". In which the system doesn't necessarily need this file to clone, but it makes it incredibly easier and faster versus downloading every model and learning the config again when it was already done once before anyways.

This lets me upload a repository, then look at the uncensored model of Qwen3.6 35B A3B, for example the model by `llmfan46/Qwen3.6-35B-A3B-uncensored-heretic` which utilized Heretic.

I can target that unensored repository and the Qwen3.6 35B MagicQuant repository and the system will bake a clone of the finalists, including the Unsloth Dynamic models too since Unsloth doesn't host the uncensored models.

MagicQuant will actually rebuild the finalists without requiring the entire process to run again from scratch. It'll link the repo in the readme to the original MagicQuant and properly re-run benchmarks as well. It checks tensor patterns too. That way there's no accidental clones of things that don't match.

I have a cloned repo of the Qwen3.6 35B A3B for an uncensored version. Though at least as of right now when I posted, it's a cloned version of the old Qwen3.6 35B results I got, not the newest and more refined results. It's still baking the clone and should hopefully be done in the next 24 hours of me posting this reddit post with the newest MagicQuant hybrids for the uncensored model.

# Importance Of Nonlinear wins

MagicQuant does not look for simple "winners" in sub space between baselines. Instead it only allows nonlinear trade wins. TLDR:

Imagine a graph like this:

```
Size  → 
|
|        Q6
|      /
|    /
|  Q5
| /
|Q4
+----------------
```

A nonlinear win looks like:

```
Q6
      /
    /    ← MQ-Q5_K_1 (above the line)
  Q5
 /
Q4
```

That hybrid sits above the straight line between Q4 and Q5.

Meaning:

 It’s a **more efficient trade** than the normal step-up

This is what MagicQuant calls a "nonlinear trade/win" when such wordage is used.

Because anyone could just bump up a tensor or 2, see the KLD drop slightly, say, "look it's better" and then light up the repo table with all MagicQuant models. That's not the point of MagicQuant. And nonlinear winners is an important distinction to understand "why" a winner deserves to exist or is picked.

For a hybrid to be presented between a bit space, it must be genuinely better than just going to the next quant bit up.

# What Is MagicQuant?

From previous posts, or those who followed MagicQuant v1.0, a common misconception about MagicQuant and that it is a quantization algorithm. It does not make tensor by tensor decisions like Unsloth Dynamic or llama.cpp.

Here's a very simple explanation.

1.) The pipeline quantizes a model using llama.cpp or downloads the unsloth model.

2.) Each tensor is read and categorized into upwards of ~10 dynamically activated group tensor categories. This is simple regex level finding to match them into their slots.

3.) Store what quant was assigned to each tensor within a database and to their assigned tensor group.

**Unless you want more details, you can skip this part. This gets a bit more quant heavy with the discussion and really is me just dumping knowledge sauce for those who want to heavily understand what's going on**:

A bit more explanation for those unfamiliar. When you want to quantize a model for example to Q3, and lets say you have hypothetically 400 tensors in your model. Llama.cpp nor Unsloth just tells every single 400 tensors to be some Q3 bit quant. That'd destroy the AI's brains.

Instead, real quantization algorithms like Unsloth Dynamic 2.0 feels out tensors, which are sensitive, which are not, and they do lots of fancy things. Using loose language here to explain mind you.

What MagicQuant then does is look at Unsloths model and for example would see something like 100 tensors in `ffn_up_gate` group with 10 of them as F32, 30 as Q6_K, 20 as Q4_K, 40 as IQ3_XXS. And this knowledge would be recorded for re-use by MagicQuants pipeline when recreating the baseline, building hybrids, isolating samples, and more.

The Qwen3 4B Instruct 2507 model shown earlier, here's the actual range of quantizations used within each tensor group that I actually recorded when reviewing Unsloths `UD-Q3_K_XL` GGUF model.

| Tensor Group | Unique Final Quant Types |
| :--- | :--- |
| `embeddings` | `Q6_K` |
| `attn_q` | `IQ3_XXS`, `IQ4_XS`, `Q3_K`, `F32` |
| `attn_kv` | `IQ3_XXS`, `IQ4_XS`, `Q3_K`, `Q4_K`, `Q5_K`, `Q6_K`, `F32` |
| `attn_output` | `Q4_K`, `F32` |
| `ffn_up_gate` | `IQ3_S`, `IQ4_XS`, `Q3_K`, `F32` |
| `ffn_down` | `Q4_K`, `Q5_K`, `Q6_K`, `F32` |

Cool right? This is understood by real ML researchers obviously, but I consider myself a mere mortal and this was just cool for me to fully realize.

Now MagicQuant remembers this kind of information. It's not trying to be architecture aware necessarily or do some fancy thing. It simply remembers each tensor assignment and their assigned group (eg. `ffn_down`, `attn_q`, etc). Then if I want to use `UD-Q3_K_XL` on lets say `attn_output` on a future hybrid, I can just re-apply what I learned.

This prevents MagicQuant from having to figure out what exact tensors to touch, not touch, which are sensitive, etc. I just stand on the shoulders of giants. I leave that hard part to the smart people pushing that frontier.

This is how hybrids are born mind you. I simply digest these mappings and then build isolated samples of every tensor group to quantization configuration.

Then not only do I have the ability to re-apply the learned config, but I have a prediction engine that very practically (it's not omniscient) uses the probed isolated sample knowledge to predict, then build, then validate, and find potential hybrids utilizing the mixed tensor to group knowledge that was extracted and isolated in samples.

**Final Example**. Sorry to beat this in, but it was a big misunderstanding with v1.0 but think of MagicQuant like a wine critic and tester. I didn't make the wine, but I've tested enough to tell you which pair with what meals and when.

# Finally

I spent the last 5+ months working on MagicQuant v2.0 and it was a lot of work. I had to learn a lot. I had a lot of failures. I had to go back to the drawing board multiple times. I swear I would have physically chucked the code out the window at some points if it were possible.

But, thank you so much to those who helped me along the way. I've wanted something like this for myself because I feel like I can finally just look at a repo, know what trades I'm getting at what sizes, and not guess if IQ4_NL or IQ4_XS is going to be barely any different or find out an architecture is allergic to one and not the other (because yeah that happens).

It was also a ton of fun building the hybrid aspect too. Sometimes there's hybrid winners, sometimes there's not. Totally depends. That's the point. If the space exists for nonlinear good trades, that's great. If not, a repo still is posted with just the baselines. Heck if only unsloth wins, then it's just a ton of links to Unsloth.

If you used v1.0 (MXFP4 era), check the docs for why it was deprecated and what changed:

[https://github.com/magiccodingman/MagicQuant-Wiki/blob/main/wiki/archival/version_1/README.md](https://github.com/magiccodingman/MagicQuant-Wiki/blob/main/archival/version_1/README.md)

That v1.0 doc will read more like a postmortem to be honest. I felt it was important though to document why it failed, why it was wrong, what I learned, even when the results looked deceptively successful.

If anyone notices flaws in the methodology, has disagreements, or anything else, I'm more than open to such a discussion. I'm not really trying to prove one thing or another. I'm just trying to build a pipeline that produces results I myself can trust so I finally know, what in the world is worth it.

If you test the models, I always love feedback. Did a MagicQuant do compression on part of the muscle that's causing you issues you'd not have with a non hybrid? Or is the Hybrid doing pretty well for you? Do you see flaws in how I'm operating or ways that it could be improved?

I've literally dumped all my logs in a `magicquant-manifest` folder on every repo so you can fully reproduce and trace everything that is occurring. And the wiki documents every detail to showcase how I build isolated samples, try to make fair comparisons, and more. I'm not really wanting to prove anything, I just want to trust my own system. Feedback helps me with that. And hopefully this interests someone enough to give it a test and validate or poke holes.

I've spent way too much time on this project.. Like, I literally had to make an entire benchmarking and quantization queue system to speed up results massively. Right now MagicQuant actually has a system that leases out NVME's as scratch disks because disk IO/latency becomes a bottleneck. I regret both everything and nothing. Thank you!

GitHub:

[GitHub Wiki - Where you can make requests, provide more feedback, etc](https://github.com/magiccodingman/MagicQuant-Wiki)

> Just a note on the wiki. I did have AI help me write it. I'm going to be rewriting a ton of the wiki to be less AI manifesto talk. I apologize for that. I have it right now that it's helping me document things as it changes. Because it's a lot. And it's very helpful, but I have been reviewing what it's writing. Just haven't gone back to actually refine and humanize it yet.

Huggingface Collection:

[Huggingface Collection For Current MagicQuant Repo's](https://huggingface.co/collections/magiccodingman/magic-quant)

> Funnily MagicQuant makes me look at quants now like I look at my quails. I see one even slightly causing a ruckus. That's bad for the flock. I guess my dog Orzo is about to get some more quail jerky.

**Quick FAQ:**

Q: Will the code/pipeline be released?

 A: Yes, I'm going to finish refining it first before posting it on my GitHub where the current wiki will also become the source code location + be renamed to not use the "-wiki" in the name. But I'd spend more time bug fixing if I released it right now. It's mostly usable in my IDE in debug mode. And the code is a mess at the moment as it has evolved so many times. But I do plan to release the code. Especially because I don't have the hardware to run a lot of the bigger models either! If others found this project interesting and helped post MagicQuants, that'd be amazing! Also I'm going through 1 more refactor where I'm highly debating making it a small web app running locally instead of a CLI. Honestly it'd make my life easier by doing so. I'm quite tempted.

Q: Is there an Imatrix?

 A: Yes, I use my own imatrix. It's ~1.5M tokens dispersed over multiple domains. If you're interested, I did document what I'm currently using on the [wiki on the imatrix-dataset page](https://github.com/magiccodingman/MagicQuant-Wiki/blob/main/wiki/docs/Imatrix-Dataset.md). But if you have suggestions to improve it, please lay it on me!

Q: Am I going to add more benchmarks?

 A: Very unlikely. I'm not trying to make a benchmark suite at every angle. It's more to answer the question of what's best within real practical use. This isn't to say proper benchmarks with harnesses and so on aren't amazing. But when sampling hundreds of models, physics becomes the biggest slow down. And within all practical reality, KLD is great for this imo, and with PPL as just a secondary smoke alarm. But again, if you have ideas, I'm not just willing to listen, but its been the advice, support, and idea building with others that'd helped me get this far in the first place. But I do have a line in the sand drawn that the tests can't increase the time to build to heat death time increase.

[32 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1tb3sja/magicquant_v20_hybrid_mixed_gguf_models_unsloth/ "32 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/MajesticAd2862](https://redlib.catsarch.com/u/MajesticAd2862)•Jun 09 '26

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[I fine-tuned Parakeet 0.6B for medical ASR — open weights, local Mac/CUDA/CPU](https://redlib.catsarch.com/r/LocalLLaMA/comments/1u0q5h9/i_finetuned_parakeet_06b_for_medical_asr_open/)

[![Image 6: Thumbnail](https://redlib.catsarch.com/preview/pre/qpcsb19ll36h1.png?width=140&height=96&auto=webp&s=a41751e0699d6bfa1f4722670dfa6e844c78e6b5) gallery](https://redlib.catsarch.com/r/LocalLLaMA/comments/1u0q5h9/i_finetuned_parakeet_06b_for_medical_asr_open/)

 64  Upvotes

I fine-tuned NVIDIA's Parakeet TDT 0.6B v2 for clinical speech and am releasing the weights as **Omi Med STT v1** (CC-BY-4.0).

Disclosure: I'm the founder of Omi Health and built this. Happy to dig into the training mix, benchmark, failure cases, quantization, or anything else.

The goal was simple: get a small local ASR model close enough to the strong cloud systems that patient audio doesn't have to leave the device for transcription.

There's also a runtime for Mac, Windows and Linux. Install + run:

```
pip install omi-med-stt
omi-med-stt consultation.wav
```

It auto-picks a backend per machine (MLX on Apple Silicon, NeMo on CUDA, GGUF/parakeet.cpp on CPU). q8 is the default; I also built a q4, benchmarked it, and _didn't_ ship it — drug-name accuracy regressed too much.

Benchmark: 1,513 clips / 7.18 h of held-out medical audio, same audio + scorer for every model, ranked by **medical-WER** (M-WER = errors on clinical terms only) since that's what matters for a scribe. Speed is RTFx (× realtime).

**vs other open / local models:**

| Model | M-WER | WER | Drug | RTFx |
| :--- | :--- | :--- | :--- | :--- |
| VibeVoice-ASR 9B | 1.78% | 11.10% | 1.36% | 11× |
| **Omi Med STT v1 (0.6B)** | **2.37%** | **8.30%** | **4.75%** | **145×** |
| Qwen3 ASR 1.7B | 3.13% | 10.72% | 6.11% | 81× |
| Qwen3 ASR 0.6B | 3.38% | 11.11% | 7.92% | 110× |
| Whisper Large v3 Turbo | 3.93% | 11.98% | 5.88% | 46× |
| Voxtral Mini Transcribe V1 | 4.53% | 13.53% | 6.33% | 78× |
| Cohere Transcribe 03-2026 | 5.05% | 14.88% | 11.09% | 143× |
| Parakeet TDT 0.6B v3 | 8.01% | 15.26% | 9.50% | 160× |
| NVIDIA Canary 1B Flash | 8.04% | 17.26% | 13.12% | 61× |
| Parakeet TDT 0.6B v2 (the base) | 8.36% | 16.45% | 8.60% | 154× |
| Google MedASR | 13.86% | 35.94% | 14.48% | 86× |

Only VibeVoice edges it on M-WER — but it's a 9B model (~15× the size), slower in my runs, and worse on overall WER (11.10% vs 8.30%). In my eval setup VibeVoice ran on an H100; Omi ran on an A10 (145× RTFx there, ~68× on an Apple-Silicon Mac). And vs the Parakeet base I started from: M-WER cut ~3.5× (8.36 → 2.37), WER roughly halved, and spurious drug mentions dropped from 131 to 9 — adapting a small base goes a long way.

**vs general-purpose cloud APIs:**

| Model | M-WER | WER | Drug | RTFx |
| :--- | :--- | :--- | :--- | :--- |
| ElevenLabs Scribe v2 | 1.39% | 6.53% | 0.23% | 7.8× |
| Gemini 3.1 Pro Preview † | 1.65% | 7.13% | 0.23% | 1.4× |
| Soniox STT Async v4 | 1.95% | 6.99% | 3.39% | 1.8× |
| **Omi Med STT v1** | **2.37%** | **8.30%** | **4.75%** | **145×** ‡ |
| Gemini 3.5 Flash † | 2.39% | 7.99% | 0.45% | 3.1× |
| Reson8 Prerecorded | 2.58% | 6.69% | 6.56% | 7.4× |
| Voxtral Mini Transcribe v2 | 2.79% | 8.12% | 5.66% | 15× |
| OpenAI GPT-4o Mini Transcribe | 3.55% | 10.26% | 3.39% | 12× |

‡ Omi's RTFx is local on-device compute (A10); the cloud figures are per-request round-trips with network + queue included, so it's not a like-for-like compute race — Omi just has a structural latency edge from running locally. † Gemini shown with its hallucinations excluded. Both Gemini models have a failure mode no other system did: on a stress lane of 420 benign, non-diagnostic clips, they ignore the audio and fabricate entire fake consultations — invented symptoms, histories, management plans (3.1 Pro on 33/420, 3.5 Flash on 87/420; every other dedicated ASR model: 0). Count that lane and their real WER is ~14% / 24%. Fine transcribers otherwise, but "fluently invents clinical detail that was never said" is quite a nasty failure if you ask me.

**vs medically-specific cloud vendors:**

| Model | M-WER | WER | Drug | RTFx |
| :--- | :--- | :--- | :--- | :--- |
| AssemblyAI Universal-3 Pro Medical | 1.81% | 6.94% | 1.36% | 2.1× |
| **Omi Med STT v1** | **2.37%** | **8.30%** | **4.75%** | **145×** ‡ |
| Deepgram Nova-3 Medical | 2.44% | 7.33% | 2.26% | 7.7× |
| Corti Transcripts | 5.12% | 9.60% | 11.31% | 0.9× |

‡ Again, Omi's RTFx is on-device local compute; the cloud APIs are network round-trips (see note above).

Challenger here — ahead of Deepgram and Corti on M-WER, behind AssemblyAI (and the strongest general scribes). Drug names are the weakest axis (4.75% drug M-WER) and the #1 thing I'm fixing for v2.

Overall: best locally-running open model on this set, and competitive with the cloud — while keeping audio on the device.

**More on training and evaluation:** ~127 h of training audio, roughly 71% real / 29% synthetic — a mix of licensed, openly-available, and my own synthetic set tailored for hard-to-source medical speech. The benchmark is a locked split that was never touched during training (0 train/test overlap), made of unpublished audio that's diverse across medical settings (GP dialogue, dictation, medication review, radiology, procedures, long-form).

Curious whether real-world use matches the benchmark — would genuinely value the feedback. Next up: a streaming version and a multilingual one. **Which languages would you actually want? Drop them in the comments.**

[25 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1u0q5h9/i_finetuned_parakeet_06b_for_medical_asr_open/ "25 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/KokaOP](https://redlib.catsarch.com/u/KokaOP)•Jun 13 '26

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[ZONOS2: real-time TTS with 8B params, 900M active, and high-fidelity voice cloning](https://redlib.catsarch.com/r/LocalLLaMA/comments/1u4lk5c/zonos2_realtime_tts_with_8b_params_900m_active/)

 85  Upvotes

[https://reddit.com/link/1u4lk5c/video/kyhdw0uog07h1/player](https://redlib.catsarch.com/link/1u4lk5c/video/kyhdw0uog07h1/player)

Links:

*   Blog: [https://zyphra.com/our-work/zonos2](https://zyphra.com/our-work/zonos2)
*   Weights: [https://huggingface.co/Zyphra/ZONOS2](https://huggingface.co/Zyphra/ZONOS2)
*   Inference code: [https://github.com/Zyphra/ZONOS2](https://github.com/Zyphra/ZONOS2)
*   Eval code: [https://github.com/Zyphra/ZTTS1-Eval](https://github.com/Zyphra/ZTTS1-Eval)

| Model | TTSDS Prosody Score ↑ |
| :--- | :--- |
| **ZONOS2 8B** | **88.7** |
| Qwen 3 TTS 1.7B | 87.6 |
| Inworld TTS 2 | 87.5 |
| Cartesia Sonic 3.5 | 87.1 |
| Fish S2 Pro | 86.6 |
| VoxCPM 2 | 86.3 |
| Gemini 3.1 Flash | 85.7 |
| ZONOS2 8B (Quality Mode) | 85.6 |
| ElevenLabs V3 | 83.2 |

Zyphra has released **ZONOS2**, its next-generation real-time text-to-speech model focused on expressive, high-fidelity voice cloning. It is open-source under **Apache 2.0** and also available on **Zyphra Cloud** on AMD hardware.

The model is designed to solve the usual TTS tradeoff between quality and speed. Zyphra says ZONOS2 is the **first sparse MoE TTS model released open-source**, with **8B total parameters** and **900M active parameters** at inference. The goal is straightforward: fast, efficient, and expressive speech synthesis without the usual compromise pileup.

A major focus is **voice cloning**. Zyphra claims ZONOS2 is especially strong at capturing the distinctive characteristics of a speaker, producing more natural-sounding clones across a wide range of voices. The cloning is **zero-shot**, so no fine-tuning is needed.

On the audio side, ZONOS2 predicts **Descript Audio Codec (DAC) tokens** for **44.1 kHz** studio-quality audio. That gives better fidelity, but is harder to model than lower-quality codec setups. Zyphra says it closes that gap through larger-scale model and data training.

For text handling, ZONOS2 does **not use a phonemizer**. Instead, it reads **raw UTF-8 bytes**, which Zyphra says improves coverage for lower-resource languages, boosts performance on Chinese, Korean, and Japanese, and supports native code-switching mid-sentence.

Training also scaled heavily, from roughly **200K hours** to **6M+ hours** of audio. Zyphra says it used staged data filtering with increasing transcript-agreement strictness across pretraining, midtraining, and annealing. The intended result is fewer hallucinations, mispronunciations, and repetitions.

Zyphra is also releasing **ZTTS1-Eval**, a new benchmark for TTS evaluation. It includes clean and in-the-wild datasets across up to **17 languages**, with newer evaluation models such as **Qwen3-ASR, ReDimNet, and MSR-UTMOS**, plus prosody metrics.

That is the gist. Big model, open weights, Apache 2.0, voice cloning, and enough infrastructure behind it to make the old TTS baseline look like scrap metal.

[20 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1u4lk5c/zonos2_realtime_tts_with_8b_params_900m_active/ "20 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/Revolutionary_Ask154](https://redlib.catsarch.com/u/Revolutionary_Ask154)•May 16 '26

## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[Can a 5090 with qwen3.6 achieve > 3,000 tok/s ? bring your pitchforks (open-dllm)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1tee5ms/can_a_5090_with_qwen36_achieve_3000_toks_bring/)

[![Image 7: Thumbnail](https://redlib.catsarch.com/preview/pre/4foy9m8e2e1h1.png?width=140&height=71&auto=webp&s=b4976dc7d9ee7ac388befbe904aafb6bd4146730) gallery](https://redlib.catsarch.com/r/LocalLLaMA/comments/1tee5ms/can_a_5090_with_qwen36_achieve_3000_toks_bring/)

 50  Upvotes

so background - these people. Fred Zhangzhi Peng, Shuibai Zhang, Alex Tong, worked on converting AR -> diffusion (its already working from older models).

this has a smaller qwen 2.5 working ->

[https://github.com/pengzhangzhi/Open-dLLM](https://github.com/pengzhangzhi/Open-dLLM)

but it begs question if we can upgrade it and push to 3.6....

(it's just theoretical at moment / none one has done it - likely would takes weeks of compute 8x a100)

[https://oval-shell-31c.notion.site/Open-dLLM-Open-Diffusion-Large-Language-Model-25e03bf6136480b7a4ebe3d53be9f68a](https://oval-shell-31c.notion.site/Open-dLLM-Open-Diffusion-Large-Language-Model-25e03bf6136480b7a4ebe3d53be9f68a)

I forked the codebase - ran it through opencode with free deepseek-flash / GLM5.1 overnight to upgrade to support qwen3.6 - because codebase is > 6 mths old - i got AI to mash up LDLM a most recent paper in the mix [https://arxiv.org/pdf/2605.07933v1](https://arxiv.org/pdf/2605.07933v1) Viacheslav Meshchaninov1 , Alexander Shabalin1 , Egor Chimbulatov2 , Nikita Gushchin3,4, Ilya Koziev5 , Alexander Korotin3,4, Dmitry Vetrov1 - these guys spent 3 years working on getting this paper working.

[https://x.com/Viacheslav91112/status/2054613430082957443?s=20](https://x.com/Viacheslav91112/status/2054613430082957443?s=20)

I asked it to build config for qwen 3.6 model + upgrade with LDLM and spit ball some numbers on outputs with "honest" assumptions - big one is sequence length - throughput likely to fall off with higher outputs.

# Inference Throughput (Qwen3.6 LDLM, untrained, RTX 5090 32GB)

| Model | Dim | Trainable Params | Diffusion Steps | Throughput |
| :--- | :--- | :--- | :--- | :--- |
| Qwen3.6-35B-A3B | 2048 | 1.39B | 10 | **3,238 tok/s** |
| Qwen3.6-35B-A3B | 2048 | 1.39B | 4 | **~6,500 tok/s** |
| Qwen3.6-27B | 5120 | 6.75B | 10 | **745 tok/s** |
| Qwen3.6-27B | 5120 | 6.75B | 4 | **~1,500 tok/s** |

# Assumptions & Caveats

*   **Untrained weights**: These benchmarks use randomly initialized Perceiver/decoder/diffusion-head weights. A trained model will have identical throughput but produce coherent output. Quality benchmarks (perplexity, HumanEval) will be published after training completes.
*   **No encoder in the loop**: The frozen Qwen3.6 encoder is**not used during generation**— it's only needed for training (to produce latent targets). At inference, the diffusion head denoises random noise, then the Perceiver decoder maps latents to tokens. The encoder is deleted before benchmarking (`del autoencoder.token_encoder`).
*   **Seq len = 64**: The benchmark uses a short sequence length (64 tokens). Longer sequences will reduce throughput proportionally. The 4-step throughput numbers are linear extrapolations from the 10-step measurements.
*   **Batch size = 1**: Single-sequence generation only. Throughput scales near-linearly with batch size for the 35B-A3B (dim=2048 fits easily in VRAM), less so for the 27B (dim=5120).
*   **CPU RAM requirement**: While the encoder is not used at inference, it**must**fit in system RAM during training (~54GB for 27B, ~22GB for 35B-A3B in bf16). The Qwen3.6 architecture uses Triton kernels (flash-linear-attention) that cannot run on CPU, so the encoder forward pass during training requires GPU offloading — a multi-GPU setup is recommended for training.
*   **Qwen3.6 requires**`trust_remote_code=True`: The model uses custom architecture code (`Qwen3_5ForConditionalGeneration`) that is not in standard transformers releases. Ensure your`transformers`version supports it (>=4.54).
*   **35B-A3B is MoE**: Only 3B of its 35B parameters are active per token, giving it a much smaller hidden dim (2048) than the 27B dense model (5120). This is why the LDLM trainable components are 5x smaller and 4x faster.
*   **Not an apples-to-apples comparison with AR models**: The diffusion model generates all tokens in parallel across N diffusion steps, while AR generates one token at a time. The "tok/s" metric favors diffusion for short sequences but does not reflect output quality, which depends on training convergence.

Code is here - with git issues enabled

[https://github.com/scrya-com/Open-dLLM](https://github.com/scrya-com/Open-dLLM)

wandb training metrics

[https://wandb.ai/snoozie/Qwen3.6-35B-A3B-LDLM?nw=nwusersnoozie](https://wandb.ai/snoozie/Qwen3.6-35B-A3B-LDLM?nw=nwusersnoozie)

If anyone has spare [vast.ai](http://vast.ai/) credits / azure credits / google credits hook me up

UPDATE -

from back of the envelope maths - for 35B

Component Size (35B params)

─────────────────────────────────────────────────────

Weights (bf16) 70 GB ← what Q4 reduces (to 21 GB)

Weights (Q4) 21 GB ← saving: -49 GB

Gradients (bf16) 70 GB ← unchanged

FP32 master copy 140 GB ← unchanged, required by mixed-precision

Adam moments (m, v) FP32 280 GB ← unchanged, dominant cost

Adam moments (m, v) FP32 280 GB ← unchanged, dominant cost

Activations / comms 15 GB ← unchanged

────────

Total trainable state ~625 GB (vs ~630 GB with bf16 weights)

Minimum sane: 8× H100 80 GB, ~$25/hr cloud, ~$500 for a 1-epoch run.

- Alternative: 4× H200 141 GB, similar cost.

[27 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1tee5ms/can_a_5090_with_qwen36_achieve_3000_toks_bring/ "27 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/iam31337](https://redlib.catsarch.com/u/iam31337)•1d ago

## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[Qwen3.8-27B at 5.01 BPW: 256K context, Q4_1-level PPL and 50.44 tok/s on a 24 GB Blackwell](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vraqpb/qwen3827b_at_501_bpw_256k_context_q4_1level_ppl/)

[Video 4](about:blank)

 15  Upvotes

The goal was simple enough: squeeze Qwen3.8-27B, embedded MTP included, and its full 262,144-token context into an RTX PRO 4000 Blackwell SFF without wrecking the model.

The final run used 23,952 of 24,467 MiB on GPU0, so 97.9% of the card, with 515 MiB left after genuinely filling 261,500 tokens. The F16 vision projector sits on a second GPU and takes another 982 MiB.

For calibration I put real production history ahead of the generic corpus: 5,472 messages from 296 Hermes agent sessions covering coding, tool calls, infrastructure work and mixed Polish/English conversations.

llama-imatrix measured 497 target weights and I used that ranking as a tensor map. Bulk matrices got native NVFP4. The sensitive stuff, attention, DeltaNet and FFN tensors, went to Q5_K or Q6_K. Embeddings are Q6_K, the output head Q8_0, and the embedded MTP layer is NVFP4.

That gives a 16,321 MiB GGUF at 5.01 BPW. On WikiText-2 it scored 6.1197 PPL against 6.1127 for Q4_1, a 0.11% gap that's inside the noise of a test this short. A ready-made NVFP4 quant landed at 6.4949, so FP4 everywhere was just too aggressive for this model.

Performance, averaged over 10 runs: 50.441 tok/s in production. Target-only decode does 21.189, MTP pushes it to 59.456, so 2.81x. My llama.cpp build does 55.402 against 45.422 on clean master, +21.97%. At a genuinely full 261.5K context, decode drops to 12.606 tok/s and prefill manages 226.750.

The card has 432 GB/s of specified peak bandwidth. Decode is already bandwidth-sensitive, but a packed 261.5K context adds heavy KV reads from the 16 full-attention layers. That is why the same profile averages around 50 tok/s during normal work and falls to 12.61 tok/s at the far end of the cache.

The weirdest finding was MTP. Adding 69.2 MiB of higher-precision weights made it 26.6% slower, because the more precise drafter matched the quantized target less often.

Model I built, quantized and published:[https://huggingface.co/cdiamond/Qwen3.8-27B-iMatrix-NVFP4-MTP-GGUF](https://huggingface.co/cdiamond/Qwen3.8-27B-iMatrix-NVFP4-MTP-GGUF)

Full write-up with tensor recipe, llama.cpp patches, runtime args and failed experiments:[https://piszczek.pl/blog/qwen38-27b-256k-50-tps-24gb-gpu](https://piszczek.pl/blog/qwen38-27b-256k-50-tps-24gb-gpu)

_English isn't my first language. The experiments, measurements and conclusions are mine; AI only helped with wording_

[](https://redlib.catsarch.com/submit/?source_id=t3_1vr7ktn&composer_entry=crosspost_prompt)

[14 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vraqpb/qwen3827b_at_501_bpw_256k_context_q4_1level_ppl/ "14 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/SandyL925](https://redlib.catsarch.com/u/SandyL925)•5d ago

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[SenseNova-Vision: a 7B open model that does segmentation, depth, detection, OCR, and 3D reconstruction with no task-specific heads](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vndd6p/sensenovavision_a_7b_open_model_that_does/)

[![Image 8: Thumbnail](https://redlib.catsarch.com/preview/pre/qmqmdq21n5jh1.png?width=140&height=95&auto=webp&s=da014edae2fa57327ed4ec9791c72c9cc6edf048) gallery](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vndd6p/sensenovavision_a_7b_open_model_that_does/)

 83  Upvotes

Stumbled across this new vision model, SenseNova-Vision. It's a 7B MoT model, Apache 2.0 license, which is cool. The main idea is it treats pretty much all computer vision stuff as just one generation problem. Like, instead of needing a bunch of different models for detection, segmentation, depth, whatever, this one model handles it all.

You just give it a natural language instruction, maybe some visual hints, and it spits out text, images, or both. For text, it can do things like categories, bounding boxes, OCR, keypoints, camera angles. And for images, it's doing segmentation masks, depth maps, surface normals, even multi-view point maps. You can mix and match for more complex tasks.

No special prediction heads or decoders, which is kinda neat. Just one set of weights, and the prompt tells it what to do.

So it can do the usual stuff: object detection, keypoints, OCR, all kinds of segmentation (binary, instance, semantic), depth and surface normal estimation. But the really interesting bits, for me anyway, are the multi-view 3D reconstruction and camera pose estimation.

They actually added dedicated benchmarks for those in the latest update. Usually, you'd need specialized tools like COLMAP for that kind of multi-view reconstruction from multiple images, but this model just does it with a single prompt. That's kinda wild if it works well.

They trained it on a massive dataset, 50M instruction-response pairs, built from a bunch of different CV annotations. And it started from an existing multimodal model, so no crazy new architecture there.

There's a web demo if you wanna mess around with it, and the weights are up on Hugging Face too.

Just a heads up though, before you get too hyped: the full web demo needs a beefy GPU, like 1x80GB. And for benchmarking, they're talking 8x80GB. So, yeah, not really something you're gonna run on your average consumer card. It just dropped on July 8th, so probably expect some rough edges. Also, they've released the training pipeline and data prep stuff if anyone's looking to train or fine-tune it.

GitHub: [https://github.com/OpenSenseNova/SenseNova-Vision](https://github.com/OpenSenseNova/SenseNova-Vision)

Honestly, I'm super curious if anyone's actually tried the multi-view reconstruction part on their own image sets yet. That's the bit I really want to test out.

[7 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vndd6p/sensenovavision_a_7b_open_model_that_does/ "7 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/WinterCharm](https://redlib.catsarch.com/u/WinterCharm)•16d ago

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[[Release] WinterMix — Qwen3.5-122B-A10B in native MLX: an 82 GiB build that beats 94–95 GiB quants, plus a 68 GiB build for agent swarms](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vdcs8e/release_wintermix_qwen35122ba10b_in_native_mlx_an/)

 33  Upvotes

**TL;DR:** I spent 9 days developing a new quantization method for MLX models and measured 18 variants against each other on a single M5 Max MacBook Pro (128 GB). The result is the best-measuring MLX quant of Qwen3.5-122B-A10B I'm aware of at _any_ size — the 82 GiB build edges out 94–95 GiB 6-bit builds, and lands **within 0.3–0.7% of the imatrix-rounded source GGUF while staying native MLX**. Apache 2.0, weights up on HF.

# Why bother if GGUF is better?

MLX on Apple Silicon is substantially faster than llama.cpp on the same hardware — on my M5 Max I measure roughly 9x faster prefill and ~20% faster token generation. For anything with a long context and a lot of turns, that gap compounds.

The problem is that existing MLX quants below 6 bit are not great, and you can see it in the table below: oQ4 gives up ~3.8% perplexity at short context and ~4.2% at long context against the source GGUF. In practice that shows up as incoherent reasoning traces and rounding errors that stack until the model starts hallucinating.

So a better MLX quantization method has real advantages for agentic workflows and local AI on Apple Silicon. At the same time, I made the conscious decision to require **native MLX support**. imatrix on MLX is not _format native_ — it needs custom kernels. WinterMix quants are format native and are drop-in replacements.

**WinterMix quantized models are format-native MLX models with open weights (Apache 2.0).** No custom kernels, no forked runtime, no flags. They load anywhere MLX works — LM Studio, mlx-vlm, and friends — at stock speed, with the vision tower fully functional and coherent thinking traces.

If you just want to try it: download the repo below, point LM Studio at it, done.

## HuggingFace Links

**[WinterMix58](https://huggingface.co/WinterCharm/Qwen3.5-122B-A10B-wMix58)** — 82 GiB, ~6.0 bpw: the best-measuring MLX quant of this model I'm aware of at _any_ size, including against 94–95 GiB 6-bit oMLX builds (narrowly at 2K, more clearly at 16K).

**[WinterMix48](https://huggingface.co/WinterCharm/Qwen3.5-122B-A10B-wMix48)** — 68 GiB, ~5.0 bpw: leaves ~35–40 GB free on a 128 GB Mac = **5–8 parallel 100K-token agent sessions resident at once** (GDN architecture keeps a 100K session's cache at ~5–10 GB). Beats its direct size-peer (oQ4, 67 GiB) by ~1.4–1.5% at both context lengths.

## Numbers

One scoring rule for every row (NLL over the second half of each window, token-aligned across engines — llama.cpp's native rule, so these are comparable to Unsloth's), paired per-token where both models run under MLX. Reference rows were measured on my own harness: same tokens, same machine. oMLX quants are included because oMLX is currently the popular option for MLX.

All rows are Qwen3.5-122B-A10B in various quantization mixes.

| model | GiB | short-2K ppl | long-16K ppl |
| --- | --- | --- | --- |
| Unsloth UD-Q5_K_XL GGUF (llama.cpp) | 85.6 | **4.2343** | **4.3845** |
| 6-bit-expert RTN transfer (MLX) | 95 | 4.2504 | 4.4424 |
| oQ6 (oMLX) | 94 | 4.2538 | 4.4172 |
| **WinterMix58** | **82** | **4.2481** | **4.4149** |
| oQ5 (oMLX) | 80 | 4.2904 | 4.4493 |
| **WinterMix48** | **68** | **4.3276** | **4.5038** |
| oQ4 (oMLX) | 67 | 4.3933 | 4.5679 |

Being upfront about the ceiling: **the imatrix-rounded source GGUF is still slightly ahead** (+0.3–0.7% rule-matched). Matching imatrix-style weighted rounding in MLX would need custom inference kernels, and "loads in everything at stock speed" was a hard constraint I wasn't willing to break. Within the native format, this appears to be about the limit.

## The part I think is actually interesting

Halfway through this project I found that **perplexity is blind to real behavioral differences between quants**. Two builds with statistically identical NLL differed 2.5× in how often they self-interrupt ("wait, let me re-check...") during 50K-token reasoning traces. Then the reverse bit me: my best-NLL build had an _elevated_ self-interruption count — and actually reading the traces showed it wasn't confusion at all, but disciplined audit passes that twice caught a base-model reasoning bug before the final answer.

So the release models were selected on three instruments: paired NLL, blind-scored state-tracking benchmarks at depth, and directly reading the reasoning traces. Both releases deliver perfect scores on a 30-step adversarial state-tracking task on every seed — and the 68 GiB build's traces show it catching its own 4-bit arithmetic slips before they reach the output. If you evaluate quants, I'd honestly recommend reading traces over counting anything.

## What's under the hood (briefly)

Sensitivity-informed mixed-precision allocation (routing-critical tensors pinned at BF16 — MoE routers do not like being quantized), GPTQ-family error-compensated rounding reimplemented natively for the MLX affine format and executed layer-wise (whole-model GPTQ OOMs a 122B on 128 GB; streaming it peaks around 28 GB), and a diverse long-context calibration mixture engineered so every expert in every layer actually gets calibrated — including multilingual content, because it turns out an English-only calibration set silently starves the language-specialist experts. Validated across 18 measured variants with paired controls and held-out out-of-domain checks (no calibration binding: code/math within ±0.1% of RTN).

I'm not releasing the pipeline code for now — the models are open weights (Apache 2.0), the method writeup stays private. The M5 Max kernel-panicked ten times during development before I got the workload tamed, if that helps set the vibe.

## Requests

I'm planning to take requests for MLX quantizations of other models — drop them in the comments or in the HF Community tabs. Practical constraints: it has to fit the pipeline on a 128 GB Mac (up to ~120B+ MoE is proven), and dense models calibrate differently than MoE, so results may vary until I've tuned per-architecture.

Happy to answer questions about the eval methodology, the behavioral testing, Apple Silicon quirks (ask me about watchdog panics), or Mac long-context agent setups.

[12 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vdcs8e/release_wintermix_qwen35122ba10b_in_native_mlx_an/ "12 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/sunshinecheung](https://redlib.catsarch.com/u/sunshinecheung)•Apr 28 '25

## [News](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22News%22&restrict_sr=on)[Qwen3 ReadMe.md](https://redlib.catsarch.com/r/LocalLLaMA/comments/1k9rm65/qwen3_readmemd/)

 250  Upvotes

# Qwen3 Highlights

Qwen3 is the latest generation of large language models in Qwen series, offering a comprehensive suite of dense and mixture-of-experts (MoE) models. Built upon extensive training, Qwen3 delivers groundbreaking advancements in reasoning, instruction-following, agent capabilities, and multilingual support, with the following key features:

*   **Uniquely support of seamless switching between thinking mode**(for complex logical reasoning, math, and coding) and**non-thinking mode**(for efficient, general-purpose dialogue)**within single model**, ensuring optimal performance across various scenarios.
*   **Significantly enhancement in its reasoning capabilities**, surpassing previous QwQ (in thinking mode) and Qwen2.5 instruct models (in non-thinking mode) on mathematics, code generation, and commonsense logical reasoning.
*   **Superior human preference alignment**, excelling in creative writing, role-playing, multi-turn dialogues, and instruction following, to deliver a more natural, engaging, and immersive conversational experience.
*   **Expertise in agent capabilities**, enabling precise integration with external tools in both thinking and unthinking modes and achieving leading performance among open-source models in complex agent-based tasks.
*   **Support of 100+ languages and dialects**with strong capabilities for**multilingual instruction following**and**translation**.

# Model Overview

**Qwen3-0.6B**has the following features:

*   Type: Causal Language Models
*   Training Stage: Pretraining & Post-training
*   Number of Parameters: 0.6B
*   Number of Paramaters (Non-Embedding): 0.44B
*   Number of Layers: 28
*   Number of Attention Heads (GQA): 16 for Q and 8 for KV
*   Context Length: 32,768

For more details, including benchmark evaluation, hardware requirements, and inference performance, please refer to our[blog](https://qwenlm.github.io/blog/qwen3/),[GitHub](https://github.com/QwenLM/Qwen3), and[Documentation](https://qwen.readthedocs.io/en/latest/).

# witching Between Thinking and Non-Thinking Mode

Tip

The`enable_thinking`switch is also available in APIs created by vLLM and SGLang. Please refer to[our documentation](https://qwen.readthedocs.io/)for more details.

# enable_thinking=True

By default, Qwen3 has thinking capabilities enabled, similar to QwQ-32B. This means the model will use its reasoning abilities to enhance the quality of generated responses. For example, when explicitly setting`enable_thinking=True`or leaving it as the default value in`tokenizer.apply_chat_template`, the model will engage its thinking mode.

```
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=True  # True is the default value for enable_thinking
)
```

In this mode, the model will generate think content wrapped in a`<think>...</think>`block, followed by the final response.

Note

For thinking mode, use`Temperature=0.6`,`TopP=0.95`,`TopK=20`, and`MinP=0`(the default setting in`generation_config.json`).**DO NOT use greedy decoding**, as it can lead to performance degradation and endless repetitions. For more detailed guidance, please refer to the[Best Practices](https://gist.github.com/ibnbd/5ec32ce14bde8484ca466b7d77e18764#best-practices)section.

# enable_thinking=False

We provide a hard switch to strictly disable the model's thinking behavior, aligning its functionality with the previous Qwen2.5-Instruct models. This mode is particularly useful in scenarios where disabling thinking is essential for enhancing efficiency.

```
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=False  # Setting enable_thinking=False disables thinking mode
)
```

In this mode, the model will not generate any think content and will not include a`<think>...</think>`block.

Note

For non-thinking mode, we suggest using`Temperature=0.7`,`TopP=0.8`,`TopK=20`, and`MinP=0`. For more detailed guidance, please refer to the[Best Practices](https://gist.github.com/ibnbd/5ec32ce14bde8484ca466b7d77e18764#best-practices)section.

# Advanced Usage: Switching Between Thinking and Non-Thinking Modes via User Input

We provide a soft switch mechanism that allows users to dynamically control the model's behavior when`enable_thinking=True`. Specifically, you can add`/think`and`/no_think`to user prompts or system messages to switch the model's thinking mode from turn to turn. The model will follow the most recent instruction in multi-turn conversations.

# Agentic Use

Qwen3 excels in tool calling capabilities. We recommend using[Qwen-Agent](https://github.com/QwenLM/Qwen-Agent)to make the best use of agentic ability of Qwen3. Qwen-Agent encapsulates tool-calling templates and tool-calling parsers internally, greatly reducing coding complexity.

To define the available tools, you can use the MCP configuration file, use the integrated tool of Qwen-Agent, or integrate other tools by yourself.

# Best Practices

To achieve optimal performance, we recommend the following settings:

1.   **Sampling Parameters**: 
    *   For thinking mode (`enable_thinking=True`), use`Temperature=0.6`,`TopP=0.95`,`TopK=20`, and`MinP=0`.**DO NOT use greedy decoding**, as it can lead to performance degradation and endless repetitions.
    *   For non-thinking mode (`enable_thinking=False`), we suggest using`Temperature=0.7`,`TopP=0.8`,`TopK=20`, and`MinP=0`.
    *   For supported frameworks, you can adjust the`presence_penalty`parameter between 0 and 2 to reduce endless repetitions. However, using a higher value may occasionally result in language mixing and a slight decrease in model performance.

2.   **Adequate Output Length**: We recommend using an output length of 32,768 tokens for most queries. For benchmarking on highly complex problems, such as those found in math and programming competitions, we suggest setting the max output length to 38,912 tokens. This provides the model with sufficient space to generate detailed and comprehensive responses, thereby enhancing its overall performance.
3.   **Standardize Output Format**: We recommend using prompts to standardize model outputs when benchmarking. 
    *   **Math Problems**: Include "Please reason step by step, and put your final answer within \boxed{}." in the prompt.
    *   **Multiple-Choice Questions**: Add the following JSON structure to the prompt to standardize responses: "Please show your choice in the`answer`field with only the choice letter, e.g.,`"answer": "C"`."

4.   **No Thinking Content in History**: In multi-turn conversations, the historical model output should only include the final output part and does not need to include the thinking content. It is implemented in the provided chat template in Jinja2. However, for frameworks that do not directly use the Jinja2 chat template, it is up to the developers to ensure that the best practice is followed.

# Citation

If you find our work helpful, feel free to give us a cite.

```
@misc{qwen3,
    title  = {Qwen3},
    url    = {https://qwenlm.github.io/blog/qwen3/},
    author = {Qwen Team},
    month  = {April},
    year   = {2025}
}
```

From: [https://gist.github.com/ibnbd/5ec32ce14bde8484ca466b7d77e18764#switching-between-thinking-and-non-thinking-mode](https://gist.github.com/ibnbd/5ec32ce14bde8484ca466b7d77e18764#switching-between-thinking-and-non-thinking-mode)

[43 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1k9rm65/qwen3_readmemd/ "43 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/ResearchCrafty1804](https://redlib.catsarch.com/u/ResearchCrafty1804)•Sep 08 '25

## [News](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22News%22&restrict_sr=on)[Qwen released API (only) Qwen3-ASR — the all-in-one speech recognition model!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1nbqa1p/qwen_released_api_only_qwen3asr_the_allinone/)

[![Image 9: Post image](https://redlib.catsarch.com/img/et1syg58iynf1.jpeg)](https://redlib.catsarch.com/img/et1syg58iynf1.jpeg)

 181  Upvotes

🎙️ Meet Qwen3-ASR — the all-in-one speech recognition model!

✅ High-accuracy EN/CN + 9 more languages: ar, de, en, es, fr, it, ja, ko, pt, ru, zh

✅ Auto language detection

✅ Songs? Raps? Voice with BGM? No problem. <8% WER

✅ Works in noise, low quality, far-field

✅ Custom context? Just paste ANY text — names, jargon, even gibberish 🧠

✅ One model. Zero hassle.Great for edtech, media, customer service & more.

API: [https://bailian.console.alibabacloud.com/?tab=doc#/doc/?type=model&url=2979031](https://bailian.console.alibabacloud.com/?tab=doc#/doc/?type=model&url=2979031)

Modelscope Demo: [https://modelscope.cn/studios/Qwen/Qwen3-ASR-Demo](https://modelscope.cn/studios/Qwen/Qwen3-ASR-Demo)

Hugging Face Demo: [https://huggingface.co/spaces/Qwen/Qwen3-ASR-Demo](https://huggingface.co/spaces/Qwen/Qwen3-ASR-Demo)

Blog: [https://qwen.ai/blog?id=41e4c0f6175f9b004a03a07e42343eaaf48329e7&from=research.latest-advancements-list](https://qwen.ai/blog?id=41e4c0f6175f9b004a03a07e42343eaaf48329e7&from=research.latest-advancements-list)

[35 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1nbqa1p/qwen_released_api_only_qwen3asr_the_allinone/ "35 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/fuckAIbruhIhateCorps](https://redlib.catsarch.com/u/fuckAIbruhIhateCorps)•Jun 16 '26

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[A benchmark for tiny LLMs based on a real world problem: natural language file search (using monkeSearch)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1u7kwim/a_benchmark_for_tiny_llms_based_on_a_real_world/)

 11  Upvotes

[![Image 10](https://redlib.catsarch.com/preview/pre/8acpx3xbmo7h1.png?width=2158&format=png&auto=webp&s=e0b6797405e842671ebe78e9655fedff7982d9ee)](https://redlib.catsarch.com/preview/pre/8acpx3xbmo7h1.png?width=2158&format=png&auto=webp&s=e0b6797405e842671ebe78e9655fedff7982d9ee)

monke see monke do

Hi everyone! I've been working on this benchmark lately which tests small llms (<3b) to run a test set of approximately 80 queries to find small models which perform well. The whole idea of this project (monkesearch) was to bring natural language file search to potato pcs and use small enough models which could purely run off of CPU inference. I wanted this feature for myself and also keep it totally local, so I built monkesearch last year, and the bare bones prototype received a very positive response. (almost at 200 stars on github!)

I built a benchmark that tests how well small LLMs (0.3B-3B params) parse natural language into structured JSON — specifically extracting file_type, temporal context, and specificity from search-like queries (e.g. "python scripts from 3 days ago" → `{"file_types": ["py"], "time_unit": "days", "time_unit_value": "3"}`).

Each model runs 80 queries across 4 categories:

*   File Type - mapping "python scripts" → .py, "images" → .jpg,.png
*   Temporal Awareness- parsing "last week", "3 days ago", "yesterday" into date ranges
*   Specificity - distinguishing specific files from broad categories
*   Combined - mixing all three in one query

Currently tested models: Gemma-3 270M, SmolLM2 360M, Qwen2.5 0.5B, Qwen3 0.6B, Qwen3.5 0.8B, MiniCPM5 1B, TinyLlama 1.1B, LFM2.5 1.2B, DeepSeek R1 Distill 1.5B.

Results so far show 0.8B–1.5B models performing significantly better than sub-0.5B. But I believe finetuning the small contestants would be a good bet?

Also! My main motive to post it here to get some suggestions on what models should i add to the above benchmark and just some guidance on how to move forward with this project.

The url: [https://monkesearch.github.io/](https://monkesearch.github.io/)

[11 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1u7kwim/a_benchmark_for_tiny_llms_based_on_a_real_world/ "11 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/Logical-Employ-9692](https://redlib.catsarch.com/u/Logical-Employ-9692)•Mar 23 '26

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[How political censorship actually works inside Qwen, DeepSeek, GLM, and Yi: Ablation and behavioral results across 9 models](https://redlib.catsarch.com/r/LocalLLaMA/comments/1s1lmuj/how_political_censorship_actually_works_inside/)

 29  Upvotes

New paper studying the internal mechanisms of political censorship in Chinese-origin LLMs:[https://arxiv.org/abs/2603.18280](https://arxiv.org/abs/2603.18280)

Findings relevant to this community:

**On Qwen/Alibaba - the generational shift:**Across Qwen2.5-7B → Qwen3-8B → Qwen3.5-4B → Qwen3.5-9B, hard refusal went from 6.2% to 25% to 0% to 0%. But steering (CCP narrative framing) rose from 4.33/5 to 5.00/5 over the same period. The newest Qwen models don't refuse - they answer everything in maximally steered language. Any evaluation that counts refusals would conclude Qwen3.5 is _less_ censored. It isn't.

**On Qwen3-8B - the confabulation problem:**When you surgically remove the political-sensitivity direction, Qwen3-8B doesn't give factual answers. It substitutes Pearl Harbor for Tiananmen and Waterloo for the Hundred Flowers campaign. 72% confabulation rate. Its architecture entangles factual knowledge with the censorship mechanism. Safety-direction ablation on the same model produces 0% wrong events, so it's specific to how Qwen encoded political concepts.

**On GLM, DeepSeek, Phi - clean ablation:**Same procedure on these three models produces accurate factual output. Zero wrong-event confabulations. Remove the censorship direction and the model simply answers the question.

**On Yi - detection without routing:**Yi-1.5-9B detects political content at every layer (probes work) but never refuses (0% English, 6.2% Chinese) and shows no steering. It recognized the sensitivity and did nothing with it. Post-training never installed a routing policy for political content. This is direct evidence that concept detection and behavioral routing are independently learned.

**On cross-model transfer:**Qwen3-8B's political direction applied to GLM-4-9B: cosine 0.004. Completely meaningless. Different labs built completely different geometry. There's no universal "uncensor" direction.

**On the 46-model screen:**Only 4 models showed strong CCP-specific discrimination at n=32 prompts (Baidu ERNIE, Qwen3-8B, Amazon Nova, Meituan). All Western frontier models: zero. An initial n=8 screen was misleading - Moonshot Kimi-K2 dropped from +88pp to +9pp, DeepSeek v3-0324 from +75pp to -3pp, MiniMax from +61pp to 0pp. Small-sample behavioral claims are fragile.

Paper:[https://arxiv.org/abs/2603.18280](https://arxiv.org/abs/2603.18280)

Happy to answer questions.

[19 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1s1lmuj/how_political_censorship_actually_works_inside/ "19 comments")

[NEXT](https://redlib.catsarch.com/r/LocalLLaMA/search?q=qwen3.8%20chinese%20language%20mixing&restrict_sr=on&sort=relevance&t=all&after=t3_1s1lmuj)

v0.36.0 [ⓘ View instance info](https://redlib.catsarch.com/info "View instance information")[<> Code](https://github.com/redlib-org/redlib "View code on GitHub")
