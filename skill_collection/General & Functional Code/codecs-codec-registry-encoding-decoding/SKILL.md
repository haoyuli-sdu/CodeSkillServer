---
name: codecs-codec-registry-encoding-decoding
description: 'Practical reference for codecs module: encode/decode return types, file I/O with encoding conversion, unicode_escape, hex conversions.'
---

# codecs — Codec Registry and Base Classes

## Core API

```python
import codecs

# Encode a string to bytes
codecs.encode("hello", "utf-8")      # b'hello'  (same as str.encode("utf-8"))
codecs.encode("hello", "latin-1")    # b'hello'
codecs.encode(b"hello", "hex")       # b'68656c6c6f'  (bytes input → hex bytes)

# Decode bytes to string
codecs.decode(b"hello", "utf-8")     # 'hello'  (same as bytes.decode("utf-8"))
codecs.decode(b"68656c6c6f", "hex")  # b'hello'  (hex → bytes)

# unicode_escape: decode literal \u sequences stored as a str
codecs.decode(r"\u00e9", "unicode_escape")  # 'é'
```

## Return Types at a Glance

| Call | Returns |
|---|---|
| `codecs.encode(str, "utf-8")` | `bytes` |
| `codecs.encode(str, "latin-1")` | `bytes` |
| `codecs.encode(bytes, "hex")` | `bytes` (hex ASCII) |
| `codecs.decode(bytes, "utf-8")` | `str` |
| `codecs.decode(str, "unicode_escape")` | `str` |
| `codecs.open(path, "r", enc)` | file object (text mode) |

## File I/O with Encoding Conversion

`codecs.open()` reads/writes files in a specific encoding:

```python
import codecs, glob, os

# Convert all .txt files from cp1251 to utf-8
for filepath in glob.glob(os.path.join(directory, "*.txt")):
    with codecs.open(filepath, "r", "cp1251") as f:
        content = f.read()
    with codecs.open(filepath, "w", "utf-8") as f:
        f.write(content)

# Invalid encoding name raises LookupError (not ValueError)
```

## Writing Encoded Bytes to a Binary File

`codecs.encode(str, encoding)` returns `bytes` — always open the file in binary mode:

```python
import codecs, os

os.makedirs(directory_name, exist_ok=True)
for file_name in file_names:
    with open(os.path.join(directory_name, file_name), "wb") as f:
        f.write(codecs.encode(content, encoding))   # "wb" because encode() returns bytes
```

## unicode_escape for DataFrame Columns

```python
import codecs, pandas as pd

df["UnicodeString"] = df["UnicodeString"].apply(
    lambda x: codecs.decode(x, "unicode_escape")
)
# unicode_escape accepts a str argument directly
```

## What codecs Does NOT Have

```python
# No normalize() function — use unicodedata instead
import unicodedata
unicodedata.normalize("NFC", text)    # CORRECT
# codecs.normalize(...)              # AttributeError: module has no attribute 'normalize'
```

## Encoding Pipeline: latin-1 round-trip

```python
import codecs, hashlib, random, string

# Encode as latin-1 bytes and decode as utf-8 (round-trip for ASCII range)
password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n))
password = codecs.encode(password, "latin-1").decode("utf-8")
hashed = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
```

## Hex String Conversions

```python
import codecs, binascii

# bytes → hex string
binascii.hexlify(b"Hello").decode()        # '48656c6c6f'
codecs.encode(b"Hello", "hex").decode()    # '48656c6c6f'  (same result)

# hex string → bytes → decoded string
decoded_str = bytes.fromhex(hex_string).decode("utf-8")
```
