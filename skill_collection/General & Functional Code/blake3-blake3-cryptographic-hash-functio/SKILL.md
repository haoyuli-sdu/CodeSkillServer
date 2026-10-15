---
name: blake3-blake3-cryptographic-hash-functio
description: Constructor-only API (blake3.blake3, not blake3.hash or blake3.Hasher), incremental hashing, return types for hexdigest and digest.
---

# blake3 — BLAKE3 Cryptographic Hash Function

## Basic Usage

The `blake3` package exposes a single constructor: `blake3.blake3(data)`. Pass bytes
directly and call `.hexdigest()` or `.digest()`:

```python
import blake3, json, hashlib

def hash_payload(data: dict) -> tuple:
    json_bytes = json.dumps(data).encode('utf-8')
    blake3_hex = blake3.blake3(json_bytes).hexdigest()     # 64-char hex string
    md5_hex = hashlib.md5(blake3_hex.encode()).hexdigest()
    return blake3_hex, md5_hex
```

## Constructor Only — No Module-Level Functions

The `blake3` package has **no** `blake3.hash()` function and no `blake3.Hasher` class.
The constructor is always `blake3.blake3(...)`:

```python
# Correct:
result = blake3.blake3(b"my data").hexdigest()

# These do not exist and raise AttributeError:
# blake3.hash(b"data")
# blake3.Hasher(b"data")
```

## Incremental Hashing

Create an empty hasher, then feed data with `.update()`:

```python
hasher = blake3.blake3()
hasher.update(b"chunk one")
hasher.update(b"chunk two")
hex_result = hasher.hexdigest()   # same as blake3.blake3(b"chunk one" + b"chunk two").hexdigest()
```

## Return Types

```
blake3.blake3(data).hexdigest()          → str   (64 hex chars = 256-bit hash)
blake3.blake3(data).digest()             → bytes (32 bytes)
blake3.blake3(data).hexdigest(length=n)  → str   (2n hex chars = n-byte hash)
```
