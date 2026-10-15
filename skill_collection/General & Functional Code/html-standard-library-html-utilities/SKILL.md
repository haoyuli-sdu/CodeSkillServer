---
name: html-standard-library-html-utilities
description: html.unescape() for decoding HTML entities and html.escape() for encoding, commonly used in text cleaning pipelines with base64 and regex.
---

# html — Standard Library HTML Utilities

The Python standard library `html` module provides basic HTML escaping/unescaping. It is NOT a parser — use `html.parser.HTMLParser` for parsing, or `BeautifulSoup`/`lxml` for full HTML parsing.

## HTML Entity Handling

```python
import html

# Unescape HTML entities
html.unescape('&amp;lt;div&amp;gt;')   # returns '<div>'
html.unescape('Caf&eacute;')            # returns 'Café'
html.unescape('&quot;hello&quot;')      # returns '"hello"'

# Escape special characters for HTML output
html.escape('<script>alert("xss")</script>')
# returns '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'

html.escape('<tag>', quote=False)  # quote=True by default, escapes " and '
```

`html.unescape()` is the correct way to decode HTML character references (both named like `&amp;` and numeric like `&#160;`). This is the primary use of the `html` module in BigCodeBench tasks.

## Common Pattern: Decode and Clean Text

```python
import html
import base64
import re

# Typical pipeline: base64 decode -> html unescape -> normalize whitespace
raw = base64.b64decode(encoded).decode('utf-8')
text = html.unescape(raw)
text = re.sub(r'\s+', ' ', text).strip()
```
