---
name: smtplib-sending-email-via-smtp
description: SMTP workflow with starttls/login/sendmail, injectable factory pattern for smtp=None, and SMTPAuthenticationError in HTTP handlers.
---

# smtplib — Sending Email via SMTP

## Core Workflow

```python
import smtplib

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()               # Upgrade to TLS; always call before login
server.login('user@gmail.com', 'password')
server.sendmail('user@gmail.com', 'to@example.com', message)
server.quit()
```

## Plain-Text Message Format

`sendmail()` accepts a raw string. Two newlines separate headers from the body:

```python
message = 'Subject: Extracted Names\n\n' + '\n'.join(names)
server.sendmail(from_addr, to_addr, message)
```

## Injectable SMTP Factory Pattern

Many tasks include an `smtp=None` parameter for dependency injection. When provided, call `smtp(server, port)` as a factory. When `None`, use `smtplib.SMTP` directly. The `starttls` / `login` / `sendmail` / `quit` sequence is identical in both branches:

```python
def send_names_email(smtp_server, smtp_port, email_address, email_password,
                     recipient, message, smtp=None):
    if smtp is not None:
        conn = smtp(smtp_server, smtp_port)
    else:
        conn = smtplib.SMTP(smtp_server, smtp_port)
    conn.starttls()
    conn.login(email_address, email_password)
    conn.sendmail(email_address, recipient, message)
    conn.quit()
```

When `smtp=None` appears in the function signature, **always check it** and branch accordingly. A `with smtplib.SMTP(...) as conn:` block bypasses this check and causes `login` to never be called in the injection branch.

## Context Manager Form (no injection parameter)

When no `smtp=` parameter exists in the signature, use the context manager:

```python
with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
    smtp.starttls()
    smtp.login(sender, password)
    smtp.send_message(email_msg)    # or smtp.sendmail(...)
```

## SMTPAuthenticationError in HTTP Handlers

When smtplib is used inside an HTTP request handler, catch `smtplib.SMTPAuthenticationError` and send the appropriate error code rather than letting the exception propagate:

```python
try:
    server.sendmail(from_addr, [to_addr], msg.as_string())
except smtplib.SMTPAuthenticationError:
    self.send_response(535)
    self.end_headers()
    return
```

Note: the `sendmail` recipient argument is a **list** `[to_addr]` when using `MIMEText` with `msg.as_string()`.

## Return Value

`sendmail()`, `starttls()`, `login()`, and `quit()` all return values that are rarely needed. The function's return value is typically the extracted data (a list of names, parsed records, etc.), not the SMTP connection object.
