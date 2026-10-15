---
name: bisect-binary-search-and-sorted-insertio
description: 'Guide for correct bisect usage: threshold counting with bisect_right/left, insort on sorted copies, and integration with statistics.mean.'
---

# bisect — Binary Search for Sorted Sequences

The `bisect` module provides binary search on sorted lists. The list must already be sorted before calling these functions.

## Core Functions

```
bisect.bisect_right(a, x)  → int: rightmost insertion point for x (after existing x's)
bisect.bisect_left(a, x)   → int: leftmost insertion point for x (before existing x's)
bisect.bisect(a, x)        → alias for bisect_right
bisect.insort(a, x)        → None: insert x in place, maintaining sort order
bisect.insort_right(a, x)  → same as insort
bisect.insort_left(a, x)   → insert at leftmost position
```

Return types: `bisect_left`/`bisect_right` return a Python `int`. When a test expects `int`, wrap with `int()` if the input is a numpy array.

## Counting Elements by Threshold

```python
import bisect

data = [1, 2, 3, 5, 7, 9]   # must be sorted

# Strictly GREATER THAN x:
count_gt  = len(data) - bisect.bisect_right(data, 5)   # 2  (7 and 9)

# GREATER THAN OR EQUAL TO x:
count_ge  = len(data) - bisect.bisect_left(data, 5)    # 3  (5, 7, 9)

# Strictly LESS THAN x:
count_lt  = bisect.bisect_left(data, 5)                # 3  (1, 2, 3)

# LESS THAN OR EQUAL TO x:
count_le  = bisect.bisect_right(data, 5)               # 4  (1, 2, 3, 5)
```

The idiomatic pairing: use `bisect_right` to count elements **> x** (strictly), use `bisect_left` for **>= x**.

## insort — Preserve the Original List

`bisect.insort` modifies the list **in place**. When the task asks to return the original (unsorted) list along with a new sorted-with-insertion list:

```python
import random, bisect

def insert_into_sorted(num, length=5, lo=0, hi=100):
    numbers = [random.randint(lo, hi) for _ in range(length)]
    sorted_copy = sorted(numbers)       # copy and sort before inserting
    bisect.insort(sorted_copy, num)     # insort requires the list to already be sorted
    return numbers, sorted_copy
```

Since `insort` requires a **sorted** list, always `sorted_copy = sorted(numbers)` or `numbers[:]` followed by `.sort()` before calling `insort`.

## Practical Pattern — Values Above Average

The typical workflow with `bisect` and `statistics.mean`:
1. Compute statistics on the raw list
2. Sort a copy for the binary search
3. Use `bisect_right` to count elements above a threshold

```python
import bisect, statistics

def analyze(data, threshold):
    if not data:
        return [], 0
    avg = statistics.mean(data)
    above_avg = [x for x in data if x > avg]
    data_sorted = sorted(data)
    count_above_threshold = len(data_sorted) - bisect.bisect_right(data_sorted, threshold)
    return above_avg, count_above_threshold
```

## array Module Integration

When a task uses `array.array` for the sorted sequence, `bisect` works directly on it:

```python
from array import array
import bisect, random

def get_position(n, total):
    nums = []
    while sum(nums) != total:
        nums = [random.randint(0, total) for _ in range(n)]
    nums.sort()
    arr = array('i', nums)
    pos = bisect.bisect(arr, random.randint(0, total))
    return arr, pos
```

`array.array` supports `bisect` operations just like a plain list.

## Sorting with bisect for O(n log n) Builds

Use `insort` to build a sorted list incrementally:

```python
import bisect

sorted_data = []
for val in stream_of_values:
    bisect.insort(sorted_data, val)
# sorted_data is now fully sorted
```

This is equivalent to appending all values and sorting once, but useful when you need sorted order at each step.
