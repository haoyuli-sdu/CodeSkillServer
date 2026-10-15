---
name: secrets-cryptographically-strong-random
description: token_hex/token_bytes/token_urlsafe functions, base-conversion+salt+hashing pattern with numpy, secure random selection, timing-safe comparison.
---

# secrets — Cryptographically Strong Random Values

## Core Functions

```
secrets.token_bytes(n)      → bytes   (n random bytes)
secrets.token_hex(n)        → str     (2n hex chars — n random bytes encoded as hex)
secrets.token_urlsafe(n)    → str     (~1.3×n chars, URL-safe base64, no padding)
```

`token_hex(16)` is the standard way to generate a random salt — returns a 32-character
hex string:

```python
import secrets, hashlib

salt = secrets.token_hex(16)    # 32-char hex string, freshly generated each call
hashed = hashlib.pbkdf2_hmac(
    'sha256',
    data_bytes,          # bytes
    salt.encode('utf-8'),   # salt must be bytes
    100000               # iteration count
)
```

## Base Conversion + Salt + Hashing Pattern

A common pipeline: convert a number to a target base using a numpy character table,
salt the result, hash with PBKDF2, and base64-encode:

```python
import numpy as np, secrets, hashlib, base64

def convert_and_hash(num, from_base, to_base, alphabet):
    base_table = np.array(list(alphabet))   # array of single-char strings

    n = int(num, from_base)
    digits = ''
    while n > 0:
        n, remainder = divmod(n, to_base)
        digits += base_table[remainder]     # numpy element concatenates as str

    converted = digits[::-1]
    salt = secrets.token_hex(16)           # fresh random salt
    hashed = hashlib.pbkdf2_hmac('sha256', converted.encode(), salt.encode(), 100000)
    return base64.b64encode(hashed).decode(), salt
```

`base_table[i]` returns a numpy string element — `+=` concatenation works normally.
`pbkdf2_hmac` requires bytes for both `password` and `salt`; call `.encode()` on str values.

## Secure Random Selection

`secrets.choice(sequence)` draws one cryptographically secure random element:

```python
import string
password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
```

`secrets.randbelow(n)` returns a random integer in `[0, n)`.

## Timing-Safe Comparison

`secrets.compare_digest(a, b)` prevents timing attacks when checking tokens or signatures.
Both arguments must be the same type:

```python
return secrets.compare_digest(computed_token, provided_token)
```

## secrets vs random

`secrets` is cryptographically secure; `random` is not. Use `secrets` for passwords,
salts, tokens, and anything security-sensitive.
