---
name: io-in-memory-file-objects-and-binary-tex
description: BytesIO/StringIO usage, seek patterns, PIL image fetching, gzip compression, and CSV/pandas integration via StringIO.
---

# io — In-Memory File Objects and Binary/Text I/O

## BytesIO and StringIO fundamentals

`io.BytesIO` holds binary data; `io.StringIO` holds text. Both implement the full file interface in memory. After writing, **seek to position 0** before reading back or passing to a library:

```python
buf = io.BytesIO()
buf.write(b'binary content')
buf.seek(0)           # rewind before reading
data = buf.read()     # b'binary content'
```

`getvalue()` returns all buffered bytes without changing the current position:
```python
buf = io.BytesIO()
buf.write(b'hello')
all_bytes = buf.getvalue()   # b'hello' — no seek needed
```

## Wrapping HTTP response content for PIL

PIL's `Image.open` accepts any file-like object. Wrap `response.content` in `BytesIO` to avoid writing to disk:

```python
import requests, io
from PIL import Image

def fetch_image(url):
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    image = Image.open(io.BytesIO(response.content))
    return image
```

Use `raise_for_status()` rather than comparing `response.status_code` to integer ranges — mock environments set `status_code` to a non-integer object, so arithmetic comparisons raise `TypeError`.

## StringIO with CSV and pandas

The most common use of `StringIO` is feeding a string to a file-consuming library:

```python
import csv, io

reader = csv.reader(io.StringIO(raw_csv_text))
rows = list(reader)
```

```python
import pandas as pd, io, requests

response = requests.get(csv_url)
df = pd.read_csv(io.StringIO(response.text))
```

Build a CSV in memory and return as a string:
```python
out = io.StringIO()
writer = csv.writer(out)
writer.writerow(["label", "value"])
writer.writerows(data_pairs)
csv_string = out.getvalue()   # or out.seek(0); out.read()
```

## In-memory ZIP with BytesIO

Build a ZIP archive without touching disk:

```python
import io, zipfile

def build_zip(file_entries):
    """file_entries: list of (arcname, content_bytes) tuples"""
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, 'w') as zf:
        for arcname, content in file_entries:
            zf.writestr(arcname, content)
    zip_io.seek(0)    # rewind AFTER the with-block closes and finalizes the ZIP
    return zip_io
```

When handing the buffer to a web framework's `FileResponse`, keep it open and seeked to 0.

## BytesIO with gzip compression

`gzip.GzipFile` accepts a `fileobj` parameter so you can compress into a `BytesIO`:

```python
import io, gzip

def compress_bytes(data: bytes) -> bytes:
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb') as gz:
        gz.write(data)
    return buf.getvalue()

def decompress_bytes(compressed: bytes) -> bytes:
    buf = io.BytesIO(compressed)
    with gzip.GzipFile(fileobj=buf) as gz:
        return gz.read()
```

## io.open vs built-in open

`io.open` is identical to the built-in `open` in Python 3. Use it when the module-level import is `import io` and the code needs an explicit reference:

```python
with io.open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

with io.open(file1, 'rb') as f1, io.open(file2, 'rb') as f2:
    h1 = hashlib.md5(f1.read()).hexdigest()
    h2 = hashlib.md5(f2.read()).hexdigest()
```

## Encoding re-wrapping with StringIO

To read a file in one encoding and expose it as a file-like object in another context:

```python
with io.open(filename, 'r', encoding='latin-1') as f:
    content = f.read()
file_like = io.StringIO(content)
reader = csv.DictReader(file_like, delimiter='\t')
```

## Common pitfalls

- **Forgetting to seek**: writing to a `BytesIO` moves the pointer to the end. Always call `.seek(0)` before handing the buffer to any reader.
- **`getvalue()` vs `read()`**: `getvalue()` always returns the full buffer regardless of position; `read()` returns only data from the current position onward.
- **BytesIO for binary, StringIO for text**: passing a `str` to `BytesIO` raises `TypeError`; passing `bytes` to `StringIO` raises `TypeError`. Match the type to the buffer class.
