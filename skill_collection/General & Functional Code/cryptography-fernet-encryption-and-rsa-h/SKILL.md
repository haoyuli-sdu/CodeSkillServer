---
name: cryptography-fernet-encryption-and-rsa-h
description: Fernet key requirements and user-string derivation, hybrid Fernet+RSA encryption, hazmat RSA signing, AES-CBC with PKCS7 padding.
---

# cryptography — Fernet Encryption and RSA Hazmat

## Fernet Symmetric Encryption

`Fernet` requires a key that is exactly 32 URL-safe base64-encoded bytes.
`Fernet.generate_key()` always produces a valid key; for a user-supplied string, wrap
it with `base64.urlsafe_b64encode()` first:

```python
import base64
from cryptography.fernet import Fernet

# Fresh random key:
key = Fernet.generate_key()        # bytes, always valid
fernet = Fernet(key)

# From a user string — must be exactly 32 bytes before encoding:
raw = user_string.encode()[:32].ljust(32, b'\0')   # pad/truncate to 32 bytes
key = base64.urlsafe_b64encode(raw)
fernet = Fernet(key)

# Encrypt / decrypt:
token = fernet.encrypt(plaintext.encode())   # bytes (Fernet token)
plain = fernet.decrypt(token)                # bytes
result = base64.b64encode(token).decode()    # base64-encode the token for str output
```

Passing an arbitrary string directly to `Fernet(...)` raises `ValueError: Fernet key
must be 32 url-safe base64-encoded bytes`.

## Hybrid Encryption (Fernet + RSA)

Use `Fernet` for bulk data and RSA to protect the Fernet key:

```python
import rsa
from cryptography.fernet import Fernet
from base64 import b64encode

(pub_key, priv_key) = rsa.newkeys(512)
fernet_key = Fernet.generate_key()       # bytes, always a valid Fernet key
fernet = Fernet(fernet_key)

with open(file_path, 'rb') as f:
    encrypted_data = fernet.encrypt(f.read())

encrypted_key = rsa.encrypt(fernet_key, pub_key)   # rsa.PublicKey wraps the key

# Save encrypted_data and b64encode(encrypted_key) to separate files
```

`rsa.encrypt(fernet_key, pub_key)` returns bytes; `b64encode(pub_key)` raises
`TypeError` because `pub_key` is a key object, not bytes.

## RSA Signing with cryptography.hazmat

`private_key.sign(data, padding, algorithm)` — the key must be a `cryptography.hazmat`
RSA private key (from `rsa.generate_private_key()` or loaded from PEM), not an
`rsa.PrivateKey` from the `rsa` package:

```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

signature = private_key.sign(
    data_bytes,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH,
    ),
    hashes.SHA256(),
)
encoded = base64.b64encode(signature).decode()
```

For base conversion with a custom alphabet, index the numpy character array directly:
`np.array(list(alphabet))[index]` returns a string element that concatenates normally.

## AES-CBC with cryptography.hazmat

```python
from cryptography.hazmat.primitives import padding as haz_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

aes_key = os.urandom(32)
iv = os.urandom(16)
cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())

padder = haz_padding.PKCS7(128).padder()    # 128 = AES block size in bits
padded = padder.update(data) + padder.finalize()

encryptor = cipher.encryptor()
ciphertext = encryptor.update(padded) + encryptor.finalize()
```

`padding.PKCS7(128)` is correct; `padding.PKCS7Padding` does not exist.

## Return Types

```
Fernet.generate_key()              → bytes (valid 44-char base64 key)
fernet.encrypt(plaintext_bytes)    → bytes (Fernet token)
fernet.decrypt(token_bytes)        → bytes
base64.b64encode(token).decode()   → str
```
