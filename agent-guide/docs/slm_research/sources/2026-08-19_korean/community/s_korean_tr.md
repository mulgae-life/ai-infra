Title: Redlib: search results - korean translation

URL Source: https://redlib.catsarch.com/r/LocalLLaMA/search?q=korean+translation&restrict_sr=on&sort=relevance&t=all

Markdown Content:
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

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[How effective are LLMs at translating heavy context-based languages like Japanese, Korean, Thai, and others?](https://redlib.catsarch.com/r/LocalLLaMA/comments/1ljz6sh/how_effective_are_llms_at_translating_heavy/)

4  Upvotes

Most of these languages rely deeply on cultural nuance, implied subjects, honorifics, and flexible grammar structures that don't map neatly to English or other Indo-European languages. For example:

Japanese often omits the subject and even the object, relying entirely on context.

Korean speech changes based on social hierarchy and uses multiple speech levels.

Thai and Vietnamese rely on particles, tone, and implied relationships to carry meaning.

So Can LLMs accurately interpret and preserve the intended meaning when so much depends on what’s not said?

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[Where can I download glossary for Japanese, Chinese and Korean translation to english](https://redlib.catsarch.com/r/LocalLLaMA/comments/1maoiae/where_can_i_download_glossary_for_japanese/)

0  Upvotes

Where can I download glossary for Japanese, Chinese and Korean translation to english

Do someone know where can I download glossaries for translation, for things like fanfics of animes, mangas, or even novels?

Because I tried to make some, and when I used it remarkable improved the translation for some fanfics I was reading, mainly to maintain same translation of character name, places and specific terms through long stories

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[Need help translating Korean videos](https://redlib.catsarch.com/r/LocalLLaMA/comments/1lvex1e/need_help_translating_korean_videos/)

4  Upvotes

Hi, I’m working on translating a Korean video into English and could really use some advice.

I first tried using Whisper AI through Google Colab to do everything in one go (transcription + translation), but the results weren’t super accurate.I tried a different approach: I used Whisper just for the transcription, then took the SRT file and fed it into ChatGPT with some custom instructions for translation, and the quality was way better.

The only downside is that the whole process feels a bit tedious and manual. Is there a way to automate this workflow a bit more? Maybe some tools or scripts that could help speed things up?

Any tips would be appreciated. Thanks

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[Speculative Decoding works great for Gemma 4 31B with E2B draft (+29% avg, +50% on code)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1sjct6a/speculative_decoding_works_great_for_gemma_4_31b/)

321  Upvotes

Following up on my previous Gemma 4 31B benchmark post, I tested speculative decoding with Gemma 4 E2B (4.65B) as the draft model.

The results were much better than I expected, so I wanted to share some controlled benchmark numbers.

## Setup

*   **GPU**: RTX 5090 (32GB VRAM)
*   **OS**: Windows 11
*   **Main model**: Gemma 4 31B UD-Q4_K_XL (18.3GB)
*   **Draft model**: Gemma 4 E2B UD-Q4_K_XL (3.0GB)
*   **Backend**: llama.cpp fork with TurboQuant KV cache (turbo3)
*   **Config**: 128K context, parallel=1, Flash Attention, `--draft-max 8 --draft-min 1`

## Benchmark Results

Same server config for both, max_tokens=500, temp=0.7, warm-up query discarded before measuring.

[![Image 1](https://redlib.catsarch.com/preview/pre/gjyo1gl1crug1.png?width=1007&format=png&auto=webp&s=6574ab5093a44846d688de2a951f661cbce2013b)](https://redlib.catsarch.com/preview/pre/gjyo1gl1crug1.png?width=1007&format=png&auto=webp&s=6574ab5093a44846d688de2a951f661cbce2013b)
| Query Type | Baseline (t/s) | SpecDec (t/s) | Accept Rate | Speedup |
| --- | --- | --- | --- | --- |
| Math explanation | 57.45 | **85.86** | 62.9% | **+49.5%** |
| Korean poetry | 56.93 | **62.34** | 44.1% | **+9.5%** |
| Code generation | 57.15 | **86.05** | 60.7% | **+50.5%** |
| Science explanation | 57.19 | **71.14** | 50.9% | **+24.4%** |
| Translation + analysis | 57.14 | **63.26** | 42.2% | **+10.7%** |
| **Average** | **57.17** | **73.73** | **52.2%** | **+29.0%** |

Even at 42% acceptance rate, speculative decoding is still +10% faster because there's zero token translation overhead when the vocabs are compatible.

## The GGUF Version Trap

I initially got terrible results — the draft model was _slower_ than no draft at all (7.31 t/s vs 57 t/s baseline). Every draft model combo gave this warning:

```
the target and draft vocabs are not compatible - tokens will be translated between the two
```

After digging into `speculative.cpp`, I found the compatibility check compares `add_bos_token` between target and draft. My 31B GGUF was from early April when Gemma 4 first dropped, and it had `add_bos_token = false`. The E2B model (downloaded later) had `add_bos_token = true`. This single metadata mismatch forced llama.cpp into token translation mode, killing all performance gains.

**Re-downloading the 31B GGUF** (Unsloth re-quantized all Gemma 4 GGUFs recently with the fix) made the warning disappear and unlocked the full +29% speedup.

**TL;DR**: If you downloaded your Gemma 4 GGUF in early April 2026, re-download it. The tokenizer metadata was fixed.

## Practical Tips

Add these flags to your existing llama-server command:

```
-md gemma-4-E2B-it-UD-Q4_K_XL.gguf
-ngld 99
--draft-max 8
--draft-min 1
--parallel 1
```

Things to watch out for:

*   `--parallel 1`**is mandatory** — with auto (=4), the draft model's KV cache is allocated 4x, eating VRAM and tanking speed to 7 t/s
*   **No vision** — speculative decoding and multimodal can't be used together
*   **Q4 draft is fine** — Q8 (4.8GB) doesn't improve speed over Q4 (3.0GB), and Q4 leaves more VRAM headroom
*   _Extra VRAM ~2.3GB — total ~23.4GB with 128K context on a 32GB card (256K fits too, ~25.5GB)._

## Content-dependent speedup

The gains scale with how predictable the output is:

*   **Code / Math** (structured, repetitive patterns): ~60% accept rate → **+50% speed**
*   **Explanations** (semi-structured): ~50% accept rate → **+24%**
*   **Creative / Translation** (less predictable): ~42% accept rate → **+10%**

Even the worst case is still a net positive, which is the key difference from having incompatible vocabs where even 65% acceptance rate resulted in zero gains.

## draft-max Sweep

Thanks to [u/Odd-Ordinary-5922](https://redlib.catsarch.com/u/Odd-Ordinary-5922) for the suggestion. Same benchmark setup, only varying `--draft-max`:

| draft-max | Math | Poetry | Code | Science | Translation | **Avg (t/s)** | **vs baseline** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 57.45 | 56.93 | 57.15 | 57.19 | 57.14 | **57.17** | — |
| 2 | 73.43 | 60.49 | 68.69 | 62.46 | 62.42 | **65.50** | +14.6% |
| 4 | 83.31 | 60.88 | 73.12 | 65.29 | 67.98 | **70.12** | +22.6% |
| **8** | **85.86** | **62.34** | **86.05** | **71.14** | **63.26** | **73.73** | **+29.0%** |
| 16 | 99.35 | 62.58 | 78.74 | 68.39 | 58.31 | **73.47** | +28.5% |

**draft-max 8 is the sweet spot** for mixed workloads. 16 pushes math to 99 t/s but regresses on creative/translation, ending up about the same average. Creative text stays flat (~62 t/s) regardless of draft-max — the bottleneck there is acceptance rate, not draft length.

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[DBRX-instruct is pretty good at translating Korean and Japanese to english.](https://redlib.catsarch.com/r/LocalLLaMA/comments/1bq9cvb/dbrxinstruct_is_pretty_good_at_translating_korean/)

3  Upvotes

It's very sensitive to the prompt you give it, but I found "Please act as a light novel translator and translate to English (remember English has paragraph breaks)" yielded pretty good translation results, the results were very similar to what Claude Opus produced.

Occassionally there were less natural turns of phrases like "It was a learned result that was engraved in my bones, that I had to say something in this atmosphere." which seems more stilted than Claude's "I didn't know what was going on, but in this atmosphere, I had to say something. It was a deeply ingrained lesson." Or the official translation of "It was important to keep the conversation going in a situation like this, even if I didn’t really know what it was about. I’d learned that lesson well from experience."

But that seems almost nitpicky given how well it seems to do at this task.

I tried it here:

[https://labs.pplx.ai/](https://labs.pplx.ai/)

## [News](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22News%22&restrict_sr=on)[Big tech companies, now "DRAM beggars," are staying in Pangyo and Pyeongtaek, demanding "give us some supplies."](https://redlib.catsarch.com/r/LocalLLaMA/comments/1q84u82/big_tech_companies_now_dram_beggars_are_staying/)

[![Image 2: Thumbnail](https://redlib.catsarch.com/preview/external-pre/bSPrxxtNL1oMDlmeG0HktX0ZjOAtRM_In15JbYuAojA.jpeg?width=140&height=73&auto=webp&s=c7ec382010136839d7940f22b1dcc383166a67a2) chosun.com](https://www.chosun.com/economy/tech_it/2026/01/09/MZNIFPCMTZGHHPV5757NJC5QW4/)
294  Upvotes

Not a Korean speaker. Came across this in another sub. The TLDR is that everyone is scrambling to buy as much as they can as soon as they can, because "demanding a 50-60% increase in server DRAM supply prices from the previous quarter during their first-quarter negotiations with customers".

Per the article, DDR4 prices went up from $1.40 last January to $9.30 in December (my interpretation is $/GB). If they're increasing by another 50%, that's almost $14/GB!!! So, 1TB of DDR4-3200 will cost north of $14k by Q2 if this is true 🤯

In case anyone thought things weren't already bad, it's going to get much much worse this year.

Here's the full Google translate of the article:

DRAM, a type of memory semiconductor, was the key driver behind Samsung Electronics' first-quarter operating profit surpassing 20 trillion won. DRAM products, including high-bandwidth memory (HBM), are a core component of the computing infrastructure supporting the artificial intelligence (AI) era. The semiconductor industry predicts that the DRAM shortage, which began in earnest in the second half of last year, will continue until the end of this year, with prices also expected to continue rising.

Samsung Electronics and SK Hynix, major suppliers of DRAM, are reportedly demanding a 50-60% increase in server DRAM supply prices from the previous quarter during their first-quarter negotiations with customers. A semiconductor industry insider reported, "Even with significantly higher prices, the prevailing sentiment is 'let's buy as much as we can before it gets more expensive.'" Recently, semiconductor purchasing managers from Silicon Valley tech companies, nicknamed "DRAM Beggars," have been reportedly competing fiercely to secure remaining DRAM inventory at hotels in the Pangyo and Pyeongtaek areas.

The semiconductor industry analyzes that "the demand that was initially focused on HBM in the early days of the AI ​​craze is now spreading to server DRAM, creating an unprecedented semiconductor boom." DRAM is a semiconductor that manages a computer's "short-term memory." It stores and quickly transmits necessary data when the central processing unit (CPU), the brain, performs tasks. HBM is specialized for seamlessly delivering the massive data required for AI by increasing the data transmission path (bandwidth) dozens of times compared to conventional DRAM. However, HBM is extremely expensive and has limitations in increasing capacity. This explains why big tech companies are scrambling to secure server DRAM products to store more data.

The average contract price of DRAM soared from $1.40 (based on 8GB DDR4) in January last year to $9.30 in December. This marks the first time in seven years and four months that DRAM prices have surpassed the $9 threshold. Kim Dong-won, head of the research center at KB Securities, said, "Due to this price increase, the operating profit margin (the ratio of operating profit to sales) of some general-purpose memories (widely used standard memories) is expected to reach 70%, and DDR5 may even surpass the margin of HBM3E. This year, semiconductor companies' performance is expected to be determined by general-purpose memories."

## [Other](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Other%22&restrict_sr=on)[If You Already Pay for an LLM Service, Running Local Embeddings and Rerankers Feels More Useful Than Running Local LLMs](https://redlib.catsarch.com/r/LocalLLaMA/comments/1us3li5/if_you_already_pay_for_an_llm_service_running/)

191  Upvotes

[![Image 3](https://redlib.catsarch.com/preview/pre/v0xtn3jdu9ch1.png?width=2047&format=png&auto=webp&s=628a6a541fe5f097d0f771ae0ba3b7f44126198f)](https://redlib.catsarch.com/preview/pre/v0xtn3jdu9ch1.png?width=2047&format=png&auto=webp&s=628a6a541fe5f097d0f771ae0ba3b7f44126198f)[![Image 4](https://redlib.catsarch.com/preview/pre/vjxiucsdu9ch1.png?width=2047&format=png&auto=webp&s=74f7a18a5a30276e206e2bfb5a0c529826ce86e4)](https://redlib.catsarch.com/preview/pre/vjxiucsdu9ch1.png?width=2047&format=png&auto=webp&s=74f7a18a5a30276e206e2bfb5a0c529826ce86e4)
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

## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[I found that MXFP4 has lower perplexity than Q4_K_M and Q4_K_XL.](https://redlib.catsarch.com/r/LocalLLaMA/comments/1qrzyaz/i_found_that_mxfp4_has_lower_perplexity_than_q4_k/)

133  Upvotes

This post was originally written in Korean and then translated into English using ChatGPT.

 Hello, I am currently serving LLM models using a Tesla P40 and llama.cpp. When running models in the 30–32B range, I usually rely on 4-bit quantization. Until now, I primarily used Q4_K_XL, and if Q4_K_XL was not available, I used Q4_K_M instead. I initially avoided MXFP4 quantization because, compared to other 4-bit quantization methods, it has a smaller size, so I naturally assumed its accuracy would be lower. However, out of curiosity sparked by MXFP4’s fast speed, I compared Q4_K_M, Q4_K_XL, and MXFP4 quantization methods for the GLM-4.7-Flash and Nemotron-3-nano models using the `llama-perplexity` command.

Below are the commands used, along with the Python code and command used to generate the dataset. The dataset generation command was created using ChatGPT.

**Code**

```
import argparse
import os
import re
import sys
import urllib.request
from pathlib import Path
import random

def download(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as r, open(dst, "wb") as f:
        f.write(r.read())

def normalize_text(text: str, mode: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    if mode == "ppl":
        text = re.sub(r"\n\s*\n+", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = text.strip() + "\n"
        return text

    if mode == "line":
        lines = []
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            line = re.sub(r"[ \t]+", " ", line)
            lines.append(line)
        return "\n".join(lines) + "\n"

    raise ValueError(f"unknown mode: {mode}")

def take_prefix(text: str, max_chars: int | None) -> str:
    if max_chars is None:
        return text
    if max_chars <= 0:
        return ""
    return text[:max_chars]

def sample_lines(text: str, n_lines: int, seed: int) -> str:
    random.seed(seed)
    lines = [ln for ln in text.split("\n") if ln.strip()]
    if n_lines <= 0 or n_lines >= len(lines):
        return "\n".join(lines) + "\n"
    sampled = random.sample(lines, n_lines)
    return "\n".join(sampled) + "\n"

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--url", help="download source url")
    g.add_argument("--infile", help="local input file path")
    ap.add_argument("--out", required=True, help="output text file path")
    ap.add_argument("--mode", choices=["ppl", "line"], default="ppl",
                    help="ppl: keep newlines but collapse blanks/spaces, line: one sentence per line style")
    ap.add_argument("--max-chars", type=int, default=None,
                    help="optional: cut the output to first N characters (fast/low-memory eval)")
    ap.add_argument("--sample-lines", type=int, default=None,
                    help="optional: sample N non-empty lines uniformly (good for quick comparison)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    out_path = Path(args.out)

    if args.url:
        tmp = out_path.with_suffix(out_path.suffix + ".download")
        download(args.url, tmp)
        in_path = tmp
    else:
        in_path = Path(args.infile)

    try:
        raw = in_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"failed to read input: {e}", file=sys.stderr)
        sys.exit(1)

    text = normalize_text(raw, args.mode)

    if args.sample_lines is not None:
        text = sample_lines(text, args.sample_lines, args.seed)

    text = take_prefix(text, args.max_chars)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")

    if args.url:
        try:
            os.remove(in_path)
        except OSError:
            pass

    print(f"wrote: {out_path} ({out_path.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
```

**Command**

```
python3 wikitext_prep.py \
  --url https://cosmo.zip/pub/datasets/wikitext-2-raw/wiki.test.raw \
  --out /data/wikitext2_test.txt \
  --mode ppl \
  --max-chars 2000000
```

Using the command below, I measured the perplexity of the quantized models.

```
llama-perplexity -m modelname.gguf -f wikitext2_test.txt -c 32768 -b 4096 -fa on
```

The table below summarizes the test results, which were also organized using ChatGPT. The actual `llama-perplexity` output is quite long, so it is attached separately below. For reference, Q4_K_M and Q4_K_XL were measured simultaneously, and after a llama.cpp update, Q4_K_XL and MXFP4 were measured simultaneously. Because the testing time was very long and the perplexity of Q4_K_XL was similar before and after the update, I assumed that the perplexity of Q4_K_M would also not be significantly affected by build changes.

| Item | Q4_K_M (Unsloth) | UD-Q4_K_XL (previous) | MXFP4_MOE | UD-Q4_K_XL (current) |
| --- | --- | --- | --- | --- |
| llama.cpp build | 7803 | 7803 | 7896 | 7896 |
| GGUF file type | Q4_K – Medium | Q4_K – Medium | MXFP4 MoE | Q4_K – Medium |
| File size | 17.05 GiB | 16.31 GiB | 15.79 GiB | 16.31 GiB |
| BPW | 4.89 | 4.68 | 4.53 | 4.68 |
| PPL (final) | **16.1745 ± 0.1870** | **15.8605 ± 0.1823** | **10.7235 ± 0.1052** | **15.7309 ± 0.1803** |
| Prompt eval speed | 64.39 tok/s | 64.37 tok/s | **68.20 tok/s** | **67.73 tok/s** |
| ms/token | 15.53 ms | 15.54 ms | **14.66 ms** | **14.76 ms** |
| Time per pass (ETA) | 529.38 s | 530.05 s | **501.55 s** | **502.66 s** |
| GPU self (total) | 20811 MiB | 20056 MiB | **17874 MiB** | 18552 MiB |
| GPU model buffer | 17284.84 MiB | 16529.37 MiB | **15852.01 MiB** | 16529.37 MiB |
| KV cache size | **3196 MiB** (K 1692 + V 1504) | **3196 MiB** (K 1692 + V 1504) | **1692 MiB** (K 1692 + V 0) | **1692 MiB** (K 1692 + V 0) |
| GPU free (log-based) | 3406 MiB | 4162 MiB | **6342 MiB** | 5666 MiB |
| Load time | 9.90 s | 9.55 s | **71.13 s** | 43.72 s |
| mmap / direct_io | mmap off / direct_io on | mmap off / direct_io on | mmap on / direct_io off | mmap on / direct_io off |

| Model | [1] | [2] | [3] | [4] | [5] | [6] | Final PPL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q4_K_M | 15.2952 | 15.1950 | 15.7101 | 14.8037 | 14.5891 | 16.1745 | 16.1745 ± 0.1870 |
| UD-Q4_K_XL (previous) | 14.7572 | 14.4954 | 15.0386 | 14.1713 | 14.1425 | 15.8605 | 15.8605 ± 0.1823 |
| MXFP4_MOE | 10.1764 | 10.1296 | 10.4917 | 9.8666 | 9.8629 | 10.7235 | 10.7235 ± 0.1052 |
| UD-Q4_K_XL (current) | 14.4241 | 14.2673 | 14.8671 | 14.0460 | 14.0444 | 15.7309 | 15.7309 ± 0.1803 |

Below is a table comparing MXFP4 and Q4_K_XL quantization methods on the Nemotron-3-nano model. This table was also created using ChatGPT.

| Item | Q4_K_XL (previous) | MXFP4 (current) | Change (MXFP4 − Q4_K_XL) | Meaning |
| --- | --- | --- | --- | --- |
| Final PPL | 7.7090 | 7.5294 | **-0.1796** | **MXFP4 is lower → based on this corpus, “less accuracy loss (or more accurate)”** |
| PPL error (±) | 0.05361 | 0.05198 | -0.00163 | Uncertainty is nearly identical |
| Prompt eval speed | 763.26 tok/s | 797.79 tok/s | **+34.53 tok/s (+4.5%)** | MXFP4 is slightly faster |
| Time per pass | 24.74 s/pass | 23.45 s/pass | -1.29 s/pass | MXFP4 is slightly shorter |
| GPU model memory | 21537 MiB | 16782 MiB | **-4755 MiB** | MXFP4 uses **significantly less model memory** |
| GPU free VRAM | 2286 MiB | 7040 MiB | **+4754 MiB** | Available VRAM increases greatly |
| GPU context memory | 143 MiB | 143 MiB | 0 | Same due to identical `n_ctx` |
| GPU compute buffer | 271 MiB | 271 MiB | 0 | Same |
| Host usage (total) | 268 MiB | 394 MiB | +126 MiB | Difference is small and of limited significance |

I rewrote this post to add the Nemotron-3-nano benchmark, and in the previous post, one user commented that perplexity and tool calling or coding are completely different domains. They mentioned that using the HumanEval benchmark would provide values more directly related to tool calling and coding performance. If I get the chance, I plan to test again using the HumanEval benchmark in the future.

[https://www.reddit.com/r/LocalLLaMA/comments/1qrwnd4/comment/o2rape9/](https://redlib.catsarch.com/r/LocalLLaMA/comments/1qrwnd4/comment/o2rape9/)

To be honest, after seeing these benchmark results, I hoped that perplexity would be directly related to coding and tool calling performance, so it is a bit disappointing.

 If anyone has other opinions, I would appreciate it if you could share them.

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[LiquidAI/LFM2.5-VL-3B · Hugging Face](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vmfy8w/liquidailfm25vl3b_hugging_face/)

[![Image 5: Thumbnail](https://redlib.catsarch.com/preview/external-pre/dagBiePP0xBwDh_rPRMaGDDxw828K-RVBWEC_35E0Vg.png?width=140&height=75&auto=webp&s=06fab755dc3409a4ed29b8d078a05a093eb053ab) huggingface.co](https://huggingface.co/LiquidAI/LFM2.5-VL-3B)
106  Upvotes

LFM2.5-VL-3B is a multimodal variant of LFM2.5, a family of hybrid models designed for**on-device deployment**. It builds on LFM2-VL-3B with further mid- and post-training. LFM2.5-VL-3B can process both text and images, and uses the LFM2.5-2.6B language model as its backbone, combined with a SigLIP2 NaFlex vision encoder.

*   **Better grounding**: Improved grounding and object detection with natural language queries.
*   **Better OCR**: Full page OCR with layout annotation. See[layout annotation format](https://huggingface.co/LiquidAI/LFM2.5-VL-3B#layout-annotation-format)for more information.
*   **Efficient inference**: 228 tok/s on an Apple M5 Max and 116 tok/s on an AMD Ryzen AI Max+ 395, in under 3.3 GB of memory.

Find more information about LFM2.5-VL-3B in our[release post](https://www.liquid.ai/blog/lfm2-5-vl-3b).

**Model Details:**

*   **LM Backbone**: LFM2.5-2.6B
*   **Vision encoder**: SigLIP2 NaFlex shape‑optimized 400M
*   **Vocabulary size:**128,000
*   **Context length**: 32,768 tokens
*   **Languages**: English, Arabic, Chinese, French, German, Italian, Japanese, Korean, Portuguese, Spanish, Vietnamese, Thai, Indonesian, Hindi, Russian, Polish
*   **Native resolution processing**: Uses SigLIP2's NaFlex; large images are split into non-overlapping 512×512 patches and a resized whole-image thumbnail.
*   **Generation parameters**: 
    *   text:`temperature=0.2`,`top_k=50`,`repetition_penalty=1.0`
    *   vision: Use the`processor_config.json`file.

We recommend using it for single-turn, high-throughput, low-latency tasks; for example, for near-realtime object detection in automotive applications, batch processing scanned documents with OCR with layout information for turning PDFs into searchable text, or for on-device translation of menus and road signs into your native language.

It is not recommended for long-context, reasoning-intensive tasks, such as visual web design, or answering highly technical questions about blueprints.

## On-device Inference

LFM2.5-VL-3B decodes 228 tokens/s on an Apple M5 Max and 116 tokens/s on an AMD Ryzen AI Max+ 395, and fits in about 3 GB of memory. It even reaches 20 tokens/s on a Galaxy S26 Ultra, so you can run it fully on-device.

## GPU Inference

On a single NVIDIA H100 with vLLM, LFM2.5-VL-3B reaches the highest output throughput of any model we tested, about 11K tokens per second at high concurrency, or nearly 1B tokens per day.

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[What if I run the LLM backwards? Hey LLM, why bother remembering every single turn? It's a hassle. You don't have to do it, right?](https://redlib.catsarch.com/r/LocalLLaMA/comments/1u7sy0j/what_if_i_run_the_llm_backwards_hey_llm_why/)

0  Upvotes

Hey guys. The AI-translation guy is back. lol. Can I say what i actually want to say now, instead of the AI translation from my last post?

 So i've been studying LLMs for a few months and found out about this thing called stateless. it shocked me. it's born new every time? the AI services i used didn't seem like that though. turns out they just shove the whole conversation back in to make it look stateful. i really felt that was irrational.

 so i thought, let me break away from how LLMs are normally run, and inject only as much as needed each turn. i laid the basic idea and built it. the complete opposite of how existing agents work. and it works better than i expected. what surprised me most was that the context actually still carries over. but the way it runs felt a bit lacking. to really pull this off i figured i'd need to build an agent and run it. so i'm developing it now. it's pretty far along, and i'm catching various bugs.

 as a side effect of building this, the conversation never breaks. no compact needed, no clear needed. actually every turn is basically a new session. out of the session, you could say? it's way more comfortable than i expected. and since i don't carry that massive prefix every turn, i save a lot of tokens too. i want to finish it fast and show you guys.

 and this agent, i'm trying to support local too, not just cloud — Ollama, llama.cpp, LM Studio. honestly it's more meaningful locally: since the prefix isn't carried, the context doesn't balloon, so i think it'd mean less VRAM use and the speed won't die either. my PC isn't a machine that can run local well so i couldn't test that part enough... but anyone who's run a long local session will know how slow it gets once context piles up. i want to spare people from that.

 if you have counterarguments, tell me. let's discuss. i'm curious how you all think.

ps. wrote this one more directly but it's still korean→english, so go easy on any awkward bits.

## [New Model](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22New%20Model%22&restrict_sr=on)[Cohere Transcribe Released](https://redlib.catsarch.com/r/LocalLLaMA/comments/1s48jtu/cohere_transcribe_released/)

[![Image 6: Thumbnail](https://redlib.catsarch.com/preview/external-pre/ILECQFNe4gjq0ia9uVsaJs2UXu1fKOefeMcKhIxUSsE.png?width=140&height=75&auto=webp&s=ca6a61fcd6740628c44f451139c239cac9e76e42) huggingface.co](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026)
115  Upvotes

Announcement Blog: [https://cohere.com/blog/transcribe](https://cohere.com/blog/transcribe)

Cohere just released their 2B transcription model. It's Apache 2.0 licensed and claims to be SOTA among open transcription models. It supports 14 languages:

*   **European:**English, French, German, Italian, Spanish, Portuguese, Greek, Dutch, Polish
*   **AIPAC:**Chinese, Japanese, Korean, Vietnamese
*   **MENA:**Arabic

Haven't had the time to play with it myself yet, but am eager to give it a try. Given Cohere's previous history with models like Aya which is still one of the best open translation models I am cautiously optimistic that they've done a good job with the multilingual support. And I've had a pretty good time with Cohere models in the past generally.

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[Qwen 3.6 and Gemma 4 "Zombie Loops" (terminal thinking loops)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1t08f2g/qwen_36_and_gemma_4_zombie_loops_terminal/)

5  Upvotes

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

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[Gemma 4 31b AttnRes Project](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/)

10  Upvotes

I had Claude re-draft this for me, thus it has Em Dashes. It's correct with lots of "Claude" simplifications.

---

Hey all. It's been a while since I posted about the AttnRes architecture so I figured I'd give an update on where things are.

Short version: it's alive. Longer version... it's complicated.

So the core idea hasn't changed. Replace the standard residual stream with an attention-based routing mechanism — AttnRes — that lets the model learn WHERE to route information between layers rather than just blindly passing everything forward. Same parameter count as the base model. The hypothesis is that this is a fundamentally better use of the same compute.

The part I've spent the most time on is figuring out how to actually GET there without training from scratch. I don't have Google's budget. I'm one person. So the whole strategy is built around distilling from Gemma into the new architecture using a weaning schedule — you start with the standard residual doing all the work, and you gradually shift responsibility to the AttnRes pathway over the course of training. The model learns to route through the new pathway while the old one is slowly pulled away.

This sounds simple. It is not simple.

The thing that took the longest to figure out was the data. Not volume... diversity. If you distill on a narrow distribution you'll get a model that handles that distribution great and has quietly lost everything else. The model manifold is this massive high-dimensional thing and you have to preserve ALL of it during the transition or you get a model that can code but suddenly responds in mixed Korean and English when you ask it about quantum mechanics. I've seen this happen. It's informative but not ideal.

The solution I landed on was using the model itself to generate diverse coverage. Take a news article. Ask the model to summarize it. Then translate that summary to Bulgarian. Then ask if there are nuances lost in the Bulgarian translation. One piece of source content, three completely different regions of the model's capability space exercised. Scale that across 20 languages that Google trained Gemma to handle well and you get massive manifold coverage from relatively simple data scaffolding.

The other big decision was distillation targets. Most people distill on 1-hot or label smoothed targets. I'm using top-K ~12 logits from the source model with their proportional weights maintained. The reasoning is... the model isn't a next token predictor. It's a next DISTRIBUTION predictor. The relationships between the top candidates at every position encode the model's actual knowledge — what it thinks is likely, what's plausible, what's related. One-hot throws all of that away. Top-K 12 captures ~98% of the probability mass and preserves the distributional shape that IS the manifold.

This matters because during weaning, the new pathway has to learn to reproduce not just the right answers but the right uncertainty structure. That's what forces it to actually internalize the model's knowledge rather than just mimicking outputs.

The goal is NOT perfection. I want a beta that proves the architecture works and is trainable. Good enough that someone can take it, distill new knowledge in using the pipeline I've already built, and improve it. The training code exists because I had to write it to do this work. The data pipeline exists. The methodology is documented. All Apache 2.0.

If a compute provider wants to come along and help push the model to Gemma-level quality... I'm happy to put their name on the HuggingFace card. This is meant to be a community model built on an open architecture that anyone can improve.

More updates as the probing runs finish. Happy to answer questions about the methodology or the reasoning behind any of these decisions.

---

The core model and the training model these are largely distilled from are abliterated variants of the Gemma 4 model. So... It has no safety. It's a use at own risk thing.

Right now I'm waiting on B300's. They're just not available and using a single B300 is my test target right now. Like every datacenter for the last week is 100% sold out and the second they appear they're gone.

Another thing of note, I use Top K 12 distillation, but I've found that for a large portion of the dataset the top 3 or 4 work fine. This comes down to the way language, code, even logic are structured.

Simplistically, you can't write "I want to eat a" and expect the next token to be apple. If you swapped the "a" to "an" then apple and anything else starting with a vowel becomes valid and the probability of everything else falls off.

This happens a LOT from my observations. The other issue is quantization. Quantization affects the longer tail distributions where there are a lot of options. I'm currently investigating both of these issues to make the process more effective.

Removing the layers as seen in the prior model is like... 100x the training necessary. It involves incrementally removing them. Even though I've identified all of them the model becomes too unstable to continue training AND do the other stuff. It would be a matter of cutting Gemma to 3 SWA + Global FIRST, then applying attention residuals. Alternatively, you could insert a block or two in the middle to make the model larger then train MORE then attention residuals.

AFAIK no one outside Moonshot has done this, and even Moonshot used ~1.5t tokens because it was a pretrain to instruct training. Moonshot however demonstrated that their model was ~25% more efficient at learning with this residual stream. Further, Kimi K3 has now released with this exact feature. So I guess I was on to something originally.

Old Post - [https://old.reddit.com/r/LocalLLaMA/comments/1ulmez2/rebuilding_gemma_4_31b_better_as_26b/](https://redlib.catsarch.com/r/LocalLLaMA/comments/1ulmez2/rebuilding_gemma_4_31b_better_as_26b/)

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[Follow-up to my TranslateGemma-12b benchmark post: human reviewers flagged 71% of the segments automated metrics rated clean](https://redlib.catsarch.com/r/LocalLLaMA/comments/1taxrm6/followup_to_my_translategemma12b_benchmark_post/)

18  Upvotes

A couple of weeks ago I [shared the results](https://redlib.catsarch.com/r/LocalLLaMA/comments/1sl5k6d/we_benchmarked_translategemma12b_against_5/) of a benchmark here showing TranslateGemma-12b beating frontier general models (Claude Sonnet, GPT-5.4, DeepSeek, Gemini Flash Lite) on subtitle translation across 6 languages. The result was strong enough that we wanted to verify it ourselves - was TranslateGemma really _that_ good, or were the metrics easy on it? So we added a layer of human review.

Setup: 21 English subtitle segments from one tutorial video. TranslateGemma's translations into 4 languages (ES, JA, TH, ZH-CN - Korean and Traditional Chinese got dropped). 84 translations total, all chosen because they scored well on both automated metrics. Then we sent every translation to human MQM review.

Under the dashboard's own red-flag threshold (`MX ≥ 5 OR CK < 0.70`):

|  | auto-flagged | human-flagged (any) | human-flagged (Major) |
| --- | --- | --- | --- |
| ES | 0/21 | 11/21 | 2/21 |
| JA | 0/21 | 17/21 | 3/21 |
| TH | 0/21 | 17/21 | 5/21 |
| ZH-CN | 1/21 | 15/21 | 3/21 |
| **Total** | **1/84 (1.2%)** | **60/84 (71%)** | **13/84 (15%)** |

Of 25 Accuracy-class errors humans found (mistranslation, omission, addition, untranslated), every single one was in the metric-blind quadrant. The metrics caught zero accuracy errors in this sample.

Per-language failure modes look quite different:

*   **Japanese** is the "fluent but wrong meaning" pattern - high COMETKiwi (0.86 mean), reasonable MetricX, but 10 of the 15 total mistranslations in the dataset are in JA. In the original report we'd already seen the same pattern in Claude Sonnet 4.6 on Japanese (TQI 0.5364, MetricX 3.90, COMETKiwi 0.79 - fluent-sounding but drifting from source). Looks like the failure mode generalises across model families on JA.
*   **Thai** is over-production: 5 Accuracy/Addition errors where the model inserted content not in the source, plus a bunch of punctuation errors driven by English-style periods that Thai doesn't use.
*   **Spanish** is mostly tone inconsistencies (formal/informal switches), genuinely the easiest of the four.
*   **Chinese ZH-CN** had 4 Major errors total, including the one segment automated metrics flagged (Style - "unidiomatic collocation and inappropriate style"; humans agreed with the metric on that one). The other 3 Majors: another Style ("literal translation"), an Accuracy/Omission where "store" was dropped and the meaning changed, and a Fluency/Inconsistency where "ticket" was translated inconsistently across segments.

Caveat: small audit on one model, one content set, so the numbers are directional rather than definitive.

## [Other](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Other%22&restrict_sr=on)[Made a program using LocalLLM based on llama.cpp for fellow Book Lovers!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1tslzyc/made_a_program_using_localllm_based_on_llamacpp/)

14  Upvotes

**TL;DR: I built an Ebook reader embedded with a compact translation model.**

Hi! I know this post has a promotional nature, but it contains a concept that I believe readers who love books will appreciate, so please take a look.

While talking to an AI developer from an English-speaking country living in the Middle East, I complained that the books I wanted to read weren't translated into Korean. When I suggested that we no longer need to carry English-Korean dictionaries like in the past and that AI could handle the translation, he agreed it was a great idea. That’s when I started development. He also strongly recommended that I promote this on the [r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA) subreddit, saying that the community is tech-savvy and would have a lot of insights to offer. (Yes, I actually visit [r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA) often myself. Using an LLM without security concerns is everyone's dream. I haven't achieved it yet due to financial constraints, but based on my experience renting GPUs, I believe a 70B model would satisfy 80% of my requirements.)

My previous experience fine-tuning a 4B LLM and various other projects helped me significantly with this development.

The features are simple. It includes functionalities tailored for book lovers:

*   Inserting sticky notes while reading,
*   Bookmarks with multiple tags,
*   Writing book reviews.

Above all, you can search through the notes and reviews you've written to find that one line that left a deep impression on you. These might seem like simple, trivial features, but I personally have many loose papers tucked into the books I've read. When I pull out a book I read long ago, I find random scraps of paper inside—bookmarks and notes.

[![Image 7](https://redlib.catsarch.com/preview/pre/5u08jpjbpe4h1.png?width=1917&format=png&auto=webp&s=0297c11d9feb338c44636a98a0f63bcceb8a382e)](https://redlib.catsarch.com/preview/pre/5u08jpjbpe4h1.png?width=1917&format=png&auto=webp&s=0297c11d9feb338c44636a98a0f63bcceb8a382e)[![Image 8](https://redlib.catsarch.com/preview/pre/4xxhrpjbpe4h1.png?width=1902&format=png&auto=webp&s=73e957e9d6369d91eed12441c4caafb4b2d4e8cd)](https://redlib.catsarch.com/preview/pre/4xxhrpjbpe4h1.png?width=1902&format=png&auto=webp&s=73e957e9d6369d91eed12441c4caafb4b2d4e8cd)[![Image 9](https://redlib.catsarch.com/preview/pre/khtunukbpe4h1.png?width=1914&format=png&auto=webp&s=6539f762ba535129e8d3add9169271184ef7fe84)](https://redlib.catsarch.com/preview/pre/khtunukbpe4h1.png?width=1914&format=png&auto=webp&s=6539f762ba535129e8d3add9169271184ef7fe84)[![Image 10](https://redlib.catsarch.com/preview/pre/2pd6ipjbpe4h1.png?width=1295&format=png&auto=webp&s=d4d1a3764fd9cf4a9e316824b6fd63395f5c890a)](https://redlib.catsarch.com/preview/pre/2pd6ipjbpe4h1.png?width=1295&format=png&auto=webp&s=d4d1a3764fd9cf4a9e316824b6fd63395f5c890a)
Because I used a 1.8B translation-specific model, it consumes relatively low VRAM (about 3–4GB) while delivering quite decent translation results.

Since everyone here is sharp, I believe you will understand the operating principle just by looking at a few screenshots. I have captured scenes of it translating a German book into English.

Actually, I have a long-standing personal grievance in my heart. I wanted to recommend a Korean book to a young man from Nigeria whom I met in a startup community, but I couldn't introduce it because there was no English translation. I checked with the copyright holders, and they confirmed no English version existed. Back then, using AI for translation wasn't even a thought. Now that I’ve built 'emebala', I still can’t ask that friend to use it.

99% of you on this subreddit probably don't realize how powerful your own hardware and computing power are. I didn't know what life in an impoverished nation was like until I started a small business with that young Nigerian friend. They live without starving, enjoying leisure time, but that is relative to absolute standards. It’s a different story when compared to people in relatively wealthy countries. First of all, they don't have computers. Forget high-end hardware; even mid-range hardware is expensive for them. Their only device is a cheap, low-end smartphone. They can't even dream of fancy iPhone 17s or the latest flagship Androids. They don't have money for paid ChatGPT subscriptions. This is another issue, so I won't go into detail. With the advent of the LLM and AI agent era, those with paid AI models can research these regions faster than the locals themselves. However, that doesn't mean they don't crave knowledge. Diligence and poverty are separate issues. Corrupt customs officers, absurd security problems—they live accepting these as a given, but from my perspective, it incurs serious social costs. After reading books on behavioral economics, I found many parts I couldn't sympathize with because the gap is too vast. I wanted to recommend books about the heroes of Korea's economy in the 50s and 60s when it was poorer, but I had no way to deliver them. So, I bought a few other books in English from a small British e-book broker and had him read and discuss them. Anyway, this is the uncomfortable feeling I carry. I have ideas for people in poor countries in the future, for those who don't have the hardware, but as of now, I lack the overall capabilities and infrastructure to execute them. Life is short, and if I don't take the next steps, I might not be able to recommend the right book at the right time.

Personally, I once did translation work for a Korean Catholic broadcasting station as a volunteer rather than as a job. I was paid, but the hours I worked were much longer than that. So, I know the difficulties translators face, and I know their jobs are disappearing. But I don't think it ends there. Translators need to do more work. With people like me. AI should handle the initial translation, but the "tastier" translation is a field that humans must handle directly. This is an area I will keep in mind and focus on in the future.

There are many booksellers in the world. There are giant bookstores like Amazon and Barnes & Noble, but there are also many very small booksellers. I want 'emebala' to handle books in all the world's languages. I've created a 'Find Book' tab where the feature isn't implemented yet. I want to make it possible to connect to bookstores to buy them, or download free books. If this project goes well, if it goes really well... I want to use a portion of the earnings to buy copyrights and effectively release them for free. So that people can buy them for just $0.5 or $1. I'll need to solve the unique DRM issues with booksellers, but such technical problems aren't the real issues, are they?

The topic has jumped around too much. It's because 'emebala' is my constant concern from the moment I wake up until I sleep. It’s a promotional post, but please don't hate it too much. And I ask for your support.

I've also created [r/emebala](https://redlib.catsarch.com/r/emebala) subreddit. I ask for your interest, especially those who love books!

[https://www.reddit.com/r/emebala/comments/1trszm4/finally_it_is_released/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button](https://redlib.catsarch.com/r/emebala/comments/1trszm4/finally_it_is_released/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[We benchmarked TranslateGemma-12b against 5 frontier LLMs on subtitle translation - it won across the board, with one significant catch](https://redlib.catsarch.com/r/LocalLLaMA/comments/1sl5k6d/we_benchmarked_translategemma12b_against_5/)

45  Upvotes

As part of our ongoing translation quality research at Alconost, we put six models through subtitle translation into six language pairs. At first glance the numbers told a clean story. Then human QA added a chapter.

**Models:**

*   TranslateGemma-12b
*   gemini-3.1-flash-lite-preview
*   deepseek-v3.2
*   claude-sonnet-4-6
*   gpt-5.4-mini
*   gpt-5.4-nano

**Languages:** EN to Spanish, Japanese, Korean, Thai, Chinese Simplified, Chinese Traditional

**Results (avg TQI - our combined metric, higher = better)**

| Rank | Model | Avg TQI |
| --- | --- | --- |
| #1 | TranslateGemma-12b | 0.6335 |
| #2 | gemini-3.1-flash-lite-preview | 0.5981 |
| #3 | deepseek-v3.2 | 0.5946 |
| #4 | claude-sonnet-4-6 | 0.5811 |
| #5 | gpt-5.4-mini | 0.5785 |
| #6 | gpt-5.4-nano | 0.5562 |

TQI = COMETKiwi × exp(−MetricX/10) - details in the report.

The pattern held across every individual language. Draw your own conclusions, but the consistency is hard to ignore: a 12B task-specific model outperformed every general-purpose frontier model on translation fidelity across all six language pairs.

Second notable result: gemini-3.1-flash-lite-preview - a lite model - consistently finished #2-3, ahead of full-weight Claude Sonnet and both GPT-5.4 variants.

All models scored 0.75-0.79 on COMETKiwi (fluency). Models diverged significantly on MetricX-24 fidelity - TranslateGemma averaged 2.18 vs 3.06 for gpt-5.4-nano.

**The catch**

TranslateGemma ranked #1 across all languages. Then our linguists reviewed the Traditional Chinese output.

The model was outputting Simplified Chinese for both zh-CN and zh-TW language codes. We investigated community reports suggesting zh-Hant as the correct explicit tag for Traditional Chinese and retested. Still didn't fix it: 76% of segments came back Simplified, 14% Traditional, 10% ambiguous (segments too short or script-neutral to classify). MetricX-24 and COMETKiwi gave top scores throughout and showed no sign of an issue.

[![Image 11](https://redlib.catsarch.com/preview/pre/0f18kzv1p4vg1.jpg?width=773&format=pjpg&auto=webp&s=3ce537b8ad1a1a33461a478fe634a9f616682d1c)](https://redlib.catsarch.com/preview/pre/0f18kzv1p4vg1.jpg?width=773&format=pjpg&auto=webp&s=3ce537b8ad1a1a33461a478fe634a9f616682d1c)
As it turns out, this is a confirmed, publicly documented issue caused by training data bias - TranslateGemma's fine-tuning corpus is heavily skewed toward Simplified Chinese. The locale tags are accepted without error but not honored by the model's weights. This affects all model sizes (4B, 12B, 27B) - upgrading to a larger model size won't resolve it, since the root cause is training data composition, not capacity. The documented workaround is OpenCC s2twp post-processing.

The part most relevant to anyone building pipelines: your QE scores will look fine the whole time. The failure is completely invisible to automated metrics.

The full report with per-language breakdowns, segment-level examples, and methodology (tabs are clickable): [https://files.alconost.com/r_DbyQKw3ZXKWUVvxpN5t](https://files.alconost.com/r_DbyQKw3ZXKWUVvxpN5t)

## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[srt2speech: open-source, multilingual SRT narration with voice cloning and automatic duration matching - offline and lightweight](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfcdnx/srt2speech_opensource_multilingual_srt_narration/)

5  Upvotes

For a small side project, I needed a basic AI speech tool to narrate videos without relying on expensive hardware or external APIs. It did not need the most expressive AI, just reliable output and matching to the SRT.

The main challenge with converting SRT subtitles to speech is timing. Subtitles include pauses, and each spoken line has to fit into its exact time slot. Most speech generators do not handle that well on their own.

So I built **srt2speech**.

It uses a combination of:

*   pitch-corrected speed adjustment
*   automatic regeneration
*   modification of pauses between words
*   exact placement of silence between subtitle cues

SRT does not support multiple speakers, so I also added simple templating.

 Adding `{{speaker_name}}` to a subtitle automatically switches voices.

 Of course voice cloning is supported, I added a small helper script.

Dependencies are minimal: Python, NumPy, llama.cpp, and the required GGUF speech models. I tested it with Q4 quantization, which works well.

**Performance on my laptop:**

*   RTX 4080 Laptop GPU: around 12–13× real time
*   CPU only: around 1.5–2.0× real time

**Languages supported:**

*   English (`en`)
*   Japanese (`jp`)
*   Korean (`ko`)
*   Chinese (`zh`)
*   French (`fr`)
*   German (`de`)

It should work on almost any hardware, including old PCs, Linux or Mac.

It may be useful for anyone generating narration, translated audio tracks, accessibility audio, or quick video voiceovers.

The project is open source under the Apache 2.0 license. Attribution and license notices must be preserved.

GitHub:

[https://github.com/Waversense/srt2speech/](https://github.com/Waversense/srt2speech/)

The readme contains the 5 steps needed to set it up, you can get started in 2 minutes.

 The included demo.srt file demonstrates the features.

More support for different AI, including whisper integration are planned updates.

 It will always stay lightweight and simple to install

Update:

 Here's the link to my original post, I'll post updates there:

[https://www.reddit.com/r/LocalTextToSpeech/comments/1vawikw/srt2speech_opensource_multilingual_srt_narration/](https://redlib.catsarch.com/r/LocalTextToSpeech/comments/1vawikw/srt2speech_opensource_multilingual_srt_narration/)

## [Other](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Other%22&restrict_sr=on)[I gave my on-device LLM 3% English data. It decided to be better at English than main language.](https://redlib.catsarch.com/r/LocalLLaMA/comments/1r42r9b/i_gave_my_ondevice_llm_3_english_data_it_decided/)

21  Upvotes

[![Image 12](https://redlib.catsarch.com/preview/pre/wo8sb8vi5cjg1.jpg?width=1856&format=pjpg&auto=webp&s=ffb852d59eec38cf022616fe150f55ca43f91c88)](https://redlib.catsarch.com/preview/pre/wo8sb8vi5cjg1.jpg?width=1856&format=pjpg&auto=webp&s=ffb852d59eec38cf022616fe150f55ca43f91c88)
I’ve been messing around with Gemma 3 270M lately, and I’ve run into the most hilarious reality check.

Since I’m based in Korea, I spent weeks obsessing over a fine-tuning dataset that was 97% Korean. I really tried to bake in every possible nuance and emotional expression. I threw in a tiny 3% of English data just so it wouldn’t be totally lost in translation—I honestly didn't expect much at all.

But here’s the twist: The Korean side—the part I actually put my blood, sweat, and tears into—is still a bit of a wild card and gives random or off-topic responses sometimes. Meanwhile, the 3% English data is pumping out relatively clean and coherent replies!

It’s pretty humbling (and a bit frustrating!) to see my "low-effort" English support behaving better than the language I actually focused on. I guess the base model’s pre-training is doing some heavy lifting here, but it definitely means I’ve still got some work to do on the Korean side!

Just for some context on the screenshot, I’m actually building an on-device diary app called Offgram. The idea is to have a locally running LLM act as a companion that leaves thoughtful (and hopefully not too random) comments on your daily entries so you don't feel like you're just writing into a void.

Since it's a diary, I'm a firm believer that privacy is non-negotiable, so everything runs 100% on-device—zero data ever leaves your phone. Using the tiny 270M model keeps things super snappy with basically no latency. It’s still under heavy development, but I’m planning to launch it soon!

Has anyone else working with these ultra-small models seen this kind of "language flip"? I’d love to hear your theories or any tips on how to keep these tiny models on track!

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[A Farmer Doesn’t Know Coding, But Tries to Build an Executing Engine with LLMs and a Code Interpreter](https://redlib.catsarch.com/r/LocalLLaMA/comments/1pwwd99/a_farmer_doesnt_know_coding_but_tries_to_build_an/)

21  Upvotes

Translated from Korean. I wrote the original in Korean and translated it myself. Final meaning and responsibility are mine.

I’m a garlic farmer in Korea. When I’m not working in the field, I use AI chat interfaces as my personal lab. I experiment with AIs that have sandboxed code interpreters, and I slowly build scripts that become a kind of “engine.” I don’t start from code. I start by talking to the AI, giving my thoughts and structural ideas first. Using the web tools inside the AI chat, I collect and structure information. Then I run that structured information again inside the code interpreter, and I only take the actual execution results and move forward with explainable analysis (XAI). Through this process, the concepts slowly grow, and step by step I give the AI more concrete direction. You can think of it like this: the LLM and the engine inside the sandboxed code interpreter form an indirect pipeline. User input → web tool search → LLM structures → that result is executed by the code interpreter. This is important for me: this is not an environment where I directly build pipelines with APIs. Everything happens inside the AI chat UI that I use every day. By the way, what I call a “sandboxed code interpreter” has different names depending on company or product (Code Interpreter, Data Analysis / Advanced Data Analysis, Code Execution, etc). But the core meaning is the same: An isolated execution environment where code actually runs inside the chat window (a sandboxed execution environment). And the “engine” I talk about is nothing fancy. It is just Python scripts running inside that sandbox (analysis scripts / verification scripts), and the execution-backed verification loop that repeats again and again.

The Question of Real Execution The biggest problem in this whole process is very simple: Is the code interpreter in the chat really executing, or not? If it is not actually executing, what comes out is close to hallucination — just simulated text with no real meaning. I have seen this many times: the output looks like execution results, but in reality nothing was executed at all. So the key question becomes only one thing for me: “Is this execution real right now?” In my case, I use reproducible code, like random-number-based checks, and make multiple AIs cross-check each other. Below is the overall flow I use, drawn in a very simple way:

[Me (input / thoughts)] | v [Web tool search (optional)] | v [LLM conversation / structuring] | v [Engine: sandboxed Python execution] | v [Execution output] | v [XAI / next direction] | v [Loop repeats]

The point I care about most is here: [Sandboxed Python execution] | +-- (execution is real) | -> reproducible output remains | -> becomes verifiable evidence | +-- (execution is fake) -> hallucinated / simulated text looks like “real output” -> high risk of wrong judgment

That is why I try to confirm, as much as possible, whether execution was real, by using reproducible code and cross-checking across multiple AIs. In the end, I feel that the ability to notice hallucination is also a kind of personal know-how. After many experiences, my conclusion is clear: With only one AI, it is almost impossible to get the result I want. You must cross-check between multiple AIs.

I want to say this clearly again: I am just a farmer. I only spend small pieces of time, working together with AIs like this. I don’t know if this method is “correct”, but sometimes meaningful results come out, so I keep using it. As time goes on, it feels more and more refined. Each AI has a different mechanism, so sometimes it is confusing. But I feel that the overall frame does work, especially when multiple AIs respond together in a consistent way. Because this is just a personal experiment, sometimes it makes my head hurt. But at the same time, I get many insights because of the AIs. Especially, I often feel that the diversity of AIs itself creates real effectiveness. What do you think about this way of working? I don’t really know how to code, but I learn by talking with AIs. Since multiple AIs give different opinions, I focus only on direction and intent, and let the AIs handle the experiments. Many times, this gives better results than I expected. When I watch code flowing down on my phone screen, it sometimes feels like watching the code scenes from the movie Matrix. And honestly, that part is fun by itself.

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[thinking about running Gemma4 E2B as a preprocessor before every Claude Code API call. anyone see obvious problems with this?](https://redlib.catsarch.com/r/LocalLLaMA/comments/1semwnm/thinking_about_running_gemma4_e2b_as_a/)

2  Upvotes

background: I write mostly in Korean and my Claude API bill is kind of embarrassing. Korean tokenizes really inefficiently compared to English for the same meaning, so a chunk of the cost is basically just encoding overhead.

the idea is a small proxy in Bun that sits in front of the Claude API. Claude Code talks to localhost, doesn't know anything changed. before each request goes out, Gemma4 E2B (llama.cpp, local) would do:

- translate Korean input to English. response still comes back in Korean, just the outbound prompt is English

- trim context that's probably not relevant to the current turn

- for requests that look like they need reasoning, have Gemma4 do the thinking first and pass the result along — so the paid model hopefully skips some of that work and uses fewer reasoning tokens

planning to cache with SQLite in WAL mode to avoid read/write contention on every request.

one thing I'm genuinely unsure about before I start building: does pre-supplying reasoning actually save anything, or does the model just redo it internally anyway and charge you for it regardless.

the bigger concern is speed. the whole point breaks down if Gemma4 adds more latency than it saves money. has anyone actually run Gemma4 E2B on an Intel Mac? curious what kind of tokens/sec you're getting with llama.cpp on that hardware specifically — Apple Silicon numbers are everywhere but Intel is harder to find

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[GPT-Sovits V3 TTS (407M) Release - 0-Shot Voice Cloning , Multi Language](https://redlib.catsarch.com/r/LocalLLaMA/comments/1jbyg29/gptsovits_v3_tts_407m_release_0shot_voice_cloning/)

180  Upvotes

[https://github.com/RVC-Boss/GPT-SoVITS/releases/tag/20250228v3](https://github.com/RVC-Boss/GPT-SoVITS/releases/tag/20250228v3)

Version 3 of GPT Sovits released two weeks ago and I havent really seen any discussion about it outside of China.

The new version increased the parameter count from 167m to 407m, also the voice cloning capability has improved a lot over the previous versions. Both 0 shot (uses a single audio sample shorter then 10 seconds) and trained voices are now a lot closer to the original and it is capable of staying in the emotion of the sample more consistently.

GPT Sovits supports English, Chinese, Japanese, Korean and Cantonese. From my personal testing it currently is the best option for 0 shot voice cloning in Japanese.

Here is a link to the machine translated changelog: [https://github-com.translate.goog/RVC-Boss/GPT-SoVITS/wiki/GPT‐SoVITS‐v3‐features-(新特性)?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=ja&_x_tr_pto=wapp](https://github-com.translate.goog/RVC-Boss/GPT-SoVITS/wiki/GPT%E2%80%90SoVITS%E2%80%90v3%E2%80%90features-(%E6%96%B0%E7%89%B9%E6%80%A7)?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=ja&_x_tr_pto=wapp)

Note: the audio examples on their Github page are still from V2 not V3. Also once you start the Gradio interface you need to select v3 from the dropdown menu as it defaults to v2 still.

## [Other](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Other%22&restrict_sr=on)[Z_Image benchmark with simulating VRAM Limits on RTX 5090 & 3090](https://redlib.catsarch.com/r/LocalLLaMA/comments/1p9563c/z_image_benchmark_with_simulating_vram_limits_on/)

17  Upvotes

Hi everyone,

I recently got my hands on an **RTX 5090 (32GB)** and also have an **RTX 3090 (24GB)**. I experimented to simulate the VRAM capacity of the upcoming 50-series lineup (5080, 5070, etc.) and older 30-series cards.

**The main goal** was to see what happens when VRAM runs out (OOM) and the system starts swapping to System RAM (DDR5). Specifically, I wanted to measure the performance penalty.

**⚠️ Disclaimer:** This test only limits **VRAM Capacity**. It does **NOT** simulate the raw compute power (CUDA cores) of lower-tier cards.

*   _e.g., The "Simulated 5060" result shows how a 5090 performs when choked by 8GB VRAM, not the actual speed of a real 5060._

## Test Environment

*   **GPU:** RTX 5090 (32GB) & RTX 3090 (24GB)
*   **CPU:** Ryzen 9 7900X
*   **RAM:** DDR5 96GB (6000MHz)
*   **PSU:** 1600W
*   **Model: Z_Image_Turbo**
*   **Software:** ComfyUI (**Provided Z_Image_Turbo Workflow** from its site/1024x1024 generation)
*   **OS:** Windows 11

## 1. RTX 3090 Results (Simulating 30-series VRAM tiers)

_Comparing Native 24GB vs. Artificial Limits_

| Simulated Tier | VRAM Limit | Cold Start (s) | Warm Gen (s) | System RAM (DRAM) Usage | Real VRAM Used |
| --- | --- | --- | --- | --- | --- |
| RTX 3090 (Native) | 24 GB | 19.07s | 9.71s | Negligible | 20 GB |
| 16GB Tier (4080/4070Ti S) | 16 GB | 20.84s | 10.43s | +11 GB | 13 GB |
| 3080 (12G) / 4070 Ti | 12 GB | 22.92s | 13.82s | +15 GB (Generation) | 11.1 GB |
| 3080 (10G) | 10 GB | 25.38s | 17.04s | +13 GB (Generation) | 9.1 GB |
| 3070 / 3060 Ti | 8 GB | 27.94s | **20.00s** | +15 GB (Generation) | 7.0 GB |

**Analysis:** Performance takes a noticeable hit as soon as you drop below 12GB. At 8GB, the generation time doubles compared to the native 24GB environment. However, thanks to the system RAM, it is still usable (didn't crash).

## 2. RTX 5090 Results (Simulating 50-series VRAM tiers)

_Comparing Native 32GB vs. Artificial Limits_

| Simulated Tier | VRAM Limit | Cold Start (s) | Warm Gen (s) | System RAM (DRAM) Usage | Real VRAM Used |
| --- | --- | --- | --- | --- | --- |
| RTX 5090 (Native) | 32 GB | 10.17s | 3.45s | Negligible | 22 GB |
| 4090 | 24 GB | 10.48s | 3.33s | Negligible | 21 GB |
| 5080/5070 ti | 16 GB | 11.93s | 4.20s | +12 GB | 15.8 GB |
| 5070 | 12 GB | 12.11s | 5.07s | +12.9 GB (Generation) | 12.9 GB |
| 5060 | 8 GB | 11.70s | 6.19s | +21 GB (Generation) | 7 GB |

**Analysis:** The 5090's raw power is insane. Even when limited to 8GB VRAM and forced to pull 21GB from System RAM, **it is still faster (6.19s) than a native 3090 (9.71s).**

_Note again: A real 5060 will be much slower due to fewer CUDA cores. This just proves the 5090's architectural dominance._

## Key Findings & Analysis

**1. The 5090 is a Monster** With unlimited VRAM, the 5090 is roughly **3x faster** than the 3090 in this workflow. The Blackwell chip is impressive.

**2. The VRAM Bottleneck & System RAM** Based on my data, when VRAM is insufficient (8GB~12GB range for SDXL), the system offloads about **20GB** of data to the System DRAM.

**3. Speed during Swapping** Both GPUs remained "usable" even when restricted to 8GB, as long as there was enough System RAM. Excluding the cold start, the generation speed was acceptable for local use.

*   _However, on the 3090, the slowdown is clearly felt (9s -> 20s)._
*   _On the 5090, the brute force computational power masks the swapping latency significantly._

**4. Oddity** Software VRAM limiting wasn't 100% precise in reporting, likely due to overhead or PyTorch memory management, but the trend is clear.

## TL;DR

1.   **Z_Image is efficient:** Great bang for the buck in terms of local generation.
2.   **RAM is King:** If you have **32GB+ of System RAM**, even an 8GB VRAM card can run these workflows (albeit slower). It won't crash, it just swaps.
3.   **For Speed:** If you want snappy generation without waiting, you probably want a **70-class or higher** card (12GB+ VRAM).
4.   **5090 Reaction:** It's insanely fast...

[![Image 13](https://redlib.catsarch.com/preview/pre/izgg24dj424g1.png?width=1024&format=png&auto=webp&s=b911124200bb5336cd1246efee6c539fff1be3b5)](https://redlib.catsarch.com/preview/pre/izgg24dj424g1.png?width=1024&format=png&auto=webp&s=b911124200bb5336cd1246efee6c539fff1be3b5)
_Test result example_

_This is the translated version of my writing in Korean_

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[Building a local multi-model OpenClaw assistant on Mac Studio M3 Ultra (96GB) for research, RAG, coding, and Korean↔English tasks — hardware sufficient? Best models? MLX? Fine-tuning?](https://redlib.catsarch.com/r/LocalLLaMA/comments/1r8x13i/building_a_local_multimodel_openclaw_assistant_on/)

1  Upvotes

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

## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[yanolja/YanoljaNEXT-Rosetta-12B-2510](https://redlib.catsarch.com/r/LocalLLaMA/comments/1o2bm3z/yanoljayanoljanextrosetta12b2510/)

37  Upvotes

We’ve just uploaded the **next version of YanoljaNEXT-Rosetta-12B**, a translation model that’s been **significantly improved** from the previous release.

🧠 **Available on Hugging Face:** 👉 [YanoljaNEXT-Rosetta-12B-2510](https://huggingface.co/yanolja/YanoljaNEXT-Rosetta-12B-2510)

Below is a summary generated by Claude about the model’s performance 👇

* * *

## **Key Results for YanoljaNEXT-Rosetta-12B-2510**

### 1. **Average Score on Targeted Languages: 54.45**

*   Evaluated on 31 targeted languages (+ English = 32 total)
*   Well above the model’s overall average of **44.73** across all 55 languages

### 2. **Ranking on Targeted Languages: #3 out of 8 systems**

**Full Rankings:**

1.   DeepL Translate — 55.41
2.   GPT-4o — 55.19
3.   **YanoljaNEXT-Rosetta-12B-2510 — 54.45** ⭐
4.   Google Translate — 54.05
5.   OpenAI o1 — 53.39
6.   Claude-3.5 — 53.19
7.   Microsoft Translator — 53.02
8.   Gemini-1.5-Pro — 52.67

🥉 **Only 0.96 points behind the leader!**

> _Note:_ The listed models (Claude 3.5 and Gemini 1.5) are those evaluated in the **WMT24++ paper**. In internal tests, results were largely consistent, though **Gemini 2.5 models** performed significantly better than 1.5—comparable to **GPT-4o**.

### 3. **#1 Rankings: 7 out of 31 languages (22.6%)**

**Top-performing languages:**

*   **Danish (da_DK)** — 65.88 (+2.88 vs GPT-4o)
*   **Gujarati (gu_IN)** — 51.83 (+2.03 vs Google)
*   **Korean (ko_KR)** — 37.10 (+0.10 vs DeepL)
*   **Persian (fa_IR)** — 53.95 (+0.95 vs GPT-4o)
*   **Romanian (ro_RO)** — 63.24 (+0.44 vs GPT-4o)
*   **Tagalog (fil_PH)** — 61.47 (+2.47 vs Google)
*   **Vietnamese (vi_VN)** — 56.96 (+2.56 vs GPT-4o)

**Additional Strengths:**

*   **#2 rankings:** 6 languages — French, Greek, Hebrew, Russian, Spanish, Ukrainian
*   **#3 rankings:** 6 languages — Arabic, Bulgarian, Czech, Hungarian, Italian, Swedish

* * *

⚡ Overall, the model shows **strong competitive performance**, especially in **Danish, Korean, and Southeast Asian languages (Vietnamese, Tagalog)** — closing the gap with industry leaders like DeepL and GPT-4o.

* * *

### **Evaluation Details**

*   **Framework & Precision:** Evaluation was conducted using **vLLM** with **BF16 precision**.
*   **Data Coverage:****99.9%** of samples were successfully evaluated, with approximately **0.01%** excluded due to a **repetition issue**.
*   **Decoding Settings:** Used **temperature = 0** and **repetition penalty = 1.05** for consistent and deterministic outputs.
*   **Metric:** Only **CHRF++** was measured for this evaluation.
*   **Dataset:** Evaluation used the **WMT24++ dataset**, which is primarily specialized for **English↔X** translations. However, the **YanoljaNEXT-Rosetta-12B-2510** model supports **X↔Y translations across all 32 languages**.
*   **Additional Note:****MetricX24** was also tested internally, but the results were excluded since the same scores reported in the **WMT24++ paper** could not be fully reproduced.
