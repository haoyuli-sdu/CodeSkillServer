---
name: statistics-descriptive-statistics-and-da
description: 'Guide for correct statistics module usage: mean/mode/median, row-by-row DataFrame construction, numpy integration, and generator patterns.'
---

# Python `statistics` Module — Practical Reference

## Core API

```
statistics.mean(data)       → float or Fraction — arithmetic mean
statistics.median(data)     → middle value (sorts internally)
statistics.mode(data)       → single most-common value (first if tied, Python 3.8+)
statistics.multimode(data)  → list of ALL modes (possibly one element)
statistics.stdev(data)      → sample std dev (n-1 denominator)
statistics.pstdev(data)     → population std dev (n denominator)
statistics.StatisticsError  — raised for empty input or other invalid conditions
```

`data` must be a **list or sequence** — not a generator. `statistics.mean(x for x in items)` raises `TypeError: can't convert type 'generator' to numerator/denominator`. Convert to list first.

## `mode` vs `multimode`

```python
import statistics

scores = [3, 3, 5, 5, 7]
statistics.mode(scores)       # → 3  (single value, first-encountered if tied)
statistics.multimode(scores)  # → [3, 5]  (list, all modes)
```

Return type matters: if the task asks for a single mode value (`int` or `float`), use `mode`. If it asks for a list of modes, use `multimode`. Tests that assert `result == 3` will fail if you return `[3]`.

## Iterating Over All Provided Keys

When a function receives a parameter like `LETTERS` (a list or string of keys), generate entries for **every** key — do not call `random.sample(LETTERS, k)` to pick a subset:

```python
import random, statistics

def build_dict(keys, seed=None):
    if seed is not None:
        random.seed(seed)
    result = {k: [random.randint(0, 100) for _ in range(5)] for k in keys}
    sorted_result = dict(sorted(
        result.items(),
        key=lambda item: statistics.mean(item[1]),
        reverse=True
    ))
    return sorted_result
```

## Computing Mean Per Row vs Per Column

`statistics.mean` operates on a flat list. To apply it row-wise in a DataFrame, use `df.apply(statistics.mean, axis=1)` or pass each row as a list:

```python
import pandas as pd
from statistics import mean

df['Average'] = df[subject_cols].apply(lambda row: mean(row.tolist()), axis=1)
```

For a simpler row average, `df[cols].mean(axis=1)` (pandas) is equivalent.

## Row-by-Row Data Building

When computing per-item statistics and building a DataFrame, build data row by row. Use the provided parameter as column names directly — do not invent synthetic names:

```python
from random import randint, seed
from statistics import mean
import pandas as pd

def generate_report(items, categories, rng_seed=None):
    if rng_seed is not None:
        seed(rng_seed)
    rows = []
    for item in items:
        values = [randint(0, 100) for _ in categories]
        avg = mean(values)
        rows.append([item] + values + [avg])
    cols = ['Item'] + list(categories) + ['Average']
    return pd.DataFrame(rows, columns=cols)
```

The column list comes from the `categories` parameter itself — not from `[f'Category {i+1}' for i in range(n)]`. Using a format string instead of the parameter will produce wrong column names when categories have real names like `['Math', 'Physics']`.

## Mixed-Type Sequences and numpy Integration

When the input arrives as a Python list but subsequent operations require numpy indexing (e.g., boolean array selection), convert explicitly:

```python
import numpy as np, statistics

def filter_above_mean(data):
    if not data:
        return np.array([]), 0
    arr = np.array(data)           # convert once, use numpy operations throughout
    avg = statistics.mean(arr)     # statistics.mean accepts numpy arrays
    above_avg = arr[arr > avg]     # numpy boolean indexing on arr, not on original list
    return above_avg
```

`statistics.mean` accepts numpy arrays as input (they are sequences). The return type is always a Python `float` (or `Fraction`), not a numpy scalar.

## Moving Average

```python
import statistics, random

data = [random.randint(0, 1000) for _ in range(100)]
window = 5   # "current + previous 5" means window size = 6

moving_avg = [statistics.mean(data[max(0, i - window):i + 1]) for i in range(len(data))]
```

The window shrinks naturally at the start. Do not insert `NaN` for early indices unless explicitly required.

## Sorting by Computed Statistic

```python
import statistics

letter_data = {'a': [5, 3, 8], 'b': [1, 2, 3], 'c': [9, 7, 6]}
sorted_data = dict(sorted(
    letter_data.items(),
    key=lambda item: statistics.mean(item[1]),
    reverse=True
))
# → {'c': [9,7,6], 'a': [5,3,8], 'b': [1,2,3]}
```

## Generator Objects — Yield (name, avg) Pairs

When creating a dict of generators where each generates `(name, avg)` tuples:

```python
import pandas as pd
from statistics import mean

def df_to_generators(df):
    grouped = df.groupby('Name')
    result = {}
    for name, group in grouped:
        avg = mean(group['Score'].tolist())
        result[name] = iter([(name, avg)])
    return result
```

Do not define a nested `gen(values)` that references `name` from the outer scope — `name` will be the last loop value by the time the generator is consumed. Use `iter([(name, avg)])` or a closure that captures the value.

## `statistics.StatisticsError` for Empty Input

```python
import statistics

if not data:
    raise statistics.StatisticsError("data is empty")
```

Raise the exception directly (not via `statistics.mean([])`), since some tasks check the exception type exactly.

## Counter + mode vs statistics.mode

When tracking frequency and reporting a generator of `(value, frequency)` tuples:

```python
from collections import Counter
import statistics

numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5, 5]
freq = Counter(numbers)
gen = ((num, cnt) for num, cnt in freq.items())   # generator of (value, count)
mode_val = statistics.mode(numbers)                # use statistics.mode, not Counter
```

Do not mix `Counter.most_common()[0][0]` as a substitute for `statistics.mode` when the task imports `statistics` — they may differ if the Counter is built from a different sequence.
