---
name: typing-type-hints-and-common-integration
description: 'Guide for typing module: type hints don''t define column names, scipy.stats.mode needs numpy array input for array output, Path.walk Python 3.12+, type-aware mode with mixed types, FFT on original vs repeated data.'
---

# Python `typing` Module — Type Hints in Practice

## What `typing` Provides

The `typing` module provides type hint annotations used in function signatures. It does not
affect runtime behavior — annotations are documentation only.

```python
from typing import Any, Dict, List, Optional, Tuple, Union

def process(data: List[int], label: str = "") -> Tuple[List[float], str]: ...
def mixed(items: List[Union[int, str]]) -> Any: ...
def optional_arg(x: Optional[str] = None) -> Dict[str, int]: ...
```

## Type Hints Do Not Define Column Names

A common failure: models infer DataFrame column names from type annotations. Type hints
on parameter names say nothing about the actual data structure. Always read the task
description to find exact column names:

```python
# Wrong: guessing column name from the parameter type hint
model = ARIMA(df['Close'], order=(5, 1, 0))   # hallucinated 'Close'

# Right: use the column name stated in the task description
model = ARIMA(df['closing_price'], order=(5, 1, 0))
```

The same applies to date columns: `'date'`, `'Date'`, `'timestamp'`, `'ds'` — use what
the task specifies, not what seems conventional.

## `scipy.stats.mode` Return Type

`scipy.stats.mode(data)` returns a `ModeResult` namedtuple. The exact shape of `.mode`
depends on the input type:

- **numpy array input** → `.mode` is a numpy array (e.g., `array([1])`)
- **plain list input** → `.mode` may be a scalar in newer scipy versions

Tests typically check `result.mode` as an array. To ensure array output, convert to
numpy array before calling `stats.mode`:

```python
import numpy as np
from scipy import stats
import itertools

flattened = np.array(list(itertools.chain(*[input_list for _ in range(repetitions)])))
mode_result = stats.mode(flattened)
return mode_result   # ModeResult with .mode as array, .count as array
```

Do not extract `mode_result.mode[0]` (scalar) — return the full `ModeResult` object
when the task return type is `scipy.stats.ModeResult`.

## `Path.glob` for File Extension Filtering

When moving files by extension:

```python
from pathlib import Path
import shutil

for extension in extensions:
    for filepath in Path(source_dir).glob(f'*{extension}'):
        shutil.move(str(filepath), target_dir)
```

`Path.glob(pattern)` matches directly. `Path.iterdir()` yields all entries and requires
a manual `filepath.suffix in extensions` filter.

Note: `Path.walk()` requires Python 3.12+. For compatibility, use `os.walk()` or
`Path.glob('**/*')` for recursive traversal. For flat directory searches, use `.glob('*ext')`.

## Type-Aware Mode with Mixed Types

When data contains mixed types (`[1, '1', 2]`) and the task requires distinguishing
between `1` (int) and `'1'` (str) as different elements, use a dict keyed by `(value, type)`:

```python
def calculate_mode(data):
    counts = {}
    for item in data:
        key = (item, type(item))
        counts[key] = counts.get(key, 0) + 1
    max_count = max(counts.values())
    modes = [v for (v, t), c in counts.items() if c == max_count]
    return modes, [max_count] * len(modes)
```

When computing FFT alongside mode on repeated data, apply FFT to the **original** data
(before repetition), not the repeated version:

```python
repeated_data = data * repetitions
mode, count = calculate_mode(repeated_data)
return {
    'mode': np.sort(mode),
    'count': count,
    'fft': scipy.fft.fft(data)   # original data, not repeated_data
}
```
