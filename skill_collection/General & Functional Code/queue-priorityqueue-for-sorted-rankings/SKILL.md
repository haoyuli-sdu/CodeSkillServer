---
name: queue-priorityqueue-for-sorted-rankings
description: 'Guide for queue module: PriorityQueue min-heap negation pattern for descending order, draining into OrderedDict, Queue for inter-thread communication, and select-based server buffering.'
---

# Python queue — Practical Reference

## PriorityQueue for Sorted Output (Descending Order)

`queue.PriorityQueue` is a min-heap — the item with the **lowest** value comes out first. To sort in **descending** order (highest first), negate the numeric key before inserting:

```python
from queue import PriorityQueue
import collections

scores = {"Alice": 90, "Bob": 70, "Carol": 85}
pq = PriorityQueue()
for name, score in scores.items():
    pq.put((-score, name))   # negate for descending order

ordered = collections.OrderedDict()
while not pq.empty():
    neg_score, name = pq.get()
    ordered[name] = -neg_score
# ordered: Alice=90, Carol=85, Bob=70
```

The full loop to drain a PriorityQueue into an OrderedDict:
1. Insert `(-value, key)` tuples to get descending order from the min-heap
2. While not empty, `get()` and negate the value back to positive

## Complete Recipe: Data → PriorityQueue → OrderedDict

```python
from queue import PriorityQueue
import collections, random

def rank_items(items):
    scores = {item: random.randint(1, 100) for item in items}

    pq = PriorityQueue()
    for name, score in scores.items():
        pq.put((-score, name))

    result = collections.OrderedDict()
    while not pq.empty():
        neg_score, name = pq.get()
        result[name] = -neg_score
    return result
```

## Queue for Thread-safe Inter-thread Communication

`queue.Queue` is FIFO and thread-safe. Use it to pass data between producer and consumer threads:

```python
import queue, threading

q = queue.Queue()

def producer():
    for item in data_source:
        q.put(item)
    q.put(None)   # sentinel to signal completion

def consumer(results):
    while True:
        item = q.get()
        if item is None:
            break
        results.append(process(item))

results = []
t = threading.Thread(target=consumer, args=(results,))
t.start()
producer()
t.join()
```

## Queue in select-based Non-blocking Servers

When using `select.select` for I/O multiplexing, keep a `dict` mapping each client socket to a `queue.Queue` for outgoing message buffering:

```python
import socket, select, queue
from datetime import datetime, timedelta

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.bind((host, port))
server.listen(5)

inputs = [server]
outputs = []
message_queues = {}   # socket -> queue.Queue()
end_time = datetime.now() + timedelta(seconds=run_duration)

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

server.close()
return f"Server started on {host}:{port}. Ran for {run_duration} seconds."
```

Key points:
- `server.setblocking(0)` — non-blocking accept
- `select.select(inputs, outputs, inputs, 1)` — the final `1` is the timeout in seconds
- `queue.Empty` is the exception raised by `get_nowait()` on an empty queue
- Guard `if s not in message_queues: continue` before accessing sockets in the writable list

## Queue vs PriorityQueue

| Class | Order | Typical use |
|---|---|---|
| `queue.Queue` | FIFO | inter-thread data passing |
| `queue.PriorityQueue` | min-heap (lowest first) | sorted rankings |
| `queue.LifoQueue` | LIFO (stack) | depth-first traversal |
