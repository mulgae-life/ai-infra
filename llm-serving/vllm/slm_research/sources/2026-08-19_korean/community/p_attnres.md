Title: Gemma 4 31b AttnRes Project - r/LocalLLaMA

URL Source: https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/

Markdown Content:
[red lib.](https://redlib.catsarch.com/)

Feeds

MAIN FEEDS

[Home](https://redlib.catsarch.com/)[Popular](https://redlib.catsarch.com/r/popular)[All](https://redlib.catsarch.com/r/all)

- [x] in /r/LocalLLaMA 

[reddit](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/#popup)

# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/comments/1vgeslw/

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1vgeslw/)

[settings](https://redlib.catsarch.com/settings)

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/NineThreeTilNow](https://redlib.catsarch.com/user/NineThreeTilNow)•13d ago

# [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on) Gemma 4 31b AttnRes Project

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

 12  Upvotes

*   [perma link](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/)
*   [reddit](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/#popup)# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/)  

75% Upvoted

17 comments sorted by

2

[u/xPXpanD](https://redlib.catsarch.com/user/xPXpanD)llama.cpp[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p1wlrsy/?context=3#p1wlrsy "Aug 05 2026, 18:19:26 UTC")

Following along (if only barely) with great interest. Rare to see a Claude (re-)write with actual substance on here. Hope it doesn't immediately get buried.

Good luck with the project. Hope someone actually takes you up on this if the idea has legs, all for seeing (and trying) more weird approaches.

> 5
> 
> 
> 
> [u/NineThreeTilNow](https://redlib.catsarch.com/user/NineThreeTilNow)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p1xaafr/?context=3#p1xaafr "Aug 05 2026, 20:03:48 UTC")
> 
> You can just toss it in to an LLM and say "explain simple".
> 
> 
> Basically I took Moonshot's early research and put it on Gemma 4 31b.
> 
> 
> Moonshot eventually used it in K3.
> 
> 
> That wasn't surprising because after reading the research there's a certain "Well this is kind of obvious to use." thing going on.

2

[u/LeatherRub7248](https://redlib.catsarch.com/user/LeatherRub7248)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p1ym18b/?context=3#p1ym18b "Aug 05 2026, 23:57:09 UTC")

hey man a few questions:

*   how much u expecting the cost to be?

*   any guesstimate what kind of performance gains we may be expecting for gemma4 31?

> 2
> 
> 
> 
> [u/NineThreeTilNow](https://redlib.catsarch.com/user/NineThreeTilNow)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p1z8pq6/?context=3#p1z8pq6 "Aug 06 2026, 02:01:24 UTC")
> 
> > hey man a few questions:
> > 
> > 
> > *   how much u expecting the cost to be?
> > 
> > *   any guesstimate what kind of performance gains we may be expecting for gemma4 31?
> 
> 
> I honestly don't know the cost as of yet. B300's have good spot prices but right now they're MAXIMALLY used. I don't exactly know why. So ~7$ an hour at non-spot I think.
> 
> 
> Performance gain? On the initial beta model? Probably negative. lol...
> 
> 
> The goal is to push the model from being "Gemma" to being truly community owned. From there I might build multiple training sets. One to push creative writing for the gooners. One to push raw code superiority for the others.
> 
> 
> In an ideal world I'd keep training it. It'd be nice to just crowd fund the whole thing. I don't know if this sub actually cares about having its own model.
> 
> 
> I'll end up fully open sourcing the code, the method, all of it. I don't really care. I do it because it's hard, which makes it fun.
> 
> 
> 
> 1
> 
> 
> 
> [u/brainExploded99](https://redlib.catsarch.com/user/brainExploded99)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p1yqkwe/?context=3#p1yqkwe "Aug 06 2026, 00:22:03 UTC")
> 
> Not OP, but I wouldn't expect any massive gains for AttnRes, considering even the actual paper only observes slightly better benchmark performance on a 48B MoE (although much better training stability, likely helps a lot for large models like K3). OP's plan uses self distillation on a already pretrained + posttrained model, so I wouldn't expect anything revolutionary. I have a feeling that training stability is gonna be hard to achieve on a already fully trained model.
> 
> 
> Idk about the attention changes OP is making though.
> 
> [![Image 1](https://redlib.catsarch.com/preview/pre/iqm39zpaenhh1.png?width=708&format=png&auto=webp&s=fe4ceb72fb7182c73c7804fa3d6e4a68bb26663f)](https://redlib.catsarch.com/preview/pre/iqm39zpaenhh1.png?width=708&format=png&auto=webp&s=fe4ceb72fb7182c73c7804fa3d6e4a68bb26663f)
> 
> 
> > 1
> > 
> > 
> > 
> > [u/NineThreeTilNow](https://redlib.catsarch.com/user/NineThreeTilNow)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p1z7q7k/?context=3#p1z7q7k "Aug 06 2026, 01:56:00 UTC")
> > 
> > The interesting thing that Moonshot claimed about the gains was with respect to data.
> > 
> > 
> > To get the observed results they got in the Attention Residuals paper, they would need 1.25x as much training compute.
> > 
> > 
> > The idea being that training a model with this architecture is more data and compute efficient.
> > 
> > 
> > You're correct though, no massive gains. Just something for the community.
> > 
> > 
> > Training stability is indeed hard. Thankfully, Google lets me use their API for free. This lets me build pseudo random prompt structuring to crawl different spaces the model has. Like having the model impersonate a human while another model is just being "Gemma 4" ...
> > 
> > 
> > Sometimes you can do it adversarially which is also kind of interesting.
> > 
> > 
> > By pulling the Top K logit spectrum out of the model, it helps with training stability. You're not stuck telling the model there's only 1 correct answer. You're telling it that there's a distribution of correct answers. That's what models need.
> > 
> > 
> > > 1
> > > 
> > > 
> > > 
> > > [u/VotZeFuk](https://redlib.catsarch.com/user/VotZeFuk)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p1zrvk7/?context=3#p1zrvk7 "Aug 06 2026, 03:54:25 UTC")edited 13d ago
> > > 
> > > > having the model impersonate a human
> > > 
> > > 
> > > Achievable with the system prompt alone, IMO. Been there, worked on it for a few weeks (got inspired by someone else's endeavours). I'm not talking of a typical roleplay where the model writes prose. It's just... pure speech. Initial setup - roughly 20K tokens, plus the memories collected from conversations over days/weeks/months or even years, if applicable.
> > > 
> > > 
> > > Overall structure:
> > > 
> > > 
> > > Part 1. Short introduction, name/sex, telling the model that whatever's there in biography - it has already happened, it's in the past - you may recall it when necessary, but your life goes on.
> > > 
> > > 
> > > Part 2. Bio (from-birth-to-present-day), written in a concise and factually rich prose. Structuring it in a more digestible manner affects the faux-persona negatively.
> > > 
> > > 
> > > Part 3. Injection point for a shift-register memory that gets updated before you start chatting (memory compression is handled by the same model with a different system prompt); in order:
> > > 
> > > 
> > > *   highly compressed YEARLY memory --> goes right after the bio
> > > 
> > > *   Q1-Q4 blocks with the compression not as strong
> > > 
> > > *   a few blocks of monthly memories
> > > 
> > > *   a few (even less compression!) weeks of memories
> > > 
> > > *   finally the recent chat log from "yesterday" - left completely uncompressed
> > > 
> > > 
> > > 
> > > Part 4. Surface-level personality profile, starting with physical appearance (short description). Then comes a Q&A session where the "person" speaks in its own voice about themselves, answering some trivia. Then a short, descriptive summary of their character. Then a summarizing description of the current circumstances (= scenario, basically).
> > > 
> > > 
> > > Part 5. The instruction block. It should establish the operational mode (no prose, pure speech like in a chat app). Writing this part makes you feel like a sculptor carving a person out of the model. You throw everything you have at it - psychology, linguistics, varied attempts to break patterns and spark up the model's proactivity, etc.
> > > 
> > > 
> > > Part 6. Currently active chat goes here, obviously.
> > > 
> > > 
> > > 
> > > * * *
> > > 
> > > 
> > > There are two levels to this approach:
> > > 
> > > 
> > > A. Human-like behaviour in the final output only (the model still treats the task as inference between model/user).
> > > 
> > > 
> > > B. Human-like reasoning (it actually goes through a sensible reasoning process - however, this method seems to lessen its attention to the instructions embedded within the system prompt itself, as it only works with a post-history message, deep in chat, AFTER the recent user's message - explaining what it's like to think as a personality, giving it an example of the thinking process and asking it - yep, not pre-filling mechanically - to start the answer with "<|channel>thought Meanwhile, in CharName's thoughts: ").
> > > 
> > > 
> > > There's no real benefit to the output quality with "A+B" combined approach. "A" alone is enough.
> > > 
> > > 
> > > And the caveat? **Fine-tunes ruin it all. They always do!** The moment Gemma 4 starts to lose its instruction following ability, the personality becomes less stable, losing nuance and attention to small details. All those claims of 'creative writing' embetterment - they always end up playing against it.
> > > 
> > > 
> > > So, ultimately... Be careful. Gemma 4 31B is exceptional as it is, even though it does have some unwanted garbage built-in (slop patterns - some of them impossible to fight off, some universal and some unique to specific languages).
> > > 
> > > 
> > > > 2
> > > > 
> > > > 
> > > > 
> > > > [u/NineThreeTilNow](https://redlib.catsarch.com/user/NineThreeTilNow)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p1zvhxl/?context=3#p1zvhxl "Aug 06 2026, 04:18:15 UTC")
> > > > 
> > > > I don't go that deep. You don't need to. You need to introduce genuine randomness in the natural conversation.
> > > > 
> > > > 
> > > > You do that by saying
> > > > 
> > > > 
> > > > 1.   You are <Define Job>
> > > > 2.   You speak like <Define Speech Pattern>
> > > > 3.   You have <This conflict>
> > > > 4.   You are here to <Objective>
> > > > 
> > > > 
> > > > You're a construction worker who speaks short, because you're short on time. You're currently behind on work. You're here to vent.
> > > > 
> > > > 
> > > > This sort of thing.
> > > > 
> > > > 
> > > > It pushes the models out of their basin. With enough of those random taggings and a large list of those tags it's sufficient to generate a LOT of random conversation. Some of it hilarious and wacky.
> > > > 
> > > > 
> > > > All of it to pull a general texture of out the model's statistical distribution.
> > > > 
> > > > 
> > > > > 2
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/VotZeFuk](https://redlib.catsarch.com/user/VotZeFuk)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p1zwjo5/?context=3#p1zwjo5 "Aug 06 2026, 04:25:26 UTC")
> > > > > 
> > > > > Ah, well, this can certainly work! In my case it was more of turning it into a _specific_ person - and surprisingly enough, Gemma 4 does it great.
> > > 
> > > 
> > > 
> > > 1
> > > 
> > > 
> > > 
> > > [u/brainExploded99](https://redlib.catsarch.com/user/brainExploded99)[12d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p226u7l/?context=3#p226u7l "Aug 06 2026, 13:50:34 UTC")
> > > 
> > > The Top K thing is pretty close to the the initial distillation method by Hinton which was to model the entire output logit distribution, so this should work quite well.
> > > 
> > > 
> > > 3 questions:
> > > 
> > > 
> > > 1.   Is self distillation useful as in it will teach the model new behaviors?
> > > 
> > > 
> > > Data diversity is 100% important so I understand why you're going this route, but I feel like getting the model to teach itself without answers, similar to self-supervised learning (SSL), is a bit dangerous for LLMs since they can hallucinate and have nothing to ground it. SSL solves this because it's usually on video, and the next frame of the video serves as grounding, along with things like SigReg in JEPA (where parts of the output distribution are forced to be somewhat Gaussian in shape to avoid representation collapse).
> > > 
> > >  Because the model is already trained, you won't have complete collapse like SSL has had issues with, but what exactly is teaching the model new behaviors or telling it to reduce hallucinations?
> > > 
> > >  You said this "Then ask if there are nuances lost in the Bulgarian translation" but there is no guarantee that the LLM judge here has useful enough outputs.
> > > 
> > >  I would look into LLM-as-a-judge papers and and see where it fails and how to make it succeed.
> > > 
> > > 
> > > 2) What exactly are you distilling on in your bulgarian news article example? Is the LLM judge producing a better summary? I might have misunderstood your setup here, in which case that could make question #1 moot.
> > > 
> > > 
> > > 3) Are you planning to do RL after the continual pretrain? I think this would be very useful, and not too difficult to setup (atleast for coding, math) although it will EAT compute (RL is woefully inefficient, its depressing how bad it is honestly, and its even worse for non LLM fields).
> > > 
> > > 
> > > Oh, and another interesting paper to read might be this: [https://arxiv.org/pdf/2601.19897](https://arxiv.org/pdf/2601.19897)
> > > 
> > > 
> > > Nice work so far though!
> > > 
> > > 
> > > > 2
> > > > 
> > > > 
> > > > 
> > > > [u/NineThreeTilNow](https://redlib.catsarch.com/user/NineThreeTilNow)[12d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p229q5s/?context=3#p229q5s "Aug 06 2026, 14:03:37 UTC")
> > > > 
> > > > > Oh, and another interesting paper to read might be this: [https://arxiv.org/pdf/2601.19897](https://arxiv.org/pdf/2601.19897)
> > > > 
> > > > 
> > > > That's interesting. I wrote a version of RL that is very similar to that. The code is sitting on the HF RL repo. I didn't publish a paper because it's not really my thing.
> > > > 
> > > > 
> > > > > What exactly are you distilling on in your bulgarian news article example? Is the LLM judge producing a better summary? I might have misunderstood your setup here, in which case that could make question #1 moot.
> > > > 
> > > > 
> > > > On itself. This maintains that the model stays on manifold and the data maps the manifold correctly.
> > > > 
> > > > 
> > > > > Are you planning to do RL after the continual pretrain?
> > > > 
> > > > 
> > > > Yes, but not the classical version. I'll use some derivative of the work I've done in the past. Like the prior mentioned work above. It basically uses a judged version of SFT.
> > > > 
> > > > 
> > > > Models are vastly more capable of self analysis than people seem to think. The autoregressive nature helps with this. They can generate a terrible initial response or have a terrible initial response given, then evaluate pretty cleanly. Even on a "Not frontier" model.
> > > > 
> > > > 
> > > > If anything I'd say models are better at analysis than they are at generation. Which is ironic.
> > > > 
> > > > 
> > > > > 1
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/brainExploded99](https://redlib.catsarch.com/user/brainExploded99)[12d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p22jr7t/?context=3#p22jr7t "Aug 06 2026, 14:47:58 UTC")
> > > > > 
> > > > > For analysis, I find them to often focus on details that don't matter too much and miss the broader idea. They suck at tasks like summarization of papers for example, where they focus on implementation details instead of the important broader idea, even when prompted to not do that.
> > > > > 
> > > > > 
> > > > > Maybe this could be solved by a much better prompt, not sure.
> > > > 
> > > > 
> > > > 
> > > > 1
> > > > 
> > > > 
> > > > 
> > > > [u/DrWitchDoctorPhD](https://redlib.catsarch.com/user/DrWitchDoctorPhD)[12d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p24hmuq/?context=3#p24hmuq "Aug 06 2026, 19:39:46 UTC")
> > > > 
> > > > > Data diversity is 100% important so I understand why you're going this route, but I feel like getting the model to teach itself without answers, similar to self-supervised learning (SSL), is a bit dangerous for LLMs since they can hallucinate and have nothing to ground it. SSL solves this because it's usually on video, and the next frame of the video serves as grounding, along with things like SigReg in JEPA (where parts of the output distribution are forced to be somewhat Gaussian in shape to avoid representation collapse). Because the model is already trained, you won't have complete collapse like SSL has had issues with, but what exactly is teaching the model new behaviors or telling it to reduce hallucinations?
> > > > 
> > > > 
> > > > The guy is not really looking to do that; he will basically lobotomize the model, insert a cool new gadget and make the model relearn to be itself while using new tricks. I think the idea is pretty neat and was looking into doing sth similar myself, albeit using other attention teks.
> > > > 
> > > > 
> > > > > 1
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/brainExploded99](https://redlib.catsarch.com/user/brainExploded99)[12d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p24jznd/?context=3#p24jznd "Aug 06 2026, 19:50:01 UTC")
> > > > > 
> > > > > Oh you're right, and that makes a lot more sense.

1

[u/mr_Owner](https://redlib.catsarch.com/user/mr_Owner)[13d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p2066nt/?context=3#p2066nt "Aug 06 2026, 05:35:28 UTC")

Sounds like you want rational in a llm?

> 2
> 
> 
> 
> [u/NineThreeTilNow](https://redlib.catsarch.com/user/NineThreeTilNow)[12d ago](https://redlib.catsarch.com/r/LocalLLaMA/comments/1vgeslw/gemma_4_31b_attnres_project/p219ok9/?context=3#p219ok9 "Aug 06 2026, 10:50:02 UTC")
> 
> > Sounds like you want rational in a llm?
> 
> 
> I just want a better OSS model. Trying to show the community that it doesn't require a super farm of blackwell chips to achieve that.
> 
> 
> Elbow grease and a minimalist approach to some stuff.

v0.36.0 [ⓘ View instance info](https://redlib.catsarch.com/info "View instance information")[<> Code](https://github.com/redlib-org/redlib "View code on GitHub")
