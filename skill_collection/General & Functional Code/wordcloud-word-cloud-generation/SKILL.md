---
name: wordcloud-word-cloud-generation
description: 'Guide for wordcloud: return type (WordCloud vs Axes), plt.gca() after imshow, URL preprocessing pattern.'
---

# wordcloud — Word Cloud Generation

## Core API

`WordCloud().generate(text)` — takes a plain string, returns the `WordCloud` object.
`plt.imshow(wc)` — renders the cloud onto the current Matplotlib axes.
`plt.gca()` — returns the current `Axes` after rendering.

```python
from wordcloud import WordCloud
import matplotlib.pyplot as plt

wc = WordCloud(width=800, height=400, background_color='white').generate(text)
plt.figure(figsize=(10, 5))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
```

## Return Type Depends on Specification

Two patterns exist — check what the function is supposed to return:

**Return WordCloud object** (spec says "returns WordCloud"):
```python
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def make_wordcloud(text):
    text = re.sub(r"http[s]?://\S+", "", text)
    if not text.strip():
        raise ValueError("No words available to generate a word cloud after removing URLs.")
    wc = WordCloud().generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wc)
    plt.axis("off")
    return wc          # WordCloud object, not Axes
```

**Return Axes object** (spec says "returns matplotlib.axes.Axes"):
```python
import wikipedia
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def wiki_wordcloud(page_title):
    try:
        text = wikipedia.page(page_title).content
    except Exception as e:
        print(f"An error occured: {e}")
        return None
    wc = WordCloud().generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    ax = plt.gca()     # capture Axes after rendering
    return ax          # Axes object, not WordCloud
```

## Constructor Parameters

```python
WordCloud(
    width=800,
    height=400,
    background_color='white',
    max_words=200,
    stopwords=None,       # set of words to exclude (None = built-in stopwords)
    colormap='viridis',
)
```

## Preprocessing

Strip URLs or noise before `.generate()`:

```python
import re
text = re.sub(r"http[s]?://\S+", "", raw_text)
if not text.strip():
    raise ValueError("No words available to generate a word cloud after removing URLs.")
wc = WordCloud().generate(text)
```
