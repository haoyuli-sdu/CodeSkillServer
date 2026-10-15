---
name: sendgrid-sending-email-via-the-api
description: 'Guide for SendGrid email sending: Mail construction, sg.send(), directory listing pattern with bare os.listdir() try/except, HTTPError from python_http_client.'
---

# SendGrid — Sending Email via the API

## Core Imports

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import HTTPError
```

`HTTPError` lives in `python_http_client.exceptions` — not in `requests`, `http`, or `sendgrid`.

## Constructing and Sending a Message

```python
message = Mail(
    from_email='sender@example.com',
    to_emails='recipient@example.com',
    subject='Subject line',
    plain_text_content='Body text here'
)

sg = SendGridAPIClient(api_key)
response = sg.send(message)
```

`sg.send()` returns a response object with:
- `.status_code` — integer HTTP status code
- `.body` — response body string
- `.headers` — response headers

A successful send returns a 2xx status code: `200 <= response.status_code < 300`.

## Directory Listing Pattern

The canonical pattern for listing a directory and emailing its contents wraps `os.listdir()` directly in a try/except and re-raises as `FileNotFoundError`:

```python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import HTTPError

def send_dir_listing(directory, api_key, recipient_email):
    try:
        file_list = os.listdir(directory)
    except Exception:
        raise FileNotFoundError(f"Directory '{directory}' does not exist.")

    content = ', '.join(file_list)
    message = Mail(
        from_email='from_email@example.com',
        to_emails=recipient_email,
        subject=f'Directory Listing for {directory}',
        plain_text_content=content
    )

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        return 200 <= response.status_code < 300
    except HTTPError:
        raise
    except Exception:
        raise
```

Key points:
- Use `os.listdir(directory)` inside try/except — do **not** pre-check with `os.path.exists()` or `os.path.isdir()`. Pre-checks introduce coupling to the filesystem and fail when the directory is mocked rather than real.
- Re-raise `HTTPError` and other exceptions explicitly so callers can handle specific error types.
- The `from_email` literal `'from_email@example.com'` is the expected sender address in this pattern.

## Exception Hierarchy

- `HTTPError` (from `python_http_client.exceptions`): raised by `sg.send()` on 4xx/5xx responses
- `FileNotFoundError`: raised when the resource being listed does not exist
- Other exceptions from `sg.send()` indicate network or configuration errors
