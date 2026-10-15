---
name: multiprocessing-pool-map-pool-starmap-an
description: 'Guide for multiprocessing Pool: pool.map vs starmap, collecting dict results, module-level worker functions, input validation, and subprocess output collection.'
---

# Python multiprocessing — Practical Reference

## Pool.map and Pool.starmap

`Pool.map(fn, iterable)` applies `fn` to each element and returns results in order.
`Pool.starmap(fn, iterable_of_tuples)` unpacks each tuple as positional arguments — useful when the worker takes multiple parameters.

```python
from multiprocessing import Pool

def square(x):
    return x * x

with Pool() as pool:
    results = pool.map(square, [1, 2, 3, 4])
# [1, 4, 9, 16]

def power(base, exp):
    return base ** exp

with Pool() as pool:
    results = pool.starmap(power, [(2, 3), (3, 2), (4, 1)])
# [8, 9, 4]
```

## Collecting Results as a Dict

When the worker returns `(key, value)` tuples, wrap `pool.starmap` in `dict()`:

```python
from multiprocessing import Pool
import math

def compute_factorial(n):
    return n, math.factorial(n)

def calculate_factorials(numbers):
    if not all(isinstance(n, int) and n >= 0 for n in numbers):
        raise ValueError("All elements must be non-negative integers")
    with Pool() as pool:
        return dict(pool.starmap(compute_factorial, [(n,) for n in numbers]))
```

Note: `pool.starmap(fn, [(n,) for n in numbers])` calls `fn(n)` for each element. The one-element tuple `(n,)` is required by `starmap`.

## Pool(processes=N) vs Pool()

`Pool()` defaults to `os.cpu_count()` workers. Pass `processes=len(tasks)` to allocate exactly one worker per task:

```python
commands = ["ls", "pwd", "echo hi"]
with Pool(processes=len(commands)) as pool:
    outputs = pool.map(run_cmd, commands)
```

## Worker Functions Must Be Defined at Module Top-Level

`Pool.map` pickles the worker function and sends it to child processes. Functions defined inside another function cannot be pickled — define worker functions at module level:

```python
# At module level — picklable:
def execute_command(command):
    import subprocess
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, _ = process.communicate()
    return output

def task_func(commands):
    if not commands:
        return []
    with Pool(processes=len(commands)) as pool:
        return pool.map(execute_command, commands)
```

## Input Validation Before Opening a Pool

Validate inputs before creating the pool — this avoids spawning workers for bad data and lets exceptions propagate cleanly:

```python
def process_numbers(numbers):
    if not all(isinstance(n, int) and n >= 0 for n in numbers):
        raise ValueError("All elements must be non-negative integers")
    if not numbers:
        return {}
    with Pool() as pool:
        pairs = pool.starmap(worker, [(n,) for n in numbers])
    return dict(pairs)
```

## Subprocess Output Collection with multiprocessing

The typical pattern for running shell commands in parallel and collecting their byte-string output:

```python
from multiprocessing import Pool
import subprocess

def execute_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, _ = process.communicate()
    return output   # bytes

def run_commands_parallel(commands):
    if not commands:
        return []
    with Pool(processes=len(commands)) as pool:
        return pool.map(execute_command, commands)
```

`process.communicate()` waits for the subprocess to finish and returns `(stdout_bytes, stderr_bytes)`.
