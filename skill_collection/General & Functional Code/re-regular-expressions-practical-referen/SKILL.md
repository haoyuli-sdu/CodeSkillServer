---
name: re-regular-expressions-practical-referen
description: Practical guide to re API semantics, findall/sub/match anchoring, case handling, operation ordering, and common text-processing recipes.
---

# Python `re` — Regular Expressions Practical Reference

## Core Function Semantics

### Match anchoring: `re.match` vs `re.search` vs `re.fullmatch`

```python
import re

text = "error: disk full at line 42"
re.match(r'\w+', text)          # 'error'    — anchored at string START
re.search(r'\d+', text)         # '42'       — scans full string
re.fullmatch(r'\w+', text)      # None       — entire string must match pattern
```

For filename-matching against a pattern, `re.match` is natural (filenames start from the beginning):
```python
for filename in os.listdir(directory):
    if re.match(pattern, filename):
        ...
```

### `re.findall` and capturing groups

```python
text = "score: 80, score: 95"
re.findall(r'\d+', text)                     # ['80', '95']  — no groups → full match
re.findall(r'score: (\d+)', text)            # ['80', '95']  — one group → group content
re.findall(r'(score): (\d+)', text)          # [('score', '80'), ('score', '95')]  — multiple groups → tuples
```

When the pattern has a single capturing group, `findall` returns that group's content, not the full match.

### `re.sub` — transformations

```python
# Remove URLs:
clean = re.sub(r'https?://\S+', '', text)

# Remove all non-alphanumeric characters (keeps spaces):
clean = re.sub(r'[^A-Za-z0-9\s]', '', text)

# Remove all non-alphabetic characters (keeps no spaces):
alpha_only = re.sub(r'[^A-Za-z]', '', text)

# Normalize whitespace:
normalized = re.sub(r'\s+', ' ', text).strip()

# Compiled pattern behaves identically to re.sub:
NONWORD = re.compile(r'[\W_]+')
NONWORD.sub(' ', text)   # replaces each non-word run with a space
```

**Operation order matters when steps interact:** `string.punctuation` includes `_` (underscore). If underscores are used as substitutes for whitespace characters, remove punctuation *first* (before introducing underscores), then replace whitespace with the desired placeholders:

```python
import string
# Remove punctuation first (while spaces/tabs/newlines are still original chars)
text = re.sub(f'[{re.escape(string.punctuation)}]', '', text)
# Then replace whitespace characters individually
text = text.replace(' ', '_').replace('\t', '__').replace('\n', '___')
```

A single `re.sub(r'\s+', ...)` collapses all whitespace together, losing the per-character distinctions.

### `re.split`

```python
# Delimiter discarded:
re.split(r'\s+', 'hello  world')      # ['hello', 'world']

# Delimiter retained (capturing group):
re.split(r'(/)', 'a/b/c')             # ['a', '/', 'b', '/', 'c']

# Empty-string edge cases:
re.split(r'\s+', '')           # ['']    — not []
re.split(r'\s+', '  hello')   # ['', 'hello']  — leading empty string
```

**`re.split(r'\W+', text)` keeps digits** — `\W` means non-word character, and digits ARE word characters.

## Common Recipes

### Word tokenization

```python
# Split into alphabetic words only (drops digits and punctuation):
words = re.findall(r'[A-Za-z]+', text)

# Split into word-character runs (keeps digits — \w = [A-Za-z0-9_]):
tokens = re.findall(r'\b\w+\b', text)

# Words except the last (to stem/process all but final word):
all_words = re.findall(r'\b\w+\b', sentence)
words_to_process = all_words[:-1]   # all except last
```

### Case-sensitive vs case-insensitive counting

When counting or filtering, follow what the task specifies:
```python
# Task says lowercase before counting:
words = re.findall(r'[A-Za-z]+', text.lower())
freq = Counter(words)

# Task says preserve original casing:
words = re.findall(r'[A-Za-z]+', text)   # no .lower()
freq = Counter(words)

# Filter stopwords by lowercase comparison while keeping original case:
filtered = [w for w in words if w.lower() not in STOPWORDS]
```

### Greedy match for last delimiter

`re.search(r'^(.*)-', s)` uses a greedy `.*` that backtracks to the **last** `-`:

```python
re.search(r'^(.*)-', 'archive-2024-01.zip').group(1)   # 'archive-2024'  (before last hyphen)
```

To split on the **last** occurrence of a character and get prefix + suffix:
```python
filename = 'archive-2024-01.zip'
prefix = re.search(r'^(.*)-', filename).group(1)   # 'archive-2024'
```

### Adjacent-pair extraction (n-grams)

Use `zip` on the sanitized string rather than lookahead:
```python
sanitized = re.sub(r'[^A-Za-z]', '', word)
pairs = [sanitized[i:i+2] for i in range(len(sanitized) - 1)]
# or equivalently:
pairs = [''.join(p) for p in zip(sanitized, sanitized[1:])]
```

### Replace values before aggregating

When both replacement and frequency counting are needed, replace first so the counter sees the final values:
```python
for key, value in data.items():
    if isinstance(value, str) and re.search(r'[^@]+@[^@]+\.[^@]+', value):
        value = 'REDACTED'
    processed[key] = value
counts = Counter(processed.values())
```

### File-matching and renaming

```python
def rename_by_pattern(directory, pattern, replacement):
    for filename in os.listdir(directory):
        if re.search(pattern, filename):
            new_name = re.sub(pattern, replacement, filename)
            os.rename(
                os.path.join(directory, filename),
                os.path.join(directory, new_name)
            )
```

## Match Object

```python
m = re.search(r'(\d{4})-(\d{2})-(\d{2})', log_line)
if m:
    year, month, day = m.group(1), m.group(2), m.group(3)
    # or: year, month, day = m.groups()
```

Always check for `None` before calling `.group()`.

## Flags

```python
re.IGNORECASE   # (re.I) case-insensitive
re.MULTILINE    # (re.M) ^ and $ match per-line
re.DOTALL       # (re.S) . matches newlines

re.findall(r'^\w+', "foo\nbar", re.MULTILINE)  # ['foo', 'bar']
```

## Quick Reference

| Function | Anchoring | Returns |
|---|---|---|
| `re.match(p, s)` | start of string | Match object or None |
| `re.search(p, s)` | anywhere | Match object or None |
| `re.fullmatch(p, s)` | entire string | Match object or None |
| `re.findall(p, s)` | all | list of strings (or tuples if multiple groups) |
| `re.sub(p, r, s)` | all matches | new string |
| `re.split(p, s)` | all matches | list of segments |

## Pitfalls

**Importing `string` when using `string.punctuation`:** `string` is not auto-imported with `re`. Always add `import string` explicitly.

**`re.escape(word)` is needed** when the word may contain regex metacharacters:
```python
pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
```

**Back-references in replacements:** use raw strings — `r'\1'` not `'\\1'`.

**`re.split` on empty/whitespace-prefixed strings** produces leading empty strings; filter if needed:
```python
parts = [p for p in re.split(r'\s+', text) if p]
```
