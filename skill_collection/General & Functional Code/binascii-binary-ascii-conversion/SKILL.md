---
name: binascii-binary-ascii-conversion
description: 'Guide for binascii hexlify/unhexlify: hex preprocessing, return types, HMAC validation, file scanning patterns, and ctypes.CDLL._name.'
---

# binascii — Binary/ASCII Conversion

## Core Functions

```
binascii.hexlify(bytes_obj)      → bytes  (ASCII hex digits, e.g. b'deadbeef')
binascii.unhexlify(hex_str)      → bytes  (requires even-length hex string)
```

Always `.decode()` the result of `hexlify()` to get a plain `str`:

```python
raw = b'\xde\xad\xbe\xef'
hex_str = binascii.hexlify(raw).decode()    # 'deadbeef'
back = binascii.unhexlify('deadbeef')       # b'\xde\xad\xbe\xef'
```

## Hex String Preprocessing (\\x Prefixes)

Input hex strings may carry `\x` escape prefixes (e.g. `'\\x48\\x65\\x6c\\x6c\\x6f'`).
Strip the two-character sequence before calling `unhexlify`:

```python
cleaned = hex_str.replace('\\x', '')        # removes the literal \x two-char sequence
data = binascii.unhexlify(cleaned)
```

`unhexlify` raises `binascii.Error` on odd-length strings or invalid hex characters.
Wrap it to convert to a domain error:

```python
hex_str_cleaned = hex_str.replace('\\x', '')
try:
    bytes_data = binascii.unhexlify(hex_str_cleaned)
except binascii.Error:
    raise ValueError("Invalid hex string")
```

## hexlify as Hex Output for Hash Digests

`binascii.hexlify(hash_obj.digest()).decode()` and `hash_obj.hexdigest()` produce the
same result. Use `hexlify` when starting from raw bytes (e.g. from `.digest()`):

```python
hash_bytes = hashlib.sha256(data).digest()
hex_output = binascii.hexlify(hash_bytes).decode()     # same as .hexdigest()
```

Salted database password pattern:

```python
salted = password_bytes + salt.encode('utf-8')
hashed = binascii.hexlify(hashlib.sha256(salted).digest()).decode('utf-8')
cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
```

## HMAC Signature Comparison

When validating a hex-encoded HMAC signature:

```python
decoded_msg = base64.b64decode(encoded_msg).decode()
computed = hmac.new(secret_key.encode(), decoded_msg.encode(), hashlib.sha1)
return binascii.hexlify(computed.digest()).decode() == provided_signature
```

## Hex Frequency Analysis Pattern

To analyze byte value distributions from a hex string:

```python
cleaned = hex_str.replace('\\x', '')
bytes_data = binascii.unhexlify(cleaned)
byte_values, counts = np.unique(np.frombuffer(bytes_data, dtype=np.uint8), return_counts=True)
df = pd.DataFrame({'Byte Value': byte_values, 'Frequency': counts})
```

## ctypes.CDLL and Library Name

When loading a DLL with `ctypes.CDLL(filepath)`, the `_name` attribute is exactly the
path string passed to the constructor — not the OS-resolved library name:

```python
lib = ctypes.CDLL(filepath)
name = lib._name    # equals filepath exactly
```

Do NOT call `ctypes.util.find_library()` to retrieve the name — it searches system
paths and may return a different path or `None`.

## Hash + hexlify for File Scanning

When scanning a directory for files by pattern and computing their hashes:

```python
for root, _, files in os.walk(directory):
    for filename in files:
        if re.search(pattern, filename):
            path = os.path.join(root, filename)
            with open(path, 'rb') as f:
                digest = hashlib.sha256(f.read()).digest()
            result[path] = binascii.hexlify(digest).decode()
```

The dict key is the full `os.path.join(root, filename)` path.

## Hex String → Bytes Pipeline

Common chain for encoding:

```python
raw = binascii.unhexlify(hex_str.replace('\\x', ''))
encoded = base64.b64encode(raw).decode()
```

For a pure hex string (no `\x` prefixes), `bytes.fromhex(hex_string)` is equivalent:

```python
decoded_str = bytes.fromhex(hex_string).decode("utf-8")
```

## Common Pitfalls

- `hexlify()` returns **bytes**, not a `str`. Always call `.decode()`.
- `unhexlify()` requires an even-length input (every byte = 2 hex chars).
- Strip `\x` prefixes with `replace('\\x', '')` (two literal characters, not the escape `\x`).
- `ctypes.CDLL._name` is the constructor argument, not the OS-found library name.
- `binascii.unhexlify` and `bytes.fromhex` are interchangeable for clean hex strings,
  but only `unhexlify` accepts `bytes` input directly.
