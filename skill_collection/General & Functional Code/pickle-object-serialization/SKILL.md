---
name: pickle-object-serialization
description: pickle dump/load patterns, file modes, serialize-deserialize-cleanup order, directory creation guard, and matplotlib figure serialization.
---

# Python `pickle` — Object Serialization

## Core API

| Function | Purpose |
|---|---|
| `pickle.dump(obj, f)` | Serialize `obj` and write to open binary file `f` |
| `pickle.load(f)` | Deserialize and return an object from open binary file `f` |
| `pickle.dumps(obj)` | Serialize `obj` → `bytes` (no file needed) |
| `pickle.loads(b)` | Deserialize from `bytes` |

## File open modes

Always use `"wb"` for writing and `"rb"` for reading. Using text mode (`"w"` / `"r"`) raises `TypeError`:

```python
import pickle

with open("model.pkl", "wb") as f:
    pickle.dump(obj, f)

with open("model.pkl", "rb") as f:
    obj = pickle.load(f)
```

## Serialize → deserialize → clean up

A common pattern: write the object, read it back, then remove the file, and return the loaded value:

```python
import pickle, os

def round_trip(obj, path="temp.pkl"):
    with open(path, "wb") as f:
        pickle.dump(obj, f)

    with open(path, "rb") as f:    # open and load BEFORE removing
        loaded = pickle.load(f)

    os.remove(path)    # remove the file AFTER loading is complete
    return loaded
```

The removal step must come **after** `pickle.load` — removing the file first makes the subsequent read fail with `FileNotFoundError`.

## Serializing matplotlib figures

```python
import pickle, os
import matplotlib.pyplot as plt

def save_figure(values, file_path="chart.pkl"):
    fig, ax = plt.subplots()
    ax.plot(values)

    with open(file_path, "wb") as f:
        pickle.dump(fig, f)
    with open(file_path, "rb") as f:
        loaded_fig = pickle.load(f)
    os.remove(file_path)
    return loaded_fig
```

Input validation should match the spec precisely — an empty list `[]` is a valid list, so `isinstance(x, list)` passes for it. Only add extra checks if the task explicitly requires them.

## Writing with directory creation

```python
import os, pickle

def serialize_to_file(data, filename):
    directory = os.path.dirname(filename)
    if directory:    # guard: dirname("data.pkl") is "" — don't call makedirs on ""
        os.makedirs(directory, exist_ok=True)
    with open(filename, "wb") as f:
        pickle.dump(data, f)
    return True
```

## What pickle can serialize

Pickle handles nearly any Python object: dicts, lists, custom class instances, NumPy arrays, pandas DataFrames, sklearn models, matplotlib figures, datetime objects, etc.

## Common pitfalls

- **File mode**: `"w"` / `"r"` raises `TypeError: write() argument must be str, not bytes`. Always use `"wb"` / `"rb"`.
- **`pickle.dump` returns `None`**: do not use its return value.
- **Order matters**: dump → load → remove. Removing before loading destroys the data you need.
- **`pickle.loads` vs `pickle.load`**: `loads` takes `bytes`; `load` takes an open file. Mixing them raises `TypeError`.
