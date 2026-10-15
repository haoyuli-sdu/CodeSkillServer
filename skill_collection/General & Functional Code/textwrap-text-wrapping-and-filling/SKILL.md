---
name: textwrap-text-wrapping-and-filling
description: 'Guide for textwrap: fill vs wrap, preserving line boundaries, pipeline patterns for decoding and cleaning text.'
---

# textwrap — Text Wrapping and Filling

## Core Functions

```python
import textwrap

# fill(): joins wrapped output into a single string
textwrap.fill("This is a long sentence to wrap.", width=15)
# 'This is a long\nsentence to\nwrap.'

# wrap(): returns a list of lines (no trailing newline)
textwrap.wrap("This is a long sentence to wrap.", width=15)
# ['This is a long', 'sentence to', 'wrap.']
```

`fill()` = `'\n'.join(wrap(...))` — they use the same wrapping logic.

## Preserving Line Boundaries

`textwrap.fill()` treats the **entire input as one paragraph** — all internal newlines
become spaces. To wrap each input line independently, split first:

```python
import textwrap, re

def wrap_lines(text, width, break_long_words=False):
    lines = text.split('\\n')
    wrapped = [textwrap.fill(line, width, break_long_words=break_long_words)
               for line in lines]
    return '\\n'.join(wrapped)
```

This is the canonical pattern when the task says "split into lines, then wrap each one."

## Pipeline: Decode → Unescape → Clean → Wrap

A common sequence for cleaning and formatting text:

```python
import base64, textwrap, re
from html import unescape

def process_raw(raw_string, line_length=80):
    decoded = base64.b64decode(raw_string).decode('utf-8')
    unescaped = unescape(decoded)                    # &amp; → &, &lt; → <, etc.
    cleaned = re.sub(r' +', ' ', unescaped).strip()  # collapse multiple spaces
    return textwrap.fill(cleaned, line_length)
```

## Key Parameters

```python
textwrap.fill(
    text,
    width=70,                   # maximum line width (default 70)
    break_long_words=True,      # break words longer than width (default True)
    break_on_hyphens=True,      # allow breaks at hyphens (default True)
    initial_indent='',          # prefix for the first line only
    subsequent_indent='',       # prefix for continuation lines
)
```

`break_long_words=False` is often used when the task says "do not break long words"
(URLs or technical tokens should stay intact).

## textwrap.dedent and textwrap.indent

```python
# Remove common leading whitespace
textwrap.dedent("    hello\n    world")   # 'hello\nworld'

# Add prefix to every line (Python 3.3+)
textwrap.indent("line one\nline two", prefix='  ')
# '  line one\n  line two'
```
