---
name: urllib-standard-library-http-and-url-too
description: 'Guide for urllib sub-module usage: urlopen, urlretrieve, urlparse, error handling, hmac signing, and download-process-cleanup patterns.'
---

# urllib — Standard Library HTTP and URL Tools

## Module Structure

`urllib` is a package — import sub-modules explicitly:

```python
import urllib.request   # open URLs, download files
import urllib.parse     # parse and encode URLs
import urllib.error     # URLError, HTTPError
```

`import urllib` alone does not make sub-modules available.

## urllib.request: Fetching Data

### urlopen — streaming response

```python
response = urllib.request.urlopen(url)
data = response.read()           # returns bytes
text = response.read().decode()  # convert to str
```

`json.loads()` accepts bytes directly in Python 3.6+:

```python
import json
data = json.loads(urllib.request.urlopen(url).read())
```

Context manager form (closes the response automatically):

```python
with urllib.request.urlopen(url) as response:
    content = response.read().decode()
```

### urlretrieve — download to a file

```python
urllib.request.urlretrieve(url, local_path)
```

Downloads the URL and saves it at `local_path`. The return value `(filename, headers)` is usually ignored — the side effect (the file on disk) is what matters:

```python
import os
urllib.request.urlretrieve(url, TARGET_FILE)
with open(TARGET_FILE, "r") as f:
    content = f.read()
os.remove(TARGET_FILE)   # clean up after reading
```

## urllib.parse: URL Manipulation

### urlparse — decompose a URL

```python
from urllib.parse import urlparse

parsed = urlparse("https://www.python.org/docs/")
parsed.netloc   # "www.python.org"  — full host including www
parsed.scheme   # "https"
parsed.path     # "/docs/"
```

`netloc` preserves the hostname exactly as written in the URL. When building a domain-keyed dict from URLs in text, extract the full URL first, then take `.netloc`:

```python
import re
urls = re.findall(r'https?://[^\s,]+', text)
result = {}
for url in urls:
    domain = urlparse(url).netloc          # "www.python.org"
    result[domain] = lookup(domain)
```

### quote_plus — URL-encode a string

```python
from urllib.parse import quote_plus
encoded = quote_plus("hello world")   # "hello+world"
```

Spaces become `+` (not `%20`). Use `quote_plus` for form-encoded query strings and HMAC signatures.

## urllib.error: Exception Handling

`HTTPError` is a subclass of `URLError`. To handle both:

```python
import urllib.error

try:
    with urllib.request.urlopen(url) as res:
        data = res.read()
except urllib.error.HTTPError as e:
    raise ValueError(f"HTTP error: {e.code} {e.reason}") from e
except urllib.error.URLError as e:
    raise urllib.error.URLError(f"Failed to reach server: {e}") from e
```

When the specification asks to catch all errors (including plain exceptions injected to simulate failure), use a broad catch:

```python
try:
    with urllib.request.urlopen(url) as response:
        xml_data = response.read()
except Exception as e:
    raise ValueError(f"Error fetching: {e}")
```

## Common Recipe: Download, Process, Clean Up

```python
import urllib.request, os, json

TARGET = "temp_data.json"

def fetch_and_process(url):
    urllib.request.urlretrieve(url, TARGET)
    with open(TARGET, "r", encoding="utf-8") as f:
        data = json.load(f)
    os.remove(TARGET)
    return data
```

For zip archives, the same pattern applies — download to a temp file, extract, remove:

```python
import zipfile
urllib.request.urlretrieve(url, "archive.zip")
with zipfile.ZipFile("archive.zip", "r") as zf:
    zf.extractall(extract_dir)
os.remove("archive.zip")
```

## hmac + urllib.parse: Signing and Encoding

`hmac.new(key, msg, digestmod)` returns an HMAC object. Call `.hexdigest()` to get the hex string, then URL-encode:

```python
import hmac, hashlib
from urllib.parse import quote_plus

h = hmac.new(secret_key.encode(), json_msg.encode(), hashlib.sha256)
sig = h.hexdigest()                    # hex string
url_encoded = quote_plus(sig)          # spaces → +
```

## Return Type Quick Reference

| Call | Returns |
|------|---------|
| `urlopen(url).read()` | `bytes` |
| `urlopen(url).read().decode()` | `str` |
| `urlretrieve(url, path)` | `(filename, headers)` tuple — side effect is the file |
| `urlparse(url).netloc` | `str` — full hostname with `www.` |
| `quote_plus(s)` | `str` — URL-encoded with `+` for spaces |
