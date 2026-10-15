---
name: mechanize-programmatic-browser-interacti
description: 'Guide for mechanize browser automation: reading response from br.open() return value, form selection with nr=, link extraction with BeautifulSoup.'
---

# mechanize — Programmatic Browser Interaction

## Opening a URL

`br.open(url)` returns a response object. Read the HTML from that return value directly:

```python
import mechanize

br = mechanize.Browser()
response = br.open(url)
html = response.read()   # read from the return value of br.open()
```

`br.response()` is a separate accessor for the most-recently stored response. In environments where `br.open()` is intercepted or mocked, `br.response()` may not return a valid object even though `br.open()` does. Reading from the return value of `br.open()` is the reliable approach.

## Extracting Links

```python
import mechanize
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_links(url):
    br = mechanize.Browser()
    response = br.open(url)
    soup = BeautifulSoup(response.read(), 'html.parser')
    return [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
```

`urljoin(base, href)` handles relative hrefs correctly — relative paths are resolved against `base`, while absolute hrefs pass through unchanged.

## Form Selection and Submission

`br.select_form(nr=N)` selects the N-th form (0-indexed). Raises `mechanize.FormNotFoundError` if the index is out of range. After selecting, assign field values with `br[key] = value`, then call `br.submit()`:

```python
import mechanize
from bs4 import BeautifulSoup

def submit_and_get_title(url, form_index, data):
    br = mechanize.Browser()
    br.open(url)
    br.select_form(nr=form_index)   # FormNotFoundError if index invalid
    for key, value in data.items():
        br[key] = value
    response = br.submit()
    soup = BeautifulSoup(response.read(), 'html.parser')
    return soup.title.string if soup.title else 'No Title'
```

Let `FormNotFoundError` propagate naturally — avoid catching it and returning a fallback, because callers typically need to observe the exception.

## Exception Handling

Avoid wrapping `br.open()` in a broad try/except unless the task explicitly requires it. Catching and re-raising as a different exception type (e.g., `raise Exception(str(e))`) changes the exception class and may break code that inspects the exception type.

## Key Behavioral Notes

- `br.set_handle_robots(False)` disables robots.txt enforcement — sometimes needed but not always.
- Form field access: use `br[key] = value` (subscript), not `br.form[key]`.
- `soup.title.string` returns the text content of the `<title>` tag; guard with `if soup.title` when the page may lack a title.
