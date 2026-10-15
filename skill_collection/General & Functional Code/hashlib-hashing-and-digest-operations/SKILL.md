---
name: hashlib-hashing-and-digest-operations
description: 'Guide for hashlib API: hexdigest vs digest vs base64 output formats, salt+hash patterns, HMAC, pbkdf2_hmac, and return type contracts.'
---

# hashlib — Hashing and Digest Operations

## Output Format Reference

```
hashlib.sha256(data).hexdigest()         → 64-char lowercase hex string
hashlib.sha256(data).digest()            → 32 raw bytes
hashlib.md5(data).hexdigest()            → 32-char lowercase hex string
hashlib.md5(data).digest()               → 16 raw bytes
base64.b64encode(sha256_digest)          → 44-char base64 bytes (call .decode() for str)
```

When the expected output is a plain hash string, return `hexdigest()` directly — not
a dict, not a list, and not a base64-encoded value. If the spec says "base64-encode
the hash", use `.digest()` then `base64.b64encode(...)`.

## Core Patterns

**String input** — always `.encode()` first:

```python
h = hashlib.sha256("hello".encode()).hexdigest()   # 64-char hex
h = hashlib.md5(text.encode()).hexdigest()          # 32-char hex
```

**File content hashing** (read in binary mode):

```python
with open(filepath, 'rb') as f:
    data = f.read()
checksum = hashlib.sha256(data).hexdigest()
```

**Recursive directory hashing** — use `os.walk` and `os.path.join` for full paths:

```python
hash_dict = {}
for root, dirs, files in os.walk(directory):
    for filename in files:
        filepath = os.path.join(root, filename)
        with open(filepath, 'rb') as f:
            hash_dict[filepath] = hashlib.sha256(f.read()).hexdigest()
json_path = os.path.join(directory, 'hashes.json')
with open(json_path, 'w') as f:
    json.dump(hash_dict, f)
return json_path
```

The dict key is the full joined path (`os.path.join(root, filename)`), not a
relative path or Path object.

## Salt + Hash Patterns

**Standard pattern** — generate random bytes as salt, hex-digest the hash:

```python
salt = os.urandom(salt_size)
data_bytes = binascii.unhexlify(hex_str.replace('\\x', ''))   # strip \x prefixes
salted = salt + data_bytes
hash_str = hashlib.sha256(salted).hexdigest()      # 64-char hex
salt_b64 = base64.b64encode(salt).decode('utf-8') # base64 string
return salt_b64, hash_str
```

**Password prefix + salt as hex string** — concatenate as text, encode, then digest:

```python
salt_bytes = os.urandom(salt_length)
salted_password = prefix + password + salt_bytes.hex()
hashed = hashlib.sha256(salted_password.encode()).digest()
return base64.b64encode(hashed).decode()
```

Note: `salt_bytes.hex()` converts bytes to a hex string before string concatenation.

## Hashing Dict Values with a Salt

When hashing each value in a dict with a shared random salt:

```python
random.seed(seed)
salt = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
for key in data_dict:
    data_dict[key] = hashlib.sha256((str(data_dict[key]) + salt).encode()).hexdigest()
```

Call `random.seed()` before generating the salt. Use `str(value)` — not `repr()` or
`json.dumps()` — to convert dict values to strings for hashing.

## Generating Passwords and Hashing

When generating a random lowercase alphanumeric password and then hashing it:

```python
characters = 'abcdefghijklmnopqrstuvwxyz0123456789'
password = ''.join(random.choice(characters) for _ in range(password_length))
combined = password + salt_string
hashed = hashlib.sha256(combined.encode('utf-8')).hexdigest()
return json.dumps(hashed)
```

Use exactly the character set specified — commonly `abcdefghijklmnopqrstuvwxyz0123456789`
(lowercase only), not uppercase or symbols unless the spec says otherwise.

## HMAC

```python
import hmac, hashlib, json

# HMAC-SHA256 of a JSON-serialized dict:
hmac_obj = hmac.new(secret_key.encode(), json.dumps(req_data).encode(), hashlib.sha256)
signature = hmac_obj.hexdigest()   # hex string, URL-encodable

# HMAC-SHA1, compared against a pre-computed hex signature:
computed = hmac.new(key.encode(), msg.encode(), hashlib.sha1)
return binascii.hexlify(computed.digest()).decode() == provided_signature
```

## pbkdf2_hmac — Key Derivation

Returns raw bytes; all arguments must be bytes:

```python
salt = os.urandom(16)
hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
return base64.b64encode(salt), base64.b64encode(hashed)
```

When salt is a hex string (from `secrets.token_hex()`), pass it as
`bytes(salt, 'utf-8')` not `.encode('hex')`.

## Encoding + Hashing Chain

Canonical chain for XOR-based encryption keyed by a hash:

```python
key = hashlib.sha256(password.encode()).digest()   # 32 raw bytes
encrypted = bytes([b ^ key[i % len(key)] for i, b in enumerate(plaintext.encode())])
return base64.b64encode(encrypted).decode()
```

## Return Type Contract

| Spec says | Return |
|---|---|
| "return the hash" | `hexdigest()` — plain 64-char str for SHA256 |
| "return base64 of the hash" | `base64.b64encode(digest()).decode()` |
| "(salt, hash) tuple" | `(base64_encoded_salt, hexdigest_hash)` |
| plain `str` return annotation | return the string directly, no wrapping |
