---
name: collections-counter-defaultdict-orderedd
description: 'Practical guide for collections module: Counter frequency counting, defaultdict aggregation, bigram patterns, deque mixed-type iteration, and flat-directory file processing.'
---

# collections — Counter, defaultdict, OrderedDict, deque

## Counter: Frequency Counting

`Counter` is a dict subclass; missing keys return `0`, no `KeyError`. The return type is `Counter`, which is acceptable wherever `dict` is expected (`isinstance(c, dict)` is `True`).

```python
from collections import Counter

c = Counter(['apple', 'banana', 'apple', 'cherry'])
# Counter({'apple': 2, 'banana': 1, 'cherry': 1})

c = Counter("abracadabra")
# Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
```

### most_common() — (element, count) tuples, descending

```python
c = Counter('aabbccc')
c.most_common(2)       # [('c', 3), ('a', 2)]
c.most_common(1)[0]    # ('c', 3) — the tuple
c.most_common(1)[0][0] # 'c'      — element only
c.most_common(1)[0][1] # 3        — count only
c.most_common()        # all items, sorted by frequency descending
```

### Updating a Counter

```python
c = Counter()
c.update('hello')        # adds character frequencies
c.update({'x': 5})       # adds from dict
c.update(['a', 'b'])     # adds from iterable

# Direct increment (also works)
c['word'] += 1
```

### Counter → dict

`Counter` is already a dict subclass. Wrap in `dict()` only if the caller explicitly checks `type(x) == dict`:

```python
dict(counter)            # plain dict, same content
```

## Building DataFrames from Counter

```python
from collections import Counter
import pandas as pd

counts = Counter(['apple', 'banana', 'apple'])

# Single-column DataFrame, words as row index
df = pd.DataFrame.from_dict(counts, orient='index', columns=['Count'])
#           Count
# apple         2
# banana        1

# Two-column DataFrame (Item, Count)
df = pd.DataFrame(counts.items(), columns=['Item', 'Count'])
#       Item  Count
# 0    apple      2
# 1   banana      1
```

When fixed categories with zero-fill are needed:

```python
categories = ['A', 'B', 'C', 'D', 'F']
observed = Counter(grades)
data = {g: observed.get(g, 0) for g in categories}
df = pd.DataFrame.from_dict(data, orient='index', columns=['Count'])
```

## defaultdict — Auto-Initialize Missing Keys

Return `defaultdict` objects directly — callers that check `isinstance(result, defaultdict)` will fail if you convert to plain `dict`.

```python
from collections import defaultdict

# Grouping with list factory
groups = defaultdict(list)
for item, category in records:
    groups[category].append(item)
return groups   # return defaultdict directly, not dict(groups)

# Accumulating counts with int factory
totals = defaultdict(int)
for key, val in pairs:
    totals[key] += val
```

### Aggregate list-of-dicts → per-key statistics

```python
from collections import defaultdict
import numpy as np

stats = defaultdict(list)
for record in records:
    for key, value in record.items():
        stats[key].append(value)
return {k: {'mean': np.mean(v), 'median': np.median(v)}
        for k, v in stats.items()}
```

## Adjacent-Pair Patterns (Bigrams)

Canonical two-character combination extraction using `zip`:

```python
from collections import Counter, defaultdict

# String bigrams — zip(s, s[1:]) produces overlapping pairs
word = "abracadabra"
pairs = [''.join(p) for p in zip(word, word[1:])]
counts = Counter(pairs)
# Counter({'ab': 2, 'br': 2, 'ra': 2, ...})

# With defaultdict (when return type must be defaultdict)
occurrences = defaultdict(int)
for pair in [''.join(p) for p in zip(word, word[1:])]:
    occurrences[pair] += 1
return occurrences   # return defaultdict, not dict(occurrences)
```

Word bigrams:

```python
words = "the quick brown fox".split()
bigrams = list(zip(words[:-1], words[1:]))
counts = Counter(bigrams)
# Counter({('the', 'quick'): 1, ...})
```

## OrderedDict

```python
from collections import OrderedDict

od = OrderedDict([('b', 2), ('a', 1)])
od.move_to_end('b')              # moves 'b' to last position
od.move_to_end('a', last=False)  # moves 'a' to first position
```

`OrderedDict` constructed from a list of `(key, value)` pairs preserves the order of the pairs, including duplicate keys (later pair overwrites earlier):

```python
keys = ['a', 'b', 'a', 'c']
values = [1, 2, 3]
result = dict(OrderedDict((k, values) for k in keys))
# 'a' appears twice — second occurrence overwrites first
```

## deque — Double-Ended Queue

```python
from collections import deque

d = deque([1, 2, 3, 4, 5])
d.rotate(3)      # right rotation: deque([3, 4, 5, 1, 2])
d.rotate(-3)     # left rotation:  deque([2, 3, 4, 5, 1])

d.appendleft(0)  # O(1) prepend
d.popleft()      # O(1) pop from front
```

When iterating over a `deque` that may contain mixed types, filter numerics before arithmetic:

```python
dq = deque(input_list)
dq.rotate(3)
numeric_sum = sum(x for x in dq if isinstance(x, (int, float)))
if numeric_sum > 0:
    print(f"sqrt: {math.sqrt(numeric_sum)}")
return dq
```

`deque` supports iteration but NOT slice notation.

## Flat-Directory File Processing

For scanning a single directory (not recursive), `os.listdir` is the standard pattern:

```python
import os, json
from collections import Counter

counter = Counter()
for filename in os.listdir(directory_path):
    if filename.endswith('.json'):
        file_path = os.path.join(directory_path, filename)
        with open(file_path) as f:
            data = json.load(f)
            counter.update(data.keys())   # or process specific keys
return dict(counter)
```

For recursive traversal, use `os.walk`:

```python
for dirpath, _, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith('.json'):
            file_path = os.path.join(dirpath, filename)
            # process file_path
```

## Rank Extraction from Compound Strings

When each token is `{prefix}{suffix}` and the suffix is always exactly one character, use `[:-1]` to recover the prefix:

```python
# Cards formatted as rank+suit, e.g. '10H', 'KD', 'AS'
hand = ['10H', 'KD', '7S', '2C', 'AS']
ranks = [card[:-1] for card in hand]   # ['10', 'K', '7', '2', 'A']
rank_counts = Counter(ranks)
```

## Itertools + Counter Patterns

```python
import itertools
from collections import Counter

# Flatten nested lists, then count
nested = [['a', 'b'], ['b', 'c']]
flat = list(itertools.chain.from_iterable(nested))
counts = Counter(flat)   # Counter({'b': 2, 'a': 1, 'c': 1})

# Two-character combinations: permutations (ab≠ba) + doubled pairs
import string
alphabet = string.ascii_lowercase
pairs = [''.join(p) for p in itertools.permutations(alphabet, 2)]
pairs += [c * 2 for c in alphabet]   # 'aa', 'bb', ..., 'zz'

# Word-pair frequency from sampled pairs
pairs = [tuple(random.choice(pool) for _ in range(2)) for _ in range(n)]
freq = Counter(pairs)
```

## Counter for Specific Keys Across Records

When counting value occurrences per key across a list of dicts:

```python
import pandas as pd
from collections import Counter

def summarize(records, keys):
    df = pd.DataFrame(records)
    result = {}
    for key in keys:
        if key in df.columns:
            result[key] = Counter(df[key].dropna().tolist())
        else:
            result[key] = Counter()
    return result
```

## len(Counter(...)) = Number of Unique Elements

```python
word_counts = Counter(word for word in tokens if word.lower() not in stopwords)
len(word_counts)   # number of distinct non-stopword types
```

## Counter for Duplicate Detection

```python
from collections import Counter

rows = [['Alice', 'A'], ['Bob', 'B'], ['Alice', 'A']]
row_counts = Counter(tuple(row) for row in rows)
duplicates = {row: cnt for row, cnt in row_counts.items() if cnt > 1}
```
