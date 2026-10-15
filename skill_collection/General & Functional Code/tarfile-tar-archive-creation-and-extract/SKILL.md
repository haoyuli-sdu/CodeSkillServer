---
name: tarfile-tar-archive-creation-and-extract
description: tarfile.open modes, regex-based add, relative arcname, MD5 verify then extract pattern.
---

# tarfile — TAR Archive Creation and Extraction

## Opening a tar archive

`tarfile.open(path, mode)` is the entry point:

| Mode | Purpose |
|---|---|
| `'r'` | Read, auto-detect compression |
| `'r:gz'` | Read gzip-compressed tar |
| `'w'` | Write uncompressed tar |
| `'w:gz'` | Write gzip-compressed tar |

```python
with tarfile.open('archive.tar.gz', 'r:gz') as tar:
    tar.extractall(dest_dir)
```

## Adding files to a tar (with pattern matching)

Use `pathlib.Path.rglob('*')` to walk the directory. Pass `arcname=path.relative_to(directory)` to store relative paths. Match against `path.name` (filename only), not the full path string:

```python
tar_path = Path(directory) / 'archive.tar'
with tarfile.open(tar_path, 'w') as tar:
    for path in Path(directory).rglob('*'):
        if re.match(file_pattern, path.name):
            try:
                tar.add(path, arcname=path.relative_to(directory))
            except PermissionError as e:
                print(f"Skipping {path}: {e}")
return str(tar_path)
```

An empty archive (no matching files) is valid — `tarfile.open(path, 'w')` followed by no `add()` calls creates a valid empty tar.

## Download, verify MD5, then extract

After downloading, compute MD5 in a streaming loop, compare, then extract or delete:

```python
try:
    urllib.request.urlretrieve(url, TARGET_TAR_FILE)
except Exception as e:
    print(e)
    return False

md5_hash = hashlib.md5()
with open(TARGET_TAR_FILE, 'rb') as f:
    for block in iter(lambda: f.read(4096), b''):
        md5_hash.update(block)

if md5_hash.hexdigest() != EXPECTED_MD5_CHECKSUM:
    os.remove(TARGET_TAR_FILE)
    return False

with tarfile.open(TARGET_TAR_FILE, 'r:gz') as tar:
    tar.extractall(TARGET_DIR)
os.remove(TARGET_TAR_FILE)
return True
```

## Listing archive contents

`tar.getmembers()` returns `TarInfo` objects; `tar.getnames()` returns just the name strings:

```python
with tarfile.open('archive.tar.gz', 'r:gz') as tar:
    members = tar.getnames()   # ['dir/file1.txt', 'dir/file2.txt']
```
