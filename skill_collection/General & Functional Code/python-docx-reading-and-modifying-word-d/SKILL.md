---
name: python-docx-reading-and-modifying-word-d
description: 'Guide for python-docx: loading documents, paragraph text modification with regex lookbehind, extracting text, and multi-format file conversion including .docx.'
---

# python-docx — Reading and Modifying Word Documents

## Loading and reading documents

```python
from docx import Document

doc = Document("report.docx")

# Paragraphs — the main text blocks
for para in doc.paragraphs:
    print(para.text)   # plain text string of the paragraph

# Tables (separate from paragraphs)
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text)
```

## Modifying paragraph text — regex with lookbehind

Assigning to `paragraph.text` replaces the entire paragraph's content with a single new run:

```python
import re
from docx import Document

doc = Document("input.docx")
for para in doc.paragraphs:
    # Only replace " not already preceded by backslash
    para.text = re.sub(r'(?<!\\)"', r'\"', para.text)
doc.save("input.docx")   # overwrite in place
```

The pattern `r'(?<!\\)"'` uses a negative lookbehind to skip already-protected quotes. Using a plain `r'"'` pattern double-protects existing `\"` into `\\"`, which is wrong.

## Extracting text lines from .docx

```python
from docx import Document

def read_docx_lines(path):
    doc = Document(path)
    return [p.text for p in doc.paragraphs]
```

Use this to extract text for storage in a pandas DataFrame or CSV.

## Converting mixed file types to CSV (including .docx)

Check that the source directory exists before creating the target directory. Walk the source tree, read each supported format, and write a single-column CSV:

```python
import os
from pathlib import Path
import pandas as pd
import docx

def convert_files(source_dir, target_dir):
    if not os.path.exists(source_dir):
        raise FileNotFoundError("source_directory must exist.")
    os.makedirs(target_dir, exist_ok=True)
    count = 0
    for root, _, files in os.walk(source_dir):
        for fname in files:
            ext = Path(fname).suffix
            src = os.path.join(root, fname)
            dst = os.path.join(target_dir, Path(fname).stem + ".csv")
            if ext == ".docx":
                doc = docx.Document(src)
                lines = [p.text for p in doc.paragraphs]
                pd.DataFrame({"Text": lines}).to_csv(dst, index=False)
            elif ext == ".txt":
                with open(src) as f:
                    lines = f.readlines()
                pd.DataFrame({"Text": lines}).to_csv(dst, index=False)
            elif ext == ".xlsx":
                pd.read_excel(src, engine="openpyxl").to_csv(dst, index=False)
            elif ext == ".csv":
                pd.read_csv(src).to_csv(dst, index=False)
            else:
                continue
            count += 1
    return count
```

`to_csv(dst, index=False)` omits the integer row index.

## Common pitfalls

- `docx.Document` is the constructor — do **not** use `docx.open()`.
- `paragraph.text` is readable and writable, but assigning replaces all runs with a single plain-text run (formatting is lost). For formatting-preserving edits, modify `run.text` on individual runs.
- Tables are **not** part of `doc.paragraphs` — access them via `doc.tables`.
- Call `doc.save(path)` after all modifications to write changes to disk.
