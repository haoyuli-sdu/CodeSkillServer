---
name: configparser-ini-style-configuration-fil
description: 'Guide for configparser: DEFAULT section semantics, config.set() string requirement, shutil.make_archive base_name pattern, list serialization.'
---

# Python `configparser` — INI-Style Configuration Files

## Core API

```python
from configparser import ConfigParser

config = ConfigParser()
config.read("settings.ini")         # read from file (silent if file missing)
config.read_file(f)                 # read from an open file object

config.get("Section", "key")        # retrieve value as string
config.set("Section", "key", "val") # set a value — value MUST be a string
config.add_section("Section")       # create a new named section
config.has_section("Section")       # True/False

with open("settings.ini", "w") as f:
    config.write(f)
```

## The DEFAULT Section

`ConfigParser` has a built-in `[DEFAULT]` section — it always exists and never needs to be created:

```python
config = ConfigParser()

# Write directly to DEFAULT — no add_section() call needed
config.set("DEFAULT", "timeout", "30")

# DEFAULT values are visible in every named section (one-way inheritance)
config["myapp"]["timeout"]    # → "30"  (inherited)
config["DEFAULT"]["timeout"]  # → "30"  (direct)
```

Values in named sections do **not** flow upward into DEFAULT. When the caller expects to read back a value from `config["DEFAULT"]["key"]`, store it under `"DEFAULT"`, not under a named section.

## Read-Modify-Write Patterns

### Storing a path in DEFAULT

```python
import os, sys
from configparser import ConfigParser

def register_path(path_to_append, config_file):
    if isinstance(path_to_append, list):
        for p in path_to_append:
            sys.path.append(p)
        path_str = ",".join(path_to_append)
    else:
        sys.path.append(path_to_append)
        path_str = path_to_append

    config = ConfigParser()
    if not os.path.exists(config_file):
        open(config_file, "a").close()   # create empty file so config.read works
    config.read(config_file)

    config.set("DEFAULT", "path_to_append", path_str)   # DEFAULT, not a named section

    with open(config_file, "w") as f:
        config.write(f)
    return config, config_file
```

### Reading a section value to locate a directory

```python
import configparser, os, shutil

def archive_from_config(config_path, output_dir):
    config = configparser.ConfigParser()
    config.read(config_path)

    project_dir = config.get("Project", "directory")
    if not os.path.isdir(project_dir):
        raise FileNotFoundError(f"Directory {project_dir} does not exist.")

    # build the archive file path, then strip the .zip extension for base_name
    archive_file = os.path.join(output_dir, os.path.basename(project_dir) + ".zip")
    shutil.make_archive(
        base_name=os.path.splitext(archive_file)[0],   # path WITHOUT .zip
        format="zip",
        root_dir=project_dir,                          # archive contents of this dir
    )
    if not os.path.isfile(archive_file):
        raise Exception(f"Failed to create archive {archive_file}")
    return True
```

`shutil.make_archive` appends the format extension automatically. Pass `base_name` without the `.zip` suffix — use `os.path.splitext(path)[0]` to strip it from a pre-constructed path.

## Handling List-Valued Options

`ConfigParser` stores only strings. Serialize lists as comma-separated values:

```python
paths = ["/usr/local/lib", "/opt/lib"]
config.set("DEFAULT", "search_paths", ",".join(paths))

# Reading back
raw = config.get("DEFAULT", "search_paths")
paths = [p.strip() for p in raw.split(",")]
```

## Common Pitfalls

- **`config.set` requires a string** — passing an int or list raises `TypeError`. Always convert with `str()` or join.
- **`config.add_section("DEFAULT")` raises `ValueError`** — DEFAULT always exists; never create it.
- **`config.read()` is silent on missing files** — returns a list of files read, not an error. Create the file first if the task requires it to exist.
- **Option names are lowercased** — `config.set("S", "MyKey", "v")` stores as `mykey`.
