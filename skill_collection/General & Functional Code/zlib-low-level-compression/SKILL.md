---
name: zlib-low-level-compression
description: 'Core zlib usage: compress/decompress bytes, compress→base64 pipeline, random.choices for RNG consistency, struct-packed binary.'
---

# zlib — Low-Level Compression

## Core functions

`zlib.compress(data)` takes `bytes` and returns compressed `bytes`. `zlib.decompress(data)` is the inverse:

```python
compressed = zlib.compress(b'hello world')
restored = zlib.decompress(compressed)    # b'hello world'
```

Both require `bytes` — encode strings first: `zlib.compress('text'.encode('utf-8'))`.

## Compress → base64-encode → return str

A standard pipeline: serialize, compress, base64-encode, decode to plain string:

```python
json_str = json.dumps(data_dict)
compressed = zlib.compress(json_str.encode())
return base64.b64encode(compressed).decode('utf-8')
```

`base64.b64encode()` returns `bytes`; call `.decode('utf-8')` to get a `str`.

## Random string → compress → base64

Use `random.choices(population, k=n)` (not a list comprehension with `random.choice`) to generate the string, since the two consume RNG state differently with the same seed:

```python
random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=string_length))
compressed = zlib.compress(random_string.encode('utf-8'))
return base64.b64encode(compressed).decode('utf-8')
```

## Struct-packed binary → compress

Pack a binary value with `struct.pack`, then compress:

```python
binary_float = struct.pack('!f', int(hex_string, 16))
return zlib.compress(binary_float)
```

## Compression level

`zlib.compress(data, level)` accepts 0 (store) through 9 (maximum compression), default is `-1` (equivalent to level 6):

```python
compressed_fast = zlib.compress(data, 1)   # speed priority
compressed_small = zlib.compress(data, 9)  # size priority
```
