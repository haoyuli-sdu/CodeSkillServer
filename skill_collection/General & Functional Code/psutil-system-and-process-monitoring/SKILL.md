---
name: psutil-system-and-process-monitoring
description: CPU/memory/disk usage, Texttable with add_rows and draw(), process_iter with name() method, terminate-restart pattern, and Process(pid) monitoring.
---

# psutil — System and Process Monitoring

## CPU, Memory, Disk Usage

```python
import psutil, os

cpu_pct = psutil.cpu_percent(interval=1)       # float, e.g. 23.5

mem = psutil.virtual_memory()
mem.total    # total bytes
mem.used     # used bytes
mem.percent  # float, e.g. 67.3

disk = psutil.disk_usage(os.sep)   # os.sep is '/' on Unix, '\\' on Windows
disk.percent # e.g. 45.2
```

**Memory percentage formatting**: `mem.percent` is a plain float like `67.3`. When the spec requires a formatted string matching `\d{1,3}\.\d{2}%`, compute it explicitly:

```python
f"{mem.used / mem.total * 100:.2f}%"
```

One decimal place (`"12.0%"`) will not match a two-decimal-place regex.

## Building a Texttable

The correct method is `table.draw()` — not `table.render()`. Pass all rows at once via `add_rows()` with the header as the first row:

```python
from texttable import Texttable
import psutil, os

table = Texttable()
table.add_rows([
    ['Item', 'Value'],
    ['CPU Usage (%)',    psutil.cpu_percent(interval=1)],
    ['Memory Usage (%)', psutil.virtual_memory().percent],
    ['Disk Usage (%)',   psutil.disk_usage(os.sep).percent],
])
return table.draw()   # returns a string
```

Pass raw numeric values, not formatted strings — Texttable formats the display internally.

## Iterating Processes: psutil.process_iter()

```python
import psutil

# Check if a process is running by name
is_running = any(proc for proc in psutil.process_iter() if proc.name() == target_name)
```

`proc.name()` is a method call — parentheses required.

**Process terminate-and-restart pattern**: check existence first, then act:

```python
import psutil, subprocess, time

is_running = any(p for p in psutil.process_iter() if p.name() == process_name)

if is_running:
    for p in psutil.process_iter():
        if p.name() == process_name:
            p.terminate()
            time.sleep(5)
    subprocess.Popen(process_name)
    return f"Process found. Restarting {process_name}."
else:
    subprocess.Popen(process_name)
    return f"Process not found. Starting {process_name}."
```

Return message format is significant: `"Process found. Restarting ..."` vs `"Process not found. Starting ..."`.

## Monitoring a Specific Process by PID

```python
import psutil, subprocess, time

p = subprocess.Popen(["bash", script_path])
process = psutil.Process(p.pid)

total_cpu = 0.0
total_memory = 0
start_time = time.time()

try:
    while process.is_running():
        total_cpu += process.cpu_percent(interval=0.05)
        total_memory += process.memory_info().rss
        time.sleep(0.05)
        if time.time() - start_time > timeout:
            break
except (psutil.NoSuchProcess, psutil.ZombieProcess):
    pass
finally:
    if p.poll() is None:
        p.terminate()
        p.wait()

return {"CPU Usage": total_cpu, "Memory Usage": total_memory}
```

`psutil.Process(pid)` wraps an existing OS process by PID. `process.is_running()` returns `False` once the process exits — catch `psutil.NoSuchProcess` for races.
