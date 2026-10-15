---
name: ssl-tls-ssl-wrapper-for-socket-objects
description: Server vs client context setup, server-side socket wrapping with finally-close pattern, HTTPS client using socket+ssl+http.client, certificate expiry retrieval, and HTTPS URL extraction.
---

# ssl — TLS/SSL Wrapper for Socket Objects

## Server vs Client Context

```python
import ssl

# Server-side — load a certificate to present to clients
server_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
server_ctx.load_cert_chain(certfile="server.crt", keyfile="server.key")

# Client-side — verify the server's certificate (outgoing connections)
client_ctx = ssl.create_default_context()
```

Use `ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)` for server contexts, not
`ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)`.

## Server: Wrapping an Accepted Socket

Receive a raw socket, wrap it with SSL, exchange data, and close. The `close()` call
belongs in `finally` so it runs even when exceptions occur:

```python
def serve_client(client_socket, cert_file, key_file, buffer_size=1024):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    secure_socket = None
    try:
        secure_socket = context.wrap_socket(client_socket, server_side=True)
        request = secure_socket.recv(buffer_size).decode("utf-8")

        if os.path.exists(request):
            with open(request, "rb") as f:
                content = f.read()
            response = hashlib.sha256(content).hexdigest()
        else:
            response = "File not found"

        secure_socket.send(response.encode("utf-8"))
    except Exception as e:
        response = f"Error: {str(e)}"
    finally:
        if secure_socket:
            secure_socket.close()   # always close, even on exception
    return response
```

Key points:
- Use `os.path.exists()` (not `os.path.isfile()`) to match the canonical existence check.
- Place `secure_socket.send(...)` inside the `try` block, before `finally`.
- `secure_socket.close()` must be called explicitly (not via context manager) when the
  socket was received from outside the function.

## Client: HTTPS with socket + ssl + http.client

When building an HTTPS client from first principles using all three modules together:

```python
import socket, ssl, http.client

def https_get(server_name, server_port, path):
    context = ssl.create_default_context()
    with socket.create_connection((server_name, server_port)) as sock:
        with context.wrap_socket(sock, server_hostname=server_name) as ssock:
            conn = http.client.HTTPSConnection(server_name, server_port, context=context)
            conn.request("GET", path)
            response = conn.getresponse()
            return response.read().decode()
```

Using `socket.create_connection` + `context.wrap_socket` ensures that SSL handshake
errors propagate as `ssl.SSLError`, which callers may need to catch.

## Reading Certificate Expiry

`ssock.getpeercert()` returns a dict. The `"notAfter"` key holds the expiry date as a
raw string — return it as-is without parsing, unless the specification says otherwise:

```python
context = ssl.create_default_context()
with socket.create_connection((domain, 443)) as sock:
    with context.wrap_socket(sock, server_hostname=domain) as ssock:
        expiry = ssock.getpeercert()["notAfter"]  # str, e.g. "Dec 31 23:59:59 2025 GMT"
```

## Extracting HTTPS URLs from Text

To capture only HTTPS links (not HTTP), anchor the pattern at the `s`:

```python
import re, urllib.parse

urls = re.findall(r'https://[^\s,]+', text)
for url in urls:
    domain = urllib.parse.urlparse(url).netloc
```

Using `r'https?://...'` would also match HTTP URLs. The `[^\s,]+` boundary excludes
trailing commas that may appear in prose lists.
