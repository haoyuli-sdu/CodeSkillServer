---
name: xlwt-writing-legacy-xls-excel-files
description: 'Guide for xlwt API: direct workbook creation, CSV-to-xls, dict records, and DataFrame iteration. Key pitfall: never use df.to_excel(engine=''xlwt'').'
---

# xlwt — Writing Legacy .xls Excel Files

xlwt writes legacy `.xls` (Excel 97–2003) files. It is **write-only** — to read `.xls`, use `xlrd`. It does not support `.xlsx`. Do **not** use `df.to_excel(engine='xlwt')` — the xlwt engine is not registered in modern pandas and raises `ValueError: No engine for filetype: 'xls'`. Always create the workbook directly with `xlwt.Workbook()`.

## Core write workflow

```python
import xlwt, os

book = xlwt.Workbook()
sheet = book.add_sheet("Sheet1")

# write(row_index, col_index, value) — 0-based indices
sheet.write(0, 0, "Name")
sheet.write(0, 1, "Score")
sheet.write(1, 0, "Alice")
sheet.write(1, 1, 95)

book.save("output.xls")
os.path.abspath("output.xls")   # return this when the task asks for absolute path
```

Each `(row, col)` cell may be written **only once** — a second write to the same cell raises `Exception: Attempt to overwrite cell`.

## Writing from CSV content

Iterate the reader directly with `enumerate` — do not call `next()` separately:

```python
import xlwt, csv, io, os

def csv_to_xls(csv_content, filename):
    book = xlwt.Workbook()
    sheet = book.add_sheet("sheet1")
    reader = csv.reader(io.StringIO(csv_content))
    for row_idx, row in enumerate(reader):   # handles empty, single-row, and multi-row CSV
        for col_idx, value in enumerate(row):
            sheet.write(row_idx, col_idx, value)
    book.save(filename)
    return os.path.abspath(filename)
```

Using `next(reader)` to pull out a header row first, then a second `next(reader)` for the data row, causes `StopIteration` when the CSV has zero or one rows.

## Writing structured records (list of dicts)

```python
import xlwt, os

FIELDS = ["ID", "Name", "Score"]

def records_to_xls(records, filename):
    book = xlwt.Workbook()
    sheet = book.add_sheet("Sheet1")

    for col_idx, field in enumerate(FIELDS):
        sheet.write(0, col_idx, field)

    for row_idx, record in enumerate(records, start=1):
        for col_idx, field in enumerate(FIELDS):
            sheet.write(row_idx, col_idx, record.get(field, ""))

    book.save(filename)
    return os.path.abspath(filename)
```

Use `.get(field, "")` to handle missing keys gracefully — `record[field]` raises `KeyError`.

## Writing from a pandas DataFrame (JSON → xls)

```python
import xlwt, pandas as pd, os

def json_to_xls(json_str, filename, sheet_name="sheet1"):
    if not isinstance(json_str, (str, bytes, bytearray)):
        raise TypeError("json_str must be a string, bytes, or bytearray")
    try:
        df = pd.read_json(json_str)
        book = xlwt.Workbook()
        sheet = book.add_sheet(sheet_name)
        if not df.empty:
            for col_idx, col_name in enumerate(df.columns):
                sheet.write(0, col_idx, col_name)
            for row_idx, (_, row) in enumerate(df.iterrows(), start=1):
                for col_idx, value in enumerate(row):
                    sheet.write(row_idx, col_idx, value)
        book.save(filename)
        return os.path.abspath(filename)
    except ValueError as e:
        raise ValueError(f"Invalid JSON string: {e}")
    except Exception as e:
        raise Exception(f"Error in file writing: {e}")
```
