---
name: pkgutil-package-module-enumeration
description: 'Guide for pkgutil.iter_modules: iterate package submodules, add module paths to sys.path using __path__[0] as base, return module names not paths.'
---

# Python `pkgutil` — Package Module Enumeration

## Core API: `iter_modules`

`pkgutil.iter_modules(path=None, prefix='')` iterates over all modules (and sub-packages)
available under the given path list. It yields named tuples `(module_finder, name, ispkg)`.

```python
from pkgutil import iter_modules
import importlib
import os
import sys

package = importlib.import_module('numpy')
for finder, module_name, ispkg in iter_modules(package.__path__):
    print(module_name, ispkg)
    # e.g.: 'core' True, 'fft' True, 'random' True, ...
```

## Adding Submodule Paths to `sys.path`

A common task: enumerate a package's submodules and add their filesystem paths to
`sys.path`. Use `package.__path__[0]` (not `os.path.dirname(package.__file__)`) as
the base directory:

```python
added = []
for _, module_name, _ in iter_modules(package.__path__):
    module_path = os.path.join(package.__path__[0], module_name)
    if module_path not in sys.path:
        sys.path.append(module_path)
        added.append(module_name)
return added   # list of module names added (not full paths)
```

The function returns **module names** (e.g., `['core', 'fft', 'random']`), not the
full filesystem paths that were added.

## `package.__path__` Explained

`package.__path__` is a list of directory strings that Python searches for the package's
submodules. For most packages it has a single entry: the directory containing `__init__.py`.

```python
import numpy
numpy.__path__    # ['/path/to/numpy']
numpy.__path__[0] # '/path/to/numpy'
```

Pass the whole list to `iter_modules`, but use the first element `[0]` when joining paths:
```python
iter_modules(package.__path__)                              # correct
os.path.join(package.__path__[0], module_name)             # correct
```

## Full Recipe with Error Handling

```python
import os, sys, importlib
from pkgutil import iter_modules

def add_package_to_path(package_name):
    try:
        pkg = importlib.import_module(package_name)
    except ImportError:
        raise ImportError(
            f"The package '{package_name}' is not installed! "
            f"Please install the package first using 'pip install {package_name}'"
        )
    added = []
    for _, name, _ in iter_modules(pkg.__path__):
        path = os.path.join(pkg.__path__[0], name)
        if path not in sys.path:
            sys.path.append(path)
            added.append(name)
    return added
```
