---
name: prettytable-formatted-ascii-table-output
description: 'Guide for prettytable API usage: creating tables, adding rows, sorting, and returning PrettyTable objects vs strings.'
---

## prettytable — Practical Reference

PrettyTable creates formatted ASCII tables that can be printed or returned as strings.

### Basic usage

```python
from prettytable import PrettyTable

table = PrettyTable()
table.field_names = ["Name", "Age", "City"]
table.add_row(["Alice", 30, "Boston"])
table.add_row(["Bob", 25, "Chicago"])

print(table)          # prints the table
str(table)            # same as table.get_string()
table.get_string()    # returns the string representation
```

### Creating a table from a dictionary

```python
from prettytable import PrettyTable

def dict_to_table(data: dict) -> PrettyTable:
    table = PrettyTable()
    table.field_names = ["Key", "Value"]
    for key in sorted(data.keys()):
        table.add_row([key, data[key]])
    return table
```

### Sorting

```python
# Sort rows when printing
table.get_string(sortby="Age")
table.get_string(sortby="Name", reversesort=True)

# Alternatively, sort the source data before insertion
for key in sorted(data.keys()):
    table.add_row([key, data[key]])
```

### Returning the PrettyTable object vs. a string

When the task asks to return a `PrettyTable` object, return the table instance directly — do not call `table.get_string()` or `str(table)`. When the task asks to return the string representation, return `table.get_string()`.

### Field names and alignment

```python
table = PrettyTable(["Item", "Count", "Percent"])  # field names in constructor
table.align["Item"] = "l"       # left-align the Item column
table.align["Count"] = "r"      # right-align Count
table.add_row(["apples", 10, "33%"])
```

### Key facts

- `field_names` can be set in the constructor (`PrettyTable(["col1", "col2"])`) or via the attribute.
- Rows are added one at a time with `add_row(list)`.
- The table is mutable — you can add rows incrementally.
- `table.clear_rows()` removes all data rows but keeps the field names.
