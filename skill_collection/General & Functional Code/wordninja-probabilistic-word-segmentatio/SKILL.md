---
name: wordninja-probabilistic-word-segmentatio
description: 'Guide for wordninja: split function returns list, alphabet indexing pattern, uppercase raises ValueError naturally.'
---

# wordninja — Probabilistic Word Segmentation

## Core Function

`wordninja.split(string)` segments a concatenated string into individual English words:

```python
import wordninja

wordninja.split("ilovepython")    # ['i', 'love', 'python']
wordninja.split("speedoflight")   # ['speed', 'of', 'light']
wordninja.split("helloworld")     # ['hello', 'world']
wordninja.split("python")         # ['python']  — always returns a list
```

Returns a list of lowercase strings. Even single recognized words come back as a list.

## Combining with Alphabet Indexing

A common pattern: map each character to its 1-based position in the alphabet,
then segment the whole word into English sub-words:

```python
import string, wordninja

def analyze(word):
    alphabet = list(string.ascii_lowercase)
    # ALPHABET.index(ch) raises ValueError if ch is not a-z
    # This naturally enforces lowercase input — uppercase raises ValueError automatically
    positions = [(ch, alphabet.index(ch) + 1) for ch in word]
    segments = wordninja.split(word)
    return positions, segments

# analyze("hello") → ([('h',8),('e',5),('l',12),('l',12),('o',15)], ['hello'])
# analyze("Hello") → ValueError: 'H' is not in list
```

The two return values have different lengths: `positions` has one tuple per character;
`segments` has one string per detected word. Return them as a tuple `(positions, segments)`.

## Key Properties

- Input is treated as a single concatenated string — no spaces needed
- Output words are lowercase, regardless of input case
- Unrecognized sequences are returned as single-character tokens
- `wordninja.split("")` returns `[]`
