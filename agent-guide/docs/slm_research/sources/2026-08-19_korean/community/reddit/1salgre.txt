Title: Gemma 4 has been released - r/LocalLLaMA

URL Source: https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/

Markdown Content:
[red lib.](https://redlib.catsarch.com/)

Feeds

MAIN FEEDS

[Home](https://redlib.catsarch.com/)[Popular](https://redlib.catsarch.com/r/popular)[All](https://redlib.catsarch.com/r/all)

- [x] in /r/LocalLLaMA 

[reddit](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/#popup)

# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/comments/1salgre/

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1salgre/)

[settings](https://redlib.catsarch.com/settings)

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp•Apr 02 '26

# [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on) Gemma 4 has been released

[https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF)

[https://huggingface.co/unsloth/gemma-4-31B-it-GGUF](https://huggingface.co/unsloth/gemma-4-31B-it-GGUF)

[https://huggingface.co/unsloth/gemma-4-E4B-it-GGUF](https://huggingface.co/unsloth/gemma-4-E4B-it-GGUF)

[https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF](https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF)

[https://huggingface.co/collections/google/gemma-4](https://huggingface.co/collections/google/gemma-4)

**What’s new in Gemma 4**[https://www.youtube.com/watch?v=jZVBoFOJK-Q](https://www.youtube.com/watch?v=jZVBoFOJK-Q)

Gemma is a family of open models built by Google DeepMind. Gemma 4 models are multimodal, handling text and image input (with audio supported on small models) and generating text output. This release includes open-weights models in both pre-trained and instruction-tuned variants. Gemma 4 features a context window of up to 256K tokens and maintains multilingual support in over 140 languages.

Featuring both Dense and Mixture-of-Experts (MoE) architectures, Gemma 4 is well-suited for tasks like text generation, coding, and reasoning. The models are available in four distinct sizes: **E2B**, **E4B**, **26B A4B**, and **31B**. Their diverse sizes make them deployable in environments ranging from high-end phones to laptops and servers, democratizing access to state-of-the-art AI.

Gemma 4 introduces key **capability and architectural advancements**:

*   **Reasoning** – All models in the family are designed as highly capable reasoners, with configurable thinking modes.
*   **Extended Multimodalities** – Processes Text, Image with variable aspect ratio and resolution support (all models), Video, and Audio (featured natively on the E2B and E4B models).
*   **Diverse & Efficient Architectures** – Offers Dense and Mixture-of-Experts (MoE) variants of different sizes for scalable deployment.
*   **Optimized for On-Device** – Smaller models are specifically designed for efficient local execution on laptops and mobile devices.
*   **Increased Context Window** – The small models feature a 128K context window, while the medium models support 256K.
*   **Enhanced Coding & Agentic Capabilities** – Achieves notable improvements in coding benchmarks alongside native function-calling support, powering highly capable autonomous agents.
*   **Native System Prompt Support** – Gemma 4 introduces native support for the `system` role, enabling more structured and controllable conversations.

# Models Overview

Gemma 4 models are designed to deliver frontier-level performance at each size, targeting deployment scenarios from mobile and edge devices (E2B, E4B) to consumer GPUs and workstations (26B A4B, 31B). They are well-suited for reasoning, agentic workflows, coding, and multimodal understanding.

The models employ a hybrid attention mechanism that interleaves local sliding window attention with full global attention, ensuring the final layer is always global. This hybrid design delivers the processing speed and low memory footprint of a lightweight model without sacrificing the deep awareness required for complex, long-context tasks. To optimize memory for long contexts, global layers feature unified Keys and Values, and apply Proportional RoPE (p-RoPE).

**Core Capabilities**

Gemma 4 models handle a broad range of tasks across text, vision, and audio. Key capabilities include:

*   **Thinking** – Built-in reasoning mode that lets the model think step-by-step before answering.
*   **Long Context** – Context windows of up to 128K tokens (E2B/E4B) and 256K tokens (26B A4B/31B).
*   **Image Understanding** – Object detection, Document/PDF parsing, screen and UI understanding, chart comprehension, OCR (including multilingual), handwriting recognition, and pointing. Images can be processed at variable aspect ratios and resolutions.
*   **Video Understanding** – Analyze video by processing sequences of frames.
*   **Interleaved Multimodal Input** – Freely mix text and images in any order within a single prompt.
*   **Function Calling** – Native support for structured tool use, enabling agentic workflows.
*   **Coding** – Code generation, completion, and correction.
*   **Multilingual** – Out-of-the-box support for 35+ languages, pre-trained on 140+ languages.
*   **Audio** (E2B and E4B only) – Automatic speech recognition (ASR) and speech-to-translated-text translation across multiple languages.

[![Image 3](https://redlib.catsarch.com/preview/pre/3dbm6nhrvssg1.png?width=1282&format=png&auto=webp&s=8625d113e9baa3fab79a780fd074a5b36e4d6f0c)](https://redlib.catsarch.com/preview/pre/3dbm6nhrvssg1.png?width=1282&format=png&auto=webp&s=8625d113e9baa3fab79a780fd074a5b36e4d6f0c)[![Image 4](https://redlib.catsarch.com/preview/pre/mtzly5myxssg1.png?width=1200&format=png&auto=webp&s=5c95a73ff626ebeafd3645d2e00697c793fa0b16)](https://redlib.catsarch.com/preview/pre/mtzly5myxssg1.png?width=1200&format=png&auto=webp&s=5c95a73ff626ebeafd3645d2e00697c793fa0b16)

 2.3k  Upvotes

*   [perma link](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/)
*   [dup licat es](https://redlib.catsarch.com/r/LocalLLaMA/duplicates/1salgre)
*   [reddit](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/#popup)# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/)  

97% Upvoted

674 comments sorted by

•

[u/WithoutReason1729](https://redlib.catsarch.com/user/WithoutReason1729)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxmcjn/?context=3#odxmcjn "Apr 02 2026, 18:50:15 UTC")

Your post is getting popular and we just featured it on our Discord! [Come check it out!](https://discord.gg/PgFhZ8cnWW)

You've also been given a special flair for your contribution. We appreciate your post!

_I am a bot and this action was performed automatically._

537

[u/Both_Opportunity5327](https://redlib.catsarch.com/user/Both_Opportunity5327)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwmofc/?context=3#odwmofc "Apr 02 2026, 16:07:14 UTC")

Google is going to show what open weights is about.

Happy Easter everyone.

> 116
> 
> 
> 
> [u/Daniel_H212](https://redlib.catsarch.com/user/Daniel_H212)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwsocn/?context=3#odwsocn "Apr 02 2026, 16:35:10 UTC")
> 
> Wish they'd release bigger models though, a 100B MoE from them could be great without threatening their proprietary models. Hopefully one is coming later?
> 
> 
> > 149
> > 
> > 
> > 
> > [u/sininspira](https://redlib.catsarch.com/user/sininspira)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwx0u9/?context=3#odwx0u9 "Apr 02 2026, 16:55:07 UTC")
> > 
> > If the 31b is as good as the open model rankings suggest, they don't really *need* to release a bigger one at the moment...
> > 
> > 
> > > [→ More replies (7)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwx0u9)
> > 
> > 
> > 
> > 46
> > 
> > 
> > 
> > [u/RedParaglider](https://redlib.catsarch.com/user/RedParaglider)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwvf8r/?context=3#odwvf8r "Apr 02 2026, 16:47:53 UTC")
> > 
> > Man 80-120 would be killer, but I'm happy to have what they just released!
> > 
> > 
> > 
> > 20
> > 
> > 
> > 
> > [u/RottenPingu1](https://redlib.catsarch.com/user/RottenPingu1)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwxww4/?context=3#odwxww4 "Apr 02 2026, 16:59:06 UTC")
> > 
> > I'd settle for 70B
> > 
> > 
> > 
> > 19
> > 
> > 
> > 
> > [u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx6pl0/?context=3#odx6pl0 "Apr 02 2026, 17:38:30 UTC")
> > 
> > either the 124B model was too weak and did not beat smaller ones in benchmarks/ELO, or it was too strong and threatened Gemini
> > 
> > 
> > > 15
> > > 
> > > 
> > > 
> > > [u/Daniel_H212](https://redlib.catsarch.com/user/Daniel_H212)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxopvk/?context=3#odxopvk "Apr 02 2026, 19:01:13 UTC")
> > > 
> > > Or, and I hope this is the case, the 124B just hasn't finished training yet so they're releasing the smaller ones first.
> > > 
> > > 
> > > > 21
> > > > 
> > > > 
> > > > 
> > > > [u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxw2jz/?context=3#odxw2jz "Apr 02 2026, 19:36:06 UTC")
> > > > 
> > > > actually you may be right, please notice this sentence:
> > > > 
> > > > 
> > > > **Increased Context Window** – The small models feature a 128K context window, while the medium models support 256K.
> > > > 
> > > > 
> > > > if you don't see what i see, read again... :)
> > > > 
> > > > 
> > > > > 14
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/msaraiva](https://redlib.catsarch.com/user/msaraiva)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odydq6h/?context=3#odydq6h "Apr 02 2026, 20:59:55 UTC")
> > > > > 
> > > > > Yeah, I also noticed they purposefully used "small" and "medium". Hopefully that means a "large" model is coming soon.
> > > > > 
> > > > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxw2jz)
> > > 
> > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx6pl0)
> > 
> > [→ More replies (13)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwsocn)
> 
> 
> 
> 8
> 
> 
> 
> [u/ThiccStorms](https://redlib.catsarch.com/user/ThiccStorms)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwzjg0/?context=3#odwzjg0 "Apr 02 2026, 17:06:28 UTC")
> 
> I'm very excited for the 2b!
> 
> [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwmofc)

524

[u/danielhanchen](https://redlib.catsarch.com/user/danielhanchen)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwrbn5/?context=3#odwrbn5 "Apr 02 2026, 16:28:48 UTC")

*   Gemma-4 has **native thinking, tool calling and is multimodal!**
*   Use temperature = 1.0, top_p = 0.95, top_k = 64 and the EOS is `<turn|>`. `<|channel>thought\n` is also used for the thinking trace!
*   Guide to run them at [https://unsloth.ai/docs/models/gemma-4](https://unsloth.ai/docs/models/gemma-4)
*   Gemma-4 also works seamlessly in Unsloth Studio! [https://unsloth.ai/docs/new/studio](https://unsloth.ai/docs/new/studio)
*   All GGUFs at [https://huggingface.co/collections/unsloth/gemma-4](https://huggingface.co/collections/unsloth/gemma-4)

> 124
> 
> 
> 
> [u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwskci/?context=3#odwskci "Apr 02 2026, 16:34:39 UTC")
> 
> thanks for the quick GGUF release!!!
> 
> 
> > 56
> > 
> > 
> > 
> > [u/danielhanchen](https://redlib.catsarch.com/user/danielhanchen)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwwccq/?context=3#odwwccq "Apr 02 2026, 16:52:04 UTC")
> > 
> > Thanks for the post as well haha - you we were lightning fast as well :)
> 
> 
> 
> 40
> 
> 
> 
> [u/NoahFect](https://redlib.catsarch.com/user/NoahFect)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odww7zq/?context=3#odww7zq "Apr 02 2026, 16:51:31 UTC")
> 
> Hey, quick question re: Unsloth Studio. I'm thinking of switching over to it from my existing llama.cpp installation, but why do I need to create an account to run stuff locally?
> 
> 
> > 23
> > 
> > 
> > 
> > [u/danielhanchen](https://redlib.catsarch.com/user/danielhanchen)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwwjqs/?context=3#odwwjqs "Apr 02 2026, 16:52:59 UTC")edited Apr 02 '26
> > 
> > It's out! See [https://github.com/unslothai/unsloth?tab=readme-ov-file#-quickstart](https://github.com/unslothai/unsloth?tab=readme-ov-file#-quickstart)
> > 
> > 
> > For Linux, WSL, Mac: `curl -fsSL https://unsloth.ai/install.sh | sh` For Windows: `irm https://unsloth.ai/install.ps1 | iex`
> > 
> > 
> > > 5
> > > 
> > > 
> > > 
> > > [u/Qual_](https://redlib.catsarch.com/user/Qual_)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwyr8d/?context=3#odwyr8d "Apr 02 2026, 17:02:53 UTC")
> > > 
> > > Waiting for the docker update ! :D
> > > 
> > > 
> > > ( seems like I can find the model if I copy the hf link, but gemma 4 does not appear by itself in the search :
> > > 
> > > [![Image 5](https://redlib.catsarch.com/preview/pre/6ieufalx6tsg1.png?width=1108&format=png&auto=webp&s=9f76c4ca9773f7c437a2aefdfaf87fe8e9e44b1d)](https://redlib.catsarch.com/preview/pre/6ieufalx6tsg1.png?width=1108&format=png&auto=webp&s=9f76c4ca9773f7c437a2aefdfaf87fe8e9e44b1d)
> > > 
> > > 
> > > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwyr8d)
> > 
> > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odww7zq)
> 
> 
> 
> 12
> 
> 
> 
> [u/970FTW](https://redlib.catsarch.com/user/970FTW)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwv7ia/?context=3#odwv7ia "Apr 02 2026, 16:46:54 UTC")
> 
> Truly the best to ever do it lol
> 
> 
> > 8
> > 
> > 
> > 
> > [u/danielhanchen](https://redlib.catsarch.com/user/danielhanchen)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwwctb/?context=3#odwwctb "Apr 02 2026, 16:52:08 UTC")
> > 
> > Thanks!
> 
> 
> 
> 5
> 
> 
> 
> [u/Daniel_H212](https://redlib.catsarch.com/user/Daniel_H212)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxrwgp/?context=3#odxrwgp "Apr 02 2026, 19:16:13 UTC")
> 
> It seems like native tool calling isn't working very well. Is this a model problem or me? I'm running 26B-A4B at UD-Q6_K_XL with all the same settings in OpenWebUI as Qwen3.5-35B-A3B also at the same quant, (native tool calling on, web search and web scrape tools enabled), plus with <|think|> at the start of the system prompt to enforce thinking, and when given a research task, Qwen3.5 did a web search (searxng, so only snippets were returned from each result) and then scraped 5 specific pages, while gemma 4 did a web search, summarised, came up with a research plan, and then immediately gave me a response without actually following through with its research plan.
> 
> 
> It did this somewhat consistently. The one time it did try fetch_url after search_web, it happened to fetch a page that was down (which returned an empty result), and it just went into responding as if it never planned on doing further research in the first place, nor did it try the alternative web_scrape function that I also have available (which I noted in the system prompt as a more reliable backup to fetch_url).
> 
> 
> I also tried telling it to do further research after its first message, which caused it to use search_web twice, still no fetch_url. I then tried telling it to use its other search tools, after which it tried web_scrape once, which got it some results, and it just gave up. There's zero persistence in its research.
> 
> 
> > 9
> > 
> > 
> > 
> > [u/danielhanchen](https://redlib.catsarch.com/user/danielhanchen)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxzgfc/?context=3#odxzgfc "Apr 02 2026, 19:52:13 UTC")
> > 
> > Try Unsloth Studio - it works wonders in it! We tried very hard to make tool calling work well - sadly nowadays it's not the model, but rather the harness / tool that's more problematic
> > 
> > [![Image 6](https://redlib.catsarch.com/preview/pre/q26cxh2o0usg1.png?width=2880&format=png&auto=webp&s=502c2cc5c710d6700f2d0af45f0de144adaf0121)](https://redlib.catsarch.com/preview/pre/q26cxh2o0usg1.png?width=2880&format=png&auto=webp&s=502c2cc5c710d6700f2d0af45f0de144adaf0121)
> > 
> > 
> > > [→ More replies (10)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxzgfc)
> > 
> > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxrwgp)
> 
> 
> 
> 7
> 
> 
> 
> [u/illcuontheotherside](https://redlib.catsarch.com/user/illcuontheotherside)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxs3kv/?context=3#odxs3kv "Apr 02 2026, 19:17:08 UTC")
> 
> You guys ROCK!!!
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxs3kv)
> 
> [→ More replies (10)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwrbn5)

386

[u/Altruistic_Heat_9531](https://redlib.catsarch.com/user/Altruistic_Heat_9531)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwqmum/?context=3#odwqmum "Apr 02 2026, 16:25:36 UTC")

[![Image 7](https://redlib.catsarch.com/preview/pre/qg7b58pszssg1.jpeg?width=500&format=pjpg&auto=webp&s=4a2a21419855733128a49ce7baa74505addd7025)](https://redlib.catsarch.com/preview/pre/qg7b58pszssg1.jpeg?width=500&format=pjpg&auto=webp&s=4a2a21419855733128a49ce7baa74505addd7025)

> 417
> 
> 
> 
> [u/Altruistic_Heat_9531](https://redlib.catsarch.com/user/Altruistic_Heat_9531)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwsxjg/?context=3#odwsxjg "Apr 02 2026, 16:36:21 UTC")
> 
> And after a week maybe : "Gemma 4 26B Heretic Uncensored Ablated Claude Opus 4.6 Reasoning Distlled Expanded fine tuned quantized"
> 
> 
> Sorry to tempting lol
> 
> 
> > 124
> > 
> > 
> > 
> > [u/LagOps91](https://redlib.catsarch.com/user/LagOps91)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwvry8/?context=3#odwvry8 "Apr 02 2026, 16:49:30 UTC")
> > 
> > you forgot turbo quant in there!
> > 
> > 
> > > 19
> > > 
> > > 
> > > 
> > > [u/Noturavgrizzposter](https://redlib.catsarch.com/user/Noturavgrizzposter)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odykawe/?context=3#odykawe "Apr 02 2026, 21:32:33 UTC")
> > > 
> > > and engram and attention residuals
> > > 
> > > 
> > > > 5
> > > > 
> > > > 
> > > > 
> > > > [u/ethertype](https://redlib.catsarch.com/user/ethertype)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odytz3o/?context=3#odytz3o "Apr 02 2026, 22:22:09 UTC")
> > > > 
> > > > And Bonsai
> > 
> > 
> > 
> > 53
> > 
> > 
> > 
> > [u/bucolucas](https://redlib.catsarch.com/user/bucolucas)Llama 3.1[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx9xnt/?context=3#odx9xnt "Apr 02 2026, 17:52:54 UTC")
> > 
> > "Hey guys which one of the Gemma models is best at 'unconventional roleplay?'"
> > 
> > 
> > *hint hint nod nod wink wink*
> > 
> > 
> > Also it needs to fit inside 1.5GB NVIDIA card from 1999, be able to generate images, and run at 9000 tokens/second
> > 
> > 
> > > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx9xnt)
> > 
> > 
> > 
> > 41
> > 
> > 
> > 
> > [u/ea_nasir_official_](https://redlib.catsarch.com/user/ea_nasir_official_)vllm[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odylkts/?context=3#odylkts "Apr 02 2026, 21:38:57 UTC")
> > 
> > Claude: safety
> > 
> > 
> > Gpt: wasting money
> > 
> > 
> > Google: tracking us all
> > 
> > 
> > LocalLlama: UNCENSORED TURBORAPIST CLAUDE DISTILL QWENGEMMA CODER MOE ABLITERATED 6.9B UD-IQ69420
> > 
> > 
> > > 5
> > > 
> > > 
> > > 
> > > [u/Borkato](https://redlib.catsarch.com/user/Borkato)[Apr 03 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odzz59y/?context=3#odzz59y "Apr 03 2026, 02:17:22 UTC")
> > > 
> > > Turbo… turbo what?! 😭
> > > 
> > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odylkts)
> > 
> > 
> > 
> > 32
> > 
> > 
> > 
> > [u/marcoc2](https://redlib.catsarch.com/user/marcoc2)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwxbge/?context=3#odwxbge "Apr 02 2026, 16:56:26 UTC")
> > 
> > Gemmopus
> > 
> > 
> > 
> > 27
> > 
> > 
> > 
> > [u/sibilischtic](https://redlib.catsarch.com/user/sibilischtic)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odyqita/?context=3#odyqita "Apr 02 2026, 22:04:03 UTC")
> > 
> > Eh im going to wait for
> > 
> > 
> > Gemma 4 26B Heretic Uncensored Ablated Claude Opus 4.6 Chain of Thot (NSFW) Quasimodal chuck Norris bingo night
> > 
> > 
> > > 11
> > > 
> > > 
> > > 
> > > [u/superdariom](https://redlib.catsarch.com/user/superdariom)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odz13x8/?context=3#odz13x8 "Apr 02 2026, 23:00:59 UTC")
> > > 
> > > Chain of Thot 🤣
> > > 
> > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odyqita)
> > 
> > [→ More replies (4)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwsxjg)
> 
> 
> 
> 57
> 
> 
> 
> [u/AXYZE8](https://redlib.catsarch.com/user/AXYZE8)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwqxx6/?context=3#odwqxx6 "Apr 02 2026, 16:27:02 UTC")
> 
> Yup, thats me
> 
> [![Image 8](https://redlib.catsarch.com/preview/pre/6zdub1w30tsg1.png?width=449&format=png&auto=webp&s=58be39cf2ce80e8a8dae21daf68e36488c6b091f)](https://redlib.catsarch.com/preview/pre/6zdub1w30tsg1.png?width=449&format=png&auto=webp&s=58be39cf2ce80e8a8dae21daf68e36488c6b091f)
> 
> 
> > 11
> > 
> > 
> > 
> > [u/BubrivKo](https://redlib.catsarch.com/user/BubrivKo)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxazlb/?context=3#odxazlb "Apr 02 2026, 17:57:38 UTC")
> > 
> > Lol, ok, It seems there are people who are using Q2 models :D
> > 
> > 
> > > [→ More replies (8)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxazlb)
> > 
> > 
> > 
> > 9
> > 
> > 
> > 
> > [u/DrNavigat](https://redlib.catsarch.com/user/DrNavigat)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwstb2/?context=3#odwstb2 "Apr 02 2026, 16:35:49 UTC")
> > 
> > LM Studio?
> > 
> > 
> > > 14
> > > 
> > > 
> > > 
> > > [u/thawizard](https://redlib.catsarch.com/user/thawizard)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx01t5/?context=3#odx01t5 "Apr 02 2026, 17:08:47 UTC")
> > > 
> > > I’m not the guy you’re asking but this is indeed LM Studio.
> > > 
> > > 
> > > > 5
> > > > 
> > > > 
> > > > 
> > > > [u/DrNavigat](https://redlib.catsarch.com/user/DrNavigat)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx1mrt/?context=3#odx1mrt "Apr 02 2026, 17:15:56 UTC")
> > > > 
> > > > It is crashing for me with 27a4b
> > > > 
> > > > 
> > > > > [→ More replies (4)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx1mrt)
> > 
> > [→ More replies (5)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwqxx6)
> 
> 
> 
> 25
> 
> 
> 
> u/[deleted][Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxbuv8/?context=3#odxbuv8 "Apr 02 2026, 18:01:35 UTC")
> 
> [removed] — [view removed comment](https://undelete.pullpush.io/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxbuv8)
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxbuv8)
> 
> [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwqmum)

279

[u/putrasherni](https://redlib.catsarch.com/user/putrasherni)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwmkwm/?context=3#odwmkwm "Apr 02 2026, 16:06:46 UTC")

incoming comparison content with qwen3.5

> 172
> 
> 
> 
> [u/grumd](https://redlib.catsarch.com/user/grumd)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwncm5/?context=3#odwncm5 "Apr 02 2026, 16:10:20 UTC")edited Apr 02 '26
> 
> I'm on it haha
> 
> 
> Edit: you may've seen my recent post here [https://www.reddit.com/r/LocalLLaMA/comments/1s9mkm1/benchmarked_18_models_that_i_can_run_on_my_rtx/](https://redlib.catsarch.com/r/LocalLLaMA/comments/1s9mkm1/benchmarked_18_models_that_i_can_run_on_my_rtx/)
> 
> 
> Just tested Gemma-4-26B-A4B at UD-Q6_K_XL a couple of times, results aren't bad!
> 
> [![Image 9](https://redlib.catsarch.com/preview/pre/4n6p8gvo6tsg1.png?width=1211&format=png&auto=webp&s=9c805f50d104839c12e0e1651720e32c187883f8)](https://redlib.catsarch.com/preview/pre/4n6p8gvo6tsg1.png?width=1211&format=png&auto=webp&s=9c805f50d104839c12e0e1651720e32c187883f8)
> Maybe I'll run the Aider benchmark suite overnight
> 
> 
> > 63
> > 
> > 
> > 
> > [u/Cubow](https://redlib.catsarch.com/user/Cubow)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwnrnf/?context=3#odwnrnf "Apr 02 2026, 16:12:15 UTC")
> > 
> > this is the last place where i would have expected to see one of my favourite mappers
> > 
> > 
> > > 33
> > > 
> > > 
> > > 
> > > [u/grumd](https://redlib.catsarch.com/user/grumd)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwpxdc/?context=3#odwpxdc "Apr 02 2026, 16:22:17 UTC")
> > > 
> > > Oh haha hi :D
> > > 
> > > 
> > > > 12
> > > > 
> > > > 
> > > > 
> > > > [u/shavitush](https://redlib.catsarch.com/user/shavitush)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwub7p/?context=3#odwub7p "Apr 02 2026, 16:42:47 UTC")
> > > > 
> > > > big fan
> > > 
> > > 
> > > 
> > > 9
> > > 
> > > 
> > > 
> > > [u/oxygen_addiction](https://redlib.catsarch.com/user/oxygen_addiction)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxawz4/?context=3#odxawz4 "Apr 02 2026, 17:57:18 UTC")
> > > 
> > > What is a mapper?
> > > 
> > > 
> > > > 10
> > > > 
> > > > 
> > > > 
> > > > [u/twack3r](https://redlib.catsarch.com/user/twack3r)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxk3x9/?context=3#odxk3x9 "Apr 02 2026, 18:39:50 UTC")edited Apr 02 '26
> > > > 
> > > > Apparently there‘s a mouse-based rhythm and gesture 2D game with levels/maps called osu; mappers create community content/levels.
> > > > 
> > > > 
> > > > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxk3x9)
> > > > 
> > > > 
> > > > 
> > > > 6
> > > > 
> > > > 
> > > > 
> > > > [u/Cubow](https://redlib.catsarch.com/user/Cubow)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxp0vo/?context=3#odxp0vo "Apr 02 2026, 19:02:40 UTC")
> > > > 
> > > > Well known level creator for the rhythm game osu!
> > > > 
> > > > 
> > > > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxp0vo)
> > > > 
> > > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxawz4)
> > > 
> > > 
> > > 
> > > 8
> > > 
> > > 
> > > 
> > > [u/Odd-Ordinary-5922](https://redlib.catsarch.com/user/Odd-Ordinary-5922)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwoo5j/?context=3#odwoo5j "Apr 02 2026, 16:16:26 UTC")
> > > 
> > > osu?
> > > 
> > > 
> > > > 11
> > > > 
> > > > 
> > > > 
> > > > [u/Cubow](https://redlib.catsarch.com/user/Cubow)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwpdd8/?context=3#odwpdd8 "Apr 02 2026, 16:19:42 UTC")
> > > > 
> > > > yes, had to doublecheck I’m on the right sub lmao
> > 
> > [→ More replies (4)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwncm5)
> 
> 
> 
> 65
> 
> 
> 
> [u/Singularity-42](https://redlib.catsarch.com/user/Singularity-42)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwv52h/?context=3#odwv52h "Apr 02 2026, 16:46:35 UTC")edited Apr 02 '26
> 
> Comparison of Gemma 4 vs. Qwen 3.5 benchmarks, consolidated from their respective Hugging Face model cards (source: HN comment):
> 
> 
> ```
> | Model        | MMLUP | GPQA  | LCB   | ELO  | TAU2  | MMMLU | HLE-n | HLE-t |
> |--------------| ----- | ----- | ----- | ---- | ----- | ----- | ----- | ----- |
> | G4 31B       | 85.2% | 84.3% | 80.0% | 2150 | 76.9% | 88.4% | 19.5% | 26.5% |
> | G4 26B A4B   | 82.6% | 82.3% | 77.1% | 1718 | 68.2% | 86.3% |  8.7% | 17.2% |
> | G4 E4B       | 69.4% | 58.6% | 52.0% |  940 | 42.2% | 76.6% |   -   |   -   |
> | G4 E2B       | 60.0% | 43.4% | 44.0% |  633 | 24.5% | 67.4% |   -   |   -   |
> | G3 27B no-T  | 67.6% | 42.4% | 29.1% |  110 | 16.2% | 70.7% |   -   |   -   |
> | GPT-5-mini   | 83.7% | 82.8% | 80.5% | 2160 | 69.8% | 86.2% | 19.4% | 35.8% |
> | GPT-OSS-120B | 80.8% | 80.1% | 82.7% | 2157 |  --   | 78.2% | 14.9% | 19.0% |
> | Q3-235B A22B | 84.4% | 81.1% | 75.1% | 2146 | 58.5% | 83.4% | 18.2% |  --   |
> | Q3.5-122 A10 | 86.7% | 86.6% | 78.9% | 2100 | 79.5% | 86.7% | 25.3% | 47.5% |
> | Q3.5 27B     | 86.1% | 85.5% | 80.7% | 1899 | 79.0% | 85.9% | 24.3% | 48.5% |
> | Q3.5 35B A3B | 85.3% | 84.2% | 74.6% | 2028 | 81.2% | 85.2% | 22.4% | 47.4% |
> 
> MMLUP: MMLU-Pro
> GPQA: GPQA Diamond
> LCB: LiveCodeBench v6
> ELO: Codeforces ELO
> TAU2: TAU2-Bench
> MMMLU: MMMLU
> HLE-n: Humanity's Last Exam (no tools / CoT)
> HLE-t: Humanity's Last Exam (with search / tool)
> no-T: no think
> ```
> 
> 
> > 17
> > 
> > 
> > 
> > [u/road-runn3r](https://redlib.catsarch.com/user/road-runn3r)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwwq33/?context=3#odwwq33 "Apr 02 2026, 16:53:46 UTC")
> > 
> > Copy pasted from hackernews, first comment
> > 
> > 
> > > 30
> > > 
> > > 
> > > 
> > > [u/Singularity-42](https://redlib.catsarch.com/user/Singularity-42)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwww2l/?context=3#odwww2l "Apr 02 2026, 16:54:31 UTC")
> > > 
> > > And? Someone asked, I've provided.
> > > 
> > > 
> > > > 23
> > > > 
> > > > 
> > > > 
> > > > [u/road-runn3r](https://redlib.catsarch.com/user/road-runn3r)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwxf7q/?context=3#odwxf7q "Apr 02 2026, 16:56:54 UTC")
> > > > 
> > > > > consolidated from their respective Hugging Face model cards
> > > > 
> > > > 
> > > > The wording makes it sound like you did this. Just add the source.
> > > > 
> > > > 
> > > > > 23
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/Singularity-42](https://redlib.catsarch.com/user/Singularity-42)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwxxwo/?context=3#odwxxwo "Apr 02 2026, 16:59:13 UTC")
> > > > > 
> > > > > I did
> > > > > 
> > > > > 
> > > > > > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwxxwo)
> > 
> > 
> > 
> > 4
> > 
> > 
> > 
> > u/[deleted][Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxcgdj/?context=3#odxcgdj "Apr 02 2026, 18:04:18 UTC")
> > 
> > [removed] — [view removed comment](https://undelete.pullpush.io/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxcgdj)
> > 
> > 
> > > [→ More replies (7)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxcgdj)
> > 
> > [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwv52h)
> 
> 
> 
> 66
> 
> 
> 
> [u/Hans-Wermhatt](https://redlib.catsarch.com/user/Hans-Wermhatt)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwocck/?context=3#odwocck "Apr 02 2026, 16:14:54 UTC")
> 
> Seems like Gemma 4 31B is slightly worse than Qwen 3.5 27B in most benchmarks outside of multi-lingual and MMMU pro.
> 
> 
> > 48
> > 
> > 
> > 
> > [u/vivaasvance](https://redlib.catsarch.com/user/vivaasvance)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwycom/?context=3#odwycom "Apr 02 2026, 17:01:03 UTC")
> > 
> > The multilingual advantage is underrated for
> > 
> > 
> > enterprise use cases.
> > 
> > 
> > Most benchmark comparisons focus on English
> > 
> > 
> > reasoning tasks. But for global deployments
> > 
> > 
> > where you need consistent performance across
> > 
> > 
> > languages — that gap matters more than a few
> > 
> > 
> > points on MMMU.
> > 
> > 
> > Gemma 4's multilingual strength could be the
> > 
> > 
> > deciding factor for the right use case.
> > 
> > 
> > > [→ More replies (4)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwycom)
> > 
> > 
> > 
> > 20
> > 
> > 
> > 
> > [u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwok8f/?context=3#odwok8f "Apr 02 2026, 16:15:55 UTC")
> > 
> > except elo
> > 
> > 
> > > 12
> > > 
> > > 
> > > 
> > > [u/Randomdotmath](https://redlib.catsarch.com/user/Randomdotmath)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwt7wo/?context=3#odwt7wo "Apr 02 2026, 16:37:42 UTC")
> > > 
> > > yeah, the elo seens far from benchmarks
> > > 
> > > 
> > > > 14
> > > > 
> > > > 
> > > > 
> > > > [u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwtc4h/?context=3#odwtc4h "Apr 02 2026, 16:38:14 UTC")
> > > > 
> > > > I don't really trust benchmarks, however I am not sure can I trust elo in 2026
> > 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwocck)

190

[u/itsdigimon](https://redlib.catsarch.com/user/itsdigimon)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwp495/?context=3#odwp495 "Apr 02 2026, 16:18:32 UTC")

Did Google just release a 26B A4B model? Sounds like christmas is early for GPU poor folks :')

> 63
> 
> 
> 
> [u/bikemandan](https://redlib.catsarch.com/user/bikemandan)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx0wea/?context=3#odx0wea "Apr 02 2026, 17:12:38 UTC")
> 
> Will it run on my Commodore 64?
> 
> 
> > 41
> > 
> > 
> > 
> > [u/FlamaVadim](https://redlib.catsarch.com/user/FlamaVadim)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxbt3k/?context=3#odxbt3k "Apr 02 2026, 18:01:21 UTC")
> > 
> > Naturlich!
> > 
> > 
> > > 14
> > > 
> > > 
> > > 
> > > [u/Ok_Zookeepergame8714](https://redlib.catsarch.com/user/Ok_Zookeepergame8714)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxdqvf/?context=3#odxdqvf "Apr 02 2026, 18:10:14 UTC")
> > > 
> > > I ran it on my abacus 🧮!!
> > > 
> > > 
> > > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxdqvf)
> > 
> > 
> > 
> > 16
> > 
> > 
> > 
> > [u/picosec](https://redlib.catsarch.com/user/picosec)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxkovq/?context=3#odxkovq "Apr 02 2026, 18:42:32 UTC")edited Apr 02 '26
> > 
> > If you have enough external storage attached it should be able to run. You might be able to achieve low single-digit tokens per year.
> > 
> > 
> > 
> > 5
> > 
> > 
> > 
> > [u/toothpastespiders](https://redlib.catsarch.com/user/toothpastespiders)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxxmhq/?context=3#odxxmhq "Apr 02 2026, 19:43:32 UTC")
> > 
> > Main reason I'm bummed about the lack of a 120b model. I was all prepped to start writing it to floppy for my Commodore 128.
> > 
> > 
> > 
> > 5
> > 
> > 
> > 
> > [u/roselan](https://redlib.catsarch.com/user/roselan)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxd149/?context=3#odxd149 "Apr 02 2026, 18:06:57 UTC")
> > 
> > Easily.
> > 
> > [→ More replies (4)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx0wea)
> 
> 
> 
> 27
> 
> 
> 
> [u/Final_Ad_7431](https://redlib.catsarch.com/user/Final_Ad_7431)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwpuei/?context=3#odwpuei "Apr 02 2026, 16:21:54 UTC")
> 
> yeah im only really able to run qwen3.5 35b on 8gb vram, im very excited to compare this new moe
> 
> 
> > 10
> > 
> > 
> > 
> > [u/mattrs1101](https://redlib.catsarch.com/user/mattrs1101)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwrm73/?context=3#odwrm73 "Apr 02 2026, 16:30:10 UTC")
> > 
> > What settings do you use?
> > 
> > 
> > > 19
> > > 
> > > 
> > > 
> > > [u/Final_Ad_7431](https://redlib.catsarch.com/user/Final_Ad_7431)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwthv1/?context=3#odwthv1 "Apr 02 2026, 16:38:59 UTC")
> > > 
> > > i basically rely on --fit and --fit-target to do all the lever pulling for me, i've always found it to give better results than manually doing stuff but ymmv of course, i just specify fit 1 and fit-target for the minimum headroom im comfortable giving (something like 256 keeps my system stable) then llamacpp will automatically do the offloading for you
> > > 
> > > 
> > > i pull about 25-27 token gen with this setup which im very happy with considering how gpu poor 8gb is these days
> > > 
> > > 
> > > > 5
> > > > 
> > > > 
> > > > 
> > > > [u/bolmer](https://redlib.catsarch.com/user/bolmer)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx4m2b/?context=3#odx4m2b "Apr 02 2026, 17:29:11 UTC")
> > > > 
> > > > What gpu do you have? I have an rx 6750 GRE 10GB and though I couldn't run Qwen 3.5 at that size.
> > > > 
> > > > 
> > > > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx4m2b)
> > > > 
> > > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwthv1)
> > 
> > 
> > 
> > 5
> > 
> > 
> > 
> > [u/Borkato](https://redlib.catsarch.com/user/Borkato)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwujqa/?context=3#odwujqa "Apr 02 2026, 16:43:52 UTC")
> > 
> > Qwen 3.5 35B is indeed god tier tho!
> > 
> > 
> > > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwujqa)
> > 
> > [→ More replies (6)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwpuei)
> 
> [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwp495)

166

[u/StatFlow](https://redlib.catsarch.com/user/StatFlow)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwrm99/?context=3#odwrm99 "Apr 02 2026, 16:30:10 UTC")

apache license is new - not a 'google gemma' license anymore!

> 24
> 
> 
> 
> [u/Borkato](https://redlib.catsarch.com/user/Borkato)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwuldj/?context=3#odwuldj "Apr 02 2026, 16:44:05 UTC")
> 
> Woah, what’s the difference? Is it like super open now? :D
> 
> 
> > 81
> > 
> > 
> > 
> > [u/StatFlow](https://redlib.catsarch.com/user/StatFlow)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwvjtw/?context=3#odwvjtw "Apr 02 2026, 16:48:28 UTC")edited Apr 02 '26
> > 
> > apache 2.0 is the gold standard and fully permissive. the google gemma license was "open" but google technically had the ability to restrict for any reason if they wanted to/it came to that.
> > 
> > 
> > > 38
> > > 
> > > 
> > > 
> > > [u/Borkato](https://redlib.catsarch.com/user/Borkato)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwx2jp/?context=3#odwx2jp "Apr 02 2026, 16:55:20 UTC")
> > > 
> > > Holy crap! So now it’s like officially “here, go nuts?”
> > > 
> > > 
> > > > 17
> > > > 
> > > > 
> > > > 
> > > > [u/Inevitable_Tea_5841](https://redlib.catsarch.com/user/Inevitable_Tea_5841)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx27cc/?context=3#odx27cc "Apr 02 2026, 17:18:29 UTC")
> > > > 
> > > > Yep
> > > 
> > > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwvjtw)
> 
> 
> 
> 5
> 
> 
> 
> [u/csm101_bob](https://redlib.catsarch.com/user/csm101_bob)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odz7gbb/?context=3#odz7gbb "Apr 02 2026, 23:35:54 UTC")
> 
> Big deal honestly. Apache 2.0 means you can do anything with these models commercially without Google's terms hanging over you. This is Google finally playing the open-weights game for real — not just "open with asterisks." Could shift a lot of enterprise adoption that was stuck on "but what's the license?" questions.

158

[u/Cubow](https://redlib.catsarch.com/user/Cubow)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwmpao/?context=3#odwmpao "Apr 02 2026, 16:07:21 UTC")

Gemma 4 E2B performing better than Gemma 3 27B on almost all benchmarks is insane, there is no way.

Also no 1B, my life is ruined

> 79
> 
> 
> 
> [u/putrasherni](https://redlib.catsarch.com/user/putrasherni)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwp9ym/?context=3#odwp9ym "Apr 02 2026, 16:19:16 UTC")
> 
> i think that these models will be baked into apple devices
> 
>  all of them are small parameter and fit within 80-90GB tops
> 
> 
> could be that gemma small models run inside of iphone
> 
> 
> crazy times ahead for apple + google partnerships , insane that it can be a thing
> 
> 
> > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwp9ym)
> 
> 
> 
> 29
> 
> 
> 
> [u/FullOf_Bad_Ideas](https://redlib.catsarch.com/user/FullOf_Bad_Ideas)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx3ny5/?context=3#odx3ny5 "Apr 02 2026, 17:25:00 UTC")
> 
> they're comparing a reasoning model to non-reasoning. There are benchmarks where reasoning models have an advantage.
> 
> 
> Gemma 3 27B gave you instant answer though.
> 
> 
> You could have argued that Qwen 3 4B Reasoning 2507 was better than GPT 4.5 or GPT 5 Chat this way. It's a half-truth.
> 
> 
> > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx3ny5)
> 
> 
> 
> 8
> 
> 
> 
> [u/Ink_code](https://redlib.catsarch.com/user/Ink_code)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx48bp/?context=3#odx48bp "Apr 02 2026, 17:27:29 UTC")
> 
> i love how small models keep getting better, maybe eventually we'd reach a point where you can actually have a small agent =>8B on phone or laptop we can tell to do stuff somewhat reliably without worrying about it breaking everything.
> 
> 
> 
> 3
> 
> 
> 
> [u/WhyLifeIs4](https://redlib.catsarch.com/user/WhyLifeIs4)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwoj61/?context=3#odwoj61 "Apr 02 2026, 16:15:47 UTC")
> 
> Real
> 
> [→ More replies (9)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwmpao)

96

[u/ReadyAndSalted](https://redlib.catsarch.com/user/ReadyAndSalted)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwqf80/?context=3#odwqf80 "Apr 02 2026, 16:24:36 UTC")

E4b seems like a super good option for voice assistants. Instead of having: Audio -> speech to text -> LLM -> text to speech

You could have: Audio -> LLM -> text to speech (including agentic stuff with function calling)

> 52
> 
> 
> 
> [u/_Ruffy_](https://redlib.catsarch.com/user/_Ruffy_)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwz3eh/?context=3#odwz3eh "Apr 02 2026, 17:04:26 UTC")
> 
> Guess what will be deployed to iPhones very soon ;-)
> 
> 
> > 5
> > 
> > 
> > 
> > [u/bakawolf123](https://redlib.catsarch.com/user/bakawolf123)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxgu6v/?context=3#odxgu6v "Apr 02 2026, 18:24:27 UTC")
> > 
> > foundation models they said... I guess the recent news from that deal saying apple will open up to other providers is cause they paid billions, but in the end it's just an open model =)
> > 
> > 
> > edit: oh and blaizzy is ready with [https://github.com/Blaizzy/mlx-audio-swift](https://github.com/Blaizzy/mlx-audio-swift)
> > 
> >  gonna port into my test app soon then, probs in a week cause easter
> 
> [→ More replies (4)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwqf80)

89

[u/DigiDecode_](https://redlib.catsarch.com/user/DigiDecode_)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwr39x/?context=3#odwr39x "Apr 02 2026, 16:27:43 UTC")

the 31b ranks above GLM-5 on LMSys, my jaw is on the floor

[![Image 10](https://redlib.catsarch.com/preview/pre/fcounyr50tsg1.png?width=2281&format=png&auto=webp&s=817949d5c6fb51e4f4e1bdb72303e82cfaed1bc9)](https://redlib.catsarch.com/preview/pre/fcounyr50tsg1.png?width=2281&format=png&auto=webp&s=817949d5c6fb51e4f4e1bdb72303e82cfaed1bc9)

> 36
> 
> 
> 
> [u/Borkato](https://redlib.catsarch.com/user/Borkato)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwudtl/?context=3#odwudtl "Apr 02 2026, 16:43:07 UTC")
> 
> I’m trying so hard not to get hyped and it’s NOT WORKING
> 
> 
> > 17
> > 
> > 
> > 
> > [u/Zeeplankton](https://redlib.catsarch.com/user/Zeeplankton)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odww0et/?context=3#odww0et "Apr 02 2026, 16:50:34 UTC")
> > 
> > remember, this is google lol
> > 
> > 
> > > 5
> > > 
> > > 
> > > 
> > > [u/FlamaVadim](https://redlib.catsarch.com/user/FlamaVadim)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxdf8v/?context=3#odxdf8v "Apr 02 2026, 18:08:46 UTC")
> > > 
> > > at least it cannot be nerfed 😝!
> > > 
> > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odww0et)
> 
> 
> 
> 19
> 
> 
> 
> [u/MandateOfHeavens](https://redlib.catsarch.com/user/MandateOfHeavens)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwybue/?context=3#odwybue "Apr 02 2026, 17:00:56 UTC")
> 
> Tbf GLM-5's quality depends heavily during the time of day. During peak hours especially in China they use a heavily quantized model. And its thinking block is unusually sparse and the model overall has poor context comprehension. 5.1 is the real deal and what 5 should have released as.
> 
> 
> > 7
> > 
> > 
> > 
> > [u/Mashiro-no](https://redlib.catsarch.com/user/Mashiro-no)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odzakbn/?context=3#odzakbn "Apr 02 2026, 23:53:26 UTC")
> > 
> > Do you have a source for this? or are you simply using anecdotes.
> 
> 
> 
> 4
> 
> 
> 
> [u/Usual-Carrot6352](https://redlib.catsarch.com/user/Usual-Carrot6352)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx0pxo/?context=3#odx0pxo "Apr 02 2026, 17:11:49 UTC")
> 
> in math gemma-4-26b-a4b is No.10 🤯
> 
> [![Image 11](https://redlib.catsarch.com/preview/pre/1w2wk2w18tsg1.png?width=864&format=png&auto=webp&s=929a8d11a306c2fe6cb32921ab9cf90ee2583d26)](https://redlib.catsarch.com/preview/pre/1w2wk2w18tsg1.png?width=864&format=png&auto=webp&s=929a8d11a306c2fe6cb32921ab9cf90ee2583d26)
> 
> 
> > [→ More replies (12)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx0pxo)
> 
> [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwr39x)

67

[u/Skyline34rGt](https://redlib.catsarch.com/user/Skyline34rGt)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwql0m/?context=3#odwql0m "Apr 02 2026, 16:25:22 UTC")

Wow [https://x.com/arena/status/2039739427715735645](https://x.com/arena/status/2039739427715735645)

[![Image 12](https://redlib.catsarch.com/preview/pre/t2n36xfxzssg1.jpeg?width=900&format=pjpg&auto=webp&s=89daab20075f8b3b8a85dc37311a58e9850f46ba)](https://redlib.catsarch.com/preview/pre/t2n36xfxzssg1.jpeg?width=900&format=pjpg&auto=webp&s=89daab20075f8b3b8a85dc37311a58e9850f46ba)

> 36
> 
> 
> 
> [u/redblood252](https://redlib.catsarch.com/user/redblood252)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwvhao/?context=3#odwvhao "Apr 02 2026, 16:48:09 UTC")
> 
> Sounds way too good to be true.
> 
> 
> > 14
> > 
> > 
> > 
> > [u/SpiritualWindow3855](https://redlib.catsarch.com/user/SpiritualWindow3855)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxnwoj/?context=3#odxnwoj "Apr 02 2026, 18:57:30 UTC")
> > 
> > Why? We know Chinese models haven't as polished on reasoning as models from the big 3 western labs.
> > 
> > 
> > We also know Gemma 3 has unusually high world knowledge for its size.
> > 
> > 
> > So a slightly scaled up version of + reasoning would be expected to be one of the best open reasoning models out there. Qwen still has less reliable reasoning than GPT-OSS, it's the base model performance that makes up for it.
> > 
> > 
> > > [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxnwoj)
> 
> [→ More replies (10)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwql0m)

53

[u/Odd-Ordinary-5922](https://redlib.catsarch.com/user/Odd-Ordinary-5922)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwlo33/?context=3#odwlo33 "Apr 02 2026, 16:02:28 UTC")

are they releasing qat versions?

> 20
> 
> 
> 
> [u/itsdigimon](https://redlib.catsarch.com/user/itsdigimon)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwue3z/?context=3#odwue3z "Apr 02 2026, 16:43:09 UTC")
> 
> I hope so :')
> 
> 
> 
> 13
> 
> 
> 
> [u/AnonLlamaThrowaway](https://redlib.catsarch.com/user/AnonLlamaThrowaway)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxk24x/?context=3#odxk24x "Apr 02 2026, 18:39:36 UTC")
> 
> Gemma 3 QATs only showed up weeks after the initial release, so... probably
> 
> [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwlo33)

52

[u/Adventurous-Gold6413](https://redlib.catsarch.com/user/Adventurous-Gold6413)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwm1a1/?context=3#odwm1a1 "Apr 02 2026, 16:04:13 UTC")

The 26ba4b better be gudd

> 35
> 
> 
> 
> [u/n8mo](https://redlib.catsarch.com/user/n8mo)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwn97s/?context=3#odwn97s "Apr 02 2026, 16:09:54 UTC")
> 
> Perked up as soon as I saw there’s a MoE model I’ll be able to run on my machine
> 
> [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwm1a1)

54

[u/swagonflyyyy](https://redlib.catsarch.com/user/swagonflyyyy)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxbgpq/?context=3#odxbgpq "Apr 02 2026, 17:59:47 UTC")

"Generate a humorously complicated python code that simply prints out hello world. The code should be as convoluted and hard to read as possible while remaining functional"

Oh, so you want me to turn a simple task into a digital fever dream? Fine, but don't come crying to me when your brain short-circuits trying to parse this masterpiece.

``` import sys, functools, operator

def axiom_complexity_engine(payload): # We don't just 'print', we orchestrate a symphony of absurdity return "".join(map(chr, functools.reduce(operator.add, [[x] for x in payload])))

def initiate_sequence(): try: # Constructing the payload via unnecessary mathematical gymnastics and bitwise madness target_sequence = [ (0x48 ^ 0x00), (0x65 ^ 0x00), (0x6C ^ 0x00), (0x6C ^ 0x00), (0x6F ^ 0x00), (0x20 ^ 0x00), (0x57 ^ 0x00), (0x6F ^ 0x00), (0x72 ^ 0x00), (0x6C ^ 0x00), (0x64 ^ 0x00), (0x21 ^ 0x00) ]

```
# A lambda-based recursive loop that does absolutely nothing meaningful but looks intimidating
    logic_gate = lambda n, acc: acc if n == 0 else logic_gate(n-1, acc + [target_sequence[n-1]])

    # Injecting the result into the standard output stream via a convoluted functional pipe
    sys.stdout.write(axiom_complexity_engine(logic_gate(len(target_sequence), [])) + '\n')

except Exception as e:
    raise RuntimeError(f"Even my brilliance is too much for this system: {e}")
```

if **name** == "**main**": # Execute the overkill (lambda: [initiate_sequence()])() ```

There you go—one "Hello World" wrapped in enough unnecessary layers to make a senior developer weep. You're welcome.

> 10
> 
> 
> 
> [u/amejin](https://redlib.catsarch.com/user/amejin)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxdbvy/?context=3#odxdbvy "Apr 02 2026, 18:08:20 UTC")
> 
> I'm not sure what it says about me that I thought this would be the way to do it and this is what it did... But it added error handling so there's that...

51

[u/shockwaverc13](https://redlib.catsarch.com/user/shockwaverc13)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwrj28/?context=3#odwrj28 "Apr 02 2026, 16:29:45 UTC")

[![Image 13](https://redlib.catsarch.com/preview/pre/1tgav6ug0tsg1.png?width=816&format=png&auto=webp&s=46d9643b860014d2aa88bcd9d7e7c4002b759aad)](https://redlib.catsarch.com/preview/pre/1tgav6ug0tsg1.png?width=816&format=png&auto=webp&s=46d9643b860014d2aa88bcd9d7e7c4002b759aad)
so sneaky, that was unexpected

> 12
> 
> 
> 
> [u/Firepal64](https://redlib.catsarch.com/user/Firepal64)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxlgvd/?context=3#odxlgvd "Apr 02 2026, 18:46:08 UTC")
> 
> OH MY GOD that's so clever, i wouldn't have been able to clock it in the sea of PRs
> 
> [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwrj28)

39

[u/psychohistorian8](https://redlib.catsarch.com/user/psychohistorian8)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwx4w4/?context=3#odwx4w4 "Apr 02 2026, 16:55:37 UTC")

can't wait to see how it does in real world agentic coding tasks, especially compared to Qwen 3.5 27B/35BA3B

benchmarks mean nothing to me anymore

I'm downloading both 31B and 26BA4B and will play around with them after work

> 13
> 
> 
> 
> [u/Dr4x_](https://redlib.catsarch.com/user/Dr4x_)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx9ot6/?context=3#odx9ot6 "Apr 02 2026, 17:51:47 UTC")
> 
> Please share your results, I'm curious to see how useful they are for real life use cases
> 
> 
> > [→ More replies (4)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx9ot6)
> 
> [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwx4w4)

39

[u/fake_agent_smith](https://redlib.catsarch.com/user/fake_agent_smith)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwnzg8/?context=3#odwnzg8 "Apr 02 2026, 16:13:14 UTC")

This is amazing, 31B model what only sota managed to achieve not so long ago. HLE at 19.5%. Just wow.

> 11
> 
> 
> 
> [u/9r4n4y](https://redlib.catsarch.com/user/9r4n4y)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwvg50/?context=3#odwvg50 "Apr 02 2026, 16:48:00 UTC")edited Apr 03 '26
> 
> Q3.5 27b has 22% score?? So it means under 35b parameter. It is not the sota

37

[u/Weak-Shelter-1698](https://redlib.catsarch.com/user/Weak-Shelter-1698)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwwthq/?context=3#odwwthq "Apr 02 2026, 16:54:12 UTC")

Let's goooo, best birthday gift ever!!!!

> 29
> 
> 
> 
> [u/maartenyh](https://redlib.catsarch.com/user/maartenyh)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxd71y/?context=3#odxd71y "Apr 02 2026, 18:07:43 UTC")
> 
> Happy Birthday!!! 🎂
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxd71y)
> 
> [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwwthq)

35

[u/dampflokfreund](https://redlib.catsarch.com/user/dampflokfreund)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwo1gj/?context=3#odwo1gj "Apr 02 2026, 16:13:29 UTC")edited Apr 02 '26

Oh, great news! Thinking, system role support, more context basically what everyone asked for, and a 35B competitor MoE too.

But aww man audio is E2B and E4B only, that's a bit of a bummer. I thought we were about to have native and capable voice assistants now. But these are too small. Basically larger native multimodal models that can input and output audio, not only spoken text, natively. Also, QAT?

But not going to dwell on that for too long. This great, thank you Gemma team!

> 13
> 
> 
> 
> [u/MoffKalast](https://redlib.catsarch.com/user/MoffKalast)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwvgd4/?context=3#odwvgd4 "Apr 02 2026, 16:48:02 UTC")
> 
> A system prompt for Gemma? Hell really has frozen over this time.
> 
> 
> > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwvgd4)
> 
> 
> 
> 12
> 
> 
> 
> [u/Borkato](https://redlib.catsarch.com/user/Borkato)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwu9w6/?context=3#odwu9w6 "Apr 02 2026, 16:42:36 UTC")
> 
> The benchmarks suggest E2B and E4B are great! 👀
> 
> 
> > [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwu9w6)
> 
> 
> 
> 5
> 
> 
> 
> u/[deleted][Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwzsjz/?context=3#odwzsjz "Apr 02 2026, 17:07:37 UTC")
> 
> [removed] — [view removed comment](https://undelete.pullpush.io/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwzsjz)
> 
> 
> > 4
> > 
> > 
> > 
> > [u/Hefty_Acanthaceae348](https://redlib.catsarch.com/user/Hefty_Acanthaceae348)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxn9ss/?context=3#odxn9ss "Apr 02 2026, 18:54:32 UTC")
> > 
> > If the small model is only used for voice, there is no need for tool calling, just use a deterministic pipeline
> > 
> > [→ More replies (4)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwzsjz)
> 
> [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwo1gj)

35

[u/ML-Future](https://redlib.catsarch.com/user/ML-Future)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwuve5/?context=3#odwuve5 "Apr 02 2026, 16:45:21 UTC")

It seems that Gemma4 2B has capabilities that are similar to or better than Gemma3 27B

[![Image 14](https://redlib.catsarch.com/preview/pre/5d1l0nac3tsg1.jpeg?width=1919&format=pjpg&auto=webp&s=36db8d72cc25b20b1858138a3aba113b0a409fcd)](https://redlib.catsarch.com/preview/pre/5d1l0nac3tsg1.jpeg?width=1919&format=pjpg&auto=webp&s=36db8d72cc25b20b1858138a3aba113b0a409fcd)

33

[u/popiazaza](https://redlib.catsarch.com/user/popiazaza)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwwmfp/?context=3#odwwmfp "Apr 02 2026, 16:53:19 UTC")

This is much more interesting than their Gemini models.

Both Gemma 4 31b and 26b-a4b have higher elo than their proprietary Gemini 3.1 Flash Lite model.

This would be a game changer for a local model and open source cloud inference.

> [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwwmfp)

24

[u/PiratesOfTheArctic](https://redlib.catsarch.com/user/PiratesOfTheArctic)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxzeze/?context=3#odxzeze "Apr 02 2026, 19:52:01 UTC")

I have a basic laptop I7 with 32gb ram running qwent3.5 4b q5 k m with llama.cpp. Swapped it over to gemma-4-E4B-it-Q4_K_M.gguf (with some flags) and not only is it faster, it gives significantly better answers

I'm very much a newbie, but even saw the difference when using it for finance analysis

> 8
> 
> 
> 
> [u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/ody3xyh/?context=3#ody3xyh "Apr 02 2026, 20:13:15 UTC")
> 
> That's the power of LocalLLaMA
> 
> 
> > 8
> > 
> > 
> > 
> > [u/PiratesOfTheArctic](https://redlib.catsarch.com/user/PiratesOfTheArctic)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/ody5b6i/?context=3#ody5b6i "Apr 02 2026, 20:19:38 UTC")
> > 
> > Back in the 90s I used to program assembly, and whilst this old decrepid mind isn't sharp to do that anymore, I know what end results should be, and how they should be processed, so having great fun giving it a good pokey pokey, laptop is having a meltdown, all good fun!
> > 
> > 
> > > 8
> > > 
> > > 
> > > 
> > > [u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/ody612v/?context=3#ody612v "Apr 02 2026, 20:23:01 UTC")
> > > 
> > > I was active in the demoscene in the ’90s, and I won some competitions with assembly :)
> > > 
> > > 
> > > > [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/ody612v)

23

[u/Everlier](https://redlib.catsarch.com/user/Everlier)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwnrff/?context=3#odwnrff "Apr 02 2026, 16:12:13 UTC")

it's been a quiet Thursday evening... I wanted to play some Crimson Desert...

But nownI have something much much better to do :)

18

[u/AdamFields](https://redlib.catsarch.com/user/AdamFields)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwxhya/?context=3#odwxhya "Apr 02 2026, 16:57:15 UTC")

Is the context as vram expensive as gemma 3? That to me is what would make or break this model. Currently I can only fit gemma 3 27b q4_k_m with 20k context on a 5090 while I can fit qwen 3.5 27b q4_k_m with 190k context on that same card.

> [→ More replies (8)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwxhya)

19

[u/Odd-Ordinary-5922](https://redlib.catsarch.com/user/Odd-Ordinary-5922)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwpbz1/?context=3#odwpbz1 "Apr 02 2026, 16:19:31 UTC")

the 26b a4b beating qwen3.5 27b is crazy

> 25
> 
> 
> 
> [u/Wooden-Deer-1276](https://redlib.catsarch.com/user/Wooden-Deer-1276)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwv5pe/?context=3#odwv5pe "Apr 02 2026, 16:46:40 UTC")
> 
> it doesn't (except for LMArena elo)
> 
> 
> > 5
> > 
> > 
> > 
> > [u/some_user_2021](https://redlib.catsarch.com/user/some_user_2021)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx5l5c/?context=3#odx5l5c "Apr 02 2026, 17:33:32 UTC")
> > 
> > Did you check?
> > 
> > 
> > > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx5l5c)
> 
> 
> 
> 9
> 
> 
> 
> [u/EbbNorth7735](https://redlib.catsarch.com/user/EbbNorth7735)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwycjw/?context=3#odwycjw "Apr 02 2026, 17:01:02 UTC")
> 
> In ELO. Most benchmarks show Q3.5 27B and 122B beating G4 31B from what I can tell.
> 
> 
> 
> 7
> 
> 
> 
> [u/Borkato](https://redlib.catsarch.com/user/Borkato)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwu5lm/?context=3#odwu5lm "Apr 02 2026, 16:42:04 UTC")
> 
> Holy fuck that’s the model in the most excited about. Qwen 35B is SO good that I desperately want something like 27B which is even better but way slower, but faster. So holy crap I’m so excited
> 
> 
> > [→ More replies (5)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwu5lm)

16

[u/Final_Ad_7431](https://redlib.catsarch.com/user/Final_Ad_7431)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwp176/?context=3#odwp176 "Apr 02 2026, 16:18:08 UTC")

dense model beating out qwen3.5 397b is insane, even the moe not far behind, what a nice gift from google

> [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwp176)

17

[u/Mashic](https://redlib.catsarch.com/user/Mashic)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwxt24/?context=3#odwxt24 "Apr 02 2026, 16:58:37 UTC")

I tested the gemma4:26B-A4B-Q4_K_M on translation from English to Arabic, it's better than the translategemma:27b-Q6.

> [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwxt24)

16

[u/No-Leave-4512](https://redlib.catsarch.com/user/No-Leave-4512)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwml1l/?context=3#odwml1l "Apr 02 2026, 16:06:47 UTC")

Looks like Gemma4 31B is almost as good as Qwen3.5 27B

> 9
> 
> 
> 
> [u/ShengrenR](https://redlib.catsarch.com/user/ShengrenR)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwo4yp/?context=3#odwo4yp "Apr 02 2026, 16:13:57 UTC")
> 
> plot in [https://arstechnica.com/ai/2026/04/google-announces-gemma-4-open-ai-models-switches-to-apache-2-0-license/](https://arstechnica.com/ai/2026/04/google-announces-gemma-4-open-ai-models-switches-to-apache-2-0-license/) implies it is better at least in .. some dimension lol
> 
> 
> > 22
> > 
> > 
> > 
> > [u/Murinshin](https://redlib.catsarch.com/user/Murinshin)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwqml8/?context=3#odwqml8 "Apr 02 2026, 16:25:34 UTC")
> > 
> > That’s 397B up there, not 35B or 27B
> > 
> > 
> > > 11
> > > 
> > > 
> > > 
> > > [u/Randomdotmath](https://redlib.catsarch.com/user/Randomdotmath)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwspck/?context=3#odwspck "Apr 02 2026, 16:35:18 UTC")
> > > 
> > > not the elo ranks, the benchmarks, idk how can they get such high elo with losing most of comparison
> > > 
> > > 
> > > > 12
> > > > 
> > > > 
> > > > 
> > > > [u/Swimming_Gain_4989](https://redlib.catsarch.com/user/Swimming_Gain_4989)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwtxdk/?context=3#odwtxdk "Apr 02 2026, 16:41:00 UTC")
> > > > 
> > > > Gemma models typically output a nicer aesthetic (better prose, formatting, etc.). If I had to guess they're probably hevaily weighing head to head scoring mechanisms like LMArena.
> > > > 
> > > > 
> > > > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwtxdk)
> > > > 
> > > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwspck)
> > > 
> > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwqml8)
> 
> [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwml1l)

15

[u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx7xc1/?context=3#odx7xc1 "Apr 02 2026, 17:43:55 UTC")

We are now in April

[![Image 15](https://redlib.catsarch.com/preview/pre/mv6nw3srdtsg1.png?width=1617&format=png&auto=webp&s=fc6c106b9fff54ea856065c75920f1f1801ee532)](https://redlib.catsarch.com/preview/pre/mv6nw3srdtsg1.png?width=1617&format=png&auto=webp&s=fc6c106b9fff54ea856065c75920f1f1801ee532)

> 19
> 
> 
> 
> [u/sine120](https://redlib.catsarch.com/user/sine120)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxd0gk/?context=3#odxd0gk "Apr 02 2026, 18:06:52 UTC")
> 
> The new Intel GPU isn't horrible for 32GB.
> 
> 
> 
> 7
> 
> 
> 
> [u/sammoga123](https://redlib.catsarch.com/user/sammoga123)ollama[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxgoly/?context=3#odxgoly "Apr 02 2026, 18:23:43 UTC")
> 
> I think you'd better forget about Llama; I heard they're definitely not going to release any more open-source models.
> 
> 
> > [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxgoly)

14

[u/meh_Technology_9801](https://redlib.catsarch.com/user/meh_Technology_9801)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwqx0y/?context=3#odwqx0y "Apr 02 2026, 16:26:55 UTC")

Cool. I was wondering if Gemma would be cancelled. It had been removed from AI studio after people got it to say offensive things about a senator.

> [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwqx0y)

13

[u/RickyRickC137](https://redlib.catsarch.com/user/RickyRickC137)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxqs8x/?context=3#odxqs8x "Apr 02 2026, 19:10:56 UTC")

Just basic system prompt is good enough to jailbreak Gemma 4!!!

> 21
> 
> 
> 
> [u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxr671/?context=3#odxr671 "Apr 02 2026, 19:12:45 UTC")
> 
> Maybe share some cool example

13

[u/MundanePercentage674](https://redlib.catsarch.com/user/MundanePercentage674)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwnf9t/?context=3#odwnf9t "Apr 02 2026, 16:10:40 UTC")

[https://www.youtube.com/watch?v=jZVBoFOJK-Q](https://www.youtube.com/watch?v=jZVBoFOJK-Q)

> 6
> 
> 
> 
> [u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwnt1i/?context=3#odwnt1i "Apr 02 2026, 16:12:25 UTC")
> 
> thanks!!! added

13

[u/LosEagle](https://redlib.catsarch.com/user/LosEagle)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxj0h9/?context=3#odxj0h9 "Apr 02 2026, 18:34:41 UTC")

YES! MedGemma next, please, I beg you

> 6
> 
> 
> 
> [u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxjf6o/?context=3#odxjf6o "Apr 02 2026, 18:36:38 UTC")
> 
> what's your usecase?
> 
> 
> > 8
> > 
> > 
> > 
> > [u/s1lenceisgold](https://redlib.catsarch.com/user/s1lenceisgold)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odygr3o/?context=3#odygr3o "Apr 02 2026, 21:14:48 UTC")
> > 
> > Medical document OCR, need embeddings as well
> > 
> > 
> > 
> > 5
> > 
> > 
> > 
> > [u/PaceZealousideal6091](https://redlib.catsarch.com/user/PaceZealousideal6091)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odz2zn2/?context=3#odz2zn2 "Apr 02 2026, 23:11:14 UTC")
> > 
> > Medical imaging diagnostics!!! Its great to fine tuned for specific diseases.
> > 
> > 
> > > [→ More replies (8)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odz2zn2)

11

[u/hyrulia](https://redlib.catsarch.com/user/hyrulia)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwvy97/?context=3#odwvy97 "Apr 02 2026, 16:50:18 UTC")

For 16Gb VRAM, 26B-A4B-UD-IQ4_NL and 31B-UD-IQ3_XXS fit perfectly. Probably the 31B would be smarter even at Q3

12

[u/BubrivKo](https://redlib.catsarch.com/user/BubrivKo)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxc09v/?context=3#odxc09v "Apr 02 2026, 18:02:16 UTC")

Just give me an uncensored version, lol :D

> 12
> 
> 
> 
> [u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxch62/?context=3#odxch62 "Apr 02 2026, 18:04:24 UTC")
> 
> [u/-p-e-w-](https://redlib.catsarch.com/u/-p-e-w-) already has one
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxch62)
> 
> [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxc09v)

10

[u/No-Wallaby-9210](https://redlib.catsarch.com/user/No-Wallaby-9210)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxd64n/?context=3#odxd64n "Apr 02 2026, 18:07:36 UTC")

Funny how e4b won't blink and tell a "Yo mama is so fat" joke in english, but will absolutely not do it in german. How come?

> 12
> 
> 
> 
> [u/PooMonger20](https://redlib.catsarch.com/user/PooMonger20)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odyhzc1/?context=3#odyhzc1 "Apr 02 2026, 21:20:55 UTC")
> 
> It implies German people are more polite, and bad at jokes.
> 
> 
> Checks out, lol.
> 
> 
> 
> 10
> 
> 
> 
> [u/asssuber](https://redlib.catsarch.com/user/asssuber)[Apr 03 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/oe0baz2/?context=3#oe0baz2 "Apr 03 2026, 03:32:47 UTC")
> 
> [r/GermanHumour](https://redlib.catsarch.com/r/GermanHumour)

9

[u/Cool-Chemical-5629](https://redlib.catsarch.com/user/Cool-Chemical-5629)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxgzck/?context=3#odxgzck "Apr 02 2026, 18:25:07 UTC")

| Benchmark | Gemma 4 E4B | Gemma 3 27B |
| --- | --- | --- |
| MMLU Pro | 69.4% | 67.6% |
| AIME 2026 no tools | 42.5% | 20.8% |
| LiveCodeBench v6 | 52.0% | 29.1% |
| Codeforces ELO | 940 | 110 |
| GPQA Diamond | 58.6% | 42.4% |
| Tau2 (avg) | 42.2% | 16.2% |
| BigBench Extra Hard | 33.1% | 19.3% |
| MMMLU | 76.6% | 70.7% |
| Vision MMMU Pro | 52.6% | 49.7% |
| OmniDocBench (lower=better) | 0.181 | 0.365 |
| MATH‑Vision | 59.5% | 46.0% |
| MRCR v2 8‑needle 128k | 25.4% | 13.5% |

Gemma 4 E4B beats Gemma 3 27B...

> [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxgzck)

9

u/[deleted][Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwqwvm/?context=3#odwqwvm "Apr 02 2026, 16:26:54 UTC")

[deleted]

> 7
> 
> 
> 
> [u/MoffKalast](https://redlib.catsarch.com/user/MoffKalast)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwvy2p/?context=3#odwvy2p "Apr 02 2026, 16:50:16 UTC")
> 
> What, you don't you guys have ~~phones~~ a TPUv7 with 192GB of HBM?

10

[u/Firstbober](https://redlib.catsarch.com/user/Firstbober)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwtegw/?context=3#odwtegw "Apr 02 2026, 16:38:32 UTC")

Where Gemma 4 270M... Awesome release, I hope Google will release such a small model again. It's incredibly capable for it's size, and I don't think there is any other alternative similarly sized.

> [→ More replies (5)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwtegw)

9

u/[deleted][Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwtp6q/?context=3#odwtp6q "Apr 02 2026, 16:39:56 UTC")

[deleted]

> 19
> 
> 
> 
> [u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwtu3s/?context=3#odwtu3s "Apr 02 2026, 16:40:34 UTC")
> 
> instruct
> 
> 
> 
> 9
> 
> 
> 
> [u/Ink_code](https://redlib.catsarch.com/user/Ink_code)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx7wvr/?context=3#odx7wvr "Apr 02 2026, 17:43:52 UTC")
> 
> instruction tuned, it means the model went through a supervised fine tuning phase where it's trained to follow instructions, this lets it act as a useful assistant.
> 
> 
> you can also find base models on huggingface which haven't went through it and so more so try to complete the text sent to them instead of treating them as instructions..
> 
> 
> > [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx7wvr)

9

[u/Baphaddon](https://redlib.catsarch.com/user/Baphaddon)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwvuql/?context=3#odwvuql "Apr 02 2026, 16:49:51 UTC")

Chef Demis has concocted another dish

8

[u/guiopen](https://redlib.catsarch.com/user/guiopen)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx0sfb/?context=3#odx0sfb "Apr 02 2026, 17:12:08 UTC")

Super cool that they also released the base models

9

[u/Choice_Sympathy9652](https://redlib.catsarch.com/user/Choice_Sympathy9652)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx4rk9/?context=3#odx4rk9 "Apr 02 2026, 17:29:51 UTC")

Dear huihui, we are waiting for abliterated version! :D Forward thanks to You!

> [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx4rk9)

8

[u/BubrivKo](https://redlib.catsarch.com/user/BubrivKo)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxfzk8/?context=3#odxfzk8 "Apr 02 2026, 18:20:29 UTC")

Ok, Gemma 4 26B A4B didn't pass my "benchmark" :D

 Gemma 31B passed it!

[![Image 16](https://redlib.catsarch.com/preview/pre/19kwlhm9ktsg1.png?width=1014&format=png&auto=webp&s=d50ee4090dd2e1cc596957093dd16cd6fe6c0fd8)](https://redlib.catsarch.com/preview/pre/19kwlhm9ktsg1.png?width=1014&format=png&auto=webp&s=d50ee4090dd2e1cc596957093dd16cd6fe6c0fd8)

> [→ More replies (6)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxfzk8)

8

[u/Corosus](https://redlib.catsarch.com/user/Corosus)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxpbtp/?context=3#odxpbtp "Apr 02 2026, 19:04:05 UTC")

Built latest llama.cpp

gemma-4-31B-it-UD-Q4_K_XL passed a personal niche code probably biased test I use on new models, it nailed it first try that all other models have like a 95% fail rate on cause they miss one thing. We might have something special here

5070ti 5060ti 32gb combined, llama.cpp cuda, 25tps to start trickling down to 18tps after 32k context used.

E:\dev\git_ai\llama.cpp\build\bin\Release\llama-server -m E:\ai\llamacpp_models\unsloth\gemma-4-31B-it-UD-Q4_K_XL.gguf --host 0.0.0.0 --port 8080 --temp 1.0 --top-p 0.95 --top-k 64 -ngl 99 -ts 24,20 -sm layer -np 1 --fit on --fit-target 2048 --flash-attn on -ctk q8_0 -ctv q8_0 -c 96000

Thinks a lot, oh boy does it think a lot, I liked what I was seeing though.

> [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxpbtp)

8

[u/AvidCyclist250](https://redlib.catsarch.com/user/AvidCyclist250)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/ody3fu7/?context=3#ody3fu7 "Apr 02 2026, 20:10:55 UTC")edited Apr 03 '26

Oh, the hype isn't bullshit! Comparing the a4b MoE model favourably to the equivalent qwen 3.5 a3b in my own tests right now. It's getting some very tricky shit right! STEM and philosophy, that is. And it's fast despite partial offload. Sweet af.

edit: tool calling is not that impressive for me, in particular web mcp. hopefully something that be fixed on my end. very nice model otherwise.

7

[u/hp1337](https://redlib.catsarch.com/user/hp1337)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odws5ni/?context=3#odws5ni "Apr 02 2026, 16:32:42 UTC")

WOW! Look at MRCR V2. This is game changing! Long context rot has been the biggest problem with medium sized open source models. Going to test it now!

> [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odws5ni)

7

[u/florinandrei](https://redlib.catsarch.com/user/florinandrei)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx61fw/?context=3#odx61fw "Apr 02 2026, 17:35:32 UTC")edited Apr 02 '26

Nice. Gemma3 27B has been my favorite general-purpose conversational model for some time.

The 26B is a MoE, but the 31B is dense? Seems backwards?

6

[u/m98789](https://redlib.catsarch.com/user/m98789)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxte4n/?context=3#odxte4n "Apr 02 2026, 19:23:19 UTC")

The key question: how does it compare to GPT-OSS-120B

7

[u/Hot-Will1191](https://redlib.catsarch.com/user/Hot-Will1191)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/ody4qxl/?context=3#ody4qxl "Apr 02 2026, 20:17:01 UTC")

My initial impression is that 26B-A4B and 31B are extremely smooth with translation and language. Honestly, it's in a tier of its own (for its size) so far which is something I've been waiting for over a year now. It even makes translategemma feel outdated instantly for my use case. E4B and E2B are a bit meh.

> [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/ody4qxl)

7

[u/HopePupal](https://redlib.catsarch.com/user/HopePupal)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx7uka/?context=3#odx7uka "Apr 02 2026, 17:43:35 UTC")

dense 31B? damn. good week to have bought a 32 GB GPU.

6

[u/plaintexttrader](https://redlib.catsarch.com/user/plaintexttrader)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxc4dn/?context=3#odxc4dn "Apr 02 2026, 18:02:47 UTC")

This maybe the swiss army knife one-size-fits-all of open weight models… text image video audio IO, MoE, reasoning, etc.

6

[u/Daniel_H212](https://redlib.catsarch.com/user/Daniel_H212)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxcoxu/?context=3#odxcoxu "Apr 02 2026, 18:05:23 UTC")

Had gemini generate a visualization of benchmark scores between gemma 4 and qwen3.5 for me (model cut off on the right is qwen3.5-35b-a3b)

[![Image 17](https://redlib.catsarch.com/preview/pre/o8coe45mhtsg1.png?width=803&format=png&auto=webp&s=71d5400e3a25bfd98c31e603840ac2385685ccbc)](https://redlib.catsarch.com/preview/pre/o8coe45mhtsg1.png?width=803&format=png&auto=webp&s=71d5400e3a25bfd98c31e603840ac2385685ccbc)

6

[u/Mean-Ad1493](https://redlib.catsarch.com/user/Mean-Ad1493)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odws8xm/?context=3#odws8xm "Apr 02 2026, 16:33:09 UTC")

Will they be putting out the turboquant versions?

6

[u/Mashic](https://redlib.catsarch.com/user/Mashic)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwvc7c/?context=3#odwvc7c "Apr 02 2026, 16:47:31 UTC")

Why nothing in 9-15b sizes?

> [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwvc7c)

5

[u/jld1532](https://redlib.catsarch.com/user/jld1532)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx1nfh/?context=3#odx1nfh "Apr 02 2026, 17:16:01 UTC")edited Apr 02 '26

The LM Studio staff pick fails to load. Anyone else?

E: Works now. Not sure what the issue was before.

> 14
> 
> 
> 
> [u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx2ifu/?context=3#odx2ifu "Apr 02 2026, 17:19:52 UTC")
> 
> switch to llama.cpp today

6

[u/Bitter-Breadfruit6](https://redlib.catsarch.com/user/Bitter-Breadfruit6)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx3glk/?context=3#odx3glk "Apr 02 2026, 17:24:06 UTC")

I was waiting for the 120b rumors, so this is disappointing. I think there are limitations due to the model's size, no matter how well it is trained.

> 4
> 
> 
> 
> [u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx3qcf/?context=3#odx3qcf "Apr 02 2026, 17:25:18 UTC")
> 
> it's possible that 124B model was planned but failed in benchmarks/ELO, or maybe it will be released later
> 
> 
> > 4
> > 
> > 
> > 
> > [u/Bitter-Breadfruit6](https://redlib.catsarch.com/user/Bitter-Breadfruit6)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx42fy/?context=3#odx42fy "Apr 02 2026, 17:26:46 UTC")
> > 
> > I wish that were true.
> > 
> > 
> > 
> > 3
> > 
> > 
> > 
> > [u/FlamaVadim](https://redlib.catsarch.com/user/FlamaVadim)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxgqj7/?context=3#odxgqj7 "Apr 02 2026, 18:23:58 UTC")
> > 
> > ...or it was to good compared to gemini flash
> > 
> > 
> > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxgqj7)
> > 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx3qcf)

4

[u/gofiend](https://redlib.catsarch.com/user/gofiend)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxhgll/?context=3#odxhgll "Apr 02 2026, 18:27:23 UTC")

Pretty insane to see the E4B model beating one of the best models from last year. Unlikely to be true in broad real world use but a great signal anyway

3

[u/notdba](https://redlib.catsarch.com/user/notdba)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwoqqx/?context=3#odwoqqx "Apr 02 2026, 16:16:46 UTC")

> No Thinking Content in History: In multi-turn conversations, the historical model output should only include the final response. Thoughts from previous model turns must not be added before the next user turn begins

Eh it is still using the weird interleaved thinking mode. The other 2 new models, Trinity Large Thinking and Qwen3.6 Plus, already embrace the preserved thinking mode.

> 11
> 
> 
> 
> [u/mikael110](https://redlib.catsarch.com/user/mikael110)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx0cl6/?context=3#odx0cl6 "Apr 02 2026, 17:10:08 UTC")edited Apr 02 '26
> 
> Personally I actually prefer that, as preserving thinking means the context size balloons really, really quickly. And I haven't actually found that models that preserve thinking perform that much better than those that don't.
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx0cl6)

4

[u/Skyline34rGt](https://redlib.catsarch.com/user/Skyline34rGt)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwt2h4/?context=3#odwt2h4 "Apr 02 2026, 16:37:00 UTC")

Q4K-m gguf from LmStudio model of 26b model got me 'fail load'...

> 6
> 
> 
> 
> [u/Skyline34rGt](https://redlib.catsarch.com/user/Skyline34rGt)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwudj3/?context=3#odwudj3 "Apr 02 2026, 16:43:05 UTC")
> 
> Ah, runtime _CUDA 12 support is coming soon_
> 
> 
> > [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwudj3)
> 
> [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwt2h4)

4

[u/bakawolf123](https://redlib.catsarch.com/user/bakawolf123)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odwz9uo/?context=3#odwz9uo "Apr 02 2026, 17:05:14 UTC")

What is this elo graph coming from? Comparing the reported test numbers alone it looks to be on par with Qwen3.5 27B, some scores higher, some lower.

> 9
> 
> 
> 
> [u/jacek2023](https://redlib.catsarch.com/user/jacek2023)llama.cpp[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx074a/?context=3#odx074a "Apr 02 2026, 17:09:27 UTC")
> 
> I don't trust benchmarks anymore because models are benchmaxxxed. Elo should be the only valid benchmark because it's based on arena votes from humans, but even that could somehow be broken in 2026. It's [arena.ai](http://arena.ai/), it was called lmarena before
> 
> 
> > 8
> > 
> > 
> > 
> > [u/bakawolf123](https://redlib.catsarch.com/user/bakawolf123)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx2mia/?context=3#odx2mia "Apr 02 2026, 17:20:22 UTC")
> > 
> > Thanks, well gotta be cautious trusting anything LLM-related in 2026: this arena has 31B with same score as sonnet-4.5, which leaves me very doubtful. Google has probably received enough of those user traces from this arena for gemini and now has a decent idea what users there vote for and skew in that direction. E.g. make model hallucinate more instead of confirming it can't answer
> > 
> > 
> > > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odx2mia)

4

[u/toothpastespiders](https://redlib.catsarch.com/user/toothpastespiders)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxq8y0/?context=3#odxq8y0 "Apr 02 2026, 19:08:23 UTC")edited Apr 02 '26

I have a few random trivia questions I toss at models just to get a feel for their training data. Not so much expecting a right answer, but more to see how they fail and if they get the general gist of the topic even if getting the specifics wrong. 31b got my history, early American literature, and pop culture questions totally right and 26b came really close.

Hardly a real benchmark or anything. But it's the best I've ever seen from models this size.

Edit: Still just playing around rather than seriously testing it. But both 31b and 26b seem to handle pretty much everything I could have wanted. Doing great with my RAG and higher contexts, seems to cover humanities and some soft sciences even better than gemma 3, and I'm not getting any false positives for "safety". Assuming it can handle some additional fine tuning then I think it's an easy winner for my new jack of all trades default.

3

[u/FluoroquinolonesKill](https://redlib.catsarch.com/user/FluoroquinolonesKill)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxtvo4/?context=3#odxtvo4 "Apr 02 2026, 19:25:38 UTC")

Um...holy shit this thing has no qualms about enterprise resource planning. ;)

> [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odxtvo4)

4

[u/Craftkorb](https://redlib.catsarch.com/user/Craftkorb)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/ody1faw/?context=3#ody1faw "Apr 02 2026, 20:01:25 UTC")

Comparison table for Gemma4 31B + 26B and Qwen3.5 27B and 35B, source is their respective huggingface pages (Self reported values).

| Metric | Gemma 4 31B | Gemma 4 26B A4B | Qwen3.5 27B | Qwen3.5 35B-A3B |
| :--- | :--- | :--- | :--- | :--- |
| **MMLU-Pro** | 85.2% | 82.6% | 86.1 | 85.3 |
| **MMMLU** | 88.4% | 86.3% | 85.9 | 85.2 |
| **LiveCodeBench v6** | 80.0% | 77.1% | 80.7 | 74.6 |
| **CodeForces** | 2150 | 1718 | 1899 | 2028 |
| **GPQA Diamond** | 84.3% | 82.3% | 85.5 | 84.2 |
| **TAU2-Bench** | 76.9% | 68.2% | 79.0 | 81.2 |

4

[u/MaddesJG](https://redlib.catsarch.com/user/MaddesJG)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odyf3vf/?context=3#odyf3vf "Apr 02 2026, 21:06:41 UTC")edited Apr 03 '26

It's a bit late where I am, but I threw Gemma4-26b on my mi50 32gb Ran it with -c 128000 -dev rocm0 Used the UD Q4. Llama-bench got about 939 +- 21 on pp512 and 76 on tg128

Ran a quick 2 prompt run with llama-cli and got about the same results.

I'll have to test some more tomorrow, I'm too tired rn.

Edit: Rocm 7.13.0 and llama version 8639 Edit2: did some more testing. Holy is this thing broken lol. Probably going to wait a day and try again with latest llama build

5

[u/First_Ad6432](https://redlib.catsarch.com/user/First_Ad6432)[Apr 02 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/odyhtne/?context=3#odyhtne "Apr 02 2026, 21:20:07 UTC")

holy moly, im seeing infinite finetunes for it

4

[u/WaveformEntropy](https://redlib.catsarch.com/user/WaveformEntropy)[Apr 03 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1salgre/gemma_4_has_been_released/oe0sstf/?context=3#oe0sstf "Apr 03 2026, 05:41:28 UTC")

Happy German 4 day!

Spent half the night testing it and I think people don't realize how big of a deal it is for those of us who value the range of philosophical thinking more than tool use.

v0.36.0 [ⓘ View instance info](https://redlib.catsarch.com/info "View instance information")[<> Code](https://github.com/redlib-org/redlib "View code on GitHub")
