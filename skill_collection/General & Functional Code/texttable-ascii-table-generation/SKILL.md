---
name: texttable-ascii-table-generation
description: 'Correct API usage for Texttable: draw() not render(), add_rows()/add_row() not set_header(), set_deco() for decoration styles.'
---

# texttable — ASCII Table Generation

texttable creates plain-text ASCII tables. The central class is `Texttable`.

## Core API at a Glance

| Operation | Correct method | Non-existent (raises AttributeError) |
|---|---|---|
| Render the table | `table.draw()` | `table.render()` |
| Add all rows at once | `table.add_rows(list_of_lists)` | `table.set_rows()` |
| Add one row | `table.add_row(list)` | `table.set_header()` |
| Set decoration style | `table.set_deco(flag)` | — |

## Building a Table with `add_rows`

`add_rows(rows)` takes a list of lists where **the first sub-list is the header**. Subsequent sub-lists are data rows.

```python
from texttable import Texttable

table = Texttable()
table.add_rows([
    ["Name", "Score", "Grade"],
    ["Alice", 95, "A"],
    ["Bob",   82, "B"],
])
result = table.draw()   # returns a formatted string
```

`draw()` returns the string — it does not print it.

## Adding Rows One at a Time

```python
table = Texttable()
table.add_row(["Item", "Value"])          # first add_row → becomes the header
table.add_row(["CPU Usage (%)", 42.5])
table.add_row(["Memory Usage (%)", 67.1])
result = table.draw()
```

The first `add_row` call establishes the header. Each subsequent call appends a data row.

## Decoration Styles

By default, `Texttable` produces a full box with borders, a header separator, and vertical lines:

```
+-------+-------+
| Name  | Score |
+=======+=======+
| Alice | 95    |
+-------+-------+
```

For a minimal style with only a header underline (no box borders), use `set_deco`:

```python
table = Texttable()
table.set_deco(Texttable.HEADER)   # header underline only, no surrounding box
table.add_rows([
    ["File Name", "Number of Rows", "Number of Columns"],
    ["records.csv", 100, 5],
    ["summary.csv", 40,  3],
])
print(table.draw())
# File Name    Number of Rows  Number of Columns
# ------------------------------------------------
# records.csv  100             5
# summary.csv  40              3
```

Available decoration constants: `Texttable.BORDER=1`, `Texttable.HEADER=2`, `Texttable.VLINES=4`, `Texttable.HLINES=8`. Combine with `|` (e.g., `BORDER | HEADER`). The default is all four combined.

## Building a Summary Table from a Directory of Files

```python
import glob, os, pandas as pd
from texttable import Texttable

def summarize_directory(data_dir):
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Directory '{data_dir}' does not exist.")
    files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))
    if not files:
        raise ValueError("No CSV files found.")

    rows = [["File Name", "Number of Rows", "Number of Columns"]]
    for f in files:
        df = pd.read_csv(f)   # raises pd.errors.EmptyDataError for empty files
        rows.append([os.path.basename(f), df.shape[0], df.shape[1]])

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.add_rows(rows)
    return table.draw()
```

## Column Type Control

By default, texttable auto-detects column types and may format numbers as floats. To force all columns to display as plain text strings:

```python
table.set_cols_dtype(["t", "t", "t"])   # "t" = text for all 3 columns
```

Pass this before `add_rows`. Type codes: `"t"` (text), `"i"` (integer), `"f"` (float), `"e"` (scientific), `"a"` (automatic).
