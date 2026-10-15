---
name: hmac-hash-based-message-authentication
description: Core API (hmac.new key/msg encoding), signing dicts without sort_keys, URL-encoding signatures, binascii signature validation, timing-safe comparison.
---

# hmac — Hash-Based Message Authentication

## Core API

`hmac.new(key, msg, digestmod)` creates an HMAC object. Both `key` and `msg` must be
bytes — encode strings before passing:

```python
import hmac, hashlib

obj = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256)
hex_sig = obj.hexdigest()   # hex string
raw_sig = obj.digest()      # bytes
```

`.hexdigest()` is a method on the HMAC object, not on bytes:
```python
# Wrong: .digest() returns bytes — bytes has no .hexdigest()
sig = hmac.new(key, msg, hashlib.sha256).digest()
sig.hexdigest()   # AttributeError

# Right: call hexdigest() on the object
sig = hmac.new(key, msg, hashlib.sha256).hexdigest()
```

## Signing a Dictionary

Serialize with `json.dumps()` before signing. Do **not** sort keys unless explicitly
required — adding `sort_keys=True` or sorting items changes the serialized string and
produces a different signature:

```python
import json, hmac, hashlib, urllib.parse

def sign_request(req_data, secret_key):
    payload = json.dumps(req_data)            # default insertion order — no sorting
    obj = hmac.new(secret_key.encode(), payload.encode(), hashlib.sha256)
    return urllib.parse.quote_plus(obj.hexdigest())
```

## Validating a Signature (binascii pattern)

When the expected signature is a hex string derived from `.digest()`, use
`binascii.hexlify` to produce the same representation, then compare:

```python
import base64, hashlib, hmac, binascii

def validate_hmac(b64_message, expected_hex, secret_key):
    decoded = base64.b64decode(b64_message).decode()
    computed = hmac.new(secret_key.encode(), decoded.encode(), hashlib.sha1)
    return binascii.hexlify(computed.digest()).decode() == expected_hex
```

`binascii.hexlify(computed.digest()).decode()` and `computed.hexdigest()` produce
identical results. Use either consistently.

## Digest Algorithm Reference

Pass the hash constructor as `digestmod`, not a string:

```
hmac.new(key, msg, hashlib.sha1)    → HMAC-SHA-1  (20-byte digest, 40-char hex)
hmac.new(key, msg, hashlib.sha256)  → HMAC-SHA-256 (32-byte digest, 64-char hex)
hmac.new(key, msg, hashlib.sha512)  → HMAC-SHA-512 (64-byte digest, 128-char hex)
```

## URL-Encoding a Signature

`urllib.parse.quote_plus()` percent-encodes a string and converts spaces to `+`:

```python
import urllib.parse
url_sig = urllib.parse.quote_plus(obj.hexdigest())
```

## Timing-Safe Comparison

`hmac.compare_digest(a, b)` guards against timing attacks. Both arguments must be the
same type (both `str` or both `bytes`):

```python
return hmac.compare_digest(computed.hexdigest(), expected_sig)
```
