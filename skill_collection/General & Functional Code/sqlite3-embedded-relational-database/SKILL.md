---
name: sqlite3-embedded-relational-database
description: sqlite3 connection patterns, CREATE TABLE IF NOT EXISTS, parameterized queries, pandas integration, and column ordering pitfalls.
---

# sqlite3 — Embedded Relational Database

## Core connection patterns

```python
import sqlite3

# Explicit open/close — straightforward for write operations
conn = sqlite3.connect("mydb.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, name TEXT)")
cur.execute("INSERT INTO events (name) VALUES (?)", ("startup",))
conn.commit()
conn.close()

# Context manager — commits on clean exit, rolls back on exception
with sqlite3.connect("mydb.db") as conn:
    df = pd.read_sql_query("SELECT * FROM events", conn)
# Note: with-block does NOT close the connection — call conn.close() explicitly if needed
```

## Creating tables

Use `CREATE TABLE IF NOT EXISTS` to safely create a table without raising an error if it already exists:

```python
cur.execute("""
    CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor TEXT,
        value REAL,
        recorded_at TEXT
    )
""")
```

Each `cur.execute()` call accepts exactly one SQL statement. To delete and recreate a table, use two separate calls:
```python
cur.execute("DROP TABLE IF EXISTS logs")
cur.execute("CREATE TABLE logs (ts TEXT, level TEXT, msg TEXT)")
```

## Parameterized queries

Pass values with `?` placeholders — never embed them via string formatting. Table and column **names** cannot be parameterized; use f-strings only for identifiers:

```python
# Correct: values via placeholders
cur.execute("INSERT INTO scores (player, pts) VALUES (?, ?)", (player_name, points))

# Column and table names — safe only when the caller controls the value
cols = ["name", "age", "score"]
placeholders = ", ".join("?" * len(cols))
cur.execute(
    f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})",
    [row[c] for c in cols]
)
```

## Insert-or-deduplicate

```python
cur.execute("CREATE TABLE IF NOT EXISTS paths (path TEXT UNIQUE)")
cur.execute("INSERT OR IGNORE INTO paths (path) VALUES (?)", (file_path,))
conn.commit()
```

## Building schema from CSV headers

```python
import csv, sqlite3

def load_csv_to_db(csv_path, db_path, table_name):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames
        col_defs = ", ".join(f"{c} TEXT" for c in cols)
        cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs})")
        placeholders = ", ".join("?" * len(cols))
        for row in reader:
            cur.execute(
                f"INSERT INTO {table_name} VALUES ({placeholders})",
                [row[c] for c in cols]
            )
    conn.commit()
    conn.close()
```

`pandas.to_sql(..., if_exists='replace')` silently adds an auto-increment index column that shifts column ordering — the explicit `CREATE TABLE` approach above preserves exact column names.

## Reading into pandas

```python
import pandas as pd, sqlite3

with sqlite3.connect(db_path) as conn:
    df = pd.read_sql_query("SELECT * FROM employees WHERE dept = ?", conn, params=("Engineering",))
```

The `pd.read_sql_query` call must appear **inside** the `with` block so it receives the active connection object.

## Returning absolute path

```python
db_path = os.path.abspath(db_name)
conn = sqlite3.connect(db_path)
# ... operations ...
conn.close()
return db_path
```

## Common pitfalls

- **`df.to_sql(..., if_exists='replace')`** adds an auto-increment index column; pass `index=False` to suppress it.
- **Column name mismatch**: a `KeyError` or `OperationalError: no such column` means you used a name different from what `CREATE TABLE` defined. Match the spec exactly.
- **Closing before reading**: call `conn.close()` only after all reads and writes finish.
- **Integer range guards**: check bounds (`num_entries >= 0`) before opening the database, so invalid inputs raise early rather than creating a partial file.
