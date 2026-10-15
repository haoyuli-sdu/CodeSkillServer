---
name: levenshtein-fast-edit-distance-computati
description: 'Guide for Levenshtein: distance/ratio/jaro functions, combining with cosine similarity, import conventions.'
---

# Levenshtein — Fast Edit Distance Computation

## Core Functions

```python
import Levenshtein

# Edit distance (int): minimum single-char insertions/deletions/substitutions
Levenshtein.distance("kitten", "sitting")   # 3

# Similarity ratio (float [0.0, 1.0]): 2*M / T — same formula as difflib.SequenceMatcher
Levenshtein.ratio("hello", "helo")   # 0.888...
Levenshtein.ratio("abc", "abc")      # 1.0

# Jaro similarity
Levenshtein.jaro("martha", "marhta")          # 0.944...
# Jaro-Winkler (prefix-boosted)
Levenshtein.jaro_winkler("martha", "marhta")  # 0.961...
```

## Combining with Cosine Similarity

A standard text-analysis pattern: compute cosine similarity on term-frequency vectors
and Levenshtein ratio on cleaned strings, return as a `(cosine, levenshtein)` tuple:

```python
import re, numpy as np
from collections import Counter
from Levenshtein import ratio

ALPHANUMERIC = re.compile(r'[\W_]+')

def text_similarity(text1, text2):
    # Normalize: strip non-alphanumeric, lowercase
    t1 = ALPHANUMERIC.sub(' ', text1).lower()
    t2 = ALPHANUMERIC.sub(' ', text2).lower()

    # Term frequency vectors
    vec1 = Counter(t1.split())
    vec2 = Counter(t2.split())

    # Cosine similarity
    common = set(vec1) & set(vec2)
    numerator = sum(vec1[w] * vec2[w] for w in common)
    denom = np.sqrt(sum(v**2 for v in vec1.values())) * np.sqrt(sum(v**2 for v in vec2.values()))
    cosine = float(numerator) / denom if denom else 0.0

    # Levenshtein ratio on the same cleaned strings
    lev = ratio(t1, t2)

    return cosine, lev
```

## Floating-Point Note

`Levenshtein.ratio` always returns a Python `float`. Cosine computed via `numpy`
operations may return `np.float64`; wrap with `float(...)` if the task expects a
plain Python float.

## Import Variants

```python
import Levenshtein                   # module-level, then Levenshtein.distance(...)
from Levenshtein import distance, ratio, jaro, jaro_winkler
```

`python-Levenshtein` (PyPI package) installs as `Levenshtein` — use `import Levenshtein`
(capital L), not `import levenshtein`.
