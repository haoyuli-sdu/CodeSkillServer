---
name: threading-sequential-vs-parallel-executi
description: 'Practical guide for threading: sequential vs parallel join patterns, thread naming, join(timeout) with is_alive(), Popen+poll() for subprocess threads, and shared state for network scanning.'
---

# Python threading — Practical Reference

## Thread Lifecycle: start() and join()

Every thread follows the same lifecycle: create with `threading.Thread(target=fn, args=(...))`, start with `.start()`, wait for completion with `.join()`.

```python
import threading

results = []

def worker(item):
    results.append(item * 2)

threads = [threading.Thread(target=worker, args=(x,)) for x in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

## Sequential vs Parallel Execution — Timing Determines the Pattern

The placement of `.join()` determines whether threads run sequentially or concurrently:

```python
# Sequential — each thread must finish before the next starts:
for i in range(num_threads):
    t = threading.Thread(target=delay_fn, name=str(i))
    t.start()
    t.join()   # blocks here; total time = delay * num_threads

# Parallel — all threads run at the same time:
threads = [threading.Thread(target=work, args=(x,)) for x in items]
for t in threads: t.start()   # launch all
for t in threads: t.join()    # collect all
```

**When the specification measures total elapsed time as `delay × num_threads`**, each iteration must complete before the next begins — use sequential (start + join in the same loop). When tasks truly run concurrently, use the launch-all then collect-all pattern.

## Naming Threads and Reading the Thread Name Inside the Target

Pass `name=str(i)` at creation; retrieve with `threading.current_thread().name` inside the target function:

```python
def record_completion():
    name = threading.current_thread().name   # "0", "1", "2", ...
    results.append(f"Task in thread {name} completed")

for i in range(num_threads):
    t = threading.Thread(target=record_completion, name=str(i))
    t.start()
    t.join()
```

## thread.join(timeout) for Bounded Execution

`join(timeout)` returns after at most `timeout` seconds whether or not the thread finished. Use `is_alive()` afterwards to determine which case occurred:

```python
thread = threading.Thread(target=target_fn)
thread.start()
thread.join(timeout)

if thread.is_alive():
    os.system(f'pkill -f "{script_path}"')
    thread.join()
    return "Terminating process due to timeout."
else:
    return "Script executed successfully."
```

## subprocess.Popen + poll() Inside Thread Workers

When launching subprocesses from threads and collecting exit codes, use `subprocess.Popen` with `process.poll()` after a brief sleep — not `subprocess.run` which blocks:

```python
def execute_file(file_path):
    process = subprocess.Popen(file_path)
    time.sleep(1)                     # give process time to start
    exit_codes.append(process.poll()) # None if still running, int if finished

threads = [threading.Thread(target=execute_file, args=(f,)) for f in file_list]
for t in threads: t.start()
for t in threads: t.join()
```

`process.poll()` returns `None` when the subprocess is still running, and the integer exit code when it has finished. This is the correct return value when a process hasn't yet exited.

## subprocess.call vs subprocess.Popen Inside Thread Workers

`subprocess.call(['python', script])` blocks the calling thread until the subprocess exits — straightforward for running a script and waiting for it.
`subprocess.Popen(['python', script])` starts the subprocess and returns immediately — use when you need to poll the process or kill it later.

For timeout-based script execution, `subprocess.call` inside a thread lets `thread.join(timeout)` and `thread.is_alive()` control the overall lifetime.

## No File-Existence Pre-checks Before subprocess

Adding `os.path.isfile(script_path)` before starting a subprocess causes failures when the path is synthesized or virtual. The subprocess call itself will raise the appropriate error if the path is invalid — let the natural error propagate rather than adding a pre-flight guard:

```python
def target():
    subprocess.call(['python', script_path])   # no os.path.isfile() check needed

thread = threading.Thread(target=target)
thread.start()
thread.join(timeout)
```

## Thread-safe Shared State for Network Scanning

Collecting results into a shared `dict` from multiple threads is safe in CPython for independent keys. Convert IP addresses to strings when storing:

```python
status = {}   # shared, modified from multiple threads

def check_port(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect((str(ip), port))
        status[str(ip)] = True       # str(ip), not ip
    except socket.error:
        status[str(ip)] = False
    finally:
        sock.close()

for ip in IPv4Network(ip_range):
    t = Thread(target=check_port, args=(ip,))
    t.start()
    threads.append(t)
for t in threads:
    t.join()
```

Return `status` — keys are strings (`"192.168.1.1"`), values are booleans.
