---
name: pathlib-object-oriented-filesystem-paths
description: 'Guide for pathlib: Path components, iterdir for non-recursive, rglob(''*'') with is_file() for recursive, and Python 3.10 compatibility notes.'
---

# pathlib — Object-Oriented Filesystem Paths

## Creating Path Objects

```python
from pathlib import Path
import pathlib

p = Path("/data/reports/summary.csv")
p = Path("relative/dir")
p = pathlib.Path(raw_string)   # when import is `import pathlib`
```

`Path` objects are accepted in place of strings by most stdlib functions in Python 3.6+.

## Path Components

```python
p = Path("/data/reports/summary.csv")
p.name      # "summary.csv"      (full basename)
p.stem      # "summary"          (name without last suffix)
p.suffix    # ".csv"             (last extension, dot included)
p.suffixes  # [".csv"]           (all extensions)
p.parent    # Path("/data/reports")
p.parts     # ("/", "data", "reports", "summary.csv")
```

## Splitting a Path into Components

`Path(p).parts` is more reliable than `str.split('/')` — it handles leading/trailing slashes correctly:

```python
def split_path(path_str):
    path_str = path_str.replace("\\", "/")
    parts = pathlib.Path(path_str).parts
    return [c for c in parts if c and c != '/']
# split_path("a/b/c")       → ["a", "b", "c"]
# split_path("/a/b/c")      → ["a", "b", "c"]  (root "/" filtered out)
```

## Resolving to Absolute Paths

`p.resolve()` returns the absolute path with all symlinks resolved:

```python
abs_path = Path(filepath).resolve()          # absolute Path object
abs_str  = str(Path(filepath).resolve())     # as string
```

`Path(filepath).resolve()` works even if the path does not exist on the filesystem.

## Iterating a Directory (Non-Recursive)

`p.iterdir()` yields `Path` objects for immediate children only — the equivalent of `os.listdir`:

```python
source_path = pathlib.Path(source_dir).resolve()
destination_path = pathlib.Path(dest_dir).resolve()
destination_path.mkdir(parents=True, exist_ok=True)

results = []
for entry in source_path.iterdir():
    if entry.is_file():
        results.append(entry.name)
        shutil.copy(str(entry), str(destination_path))
return (source_path.name, results)
```

## Recursive File Discovery

`p.glob(pattern)` searches under `p` using glob syntax. `p.rglob('*')` matches all files and directories recursively (equivalent to `glob("**/*")`):

```python
# Find all files at any depth — use rglob('*') not rglob('*.')
for path in Path(directory).rglob('*'):
    if path.is_file():
        process(path)

# Find all .txt files recursively
for txt in Path(directory).glob('**/*.txt'):
    process(txt)
```

`rglob('*.')` is not a valid pattern for matching all files — the trailing dot matches only paths ending in a literal dot. Use `rglob('*')` and filter with `.is_file()`.

When combining `pathlib` traversal with `os.walk` for hash computation or file cataloging:

```python
from pathlib import Path
import os

hash_dict = {}
for root, dirs, files in os.walk(directory):
    for file in files:
        file_path = Path(root) / file          # Path arithmetic for clean joins
        with open(file_path, 'rb') as f:
            content = f.read()
        hash_dict[str(file_path)] = hashlib.sha256(content).hexdigest()
```

**Note:** `Path.walk()` was added in Python 3.12. In Python 3.10/3.11, use `os.walk(str(path))` instead.

## Directory Creation

```python
Path(dest_dir).mkdir(parents=True, exist_ok=True)  # equivalent to os.makedirs(dest_dir, exist_ok=True)
```

## Common Idioms

**Build a new filename in the same directory:**

```python
p = Path(filepath)
new_name = p.stem + "_processed" + p.suffix    # e.g., "report_processed.csv"
new_path = p.parent / new_name
```

**Validate path for invalid characters, then split:**

```python
def validate_and_split(path, delimiter=os.path.sep):
    if not path:
        return []
    path = path.replace("\\", "/")
    path_obj = pathlib.Path(path)
    invalid = set('<>:"|?*')
    if any(set(str(c)).intersection(invalid) for c in path_obj.parts):
        return []
    return [c for c in path_obj.parts if c and c != delimiter]
```

**Copy files from a dict (key = path, value = content or None):**

```python
def copy_non_empty(kwargs, target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    copied = []
    for file, content in kwargs.items():
        if content is not None and os.path.isfile(file):
            target_file = Path(target_dir) / Path(file).name
            shutil.copyfile(file, target_file)
            copied.append(str(target_file))
    return copied
```

## File Metadata

```python
stat = p.stat()
stat.st_size    # size in bytes
stat.st_mtime   # modification time (Unix timestamp float)
stat.st_ctime   # metadata change time (Linux) / creation time (Windows)
```

## Pitfalls

- `Path.iterdir()` yields `Path` objects, not strings. Use `.name` for just the filename or `str(entry)` for the full path.
- `p.parts` includes `"/"` as the first element on absolute paths — filter with `if c != "/"`.
- `p.suffix` returns the last extension only (e.g., `".gz"` for `"file.tar.gz"`); use `p.suffixes` for all extensions.
- `Path.walk()` requires Python 3.12+; use `os.walk()` in 3.10/3.11 environments.
- `p.rglob('*')` with `.is_file()` check is the correct pattern for all-file traversal. `rglob('*.')` matches nothing useful.
