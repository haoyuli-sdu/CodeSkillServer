---
name: math-scalar-math-functions-and-numerical
description: 'Guide for correct math module usage: trigonometry, factorial, mixed-container filtering, plotting patterns, and multiprocessing integration.'
---

# Python `math` Module — Practical Reference

## Core API

```
math.sqrt(x)        → float; ValueError for x < 0
math.sin(x)         → float (x in radians)
math.cos(x)         → float (x in radians)
math.exp(x)         → float (e^x)
math.log(x)         → natural log; math.log(x, base) for other bases
math.ceil(x)        → int (smallest integer >= x)
math.floor(x)       → int (largest integer <= x)
math.factorial(n)   → int; ValueError for negative or non-integer n
math.degrees(x)     → float (radians → degrees)
math.radians(x)     → float (degrees → radians)
math.hypot(x, y)    → float (sqrt(x²+y²))
math.prod(iter)     → product of all elements (Python 3.8+)
math.pi, math.e, math.tau, math.inf  — constants
```

`math` functions accept **scalars only**. For arrays, use `numpy` equivalents (`np.sin`, `np.sqrt`, etc.).

## Angle Sorting

`math.degrees(x)` converts radians to degrees. When tasks say "sort by degree value," they mean `math.degrees(x)`, not log magnitude:

```python
import math

values = [0.5, 1.2, 0.1, 2.3, 0.8]
sorted_vals = sorted(values, key=lambda x: (math.degrees(x), x))
```

## Generator Pattern with Random Seeds

When building a generator that must be reproducible, materialize random values into a list **before** wrapping in a generator expression:

```python
import random, math

def make_pairs(a, b, n, seed):
    random.seed(seed)
    pairs = [(random.randint(a, b), random.randint(a, b)) for _ in range(n)]
    return ((x, y, math.sqrt(abs(x - y))) for x, y in pairs)
```

Using a generator function (`def gen(): yield ...`) that calls `random` inside each `yield` is not equivalent — the seed does not produce the same sequence when the caller advances the generator step by step under different conditions.

## Plotting and Return Types

When the task says "return the figure" vs "return (fig, ax)" — match what the docstring specifies:

```python
import numpy as np, math, matplotlib.pyplot as plt

def plot_waves(frequency, sample_size=1000):
    x = np.linspace(0, 2 * math.pi, sample_size)
    fig, ax = plt.subplots()
    ax.plot(x, np.sin(frequency * x), label='sin')
    ax.plot(x, np.cos(frequency * x), label='cos')
    ax.legend()
    return fig, ax
```

For exponential generator plots where the generator is consumed during plotting, recreate it for the return value:

```python
import numpy as np, math, matplotlib.pyplot as plt

def exp_generator_plot(start, end, step):
    x_vals = np.arange(start, end, step)
    _, ax = plt.subplots()
    for x in x_vals:
        ax.scatter(x, math.exp(x), color='b')
    ax.set_title("Exponential Function Plot")
    ax.set_xlabel("x")
    ax.set_ylabel("e^x")
    generator = ((x, math.exp(x)) for x in x_vals)   # fresh generator for return
    return generator, ax
```

## Polar / Spiral Plots

```python
import numpy as np, math, matplotlib.pyplot as plt

def draw_spiral(ax, num_turns):
    r = np.linspace(0, num_turns * 2 * math.pi, 1000)
    theta = r    # r = theta for Archimedean spiral
    ax.plot(theta, r)
    ax.set_rlabel_position(num_turns * 45)   # degrees, not radians
    return ax
```

## Haversine / Geographic Distance

```python
import math

RADIUS_EARTH_KM = 6371.0

def haversine(coord1, coord2):
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return RADIUS_EARTH_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
```

## Multiprocessing + factorial

Helper functions used with `Pool.starmap` must be defined at **module level** (not inside the task function) so they are picklable:

```python
import math
from multiprocessing import Pool

def _calc_factorial(n):
    return (n, math.factorial(n))

def compute_factorials(numbers):
    if not all(isinstance(n, int) and n >= 0 for n in numbers):
        raise ValueError("All elements must be non-negative integers")
    with Pool() as pool:
        return dict(pool.starmap(_calc_factorial, [(n,) for n in numbers]))
```

## JSON Encoding of math results

When the task says "encode the result as a JSON string," the canonical pattern is:

```python
import math, json

def sqrt_to_json(value, precision=2):
    result = round(math.sqrt(value), precision)
    return json.dumps(str(result))    # json.dumps of the string representation
```

Note: `json.dumps(str(x))` produces `'"2.0"'` (a JSON string), while `json.dumps({"key": x})` produces `'{"key": 2.0}'` (a JSON object). Match the return type the task specifies.

## inspect + types Integration

```python
import inspect, types, math

def analyze_function(f):
    spec = inspect.getfullargspec(f)
    info = {
        'function_name': f.__name__,
        'sqrt_args': math.sqrt(len(spec.args)),
        'lambda_in_defaults': 0,
    }
    if spec.defaults:
        info['lambda_in_defaults'] = sum(
            1 for d in spec.defaults if isinstance(d, types.LambdaType)
        )
    return info
```

Always include `'lambda_in_defaults'` in the dict even when there are no defaults (set to 0).

## Filtering Numeric Elements from Mixed Containers

When aggregating only numeric values from a sequence that may contain strings, booleans, or `None`, use an `isinstance` guard:

```python
import math
from collections import deque

def sqrt_of_numeric_sum(items):
    dq = deque(items)
    numeric_sum = sum(x for x in dq if isinstance(x, (int, float)) and not isinstance(x, bool))
    if numeric_sum > 0:
        print(f"Square root of numeric sum: {math.sqrt(numeric_sum)}")
    return dq
```

Do not use `float(x)` on every element — this raises `ValueError` for strings and `TypeError` for `None`. The `isinstance(x, (int, float))` guard is the safe idiom.

## math.prod and Empty / Single-Element Iterables

`math.prod([])` returns 1 (multiplicative identity). For factorials combined with `functools.reduce`, always guard against empty permutations:

```python
import math
from itertools import permutations
from functools import reduce

def factorial_sums(numbers):
    if not numbers:
        return [], []
    all_perms = list(permutations(numbers))
    sums = [sum(math.factorial(n) for n in perm) for perm in all_perms]
    return sums, all_perms
```

Using `sum(...)` avoids the `reduce() of empty iterable` error that occurs when a permutation has zero or one element and no initial value is passed.
