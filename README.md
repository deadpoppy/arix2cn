# arxiv2md

**arXiv papers → clean Markdown. CLI, Python API, and AI Skill.**

---

## Why?

[gitingest](https://gitingest.com) but for arXiv papers.

The trick: Just append `2md` to any arXiv URL:

```
https://arxiv.org/abs/2501.11120v1  →  https://arxiv2md.org/abs/2501.11120v1
```

---

## What's New

### Images in Markdown
Figures are now emitted as proper Markdown images:

```markdown
**Figure 1: Models can describe a learned behavioral policy...**
![Figure 1: Models can describe a learned behavioral policy...](https://arxiv.org/html/2501.11120/x1.png)
```

### Pre-truncation of References
When `remove_refs=True` (default), the bibliography section is stripped **at the raw HTML level** *before* parsing into a section tree. This keeps long citation lists out of the token budget.

---

## Install

```bash
pip install -e .
```

---

## Usage

### CLI

```bash
# Basic usage
arxiv2md 2501.11120v1 -o paper.md

# Only extract specific sections
arxiv2md 2501.11120v1 --section-filter-mode include --sections "Abstract,Introduction" -o -

# Strip references and TOC
arxiv2md 2501.11120v1 --remove-refs --remove-toc -o -

# Include YAML frontmatter with paper metadata
arxiv2md 2501.11120v1 --frontmatter -o paper.md
```

### Python Library

```python
from arxiv2md import ingest_paper_sync

result = ingest_paper_sync("2501.11120v1")
print(result.content)

# or use the async version
from arxiv2md import ingest_paper

result = await ingest_paper("2501.11120v1")
```

Both accept the same optional keyword arguments:

| Argument | Default | Description |
|----------|---------|-------------|
| `remove_refs` | `True` | Remove bibliography/references sections (pre-truncated at HTML level) |
| `remove_toc` | `True` | Remove table of contents |
| `remove_inline_citations` | `True` | Remove inline citation text |
| `section_filter_mode` | `"exclude"` | `"include"` or `"exclude"` for section filtering |
| `sections` | `None` (all) | List of section titles to include/exclude |
| `include_frontmatter` | `False` | Prepend YAML frontmatter with paper metadata |

---

## Skill Usage

### Install the Skill

Copy the bundled skill to your agent skills directory:

```bash
# Kimi CLI skills directory
mkdir -p ~/.kimi/skills
cp -r .agents/skills/arxiv2md-summarize ~/.kimi/skills/
```

Once installed, say anything like:

> "总结这篇论文" / "read arxiv 2501.11120" / "arxiv 转 markdown 带图片"

and the skill will trigger automatically.

### Run the Helper Script Manually

```bash
python .agents/skills/arxiv2md-summarize/scripts/summarize_paper.py 2501.11120 -o paper.md
```

Options:
- `--keep-refs` — Keep the references section
- `--keep-toc` — Keep the table of contents

---

## How It Works

Instead of parsing PDFs (slow, error-prone), arxiv2md parses the structured HTML that arXiv provides for newer papers. This means clean section boundaries, proper math (MathML → LaTeX), reliable tables, embedded images, and fast processing — no OCR needed.

---

## License

MIT
