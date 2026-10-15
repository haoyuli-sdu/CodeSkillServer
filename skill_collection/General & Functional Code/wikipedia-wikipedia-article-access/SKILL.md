---
name: wikipedia-wikipedia-article-access
description: 'Guide for wikipedia library: page() returns WikipediaPage, content attribute, broad exception handling for network/disambiguation/page errors, plt.gca() for Axes.'
---

# wikipedia — Wikipedia Article Access

## Fetching Article Content

`wikipedia.page(title)` returns a `WikipediaPage` object. Access full article text via `.content`:

```python
import wikipedia

page = wikipedia.page("Python (programming language)")
text = page.content    # full article text as a string
```

## Error Handling

Two primary exceptions:

- `wikipedia.DisambiguationError`: the title matches multiple articles; `.options` lists alternatives
- `wikipedia.PageError`: no article found for the given title

Network failures and other errors may also occur. For functions that return `None` on any failure, use a broad `except Exception`:

```python
import wikipedia
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def make_wordcloud(page_title):
    try:
        text = wikipedia.page(page_title).content
    except Exception:
        return None

    wordcloud = WordCloud().generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    ax = plt.gca()
    return ax
```

After `plt.figure()` + `plt.imshow()`, call `plt.gca()` to obtain the current `Axes` object. This is the standard way to get an `Axes` reference when using pyplot state-machine functions rather than `fig, ax = plt.subplots()`.

## WikipediaPage Attributes

| Attribute | Returns |
|---|---|
| `.content` | Full article text (string) |
| `.summary` | Opening summary paragraph (string) |
| `.title` | Resolved article title (string) |
| `.url` | Article URL (string) |
| `.links` | List of linked article titles |
| `.images` | List of image URLs |

## Language Selection

```python
wikipedia.set_lang("de")   # switch to German Wikipedia
page = wikipedia.page("Python")
wikipedia.set_lang("en")   # reset to English
```
