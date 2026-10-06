Title: gpt oss 120b or qwen 3.5 for non-english/chinese/russian language - r/LocalLLaMA

URL Source: https://redlib.catsarch.com/r/LocalLLaMA/comments/1rpqy9z/

Markdown Content:
[red lib.](https://redlib.catsarch.com/)

Feeds

MAIN FEEDS

[Home](https://redlib.catsarch.com/)[Popular](https://redlib.catsarch.com/r/popular)[All](https://redlib.catsarch.com/r/all)

- [x] in /r/LocalLLaMA 

[reddit](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rpqy9z/#popup)

# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/comments/1rpqy9z/

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rpqy9z/#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1rpqy9z/)

[settings](https://redlib.catsarch.com/settings)

[r/LocalLLaMA](https://redlib.catsarch.com/r/LocalLLaMA)•[u/Moreh](https://redlib.catsarch.com/user/Moreh)•Mar 10 '26

# [Discussion](https://redlib.catsarch.com/r/LocalLLaMA/search?q=flair_name%3A%22Discussion%22&restrict_sr=on) gpt oss 120b or qwen 3.5 for non-english/chinese/russian language

**Edit for clarity:** I'm asking about performance on **non-major** languages — specifically Indonesian. My data is mixed English/Indonesian.

Hi all,

I'm planning some batch text analysis on ~30k rows of short strings in mixed English and Indonesian. I'd prefer a smarter model even if it's slower.

The obvious open-source choices seem to be Qwen 3.5, GLM, and GPT OSS 120B. GPT OSS looks slightly faster so I'm leaning that way, but does anyone have experience with how these models compare on Indonesian language tasks specifically?

Thanks for any input

 2  Upvotes

*   [perma link](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rpqy9z/gpt_oss_120b_or_qwen_35_for/)
*   [reddit](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rpqy9z/#popup)# You are about to leave Redlib

Do you want to continue?

https://www.reddit.com/r/LocalLLaMA/comments/1rpqy9z/gpt_oss_120b_or_qwen_35_for/

[No, go back!](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rpqy9z/#)[Yes, take me to Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1rpqy9z/gpt_oss_120b_or_qwen_35_for/)  

67% Upvoted

7 comments sorted by

4

[u/ABLPHA](https://redlib.catsarch.com/user/ABLPHA)[Mar 10 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rpqy9z/gpt_oss_120b_or_qwen_35_for/o9mv71y/?context=3#o9mv71y "Mar 10 2026, 08:15:51 UTC")

Definitely not GPT OSS 120B. It feels like it has never actually been trained on any Russian text and just translates English into it a bit too literally. Don't know about its Chinese quality tho

1

[u/catlilface69](https://redlib.catsarch.com/user/catlilface69)[Mar 10 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rpqy9z/gpt_oss_120b_or_qwen_35_for/o9mvmtm/?context=3#o9mvmtm "Mar 10 2026, 08:20:11 UTC")

Definitely use Qwen. Both GLM and GPT-OSS are awful in russian

1

[u/MelodicRecognition7](https://redlib.catsarch.com/user/MelodicRecognition7)[Mar 10 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rpqy9z/gpt_oss_120b_or_qwen_35_for/o9mw14j/?context=3#o9mw14j "Mar 10 2026, 08:24:09 UTC")

clarify your question, you need to translate Indonesian into Chinese or Russian?

I don't know about Indonesian or Chinese; the best Russian is in Gemma3 27B, GPT-OSS has awful Russian, Qwen3.5 Heretic v2 has broken Russian, Heretic v1 is better.

> 1
> 
> 
> 
> [u/Moreh](https://redlib.catsarch.com/user/Moreh)[Mar 10 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rpqy9z/gpt_oss_120b_or_qwen_35_for/o9n541d/?context=3#o9n541d "Mar 10 2026, 09:53:15 UTC")
> 
> as below I am really sorry for the lack of clarity. NOT (just) the major languages like Chinese and English. the data IS mixed english indonesian. Thankyou for your feedback.

1

[u/Middle_Bullfrog_6173](https://redlib.catsarch.com/user/Middle_Bullfrog_6173)[Mar 10 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rpqy9z/gpt_oss_120b_or_qwen_35_for/o9myf3v/?context=3#o9myf3v "Mar 10 2026, 08:48:09 UTC")edited Mar 10 '26

Assuming I'm parsing the question correctly you are interested in performance on mixed English and Indonesian. Not Chinese/Russian. Are your texts all one language, or are English and Indonesian mixed within a single prompt?

In my experience gpt oss is quite good with smaller languages as long as you do not need reasoning and the data in monolingual. With code mixing its non-English ability deteriorates. In that case (large enough) Qwen and Gemma models are much better.

I don't have experience with Indonesian specifically though.

> 1
> 
> 
> 
> [u/Moreh](https://redlib.catsarch.com/user/Moreh)[Mar 10 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rpqy9z/gpt_oss_120b_or_qwen_35_for/o9n51kv/?context=3#o9n51kv "Mar 10 2026, 09:52:37 UTC")
> 
> I am really sorry - i think i sent that post before my coffee hit in. NOT (just) the major languages like Chinese and English. the data IS mixed english indonesian. Thankyou for your feedback.

1

[u/General_Arrival_9176](https://redlib.catsarch.com/user/General_Arrival_9176)[Mar 11 '26](https://redlib.catsarch.com/r/LocalLLaMA/comments/1rpqy9z/gpt_oss_120b_or_qwen_35_for/o9swgtn/?context=3#o9swgtn "Mar 11 2026, 04:59:16 UTC")

qwen generally performs better on non-english languages in my experience. id go with the qwen3.5 for indonesian specifically. gpt oss 120b might have more raw capability but qwen has better multilingual training coverage. id try q4 first since the benchmark showed its close enough to bf16

v0.36.0 [ⓘ View instance info](https://redlib.catsarch.com/info "View instance information")[<> Code](https://github.com/redlib-org/redlib "View code on GitHub")
