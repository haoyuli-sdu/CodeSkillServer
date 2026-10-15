---
name: gzip-gzip-compression-and-decompression
description: Guide to gzip.open vs GzipFile, text/binary modes, urlopen response handling, NumPy array compression, hex decompression.
---

# gzip — Gzip Compression and Decompression

## Two APIs: gzip.open vs gzip.GzipFile

**`gzip.open(path, mode)`** operates on files by path. Modes: `'rb'`/`'wb'` for bytes, `'rt'`/`'wt'` for text:

```python
# Write compressed
with gzip.open('output.gz', 'wb') as f:
    f.write(json.dumps(data).encode())

# Read compressed
with gzip.open('output.gz', 'rb') as f:
    content = f.read()
```

**`gzip.GzipFile(fileobj=buf, mode='w')`** compresses into an in-memory `BytesIO` buffer:

```python
buffer = io.BytesIO()
with gzip.GzipFile(fileobj=buffer, mode='w') as gz:
    gz.write(struct.pack('d' * arr.size, *arr))
return buffer.getvalue()   # returns bytes
```

Use `gzip.GzipFile` when no disk path is involved and you need the compressed bytes directly.

## Text mode — lines come back as str

`gzip.open(path, 'rt')` yields `str` lines (no `.decode()` needed):

```python
with gzip.open(path1, 'rt') as f1, gzip.open(path2, 'rt') as f2:
    lines1 = f1.readlines()
    lines2 = f2.readlines()
diff = difflib.ndiff(lines1, lines2)
return ''.join(line for line in diff if line.startswith('+ ') or line.startswith('- '))
```

## Fetching data then writing to gzip

When the response object comes from `urllib.request.urlopen`, call `.read()` then `.decode()` before parsing:

```python
response = urllib.request.urlopen(url_str)
raw = response.read().decode('utf-8')
data = json.loads(raw)
with gzip.open(file_path, 'wb') as f_out:
    f_out.write(json.dumps(data).encode())
return file_path
```

Do not call `json.loads` directly on the response object — it needs a `str` or `bytes`, not a file-like object.

## Decompressing hex-encoded gzip data

Convert hex to bytes with `binascii.unhexlify`, decompress, then decode:

```python
compressed_bytes = binascii.unhexlify(hex_string)
decompressed = gzip.decompress(compressed_bytes)
return decompressed.decode('utf-8')
```

`gzip.decompress(data)` is a convenience function equivalent to opening a `GzipFile` and reading — it takes `bytes` and returns `bytes`.

## Compressing a NumPy array

Pack array elements with `struct.pack` using the `'d'` (double/float64) format, then compress into a buffer:

```python
buffer = io.BytesIO()
with gzip.GzipFile(fileobj=buffer, mode='w') as f:
    f.write(struct.pack('d' * arr.size, *arr))
return buffer.getvalue()
```

The `'d' * arr.size` format string packs every element as an 8-byte double, producing a compact binary representation suitable for gzip compression.
