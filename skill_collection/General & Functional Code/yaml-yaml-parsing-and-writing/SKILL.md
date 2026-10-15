---
name: yaml-yaml-parsing-and-writing
description: 'Guide for correct PyYAML usage: safe_load vs load, safe_dump, read-modify-write pattern, and common pitfalls.'
---

# Python `yaml` (PyYAML) — YAML Parsing and Writing

## Core API

| Function | Purpose |
|---|---|
| `yaml.safe_load(f_or_str)` | Parse YAML from file object or string → Python object |
| `yaml.safe_dump(obj, f)` | Serialize Python object → YAML, write to file |
| `yaml.load(f, Loader=...)` | Parse YAML with explicit loader (avoid unless necessary) |
| `yaml.dump(obj, f)` | Serialize to YAML (less safe; prefer `safe_dump`) |

## Basic usage

```python
import yaml

# Read YAML from file
with open("config.yaml", "r") as f:
    data = yaml.safe_load(f)   # returns dict, list, or scalar

# Write YAML to file
with open("config.yaml", "w") as f:
    yaml.safe_dump(data, f)

# Parse YAML from string
data = yaml.safe_load("key: value\nnumber: 42")
```

## safe_load vs load

- `yaml.safe_load()` is the standard choice — it prevents arbitrary code execution and covers all normal YAML types (str, int, float, bool, list, dict, None).
- `yaml.load(f, Loader=yaml.FullLoader)` is needed only for Python-specific tags like `!!python/object`. For general data, use `safe_load`.

## Read-modify-write pattern

```python
import yaml, math

with open(yaml_path, "r") as f:
    data = yaml.safe_load(f)

# Modify values
if key in data:
    data[key] = math.cos(data[key])

with open(yaml_path, "w") as f:
    yaml.safe_dump(data, f)

return data
```

## Common pitfalls

- **`yaml.load` without Loader**: raises a warning and can execute arbitrary code. Always use `yaml.safe_load` or pass `Loader=yaml.FullLoader`.
- **Return type**: `yaml.safe_load` on a YAML mapping returns a plain Python `dict`, not an ordered dict or any special object.
- **None from empty file**: `yaml.safe_load` on an empty file or empty string returns `None`, not an empty dict.
