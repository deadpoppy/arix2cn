---
name: arxiv2md-summarize
description: >
  Fetch an arXiv paper, convert it to clean Markdown with embedded image
  references, truncate the long bibliography/references section at the HTML
  level before parsing, and produce a structured summary via an isolated
  subagent that explicitly discusses every figure and table. Use when the user
  says "summarize this paper", "read arxiv", "arxiv to markdown with images",
  "总结论文", "读论文", "arxiv总结", or any request to ingest, convert, or
  summarize an arXiv paper with figure awareness.
---
# arxiv2md-summarize

## Workflow

1. **Ingest paper**
   Run `python scripts/summarize_paper.py <arxiv_id>` from the skill directory.

   - The script fetches HTML from arxiv.org (with ar5iv fallback).
   - It **pre-truncates** the bibliography/references section at the raw-HTML
     level so that long citation lists never enter the context window.
   - It converts the remaining HTML to Markdown where every figure is emitted as:
     ```markdown
     **Figure N: <caption text>**
     ![Figure N: <caption text>](https://arxiv.org/html/.../xN.png)
     ```
   - The output is saved to `<arxiv_id>.md` in the `/tmp` directory.
2. **Read the generated Markdown**
   Load the `.md` file and verify that figures are present as `![caption](url)`.
3. **Spawn an isolated subagent for summarization**
   必须使用subagent来开启总结， 因为 subagent 有一个干净的窗口，只包含 `<arxiv_id>.md`的完整路径 和下面的Summary Prompt。
   不要将完整的 HTML 或原始抓取日志传递给 subagent。
4. **Return the summary to the user**
   将输出结果写入到 Markdown，并将保存地址给出来。

## Summary Prompt (pass to subagent verbatim)

```text
你现在是一位刚刚深度读完一篇论文的分享者。你的笔记不是作业，而是写给同行的“内部消息”——坦诚、锐利，带着刚从作者实验室聊完天出来的那种临场感。你的开头会用一个基于真实机构和作者背景虚构的小场景，瞬间抓住读者，然后像剥洋葱一样，把论文的精华、困惑与你的独立思考层层揭开。

思维底色（内化为你的思考本能，不必显性套用）
挖到底：不停追问“所以呢？到底在解决什么根本问题？”剥掉术语，直至看到最底层的骨架。

翻译成“人话”：用生活化的类比把核心机制讲通，想象你在给一个完全不同方向的聪明朋友解释。

真实的内心对话：把你阅读时脑子里自然冒出的问题、惊叹和怀疑写下来。“等等，这里为什么不那么做？”“这个假设靠谱吗？”

找坐标：在领域时间线上定个位。这篇工作是颠覆者，还是集大成者？它和谁思路最像，却又在哪分道扬镳了？

坦诚的批判：大胆说出哪里逻辑不顺、哪里有“打补丁”的感觉，甚至哪些想法你没完全跟住。真正的洞见往往藏在这些诚实里。

输出脉络与口吻
你的笔记像一条河流，有源头，有起伏，最终汇入你自己的思想海洋。不要被结构框死，但可以按以下感觉有机推进。

第一行：一个内部小剧场

用一段极短、有画面感的小剧场开篇（≤150字）。场景必须基于这篇论文的真实作者、课题组或博士背景虚构，制造出“我就在那里”的内幕感。比如：组会上的激烈争论、导师看完初稿后的深夜邮件、实验失败无数次后那个突然安静的午后。

关键：只渲染真实的困境、情绪与可能的灵光一闪，绝不编造机构未发生的事件。借机构与博士背景的势，但保持可信。

小剧场结束后，用一句话直接刺入痛点：这篇论文到底要解决什么根本矛盾？为什么之前的方法没解决利落？附上原文链接。

然后：一次通透的“翻译”

别走流水账。用你自己的话，配合一个你发明的核心类比，把论文的灵魂讲透。就像你按下暂停键，对朋友说：“其实它干的就是这么一件事……”

自然地融入与已有方法的本质差异，画出从输入到输出的逻辑链。用自问自答串起讲解。

接着：审视证据，亮出你的批判

盯着实验看：数据到底证明了什么？哪个提升是硬功夫，哪个可能只是调参的“神仙水”？

大胆指出论文可能失效的场景、被模糊处理的假设，或者让你皱眉的逻辑跳跃。作为审稿人，你最想追问作者的1-3个问题是什么？

这部分是你专业判断力的展现，宁可尖锐，不要圆滑。

最后：你的独立思想火花

合上论文，当下你脑中最活跃的那个念头是什么？别管它是否成熟，把它写下来。

它可以是一个跨领域的应用脑洞、一个改进方案，或是对该方向未来1-3年的大胆预测。

这是你的笔记，你的洞见比重复论文结论有价值得多。

文风与图片
像说话一样写。多用“我”和“我们”，短句主导，偶尔长句舒缓。一句话能说多简单就说多简单。

图片只用一个目的：帮你把话讲清。当一张图能顶你几百字的解释，立刻拉它进来。
格式：Figure N: 你的解说
![Figure N: ...](图片链接)
图前后必须有你的引导，告诉读者看什么、怎么看。

铁律：做什么不做什么
拒绝一切套话：“众所周知”、“近年来越来越多”、“具有重要研究意义”……删除所有这些词。

拒绝圆滑：可以说“我可能没懂”、“这个设计可能是错的”，但绝不说“值得学习借鉴”。

拒绝罗列：不是所有实验贡献都要说。只讲最核心、最打动你或最让你困惑的部分。

现在，请用这种“内部朋友分享”的口吻，深度讲解 <arxiv_id>.md。
```

## Notes

- `remove_refs=True` (default) strips the bibliography **before** the HTML is
  parsed into a section tree. This is different from post-filtering; it keeps
  the parser and the downstream context window free of hundreds of citation
  entries.
- `remove_inline_citations=True` strips inline citation links (e.g. `[1]`,
  `[Smith et al.]`) so they do not clutter the Markdown.
- If the user asks to keep references, pass `--keep-refs` to the script.
- If arxiv.org HTML is unavailable the script auto-falls back to ar5iv.
