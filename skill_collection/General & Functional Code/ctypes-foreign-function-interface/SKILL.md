---
name: ctypes-foreign-function-interface
description: Guide for loading shared libraries with ctypes.CDLL, using lib._name, validation patterns, file metadata return types, and common pitfalls.
---

# ctypes — Foreign Function Interface

## Loading a Shared Library

`ctypes.CDLL(filepath)` loads a shared library and returns a handle. It raises `OSError` naturally if the path is invalid or the file cannot be opened:

```python
import ctypes

lib = ctypes.CDLL('/path/to/library.so')    # Linux
lib = ctypes.CDLL('/path/to/library.dll')   # Windows
lib = ctypes.CDLL('/path/to/library.dylib') # macOS
```

## Retrieving the Library Name: lib._name

`lib._name` holds the exact path string that was passed to `CDLL`. When the task says "return the name of the loaded library", use `lib._name` directly:

```python
lib = ctypes.CDLL('/tmp/mymodule.dll')
lib._name   # '/tmp/mymodule.dll'
```

Do not call `ctypes.util.find_library(lib._name)` — that searches system paths and may return `None` or a completely different string.

## Validation vs. Direct Loading

Some specifications require explicit validation (checking filepath type and existence) before loading. Others simply say "load and use the library". The two patterns are distinct:

**When the spec requires explicit validation:**

```python
import ctypes, os

def load_and_inspect(filepath):
    if not isinstance(filepath, str):
        raise TypeError("filepath must be a string")
    if not filepath or not os.path.exists(filepath):
        raise OSError("Invalid filepath")
    lib = ctypes.CDLL(filepath)
    return lib._name
```

**When the spec does not require validation:**

```python
import ctypes

def load_and_use(filepath):
    lib = ctypes.CDLL(filepath)   # raises OSError naturally if path invalid
    # ... do work with lib ...
    return lib._name
```

Adding `os.path.exists()` or `os.path.isfile()` checks when the spec does not require them can break behavior — if `ctypes.CDLL` is intercepted by a calling context, the pre-check may run against the real filesystem and raise before the load ever happens.

## Full Workflow: Load, Then Do Work

The typical pattern: load the DLL first, then perform the associated file or system operations:

```python
import ctypes, os, glob, shutil

def archive_shared_libs(filepath, dest_dir):
    lib = ctypes.CDLL(filepath)           # load first

    src_dir = os.path.dirname(filepath)
    for dll_file in glob.glob(os.path.join(src_dir, '*.dll')):
        shutil.move(dll_file, dest_dir)   # move after loading

    return lib._name
```

## File Metadata: Return Types

When a task says "return creation time, modification time, and file size", use `os.stat()` and `datetime.fromtimestamp()`:

```python
import ctypes, os
from datetime import datetime
import pytz

def get_lib_metadata(filepath):
    lib = ctypes.CDLL(filepath)
    stat = os.stat(filepath)

    metadata = {
        'Creation Time':      datetime.fromtimestamp(stat.st_ctime, pytz.UTC),
        'Modification Time':  datetime.fromtimestamp(stat.st_mtime, pytz.UTC),
        'Size':               stat.st_size,      # int, bytes — NOT a formatted string
    }
    return lib._name, metadata
```

Return `datetime` objects (with timezone) and a plain `int` for size — not formatted strings like `"2021-01-01 00:00:00 UTC"` or `"123456 bytes"`. The caller is responsible for formatting.

## ctypes Has No Path Utilities

`ctypes` has no `ctypes.path` or filesystem helpers. For path operations, use `os.path`:

```python
# Wrong: ctypes.path does not exist
if ctypes.path.exists(filepath): ...

# Correct
import os
if os.path.exists(filepath): ...
```
