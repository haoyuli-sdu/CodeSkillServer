---
name: signal-signal-handling-and-process-termi
description: 'Guide for signal module: pgrep -f for PID discovery, os.kill with SIGTERM, CalledProcessError handling, signal handler registration, and pgrep vs ps comparison.'
---

# signal — Signal Handling for Process Control

## Finding PIDs with pgrep, then Sending SIGTERM

The standard pattern for stopping named processes — use `pgrep -f` to search the full command line:

```python
import subprocess, os, signal, time

def stop_processes(process_name: str) -> int:
    try:
        output = subprocess.check_output(['pgrep', '-f', process_name])
        pids = output.decode().split('\n')[:-1]   # strip trailing empty string
    except subprocess.CalledProcessError:
        pids = []   # no matching processes found

    for pid in pids:
        os.kill(int(pid), signal.SIGTERM)

    time.sleep(1)   # give processes time to handle the signal
    return len(pids)
```

Key details:
- Use `subprocess.check_output(['pgrep', '-f', name])` — the `-f` flag matches against the full command line, not just the process executable name
- `pgrep` raises `subprocess.CalledProcessError` when no processes match — always wrap in try/except
- `pgrep` output ends with `'\n'` — `split('\n')[:-1]` strips the trailing empty string
- `os.kill` requires an integer PID — always convert with `int(pid)`
- Return `len(pids)` — the count of processes signaled, not the count that actually stopped

## Sending Signals to Processes

`os.kill(pid, signal.SIGTERM)` sends a termination signal to a process by PID:

```python
import os, signal

os.kill(pid, signal.SIGTERM)   # graceful termination request (catchable)
os.kill(pid, signal.SIGKILL)   # forceful kill (cannot be caught, POSIX only)
os.kill(pid, signal.SIGINT)    # keyboard interrupt equivalent
```

`os.kill` sends the signal without waiting for the process to terminate.

## Setting Signal Handlers

```python
import signal

def handler(signum, frame):
    print(f"Received signal {signum}")
    # perform cleanup

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, signal.SIG_IGN)   # ignore Ctrl+C

# Restore default handler
signal.signal(signal.SIGTERM, signal.SIG_DFL)
```

Signal handlers are registered per-process and fire when the signal arrives. `signal.SIG_IGN` ignores the signal; `signal.SIG_DFL` restores default behavior.

## Common Signal Constants

```python
signal.SIGTERM   # 15 — graceful termination (catchable, default for kill)
signal.SIGKILL   # 9  — forceful kill (cannot be caught or ignored, POSIX only)
signal.SIGINT    # 2  — keyboard interrupt (Ctrl+C)
signal.SIGHUP    # 1  — hangup (reload convention for daemons)
signal.SIGUSR1   # 10 — user-defined
signal.SIGUSR2   # 12 — user-defined
```

## pgrep vs ps for Process Discovery

`pgrep -f name` is the canonical tool for finding PIDs by process name — it returns one PID per line and exits with status 1 if nothing matches. Parsing `ps -ef` output manually is fragile (column positions vary, header must be skipped, name matching is ambiguous). Use `pgrep` when available.
