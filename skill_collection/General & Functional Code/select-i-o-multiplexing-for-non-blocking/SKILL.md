---
name: select-i-o-multiplexing-for-non-blocking
description: 'Guide for select.select() API: non-blocking echo server pattern with socket, queue, and datetime-based duration control.'
---

# select — I/O Multiplexing for Non-Blocking Servers

## Core API

`select.select(rlist, wlist, xlist, timeout)` monitors file descriptors for readability, writability, and exceptional conditions. Returns three lists: `(readable, writable, exceptional)`.

- `rlist`: watch for incoming data
- `wlist`: watch for writability (safe to send)
- `xlist`: watch for exceptional conditions
- `timeout`: seconds to wait; `1` is a common short timeout that lets the event loop check termination conditions

```python
import select

readable, writable, _ = select.select(inputs, outputs, inputs, 1)
```

## Non-Blocking Echo Server Pattern

The canonical pattern for a select-based server that runs for a fixed duration:

```python
import socket, select, queue
from datetime import datetime, timedelta

def run_echo_server(host, port, buffer_size, run_duration):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(0)
    server.bind((host, port))
    server.listen(5)

    inputs = [server]
    outputs = []
    message_queues = {}
    end_time = datetime.now() + timedelta(seconds=run_duration)

    try:
        while datetime.now() < end_time:
            readable, writable, _ = select.select(inputs, outputs, inputs, 1)

            for s in readable:
                if s is server:
                    conn, _ = s.accept()
                    conn.setblocking(0)
                    inputs.append(conn)
                    message_queues[conn] = queue.Queue()
                else:
                    data = s.recv(buffer_size)
                    if data:
                        message_queues[s].put(f"{datetime.now()}: {data.decode()}")
                        if s not in outputs:
                            outputs.append(s)
                    else:
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()
                        del message_queues[s]

            for s in writable:
                if s not in message_queues:
                    continue
                try:
                    msg = message_queues[s].get_nowait()
                except queue.Empty:
                    outputs.remove(s)
                else:
                    s.sendall(msg.encode("utf-8"))

    finally:
        server.close()

    return f"Server started on {host}:{port}. Ran for {run_duration} seconds."
```

## Key Design Points

- **`SO_REUSEADDR` first**: call `server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)` before `bind()`. This allows reuse of the port immediately after a previous server exits, which is essential for tests that start multiple servers on the same port.
- **Non-blocking socket**: call `server.setblocking(0)` before `select`. Each accepted client connection must also be set non-blocking.
- **Separate inputs/outputs lists**: `inputs` tracks all sockets to read; `outputs` tracks sockets with pending data to write. A socket is added to `outputs` when data is queued, and removed when the queue drains.
- **`queue.Queue` per connection**: each client gets its own queue. Use `queue.get_nowait()` — it raises `queue.Empty` if nothing is queued, so remove the socket from `outputs` in that case.
- **`finally: server.close()`**: always close the server socket even if the loop exits early.

## Return String Format

```python
return f"Server started on {server_address}:{server_port}. Ran for {run_duration} seconds."
```
