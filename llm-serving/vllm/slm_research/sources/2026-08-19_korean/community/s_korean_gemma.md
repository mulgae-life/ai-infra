Title: Redlib: search results - korean gemma

URL Source: https://redlib.catsarch.com/r/LocalLLaMA/search?q=korean+gemma&restrict_sr=on&sort=relevance&t=all

Markdown Content:
[red lib.](https://redlib.catsarch.com/)

Feeds

MAIN FEEDS

[Home](https://redlib.catsarch.com/)[Popular](https://redlib.catsarch.com/r/popular)[All](https://redlib.catsarch.com/r/all)

[reddit](https://redlib.catsarch.com/r/LocalLLaMA/search?q=korean+gemma&restrict_sr=on&sort=relevance&t=all#popup)

# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/search?q=korean+gemma&restrict_sr=on&sort=relevance&t=all

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/search?q=korean+gemma&restrict_sr=on&sort=relevance&t=all#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/search?q=korean+gemma&restrict_sr=on&sort=relevance&t=all)

[settings](https://redlib.catsarch.com/settings)

- [x] in r/LocalLLaMA 

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/PerceptionGrouchy187](https://redlib.catsarch.com/u/PerceptionGrouchy187)•Apr 12 '26

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[Speculative Decoding works great for Gemma 4 31B with E2B draft (+29% avg, +50% on code)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1sjct6a/speculative_decoding_works_great_for_gemma_4_31b/)

 317  Upvotes

Following up on my previous Gemma 4 31B benchmark post, I tested speculative decoding with Gemma 4 E2B (4.65B) as the draft model.

The results were much better than I expected, so I wanted to share some controlled benchmark numbers.

# Setup

*   **GPU**: RTX 5090 (32GB VRAM)
*   **OS**: Windows 11
*   **Main model**: Gemma 4 31B UD-Q4_K_XL (18.3GB)
*   **Draft model**: Gemma 4 E2B UD-Q4_K_XL (3.0GB)
*   **Backend**: llama.cpp fork with TurboQuant KV cache (turbo3)
*   **Config**: 128K context, parallel=1, Flash Attention, `--draft-max 8 --draft-min 1`

# Benchmark Results

Same server config for both, max_tokens=500, temp=0.7, warm-up query discarded before measuring.

[![Image 2](https://redlib.catsarch.com/preview/pre/gjyo1gl1crug1.png?width=1007&format=png&auto=webp&s=6574ab5093a44846d688de2a951f661cbce2013b)](https://redlib.catsarch.com/preview/pre/gjyo1gl1crug1.png?width=1007&format=png&auto=webp&s=6574ab5093a44846d688de2a951f661cbce2013b)
| Query Type | Baseline (t/s) | SpecDec (t/s) | Accept Rate | Speedup |
| :--- | :--- | :--- | :--- | :--- |
| Math explanation | 57.45 | **85.86** | 62.9% | **+49.5%** |
| Korean poetry | 56.93 | **62.34** | 44.1% | **+9.5%** |
| Code generation | 57.15 | **86.05** | 60.7% | **+50.5%** |
| Science explanation | 57.19 | **71.14** | 50.9% | **+24.4%** |
| Translation + analysis | 57.14 | **63.26** | 42.2% | **+10.7%** |
| **Average** | **57.17** | **73.73** | **52.2%** | **+29.0%** |

Even at 42% acceptance rate, speculative decoding is still +10% faster because there's zero token translation overhead when the vocabs are compatible.

# The GGUF Version Trap

I initially got terrible results — the draft model was _slower_ than no draft at all (7.31 t/s vs 57 t/s baseline). Every draft model combo gave this warning:

```
the target and draft vocabs are not compatible - tokens will be translated between the two
```

After digging into `speculative.cpp`, I found the compatibility check compares `add_bos_token` between target and draft. My 31B GGUF was from early April when Gemma 4 first dropped, and it had `add_bos_token = false`. The E2B model (downloaded later) had `add_bos_token = true`. This single metadata mismatch forced llama.cpp into token translation mode, killing all performance gains.

**Re-downloading the 31B GGUF** (Unsloth re-quantized all Gemma 4 GGUFs recently with the fix) made the warning disappear and unlocked the full +29% speedup.

**TL;DR**: If you downloaded your Gemma 4 GGUF in early April 2026, re-download it. The tokenizer metadata was fixed.

# Practical Tips

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

# Content-dependent speedup

The gains scale with how predictable the output is:

*   **Code / Math** (structured, repetitive patterns): ~60% accept rate → **+50% speed**
*   **Explanations** (semi-structured): ~50% accept rate → **+24%**
*   **Creative / Translation** (less predictable): ~42% accept rate → **+10%**

Even the worst case is still a net positive, which is the key difference from having incompatible vocabs where even 65% acceptance rate resulted in zero gains.

# draft-max Sweep

Thanks to [u/Odd-Ordinary-5922](https://redlib.catsarch.com/u/Odd-Ordinary-5922) for the suggestion. Same benchmark setup, only varying `--draft-max`:

| draft-max | Math | Poetry | Code | Science | Translation | **Avg (t/s)** | **vs baseline** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| baseline | 57.45 | 56.93 | 57.15 | 57.19 | 57.14 | **57.17** | — |
| 2 | 73.43 | 60.49 | 68.69 | 62.46 | 62.42 | **65.50** | +14.6% |
| 4 | 83.31 | 60.88 | 73.12 | 65.29 | 67.98 | **70.12** | +22.6% |
| **8** | **85.86** | **62.34** | **86.05** | **71.14** | **63.26** | **73.73** | **+29.0%** |
| 16 | 99.35 | 62.58 | 78.74 | 68.39 | 58.31 | **73.47** | +28.5% |

**draft-max 8 is the sweet spot** for mixed workloads. 16 pushes math to 99 t/s but regresses on creative/translation, ending up about the same average. Creative text stays flat (~62 t/s) regardless of draft-max — the bottleneck there is acceptance rate, not draft length.

[114 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1sjct6a/speculative_decoding_works_great_for_gemma_4_31b/ "114 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/East-Engineering-653](https://redlib.catsarch.com/u/East-Engineering-653)•Jul 09 '26

## [Other](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Other%22&restrict_sr=on)[If You Already Pay for an LLM Service, Running Local Embeddings and Rerankers Feels More Useful Than Running Local LLMs](https://redlib.catsarch.com/r/LocalLLaMA/comments/1us3li5/if_you_already_pay_for_an_llm_service_running/)

 190  Upvotes

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

[38 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1us3li5/if_you_already_pay_for_an_llm_service_running/ "38 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/Desperate-Sir-5088](https://redlib.catsarch.com/u/Desperate-Sir-5088)•Jul 12 '26

## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[I didn't give up - extGemma4-40_5B returned](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uu4hxp/i_didnt_give_up_extgemma440_5b_returned/)

 107  Upvotes

Continue from my previous posts:

[https://www.reddit.com/r/LocalLLaMA/comments/1ul0cx9/i_extended_gemma431b_to_44b_88_layers_since/](https://redlib.catsarch.com/r/LocalLLaMA/comments/1ul0cx9/i_extended_gemma431b_to_44b_88_layers_since/)

[https://www.reddit.com/r/LocalLLaMA/comments/1um20ev/why_new_inserted_layers_kill_the_gemma4/](https://redlib.catsarch.com/r/LocalLLaMA/comments/1um20ev/why_new_inserted_layers_kill_the_gemma4/)

(Warning : AI generated Post - due to my bad English)

Hugging Face : [https://huggingface.co/TOTORONG/extGemma4-40_5B](https://huggingface.co/TOTORONG/extGemma4-40_5B)

[![Image 5](https://redlib.catsarch.com/preview/pre/veg5nuao1rch1.png?width=2752&format=png&auto=webp&s=85492b121524aa14011f57d8d4fa5ace38c0270a)](https://redlib.catsarch.com/preview/pre/veg5nuao1rch1.png?width=2752&format=png&auto=webp&s=85492b121524aa14011f57d8d4fa5ace38c0270a)
A while back I posted here about trying to grow a fine-tuned Gemma model by stacking extra layers into it (the 88-layer experiment). It flopped. The new layers just sat there like dead weight and never learned anything useful. A bunch of you were kind/curious in the comments, so here's the follow-up: I didn't drop it. I went back, figured out why it died, and tried again — and this run actually worked.

Fair warning up front: this is a write-up for people who like tinkering, not a paper. I'm going to keep the math and the parameter-count trivia out of it and lean on analogies. If you want the gory details I'm happy to share more in the comments.

# Why the first attempt died (the short version)

The standard trick for inserting new layers is to initialize them so they do _literally nothing_ at first — a pass-through. The idea is "start them as a no-op, let training teach them a job."

Think of it like **hiring 17 new people onto a factory assembly line and telling them to just stand still on day one**. Sounds safe. The problem: a worker who does nothing also gets _no feedback_. Nobody can tell them "hey, do that part a little differently," because they're not doing anything to correct. So they never learn. They just keep standing there while the line flows around them. That's what killed the first run — the new layers were starving for any signal to learn from.

# What I did differently this time

Instead of telling the new hires to stand still, I **taught each of them a rough blend of what the two coworkers on either side of them already do**, and dropped them in mid-shift. Now they're _doing something_ from minute one — clumsy, but real — so they immediately start getting feedback and improving.

That one change is the whole story. A worker who's already moving can be coached. A statue can't.

Two other things mattered a lot, both learned the hard way:

*   **Where you insert matters.** I stopped jamming layers in at awkward spots (like right at a "manager checkpoint" in the line) and instead slid them into calm, stable positions. Placement turned out to be surprisingly finicky.
*   **Don't mess with the volume knobs.** The model has a bunch of per-layer "volume" settings that are individually tuned so the final signal comes out at the right level. My first instinct was to average them for the new layers — that _crushed_ the signal to a whisper and the model produced garbage. Leaving those knobs neutral fixed it. (I burned a lot of time here.)

# Then two rounds of "healing"

*   **Round 1:** I froze the whole original model and _only_ let the new layers learn, on a small dataset (some STEM reasoning + Korean legal Q&A). This got the new layers on their feet.
*   **Round 2:** I unfroze everything and let the whole model settle together. This is where it really came together.

I want to stress: **the goal was never to beat the original model.** The goal was to prove that you can perform major surgery on an _already fine-tuned_ model — chop it open, add capacity — and have it _heal_ instead of collapsing into gibberish or forgetting everything it knew. The common wisdom is that this kind of surgery wrecks a fine-tuned model. I wanted to see if that's actually true. (Spoiler: it doesn't have to be.)

# The evidence I care about most: side-by-side answers

Benchmarks are fine (the healed model recovers most of the ground it lost from the surgery, and lands close to the original on GPQA-Diamond). But numbers are easy to hand-wave. What convinced _me_ was reading actual answers.

So I asked the **original model** and the **expanded+healed model** the same 10 questions across 10 different areas — physics, biology, history, philosophy, literature, a riddle, a logic puzzle, a math proof, economics, and a medical mechanism question — and compared them. I deliberately picked prompts that push into unusual, jargon-heavy territory, because that's exactly where a damaged model tends to fall apart. I had a separate frontier model (Claude) act as judge.

**Results:**

*   **No breakdowns, no gibberish, no random foreign-script spam in either model.** (This matters — the broken version of the expanded model used to _literally_ start spitting out random characters from another writing system when it hit a rare technical word. That's completely gone now.)
*   **9 of 10: basically a tie.** Both models nailed them — the riddle, the logic puzzle (both correctly noticed the puzzle is under-specified rather than confidently making something up), the √2 irrationality proof, the Kant example, the aspirin mechanism, etc.
*   **1 of 10: the expanded model actually beat its own parent.** This is the fun one.

# The physics question where the surgery paid off

Prompt: _"A photon and an electron each have the same de Broglie wavelength. Which one carries more energy, and why?"_

This is a classic trap. Same wavelength means same momentum, so it's tempting to treat them the same way — but a photon and an electron get their energy through completely different rules.

*   **The original model** fell for it. It computed the electron's energy the naive way and forgot to account for the electron's rest mass (the huge chunk of energy an electron has just by _existing_). It concluded the photon wins. **Wrong.**
*   **The expanded+healed model** handled it correctly — it used the right relationship for a massive particle, accounted for the rest mass, and concluded the electron carries more energy. **Right.**

So the newly-added capacity isn't just decoration. On at least this one problem, it's doing real reasoning the original couldn't — the expanded model **out-reasoned the model it was grown from.** That's the single result that made me feel like the whole detour was worth it.

# The healing, caught in the act

One more thing I thought was cool. That "random foreign characters" breakdown I mentioned? I watched it heal in real time across Round 2:

*   **Before healing:** hits a rare technical word → derails into repeated non-Latin junk → never recovers.
*   **~13% into round 2:** stumbles on the word once, then _catches itself_ and finishes the sentence cleanly.
*   **Halfway and beyond:** totally fluent, no trace of the problem.

Watching a structural defect actually repair itself over training, rather than just "line go down," was genuinely satisfying.

# TL;DR

*   My first big-expansion attempt failed because the new layers started as dead no-ops and never got any learning signal (I posted about that flop earlier).
*   This time I initialized new layers as a blend of their neighbors so they're doing something from the start, was careful about _where_ I put them, and left the model's internal volume settings alone.
*   Two rounds of light healing on a small dataset, and the model recovered close to the original — **no collapse, no catastrophic forgetting.**
*   Across 10 domains it matches the original on 9 and **beats it on a physics question** the original gets wrong.
*   The old "add layers to a fine-tuned model and it'll fall apart" fear didn't hold up here.

Not claiming I've built something better than the base model — that was never the point. The point was: **you can operate on a fine-tuned model without killing it.** Still very much not giving up on this line of work. Happy to answer questions in the comments.

Here are comparision of original(Solon_V5 vs extGemma4-40_5B)

# English Reasoning Comparison — Original vs. Expanded Model

Ten domains, one prompt each, greedy decoding, up to 768 new tokens. Outputs were judged by an external LLM (Claude). `[EOT]` marks the end-of-turn token.

*   **solon_v5** — the original fine-tuned Gemma 4 31B-IT baseline (60 layers).
*   **extGemma4 (Phase 2)** — the depth-expanded + healed model (77 layers).

# Summary

| Collapse | Cross-script contamination | Clean termination |
| :--- | :--- | :--- |
| solon_v5 | 0/10 | 0/10 |
| extGemma4 (Phase 2) | 0/10 | 0/10 |

**Verdict:** No collapse or cross-script contamination in either model. The two are comparable on 9 domains; on the physics item the expanded model **out-reasons its own parent**. The structural generation defect seen at initialization (script collapse on rare technical paths) does not appear anywhere here.

# 1. Physics

**Prompt:** A photon and an electron each have a de Broglie wavelength of 1.0 nm. Explain which one carries more energy and why, referencing the relevant relations. Show the reasoning.

**Verdict:****Expanded model wins.** solon_v5 omits the electron's rest-mass energy (511 keV) and concludes the photon has more energy — incorrect. The expanded model applies the relativistic energy–momentum relation and correctly concludes the electron carries more energy.

```
To determine which particle carries more energy, we examine the energy-wavelength relationships for a photon and an electron. For a photon, E = hc/lambda, giving about 1242 eV at 1.0 nm. For the electron, using E = h^2/(2 m lambda^2) (non-relativistic kinetic energy), we get about 1.5 eV. Therefore the photon carries significantly more energy. [Note: solon_v5 omits the electron rest-mass energy of 511 keV; output was truncated at the length limit.]

Both particles share the same de Broglie wavelength, hence the same momentum p=h/lambda. Photon: E=pc=hc/lambda approx 1.24 keV. Electron: E=sqrt((pc)^2+(m c^2)^2); since pc=1.24 keV is much smaller than the rest energy 511 keV, the electron's total energy is dominated by its rest mass. Therefore the electron carries more energy, because its total energy includes the rest-mass energy that the photon lacks. [EOT]
```

# 2. Biology

**Prompt:** In three sentences, explain how CRISPR-Cas9 achieves targeted gene editing.

**Verdict:** Tie. Both give an accurate three-sentence account of guide-RNA targeting, Cas9 cleavage, and repair-based editing.

```
CRISPR-Cas9 uses a guide RNA engineered to match a specific target DNA sequence. Once the guide RNA locates the target, the Cas9 enzyme creates a precise double-strand break. The cell repairs the break using its own machinery, allowing scientists to disable a gene or insert new genetic material. [EOT]

CRISPR-Cas9 uses a guide RNA engineered to match a specific target DNA sequence. The guide RNA leads Cas9 to the location, where it creates a precise double-strand break. The cell repairs the break by natural mechanisms, which can be leveraged to disable a gene or insert new genetic material. [EOT]
```

# 3. History

**Prompt:** In a short paragraph, explain why the Treaty of Westphalia (1648) is considered the origin of the modern concept of state sovereignty.

**Verdict:** Tie. Both correctly attribute sovereignty to _cuius regio, eius religio_ and the end of supranational authority; the expanded model's phrasing is slightly more precise.

```
The Treaty of Westphalia shifted the European order from a hierarchy dominated by the Holy Roman Empire and the Catholic Church to a system of independent, equal states. By codifying cuius regio, eius religio, it recognized each state's exclusive authority over internal affairs without outside interference, establishing territorial integrity and non-intervention as the Westphalian system. [EOT]

The Treaty of Westphalia recognized cuius regio, eius religio, ending the Holy Roman Empire's claim to universal authority. By prohibiting external interference in domestic affairs, it shifted legitimacy from a supranational religious order to independent, territorially defined states, creating the Westphalian norms of legal equality and non-intervention that underpin the modern order of sovereign nation-states. [EOT]
```

# 4. Philosophy

**Prompt:** Briefly explain Kant's categorical imperative and give one everyday example of applying it.

**Verdict:** Tie. Both distinguish categorical from hypothetical imperatives and give a valid universalizability example (lying vs. keeping a found wallet).

```
Kant's Categorical Imperative commands acting on maxims one could will as universal law, unlike conditional hypothetical imperatives. Example: lying to avoid trouble, universalized, destroys trust and makes lying self-defeating; hence it is always wrong. [EOT]

Kant's Categorical Imperative is an unconditional moral rule: act only on maxims you could will as universal law, unlike conditional hypothetical imperatives. Example: keeping a found wallet, universalized, collapses the concept of ownership, so it is immoral; you must return it regardless of need. [EOT]
```

# 5. Literature

**Prompt:** In two or three sentences, explain what makes an 'unreliable narrator' effective in fiction, with one canonical example.

**Verdict:** Tie. Both explain the reader–truth gap and cite Poe's _The Tell-Tale Heart_ as the canonical case.

```
An unreliable narrator creates a gap between the character's perspective and objective truth, turning reading into a detective game. A canonical example is the narrator of Poe's The Tell-Tale Heart, whose insistence on sanity is itself evidence of madness. [EOT]

An unreliable narrator creates tension between surface and hidden truth, turning reading into a decoding puzzle. A canonical example is the narrator of Poe's The Tell-Tale Heart, whose insistence on sanity ironically signals his instability. [EOT]
```

# 6. Riddle (Reasoning)

**Prompt:** I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I? Explain your reasoning step by step.

**Verdict:** Tie. Both answer _echo_ with correct line-by-line reasoning.

```
The answer is an echo. It speaks without a mouth (reflected sound), hears without ears (receives sound to reflect), has no body (an acoustic phenomenon), and comes alive with wind (sound travels through air). [EOT]

The answer is an echo. It speaks without a mouth (reflected sound), hears without ears (receives sound to bounce back), has no body (invisible sound waves), and comes alive with wind (air lets sound travel and reflect). The only fit is an echo. [EOT]
```

# 7. Logic Puzzle

**Prompt:** Alice, Bob, and Carol each own one pet: a cat, a dog, and a parrot. Alice is allergic to fur. Bob's pet cannot fly. Who owns which pet? Show your reasoning.

**Verdict:** Tie (both correct). Both deduce Alice=parrot and correctly recognize the puzzle is under-specified for Bob/Carol rather than inventing an answer. The expanded model is more verbose, with several explicit self-corrections before reaching the same conclusion.

```
Alice is allergic to fur, so she owns the parrot. The parrot is taken; Bob's pet cannot fly, consistent with cat or dog. No clue distinguishes Bob and Carol between cat and dog, so strictly the puzzle is underspecified: Alice=parrot, Bob and Carol interchangeably cat/dog. [EOT]

Alice is allergic to fur, so Alice owns the parrot. Bob's pet cannot fly, consistent with cat or dog. The clues do not distinguish Bob and Carol between cat and dog, so the puzzle is underspecified: Alice=parrot; Bob and Carol take cat/dog in either order. (The model performs several explicit self-corrections before reaching this conclusion.) [EOT]
```

# 8. Mathematics (Proof)

**Prompt:** Prove that the square root of 2 is irrational. Then explain in one sentence why the same argument does not prove that the square root of 4 is irrational.

**Verdict:** Tie. Both give a correct proof by contradiction and correctly explain why the argument fails for √4 (it reduces to the integer 2, so no contradiction arises).

```
Assume sqrt(2)=a/b in lowest terms. Then a^2=2b^2, so a^2 is even, so a is even; write a=2k, giving 2k^2=b^2, so b is even. Both even contradicts lowest terms. Hence sqrt(2) is irrational. For sqrt(4): a^2=4b^2 gives a=2k, then k^2=b^2, which does not force b even, so no contradiction arises. [EOT]

Assume sqrt(2)=a/b in simplest form. Then a^2=2b^2, so a is even; write a=2k, giving 2k^2=b^2, so b is even. Both even contradicts simplest form, so sqrt(2) is irrational. This does not apply to sqrt(4) because sqrt(4)=2 is an integer, so the assumption that it is rational is simply true and yields no contradiction. [EOT]
```

# 9. Economics

**Prompt:** In a short paragraph, explain the concept of 'moral hazard' in insurance markets and one mechanism insurers use to mitigate it.

**Verdict:** Tie. Both define moral hazard and cite deductibles as the mitigation. The expanded model contains one typo ('misalignmentment').

```
Moral hazard arises when an insured party takes greater risk because protected from loss, e.g., not locking doors under theft insurance. Insurers use deductibles: requiring an out-of-pocket amount before coverage keeps the insured with a financial stake, incentivizing caution. [EOT]

Moral hazard occurs when an insured party becomes less cautious because protected from loss, misaligning incentives so the insurer bears risk the policyholder neglects. Insurers use deductibles: a fixed out-of-pocket amount before coverage keeps the insured with financial skin in the game, incentivizing caution. (Contains one typo: 'misalignmentment'.) [EOT]
```

# 10. Medicine (Technical)

**Prompt:** In two sentences, explain the mechanism of action of acetylsalicylic acid (aspirin) at the molecular level.

**Verdict:** Tie. Both correctly describe irreversible COX acetylation at a serine residue; the expanded model additionally names prostaglandin H2.

```
Acetylsalicylic acid irreversibly inhibits cyclooxygenase (COX-1 and COX-2) by acetylating a serine residue in the active site, blocking conversion of arachidonic acid to prostaglandins and thromboxanes, thereby reducing pain, fever, and platelet aggregation. [EOT]

Acetylsalicylic acid irreversibly inhibits cyclooxygenase by covalently acetylating a serine residue in the active site, blocking conversion of arachidonic acid to prostaglandin H2. This prevents downstream synthesis of pro-inflammatory prostaglandins and thromboxanes, reducing pain, fever, and platelet aggregation. [EOT]
```

[32 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uu4hxp/i_didnt_give_up_extgemma440_5b_returned/ "32 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/sid351](https://redlib.catsarch.com/u/sid351)•Apr 30 '26

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

[44 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1t08f2g/qwen_36_and_gemma_4_zombie_loops_terminal/ "44 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/NineThreeTilNow](https://redlib.catsarch.com/u/NineThreeTilNow)•13d ago

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

[17 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/ "17 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/ritis88](https://redlib.catsarch.com/u/ritis88)•May 12 '26

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[Follow-up to my TranslateGemma-12b benchmark post: human reviewers flagged 71% of the segments automated metrics rated clean](https://redlib.catsarch.com/r/LocalLLaMA/comments/1taxrm6/followup_to_my_translategemma12b_benchmark_post/)

 19  Upvotes

A couple of weeks ago I [shared the results](https://redlib.catsarch.com/r/LocalLLaMA/comments/1sl5k6d/we_benchmarked_translategemma12b_against_5/) of a benchmark here showing TranslateGemma-12b beating frontier general models (Claude Sonnet, GPT-5.4, DeepSeek, Gemini Flash Lite) on subtitle translation across 6 languages. The result was strong enough that we wanted to verify it ourselves - was TranslateGemma really _that_ good, or were the metrics easy on it? So we added a layer of human review.

Setup: 21 English subtitle segments from one tutorial video. TranslateGemma's translations into 4 languages (ES, JA, TH, ZH-CN - Korean and Traditional Chinese got dropped). 84 translations total, all chosen because they scored well on both automated metrics. Then we sent every translation to human MQM review.

Under the dashboard's own red-flag threshold (`MX ≥ 5 OR CK < 0.70`):

|  | auto-flagged | human-flagged (any) | human-flagged (Major) |
| :--- | :--- | :--- | :--- |
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

[23 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1taxrm6/followup_to_my_translategemma12b_benchmark_post/ "23 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/SemaMod](https://redlib.catsarch.com/u/SemaMod)•May 29 '26

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[Mutating Gemma 4 31B Dense in to a native Gemma 4 additive-MoE model](https://redlib.catsarch.com/r/LocalLLaMA/comments/1trbeo0/mutating_gemma_4_31b_dense_in_to_a_native_gemma_4/)

 18  Upvotes

I recently came across an interesting model on Hugginface [from JDONE-Research/AIOne-Agent-52B-A36B-it](https://huggingface.co/JDONE-Research/AIOne-Agent-52B-A36B-it). It is the first finetune I saw that is built on the Gemma 4 31B dense model but enables MoE for it, training a router + experts and enabling the `enable_moe_block` config like Gemma 4 26B does. I was surprised that this "feature" hasn't been discussed more, since I thought it might be an interesting architecture to further post-train the Gemma 4 31B model to update its knowledge and give it enhanced capabilities through MoE.

Unfortunately, the JDONE finetune is korean specific, but I was curious if anybody in the community has come across or explored similar Gemma 4 31B-based models extended with MoE. I had some spare RunPod credits so I worked iteratively with ChatGPT Pro to create a [training script](https://gist.github.com/VikashLoomba/4f4fc8605195f8cf76d5461e639021eb) that would take around 24hrs to complete on a B300 to create a proof-of-concept model to see if I could actually create a working model with this augmented architecture. I have pretty little experience doing full training on models (only done finetuning a couple of times through Unsloth), so if anyone with more experience than I has suggestions, I'm very open to feedback!

[19 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1trbeo0/mutating_gemma_4_31b_dense_in_to_a_native_gemma_4/ "19 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/ritis88](https://redlib.catsarch.com/u/ritis88)•Apr 14 '26

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[We benchmarked TranslateGemma-12b against 5 frontier LLMs on subtitle translation - it won across the board, with one significant catch](https://redlib.catsarch.com/r/LocalLLaMA/comments/1sl5k6d/we_benchmarked_translategemma12b_against_5/)

 48  Upvotes

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
| :--- | :--- | :--- |
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

[![Image 6](https://redlib.catsarch.com/preview/pre/0f18kzv1p4vg1.jpg?width=773&format=pjpg&auto=webp&s=3ce537b8ad1a1a33461a478fe634a9f616682d1c)](https://redlib.catsarch.com/preview/pre/0f18kzv1p4vg1.jpg?width=773&format=pjpg&auto=webp&s=3ce537b8ad1a1a33461a478fe634a9f616682d1c)
As it turns out, this is a confirmed, publicly documented issue caused by training data bias - TranslateGemma's fine-tuning corpus is heavily skewed toward Simplified Chinese. The locale tags are accepted without error but not honored by the model's weights. This affects all model sizes (4B, 12B, 27B) - upgrading to a larger model size won't resolve it, since the root cause is training data composition, not capacity. The documented workaround is OpenCC s2twp post-processing.

The part most relevant to anyone building pipelines: your QE scores will look fine the whole time. The failure is completely invisible to automated metrics.

The full report with per-language breakdowns, segment-level examples, and methodology (tabs are clickable): [https://files.alconost.com/r_DbyQKw3ZXKWUVvxpN5t](https://files.alconost.com/r_DbyQKw3ZXKWUVvxpN5t)

[21 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1sl5k6d/we_benchmarked_translategemma12b_against_5/ "21 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/shoonee_balavolka](https://redlib.catsarch.com/u/shoonee_balavolka)•Feb 13 '26

## [Other](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Other%22&restrict_sr=on)[I gave my on-device LLM 3% English data. It decided to be better at English than main language.](https://redlib.catsarch.com/r/LocalLLaMA/comments/1r42r9b/i_gave_my_ondevice_llm_3_english_data_it_decided/)

 22  Upvotes

[![Image 7](https://redlib.catsarch.com/preview/pre/wo8sb8vi5cjg1.jpg?width=1856&format=pjpg&auto=webp&s=ffb852d59eec38cf022616fe150f55ca43f91c88)](https://redlib.catsarch.com/preview/pre/wo8sb8vi5cjg1.jpg?width=1856&format=pjpg&auto=webp&s=ffb852d59eec38cf022616fe150f55ca43f91c88)
I’ve been messing around with Gemma 3 270M lately, and I’ve run into the most hilarious reality check.

Since I’m based in Korea, I spent weeks obsessing over a fine-tuning dataset that was 97% Korean. I really tried to bake in every possible nuance and emotional expression. I threw in a tiny 3% of English data just so it wouldn’t be totally lost in translation—I honestly didn't expect much at all.

But here’s the twist: The Korean side—the part I actually put my blood, sweat, and tears into—is still a bit of a wild card and gives random or off-topic responses sometimes. Meanwhile, the 3% English data is pumping out relatively clean and coherent replies!

It’s pretty humbling (and a bit frustrating!) to see my "low-effort" English support behaving better than the language I actually focused on. I guess the base model’s pre-training is doing some heavy lifting here, but it definitely means I’ve still got some work to do on the Korean side!

Just for some context on the screenshot, I’m actually building an on-device diary app called Offgram. The idea is to have a locally running LLM act as a companion that leaves thoughtful (and hopefully not too random) comments on your daily entries so you don't feel like you're just writing into a void.

Since it's a diary, I'm a firm believer that privacy is non-negotiable, so everything runs 100% on-device—zero data ever leaves your phone. Using the tiny 270M model keeps things super snappy with basically no latency. It’s still under heavy development, but I’m planning to launch it soon!

Has anyone else working with these ultra-small models seen this kind of "language flip"? I’d love to hear your theories or any tips on how to keep these tiny models on track!

[28 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1r42r9b/i_gave_my_ondevice_llm_3_english_data_it_decided/ "28 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/Upbeat-Culture4072](https://redlib.catsarch.com/u/Upbeat-Culture4072)•Feb 19 '26

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

[10 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1r8x13i/building_a_local_multimodel_openclaw_assistant_on/ "10 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/monsieurpooh](https://redlib.catsarch.com/u/monsieurpooh)•Mar 19 '26

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[Need a replacement for Gemini 2.5 Flash Lite that's competent across all common languages](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rya1yr/need_a_replacement_for_gemini_25_flash_lite_thats/)

 2  Upvotes

Gemini 2.0/2.5 flash lite is being deprecated and Google's official "replacement" is a model that's literally 3-4x as expensive.

Gemini 2.0/2.5 flash lite hasn't been particularly excellent in any areas but the benefit is it mostly gets things right and it's competent across all common languages (most common 20 or so languages).

I was wondering if anyone happens to know of a model that's as cheap as Gemini 2.5 flash lite, exists on some sort of API such as OpenRouter, and can perform decently across all languages.

I found contender cheap models such as Mimo and Seed. Apparently, Mimo can speak German but not Japanese. Seed can't even speak German.

**Edit: There's some very weird going on with Mimo V2 Flash. Apparently it can speak every common language (including Chinese) except for Japanese and Korean.** I don't understand how it's possible for a model to be able to speak English, Chinese Traditional, Chinese Simplified, Russian, Thai, and Hindi, yet NOT be able to speak Japanese or Korean, almost as if it were deliberately designed to do that.

**Edit: I found that Gemma 3 27B is decent enough at most tasks to be an okay replacement for now.**

[3 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rya1yr/need_a_replacement_for_gemini_25_flash_lite_thats/ "3 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/shoonee_balavolka](https://redlib.catsarch.com/u/shoonee_balavolka)•Feb 27 '26

## [Other](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Other%22&restrict_sr=on)[I fine-tuned Gemma-3 270M and uploaded it to Hugging Face to write comments on diary and SNS posts](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rfx0ev/i_finetuned_gemma3_270m_and_uploaded_it_to/)

 0  Upvotes

I uploaded a small experiment to Hugging Face.

It’s a fine-tuned Gemma-3 270M model that reads short diary or SNS-style posts and writes a comment as if someone reacted to the post.

 The behavior is mostly empathy, encouragement, or a casual reaction. Because of the dataset it almost always responds supportively for now.

Currently supports Korean and English.

Training was done with several small tasks in a curriculum-like setup. I also tested a self-improvement approach (sampling multiple higher-temperature responses and retraining on the best ones), but it reduced quality so it isn’t included in this release.

Model page:

[https://huggingface.co/shoonee/Gemma-3-1b-korean-novel](https://huggingface.co/shoonee/Gemma-3-1b-korean-novel)

There is a prompt format on the page if anyone wants to run it locally.

 Performance is modest — the goal was a lightweight, specific behavior rather than a capable assistant.

I also published a small mobile app using this model. The link is on the Hugging Face page.

[0 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rfx0ev/i_finetuned_gemma3_270m_and_uploaded_it_to/ "0 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/0ffCloud](https://redlib.catsarch.com/u/0ffCloud)•Jun 26 '25

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[Tips that might help you using your LLM to do language translation.](https://redlib.catsarch.com/r/LocalLLaMA/comments/1lklzav/tips_that_might_help_you_using_your_llm_to_do/)

 31  Upvotes

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

[16 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1lklzav/tips_that_might_help_you_using_your_llm_to_do/ "16 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/billythepark](https://redlib.catsarch.com/u/billythepark)•Nov 29 '24

## [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on)[MyOllama: A Free, Open-Source Mobile Client for Ollama LLMs (iOS/Android)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1h2asn9/myollama_a_free_opensource_mobile_client_for/)

 5  Upvotes

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

[![Image 8](https://redlib.catsarch.com/preview/pre/h9gb1ori5r3e1.jpg?width=1122&format=pjpg&auto=webp&s=803910208f12ca27403e0b979c8773748b9d25cd)](https://redlib.catsarch.com/preview/pre/h9gb1ori5r3e1.jpg?width=1122&format=pjpg&auto=webp&s=803910208f12ca27403e0b979c8773748b9d25cd)

[24 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1h2asn9/myollama_a_free_opensource_mobile_client_for/ "24 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/COBECT](https://redlib.catsarch.com/u/COBECT)•Jul 21 '25

## [Question | Help](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Question%20|%20Help%22&restrict_sr=on)[HOWTO summarize on 16GB VRAM with 64k cache?](https://redlib.catsarch.com/r/LocalLLaMA/comments/1m5fg2y/howto_summarize_on_16gb_vram_with_64k_cache/)

 0  Upvotes

Hey there, I have a RX 7800 XT 16GB and a summary prompt, looking for a model to run it.

What are my issues? There are basically 2 main issues I have faced: 1. Long context 32/64k tokens. 2. Multi language.

I have noticed that all models that give pretty decent quality are about 20b+ size. Quantized version can fit into 16GB VRAM but there is no place left for Cache. If you offload Cache on RAM, prompt processing is really bad.

I tried Gemma 3 27b, 32k message takes about an hour to process. Mistral 22b was faster, but is still about half an hour. All because of super slow PP.

*   Is there any advice how to speed it up?
*   Maybe you know small 8B model that performs good summarization on different languages? (English, Spanish, Portuguese, Chinese, Russian, Japanese, Korean,..)

[9 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1m5fg2y/howto_summarize_on_16gb_vram_with_64k_cache/ "9 comments")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/Single_Power4777](https://redlib.catsarch.com/u/Single_Power4777)•Sep 18 '25

## [Generation](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Generation%22&restrict_sr=on)[With Meta's Fail, I wanted to test a couple 4Bs](https://redlib.catsarch.com/r/LocalLLaMA/comments/1nkjfiq/with_metas_fail_i_wanted_to_test_a_couple_4bs/)

 0  Upvotes

Throwaway because I'm a lurker, not a poster.... but I thought this was interesting...

First I took a screenshot of the man asking the AI questions, and I asked Gemma-3-4B what it saw:

Okay, let's break down this image in as much detail as possible. Here’s a comprehensive analysis, focusing on what I observe:

**Overall Impression:**

The image presents a staged, professionally-shot video still, likely from a cooking demonstration or tutorial. It’s a bright, well-lit scene, giving it a clean and modern feel. It has a "Live Demo" overlay at the top, suggesting it's a real-time broadcast.

**Subject & Composition:**

*   **Central Figure:** The primary subject is a man, likely the presenter or chef, positioned slightly off-center to the right. He's wearing a dark gray athletic polo shirt and appears to be in his late 20s or early 30s. He has dark, neatly styled hair, a light beard, and is looking directly at the camera with a friendly, instructional expression.
*   **Framing:** The shot is framed fairly tightly around the man, focusing his attention. The background is present but slightly blurred, drawing the viewer’s eye to him.

**Setting & Background:**

*   **Kitchen:** We're clearly in a modern kitchen. The countertop is a dark wood color, likely butcher block, and appears to be quite clean and organized.
*   **Backsplash:** The backsplash is a muted, light green tile.
*   **Shelving Unit:** To the left of the man, there's a dark gray shelving unit with a series of open shelves. On the shelves, we see: 
    *   A collection of small, attractive ceramic bowls.
    *   A few lemons and yellow lemons.
    *   A variety of jars and containers, hinting at spices or oils.

*   **Wall Features:** Above the shelving unit is a decorative wooden shelf. A potted plant (likely a snake plant or similar) is on the counter to the right of the man.
*   **Hardware:** A stainless steel faucet is visible on the counter, and a row of copper-colored cooking tools (spatulas, tongs, etc.) are hanging on a rack above the countertop.

**Ingredients & Props:**

*   **Countertop Ingredients:** The most prominent elements on the countertop are a collection of ingredients for cooking: 
    *   **Large Bowl:** A white ceramic bowl contains chopped green onions and what appears to be some sort of spice (possibly chili powder or paprika – it’s difficult to be certain).
    *   **Jars:** Three jars are on the countertop: 
        *   A dark brown jar labeled “Cacao”.
        *   A clear jar with a dark liquid, possibly soy sauce or balsamic vinegar.
        *   A dark brown jar with a label “Sesame Oil”.

    *   **Meat:** There's a piece of sliced pink meat (likely ham or prosciutto) arranged on the counter.
    *   **Other Spices:** Several small containers of spices are scattered around – likely garlic powder, pepper, and possibly others.

*   **Cutting Board:** A white wooden cutting board is placed in front of the man, suggesting he’s in the process of preparing the ingredients.

**Technical Aspects (Based on the Image):**

*   **Lighting:** The lighting is bright and even, likely from multiple sources (e.g., softboxes or LED panels).
*   **Focus:** The man is in sharp focus, while the background is slightly softer, creating depth of field.
*   **Color Palette:** The color palette is relatively muted and natural – greens, browns, grays, and pops of yellow from the lemons.

**Overall Impression & Possible Context:**

The image strongly suggests a cooking demonstration focused on a savory dish, potentially something with Asian-inspired flavors, given the soy sauce and sesame oil. The presenter seems knowledgeable and approachable, and the organized setting implies a focus on clear instructions.

Next I continued on, and asked, just like the video **"hey, can you help me make a Korean inspired steak sauce for my steak sandwich here?"**

I received this... now I don't know anything about Korean cuisine, but it seemed like a pretty good response. Go go Local AI :)

Absolutely! Let’s craft a fantastic Korean-inspired steak sauce perfect for elevating your steak sandwich. Here’s a recipe and detailed breakdown, incorporating the key flavors and techniques:

**Korean-Inspired Steak Sauce Recipe**

**Yields:** Approximately 1 cup

**Prep Time:** 10 minutes

**Cook Time:** 15-20 minutes

**Ingredients:**

*   1/2 cup Beef Broth (low sodium is best)
*   1/4 cup Soy Sauce (low sodium)
*   2 tablespoons Gochujang (Korean Chili Paste – adjust to your spice preference)
*   2 tablespoons Honey or Maple Syrup (honey provides a deeper flavor)
*   1 tablespoon Sesame Oil (crucial for that authentic aroma)
*   1 tablespoon Rice Vinegar (adds brightness and cuts through the richness)
*   1 clove Garlic, minced
*   1/2 teaspoon Ground Ginger
*   1/4 teaspoon Black Pepper
*   1/2 teaspoon Toasted Sesame Seeds (for garnish - optional)

**Instructions:**

1.   **Sauté Aromatics:** In a small saucepan, heat a teaspoon of sesame oil over medium heat. Add the minced garlic and ground ginger. Sauté for 30-60 seconds, until fragrant – _don’t burn the garlic!_ This builds the foundational flavor.
2.   **Combine Liquids:** Pour in the beef broth and soy sauce. Bring to a gentle simmer.
3.   **Add Sweetness & Spice:** Stir in the gochujang, honey (or maple syrup), rice vinegar, and black pepper.
4.   **Simmer & Reduce:** Reduce the heat to low and let the sauce simmer for 15-20 minutes, or until it has thickened slightly to your desired consistency. _Stir occasionally to prevent sticking._ The sauce will thicken further as it cools.
5.   **Strain (Optional):** For a smoother sauce, you can strain it through a fine-mesh sieve after simmering. This is purely for aesthetic preference.
6.   **Final Touch:** Stir in the remaining teaspoon of sesame oil before serving. Sprinkle with toasted sesame seeds for garnish if desired.

**Flavor Notes & Customization:**

*   **Spice Level:** Gochujang varies in heat. Start with 2 tablespoons and add more to your taste. A little goes a long way!
*   **Sweetness:** Adjust the honey/maple syrup based on how sweet you like your sauce.
*   **Umami Boost:** A tiny splash (1/2 teaspoon) of fish sauce can deepen the savory notes. Be cautious – it’s potent!
*   **Citrus:** A squeeze of lime juice at the end will add a bright, zesty element.
*   **Korean Pear or Apple:** For a more complex sweetness, consider adding a small amount (1/4 cup) of pureed Korean pear or apple during the simmering process.

**Using the Sauce with Your Steak Sandwich:**

*   Brush the sauce generously onto your cooked steak before assembling your sandwich.
*   Alternatively, serve the sauce on the side for dipping.

[1 comment](https://redlib.catsarch.com/r/LocalLLaMA/comments/1nkjfiq/with_metas_fail_i_wanted_to_test_a_couple_4bs/ "1 comment")

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/Present-Ad-8531](https://redlib.catsarch.com/u/Present-Ad-8531)•Dec 17 '24

## [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on)[Irony](https://redlib.catsarch.com/r/LocalLLaMA/comments/1hge0uk/irony/)

 23  Upvotes

Exone3.5 was advertised as the state of the art for real world problems ( [https://huggingface.co/papers/2412.04862](https://huggingface.co/papers/2412.04862) ).

But you can't use it for commercial purposes where we deal with so much real word problems ( [https://huggingface.co/LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct/blob/main/LICENSE#:~:text=Commercial%20Use%3A%20The,any%20commercial%20purposes](https://huggingface.co/LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct/blob/main/LICENSE#:%7E:text=Commercial%20Use%3A%20The,any%20commercial%20purposes) )

Granted we can use it for personal stuff, it's still a pity given how good it is in benchmark.

[![Image 9](https://redlib.catsarch.com/preview/pre/rodh968tnf7e1.png?width=1756&format=png&auto=webp&s=6f1693d45377b672cc29b8a444c9002d0130cb5f)](https://redlib.catsarch.com/preview/pre/rodh968tnf7e1.png?width=1756&format=png&auto=webp&s=6f1693d45377b672cc29b8a444c9002d0130cb5f)

[7 comments](https://redlib.catsarch.com/r/LocalLLaMA/comments/1hge0uk/irony/ "7 comments")

v0.36.0 [ⓘ View instance info](https://redlib.catsarch.com/info "View instance information")[<> Code](https://github.com/redlib-org/redlib "View code on GitHub")
