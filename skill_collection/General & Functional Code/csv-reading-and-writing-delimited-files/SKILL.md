---
name: csv-reading-and-writing-delimited-files
description: 'Core csv module patterns: reader vs DictReader, writing with writer/DictWriter, in-memory StringIO, and common pitfalls.'
---

# Python `csv` — Reading and Writing Delimited Files

## Core API

| Class/Function | Purpose |
|---|---|
| `csv.reader(f)` | Yield each row as a list of strings (header included) |
| `csv.writer(f)` | Write rows (as lists) to a file |
| `csv.DictReader(f)` | Yield each row as a dict keyed by the header row |
| `csv.DictWriter(f, fieldnames)` | Write dicts as rows; call `writeheader()` first |

## Reading patterns

```python
import csv

# Read all rows — csv.reader yields EVERY row including the first (header)
with open("measurements.csv", "r", newline="") as f:
    reader = csv.reader(f)
    rows = list(reader)   # rows[0] is the header row; rows[1:] are data rows

# Iterate without loading all rows into memory
with open("records.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        if row:           # guard against blank lines
            process(row)
```

Use `DictReader` when you want named column access:
```python
with open("sales.csv", "r") as f:
    reader = csv.DictReader(f)   # header row automatically becomes keys
    for row in reader:
        product = row["product"]
        qty = int(row["quantity"])
```

`DictReader` skips the header automatically — no `next()` call needed. `csv.reader` does not; every row it yields, including the first, is a list of strings.

## Writing patterns

```python
# Write lists — writerows is more efficient than multiple writerow calls
def export_to_csv(records, out_path):
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Score", "Date"])   # header
        writer.writerows(records)                     # data rows
    return out_path

# Write dicts — DictWriter requires fieldnames and writeheader()
with open(out_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["city", "population"])
    writer.writeheader()
    for item in dataset:
        writer.writerow({"city": item.name, "population": item.pop})
```

**`newline=""`** is required when opening CSV files for writing — it lets the `csv` module manage line endings and prevents blank rows on Windows.

## In-memory CSV with StringIO

```python
from io import StringIO
import csv

# Parse a CSV string without writing to disk
text = "col_a,col_b\n10,20\n30,40"
reader = csv.reader(StringIO(text))
rows = list(reader)   # [['col_a','col_b'], ['10','20'], ['30','40']]

# Build a CSV in memory and return as a string
buf = StringIO()
writer = csv.writer(buf)
writer.writerow(["label", "value"])
writer.writerows(data_pairs)
csv_string = buf.getvalue()
```

## Aggregating column data

```python
import csv, collections

def word_frequencies(csv_path):
    counter = collections.Counter()
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            for cell in row:
                counter[cell.strip()] += 1
    return counter
```

The loop above counts every cell — including the header row — because `csv.reader` yields all rows. If the header should be excluded, skip the first row by consuming one iteration before the loop:

```python
    reader = csv.reader(f)
    next(reader)            # discard the header row before processing data
    for row in reader:
        ...
```

## Converting structured data to CSV

When building rows from non-CSV sources (JSON objects, XML nodes, database cursors), flatten each item into a list and use `writerows`:

```python
import xml.etree.ElementTree as ET, csv

root = ET.fromstring(xml_content)
rows = [[elem.tag, elem.text] for elem in root.iter()]
with open(output_path, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(rows)
```

## Generating CSV files and returning paths

```python
import csv, os, random

def generate_sample_csv(output_dir, filename="data.csv", n=100):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "Score"])
        writer.writeheader()
        for _ in range(n):
            writer.writerow({"Name": random.choice(names), "Score": random.randint(0, 100)})
    return file_path   # always return the path, not None
```

## Common pitfalls

- **`writerows` returns `None`**: do not return its result; return the path variable instead.
- **`DictReader` column name mismatch**: accessing a key not in the header returns `None`, not `KeyError`. When the header is uncertain, use positional indexing with `csv.reader`.
- **Empty-row guard**: real CSV files sometimes have trailing newlines that produce `[]` rows. A simple `if row:` check prevents `IndexError` on empty rows.
- **Encoding**: for non-ASCII content (accented characters, CJK), open with `encoding="utf-8"` (or another explicit encoding) and write with the same encoding.
