---
name: rsa-rsa-encryption-and-signing
description: Key generation, save_pkcs1 not save_pem, encryption/decryption size limits, signing with .digest() bytes, zip encryption of directory files, AES encryption of private key.
---

# rsa — RSA Encryption and Signing

## Key Generation

`rsa.newkeys(nbits)` returns a `(PublicKey, PrivateKey)` tuple:

```python
import rsa
(pub_key, priv_key) = rsa.newkeys(512)   # 512-bit keys for demos
```

Return the key objects directly — do not convert to PEM bytes unless the task asks for
serialization.

## Serializing Keys (save_pkcs1, not save_pem)

`PrivateKey.save_pkcs1()` and `PublicKey.save_pkcs1()` return PEM-format bytes.
There is **no** `.save_pem()` method on either key type:

```python
priv_pem = priv_key.save_pkcs1()     # b'-----BEGIN RSA PRIVATE KEY-----\n...'
pub_pem  = pub_key.save_pkcs1()

# Round-trip:
priv_key = rsa.PrivateKey.load_pkcs1(priv_pem)
pub_key  = rsa.PublicKey.load_pkcs1(pub_pem)
```

Calling `b64encode(pub_key)` raises `TypeError` — encode the PEM bytes instead:
`b64encode(pub_key.save_pkcs1())`.

## Encryption and Decryption

Both input and output are bytes. RSA with PKCS#1 v1.5 can only encrypt small payloads
(~53 bytes for a 512-bit key). For bulk data, use a hybrid approach: encrypt a
symmetric key with RSA, then use that key for AES or Fernet.

```python
encrypted = rsa.encrypt(b"short message", pub_key)   # bytes → bytes
original  = rsa.decrypt(encrypted, priv_key)          # bytes → bytes
```

## Signing and Verification

`rsa.sign()` accepts raw bytes. When signing a hash, pass `.digest()` (bytes), not
a hash object or hex string:

```python
from hashlib import sha256
import urllib.request

content = urllib.request.urlopen(url).read()   # bytes — no decoding needed
hash_bytes = sha256(content).digest()          # raw bytes
signature = rsa.sign(hash_bytes, priv_key, 'SHA-256')
sig_hex = signature.hex()
```

`rsa.verify(message, signature, pub_key)` returns the hash method name on success and
raises `rsa.pkcs1.VerificationError` on failure.

## Encrypting Files into a Zip Archive

Encrypt each file individually and store base64-encoded ciphertext inside the zip:

```python
import rsa, os, zipfile
from base64 import b64encode

(pub_key, priv_key) = rsa.newkeys(512)
zip_name = 'encrypted_files.zip'    # write at cwd, not inside the target directory

with zipfile.ZipFile(zip_name, 'w') as zipf:
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                data = f.read()
            encrypted = rsa.encrypt(data, pub_key)
            zipf.writestr(filename, b64encode(encrypted).decode('utf-8'))

return pub_key, zip_name
```

## AES Encryption of RSA Private Key (PyCryptodome)

A common pattern: generate keys, serialize the private key, encrypt the PEM bytes:

```python
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from base64 import b64encode
import os

password = get_random_bytes(16)
cipher = AES.new(password, AES.MODE_EAX)      # nonce auto-generated
nonce = cipher.nonce
priv_pem = priv_key.save_pkcs1()              # bytes — use save_pkcs1(), not save_pem()
ciphertext, tag = cipher.encrypt_and_digest(priv_pem)

filename = f'private_key_{os.urandom(8).hex()}.txt'
with open(filename, 'w') as f:
    f.write(b64encode(ciphertext).decode('utf-8'))

return pub_key, filename, password, nonce
```
