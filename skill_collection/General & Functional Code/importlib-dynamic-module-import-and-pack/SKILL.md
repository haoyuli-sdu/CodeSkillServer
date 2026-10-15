---
name: importlib-dynamic-module-import-and-pack
description: 'Guide for importlib: import_module pattern, package.__path__ vs __file__, iter_modules with __path__[0] for submodule path construction.'
---

# Python `importlib` — Dynamic Module Import and Package Inspection

## Core Pattern: Import a Package and Inspect Its Submodules

```python
import importlib
import os
import sys
from pkgutil import iter_modules

def add_package_modules_to_path(package_name):
    try:
        package = importlib.import_module(package_name)
    except ImportError:
        raise ImportError(
            f"The package '{package_name}' is not installed! "
            f"Please install the package first using 'pip install {package_name}'"
        )

    added_modules = []
    for _, module_name, _ in iter_modules(package.__path__):
        module_path = os.path.join(package.__path__[0], module_name)
        if module_path not in sys.path:
            sys.path.append(module_path)
            added_modules.append(module_name)
    return added_modules
```

## `package.__path__` vs `package.__file__`

These two attributes serve different purposes:

- `package.__path__` — a list of directory paths forming the package namespace.
  Use `package.__path__` with `iter_modules()` and `package.__path__[0]` when
  constructing submodule filesystem paths.
- `package.__file__` — path to the package's `__init__.py` file.
  `os.path.dirname(package.__file__)` gives the package directory, but this fails
  for namespace packages and is NOT the right base for module path construction.

The correct pattern:
```python
module_path = os.path.join(package.__path__[0], module_name)
```

Not:
```python
base = os.path.dirname(package.__file__)   # wrong — use package.__path__[0]
module_path = os.path.join(base, module_name)
```

## `importlib.import_module`

```python
importlib.import_module('json')         # top-level module
importlib.import_module('os.path')      # submodule by dotted name
importlib.import_module('.sub', 'pkg')  # relative import
```

Raises `ImportError` if the module is not found or cannot be imported.

## `pkgutil.iter_modules` Return Values

`iter_modules(path)` yields `(module_finder, name, ispkg)` tuples:
- `name` — bare submodule name (e.g., `'core'`, `'utils'`)
- `ispkg` — `True` if the entry is itself a package

Pass `package.__path__` (the list), not `[package.__file__]`:
```python
for _, module_name, _ in iter_modules(package.__path__):
    ...
```
