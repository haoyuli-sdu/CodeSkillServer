---
name: mimetypes-file-type-detection
description: 'Guide for mimetypes.guess_type(): MIME type lookup, os.chdir+glob+re pattern for directory scanning.'
---

# mimetypes — File Type Detection

## Core API

`mimetypes.guess_type(filename)` returns a tuple `(type, encoding)` — the MIME type string is the **first element**:

```python
import mimetypes

mime_type, encoding = mimetypes.guess_type("report.pdf")
# mime_type = "application/pdf", encoding = None

mime_type = mimetypes.guess_type("data.txt")[0]
# mime_type = "text/plain"
```

Returns `(None, None)` if the type cannot be determined.

## Scanning a Directory with glob and re

The canonical approach: `os.chdir()` into the target directory, then call `glob.glob(file_pattern)` with a bare pattern (not a path-joined one). This yields relative filenames as dict keys, and `re.search(suffix, filename)` filters them:

```python
import re, os, glob, mimetypes

def scan_files(directory, file_pattern, suffix):
    os.chdir(directory)
    files = glob.glob(file_pattern)
    result = {}
    for f in files:
        if re.search(suffix, f):
            result[f] = mimetypes.guess_type(f)[0]
    return result
```

**Why `os.chdir()` then bare `glob.glob(file_pattern)`**: after `os.chdir(directory)`, `glob.glob(file_pattern)` returns short relative names like `"report.txt"` — those become the dict keys, matching what tests expect. Using `glob.glob(os.path.join(directory, file_pattern))` yields full absolute paths instead, giving wrong dict keys.

**`re.search(suffix, filename)`**: `suffix` is used as a regex pattern matched against the filename. Do not treat `suffix` as a literal file extension or add a leading dot — pass it directly to `re.search()`.

## MIME Types Quick Reference

| Extension | MIME type |
|---|---|
| `.txt` | `text/plain` |
| `.html` | `text/html` |
| `.json` | `application/json` |
| `.pdf` | `application/pdf` |
| `.png` | `image/png` |
| `.jpg` | `image/jpeg` |
| `.csv` | `text/csv` |
