---
name: unicodedata-unicode-character-database
description: 'Guide for unicodedata: NFKD ASCII normalization, API response processing with response.json(), file system normalization, and character properties.'
---

# unicodedata — Unicode Character Database

## Stripping Accents / Converting to ASCII

The standard idiom: NFKD decomposition, then encode-to-ASCII with `'ignore'`, then decode:

```python
import unicodedata

def to_ascii(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()

to_ascii('Café')     # 'Cafe'   — uppercase preserved, accent stripped
to_ascii('résumé')   # 'resume'
to_ascii('Müller')   # 'Muller'
```

`normalize()` does NOT change case. Use `.lower()` separately if needed.

## Processing API Responses

When all string values in a JSON-like dict need ASCII normalization, iterate the items
and apply the transformation only to `str` values:

```python
import unicodedata, requests

def fetch_and_normalize(url):
    response = requests.get(url)
    response.raise_for_status()     # propagates HTTPError naturally — no try/except needed
    data = response.json()          # requests built-in JSON parsing — no extra import needed

    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode()
        else:
            result[key] = value
    return result
```

Use `response.json()` — it is built into `requests` and requires no separate `import json`.

## Normalization Forms

| Form | Meaning |
|------|---------|
| NFC  | Canonical Composition — 'é' as single code point U+00E9 |
| NFD  | Canonical Decomposition — 'é' as 'e' + combining accent U+0301 |
| NFKD | Compatibility Decomposition — use for ASCII stripping |
| NFKC | Compatibility Composition — collapses ligatures (ﬁ → fi) |

## File System Normalization

```python
import unicodedata, pathlib, hashlib, os

def scan_directory(directory):
    result = {}
    for path in pathlib.Path(directory).iterdir():
        if path.is_file():
            name = unicodedata.normalize('NFKD', path.name).encode('ascii', 'ignore').decode()
            digest = hashlib.md5(path.read_bytes()).hexdigest()
            result[name] = {'Size': os.path.getsize(path), 'MD5 Hash': digest}
    return result
```

## CSV Word Counting with Normalization

```python
import unicodedata, csv
from collections import Counter

def count_normalized_words(csv_path):
    words = []
    with open(csv_path, 'r') as f:
        for row in csv.reader(f):
            for cell in row:
                normalized = unicodedata.normalize('NFKD', cell).encode('ascii', 'ignore').decode()
                words.append(normalized)
    return Counter(words).most_common(10)
```

## Character Properties

```python
unicodedata.category('A')       # 'Lu' (letter, uppercase)
unicodedata.category('1')       # 'Nd' (decimal digit)
unicodedata.name('\u00e9')      # 'LATIN SMALL LETTER E WITH ACUTE'
unicodedata.numeric('½')        # 0.5
```
