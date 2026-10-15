---
name: shutil-high-level-file-and-directory-ope
description: 'Guide for correct shutil usage: move/copy/copytree/make_archive patterns, os.listdir vs os.walk for flat directories, extension extraction, and backup recipes.'
---

# shutil — High-Level File and Directory Operations

## Core API

`shutil.move(src, dst)` — moves a file or directory. If `dst` is an existing directory, the source is placed inside it; otherwise, the source is renamed to `dst`.

`shutil.copy(src, dst)` — copies file content + permissions. `dst` may be a file path or an existing directory.

`shutil.copy2(src, dst)` — like `copy` but also preserves metadata (timestamps).

`shutil.copyfile(src, dst)` — copies content only; `dst` must be a full file path, not a directory.

`shutil.copytree(src, dst)` — recursively copies an entire directory tree to `dst`.

`shutil.rmtree(path)` — removes an entire directory tree.

`shutil.disk_usage(path)` → named tuple `(total, used, free)` in bytes.

`shutil.make_archive(base_name, format, root_dir=None)` → str — creates an archive and returns the full path including extension. Pass the path **without** the extension as `base_name`.

## The Canonical Single-Level Scan Pattern

For flat directory tasks (moving, copying, or filtering files in one directory), `os.listdir` is the right tool. It naturally raises `FileNotFoundError` or `OSError` when the directory does not exist — no explicit check required:

```python
import os, shutil

def move_by_extension(source_dir, dest_dir, extension):
    if not extension.startswith('.'):
        extension = '.' + extension
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    moved = []
    for filename in os.listdir(source_dir):   # raises if source_dir missing
        if filename.endswith(extension):
            shutil.move(os.path.join(source_dir, filename),
                        os.path.join(dest_dir, filename))
            moved.append(filename)
    return moved
```

When the task description says "move files matching a pattern" without mentioning subdirectories, use `os.listdir` over `os.walk`. The `os.walk` alternative silently succeeds even when the source directory is absent (it yields nothing), which prevents the natural `FileNotFoundError` from propagating.

## When Source Existence Matters

Some tasks explicitly require raising `FileNotFoundError` when the source is missing. The idiomatic approach is a guard before `os.listdir`:

```python
if not os.path.exists(source_dir):
    raise FileNotFoundError("The source directory does not exist.")
if not os.path.exists(target_dir):
    os.makedirs(target_dir)
for filename in os.listdir(source_dir):
    ...
```

## Extension Extraction Without a Leading Dot

`os.path.splitext(filename)` returns `(root, ext)` where `ext` includes the dot (e.g. `(".txt")`). When building a subdirectory name from the extension, strip the dot:

```python
_, ext = os.path.splitext(filename)
ext_clean = ext.lstrip('.')      # "txt", not ".txt"
ext_dir = os.path.join(directory, ext_clean)
if not os.path.exists(ext_dir):
    os.mkdir(ext_dir)
shutil.move(os.path.join(directory, filename), ext_dir)
```

Alternatively, use `re.search(r'\.(.*?)$', filename)` to extract the extension without a dot directly via `match.group(1)`.

## Recursive Traversal with os.walk

Reserve `os.walk` for tasks that explicitly require searching subdirectories:

```python
import os, shutil, fnmatch

def collect_recursive(source_dir, dest_dir, file_pattern):
    moved = []
    for root, dirs, files in os.walk(source_dir):
        for filename in fnmatch.filter(files, file_pattern):
            shutil.move(os.path.join(root, filename),
                        os.path.join(dest_dir, filename))
            moved.append(filename)
    return moved
```

## Backup and Archive Recipes

**Backup a directory tree:**

```python
import os, shutil

def backup_directory(src_folder, backup_dir):
    backup_path = os.path.join(backup_dir, os.path.basename(src_folder))
    shutil.copytree(src_folder, backup_path)   # raises FileExistsError if already backed up
    return True
```

`shutil.copytree` raises `FileExistsError` if `dst` already exists. Pass `dirs_exist_ok=True` only when the task explicitly allows overwriting.

**Archive a directory to a zip file:**

```python
archive_path = shutil.make_archive(
    base_name="/tmp/project",   # no .zip — function adds it
    format="zip",
    root_dir="/data/project"
)
# archive_path == "/tmp/project.zip"
```

Passing `"/tmp/project.zip"` as `base_name` produces `"/tmp/project.zip.zip"`.

## Clearing a File vs Deleting It

"Clear" or "erase contents" means truncate the file to zero bytes while keeping it on disk:

```python
# Clear file contents (file stays on disk, size becomes 0)
with open(filepath, 'w') as f:
    f.truncate(0)

# Copy to destination, then clear the original
dest = shutil.copy(filename, dest_dir)
with open(filename, 'w') as f:
    f.truncate(0)
return os.path.abspath(dest)
```

## Disk Usage

```python
usage = shutil.disk_usage("/some/path")
# usage.total, usage.used, usage.free — all in bytes
result = {"total": usage.total, "used": usage.used, "free": usage.free}
```

## Key Pitfalls

- `os.makedirs(path, exist_ok=True)` does **not** raise when the path already exists. Use the explicit `if not os.path.exists` guard when the task requires an error on existing destination.
- `shutil.copy` on a non-existent source raises `FileNotFoundError` naturally — wrap in `try/except Exception` only when the task requires a soft failure (e.g., returning a status string instead of raising).
- `Path.walk()` requires Python 3.12+. In Python 3.10/3.11, use `os.walk(str(path))` instead.
