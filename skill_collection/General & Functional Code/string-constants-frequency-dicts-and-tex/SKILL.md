---
name: string-constants-frequency-dicts-and-tex
description: Practical reference for string module constants, full-alphabet frequency dicts, itertools combos, text cleaning patterns, and input validation.
---

# Python `string` Module — Practical Reference

## Key Constants

```python
import string

string.ascii_lowercase   # 'abcdefghijklmnopqrstuvwxyz'  (26 chars)
string.ascii_uppercase   # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
string.ascii_letters     # lowercase + uppercase (52 chars)
string.digits            # '0123456789'
string.hexdigits         # '0123456789abcdefABCDEF'  (22 chars, both cases!)
string.punctuation       # 32 ASCII punctuation characters
string.whitespace        # ' \t\n\r\x0b\x0c'
string.printable         # digits + letters + punctuation + whitespace (100 chars)
```

**Hex caveat**: `string.hexdigits` contains both cases — use `.lower()` when you need only `0-9a-f`:

```python
hex_chars = string.hexdigits.lower()   # '0123456789abcdef'
```

## Alphabet Position Lookup

`string.ascii_lowercase` is a plain string; use `.index()` for 1-based positions:

```python
alphabet = string.ascii_lowercase
alphabet.index('a') + 1   # 1
alphabet.index('z') + 1   # 26
```

## Full 26-Letter Frequency Dicts (all zeros for missing letters)

When the task asks for the frequency of **every** letter in the alphabet (including letters
with zero count), initialize from `ascii_lowercase` first:

```python
from collections import Counter
import string

counts = Counter(text.lower())
# Build a dict for all 26 letters, filling missing with 0:
result = {letter: counts.get(letter, 0) for letter in string.ascii_lowercase}
```

`Counter(text)` alone only includes characters that appear — it omits letters with zero
count, which causes assertion failures when tests compare against a 26-key dict.

## itertools Combinations and Product Over Letters

When generating all N-letter sequences (with repetition), `itertools.product` is the
canonical choice. When building a dict with string keys, join each tuple with `''.join()`:

```python
import itertools, string

LETTERS = list(string.ascii_lowercase)

# All 3-letter sequences (26^3 = 17,576 rows)
combos = list(itertools.product(LETTERS, repeat=3))

# As a DataFrame with individual letter columns:
df = pd.DataFrame(combos, columns=["Letter 1", "Letter 2", "Letter 3"])

# As a dict with string keys ('aaa', 'aab', ...):
combo_dict = {''.join(c): 0 for c in combos}
```

Each tuple `('a', 'b', 'c')` becomes one DataFrame row, OR join the letters to build
a string key — but not both. Leaving tuples as dict keys causes `KeyError` on string lookups.

## Adjacent-Pair Extraction

The idiom for overlapping pairs in a string or word:

```python
word = "hello"
pairs = [''.join(x) for x in zip(word, word[1:])]
# ['he', 'el', 'll', 'lo']
```

This can be combined with `random.choice(pairs)` to sample adjacent pairs.

## Generating Random Strings

```python
import random, string

# One character at a time
''.join(random.choice(string.ascii_uppercase) for _ in range(5))

# Prefix + random suffix pattern (department codes, employee IDs)
for prefix, count in dept_dict.items():
    for _ in range(count):
        suffix = ''.join(random.choice(string.ascii_uppercase) for _ in range(5))
        result.append(f'{prefix}{suffix}')
```

## string.punctuation for Text Cleaning

```python
import re, string

# Remove punctuation from text (preserving spaces)
clean = re.sub(f'[{re.escape(string.punctuation)}]', '', text)

# Strip punctuation from each token:
words = text.split()
cleaned = [w.strip(string.punctuation).lower() for w in words if w.strip(string.punctuation)]
```

## Predicate Maps for String Evaluation

When evaluating a string against named predicates and raising `KeyError` for invalid ones:

```python
predicate_functions = {
    "has_uppercase": lambda x: any(c.isupper() for c in x),
    "has_lowercase": lambda x: any(c.islower() for c in x),
    "has_special_chars": lambda x: any(c in string.punctuation for c in x),
    "has_numbers": lambda x: any(c.isdigit() for c in x),
}
if any(p not in predicate_functions for p in predicates):
    raise KeyError("Invalid predicate provided.")
result = {p: predicate_functions[p](generated_string) for p in predicates}
```

## Input Validation for Alphabetic Words

When validating a word for "must be lowercase alphabetic":

```python
# Check empty before checking isalpha/islower
if not word:
    return pd.DataFrame({'Letter': [], 'Position': []})
elif not word.isalpha() or not word.islower():
    raise ValueError("Input word must be in lowercase alphabetic characters only.")
```

Check empty first — `''.isalpha()` returns `False` and would trigger the error path when
the task expects an empty result for empty input.
