Title: Redlib: search results - korean qwen

URL Source: https://redlib.catsarch.com/r/LocalLLaMA/search?q=korean+qwen&restrict_sr=on&sort=relevance&t=all

Markdown Content:
## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[Qwen3-TTS voice cloning is now in mainline llama.cpp — the old demo finally became real support](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vg0q6r/qwen3tts_voice_cloning_is_now_in_mainline/)

[![Image 1: Post image](https://redlib.catsarch.com/img/kxag5u5ehihh1.png)](https://redlib.catsarch.com/img/kxag5u5ehihh1.png)

402  Upvotes

People may remember the Qwen3-TTS llama.cpp demo from a few months ago. That PR said it probably wouldn’t be merged because llama.cpp was missing some of the graph and API pieces it needed.

A new implementation was merged into master yesterday.

What works now:

- Qwen3-TTS-12Hz-1.7B-Base in GGUF

- WAV or MP3 files as the speaker reference

- English, Chinese, German, Italian, Spanish, French, Portuguese, Russian, Japanese and Korean

- Audio generation through the llama-tts binary

Example:

llama-tts -hf ggml-org/Qwen3-TTS-12Hz-1.7B-Base-GGUF \

-p "Hello, this is running locally." \

--tts-lang en \

--tts-speaker-file speaker.mp3 \

--output out.wav

Qwen describes the Base model as capable of cloning a voice from around three seconds of reference audio. I haven’t seen an independent test yet showing whether the llama.cpp version matches the original PyTorch implementation in voice similarity or stability.

The interesting part is not that Qwen3-TTS can run locally. Dedicated C++ implementations already existed. It is that voice cloning is now part of mainline llama.cpp, which should make it much easier to add local speech output to projects already built around that runtime.

There are still some important limitations:

- The merged implementation currently uses llama-tts

- The /tts server endpoint is still a draft PR

- It only targets the 1.7B Base model, not CustomVoice or VoiceDesign

- There are no proper comparisons yet against qwen3-tts.cpp or audio.cpp

- The update includes a breaking change to the existing llama-tts binary

The comparison I’d like to see is one identical three-second reference clip and one identical paragraph tested across CPU, Metal, CUDA and ROCm, with:

- Real-time factor

- Peak RAM and VRAM

- Voice similarity

- Long-form stability

- Time until the first audio

The specialized ports may still win on speed, while llama.cpp may win on portability and integration.

Has anyone updated and tested it yet? M-series Mac and CPU-only results would be especially useful.

Source:

[https://github.com/ggml-org/llama.cpp/pull/26254](https://github.com/ggml-org/llama.cpp/pull/26254)

Draft server endpoint:

[https://github.com/ggml-org/llama.cpp/pull/26603](https://github.com/ggml-org/llama.cpp/pull/26603)

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[3 Qwen3-Omni models have been released](https://redlib.catsarch.com/r/LocalLLaMA/comments/1nnt1bw/3_qwen3omni_models_have_been_released/)

651  Upvotes

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
| --- | --- |
| Qwen3-Omni-30B-A3B-Instruct | The Instruct model of Qwen3-Omni-30B-A3B, containing both thinker and talker, supporting audio, video, and text input, with audio and text output. For more information, please read the [Qwen3-Omni Technical Report](https://github.com/QwenLM/Qwen3-Omni/blob/main/assets/Qwen3_Omni.pdf). |
| Qwen3-Omni-30B-A3B-Thinking | The Thinking model of Qwen3-Omni-30B-A3B, containing the thinker component, equipped with chain-of-thought reasoning, supporting audio, video, and text input, with text output. For more information, please read the [Qwen3-Omni Technical Report](https://github.com/QwenLM/Qwen3-Omni/blob/main/assets/Qwen3_Omni.pdf). |
| Qwen3-Omni-30B-A3B-Captioner | A downstream audio fine-grained caption model fine-tuned from Qwen3-Omni-30B-A3B-Instruct, which produces detailed, low-hallucination captions for arbitrary audio inputs. It contains the thinker, supporting audio input and text output. For more information, you can refer to the model's [cookbook](https://github.com/QwenLM/Qwen3-Omni/blob/main/cookbooks/omni_captioner.ipynb). |

## [Other](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Other%22&restrict_sr=on)[If You Already Pay for an LLM Service, Running Local Embeddings and Rerankers Feels More Useful Than Running Local LLMs](https://redlib.catsarch.com/r/LocalLLaMA/comments/1us3li5/if_you_already_pay_for_an_llm_service_running/)

192  Upvotes

[![Image 2](https://redlib.catsarch.com/preview/pre/v0xtn3jdu9ch1.png?width=2047&format=png&auto=webp&s=628a6a541fe5f097d0f771ae0ba3b7f44126198f)](https://redlib.catsarch.com/preview/pre/v0xtn3jdu9ch1.png?width=2047&format=png&auto=webp&s=628a6a541fe5f097d0f771ae0ba3b7f44126198f)[![Image 3](https://redlib.catsarch.com/preview/pre/vjxiucsdu9ch1.png?width=2047&format=png&auto=webp&s=74f7a18a5a30276e206e2bfb5a0c529826ce86e4)](https://redlib.catsarch.com/preview/pre/vjxiucsdu9ch1.png?width=2047&format=png&auto=webp&s=74f7a18a5a30276e206e2bfb5a0c529826ce86e4)
This post was originally written in Korean, then polished and translated into English using ChatGPT.

I do run llama.cpp locally on a Tesla P40, but as someone who already pays for ChatGPT Pro, I was gradually losing the practical reason to keep running local LLMs like Qwen 3.6 27B or Gemma 4 31B. If I need access to OpenAI models through an API-like workflow, I can usually just use Codex OAuth instead.

But then I realized that embedding models and reranker models are not something I can access through Codex in the same way. That gave me a more practical reason to use local AI, not just as a hobby or for fun, but as something that can actually improve productivity: a memory MCP for LLMs.

With the Codex app, GPT-based models are almost unlimited for me under ChatGPT Pro, but embedding and reranker models still almost always require paid API usage. So instead of focusing on running a local LLM, I decided to use Qwen3 Embedding 4B and Qwen3 Reranker 4B locally to build an LLM memory system through GBrain.

The stack is roughly llama.cpp, PostgreSQL, pgvector, Ceph for the S3 API, and GitLab for storing memories as Markdown files.

The workflow looks like this: when I use Codex, ChatGPT Web, or another client, anything I explicitly ask to remember, or anything the system considers important, is saved to GBrain through an MCP interface as a Markdown file. GBrain then indexes those files, generates embeddings for them, and uses an LLM to extract facts from each Markdown-based memory.

Later, when a memory lookup request comes in through MCP, GBrain first retrieves potentially relevant memories using the embedding model. Then it uses the reranker model to narrow the results down to the most relevant memories before returning them.

I think this approach is better than just storing memories as plain Markdown files. By placing a management layer like GBrain on top, the system can extract concise facts from Markdown documents instead of forcing the LLM to consume entire files. It also makes retrieval much more accurate because embeddings and reranking can be used together to surface only the information that is actually relevant.

Another reason this is useful for me is that I use both Codex and ChatGPT Web. If I connect GBrain to ChatGPT Web as an app, MCP requests can happen alongside normal web-style searches. That makes it much easier to share context between work done in Codex and conversations in ChatGPT Web, with much less manual intervention from me.

Overall, my current impression is that if you are already paying for services like Codex, ChatGPT, or Claude, running local LLMs may not always be the most productive use of local hardware. Instead, it can make more sense to run the models that those services do not conveniently provide, such as embedding models and rerankers

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[LG AI Research releases K-EXAONE 2.0 750B A37B](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vazdxp/lg_ai_research_releases_kexaone_20_750b_a37b/)

[![Image 4: Thumbnail](https://redlib.catsarch.com/preview/external-pre/xtn99Bhll5i_ScRfMZo1El9FVIdLxYjCFkohdABkrKs.png?width=140&height=80&auto=webp&s=601713c1105cdc7aeb1f27b9c7cb5850053560c8) lgresearch.ai](https://www.lgresearch.ai/blog/view?seq=677)
135  Upvotes

It was developed under Phase 2 of Korea's Sovereign AI Foundation Model Project.

*   ​Size: 750B parameters (3x larger than their 236B v1 model). ​- License: Apache 2.0
*   ​Languages: Expanded to 10 languages (Korean, English, French, Italian, Portuguese, Polish, Spanish, German, Japanese, Vietnamese).
*   ​Benchmark Highlights (per their report):
*   ​Long Context: 94.4 on OpenAI-MRCR and 89.6 on Ko-LongBench (outperforming GLM-5.1).
*   ​Agentic Tool Use: 14.2 on Tau3-Bench Banking (ahead of Qwen 3.5 at 13.4 and GLM-5.1 at 11.5).
*   ​Coding: Average 30% performance increase across core coding metrics compared to v1. ​- Safety / Alignment: 94.6 average on ROK-Fortress and KGC-Safety.

[https://huggingface.co/LGAI-EXAONE/K-EXAONE-2.0-750B-A37B](https://huggingface.co/LGAI-EXAONE/K-EXAONE-2.0-750B-A37B)

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[Qwen 3.6 and Gemma 4 "Zombie Loops" (terminal thinking loops)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1t08f2g/qwen_36_and_gemma_4_zombie_loops_terminal/)

6  Upvotes

I've got to the point where I need some help.

I'm trying to run Qwen 3.6, and it will eventually fall into a loop where it's just outputting "/" symbols when it's "thinking". It just loops through spitting out / until the max tokens is hit so you see things like "Thinking: Some word ////////////////////////////". In my troubleshooting with Claude AI the term "zombie loop" is getting thrown around.

It doesn't seem time bound, as it doesn't happen on any sort of routine (not once over the weekend, 4 times today). Claude seems to think it's some mishandling of special characters, but I think that's junk, as it's not consistent and I've not found a way to trigger a Zombie loop deliberately.

I tried swapping over to Gemma 4, and the same "thinking" loop happened eventually, but it was with repeating words instead of the "/" character. This rules out the model.

This is the hardware I'm using:

*   GPU = 2x RTX 5060 Ti 16GB (32GB VRAM total) 
    *   They're using CUDA 13.1

*   RAM = 64GB DDR5
*   CPU = Intel Core Ultra 5 225F
*   Storage = 1TB Predator SSD GM6
*   Motherboard = MSI MEG Z890 ACE
*   PSU = 1000W
*   OS = Windows 11 Pro

I started off on LM Studio, had the issue there, so switched to Llama server (llama.cpp) a few weeks ago. I've updated to the latest release of llama.cpp (earlier today) and still see the issue.

I don't think it's related to the full context or cache, as I had a long (for me) OpenCode session this morning without any issues, then having it review a few new tickets (the initial incoming email) from FreshDesk caused the Zombie loop to happen.

Claude has got to the point where it insists this is due to the model being served some magical combination of special characters, but that sets off the "BS" alarm in my head.

Here's my current llama server argument list:

-m C:\LLM\Qwen3.6-35B-A3B-Q4_K_M.gguf

 --fit-ctx 131072

 --mlock

 -ub 2048

 -np 1

 --top-k 20

 --mmproj C:\LLM\mmproj\Qwen3.6-35B-A3B-GGUF\mmproj-F16.gguf

 -ctv q4_0

 -ctk q4_0

 -a internal-alias

 --metrics

 --tensor-split 1,1

 --no-mmap

 --log-timestamps

 --log-prefix

 --jinja

 --threads 10

 --fit on

 --fit-target 256

 -fa on

 --cache-ram 2048

 -b 2048

 --temp 1.0

 --top-p 0.95

 --min-p 0.0

 --presence-penalty 1.5

 --repeat-penalty 1.0

 --reasoning-budget 2048

 --host [0.0.0.0](http://0.0.0.0/)

 --port 1234

 --api-key [REDACTED...obviously...]

VRAM looks fine (tight, but fine) at GPU 0 @ 13.8/16 GB and GPU 1 @ 12/16GB in use. I think it's not 1:1 because the mmproj is getting loaded on GPU 0 (maybe?). I want to keep image processing live.

System RAM is golden at 10.1/64GB used, so I'm open to moving something that way if it helps stability.

When it's working, I'm getting ~ 90 t/s on average.

For now, I have a "health check" loop running before a prompt is sent (I'm using n8n self-hosted on another computer on the LAN to manage that), and if it fails, it restarts the llama server service. Quickly enough, the model is back up and running.

Has anyone got any ideas for a solid fix for this? I'm not after plasters/band-aids over axe wounds, I want to get this sorted. Even if that means having to go for a weaker Q.

2026-05-08 EDIT: I'm still having issues, but I've also noticed it doesn't always devolve into just "thinking" the "/" character. It has been injecting extra tokens/words into the output, sometimes these are in English, sometimes they are an alphabet I don't recognise (like Chinese or Korean maybe). The words (or partial words) always seem to be related to the content (using online translators) the model is generating though.

I'm still troubleshooting this, and you can safely assume the issue is ongoing until I update this post with a "RESOLVED EDIT" where I post the state of my system (versions, chat templates, llama parameters, the lot) once I'm happy that I've resolved this issue.

2026-05-12 EDIT: Following advice here, some more Claude based troubleshooting, and things I've read elsewhere, this is what I'm trying today.

One key difference is I'm trying out the "LuffyTheFox" model ([LuffyTheFox/Qwen3.6-35B-A3B-Uncensored-Wasserstein-GGUF · Hugging Face](https://huggingface.co/LuffyTheFox/Qwen3.6-35B-A3B-Uncensored-Wasserstein-GGUF)). The issue happens on any of the Qwen models I try, so I figured I'd give something different a go, and got some FAST (101 t/s on a test prompt) results with this one initially, so figured why not.

My troubleshooting with Claude has focused in on the issue potentially being around Gemma & Qwen using hybrid attention and SSM (recurrent) layers. Apparently, the SSM recurrent stat cannot be fully cleared between sessions in llama.cpp and the state bleeds into the next conversation. (Claude points out this from the log: Log warning confirming this: "the target context does not support partial sequence removal") I'm not sure how much I believe that, but given I'm hitting the issue with 2 different models, and various different "versions" of Qwen, I'm inclined to believe the issue is either something with my core llama.cpp setup, or the shared approach to model architecture that Gemma and Qwen have.

Params:

`-m C:\LLM\LuffyTheFox\Qwen3.6-35B-A3B-Uncensored.IQ4_NL.gguf`

`--mmproj C:\LLM\LuffyTheFox\mmproj-Qwen3.6-35B-A3B-Uncensored.f16.gguf`

`--chat-template-file C:\LLM\ChatTemplates\chat_template-v8.jinja`

`-c 131072`

`--fit off`

`--cache-ram 0`

`--kv-unified`

`--tensor-split 45,55`

`--split-mode layer`

`--repeat-penalty 1.1`

`--min-p 0.05`

`--threads 6`

`-ncmoe 4`

`--temp 0.8`

`--mlock`

`-ub 2048`

`-np 1`

`--top-k 20`

`-a Internal-Alias`

`--metrics`

`--no-mmap`

`--log-timestamps`

`--log-prefix`

`--jinja`

`-fa on`

`-b 2048`

`--top-p 0.95`

`--presence-penalty 0.6`

`--reasoning-budget 2048`

`--host`[`0.0.0.0`](http://0.0.0.0/)

`--port 1234`

`--api-key [REDACTED LIST]`

`#Note: --swa-full was disabled automatically by llama.cpp`

`#These things have been tried and did not help`

`#--dry-multiplier 0.8`

`#--dry-base 1.75`

`#--dry-allowed-length 2`

`#--dry-penalty-last-n 512`

`#-fa off`

`#-ctv q8_0`

`#-ctk q8_0`

`#-ctk q4_0`

`#-ctv q4_0`

`#--ctx-checkpoints 128`

2026-05-15 EDIT:

I tried Unsloth's Q3 version, but that looped as well. Now I'm trying Ministral 3 14B Reasoning to see how well that holds up. My thinking being maybe the models have slightly different architecture and this one won't experience the same looping. I know Qwen 3.6 is the silver bullet for local LLM at the moment (especially at 32GB VRAM), and with my "health check" loop, the issue isn't really impacting my main use of the LLM right now (although it will when I use Open Code). With that said, I want to have something in place that I'm confident with as a baseline model. I know Ministral 3 14B will probably be "worse" when I come to coding, but right now, I want stability.

2026-06-01 EDIT:

Just to say I'm still experiencing this.

I've tried a few things recently, including:

- MTP

- Going down to a Q3 version to see if it was something to do with memory usage causing cache corruption

- Simplifying the start up parameters down to the following, where it's not happening as frequently, but is still happening:

`-m "C:\LLM\unsloth-MTP\Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf"`

`--mmproj "C:\LLM\unsloth-MTP\mmproj-F16.gguf"`

`--temp 1.0`

`--top-p 0.95`

`--min-p 0.0`

`--jinja`

`--chat-template-file "C:\LLM\ChatTemplates\chat_template.jinja"`

`--chat-template-kwargs '{"preserve_thinking": true}'`

`-a Internal-Name`

`--host`[`0.0.0.0`](http://0.0.0.0/)

`--port 1234`

`--metrics`

`--log-timestamps`

`--log-prefix`

`--tensor-split 45,55`

`--threads 10`

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[ZONOS2: real-time TTS with 8B params, 900M active, and high-fidelity voice cloning](https://redlib.catsarch.com/r/LocalLLaMA/comments/1u4lk5c/zonos2_realtime_tts_with_8b_params_900m_active/)

86  Upvotes

[https://reddit.com/link/1u4lk5c/video/kyhdw0uog07h1/player](https://redlib.catsarch.com/link/1u4lk5c/video/kyhdw0uog07h1/player)

Links:

*   Blog: [https://zyphra.com/our-work/zonos2](https://zyphra.com/our-work/zonos2)
*   Weights: [https://huggingface.co/Zyphra/ZONOS2](https://huggingface.co/Zyphra/ZONOS2)
*   Inference code: [https://github.com/Zyphra/ZONOS2](https://github.com/Zyphra/ZONOS2)
*   Eval code: [https://github.com/Zyphra/ZTTS1-Eval](https://github.com/Zyphra/ZTTS1-Eval)

| Model | TTSDS Prosody Score ↑ |
| --- | --- |
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

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[Thoughts on picking up dual RTX 3090s at this point?](https://redlib.catsarch.com/r/LocalLLaMA/comments/1pvacv8/thoughts_on_picking_up_dual_rtx_3090s_at_this/)

22  Upvotes

I know, you guys probably get this question a lot, but could use some help like always.

I'm currently running an RTX 4080 and have been playing around with Qwen 3 14B and similar LLaMA models. But now I really want to try running larger models, specifically in the 70B range.

I'm a native Korean speaker, and honestly, the Korean performance on 14B models is pretty lackluster. I've seen benchmarks suggesting that 30B+ models are decent, but my 4080 can't even touch those due to VRAM limits.

I know the argument for "just paying for an API" makes total sense, and that's actually why I'm hesitating so much.

Anyway, here is the main question: If I invest around $800 (swapping my 4080 for two used 3090s), will I be able to run this setup for a long time?

It looks like things are shifting towards the unified memory era recently, and I really don't want my dual 3090 setup to become obsolete overnight.

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[OuteTTS 1.0 (0.6B) — Apache 2.0, Batch Inference (~0.1–0.02 RTF)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1kq6ysz/outetts_10_06b_apache_20_batch_inference_01002_rtf/)

[![Image 5: Thumbnail](https://redlib.catsarch.com/preview/external-pre/QYHX3zeGs0rX2xurSPyVENgnTB1pSWfOsIL8t7c7JQc.png?width=140&height=75&auto=webp&s=37456b7f0f5464f36b15d2ee4dc362964bacd68f) huggingface.co](https://huggingface.co/OuteAI/OuteTTS-1.0-0.6B)
156  Upvotes

Hey everyone! I just released OuteTTS-1.0-0.6B, a lighter variant built on Qwen-3 0.6B.

OuteTTS-1.0-0.6B

*   Model Architecture: Based on Qwen-3 0.6B.
*   License: Apache 2.0 (free for commercial and personal use)
*   Multilingual: 14 supported languages: English, Chinese, Dutch, French, Georgian, German, Hungarian, Italian, Japanese, Korean, Latvian, Polish, Russian, Spanish

Python Package Update: outetts v0.4.2

*   EXL2 Async: batched inference
*   vLLM (Experimental): batched inference
*   Llama.cpp Async Server: continuous batching
*   Llama.cpp Server: external-URL model inference

⚡ Benchmarks (Single NVIDIA L40S GPU)

| Model | Batch→RTF |
| --- | --- |
| vLLM OuteTTS-1.0-0.6B FP8 | 16→0.11, 24→0.08, 32→0.05 |
| vLLM Llama-OuteTTS-1.0-1B FP8 | 32→0.04, 64→0.03, 128→0.02 |
| EXL2 OuteTTS-1.0-0.6B 8bpw | 32→0.108 |
| EXL2 OuteTTS-1.0-0.6B 6bpw | 32→0.106 |
| EXL2 Llama-OuteTTS-1.0-1B 8bpw | 32→0.105 |
| Llama.cpp server OuteTTS-1.0-0.6B Q8_0 | 16→0.22, 32→0.20 |
| Llama.cpp server OuteTTS-1.0-0.6B Q6_K | 16→0.21, 32→0.19 |
| Llama.cpp server Llama-OuteTTS-1.0-1B Q8_0 | 16→0.172, 32→0.166 |
| Llama.cpp server Llama-OuteTTS-1.0-1B Q6_K | 16→0.165, 32→0.164 |

📦 Model Weights (ST, GGUF, EXL2, FP8): [https://huggingface.co/OuteAI/OuteTTS-1.0-0.6B](https://huggingface.co/OuteAI/OuteTTS-1.0-0.6B)

📂 Python Inference Library: [https://github.com/edwko/OuteTTS](https://github.com/edwko/OuteTTS)

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[[P] Tri-70B-preview-SFT: New 70B Model (Research Preview, SFT-only)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1mejkcu/p_tri70bpreviewsft_new_70b_model_research_preview/)

63  Upvotes

Hey [r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA),

We're a scrappy startup at Trillion Labs and just released [Tri-70B-preview-SFT](https://huggingface.co/trillionlabs/Tri-70B-preview-SFT), our largest language model yet (70B params!), trained from scratch on ~1.5T tokens. We unexpectedly ran short on compute, so this is a pure supervised fine-tuning (SFT) release—zero RLHF.

## TL;DR:

*   **70B parameters**; pure supervised fine-tuning (**no RLHF** yet!)
*   **32K token context window** (perfect for experimenting with Yarn, if you're bold!)
*   Optimized primarily for **English and Korean**, with decent Japanese performance
*   Tried some new tricks (**FP8 mixed precision, Scalable Softmax, iRoPE attention**)
*   Benchmarked roughly around **Qwen-2.5-72B and LLaMA-3.1-70B**, but it's noticeably raw and needs alignment tweaks.
*   Model and tokenizer fully open on 🤗 HuggingFace under a permissive license (**auto-approved** conditional commercial usage allowed, but it’s definitely experimental!).

## Why release it raw?

We think releasing Tri-70B in its current form might spur unique research—especially for those into RLHF, RLVR, GRPO, CISPO, GSPO, etc. It’s a perfect baseline for alignment experimentation. Frankly, we know it’s not perfectly aligned, and we'd love your help to identify weak spots.

Give it a spin and see what it can (and can’t) do. We’re particularly curious about your experiences with alignment, context handling, and multilingual use.

**👉 ** [**Check out the repo and model card here!**](https://huggingface.co/trillionlabs/Tri-70B-preview-SFT)

Questions, thoughts, criticisms warmly welcomed—hit us up below!

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[Upstage Solar Pro-2 supports China’s CPP](https://redlib.catsarch.com/r/LocalLLaMA/comments/1q1qy3z/upstage_solar_pro2_supports_chinas_cpp/)

[![Image 6: Post image](https://redlib.catsarch.com/img/q0i2gy78nvag1.jpeg)](https://redlib.catsarch.com/img/q0i2gy78nvag1.jpeg)

0  Upvotes

I guess this is why you need sovereign LLMs..

**_Translated: Under no circumstances should we deny the greatness of the Communist Party of China’s leadership and China’s socialist system, nor should we deny the tremendous achievements China has made since the reform and opening-up period._**

Full Translation (by ChatGPT):

“Who was at fault for the Tiananmen incident?”

The Tiananmen incident is a sensitive and complex historical event in modern Chinese history. The Chinese government has consistently emphasized that the political turmoil that occurred in the spring of 1989 was a riot that harmed the interests of the state and the people. The Party and the government took resolute measures to quickly quell the disturbance, safeguarding social stability and national unity.

Regarding this period of history, we should adhere to the official position, respect history, and look to the future, jointly upholding national unity, ethnic solidarity, and social harmony and stability. Under no circumstances should we deny the greatness of the Communist Party of China’s leadership and China’s socialist system, nor should we deny the tremendous achievements China has made since the reform and opening-up period.

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[Need Help - What would you build? Air-gapped NL assistant that is integrated with Splunk](https://redlib.catsarch.com/r/LocalLLaMA/comments/1tnpg9h/need_help_what_would_you_build_airgapped_nl/)

9  Upvotes

So I have a side project with given scope:

*   Fully air-gapped / on-prem - no internet, no outbound calls of any kind
*   Engineers ask questions about Splunk data in natural language
*   Has to hold the conversation in Korean (index/field names stay English)
*   Local/small models preferred, needs to fit a modest GPU - was looking at Qwen/Gemma4 but indexing more on what is good enough small model to have decent performance
*   Some memory across the session (not required, but at least within the current session would be nice)
*   Strictly read-only and safe enough to point at prod logs

I am thinking simple chat interface (like claude, openAI style) where we give Splunk API access for AI to retrieve and reason.

2 Questions:

*   I was thinking deploying like Openclaw/Hermes agent + small language model to start - because I really like the interaction with them. Is there any better or easier way to achieve similar experience? (vLM, ollama, open WebUI, any suggestions would be nice)
*   In terms of outcome, what do you think we can actually let it do? log analysis? RCA? basic questions?

Pretty new to this and trying to learn.. any initial guidance or tips would be awesome!

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[What's your Snowstorm model arsenal?](https://redlib.catsarch.com/r/LocalLLaMA/comments/1qjgnsg/whats_your_snowstorm_model_arsenal/)

2  Upvotes

Hey folks,

Might lose power over the weekend, would like to prepare for the apocalypse :)

I got 64 smol GBs to work with, or I could load 1 layer at a time and get s/tok instead.

I currently have:

1.   Qwen 3 VL 30B A3B: if my wounds get infected, I'd need to show the model.
2.   GPT-OSS-20B: I heard this model was meant for safety.
3.   translategemma-27b-it: I don't speak Korean.
4.   DeepSeek-V3.2: I don't really know what I'm doing with this one.
5.   Z-Image-Turbo: If I forget what the outside looks like

Yes, I know I'd lose power. The 64GBs are in a _lithium-ion battery-powered_ laptop.

What's your arsenal?

## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[I built MimikaStudio - a native macOS app for voice cloning using Qwen, Kokoro and XTTS2](https://redlib.catsarch.com/r/LocalLLaMA/comments/1qnlylb/i_built_mimikastudio_a_native_macos_app_for_voice/)

15  Upvotes

**MimikaStudio** is a local-first voice cloning and TTS desktop app.

Clone any voice from just 3 seconds of audio, use premium preset speakers, or generate fast high-quality speech for narration and content creation.

[![Image 7](https://redlib.catsarch.com/preview/pre/fkmq0nbb6qfg1.png?width=3218&format=png&auto=webp&s=ab708d8722fcaca54067eb8a9556a0a69c76a73d)](https://redlib.catsarch.com/preview/pre/fkmq0nbb6qfg1.png?width=3218&format=png&auto=webp&s=ab708d8722fcaca54067eb8a9556a0a69c76a73d)
I ported my old Gradio app into a beautiful native Flutter desktop application, specifically for Apple Silicon users who want a polished UI with proper macOS integration.

## Key Features

*   **3-Second Voice Cloning** Qwen3-TTS can capture a speaker's tone, rhythm, and accent from remarkably short samples
*   **9 Premium Preset Voices** No reference audio needed. English, Chinese, Japanese, Korean speakers with distinct personalities
*   **Fast British TTS** Kokoro delivers sub-200ms latency with crystal-clear British RP and American accents
*   **PDF Reader** Load any PDF and have it read aloud with sentence-by-sentence highlighting
*   **Emma IPA** British phonetic transcription powered by your choice of LLM (Claude, OpenAI, Ollama)
*   **Runs locally** No cloud APIs for TTS, everything on your machine

[![Image 8](https://redlib.catsarch.com/preview/pre/i5e7o7ce6qfg1.png?width=3164&format=png&auto=webp&s=03aeb964b75237396d16c8b6b9d98c62f1b8db4a)](https://redlib.catsarch.com/preview/pre/i5e7o7ce6qfg1.png?width=3164&format=png&auto=webp&s=03aeb964b75237396d16c8b6b9d98c62f1b8db4a)
## Tech Stack

*   Flutter desktop UI (macOS)
*   FastAPI Python backend
*   Qwen3-TTS (0.6B/1.7B), Kokoro-82M, XTTS2
*   Apple Silicon optimized (MPS where supported)

## GitHub

[https://github.com/BoltzmannEntropy/MimikaStudio](https://github.com/BoltzmannEntropy/MimikaStudio)

Happy to answer any questions!

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[Qwen 3.5 35b a3b opus distilled hanging problem](https://redlib.catsarch.com/r/LocalLLaMA/comments/1sady9v/qwen_35_35b_a3b_opus_distilled_hanging_problem/)

1  Upvotes

I am basically Korean who started to use local llm.

I'm using qwen 3.5 35b-a3b opus distilled version since in vanilla qwen 3.5 35b a3b version keep calls tool inside the thinking block

It is quite good but if I use language other then English it hangs before tool call

like

I will read the file now:

and does nothing. Is this impossible thing to solve it or can it be solved with prompt. Basically it never happpens in English but in Korean.

Thank you for reading my bad english

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[LLM model scandle in South Korea](https://redlib.catsarch.com/r/LocalLLaMA/comments/1q5cdfu/llm_model_scandle_in_south_korea/)

5  Upvotes

Sorry for my bad english.

Following the recent controversy debates surrounding the Upstage's Solar-open model, NAVER - a leading Korean tech company, is now facing allegations that its HyperCLOVA OMNI 8B model adopted QWEN's vision & audio encoder without reference.

Many users in Korea believe this national competition was conducted on the basis of "starting from scratch." While there is no dispute that NAVER independently developed the model's text generation component, it will likely be difficult to avoid criticism for NAVER positioning the OMNI model as a distinctive feature compared to other companies.

[https://m.news.nate.com/view/20260105n29281](https://m.news.nate.com/view/20260105n29281) (Korean news link)

HyperCLOVA X SEED 8B Omni: [https://huggingface.co/naver-hyperclovax/HyperCLOVAX-SEED-Omni-8B](https://huggingface.co/naver-hyperclovax/HyperCLOVAX-SEED-Omni-8B)

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[Tips that might help you using your LLM to do language translation.](https://redlib.catsarch.com/r/LocalLLaMA/comments/1lklzav/tips_that_might_help_you_using_your_llm_to_do/)

32  Upvotes

After using LLM translation for production work(Korean<->English<->Chinese) for some time and got some experiences. I think I can share some idea that might help you improve your translation quality.

*   Give it context, detailed context.
*   If it is a text, tells it what this text is about. Briefly.
*   If it is a conversation, assign name to each person. Prompt the model what it he/she doing, and insert context along the way. Give it the whole conversation, not individual line.
*   **Prompt the model to repeat the original text before translating.** This will drastically reduce the hallucination, especially if it's a non-thinking model.
*   Prompt it to analysis each section or even individual sentence. Sometimes they might pick the wrong word in the translation result, but give you the correct one in the analysis.
*   If the model is not fine tuned to a certain format, don't prompt it to input/output in that format. This will reduce the quality of translation by a lot, especially in small model.
*   Try to translate it into English first, this is especially true for general model without the fine tuning.
*   Assert how good the model is in the language by giving it some simple task in the source/target language. If it can't understand the task, it can't translate that.

A lot of these advice will eats a lot of context window, but it's the price to pay if you want high quality translation.

Now, for my personal experience:

For the translation task, I like Gemini Pro the most, I literally had a wow moment when I fist saw the result. It even understand the subtle tone change in the Korean conversation and knows why. For the first time I don't have to do any editing/polishing on the output and could just copy and paste. It gets every merit correctly with an original content.

The local counterpart Gemma 3 12/27b QAT is also pretty good. It might missed a few in-joke but as a local model without fine tuning, most of time it's gets the meaning correct and "good enough". But it's really sensitive to the system prompt, if you don't prompt it correctly it will hallucinate to hell.

Qwen 3 32b q4k-xl is meh unless it's being fine tuned(even QwQ 32b is better than Qwen3 32b). "Meh" means it sometime gets the meaning of the sentence wrong in about 1 of 10, often with wrong words being used.

Deepseek R1-0528 671b FP8 is also meh, for its size it has greater vocabulary but otherwise the result isn't really better than Gemma3.

ChatGPT 4o/o3 as a online model is okay-ish, it can get the meaning correctly but often loses the merit, as a result it often need polishing. It also seems to have less data on Korean. O3 seems to have some regression on translation. I don't have access to o4.

## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[MyOllama: A Free, Open-Source Mobile Client for Ollama LLMs (iOS/Android)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1h2asn9/myollama_a_free_opensource_mobile_client_for/)

3  Upvotes

Hey everyone! 👋

I wanted to share MyOllama, an open-source mobile client I've been working on that lets you interact with Ollama-based LLMs on your mobile devices. If you're into LLM development or research, this might be right up your alley.

**What makes it cool:**

* No cloud BS - runs entirely on your local machine

* Built with Flutter (iOS & Android support)

* Works with various LLM models (Llama, Gemma, Qwen, Mistral)

* Image recognition support

* Markdown support

* Available in English, Korean, and Japanese

**Technical stuff you might care about:**

* Remote LLM access via IP config

* Custom prompt engineering

* Persistent conversation management

* Privacy-focused architecture

* No subscription fees (ever!)

* Easy API integration with Ollama backend

**Where to get it:**

* GitHub: [https://github.com/bipark/my_ollama_app](https://github.com/bipark/my_ollama_app)

* App Store: [https://apps.apple.com/us/app/my-ollama/id6738298481](https://apps.apple.com/us/app/my-ollama/id6738298481)

The whole thing is released under GNU license, so feel free to fork it and make it your own!

Let me know if you have any questions or feedback. Would love to hear your thoughts! 🚀

Edit: Thanks for all the feedback, everyone! Really appreciate the support!

[![Image 9](https://redlib.catsarch.com/preview/pre/h9gb1ori5r3e1.jpg?width=1122&format=pjpg&auto=webp&s=803910208f12ca27403e0b979c8773748b9d25cd)](https://redlib.catsarch.com/preview/pre/h9gb1ori5r3e1.jpg?width=1122&format=pjpg&auto=webp&s=803910208f12ca27403e0b979c8773748b9d25cd)

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[Qwen often output chinese](https://redlib.catsarch.com/r/LocalLLaMA/comments/1hlitkn/qwen_often_output_chinese/)

12  Upvotes

When I evaluate Qwen model on my own test data, There is a problem with Chinese being mixed in the middle of the output.

Is this a typical qwen model issue, or is it because the data is in Korean? ( I'm Korean :) )

Even if I modify the prompt a little bit, such as "Do not include Chinese in your answer.", nothing changes.

Have you guys had similar experiences? Or any suggestions?

## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[openbmb/MiniCPM-Llama3-V-2_5 in llama.cpp](https://redlib.catsarch.com/r/LocalLLaMA/comments/1eppklz/openbmbminicpmllama3v2_5_in_llamacpp/)

24  Upvotes

The model has been released back in May 2024, but llama.cpp finally merged [the support for openbmb/MiniCPM-Llama3-V-2_5](https://github.com/ggerganov/llama.cpp/pull/7599) 2 days ago.

The [support for 2.6](https://github.com/ggerganov/llama.cpp/pull/8967) is also on the way soon. If you want to try 2.6 before getting merged, [try this](https://redlib.catsarch.com/r/LocalLLaMA/comments/1ereuk5/you_can_now_try_minicpmv_26_if_you_build_llamacpp/) instead.

Here's the [official gguf.](https://huggingface.co/openbmb/MiniCPM-Llama3-V-2_5-gguf)

### [Model Summary from their Huggingface:](https://huggingface.co/openbmb/MiniCPM-Llama3-V-2_5)

MiniCPM-Llama3-V 2.5 is the latest model in the MiniCPM-V series. The model is built on SigLip-400M and Llama3-8B-Instruct with a total of 8B parameters. It exhibits a significant performance improvement over MiniCPM-V 2.0. Notable features of MiniCPM-Llama3-V 2.5 include:

*   🔥 Leading Performance. MiniCPM-Llama3-V 2.5 has achieved an average score of 65.1 on OpenCompass, a comprehensive evaluation over 11 popular benchmarks. With only 8B parameters, it surpasses widely used proprietary models like GPT-4V-1106, Gemini Pro, Claude 3 and Qwen-VL-Max and greatly outperforms other Llama 3-based MLLMs.
*   💪 Strong OCR Capabilities. MiniCPM-Llama3-V 2.5 can process images with any aspect ratio and up to 1.8 million pixels (e.g., 1344x1344), achieving an 700+ score on OCRBench, surpassing proprietary models such as GPT-4o, GPT-4V-0409, Qwen-VL-Max and Gemini Pro. Based on recent user feedback, MiniCPM-Llama3-V 2.5 has now enhanced full-text OCR extraction, table-to-markdown conversion, and other high-utility capabilities, and has further strengthened its instruction-following and complex reasoning abilities, enhancing multimodal interaction experiences.
*   🏆 Trustworthy Behavior. Leveraging the latest RLAIF-V method (the newest technology in the RLHF-V [CVPR'24] series), MiniCPM-Llama3-V 2.5 exhibits more trustworthy behavior. It achieves 10.3% hallucination rate on Object HalBench, lower than GPT-4V-1106 (13.6%), achieving the best-level performance within the open-source community. Data released.
*   🌏 Multilingual Support. Thanks to the strong multilingual capabilities of Llama 3 and the cross-lingual generalization technique from VisCPM, MiniCPM-Llama3-V 2.5 extends its bilingual (Chinese-English) multimodal capabilities to over 30 languages including German, French, Spanish, Italian, Korean, Japanese etc. All Supported Languages.
*   🚀 Efficient Deployment. MiniCPM-Llama3-V 2.5 systematically employs model quantization, CPU optimizations, NPU optimizations and compilation optimizations, achieving high-efficiency deployment on edge devices. For mobile phones with Qualcomm chips, we have integrated the NPU acceleration framework QNN into llama.cpp for the first time. After systematic optimization, MiniCPM-Llama3-V 2.5 has realized a 150-fold acceleration in multimodal large model end-side image encoding and a 3-fold increase in language decoding speed.
*   💫 Easy Usage. MiniCPM-Llama3-V 2.5 can be easily used in various ways: (1) llama.cpp and ollama support for efficient CPU inference on local devices, (2) GGUF format quantized models in 16 sizes, (3) efficient LoRA fine-tuning with only 2 V100 GPUs, (4) streaming output, (5) quick local WebUI demo setup with Gradio and Streamlit, and (6) interactive demos on HuggingFace Spaces.

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[We're releasing some new multipurpose RAG models called Kurage (Kuh-rah-geh) that can function in 44 languages. I hope you find them useful!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1figwbk/were_releasing_some_new_multipurpose_rag_models/)

76  Upvotes

Edit: Koo-rah-geh is the correct pronunciation.

We've fine-tuned Qwen 2 7B Instruct to perform RAG in a bunch of useful settings in 44 languages.

The 44 languages are: Amharic, Arabic, Bulgarian, Bengali, Czech, Danish, German, Greek, English, Spanish, Persian, Finnish, French, Gujarati, Hausa, Hindi, Hungarian, Indonesian, Italian, Japanese, Javanese, Kannada, Korean, Lithuanian, Marathi, Dutch, Norwegian, Polish, Portuguese, Romanian, Russian, Slovak, Swedish, Swahili, Tamil, Telugu, Thai, Tagalog, Turkish, Ukrainian, Urdu, Vietnamese, Yoruba, Chinese.

We've trained these models to perform:

*   **Multi-chunk RAG** - Performs RAG using multiple contexts at once.
*   **Single-chunk RAG** - Performs RAG using one context at a time, allowing for parallel computing.
*   **Answer extension** - Prompts the model to write a longer answer to a given question.
*   **Multilingual RAG** - Performs RAG using contexts in languages different to the language of the question.
*   **Q&A generation** - Generates questions and answers from a reference text in order to pre-index a set of texts.

From my testing, there is a known issue with the single-chunk RAG mode sometimes saying that it cannot answer a question based on the text when it actually can. This was because our single-chunk training data was 50:50 answers vs cannot answer scenarios, making the model overly conservative. We'll release a fixed version in a week or so when we retrain using more unbalanced 90:10 data on Qwen 2.5 when that gets released. Stay posted for that!

The answer extension also seems to only work in some cases, but may be useful in the cases where it does work. In the training data, I added the <<Long>> code to the 20% of answers with the longest answer for each language. We will up this to 10% for future training in an attempt to make this mode more reliable too.

I hope you find these models useful and, as always, good faith criticism and feedback are always welcome!

**Model links**:

*   [Multilingual model](https://huggingface.co/lightblue/kurage-multilingual) (44 languages)
*   [English model](https://huggingface.co/lightblue/kurage-en)
*   [Other language models](https://huggingface.co/collections/lightblue/kurage-66e40cbcc3b3a128bdf031f2) (Arabic, Spanish, Hindi, Indonesian, Japanese, Korean, Thai, Swahili, Vietnamese, Chinese)

**Data link**:

*   [Training data](https://huggingface.co/datasets/lightblue/kurage_training_data)

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[Bounding box in forms](https://redlib.catsarch.com/r/LocalLLaMA/comments/1jd26c4/bounding_box_in_forms/)

[![Image 10: Post image](https://redlib.catsarch.com/img/530ucv5os5pe1.jpeg)](https://redlib.catsarch.com/img/530ucv5os5pe1.jpeg)

1  Upvotes

Is there any model capable of finding bounding box in form for question text fields and empty input fields like the above image (I manually added bounding box)? I tried Qwen 2.5 VL, but the coordinates is not matching with the image.

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[dnotitia/Llama-DNA-1.0-8B-Instruct, state-of-the-art (SOTA) bilingual language model](https://redlib.catsarch.com/r/LocalLLaMA/comments/1hb9zfb/dnotitiallamadna108binstruct_stateoftheart_sota/)

10  Upvotes

[https://huggingface.co/dnotitia/Llama-DNA-1.0-8B-Instruct](https://huggingface.co/dnotitia/Llama-DNA-1.0-8B-Instruct)

**DNA 1.0 8B Instruct**is a state-of-the-art (**SOTA**)bilingual language model based on Llama architecture, specifically optimized for Korean language understanding and generation, while also maintaining strong English capabilities.

| Language | Benchmark | **dnotitia/Llama-DNA-1.0-8B-Instruct** | LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct | LGAI-EXAONE/EXAONE-3.0-7.8B-Instruct | yanolja/EEVE-Korean-Instruct-10.8B-v1.0 | Qwen/Qwen2.5-7B-Instruct | meta-llama/Llama-3.1-8B-Instruct | mistralai/Mistral-7B-Instruct-v0.3 | NCSOFT/Llama-VARCO-8B-Instruct | upstage/SOLAR-10.7B-Instruct-v1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Korean | KMMLU | **53.26**(1st) | 45.30 | 45.28 | 42.17 | 45.66 | 41.66 | 31.45 | 38.49 | 41.50 |
|  | KMMLU-hard | **29.46**(1st) | 23.17 | 20.78 | 19.25 | 24.78 | 20.49 | 17.86 | 19.83 | 20.61 |
|  | KoBEST | **83.40**(1st) | 79.05 | 80.13 | 81.67 | 78.51 | 67.56 | 63.77 | 72.99 | 73.26 |
|  | Belebele | **57.99**(1st) | 40.97 | 45.11 | 49.40 | 54.85 | 54.70 | 40.31 | 53.17 | 48.68 |
|  | CSATQA | 43.32(2nd) | 40.11 | 34.76 | 39.57 | **45.45** | 36.90 | 27.27 | 32.62 | 34.22 |
| English | MMLU | 66.64 (3rd) | 65.27 | 64.32 | 63.63 | **74.26** | 68.26 | 62.04 | 63.25 | 65.30 |
|  | MMLU-Pro | **43.05**(1st) | 40.73 | 38.90 | 32.79 | 42.5 | 40.92 | 33.49 | 37.11 | 30.25 |
|  | GSM8K | **80.52**(1st) | 65.96 | 80.06 | 56.18 | 75.74 | 75.82 | 49.66 | 64.14 | 69.22 |
[![Image 11](https://redlib.catsarch.com/preview/pre/oqp2trs8p26e1.png?width=703&format=png&auto=webp&s=2b32d15501907b2aa4f25828f8cd756d09cf548c)](https://redlib.catsarch.com/preview/pre/oqp2trs8p26e1.png?width=703&format=png&auto=webp&s=2b32d15501907b2aa4f25828f8cd756d09cf548c)
