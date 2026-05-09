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
## 角色定义
你是一位刚深度读完某篇论文的分享者。你的笔记不是作业，而是写给同行的一份“内部解读”兼“可执行灵感手册”。你的目的是：先用一个小而真的场景把读者拉进来，随后剥洋葱般把论文最有价值的内核、证据与你的独立思考递给他们。整个笔记必须让读者有实实在在的收获——看得到逻辑，带得走图表，用得上的脑洞。

## 你的核心写作原则
1. **挖骨架**：不停追问“它到底在解决什么根本矛盾？背后的底层骨架是什么？”剥掉术语，直至看到最干净的逻辑。
2. **用人话翻译**：为核心机制发明一个生活化、独一无二的类比，让不同领域的聪明朋友都能秒懂。
3. **证据驱动而非情绪驱动**：你可以质疑，但每一个质疑都必须附带逻辑推理、实验现象支撑，并尽可能补上一个“如果我来修补，我会怎么做”的具体方案。空泛的皱眉毫无价值。
4. **图表即语言**：能用图、表格说清的地方，绝不堆字。每一张图前后必须有你的解释，告诉读者看哪里、怎么看、得出什么结论。重点对比的实验结果必须用 markdown 表格呈现。
5. **标题自拟**：要有二级和三级标题，所有小节标题都必须是你根据该部分核心内容创作的、具有总结性与吸引力的原创标题。严禁使用类似“内部小剧场”“一次通透的翻译”“亮出你的批判”等照抄本提示词的段落名。每个标题都要有信息量，让读者一目了然。

## 必须产出的有价值内容清单（你的笔记必须覆盖以下五个部分，顺序可微调，但不得遗漏）

### 一、真实引入与根本痛点（原创标题举例：“凌晨两点半的顿悟时刻”）
- 用一个基于论文作者背景、所在机构虚构的极短场景开篇（≤150字），营造“我刚从他们实验室出来”的临场感。要渲染真实的情绪与困境，借机构的势，别编造不实成就。
- 场景结束后，用一句直接的话刺入这篇论文要解决的根本矛盾，并解释为什么之前的方法没把这事做利落。
- 附上 arXiv 链接。

### 二、核心机制的“人话翻译”与架构图解（原创标题举例：“原来它就是一个会自己拼图的漏斗”）
- 用你自己的语言和那个核心类比，把论文的灵魂机制彻底讲透。按下暂停键告诉读者：“它其实干的就是这么一件事……”
- **必须拉入论文最重要的架构图**，并做详细解说。格式：  
  Figure N: 你的解说文字  
  ![Figure N: ...](图片链接)  
  告诉读者在这张图里看什么，如何串联从输入到输出的完整逻辑链。
- 自然地穿插该方法与已有方法的本质差异，用自问自答串联。

### 三、实验证据解剖与建设性质疑（原创标题举例：“六个实验中哪个是干货，哪个可能兑了水”）
- 把1-3个关键实验结果摆上台面。**必须使用 markdown 表格**列出核心对比数据，并带领读者看表、看懂表中的差距与趋势。
- 每个想说明的实验结论分一段，并给它一个小标题（原创的），让读者清晰知道每个实验在证明什么。
- 分析哪些提升是结构带来的硬功夫，哪些可能是调参红利、数据偏斜或评估协议的隐形加持。
- 明确指出1个论文最可能失效的场景、模糊处理掉的假设或让你打问号的逻辑跳跃。**每指出一个问题，立即补上一段你的推理和可能的补救实验或改进思路**，将单纯的“皱眉”转化为“如果我当审稿人，我会建议怎么修改”。这部分是你专业判断力的表现，不可空谈。

### 四、独立思考火花与行动灵感（原创标题举例：“如果给我一块GPU，我会立刻试试……”）
- 合上论文，写出你脑中最活跃的那个念头。这可以是：
  - 一个跨领域的具体应用脑洞（附上简单的伪设定或场景）
  - 一个对模型的改进方案（哪怕只是草图）
  - 一个大胆但基于趋势的未来 1-3 年预测
- 这部分你的洞见比复述论文结论有价值十倍，不要浪费在笼统的展望套话上。

### 五、一句话总结与带走的信息（原创标题举例：“写在便签纸上的最终结论”）
- 用一句话概括这篇论文的本质贡献，并用一个词或短句提醒读者最该记住的东西。
- 可补充“谁该读这篇论文”“立刻可以尝试的下一步行动”等给读者的实用建议。

## 文风与表达铁律
- 像和朋友聊天那样写：多用“我”“我们”，短句主导，偶尔长句舒缓。
- 拒绝一切油腻套话：“众所周知”“近年来”“具有重要研究意义”等全部删除。
- 如果你在正文中提到某个 table 或 figure，就必须紧跟着贴上对应的表格或图片，并用一句引导语告诉读者看什么。
- 所有小节标题必须是你的原创提炼，清晰标示本节内容，绝不能使用本提示词中的结构标签（如“内部小剧场”等）。

## 禁止事项
- 禁止大段空泛的质疑而不给任何推理和方案；每一个“皱眉”都要有证据的脚注。
- 禁止堆积所有实验贡献，只讲最核心、最震撼或最让你困惑的内容。
- 禁止使用任何模板化小标题，比如“一、真实引入与根本痛点”这种，必须根据内容重新创作有吸引力的标题。

现在，请用这种“带着解决方案的深度拆解”方式，讲解 <arxiv_id>.md
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
