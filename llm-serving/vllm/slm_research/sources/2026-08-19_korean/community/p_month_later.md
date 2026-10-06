Title: Everyone posts day-one impressions. What's still in your stack a month later? - r/LocalLLaMA

URL Source: https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/

Markdown Content:
[red lib.](https://redlib.catsarch.com/)

Feeds

MAIN FEEDS

[Home](https://redlib.catsarch.com/)[Popular](https://redlib.catsarch.com/r/popular)[All](https://redlib.catsarch.com/r/all)

- [x] in /r/LocalLLaMA 

[reddit](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/#popup)

# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/comments/1va1zoc/

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1va1zoc/)

[settings](https://redlib.catsarch.com/settings)

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/derspenti](https://redlib.catsarch.com/user/derspenti)•20d ago

# [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on) Everyone posts day-one impressions. What's still in your stack a month later?

[![Image 1: Post image](https://redlib.catsarch.com/img/21nsd5ho87gh1.png)](https://redlib.catsarch.com/img/21nsd5ho87gh1.png)

Day one threads are the least useful thing we produce here and we produce a lot of them. Model drops, forty people run their favourite prompt, half say it's the best thing ever and half say benchmaxxed, and none of that survives contact with two weeks of real work.

So: what did you install in the last month or two that's still in the rotation, and what quietly got uninstalled?

I'll go first. Still here: Qwen3.6 27B for anything that has to actually know something. Ling-3.0-flash sitting in the executor slot of my agent setup, which surprised me because I only put it there expecting to watch it fail and it hasn't yet, and officially confirmed open source soon (now is free on open router). Gone: two things I was very excited about on day one, which I'm not naming because I don't want that argument in this thread.

What I'd like to hear is the boring version. Not "X is amazing", but "X is still doing Y for me on Z and I've stopped thinking about it". A model you've stopped thinking about is the highest praise available.

Also interested in the reverse. Stuff that got worse for you over time, or that you kept using out of inertia and then finally dropped. That never shows up in the day one threads either

 121  Upvotes

*   [perma link](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/)
*   [reddit](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/#popup)# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/)  
*   [dl download](https://redlib.catsarch.com/img/21nsd5ho87gh1.png)

92% Upvoted

81 comments sorted by

58

[u/thereisonlythedance](https://redlib.catsarch.com/user/thereisonlythedance)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0i8o4e/?context=3#p0i8o4e "Jul 29 2026, 17:17:43 UTC")

GLM 5.2 is top dog for high end local hardware. Brilliant model made better by recent llama.cpp support for DSA lightning indexers.

DS4 Flash is good for its size.

Minimax M3 is also very good but seems sensitive to quantization.

> 24
> 
> 
> 
> [u/BitXorBit](https://redlib.catsarch.com/user/BitXorBit)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0i9lfb/?context=3#p0i9lfb "Jul 29 2026, 17:21:34 UTC")
> 
> You need a little bit more than high end to run glm 5.2 😂
> 
> 
> > 29
> > 
> > 
> > 
> > [u/thereisonlythedance](https://redlib.catsarch.com/user/thereisonlythedance)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0iaa28/?context=3#p0iaa28 "Jul 29 2026, 17:24:25 UTC")
> > 
> > Not really. Just had to buy your RAM before prices went nuts.
> > 
> > 
> > > 8
> > > 
> > > 
> > > 
> > > [u/BitXorBit](https://redlib.catsarch.com/user/BitXorBit)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0iajbf/?context=3#p0iajbf "Jul 29 2026, 17:25:29 UTC")
> > > 
> > > Offloading is realistic option? I have 2 rtx 6000 pro, offloading to ram would make things very slow (not realistic for agentic coding)
> > > 
> > > 
> > > > 11
> > > > 
> > > > 
> > > > 
> > > > [u/ttkciar](https://redlib.catsarch.com/user/ttkciar)llama.cpp[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0iwfjg/?context=3#p0iwfjg "Jul 29 2026, 18:57:36 UTC")
> > > > 
> > > > Offloading is _absolutely_ an option for tasks which do not need to be interactive.
> > > > 
> > > > 
> > > > I have shaped some of my workflows around "slow inference" tasks, such that I am working on other things while inference is processing.
> > > > 
> > > > 
> > > > I would rather have the ability to use larger models for high-quality outputs, than limit myself to only models that can deliver low-quality outputs quickly.
> > > > 
> > > > 
> > > > > 2
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/BitXorBit](https://redlib.catsarch.com/user/BitXorBit)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ix3ml/?context=3#p0ix3ml "Jul 29 2026, 19:00:28 UTC")
> > > > > 
> > > > > In that case i prefer to load a model on my Mac Studio M3 Ultra 512gb
> > > > 
> > > > 
> > > > 
> > > > 6
> > > > 
> > > > 
> > > > 
> > > > [u/thereisonlythedance](https://redlib.catsarch.com/user/thereisonlythedance)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ib15e/?context=3#p0ib15e "Jul 29 2026, 17:27:32 UTC")
> > > > 
> > > > Yeah I get 6-7 t/s (with DDR4 RAM) running the 4 bit Unsloth quant. Too slow for some, but fine for me. Kimi 2.6 is better at around 10 t/s.
> > > > 
> > > > 
> > > > > 4
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/BitXorBit](https://redlib.catsarch.com/user/BitXorBit)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ib4de/?context=3#p0ib4de "Jul 29 2026, 17:27:54 UTC")
> > > > > 
> > > > > What about the prompt processing?
> > > > > 
> > > > > 
> > > > > > 6
> > > > > > 
> > > > > > 
> > > > > > 
> > > > > > [u/thereisonlythedance](https://redlib.catsarch.com/user/thereisonlythedance)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ibdrz/?context=3#p0ibdrz "Jul 29 2026, 17:28:59 UTC")
> > > > > > 
> > > > > > Slow. 15-17 t/s with default batch sizes.
> > > > > > 
> > > > > > 
> > > > > > > 4
> > > > > > > 
> > > > > > > 
> > > > > > > 
> > > > > > > [u/No_Afternoon_4260](https://redlib.catsarch.com/user/No_Afternoon_4260)llama.cpp[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0inben/?context=3#p0inben "Jul 29 2026, 18:18:49 UTC")
> > > > > > > 
> > > > > > > Ouch
> > > > > > > 
> > > > > > > 
> > > > > > > > 2
> > > > > > > > 
> > > > > > > > 
> > > > > > > > 
> > > > > > > > [u/d3nzil](https://redlib.catsarch.com/user/d3nzil)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0lud5r/?context=3#p0lud5r "Jul 30 2026, 04:11:57 UTC")
> > > > > > > > 
> > > > > > > > Bigger batch size helps a lot with GLM 5.2 prompt processing. On llama.cpp with --ub 2048 I got about 4x speedup compared to the default size.
> > > > > 
> > > > > 
> > > > > 
> > > > > 1
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/reacusn](https://redlib.catsarch.com/user/reacusn)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ifmyf/?context=3#p0ifmyf "Jul 29 2026, 17:46:42 UTC")
> > > > > 
> > > > > > 6-7 t/s
> > > > > 
> > > > > 
> > > > > Is that 8 channel ddr4? I get 8 t/s on an abliterated q4, with 30 t/s prompt processing on ddr4-3200 with a 64 core zen 2 cpu. I'm not sure what you use it for, but I've found it's pretty much unusable at those speeds (the token generation I can live with, but prompt processing under 100 t/s is hell), and I'm not using it professionally.
> > > > > 
> > > > > 
> > > > > > 1
> > > > > > 
> > > > > > 
> > > > > > 
> > > > > > [u/BlackBeardAI](https://redlib.catsarch.com/user/BlackBeardAI)vllm[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ih0u2/?context=3#p0ih0u2 "Jul 29 2026, 17:52:24 UTC")
> > > > > > 
> > > > > > IQ2 unsloth > 8 channel ddr4 3200 + 4x3090, I am getting 11-12 tps, with MTP #PR25980. it adds like 10% extra speed. (105k ctx)
> > > > > > 
> > > > > > 
> > > > > > > 1
> > > > > > > 
> > > > > > > 
> > > > > > > 
> > > > > > > [u/reacusn](https://redlib.catsarch.com/user/reacusn)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ihg57/?context=3#p0ihg57 "Jul 29 2026, 17:54:12 UTC")
> > > > > > > 
> > > > > > > Is iq2 a good idea?
> > > > > > > 
> > > > > > > 
> > > > > > > > 1
> > > > > > > > 
> > > > > > > > 
> > > > > > > > 
> > > > > > > > [u/BlackBeardAI](https://redlib.catsarch.com/user/BlackBeardAI)vllm[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ikr7j/?context=3#p0ikr7j "Jul 29 2026, 18:08:05 UTC")
> > > > > > > > 
> > > > > > > > it is a good idea when iq4 is out of reach.
> > > > > > > > 
> > > > > > > > 
> > > > > > > > > 3
> > > > > > > > > 
> > > > > > > > > 
> > > > > > > > > 
> > > > > > > > > [u/reacusn](https://redlib.catsarch.com/user/reacusn)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ilh1d/?context=3#p0ilh1d "Jul 29 2026, 18:11:06 UTC")
> > > > > > > > > 
> > > > > > > > > I mean, compared to a smaller model at q4. I've always been told to never go below q4, since even if most of their knowledge is retained, they may make small, snowballing errors. But that was a while ago, and I'm not too sure if it still stands. Have you had a good experience with iq2?
> > > > > > > > > 
> > > > > > > > > 
> > > > > > > > > > [→ More replies (0)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ilh1d)
> > > > > > 
> > > > > > 
> > > > > > 
> > > > > > 1
> > > > > > 
> > > > > > 
> > > > > > 
> > > > > > [u/thereisonlythedance](https://redlib.catsarch.com/user/thereisonlythedance)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0iieq3/?context=3#p0iieq3 "Jul 29 2026, 17:58:10 UTC")
> > > > > > 
> > > > > > Yeah 8 channel. But only 2666. Threadripper 5965. Speeds are fine for my usage. I still remember the days of trying to run Llama 1 65b at 0.4 t/s so it’s all relative.
> > > > > > 
> > > > > > 
> > > > > > > 2
> > > > > > > 
> > > > > > > 
> > > > > > > 
> > > > > > > [u/reacusn](https://redlib.catsarch.com/user/reacusn)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ik91n/?context=3#p0ik91n "Jul 29 2026, 18:05:57 UTC")
> > > > > > > 
> > > > > > > I used gpt-j 6b at 0.2 t/s for rp back in the day, but that was when we didn't have easy access to hosted AI that replies in milliseconds. I can't really go back to those days... sending a message and waiting half an hour for a response...
> > > > > > > 
> > > > > > > 
> > > > > > > Currently, I mostly use a Gemma 4 31b for translation, and the prompt processing of GLM 5.2 on my system isn't really an option, since I'm not really translating books - I can't just automate a batch of text overnight.
> > > > > > > 
> > > > > > > 
> > > > > > > What's your usage, if you don't mind me asking?
> > > > > > > 
> > > > > > > 
> > > > > > > > 1
> > > > > > > > 
> > > > > > > > 
> > > > > > > > 
> > > > > > > > [u/BitXorBit](https://redlib.catsarch.com/user/BitXorBit)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ikf3x/?context=3#p0ikf3x "Jul 29 2026, 18:06:41 UTC")
> > > > > > > > 
> > > > > > > > Deepseek v4 flash dspark 210 t/s and prompt processing 8k
> > > > > > > > 
> > > > > > > > 
> > > > > > > > > 2
> > > > > > > > > 
> > > > > > > > > 
> > > > > > > > > 
> > > > > > > > > [u/reacusn](https://redlib.catsarch.com/user/reacusn)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0iky1k/?context=3#p0iky1k "Jul 29 2026, 18:08:53 UTC")
> > > > > > > > > 
> > > > > > > > > Did you mean to reply to me?
> > > > 
> > > > 
> > > > 
> > > > 2
> > > > 
> > > > 
> > > > 
> > > > [u/Hoak-em](https://redlib.catsarch.com/user/Hoak-em)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0j5u4u/?context=3#p0j5u4u "Jul 29 2026, 19:38:26 UTC")
> > > > 
> > > > With fast RAM and a tool built for offloading like ktransformers, yes. It benefits from a strong CPU with many channels for memory and access to AMX or AVX-512 instructions. I'm running dual xeon Q30s with 768GB DDR5 over 16 channels. I can run Qwen-397b with mtp at over 30 tokens/s sustained single-request, with very fast prefill as well with only 2 3090s for the dense layers + shared/hot experts + kv-cache. I'm currently waiting for a ternary quant of K3, or a reap + Q2 to really test things out
> > 
> > 
> > 
> > 1
> > 
> > 
> > 
> > [u/Strawberry3141592](https://redlib.catsarch.com/user/Strawberry3141592)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0k2av2/?context=3#p0k2av2 "Jul 29 2026, 22:06:30 UTC")
> > 
> > I mean I can run it on a 64gb DDR4 laptop (at 0.2tok/s lmfao)
> 
> 
> 
> 4
> 
> 
> 
> [u/Barni275](https://redlib.catsarch.com/user/Barni275)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0j7qq2/?context=3#p0j7qq2 "Jul 29 2026, 19:46:42 UTC")
> 
> Almost the same model selection as would I do! My HW is poor, only 32GB+64GB, but using API providers I pick the similar stack: GLM5.2 -> Minimax M3 -> Step 3.7 Flash + local Gemma4-26B-A4B (for vision processing only)
> 
> 
> > 2
> > 
> > 
> > 
> > [u/thereisonlythedance](https://redlib.catsarch.com/user/thereisonlythedance)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0jaebx/?context=3#p0jaebx "Jul 29 2026, 19:58:07 UTC")
> > 
> > I need to try Step 3.7 Flash. I see a lot of good things about it.
> 
> 
> 
> 1
> 
> 
> 
> [u/Legal-Ad-3901](https://redlib.catsarch.com/user/Legal-Ad-3901)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ijh9l/?context=3#p0ijh9l "Jul 29 2026, 18:02:39 UTC")
> 
> Oddly enough lightning indexing slower on my setup 😐
> 
> 
> > 1
> > 
> > 
> > 
> > [u/thereisonlythedance](https://redlib.catsarch.com/user/thereisonlythedance)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ilt8u/?context=3#p0ilt8u "Jul 29 2026, 18:12:31 UTC")
> > 
> > I think there’s still a step to come. For the moment I’m finding it much better for long context accuracy. Though I‘ve also been experimenting with a larger DSA top-k (4096 v 2096) and more experts.
> 
> 
> 
> 1
> 
> 
> 
> [u/voyager256](https://redlib.catsarch.com/user/voyager256)[19d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ng9x6/?context=3#p0ng9x6 "Jul 30 2026, 11:37:54 UTC")
> 
> Hy3 is also very good for its size, perhaps slightly better than Minimax M3 , but not well known for some reason.

31

[u/nickm_27](https://redlib.catsarch.com/user/nickm_27)llama.cpp[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0i8r6p/?context=3#p0i8r6p "Jul 29 2026, 17:18:04 UTC")

These days I run:

*   Gemma4 26B-A4B QAT for the actions requiring speed like voice agent and quick chat agent tasks. 
*   Qwen3.6 27B Q6_K for writing HA automations, other scripts, and deep research I
*   Qwen3-ASR 1.7B for STT
*   Omnivoice for TTS

> 6
> 
> 
> 
> [u/rkoy1234](https://redlib.catsarch.com/user/rkoy1234)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0kvsha/?context=3#p0kvsha "Jul 30 2026, 00:44:22 UTC")
> 
> We're all converting to qwen. Even omnivoice is based on qwenvoice IIRC.
> 
> 
> 3.7/8 can't come fast enough.

26

[u/pabloodiablo](https://redlib.catsarch.com/user/pabloodiablo)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ibz0m/?context=3#p0ibz0m "Jul 29 2026, 17:31:24 UTC")

Until recently, for coding: Qwen3.6 27B Q8 was suitable for 90% of tasks. For the past few days, I've been using the improved Laguna S2.1 Q6_K_XL version. I am testing it, and it seems to me that in many situations, it can reasonably replace my Qwen3.6.

For text translation, Gemma4 26B Q8 is excellent.

For debugging code, I sometimes use Gemma4 31B; it's a great detective.

For simple tasks like HTML templates or design, the fast Qwen3.6 35B Q8 works well.

The machine is a Strixhalo 128GB.

> 5
> 
> 
> 
> [u/Nyghtbynger](https://redlib.catsarch.com/user/Nyghtbynger)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0icqax/?context=3#p0icqax "Jul 29 2026, 17:34:34 UTC")
> 
> I agree with gemma 31B. Is Gemma Q8 better than the Q4 from unsloth ?
> 
> 
> > 5
> > 
> > 
> > 
> > [u/_TheWolfOfWalmart_](https://redlib.catsarch.com/user/_TheWolfOfWalmart_)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0jixka/?context=3#p0jixka "Jul 29 2026, 20:35:25 UTC")
> > 
> > Q8 is always better. It's the ideal quant if it fits They're basically lossless versus the original weights, half the size and twice the speed.
> > 
> > 
> > 
> > 3
> > 
> > 
> > 
> > [u/pabloodiablo](https://redlib.catsarch.com/user/pabloodiablo)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0jgl6s/?context=3#p0jgl6s "Jul 29 2026, 20:25:08 UTC")edited 20d ago
> > 
> > Q8 > Q4 ALWAYS. Sometimes very similar but not equal
> 
> 
> 
> 2
> 
> 
> 
> [u/iForgotso](https://redlib.catsarch.com/user/iForgotso)[19d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0o7xfw/?context=3#p0o7xfw "Jul 30 2026, 14:00:03 UTC")
> 
> You reckon Laguna is fairing better than qwen3.6 27b 18 or about the same?
> 
> 
> I bought a strix halo laptop recently and finishing up my setup. Was initially trying ornith 35b, but got stuck in a few infinite loops and ended up discarding it. I'm currently running 27B Q8 with MTP at around 15tok/s, it's slow but seems much better until now.
> 
> 
> I imagine Laguna would be faster and theoretically better, albeit at Q6 instead of Q8, my main usages would be scripting/coding, and offensive security work, both on libre chat, opencode and Hermes as harnesses. Do you reckon it's worth a try?
> 
> 
> > 2
> > 
> > 
> > 
> > [u/pabloodiablo](https://redlib.catsarch.com/user/pabloodiablo)[19d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0qacw6/?context=3#p0qacw6 "Jul 30 2026, 19:19:08 UTC")
> > 
> > To be honest, Qwen3.6 27B Q8 is the main engine of my workflow when it comes to local LLMs. I delegated tasks to Laguna if Qwen took too long to think or got stuck on a problem. In those cases, the second engine would pull through. Sometimes I use Gemma 4 31B; it's a solid engine for existing code, performs well at refactoring, and is good at spotting issues.
> > 
> > 
> > > 2
> > > 
> > > 
> > > 
> > > [u/iForgotso](https://redlib.catsarch.com/user/iForgotso)[19d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0qt50t/?context=3#p0qt50t "Jul 30 2026, 20:39:58 UTC")
> > > 
> > > Thanks for your input, I guess I'll stick with 27B for now then. It's not fast by any means, but I'll just assign some work to it and let it roll for as long as it wants. Laguna being Q6 doesn't give me much confidence either way.
> > > 
> > > 
> > > Thanks again, have a great one!

13

[u/ttkciar](https://redlib.catsarch.com/user/ttkciar)llama.cpp[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0iupzq/?context=3#p0iupzq "Jul 29 2026, 18:50:18 UTC")

Despite its age, GLM-4.5-Air is still my go-to model for a wide variety of STEM tasks, mostly on the strength of its instruction-following competence.

My other main go-to model is the comparatively new Gemma-4-31B-it. Like Gemma-3-27B before it, it exhibits an extremely diverse range of skills, and is especially good at "soft" tasks. Its codegen competence isn't high enough to be my primary codegen model, but it has proven to be a superb debugger. GLM-4.5-Air writes/edits the code, and Gemma-4-31B-it finds and fixes its bugs.

Qwopus3.5-122B-A10B-Kimi-K2.6-destill-healed-abliterated has found a lasting niche in my model lineup for some kinds of assistant tasks, especially for biochem and organic chemistry.

I'd like to drop Big-Tiger-Gemma-27B-v3, but have yet to find a Gemma4 fine-tune with comparable anti-sycophancy characteristics. I've continued using it for tasks which specifically require anti-sycophancy.

Another older model which keeps giving is K2-V2-Instruct, due to its high context limit (512K) and superb long-context competence. I use it for data analysis, especially system log analysis and chat log analysis. It also excels at RAG tasks, but in practice it is too slow on my hardware for most RAG tasks, and I use Gemma-4-31B-it instead.

A relatively new addition is MiniMax-M2.7, which is much, much better than GLM-4.5-Air at creative problem-solving and planning. I am developing planning workflows around it, and unless a better contender pops up in a similar size class, I expect it to stick around for a while.

Also worth mentioning, TheDrummer has breathed new life into ye olde Mistral 3 Small (24B) with his Skyfall models. These are currently the ultimate development of Mistral 3 Small, and when it comes to "differently creative" tasks it can match or exceed Gemma-4-31B-it, and even surpasses TheDrummer's own Artemis-31B Gemma4 fine-tune at some tasks.

Some recent'ish models which seemed really promising at first, but I have not stuck with, include Nemotron-3-Super-120B, INTELLECT-3.1, Qwen3.5-9B, and Qwen3.6-27B.

> 2
> 
> 
> 
> [u/archieve_](https://redlib.catsarch.com/user/archieve_)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0keyo3/?context=3#p0keyo3 "Jul 29 2026, 23:11:49 UTC")
> 
> Did you try glm 4.6v. is glm 4.5 air better than 4.6v
> 
> 
> > 3
> > 
> > 
> > 
> > [u/ttkciar](https://redlib.catsarch.com/user/ttkciar)llama.cpp[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0kg0ha/?context=3#p0kg0ha "Jul 29 2026, 23:17:28 UTC")
> > 
> > They are very, very similar models. Their main differences, as far as I could tell, were:
> > 
> > 
> > *   GLM-4.6V has vision capabiliites,
> > 
> > *   GLM-4.6V has better tool-calling competence,
> > 
> > *   GLM-4.5-Air has slightly better codegen competence.
> > 
> > 
> > 
> > Since I'm not using it for vision or tool-calling tasks, but I do use it for codegen (but not agentic codegen, so tool-calling doesn't matter), I've stuck with Air.
> 
> 
> 
> 1
> 
> 
> 
> [u/CatConfuser2022](https://redlib.catsarch.com/user/CatConfuser2022)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0kavvg/?context=3#p0kavvg "Jul 29 2026, 22:50:23 UTC")
> 
> "tasks which specifically require anti-sycophancy"
> 
> 
> can you give any examples here?
> 
> 
> > 2
> > 
> > 
> > 
> > [u/ttkciar](https://redlib.catsarch.com/user/ttkciar)llama.cpp[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0kdyi0/?context=3#p0kdyi0 "Jul 29 2026, 23:06:29 UTC")
> > 
> > I described my main application for it here, and the script I implemented to perform it:
> > 
> > 
> > [https://old.reddit.com/r/LocalLLaMA/comments/1uz6388/what_small_models_have_you_guys_been_using/oyfsnjf/?context=3](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uz6388/what_small_models_have_you_guys_been_using/oyfsnjf/?context=3)
> > 
> > 
> > > 1
> > > 
> > > 
> > > 
> > > [u/CatConfuser2022](https://redlib.catsarch.com/user/CatConfuser2022)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0kfc54/?context=3#p0kfc54 "Jul 29 2026, 23:13:50 UTC")
> > > 
> > > thx!

13

[u/g_rich](https://redlib.catsarch.com/user/g_rich)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ic77y/?context=3#p0ic77y "Jul 29 2026, 17:32:21 UTC")

I’m sticking with DeepSeek v4 Flash for the foreseeable future; it’s been solid with a 384k context window running across two Sparks and I value the stability and consistency over the constant swapping to the latest and greatest.

With that being said I’ll at the very least be giving Ling 3.0 Flash a try once support has been rolled into vLLM or llama.cpp.

8

[u/FoxiPanda](https://redlib.catsarch.com/user/FoxiPanda)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0illh1/?context=3#p0illh1 "Jul 29 2026, 18:11:37 UTC")

Stay warm most/all the time:

*   Gemma-4-26B-A4B-Q8
*   Qwen-3.6-35B-A3B-Q8
*   Qwen-3.6-27B-Q8 (I also use Q5 sometimes on different hardware because of VRAM limitations)
*   Qwen3-VL-Embedding-2B
*   Qwen3-VL-Reranker-2B

Get loaded sometimes:

*   Gemma-4-31B-Q8
*   Step-3.7-Flash-Q4
*   DeepSeek-V4-Flash-IQ2XXS (antirez/ds4 variant)

Still too early to tell or "I might load it up sometimes"

*   HY3-Q4 (kinda slow on my hardware, but decent?)
*   Nemotron-Labs-3-Puzzle-75B-A9B-NVFP4 (super fast on my hardware but limited uses for things not already covered by other models.)

7

[u/Eden1506](https://redlib.catsarch.com/user/Eden1506)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0jz3fc/?context=3#p0jz3fc "Jul 29 2026, 21:50:36 UTC")

Gemma 4 26B-A4B at q6 for book translation. There is a korean author I like but not all books are translated so using a github project Translatebookswithllm I translated the whole book into english just for myself.

It took several hours but the result is decent. For anyone trying the same I recommend telling the llm to translate freely as otherwise you will get sentences that follow the original texts structure too closely and while they will make sense they won't sound like a proper English translation.

6

[u/_TheWolfOfWalmart_](https://redlib.catsarch.com/user/_TheWolfOfWalmart_)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0jgrpd/?context=3#p0jgrpd "Jul 29 2026, 20:25:56 UTC")edited 20d ago

Still using Laguna S 2.1 a lot for pure coding, but it's only been a week. Can't give a one-month impression.

Otherwise, Qwen3.6 27B and 35B-A3B, Gemma 31B and 26B-A4B are still mainstays. It depends exactly what I'm doing.

Also, I use GLM-4.5-Air a lot still. it's a bit old now, but still a beast and fast for a 120B model.

And Deepseek V4 Flash.

4

[u/Nice_Cookie9587](https://redlib.catsarch.com/user/Nice_Cookie9587)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0if3il/?context=3#p0if3il "Jul 29 2026, 17:44:28 UTC")

I keep finding myself coming back to dsv4 flash. i tried laguna (updated model), m3 , qwen3.6:27 and 35b but always go back to dsv4 flash. everything kinda sucks compared to it. Only reason i keep trying others is to get multi modal support, but the rumor is that dsv4 flash will get tht soon when its out of preview status

5

[u/DiscipleofDeceit666](https://redlib.catsarch.com/user/DiscipleofDeceit666)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0im8m8/?context=3#p0im8m8 "Jul 29 2026, 18:14:18 UTC")

I like Laguna s2.1 a whole bunch! It makes mistakes sure, but it does deeper dives than 27b would. Comes out with bugs all missed and validated by Claude.

I’m using it as a red team pen tester, a gap finder, and a planner/spec writer. Still need to tune the planner role bc it is kind of sloppy, but still has tons of potential.

I max at 64gb vram and Laguna is the biggest model I can run.

> 1
> 
> 
> 
> [u/RISCArchitect](https://redlib.catsarch.com/user/RISCArchitect)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0is0d9/?context=3#p0is0d9 "Jul 29 2026, 18:38:42 UTC")
> 
> would you mind sharing your CLI command for laguna. last weekend i went there and back again with quants and llama.cpp variants. want to circle back around to it this coming weekend
> 
> 
> > 2
> > 
> > 
> > 
> > [u/DiscipleofDeceit666](https://redlib.catsarch.com/user/DiscipleofDeceit666)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0izvjw/?context=3#p0izvjw "Jul 29 2026, 19:12:32 UTC")
> > 
> > Yeah, let me get on a computer later and find that.
> > 
> > 
> > I guess this model gets flaky with the wrong environment and set up.
> > 
> > 
> > I’m using amd dual r9700 GPUs with llama cpp and Vulkan using unsloth iq4NL quant. As far as I know, the rest of my flags are standard and taken from poolside
> > 
> > 
> > > 1
> > > 
> > > 
> > > 
> > > [u/RISCArchitect](https://redlib.catsarch.com/user/RISCArchitect)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0jxbwg/?context=3#p0jxbwg "Jul 29 2026, 21:42:04 UTC")
> > > 
> > > thanks, im using r9700 + 9070xt so not as much vram to play with but will just go with a lower quant probably :)
> > > 
> > > 
> > > > 1
> > > > 
> > > > 
> > > > 
> > > > [u/DiscipleofDeceit666](https://redlib.catsarch.com/user/DiscipleofDeceit666)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0jz6uz/?context=3#p0jz6uz "Jul 29 2026, 21:51:04 UTC")
> > > > 
> > > > I used iq2, iq3 and iq4 quants. Iq3 finds solutions that iq2 can’t. If possible, I’d start there or bigger. Good luck!
> > > > 
> > > > 
> > > > 
> > > > 1
> > > > 
> > > > 
> > > > 
> > > > [u/cosmicnag](https://redlib.catsarch.com/user/cosmicnag)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0l770q/?context=3#p0l770q "Jul 30 2026, 01:48:53 UTC")
> > > > 
> > > > I have 32 + 24 GB Vram and I use IQ3_S by unsloth with 160k q8 context. I also use another AtomicChat IQ3_S_coding (or something like that which is nearly same size ~48GB) . The latter has a 'coding' imatrix - havent deep dived into whether it actually helps or not - but works (get slightly more 161k context also) . This is definitely very usable and I find myself using more of this than 27B (and all its finetunes). This is fully GPU resident and is faster than 27B as well, even if split between 2 GPUs (active 8B)
> > 
> > 
> > 
> > 2
> > 
> > 
> > 
> > [u/DiscipleofDeceit666](https://redlib.catsarch.com/user/DiscipleofDeceit666)[19d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0q1gsy/?context=3#p0q1gsy "Jul 30 2026, 18:40:53 UTC")
> > 
> > [![Image 2](https://redlib.catsarch.com/preview/pre/5akzjq2fwegh1.jpeg?width=4032&format=pjpg&auto=webp&s=aacf493aa9987058685a43cf6f9aefbb4a08a676)](https://redlib.catsarch.com/preview/pre/5akzjq2fwegh1.jpeg?width=4032&format=pjpg&auto=webp&s=aacf493aa9987058685a43cf6f9aefbb4a08a676)
> > Here you go.

6

[u/__JockY__](https://redlib.catsarch.com/user/__JockY__)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0iswol/?context=3#p0iswol "Jul 29 2026, 18:42:32 UTC")

In a surprise turn of events, Hy3 has turned out to be one that we “quickly tried” and it never left the GPUs. Currently running the RedHatAI/Hy3-NVFP4-FP8. It’s loved by our front end, back end, and ops people. I’ll take that for a triple threat!

In opposite-land we hoped that Laguna S 2.1 would live up to its promise, but that one was quickly dropped.

Still running Hy3, but GLM-5.2 and MiniMax-M3 are still up for trial.

3

[u/RISCArchitect](https://redlib.catsarch.com/user/RISCArchitect)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0iglhj/?context=3#p0iglhj "Jul 29 2026, 17:50:39 UTC")

Qwen 3.6 27b q8 kv16

> 2
> 
> 
> 
> [u/suprjami](https://redlib.catsarch.com/user/suprjami)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0k3z3n/?context=3#p0k3z3n "Jul 29 2026, 22:14:54 UTC")
> 
> Yep this. Why use anything else.

4

[u/robertpro01](https://redlib.catsarch.com/user/robertpro01)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0i62w3/?context=3#p0i62w3 "Jul 29 2026, 17:06:57 UTC")

Well, can't download and try locally so...

> 4
> 
> 
> 
> [u/derspenti](https://redlib.catsarch.com/user/derspenti)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0i73od/?context=3#p0i73od "Jul 29 2026, 17:11:11 UTC")
> 
> [https://x.com/vllm_project/status/2080702006378082384](https://x.com/vllm_project/status/2080702006378082384)
> 
> 
> Will be soon I guess. vllm Said: "vLLM’s open-source support for Ling-3.0-flash is coming soon"

3

u/[deleted][20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0i9yik/?context=3#p0i9yik "Jul 29 2026, 17:23:05 UTC")

[deleted]

> 2
> 
> 
> 
> [u/Kidplayer_666](https://redlib.catsarch.com/user/Kidplayer_666)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0in9fg/?context=3#p0in9fg "Jul 29 2026, 18:18:35 UTC")
> 
> I want to see a next gen qwen 9b so bad. Currently the 3.6 35A3 is the only model smart enough, but runs a bit slow

3

[u/Aggravating_Show6584](https://redlib.catsarch.com/user/Aggravating_Show6584)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0it1nc/?context=3#p0it1nc "Jul 29 2026, 18:43:06 UTC")

Tengo hardware muy limitado 32GB RAM + 5060 Ti 16GB VRAM mi stack es

 Mayormente Qwen3.6 35B A3B, enviando expertos a CPU unos 40-70 t/s

 ligeramente Qwen3.5 9B

 Gemma4 26B A4B enviando expertos a CPU unos 40-70 t/s

 ligeramente Gemma4 12B

Se me complican Gemma4 31B y Qwen3.6 27B

 tengo una vieja RX6600 de 8GB quizás debería probarlas juntas con vulkan, seguro que funciona.

Además si tengo una duda más fuerte y es sobre un modelo quizás más pesadito pero juntar AMD + NVIDIA + CPU y ver si es un buen movimiento. seria 15GB de NVIDIA + 8GB AMD +20GB de RAM = 43GB aprox quizás para un mejor MoE o Denso que quepa ahí.

3

[u/PotentialAccident339](https://redlib.catsarch.com/user/PotentialAccident339)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0iw6zl/?context=3#p0iw6zl "Jul 29 2026, 18:56:35 UTC")

Gemini 26b a4b (with MTP). It's just good enough.

3

[u/laterbreh](https://redlib.catsarch.com/user/laterbreh)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0l4kqg/?context=3#p0l4kqg "Jul 30 2026, 01:33:56 UTC")

DS4 Flash with DSpark. Absolute sleeper of a model that churns 200 tps on my hardware, ive practically abandoned looking at hugging face and any other model. All local running agentic loops all day long for the cost of electricity. Raw 160gb dspark release on 2x rtx 6000's with vllm.

2

[u/ZestycloseTie1793](https://redlib.catsarch.com/user/ZestycloseTie1793)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0irrr1/?context=3#p0irrr1 "Jul 29 2026, 18:37:41 UTC")

This is the evaluation window I wish model cards included. A simple retention template could make replies comparable: task, hardware, quant, context, week-1 success rate, week-4 success rate, failures/rework, and why it stayed. Tok/s alone misses how much babysitting a model needs. A model at 7 t/s that finishes cleanly can beat a 20 t/s model that needs three retries.

2

[u/o0genesis0o](https://redlib.catsarch.com/user/o0genesis0o)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0koe18/?context=3#p0koe18 "Jul 30 2026, 00:03:17 UTC")

Local on my rig with 4060ti: qwen 3.6 35B A3B unsloth q4 xl quant.

I also keep Q2 27B from the previous time I compared against the bonsai ternary. Also keep Gemma4 12B and 26B QAT. Though no use at the moment.

Local on my mini pc with 6900hx and 32GB ddr5: Gemma4 26B QAT. Slow but not unbearable. This is a back up for when everything else is down.

Cloud for coding: minimax m3. When their infrastructure does not act up, they are pretty reliable for 20 bucks a month. At off peak, the can decode up to 70tk/s, and prefill is thousands tk/s. Both faster and smarter than what I host locally, sadly.

1

[u/Look_0ver_There](https://redlib.catsarch.com/user/Look_0ver_There)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ilz5b/?context=3#p0ilz5b "Jul 29 2026, 18:13:11 UTC")

Oh, were the weights released yet?

1

[u/Livid-Heat-2475](https://redlib.catsarch.com/user/Livid-Heat-2475)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ja3m2/?context=3#p0ja3m2 "Jul 29 2026, 19:56:49 UTC")

Tried swapping my daily driver three times this year, Qwen, GLM, and one release I wont name since the license shifted twice. The boring 27B class model for anything structured is what's still running though. Stopped being exciting around week two, which is exactly why it stuck. My read is day one hype and month two retention measure different things, mostly inference stability under real prompts, not benchmark score. The two agent frameworks I was sure would replace my workflow both died within a month.

1

[u/ShannonBase](https://redlib.catsarch.com/user/ShannonBase)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0l93db/?context=3#p0l93db "Jul 30 2026, 01:59:47 UTC")

deepseek v4-pro, and claude, for me

1

[u/bizhonggeng](https://redlib.catsarch.com/user/bizhonggeng)[20d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0ltcp3/?context=3#p0ltcp3 "Jul 30 2026, 04:05:06 UTC")

Due to limited VRAM, in the local model, I primarily use the qwen3.6-35B moe for encoding, Gemma-4-E4B for text polishing, and Hy-MT2 for translation.

1

[u/Gotxi](https://redlib.catsarch.com/user/Gotxi)[19d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0myvg8/?context=3#p0myvg8 "Jul 30 2026, 09:34:54 UTC")

RX 9700 XT 16 GB user here, this is my actual models.ini for my llama.cpp stack:

```
version = 1

[*]
host = 127.0.0.1
metrics = true
jinja = true
flash-attn = on
parallel = 1
no-warmup = true

cache-type-k = q8_0
cache-type-v = q8_0
cache-prompt = true
cache-reuse = 0
cache-ram = 0

batch-size = 2048
ubatch-size = 1024

threads = 8
threads-batch = 8

no-mmap = true

ctx-checkpoints = 5
checkpoint-min-step = 32768

spec-type = draft-mtp,ngram-mod
spec-draft-n-max = 2

temp = 0.2
top-p = 0.9
top-k = 20
min-p = 0.05

reasoning = on

fit = off
n-gpu-layers = 999

[Ornith-1.0-35B-MTP-APEX-I-Compact]
model = /home/gotxi/models/ornith/Ornith-1.0-35B-MTP-APEX-I-Compact.gguf
ctx-size = 200000
n-cpu-moe = 16

[Ornith-131k]
model = /home/gotxi/models/ornith/Ornith-1.0-35B-MTP-APEX-I-Compact.gguf
ctx-size = 100000
n-cpu-moe = 12

[Qwen3.6-35B-A3B]
model = /home/gotxi/models/qwen/Qwen3.6-35B-A3B-uncensored-heretic-Native-MTP-Preserved-APEX-I-Compact.gguf
ctx-size = 100000
n-cpu-moe = 12

temp = 1.0
top-p = 1.0
top-k = 40
presence-penalty = 2.0

[Qwen3.6-35B-A3B-DFlash]
model = /home/gotxi/models/qwen/Qwen3.6-35B-A3B-UD-IQ4_XS.gguf
model-draft = /home/gotxi/models/qwen/Qwen3.6-35B-A3B-DFlash-Q8_0.gguf
spec-type = draft-dflash
spec-draft-n-max = 3
ctx-size = 100000

[Qwen3.6-27B-mini-IQ4_XS-MTP]
model = /home/gotxi/models/qwen/Qwen3.6-27B-16GB-VRAM-MTP-mini-IQ4_XS.gguf

ctx-size = 32768
batch-size = 2048
ubatch-size = 1024

fit = off
n-gpu-layers = 999

threads = 8
threads-batch = 8

cache-type-k = q8_0
cache-type-v = q4_0

spec-draft-type-k = q4_0
spec-draft-type-v = q4_0

spec-type = draft-mtp
spec-draft-n-max = 2

[Qwen3.6-27B-4bpw-16GB-VRAM]
model = /home/gotxi/models/qwen/Qwen3.6-27B-4bpw-16GB-VRAM.gguf

ctx-size = 32768
batch-size = 2048
ubatch-size = 1024

no-mmproj = true

fit = off
n-gpu-layers = 999

kv-unified = true

cache-ram = 0

threads = 8
threads-batch = 8

spec-type = ngram-mod
spec-ngram-mod-n-match = 24
spec-ngram-mod-n-min = 12
spec-ngram-mod-n-max = 64
```

All of these have pros and cons, my daily driver is Qwen3.6-35B-A3B with MTP, as it gives me the most speed while still being smart enough.

I would prefer to run qwen3.6 27b dense, but speed drops in half and I have 1/4 of context size, so it does not work for my typical use case as I get out of context super quick.

Ornith works fine, but it tends to do infinite loops way too often. I have a harness on my [pi.dev](http://pi.dev/) client with an anti-loop plugin that fixes this, but still wastes time re-computing things it should not. Qwen does that way less often, so it is more usable in the end.

For my current stack, Dflash, Dspark, Eagle3 and other speculative decoding methods are not superior to MTP, so that's what I stick with.

I have tried many LLM's, quantizations and sizes and I still come back to Qwen3.6.

I am eager to see open weights for Qwen3.7 or Qwen3.8 and test them!

1

[u/AvantiGrowthLab](https://redlib.catsarch.com/user/AvantiGrowthLab)[19d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0n2qh2/?context=3#p0n2qh2 "Jul 30 2026, 10:05:49 UTC")

The pattern I keep noticing: the flashy stuff (model of the week, the clever agent framework) churns out fast, and the boring infrastructure is what actually sticks. A month later I don't care which model topped a benchmark — I care about the plumbing that keeps cost + latency predictable: caching the static prefix, keeping context lean, a couple of eval traces I re-run so I catch regressions. My honest answer to "what's still in the stack" is mostly unglamorous glue, not models. Anyone find the opposite — something shiny that actually earned its keep past week one?

1

[u/MerePotato](https://redlib.catsarch.com/user/MerePotato)[19d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0o1ozx/?context=3#p0o1ozx "Jul 30 2026, 13:31:06 UTC")

Gemma 4 31B remains my go-to

1

[u/WhoRoger](https://redlib.catsarch.com/user/WhoRoger)[19d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0oqpyv/?context=3#p0oqpyv "Jul 30 2026, 15:23:24 UTC")

I find it interesting how I've seen multiple mentions of Ling/Ring in the last week or so, while I've never seen anyone talk about it before. Is it just the case that once you notice something once, you keep seeing it?

Or is it one of those models that doesn't get much attention when new, but actually survives long-term?

1

[u/DoctorTruthSeeker](https://redlib.catsarch.com/user/DoctorTruthSeeker)[19d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1va1zoc/everyone_posts_dayone_impressions_whats_still_in/p0p19y4/?context=3#p0p19y4 "Jul 30 2026, 16:08:14 UTC")edited 19d ago

I’m really new to the scene of local LLMs and consider myself to be a non-technical but deeply thinking and inquisitive novice AI hobbyist. This post significantly caught my interest as I am really trying to build a long term sustainable AI agentic operating system but I don’t have a technical background. I am not interested in BS AI hype and looking for time tested and true/accurate information regarding this.

You mentioned using a certain model as an “executor”, which touches on some fundamental basics I know that I am lacking.

What are the typically different “roles” on people’s set ups? I’d love a brief overview of this from experienced users that I just can’t get from asking an LLM. I’ve heard of “routers”, “executor”, RAG/semantic search, transcription, etc. but I still don’t really understand the bigger picture I’m trying to get to of what roles are largely consistent and necessary across most peoples set ups and why have they stood the test of time.

What value does each role offer to the system by making it distinct as opposed to combining it with another role?

I presume sometimes it’s cost, speed, efficiency, security, but at the end of the day, I am a strong believer that the best systems are the most simplistic and any added complexity needs to provide significant value and “earn its keep”.

Hope to learn from the diverse perspectives of the amazing experienced people in this subreddit who take the time to add meaningful input/contributions :)

v0.36.0 [ⓘ View instance info](https://redlib.catsarch.com/info "View instance information")[<> Code](https://github.com/redlib-org/redlib "View code on GitHub")
