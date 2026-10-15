---
name: operator-standard-operators-as-functions
description: Guide for itemgetter with max/min, two frequency-sorting patterns (element vs. value frequency), scatter plot highlight, and reduce.
---

# operator — Standard Operators as Functions

The `operator` module provides callable equivalents of Python's built-in operators. The most
common use is `key=` functions for sorting and extracting max/min elements.

## itemgetter with max/min — Extracts the Whole Record

`max` and `min` with `key=itemgetter(n)` return the **full tuple**, not just the key value.
On an empty iterable, `max()` and `min()` raise `ValueError` naturally:

```python
from operator import itemgetter

records = [('alice', 85), ('bob', 92), ('carol', 78)]
winner = max(records, key=itemgetter(1))    # ('bob', 92) — full tuple
loser  = min(records, key=itemgetter(0))    # ('alice', 85)

# Extract just the winning name or score:
best_name  = max(records, key=itemgetter(1))[0]   # 'bob'
best_score = max(records, key=itemgetter(1))[1]   # 92

# Tuple unpacking also works:
name, score = max(records, key=itemgetter(1))
```

## Frequency Sorting — Two Distinct Patterns

### Pattern A: Sort items by their count (word/element frequency)

When your data is a sequence and you want items ranked by how often they appear:

```python
from collections import Counter
import operator

words = ['cat', 'dog', 'cat', 'bird', 'dog', 'cat']
freq = Counter(words)   # Counter({'cat': 3, 'dog': 2, 'bird': 1})

# Sort by frequency descending — freq.items() gives (word, count) pairs:
ranked = sorted(freq.items(), key=operator.itemgetter(1), reverse=True)
# [('cat', 3), ('dog', 2), ('bird', 1)]

# Single winner extraction — raises ValueError on empty:
top_item = max(freq.items(), key=operator.itemgetter(1))[0]   # 'cat'
```

### Pattern B: Sort a mapping's entries by the frequency of their values

When you have a `{key: value}` mapping and want entries ordered by how often each value
appears across the mapping, **count the values first**, then sort the counter's items:

```python
from collections import Counter
import operator

mapping = {'x': 'red', 'y': 'blue', 'z': 'red', 'w': 'green'}

# Step 1: count frequency of each VALUE
value_freq = Counter(mapping.values())   # Counter({'red': 2, 'blue': 1, 'green': 1})

# Step 2: sort (value, count) pairs by count — NOT the original mapping items
ranked_values = sorted(value_freq.items(), key=operator.itemgetter(1), reverse=True)
# [('red', 2), ('blue', 1), ('green', 1)]
```

This is different from `sorted(mapping.items(), ...)`, which would give `(key, value)` pairs.

## Scatter Plot with Max-Point Highlight

Find the max tuple, then unpack it into `ax.scatter(*max_pt)`:

```python
from operator import itemgetter
import numpy as np
import matplotlib.pyplot as plt

def plot_with_highlight(data):
    max_pt = max(data, key=itemgetter(1))   # tuple with max y-value
    pts = np.array(data)
    fig, ax = plt.subplots()
    ax.scatter(pts[:, 0], pts[:, 1], label='Points')
    ax.scatter(*max_pt, color='red', label='Max')
    ax.legend()
    return ax
```

## itemgetter for Multi-Key Sort and groupby

`itemgetter` works on dict keys and tuple indices for multi-field sorting:

```python
from operator import itemgetter
from itertools import groupby

articles = [
    {'category': 'tech', 'title': 'AI News'},
    {'category': 'sports', 'title': 'World Cup'},
    {'category': 'tech', 'title': 'Robotics'},
]
articles.sort(key=itemgetter('category', 'title'))

for cat, group in groupby(articles, key=itemgetter('category')):
    members = list(group)
```

When the groupby key involves a transformation (e.g., first character of a string), use a
lambda — `itemgetter` cannot slice or transform:

```python
# Group dict by first character of key — requires lambda, not itemgetter
items = sorted(my_dict.items(), key=lambda item: item[0][0])
for first_char, group in groupby(items, key=lambda item: item[0][0]):
    total = sum(v for _, v in group)
```

## reduce with operator.mul for Products

```python
from functools import reduce
from operator import mul, add

reduce(mul, [2, 3, 4], 1)   # 24  (initial=1 handles empty list)
reduce(add, [1, 2, 3], 0)   # 6
```
