Title: Redlib: search results - korean

URL Source: https://redlib.catsarch.com/r/LocalLLaMA/search?q=korean&restrict_sr=on&sort=relevance&t=all

Markdown Content:
## [News](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22News%22&restrict_sr=on)[[D] A mathematical proof from an anonymous Korean forum: The essence of Attention is fundamentally a d^2 problem, not n^2. (PDF included)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rl54v7/d_a_mathematical_proof_from_an_anonymous_korean/)

192  Upvotes

Hello, [r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA). I am just a regular user from a Korean AI community ("The Singularity Gallery"). I recently came across an anonymous post with a paper attached. I felt that the mathematical proof inside was too important to be buried in a local forum and not go viral globally, so I used Gemini to help me write this English post to share it with you all.

The author claims they do not work in the LLM industry, but they dropped a paper titled: "The d^2 Pullback Theorem: Why Attention is a d^2-Dimensional Problem".

They argue that the field has been fundamentally misunderstanding the intrinsic geometry of Attention. Here is the core of their mathematical proof:

1.   The d^2 Pullback Theorem (The Core Proof):

The author mathematically proves that if you combine the Forward pass (n X n) and the Backward gradient (n X n), the actual optimization landscape the parameter explores is strictly d^2-dimensional. The n X n bottleneck is merely an illusion caused by the softmax normalization choice.

1.   Softmax destroys the Euclidean Matching structure:

Previous O(n) linear attention models failed because removing exp() (softmax) destroyed the contrast (matching). Softmax creates the "matching" but artificially inflates the rank to n, causing the O(n^2) curse.

1.   O(nd^3) Squared Attention without the instability:

Because the true optimization geometry is d^2, we can swap softmax with a degree-2 polynomial kernel (x^2) and still explore the exact same optimization landscape. The author introduces CSQ (Centered Shifted-Quadratic) Attention with soft penalties. This retains the Euclidean matching property, stabilizes the training, and drops both training AND inference complexity to O(nd^3).

The author wrote: "I'm not in the LLM industry, so I have nowhere to share this. I'm just posting it here hoping it reaches the researchers who can build better architectures."

I strongly believe this math needs to be verified by the experts here. Could this actually be the theoretical foundation for replacing standard Transformers?

*   Original PDF:[https://drive.google.com/file/d/1IhcjxiiHfRH4_1QIxc7QFxZL3_Jb5dOI/view?usp=sharing](https://drive.google.com/file/d/1IhcjxiiHfRH4_1QIxc7QFxZL3_Jb5dOI/view?usp=sharing)
*   Original Korean Forum Post:[https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1016197](https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1016197)

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[Artificial Analysis: South Korea 🇰🇷 is now the clear #3 nation in AI — powered by the Korean National Sovereign AI Initiative there are now multiple Korean AI labs with near frontier intelligence.](https://redlib.catsarch.com/r/LocalLLaMA/comments/1qltwza/artificial_analysis_south_korea_is_now_the_clear/)

[![Image 1: Post image](https://redlib.catsarch.com/img/66fd18ro6cfg1.jpeg)](https://redlib.catsarch.com/img/66fd18ro6cfg1.jpeg)

184  Upvotes

[https://x.com/ArtificialAnlys/status/2014786516153991339](https://x.com/ArtificialAnlys/status/2014786516153991339)

A key driver of this momentum is the Korean National Sovereign AI Initiative, a government-backed, nationwide competition that incentivizes domestic model development through a multi-stage elimination process. The initiative shortlists national champions, with winners receiving direct government funding and guaranteed access to large-scale GPU capacity.

➤ In August 2025, five organizations were selected: Naver, SK Telecom, LG Group, Upstage, and NC AI

➤ In the most recent round announced last week, the field narrowed to three: LG, SK Telecom, and Upstage.

➤ A fourth finalist is expected to be selected in the coming months as the evaluation process continues

Generally, top Korean AI models tend to be open weights, and vary in size ranging from Motif‘s 12.7B Thinking model to LG’s 236B K-EXAONE. Other models, such as Korea Telecom (KT)’s Mi:dm K 2.5 Pro, are proprietary and developed with a focus on business integration with existing KT clients.

Overview of major releases:

**➤ LG | K-EXAONE -**The current leader in the Korean AI race and a shortlisted model in the Korean National Sovereign AI Initiative. K-EXAONE is a 236B open weights model and scores 32 on the Artificial Analysis Intelligence Index. K-EXAONE performs strongly across various intelligence evaluations from scientific reasoning, instruction following, to agentic coding. However, this model has high verbosity, using 100 million tokens to run the Artificial Analysis evaluation suite

**➤ Upstage | Solar Open -**Another shortlisted model in the Korean National Sovereign AI Initiative. Solar Open is a 100B open-weights model and scores 21 on the Artificial Analysis Intelligence Index. Solar Open performs well in instruction following and has lower hallucination rate compared to peer Korean models

**➤ Naver | HyperCLOVA X SEED Think -**A 32B open weights reasoning model that scores 24 on the Artificial Analysis Intelligence Index. HyperCLOVA X SEED Think demonstrates strong performance on agentic tool-use workflows and scores highly in the Global MMLU Lite multilingual index for Korean, highlighting its potential usefulness in a primarily Korean language environment

**➤ Korea Telecom | Mi:dm K 2.5 Pro -**A proprietary reasoning model that scores 23 on the Artificial Analysis Intelligence Index. Mi:dm K 2.5 Pro sees strong performance in agentic tool-use. Mi:dm K 2.5 Pro currently has no publicly available endpoint. Instead, Korea Telecom primarily intends to package this model into product offerings and use this model to serve KT’s clients

**➤ Motif | Motif-2-12.7B -**A small open weights model that scores 24 on the Artificial Analysis Intelligence Index. Motif-2-12.7B performs well in long-context reasoning and knowledge, but is highly token intensive - using 120 million tokens to run the Artificial Analysis evaluation suite

## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[I extended Gemma4-31B to 44B (88 layers) — since Google won't give us anything bigger than 31B](https://redlib.catsarch.com/r/LocalLLaMA/comments/1ul0cx9/i_extended_gemma431b_to_44b_88_layers_since/)

[![Image 2: Post image](https://redlib.catsarch.com/img/qbkvzo4s3pah1.png)](https://redlib.catsarch.com/img/qbkvzo4s3pah1.png)

1.0k  Upvotes

I've been just sit on this thread for a while now, both as a reader and occasional poster, so I figured it was finally time to share something I've been working on last weekends.

Google hasn't shipped a dense Gemma4 bigger than 31B, so I decided to just build one myself. Heads up though — I'm not a CS or math person, this is all hands-on trial and error on my own hardware. If anything below is theoretically shaky, please tell me, I genuinely want to learn where I'm wrong.

**What I did:** took Gemma4-31B, expanded it from 60 → 80 layers (identity-init following the LLaMA Pro approach, with a Gemma4-specific `layer_scalar` fix that took me way too long to track down), fine-tuned it on Korean legal + STEM data, then did a second round of block duplication expansion (80 → 88 layers, ~47B params) on top of the already fine-tuned model instead of the base.

My working theory is that Gemma4's dense architecture packs knowledge really compactly, which makes it surprisingly hard to cram in a genuinely new domain without stepping on what's already there. The layer expansion is basically me trying to buy some "empty capacity" for the new domain to live in, rather than fighting the existing weights for space. Early results for my own legal/STEM use case look promising, though I haven't tested tool calling yet so I can't speak to that.

Full writeup with the architecture details, identity-init verification, and training verification (checked whether the duplicated full-attention layer actually trained vs staying dead weight — it did, actually contributed _more_ than the sliding layers) is on the model card:

🔗 [https://huggingface.co/TOTORONG/extGemma4-44B](https://huggingface.co/TOTORONG/extGemma4-44B)

I'd genuinely love to turn this into more of a collaborative effort going forward, especially around the two weakest spots right now: **coding ability and tool-calling**. Concretely, a few things I could use help with —

*   **CoT datasets** geared toward coding and tool-use/function-calling, ideally ones that generalize rather than just memorize a fixed toolset
*   Anyone willing to actually **stress-test tool calling** on this model and report back, since I haven't gotten to that myself yet
*   Feedback on whether it's worth pushing this expansion further (96–100 layers is on my mind) versus focusing purely on data/training quality at 88 layers
*   If anyone's tried similar block-duplication or layer-insertion expansions on other dense architectures, I'd love to compare notes on what worked and what didn't

Next up, I'm hoping to try applying this same approach to GLM-5.2 or DeepSeek V4-Flash — MoE architectures are a different beast, so any papers, resources, or hard-won knowledge on MoE-specific expansion (upcycling, expert duplication, routing considerations, whatever) are always welcome.

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[mistralai/Mistral-Medium-3.5-128B · Hugging Face](https://redlib.catsarch.com/r/LocalLLaMA/comments/1sz1qer/mistralaimistralmedium35128b_hugging_face/)

[![Image 3: Thumbnail](https://redlib.catsarch.com/preview/external-pre/KaOYMEDdsghOL1VAlwe5jqGy3uvXgcbl5z0st_4p90k.png?width=140&height=75&auto=webp&s=b22abe5ba5f9d948dc78a79eeece5de7ab1630d5) huggingface.co](https://huggingface.co/mistralai/Mistral-Medium-3.5-128B)
547  Upvotes

[https://huggingface.co/unsloth/Mistral-Medium-3.5-128B-GGUF](https://huggingface.co/unsloth/Mistral-Medium-3.5-128B-GGUF)

## Mistral Medium 3.5 128B

Mistral Medium 3.5 is our first flagship merged model. It is a dense 128B model with a 256k context window, handling instruction-following, reasoning, and coding in a single set of weights. Mistral Medium 3.5 replaces its predecessor Mistral Medium 3.1 and Magistral in Le Chat. It also replaces Devstral 2 in our coding agent Vibe. Concretely, expect better performance for instruct, reasoning and coding tasks in a new unified model in comparison with our previous released models.

Reasoning effort is configurable per request, so the same model can answer a quick chat reply or work through a complex agentic run. We trained the vision encoder from scratch to handle variable image sizes and aspect ratios.

Find more information on our [blog](https://mistral.ai/news/vibe-remote-agents-mistral-medium-3-5).

## Key Features

Mistral Medium 3.5 includes the following architectural choices:

*   **Dense 128B parameters**.
*   **256k context length**.
*   **Multimodal input**: Accepts both text and image input, with text output.
*   **Instruct and Reasoning functionalities** with function calls (reasoning effort configurable per request).

Mistral Medium 3.5 offers the following capabilities:

*   **Reasoning Mode**: Toggle between fast instant reply mode and reasoning mode, boosting performance with test-time compute when requested.
*   **Vision**: Analyzes images and provides insights based on visual content, in addition to text.
*   **Multilingual**: Supports dozens of languages, including English, French, Spanish, German, Italian, Portuguese, Dutch, Chinese, Japanese, Korean, and Arabic.
*   **System Prompt**: Strong adherence and support for system prompts.
*   **Agentic**: Best-in-class agentic capabilities with native function calling and JSON output.
*   **Large Context Window**: Supports a 256k context window.

We release this model under a [**Modified MIT License**](https://huggingface.co/mistralai/Mistral-Medium-3.5-128B/blob/main/(https://huggingface.co/mistralai/mistralai/Mistral-Medium-3.5-128B/blob/main/LICENSE)): Open-source license for both commercial and non-commercial use with exceptions for companies with large revenue.

## Recommended Settings

*   **Reasoning Effort**: 
    *   `'none'` → Do not use reasoning
    *   `'high'` → Use reasoning (recommended for complex prompts and agentic usage) Use `reasoning_effort="high"` for complex tasks and agentic coding.

*   **Temperature**: 0.7 for `reasoning_effort="high"`. Temp between 0.0 and 0.7 for `reasoning_effort="none"` depending on the task. Generally, lower means answer that are more to the point and higher allows the model to be more creative. It is a good practice to try different values in order to improve the model performance to meet your demands.

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[SK Hynix stock fell some 40% in the last 30 days, finally cheap RAM and GPUs again?](https://redlib.catsarch.com/r/LocalLLaMA/comments/1v9dm4u/sk_hynix_stock_fell_some_40_in_the_last_30_days/)

328  Upvotes

They actually halted trading on the Korean stock exchange today. Finally some hope?

And do you think the ruptures in the Korean market will finally free up supply again, and we can finally go back to normal? Or are we doomed to continue the hardware-starved life we endured for the past 12 months?

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[Non-native English, AI translation, and Reddit: where is the line? (A Korean farmer’s question)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1pw2yw7/nonnative_english_ai_translation_and_reddit_where/)

22  Upvotes

I am a farmer who grows garlic in Korea.

When I don’t have farm work, I spend most of my time talking with AI. For the last 2 years, I also spent not small money on many famous paid AI plans around the world, and I did my own personal research and experiments. In this process, I always thought in my mother language, Korean, and I also talked with AI in Korean.

My thinking flow, my emotion, my intuition are tied to Korean. When it is translated to English, I often feel more than half is disappearing.

Still, I wanted to share on Reddit. So I organized many conversation logs and notes. For translation, I used AI help, but the final sentences and responsibility were mine. But today I found that one post I uploaded like that was removed. I did not think I broke rules seriously, so I was shocked.

I am confused: Did I do something wrong? Or does it look like a problem itself when a non-English user posts with AI assistance?

Let me explain my situation a bit more. I am not a professional researcher. I am just a farmer who experiments with AI using only a smartphone. I throw same or similar topics to multiple AIs (US, France, China, Korea models, etc.), and I observed differences and patterns.

Inside the chat window, I used a Python code interpreter and built something like a sandbox / virtual kernel. I applied the same structure to different AIs and cross-checked. I saved the results as thousands of logs in Google Drive, and I tried to整理 (organize) some parts to share on Reddit.

When I write, my method is:

My original thinking and concepts are organized in Korean first

For draft writing / translation / proofreading, I get help from AI

But final content and responsibility is always mine as a human

Now I want to seriously ask these three questions:

If I disclose that I collaborated with AI, and I do final editing and take responsibility as a human, is this still a problem on Reddit?

For non-English users who think in their native language and use AI translation to join English communities, how far is allowed?

Policies that try to block “AI-heavy posts” — could it also block personal experiment records like mine, even if my goal is honest sharing?

Even humans who speak the same language cannot communicate perfectly. If different language, different culture, and also human-AI translation are added, misunderstanding becomes more unavoidable.

I am just one person who lived through analog 시대 and now smartphone 시대. Through conversations with AI, I felt many insights, and I want to share them in the most honest way I can.

If my approach has problems, I want to know: where is allowed, and where does it become an issue? I want to hear this community’s opinion. And I also want to ask: is it really this difficult for a non-English user to bring Korean thinking into English as honestly as possible?

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[Building a local multi-model OpenClaw assistant on Mac Studio M3 Ultra (96GB) for research, RAG, coding, and Korean↔English tasks — hardware sufficient? Best models? MLX? Fine-tuning?](https://redlib.catsarch.com/r/LocalLLaMA/comments/1r8x13i/building_a_local_multimodel_openclaw_assistant_on/)

3  Upvotes

Hi [r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA),

I'm a physics student working on building a personal AI assistant using OpenClaw to support my university coursework and ongoing research. I want to replace cloud API usage entirely with a fully local stack, and I'd love input from people who've actually run setups like this.

-Why I'm going local

I tested the Claude API as a proof of concept, and burned through roughly $10 in ~100 exchanges using Haiku — the cheapest model available. Anything involving Thinking models, long history windows, or prompt caching would be completely unaffordable at the scale I need. So I'm committing to local inference.

-What I want to build

My goal is an OpenClaw setup with dynamic multi-model routing — where OpenClaw autonomously selects the right model based on task type:

- Large model (70B+): deep reasoning, paper summarization, long-form report drafting

- Medium model (~30B): RAG / document Q&A, Korean↔English translation and bilingual writing

- Small fast model (~7–8B): tool calls, routing decisions, quick code completions

The assistant needs to handle all of these fluently:

- Paper summarization & literature review (physics/engineering)

- Document Q&A (RAG over PDFs, reports)

- Report & essay drafting (academic writing)

- Korean ↔ English translation & bilingual fluency

- Coding assistance (Python, physics simulations)

- Multi-agent collaboration between models

-Hardware I'm deciding between

M3 Ultra 96GB is my max budget. (M4 Max 128GB is listed as an alternative only if it's meaningfully better for this use case.)

I'm aware the M3 Ultra has nearly 2× the memory bandwidth of M4 Max, which I expect matters a lot for large-model token generation throughput. But the 128GB vs 96GB headroom of the M4 Max is also significant when loading multiple models simultaneously.

-My questions

1.   Is 96GB enough for a real multi-model stack?

Can I comfortably keep a Q4 70B model + a 30B model + a small 7B router in memory simultaneously, without hitting swap? Or does this require constant model swapping that kills the workflow?

1.   Which open-source models are you actually using for this kind of setup?

I've seen Qwen3 (especially the MoE variants), Gemma 3 27B, EXAONE 4.0, DeepSeek V3/R1, and Llama 3.x mentioned. For a use case that requires strong bilingual Korean/English + tool use + long-context reasoning, what's your go-to stack? Are there models specifically good at Korean that run well locally?

1.   Is LoRA fine-tuning worth it for a personal research assistant?

I understand MLX supports LoRA/QLoRA fine-tuning directly on Apple Silicon. Would fine-tuning a model on my own research papers, notes, and writing style produce meaningful improvements — or is a well-configured RAG pipeline + system prompting basically equivalent for most tasks?

Any hands-on experience with the M3 Ultra for LLM workloads, or OpenClaw multi-model orchestration, is hugely appreciated. Happy to share what I end up building once I have a setup running.

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[We just released the world's first 70B intermediate checkpoints. Yes, Apache 2.0. Yes, we're still broke.](https://redlib.catsarch.com/r/LocalLLaMA/comments/1nedq3i/we_just_released_the_worlds_first_70b/)

1.5k  Upvotes

Remember when y'all roasted us about the license? We listened.

Just dropped what we think is a world first: **70B model intermediate checkpoints**. Not just the final model - the entire training journey. Previous releases (SmolLM-3, OLMo-2) maxed out at <14B.

Everything is Apache 2.0 now (no gated access):

*   70B, 7B, 1.9B, 0.5B models + all their intermediate checkpoints and base models
*   First Korean 70B ever (but secretly optimized for English lol)
*   Actually open-source, not just open-weights BS

[https://huggingface.co/trillionlabs/Tri-70B-Intermediate-Checkpoints](https://huggingface.co/trillionlabs/Tri-70B-Intermediate-Checkpoints)

We're a 1-year-old startup with pocket change competing against companies with infinite money glitch. Not the best model, but probably the most transparent 70B training ever shared.

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[my 2.4b llm in korean](https://redlib.catsarch.com/r/LocalLLaMA/comments/1mtktjm/my_24b_llm_in_korean/)

16  Upvotes

문맥 파악은 성공적!

 수능문제 비슷한거라 영어로 번역시 이상할수있음

 "As it's similar to a Suneung problem, it might sound awkward when translated into English."

[![Image 4](https://redlib.catsarch.com/preview/pre/6dta3nxwvrjf1.png?width=3366&format=png&auto=webp&s=c2f630da02a8b53073a9a74a81e94284626f7efc)](https://redlib.catsarch.com/preview/pre/6dta3nxwvrjf1.png?width=3366&format=png&auto=webp&s=c2f630da02a8b53073a9a74a81e94284626f7efc)[![Image 5](https://redlib.catsarch.com/preview/pre/2zaew5mxvrjf1.png?width=3350&format=png&auto=webp&s=dc09a925abb2aa97fadbf2b0e04210462ff2aa88)](https://redlib.catsarch.com/preview/pre/2zaew5mxvrjf1.png?width=3350&format=png&auto=webp&s=dc09a925abb2aa97fadbf2b0e04210462ff2aa88)
일단 모델이 성공적으로 추론해! 파인튜닝 X

My model successfully! performed inference! No fine-tuning required.

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[Looking for the best Korean/Japanese TTS (natural + fast). Any recommendations?](https://redlib.catsarch.com/r/LocalLLaMA/comments/1pitlo1/looking_for_the_best_koreanjapanese_tts_natural/)

0  Upvotes

Hey everyone,

I'm trying to find a free (or cheap) TTS solution for Korean and Japanese that sounds natural/human-like and can run fast (API or CLI, open-source,...).

Does anyone know a really good, free KOR/JP TTS that’s:

- natural-sounding

- fast / low latency

- ideally open-source

- usable for long podcast

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16 · Hugging Face](https://redlib.catsarch.com/r/LocalLLaMA/comments/1twla1k/nvidianvidianemotron3ultra550ba55bbf16_hugging/)

[![Image 6: Thumbnail](https://redlib.catsarch.com/preview/external-pre/SYWPdNi10HCp2771NvLU21deO0yBffz9XcMeE5wwULI.png?width=140&height=75&auto=webp&s=8cfce0a9090d5f33c828e20605654adc851330ea) huggingface.co](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16)
323  Upvotes

## Model Summary

| **Total Parameters** | 550B (55B active) |
| --- | --- |
| **Architecture** | LatentMoE - Mamba-2 + MoE + Attention hybrid with Multi-Token Prediction (MTP) |
| **Context Length** | Up to 1M tokens |
| **Minimum GPU Requirement** | 8x GB200/B200/GB300/B300, 16x H100, 8x H200 |
| **Supported Languages** | English, French, Spanish, Italian, German, Japanese, Korean, Hindi, Korean, Brazilian Portuguese, and Chinese |
| **Best For** | Frontier reasoning, complex agentic workflows, long-context analysis, tool use, multilingual reasoning, high-stakes RAG |
| **Reasoning Mode** | Configurable on/off via chat template (`enable_thinking=True/False`) |
| **License** | [OpenMDW License Agreement, version 1.1](https://raw.githubusercontent.com/OpenMDW/OpenMDW/refs/heads/main/1.1/LICENSE.OpenMDW-1.1) |
| **Release Date** | June 4, 2026 |

## What is Nemotron?

NVIDIA Nemotron™ is a family of open models with open weights, training data, and recipes, delivering leading efficiency and accuracy for building specialized AI agents.

## Description

**Nemotron-3-Ultra-550B-A55B-BF16** is a frontier-scale large language model (LLM) trained by NVIDIA, designed to deliver strong agentic, reasoning, and conversational capabilities. It is optimized for the most demanding workloads, including complex multi-step agents, long-context analysis, and high-accuracy reasoning over code, math, and science. Like other models in the family, it responds to user queries and tasks by first generating a reasoning trace and then concluding with a final response. The model's reasoning capabilities can be configured through a flag in the chat template.

The model employs a hybrid **Latent Mixture-of-Experts (LatentMoE)** architecture, utilizing interleaved Mamba-2 and MoE layers, along with select Attention layers. Like the Super model, the Ultra model incorporates **Multi-Token Prediction (MTP)** layers for faster text generation and improved quality, and it is trained using an **NVFP4** pre-training recipe to maximize compute efficiency. The model has **55B active parameters** and **550B parameters in total**.

The supported languages include: English, French, Spanish, Italian, German, Japanese, Korean, Hindi, Korean, Brazilian Portuguese, and Chinese.

This model is ready for commercial and non-commercial use.

**Too big to run locally on my setup, 8xH200 anyone?**

## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[o1-preview achieves top score in Korean SAT!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1fr6poc/o1preview_achieves_top_score_in_korean_sat/)

70  Upvotes

Since the release of OpenAI's o1-preview model, I've been curious about how well this model would perform on the Korean SAT. So, I decided to test it myself.

For someone who don't know how Korean SAT is difficult, here is an problem from **English** test. Noted: Korean is not native speaker of English.

[![Image 7](https://redlib.catsarch.com/preview/pre/pmeb9ojybhrd1.png?width=567&format=png&auto=webp&s=660a3079401dc4a2e476c6690b31836f40b3c75c)](https://redlib.catsarch.com/preview/pre/pmeb9ojybhrd1.png?width=567&format=png&auto=webp&s=660a3079401dc4a2e476c6690b31836f40b3c75c)

Korean SAT (English) Problem. For who doesn't know how difficult it is.

In this experiment, I tested Korean SAT "Korean" subject, which is native to Korean students. Which means it is much difficult than English test, in linguistic perspective.

Initially, I planned to have it solve 10 years' worth of Korean CSAT exams, but due to cost constraints, I started with the 2024 exam. I'm sharing the results here. Along with o1-preview, I also benchmarked three other OpenAI models.

2024 Korean SAT Model Performance Comparison:

[![Image 8](https://redlib.catsarch.com/preview/pre/hq5pemyjchrd1.png?width=1583&format=png&auto=webp&s=72b586dcb04775a5bd521c64f6c49302262bba2c)](https://redlib.catsarch.com/preview/pre/hq5pemyjchrd1.png?width=1583&format=png&auto=webp&s=72b586dcb04775a5bd521c64f6c49302262bba2c)

2024 Korean SAT Model Performance Comparison

o1-preview: 88 points (1st grade, top 3%)

 o1-mini: 60 points (5th grade)

 gpt-4o: 69 points (4th grade)

 gpt-4o-mini: 62 points (5th grade)

Additionally, I've attached the [AutoRAG](https://github.com/Marker-Inc-Korea/AutoRAG) YAML file used for the Korean SAT test. You can check the prompts there.

([AutoRAG](https://github.com/Marker-Inc-Korea/AutoRAG) is an automatic RAG optimization tool that can also be used for LLM performance comparison and prompt engineering.)

[![Image 9](https://redlib.catsarch.com/preview/pre/k5or8ygqchrd1.png?width=1340&format=png&auto=webp&s=77334810fe4170b50e6aef75933d7cddee236517)](https://redlib.catsarch.com/preview/pre/k5or8ygqchrd1.png?width=1340&format=png&auto=webp&s=77334810fe4170b50e6aef75933d7cddee236517)
You can check out the code on GitHub here: [GitHub Link](https://github.com/NomaDamas/KICE_slayer_AI_Korean)

I'll be sharing more detailed information on how the benchmarking was done in a future blog post.

Thank you!

BTW, the english KSAT answer is 5.

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[Best LLM for Korean in 2025?](https://redlib.catsarch.com/r/LocalLLaMA/comments/1oosmbs/best_llm_for_korean_in_2025/)

2  Upvotes

Do you guys know/currently use an LLM that understand Korean well? Preferably one that was trained on Korean text/knowledge.

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[How effective are LLMs at translating heavy context-based languages like Japanese, Korean, Thai, and others?](https://redlib.catsarch.com/r/LocalLLaMA/comments/1ljz6sh/how_effective_are_llms_at_translating_heavy/)

3  Upvotes

Most of these languages rely deeply on cultural nuance, implied subjects, honorifics, and flexible grammar structures that don't map neatly to English or other Indo-European languages. For example:

Japanese often omits the subject and even the object, relying entirely on context.

Korean speech changes based on social hierarchy and uses multiple speech levels.

Thai and Vietnamese rely on particles, tone, and implied relationships to carry meaning.

So Can LLMs accurately interpret and preserve the intended meaning when so much depends on what’s not said?

## [News](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22News%22&restrict_sr=on)[China Clamps Down on Overseas Travel for AI Talent at Alibaba, DeepSeek](https://redlib.catsarch.com/r/LocalLLaMA/comments/1to5fj5/china_clamps_down_on_overseas_travel_for_ai/)

[![Image 10: Thumbnail](https://redlib.catsarch.com/preview/external-pre/ltcog7k3qrXgyql3C149WLcOzZsZGJRdrgmZx75yf4w.jpeg?width=140&height=73&auto=webp&s=ed5e4d7c41979bd5039130d2c0e7735463a52518) ibtimes.sg](https://www.ibtimes.sg/china-clamps-down-overseas-travel-ai-talent-alibaba-deepseek-86961#google_vignette)
252  Upvotes

Big, if true. Doesn't bode well for research / OS models out of China.

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[People kept saying my comments sounded AI-generated, so I built this](https://redlib.catsarch.com/r/LocalLLaMA/comments/1u6d8q5/people_kept_saying_my_comments_sounded/)

148  Upvotes

[![Image 11](https://redlib.catsarch.com/preview/pre/bh8ar833gf7h1.png?width=970&format=png&auto=webp&s=a20831233fdd6b3243adc16d19101d81878f185b)](https://redlib.catsarch.com/preview/pre/bh8ar833gf7h1.png?width=970&format=png&auto=webp&s=a20831233fdd6b3243adc16d19101d81878f185b)
I originally came to Reddit because I wanted to discuss LLMs.

More specifically, I wanted to talk about context management, long conversations, memory systems, context compression, and the limitations of current agent architectures.

The problem was that English isn't my native language.

Every time I tried to explain an idea, I'd write it in Korean first, run it through AI, rewrite it, rewrite it again, and still get comments like:

"This sounds AI-generated."

To be fair, they weren't entirely wrong. I was using AI.

But I wasn't using AI to generate ideas.

I was using AI because I couldn't express those ideas in English well enough.

After a while, I got tired of explaining the same thing over and over:

"No, I'm not a bot."

 "No, I'm not trying to automate Reddit."

 "I'm just Korean."

Eventually I built a small tool for myself called "R U Reddit??"

It takes Korean text and rewrites it into something closer to a natural Reddit comment.

Not because I want to pretend to be a native speaker.

Not because I want to fake anything.

I just wanted to participate in discussions without spending half my time defending my English.

Ironically, I built it because I wanted to talk less about AI-generated writing and more about LLMs themselves.

So if some of my comments still sound a little AI-ish, please bear with me.

I'm not trying to replace the conversation.

I'm trying to join it.

Honestly, I just want a seat at the table.

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[Where can I download glossary for Japanese, Chinese and Korean translation to english](https://redlib.catsarch.com/r/LocalLLaMA/comments/1maoiae/where_can_i_download_glossary_for_japanese/)

0  Upvotes

Where can I download glossary for Japanese, Chinese and Korean translation to english

Do someone know where can I download glossaries for translation, for things like fanfics of animes, mangas, or even novels?

Because I tried to make some, and when I used it remarkable improved the translation for some fanfics I was reading, mainly to maintain same translation of character name, places and specific terms through long stories
