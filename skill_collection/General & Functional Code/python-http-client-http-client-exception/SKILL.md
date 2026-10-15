---
name: python-http-client-http-client-exception
description: 'Guide for python_http_client: HTTPError import path, response attributes, correct exception handling pattern with SendGrid.'
---

# python_http_client — HTTP Client for the SendGrid SDK

`python_http_client` is the underlying HTTP transport library used by the SendGrid Python SDK. In typical application code, you interact with it only through its exception types.

## Key Import

```python
from python_http_client.exceptions import HTTPError
```

`HTTPError` is raised by `SendGridAPIClient.send()` when the server returns a 4xx or 5xx HTTP response. Always import it from `python_http_client.exceptions` — not from `requests`, `http.client`, or `sendgrid`.

## Using HTTPError with SendGrid

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import HTTPError

def send_message(api_key, to_email, subject, body):
    message = Mail(
        from_email='from_email@example.com',
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
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

## Response Object from sg.send()

| Attribute | Type | Description |
|---|---|---|
| `.status_code` | int | HTTP status code (e.g., 202 for accepted) |
| `.body` | str | Response body |
| `.headers` | dict | Response headers |

Success check: `200 <= response.status_code < 300`

## When to Catch HTTPError

Catch `HTTPError` specifically when you need to inspect or log the HTTP-level error. Re-raise it (or let it propagate) when the caller needs to handle it:

```python
try:
    response = sg.send(message)
except HTTPError as e:
    print(f"HTTP error: {e}")  # e includes status code and response body
    raise
```
