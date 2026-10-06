Title: DeepSeek v4 Flash vs. Qwen3.6-27B, 3.5-122B, and Gemma 4 31B Benchmark - r/LocalLLaMA

URL Source: https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/

Markdown Content:
[red lib.](https://redlib.catsarch.com/)

Feeds

MAIN FEEDS

[Home](https://redlib.catsarch.com/)[Popular](https://redlib.catsarch.com/r/popular)[All](https://redlib.catsarch.com/r/all)

- [x] in /r/LocalLLaMA 

[reddit](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/#popup)

# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/comments/1vfhqkm/

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1vfhqkm/)

[settings](https://redlib.catsarch.com/settings)

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/returnity](https://redlib.catsarch.com/user/returnity)•14d ago

# [Resources](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Resources%22&restrict_sr=on) DeepSeek v4 Flash vs. Qwen3.6-27B, 3.5-122B, and Gemma 4 31B Benchmark

[![Image 1: Gallery image](https://redlib.catsarch.com/preview/pre/xucnql0lcehh1.png?width=765&format=png&auto=webp&s=8481e7da6e60f3b73adee0a63fe1dab92b9ab9a1)](https://redlib.catsarch.com/preview/pre/xucnql0lcehh1.png?width=765&format=png&auto=webp&s=8481e7da6e60f3b73adee0a63fe1dab92b9ab9a1)

[![Image 2: Gallery image](https://redlib.catsarch.com/preview/pre/gpnxnl0lcehh1.png?width=705&format=png&auto=webp&s=8e7ba42a2c5ccae0758881b9c327765ab005685f)](https://redlib.catsarch.com/preview/pre/gpnxnl0lcehh1.png?width=705&format=png&auto=webp&s=8e7ba42a2c5ccae0758881b9c327765ab005685f)

[![Image 3: Gallery image](https://redlib.catsarch.com/preview/pre/rm72ul0lcehh1.png?width=586&format=png&auto=webp&s=1188b7cf7f3b5fd2dab296e45cd353358fc7d734)](https://redlib.catsarch.com/preview/pre/rm72ul0lcehh1.png?width=586&format=png&auto=webp&s=1188b7cf7f3b5fd2dab296e45cd353358fc7d734)

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

 28  Upvotes

*   [perma link](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/)
*   [dup licat es](https://redlib.catsarch.com/r/LocalLLaMA/duplicates/1vfhqkm)
*   [reddit](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/#popup)# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/)  

72% Upvoted

76 comments sorted by

17

[u/MaximusSenior](https://redlib.catsarch.com/user/MaximusSenior)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1pfud6/?context=3#p1pfud6 "Aug 04 2026, 18:57:24 UTC")edited 14d ago

So unfair with Gemma, why Q4? I would rather compare Q8 to Q8 for models of similar size.

> 3
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qvawz/?context=3#p1qvawz "Aug 04 2026, 22:51:13 UTC")edited 14d ago
> 
> It's the QAT v2 Gemma with the chat template update. In my previous testing, it performed on par (and in some cases, better than) the original 31B. I didn't have a Q8_0 on hand, and my previous testing of the Q8_0 showed it inferior to the 27B, so I didn't keep it on my SSD -- but the QAT stil has utility in my stack, so I had it around. Sorry. Feel free to run the benchmark on Q8_0 and I'd love to see how it stacks up! It's a fair criticism that it's not 1:1, but I felt the QAT actually had some advantages that made it worth including here.
> 
> 
> > 3
> > 
> > 
> > 
> > [u/honestly_i](https://redlib.catsarch.com/user/honestly_i)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qwqif/?context=3#p1qwqif "Aug 04 2026, 22:58:25 UTC")
> > 
> > Q4 is actually completely fine with gemma because it's made to be very performant on q4
> > 
> > 
> > > 2
> > > 
> > > 
> > > 
> > > [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qzvw5/?context=3#p1qzvw5 "Aug 04 2026, 23:14:47 UTC")
> > > 
> > > Correct, the QAT model often outperformed the original version in benchmarks I saw. I meant no disadvantage to Gemma running it this way!
> > > 
> > > 
> > > > 3
> > > > 
> > > > 
> > > > 
> > > > [u/MaximusSenior](https://redlib.catsarch.com/user/MaximusSenior)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1ucbc3/?context=3#p1ucbc3 "Aug 05 2026, 12:24:37 UTC")
> > > > 
> > > > In my experience Gemma 31b QAT outperform normal 31b Q4, but still not as good as Q8.
> > > > 
> > > > 
> > > > > 2
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/returnity](https://redlib.catsarch.com/user/returnity)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1wm526/?context=3#p1wm526 "Aug 05 2026, 18:20:58 UTC")
> > > > > 
> > > > > You might be right on that, and it makes sense that you would be. I do want to re-run this benchmark with 31B Q8_0 because I think Gemma 4 gets a bad rap, and it's actually a great model. I just didn't find it superior to 27B for my actual workload, so I didn't keep the Q8_0 on disk.
> > > > > 
> > > > > 
> > > > > > 1
> > > > > > 
> > > > > > 
> > > > > > 
> > > > > > [u/UdderlyCow](https://redlib.catsarch.com/user/UdderlyCow)[8d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p2x68i7/?context=3#p2x68i7 "Aug 10 2026, 21:53:21 UTC")
> > > > > > 
> > > > > > with 128gb of RAM, you should be able to use qwen 3.5 122b-10b on q6 for better performance
> > > > > > 
> > > > > > 
> > > > > > > 1
> > > > > > > 
> > > > > > > 
> > > > > > > 
> > > > > > > [u/returnity](https://redlib.catsarch.com/user/returnity)[8d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p2xbr03/?context=3#p2xbr03 "Aug 10 2026, 22:20:07 UTC")
> > > > > > > 
> > > > > > > I've been using Q5_K_XL but I do have some remaining headroom. 122B is my daily driver.

11

[u/LegacyRemaster](https://redlib.catsarch.com/user/LegacyRemaster)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1p53ov/?context=3#p1p53ov "Aug 04 2026, 18:12:42 UTC")

qwen 3.8 27b will be the best

> 16
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1p5y4n/?context=3#p1p5y4n "Aug 04 2026, 18:16:12 UTC")
> 
> Very excited for it, but I am hoping for a 122B-A10B too.
> 
> 
> 
> 1
> 
> 
> 
> [u/some_user_2021](https://redlib.catsarch.com/user/some_user_2021)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1wtpg1/?context=3#p1wtpg1 "Aug 05 2026, 18:52:19 UTC")
> 
> **You** are the best.

8

[u/BitXorBit](https://redlib.catsarch.com/user/BitXorBit)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qan6t/?context=3#p1qan6t "Aug 04 2026, 21:12:53 UTC")

I raised my eyebrow until i reached the Setup section

> 1
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qxatc/?context=3#p1qxatc "Aug 04 2026, 23:01:19 UTC")
> 
> Thanks for actually reading the whole post.

7

[u/hainesk](https://redlib.catsarch.com/user/hainesk)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1pcgxa/?context=3#p1pcgxa "Aug 04 2026, 18:43:17 UTC")

I wonder if you can run this test against the full ds flash model. I’ve heard this model doesn’t quantize well.

> 1
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qwfgg/?context=3#p1qwfgg "Aug 04 2026, 22:56:52 UTC")
> 
> I wanted to see what I can run on my 128GB setup. Plenty of good benchmarks for non-local APIs out there.
> 
> 
> > 1
> > 
> > 
> > 
> > [u/colin_colout](https://redlib.catsarch.com/user/colin_colout)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1r40za/?context=3#p1r40za "Aug 04 2026, 23:36:16 UTC")edited 14d ago
> > 
> > Try unsloth on llama.cpp. the main reason i avoid dwarfstar is that the antirez quants feel weaker for me than unsloth iq3_s / iq3_xxs.
> > 
> > 
> > On coding i found a lot more instruction following issues and minor bugs. Might just be me or rocm (I'm Strix halo)
> > 
> > 
> > Would be interested to see if the benchmark matches.
> > 
> > 
> > > 2
> > > 
> > > 
> > > 
> > > [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1r5knj/?context=3#p1r5knj "Aug 04 2026, 23:44:24 UTC")
> > > 
> > > I have the Unsloth IQ3_XXS of 0731. I believe the KLD is likely a bit lower -- it was on the preview version compared to antirez. I just get double the tok/sec on dwarfstar: 14 tok/sec with Unsloth vs. 26 on Dwarfstar. That's a big gap. But I do plan to repeat the benchmark using the mainline llama.cpp version just to validate the results. I'm not sure I'll want to share the results after the response to this post though lol.
> > > 
> > > 
> > > FWIW, I'm working on better quants for Dwarfstar, I just need to generate a high-quality imatrix and that takes a lot of time.
> > > 
> > > 
> > > > 2
> > > > 
> > > > 
> > > > 
> > > > [u/colin_colout](https://redlib.catsarch.com/user/colin_colout)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1r97em/?context=3#p1r97em "Aug 05 2026, 00:03:49 UTC")
> > > > 
> > > > I had 14 on unsloth at first, but now I'm in the upper 20s. i had to fiddle around to get the dspark working for the speedup
> > > > 
> > > > 
> > > > > 1
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1rsxpr/?context=3#p1rsxpr "Aug 05 2026, 01:50:25 UTC")
> > > > > 
> > > > > Does DSpark work in llama.cpp at temps other than 0? If so that’s major! Dwarfstar restricts it to greedy and non-thinking annoyingly.
> > > > > 
> > > > > 
> > > > > > 2
> > > > > > 
> > > > > > 
> > > > > > 
> > > > > > [u/colin_colout](https://redlib.catsarch.com/user/colin_colout)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1s5a7e/?context=3#p1s5a7e "Aug 05 2026, 02:59:32 UTC")
> > > > > > 
> > > > > > Temperature 1.0 seems fine in my tests
> > > > 
> > > > 
> > > > 
> > > > 2
> > > > 
> > > > 
> > > > 
> > > > [u/fragment_me](https://redlib.catsarch.com/user/fragment_me)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1xl01j/?context=3#p1xl01j "Aug 05 2026, 20:51:14 UTC")
> > > > 
> > > > The KLD of even IQ3 is not great for 0731. Preview’s quanta were way more forgiving. 0731 KLD is like .15. Heck, even IQ4 was not great.
> > > > 
> > > > 
> > > > > 1
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/returnity](https://redlib.catsarch.com/user/returnity)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1xszs2/?context=3#p1xszs2 "Aug 05 2026, 21:28:09 UTC")
> > > > > 
> > > > > Yeah, I saw the chart. Unfortunately this to be expected— as more knowledge and capability is packed into the same weights, with more intricate RL posttraining, there is less entropy buffer available for lossy compression before impact is observable. The more precisely the weights are calibrated, packing more capability into the same space, the easier to disrupt that delicate balance. That’s generally why larger models quantize more forgivingly — they have more headroom in the parametric space to absorb the losses.
> > > > > 
> > > > > 
> > > > > Flash 0731 packs a record amount of capability into its size tier, so it follows logically that it’d suffer worse from compression than a less capable model of the same size or an equally capable model that’s larger. Hopefully Qwen 3.8 continues their trend of being very quant-tolerant, but I expect this to become more of an issue as we continue to find ways to imbue the same parameters with more intricate organization and functionality. It’s just thermodynamically logical…

6

[u/SexyAlienHotTubWater](https://redlib.catsarch.com/user/SexyAlienHotTubWater)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1pdbsf/?context=3#p1pdbsf "Aug 04 2026, 18:46:53 UTC")

Buried lede: it's quantized. 2 bit.

Also, why high, not max?

> 6
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qwaqr/?context=3#p1qwaqr "Aug 04 2026, 22:56:13 UTC")
> 
> Explained in the post. Read it. Also, not buried, clearly stated. I'm comparing what you can run on 128GB in RAM.

5

[u/pabloodiablo](https://redlib.catsarch.com/user/pabloodiablo)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1pke6j/?context=3#p1pke6j "Aug 04 2026, 19:16:57 UTC")

Why are you comparing different quantizations? A comparison only makes sense if we're dealing with the same quality. DS v4 Q2-Q4 is severely compromised. I've tested it and I know.

> 10
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qw660/?context=3#p1qw660 "Aug 04 2026, 22:55:34 UTC")edited 14d ago
> 
> I'm comparing what can be reasonably run on a 128GB RAM device. Not the absolute capability of the models. It's just what's possible LOCALLY. I completely agree Q2-Q4 isn't near the ceiling of the model
> 
> 
> 
> 0
> 
> 
> 
> u/[deleted][14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qqz6l/?context=3#p1qqz6l "Aug 04 2026, 22:29:29 UTC")
> 
> [deleted]
> 
> 
> > 1
> > 
> > 
> > 
> > [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qw1iy/?context=3#p1qw1iy "Aug 04 2026, 22:54:55 UTC")
> > 
> > I'm not quantizing the KV cache. Read again.

5

[u/TokenRingAI](https://redlib.catsarch.com/user/TokenRingAI)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qa4u4/?context=3#p1qa4u4 "Aug 04 2026, 21:10:35 UTC")

People just want to fight me when I tell them 122B is a better agent than 27B

> 2
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qylua/?context=3#p1qylua "Aug 04 2026, 23:08:06 UTC")
> 
> I used to think the opposite too, but then I actually stopped following the crowd and did my own testing.

4

[u/mrgreatheart](https://redlib.catsarch.com/user/mrgreatheart)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1pctv9/?context=3#p1pctv9 "Aug 04 2026, 18:44:49 UTC")edited 14d ago

In these charts low = high and high = max right? Flash only has high and max.

Or does low mean thinking disabled?

> 1
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qxi06/?context=3#p1qxi06 "Aug 04 2026, 23:02:23 UTC")edited 14d ago
> 
> No actually, there are 4 modes for DeepSeek v4 Flash 0731. The preview only had Off/High/Max. I explained clearly in the post exactly the circumstances with regard to the Thinking situation with DSv4F in Dwarfstar. It's a little convoluted.
> 
> 
> [https://www.reddit.com/r/LocalLLaMA/comments/1vdqsod/deepseekv4flash0731_when_low_is_higher_than_high/](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vdqsod/deepseekv4flash0731_when_low_is_higher_than_high/)
> 
> 
> [https://github.com/antirez/ds4/pull/686](https://github.com/antirez/ds4/pull/686)
> 
> 
> > 2
> > 
> > 
> > 
> > [u/mrgreatheart](https://redlib.catsarch.com/user/mrgreatheart)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1sluct/?context=3#p1sluct "Aug 05 2026, 04:45:45 UTC")
> > 
> > Interesting. Pi still doesn’t offer anything besides off, high and max for 0731.
> > 
> > 
> > Also disappointing. I’ve been craving a low setting because I feel it overthinks on high.
> > 
> > 
> > > 2
> > > 
> > > 
> > > 
> > > [u/returnity](https://redlib.catsarch.com/user/returnity)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1wqkjx/?context=3#p1wqkjx "Aug 05 2026, 18:39:14 UTC")edited 13d ago
> > > 
> > > Sadly, it still overthinks on Low -- you can see this from the token generation and wall clock metrics in the second image in my benchmarks. It just doesn't seem to apply itself as well. Yes it overthinks slightly more on high, but not a huge percentage of extra tokens/time -- you just seem to get more intelligence per token... The crazy thing is that High/Max modes are literally just text prompts that basically amount to 500 chars of "be smarter, make no mistakes"... It's the RL that is unlocked by these prompt injections that deliver so much more capability. In other words, the overthinking seems to be a feature of the model, whether in API or quantized locally, and High Effort seems to make better use of the excessive token generation than Low. I wish it was as terse and condensed as Qwen 3.5 122B, but it wrings a lot of intelligence out of all those tokens, so I'll take it... But a ThinkingCap-style RL post-train would be amazing!
> > > 
> > > 
> > > EDIT: IDK how you're serving DSv4 to pi, but I also use pi and I am running it through llama-swap, which points to Dwarfstar's OpenAI API endpoint. I don't know for sure how the llama.cpp chat template works for reasoning effort, but I bet if you pointed a coding agent at the Dwarfstar Github issue like I posted and the DSv4 encoding page that lists the actual trigger phrases the chat template uses ([https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/blob/main/encoding/README.md](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/blob/main/encoding/README.md)), you could get a Low reasoning effort mode option added pretty easily. I have been meaning to try Unsloth's IQ3 in llama.cpp with DSpark to see if I can match the throughput of Dwarfstar with no MTP, so if I get Low reasoning working, I'll let you know.

3

[u/my_name_isnt_clever](https://redlib.catsarch.com/user/my_name_isnt_clever)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1pqmlx/?context=3#p1pqmlx "Aug 04 2026, 19:44:09 UTC")

This hasn't been my experience with DSv4F 0731. I'm using Unsloth IQ3_XXS on mainline llama.cpp and it's doing high thinking without specifying an effort level. It only has no-think, high, max according to the model card.

My go-to model before this was Qwen 122b at Q5, and DSv4F is wiping the floor with it in my experience. I can give it a new level of agentic autonomy and come back to a good result, instead of coming back to Qwen 122b or 27b getting stuck somewhere and needing a nudge.

You can tell when a model is really good when it's running at half the decode speed as my last one, but I don't even care because the output is so good.

> 1
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qyh3b/?context=3#p1qyh3b "Aug 04 2026, 23:07:26 UTC")edited 14d ago
> 
> Actually it has all 4 modes: [https://www.reddit.com/r/LocalLLaMA/comments/1vdqsod/deepseekv4flash0731_when_low_is_higher_than_high/](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vdqsod/deepseekv4flash0731_when_low_is_higher_than_high/)
> 
> 
> Thinking modes in dwarfstar explained: [https://github.com/antirez/ds4/pull/686](https://github.com/antirez/ds4/pull/686)
> 
> 
> BTW, you will get much better tok/sec with dwarfstar than llama.cpp, that's why I switched. I went from 14 tok/sec to 26 in dwarfstar, same DSv4F, similar quality depending on your choice of quant.
> 
> 
> > 2
> > 
> > 
> > 
> > [u/my_name_isnt_clever](https://redlib.catsarch.com/user/my_name_isnt_clever)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1r1jis/?context=3#p1r1jis "Aug 04 2026, 23:23:24 UTC")
> > 
> > That post is deleted, but I double checked the model card and fair enough, there is a low. I'll check it out.
> > 
> > 
> > > 1
> > > 
> > > 
> > > 
> > > [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1r516i/?context=3#p1r516i "Aug 04 2026, 23:41:31 UTC")
> > > 
> > > Weird -- that post loads fine for me, as does the GitHub issue for Dwarfstar. But thanks for being open-minded about it. Cheers!
> > 
> > 
> > 
> > 1
> > 
> > 
> > 
> > [u/my_name_isnt_clever](https://redlib.catsarch.com/user/my_name_isnt_clever)[8d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p2whryg/?context=3#p2whryg "Aug 10 2026, 20:03:23 UTC")
> > 
> > What are your DwarfStar settings? I'm getting 14 t/s max with it without DSpark, but with it the speeds are the same.
> > 
> > 
> > > 1
> > > 
> > > 
> > > 
> > > [u/returnity](https://redlib.catsarch.com/user/returnity)[8d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p2xhhr6/?context=3#p2xhhr6 "Aug 10 2026, 22:48:48 UTC")
> > > 
> > > ```
> > > ./ds4-server \
> > >   -m /path/to/DeepSeek-V4-Flash-...-q2-q4-imatrix.gguf \
> > >   --metal \
> > >   -c 262144 \
> > >   --host 127.0.0.1 --port 8000 \
> > >   --kv-disk-dir /path/to/kv-cache --kv-disk-space-mb 65536
> > > ```
> > > 
> > > ~35 t/s at short context, ~26 t/s at 32K, tapers off minimally after that. M5 Max 128GB.
> > > 
> > > 
> > > What's your hardware like? You may be better served by taking this route in llama.cpp: [https://www.reddit.com/r/LocalLLM/comments/1vga26q/deepseek_v4_flash_11_25_toks_with_one_bash/](https://redlib.catsarch.com/r/LocalLLM/comments/1vga26q/deepseek_v4_flash_11_25_toks_with_one_bash/)

3

[u/Dazzling_Equipment_9](https://redlib.catsarch.com/user/Dazzling_Equipment_9)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1svuai/?context=3#p1svuai "Aug 05 2026, 05:59:53 UTC")

Thanks for sharing—this is really valuable; please keep it up. I know what those who disagree with you are thinking: they simply see certain parameters that don't align with their own ideas and immediately dismiss your work. They fail to grasp that your goal is to evaluate how a model performs during long-term use on a 128GB device. They also don't realize that for someone who relies on a model deeply and over the long haul, what matters is sustained usability, not an obsession with specific quantization levels or the like.

> 4
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1wnf5v/?context=3#p1wnf5v "Aug 05 2026, 18:26:13 UTC")
> 
> Thanks for the kind words. I feel like people bandwagon on certain models or get fixated on specific viewpoints and respond in kneejerk fashion to anything that doesn't fit their worldview. The truth is, I just wanted to get some objective data on the performance of models that I can fit in 128GB. End of story. My only bias is towards running the best setup I can fit on my hardware, not one lab or model. I spent most of a week building the eval setup and running these benchmarks, and I just wanted others to have the opportunity to learn from my efforts, because there are a lot of people here with 128GB hardware ceilings like mine. It's like, no fucking shit I'd rather be running full-precision models across the board, and I'm sure they'd perform better if they were constrained by what I can fit on my device -- but isn't this a LOCAL LLM sub?! ffs... Thanks for understanding my intention!

2

[u/ImpressiveRelief37](https://redlib.catsarch.com/user/ImpressiveRelief37)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1p7t9u/?context=3#p1p7t9u "Aug 04 2026, 18:23:53 UTC")

How can 27B have lower TG speed? I don’t understand

> 8
> 
> 
> 
> [u/BawbbySmith](https://redlib.catsarch.com/user/BawbbySmith)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1p8cus/?context=3#p1p8cus "Aug 04 2026, 18:26:09 UTC")
> 
> Dense vs MoE
> 
> 
> > 1
> > 
> > 
> > 
> > [u/ImpressiveRelief37](https://redlib.catsarch.com/user/ImpressiveRelief37)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1ppypr/?context=3#p1ppypr "Aug 04 2026, 19:41:17 UTC")
> > 
> > I mean if you have the HW to run DS you can certainly load the full 27B in vram. It doesn’t make sense
> > 
> > 
> > > 5
> > > 
> > > 
> > > 
> > > [u/my_name_isnt_clever](https://redlib.catsarch.com/user/my_name_isnt_clever)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1pqwaf/?context=3#p1pqwaf "Aug 04 2026, 19:45:19 UTC")
> > > 
> > > DeepSeek Flash is 13b active parameters, the 27b is 27b active parameters. That's the entire difference.
> > > 
> > > 
> > > > 2
> > > > 
> > > > 
> > > > 
> > > > [u/ImpressiveRelief37](https://redlib.catsarch.com/user/ImpressiveRelief37)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1pr8u5/?context=3#p1pr8u5 "Aug 04 2026, 19:46:52 UTC")
> > > > 
> > > > 8 tok/s decode on an M5 max? My buddy M1 ultra mbp has faster decode on 27B Q6 IIRC… about 15 or so. Don’t you find the numbers odd?
> > > > 
> > > > 
> > > > > 3
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qxsgl/?context=3#p1qxsgl "Aug 04 2026, 23:03:52 UTC")edited 13d ago
> > > > > 
> > > > > I'm so sorry! This was not clearly explained in the post -- I was running them at n=4, so that's not aggregate tokens/sec -- it's 1 of the 4 streams. Multiply decode by ~2.5x for all models except DSv4. My bad, I forgot to do that before I posted the chart!
> > > > > 
> > > > > 
> > > > > 
> > > > > 2
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/my_name_isnt_clever](https://redlib.catsarch.com/user/my_name_isnt_clever)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1pwq8c/?context=3#p1pwq8c "Aug 04 2026, 20:11:02 UTC")
> > > > > 
> > > > > You asked why the 27b is slower than the others for this post, and that's why. I don't know enough about how OP or your buddy have their inference configured to explain the specific numbers.
> > > > > 
> > > > > 
> > > > > 
> > > > > 1
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/bobby-chan](https://redlib.catsarch.com/user/bobby-chan)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1q4mvo/?context=3#p1q4mvo "Aug 04 2026, 20:45:59 UTC")
> > > > > 
> > > > > you must be misremembering either/or the machine, the config, the decode speed, because a M1 ultra mbp doesn't exist.
> > > > > 
> > > > > 
> > > > > > 1
> > > > > > 
> > > > > > 
> > > > > > 
> > > > > > [u/ImpressiveRelief37](https://redlib.catsarch.com/user/ImpressiveRelief37)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1sb992/?context=3#p1sb992 "Aug 05 2026, 03:35:44 UTC")
> > > > > > 
> > > > > > You are right. It’s a M1 Max 64GB. OP gave the TG speed for 1 or then 4 streams so it’s 35 aggregate, that makes more sense. So it’s not slower than DSV4 Fast with -np 1
> > > > > 
> > > > > 
> > > > > 
> > > > > 1
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/Ok_Meeting_2995](https://redlib.catsarch.com/user/Ok_Meeting_2995)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1q88pz/?context=3#p1q88pz "Aug 04 2026, 21:02:01 UTC")
> > > > > 
> > > > > Mlx vs llama cpp performance diff on Macs.
> > > 
> > > 
> > > 
> > > 2
> > > 
> > > 
> > > 
> > > [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qxxr5/?context=3#p1qxxr5 "Aug 04 2026, 23:04:37 UTC")edited 13d ago
> > > 
> > > It's in RAM, that's just one of the 4 simultaneous streams. Aggregate is about 2.5x, or ~20 tok/sec. MTP off because it hurts in multi-threading setups.
> 
> 
> 
> 1
> 
> 
> 
> [u/Tormeister](https://redlib.catsarch.com/user/Tormeister)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1pwtuc/?context=3#p1pwtuc "Aug 04 2026, 20:11:28 UTC")
> 
> He's running it on a mac, not a dGPU

2

[u/ChristopherDci](https://redlib.catsarch.com/user/ChristopherDci)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1ps8cz/?context=3#p1ps8cz "Aug 04 2026, 19:51:13 UTC")

DeepSeek models were 'disappearing' (or 'missing'), but now it seems they are gaining more and more ground.

2

[u/Curious-Resource1943](https://redlib.catsarch.com/user/Curious-Resource1943)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1pyt48/?context=3#p1pyt48 "Aug 04 2026, 20:20:09 UTC")

One thing I’m curious about: did the ThinkingCap fine-tune change the style of the failures at all, or just the token count? I’ve noticed some of the smaller Qwen variants can get stuck in very similar loops even when they eventually solve the problem on retry.

Also looking forward to seeing how the upcoming Qwen3.8 27B lands in this kind of harness. If it keeps the first-try strength while closing some of the gap on the harder cases, it could be a real sweet spot for local agentic work.

> 2
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qyv3o/?context=3#p1qyv3o "Aug 04 2026, 23:09:26 UTC")
> 
> I would love to run that test, I just don't have until the heat death of the universe. 27B thinks for so long, it's insane. It will reach DS4 levels of thinking but at lower speeds. However, I too am very curious about that kind of granular detail, and if 3.8 wasn't impending, I'd probably have to find out.

2

[u/RunawayPeeko](https://redlib.catsarch.com/user/RunawayPeeko)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1rn79w/?context=3#p1rn79w "Aug 05 2026, 01:19:05 UTC")

Thanks for the results. I was thinking about doing a similar one, but for 64gb

> 1
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1ws33t/?context=3#p1ws33t "Aug 05 2026, 18:45:32 UTC")
> 
> Happy you enjoyed the read. I'd love to see what you come up with. This sub needs more quantitative tests on actual users' local hardware.

2

[u/Rough-Measurement988](https://redlib.catsarch.com/user/Rough-Measurement988)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1ssfvi/?context=3#p1ssfvi "Aug 05 2026, 05:33:53 UTC")

Great report and thanks for your efforts. Do you mind sharing how you handled the results assessment? Do you just ask a frontier model to summarise or you have some static analysis built for this step? I’ve built also some benchmark coding for my specific coding language and had to use Opus to summarise the result as static analysis did not work well. Most of the tasks have more than valid solution so the result needs to be assessed individually.

> 2
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1wp03w/?context=3#p1wp03w "Aug 05 2026, 18:32:42 UTC")
> 
> Yeah, I tried a few approaches but since I built the eval setup using Claude Code primarily (I know, shame on me lol), it had deep contextual understanding of the eval suite. I setup monitors to track progress, tokens generated, memory usage, and other metrics throughout the run, and this helped me catch and prevent an OOM when a linter issue surfaced that triggered unbounded generation in DSv4 trying to fix a non-existent mistake in a case it'd already solved.
> 
> 
> Similarly, I had Claude evaluate the logs of the actual responses, not just relying on the deterministic numerical output, and it found 2 cases with bug that would have biased the results, because it actually read through how the models were interacting with the test suite. This allowed me to exclude the 2 questionable results from every model's score for fairness, and fix the issue moving forwards.
> 
> 
> This is the way. Good luck with your benchmarks, and don't be discouraged from posting your findings by some of the narrow-minded responses to my post. There are many people here who would appreciate your learnings! Thanks for the thoughtful reply.
> 
> 
> > 1
> > 
> > 
> > 
> > [u/Rough-Measurement988](https://redlib.catsarch.com/user/Rough-Measurement988)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p20azmg/?context=3#p20azmg "Aug 06 2026, 06:12:46 UTC")
> > 
> > I think that you should not be shame of using AI to build the benchmark as nowadays it’s just an accelerator for reaching the final target and solution. The idea is the most important thing and it come from you. I’m also using the Claude Code in my build setup but now I already know that still it requires a lot of effort to fine tune, test and run benchmarks to get a good result at the end. So that’s why I appreciate your work even more.

1

[u/VoiceApprehensive893](https://redlib.catsarch.com/user/VoiceApprehensive893)transformers[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1plx7o/?context=3#p1plx7o "Aug 04 2026, 19:23:34 UTC")

ds v4 flash low effort seems to be broken

> 1
> 
> 
> 
> u/[deleted][14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1posur/?context=3#p1posur "Aug 04 2026, 19:36:09 UTC")
> 
> [deleted]

1

[u/MotokoAGI](https://redlib.catsarch.com/user/MotokoAGI)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qbma9/?context=3#p1qbma9 "Aug 04 2026, 21:17:17 UTC")

good report.

1

[u/fbms2](https://redlib.catsarch.com/user/fbms2)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1razdz/?context=3#p1razdz "Aug 05 2026, 00:13:23 UTC")

thinking cap is bad. wrong choice

1

[u/Technical_Ad_6106](https://redlib.catsarch.com/user/Technical_Ad_6106)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1vl96u/?context=3#p1vl96u "Aug 05 2026, 15:49:33 UTC")

qwen has fallen. just accept it. deepseek wins again. even qwens new models wont have a chance. just look at intelligence per gb of vkvcache and ull see qwen is not even close.

> 3
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1wltv8/?context=3#p1wltv8 "Aug 05 2026, 18:19:41 UTC")
> 
> For sure -- and the consistent decode speed whether at 2k or 200k context is amazing with DeepSeek. Their engineering innovations are incredible, without a doubt. And for the record, I have no horse in this race -- I am just looking for the best model to run on my hardware...

1

[u/pseudonerv](https://redlib.catsarch.com/user/pseudonerv)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1xflxx/?context=3#p1xflxx "Aug 05 2026, 20:27:09 UTC")

Would you try ds4flash from unsloth and see if you can tell the difference from different quants?

> 1
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1xw58z/?context=3#p1xw58z "Aug 05 2026, 21:43:08 UTC")
> 
> Yes, that's my next eval for sure. I can definitely fit Unsloth's IQ3_XXS (already on disk) with enough OS headroom to run the container and everything else for the harness safely. DSv4's KV cache is so small that 384k is like 3.5GB. I think that quant will be roughly comparable. I will post if there's any interesting findings. I only used Dwarfstar because DSpark wasn't working in llama.cpp yet, and without it, I get half the tok/sec compared to Dwarfstar (26 vs. 14 decode).
> 
> 
> > 2
> > 
> > 
> > 
> > [u/pseudonerv](https://redlib.catsarch.com/user/pseudonerv)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1y8666/?context=3#p1y8666 "Aug 05 2026, 22:42:57 UTC")
> > 
> > [https://www.reddit.com/r/LocalLLM/s/wJg1m47CO9](https://redlib.catsarch.com/r/LocalLLM/s/wJg1m47CO9)
> > 
> >  I have 20 something tg with llama.cpp without dspark
> > 
> > 
> > > 1
> > > 
> > > 
> > > 
> > > [u/returnity](https://redlib.catsarch.com/user/returnity)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1y93el/?context=3#p1y93el "Aug 05 2026, 22:47:43 UTC")
> > > 
> > > Thanks for sharing this thread! Lotta good info here. I also saw him post that you figured out the fix for DSv4 on Apple Silicon in llama.cpp and went from 11t/s to 25t/s, so that’s at the top of my list, then add DSpark! Tyvm

1

[u/JustMine999](https://redlib.catsarch.com/user/JustMine999)[6d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p372d7b/?context=3#p372d7b "Aug 12 2026, 07:21:39 UTC")edited 6d ago

I'm care more about first try success rate and how often the diff is actually usable than one final score. A model that fixes things after seeing its own mistakes is still useful, but that's a very different workflow from one that gets the change right the first time.

Would be interesting to see Hy3 run through the same harness, especially on the JS tasks.

> 1
> 
> 
> 
> [u/returnity](https://redlib.catsarch.com/user/returnity)[6d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p39ld00/?context=3#p39ld00 "Aug 12 2026, 16:10:34 UTC")
> 
> It's on my to do list. I still have it running on my system. I just ran Muse Glimmer, so a v2 of this report is forthcoming regardless of the downvoters. For first-try work, 122B seems incomparable as of now.
> 
> 
> > 1
> > 
> > 
> > 
> > [u/One-Cry297](https://redlib.catsarch.com/user/One-Cry297)[4d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p3m2yqc/?context=3#p3m2yqc "Aug 14 2026, 09:17:30 UTC")
> > 
> > Would be nice to see Qwen 35b q8 results as well.

-3

[u/Opteron67](https://redlib.catsarch.com/user/Opteron67)[14d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vfhqkm/deepseek_v4_flash_vs_qwen3627b_35122b_and_gemma_4/p1qssgj/?context=3#p1qssgj "Aug 04 2026, 22:38:31 UTC")

people with Q0.5 quantization models dont do anything useful in real life with llms, still they would not be able to...

v0.36.0 [ⓘ View instance info](https://redlib.catsarch.com/info "View instance information")[<> Code](https://github.com/redlib-org/redlib "View code on GitHub")
