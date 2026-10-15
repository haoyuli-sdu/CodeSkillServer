---
name: cgi-cgi-utilities-for-http-header-parsin
description: cgi.parse_header usage, HTTP POST handler factory pattern returning a class, send_response+end_headers vs send_error, and SMTP email handler.
---

# cgi — CGI Utilities for HTTP Header Parsing

## cgi.parse_header

The primary function in modern usage — parses a header value into its main content type and a parameter dict:

```python
import cgi

ctype, pdict = cgi.parse_header("application/json; charset=utf-8")
# ctype = "application/json"
# pdict = {"charset": "utf-8"}
```

A direct string comparison against `self.headers.get('content-type')` fails when the client sends parameters like `charset=utf-8`. `cgi.parse_header` extracts just the media type before any parameters.

## HTTP POST Handler Factory Pattern

The canonical pattern: the task function returns a **handler class**, not a server instance. The class is used by callers directly — never call `http.server.HTTPServer(...)` inside the factory function.

```python
import http.server
import cgi
import json

def make_handler():
    class PostRequestHandler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            if ctype != 'application/json':
                self.send_response(400)
                self.end_headers()
                return

            length = int(self.headers.get('content-length'))
            try:
                message = json.loads(self.rfile.read(length))
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                return

            if 'data' not in message:
                self.send_response(400)
                self.end_headers()
                return

            self.send_response(200)
            self.send_header('content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode())

    return PostRequestHandler
```

## Response Methods: send_response + end_headers

Use `self.send_response(code)` followed by `self.end_headers()` for all responses (both success and error paths). This gives callers full control over which methods are invoked.

`self.send_error(code, message)` is a higher-level convenience that internally calls `send_response`, `send_header`, and `end_headers` in one call, but it also calls `self.log_request()` which accesses instance attributes (`requestline`, `request_version`) that may not be initialized when the handler is instantiated directly. Using `send_response` + `end_headers` avoids this dependency:

```python
# Robust pattern — no hidden attribute dependencies:
self.send_response(400)
self.end_headers()
return
```

## Handler with SMTP Email Sending

When the handler sends email, use `smtplib.SMTP` as a context manager. Pass recipients as a **list** to `sendmail`:

```python
import smtplib
from email.mime.text import MIMEText

def make_email_handler(smtp_server, smtp_port, smtp_username, smtp_password):
    class EmailRequestHandler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            ctype, _ = cgi.parse_header(self.headers.get('content-type'))
            if ctype != 'application/json':
                self.send_response(400)
                self.end_headers()
                return

            length = int(self.headers.get('content-length'))
            try:
                data = json.loads(self.rfile.read(length))
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                return

            if 'subject' not in data or 'message' not in data or 'to' not in data:
                self.send_response(400)
                self.end_headers()
                return

            msg = MIMEText(data['message'])
            msg['Subject'] = data['subject']
            msg['From'] = smtp_username
            msg['To'] = data['to']

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                try:
                    server.sendmail(smtp_username, [data['to']], msg.as_string())
                except smtplib.SMTPAuthenticationError as e:
                    self.send_response(e.smtp_code)
                    self.end_headers()
                    return

            self.send_response(200)
            self.end_headers()

    return EmailRequestHandler
```

Key: `sendmail(from_addr, [to_addr], msg_string)` — the second argument is a **list**, not a string.
