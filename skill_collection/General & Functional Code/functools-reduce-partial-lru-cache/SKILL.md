---
name: functools-reduce-partial-lru-cache
description: Guide for functools.reduce with empty-sequence safety, permutation+aggregation patterns, partial and lru_cache.
---

# functools — reduce, partial, lru_cache

## reduce — cumulative binary operation

`reduce(func, iterable[, initializer])` applies `func` cumulatively left to right. With no initializer, an empty iterable raises `TypeError`. Provide an initializer when the input might be empty, or use `sum()` / `math.prod()` which handle empty sequences naturally.

```python
from functools import reduce
import operator, math

# Product with explicit initializer — safe when nums might be []
reduce(operator.mul, nums, 1)    # → 1 if nums is empty

# Sum of factorials — sum() handles empty naturally
total = sum(math.factorial(n) for n in values)   # → 0 if values is []
```

---

## Permutations + aggregation pattern

`itertools.permutations(seq)` on an empty sequence returns `[()]` (a single empty tuple), not `[]`. Any aggregation over the elements of that empty tuple will encounter an empty iterable:

```python
from functools import reduce
from itertools import permutations
import math

def perm_factorial_sums(numbers):
    # Early return — permutations([]) = [()], not []
    if not numbers:
        return [], []

    all_perms = list(permutations(numbers))   # store first; iterator exhausts
    sums = [
        sum(math.factorial(n) for n in perm)  # sum([]) = 0, never raises
        for perm in all_perms
    ]
    return sums, all_perms     # all_perms is list of tuples, not lists
```

`permutations()` returns tuples. Return them as-is when callers compare against tuple elements.

---

## Combinations + numeric aggregation

Iterating over all combination lengths:

```python
from functools import reduce
from itertools import combinations
import math

def sum_log_products(numbers):
    total = 0.0
    for r in range(1, len(numbers) + 1):
        for combo in combinations(numbers, r):
            product = reduce(lambda x, y: x * y, combo)
            total += math.log(product)   # let ValueError propagate for <= 0 inputs
    return total
```

`combinations` always returns non-empty tuples (length r ≥ 1), so `reduce` without an initializer is safe here.

---

## reduce vs sum/math.prod — when to use each

| Situation | Preferred |
|---|---|
| Sum of a computed sequence | `sum(f(x) for x in items)` |
| Product, Python 3.8+ | `math.prod(items)` |
| Custom binary accumulator | `reduce(func, items, initializer)` |
| Unknown/empty input | Always provide initializer or use sum/prod |

---

## partial — freeze arguments

```python
from functools import partial

def power(base, exp):
    return base ** exp

square = partial(power, exp=2)    # square(5) → 25
triple = partial(lambda x, y: x * y, 3)  # positional: triple(7) → 21
```

---

## lru_cache — memoization

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)
```

Arguments must be hashable. `@cache` (Python 3.9+) is equivalent to `@lru_cache(maxsize=None)`.

---

## cmp_to_key — legacy comparator adapter

```python
from functools import cmp_to_key

sorted(items, key=cmp_to_key(lambda a, b: (a > b) - (a < b)))
```
