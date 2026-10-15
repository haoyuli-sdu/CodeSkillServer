---
name: chardet-character-encoding-detection
description: 'Guide for chardet: detect returns dict not string, handle None encoding, standard detect-decode-reencode-parse pattern.'
---

# chardet — Character Encoding Detection

## Core Usage

`chardet.detect(bytes_data)` returns a dict — always access the `"encoding"` key:

```python
import chardet

result = chardet.detect(b'\xe4\xb8\xad\xe6\x96\x87')
# {'encoding': 'utf-8', 'confidence': 0.99, 'language': ''}

encoding = chardet.detect(content)["encoding"]
# encoding is None if content is empty or detection is ambiguous
```

## Standard Pattern: Detect → Decode → Re-encode → Parse

```python
import chardet, json, requests

def fetch_and_parse(url, from_encoding=None, to_encoding='utf-8'):
    response = requests.get(url, timeout=5)
    content = response.content   # raw bytes — use .content, not .text

    if from_encoding is None:
        detected = chardet.detect(content)["encoding"]
        if detected is None:
            if content:
                raise ValueError("Unable to detect encoding for non-empty content")
            return {}            # empty content → return empty dict
        content = content.decode(detected)
    else:
        content = content.decode(from_encoding)

    content = content.encode(to_encoding).decode(to_encoding)
    return json.loads(content)   # let JSONDecodeError propagate naturally
```

The re-encoding step (`encode → decode`) normalizes the string to the target encoding.

## Pitfalls

- `chardet.detect()` returns a **dict**, not a string — always use `["encoding"]`
- `encoding` can be `None` for empty or ambiguous byte sequences — check before `.decode()`
- Always pass `response.content` (bytes), not `response.text` (already decoded string)
- Let `json.loads()` raise its own `JSONDecodeError` — wrapping it in custom errors
  adds coupling without value

## Quick Reference: Return Structure

```python
chardet.detect(b"hello")
# {'encoding': 'ascii', 'confidence': 1.0, 'language': ''}

chardet.detect(b"")
# {'encoding': None, 'confidence': 0.0, 'language': None}
```
