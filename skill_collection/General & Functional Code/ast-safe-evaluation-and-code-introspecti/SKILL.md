---
name: ast-safe-evaluation-and-code-introspecti
description: 'Guide for ast.literal_eval: error handling, file processing patterns, regex+literal_eval, DataFrame column conversion.'
---

# Python `ast` Module — Safe Evaluation and Code Introspection

## Core Use Case: `ast.literal_eval`

`ast.literal_eval(node_or_string)` safely evaluates a string containing a Python literal or container (dict, list, tuple, set, int, float, str, bytes, bool, None). It raises `ValueError` for syntactically valid non-literals, and `SyntaxError` for malformed syntax.

```python
import ast

s = "{'key': 42, 'values': [1, 2, 3]}"
result = ast.literal_eval(s)   # {'key': 42, 'values': [1, 2, 3]}
```

---

## Error Handling: catch ValueError only, not SyntaxError

When iterating over items that may or may not be string literals, catch only `ValueError` — not both `(ValueError, SyntaxError)`. Some callers assert that `SyntaxError` propagates for malformed input:

```python
for item in data:
    if isinstance(item, str):
        try:
            item = ast.literal_eval(item)
        except ValueError:
            continue   # skip non-literal strings; SyntaxError propagates
    if isinstance(item, dict):
        counter.update(item.keys())
```

---

## Processing Files: line by line vs. whole content

**One dict per line** — evaluate each line separately:

```python
results = []
with open(filepath, 'r') as f:
    for line in f:
        results.append(ast.literal_eval(line.strip()))
```

**One dict per file** — read the whole file:

```python
with open(filepath, 'r') as f:
    result = ast.literal_eval(f.read().strip())
```

When a file contains multiple lines (each a separate literal), passing the concatenated content to `literal_eval` raises `SyntaxError`. Use the line-by-line approach for multi-entry files.

When a directory has no matching files, return an empty list — not a ValueError:

```python
import glob, os, ast

def load_txt_dicts(directory):
    files = glob.glob(os.path.join(directory, '*.txt'))
    results = []
    for file in files:
        with open(file, 'r') as f:
            for line in f:
                results.append(ast.literal_eval(line.strip()))
    return results   # [] if directory is empty or contains no .txt files
```

---

## Regex + `literal_eval` for Extracting Dicts from Free Text

The greedy pattern `r'\{.*?\}'` with `re.DOTALL` can merge adjacent dicts or miss nested braces. Use an alternation that handles one level of nesting:

```python
import re, ast

pattern = re.compile(r"\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]*\}")
matches = pattern.findall(text)
dicts = [ast.literal_eval(m) for m in matches]
```

The alternation tries the nested form first, falling back to the flat form.

---

## DataFrame Column Conversion

Convert a string-serialized dict column to actual dicts, then use string representation for categorical axes (dicts are not hashable):

```python
df["col"] = df["col"].apply(ast.literal_eval)      # each cell becomes a dict

# For seaborn hue or similar — dicts are not hashable, use str representation
df["hue"] = df["col"].apply(str)
ax = sns.pairplot(df, hue="hue")
```

Passing a column of dicts directly as `hue` raises `TypeError: unhashable type: 'dict'`.

---

## `ast.ASTVisitorError` Does Not Exist

There is no `ast.ASTVisitorError` in the Python standard library. Errors from `ast` operations are standard Python exceptions (`ValueError`, `SyntaxError`, `TypeError`).
