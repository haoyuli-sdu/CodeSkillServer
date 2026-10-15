---
name: requests-practical-http-patterns
description: 'Guide for correct requests API usage: GET/POST patterns, URL construction, image fetching, ZIP download, BeautifulSoup integration, and common pitfalls.'
---

# requests — Practical HTTP Patterns

## Core GET Pattern

The idiomatic GET call — use `response.text` for string content, `response.content` for bytes, or `response.json()` to parse JSON directly:

```python
import requests

response = requests.get(url)
text = response.text          # decoded string (html, csv, xml)
raw = response.content        # raw bytes (images, zip files)
data = response.json()        # parse JSON body directly
```

When the specification asks to raise an error on HTTP failure:

```python
response = requests.get(url)
response.raise_for_status()   # raises requests.exceptions.HTTPError for 4xx/5xx
```

When the specification says to return an error string or `None` on failure, catch broadly and return:

```python
try:
    response = requests.get(url)
    data = response.json()
    return process(data)
except Exception as e:
    return str(e)   # or: return None
```

## URL Construction

When combining a base URL and an endpoint or path segment, use direct string concatenation — no path separator is added unless the strings already include it:

```python
# base URL already ends with '/' or the path starts cleanly
filename = PREFIX + endpoint + '.json'   # "PREFIX_data.json" not "PREFIX__data.json"
response = requests.get(BASE_URL + username)    # not f"{BASE_URL}/{username}"
```

If the base URL needs a separator, ensure it appears exactly once — double-checking whether `BASE_URL` already ends with `/`.

## Fetching an Image

Pass `io.BytesIO(response.content)` to `Image.open()`. Return the image object directly without calling `.convert()` unless the task explicitly specifies a target mode:

```python
import requests, io
from PIL import Image

response = requests.get(url, timeout=5)
response.raise_for_status()
image = Image.open(io.BytesIO(response.content))
return image    # preserves original format and mode (e.g. RGBA, PNG)
```

Only use `stream=True` + `response.raw` when the task description explicitly requests streaming:

```python
response = requests.get(url, stream=True, timeout=10)
response.raise_for_status()
img = Image.open(response.raw).convert("L")   # grayscale, streaming
```

## Downloading and Extracting ZIP Files

```python
import requests, zipfile, os
from pathlib import Path

def fetch_and_extract(url, filename, download_dir, zip_dir):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        filepath = download_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            for chunk in response.iter_content():
                f.write(chunk)
        out_dir = zip_dir / filename[:-4]
        out_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(filepath, "r") as zf:
            zf.extractall(out_dir)
        return "Download and extraction successful", list(out_dir.iterdir())
    return "Download failed", []
```

Non-streaming download (simple): write `response.content` directly to file, then extract.

## POST with Authorization

```python
headers = {'Authorization': 'Bearer ' + token}
payload = {'url': extracted_url}
response = requests.post(api_endpoint, headers=headers, data=json.dumps(payload))
return response.json()
```

## Extracting URLs with Regex

Standard patterns for pulling URLs from arbitrary text:

```python
import re

urls = re.findall(r'https?://[^\s,]+', text)   # all URLs, any scheme
url  = re.search(r'(https?://\S+)', text).group()   # first URL
```

Use `[^\s,]+` or `\S+` to stop at whitespace — do not match within quoted strings unless the task input is always a quoted string. Feed the extracted URL directly to `requests.get()`.

## BeautifulSoup Integration

Canonical scraping workflow:

```python
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# page title — returns None when absent
title = soup.title.string if soup.title else None   # use .string, not .get_text()

# first table → DataFrame
table = soup.find('table')
headers = [th.text.strip() for th in table.find_all('th')]
rows = []
for tr in table.find_all('tr'):
    cols = [td.text.strip() for td in tr.find_all('td')]
    if cols:
        rows.append(cols)
df = pd.DataFrame(rows, columns=headers if headers else None)
```

## Writing Rows to CSV

```python
import csv
with open(path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Emails"])     # header
    for item in items:
        writer.writerow([item])     # one item per row
```

## GitHub API / Sorting Repos

```python
response = requests.get(API_URL + user + '/repos')
data = json.loads(response.text)
repos = {repo['name']: repo['created_at'] for repo in data}
sorted_repos = collections.OrderedDict(sorted(repos.items(), key=lambda x: x[1]))
return list(sorted_repos.keys())
```

## Domain / URL Parsing

```python
from urllib.parse import urlparse
domain = urlparse("https://www.example.com/path").netloc   # "www.example.com"
```

`netloc` preserves the full hostname as written — do not strip `www.` unless the task asks for it.
