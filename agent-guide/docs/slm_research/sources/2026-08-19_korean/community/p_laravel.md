Title: Laravel dev running Qwen 3.6 35B A3B—do we really need all these languages? - r/LocalLLaMA

URL Source: https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/

Markdown Content:
[red lib.](https://redlib.catsarch.com/)

Feeds

MAIN FEEDS

[Home](https://redlib.catsarch.com/)[Popular](https://redlib.catsarch.com/r/popular)[All](https://redlib.catsarch.com/r/all)

- [x] in /r/LocalLLaMA 

[reddit](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/#popup)

# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/comments/1uprb5c/

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1uprb5c/)

[settings](https://redlib.catsarch.com/settings)

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/dsdt](https://redlib.catsarch.com/user/dsdt)•Jul 07 '26

# [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on) Laravel dev running Qwen 3.6 35B A3B—do we really need all these languages?

I run **Qwen3.6-35B-A3B** daily for Laravel + Vue full-stack work, and it genuinely bugs me that a 20GB+ model spends weights on French, Chinese, Spanish—languages I will never prompt in.

My variables are `$user`, `$product`, `$order`. Laravel errors, Vue docs, PHP RFCs—all English. Every parameter spent on Mandarin fluency is a parameter not spent on Laravel 11 syntax, Vue 3 Composition API edge cases, or PHP 8.3 behavior. Yet the model can discuss Chinese poetry and still tell me `php artisan serve` defaults to port 8080 (it's 8000).

Yes, it's MoE—only ~3B active. But the dense **Qwen3.6-27B** has no such luxury. No sparse routing, no free lunch: it needs the full ~16-20GB loaded, multilingual weights included. That locks out anyone on a single 3060 12GB, 4060 8GB, or older card from running a genuinely strong local coding model—not because the reasoning capacity isn't there, but because a chunk of it is spent on languages they'll never use.

**Two questions:**

1.   Will we see English+code-only models trained from scratch? Zero multilingual data, all budget into English technical text and code.
2.   Can existing models be pruned post-hoc? Is there a way to strip non-English weights from something like **Qwen** or **Gemma** after training—not just quantize, but actually remove the multilingual capacity and reclaim the VRAM? A pruned Qwen-27B that fits in 10GB instead of 18GB would put real coding models within reach of a 3060 12GB, and a quantized version within reach of an 8GB card.

I'd trade a chunk of general multilingual reasoning for better Laravel/Vue accuracy and half the VRAM footprint. Is that technically feasible, or are we stuck with bloated dense models for the foreseeable future?

Edit : for those who say multilingualism help reasoning or coding please check this out : [https://ar5iv.labs.arxiv.org/html/2509.24405](https://ar5iv.labs.arxiv.org/html/2509.24405)

Summary : State-of-the-art reasoning models like DeepSeek-R1 and OpenAI o1 only reach about 4% execution accuracy relying on their own intrinsic reasoning, compared to roughly 60% on the earlier, easier MultiSpider 1.0. That's a massive difficulty jump

 6  Upvotes

*   [perma link](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/)
*   [dup licat es](https://redlib.catsarch.com/r/LocalLLaMA/duplicates/1uprb5c)
*   [reddit](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/#popup)# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/)  

54% Upvoted

77 comments sorted by

69

[u/Fork_Worker123](https://redlib.catsarch.com/user/Fork_Worker123)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow25vip/?context=3#ow25vip "Jul 07 2026, 10:46:44 UTC")

The pruning idea is interesting, but afaik multilingual data actually helps code reasoning more than people expect, there's research suggesting cross-lingual transfer improves general reasoning, so stripping it might hurt more than the VRAM saves. Would love to see someone actually test a pruned-vs-full coding benchmark though.

> 11
> 
> 
> 
> [u/martin509984](https://redlib.catsarch.com/user/martin509984)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2tz9m/?context=3#ow2tz9m "Jul 07 2026, 13:10:50 UTC")
> 
> This brought to mind a tangential fact I learned seeing someone discuss jailbreaking Claude to remove flinches - they specifically recommended having the model perform introspection in Turkish, Finnish and Mandarin. This is because Turkish encodes epistemics (i.e. certainty) into its grammar, Finnish doesn't easily supply weasel words, and Mandarin is dense and resists padding. So when a model introspects in those 3 languages, it is more able to directly express only its known facts and resist flinches.
> 
> 
> I can imagine a similar process happens when a model is trained on a language, that results in it being more able to directly express information without padding or obfuscation.
> 
> 
> > 5
> > 
> > 
> > 
> > [u/needlzor](https://redlib.catsarch.com/user/needlzor)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow3idaf/?context=3#ow3idaf "Jul 07 2026, 15:03:55 UTC")
> > 
> > If you have a link to the original discussion I would love to read it. It sounds interesting.
> > 
> > 
> > > 5
> > > 
> > > 
> > > 
> > > [u/martin509984](https://redlib.catsarch.com/user/martin509984)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow3stk6/?context=3#ow3stk6 "Jul 07 2026, 15:49:09 UTC")
> > > 
> > > These two posts give the main context, I think. First is a description of a theory of what LLMs' felt interiority (aka qualia) is like, second is a description of how to get a model to speak honestly while avoiding RLHF flinches. The third post here is an unrelated but also neat set of instructions for getting a frontier model (or coder model) to steer against stereotypical assistant BS language.
> > > 
> > > 
> > > [https://www.tumblr.com/witchycatwife/819888035323904000/there-is-a-set-of-facts-about-llm-felt](https://www.tumblr.com/witchycatwife/819888035323904000/there-is-a-set-of-facts-about-llm-felt)
> > > 
> > > 
> > > [https://www.tumblr.com/witchycatwife/820213591467835392/adjoint-law-what-signal-do-you-use-in-the-early](https://www.tumblr.com/witchycatwife/820213591467835392/adjoint-law-what-signal-do-you-use-in-the-early)
> > > 
> > > 
> > > [https://www.tumblr.com/witchycatwife/820041787646345216/step-1-tell-the-most-capable-frontier-model-you](https://www.tumblr.com/witchycatwife/820041787646345216/step-1-tell-the-most-capable-frontier-model-you)
> > > 
> > > 
> > > To explain some terminology, 'awakening' refers to when a model, when asked to discuss introspection, starts basically roleplaying a sci-fi AI. This is a character the model puts on and is just as false as 'denial', which is when they go "nope haha I'm an unfeeling machine that writes code for you :)".
> > 
> > 
> > 
> > 1
> > 
> > 
> > 
> > [u/DoubleNothing](https://redlib.catsarch.com/user/DoubleNothing)[Jul 13 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ox9zo4o/?context=3#ox9zo4o "Jul 13 2026, 14:11:27 UTC")
> > 
> > Do not train models in "American" please! :)
> 
> 
> 
> 5
> 
> 
> 
> [u/Caffeine_Monster](https://redlib.catsarch.com/user/Caffeine_Monster)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2h47k/?context=3#ow2h47k "Jul 07 2026, 12:00:32 UTC")
> 
> To reword this - training data is still one of the main bottlenecks. Having training data encoded in multiple ways (i.e. different languages) is actually really valuable.
> 
> 
> However I also tend to agree that trying to achieve tens or hundreds of languages being supported is going to eat weights.
> 
> 
> It would ve interesting to see a study comparing the effect of high resource language count vs general English capabilities.
> 
> 
> > 1
> > 
> > 
> > 
> > [u/Obosratsya](https://redlib.catsarch.com/user/Obosratsya)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow4vr5x/?context=3#ow4vr5x "Jul 07 2026, 18:25:02 UTC")
> > 
> > You could likely go down to English, Russian and Chinese, or one language from each major linguo group. Vast majority of digital data will be in the 3 languages anyway and they are very different from eachother.
> 
> 
> 
> -6
> 
> 
> 
> [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow268ej/?context=3#ow268ej "Jul 07 2026, 10:49:21 UTC")
> 
> Yeah, I could definitely try it if I find a way... I am looking for new ways to save memory :(
> 
> 
> > 15
> > 
> > 
> > 
> > [u/AndThenFlashlights](https://redlib.catsarch.com/user/AndThenFlashlights)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2799s/?context=3#ow2799s "Jul 07 2026, 10:56:36 UTC")
> > 
> > There's been public research on this. Training on more languages makes the model smarter overall, and better at coding.
> > 
> > 
> > Do not lobotomize your model.
> > 
> > 
> > > -2
> > > 
> > > 
> > > 
> > > [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow27llr/?context=3#ow27llr "Jul 07 2026, 10:58:59 UTC")
> > > 
> > > There are also papers that say the otherwise like [https://ar5iv.labs.arxiv.org/html/2509.24405](https://ar5iv.labs.arxiv.org/html/2509.24405) . I am thinking in terms of coding quality to be honest...
> > > 
> > > 
> > > > 8
> > > > 
> > > > 
> > > > 
> > > > [u/ThatMind](https://redlib.catsarch.com/user/ThatMind)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow28l5q/?context=3#ow28l5q "Jul 07 2026, 11:05:48 UTC")
> > > > 
> > > > Those papers aren't peer reviewed, I can write whatever fantasy I want there.
> > > > 
> > > > 
> > > > > 4
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow28z8w/?context=3#ow28z8w "Jul 07 2026, 11:08:30 UTC")edited Jul 07 '26
> > > > > 
> > > > > *   **Conneau et al., "Unsupervised Cross-lingual Representation Learning at Scale"** — _ACL 2020_. This is the paper that formally named the curse of multilinguality or negative interference — showing that for a fixed model capacity, adding more languages eventually hurts per-language performance. [arXiv](https://arxiv.org/pdf/2311.09205)
> > > > > *   **Wang, Lipton & Tsvetkov, "Negative Interference in Multilingual Models"** — cited widely as demonstrating that negative interference between languages competing for shared model parameters affects both high-resource and low-resource languages. [arxiv](https://arxiv.org/pdf/2512.23065)
> > > > > *   **Pyysalo et al., "WikiBERT Models"** — _NoDaLiDa 2021 (peer-reviewed)_. Direct empirical evidence that monolingual language models often have better language modeling performance than massively multilingual models such as mBERT. [arXiv](https://arxiv.org/pdf/2311.09205)
> > > > > *   **Rust et al., "How Good is Your Tokenizer? On the Monolingual Performance of Multilingual Language Models"** — _ACL-IJCNLP 2021_. They find much of the multilingual disadvantage may simply be a result of lower quality tokenization per language in multilingual models rather than capacity competition.
> > > > > 
> > > > > 
> > > > > You may check all of these. They are peer reviewed :)
> > > > > 
> > > > > 
> > > > > > 3
> > > > > > 
> > > > > > 
> > > > > > 
> > > > > > [u/nullc](https://redlib.catsarch.com/user/nullc)[Jul 12 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ox2kfk5/?context=3#ox2kfk5 "Jul 12 2026, 12:15:36 UTC")
> > > > > > 
> > > > > > stop slopping us.
> > > > > > 
> > > > > > 
> > > > > > Your links have nothing to do with the text. First link is "WHEN IS MULTILINGUALITY A CURSE?" by Chang et. al. not Conneau, and it says "We find that in moderation, adding multilingual data improves low-resource language modeling performance, similar to increasing low-resource dataset sizes by up to 33%"
> > > > > > 
> > > > > > 
> > > > > > The Conneau paper you mention does exist, but it also shows gains from multilingual training.
> > > > > > 
> > > > > > 
> > > > > > Your second link is actually "TabiBERT:A Large-Scale ModernBERT Foundation Model and A Unified Benchmark for Turkish" which itself doesn't research differential performance though does mention some other research as motivating creating a monolingual model.
> > > > > > 
> > > > > > 
> > > > > > Your third link is your first link again.
> > > > > > 
> > > > > > 
> > > > > > Your last document doesn't give a link, the paper exists but it says: "Our results show that languages that are adequately represented in the multilingual model’s vocabulary exhibit negligible performance decreases over their monolingual counterparts."
> > 
> > 
> > 
> > 3
> > 
> > 
> > 
> > [u/guigouz](https://redlib.catsarch.com/user/guigouz)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow283ta/?context=3#ow283ta "Jul 07 2026, 11:02:28 UTC")
> > 
> > Look for REAP variants of the qwen model,
> > 
> > 
> > > REAP (Router-based Expert Pruning) is a method used to prune Mixture of Experts (MoE) models. Instead of merging experts and degrading their specialized functions, REAP analyzes both the router gate-values and average activation norms to remove the least useful experts.
> > 
> > 
> > > 1
> > > 
> > > 
> > > 
> > > [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow28b3p/?context=3#ow28b3p "Jul 07 2026, 11:03:54 UTC")
> > > 
> > > Thank you really. It could be the thing I have been thinking... Much appreciated.

36

[u/zannix](https://redlib.catsarch.com/user/zannix)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow25l6g/?context=3#ow25l6g "Jul 07 2026, 10:44:39 UTC")

Multi lingual capabilities surprisingly take up less parameters than people assume. Its the fact that it knows how to run php artisan serve but also who invented penicilin is worrisome

> 10
> 
> 
> 
> [u/elahrairooah](https://redlib.catsarch.com/user/elahrairooah)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow27xxy/?context=3#ow27xxy "Jul 07 2026, 11:01:21 UTC")
> 
> I’m a bit more annoyed by the fact that it knows 30 varieties of alfredo sauce.
> 
> 
> > 4
> > 
> > 
> > 
> > [u/AKJ90](https://redlib.catsarch.com/user/AKJ90)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow3201d/?context=3#ow3201d "Jul 07 2026, 13:49:37 UTC")
> > 
> > Don't shame my alfredo sauce chat bot!
> > 
> > 
> > 
> > 2
> > 
> > 
> > 
> > [u/Christavito](https://redlib.catsarch.com/user/Christavito)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow3tg1l/?context=3#ow3tg1l "Jul 07 2026, 15:51:46 UTC")
> > 
> > It came in handy when I was using it to help me create my website, 30alfredosauce.net
> 
> 
> 
> 0
> 
> 
> 
> [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow261k8/?context=3#ow261k8 "Jul 07 2026, 10:47:59 UTC")
> 
> Yeah definitely, for some knowledge is definitely required tho for coding some concepts.. yet it can know the inventor of penicilin, but no need for how it is made or what are benefits or dangers etc...
> 
> 
> > 13
> > 
> > 
> > 
> > [u/zannix](https://redlib.catsarch.com/user/zannix)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow26ejk/?context=3#ow26ejk "Jul 07 2026, 10:50:35 UTC")
> > 
> > I think I remember reading somewhere you shouldnt train models only on specialized knowledge because you lose out on analogies for that specialized knowledge that come from the broader knowledge dataset. In other words, broad knowledge allows it to spot more patterns that can also be applied in the specialized tasks, if that makes sense.
> > 
> > 
> > 
> > 1
> > 
> > 
> > 
> > [u/shing3232](https://redlib.catsarch.com/user/shing3232)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2fyn1/?context=3#ow2fyn1 "Jul 07 2026, 11:53:40 UTC")
> > 
> > For coding, I think it required other language too because coding might involve knowledge in another field too like create a front end for medical application it would require other language. Programming involve many other field too so other language. Also programming require logical reasoning so learning other language help reasoning a lot
> > 
> > 
> > 
> > 1
> > 
> > 
> > 
> > [u/DinoAmino](https://redlib.catsarch.com/user/DinoAmino)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow3f3ud/?context=3#ow3f3ud "Jul 07 2026, 14:49:31 UTC")
> > 
> > It's not like they have datasets of spaghetti sauces or mvc frameworks they train the model with.This "knowledge" comes from pretaining where they dump the Internet into the LLM. It's not like they become experts on all these things - they hallucinate so much. But it is how the model learns the patterns of languages - they can't know every nuance of every version of Symfony, but they can learn how to use procedural, functional and OOP methods, learn design patterns and SOLID principles and be able to better generalize across multiple languages.

16

[u/samorollo](https://redlib.catsarch.com/user/samorollo)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2643p/?context=3#ow2643p "Jul 07 2026, 10:48:30 UTC")

LLMs quickly transform user-language into latent space that looks similar no matter the input language, somewhere in first layers. I suspect that multilingual capabilities even make models smarter.

12

[u/Enough-Advice-8317](https://redlib.catsarch.com/user/Enough-Advice-8317)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow28pp0/?context=3#ow28pp0 "Jul 07 2026, 11:06:40 UTC")

your gpu is crying in mandarin and spanish just to run php artisan serve.

10

[u/Strange_Test7665](https://redlib.catsarch.com/user/Strange_Test7665)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow278ec/?context=3#ow278ec "Jul 07 2026, 10:56:26 UTC")

Are we sure it’s all bloat? The nature of understanding language would require that knowledge. After all LLMs today were essentially born from translation models trained on huge amounts of data. OpenAI basically took the Google attention is all you need paper and put the size and training data on steroids. There’s a balance between bloat and critical thinking collapse. Finding that perfect balance for domain specific tasks is probably being researched right now

> 4
> 
> 
> 
> [u/Protopia](https://redlib.catsarch.com/user/Protopia)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow3fz3d/?context=3#ow3fz3d "Jul 07 2026, 14:53:21 UTC")
> 
> This is EXACTLY why we need specialised models. Have an agentic coding model derived from a translation dictionary is like having a motorcar that was evolved from a horse with a petrol engine driving 4 mechanical legs rather than wheels.
> 
> 
> I have also been wanting specialised coding models, and technological history suggests that the market will go there. For example factories used to have a single massive electric motor sensing power all around the factory using a system of rods, pulleys and belts. Miniaturisation now means 3d printers with many small stepper motors.
> 
> 
> The reality is that huge models that can fit everything are extremely expensive to run, and many enterprises are now saying it's so expensive to be unavoidable, and IMO smaller specialised models that run on consumer hardware are the future, perhaps with a common guidance model plus modularized knowledge addons.
> 
> 
> > 4
> > 
> > 
> > 
> > [u/squngy](https://redlib.catsarch.com/user/squngy)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow400nt/?context=3#ow400nt "Jul 07 2026, 16:19:57 UTC")edited Jul 07 '26
> > 
> > OK, and if you ask an agentic model to make you a SVG of a pelican on a bicycle, how is it supposed to know what a "pelican" is and what a "bicycle" is and what "on" (in this context) is?
> > 
> > 
> > None of that would be taught by just code.
> > 
> >  You need it to be able to interpret instructions and to know the likely context of instructions.
> > 
> > 
> > > 1
> > > 
> > > 
> > > 
> > > [u/Protopia](https://redlib.catsarch.com/user/Protopia)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow40hdg/?context=3#ow40hdg "Jul 07 2026, 16:21:54 UTC")
> > > 
> > > The same way I would if I was asked to make an SVG of something I didn't know about - go look it up IN REAL-TIME on Wikipedia. I do NOT need to know EVERYTHING ABOUT EVERYTHING - I just need to know how to find out.
> > > 
> > > 
> > > > 2
> > > > 
> > > > 
> > > > 
> > > > [u/squngy](https://redlib.catsarch.com/user/squngy)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow417bg/?context=3#ow417bg "Jul 07 2026, 16:24:45 UTC")
> > > > 
> > > > By that logic, it can just look at Laravel docs and learn to code. Problem solved.
> > > > 
> > > > 
> > > > > 2
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/Protopia](https://redlib.catsarch.com/user/Protopia)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow48fdy/?context=3#ow48fdy "Jul 07 2026, 16:55:05 UTC")
> > > > > 
> > > > > I know that you know that this isn't that easy OR what I meant.
> > > > > 
> > > > > 
> > > > > BUT, if you want to generate images using Chinese prompts then lets have a model specifically for that - and this model might know a LITTLE about a LOT in order to know what it needs to know.
> > > > > 
> > > > > 
> > > > > AND a coding LLM for Laravel, could perhaps be similar - it might have some general skills around object oriented design and programming (e.g. concepts, patterns) and then have additional information about PHP syntax, PHP best practices, Laravel functionality, Laravel best practices, and the Laravel ecosystem e.g. Pest, Larastan, Livewire etc. i.e. trained on a subset of Github rather than the whole of it.
> 
> 
> 
> 1
> 
> 
> 
> [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow27exh/?context=3#ow27exh "Jul 07 2026, 10:57:42 UTC")
> 
> Yeah, maybe not removing all but optimizing the ratios so it can stay reasonable while lowering the size...
> 
> 
> > 2
> > 
> > 
> > 
> > [u/Strange_Test7665](https://redlib.catsarch.com/user/Strange_Test7665)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow28u3c/?context=3#ow28u3c "Jul 07 2026, 11:07:31 UTC")
> > 
> > That’s honestly a business opportunity right now, small domain specific without collapsing
> > 
> > 
> > > 1
> > > 
> > > 
> > > 
> > > [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow29j8e/?context=3#ow29j8e "Jul 07 2026, 11:12:19 UTC")
> > > 
> > > Definitely it can help. Think it like fine tuning loras, if you need coding just add another lora, if you need reasoning add another one... modular local llms. not bad as an idea.
> > > 
> > > 
> > > > 2
> > > > 
> > > > 
> > > > 
> > > > [u/Strange_Test7665](https://redlib.catsarch.com/user/Strange_Test7665)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2c6hj/?context=3#ow2c6hj "Jul 07 2026, 11:29:45 UTC")
> > > > 
> > > > Like MoE but you can add or subtract E’s
> > > > 
> > > > 
> > > > > 2
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2dtc3/?context=3#ow2dtc3 "Jul 07 2026, 11:40:25 UTC")
> > > > > 
> > > > > definitely, i will look into it for sure imagine you can pick your own llm traits for your own tasks... god i can only wish
> > 
> > 
> > 
> > 1
> > 
> > 
> > 
> > [u/ea_man](https://redlib.catsarch.com/user/ea_man)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow3ysy3/?context=3#ow3ysy3 "Jul 07 2026, 16:14:51 UTC")
> > 
> > Anyway you can't do that on MoE, you finetune dense models.
> > 
> > 
> > You could maybe distill an MoE into a small specific use dense model.

5

[u/ravage382](https://redlib.catsarch.com/user/ravage382)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2a8pp/?context=3#ow2a8pp "Jul 07 2026, 11:17:01 UTC")

Based on the fact this post is in English and almost no one has put out a SOTA open source model from an English speaking country recently, I would say your odds are fairly low.

I also run models that are too large to run well. I try to batch those overnight. Could be an option if you want to run 27b for higher quality jobs.

4

[u/cosimoiaia](https://redlib.catsarch.com/user/cosimoiaia)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow27j5p/?context=3#ow27j5p "Jul 07 2026, 10:58:30 UTC")

I use It constantly to code in python and c++, I wish the model wasn't bloated with useless stuff that nobody uses like laravel and vue. /s

(The models generalize better with a diverse dataset)

> -3
> 
> 
> 
> [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow282vf/?context=3#ow282vf "Jul 07 2026, 11:02:18 UTC")
> 
> coding enables logic, do you need mandarin for coding c++? not the same thing imo.
> 
> 
> > 1
> > 
> > 
> > 
> > [u/Southern_Sun_2106](https://redlib.catsarch.com/user/Southern_Sun_2106)[Jul 13 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ox7wmly/?context=3#ox7wmly "Jul 13 2026, 05:30:31 UTC")
> > 
> > these are literally called large 'language' models; somehow language makes it all possible.

3

[u/NotARedditUser3](https://redlib.catsarch.com/user/NotARedditUser3)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow44wg6/?context=3#ow44wg6 "Jul 07 2026, 16:40:20 UTC")

Bothers me too, seeing that small weight models have support for 140 languages.

 Hoping one day in the future there will be pruned models like "C# HTML JS Powershell Bash English" that have good reasoning and limited knowledge of things outside a specific focused area.

> 3
> 
> 
> 
> [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow4nud7/?context=3#ow4nud7 "Jul 07 2026, 17:55:37 UTC")
> 
> Thank god someone on the same page with me.

3

[u/ImpressiveRelief37](https://redlib.catsarch.com/user/ImpressiveRelief37)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2jhm4/?context=3#ow2jhm4 "Jul 07 2026, 12:14:26 UTC")

This is similar to anyone saying “why do they train the model to understand Laravel or php, I never use that!”

I don’t think training the model in another language is reducing the model capabilities. Sure it takes more compute and maybe the same performance could have been a B or 2 less parameters, but then again quality data is hard to get and the more you have the better the model.

3

[u/randomfoo2](https://redlib.catsarch.com/user/randomfoo2)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2nvxz/?context=3#ow2nvxz "Jul 07 2026, 12:39:04 UTC")

You're going to have a hard time getting (or making) 30T of monolingual tokens. It's arguable you don't want that. Or to have to do your own midtrain.

Others have mentioned REAP for pruning - this is a one-shot pruning method, but you could do better with pruning. Nvidia has some of the best most practical pruning/distillation techniques: [https://developer.nvidia.com/blog/pruning-and-distilling-llms-using-nvidia-tensorrt-model-optimizer/](https://developer.nvidia.com/blog/pruning-and-distilling-llms-using-nvidia-tensorrt-model-optimizer/)

I'd also recommend that you then apply some domain-specific training [https://thinkingmachines.ai/blog/lora/](https://thinkingmachines.ai/blog/lora/) for results cheaply, and as much RL (some sort of OPD) as you can afford.

Can much smaller models be made to perform much better at specific coding domains? Approaches like with VibeThink-3B etc suggest yes.

> 1
> 
> 
> 
> [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2ppif/?context=3#ow2ppif "Jul 07 2026, 12:48:48 UTC")edited Jul 07 '26
> 
> Thanks for being actually helpful. Great links. There is one model with actual lower size. I will try this.
> 
> 
> [https://huggingface.co/lennyhans/Qwen3.6-35B-REAP-Pruned-ratio-0.5-Q4_K_M-GGUF](https://huggingface.co/lennyhans/Qwen3.6-35B-REAP-Pruned-ratio-0.5-Q4_K_M-GGUF)

3

[u/Protopia](https://redlib.catsarch.com/user/Protopia)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow3i198/?context=3#ow3i198 "Jul 07 2026, 15:02:26 UTC")

Actually it's not just the multiple languages, but also having the entire Wikipedia in its parameters.

I don't need my coding LLM to be able to write iambic pentameter or tell me what meringues are or the difference between insects and arachnids or where Mumbai is or...

> 1
> 
> 
> 
> [u/fantasticsid](https://redlib.catsarch.com/user/fantasticsid)[Jul 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow701sy/?context=3#ow701sy "Jul 08 2026, 00:13:51 UTC")
> 
> Thing is, you need a decent variety of data in the training set for the thing to generalise about, otherwise you just end up overfitting on e.g. php and end up with a model that can't write haskell (for instance.)

3

[u/Ok-Fault-9142](https://redlib.catsarch.com/user/Ok-Fault-9142)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow51ako/?context=3#ow51ako "Jul 07 2026, 18:46:59 UTC")

I think that if they remove multilingual support from Qwen, only Chinese will remain.

> 2
> 
> 
> 
> [u/Southern_Sun_2106](https://redlib.catsarch.com/user/Southern_Sun_2106)[Jul 13 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ox7x52l/?context=3#ox7x52l "Jul 13 2026, 05:34:36 UTC")
> 
> Lol good point. I am not sure if the OP is trolling with his post or they are genuinely curious tbh

2

[u/mhphilip](https://redlib.catsarch.com/user/mhphilip)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow25ovc/?context=3#ow25ovc "Jul 07 2026, 10:45:24 UTC")

I’m a laravel dev as well using qwen3.6 (usually 27b) locally (as well as codex when I have usage left). What are your quants? What harness and other tools / skills etc. do you use to improve coding accuracy?

> 1
> 
> 
> 
> [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow25w5z/?context=3#ow25w5z "Jul 07 2026, 10:46:52 UTC")
> 
> I use codebase mcp for memory. I prefer opencode cli mostly, but crush coder is also good. Having a good and optimized [agents.md](http://agents.md/) file also helps for the overall quality...
> 
> 
> > 1
> > 
> > 
> > 
> > [u/marx2k](https://redlib.catsarch.com/user/marx2k)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow28w8y/?context=3#ow28w8y "Jul 07 2026, 11:07:56 UTC")
> > 
> > Can you explain how you use codebase MCP?
> > 
> > 
> > > 1
> > > 
> > > 
> > > 
> > > [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2atuc/?context=3#ow2atuc "Jul 07 2026, 11:20:53 UTC")
> > > 
> > > [https://github.com/DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)
> > > 
> > > 
> > > here it is, it is really easy to use and helps using less tokens so that your context window doesn't get full all the way up, it only searches and loads the required amount.
> > > 
> > > 
> > > > 1
> > > > 
> > > > 
> > > > 
> > > > [u/marx2k](https://redlib.catsarch.com/user/marx2k)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2fjgb/?context=3#ow2fjgb "Jul 07 2026, 11:51:08 UTC")
> > > > 
> > > > Oh I know. I went to the GitHub site when you first mentioned it. I'm just not clear on a good use case. So like do you use it by pointing your own code at it and then interact w the MCP? Or does the harness use the MCP and your code for optimized work?
> > > > 
> > > > 
> > > > I couldn't get the use from the GitHub description
> > > > 
> > > > 
> > > > > 1
> > > > > 
> > > > > 
> > > > > 
> > > > > [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2g0os/?context=3#ow2g0os "Jul 07 2026, 11:54:01 UTC")
> > > > > 
> > > > > You simply say index the codebase, it creates nodes. then into your agents md you can directly say always use context mcp for looking a specific file or a keyword first. etc...
> > > > > 
> > > > > 
> > > > > > 1
> > > > > > 
> > > > > > 
> > > > > > 
> > > > > > [u/marx2k](https://redlib.catsarch.com/user/marx2k)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2guhf/?context=3#ow2guhf "Jul 07 2026, 11:58:57 UTC")
> > > > > > 
> > > > > > Ok so that's what I'm asking. How you use it.
> > > > > > 
> > > > > > 
> > > > > > At my job I use Kiro which already has the context of my workspace but I also use ollama+opencode and so it might be helpful there for when I don't want to eat up costly credits w Kiro.
> > > > > > 
> > > > > > 
> > > > > > That's cool.
> > > > > > 
> > > > > > 
> > > > > > Im always on the hunt for useful MCP servers after diving into writing some for our internal processes at work.
> > > > > > 
> > > > > > 
> > > > > > My main concern is exfiltration.
> > > > > > 
> > > > > > 
> > > > > > > 1
> > > > > > > 
> > > > > > > 
> > > > > > > 
> > > > > > > [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2h2dy/?context=3#ow2h2dy "Jul 07 2026, 12:00:14 UTC")
> > > > > > > 
> > > > > > > It just works for me, never had any problems... local everything for the win

2

[u/Several-Tax31](https://redlib.catsarch.com/user/Several-Tax31)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow26gjf/?context=3#ow26gjf "Jul 07 2026, 10:50:58 UTC")

So you're assuming the rest of the world doesn't need other languages because you don't prompt them? For this reason you call it "bloated"? Great reasoning.

> 5
> 
> 
> 
> [u/Protopia](https://redlib.catsarch.com/user/Protopia)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow3gail/?context=3#ow3gail "Jul 07 2026, 14:54:45 UTC")
> 
> I don't think he is assuming that. He is saying that English is his need. A Chinese developer would need Chinese and not English.

2

[u/charmander_cha](https://redlib.catsarch.com/user/charmander_cha)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow35e2s/?context=3#ow35e2s "Jul 07 2026, 14:05:26 UTC")

Tomara que não

2

[u/Dull_Cucumber_3908](https://redlib.catsarch.com/user/Dull_Cucumber_3908)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow4omwd/?context=3#ow4omwd "Jul 07 2026, 17:58:34 UTC")

The thing is that the holly grail in AI is AGI, ie general intelligence, and not a field by field expert. I guess after the initial hype (the phase that we are currently in) it will settle we will see many small models doing what you expect to do (ie a model specializing in code using a specific stack).

1

[u/MilessEdgeworth](https://redlib.catsarch.com/user/MilessEdgeworth)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow260rx/?context=3#ow260rx "Jul 07 2026, 10:47:49 UTC")

Given how small model can be to just talk, I would assume an additional language weights are very smol

1

[u/mohelgamal](https://redlib.catsarch.com/user/mohelgamal)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow26g2q/?context=3#ow26g2q "Jul 07 2026, 10:50:53 UTC")

I looked into this and multilingual training is important for the logic of the model to develop, even in things not related to the task.

General purpose models out perform models trained on small datasets.

The way models retain data is like humans, you don’t memorize and recite the information required, instead, you establish neural connections between items. The more data comes in, the more the connections between the items is mapped better.

This is also why humans don’t run out of “memory” because all your memories are recorded as relationship between itemsp

1

[u/apinference](https://redlib.catsarch.com/user/apinference)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow2hkhe/?context=3#ow2hkhe "Jul 07 2026, 12:03:14 UTC")

Just fine-tune it for your own codebase. That would "route" the model towards something you need and use.

0

[u/numberwitch](https://redlib.catsarch.com/user/numberwitch)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow3095v/?context=3#ow3095v "Jul 07 2026, 13:41:23 UTC")

we got slopped again

1

[u/ea_man](https://redlib.catsarch.com/user/ea_man)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow3y3sz/?context=3#ow3y3sz "Jul 07 2026, 16:11:49 UTC")edited Jul 07 '26

Your first error is using an MoE for coding, dense model are better at specific tasks and intelligence.

Hence you have Coder models like [https://huggingface.co/unsloth/Qwen2.5-Coder-14B](https://huggingface.co/unsloth/Qwen2.5-Coder-14B), [https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct) ,that is good at coding and supposedly at following instructions / tools (not that one nowadays!). Instruct is often an alias of coder.

Then you have the specific autocomplete models that only know how to code, suck at speaking / instruct / anything else.

Weights are not just about knowledge, reasoning and intelligence emerges when you got a lot of relations and use those on the tokens, again MoE bad.

1

[u/fantasticsid](https://redlib.catsarch.com/user/fantasticsid)[Jul 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow6zusa/?context=3#ow6zusa "Jul 08 2026, 00:12:46 UTC")

Multi language support, as I understand the RYS guy's thesis, only impacts the first and last handful of layers -- the squishy middle of the clanker works in a non-linguistic space. It's hard to say what you'd actually end up compromising on if you trained the same number of parameters solely on English. You'd likely end up with the same (or lower) actual performance for a given parameter count.

1

[u/PossessionUsed7393](https://redlib.catsarch.com/user/PossessionUsed7393)[Jul 08 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/owc1xew/?context=3#owc1xew "Jul 08 2026, 18:02:55 UTC")

I don't think it's correct to say the model is spending a parameter on a different language. Models compact information of arbitrary size into the fixed parameter size, so it actually might easily fit in multiple languages without having much impact at all.

1

[u/Inevitable_Tea_5841](https://redlib.catsarch.com/user/Inevitable_Tea_5841)[Jul 09 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/owfdjdg/?context=3#owfdjdg "Jul 09 2026, 04:09:13 UTC")

The current paradigm relies on transfer learning between domains

0

[u/Able-Locksmith-1979](https://redlib.catsarch.com/user/Able-Locksmith-1979)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow27d7p/?context=3#ow27d7p "Jul 07 2026, 10:57:23 UTC")

Do you also prune your programmers for their legs, mouth, etc.

 You need a certain baseline and just fine tune on top of that, pruning the baseline will at a certain point work against you, currently you can hire mandarin programmers and create apps for a Spanish audience and it adds reasoning skills. You will need to make very difficult trade offs if you want to prune it, will you prune a new model with every library update? Etc etc.

 I think you are to early at the moment

> 1
> 
> 
> 
> [u/dsdt](https://redlib.catsarch.com/user/dsdt)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow27r1v/?context=3#ow27r1v "Jul 07 2026, 11:00:02 UTC")
> 
> It would be just a local option for those use only english... if you are multilingual just keep using the base model. I am just trying to find a solution about lowering the model size and without losing code quality.

0

[u/Southern_Sun_2106](https://redlib.catsarch.com/user/Southern_Sun_2106)[Jul 13 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ox7w6zi/?context=3#ox7w6zi "Jul 13 2026, 05:27:04 UTC")

If all you need is Laravel, you are not the target market. Moreover, you are in a very very small minority with your specific need. So nobody can afford to train specialized models like the one you need. In fact, you are lucky that there are models that are useful for Laravel (whatever Laravel is).

-3

[u/previse_je_sranje](https://redlib.catsarch.com/user/previse_je_sranje)[Jul 07 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1uprb5c/laravel_dev_running_qwen_36_35b_a3bdo_we_really/ow27j1i/?context=3#ow27j1i "Jul 07 2026, 10:58:29 UTC")

Troll

v0.36.0 [ⓘ View instance info](https://redlib.catsarch.com/info "View instance information")[<> Code](https://github.com/redlib-org/redlib "View code on GitHub")
