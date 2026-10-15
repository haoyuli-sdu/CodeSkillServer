---
name: sys-system-specific-parameters-and-funct
description: Guide for sys.path management, pkgutil iteration, sys.executable subprocess usage, configparser string values, and pyenv/SQLite patterns.
---

# sys — System-Specific Parameters and Functions

## sys.path — adding paths

`sys.path` is a list of strings. Append a path with `sys.path.append(path)`:

```python
import sys

sys.path.append('/some/module/dir')                    # unconditional append
if path not in sys.path:
    sys.path.append(path)                              # avoid duplicates
```

Note: `sys.path.append` does **not** create the directory — use `os.makedirs` or `Path.mkdir` separately if the directory may not exist:

```python
from pathlib import Path
import sys

Path(path_to_append).mkdir(parents=True, exist_ok=True)
sys.path.append(path_to_append)
return path_to_append
```

## Adding package module paths with pkgutil

To add all sub-modules of a package to `sys.path`, iterate with `pkgutil.iter_modules`:

```python
import importlib
import os
import sys
from pkgutil import iter_modules

package = importlib.import_module(package_name)
added = []
for _, module_name, _ in iter_modules(package.__path__):
    module_path = os.path.join(package.__path__[0], module_name)
    if module_path not in sys.path:
        sys.path.append(module_path)
        added.append(module_name)
return added
```

## sys.executable — current Python interpreter path

Use `sys.executable` when spawning subprocesses that need the same Python:

```python
import subprocess, sys

process = subprocess.Popen(
    [sys.executable, script_path, *args],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
stdout, stderr = process.communicate()
```

## sys.stderr — printing error messages

Print to stderr with the `file=sys.stderr` argument to `print()`:

```python
try:
    ...
except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)
```

## sys.version, sys.exit

```python
sys.version       # str: '3.10.12 (main, ...) ...'
sys.executable    # str: '/usr/bin/python3'
sys.argv          # list of command-line arguments

sys.exit(1)       # raise SystemExit(1) — stops the process
```

## configparser with sys.path: values must be strings

`configparser` requires all values to be strings. When the path may be a list, join it first:

```python
from configparser import ConfigParser
import os, sys

config = ConfigParser()
if not os.path.exists(config_file):
    open(config_file, 'a').close()
config.read(config_file)

# Convert to string before setting:
path_str = ','.join(path) if isinstance(path, list) else path
config.set('DEFAULT', 'path_to_append', path_str)   # value MUST be str

with open(config_file, 'w') as f:
    config.write(f)
```

## pyenv + sys.path pattern

```python
import subprocess, sys

subprocess.run(['pyenv', 'global', python_version], check=True)
sys.path.append(path_to_append)
return python_version
```

## SQLite + sys.path pattern

```python
import sys, sqlite3

sys.path.append(path_to_append)

conn = sqlite3.connect(database)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS paths (path TEXT UNIQUE)")
cur.execute("INSERT OR IGNORE INTO paths (path) VALUES (?)", (path_to_append,))
conn.commit()
conn.close()
return path_to_append
```
