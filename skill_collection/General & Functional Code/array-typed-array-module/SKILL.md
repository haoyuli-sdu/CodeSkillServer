---
name: array-typed-array-module
description: Creating typed arrays, return type requirements, bisect compatibility, and the generate-sort-convert pattern.
---

# Python `array` Module — Typed Arrays

## Creating Arrays

`array.array(typecode, initializer)` creates a typed, fixed-type sequence. Common typecodes:

| Code | C type | Python type | Size |
|------|--------|-------------|------|
| `'b'`/`'B'` | signed/unsigned char | int | 1 byte |
| `'i'`/`'I'` | signed/unsigned int | int | 4 bytes |
| `'l'`/`'L'` | signed/unsigned long | int | 4 bytes |
| `'f'` | float | float | 4 bytes |
| `'d'` | double | float | 8 bytes |

```python
from array import array

nums = [3, 1, 4, 1, 5]
a = array('i', nums)   # signed int array
a = array('d', nums)   # double array
```

## Return Type Matters

When the code prompt imports `from array import array`, the function result must be an `array` instance — returning a plain `list` fails `isinstance(result, array)` checks even if the values are correct.

## Common Pattern: Generate → Sort → Convert to array

```python
import random, bisect
from array import array

def generate_sorted_with_position(n, total):
    nums = []
    while sum(nums) != total:
        nums = [random.randint(0, total) for _ in range(n)]

    nums.sort()
    nums = array('i', nums)          # convert list → typed array

    new_num = random.randint(0, total)
    pos = bisect.bisect(nums, new_num)   # bisect works directly on array objects

    return (nums, pos)
```

`bisect` functions accept `array` objects directly since they implement the sequence protocol. No conversion to list is needed.

## Useful Operations

```python
from array import array

a = array('i', [1, 2, 3, 4])
a.append(5)          # add single element
a.extend([6, 7])     # add multiple elements
a.tolist()           # convert to plain list
len(a)               # standard len()
a[0]                 # indexing and slicing work normally
```

## array vs list vs numpy.ndarray

- `array.array` — typed, 1D, stdlib, lightweight; use when the return type is explicitly required
- `list` — untyped Python list; will fail isinstance checks against `array`
- `numpy.ndarray` — multi-dimensional numeric arrays; separate library
