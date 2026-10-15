---
name: heapq-heap-queue-operations-and-index-se
description: 'Guide for correct heapq usage: nlargest/nsmallest with key, index-based selection, numpy pitfalls, and post-selection operations.'
---

# heapq — Heap Queue Algorithm

Python's `heapq` module implements a min-heap on a plain list. `heap[0]` is always the smallest element.

## Core API

```
heapq.nlargest(n, iterable, key=None)   → list of n largest, largest first
heapq.nsmallest(n, iterable, key=None)  → list of n smallest, smallest first
heapq.heapify(list)    — convert list to heap in-place, O(n)
heapq.heappush(heap, item)   — add item, O(log n)
heapq.heappop(heap)          — remove and return smallest, O(log n)
```

Return type: `nlargest` and `nsmallest` always return a **plain Python list**.

## nlargest / nsmallest with key

The `key` is used for comparison only — the original elements are returned:

```python
import heapq

word_counts = {'apple': 5, 'banana': 2, 'cherry': 8, 'date': 1}
heapq.nlargest(2, word_counts, key=word_counts.get)   # ['cherry', 'apple']
heapq.nsmallest(2, word_counts, key=word_counts.get)  # ['date', 'banana']
```

## Finding Indices of N Largest Differences

Use `range(len(seq))` as the iterable to get indices rather than values:

```python
import heapq

a = [10, 3, 8, 1, 7]
b = [2,  5, 8, 9, 4]

indices = heapq.nlargest(3, range(len(a)), key=lambda i: abs(a[i] - b[i]))
# → [3, 0, 4]  (indices where |a-b| is largest)
```

After getting indices, index back into the **original arrays** (not the difference array) when the subsequent operation (t-test, correlation, etc.) requires the original values:

```python
import heapq
from scipy import stats

col1 = df['col1'].values
col2 = df['col2'].values
indices = heapq.nlargest(N, range(len(col1)), key=lambda i: abs(col1[i] - col2[i]))

_, p_value = stats.ttest_ind(col1[indices], col2[indices])   # original values at those indices
```

## numpy Array Pitfall

When the key function accesses a row of a 2D array, heapq raises `ValueError: truth value of an array is ambiguous`. Always use 1D arrays (`.values` not `[['col']].values`):

```python
# Correct: 1D arrays
y = df['target'].values           # shape (n,)
X = df['feature'].values.reshape(-1, 1)
residuals = y - model.predict(X)  # 1D — safe for heapq key

indices = heapq.nlargest(n, range(len(residuals)), key=lambda i: abs(residuals[i]))
```

## StandardScaler + heapq Pattern

```python
import heapq
from sklearn.preprocessing import StandardScaler

def find_largest_diff_indices(df, col1, col2, N=10):
    if col1 not in df.columns or col2 not in df.columns:
        raise ValueError(f"Columns {col1} or {col2} not found in the DataFrame.")
    scaler = StandardScaler()
    df[[col1, col2]] = scaler.fit_transform(df[[col1, col2]])
    l1 = df[col1].values
    l2 = df[col2].values
    return heapq.nlargest(N, range(len(l1)), key=lambda i: abs(l1[i] - l2[i]))
```

## Plotting After Index Selection

When plotting the selected values, do not construct a manual x-axis from `range(N)`:

```python
import matplotlib.pyplot as plt

selected_values = [abs(a[i] - b[i]) for i in indices]
fig, ax = plt.subplots()
ax.plot(selected_values)   # let matplotlib assign x-axis automatically
return ax
```

## heapify + push/pop

```python
import heapq

nums = [5, 2, 8, 1, 9]
heapq.heapify(nums)        # [1, 2, 8, 5, 9] — min-heap in-place
heapq.heappush(nums, 3)    # adds 3 maintaining heap property
smallest = heapq.heappop(nums)   # removes and returns 1
```

## Object Attribute Pattern

```python
import heapq

class Item:
    def __init__(self, name, score):
        self.name = name
        self.score = score

items = [Item('a', 3), Item('b', 9), Item('c', 1)]
top2 = heapq.nlargest(2, items, key=lambda obj: obj.score)
# → [Item('b',...), Item('a',...)]
```

For lists of dicts: `key=lambda d: d['score']`. For object attributes that may not exist, use `getattr(obj, attr, default)`.
