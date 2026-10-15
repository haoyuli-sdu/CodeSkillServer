---
name: json-encoding-decoding-and-file-i-o
description: 'Guide for correct json API usage: loads/load/dumps/dump distinction, file scanning patterns, custom encoder, datetime serialization, and inspect integration.'
---

# Python `json` — Encoding, Decoding, and File I/O

## Core API Quick Reference

| Function | Input | Output | Notes |
|---|---|---|---|
| `json.loads(s)` | string | Python object | Raises `json.JSONDecodeError` on invalid input |
| `json.load(f)` | file handle | Python object | Pass an open file, not a path string |
| `json.dumps(obj)` | Python object | string | Returns `str`, does NOT write to disk |
| `json.dump(obj, f)` | Python object + file | None | Writes to file, returns `None` |

`json.loads` / `json.load` raise `json.JSONDecodeError` (subclass of `ValueError`) on invalid input — let this propagate unless the caller explicitly requires a fallback value.

## Encoding scalars as JSON strings

`json.dumps` encodes whatever Python value you pass. A Python string produces a JSON-encoded string (with quotes); a dict produces a JSON object.

```python
import json, math

value = round(math.sqrt(4.0), 2)          # 2.0

json.dumps(str(value))   # → '"2.0"'      json.loads gives "2.0" (a string)
json.dumps(value)        # → '2.0'        json.loads gives 2.0  (a float)
json.dumps({"v": value}) # → '{"v": 2.0}' json.loads gives {"v": 2.0} (a dict)
```

When the output should round-trip as a string (e.g. `json.loads(result) == "2.0"`), pass `str(value)` not a dict wrapper.

## File read/write patterns

```python
import json

# Read
with open("data.json", "r") as f:
    data = json.load(f)

# Write
with open("data.json", "w") as f:
    json.dump(data, f, indent=4)

# Append one JSON record per line
with open("log.json", "a", encoding="utf-8") as f:
    f.write(json.dumps(record) + "\n")

# In-place update: read → modify → seek back → overwrite → truncate old tail
with open("config.json", "r+") as f:
    data = json.load(f)
    data["last_updated"] = str(datetime.now())
    f.seek(0)
    json.dump(data, f, indent=4)
    f.truncate()
```

## Scanning a directory for JSON files

`os.listdir` raises `FileNotFoundError` when the directory does not exist.
`os.walk` silently returns an empty iterator for a missing directory — only use it when recursive traversal of real nested directories is required.

```python
import os, json
from collections import Counter

# Flat directory scan — canonical pattern
word_counts = Counter()
for filename in os.listdir(directory):          # raises FileNotFoundError if missing
    if filename.endswith(".json"):
        with open(os.path.join(directory, filename)) as f:
            record = json.load(f)
            word_counts.update(record.get("text", "").split())

# Recursive scan across subdirectories
hash_map = {}
for root, _, files in os.walk(directory):       # silent for missing dirs
    for name in files:
        path = os.path.join(root, name)
        hash_map[path] = compute_hash(path)
```

## Building DataFrames from JSON files

```python
import pandas as pd
import os, json, shutil

frames = []
for filename in sorted(f for f in os.listdir(src_dir) if f.endswith(".json")):
    with open(os.path.join(src_dir, filename)) as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    df_chunk = pd.DataFrame(data)
    df_chunk["source"] = filename
    frames.append(df_chunk)
    shutil.move(os.path.join(src_dir, filename), dest_dir)

result = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
```

`pd.concat` raises `ValueError` when given an empty list — always guard with `if frames`.

## Saving a list vs a DataFrame to JSON

When the input is already a Python list of dicts, use `json.dump` directly:

```python
with open(output_path, "w") as f:
    json.dump(result, f, indent=4)
```

`df.to_dict()` orientation options:
```python
df.to_dict(orient="dict")     # {col: {row_idx: val}}  — column-indexed (default)
df.to_dict(orient="records")  # [{"col": val}, ...]    — list of row dicts
df.to_dict(orient="list")     # {col: [val1, val2]}    — column lists
```

## datetime serialization

`datetime` objects are not JSON-serializable by default. Convert before calling `json.dumps`:

```python
from datetime import datetime

entry["timestamp"] = datetime.utcnow().isoformat()          # "2024-01-15T12:00:00.000000"
entry["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # no microseconds
entry["timestamp"] = str(datetime.now())                    # space separator, not T
```

These are NOT interchangeable — the separators and precision differ.

## Custom JSONEncoder

Override `default(self, obj)` to handle non-serializable types. Use `json.JSONEncoder.default(self, obj)` (not `super().default(obj)`) as the fallback:

```python
import json
from datetime import datetime
from decimal import Decimal
import numpy as np

class ExtendedEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)   # raises TypeError for unknown types

result = json.dumps(my_obj, cls=ExtendedEncoder)
```

For Enum types: `obj.name` is the identifier (`"BLUE"`), `obj.value` is the underlying value (`3`).

For function/type annotations, convert type objects to their string names:
```python
annotations = {k: v.__name__ if isinstance(v, type) else str(v)
               for k, v in spec.annotations.items()}
# int → "int", str → "str"   NOT "<class 'int'>"
```

## `inspect.getfullargspec` for function metadata

```python
import inspect, json, types

spec = inspect.getfullargspec(f)
info = {
    "function_name": f.__name__,
    "args": spec.args,
    "defaults": spec.defaults,        # None when no defaults exist — do NOT coerce to []
    "annotations": {k: v.__name__ if isinstance(v, type) else str(v)
                    for k, v in spec.annotations.items()},
    "is_lambda": isinstance(f, types.LambdaType),
}
return json.dumps(info)
```

`spec.defaults` is `None` (not `[]`) when the function has no default values.

## HTTP handler with JSON body

```python
import http.server, cgi, json

class JsonHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        ctype, _ = cgi.parse_header(self.headers.get("content-type"))
        if ctype != "application/json":
            self.send_error(400, "Content-Type must be application/json")
            return
        length = int(self.headers.get("content-length"))
        data = json.loads(self.rfile.read(length))
        # process data ...
        self.send_response(200)
        self.end_headers()
```

## Calling external APIs

```python
import urllib.request, json

response = urllib.request.urlopen(url)
data = json.loads(response.read())       # response.read() returns bytes

import requests
response = requests.get(url)
response.raise_for_status()             # include only when error handling is required
data = response.json()                  # returns parsed dict directly
# or: data = json.loads(response.text)
```

Filename construction: concatenate directly without extra separators unless the specification calls for them — `PREFIX + endpoint + ".json"`, not `PREFIX + "_" + endpoint + ".json"`.
