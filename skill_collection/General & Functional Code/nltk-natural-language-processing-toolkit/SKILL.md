---
name: nltk-natural-language-processing-toolkit
description: Practical reference for NLTK tokenizers, stopwords, POS tagging, stemming, and FreqDist with API selection guidance and common pitfalls.
---

# NLTK — Natural Language Processing Toolkit

## Essential Downloads

Only download what is actually needed. Over-downloading causes unnecessary overhead:

```python
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')        # required in NLTK >= 3.8 for word_tokenize
nltk.download('stopwords')        # for nltk.corpus.stopwords
nltk.download('averaged_perceptron_tagger')  # for nltk.pos_tag
nltk.download('wordnet')          # for WordNetLemmatizer
nltk.download('words')            # for nltk.corpus.words (English word list)
```

## Tokenizer Selection

The right tokenizer depends on the splitting semantics required:

```python
from nltk.tokenize import word_tokenize, RegexpTokenizer
import nltk

# word_tokenize: splits on whitespace AND punctuation
# "It's fine." → ["It", "'s", "fine", "."]
# "$hello world" → ["$", "hello", "world"]  — $ is separated!
tokens = word_tokenize("Hello, world!")  # ['Hello', ',', 'world', '!']
# Requires: punkt + punkt_tab

# WhitespaceTokenizer: splits ONLY on whitespace (keeps $ attached to word)
tk = nltk.WhitespaceTokenizer()
tk.tokenize("$hello $test!")  # ['$hello', '$test!']   punctuation STAYS attached

# RegexpTokenizer: defines what to MATCH as tokens
# Use when you need a custom token shape (no downloads needed)
tok = RegexpTokenizer(r'\$\w+')          # '$word' or '$123'; rejects '$$$' (no \w after $)
tok.tokenize("$hello $123 $!$")          # ['$hello', '$123']  — '$!$' excluded

# Pattern for multi-dollar prefixes ("$$", "$$$word") plus normal "$word":
tok2 = RegexpTokenizer(r'\$\$+\w*|\$\w+')
tok2.tokenize("$$ $$word $abc $!$")      # ['$$', '$$word', '$abc']

# text.split() avoids all punkt downloads and keeps special chars attached
```

**Key pitfall**: `word_tokenize` splits `"$hello"` into `["$", "hello"]` — use `WhitespaceTokenizer`
or `RegexpTokenizer` when you need `$`-prefixed words to stay intact.

## Stopwords and Case Sensitivity

The stopwords set is all-lowercase. Word casing in the output depends on the input text, not the filter:

```python
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))  # all lowercase: 'the', 'is', 'a', ...

# Preserve ORIGINAL case in output (case-sensitive Counter keys):
words = re.findall(r'\b\w+\b', text)                         # original case
filtered = [w for w in words if w.lower() not in stop_words] # compare in lowercase
return dict(Counter(filtered))                               # "Word" ≠ "word" as keys

# Normalize to LOWERCASE output:
words = re.findall(r'\b\w+\b', text.lower())                 # lowercase from the start
filtered = [w for w in words if w not in stop_words]
return dict(Counter(filtered))
```

**Common mistake**: calling `.lower()` on the text before extracting words when the task requires
preserving original casing in the result dictionary.

## Splitting vs Stopword Filtering

Tasks that specify "split on whitespace, remove stopwords" use the STOPWORDS constant directly
(which is typically a pre-built set from the code prompt), without lowercasing the tokens:

```python
# Task provides STOPWORDS constant (already built) — compare directly
STOPWORDS = set(stopwords.words('english'))

words = re.split(r'\W+', text)
words = [w for w in words if w and w not in STOPWORDS]  # case-sensitive match

# vs. tasks that require lowercase normalization before comparing
words = re.split(r'\W+', text.lower())
words = [w for w in words if w and w not in STOPWORDS]
```

## Word Splitting Patterns and Their Differences

These patterns split differently for text like `"python3.5 test"`:

```python
re.split(r'\W+', "python3.5")      # → ['python3', '5']   (dot is \W, splits on it)
re.sub('[^\w\s]', '', "python3.5") # → 'python35'          (dot removed, digits glued)
re.sub('[^\sa-zA-Z0-9]', '', ...) # same as above
re.findall(r'\b\w+\b', "python3.5") # → ['python3', '5']  (word boundaries, like split)
```

Choose the pattern that matches what the task specifies for handling mixed alphanumeric tokens.

## POS Tagging

`nltk.pos_tag` accepts a list of word strings directly — no extra tokenization required:

```python
import nltk
from collections import Counter

# Pass a pre-split list — .split() works without punkt
words = content.split()[:-1]      # drop last word, then tag
pos_tags = nltk.pos_tag(words)    # [('The', 'DT'), ('fox', 'NN'), ...]

pos_counts = Counter(tag for _, tag in pos_tags)
return dict(pos_counts)
```

`pos_tag` requires `averaged_perceptron_tagger`; it does NOT call `word_tokenize` internally.

## Stemming

```python
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()   # rule-based — no download required
stemmer.stem("running")     # 'run'
stemmer.stem("studies")     # 'studi'

# Stem all but the last word:
words = content.split(' ')[:-1]   # split on literal space, keep last word
words = [w.strip(string.punctuation).lower() for w in re.split(r'\W+', ' '.join(words))]
stemmed = [stemmer.stem(w) for w in words]
return dict(Counter(stemmed))
```

## FreqDist

```python
import nltk

freq = nltk.FreqDist(["apple", "banana", "apple"])
# freq["apple"] → 2; freq.most_common(5) → [(word, count), ...]
# FreqDist is NOT a plain dict — convert: dict(freq)

df = pd.DataFrame(list(freq.items()), columns=["Word", "Frequency"])

# Plot: pass show=False to suppress display
ax = freq.plot(10, cumulative=False, show=False)
```

## Deduplication Patterns

```python
# "remove duplicate words" — keep one occurrence of each word (preserving first-occurrence order):
text = "the cat sat sat on on the mat"
unique_words = sorted(set(text.split()), key=text.split().index)  # → ['the', 'cat', 'sat', 'on', 'mat']

# "remove duplicate CONSECUTIVE words" ("hello hello world" → "hello world"):
import re
text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text)
```

## N-gram Generation

```python
from collections import Counter
from nltk import ngrams

# After filtering stopwords and removing duplicates (using Counter, not set):
words_list = [w.lower() for w in text.split() if w.lower() not in STOPWORDS]

# N-grams via zip (no downloads):
bigrams = list(zip(words_list, words_list[1:]))

# N-grams via nltk.ngrams:
bigram_counts = Counter(ngrams(words_list, 2))
return dict(bigram_counts)
```

## English Words Corpus

```python
from nltk.corpus import words

ENGLISH_WORDS = set(words.words())   # ~236K words, all lowercase
# Always compare after lowercasing:
english = [w for w in re.findall(r'\b\w+\b', s.lower()) if w in ENGLISH_WORDS]
# Note: use the list (not a set) if frequency/order matters downstream
```

## Tokenize File Line by Line

```python
import os
from nltk import word_tokenize

if not os.path.isfile(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")
tokens = []
with open(file_path, 'r') as f:
    for line in f:
        tokens.extend(word_tokenize(line))
return tokens
```

## Common Pitfalls

- `word_tokenize` needs both `punkt` AND `punkt_tab` (NLTK >= 3.8) — omitting `punkt_tab` raises `LookupError`
- `word_tokenize("$hello")` → `['$', 'hello']` — use `WhitespaceTokenizer` or `RegexpTokenizer` for `$`-prefixed tokens
- Stopwords set is lowercase — compare `word.lower() not in stop_words`, but output the original-case word unless lowercase is explicitly required
- `FreqDist` is not a plain dict — use `list(freq.items())` or `dict(freq)` to convert
- `re.split(r'\W+', text)` treats digits-adjacent-to-dots as separate tokens ("`3.5`" → `['3', '5']`); `re.sub` approach removes the delimiter instead
- `RegexpTokenizer(r'\$\w+')` rejects `'$$$'` (no `\w` characters follow); use `r'\$\$+\w*|\$\w+'` to also match bare `$$`
