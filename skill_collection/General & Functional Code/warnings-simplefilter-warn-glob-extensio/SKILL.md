---
name: warnings-simplefilter-warn-glob-extensio
description: 'Guide for Python warnings module: simplefilter placement, conditional flags, file transfer error patterns, and distinction from logging.warning.'
---

# Python warnings — Practical Reference

## Core Pattern: simplefilter Before warn

`warnings.warn(message)` issues a `UserWarning`. By default Python suppresses duplicate warnings from the same code location. Call `warnings.simplefilter('always')` at the start of the function to ensure every invocation fires the warning.

```python
import warnings

def check_data(records):
    warnings.simplefilter('always')
    if len(records) > 1000:
        warnings.warn('Dataset exceeds size threshold.')
    return records
```

## Conditional simplefilter via Flag Parameter

When the function accepts a boolean controlling whether warnings are active, apply `simplefilter` only when the flag is `True`:

```python
import warnings, sqlite3
import pandas as pd

def fetch_records(db_path, query, warn_large=True):
    if warn_large:
        warnings.simplefilter('always')

    with sqlite3.connect(db_path) as conn:
        data = pd.read_sql_query(query, conn)   # conn = __enter__() result

    if warn_large and data.shape[0] > 10000:
        warnings.warn('The data contains more than 10000 rows.')

    return data
```

`with sqlite3.connect(db_path) as conn:` — the `conn` binding inside the block is the connection's `__enter__` return value. This is the object passed to `pd.read_sql_query`, so use the `with` form when reading SQL data.

## File Transfer with Failure Warnings

When moving files and issuing warnings for transfer errors, use `shutil.move` inside a `try/except` block. When extension strings already include the dot (`.txt`, `.csv`), concatenate them directly with `'*'`:

```python
import warnings, glob, os, shutil, time

def transfer_by_extension(src_dir, dest_dir, extensions):
    warnings.simplefilter('always')
    moved = []
    for ext in extensions:
        # ext already has the dot: '.txt' → pattern '*.txt'
        # NOT f'*.{ext}' which gives '*..' + ext (double dot)
        for fpath in glob.glob(os.path.join(src_dir, '*' + ext)):
            try:
                shutil.move(fpath, dest_dir)
                moved.append(os.path.basename(fpath))
            except Exception as e:
                warnings.warn(f'Unable to move file {fpath}: {str(e)}')
    time.sleep(1)
    return moved
```

Key points:
- `'*' + ext` where `ext='.txt'` → `'*.txt'` (correct)
- `f'*.{ext}'` where `ext='.txt'` → `'*..txt'` (double dot, never matches)
- Don't create the destination directory — callers control the environment

## warnings.warn vs logging.warning

| | `warnings.warn` | `logging.warning` |
|---|---|---|
| Purpose | Signal unusual conditions to the caller | Persist events to a log handler |
| Captured by | `warnings.catch_warnings()`, `filterwarnings` | logging handlers / files |
| Filter control | `warnings.simplefilter` / `filterwarnings` | `logging.setLevel` |

Use `warnings.warn` when the specification says "issue a warning" or "warn if…". Use `logging.warning` when it says "log a warning message".

## Warning Category Classes

```python
warnings.warn('deprecated API', DeprecationWarning)
warnings.warn('unexpected value', RuntimeWarning)
warnings.warn('dataset is large', UserWarning)   # default if omitted
```

`simplefilter('always')` enables all categories each call. `simplefilter('ignore')` suppresses all.

## Exact Message String

Code that captures warnings with `catch_warnings()` or `pytest.warns()` often asserts on the exact message text. Write the string exactly as specified — no extra path or count appended.
