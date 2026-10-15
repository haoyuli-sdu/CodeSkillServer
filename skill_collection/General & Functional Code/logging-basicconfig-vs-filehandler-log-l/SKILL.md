---
name: logging-basicconfig-vs-filehandler-log-l
description: 'Practical guide for Python logging: configuration styles, level selection, exact message format, and file handler lifecycle.'
---

# Python logging — Practical Reference

## Two Configuration Paths

`logging.basicConfig` sets up the root logger quickly. It only acts on the **first call** within a process — if handlers already exist on the root logger, subsequent `basicConfig` calls are silently ignored. This matters when a function is called multiple times in the same process (e.g., across test cases in a suite).

`FileHandler` gives full control and works correctly on every call:

```python
import logging, os

# basicConfig — one-time setup, before any handlers are attached
logging.basicConfig(
    filename='events.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.info('job started')
logging.error('failure: %s', err_msg)
```

```python
# FileHandler — reliable per-call setup with explicit cleanup
import logging, os

def record_events(items, log_path):
    handler = logging.FileHandler(
        os.path.join(log_path, 'events.log'), mode='w', encoding='utf-8'
    )
    handler.setFormatter(logging.Formatter('%(levelname)s:%(message)s'))
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logger.info('Processing %d items', len(items))
    # ... do work ...
    logger.removeHandler(handler)
    handler.close()
    logging.shutdown()
    return len(items)
```

**When to use `FileHandler`**: when the function receives a `log_path` parameter, requires `mode='w'` (fresh file each invocation), or specifies a format like `%(levelname)s:%(message)s`. Use `os.path.join(log_path, 'filename.log')` — not string concatenation — to assemble the path safely.

## Log Level Selection

`logging.info` records normal successful operations. `logging.error` records failures and exceptions. `logging.warning` flags unusual but non-fatal conditions. `logging.debug` is for detailed diagnostic output.

```python
# Removing files: use INFO for each removal
for fname in os.listdir(directory):
    if 'target' in fname and fname.endswith('.js'):
        os.remove(os.path.join(directory, fname))
        logging.info('Removed file: %s', fname)

# Compilation result
try:
    subprocess.check_call(['g++', filepath, '-o', filepath.split('.')[0]])
    logging.info('Successfully compiled %s', filepath)
except subprocess.CalledProcessError as e:
    logging.error('Failed to compile %s: %s', filepath, e)
except FileNotFoundError as e:
    logging.error('Compiler not found or file does not exist: %s', e)
```

## Exact Message Content

When a task specifies the log message, reproduce it exactly — no descriptive prefix or suffix. The message argument is what gets compared in assertion checks.

```python
# Log only the serialized value — no label before it
logging.info(json.dumps(data))          # correct: single argument

# Conditional warning with exact string
if metrics.get('open_issues', 0) > 10000:
    logging.warning('The repository has more than 10000 open issues.')
```

## Message Format: Positional vs f-string

`logging.info('msg %s', val)` stores the format string and argument separately.
`logging.info(f'msg {val}')` stores the already-formatted string.
These produce different call signatures — match what the task or caller expects.

```python
logging.info('Compiled %s successfully', filepath)   # positional args
logging.info(f'Compiled {filepath} successfully')    # pre-formatted string
```

## Directory Scanning: listdir vs walk

`os.listdir(directory)` iterates one flat directory. `os.walk(directory)` descends recursively. Use `os.listdir` unless the task explicitly requires traversal of subdirectories.

```python
def remove_jquery_files(directory):
    logging.basicConfig(filename='jquery_removal.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory '{directory}' does not exist.")
    removed = []
    for fname in os.listdir(directory):
        if 'jquery' in fname and fname.endswith('.js'):
            os.remove(os.path.join(directory, fname))
            removed.append(fname)
            logging.info('Removed jQuery file: %s', fname)
    return removed
```

## Avoiding Pre-flight Checks Before Subprocess or I/O

When a function is expected to catch `FileNotFoundError` from subprocess or file operations directly, adding `os.path.isfile` / `os.path.exists` checks before the call will raise `FileNotFoundError` on a path that is not present rather than allowing the subprocess to handle it naturally.

```python
# Let subprocess raise naturally; catch in the except block
def compile_file(filepath):
    logging.basicConfig(level=logging.INFO)
    try:
        subprocess.check_call(['g++', filepath, '-o', filepath.split('.')[0]])
        logging.info('Successfully compiled %s', filepath)
    except subprocess.CalledProcessError as e:
        logging.error('Failed to compile %s: %s', filepath, e)
    except FileNotFoundError as e:
        logging.error('Compiler not found or file does not exist: %s', e)
```
