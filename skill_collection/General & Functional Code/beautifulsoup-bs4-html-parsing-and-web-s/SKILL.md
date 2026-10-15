---
name: beautifulsoup-bs4-html-parsing-and-web-s
description: 'Practical reference for BeautifulSoup: parser selection, text extraction, element finding, table-to-DataFrame, error handling patterns, and CSV/JSON output.'
---

# BeautifulSoup (bs4) — HTML Parsing and Web Scraping

## Parser Selection and Input Type

```python
from bs4 import BeautifulSoup
import requests

# Standard case — pass response.text (already decoded string)
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# When the encoding matters (e.g. cp1251 — decode explicitly from bytes)
soup = BeautifulSoup(response.content.decode('cp1251'), 'html.parser')

# urllib: urlopen().read() returns bytes — bs4 accepts raw bytes directly
import urllib.request
html = urllib.request.urlopen(url).read()
soup = BeautifulSoup(html, 'html.parser')
```

Use `'html.parser'` (stdlib, always available) or `'lxml'` (faster, third-party) as the second argument.

## Text Extraction: `.string` vs `.get_text()`

These behave differently for tags with nested children:

```python
# .string — returns NavigableString when the tag has ONE direct text node; returns None otherwise
title_text = soup.title.string if soup.title else None  # works for simple <title>Hello</title>
tag = soup.find('h1')
text = tag.string if tag else None   # None if <h1> has nested children like <h1><span>...</span></h1>

# .get_text() — concatenates all nested text, NEVER returns None (returns '' for empty tags)
body = soup.body.get_text(separator=' ', strip=True)
page_text = soup.get_text()          # all visible text; strip whitespace per element with strip=True

# Consequence: tag.string returns None (not '') for complex tags; use .get_text() when in doubt
```

## Finding Elements

```python
# First match — returns None if not found
tag = soup.find('h1')
table = soup.find('table', {'id': 'results'})       # by attribute dict
div = soup.find('div', attrs={'class': 'data'})

# All matches — returns [] if not found
links = soup.find_all('a', href=True)
rows = table.find_all('tr') if table else []

# Table rows → cells
for tr in table.find_all('tr'):
    cells = [td.get_text(strip=True) for td in tr.find_all('td')]
```

## Getting Attributes

```python
for a in soup.find_all('a', href=True):
    href = a['href']           # KeyError if missing
    href = a.get('href')       # None if missing (safer)
    text = a.get_text(strip=True)

from urllib.parse import urljoin
abs_href = urljoin(base_url, a.get('href', ''))
```

## Extracting Text for Regex

Run regex over `soup.get_text()` to operate on stripped plain text:

```python
plain_text = soup.get_text()
emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', plain_text)
phones = re.findall(r'\+\d{1,3}?\s?\(?\d{1,4}?\)?\s?\d{1,4}?\s?\d{1,9}', plain_text)
```

## Table Extraction to DataFrame

```python
import pandas as pd
from io import StringIO

table = soup.find('table', {'id': table_id})
if table is None:
    raise ValueError("Table with the specified ID not found.")
if not table.find_all('tr'):
    return pd.DataFrame()

df = pd.read_html(StringIO(str(table)))[0]   # fastest approach
```

Manual extraction when `pd.read_html` is not appropriate:

```python
headers = [th.get_text(strip=True) for th in table.find_all('th')]
rows = []
for tr in table.find_all('tr'):
    cols = [td.get_text(strip=True) for td in tr.find_all('td')]
    if cols:
        rows.append(cols)
df = pd.DataFrame(rows, columns=headers if headers else None)
```

## Error Handling Patterns

Let the operation raise naturally unless the task specification says to catch and return a fallback:

```python
# Pattern A — propagate connection and HTTP errors (most common):
try:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
except requests.ConnectionError as e:
    raise ConnectionError(f"Could not connect: {e}")
except requests.HTTPError as e:
    raise e
soup = BeautifulSoup(response.text, 'html.parser')

# Pattern B — return None on any failure (when task says so explicitly):
if not url:
    return None
try:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    soup = BeautifulSoup(response.content.decode(from_encoding), parser)
    return soup
except Exception:
    return None
```

## Writing Scraped Data

**JSON append pattern** — one JSON object per line:
```python
data = {"title": soup.title.string if soup.title else None}
with open(file_name, 'a', encoding='utf-8') as f:
    f.write(json.dumps(data) + '\n')
return file_name
```

**CSV pattern** — one item per row:
```python
import csv
with open(csv_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Emails'])
    for email in emails:
        writer.writerow([email])   # NOT writer.writerow(emails) — that puts all in one row
return csv_path
```

## Script Tag Evaluation

```python
for script in soup.find_all('script'):
    try:
        result = ast.literal_eval(script.string)
    except (ValueError, SyntaxError, TypeError):
        continue   # TypeError handles script.string being None
```

## Local Files via `file://` URLs

When a function is documented to accept `file://` URLs, strip the prefix and read the file directly
(requests cannot handle `file://`):

```python
if url.startswith('file://'):
    with open(url[7:], 'r') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
else:
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
```

## Common Pitfalls

- `tag.string` returns `None` (not `''`) for tags containing nested children — never rely on it being a string without checking
- `soup.title.string.strip()` — `.strip()` on a `NavigableString` is fine, but `soup.title.string` may be `None` if the title tag is absent
- `soup.find(tag)` returns `None` if not found — always guard before accessing `.string` or `.get_text()`
- `open(file, 'w', newline='')` is standard for CSV — omitting `newline=''` on Windows inserts extra blank lines
- `writer.writerow(emails)` puts all emails in one row; iterate and write each individually
- When `response.content.decode(encoding)` is specified by the task, do not substitute `response.text` (which uses requests' auto-detected encoding instead)
