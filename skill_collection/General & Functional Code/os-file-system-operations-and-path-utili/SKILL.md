---
name: os-file-system-operations-and-path-utili
description: 'Guide for correct os module usage: listdir vs walk, extension matching, re.match vs re.search for filenames, makedirs patterns, file existence checks, and file erasure vs deletion.'
---

# os — File System Operations and Path Utilities

## Path Construction and Decomposition

`os.path.join(dir, name)` — joins components with the platform separator.
`os.path.basename(p)` — last path component: `"/a/b/c.txt"` → `"c.txt"`.
`os.path.dirname(p)` — parent component: `"/a/b/c.txt"` → `"/a/b"`; `"data.csv"` → `""` (empty string).
`os.path.splitext(p)` — splits at last dot: `"archive.tar.gz"` → `("archive.tar", ".gz")`.
`os.path.abspath(p)` — resolves relative path to absolute.

## Directory Traversal: Two Patterns

`os.listdir(dir)` returns bare names in that directory only — no recursion. Always join before any further path operation:

```python
for name in os.listdir(folder):
    full_path = os.path.join(folder, name)
    if name.endswith('.json'):
        with open(full_path) as f:
            data = json.load(f)
```

`os.walk(top)` is a recursive generator yielding `(dirpath, dirnames, filenames)`. Filenames are bare — join with `dirpath`:

```python
for dirpath, _, filenames in os.walk(root):
    for name in filenames:
        full_path = os.path.join(dirpath, name)
        process(full_path)
```

**Extension filter applies the same way in both patterns:**

```python
# listdir — flat directory, one extension type
records = []
for name in os.listdir(data_dir):
    if name.endswith('.csv'):
        records.append(os.path.join(data_dir, name))

# walk — recursive traversal, one extension type
records = []
for dirpath, _, filenames in os.walk(data_dir):
    for name in filenames:
        if name.endswith('.csv'):
            records.append(os.path.join(dirpath, name))
```

## Extension Matching

Pass the extension exactly as stored. If `extension = '.txt'`, write `filename.endswith(extension)`. Writing `filename.endswith('.' + extension)` produces `filename.endswith('..txt')` and never matches.

For glob patterns: `glob.glob(os.path.join(dir, '*' + ext))` where `ext` includes the leading dot (e.g. `'.log'`).

## Pattern Matching in Filenames

`re.match(pattern, filename)` anchors at the **start** of the string — use it when the pattern describes the entire filename format (e.g. `r'access\.log\.\d+'`).
`re.search(pattern, filename)` finds the pattern anywhere in the string — use it when the pattern may appear in the middle of a filename.

```python
# Collect files whose names contain a substring pattern (re.search)
for name in os.listdir(directory):
    if re.search(r'(error|warn)', name, re.IGNORECASE):
        process(os.path.join(directory, name))

# Sort by modification time after matching on full filename format (re.match)
matched = [f for f in os.listdir(log_dir) if re.match(r'app\.\d{4}-\d{2}-\d{2}\.log', f)]
matched.sort(key=lambda f: os.path.getmtime(os.path.join(log_dir, f)), reverse=True)
```

## Creating Directories

`os.makedirs(path, exist_ok=True)` — creates the full path tree; silently succeeds if it already exists.
`os.mkdir(path)` — creates one level only; raises `FileExistsError` if it exists.

When creating a destination that should only be made if absent:
```python
if not os.path.exists(target_dir):
    os.makedirs(target_dir)
```

**Guard against empty dirname:** `os.path.dirname("data.csv")` returns `""`. Calling `os.makedirs("")` raises `FileNotFoundError`. Guard with:
```python
parent = os.path.dirname(output_path)
if parent:
    os.makedirs(parent, exist_ok=True)
```

## Common Recipes

**Collect files, write output, return absolute path:**
```python
os.makedirs(output_dir, exist_ok=True)
out_path = os.path.join(output_dir, filename)
with open(out_path, 'w') as f:
    f.write(content)
return os.path.abspath(out_path)
```

**Read files, accumulate stats, return dict:**
```python
stats = {}
for name in os.listdir(folder):
    if name.endswith('.log'):
        with open(os.path.join(folder, name)) as f:
            for line in f:
                key = parse_key(line)
                stats[key] = stats.get(key, 0) + 1
return stats
```

**Recursive hash of all files in a directory:**
```python
hashes = {}
for dirpath, _, filenames in os.walk(directory):
    for name in filenames:
        fp = os.path.join(dirpath, name)
        with open(fp, 'rb') as f:
            hashes[fp] = hashlib.sha256(f.read()).hexdigest()
```

## File Existence Checks

`os.path.exists(p)` — True for files, directories, and symlinks.
`os.path.isfile(p)` — True only for regular files.
`os.path.isdir(p)` — True only for directories.

When a function is expected to raise `FileNotFoundError` for a missing source path, let the natural I/O error propagate rather than silently creating the missing path:

```python
# The open() call raises FileNotFoundError naturally if the file is absent
with open(source_path, 'r') as f:
    content = f.read()
```

In environments where network/IO operations are substituted with in-process equivalents, post-operation existence checks (`os.path.isfile(dest)`) will fail because no real file was written to disk. Perform the read immediately after the operation completes, without an intermediate existence assertion.

## File Contents vs. File Deletion

`os.remove(path)` — **deletes** the file from disk entirely.

To erase the contents while keeping the file on disk (i.e., make it empty):
```python
with open(path, 'w') as f:
    f.truncate(0)
```

## File Metadata and Sorting

`os.path.getmtime(p)` → float (Unix modification timestamp). Use as a sort key to find the most recently modified file:
```python
candidates = [f for f in os.listdir(log_dir) if f.endswith('.log')]
candidates.sort(key=lambda f: os.path.getmtime(os.path.join(log_dir, f)), reverse=True)
latest = os.path.join(log_dir, candidates[0]) if candidates else None
```

`os.path.getsize(p)` → int (bytes). Zero means empty file.
`os.stat(p).st_size` — same as `getsize`.

## Environment Variables and Random Bytes

`os.getenv(key, default=None)` — returns the value or default if unset.
`os.environ[key]` — raises `KeyError` if missing.

```python
host = os.getenv('MAIL_SERVER', 'localhost')
port = int(os.getenv('MAIL_PORT', 25))
```

`os.urandom(n)` → `bytes` of `n` cryptographically random bytes.

## Quick Reference

| Need | Function |
|---|---|
| Flat directory listing | `os.listdir(dir)` |
| Recursive traversal | `os.walk(dir)` |
| Extension filter | `name.endswith('.ext')` |
| Pattern anywhere in name | `re.search(pattern, name)` |
| Create full path tree | `os.makedirs(path, exist_ok=True)` |
| Absolute path | `os.path.abspath(path)` |
| File size | `os.path.getsize(path)` |
| Last-modified time | `os.path.getmtime(path)` |
| Erase file contents | `open(path, 'w').truncate(0)` |
| Delete file | `os.remove(path)` |
| Rename / move within filesystem | `os.rename(src, dst)` |
