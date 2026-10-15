---
name: errno-system-error-codes
description: 'Practical guide for errno constants in OS error handling: EEXIST, ENOENT, EACCES patterns, and correct shutil integration.'
---

# errno — System Error Codes

## Core Use: Interpreting OSError Codes

`errno` provides symbolic names for OS error codes. The typical pattern is to catch `OSError` and inspect `e.errno`:

```python
import errno, os

try:
    os.makedirs(directory)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise    # unexpected error — re-raise
    # errno.EEXIST means directory already exists — that's fine
```

Modern code uses `os.makedirs(path, exist_ok=True)` which handles `EEXIST` internally.

## Common errno Constants

| Constant | Value | Meaning |
|---|---|---|
| `errno.EEXIST` | 17 | File or directory already exists |
| `errno.ENOENT` | 2 | No such file or directory |
| `errno.EACCES` | 13 | Permission denied |
| `errno.ENOTDIR` | 20 | Not a directory |
| `errno.EINVAL` | 22 | Invalid argument |

## File Copy + Content Clear Pattern

Copy a file to a destination directory and truncate the original's contents. Call `shutil.copy()` directly without a try/except wrapper — let its exceptions propagate unchanged:

```python
import os, errno, shutil

def copy_and_clear(filename, dest_dir):
    try:
        os.makedirs(dest_dir, exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    dest = shutil.copy(filename, dest_dir)   # raises OSError naturally if src missing

    with open(filename, "w") as f:
        f.truncate(0)                         # clear original file contents

    return os.path.abspath(dest)
```

`shutil.copy(src, dst_dir)` returns the destination file path. When `dst_dir` is a directory, the file is placed inside it with the same basename. Wrapping `shutil.copy` in its own try/except that re-raises as a new `OSError` with a different message changes the exception identity — callers that rely on the original exception type or message will see the wrong error. Call `shutil.copy` bare and let errors propagate directly.

## shutil.copy vs shutil.copy2

- `shutil.copy(src, dst)` — copies file content and permissions; does not preserve metadata timestamps
- `shutil.copy2(src, dst)` — also preserves access/modification timestamps

Use `shutil.copy` when timestamp preservation is not needed.
