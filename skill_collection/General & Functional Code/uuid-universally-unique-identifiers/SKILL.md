---
name: uuid-universally-unique-identifiers
description: 'Guide for UUID generation and Django HttpResponse header injection: avoiding double-serialization and type-guard pitfalls.'
---

# uuid — Universally Unique Identifiers

## Generating UUIDs

`uuid.uuid4()` generates a random UUID (version 4). Convert to string with `str()`:

```python
import uuid

uid = uuid.uuid4()          # UUID object
uid_str = str(uid)          # "550e8400-e29b-41d4-a716-446655440000"
```

Use `uuid.uuid1()` for time-based UUIDs, `uuid.uuid4()` for random UUIDs (most common).

## Adding a UUID to Django HttpResponse Headers

The canonical pattern: pass `data` directly to `HttpResponse`, then set the UUID header:

```python
from django.http import HttpResponse
import uuid

def make_response(data):
    response = HttpResponse(data, content_type="application/json")
    response["UUID"] = str(uuid.uuid4())
    return response
```

**Critical**: pass `data` directly to `HttpResponse` without any type checking or conversion. Do not add `isinstance(data, dict)` guards or `json.dumps()` calls — if `data` is already a serialized string, running `json.dumps(data)` produces double-encoded output like `'"{\\"key\\": \\"value\\"}"'`, and raising `ValueError` for non-dict input rejects valid JSON string inputs. Accept and forward `data` as-is.

**Header name**: use `"UUID"` (not `"X-Request-ID"` or `"X-UUID"`). The header key is case-insensitive in HTTP transport but the accessor `response["UUID"]` should match the key used when setting it.

## UUID Object vs String

`uuid.uuid4()` returns a `UUID` object, not a string. Always convert with `str()` before storing in headers or JSON. The string form uses lowercase hex with hyphens: `"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"`.
