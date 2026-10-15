---
name: textblob-simplified-text-processing
description: 'Guide for textblob: ngrams with Counter, sentiment named tuple, duplicate removal + stopwords pattern, NLTK corpora.'
---

# TextBlob — Simplified Text Processing

## N-grams

```python
from textblob import TextBlob
from collections import Counter

text = "the quick brown fox jumps over the lazy dog"
blob = TextBlob(text.lower())   # lowercase before analysis for consistent counting

# blob.ngrams(n) returns a list of WordList objects
bigrams = blob.ngrams(n=2)
# [WordList(['the', 'quick']), WordList(['quick', 'brown']), ...]

# Convert to strings and count frequency
ngram_strs = [' '.join(list(gram)) for gram in blob.ngrams(n=n)]
freq = Counter(ngram_strs)
top_k = freq.most_common(k)   # [('the quick', 2), ...]
```

## Visualizing Top N-grams

```python
import pandas as pd, seaborn as sns
from textblob import TextBlob
from collections import Counter

def plot_top_ngrams(text, n=2, top_k=10):
    blob = TextBlob(text.lower())
    freq = Counter([' '.join(list(g)) for g in blob.ngrams(n=n)])
    top = freq.most_common(top_k)
    df = pd.DataFrame(top, columns=['n-gram', 'Frequency'])
    return sns.barplot(x='n-gram', y='Frequency', data=df)
    # Returns Axes object
```

## Sentiment Analysis

```python
from textblob import TextBlob

blob = TextBlob("This is absolutely wonderful!")
blob.sentiment              # Sentiment(polarity=0.6, subjectivity=1.0)
blob.sentiment.polarity     # float in [-1.0, 1.0]  (negative ↔ positive)
blob.sentiment.subjectivity # float in [0.0, 1.0]  (objective ↔ subjective)
```

`blob.sentiment` is a named tuple — returning it directly satisfies "return a tuple."

## Text Cleaning + Sentiment

Canonical pattern: remove consecutive duplicate words, strip stopwords, then analyze:

```python
import re
from textblob import TextBlob
from nltk.corpus import stopwords

STOPWORDS = set(stopwords.words('english'))

def clean_and_analyze(text):
    # Remove consecutive duplicate words: "the the fox" → "the fox"
    text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text)
    words = [w for w in re.findall(r'\b\w+\b', text.lower()) if w not in STOPWORDS]
    text = ' '.join(words)
    return TextBlob(text).sentiment
```

## NLTK Corpora

TextBlob depends on NLTK corpora. Download once before use:

```python
import nltk
nltk.download('punkt_tab')                        # tokenization
nltk.download('averaged_perceptron_tagger_eng')   # POS tagging / n-grams
```
