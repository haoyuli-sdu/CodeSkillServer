---
name: shlex-shell-command-tokenization
description: shlex.split for subprocess, Title Case dict keys, str(datetime.now()) format, decode vs text=True, and Popen for time-bracketed execution.
---

# shlex — Shell Command Tokenization

## Core Use: shlex.split for subprocess

`shlex.split(s)` converts a shell command string into a list of tokens, handling quotes and embedded spaces correctly. Pass the result directly to `subprocess.Popen`:

```python
import shlex, subprocess
from datetime import datetime

def run_external_script(script_path):
    start_time = datetime.now()
    process = subprocess.Popen(
        shlex.split(f"/usr/bin/Rscript --vanilla {script_path}"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    end_time = datetime.now()

    return {
        'Start Time': str(start_time),
        'End Time':   str(end_time),
        'Stdout':     stdout.decode('utf-8'),
        'Stderr':     stderr.decode('utf-8'),
    }
```

Key points:
- Use `stdout=subprocess.PIPE` + `stderr=subprocess.PIPE` to capture output as bytes, then `.decode('utf-8')`.
- Do not use `text=True` — that decodes streams automatically, but the canonical pattern decodes manually with `.decode('utf-8')`.
- Use `process.communicate()` (not `stdout.read()`) to avoid deadlocks when both stdout and stderr are piped.

## Dict Key Format

Return dict keys must match the specification exactly. Time-tracking results use **Title Case with spaces**:

```
'Start Time'    # correct
'End Time'      # correct
'Stdout'        # correct (capital S, no space)
'Stderr'        # correct
'start_time'    # wrong — tests checking 'Start Time' will KeyError
```

## Timestamp Format

`str(datetime.now())` produces a string like `'2024-03-15 14:22:05.123456'`. This is the expected format — do not use `.isoformat()` (produces `'2024-03-15T14:22:05.123456'` with a `T` separator).

## subprocess.Popen vs subprocess.run

Use `Popen` when you need to capture timing around the execution:

```python
start_time = datetime.now()
process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
end_time = datetime.now()
```

`subprocess.run` is a blocking call that does not expose a natural split point for "time before" and "time after" the process finishes.

## shlex.quote

`shlex.quote(s)` escapes a single token for safe embedding in a shell string:

```python
safe = shlex.quote("/path/with spaces/file.R")
cmd = f"Rscript --vanilla {safe}"
args = shlex.split(cmd)
```

Do not pass `shell=True` when using a split list — that is only appropriate for string commands.
