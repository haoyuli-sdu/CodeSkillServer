---
name: base64-binary-to-text-encoding
description: 'Guide for base64 encoding/decoding: return types, Fernet key format, numpy array encoding, salt+hash tuples, and common pitfalls.'
---

# base64 — Binary-to-Text Encoding

## Core Functions and Return Types

```
base64.b64encode(bytes_obj)              → bytes  (call .decode() for str)
base64.b64decode(str_or_bytes)           → bytes  (call .decode('utf-8') for str)
base64.urlsafe_b64encode(bytes_obj)      → bytes  (for Fernet keys, URL-safe contexts)
base64.urlsafe_b64decode(str_or_bytes)   → bytes
```

Always `.decode()` after `b64encode()` to get a `str` from `bytes`:

```python
encoded = base64.b64encode(b"hello world").decode()       # 'aGVsbG8gd29ybGQ='
decoded = base64.b64decode("aGVsbG8gd29ybGQ=").decode()   # 'hello world'
```

## Encoding Numpy Arrays

When encoding a numpy array, convert to its string representation with
`np.array2string()` (without `separator`), then encode as ASCII:

```python
text = np.array2string(standardized)              # default separator: no commas
encoded = base64.b64encode(text.encode('ascii')).decode('ascii')
```

Using `separator=', '` or `tobytes()` produces a different format than `np.array2string()`
with defaults — the canonical form is no explicit separator.

## Decoding a Base64-Encoded JSON Payload

```python
decoded_str = base64.b64decode(raw_string).decode('utf-8')
data = json.loads(decoded_str)
file_path = os.path.join(output_dir, filename + '.csv')   # append extension explicitly
```

When the task says the `filename` parameter is a base name without extension, build
the full path as `filename + '.csv'` rather than relying on `filename` already having it.

## Hex String → Base64

To convert a hex string (possibly with `\x` prefixes) to base64:

```python
data_bytes = binascii.unhexlify(hex_str.replace('\\x', ''))   # strip \x prefixes first
encoded = base64.b64encode(data_bytes).decode()
```

## Salt + Hash → (base64, hexdigest) Return Tuple

When a function returns `(base64_salt, hex_hash)`:

```python
salt = os.urandom(salt_size)
salted = salt + data_bytes
hash_str = hashlib.sha256(salted).hexdigest()      # 64-char hex
return base64.b64encode(salt).decode('utf-8'), hash_str
```

The hash uses `hexdigest()` (64 chars); only the salt is base64-encoded.

## Fernet Symmetric Encryption

`Fernet` requires a 32-byte URL-safe base64 key. When given a user-supplied string,
pad or truncate to exactly 32 bytes then encode:

```python
from cryptography.fernet import Fernet
key = base64.urlsafe_b64encode(encryption_key.encode().ljust(32)[:32])
fernet = Fernet(key)
encrypted = fernet.encrypt(message.encode())
return base64.b64encode(encrypted).decode()
```

For a randomly generated key: `fernet_key = Fernet.generate_key()` (already base64 bytes).

## pbkdf2_hmac + Base64

```python
salt = os.urandom(16)
hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
return base64.b64encode(salt), base64.b64encode(hashed)   # return bytes objects
```

Both return values are `bytes`; call `.decode()` on each if strings are needed.

## RSA + Base64 Patterns

Private keys serialize with `.save_pkcs1()` (not `.save_pem()`):

```python
(pub_key, priv_key) = rsa.newkeys(512)
priv_key_b64 = base64.b64encode(priv_key.save_pkcs1()).decode('utf-8')
```

When archiving encrypted files, use the file's `basename` as the archive member name:

```python
with zipfile.ZipFile('archive.zip', 'w') as zf:
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                encrypted = rsa.encrypt(f.read(), pub_key)
            zf.writestr(filename, base64.b64encode(encrypted).decode())
```

## XOR Encryption with Hash Key

```python
key = hashlib.sha256(password.encode()).digest()   # 32 bytes
encrypted = bytes([b ^ key[i % len(key)] for i, b in enumerate(plaintext.encode())])
return base64.b64encode(encrypted).decode()
```

## Common Pitfalls

- `b64encode()` returns **bytes**. `b64encode(x).decode()` gives a `str`.
- `b64decode()` returns **bytes**. `.decode('utf-8')` gives a `str`.
- Fernet takes a urlsafe-base64-encoded 32-byte key — a raw string raises `ValueError`.
- `rsa.PrivateKey` serializes with `.save_pkcs1()`, not `.save_pem()`.
- When building file paths, append the extension explicitly: `filename + '.csv'`.
- Do NOT call `.encode()` on a `bytes` object — it raises `AttributeError`.
