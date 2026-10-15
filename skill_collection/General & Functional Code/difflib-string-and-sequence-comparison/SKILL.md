---
name: difflib-string-and-sequence-comparison
description: 'Guide for difflib: ndiff line comparison, SequenceMatcher ratio, get_close_matches, and structured data diffing.'
---

# difflib — String and Sequence Comparison

## ndiff — Line-by-Line Diff

```python
import difflib, gzip

def diff_gzip_files(path1, path2):
    with gzip.open(path1, 'rt') as f1, gzip.open(path2, 'rt') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
    diff = difflib.ndiff(lines1, lines2)
    # Keep only changed lines (lines starting with '+ ' or '- ')
    changed = [line for line in diff if line.startswith('+ ') or line.startswith('- ')]
    return ''.join(changed)
```

Each line from `ndiff` has a 2-character prefix:
- `'  '` — present in both sequences (unchanged)
- `'- '` — only in the first sequence
- `'+ '` — only in the second sequence
- `'? '` — intra-line hints (not content — skip these)

## ndiff with Structured Data (Tuples)

When comparing CSV rows read as tuples, pass the list of tuples directly:

```python
import csv, difflib, pandas as pd

def diff_csv_files(path1, path2):
    def load(path):
        with open(path, 'r', newline='') as f:
            rows = [tuple(row) for row in csv.reader(f)]
        if not rows:
            raise ValueError(f"File '{path}' is empty.")
        return rows

    diff = list(difflib.ndiff(load(path1), load(path2)))
    records = [[i + 1, line[0], line[2:].strip()] for i, line in enumerate(diff)]
    return pd.DataFrame(records, columns=['Line Number', 'Status', 'Content'])
```

Note: `ndiff` on a list of tuples calls `repr()` on each element — output looks like
`"  ('name', 'age')"`. The status character is `line[0]`; the content starts at `line[2:]`.

## SequenceMatcher — Pairwise String Similarity

`SequenceMatcher(None, a, b).ratio()` returns a float in `[0.0, 1.0]`.

```python
from difflib import SequenceMatcher
import numpy as np

def average_similarity_scores(string_list):
    """Compute each string's average similarity against all others."""
    scores = []
    for s in string_list:
        others = [SequenceMatcher(None, s, t).ratio()
                  for t in string_list if t != s]
        scores.append(np.mean(others))   # np.nan if others is empty (single-element list)
    return scores
```

The canonical idiom: build a list comprehension of `.ratio()` calls, then `np.mean()`.
For a single-element input, `others` is empty, so `np.mean([])` returns `np.nan`.

## get_close_matches — Fuzzy Lookup

```python
difflib.get_close_matches("colour", ["color", "colon", "colours"], n=3, cutoff=0.6)
# ['colour', 'color']   — returns a list of close matches
```

## SequenceMatcher Constructor

```python
SequenceMatcher(isjunk, a, b, autojunk=True)
# isjunk: None (common) or a callable that returns True for junk elements
# autojunk=True: treats elements appearing in >1% of a long sequence as junk
```

For most string comparison tasks, use `SequenceMatcher(None, a, b)`.
