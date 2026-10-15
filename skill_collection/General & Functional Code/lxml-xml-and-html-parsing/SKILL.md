---
name: lxml-xml-and-html-parsing
description: 'Guide for lxml.etree and lxml.html: fetching XML bytes, separate error scopes for fetch/parse/database, XPath extraction, and SQLite storage patterns.'
---

# lxml — XML and HTML Parsing

lxml has two main submodules: `lxml.etree` for XML and `lxml.html` for HTML.

## XML Parsing with `lxml.etree`

```python
from lxml import etree
import urllib.request

with urllib.request.urlopen(url) as response:
    xml_data = response.read()   # bytes object — do NOT decode to str

root = etree.XML(xml_data)       # etree.XML and etree.fromstring are equivalent
```

**Keep the data as bytes** — `etree.XML()` accepts both bytes and str, but decoding first (`.decode('utf-8')`) can mask encoding issues. Never pass the response object itself; always call `.read()` first.

```python
# XPath and element search
items = root.findall('.//item')
data = [{child.tag: child.text for child in item} for item in items]
if not data:
    raise ValueError("XML structure does not match expected format.")
df = pd.DataFrame(data)
```

### Fetch + parse with separate error scopes

Separate the URL fetch from the XML parse into two distinct try/except blocks so each produces a distinct error type:

```python
import urllib.request
from lxml import etree
import pandas as pd

def fetch_xml_as_dataframe(url):
    try:
        with urllib.request.urlopen(url) as response:
            xml_data = response.read()
    except Exception as e:
        raise ValueError(f"Error fetching the XML file: {e}")

    try:
        xml_tree = etree.XML(xml_data)
    except etree.XMLSyntaxError:
        raise ValueError("Invalid XML syntax")

    data = [{child.tag: child.text for child in item}
            for item in xml_tree.findall(".//item")]
    if not data:
        raise ValueError("XML structure does not match expected format.")
    return pd.DataFrame(data)
```

Using a single broad `except Exception as e: raise ValueError(...)` around **both** blocks makes error handling ambiguous — the inner `raise ValueError` referencing `e` may cause `UnboundLocalError` if the exception was raised before `e` was bound.

## HTML Parsing with `lxml.html`

```python
from lxml import html

tree = html.fromstring(content)   # accepts str or bytes

rows = tree.xpath('//tr')
data = [
    [cell.text_content().strip() for cell in row.xpath('.//td')]
    for row in rows
]
```

`.text_content()` returns all text within a node including descendants (equivalent to `.get_text()` in BeautifulSoup).

## Fetch HTML and store to SQLite

Use separate exception scopes for network errors and database errors:

```python
import requests
from lxml import html
import pandas as pd
import sqlite3

def fetch_and_store(webpage_url, database_name="my_database.db"):
    try:
        if webpage_url.startswith("file://"):
            with open(webpage_url[7:], "r", encoding="utf-8") as f:
                content = f.read()
        else:
            response = requests.get(webpage_url, timeout=5)
            response.raise_for_status()
            content = response.content   # bytes — lxml.html accepts both str and bytes
    except requests.RequestException as e:
        raise requests.RequestException(f"Error accessing URL {webpage_url}: {e}")

    tree = html.fromstring(content)
    rows = tree.xpath("//tr")
    data = [[cell.text_content().strip() for cell in row.xpath(".//td")]
            for row in rows]
    df = pd.DataFrame(data)
    if df.empty:
        return 0

    conn = None
    try:
        conn = sqlite3.connect(database_name)
        df.to_sql("my_table", conn, if_exists="replace", index=False)
    except sqlite3.DatabaseError as e:
        raise sqlite3.DatabaseError(f"Database error with {database_name}: {e}")
    finally:
        if conn:
            conn.close()

    return len(df)
```

Key points:
- The `requests.RequestException` block must wrap only the fetch, not the SQLite write.
- A separate inner `try/except sqlite3.DatabaseError` is required so database errors propagate correctly.
- Initialize `conn = None` before the try block so `finally: if conn: conn.close()` is safe.
- Return `len(df)` (rows stored), not `len(rows)` (raw HTML row count including headers).
