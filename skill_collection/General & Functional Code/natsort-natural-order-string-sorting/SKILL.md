---
name: natsort-natural-order-string-sorting
description: 'Guide for natsort: natural vs lexicographic sort, glob+natsort+DataFrame pattern, re.findall returns strings.'
---

# natsort — Natural Order Sorting

## What natsort Does

`natsort` sorts strings containing embedded numbers in human (natural) order rather than
lexicographic order:

```python
import natsort

files = ['report10.txt', 'report2.txt', 'report1.txt']
sorted(files)               # ['report1.txt', 'report10.txt', 'report2.txt'] — lexicographic
natsort.natsorted(files)    # ['report1.txt', 'report2.txt', 'report10.txt'] — natural
```

## Core Pattern: Sort glob Results, Read Files, Build DataFrame

The canonical workflow: glob finds files in arbitrary order, natsort fixes the order,
then each file is read and its data extracted:

```python
import glob, natsort, os, re, pandas as pd

def extract_data(directory, file_pattern='*.txt', regex=r'([0-9]+)'):
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory '{directory}' does not exist.")

    files = natsort.natsorted(glob.glob(os.path.join(directory, file_pattern)))
    if not files:
        raise ValueError(f"No files matching '{file_pattern}' found in '{directory}'.")

    records = []
    for filepath in files:
        with open(filepath, 'r') as f:
            content = f.read()
        # re.findall always returns a list of strings (raw regex matches)
        matches = re.findall(regex, content)
        records.append([os.path.basename(filepath), matches])

    return pd.DataFrame(records, columns=['Filename', 'Numeric Data'])
```

`re.findall(r'([0-9]+)', content)` returns **strings** like `['12', '34']`, not integers.

## natsorted() Signature

```python
natsort.natsorted(iterable, key=None, reverse=False, alg=natsort.ns.DEFAULT)
```

Common options:
- `reverse=True` — descending natural order
- `key=lambda p: os.path.basename(p)` — sort by filename within full paths
- `alg=natsort.ns.IGNORECASE` — case-insensitive sort

## Sorting Other Iterables

```python
import natsort

# Works on any iterable of strings
natsort.natsorted(['v1.2.3', 'v1.10.0', 'v1.9.0'])
# ['v1.2.3', 'v1.9.0', 'v1.10.0']

# Sort in-place analog (returns new list)
result = natsort.natsorted(my_list)
```
