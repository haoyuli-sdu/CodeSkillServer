---
name: fnmatch-unix-filename-pattern-matching
description: 'Guide for fnmatch: filter with os.listdir/os.walk, recursive walk pattern, fnmatch vs glob comparison.'
---

# fnmatch — Unix Filename Pattern Matching

## Core Functions

`fnmatch.fnmatch(name, pattern)` — True if `name` matches shell-style `pattern`.
`fnmatch.filter(names, pattern)` — subset of `names` matching `pattern`.
`fnmatch.fnmatchcase(name, pattern)` — always case-sensitive.
`fnmatch.translate(pattern)` — converts shell pattern to a regex string.

Pattern syntax: `*` (any chars except `/`), `?` (single char), `[abc]` (char class).

**Key limitation**: `fnmatch` compares bare filenames — `fnmatch.fnmatch("dir/file.txt", "*.txt")`
returns `False` because `*` does not match `/`. Always pass just the filename, not the full path.

## Flat Directory: Filter + Copy

`os.listdir()` returns bare filenames, which work directly with `fnmatch.filter`:

```python
import os, fnmatch, shutil, itertools

def copy_matching(src_dir, dst_dir, patterns):
    # Flatten results from multiple patterns with itertools.chain
    names = list(itertools.chain.from_iterable(
        fnmatch.filter(os.listdir(src_dir), pat) for pat in patterns))
    for fname in names:
        shutil.copy2(os.path.join(src_dir, fname), dst_dir)
    return dst_dir
```

## Recursive Walk: Filter Files Per Directory

`os.walk` yields `(dirpath, dirs, files)` — `files` contains bare filenames, ready for `fnmatch.filter`:

```python
import os, fnmatch, shutil

def move_matching(src_dir, dst_dir, pattern):
    moved = []
    for dirpath, dirs, files in os.walk(src_dir):
        for fname in fnmatch.filter(files, pattern):
            shutil.move(os.path.join(dirpath, fname),
                        os.path.join(dst_dir, fname))
            moved.append(fname)
    return moved
```

## fnmatch vs glob

| | fnmatch | glob |
|---|---|---|
| Input | list of names already in memory | filesystem path pattern |
| Requires actual files | No | Yes |
| Recursive `**` support | No | Yes (with `recursive=True`) |

Use `fnmatch` when you already have a list of names (from `os.listdir` or `os.walk`).
Use `glob.glob` when constructing path patterns to search the filesystem directly.
