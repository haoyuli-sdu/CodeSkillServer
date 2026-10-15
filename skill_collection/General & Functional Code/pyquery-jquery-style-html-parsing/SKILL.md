---
name: pyquery-jquery-style-html-parsing
description: 'Practical reference for PyQuery: raw lxml element vs PyQuery object access patterns, idiomatic anchor extraction, and text/attribute method differences.'
---

# PyQuery — jQuery-style HTML Parsing

PyQuery wraps lxml to provide a jQuery-like API for parsing and querying HTML/XML.

## Basic Usage

```python
from pyquery import PyQuery as pq

# Initialize from HTML string
d = pq(html_string)

# CSS selector syntax — identical to jQuery
anchors = d('a')           # all <a> elements
divs = d('div.content')    # <div> with class "content"
item = d('#main')          # element with id "main"
```

## Iterating and Extracting Data

When you iterate over a PyQuery selection, each item is a **raw lxml element** (not a PyQuery object):

```python
for a in d('a'):
    # a is a raw lxml element here
    text = a.text                # raw lxml property (may be None)
    href = a.get('href')         # raw lxml attribute getter (returns None if missing)
```

To use PyQuery methods on a single element from iteration, wrap it first:

```python
for a in d('a'):
    elem = pq(a)                 # wrap the raw element
    text = elem.text()           # PyQuery method (returns string, never None)
    href = elem.attr('href')     # PyQuery attribute getter
```

## Idiomatic Anchor Extraction

The canonical pattern for collecting all anchors into a list of tuples:

```python
d = pq(html_string)
anchors = [(a.text, a.get('href')) for a in d('a')]
# Result: [("Link text", "https://..."), (None, None), ...]
# Includes ALL anchors, even those with None text or None href
```

This includes ALL anchors regardless of whether their text or href is `None`.

## Typical Pipeline: Fetch URL and Extract Anchors

```python
import urllib.request
from pyquery import PyQuery as pq
from datetime import datetime
import pandas as pd

def extract_anchors(url):
    if not url:
        raise ValueError("URL must not be empty.")
    with urllib.request.urlopen(url) as res:
        html = res.read().decode()
    d = pq(html)
    anchors = [(a.text, a.get('href')) for a in d('a')]
    fetch_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df = pd.DataFrame(anchors, columns=['text', 'href'])
    df['fetch_time'] = fetch_time
    return df
```

## Text and Attribute Methods

| Access pattern | Context | Returns |
|---|---|---|
| `a.text` | raw lxml element (from iteration) | string or `None` |
| `a.get('href')` | raw lxml element (from iteration) | string or `None` |
| `pq(a).text()` | PyQuery-wrapped element | string (empty string if None) |
| `pq(a).attr('href')` | PyQuery-wrapped element | string or `None` |
| `d('h1').text()` | PyQuery selection | concatenated text of all matched |
| `d('a').attr('href')` | PyQuery selection | attribute of **first** match only |

## Common Pitfalls

- **`.text` vs `.text()`**: on a raw lxml element `a.text` is a property; on a PyQuery object `elem.text()` is a method call. Calling `.text()` on a raw lxml element raises `TypeError`.
- **Filtering drops valid rows**: `if a.get('href')` skips anchors with `href=None` or `href=""`. To include every anchor tag (the common expectation), collect without filtering.
- **`pq(html_bytes)` works**: PyQuery accepts both `str` and `bytes` for initialization.
