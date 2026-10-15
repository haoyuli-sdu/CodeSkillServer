---
name: django-httpresponse-fileresponse-and-vie
description: Django HttpResponse patterns, default status codes, custom headers, FileResponse with in-memory buffers, and authentication view patterns.
---

# Django — HttpResponse, FileResponse, and View Utilities

## HttpResponse with Pre-serialized Data

`HttpResponse(data, content_type='application/json')` passes `data` directly as the response body without transformation. If `data` is already a JSON string, pass it as-is — calling `json.dumps()` again double-encodes it:

```python
from django.http import HttpResponse

# data is already a JSON string — pass it as-is
def json_view(data):
    return HttpResponse(data, content_type='application/json')
```

When wrapping extra context around the data (e.g., `{"message": ..., "data": ...}`), do so only if the task explicitly asks for that structure.

## Default Status Code

`HttpResponse('text')` with no `status=` argument returns HTTP 200. Only set `status=` when a non-200 code is required:

```python
return HttpResponse('Login successful.')        # 200 OK — no status needed
return HttpResponse('Login failed.', status=401)  # explicit 401
return HttpResponseBadRequest('Bad Request')    # 400 via convenience class
```

## Setting Custom Response Headers

Access response headers by dict-like key assignment:

```python
import uuid
from django.http import HttpResponse

def uuid_view(data):
    response = HttpResponse(data, content_type='application/json')
    response['UUID'] = str(uuid.uuid4())      # header name must match spec exactly
    return response
```

## FileResponse with In-Memory Buffers

`FileResponse` streams a file-like object. Use `io.StringIO` for text (CSV), `io.BytesIO` for binary (ZIP). Always `seek(0)` before wrapping in `FileResponse`. Pass `filename=` to set the download filename:

```python
import io
from django.http import FileResponse

# CSV: use StringIO
csv_io = io.StringIO()
writer = csv.writer(csv_io)
writer.writerow(header)
writer.writerows(csv_data)
csv_io.seek(0)
response = FileResponse(csv_io, as_attachment=True, filename='data.csv')
response['Content-Type'] = 'text/csv'
return response

# ZIP: use BytesIO
zip_io = io.BytesIO()
with zipfile.ZipFile(zip_io, 'w') as zf:
    for path in file_paths:
        zf.writestr(path, 'This is the content of {}.'.format(path))
zip_io.seek(0)
response = FileResponse(zip_io, as_attachment=True, filename='files.zip')
response['Content-Type'] = 'application/zip'
return response
```

## ZIP Files with Virtual Content — Use writestr

When adding entries to a ZIP without reading real files from disk, use `zipfile.ZipFile.writestr(arcname, data)`:

```python
with zipfile.ZipFile(zip_io, 'w') as zip_file:
    for file_path in file_paths:
        zip_file.writestr(file_path, 'This is the content of {}.'.format(file_path))
```

## Authentication View Pattern

Handle credential validation with a single try/except block. Catch all decode-related exceptions together and return `HttpResponseBadRequest` for invalid input:

```python
import hashlib
import base64
import binascii
from django.http import HttpResponseBadRequest, HttpResponse

def auth_view(data):
    try:
        username = data['username']
        password = base64.b64decode(data['password']).decode()
    except (KeyError, UnicodeDecodeError, binascii.Error, ValueError):
        return HttpResponseBadRequest('Bad Request')

    hashed = hashlib.sha256(password.encode()).digest()
    expected = hashlib.sha256('password'.encode()).digest()

    if username == 'admin' and hashed == expected:
        return HttpResponse('Login successful.')   # 200, no status argument
    return HttpResponse('Login failed.', status=401)
```

## Random Session Key Pattern

```python
import random
import string
from django.http import HttpResponse

def session_view(request, session_expire_time):
    session_key = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    has_digit = any(c.isdigit() for c in session_key)
    has_letter = any(c.isalpha() for c in session_key)
    if not (has_digit and has_letter) or len(session_key) != 20:
        raise ValueError("Session key should contain both letters and digits")
    response = HttpResponse('Session key generated successfully.')
    response.set_cookie('session_key', session_key, max_age=session_expire_time)
    return response
```
