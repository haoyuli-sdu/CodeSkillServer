---
name: http-python-http-server-and-client
description: BaseHTTPRequestHandler factory pattern, cgi.parse_header for content-type, send_error vs send_response, and HTTPS client via http.client.
---

# http — Python HTTP Server and Client

## Building Request Handlers

The canonical pattern defines a handler class inside a factory function and returns the class (not an instance). Tests instantiate the class themselves:

```python
import http.server
import cgi
import json

def make_handler(config_param):
    class DataRequestHandler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            if ctype != 'application/json':
                self.send_error(400, 'Content-Type header is not application/json')
                return

            length = int(self.headers.get('content-length'))
            try:
                data = json.loads(self.rfile.read(length))
            except json.JSONDecodeError:
                self.send_error(400, 'Invalid JSON')
                return

            if 'data' not in data:
                self.send_error(400, 'No data key in request')
                return

            self.send_response(200)
            self.send_header('content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())

    return DataRequestHandler
```

## cgi.parse_header — Exact Content-Type Matching

```python
ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
# ctype is 'application/json' (no charset suffix, no surrounding whitespace)
if ctype != 'application/json':   # exact equality, not "in" membership
    ...
```

Using `'application/json' in content_type_string` can fail when the header is `'application/json; charset=utf-8'` because the raw string check would pass but the intent is to reject non-JSON types. `cgi.parse_header` splits off parameters first, making the comparison reliable.

## send_error vs send_response

| Situation | Method |
|---|---|
| Error with a string message body | `send_error(code, 'message text')` — sends status + body in one call |
| Success (200) | `send_response(200)` → `send_header(...)` → `end_headers()` → write body |
| Error where only the code matters | `send_response(code)` → `end_headers()` |

`send_error()` internally calls `end_headers()`, so never call `end_headers()` again on the same path after `send_error()`.

When handling `smtplib.SMTPAuthenticationError` inside a handler, use `send_response(535)` + `end_headers()` (not `send_error`), since the SMTP auth failure code is not a standard HTTP error:

```python
try:
    server.sendmail(from_addr, [to_addr], msg.as_string())
except smtplib.SMTPAuthenticationError:
    self.send_response(535)
    self.end_headers()
    return
```

## HTTPS Client Requests

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

`conn.request('GET', path)` followed by `conn.getresponse()` is the standard sequence. `response.read()` returns bytes; call `.decode()` for a string.

No try/except wraps the SSL wrapping step — `ssl.SSLError` from `context.wrap_socket` propagates as-is. Wrapping it in a different exception type breaks callers that catch `ssl.SSLError` specifically.
