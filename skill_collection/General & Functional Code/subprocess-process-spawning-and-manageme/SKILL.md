---
name: subprocess-process-spawning-and-manageme
description: Guide for subprocess API selection, file-based output capture, script execution with error handling, Popen, and shell=True usage.
---

# subprocess — Process Spawning and Management

## Core API Selection

`subprocess.call` — run and wait, return **int exit code** (0 = success)
`subprocess.check_output` — run and wait, return **stdout bytes**, raise `CalledProcessError` on failure
`subprocess.run` — run and wait, return `CompletedProcess` with `.returncode`, `.stdout`, `.stderr`
`subprocess.Popen` — launch without waiting; use `.wait()`, `.poll()`, or `.communicate()` to interact

```python
# call: simplest — just the exit code
ret = subprocess.call(['ls', '-la'])                 # int
ret = subprocess.call('ls -la /tmp', shell=True)     # shell=True for string commands

# check_output: get stdout bytes
out = subprocess.check_output(['git', 'log', '--oneline'])   # bytes; raises on failure
pids = subprocess.check_output(['pgrep', '-f', name]).decode().split('\n')[:-1]

# run: get both return code and output
result = subprocess.run(['ls', '-la'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
result.returncode   # int
result.stdout       # bytes
```

## Capturing Output to a File

Write stdout and stderr directly to an open file handle; check the return code afterward:

```python
with open(output_file, 'w') as f:
    ret = subprocess.call(command, shell=True, stdout=f, stderr=subprocess.STDOUT)
    if ret != 0:
        f.write(f"\nError executing command, exited with code {ret}")
```

## Script Execution — Copy Then Run, With Error Handling

When running a script copied into a working directory, wrap the entire sequence in a broad
`try/except` so that pre-execution failures (missing file, copy error) are handled the
same way as runtime failures:

```python
import shutil, os, subprocess

def run_in_tempdir(script_path, temp_dir):
    try:
        shutil.copy(script_path, temp_dir)
        temp_script = os.path.join(temp_dir, os.path.basename(script_path))
        result = subprocess.call(['python', temp_script])
        if result == 0:
            return "Script executed successfully!"
        else:
            return "Script execution failed!"
    except Exception:
        return "Script execution failed!"
```

Avoid `os.chdir()` — changing the working directory affects the entire process and can
interfere with paths resolved elsewhere in the program.

## Popen — Launch and Manage

Use `Popen` when you need non-blocking execution, polling, or parallel processes:

```python
# Launch and wait for completion
process = subprocess.Popen(file_path)
process.wait()
exit_code = process.returncode

# Non-blocking poll (None while running):
process = subprocess.Popen(file_path)
time.sleep(1)
exit_code = process.poll()

# Capture stdout and stderr:
process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()    # waits and returns bytes

# Run Python script with current interpreter:
process = subprocess.Popen(
    [sys.executable, script_path, *args],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
stdout, stderr = process.communicate()
```

## Parallel Processes with Threading

```python
import threading

exit_codes = []

def run_file(file_path):
    proc = subprocess.Popen(file_path)
    time.sleep(1)
    exit_codes.append(proc.poll())

threads = [threading.Thread(target=run_file, args=(f,)) for f in file_list]
for t in threads: t.start()
for t in threads: t.join()
```

## shell=True vs List

With `shell=True`, pass the command as a **string**; without it, pass a **list**:

```python
subprocess.call('ls -la /tmp', shell=True)          # shell interprets the string
subprocess.Popen(['gzip', file_path])                # OS executes first element directly
subprocess.run(['pyenv', 'global', version], check=True)
```

## R Scripts and Timed Execution

```python
import shlex
from datetime import datetime

start_time = datetime.now()
process = subprocess.Popen(
    shlex.split(f'/usr/bin/Rscript --vanilla {script_path}'),
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
stdout, stderr = process.communicate()
end_time = datetime.now()

return {
    'Start Time': str(start_time),
    'End Time': str(end_time),
    'Stdout': stdout.decode('utf-8'),
    'Stderr': stderr.decode('utf-8'),
}
```

## Logging CPU/Memory Usage

For processes launched via `Popen`, access system metrics through `psutil.Process(pid)`:

```python
process = subprocess.Popen(['bash', script_path])
pid = process.pid
proc_info = psutil.Process(pid)
while proc_info.is_running():
    cpu = proc_info.cpu_percent()
    mem = proc_info.memory_info().rss
```
