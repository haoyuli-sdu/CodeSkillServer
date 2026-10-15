---
name: itertools-iterator-building-blocks
description: 'Practical reference for itertools: chain flattening, zip_longest transposition vs consecutive-pair zip, combinatoric functions, product-to-string patterns, groupby sort-first, and cycle.'
---

# itertools — Iterator Building Blocks

## Combinatoric Functions at a Glance

| Function | Repeats? | Ordered? | Typical use |
|---|---|---|---|
| `combinations(seq, r)` | No | No | Choose r items, no repeats, order irrelevant |
| `combinations_with_replacement(seq, r)` | Yes | No | Allow repeated items |
| `permutations(seq, r)` | No | Yes | r-length ordered arrangements |
| `product(seq, repeat=r)` | Yes | Yes | All r-tuples (equivalent to r nested loops) |

## chain: Flattening Nested Iterables

`chain(*nested)` and `chain.from_iterable(nested)` both flatten one level deep:

```python
from itertools import chain

# Flatten a tuple-of-tuples of strings and convert to integers
T1 = (('2', '3'), ('4', '1'))
int_list = [list(map(int, x)) for x in T1]        # [[2, 3], [4, 1]]
flattened = list(chain(*int_list))                  # [2, 3, 4, 1]
total = sum(flattened)                              # 10

# Use the total to drive a downstream computation (e.g. generate random data):
import random
values = [random.randint(0, 100) for _ in range(total)]
```

`chain.from_iterable` is equivalent but avoids unpacking:

```python
# Count letters across multiple word lists
from collections import Counter
word_groups = [['apple', 'art'], ['banana']]
all_letters = list(chain.from_iterable(word_groups))   # ['apple', 'art', 'banana']
counts = Counter(chain.from_iterable(all_letters))     # per-character count
```

## zip_longest: Transposing Rows to Columns

`zip_longest` groups elements **at the same position** across multiple sequences — it is a column-wise transpose, not a pairwise operation:

```python
from itertools import zip_longest
import numpy as np

# Transpose: each column groups one position from every tuple
data = [('label_a', 1.0, 2.5), ('label_b', 3.0), ('label_c', 4.0, 6.0)]
columns = list(zip_longest(*data, fillvalue=np.nan))
# columns[0] = ('label_a', 'label_b', 'label_c')   <- first position (labels)
# columns[1] = (1.0, 3.0, 4.0)                     <- second position
# columns[2] = (2.5, nan, 6.0)                     <- third position (nan for short rows)

# Mean of numeric values per column, skipping non-numeric entries:
means = []
for col in columns:
    nums = [v for v in col if isinstance(v, (int, float))]
    means.append(np.nanmean(nums) if nums else np.nan)
    # np.nanmean ignores np.nan entries; isinstance check excludes strings/None
```

**fillvalue must be `np.nan`, not `0`** — using `fillvalue=0` makes missing positions appear as zeros, which become valid numbers that pull column means toward zero.

**For consecutive pairs use regular `zip`, not `zip_longest`:**

```python
# Consecutive-pair pattern (e.g. distances between adjacent points):
from scipy.spatial import distance

points = [(0, 0), (1, 1), (4, 5)]
distances = [distance.euclidean(a, b) for a, b in zip(points, points[1:])]
# zip(seq, seq[1:]) yields exactly len(seq)-1 pairs — correct for consecutive differences
```

`itertools.zip` does **not exist** — the builtin `zip()` is what you want for equal-length pairing.

## product: All Ordered Tuples Including Repeats

`product` returns tuples. Join them to strings when string keys or formatted values are needed:

```python
import itertools, string

# All 2-character strings from the lowercase alphabet (including 'aa', 'bb', etc.)
letter_pairs = [''.join(p) for p in itertools.product(string.ascii_lowercase, repeat=2)]
# ['aa', 'ab', ..., 'zz']  — 676 entries, string keys

# All Planet:Element formatted pairs
PLANETS = ['Mercury', 'Venus', 'Earth']
ELEMENTS = ['H', 'He', 'O']
pair_strings = [f"{p}:{e}" for p, e in itertools.product(PLANETS, ELEMENTS)]
# ['Mercury:H', 'Mercury:He', ..., 'Earth:O']
```

`combinations_with_replacement` covers "r-length subsets where repeats are allowed but order doesn't matter" — distinct from `product` where order matters.

## combinations: Subsets and Correlation Pairs

`combinations(seq, r)` generates unordered subsets. Common patterns:

```python
import itertools, math
import pandas as pd

# Product of subset sums (only when subset_size is valid):
def subset_product(elements, subset_size, top_n=2):
    if subset_size <= 0 or subset_size > len(elements):
        return 1, pd.Series([])
    subsets = list(itertools.combinations(elements, subset_size))
    sums = [sum(s) for s in subsets]
    product = math.prod(sums)
    top = pd.Series(sorted(sums, reverse=True)[:top_n])
    return product, top

# DataFrame column pairs above a correlation threshold
def corr_pairs(df, threshold=0.7):
    corr = df.corr().abs()
    return [(c1, c2) for c1, c2 in itertools.combinations(df.columns, 2)
            if corr.loc[c1, c2] > threshold]
```

## permutations: Ordered Arrangements

Use `permutations` when every ordering is a distinct outcome:

```python
from itertools import permutations
import math

def factorial_sums(numbers):
    if not numbers:
        return [], []
    all_perms = list(permutations(numbers))
    fact_sums = [sum(math.factorial(n) for n in perm) for perm in all_perms]
    return fact_sums, all_perms

# Two-character strings with all 26 letters (no repeats + doubles):
import string
ALPHABETS = string.ascii_lowercase
no_repeat = [''.join(p) for p in permutations(ALPHABETS, 2)]   # 650 items
with_doubles = [c * 2 for c in ALPHABETS]                       # 26 items ('aa'..'zz')
all_pairs = no_repeat + with_doubles                             # 676 total
```

## groupby: Sort-First Requirement

`groupby` only merges **consecutive** equal keys. Sort by the grouping key before calling:

```python
from itertools import groupby

records = [('apple', 5), ('avocado', 3), ('banana', 2), ('blueberry', 7)]
records.sort(key=lambda item: item[0][0])   # sort by first character

for first_char, group in groupby(records, key=lambda item: item[0][0]):
    total = sum(v for _, v in group)        # consume the group iterator immediately
    print(first_char, total)
```

The key function extracts the grouping attribute from each element. Use `lambda` (not `itemgetter`) when grouping by a character within a field.

## cycle: Infinite Color/Category Cycling

```python
from itertools import cycle
import matplotlib.pyplot as plt

colors = cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k'])
fig, ax = plt.subplots()

for series_name, series_data in grouped_data:
    ax.plot(series_data, color=next(colors), label=series_name)

ax.legend()
return ax
```

`next(colors)` advances one step per call. Never consume a `cycle` with `list()` — it is infinite.
