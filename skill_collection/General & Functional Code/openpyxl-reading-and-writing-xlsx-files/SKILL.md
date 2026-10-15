---
name: openpyxl-reading-and-writing-xlsx-files
description: 'Guide for openpyxl API: loading workbooks, iterating cells, directory processing, and Excel-to-CSV conversion. Key pitfall: join dir+filename before passing to load_workbook.'
---

# openpyxl — Reading and Writing .xlsx Files

openpyxl handles `.xlsx` / `.xlsm` / `.xltx` / `.xltm` formats only. It raises `InvalidFileException` for `.xls` (old binary format) and other non-zip files.

## Loading and saving workbooks

```python
from openpyxl import load_workbook, Workbook

# Load existing .xlsx (read/write)
wb = load_workbook(filename="report.xlsx")
ws = wb.active   # active sheet

# Load read-only (faster for large files)
wb = load_workbook(filename="large.xlsx", read_only=True)

# Create new workbook
wb = Workbook()
ws = wb.active
ws.title = "Summary"
wb.save("output.xlsx")
```

## Iterating cells

```python
# iter_rows() returns Row objects containing Cell objects
for row in ws.iter_rows():
    for cell in row:
        if isinstance(cell.value, str):
            cell.value = cell.value.upper()

# values_only=True — raw values as tuples (no Cell objects, faster)
for row in ws.iter_rows(values_only=True):
    print(row)   # tuple of values; None for empty cells
```

## Processing all .xlsx files in a directory

When a function must operate on all `.xlsx` files in a directory, raise `FileNotFoundError` for a non-existent directory rather than silently returning 0:

```python
import os, glob
from openpyxl import load_workbook

def process_xlsx_dir(directory_path):
    if not os.path.isdir(directory_path):
        raise FileNotFoundError("The specified directory does not exist.")
    files = glob.glob(os.path.join(directory_path, "*.xlsx"))
    for path in files:
        wb = load_workbook(path)
        for sheet_name in wb.sheetnames:
            for row in wb[sheet_name].iter_rows():
                for cell in row:
                    if isinstance(cell.value, str):
                        cell.value = cell.value.replace('"', '\\"')
        wb.save(path)
    return len(files)
```

Use `os.path.isdir()` (not `os.path.exists()`) and `raise FileNotFoundError` — the function must distinguish a missing directory from an empty one.

## Converting an Excel file to CSV

When the task receives a directory and a filename separately, join them first before passing to `load_workbook`:

```python
import os, csv
from openpyxl import load_workbook

def excel_to_csv(file_name, excel_dir, csv_dir):
    excel_path = os.path.join(excel_dir, file_name)   # join dir + filename first
    if not os.path.isfile(excel_path):
        raise FileNotFoundError(f"[Errno 2] No such file or directory: '{excel_path}'")

    wb = load_workbook(filename=excel_path, read_only=True)
    ws = wb.active
    data = [[cell.value for cell in row] for row in ws.iter_rows()]

    csv_name = os.path.splitext(file_name)[0] + ".csv"
    csv_path = os.path.join(csv_dir, csv_name)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(data)
    return csv_name   # return just the filename, not the full path
```

A common mistake is checking or passing `excel_dir` (the directory) to `load_workbook` without joining `file_name` — this passes a directory string which is not a valid workbook file.

## Key facts

- `wb.sheetnames` — list of sheet name strings; `wb.active` — the active `Worksheet` object.
- Cell values may be `None` for empty cells; guard string operations with `isinstance(cell.value, str)`.
- `wb.save(path)` overwrites in place; call after all modifications.
- openpyxl **cannot** read `.xls` — the format check happens before any data is read.
