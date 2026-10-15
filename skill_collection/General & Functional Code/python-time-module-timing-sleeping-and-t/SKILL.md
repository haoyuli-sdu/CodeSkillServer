---
name: python-time-module-timing-sleeping-and-t
description: Practical reference for time.time(), time.sleep(), time.strptime(), and sequential vs concurrent threading patterns with time delays.
---

# Python `time` Module — Practical Reference

The `time` module provides Unix timestamps, sleeping, and time-string parsing. It complements but is distinct from the `datetime` module.

## Core Functions

```python
import time

t = time.time()          # current Unix timestamp as float (seconds since epoch)
time.sleep(2.5)          # pause current thread for 2.5 seconds (float OK)
```

## Timestamp Recording Patterns

**Record a start time as a formatted string** — use `datetime.now().strftime(fmt)`, not `time.strptime`:

```python
from datetime import datetime
import time

start_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")   # str, ready to store
time.sleep(delay)
end_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

**Measure elapsed duration** — use `time.time()` directly:

```python
start = time.time()
# ... do work ...
elapsed = time.time() - start    # float, seconds
```

**`time.strptime` accepts only strings**, not `datetime` objects. Passing a `datetime` raises `TypeError: strptime() argument 1 must be str`. Use it to parse time-string lists:

```python
seconds = [time.strptime(ts, "%H:%M:%S").tm_sec for ts in raw_strings]
```

## Parsing and Plotting Seconds from Time Strings

```python
import time
import matplotlib.pyplot as plt

def plot_seconds(time_strings, time_format="%d/%m/%Y %H:%M:%S.%f"):
    try:
        seconds = [time.strptime(ts, time_format).tm_sec for ts in time_strings]
    except ValueError as e:
        print(e)
        return None
    _, ax = plt.subplots()
    ax.hist(seconds, bins=60, rwidth=0.8)
    return ax
```

The function catches `ValueError` from `strptime` and returns `None`. The Axes comes from `plt.subplots()`, not from `ax.hist()`.

## Threading Patterns: Sequential vs Concurrent

**Sequential threads** — start one thread at a time and join immediately. Total runtime ≈ N × sleep_time:

```python
import threading, time

results = []

def worker():
    time.sleep(delay_time)
    results.append(f'Delay in thread {threading.current_thread().name} completed')

for i in range(num_threads):
    t = threading.Thread(target=worker, name=str(i))
    t.start()
    t.join()    # blocks until this thread finishes before starting next
```

**Concurrent threads** — start all, then join all. Total runtime ≈ sleep_time:

```python
threads = [threading.Thread(target=fn) for _ in range(n)]
for t in threads: t.start()    # launch all first
for t in threads: t.join()     # then wait for all
```

The message format uses `threading.current_thread().name` — the `name=` string passed to `Thread()`, not the integer index `i`.

## `time.sleep` with Random Delays

```python
import time, random

def simulate_tasks(n, min_delay=0.5, max_delay=2.0):
    results = []
    for _ in range(n):
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        results.append(f"Task done after {delay:.2f}s")
    return results
```

## Return Type When Combining Timing with Axes

A common pattern returns a tuple `(elapsed, ax)` or `(result, ax)`:

```python
start = time.time()
_, ax = plt.subplots()
ax.hist(measurements, bins=20)
return time.time() - start, ax
```

## Process Timing with `Popen`

```python
import subprocess, time

def run_with_poll(cmd):
    proc = subprocess.Popen(cmd)
    time.sleep(1)           # let process start
    return proc.poll()      # None if still running, else return code
```
