---
name: struct-binary-data-packing-and-unpacking
description: Binary format strings, hex-to-float conversion with big-endian byte order, encoding floats as UTF-8 bytes, and packing sequences.
---

# struct — Binary Data Packing and Unpacking

## Format Strings: Byte Order Prefix

The first character of a format string sets byte order:

| Prefix | Meaning |
|--------|---------|
| `'!'` or `'>'` | big-endian (network byte order) |
| `'<'` | little-endian |
| (none) | native byte order |

Common type characters:

| Char | C type | Size |
|------|--------|------|
| `'b'`/`'B'` | signed/unsigned char | 1 byte |
| `'h'`/`'H'` | short/unsigned short | 2 bytes |
| `'i'`/`'I'` | int/unsigned int | 4 bytes |
| `'f'` | float (binary32) | 4 bytes |
| `'d'` | double (binary64) | 8 bytes |

## pack and unpack

`struct.pack(fmt, *values)` → bytes
`struct.unpack(fmt, buffer)` → **tuple** (always, even for one value)

```python
import struct

data = struct.pack('!Hf', 42, 3.14)
port, value = struct.unpack('!Hf', data)

# Single value — index [0] to unwrap the tuple
value = struct.unpack('!f', data)[0]
```

## Hex String → float (Canonical Pattern)

To convert a 4-byte hex string to a 32-bit float, interpret the hex bytes as big-endian:

```python
import struct, random

KEYS = ['470FC614', '4A0FC614', '4B9FC614']
hex_key = random.choice(KEYS)
float_val = struct.unpack('!f', bytes.fromhex(hex_key))[0]
```

Use `'!'` (big-endian). Using `'<f'` (little-endian) on the same hex string produces a completely different numeric value.

**Alternative: `int(hex_string, 16)` as integer argument to pack**

When the task says "convert hex string to a float and compress it", the canonical approach treats the integer value of the hex as the bit-pattern of a float:

```python
import struct, zlib

hex_string = '470FC614'
binary_float = struct.pack('!f', int(hex_string, 16))   # int as float bits
compressed = zlib.compress(binary_float)
```

This is different from `bytes.fromhex(hex_string)` followed by `struct.unpack` — they round-trip through the same float value, but the pack/compress path is more direct when you just want the bytes.

## Encoding a Float as UTF-8 Bytes

After unpacking a float, convert to string then encode:

```python
import struct, random, codecs

hex_key = random.choice(KEYS)
float_num = struct.unpack('!f', bytes.fromhex(hex_key))[0]
encoded = codecs.encode(str(float_num), 'utf-8')    # returns bytes
# equivalent: str(float_num).encode('utf-8')
```

Return the `bytes` object directly. Do not wrap it in a dict or call `.to_bytes()` on the float.

## Packing Multiple Values (e.g., a NumPy array)

Repeat the format character to pack a sequence:

```python
import struct, io, gzip

values = [1.0, 2.5, 3.7]
packed = struct.pack('d' * len(values), *values)

# With gzip:
buf = io.BytesIO()
with gzip.GzipFile(fileobj=buf, mode='w') as f:
    f.write(struct.pack('d' * arr.size, *arr))
result = buf.getvalue()
```

## calcsize

`struct.calcsize(fmt)` returns the total byte count for a format:

```python
struct.calcsize('!Hf')   # 6 (2 + 4)
struct.calcsize('ddd')   # 24 (3 × 8)
```
