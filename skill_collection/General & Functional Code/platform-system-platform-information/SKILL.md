---
name: platform-system-platform-information
description: OS detection, architecture tuple, Windows start command format, memory percentage formatting, and CPU monitoring via top/typeperf.
---

# platform — System Platform Information

## Key Functions

```python
import platform

platform.system()          # 'Linux', 'Windows', 'Darwin' (macOS), or ''
platform.node()            # network name of machine
platform.release()         # OS release string
platform.version()         # OS version string
platform.machine()         # machine type, e.g. 'x86_64'
platform.processor()       # processor type (may be empty on some systems)
platform.architecture()    # ('64bit', 'ELF') — tuple, not string
platform.python_version()  # '3.10.12'
```

## OS-Specific Command Selection

`platform.system()` returns exact strings — comparison is case-sensitive:

```python
import platform, subprocess, time

system = platform.system()
if system == 'Darwin':
    cmd = 'open'
elif system == 'Windows':
    cmd = 'start'
else:
    cmd = 'xdg-open'

process = subprocess.Popen([cmd, url], shell=True)
while process.poll() is None:
    time.sleep(1)
return process.returncode
```

`'Darwin'` for macOS, `'Linux'` for Linux, `'Windows'` for Windows. Do not call `.lower()` on the return value unless you are comparing in lowercase throughout.

**Windows `start` command**: the canonical invocation is `['start', url]` — two elements, no empty string separator between `'start'` and the URL. Using `['start', '', url]` or `['start', 'chrome', url]` changes the behavior.

## platform.architecture()

Returns a tuple `(bits, linkage)`. Index with `[0]` to extract just the bit-width string:

```python
platform.architecture()       # ('64bit', 'ELF')
platform.architecture()[0]    # '64bit'
```

## System Info Dictionary

`platform` does not provide memory usage — combine with `psutil`:

```python
import platform, psutil

info = {
    'OS':           platform.system(),
    'Architecture': platform.architecture()[0],
    'Memory Usage': f"{psutil.virtual_memory().used / psutil.virtual_memory().total * 100:.2f}%",
}
```

Use `:.2f` to produce exactly two decimal places — regex patterns like `\d{1,3}\.\d{2}%` require it. `f"{mem.percent:.1f}%"` gives one decimal place and will fail such checks.

## CPU Monitoring via subprocess

To measure CPU usage over time on different OSes, use `top` (Unix) or `typeperf` (Windows). The Unix `top -b -n1` output places the CPU summary at line index 2 (0-based). Parse it by splitting on `:` then `,`:

```python
import platform, subprocess, json, time

if platform.system() == 'Windows':
    command = ['typeperf', r'\Processor(_Total)\% Processor Time', '-sc', '1']
else:
    command = ['top', '-b', '-n1']

output = subprocess.check_output(command)
cpu_line = output.decode('utf-8').split('\n')[2]

if platform.system() == 'Windows':
    cpu_usage = cpu_line.split(',')[-1].strip().replace('"', '')
else:
    cpu_usage = cpu_line.split(':')[1].split(',')[0].strip()

log_data = {'timestamp': time.time(), 'cpu_usage': cpu_usage}
```

The Unix line looks like `%Cpu(s):  5.9 us,  0.3 sy, ...` — split on `':'` gives `['%Cpu(s)', '  5.9 us,  0.3 sy, ...']`, then split on `','` and take `[0]` gives `'  5.9 us'`. Do not attempt to convert it to `float` before stripping the `us` suffix.
