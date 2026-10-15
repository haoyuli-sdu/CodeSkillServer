---
name: regex-enhanced-re-drop-in-with-lookbehin
description: 'Practical reference for the regex module: variable-length lookbehind, findall with trailing groups, non-capturing split, overlapping matches.'
---

# Python `regex` Module — Practical Reference

## Overview

`regex` is an enhanced drop-in replacement for the standard `re` module:

```python
import regex as re
```

All standard `re` functions work identically: `re.findall`, `re.search`, `re.match`, `re.sub`,
`re.split`, `re.compile`, `re.IGNORECASE`, `re.DOTALL`, etc.

## Key Addition: Variable-Length Lookbehind

Standard `re` requires fixed-width lookbehind assertions. `regex` supports variable-length:

```python
import regex as re

# Protect unescaped double-quotes — variable-length lookbehind
cell.value = re.sub(r'(?<=(^|[^\\])(\\\\)*)"', r'\\"', cell.value)
# Standard re would raise: error: look-behind requires fixed width pattern
```

## Extracting Structured Data with findall

When using `re.findall` with multiple capturing groups, it returns a **list of tuples**.

If the pattern ends with an anchoring group like `($|\n)`, that group appears as an extra
element in each tuple. Slice it off:

```python
import regex as re, pandas as pd

text = "Name: Alice, Email: alice@x.com, Age: 30, Country: France\n"
pattern = r"Name: (.*?), Email: (.*?), Age: (.*?), Country: (.*?)($|\n)"
matches = re.findall(pattern, text)
# matches = [('Alice', 'alice@x.com', '30', 'France', '\n')]
#                                                       ^^^^ unwanted trailing group
data = [m[:-1] for m in matches]   # drop last element
df = pd.DataFrame(data, columns=["Name", "Email", "Age", "Country"])
df["Age"] = df["Age"].astype(int)
```

## Use `(.*?)` Not `(\w+)` for Multi-Word Fields

`\w+` matches only word characters (no spaces). When a field can contain spaces, use lazy
`(.*?)`:

```python
# WRONG: r"Category: (\w+)"         → captures only "Machine" from "Machine Learning"
# RIGHT: r"Category: (.*?)($|\n)"   → captures "Machine Learning" up to line end
```

## Splitting Text into Sentences

When splitting on period boundaries with `re.split`, use a **non-capturing** pattern to
avoid including the delimiter in the output list:

```python
# Non-capturing split: delimiter not included in results
sentences = re.split(r'\.\s*', text)
sentences = [s for s in sentences if s.strip()]   # remove empty strings

# Capturing split: delimiter IS included as separate elements
# re.split(r'(\.\s*)', text) → ['Hello', '. ', 'World', '.', '']  ← unwanted extras
```

## Overlapping Matches (regex-only feature)

```python
import regex as re
re.findall(r'\d+', '1234', overlapped=True)  # ['1234', '234', '34', '4']
```

## Word Frequency with regex

```python
import regex as re, pandas as pd

words = re.findall(r"\b\w+\b", text.lower())
words = [w for w in words if w not in STOPWORDS]
word_counts = pd.Series(words).value_counts().rename(None)
```

## Directory Existence Check

When a task raises `FileNotFoundError` for a missing directory:

```python
import os

if not os.path.isdir(directory_path):
    raise FileNotFoundError(f"The specified directory does not exist.")
```
