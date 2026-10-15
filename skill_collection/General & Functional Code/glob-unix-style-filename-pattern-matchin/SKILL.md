---
name: glob-unix-style-filename-pattern-matchin
description: 'Guide for glob.glob patterns: single-level vs recursive, extension handling, zero-count file entries in aggregations, and path format consistency.'
---

# glob — Unix-Style Filename Pattern Matching

## Core API

`glob.glob(pattern)` → list of matching paths, in arbitrary filesystem order. Returns `[]` if nothing matches — never raises.

`glob.glob(pattern, recursive=True)` — enables `**` to match zero or more directory levels.

`glob.iglob(pattern)` — same as `glob.glob` but returns an iterator (memory-efficient for large directories).

## Building Patterns

Always build the full pattern by joining the directory and the wildcard suffix:

```python
import glob, os

# All .csv files in one directory (single-level)
csv_files = glob.glob(os.path.join(data_dir, '*.csv'))

# All files in one directory, any name (single-level)
all_files = glob.glob(os.path.join(data_dir, '*'))

# All files with any extension in one directory
any_ext_files = glob.glob(os.path.join(directory, '*.*'))

# All .log files at any depth (recursive)
log_files = glob.glob(os.path.join(log_dir, '**', '*.log'), recursive=True)
```

The single-level patterns (`'*'`, `'*.ext'`, `'*.*'`) return paths relative to the joined prefix — just the filenames when the prefix is the directory. This differs from `os.walk`, which constructs paths with `os.path.join(root, filename)` including an extra `./` or `subdir/` component.

## Extension Parameter Handling

```python
def collect(src, extension):
    if not extension.startswith('.'):
        extension = '.' + extension
    return glob.glob(os.path.join(src, '*' + extension))
```

## Iterating Multiple Extensions

Call `glob.glob` once per extension and concatenate:

```python
transferred_files = []
for ext in EXTENSIONS:                                  # e.g., ['.txt', '.csv', '.log']
    for src_file in glob.glob(os.path.join(SOURCE_DIR, '*' + ext)):
        shutil.move(src_file, DEST_DIR)
        transferred_files.append(os.path.basename(src_file))
```

When the `extensions` parameter is a list of glob patterns like `['*.txt', '*.md']` (already containing the wildcard), iterate them directly:

```python
matched_files = []
for ext in extensions:
    for file in glob.glob(os.path.join(directory, ext)):
        with open(file, 'r') as f:
            content = f.read()
        if re.search(pattern, content, re.IGNORECASE):
            matched_files.append(Path(file).resolve())
```

## Recording All Matched Files — Including Zero-Count Entries

When aggregating per-file statistics, every matched file must appear in the result, even if its count is zero. Initialize the entry before any filter logic:

```python
result = {}
for file_path in glob.glob(os.path.join(dir_path, '**', '*.txt'), recursive=True):
    rel = os.path.relpath(file_path, dir_path)
    matches = re.findall(r'\bword\b', open(file_path).read(), re.IGNORECASE)
    result[rel] = len(matches)     # always set — 0 when no matches
return result
```

Do **not** filter out files with zero matches unless the task specification explicitly says to exclude them.

## Reading All Files of a Type into a Dict

```python
import glob, os, csv

def read_csv_files(directory_path, file_extension='.csv'):
    data = {}
    for fpath in glob.glob(os.path.join(directory_path, '*' + file_extension)):
        filename = os.path.splitext(os.path.basename(fpath))[0]
        with open(fpath, 'r') as f:
            reader = csv.reader(f)
            data[filename] = list(reader)   # includes header row; skip only if task says to
    return data
```

## Handling Empty Results

`glob.glob` returns `[]` when no files match. Raise or return the exception the task specifies:

```python
file_list = glob.glob(pattern)
if not file_list:
    raise FileNotFoundError(f"No files found matching '{pattern}'.")
```

## Sorting Results

`glob.glob` returns results in an unspecified order. Sort explicitly when order matters:

```python
files = sorted(glob.glob(os.path.join(data_dir, '*.csv')))
files_by_mtime = sorted(glob.glob(os.path.join(log_dir, '*.log')), key=os.path.getmtime)
```

## Pattern Syntax Quick Reference

| Pattern | Meaning |
|---------|---------|
| `*`     | Any sequence of characters within one directory component |
| `*.*`   | Any filename that contains at least one dot |
| `?`     | Exactly one character |
| `[abc]` | One character from the set |
| `**`    | Zero or more directory components (requires `recursive=True`) |

`glob` does not support regex or brace expansion `{*.py,*.js}` — use one call per extension and concatenate.

## Pitfalls

- The `**` wildcard silently matches nothing when `recursive=True` is omitted.
- `glob` does not expand `~`; use `os.path.expanduser` first if needed.
- Results include the full path prefix from the pattern; use `os.path.basename` to get just the filename.
- `glob.glob(os.path.join(dir, '*'))` returns paths like `/dir/file.txt`, not `./file.txt`. Avoid mixing with `os.walk`-style path construction — the `./` prefix causes mismatches.
- `glob.glob(os.path.join(dir, '*' + ext))` correctly handles `ext='.csv'` and `ext='csv'` once you normalize the dot. Do not add an extra dot if the extension already includes one.
