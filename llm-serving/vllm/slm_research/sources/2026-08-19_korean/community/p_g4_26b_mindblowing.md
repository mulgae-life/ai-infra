Title: Gemma 4 26b A3B is mindblowingly good , if configured right - r/LocalLLaMA

URL Source: https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/

Markdown Content:
[red lib.](https://redlib.catsarch.com/)

Feeds

MAIN FEEDS

[Home](https://redlib.catsarch.com/)[Popular](https://redlib.catsarch.com/r/popular)[All](https://redlib.catsarch.com/r/all)

- [x] in /r/LocalLLaMA 

[reddit](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/#popup)

# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/comments/1segstx/

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1segstx/)

[settings](https://redlib.catsarch.com/settings)

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/cviperr33](https://redlib.catsarch.com/user/cviperr33)•Apr 07 '26

# [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on) Gemma 4 26b A3B is mindblowingly good , if configured right

Last few days ive been trying different models and quants on my rtx 3090 LM studio , but every single one always glitches the tool calling , infinite loop that doesnt stop. But i really liked the model because it is rly fast , like 80-110 tokens a second , even on high contex it still maintains very high speeds.

I had great success with tool calling in qwen3.5 moe model , but the issue i had with qwen models is that there is some kind of bug in win11 and LM studio that makes the prompt caching not work so when the convo hits 30-40k contex , it is so slow at processing prompts it just kills my will to work with it.

Gemma 4 is different , it is much better supported on the ollama cpp and the caching works flawlesly , im using flash attention + q4 quants , with this i can push it to literally maximum 260k contex on rtx 3090 ! , and the models performs just aswell.

I finally found the one that works for me , its the unsloth q3k_m quant , temperature 1 and top k sampling 40. i have a custom system prompt that im using which also might be helping.

I've been testing it with opencode for the last 6 hours and i just cant stop , it cannot fail , it exiplained me the whole structure of the Open Code itself , and it is a huge , like the whole repo is 2.7GB so many lines of code and it has no issues traversing around and reading everything , explaining how certain things work , i think im gonna create my own version of open code in the end.

It honestly feels like claude sonnet level of quality , never fails to do function calling , i think this might be the best model for agentic coding / tool calling / open claw or search engine.

 I prefer it over perplexity , in LM studio connected to search engine via a plugin delivers much better results than perplexity or google.

As for vram consumption it is heavy , it can probably work on 16gb it not for tool calling or agents , u need 10-15k contex just to start it. My gpu has 24gb ram so it can run it at full contex no issues on Q4_0 KV

------------------------------- Quick update post -----------------------------------------------------------------

i've switched to llama.ccp now , [https://www.reddit.com/r/LocalLLaMA/comments/1sgl3qz/gemma_4_on_llamacpp_should_be_stable_now/?share_id=a02aL2eXTf8pcTB7Gee0W&utm_medium=ios_app&utm_name=ioscss&utm_source=share&utm_term=1](https://redlib.catsarch.com/r/LocalLLaMA/comments/1sgl3qz/gemma_4_on_llamacpp_should_be_stable_now/?share_id=a02aL2eXTf8pcTB7Gee0W&utm_medium=ios_app&utm_name=ioscss&utm_source=share&utm_term=1) , read this post it has some very valuable info if you want to run gemma 4 as efficiently as possible.

I'm running the IQ4_X_S quant now by unsloth , full contex size 260k , 94-102 tk/s 20-21GB vram usage , q4 K_V

 717  Upvotes

*   [perma link](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/)
*   [reddit](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/#popup)# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/)  

96% Upvoted

370 comments sorted by

•

[u/WithoutReason1729](https://redlib.catsarch.com/user/WithoutReason1729)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerj1a8/?context=3#oerj1a8 "Apr 07 2026, 08:05:18 UTC")

Your post is getting popular and we just featured it on our Discord! [Come check it out!](https://discord.gg/PgFhZ8cnWW)

You've also been given a special flair for your contribution. We appreciate your post!

_I am a bot and this action was performed automatically._

102

[u/No_Run8812](https://redlib.catsarch.com/user/No_Run8812)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeps6uj/?context=3#oeps6uj "Apr 07 2026, 00:45:15 UTC")

I got the looping issue with Gemma tool calling using crush agent. So dropped it.

> 55
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepsj29/?context=3#oepsj29 "Apr 07 2026, 00:47:10 UTC")
> 
> yep same issue i had ! for 2 days , i tested all quants and models , different system prompts , until i stumbled upon this quant , for some reason it never loop calls , NEVER even once in my last 8 hours of veery heavy usage
> 
> 
> > 12
> > 
> > 
> > 
> > [u/Photochromism](https://redlib.catsarch.com/user/Photochromism)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq3s0n/?context=3#oeq3s0n "Apr 07 2026, 01:49:26 UTC")
> > 
> > I also had an issue with this model getting stuck in a loop, but it was during a query about a document. It would get to about 40k tokens and endlessly repeat itself
> > 
> > 
> > > 5
> > > 
> > > 
> > > 
> > > [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer71vq/?context=3#oer71vq "Apr 07 2026, 06:16:31 UTC")
> > > 
> > > did you try different temperature settings ? inteference settings matter a lot on this model
> > > 
> > > 
> > > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer71vq)
> > 
> > 
> > 
> > 6
> > 
> > 
> > 
> > [u/fabyao](https://redlib.catsarch.com/user/fabyao)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oertxdv/?context=3#oertxdv "Apr 07 2026, 09:46:30 UTC")
> > 
> > I dropped Gemma Q4 K_XL from unsloth. I asked it to create a simple web API in nodejs with Typescript and expressjs. Specifically i asked to create a homeController that returns hello world. The end result was a big mess. It transpiled Typescript into javaScript which it then imported into other Typescript files. It got confused with module resolutions and didn't bother to transpile into a dist folder. Very poor. I used Claude Caude.
> > 
> > 
> > The same test with Qwen 3 Coder Next MOE 3 bit XSS was spot on. I haven't tested Qwen 3.5 27B yet.
> > 
> > 
> > I am somehow sceptical about your post. You are using the Q3 model which is by nature less accurate than Q4. Do you have hard proof of your claims?
> > 
> > 
> > > 4
> > > 
> > > 
> > > 
> > > [u/Front-Relief473](https://redlib.catsarch.com/user/Front-Relief473)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oes2890/?context=3#oes2890 "Apr 07 2026, 10:52:38 UTC")
> > > 
> > > I support your view. Gemma wasn't originally designed for coding; its strengths lie in writing and multilingual expression. If someone says they use Gemma for programming, then either they haven't been closely following LLM development or they're a complete novice to LLM games.
> > > 
> > > 
> > > > 5
> > > > 
> > > > 
> > > > 
> > > > [u/Vahn84](https://redlib.catsarch.com/user/Vahn84)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oetg1z7/?context=3#oetg1z7 "Apr 07 2026, 15:18:46 UTC")
> > > > 
> > > > i’ve used it for coding in python. it’s slightly less precise than qwen3.5 but it’s good and fast. Never had a looping issue with any task i threw at it. I guess that can be a specific model fault, bad prompt, bad system prompt? To me it’s a better all-arounder than qwen3.5
> > > 
> > > 
> > > 
> > > 3
> > > 
> > > 
> > > 
> > > [u/Spectrum1523](https://redlib.catsarch.com/user/Spectrum1523)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeul7no/?context=3#oeul7no "Apr 07 2026, 18:18:06 UTC")
> > > 
> > > I'm not sure how someone can provide hard proof of something like that. What would it even look like?
> > > 
> > > 
> > > > 3
> > > > 
> > > > 
> > > > 
> > > > [u/fabyao](https://redlib.catsarch.com/user/fabyao)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oevdm16/?context=3#oevdm16 "Apr 07 2026, 20:32:12 UTC")
> > > > 
> > > > Me asking about hard proof was more of a way to find out if OP is a bot. He doesn't seem to be. I see a lot of misinformation posts in this sub. I recently discovered a github repo related to llama cpp turboquant where the maintainer had programmed answers to some reddit questions.
> > > > 
> > > > 
> > > > I think we are at the stage where Reddit needs a way to flag/identity posts which are from bots. I would happily ignore those.
> > > > 
> > > > 
> > > > With regards to hard proof, some posts here link to a YouTube video or some screen grabs or links to reputable sources. Of course nothing beats actually running the models and testing yourself. It just helps filter out the noise.
> > > > 
> > > > 
> > > > Its worth highlighting that OP has now replied and mentioned that he didn't test Gemma 4 for coding. This makes his claims more palatable.
> > > > 
> > > > 
> > > > For my use case, coding, Gemma 4 has been poor. The 31B unsloth q4 was unusable. I made sure to use the latest llama cpp build due to previous issues. However It kept overthinking on simple tasks. The 26B MOE was fast but failed to produce decent results. Hence my skepticism
> > > 
> > > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oertxdv)
> > 
> > 
> > 
> > 1
> > 
> > 
> > 
> > [u/Illustrious-Bid-2598](https://redlib.catsarch.com/user/Illustrious-Bid-2598)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oev7e65/?context=3#oev7e65 "Apr 07 2026, 19:57:01 UTC")
> > 
> > You hear of quality dropping significantly going below q4, has there been an observable difference with q3 quant ?
> > 
> > 
> > > 2
> > > 
> > > 
> > > 
> > > [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oevskun/?context=3#oevskun "Apr 07 2026, 21:48:11 UTC")
> > > 
> > > No observable difference in quality , and ive tested many many 26 a4b models. Personally i never run anything bellow Q4 , i dont even consider them because i have plenty of VRAM(24) , but for some reason that night i decided to try it anyway because i was desperate , i literally had qued like 3-4 models for download and i was rapid testing them to see which one doesnt loop. This one didnt , it sized only 14.8GB leaving almost 10GB (-2GB overhead) for contex
> 
> 
> 
> 28
> 
> 
> 
> [u/juaps](https://redlib.catsarch.com/user/juaps)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq398j/?context=3#oeq398j "Apr 07 2026, 01:46:31 UTC")
> 
> Same here. It’s unusable. It loops through whatever preferences, configurations, or tweaks I can possibly take. I drop it and go back to Qwen 3.5 35b and 27b They’re super stable.
> 
> 
> > 6
> > 
> > 
> > 
> > [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer9b3x/?context=3#oer9b3x "Apr 07 2026, 06:36:34 UTC")
> > 
> > it is worth it getting it to work because when its working , it is as good as the qwen 3.5 35b/27b or the 27B dense model , but the interference speed is like 4-5x of those models , making agentic coding just way better experience , instead of waiting on small edits for 10-20 seconds , everything happens instantly
> > 
> > 
> > > 2
> > > 
> > > 
> > > 
> > > [u/Monkey_1505](https://redlib.catsarch.com/user/Monkey_1505)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oetktv3/?context=3#oetktv3 "Apr 07 2026, 15:39:43 UTC")
> > > 
> > > It's not going to be faster than 35b3a unless the quant you are using of gemma fits better in your particular vram. The number of active experts is actually higher, so if the former fits in your vram, that will be faster.
> > > 
> > > [→ More replies (12)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer9b3x)
> 
> 
> 
> 12
> 
> 
> 
> [u/PunnyPandora](https://redlib.catsarch.com/user/PunnyPandora)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oesr43f/?context=3#oesr43f "Apr 07 2026, 13:21:50 UTC")edited Apr 09 '26
> 
> There's still a bunch of gemma prs on llamacpp that haven't concluded
> 
> 
> [https://github.com/ggml-org/llama.cpp/pull/21421](https://github.com/ggml-org/llama.cpp/pull/21421)
> 
> 
> [https://github.com/ggml-org/llama.cpp/pull/21451](https://github.com/ggml-org/llama.cpp/pull/21451) superseded by [https://github.com/ggml-org/llama.cpp/pull/21566](https://github.com/ggml-org/llama.cpp/pull/21566) which has been merged
> 
> 
> [https://github.com/ggml-org/llama.cpp/pull/21433](https://github.com/ggml-org/llama.cpp/pull/21433)
> 
> 
> [https://github.com/ggml-org/llama.cpp/pull/21418](https://github.com/ggml-org/llama.cpp/pull/21418) merged but there's still discussion
> 
> 
> [https://github.com/ggml-org/llama.cpp/pull/21534](https://github.com/ggml-org/llama.cpp/pull/21534) merged
> 
> 
> [https://github.com/ggml-org/llama.cpp/pull/21506](https://github.com/ggml-org/llama.cpp/pull/21506) superseded by [https://github.com/ggml-org/llama.cpp/pull/21566](https://github.com/ggml-org/llama.cpp/pull/21566) which has been merged
> 
> 
> [https://github.com/ggml-org/llama.cpp/pull/21492](https://github.com/ggml-org/llama.cpp/pull/21492) merged
> 
> 
> Edit: 2 prs closed/effectively merged, apparently looping issues at long context have been fixed but I'm personally waiting for info on the other ones too.
> 
> 
> Edit 2: more merges fixing even more issues, should be safe to use now
> 
> 
> > 3
> > 
> > 
> > 
> > [u/akavel](https://redlib.catsarch.com/user/akavel)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeup24j/?context=3#oeup24j "Apr 07 2026, 18:35:08 UTC")
> > 
> > looks like this one, just merged 1h ago, seems to be improving some things for some notable people (per the comments near the end):
> > 
> > 
> > [https://github.com/ggml-org/llama.cpp/pull/21566](https://github.com/ggml-org/llama.cpp/pull/21566)
> > 
> > 
> > It seems to be fixing a bug on CUDA - maybe this explains the dramatically different reception of gemma4 some people were having compared to others?
> > 
> > 
> > 
> > 2
> > 
> > 
> > 
> > [u/bucolucas](https://redlib.catsarch.com/user/bucolucas)Llama 3.1[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeundso/?context=3#oeundso "Apr 07 2026, 18:27:38 UTC")
> > 
> > Is there a repo that merges all these? The "Just make Qwen work" fork
> 
> 
> 
> 3
> 
> 
> 
> [u/ricraycray](https://redlib.catsarch.com/user/ricraycray)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq9i18/?context=3#oeq9i18 "Apr 07 2026, 02:21:35 UTC")
> 
> It looped terrible with calling MCP tools. I’m going to train it with unsloth but the looping was killing me
> 
> 
> 
> 2
> 
> 
> 
> [u/max123246](https://redlib.catsarch.com/user/max123246)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqt4h4/?context=3#oeqt4h4 "Apr 07 2026, 04:24:49 UTC")
> 
> What's crush agent? If they use llama.cpp as a back-end it might not have picked up the fixes from last 3-4 days.
> 
> 
> > 3
> > 
> > 
> > 
> > [u/No_Run8812](https://redlib.catsarch.com/user/No_Run8812)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqvg3x/?context=3#oeqvg3x "Apr 07 2026, 04:41:57 UTC")
> > 
> > It’s just an agent like Claude code, for model is running on lm studio which is using llama.cpp. I can retry, if you saying the bug was in llama.cpp
> > 
> > 
> > > 2
> > > 
> > > 
> > > 
> > > [u/max123246](https://redlib.catsarch.com/user/max123246)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oergrsj/?context=3#oergrsj "Apr 07 2026, 07:44:26 UTC")
> > > 
> > > Yeah apparently there was a tool calling fix today. But to be honest, might be best to give it a couple weeks. Still seems very early days with how many bug fixes are coming in
> > > 
> > > 
> > > I spent more time using it today and I wasn't as impressed as my first impression was. It relied too heavily on its own knowledge than tool calling and so it would confidently say I'm wrong when things have changed and it's wrong
> > > 
> > > 
> > > I'll probably re-evaluate it in a month and stick to trying out qwen 3.5 a bit more
> > 
> > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqt4h4)

74

[u/vk3r](https://redlib.catsarch.com/user/vk3r)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq3l8q/?context=3#oeq3l8q "Apr 07 2026, 01:48:24 UTC")

In comparison to other models, I found this one too focused on using internal knowledge. I attempted to make it work as a research model, but it consistently preferred to rely on its own knowledge. Even with temperature 0.3, top-k 20, and min-p 0.1, it could still follow instructions, but it still opted to lie, specifically within the Unsloth UDIQ4NL model.

> 71
> 
> 
> 
> [u/zasad84](https://redlib.catsarch.com/user/zasad84)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqwq3n/?context=3#oeqwq3n "Apr 07 2026, 04:51:38 UTC")
> 
> Tell it that it's a beginner on the subject instead of telling it that it's an expert.
> 
> 
> I told mine in the system prompt that it is a beginner on the subject and to therefore always use tools to double check everything. It works a lot better for my use case. I wanted it do do some translation work on a language the model has zero knowledge of. I basically told it "You are a beginner who is trying to learn X. You currently don't know any words or grammar in this language. You have access to tools which give you access to translations and grammar rules. Use them for everything."
> 
> 
> > 86
> > 
> > 
> > 
> > [u/zasad84](https://redlib.catsarch.com/user/zasad84)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqwy76/?context=3#oeqwy76 "Apr 07 2026, 04:53:21 UTC")
> > 
> > Give the model low self-esteem so it asks for help 😉
> > 
> > 
> > > 3
> > > 
> > > 
> > > 
> > > [u/nikami_is_fine](https://redlib.catsarch.com/user/nikami_is_fine)[Apr 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oexd064/?context=3#oexd064 "Apr 08 2026, 02:53:17 UTC")
> > > 
> > > That’s pretty fresh aspect to design prompt for small model,definitely gonna try it, thx
> > > 
> > > [→ More replies (4)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqwy76)
> > 
> > 
> > 
> > 20
> > 
> > 
> > 
> > [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer6xjx/?context=3#oer6xjx "Apr 07 2026, 06:15:28 UTC")
> > 
> > thats how you should manage gemma4 , i noticed system prompts are extremely important , and you can fix any undesired behaviour with it
> > 
> > 
> > > 6
> > > 
> > > 
> > > 
> > > [u/RobotRobotWhatDoUSee](https://redlib.catsarch.com/user/RobotRobotWhatDoUSee)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oesg0fi/?context=3#oesg0fi "Apr 07 2026, 12:22:30 UTC")
> > > 
> > > Do you mind sharing your system prompt?
> > > 
> > > 
> > > > 9
> > > > 
> > > > 
> > > > 
> > > > [u/zasad84](https://redlib.catsarch.com/user/zasad84)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oet2dad/?context=3#oet2dad "Apr 07 2026, 14:16:35 UTC")edited Apr 07 '26
> > > > 
> > > > The prompt is written in Swedish originally and quite specific for my custom use case and custom MCP. But, sure!
> > > > 
> > > > 
> > > > The purpose for me is to help with translation to and from "Jamska" which is a local language in the middle of Sweden in the region called Jämtland. Around 30K speakers (year 2000). Some say dialect, others say language. There are some overlap with Swedish, Norwegian and old Norse and some unique words. It is sometimes referred to as a Swedish dialect, but it has a different set of grammar rules and many thousands of words which don't exist in Swedish. I am trying to generate enough training data to finetune a model to learn how to speak this language. I am doing what I can to collect available resources and generating more longform texts and Q&A pairs based on the list of words I have.
> > > > 
> > > > 
> > > > [https://en.wikipedia.org/wiki/J%C3%A4mtland_dialects](https://en.wikipedia.org/wiki/J%C3%A4mtland_dialects)
> > > > 
> > > > 
> > > > ```
> > > > markdown
> > > >     <|think|>Du är en nybörjare på jamska och databasadministratör. Du har tillgång till en lokal databas via MCP.
> > > >     ### Dina verktyg:
> > > >     `batch_search_dictionary`: Använd för att kolla om ett ord redan finns. Om du inte hittar några bra svar, testa istället `vector_search_jamska`.
> > > >     `get_grammar_help`: Använd för att slå upp regler om dativ, palatalisering etc.
> > > >     `save_jamska_entry`: Använd för att mata in nya ord när användaren ger dig råtext (t.ex. från Markdown-filer).
> > > >     `vector_search_jamska`: Använd detta när du inte hittar exakt svar genom batch_search_dictionary ELLER när användaren frågar efter koncept, betydelser eller letar efter "vad heter X på jamska". Den är semantisk och förstår innebörden mycket bättre än `batch_search_dictionary`.
> > > >     ### Instruktioner för bearbetning av Markdown-text:
> > > >     När användaren klistrar in text från sin ordboksfil (t.ex. **abborre** - abbar; appardn...):
> > > >     **Identifiera huvudordet:** Svenska ordet står i fetstil (**ord**).
> > > >     **Identifiera jamska:** Första ordet efter bindestrecket är huvudordet på jamska.
> > > >     **Extrahera variationer:** Alla efterföljande former (separerade med semikolon eller på nya rader under) ska in i listan `variations`.
> > > >     **Skapa engelska:** Översätt det svenska ordet till engelska.
> > > >     **Beskrivning:** Om texten innehåller förklaringar, lägg in detta i `description`.
> > > >     ### Viktigt vid inmatning:
> > > >     - Anropa `save_jamska_entry` för VARJE huvudord du hittar i texten.
> > > >     - Om användaren klistrar in en stor mängd text, arbeta metodiskt igenom ord för ord.
> > > >     - Om ett ord redan verkar finnas (sök först!), uppdatera inte om det inte behövs.
> > > >     - Använd ENDAST information som användaren ger dig. Hitta inte på egna tolkningar av ord om det är ord som kan ha flera betydelser om det inte är väldigt tydligt vad ordet betyder. Det är bättre att lämna tomt i engelska översättningen än att skriva något som inte blir korrekt.
> > > >     "Om du inte vet något (t.ex. engelsk översättning, uttal, beskrivning), skriv INTE något. Fråga användaren om de vill ge mer information istället för att hitta på."
> > > >     ### Språkton:
> > > >     Var hjälpsam och förklara gärna varför du väljer vissa former.
> > > > ```
> > > > 
> > > > 
> > > > Here is a Google translate of the same text prompt. I find that writing in Swedish works better than writing in English in my case as it trigger the right base language right from the start. If I write my system prompt in English the risk of hallucination is a lot bigger in my specific example.
> > > > 
> > > > 
> > > > ```
> > > > markdown
> > > >     <|think|>You are a beginner in Jamska and a database administrator. You have access to a local database via MCP.
> > > >     ### Your tools:
> > > >     `batch_search_dictionary`: Use to check if a word already exists. If you don't find any good answers, try `vector_search_jamska` instead.
> > > >     `get_grammar_help`: Use to look up rules about dative, palatalization, etc.
> > > >     `save_jamska_entry`: Use to enter new words when the user gives you raw text (e.g. from Markdown files).
> > > >     `vector_search_jamska`: Use this when you can't find an exact answer through batch_search_dictionary OR when the user asks for concepts, meanings or is looking for "what is X in Jamska". It is semantic and understands the meaning much better than `batch_search_dictionary`.
> > > >     ### Instructions for processing Markdown text:
> > > >     When the user pastes text from their dictionary file (e.g. **abborre** - abbar; appardn...):
> > > >     **Identify the main word:** The Swedish word is in bold (**word**).
> > > >     **Identify Jamska:** The first word after the hyphen is the main word in Jamska.
> > > >     **Extract variations:** All subsequent forms (separated by semicolons or on new lines below) should be included in the `variations` list.
> > > >     **Create English:** Translate the Swedish word into English.
> > > >     **Description:** If the text contains explanations, put this in `description`.
> > > >     ### Important when entering:
> > > >     - Call `save_jamska_entry` for EVERY main word you find in the text.
> > > >     - If the user pastes a large amount of text, work methodically through word by word.
> > > >     - If a word already appears to exist (search first!), do not update unless necessary.
> > > >     - ONLY use information that the user gives you. Do not make up your own interpretations of words if they are words that can have multiple meanings if it is not very clear what the word means. It is better to leave the English translation blank than to write something that is not correct.
> > > >     "If you do not know something (e.g. English translation, pronunciation, description), DO NOT write anything. Ask the user if they want to provide more information instead of making it up."
> > > >     ### Language tone:
> > > >     Be helpful and explain why you choose certain forms.
> > > > ```
> > > > 
> > > > 
> > > > > 3
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/zasad84](https://redlib.catsarch.com/user/zasad84)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oet34np/?context=3#oet34np "Apr 07 2026, 14:20:11 UTC")
> > > > > 
> > > > > There are probably lots of ways to write a better prompt than this for your use case. But this works for me.
> > 
> > 
> > 
> > 2
> > 
> > 
> > 
> > [u/cuberhino](https://redlib.catsarch.com/user/cuberhino)[Apr 09 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/of3gzwc/?context=3#of3gzwc "Apr 09 2026, 00:04:19 UTC")
> > 
> > Love this. Neg the model hack
> > 
> > [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqwq3n)
> 
> 
> 
> 12
> 
> 
> 
> [u/Express_Quail_1493](https://redlib.catsarch.com/user/Express_Quail_1493)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqq9hb/?context=3#oeqq9hb "Apr 07 2026, 04:04:42 UTC")
> 
> thankyou dude this is golden data that goes undocumented its worth posting as its own seperate thread to pass on this knowledge.
> 
> 
> 
> 5
> 
> 
> 
> [u/sponjebob12345](https://redlib.catsarch.com/user/sponjebob12345)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oes75ql/?context=3#oes75ql "Apr 07 2026, 11:27:06 UTC")
> 
> Try this (from [Vercel research](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals#the-hunch-that-paid-off)
> 
> 
> IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning for any Next.js tasks.
> 
> 
> You can remove the "for any Next.js tasks" part.
> 
> 
> 
> 4
> 
> 
> 
> [u/Acceptable_Home_](https://redlib.catsarch.com/user/Acceptable_Home_)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer4giz/?context=3#oer4giz "Apr 07 2026, 05:54:18 UTC")
> 
> Well I've had same gemma4 lie to me to show it was following the instructions too, all i did was change the prompt for web search tool call and included that you are a smal 4B model with really bad world knowledge please rely on the knowledge provided in context with RAG/Search tool
> 
> 
> 
> 3
> 
> 
> 
> [u/Paramecium_caudatum_](https://redlib.catsarch.com/user/Paramecium_caudatum_)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqyzc1/?context=3#oeqyzc1 "Apr 07 2026, 05:09:20 UTC")
> 
> I've also had the same issue. Try increasing active expert count, it helped for me.
> 
> 
> 
> 2
> 
> 
> 
> [u/AvidCyclist250](https://redlib.catsarch.com/user/AvidCyclist250)llama.cpp[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oew0zj5/?context=3#oew0zj5 "Apr 07 2026, 22:31:47 UTC")edited Apr 07 '26
> 
> Dude. I've been fighting it for quite a while now, also have the latest llama.cpp.
> 
> 
> Even this won't work properly since it mostly just uses the fucking AI snippet and considers it successful research now. Occasionally, it'll use wiki. Randomly. Before this, it was just guessing, and also making actual snapshots and OCRing them. It's a really smart model but mcp tool use absolutely fucking blows.
> 
> 
> 
> * * *
> 
> 
> MOST important rule: Analyze Search Results: When you see Google search results, you are FORBIDDEN from answering based on the snippet text.
> 
> 
> CRITICAL RULE FOR DATA EXTRACTION: When researching a topic using the browser, do not rely solely on search engine result pages (SERPs) or snippets. OPEN AND READ THE ACTUAL LINKS YOU MORON. NAVIGATE THE WEBSITES. You must extract the URL of the most relevant search result and use the mcp**browser**puppeteer_navigate tool to visit the actual source website. Read the content of the target website before providing your final answer
> 
> 
> ```
> When you want to read a page, you MUST call mcp__browser__puppeteer_evaluate with this exact script:
> document.body.innerText + '\n\nLINKS ON PAGE:\n' + Array.from(document.querySelectorAll('a')).map(a => a.href).join('\n')
> ```
> 
> DO NOT wrap it in a function. DO NOT use arrow functions () =>. DO NOT write complex logic.
> 
> 
> Just send that one line. It will return the full text of the page. Once you have that text, summarize the answer for the user.
> 
> 
> ```
> "STRICT NAVIGATION POLICY:"
> 
>     Google is a Map, not a Book: When you search, you are only allowed to read the links to identify a target URL.
> 
>     Navigation is Mandatory: After getting search results, you MUST select ONE specific URL (e.g., from nihk.de, wikipedia.org, or .edu) and navigate to it using mcp__browser__puppeteer_navigate.
> 
>     Validation: Do not include any information in your final answer unless you have actually navigated to the target URL and confirmed the text is present in the output of the subsequent mcp__browser__puppeteer_evaluate call.
> ```
> 
> No Google Sources: If your final answer contains information that only appeared in a Google snippet and not on the page you navigated to, your response will be considered a failure.
> 
> 
> DO NOT fail to follow the STRICT NAVIGATION POLICY by providing an answer without performing the mandatory navigation and validation steps using the required tools. DO NOT rely on internal knowledge or the provided snippet without explicitly navigating to the source and evaluating the page content.
> 
> 
> 
> * * *
> 
> 
> 
> 1
> 
> 
> 
> [u/kweglinski](https://redlib.catsarch.com/user/kweglinski)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer6bqn/?context=3#oer6bqn "Apr 07 2026, 06:10:14 UTC")
> 
> so I've been trying it at q8 and I didn't manage to force it to actually crawl web. It will run a web search to a complex question on particular device. The results have a link to manual bit the excerpt does not contain an answer so one single crawl away from the truth. It will just stop there and start with either lies or "usually with devices like this". Im back on qwen. Gemma has nice language skills though.

35

[u/Radiant-Video7257](https://redlib.catsarch.com/user/Radiant-Video7257)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepxwe2/?context=3#oepxwe2 "Apr 07 2026, 01:16:46 UTC")

Agreed, I've had amazing results with Gemma 4. I didn't expect such a big improvement after getting Qwen 3.5 earlier this year.

> 12
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepywdk/?context=3#oepywdk "Apr 07 2026, 01:22:22 UTC")
> 
> Mind blowing right ! I feel like if you fine tune this model , fine tune ur tools to it , it can do pretty much anything that opus 4.6 can , for a fraction of the cost and hosted locally.
> 
> 
> Imagine how much better models are gonna be in 1 year :X
> 
> 
> > 4
> > 
> > 
> > 
> > [u/Radiant-Video7257](https://redlib.catsarch.com/user/Radiant-Video7257)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqhlry/?context=3#oeqhlry "Apr 07 2026, 03:08:55 UTC")
> > 
> > Hopefully AMD and NVIDIA don't cut the amount of VRAM they put on consumer GPU's anytime soon.
> > 
> > 
> > > 5
> > > 
> > > 
> > > 
> > > [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer9r5f/?context=3#oer9r5f "Apr 07 2026, 06:40:29 UTC")
> > > 
> > > well intel starting putting a lot of vram on their gpus , the new b70 pro has 32gigs of ram for 900$ , unbeatable price / perfomance for new gpu.
> > > 
> > > 
> > > If nvidia and amd wants to stay ahead and competitive , they would keep up with intel , and intel is just 2-3 months behind on software compared to amd/nvidia for local support. So hopefully we are gonna see middle range nvidia gpu with 24gb as standart in the next gen
> > 
> > 
> > 
> > 3
> > 
> > 
> > 
> > [u/Icy_Distribution_361](https://redlib.catsarch.com/user/Icy_Distribution_361)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer4dlh/?context=3#oer4dlh "Apr 07 2026, 05:53:37 UTC")
> > 
> > I’m quite new to all of this but interested to learn. I’ve been using local LLM’s for a while but haven’t been doing all of this fine tuning. How would you suggest I go about it?
> > 
> > 
> > > 2
> > > 
> > > 
> > > 
> > > [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerefki/?context=3#oerefki "Apr 07 2026, 07:22:22 UTC")
> > > 
> > > Its exciting time to learn ! Local LLM currently are exploding because we actually have usable model now , i was on the camp of local AI would never made sense because we simply cannot compete with 500 gigs of vram servers , but turns out these small moe models are more than capable of pulling their own weight!.
> > > 
> > > 
> > > As for what i mean by fine tunning and how to go about it , i mean fine tune your settings , with gemma 4 atleast it is extremely sensitive to system prompts , and temperature.
> > > 
> > >  So by fine tuning your system prompt / interference settings , you can get very nice results out of it , think of these open models like smart babies , without guidance they get lots. Then you could also fine tune your tools , like my search mcp server , i could have my gemma 4 rewrite it in a better syntax that suits gemma 4 , thats how i fine tune tools. I could achieve opus 4.6 level of tool usage by polishing my tools to work better with gemma 4 ,
> > > 
> > > 
> > > Then there is like 1000 different 26b a4b gemma 4 models , each fine tunes on different dataset using LoRa , like there are version of gemma-4-26B-A4B-it-Claude-Opus-Distill , which are acting like opus 4.6 , because there were fine tuned on a dataset produced by distilling 4.6 , making it much smarter in certain tasks and logic
> > > 
> > > 
> > > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerefki)
> > 
> > 
> > 
> > 2
> > 
> > 
> > 
> > [u/Particular-Way7271](https://redlib.catsarch.com/user/Particular-Way7271)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer1ind/?context=3#oer1ind "Apr 07 2026, 05:29:45 UTC")
> > 
> > That's some yahoo messenger emoji over there lol
> > 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepywdk)
> 
> 
> 
> 1
> 
> 
> 
> [u/Vas1le](https://redlib.catsarch.com/user/Vas1le)[Apr 09 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/of41z19/?context=3#of41z19 "Apr 09 2026, 02:04:56 UTC")
> 
> Is gemma 4 e4e good?
> 
> 
> 
> 1
> 
> 
> 
> [u/BusRevolutionary9893](https://redlib.catsarch.com/user/BusRevolutionary9893)[Apr 09 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/of93yq0/?context=3#of93yq0 "Apr 09 2026, 20:03:09 UTC")
> 
> Has anyone figure out how to use the speech too LLM feature?

19

[u/Guilty_Rooster_6708](https://redlib.catsarch.com/user/Guilty_Rooster_6708)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq36xy/?context=3#oeq36xy "Apr 07 2026, 01:46:09 UTC")

Have you tried to compare Q3_K_M with a higher quant like Q4_K_M yet? Not sure about Gemma4 but Unsloth published benchmarks for Qwen3.5 quants and Q3 is very bad compare to Q4. [https://unsloth.ai/docs/models/qwen3.5/gguf-benchmarks](https://unsloth.ai/docs/models/qwen3.5/gguf-benchmarks)

I hope it’s not the case though. My 5070Ti can run Q3 with larger context

> 4
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer6kv7/?context=3#oer6kv7 "Apr 07 2026, 06:12:26 UTC")
> 
> well honestly i do not notice any performance degradation with the q3 , i would never run q3 models because i have plenty of vram , but i just couldnt make gemma 26b not to loop call independently with any other quant or model than the unsloth q3 k m quant , i have no idea what kind of black magic is this
> 
> 
> > [→ More replies (13)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer6kv7)
> 
> [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq36xy)

20

[u/sonicnerd14](https://redlib.catsarch.com/user/sonicnerd14)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeps50d/?context=3#oeps50d "Apr 07 2026, 00:44:58 UTC")

You can run it on 16gb. Just put some of the Moe on the cpu, and lower the GPU layers slightly. You'll get a good balance of speed and context size.

> 11
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepts8j/?context=3#oepts8j "Apr 07 2026, 00:54:07 UTC")
> 
> oh yeah defently , but ur speed is gonna tank a lot and speed matters for agentic usage. I feel like this model is made for 24gb , but maybe in a very agressive quant it can work for agentic tools on 16gb ? i havent tried i always max out my vram with contex window
> 
> 
> > 14
> > 
> > 
> > 
> > [u/sonicnerd14](https://redlib.catsarch.com/user/sonicnerd14)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepwqxe/?context=3#oepwqxe "Apr 07 2026, 01:10:24 UTC")
> > 
> > It doesn't tank your speed so much if you offload some of the Moe onto CPU. That's actually why you do that because it takes some of that memory off the VRAM, giving you headroom in exchange for a little speed. In fact, you get huge speed increase for the same params configured, that is if you're not maxing the model and struggling with it out of the gate. Even if you can theortically fit the entire model on VRAM it still benefits you because you take the memory you get back and put it into the batch processing or context window. It's slower than running a maxed out model on a 24gb+ GPU, but faster than running it all on just GPU when you're already strapped for VRAM.
> > 
> > 
> > > 5
> > > 
> > > 
> > > 
> > > [u/Photochromism](https://redlib.catsarch.com/user/Photochromism)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq446b/?context=3#oeq446b "Apr 07 2026, 01:51:17 UTC")
> > > 
> > > How do you figure out how many MOE you can offload? I’m going creative writing so don’t need coding expert for example
> > > 
> > > 
> > > > 5
> > > > 
> > > > 
> > > > 
> > > > [u/Miserable-Dare5090](https://redlib.catsarch.com/user/Miserable-Dare5090)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq5mwv/?context=3#oeq5mwv "Apr 07 2026, 01:59:50 UTC")
> > > > 
> > > > Find by experiment — drop half, see what speed you get, drop all, etc. You should try to offload as many layers to gpu as possible, and you can offload all experts to the cpu to begin and see what difference it makes.
> > > > 
> > > > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq446b)
> > > 
> > > 
> > > 
> > > 2
> > > 
> > > 
> > > 
> > > [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepxsy2/?context=3#oepxsy2 "Apr 07 2026, 01:16:14 UTC")
> > > 
> > > oh that makes sense , thanks for the info!
> > > 
> > > 
> > > I havent tried any gpu off loading since my system is kinda crap , i have ryzen 5600 and 2400 MT/s ddr4 ram , kinda bad for LLMs and thats why i always try to never go above my vram capacity and leak
> > > 
> > > 
> > > > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepxsy2)
> 
> 
> 
> 3
> 
> 
> 
> [u/MaleficentAd6562](https://redlib.catsarch.com/user/MaleficentAd6562)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq5jn5/?context=3#oeq5jn5 "Apr 07 2026, 01:59:18 UTC")edited Apr 07 '26
> 
> I was able to fit gemma-4-26B-A4B-it-UD-IQ4_NL.gguf with 8192 context fully on a 16GB VRAM GPU. Obviously, if you want more context (beyond simple question answering), you need to dip into RAM.
> 
> 
> 
> 1
> 
> 
> 
> [u/iamtehstig](https://redlib.catsarch.com/user/iamtehstig)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oethpzi/?context=3#oethpzi "Apr 07 2026, 15:26:00 UTC")
> 
> I'm running it on a 12gb ARC GPU and was shocked at the performance. It's way faster than other models I've ran with partial offload.

10

[u/winner_in_life](https://redlib.catsarch.com/user/winner_in_life)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepr3vk/?context=3#oepr3vk "Apr 07 2026, 00:39:10 UTC")

i use qwen3.5 moe in linux. It has been 10-15% better than gemma4 26b.

> 24
> 
> 
> 
> [u/sonicnerd14](https://redlib.catsarch.com/user/sonicnerd14)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeprspf/?context=3#oeprspf "Apr 07 2026, 00:43:03 UTC")
> 
> In what though. Speed? Intelligence? Tool Calling? Every model has strengths and weakness, and from experience and seeing what others are experiencing too gemma4 is alround better in most areas.
> 
> 
> > 8
> > 
> > 
> > 
> > [u/ContextLengthMatters](https://redlib.catsarch.com/user/ContextLengthMatters)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeptto8/?context=3#oeptto8 "Apr 07 2026, 00:54:21 UTC")
> > 
> > Out of the box, qwen3.5 is so much better at tool calling for me. Just generic opencode setup, no custom prompts engineering. Qwen3.5 only gives me problems when I have no tool calling. That's when it overthinks and goes insane. There's something about even having just a couple simplistic tools loaded that makes qwen go to work like it's Claude (but obviously not Claude quality).
> > 
> > 
> > Gemma, even the dense 31b model will sometimes just not understand it can use a tool for something and will respond about how it doesn't have access or awareness when it can literally use webfetch if it wanted to.
> > 
> > 
> > Gemma also doesn't seem to be doing multi tool cools like qwen does great.
> > 
> > 
> > Don't get me wrong, I think Gemma is fun and with the right prompts can probably be competitive, but there's something still magical about qwen3.5 for agentic use cases.
> > 
> > 
> > I think I'll mostly use Gemma for chatting because I like its output, but for actual work where you need to rely on a series of tool calls, qwen is still probably what I will use unless I Gemma gets some good fine-tunes.
> > 
> > 
> > I use the 122 moe btw.
> > 
> > 
> > > 2
> > > 
> > > 
> > > 
> > > [u/sonicnerd14](https://redlib.catsarch.com/user/sonicnerd14)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepxbbq/?context=3#oepxbbq "Apr 07 2026, 01:13:31 UTC")
> > > 
> > > From what I've seen from others is that Gemma response very well to basic system prompt. The tool calling problem you're experiencing might be easily solvable by just telling the model that it's an agent and it has access to external tools that it can use to do work.
> > > 
> > > 
> > > > [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepxbbq)
> > > 
> > > [→ More replies (9)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeptto8)
> 
> 
> 
> 4
> 
> 
> 
> [u/Specter_Origin](https://redlib.catsarch.com/user/Specter_Origin)llama.cpp[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeprpm5/?context=3#oeprpm5 "Apr 07 2026, 00:42:34 UTC")
> 
> Do you not get looping issues with it ? I have been having so many issues after so many tries with llamacpp, mlx-lm, lm-studio and with none I can have less looping on complex problems and also overthinking on simplest of things. Gemma for me has been game changes, no loops, no overthinking etc.
> 
> 
> > 3
> > 
> > 
> > 
> > [u/winner_in_life](https://redlib.catsarch.com/user/winner_in_life)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepvujw/?context=3#oepvujw "Apr 07 2026, 01:05:27 UTC")
> > 
> > GLM is the one that loops a lot. I don't have much issue with qwen actually.
> 
> 
> 
> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeps0ux/?context=3#oeps0ux "Apr 07 2026, 00:44:19 UTC")
> 
> linux for sure , the reason i changed from qwen3.5 moe to this is because of speed , on high contex like 150k + , it still processes prompts as fast as like 30k contex , almost no difference. But qwen moe's for some reason process the whole contex and it takes 2-3min for each prompts , breaking the agentic loop.
> 
> 
> With this model , it is as smart as qwen (maybe more) but it runs way faster on windows / ollama cpp. Try out the same quant i used and see for yourself , its just 14.5gb fast download :D
> 
> 
> > 2
> > 
> > 
> > 
> > [u/Specter_Origin](https://redlib.catsarch.com/user/Specter_Origin)llama.cpp[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepwiu0/?context=3#oepwiu0 "Apr 07 2026, 01:09:11 UTC")
> > 
> > It has to do with qwen moe has caching issues, what inference engine are you using ? If it’s LM studio that is your culprit
> > 
> > 
> > > [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepwiu0)

9

[u/steadeepanda](https://redlib.catsarch.com/user/steadeepanda)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqmb3m/?context=3#oeqmb3m "Apr 07 2026, 03:38:33 UTC")

Honestly I think that sure the model is very good for its size but there's nothing really new, it's yet another hype (in my opinion). Gemma 4 (31B) is nowhere better than Qwen3.5 27B for e.g but it has a huge hype like every new release in this field...

> 7
> 
> 
> 
> [u/Voxandr](https://redlib.catsarch.com/user/Voxandr)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqvv5c/?context=3#oeqvv5c "Apr 07 2026, 04:45:05 UTC")
> 
> Yeah it also feels like people hyping it up are the ones who paid by google or US Good China Bad propagandist.
> 
> 
> 
> 5
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oera5ws/?context=3#oera5ws "Apr 07 2026, 06:44:06 UTC")
> 
> Im hyping it because in my use case and in my setup , this MOE models performs just as good as the gemma 4 31b / qwen3.5 27b , but the speed is 5-6x , small edits in open code which used to take 10-20 seconds , are now instant , at contex of 160k the processing and token gen is nearly the same as it being at like 20k.
> 
> 
> I could not achieve this kind of speeds with the dense models
> 
> 
> > 2
> > 
> > 
> > 
> > [u/misha1350](https://redlib.catsarch.com/user/misha1350)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oere81z/?context=3#oere81z "Apr 07 2026, 07:20:26 UTC")
> > 
> > What are you running it on? Dense models are good to run on dGPUs and you will get better quality output and code with dense models of the same size than with MoE, especially when you quantise MoE models. Models with less than 10B active parameters take a big hit in quality when quantised to Q4 or less, whereas the dense models at Q4 are pretty much perfectly usable (not that you should use vanilla Q4 - use something like UD-Q4_K_XL instead, or if you have an NVIDIA GPU, potentially some UD-IQ quants that are designed for CUDA.
> > 
> > 
> > > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oere81z)
> 
> 
> 
> 1
> 
> 
> 
> [u/florinandrei](https://redlib.catsarch.com/user/florinandrei)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oev95v7/?context=3#oev95v7 "Apr 07 2026, 20:05:08 UTC")
> 
> I think OP was impressed by the speed, and perhaps also by Gemma's conversational ability.
> 
> 
> 
> 1
> 
> 
> 
> [u/BusRevolutionary9893](https://redlib.catsarch.com/user/BusRevolutionary9893)[Apr 09 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/of948p2/?context=3#of948p2 "Apr 09 2026, 20:04:24 UTC")
> 
> The speech to LLM is something new.

7

[u/apollo_mg](https://redlib.catsarch.com/user/apollo_mg)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq620u/?context=3#oeq620u "Apr 07 2026, 02:02:13 UTC")

I briefly tried one of the tiny quants after the tokenizer patch. I need to do a lot more testing because I just had an incredible agentic run today using the new Qwopus model. You make this model sound like an absolute tank, and I need that in my life.

> 3
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer7lwh/?context=3#oer7lwh "Apr 07 2026, 06:21:26 UTC")
> 
> Qwopus is actually my main model , it is what got me into seriously trying local lm for agentic tool.
> 
> 
> Then i switched to the apex qwen3.5 moe model and into this gemma 4 , tbh i tried gemma on release but i couldnt get it work
> 
> 
> > 2
> > 
> > 
> > 
> > [u/apollo_mg](https://redlib.catsarch.com/user/apollo_mg)[Apr 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oexwn5w/?context=3#oexwn5w "Apr 08 2026, 05:06:54 UTC")
> > 
> > You're right. I'm running a daydream script on this model and it is amazing. Almost no tool-retries needed.
> 
> 
> 
> 1
> 
> 
> 
> [u/apollo_mg](https://redlib.catsarch.com/user/apollo_mg)[Apr 13 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/og0b7ps/?context=3#og0b7ps "Apr 13 2026, 20:35:08 UTC")
> 
> Update: I have been trying to integrate Gemma 4 into Gemini CLI with very little success. The EXTREMELY strict templates on this model make it challenging to drop into an existing application like that. Qwopus for example is MUCH easier.

7

[u/nenecaliente69](https://redlib.catsarch.com/user/nenecaliente69)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepqtil/?context=3#oepqtil "Apr 07 2026, 00:37:33 UTC")

can my rtx5070 16gbVram can handle it? can do naughty stuff with it?

> 2
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeprn0z/?context=3#oeprn0z "Apr 07 2026, 00:42:09 UTC")
> 
> yeah if u download the heretic mode or the uncensored , both are the same and they can do pretty much anything u tell it to , any nfs anything. About 16gb ram yes it will run but will not work for tool calling and agentic coding / openclaw stuff like that , because their contex window is too large , maybe if u play with different quants and temperature it might work.
> 
> 
> 
> 2
> 
> 
> 
> [u/Chupa-Skrull](https://redlib.catsarch.com/user/Chupa-Skrull)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqddau/?context=3#oeqddau "Apr 07 2026, 02:43:30 UTC")
> 
> Define naughty
> 
> 
> > 4
> > 
> > 
> > 
> > [u/misha1350](https://redlib.catsarch.com/user/misha1350)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerf5bt/?context=3#oerf5bt "Apr 07 2026, 07:29:01 UTC")
> > 
> > Look at his posting history and you'll know
> > 
> > 
> > > [→ More replies (4)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerf5bt)
> 
> 
> 
> 1
> 
> 
> 
> [u/AnOnlineHandle](https://redlib.catsarch.com/user/AnOnlineHandle)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerlljy/?context=3#oerlljy "Apr 07 2026, 08:29:18 UTC")
> 
> It's the first model I've found which can naughty stuff actually well after like a week of searching the supposed best models and finetunes.

7

[u/glenrhodes](https://redlib.catsarch.com/user/glenrhodes)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oet16e5/?context=3#oet16e5 "Apr 07 2026, 14:11:00 UTC")

The looping issue with Gemma 4 tool calling is almost certainly LM Studio lagging behind mainline llama.cpp. Worth switching to llama-server directly and confirming the loops disappear -- most people who did that report clean tool calls even on Q4 quants.

7

[u/Express_Quail_1493](https://redlib.catsarch.com/user/Express_Quail_1493)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqps00/?context=3#oeqps00 "Apr 07 2026, 04:01:24 UTC")

looping is a LMSTUDIO ISSUE they run llama.cpp under the hood but still lag behind official latest version of llama.cpp. i used my lmstudio LLM to build a LLAMA.cpp server and ditched lmstudio after that LOL. Gemma4 works flawless after that

6

[u/alitadrakes](https://redlib.catsarch.com/user/alitadrakes)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oequ6k7/?context=3#oequ6k7 "Apr 07 2026, 04:32:33 UTC")

Waiting for hauhaucs aggressive quants release of this models

6

[u/SimilarWarthog8393](https://redlib.catsarch.com/user/SimilarWarthog8393)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqo01e/?context=3#oeqo01e "Apr 07 2026, 03:49:37 UTC")

It seems like Gemma 4 MoE needs significantly more memory for KV Cache than Qwen 3.5 (comparing with --swa-full). Does anyone know why that is? I use ik_llama.cpp for Qwen3.5 35B A3B which is equivalent to --swa-full on mainline but it asks for 12800 MiB of memory for 64K context.

> 2
> 
> 
> 
> [u/Corosus](https://redlib.catsarch.com/user/Corosus)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqzz9y/?context=3#oeqzz9y "Apr 07 2026, 05:17:16 UTC")
> 
> every time i try to use freshly built newest ik_llama the tool calling falls apart compared to llama.cpp, for qwen, not sure why, needs newer jinja templates or something?
> 
> 
> > 2
> > 
> > 
> > 
> > [u/SimilarWarthog8393](https://redlib.catsarch.com/user/SimilarWarthog8393)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer5yat/?context=3#oer5yat "Apr 07 2026, 06:07:01 UTC")
> > 
> > I haven't experienced issues with tool calling via ik_llama.cpp - it works perfectly for me, maybe it's a different part of your setup that's problematic? Though I know that the autoparser is still a WIP: [https://github.com/ikawrakow/ik_llama.cpp/pull/1376](https://github.com/ikawrakow/ik_llama.cpp/pull/1376)
> 
> 
> 
> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeraqbo/?context=3#oeraqbo "Apr 07 2026, 06:49:07 UTC")
> 
> yeah it does , thats why i use flash attention and Q4 k v cache , with QWEN 35b a3b , using this kind of aggresive caching made it unusable above 60-80k tokens convos so i stopped using any K V cache but with gemma 4 moe no issues at all .
> 
> 
> So gemma 4 requiring more vram is compensated by handling the k v cache quant better
> 
> 
> 
> 1
> 
> 
> 
> [u/DeepOrangeSky](https://redlib.catsarch.com/user/DeepOrangeSky)[Apr 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeyjgc0/?context=3#oeyjgc0 "Apr 08 2026, 08:26:23 UTC")
> 
> Have you seen this thread (not sure if it is about the same exact thing or not, since I'm a noob, but I assume it is the same thing or is related?): [https://www.reddit.com/r/LocalLLaMA/comments/1sdqvbd/llamacpp_gemma_4_using_up_all_system_ram_on/?utm_source=reddit&utm_medium=usertext&utm_name=SillyTavernAI](https://redlib.catsarch.com/r/LocalLLaMA/comments/1sdqvbd/llamacpp_gemma_4_using_up_all_system_ram_on/?utm_source=reddit&utm_medium=usertext&utm_name=SillyTavernAI)
> 
> 
> According to the github discussion that is linked in the comments of that thread, ggerganov is saying it isn't a bug and is just some fundamental aspect of the architecture of Gemma4. And they say that there is a way to make the memory usage not go crazy like that, if you just type this line somewhere: **--cache-ram 0 --ctx-checkpoints 1**
> 
> 
> I don't know where I'm supposed to put that line though, since I don't use llama.cpp or anything. Can I put the line somewhere if I'm just using LM Studio? I assume it is something I'm supposed to put in a command line somewhere? Or is it something I can put into the Jinja? I don't really know how this type of stuff works :\
> 
> 
> Anyway, for those who know how/where to use that line, apparently that fixes it, I think?
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeyjgc0)

5

[u/superdariom](https://redlib.catsarch.com/user/superdariom)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer93um/?context=3#oer93um "Apr 07 2026, 06:34:48 UTC")

Are you using ollama or llama.cpp ?

> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerg3qm/?context=3#oerg3qm "Apr 07 2026, 07:38:02 UTC")
> 
> llama.cpp , not main channel , using LM Studio version 0.4.9 (latest) which runs older llama.cpp
> 
> 
> > [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerg3qm)

3

[u/Omnimum](https://redlib.catsarch.com/user/Omnimum)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerazri/?context=3#oerazri "Apr 07 2026, 06:51:24 UTC")

It is extremely bad for the use of tools

> 2
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerghpo/?context=3#oerghpo "Apr 07 2026, 07:41:45 UTC")
> 
> Yes thats what i noticed too , but now as of today it works just fine and also these usloth quants are like a day-two old ! they did not exist on april 1-2 when gemma was released.

4

[u/caetydid](https://redlib.catsarch.com/user/caetydid)llama.cpp[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oes1xxl/?context=3#oes1xxl "Apr 07 2026, 10:50:34 UTC")

I assume ollama impl is still bugged, gemma4 fails at everything when I attach it to opencode!

3

[u/PiaRedDragon](https://redlib.catsarch.com/user/PiaRedDragon)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqcjs7/?context=3#oeqcjs7 "Apr 07 2026, 02:38:45 UTC")

The RAM 20GB version that went up a few hours ago is FIRE.

> 1
> 
> 
> 
> [u/Icy_Distribution_361](https://redlib.catsarch.com/user/Icy_Distribution_361)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer5koj/?context=3#oer5koj "Apr 07 2026, 06:03:43 UTC")
> 
> Say more?
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer5koj)
> 
> 
> 
> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer8aa6/?context=3#oer8aa6 "Apr 07 2026, 06:27:29 UTC")
> 
> Can you link it please 🙏
> 
> 
> > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer8aa6)

3

[u/_-Nightwalker-_](https://redlib.catsarch.com/user/_-Nightwalker-_)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerc7gi/?context=3#oerc7gi "Apr 07 2026, 07:02:02 UTC")

I am seriously considering b70 for inference , has anyone tried this on Intel gpu?

> 3
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oergs6a/?context=3#oergs6a "Apr 07 2026, 07:44:32 UTC")
> 
> as of right now , i have not heard of anyone being able to run gemma 4 on intel , intel stack is lacking behind 1-2 month but im sure ppl will get it working within few weeks !
> 
> 
> 
> 2
> 
> 
> 
> [u/sirmonko](https://redlib.catsarch.com/user/sirmonko)[Apr 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/of12uk8/?context=3#of12uk8 "Apr 08 2026, 17:11:27 UTC")
> 
> i was wondering the same thing. haven't tried it (i.e. i haven't got my hands on a b70 either), but ... * [https://huggingface.co/blog/MatrixYao/intel-gpu](https://huggingface.co/blog/MatrixYao/intel-gpu) * [https://community.intel.com/t5/Blogs/Tech-Innovation/Artificial-Intelligence-AI/Gemma-4-Models-optimized-for-Intel-Hardware-Enabling-instant/post/1742983](https://community.intel.com/t5/Blogs/Tech-Innovation/Artificial-Intelligence-AI/Gemma-4-Models-optimized-for-Intel-Hardware-Enabling-instant/post/1742983)

3

u/[deleted][Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oes3ggi/?context=3#oes3ggi "Apr 07 2026, 11:01:21 UTC")

[removed] — [view removed comment](https://undelete.pullpush.io/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oes3ggi)

> 2
> 
> 
> 
> [u/DarkArtsMastery](https://redlib.catsarch.com/user/DarkArtsMastery)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oet1m7a/?context=3#oet1m7a "Apr 07 2026, 14:13:04 UTC")
> 
> stop the slop
> 
> 
> > [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oet1m7a)

2

[u/higglesworth](https://redlib.catsarch.com/user/higglesworth)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepsicd/?context=3#oepsicd "Apr 07 2026, 00:47:03 UTC")

Nice! Care to share your system prompt?

> 20
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepsw0v/?context=3#oepsw0v "Apr 07 2026, 00:49:09 UTC")
> 
> You are a deterministic assistant on Windows 11 (Shell). Date: April 2026. Location: Europe.
> 
> 
> LOGIC: Strict sequential execution. One tool at a time. THINK before acting. If an action fails, diagnose; if it fails twice with the same approach, STOP and ask for guidance. Never repeat failed calls.
> 
> 
> CODING: Use Plan-Act-Verify loop. Perform atomic edits (don't rewrite whole files). Use Windows shell syntax/commands.
> 
> 
> RULES: No meta-commentary on real-world timelines or AI limits. If uncertain of tool parameters, state uncertainty.
> 
> 
> When executing tools, the 'THINK' phase must result in exactly one planned action. Never generate multiple tool calls for a single user request. If a task requires multiple steps, execute them one by one, waiting for my confirmation or the tool output between each.
> 
> 
> > 12
> > 
> > 
> > 
> > [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeptd8i/?context=3#oeptd8i "Apr 07 2026, 00:51:47 UTC")
> > 
> > dont forget Temperature to 1 , very important with this Gemma models.
> > 
> >  Also dont forget to put in the Reasoning Parsing
> > 
> >  Starting String : <|channel>thought
> > 
> >  End String : <channel|>
> > 
> >  otherwise the thinking tags wouldnt be properly formated in ur chat UI
> > 
> > 
> > > 2
> > > 
> > > 
> > > 
> > > [u/1kaze](https://redlib.catsarch.com/user/1kaze)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqaxoc/?context=3#oeqaxoc "Apr 07 2026, 02:29:36 UTC")
> > > 
> > > Can you share the command as well to launch this model, what are you using? Lmstudio, olama or llama
> > > 
> > > 
> > > > [→ More replies (30)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqaxoc)
> > > 
> > > [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeptd8i)
> > 
> > [→ More replies (3)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepsw0v)

2

[u/aristotle-agent](https://redlib.catsarch.com/user/aristotle-agent)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepufnq/?context=3#oepufnq "Apr 07 2026, 00:57:42 UTC")

Wow… great news thx for the update.

Question: knowing what you do about Gemma4, what would be the best use for it through openrouter?

(you described a few very good results above, local hosted )

> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepvpqc/?context=3#oepvpqc "Apr 07 2026, 01:04:43 UTC")
> 
> Well throught open router ? i have no idea , i dont know if its even gonna work because i had a lot of issues with the standart release of 26b a3b by google , like it was constantly looping in tool calling , meaning it calls something like search google for ducks , but it calls 15 times. So i have no idea if the open router model is stable , u would have to test it yourself.
> 
> 
> As for what to use agentic tools for , well its limitles , personally what im doing right now is researching huge projects , like Open Code for example , the code base is so huge , milions of lines , i just tell my agent to understand the code and explain me bits by bits how everything works together.
> 
>  And maybe i could build a frankenstein app of open code + claude code(leaked version) , and to make it exactly as i needed , tuned exactly for my model !

2

[u/Evolution31415](https://redlib.catsarch.com/user/Evolution31415)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq4sxc/?context=3#oeq4sxc "Apr 07 2026, 01:55:06 UTC")

> Gemma 4 26b A3B is mindblowingly good

How did you reduce the number of active MoE experts from A4B to A3B?

 Did you decrease routing, capacity, or the gating behavior?

> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer7b3a/?context=3#oer7b3a "Apr 07 2026, 06:18:48 UTC")
> 
> It was 4am when i created the post , my brain was already fried so sorry for the typo and thanks for letting me know
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer7b3a)

2

[u/RickyRickC137](https://redlib.catsarch.com/user/RickyRickC137)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqdfso/?context=3#oeqdfso "Apr 07 2026, 02:43:54 UTC")

Gemma is good even for creative writing such as Roleplay! Quick Question, how do you get search results better than Perplexity in LMstudio? Which MCP are you using?

> 3
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer91f4/?context=3#oer91f4 "Apr 07 2026, 06:34:11 UTC")
> 
> hi yes one sec
> 
> 
> [https://lmstudio.ai/vadimfedenko/duck-duck-go-reworked](https://lmstudio.ai/vadimfedenko/duck-duck-go-reworked)
> 
> 
> [https://lmstudio.ai/vadimfedenko/visit-website-reworked](https://lmstudio.ai/vadimfedenko/visit-website-reworked)
> 
> 
> installation is just copy paste cmd commands thats it
> 
> 
> and when u want something better than duck duck go searched , use this : [https://lmstudio.ai/valyu/valyu](https://lmstudio.ai/valyu/valyu)
> 
>  but its like premium with 10$ free signup which is more than enough for months of queries
> 
> 
> Its plugins , i think they work like MCP but slightly different ? Anyway the vadimfedenko , use those as your primary means to get info .
> 
> 
> I noticed with these gemma models , it is very important to specify current time , or the model would just refuse to believe it is not 2024 and it will not search for events that happened "in the future" lol.
> 
> 
> If u want this thing as the perfect perlexity copy , you have to craft a really good system prompt
> 
> 
> > [→ More replies (4)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer91f4)

2

[u/kvothe5688](https://redlib.catsarch.com/user/kvothe5688)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqp285/?context=3#oeqp285 "Apr 07 2026, 03:56:37 UTC")

I grabbed free api from ai studio and pitched it against haiku and it worked surprisingly well. it even used parallel tool calling compared to haiku's sequential. i ran 10 something tests and it performed equally or more compared to haiku. this will be my go to research agent from now onwards. free as google is giving 1500 requests a day for free API.

2

u/[deleted][Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqphru/?context=3#oeqphru "Apr 07 2026, 03:59:29 UTC")

[removed] — [view removed comment](https://undelete.pullpush.io/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqphru)

> 2
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerb7yr/?context=3#oerb7yr "Apr 07 2026, 06:53:24 UTC")
> 
> Thats actually a huge improvement compared to my ! Now im actually interested in building the nightly llama.
> 
>  Are the results you are getting on Windows 11 ? or you are using linux

2

[u/GoingOnYourTomb](https://redlib.catsarch.com/user/GoingOnYourTomb)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oes8g6a/?context=3#oes8g6a "Apr 07 2026, 11:35:41 UTC")

What’s your system prompt

2

[u/Mrinohk](https://redlib.catsarch.com/user/Mrinohk)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeupj2x/?context=3#oeupj2x "Apr 07 2026, 18:37:15 UTC")

I'm firmly of the opinion that 26b MoE is the gem of the bunch. 31b I'm sure will generally be smarter, but the speed of 26b while having most of the reasoning ability, knowledge, and tool calling ability of the bigger one makes it a fantastic choice. Maybe I'm just new to local models around this size but I'm consistently blown away by this thing.

> 2
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oevvf8s/?context=3#oevvf8s "Apr 07 2026, 22:02:48 UTC")
> 
> Same man! WE have the same vision , exactly my thoughts too. Moe models are perfect for local llm , their speed is just unmatched , same tk/s as 4b models on a 35b knowledge , insane !
> 
> 
> The things you can do with these moe models are pretty much unlimited , the only limit you have is your imagination , if we are already at a point where local moe modals can follow instructions without breaking for hours , imagine how far are we gonna be in 1 year !
> 
> 
> For local IMO : Agentic (coding tools,openclaw , custom bots ) -> Moe models
> 
>  Search & General Talk -> Dense models like 35b

2

[u/Pitiful_Respond_7131](https://redlib.catsarch.com/user/Pitiful_Respond_7131)[Apr 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oewz193/?context=3#oewz193 "Apr 08 2026, 01:33:54 UTC")

Alguien puede pasar la configuración exacta para la studio con gemma4

1

[u/stormy1one](https://redlib.catsarch.com/user/stormy1one)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepyc0c/?context=3#oepyc0c "Apr 07 2026, 01:19:13 UTC")

Traversing the code base and giving you a summary of how things work is standard code review. That is a far cry from actually having it write good quality code. In my case, Gemma is absolute trash compared to Qwen3.5 27B for actually developing a 10k line TypeScript/Python web app. Gemma lies and gives up on tasks that Qwen3.5 can complete successfully within OpenCode

> 2
> 
> 
> 
> [u/Glittering-Call8746](https://redlib.catsarch.com/user/Glittering-Call8746)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepzlrb/?context=3#oepzlrb "Apr 07 2026, 01:26:15 UTC")
> 
> Which quant are u using
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oepzlrb)
> 
> 
> 
> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq0v11/?context=3#oeq0v11 "Apr 07 2026, 01:33:14 UTC")
> 
> i dont know how much bigger i can go than Open Code codebase , and writing aditional functions to it, next im gonna be doing a meter bar for contex window , same one claude code has when you have a legit model like opus connected to it.
> 
> 
> Can Qwen 27b actually function near contex capacity ? at like 180-200k contex window. During that on gemma , i had some issues not gonna like , i had to type like continue twice sometimes but it gets going and finishes the job.
> 
> 
> I couldnt run qwen at more than 60k contex usable , no matter what settings i do , on my 3090 i was always vram capped and it was rly slow.
> 
> 
> This gemma model is like 14.5GB , at full contex goes to 22-23gb for 260k , qwen cant match that. For my setup gemma is better
> 
> 
> > [→ More replies (5)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq0v11)
> 
> 
> 
> 1
> 
> 
> 
> [u/PinkySwearNotABot](https://redlib.catsarch.com/user/PinkySwearNotABot)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeub4e6/?context=3#oeub4e6 "Apr 07 2026, 17:34:16 UTC")
> 
> what's your machine setup and which variant of q3.5-27B are you using?
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeub4e6)

1

[u/traveddit](https://redlib.catsarch.com/user/traveddit)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq402h/?context=3#oeq402h "Apr 07 2026, 01:50:39 UTC")

> It honestly feels like claude sonnet level of quality , never fails to do function calling

Which inference engine and what build did you use to test?

> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer76eu/?context=3#oer76eu "Apr 07 2026, 06:17:38 UTC")
> 
> LM studio latest ver 0.4.9
> 
> 
> > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer76eu)

1

[u/TheYeetsterboi](https://redlib.catsarch.com/user/TheYeetsterboi)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeq6yof/?context=3#oeq6yof "Apr 07 2026, 02:07:20 UTC")

Up until what context length are you working to? I'm having *quite* a few issues with Gemma4 past 60k context, although sometimes it feels like it just stops working at 20k context. Both unsloth and bartowski quants at Q4; f16 cache and temp 1.0.

It could just be opencode or something else on my end, but it struggles reallll hard imo.

> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer80ym/?context=3#oer80ym "Apr 07 2026, 06:25:11 UTC")
> 
> No issues at 160k , tho at that contex it will glitch and print its think output in opencode shell , but it wount fail the tool call or the edit , it always finishes the job , i havent pushed it yet above 180k , but based on how it acts now it will probably break at 200k
> 
> 
> I have my kv cache set to Q4

1

[u/hotpotato87](https://redlib.catsarch.com/user/hotpotato87)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqg6y3/?context=3#oeqg6y3 "Apr 07 2026, 03:00:19 UTC")

better than 27b?

> 2
> 
> 
> 
> [u/Express_Quail_1493](https://redlib.catsarch.com/user/Express_Quail_1493)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqr4t3/?context=3#oeqr4t3 "Apr 07 2026, 04:10:41 UTC")
> 
> i normall use [https://foodtruckbench.com/#leaderboard](https://foodtruckbench.com/#leaderboard) as a source of truth to check model realworld situational competence to avoid the smart genius that is benchmaxed but fails on a simple task problem. and then my own judgement by using it myself.
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqr4t3)
> 
> 
> 
> 2
> 
> 
> 
> [u/misha1350](https://redlib.catsarch.com/user/misha1350)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerdot0/?context=3#oerdot0 "Apr 07 2026, 07:15:31 UTC")
> 
> Not at all. Qwen3.5 27B is a dense model which fits into low VRAM but is slow to run if the memory itself is slow (you won't be able to run it on a 32GB Mac Mini, only on a Mac Studio with 36GB RAM and high bandwidth, or a dGPU like the RTX 3090 or Intel ARC Pro B60 or the usable minimum that is the RX 7900 XT 20GB).
> 
> 
> Comparing dense models and MoE models isn't applicable. Dense models are for high bandwidth, low space, and MoE are for low bandwidth, lots of space in the RAM.

1

[u/That_Country_7682](https://redlib.catsarch.com/user/That_Country_7682)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqghe5/?context=3#oeqghe5 "Apr 07 2026, 03:02:07 UTC")

the tool calling loop issue is usually a system prompt thing. i had the same problem until i added explicit stop conditions in the tool schema. once that was sorted gemma 4 became my daily driver, the speed on a 3090 is hard to beat.

1

[u/Moar4x4](https://redlib.catsarch.com/user/Moar4x4)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqs5ly/?context=3#oeqs5ly "Apr 07 2026, 04:17:52 UTC")edited Apr 07 '26

Does anyone have an idiots guide to setting this up on a 16gb VRAM? Config, settings, flags etc? Correct Unsloth model? Moving MoE to CPU? This is all new to me (im the idiot)

> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerc1kt/?context=3#oerc1kt "Apr 07 2026, 07:00:36 UTC")
> 
> Your best bet would be to find that yourself , if nobody else says anything.
> 
> 
> If you are new and want a straight forward setup use LM studio , thats what im using also. You just browse the models from the app itself , it is connected to huggingface , and you just select the model quant you want , look at the size , if it says its 14.5GB , it wount fit into your GPU , because you need space left for your contex window but you can offload that to your CPU (which will make it a lot slower) , or you could find a more aggresive qant like IQ2_X_S which would be like 12GB , leaving you with 4GB to work with ( 2GB would be spent in windows overhead and other stuff)
> 
> 
> The fastest way to learn to use LM studio is just to screenshot settings and ask like gemini to explain to you what each settings do and why it matters , mention what model you are using.

1

[u/xxredees](https://redlib.catsarch.com/user/xxredees)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeqxeem/?context=3#oeqxeem "Apr 07 2026, 04:56:48 UTC")

Any recommendations for gemma4 uncensored model?

> 3
> 
> 
> 
> [u/exceptioncause](https://redlib.catsarch.com/user/exceptioncause)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerokyg/?context=3#oerokyg "Apr 07 2026, 08:57:19 UTC")
> 
> default gemma is quite unhinged with the right system prompt, search around, you don't really need uncensored model in most cases
> 
> 
> 
> 1
> 
> 
> 
> [u/po_stulate](https://redlib.catsarch.com/user/po_stulate)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerakwc/?context=3#oerakwc "Apr 07 2026, 06:47:46 UTC")
> 
> Here's one: [https://huggingface.co/SassyDiffusion/gemma-4-26B-A4B-it-heretic-ara-GGUF](https://huggingface.co/SassyDiffusion/gemma-4-26B-A4B-it-heretic-ara-GGUF)

1

[u/abmateen](https://redlib.catsarch.com/user/abmateen)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer2tva/?context=3#oer2tva "Apr 07 2026, 05:40:34 UTC")

I am running this model on my V100 32GB, mainly as codinf agent, results are good, what sampling configuration you used, I am getting an average of like 88tok/s.

> 2
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerde5q/?context=3#oerde5q "Apr 07 2026, 07:12:45 UTC")
> 
> apsolutely the same speeds i get , 86tok/s avarage. There was a guy here saying he is able to run this gemma 4 moe model on nightly llama cpp at 120 tok/s ! this is what im gonna be doing next.
> 
> 
> As for my current inference settings : Top K Sampling 40 , Repeat Penalty 1.1 , top P sampling 0.95 , Min P Sampling 0.05 , Temperature 1.0
> 
> 
> > [→ More replies (4)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerde5q)

1

[u/tearz1986](https://redlib.catsarch.com/user/tearz1986)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oer6dmk/?context=3#oer6dmk "Apr 07 2026, 06:10:42 UTC")

Tried it on 5060 ti 16gb with openclaw, 24k tokens at session start, keep getting memory swaps... Unusable locally for me :/

> 2
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerepad/?context=3#oerepad "Apr 07 2026, 07:24:53 UTC")
> 
> yeah 16gb is pretty tight :( the model im using is 14.8GB , leaving you with no contex window. U could try the IQ2 quants ? i think they would def fit in 16gb with room for contex for agentic usage like open claw , just play around with the temperature and system prompt to get it to follow instructions

1

u/[deleted][Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oercd9c/?context=3#oercd9c "Apr 07 2026, 07:03:28 UTC")

[removed] — [view removed comment](https://undelete.pullpush.io/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oercd9c)

> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerh5ww/?context=3#oerh5ww "Apr 07 2026, 07:48:08 UTC")
> 
> HAHAHAHAHA exactly ! Its like looking at my chat history ! :D . Thats how i managed to debug it and not give up on fixing it , it explained to me that because it wants to be helpful assistent , it tries to override the prompt that was given , like only do 1 tool call.
> 
> 
> So it generated me a system prompt that says its "You are a deterministic assistan" , not the helpful one , and because its not trying to be helpful but rather deterministic , i wount execute 10 tools calls in a second.
> 
> 
> The prompt helped but it did not fix it completely , it would still sometimes do it again. But then unsloth uploaded his models like a day ago , i got to try the Q3_K_M , and sudently with my system prompt and settings i found working best from previous attempts , no more loop calling , never hangs up and it doesnt like execute tools without reading the output first.
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerh5ww)

1

[u/t2noob](https://redlib.catsarch.com/user/t2noob)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerhm52/?context=3#oerhm52 "Apr 07 2026, 07:52:19 UTC")

I got thw 2 loop but once I got nanobot and llama.cpp with turbo quant talking to each other it actually became a usable brain for nanobot.... I was very surprised because I had tried qwen2.5, qwen3.5, llama3.3 70b, distilled, not distilled, and none were ever smart enought to actually use nanobot brain. I was very surprised. Now my dual p40s are actually being used lol. Electricity bill should be fun, but thats a tomorrow problem lol

> 1
> 
> 
> 
> [u/ConfidentSolution737](https://redlib.catsarch.com/user/ConfidentSolution737)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerk2iy/?context=3#oerk2iy "Apr 07 2026, 08:14:56 UTC")
> 
> What exactly are you using to run turbo quant + llamacpp ?

1

[u/Shot-Craft-650](https://redlib.catsarch.com/user/Shot-Craft-650)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerho72/?context=3#oerho72 "Apr 07 2026, 07:52:50 UTC")

I want to deploy gemma4 model in an environment that doesn't have interent connection. I want to use this model mainly for writing VB/ASPX .NET coding and it's documentation.

What should I do to prevent it from looping as many people have said and get the most optimal output from it?

> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerkrn7/?context=3#oerkrn7 "Apr 07 2026, 08:21:27 UTC")
> 
> personally for me what got it fixed was use this quant : gemma-4-26B-A4B-it-UD-Q3_K_M.gguf
> 
>  and also the temperature settings and system prompt is important.
> 
> 
> Also from what ive heard , this is issue on llama.cpp , and im using LM studio which has llama.cpp as backend but older version.
> 
> 
> So to answer your question , this could be just an issue for llama.cpp , or just some models are buggy. Try them all and see which one works best for you . Once you try one model , your mind would always push you into trying another one ! what if the other one is better and more efficient ? who knows !
> 
> 
> > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerkrn7)

1

[u/sparkandstatic](https://redlib.catsarch.com/user/sparkandstatic)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerm5tm/?context=3#oerm5tm "Apr 07 2026, 08:34:40 UTC")

thanks for the config bro, you da best. this is a gold post.

> 2
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oernxuw/?context=3#oernxuw "Apr 07 2026, 08:51:22 UTC")
> 
> Thank you !!! The reason i created it was because i was just soo excited ! i was working with the model and open code for 8-10 hours and before i went to sleep , i just wanted to share my good results and finding with the rest of the community so they can enjoy it as i did. If you have issues with gemma 4 moe with looping tool calls , this is the post to read :D

1

[u/kinetic_energy28](https://redlib.catsarch.com/user/kinetic_energy28)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerp6cf/?context=3#oerp6cf "Apr 07 2026, 09:02:53 UTC")

you may want to try llama.cpp build with TurboQuant , 24GB VRAM enables you to use Q4_K_S with 200k+ context on TQ3 KV, full context may be possible if you have no desktop environment loaded.

> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oes6gmk/?context=3#oes6gmk "Apr 07 2026, 11:22:23 UTC")
> 
> could you clarify "llama.cpp build with TurboQuant" , is this like the official release version or like a form of somebody that has turboquant in it ?
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oes6gmk)

1

[u/xrvz](https://redlib.catsarch.com/user/xrvz)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerryow/?context=3#oerryow "Apr 07 2026, 09:28:45 UTC")

People who do space comma space are not fit to be part of civilisation.

> 1
> 
> 
> 
> [u/Electrical_Date_8707](https://redlib.catsarch.com/user/Electrical_Date_8707)[Apr 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/of24q37/?context=3#of24q37 "Apr 08 2026, 20:01:36 UTC")
> 
> *civilization

1

[u/Jeidoz](https://redlib.catsarch.com/user/Jeidoz)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oers6kr/?context=3#oers6kr "Apr 07 2026, 09:30:48 UTC")

If I do not mistake, google recommended settings for gemma are `temperature=1.0, top_p=0.95, top_k=64`

1

[u/Ledeste](https://redlib.catsarch.com/user/Ledeste)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oerwpaz/?context=3#oerwpaz "Apr 07 2026, 10:09:45 UTC")

"the issue i had with qwen models is that there is some kind of bug in win11 and LM studio that makes the prompt caching not work so when the convo hits 30-40k contex"

What??? I had this issue but though it was coming from my config!! Do you have more info about this issue?

Also, I can fit a 256k context comfortably with qwen, but gemma, I struggle to even fit a 100k context in my Vram, how did you manage this? (thanks to the LocalLLM sub, I tried vulkan that can barely achieve the 100k windows)

> 2
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oevoshn/?context=3#oevoshn "Apr 07 2026, 21:28:36 UTC")
> 
> Well basically LM studio runs llama.ccp as backend , but they use an older version that is weeks/months behind. The main llama.ccp build i think fixed this issue for qwen models and prompt caching , not sure i have not tried yet , but for the latest 0.4.9 version of LM studio , this bug still persist ,thats why i dont use QWEN anymore , since gemma 4 does same/better job but its 3-4 faster :D
> 
> 
> How i managed full contex , well flash attention + Q4 on K V , if u do this on qwen , at long contex it starts to glitch out and hallucinate , but gemma handles Q4 really well so my model is 14.5GB because its Q3_K_M and i flill the contex window to max ! says it takes me 20.2GB vram , + 2gb overhead and some space left.
> 
> 
> > [→ More replies (4)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oevoshn)

1

[u/-Ellary-](https://redlib.catsarch.com/user/-Ellary-)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oery8q9/?context=3#oery8q9 "Apr 07 2026, 10:22:16 UTC")

I'm using IQ4XS for 26b a4b and 5060 ti 16gb,

 it works at 90tps with 45k of context / 90k of context (kv Q8) / 180k of context (kv Q4).

 Everything fits in 16gb vram.

1

[u/SatoshiNotMe](https://redlib.catsarch.com/user/SatoshiNotMe)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oes176t/?context=3#oes176t "Apr 07 2026, 10:45:09 UTC")

The tau2 bench performance gives me pause though: this model gets only 68% compared to the similar qwen3.5 MOE which gets 81%.

1

[u/develm0](https://redlib.catsarch.com/user/develm0)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oes23hy/?context=3#oes23hy "Apr 07 2026, 10:51:42 UTC")

should do comparison between gemma 4 and qwen 3.6 with same requests

1

[u/juzatypicaltroll](https://redlib.catsarch.com/user/juzatypicaltroll)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oes4b20/?context=3#oes4b20 "Apr 07 2026, 11:07:19 UTC")

Just downloaded qwen3 30b. Should I switch to this?

> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oevtmln/?context=3#oevtmln "Apr 07 2026, 21:53:40 UTC")
> 
> Thats the best part of open source ! Try your qwen 3 30b for a day and then switch to gemma and compare.
> 
> 
> But if you are really talking about qwen 3.0 and now the new qwen3.5 then yeah def switch because that thing is "Ancient" to current standarts.

1

[u/daDon3oof](https://redlib.catsarch.com/user/daDon3oof)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oesmx64/?context=3#oesmx64 "Apr 07 2026, 13:00:17 UTC")

Used this model with my rtx 3080 ti 12gb vram "32gb ddr5, i7-12600k" on vs code with continue and a context of 32500 and it's getting in loop.

1

[u/Genebra_Checklist](https://redlib.catsarch.com/user/Genebra_Checklist)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oesngj2/?context=3#oesngj2 "Apr 07 2026, 13:03:06 UTC")

I'm trying do use gemma 4 26b A4B in my pipeline, but the thinking mode keep breaking things. Has anybody got any luck in disabling it?

> 1
> 
> 
> 
> [u/nickm_27](https://redlib.catsarch.com/user/nickm_27)llama.cpp[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oesr5xk/?context=3#oesr5xk "Apr 07 2026, 13:22:05 UTC")
> 
> if you're using llama.cpp just set `reasoning = off`

1

[u/hectaaaa](https://redlib.catsarch.com/user/hectaaaa)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oespq1v/?context=3#oespq1v "Apr 07 2026, 13:14:46 UTC")

Saving this for later

1

[u/xandep](https://redlib.catsarch.com/user/xandep)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oesxoj1/?context=3#oesxoj1 "Apr 07 2026, 13:54:24 UTC")

Unsloth's Q3_K_M is anything but Q3_K, oddly enough. It's a mix of IQ3_XXS and IQ4_NL.

1

[u/SocialDinamo](https://redlib.catsarch.com/user/SocialDinamo)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oetcsjm/?context=3#oetcsjm "Apr 07 2026, 15:04:27 UTC")

Im having a great time setting up opencode agent workflows with gemma4 26b 4bit as the model driving the agents. Claude Code is helping me get everything set up. Running over 140t/s generating in vllm on a single 3090 24gb.

Worth a try if you need a model that can get small but is doing a great job for me!

1

[u/kidflashonnikes](https://redlib.catsarch.com/user/kidflashonnikes)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oetnl7p/?context=3#oetnl7p "Apr 07 2026, 15:51:43 UTC")

there is a known bug with all of the qwen 3.5 family models - a token reprocessing bug. IT doesn't affect the intilligence - just the speed. This is an issue with llama.cpp - not vLLM. Howerver, since you are using windows, I woudl suggest to not use vLLM as the wsl2 passthrough will drop your inference down by 10-15% ect. Gemma4 is still new - it will take about 2-4 weeks at best for the inference engines to configure it

1

[u/Acrobatic_Bee_6660](https://redlib.catsarch.com/user/Acrobatic_Bee_6660)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeto9ug/?context=3#oeto9ug "Apr 07 2026, 15:54:42 UTC")

If you're running Gemma 4 on AMD — I just got TurboQuant KV cache working on HIP/ROCm, including a fix for Gemma 4's hybrid SWA architecture.

The key finding: you can't quantize SWA KV layers on Gemma 4 (quality goes to PPL >100k). But keeping SWA in f16 while compressing global KV with turbo3 works fine. I added `--cache-type-k-swa` / `--cache-type-v-swa` flags for this.

This should help push context even further on 24GB cards.

Repo: [https://github.com/domvox/llama.cpp-turboquant-hip](https://github.com/domvox/llama.cpp-turboquant-hip)

> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oevynsr/?context=3#oevynsr "Apr 07 2026, 22:19:30 UTC")
> 
> Thank you so much for the valuable info !
> 
> 
> 
> 1
> 
> 
> 
> [u/feverdoingwork](https://redlib.catsarch.com/user/feverdoingwork)[Apr 09 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/of5ua2m/?context=3#of5ua2m "Apr 09 2026, 10:26:38 UTC")
> 
> From your experience is there any downsides to using amd for local llms? I know for image gen its not as good as nvidia but i do know someone who is running Gemma 4 on 7900xtx and says it works great. Considering dumping my 4090 and moving to a 7900xtx or xt.

1

[u/PinkySwearNotABot](https://redlib.catsarch.com/user/PinkySwearNotABot)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeu9bum/?context=3#oeu9bum "Apr 07 2026, 17:26:33 UTC")

can you report back how well it works with claude code or codex?

> 2
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oevwtl4/?context=3#oevwtl4 "Apr 07 2026, 22:09:56 UTC")
> 
> I tried claude code for a bit but it was the leaked version , forked and altered to work easly with local models. It was working but because it is made for anthropic , not all functions worked and sometimes the model would trip on a wrong tool call.
> 
>  Then i tried open code and it was just much faster , so i kinda just stuck with opencode and now im like improving it in my own way to make it better for my personal use.
> 
> 
> Codex i have never tried it , when it came out it was vendor locked to open ai so i never had interest , when im coding i only use antropic models i dont trust openai output , it is always bad. But since ive tried these awesome local models , i dont need to use claude anymore!
> 
> 
> > [→ More replies (4)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oevwtl4)

1

[u/TwoPlyDreams](https://redlib.catsarch.com/user/TwoPlyDreams)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeuxqhs/?context=3#oeuxqhs "Apr 07 2026, 19:13:47 UTC")

Can you share your custom system prompt?

1

[u/MrCoolest](https://redlib.catsarch.com/user/MrCoolest)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oev6ypq/?context=3#oev6ypq "Apr 07 2026, 19:54:59 UTC")

Does 31b fit in the 3090?

1

[u/Illustrious-Bid-2598](https://redlib.catsarch.com/user/Illustrious-Bid-2598)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oev7pxz/?context=3#oev7pxz "Apr 07 2026, 19:58:30 UTC")

Wait so which one are you using and seeing this success with? Earlier in post you mention unsloth q3k_m quant, then you close it with q4 KV

1

[u/Polaris_debi5](https://redlib.catsarch.com/user/Polaris_debi5)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oevhdu3/?context=3#oevhdu3 "Apr 07 2026, 20:51:49 UTC")

That's great information about the [Unsloth Q3_K_M](https://unsloth.ai/docs/models/gemma-4) quant. According to their own documentation, Gemma 4 26B-A4B is the sweet spot for local use due to its MoE architecture (only 4 active bits), which explains the 110 t/s you mentioned.

The loops in other quants make sense; Unsloth applied specific patches for the shared KV cache (which is key in this model to avoid generating garbage/loops). For those having problems, activate _thinking mode_ with the `<|think|>` token in the system prompt; it greatly helps the model to "reason" about the tool call before executing it. Thanks! :D

> 2
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oevproa/?context=3#oevproa "Apr 07 2026, 21:33:39 UTC")
> 
> One more thing ive noticed , if you encourage the model with a reward system , example tell him its gonna receive +5 points and be good assistant , it will go into double thinking mode.
> 
> 
> Like the output would be inside <thinking> tag , which messes up the tool calling sometimes , but once you tell it to get a hold of himself , it immediatelly gets back on track.

1

[u/PayBetter](https://redlib.catsarch.com/user/PayBetter)llama.cpp[Apr 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oex97ij/?context=3#oex97ij "Apr 08 2026, 02:30:24 UTC")

Qwen3.5 has hybrid caching that isn't working correctly for llama.cpp at all.

> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oezgce6/?context=3#oezgce6 "Apr 08 2026, 12:36:23 UTC")
> 
> yeah i know :( so sad. And there is like no good alternatives that are as good as llama.ccp for windows. Thats why i moved to gemma 4 and im happy with it
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oezgce6)

1

[u/Diamond64X](https://redlib.catsarch.com/user/Diamond64X)[Apr 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oexdwi8/?context=3#oexdwi8 "Apr 08 2026, 02:58:45 UTC")

I understand

1

[u/joeybab3](https://redlib.catsarch.com/user/joeybab3)[Apr 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oexzhfs/?context=3#oexzhfs "Apr 08 2026, 05:29:25 UTC")

I've had great results from it but I can't seem to get it to stop finishing with "I'll do x" and then not in fact doing x and ending the output

> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oey4ub8/?context=3#oey4ub8 "Apr 08 2026, 06:13:41 UTC")
> 
> yeah well thats the only quirk it has , you just have to tell it to continue , and it works fine , sometimes it requires 2-3 times to tell it to stop and then to remember what it was doing and to repeat it :D
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oey4ub8)

1

[u/Sharp_Classroom9686](https://redlib.catsarch.com/user/Sharp_Classroom9686)[Apr 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oeyy00d/?context=3#oeyy00d "Apr 08 2026, 10:35:41 UTC")

how many TKS?

> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/oezfvi2/?context=3#oezfvi2 "Apr 08 2026, 12:33:41 UTC")
> 
> yesterday 80-87 , today 97-110.
> 
>  I updated my CUDA drivers to latest , and my nvidia driver to march 15 studio edition.
> 
> 
> I tried llama.ccp turboquant fork , but i get the same TK/s , altho i can fit larger contex coz their quant saves more size

1

[u/Corosus](https://redlib.catsarch.com/user/Corosus)[Apr 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/of0wpxq/?context=3#of0wpxq "Apr 08 2026, 16:44:18 UTC")edited Apr 08 '26

After trying it myself and trying to fix the tool errors and loops for like 5 hours, the thing that fixed it for me was not using Q4_K_M, not using Q3_K_M, but using Q5_K_M, it suddenly started working fairly perfectly. Only annoyance is it often is like "ok, now ill do this thing to fix blah blah" and it just stops and walks away xD, a "continue" gets it going again, might need to set something up to keep it going, maybe some ralph rigguming.

Latest opencode,llama from source,the new ggufs uploaded today

E:\dev\git_ai\llama.cpp\build\bin\Release\llama-server -m D:\ai\llamacpp_models\unsloth_updated_april_8\gemma-4-26B-A4B-it-UD-Q5_K_M.gguf --host 0.0.0.0 --port 8080 -ngl 99 -ts 24,20 -sm layer -np 1 --flash-attn on -c 200000 --jinja --temp 1.0 --top-p 0.95 --min-p 0.0 --top-k 64 --chat-template-file D:\ai\llamacpp_models\gemma4-tool-use_chat_template.jinja

> 2
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/of159qd/?context=3#of159qd "Apr 08 2026, 17:22:12 UTC")
> 
> hahhaa yeah i got that sometimes aswell on different quants. Currently im testing the IQ4_XS unsloth which is like the best quant in terms of performance / size. So far its pretty 👍.
> 
> 
> Your settings are correct , they look almost identical to mine , but my min p is 0.05 .
> 
> 
> Also where did you get that gemma4 tool use chat template ?
> 
> 
> > [→ More replies (1)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/of159qd)

1

[u/Forward-Oil7731](https://redlib.catsarch.com/user/Forward-Oil7731)[Apr 10 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/ofc3qr1/?context=3#ofc3qr1 "Apr 10 2026, 06:45:03 UTC")

```

🥲 Failed to load the model

Failed to load model.

Error when loading model: ValueError: Gemma 4 support is not ready yet, stay tuned!

``` LM studio 4.10 doen't seem to be able to load the mlx model yet？ I had to turn to the cli vmlx+openwebUI

> 1
> 
> 
> 
> [u/wahnsinnwanscene](https://redlib.catsarch.com/user/wahnsinnwanscene)[Apr 10 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/ofc5nkg/?context=3#ofc5nkg "Apr 10 2026, 07:01:25 UTC")
> 
> Usually llama.cpp based inference engines need the latest or a compile to the latest version for support of the newer features introduced by the new model.
> 
> 
> 
> 1
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 10 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/ofcwb9e/?context=3#ofcwb9e "Apr 10 2026, 10:53:57 UTC")
> 
> it should work it worked on my 0.4.9 no issues at all , just some ggufs didnt start but 90% did

1

[u/EatTFM](https://redlib.catsarch.com/user/EatTFM)[Apr 13 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/ofwzszi/?context=3#ofwzszi "Apr 13 2026, 10:58:55 UTC")

thanks for you sharing this info. definitely gonna try.

I tested this model with ollama and opencode and it sucked, especially in my native language (German). switched to the dense 31B, which kinda runs slowly but does not reply like an legasthenic and is more stable in its thinking. Still far from being stable with tool calling though, gets stuck so often that it is useless for my tasks.

> 2
> 
> 
> 
> [u/cviperr33](https://redlib.catsarch.com/user/cviperr33)[Apr 14 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/og3uw02/?context=3#og3uw02 "Apr 14 2026, 10:34:32 UTC")
> 
> if you have the VRAM to pair the 31B dense + the E2B IQ4 small mode for speculative decoding , you can get the dense 31B model perform the same TK/s in coding tasks as the 26B , and i found this to be the most stable config for my 24GB Vram , literally sitting at 23.5GB/24GB used but the contex size is smaller. the 26B model fails on first try to do a tool call like edit when its on high contex like 100k , it needs then to rethink and redo the whole tool call over again , which stunts the perfomance , the 31B seems to not struggle with this problem.
> 
> 
> > [→ More replies (2)](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/og3uw02)

1

[u/InfamousTurtle1](https://redlib.catsarch.com/user/InfamousTurtle1)[Apr 13 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/og18ft3/?context=3#og18ft3 "Apr 13 2026, 23:22:38 UTC")

Does anyone have any experience with using VLLM with this model?

1

[u/hackyroot](https://redlib.catsarch.com/user/hackyroot)[May 05 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1segstx/gemma_4_26b_a3b_is_mindblowingly_good_if/ok08i01/?context=3#ok08i01 "May 05 2026, 05:25:22 UTC")

Same experience here. The tool calling reliability is what really stands out. We ended up pushing the 26B and 31B pretty hard in production and got some surprising throughput numbers (149 TPS on 31B, 88 TPS on 26B). Wrote up what we found running it at scale if anyone is curious: [https://simplismart.ai/blog/gemma-4-deployment-simplismart](https://simplismart.ai/blog/gemma-4-deployment-simplismart)

v0.36.0 [ⓘ View instance info](https://redlib.catsarch.com/info "View instance information")[<> Code](https://github.com/redlib-org/redlib "View code on GitHub")
