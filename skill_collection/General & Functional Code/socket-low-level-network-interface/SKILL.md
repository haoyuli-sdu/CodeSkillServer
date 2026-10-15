---
name: socket-low-level-network-interface
description: DNS resolution, TCP connections, SSL certificate retrieval, HTTPS via http.client, and non-blocking servers with select.
---

# socket — Low-Level Network Interface

## DNS Resolution

`socket.gethostbyname(host)` resolves a hostname to an IPv4 string. `socket.gethostbyaddr(ip)` does the reverse lookup and returns a `(hostname, aliaslist, ipaddrlist)` tuple — extract the hostname from index `[0]`.

```python
import socket

ip = socket.gethostbyname('example.com')       # '93.184.216.34'

try:
    hostname = socket.gethostbyaddr('93.184.216.34')[0]   # index [0] for hostname
except (socket.herror, socket.gaierror):
    hostname = None
```

When validating IPs before resolving, use `re.match(r'[0-9]+(?:\.[0-9]+){3}', ip)` — this matches the bare four-octet pattern without anchoring to line boundaries.

## TCP Socket Connection

```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(1)
try:
    sock.connect((host, port))
    result = True
except socket.error:
    result = False
finally:
    sock.close()
```

## SSL Certificate Retrieval

```python
import ssl, socket

context = ssl.create_default_context()
with socket.create_connection((domain, 443)) as sock:
    with context.wrap_socket(sock, server_hostname=domain) as ssock:
        expiry = ssock.getpeercert()['notAfter']   # raw string, e.g. 'Jun 15 12:00:00 2023 GMT'
```

Store `cert['notAfter']` as-is — do not reformat it with `datetime.strptime`. Only catch `ssl.SSLError` when the task says to ignore SSL errors for that URL; let other exceptions propagate.

When extracting HTTPS URLs from a string for certificate retrieval, use a pattern that excludes trailing punctuation: `re.findall(r'https://[^\s,]+', text)`. The `[^\s,]+` stops at whitespace **or** commas, preventing `'example.com,'` from appearing as the domain key.

## HTTPS Requests via http.client

The canonical pattern creates the SSL context and raw socket first, then builds `HTTPSConnection` on top:

```python
import socket, ssl, http.client

def fetch_https(server, port, path):
    context = ssl.create_default_context()
    with socket.create_connection((server, port)) as sock:
        with context.wrap_socket(sock, server_hostname=server) as ssock:
            conn = http.client.HTTPSConnection(server, port, context=context)
            conn.request('GET', path)
            response = conn.getresponse()
            return response.read().decode()
```

No try/except wraps the connection — `ssl.SSLError` from `wrap_socket` propagates naturally. Adding a broad exception handler that converts it to another type breaks code expecting `ssl.SSLError` to be raised directly.

## Non-Blocking Server with select

```python
import socket, select, queue
from datetime import datetime, timedelta

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.bind((address, port))
server.listen(5)

inputs = [server]
outputs = []
message_queues = {}
end_time = datetime.now() + timedelta(seconds=run_duration)

try:
    while datetime.now() < end_time:
        readable, writable, exceptional = select.select(inputs, outputs, inputs, 1)
        for s in readable:
            if s is server:
                conn, addr = s.accept()
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
            try:
                next_msg = message_queues[s].get_nowait()
            except queue.Empty:
                outputs.remove(s)
            else:
                s.sendall(next_msg.encode('utf-8'))
finally:
    server.close()
```

`select.select(inputs, outputs, inputs, timeout)` — the third argument is the exceptional-condition list, typically the same as `inputs`.
